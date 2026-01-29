#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Transcription Module - OpenAI Speech to Text
===================================================

Comprehensive audio transcription using OpenAI's Audio API.

Supported models:
- whisper-1: Original Whisper model (supports multiple output formats)
- gpt-4o-transcribe: Higher quality transcription
- gpt-4o-mini-transcribe: Faster, cost-effective transcription
- gpt-4o-transcribe-diarize: Speaker-aware transcription with diarization

Features:
- Transcription in original language
- Translation to English
- Speaker diarization with known speaker references
- Streaming transcription
- File chunking for large files (>25MB)
- Timestamp extraction (word/segment level)

Supported input formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
Maximum file size: 25 MB per request
"""

import os
import base64
import logging
from pathlib import Path
from typing import Optional, List, Literal, Generator, Any, Dict, Union
from dataclasses import dataclass, field

from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type aliases for clarity
TranscriptionModel = Literal[
    "whisper-1",
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
    "gpt-4o-transcribe-diarize"
]

ResponseFormat = Literal[
    "json", "text", "srt", "verbose_json", "vtt", "diarized_json"
]

TimestampGranularity = Literal["word", "segment"]


@dataclass
class TranscriptionSegment:
    """Represents a segment of transcribed audio with optional speaker info."""
    text: str
    start: Optional[float] = None
    end: Optional[float] = None
    speaker: Optional[str] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""
    text: str
    segments: List[TranscriptionSegment] = field(default_factory=list)
    words: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    model: Optional[str] = None


class AudioTranscriber:
    """
    OpenAI Audio Transcription client.
    
    Provides comprehensive audio-to-text capabilities using OpenAI's Audio API,
    including transcription, translation, diarization, and streaming.
    
    Example usage:
        transcriber = AudioTranscriber()
        
        # Simple transcription
        result = transcriber.transcribe("audio.mp3")
        print(result.text)
        
        # Transcription with speaker diarization
        result = transcriber.transcribe_with_diarization("meeting.wav")
        for segment in result.segments:
            print(f"{segment.speaker}: {segment.text}")
        
        # Translation to English
        result = transcriber.translate("german_audio.mp3")
        print(result.text)
    """
    
    # Maximum file size allowed by OpenAI API (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    # Supported audio formats
    SUPPORTED_FORMATS = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AudioTranscriber.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def _validate_file(self, file_path: Union[str, Path]) -> Path:
        """Validate that the file exists and is a supported format."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")
        
        extension = path.suffix.lower().lstrip(".")
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {extension}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            logger.warning(
                f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds 25 MB limit. "
                "Consider using chunk_and_transcribe() method."
            )
        
        return path
    
    def _file_to_data_url(self, file_path: Union[str, Path]) -> str:
        """Convert an audio file to a base64 data URL."""
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        
        # Map extensions to MIME types
        mime_types = {
            "mp3": "audio/mpeg",
            "mp4": "audio/mp4",
            "mpeg": "audio/mpeg",
            "mpga": "audio/mpeg",
            "m4a": "audio/mp4",
            "wav": "audio/wav",
            "webm": "audio/webm",
        }
        
        mime_type = mime_types.get(extension, "audio/mpeg")
        
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        
        return f"data:{mime_type};base64,{encoded}"
    
    def transcribe(
        self,
        file_path: Union[str, Path],
        model: TranscriptionModel = "gpt-4o-transcribe",
        response_format: ResponseFormat = "json",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0,
        timestamp_granularities: Optional[List[TimestampGranularity]] = None,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file to text.
        
        Args:
            file_path: Path to the audio file.
            model: The transcription model to use.
                - "whisper-1": Original Whisper (supports all formats)
                - "gpt-4o-transcribe": Higher quality
                - "gpt-4o-mini-transcribe": Faster, cost-effective
                - "gpt-4o-transcribe-diarize": With speaker labels
            response_format: Output format.
                - whisper-1: json, text, srt, verbose_json, vtt
                - gpt-4o models: json, text
                - diarize model: json, text, diarized_json
            language: ISO-639-1 language code (e.g., "en", "es", "fr").
            prompt: Context prompt to improve transcription accuracy.
            temperature: Sampling temperature (0.0 to 1.0).
            timestamp_granularities: ["word"], ["segment"], or both (whisper-1 only).
        
        Returns:
            TranscriptionResult with transcribed text and metadata.
        
        Example:
            result = transcriber.transcribe(
                "lecture.mp3",
                model="gpt-4o-transcribe",
                prompt="This is a lecture about machine learning and AI."
            )
        """
        path = self._validate_file(file_path)
        
        # Build request parameters
        params: Dict[str, Any] = {
            "model": model,
            "response_format": response_format,
        }
        
        if language:
            params["language"] = language
        
        # Prompt not supported for diarize model
        if prompt and model != "gpt-4o-transcribe-diarize":
            params["prompt"] = prompt
        
        if temperature != 0.0:
            params["temperature"] = temperature
        
        # timestamp_granularities only for whisper-1
        if timestamp_granularities and model == "whisper-1":
            params["timestamp_granularities"] = timestamp_granularities
            # verbose_json required for timestamps
            if response_format != "verbose_json":
                params["response_format"] = "verbose_json"
        
        logger.info(f"Transcribing {path.name} with model {model}")
        
        with open(path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                file=audio_file,
                **params
            )
        
        return self._parse_response(response, model)
    
    def transcribe_with_diarization(
        self,
        file_path: Union[str, Path],
        known_speakers: Optional[Dict[str, Union[str, Path]]] = None,
        chunking_strategy: str = "auto",
        response_format: ResponseFormat = "diarized_json",
    ) -> TranscriptionResult:
        """
        Transcribe audio with speaker diarization.
        
        Uses gpt-4o-transcribe-diarize to identify different speakers
        in the audio and label their segments.
        
        Args:
            file_path: Path to the audio file.
            known_speakers: Optional dict mapping speaker names to reference audio files.
                Example: {"Alice": "alice_voice.wav", "Bob": "bob_voice.wav"}
                Reference clips should be 2-10 seconds long.
            chunking_strategy: How to split audio for processing ("auto" recommended).
            response_format: "json", "text", or "diarized_json".
        
        Returns:
            TranscriptionResult with speaker-labeled segments.
        
        Example:
            result = transcriber.transcribe_with_diarization(
                "meeting.wav",
                known_speakers={
                    "Manager": "manager_intro.wav",
                    "Employee": "employee_intro.wav"
                }
            )
            for segment in result.segments:
                print(f"[{segment.start:.1f}s] {segment.speaker}: {segment.text}")
        """
        path = self._validate_file(file_path)
        
        params: Dict[str, Any] = {
            "model": "gpt-4o-transcribe-diarize",
            "response_format": response_format,
            "chunking_strategy": chunking_strategy,
        }
        
        # Add known speaker references if provided
        extra_body = {}
        if known_speakers:
            speaker_names = list(known_speakers.keys())
            speaker_refs = [
                self._file_to_data_url(ref_path) 
                for ref_path in known_speakers.values()
            ]
            extra_body["known_speaker_names"] = speaker_names
            extra_body["known_speaker_references"] = speaker_refs
        
        logger.info(
            f"Transcribing {path.name} with diarization "
            f"({len(known_speakers) if known_speakers else 0} known speakers)"
        )
        
        with open(path, "rb") as audio_file:
            if extra_body:
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    extra_body=extra_body,
                    **params
                )
            else:
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    **params
                )
        
        return self._parse_response(response, "gpt-4o-transcribe-diarize")
    
    def translate(
        self,
        file_path: Union[str, Path],
        response_format: ResponseFormat = "json",
        prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> TranscriptionResult:
        """
        Translate audio from any supported language to English.
        
        Uses the whisper-1 model to transcribe and translate the audio
        into English text.
        
        Args:
            file_path: Path to the audio file in any supported language.
            response_format: Output format (json, text, srt, verbose_json, vtt).
            prompt: Context prompt to improve translation accuracy.
            temperature: Sampling temperature (0.0 to 1.0).
        
        Returns:
            TranscriptionResult with English translation.
        
        Example:
            result = transcriber.translate("spanish_podcast.mp3")
            print(result.text)  # English translation
        """
        path = self._validate_file(file_path)
        
        params: Dict[str, Any] = {
            "model": "whisper-1",  # Only whisper-1 supports translation
            "response_format": response_format,
        }
        
        if prompt:
            params["prompt"] = prompt
        
        if temperature != 0.0:
            params["temperature"] = temperature
        
        logger.info(f"Translating {path.name} to English")
        
        with open(path, "rb") as audio_file:
            response = self.client.audio.translations.create(
                file=audio_file,
                **params
            )
        
        return self._parse_response(response, "whisper-1")
    
    def transcribe_stream(
        self,
        file_path: Union[str, Path],
        model: TranscriptionModel = "gpt-4o-mini-transcribe",
        response_format: ResponseFormat = "text",
        prompt: Optional[str] = None,
        include_logprobs: bool = False,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream transcription events as they are generated.
        
        Yields transcription events in real-time as the model processes
        the audio. Useful for live feedback during transcription.
        
        Args:
            file_path: Path to the audio file.
            model: Transcription model (gpt-4o-transcribe or gpt-4o-mini-transcribe).
            response_format: Output format ("json" or "text").
            prompt: Context prompt to improve transcription.
            include_logprobs: Whether to include log probabilities.
        
        Yields:
            Dict with event data:
            - transcript.text.delta: Partial text updates
            - transcript.text.done: Final complete transcript
            - transcript.text.segment: (diarize only) Completed segments
        
        Example:
            for event in transcriber.transcribe_stream("lecture.mp3"):
                if event.type == "transcript.text.delta":
                    print(event.delta, end="", flush=True)
        
        Note:
            Streaming is not supported for whisper-1.
        """
        if model == "whisper-1":
            raise ValueError("Streaming is not supported for whisper-1 model")
        
        path = self._validate_file(file_path)
        
        params: Dict[str, Any] = {
            "model": model,
            "response_format": response_format,
            "stream": True,
        }
        
        if prompt and model != "gpt-4o-transcribe-diarize":
            params["prompt"] = prompt
        
        if include_logprobs:
            params["include"] = ["logprobs"]
        
        logger.info(f"Starting streaming transcription of {path.name}")
        
        with open(path, "rb") as audio_file:
            stream = self.client.audio.transcriptions.create(
                file=audio_file,
                **params
            )
            
            for event in stream:
                yield event
    
    def _parse_response(self, response: Any, model: str) -> TranscriptionResult:
        """Parse API response into TranscriptionResult."""
        result = TranscriptionResult(model=model, text="")
        
        # Handle different response types
        if hasattr(response, "text"):
            result.text = response.text
        elif isinstance(response, str):
            result.text = response
        elif isinstance(response, dict):
            result.text = response.get("text", "")
        
        # Parse segments if available (diarization or verbose_json)
        segments = getattr(response, "segments", None)
        if segments is not None and hasattr(segments, "__iter__"):
            try:
                for seg in segments:
                    # Handle both object and dict responses
                    if hasattr(seg, "text"):
                        text = seg.text
                        start = getattr(seg, "start", None)
                        end = getattr(seg, "end", None)
                        speaker = getattr(seg, "speaker", None)
                    elif isinstance(seg, dict):
                        text = seg.get("text", "")
                        start = seg.get("start")
                        end = seg.get("end")
                        speaker = seg.get("speaker")
                    else:
                        continue
                    
                    segment = TranscriptionSegment(
                        text=text,
                        start=start,
                        end=end,
                        speaker=speaker,
                    )
                    result.segments.append(segment)
            except TypeError:
                # segments was not actually iterable
                pass
        
        # Parse words if available (whisper-1 with word timestamps)
        words = getattr(response, "words", None)
        if words is not None and hasattr(words, "__iter__"):
            try:
                result.words = [
                    {"word": w.word, "start": w.start, "end": w.end}
                    for w in words
                ]
            except (TypeError, AttributeError):
                pass
        
        # Additional metadata
        if hasattr(response, "language"):
            result.language = response.language
        if hasattr(response, "duration"):
            result.duration = response.duration
        
        return result


def transcribe_file(
    file_path: Union[str, Path],
    model: TranscriptionModel = "gpt-4o-transcribe",
    **kwargs
) -> str:
    """
    Convenience function to transcribe an audio file.
    
    Args:
        file_path: Path to the audio file.
        model: The transcription model to use.
        **kwargs: Additional arguments passed to AudioTranscriber.transcribe()
    
    Returns:
        Transcribed text string.
    
    Example:
        text = transcribe_file("meeting.mp3")
        print(text)
    """
    transcriber = AudioTranscriber()
    result = transcriber.transcribe(file_path, model=model, **kwargs)
    return result.text


def translate_file(file_path: Union[str, Path], **kwargs) -> str:
    """
    Convenience function to translate an audio file to English.
    
    Args:
        file_path: Path to the audio file.
        **kwargs: Additional arguments passed to AudioTranscriber.translate()
    
    Returns:
        English translation text.
    
    Example:
        english_text = translate_file("german_speech.mp3")
    """
    transcriber = AudioTranscriber()
    result = transcriber.translate(file_path, **kwargs)
    return result.text


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("OpenAI Audio Transcription Module")
    print("=" * 60)
    print()
    print("Available models:")
    print("  - whisper-1: Original Whisper (all output formats)")
    print("  - gpt-4o-transcribe: Higher quality transcription")
    print("  - gpt-4o-mini-transcribe: Faster, cost-effective")
    print("  - gpt-4o-transcribe-diarize: Speaker diarization")
    print()
    print("Usage examples:")
    print()
    print("  # Basic transcription")
    print('  transcriber = AudioTranscriber()')
    print('  result = transcriber.transcribe("audio.mp3")')
    print('  print(result.text)')
    print()
    print("  # With prompt for better accuracy")
    print('  result = transcriber.transcribe(')
    print('      "meeting.mp3",')
    print('      model="gpt-4o-transcribe",')
    print('      prompt="Meeting about Q4 sales targets"')
    print('  )')
    print()
    print("  # Speaker diarization")
    print('  result = transcriber.transcribe_with_diarization(')
    print('      "interview.wav",')
    print('      known_speakers={"Host": "host.wav", "Guest": "guest.wav"}')
    print('  )')
    print('  for seg in result.segments:')
    print('      print(f"{seg.speaker}: {seg.text}")')
    print()
    print("  # Translation to English")
    print('  result = transcriber.translate("spanish_audio.mp3")')
    print()
    print("  # Streaming transcription")
    print('  for event in transcriber.transcribe_stream("lecture.mp3"):')
    print('      print(event)')
    print()
    
    # If a file path is provided, transcribe it
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4o-transcribe"
        
        print(f"Transcribing: {audio_file}")
        print(f"Model: {model}")
        print("-" * 40)
        
        try:
            transcriber = AudioTranscriber()
            result = transcriber.transcribe(audio_file, model=model)
            print(result.text)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
