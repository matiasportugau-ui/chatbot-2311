#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speech-to-Text utility module using OpenAI Audio API.

Supports:
- Transcriptions (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize)
- Translations (whisper-1 only)
- Streaming transcriptions
- Speaker diarization
- Timestamps
- Prompting for better accuracy
"""

import os
import base64
from typing import Optional, Union, List, Dict, Any, Iterator, BinaryIO
from pathlib import Path
from enum import Enum

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not installed. Install with: pip install openai>=1.0.0")

from utils.structured_logger import get_structured_logger
from utils.request_tracking import get_request_tracker

logger = get_structured_logger(__name__)


class TranscriptionModel(str, Enum):
    """Supported transcription models"""
    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Supported response formats"""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"


class ChunkingStrategy(str, Enum):
    """Chunking strategies for long audio"""
    AUTO = "auto"


class SpeechToTextClient:
    """Client for OpenAI Speech-to-Text API operations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Speech-to-Text client.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai>=1.0.0"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.logger = get_structured_logger(__name__)
        self.request_tracker = get_request_tracker()
    
    def transcribe(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: Union[str, TranscriptionModel] = TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format: Union[str, ResponseFormat] = ResponseFormat.JSON,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
        chunking_strategy: Optional[Union[str, ChunkingStrategy]] = None,
        known_speaker_names: Optional[List[str]] = None,
        known_speaker_references: Optional[List[str]] = None,
        include_logprobs: bool = False,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file or file-like object.
                       Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
            model: Model to use for transcription
            response_format: Format of the response (json, text, srt, verbose_json, vtt, diarized_json)
            language: Language code (ISO 639-1 or 639-3) for GPT-4o models
            prompt: Optional prompt to improve transcription quality
            temperature: Sampling temperature (0-1)
            timestamp_granularities: List of granularities: ["word", "segment"] (whisper-1 only)
            chunking_strategy: Required for gpt-4o-transcribe-diarize when audio > 30s
            known_speaker_names: List of speaker names for diarization
            known_speaker_references: List of data URLs with speaker reference audio clips
            include_logprobs: Include log probabilities in response
        
        Returns:
            Transcription result as dictionary
        """
        # Validate model and response format compatibility
        model_str = model.value if isinstance(model, TranscriptionModel) else model
        
        if model_str == TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value:
            if response_format not in [ResponseFormat.JSON, ResponseFormat.TEXT, ResponseFormat.DIARIZED_JSON]:
                raise ValueError(
                    f"gpt-4o-transcribe-diarize only supports json, text, or diarized_json formats"
                )
        
        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
        else:
            file_obj = audio_file
        
        try:
            # Prepare parameters
            params = {
                "model": model_str,
                "file": file_obj,
            }
            
            if response_format:
                response_format_str = (
                    response_format.value if isinstance(response_format, ResponseFormat)
                    else response_format
                )
                params["response_format"] = response_format_str
            
            if language:
                params["language"] = language
            
            if prompt:
                params["prompt"] = prompt
            
            if temperature is not None:
                params["temperature"] = temperature
            
            if timestamp_granularities:
                params["timestamp_granularities"] = timestamp_granularities
            
            if chunking_strategy:
                chunking_str = (
                    chunking_strategy.value if isinstance(chunking_strategy, ChunkingStrategy)
                    else chunking_strategy
                )
                params["chunking_strategy"] = chunking_str
            
            # Handle speaker references for diarization
            if known_speaker_names and known_speaker_references:
                params["extra_body"] = {
                    "known_speaker_names": known_speaker_names,
                    "known_speaker_references": known_speaker_references,
                }
            
            if include_logprobs:
                params["include"] = ["logprobs"]
            
            # Make API call
            self.logger.info(
                "Transcribing audio",
                extra={
                    "model": model_str,
                    "response_format": params.get("response_format"),
                    "has_prompt": bool(prompt),
                }
            )
            
            response = self.client.audio.transcriptions.create(**params)
            
            # Convert response to dictionary
            if isinstance(response, str):
                return {"text": response}
            elif hasattr(response, "text"):
                result = {"text": response.text}
                if hasattr(response, "segments"):
                    result["segments"] = [
                        {
                            "speaker": seg.speaker if hasattr(seg, "speaker") else None,
                            "text": seg.text,
                            "start": seg.start if hasattr(seg, "start") else None,
                            "end": seg.end if hasattr(seg, "end") else None,
                        }
                        for seg in response.segments
                    ]
                if hasattr(response, "words"):
                    result["words"] = [
                        {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                        }
                        for word in response.words
                    ]
                return result
            else:
                return dict(response) if hasattr(response, "__dict__") else {"text": str(response)}
        
        finally:
            if isinstance(audio_file, (str, Path)):
                file_obj.close()
    
    def transcribe_stream(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: Union[str, TranscriptionModel] = TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
        response_format: Union[str, ResponseFormat] = ResponseFormat.TEXT,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        include_logprobs: bool = False,
        chunking_strategy: Optional[Union[str, ChunkingStrategy]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream transcription results as they become available.
        
        Args:
            audio_file: Path to audio file or file-like object
            model: Model to use (streaming not supported for whisper-1)
            response_format: Format of the response
            language: Language code
            prompt: Optional prompt
            include_logprobs: Include log probabilities
            chunking_strategy: Required for diarization with long audio
        
        Yields:
            Dictionary with transcription events
        """
        model_str = model.value if isinstance(model, TranscriptionModel) else model
        
        if model_str == TranscriptionModel.WHISPER_1.value:
            raise ValueError("Streaming not supported for whisper-1 model")
        
        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
        else:
            file_obj = audio_file
        
        try:
            params = {
                "model": model_str,
                "file": file_obj,
                "stream": True,
            }
            
            if response_format:
                response_format_str = (
                    response_format.value if isinstance(response_format, ResponseFormat)
                    else response_format
                )
                params["response_format"] = response_format_str
            
            if language:
                params["language"] = language
            
            if prompt:
                params["prompt"] = prompt
            
            if include_logprobs:
                params["include"] = ["logprobs"]
            
            if chunking_strategy:
                chunking_str = (
                    chunking_strategy.value if isinstance(chunking_strategy, ChunkingStrategy)
                    else chunking_strategy
                )
                params["chunking_strategy"] = chunking_str
            
            self.logger.info("Starting streaming transcription", extra={"model": model_str})
            
            stream = self.client.audio.transcriptions.create(**params)
            
            for event in stream:
                yield {
                    "type": getattr(event, "type", "unknown"),
                    "data": dict(event) if hasattr(event, "__dict__") else str(event),
                }
        
        finally:
            if isinstance(audio_file, (str, Path)):
                file_obj.close()
    
    def translate(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: str = TranscriptionModel.WHISPER_1.value,
        response_format: Union[str, ResponseFormat] = ResponseFormat.JSON,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Translate audio to English text.
        
        Note: Only whisper-1 model supports translations.
        
        Args:
            audio_file: Path to audio file or file-like object
            model: Model to use (only whisper-1 supported)
            response_format: Format of the response
            prompt: Optional prompt
            temperature: Sampling temperature
        
        Returns:
            Translation result as dictionary
        """
        if model != TranscriptionModel.WHISPER_1.value:
            raise ValueError("Translations only supported with whisper-1 model")
        
        # Prepare file
        if isinstance(audio_file, (str, Path)):
            file_path = Path(audio_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            file_obj = open(file_path, "rb")
        else:
            file_obj = audio_file
        
        try:
            params = {
                "model": model,
                "file": file_obj,
            }
            
            if response_format:
                response_format_str = (
                    response_format.value if isinstance(response_format, ResponseFormat)
                    else response_format
                )
                params["response_format"] = response_format_str
            
            if prompt:
                params["prompt"] = prompt
            
            if temperature is not None:
                params["temperature"] = temperature
            
            self.logger.info("Translating audio to English")
            
            response = self.client.audio.translations.create(**params)
            
            # Convert response to dictionary
            if isinstance(response, str):
                return {"text": response}
            elif hasattr(response, "text"):
                return {"text": response.text}
            else:
                return dict(response) if hasattr(response, "__dict__") else {"text": str(response)}
        
        finally:
            if isinstance(audio_file, (str, Path)):
                file_obj.close()
    
    @staticmethod
    def to_data_url(audio_file: Union[str, Path]) -> str:
        """
        Convert audio file to data URL for speaker reference.
        
        Args:
            audio_file: Path to audio file
        
        Returns:
            Data URL string
        """
        file_path = Path(audio_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
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
        
        with open(file_path, "rb") as f:
            audio_data = f.read()
            base64_data = base64.b64encode(audio_data).decode("utf-8")
        
        return f"data:{mime_type};base64,{base64_data}"


# Convenience functions
def transcribe_audio(
    audio_file: Union[str, Path, BinaryIO],
    model: Union[str, TranscriptionModel] = TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format: Union[str, ResponseFormat] = ResponseFormat.JSON,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to transcribe audio.
    
    Args:
        audio_file: Path to audio file or file-like object
        model: Model to use
        response_format: Response format
        **kwargs: Additional parameters passed to transcribe()
    
    Returns:
        Transcription result
    """
    client = SpeechToTextClient()
    return client.transcribe(audio_file, model=model, response_format=response_format, **kwargs)


def translate_audio(
    audio_file: Union[str, Path, BinaryIO],
    response_format: Union[str, ResponseFormat] = ResponseFormat.JSON,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to translate audio to English.
    
    Args:
        audio_file: Path to audio file or file-like object
        response_format: Response format
        **kwargs: Additional parameters passed to translate()
    
    Returns:
        Translation result
    """
    client = SpeechToTextClient()
    return client.translate(audio_file, response_format=response_format, **kwargs)
