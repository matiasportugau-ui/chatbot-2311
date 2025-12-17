#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speech-to-Text utility module for OpenAI Audio API.

Supports:
- Transcriptions (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize)
- Translations (whisper-1 only)
- Speaker diarization
- Streaming transcriptions
- Timestamps (word and segment level)
- Prompting for improved accuracy
- Post-processing with GPT-4 for reliability
"""

import os
import base64
from typing import Optional, List, Dict, Any, Union, Iterator, BinaryIO
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from utils.structured_logger import get_structured_logger
from utils.request_tracking import get_request_tracker


class TranscriptionModel(str, Enum):
    """Available transcription models"""
    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Available response formats"""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"


class ChunkingStrategy(str, Enum):
    """Chunking strategies for long audio"""
    AUTO = "auto"


@dataclass
class TranscriptionResult:
    """Result from transcription API"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    segments: Optional[List[Dict[str, Any]]] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class DiarizedSegment:
    """Speaker diarization segment"""
    speaker: str
    text: str
    start: float
    end: float


@dataclass
class DiarizedTranscriptionResult:
    """Result from diarized transcription"""
    text: str
    segments: List[DiarizedSegment]
    raw_response: Optional[Dict[str, Any]] = None


class SpeechToTextService:
    """Service for speech-to-text operations using OpenAI Audio API"""

    def __init__(self, api_key: Optional[str] = None, model: TranscriptionModel = TranscriptionModel.GPT_4O_TRANSCRIBE):
        """
        Initialize the Speech-to-Text service.

        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: Default transcription model to use.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is required. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key parameter.")

        self.client = OpenAI(api_key=self.api_key)
        self.default_model = model
        self.logger = get_structured_logger()
        self.request_tracker = get_request_tracker()

    def transcribe(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: Optional[TranscriptionModel] = None,
        response_format: ResponseFormat = ResponseFormat.JSON,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.

        Args:
            audio_file: Path to audio file or file-like object
            model: Transcription model to use (defaults to instance default)
            response_format: Format of the response
            language: Language code (ISO 639-1 or 639-3)
            prompt: Optional prompt to improve transcription quality
            temperature: Sampling temperature (0.0 to 1.0)
            timestamp_granularities: List of granularities: ["word", "segment"]
            **kwargs: Additional parameters

        Returns:
            TranscriptionResult with transcribed text and metadata
        """
        model = model or self.default_model
        model_str = model.value if isinstance(model, TranscriptionModel) else model

        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
            should_close = True
        else:
            file_obj = audio_file
            should_close = False

        try:
            # Prepare parameters
            params = {
                "file": file_obj,
                "model": model_str,
                "response_format": response_format.value if isinstance(response_format, ResponseFormat) else response_format,
            }

            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt
            if temperature is not None:
                params["temperature"] = temperature
            if timestamp_granularities:
                params["timestamp_granularities"] = timestamp_granularities

            # Add any additional kwargs
            params.update(kwargs)

            # Track request
            request_id = self.request_tracker.generate_request_id()
            self.logger.log_openai_request(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions",
                request_id=request_id,
            )

            # Make API call
            response = self.client.audio.transcriptions.create(**params)

            # Parse response
            if isinstance(response, str):
                # Text format
                result = TranscriptionResult(text=response)
            elif hasattr(response, 'text'):
                # JSON format
                result = TranscriptionResult(
                    text=response.text,
                    language=getattr(response, 'language', None),
                    duration=getattr(response, 'duration', None),
                    words=getattr(response, 'words', None),
                    segments=getattr(response, 'segments', None),
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                )
            else:
                result = TranscriptionResult(
                    text=str(response),
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                )

            self.logger.log_openai_response(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions",
                request_id=request_id,
            )

            return result

        except Exception as e:
            self.logger.log_openai_error(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions",
                error=str(e),
                request_id=request_id if 'request_id' in locals() else None,
            )
            raise
        finally:
            if should_close:
                file_obj.close()

    def transcribe_with_diarization(
        self,
        audio_file: Union[str, Path, BinaryIO],
        known_speaker_names: Optional[List[str]] = None,
        known_speaker_references: Optional[List[Union[str, Path]]] = None,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.AUTO,
        **kwargs
    ) -> DiarizedTranscriptionResult:
        """
        Transcribe audio with speaker diarization.

        Args:
            audio_file: Path to audio file or file-like object
            known_speaker_names: List of known speaker names
            known_speaker_references: List of reference audio files (2-10 seconds each)
            chunking_strategy: Strategy for chunking long audio
            **kwargs: Additional parameters

        Returns:
            DiarizedTranscriptionResult with speaker-labeled segments
        """
        # Prepare speaker references as data URLs
        speaker_refs_data_urls = []
        if known_speaker_references:
            for ref_path in known_speaker_references:
                if isinstance(ref_path, (str, Path)):
                    data_url = self._file_to_data_url(ref_path)
                    speaker_refs_data_urls.append(data_url)
                else:
                    speaker_refs_data_urls.append(ref_path)

        # Prepare extra_body for known speakers
        extra_body = {}
        if known_speaker_names and speaker_refs_data_urls:
            extra_body["known_speaker_names"] = known_speaker_names
            extra_body["known_speaker_references"] = speaker_refs_data_urls

        # Make transcription request
        result = self.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE,
            response_format=ResponseFormat.DIARIZED_JSON,
            chunking_strategy=chunking_strategy.value,
            extra_body=extra_body if extra_body else None,
            **kwargs
        )

        # Parse diarized segments
        segments = []
        if result.raw_response and "segments" in result.raw_response:
            for seg in result.raw_response["segments"]:
                segments.append(DiarizedSegment(
                    speaker=seg.get("speaker", "unknown"),
                    text=seg.get("text", ""),
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                ))
        elif result.segments:
            for seg in result.segments:
                segments.append(DiarizedSegment(
                    speaker=seg.get("speaker", "unknown"),
                    text=seg.get("text", ""),
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                ))

        return DiarizedTranscriptionResult(
            text=result.text,
            segments=segments,
            raw_response=result.raw_response,
        )

    def translate(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: TranscriptionModel = TranscriptionModel.WHISPER_1,
        response_format: ResponseFormat = ResponseFormat.JSON,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Translate and transcribe audio to English.

        Note: Only whisper-1 model supports translations.

        Args:
            audio_file: Path to audio file or file-like object
            model: Model to use (must be whisper-1)
            response_format: Format of the response
            prompt: Optional prompt to improve translation quality
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters

        Returns:
            TranscriptionResult with English translation
        """
        if model != TranscriptionModel.WHISPER_1:
            raise ValueError("Translations only support whisper-1 model")

        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
            should_close = True
        else:
            file_obj = audio_file
            should_close = False

        try:
            params = {
                "file": file_obj,
                "model": model.value,
                "response_format": response_format.value if isinstance(response_format, ResponseFormat) else response_format,
            }

            if prompt:
                params["prompt"] = prompt
            if temperature is not None:
                params["temperature"] = temperature

            params.update(kwargs)

            request_id = self.request_tracker.generate_request_id()
            self.logger.log_openai_request(
                provider="openai",
                model=model.value,
                endpoint="audio.translations",
                request_id=request_id,
            )

            response = self.client.audio.translations.create(**params)

            if isinstance(response, str):
                result = TranscriptionResult(text=response)
            elif hasattr(response, 'text'):
                result = TranscriptionResult(
                    text=response.text,
                    language="en",  # Translations are always English
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                )
            else:
                result = TranscriptionResult(
                    text=str(response),
                    raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                )

            self.logger.log_openai_response(
                provider="openai",
                model=model.value,
                endpoint="audio.translations",
                request_id=request_id,
            )

            return result

        except Exception as e:
            self.logger.log_openai_error(
                provider="openai",
                model=model.value,
                endpoint="audio.translations",
                error=str(e),
                request_id=request_id if 'request_id' in locals() else None,
            )
            raise
        finally:
            if should_close:
                file_obj.close()

    def transcribe_stream(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: Optional[TranscriptionModel] = None,
        response_format: ResponseFormat = ResponseFormat.TEXT,
        include_logprobs: bool = False,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream transcription results as they become available.

        Note: Streaming is not supported for whisper-1.

        Args:
            audio_file: Path to audio file or file-like object
            model: Transcription model (must not be whisper-1)
            response_format: Format of the response
            include_logprobs: Include log probabilities in response
            **kwargs: Additional parameters

        Yields:
            Dictionary with transcription events
        """
        model = model or self.default_model
        model_str = model.value if isinstance(model, TranscriptionModel) else model

        if model_str == TranscriptionModel.WHISPER_1.value:
            raise ValueError("Streaming is not supported for whisper-1 model")

        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
            should_close = True
        else:
            file_obj = audio_file
            should_close = False

        try:
            params = {
                "file": file_obj,
                "model": model_str,
                "response_format": response_format.value if isinstance(response_format, ResponseFormat) else response_format,
                "stream": True,
            }

            if include_logprobs:
                params["include"] = ["logprobs"]

            params.update(kwargs)

            request_id = self.request_tracker.generate_request_id()
            self.logger.log_openai_request(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions.stream",
                request_id=request_id,
            )

            stream = self.client.audio.transcriptions.create(**params)

            for event in stream:
                yield event

            self.logger.log_openai_response(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions.stream",
                request_id=request_id,
            )

        except Exception as e:
            self.logger.log_openai_error(
                provider="openai",
                model=model_str,
                endpoint="audio.transcriptions.stream",
                error=str(e),
                request_id=request_id if 'request_id' in locals() else None,
            )
            raise
        finally:
            if should_close:
                file_obj.close()

    def transcribe_with_post_processing(
        self,
        audio_file: Union[str, Path, BinaryIO],
        system_prompt: str,
        correction_model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        transcription_model: Optional[TranscriptionModel] = None,
        **kwargs
    ) -> str:
        """
        Transcribe audio and post-process with GPT-4 for improved accuracy.

        This method first transcribes the audio, then uses GPT-4 to correct
        spelling discrepancies, especially for uncommon words or acronyms.

        Args:
            audio_file: Path to audio file or file-like object
            system_prompt: System prompt for GPT-4 post-processing
            correction_model: GPT model to use for correction
            temperature: Temperature for GPT-4 correction
            transcription_model: Model to use for initial transcription
            **kwargs: Additional transcription parameters

        Returns:
            Corrected transcription text
        """
        # First, transcribe the audio
        transcription_result = self.transcribe(
            audio_file=audio_file,
            model=transcription_model,
            **kwargs
        )

        # Then post-process with GPT-4
        request_id = self.request_tracker.generate_request_id()
        self.logger.log_openai_request(
            provider="openai",
            model=correction_model,
            endpoint="chat.completions",
            request_id=request_id,
        )

        try:
            completion = self.client.chat.completions.create(
                model=correction_model,
                temperature=temperature,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": transcription_result.text
                    }
                ],
            )

            corrected_text = completion.choices[0].message.content

            self.logger.log_openai_response(
                provider="openai",
                model=correction_model,
                endpoint="chat.completions",
                request_id=request_id,
            )

            return corrected_text

        except Exception as e:
            self.logger.log_openai_error(
                provider="openai",
                model=correction_model,
                endpoint="chat.completions",
                error=str(e),
                request_id=request_id,
            )
            # Return original transcription if post-processing fails
            self.logger.warning(f"Post-processing failed, returning original transcription: {e}")
            return transcription_result.text

    def _file_to_data_url(self, file_path: Union[str, Path]) -> str:
        """
        Convert audio file to data URL for speaker reference.

        Args:
            file_path: Path to audio file

        Returns:
            Data URL string
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Reference audio file not found: {file_path}")

        # Determine MIME type from extension
        ext = file_path.suffix.lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".mp4": "audio/mp4",
            ".mpeg": "audio/mpeg",
            ".mpga": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
            ".webm": "audio/webm",
        }
        mime_type = mime_types.get(ext, "audio/mpeg")

        # Read and encode file
        with open(file_path, "rb") as f:
            audio_data = f.read()
            base64_data = base64.b64encode(audio_data).decode("utf-8")

        return f"data:{mime_type};base64,{base64_data}"


# Convenience functions
def get_speech_to_text_service(api_key: Optional[str] = None) -> SpeechToTextService:
    """
    Get a SpeechToTextService instance.

    Args:
        api_key: OpenAI API key (optional, uses env var if not provided)

    Returns:
        SpeechToTextService instance
    """
    return SpeechToTextService(api_key=api_key)


def transcribe_audio(
    audio_file: Union[str, Path, BinaryIO],
    model: TranscriptionModel = TranscriptionModel.GPT_4O_TRANSCRIBE,
    **kwargs
) -> TranscriptionResult:
    """
    Convenience function to transcribe audio.

    Args:
        audio_file: Path to audio file or file-like object
        model: Transcription model to use
        **kwargs: Additional parameters

    Returns:
        TranscriptionResult
    """
    service = get_speech_to_text_service()
    return service.transcribe(audio_file=audio_file, model=model, **kwargs)


def translate_audio(
    audio_file: Union[str, Path, BinaryIO],
    **kwargs
) -> TranscriptionResult:
    """
    Convenience function to translate audio to English.

    Args:
        audio_file: Path to audio file or file-like object
        **kwargs: Additional parameters

    Returns:
        TranscriptionResult with English translation
    """
    service = get_speech_to_text_service()
    return service.translate(audio_file=audio_file, **kwargs)
