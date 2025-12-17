#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio to Text Processing Module
===============================

Provides comprehensive speech-to-text functionality using OpenAI's Audio API.

Features:
- Transcription with multiple model support (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe)
- Speaker diarization with known speaker identification
- Translation to English
- Streaming transcription support
- Long audio file handling with automatic chunking
- Post-processing with GPT-4 for improved accuracy

Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
File size limit: 25 MB per request

Based on OpenAI Audio API documentation.
"""

import os
import base64
import logging
from pathlib import Path
from typing import Optional, Literal, Generator, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionModel(str, Enum):
    """Available transcription models."""
    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Available response formats."""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"


class TimestampGranularity(str, Enum):
    """Timestamp granularity options (whisper-1 only)."""
    WORD = "word"
    SEGMENT = "segment"


@dataclass
class TranscriptionSegment:
    """Represents a transcription segment with speaker diarization."""
    speaker: str
    text: str
    start: float
    end: float


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    text: str
    segments: List[TranscriptionSegment] = field(default_factory=list)
    words: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    duration: Optional[float] = None


class AudioToText:
    """
    Main class for audio-to-text processing using OpenAI's Audio API.
    
    Example usage:
        >>> from audio_to_text import AudioToText
        >>> processor = AudioToText()
        >>> result = processor.transcribe("audio.mp3")
        >>> print(result.text)
    """
    
    # Supported audio formats
    SUPPORTED_FORMATS = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    
    # Maximum file size in bytes (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AudioToText processor.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env variable.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def _validate_file(self, file_path: str) -> Path:
        """Validate the audio file exists and is supported."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        extension = path.suffix.lower().lstrip(".")
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / 1024 / 1024} MB). "
                "Use chunk_and_transcribe() for longer files."
            )
        
        return path
    
    def _to_data_url(self, file_path: str) -> str:
        """Convert an audio file to a data URL for speaker references."""
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        
        return f"data:audio/{extension};base64,{data}"
    
    def transcribe(
        self,
        file_path: str,
        model: Union[TranscriptionModel, str] = TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format: Union[ResponseFormat, str] = ResponseFormat.JSON,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        timestamp_granularities: Optional[List[TimestampGranularity]] = None,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file to text.
        
        Args:
            file_path: Path to the audio file.
            model: Transcription model to use.
            response_format: Output format (json, text, srt, verbose_json, vtt).
            language: Language code (ISO 639-1) of the audio.
            prompt: Optional prompt to guide transcription.
            temperature: Sampling temperature (0-1).
            timestamp_granularities: Granularity for timestamps (whisper-1 only).
        
        Returns:
            TranscriptionResult with the transcribed text and metadata.
        
        Example:
            >>> result = processor.transcribe(
            ...     "lecture.mp3",
            ...     model="gpt-4o-transcribe",
            ...     prompt="This is a lecture about AI and machine learning."
            ... )
            >>> print(result.text)
        """
        path = self._validate_file(file_path)
        
        # Convert enums to strings if needed
        model_str = model.value if isinstance(model, TranscriptionModel) else model
        format_str = response_format.value if isinstance(response_format, ResponseFormat) else response_format
        
        # Prepare request parameters
        params: Dict[str, Any] = {
            "model": model_str,
            "file": open(path, "rb"),
            "response_format": format_str,
            "temperature": temperature,
        }
        
        if language:
            params["language"] = language
        
        if prompt and model_str != TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value:
            params["prompt"] = prompt
        
        # Timestamp granularities only supported for whisper-1
        if timestamp_granularities and model_str == TranscriptionModel.WHISPER_1.value:
            params["timestamp_granularities"] = [
                g.value if isinstance(g, TimestampGranularity) else g 
                for g in timestamp_granularities
            ]
            if format_str != ResponseFormat.VERBOSE_JSON.value:
                params["response_format"] = ResponseFormat.VERBOSE_JSON.value
        
        try:
            response = self.client.audio.transcriptions.create(**params)
            
            # Handle different response formats
            if format_str == ResponseFormat.TEXT.value:
                return TranscriptionResult(text=response)
            
            result = TranscriptionResult(text=response.text)
            
            if hasattr(response, "words"):
                result.words = response.words
            if hasattr(response, "language"):
                result.language = response.language
            if hasattr(response, "duration"):
                result.duration = response.duration
            
            return result
            
        finally:
            params["file"].close()
    
    def transcribe_with_diarization(
        self,
        file_path: str,
        chunking_strategy: Union[str, Dict[str, Any]] = "auto",
        known_speaker_names: Optional[List[str]] = None,
        known_speaker_references: Optional[List[str]] = None,
        response_format: str = "diarized_json",
    ) -> TranscriptionResult:
        """
        Transcribe audio with speaker diarization.
        
        Uses gpt-4o-transcribe-diarize model to identify different speakers
        in the audio and label their speech segments.
        
        Args:
            file_path: Path to the audio file.
            chunking_strategy: "auto" or VAD configuration dict.
            known_speaker_names: List of known speaker names (up to 4).
            known_speaker_references: List of data URLs for speaker reference clips (2-10 seconds each).
            response_format: Output format ("json", "text", or "diarized_json").
        
        Returns:
            TranscriptionResult with speaker-labeled segments.
        
        Example:
            >>> result = processor.transcribe_with_diarization(
            ...     "meeting.wav",
            ...     known_speaker_names=["Alice", "Bob"],
            ...     known_speaker_references=[
            ...         processor._to_data_url("alice_ref.wav"),
            ...         processor._to_data_url("bob_ref.wav")
            ...     ]
            ... )
            >>> for segment in result.segments:
            ...     print(f"{segment.speaker}: {segment.text}")
        """
        path = self._validate_file(file_path)
        
        params: Dict[str, Any] = {
            "model": TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value,
            "file": open(path, "rb"),
            "response_format": response_format,
            "chunking_strategy": chunking_strategy,
        }
        
        # Add known speaker information
        extra_body: Dict[str, Any] = {}
        if known_speaker_names:
            if len(known_speaker_names) > 4:
                raise ValueError("Maximum 4 known speakers allowed")
            extra_body["known_speaker_names"] = known_speaker_names
        
        if known_speaker_references:
            if len(known_speaker_references) > 4:
                raise ValueError("Maximum 4 speaker references allowed")
            extra_body["known_speaker_references"] = known_speaker_references
        
        if extra_body:
            params["extra_body"] = extra_body
        
        try:
            response = self.client.audio.transcriptions.create(**params)
            
            result = TranscriptionResult(text=response.text)
            
            if hasattr(response, "segments"):
                result.segments = [
                    TranscriptionSegment(
                        speaker=seg.speaker,
                        text=seg.text,
                        start=seg.start,
                        end=seg.end
                    )
                    for seg in response.segments
                ]
            
            return result
            
        finally:
            params["file"].close()
    
    def translate(
        self,
        file_path: str,
        response_format: Union[ResponseFormat, str] = ResponseFormat.JSON,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> TranscriptionResult:
        """
        Translate audio to English text.
        
        Takes audio in any supported language and transcribes it to English.
        Uses the whisper-1 model (only model supporting translation).
        
        Args:
            file_path: Path to the audio file.
            response_format: Output format.
            prompt: Optional prompt for better translation.
            temperature: Sampling temperature (0-1).
        
        Returns:
            TranscriptionResult with English translation.
        
        Example:
            >>> result = processor.translate("german_speech.mp3")
            >>> print(result.text)  # English translation
        """
        path = self._validate_file(file_path)
        
        format_str = response_format.value if isinstance(response_format, ResponseFormat) else response_format
        
        params: Dict[str, Any] = {
            "model": TranscriptionModel.WHISPER_1.value,  # Only whisper-1 supports translation
            "file": open(path, "rb"),
            "response_format": format_str,
            "temperature": temperature,
        }
        
        if prompt:
            params["prompt"] = prompt
        
        try:
            response = self.client.audio.translations.create(**params)
            
            if format_str == ResponseFormat.TEXT.value:
                return TranscriptionResult(text=response)
            
            return TranscriptionResult(text=response.text)
            
        finally:
            params["file"].close()
    
    def transcribe_stream(
        self,
        file_path: str,
        model: Union[TranscriptionModel, str] = TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
        response_format: str = "text",
        prompt: Optional[str] = None,
        include_logprobs: bool = False,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream transcription of an audio file.
        
        Yields transcript events as they become available.
        Not supported for whisper-1 model.
        
        Args:
            file_path: Path to the audio file.
            model: Transcription model (gpt-4o-transcribe or gpt-4o-mini-transcribe).
            response_format: Output format ("text" or "json").
            prompt: Optional prompt for better transcription.
            include_logprobs: Include log probabilities in response.
        
        Yields:
            Dict with event type and data.
        
        Example:
            >>> for event in processor.transcribe_stream("audio.mp3"):
            ...     if event.get("type") == "transcript.text.delta":
            ...         print(event["delta"], end="", flush=True)
        """
        path = self._validate_file(file_path)
        
        model_str = model.value if isinstance(model, TranscriptionModel) else model
        
        if model_str == TranscriptionModel.WHISPER_1.value:
            raise ValueError("Streaming is not supported for whisper-1 model")
        
        params: Dict[str, Any] = {
            "model": model_str,
            "file": open(path, "rb"),
            "response_format": response_format,
            "stream": True,
        }
        
        if prompt:
            params["prompt"] = prompt
        
        if include_logprobs:
            params["include"] = ["logprobs"]
        
        try:
            stream = self.client.audio.transcriptions.create(**params)
            
            for event in stream:
                yield {
                    "type": getattr(event, "type", "unknown"),
                    "data": event
                }
                
        finally:
            params["file"].close()
    
    def transcribe_with_timestamps(
        self,
        file_path: str,
        granularities: List[str] = ["word"],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe with word or segment-level timestamps.
        
        Uses whisper-1 model with verbose_json format to get detailed timestamps.
        Useful for video editing, subtitle generation, and precise audio alignment.
        
        Args:
            file_path: Path to the audio file.
            granularities: List of "word" and/or "segment".
            language: Optional language code.
            prompt: Optional prompt for better transcription.
        
        Returns:
            TranscriptionResult with word-level timestamps.
        
        Example:
            >>> result = processor.transcribe_with_timestamps("audio.mp3", ["word", "segment"])
            >>> for word in result.words:
            ...     print(f"{word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
        """
        path = self._validate_file(file_path)
        
        params: Dict[str, Any] = {
            "model": TranscriptionModel.WHISPER_1.value,
            "file": open(path, "rb"),
            "response_format": ResponseFormat.VERBOSE_JSON.value,
            "timestamp_granularities": granularities,
        }
        
        if language:
            params["language"] = language
        
        if prompt:
            params["prompt"] = prompt
        
        try:
            response = self.client.audio.transcriptions.create(**params)
            
            result = TranscriptionResult(
                text=response.text,
                language=getattr(response, "language", None),
                duration=getattr(response, "duration", None),
            )
            
            if hasattr(response, "words"):
                result.words = [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in response.words
                ]
            
            if hasattr(response, "segments"):
                result.segments = [
                    TranscriptionSegment(
                        speaker="",
                        text=s.text,
                        start=s.start,
                        end=s.end
                    )
                    for s in response.segments
                ]
            
            return result
            
        finally:
            params["file"].close()
    
    def correct_transcription(
        self,
        transcribed_text: str,
        correction_context: str,
        model: str = "gpt-4.1",
        temperature: float = 0.0,
    ) -> str:
        """
        Post-process transcription using GPT-4 for improved accuracy.
        
        Corrects spelling, adds proper punctuation, and fixes domain-specific
        terms based on the provided context.
        
        Args:
            transcribed_text: The original transcribed text.
            correction_context: Context with correct spellings, product names, etc.
            model: GPT model to use for correction.
            temperature: Sampling temperature.
        
        Returns:
            Corrected transcription text.
        
        Example:
            >>> context = '''
            ... You are a helpful assistant for BMC Uruguay. Correct spelling for:
            ... Products: Isodec, Poliestireno, Lana de Roca, Poliuretano
            ... Terms: BMC Uruguay, aislamiento térmico, cotización
            ... '''
            >>> corrected = processor.correct_transcription(raw_text, context)
        """
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": correction_context},
                {"role": "user", "content": transcribed_text}
            ]
        )
        
        return response.choices[0].message.content


# Convenience functions for quick usage

def transcribe(
    file_path: str,
    model: str = "gpt-4o-transcribe",
    **kwargs
) -> str:
    """
    Quick transcription of an audio file.
    
    Args:
        file_path: Path to audio file.
        model: Model to use.
        **kwargs: Additional parameters for transcription.
    
    Returns:
        Transcribed text.
    """
    processor = AudioToText()
    result = processor.transcribe(file_path, model=model, **kwargs)
    return result.text


def translate(file_path: str, **kwargs) -> str:
    """
    Quick translation of audio to English.
    
    Args:
        file_path: Path to audio file.
        **kwargs: Additional parameters.
    
    Returns:
        English translation.
    """
    processor = AudioToText()
    result = processor.translate(file_path, **kwargs)
    return result.text


def transcribe_with_speakers(
    file_path: str,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Quick transcription with speaker diarization.
    
    Args:
        file_path: Path to audio file.
        **kwargs: Additional parameters.
    
    Returns:
        List of segments with speaker labels.
    """
    processor = AudioToText()
    result = processor.transcribe_with_diarization(file_path, **kwargs)
    return [
        {"speaker": s.speaker, "text": s.text, "start": s.start, "end": s.end}
        for s in result.segments
    ]


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_to_text.py <audio_file>")
        print("\nExample:")
        print("  python audio_to_text.py recording.mp3")
        print("\nSupported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    try:
        processor = AudioToText()
        print(f"Transcribing: {audio_file}")
        result = processor.transcribe(audio_file)
        print("\n" + "=" * 50)
        print("TRANSCRIPTION:")
        print("=" * 50)
        print(result.text)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Transcription failed: {e}")
        sys.exit(1)
