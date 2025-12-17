#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio to Text Processing Module

Implements OpenAI's Speech to Text API with support for:
- Transcriptions (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize)
- Translations (whisper-1 only - translates to English)
- Streaming transcriptions
- Speaker diarization
- Large file chunking
- Prompt-based improvements

Based on OpenAI API documentation for audio processing.
"""

import os
import io
import base64
import tempfile
from pathlib import Path
from typing import (
    Optional,
    Union,
    List,
    Dict,
    Any,
    Iterator,
    Literal,
    BinaryIO,
    Generator,
)
from dataclasses import dataclass, field
from enum import Enum
import json

# OpenAI integration
try:
    from openai import OpenAI
    from openai._streaming import Stream

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore
    Stream = None  # type: ignore

# PyDub for audio file handling (optional - for chunking large files)
try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None  # type: ignore


class TranscriptionModel(str, Enum):
    """Available transcription models."""

    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Response format options."""

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


class ChunkingStrategy(str, Enum):
    """Chunking strategy for diarization."""

    AUTO = "auto"
    VAD = "vad"


@dataclass
class TranscriptionSegment:
    """A segment from a transcription with timestamps."""

    text: str
    start: float
    end: float
    speaker: Optional[str] = None
    segment_id: Optional[str] = None


@dataclass
class TranscriptionWord:
    """A word from a transcription with timestamp."""

    word: str
    start: float
    end: float


@dataclass
class TranscriptionResult:
    """Result from a transcription request."""

    text: str
    model: str
    segments: List[TranscriptionSegment] = field(default_factory=list)
    words: List[TranscriptionWord] = field(default_factory=list)
    language: Optional[str] = None
    duration: Optional[float] = None
    task: str = "transcribe"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "segments": [
                {
                    "text": s.text,
                    "start": s.start,
                    "end": s.end,
                    "speaker": s.speaker,
                    "segment_id": s.segment_id,
                }
                for s in self.segments
            ],
            "words": [
                {"word": w.word, "start": w.start, "end": w.end} for w in self.words
            ],
            "language": self.language,
            "duration": self.duration,
            "task": self.task,
        }


@dataclass
class StreamEvent:
    """Event from a streaming transcription."""

    event_type: str  # transcript.text.delta, transcript.text.done, transcript.text.segment
    text: Optional[str] = None
    delta: Optional[str] = None
    segment_id: Optional[str] = None
    speaker: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None
    logprobs: Optional[List[Dict[str, Any]]] = None


@dataclass
class KnownSpeaker:
    """Known speaker for diarization."""

    name: str
    audio_path: Optional[str] = None  # Path to audio file
    audio_data_url: Optional[str] = None  # Data URL if already encoded


class AudioToText:
    """
    Audio to Text processor using OpenAI's Speech to Text API.

    Supports transcription and translation with multiple models:
    - whisper-1: Original Whisper model, supports all formats and timestamps
    - gpt-4o-transcribe: Higher quality, supports json/text, prompts, logprobs
    - gpt-4o-mini-transcribe: Faster variant of gpt-4o-transcribe
    - gpt-4o-transcribe-diarize: Speaker diarization support

    Usage:
        audio_processor = AudioToText()
        result = audio_processor.transcribe("audio.mp3")
        print(result.text)
    """

    # Supported file types
    SUPPORTED_FORMATS = ("mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm")

    # Maximum file size (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024

    # Default chunk size for large files (10 minutes in milliseconds)
    DEFAULT_CHUNK_MS = 10 * 60 * 1000

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: TranscriptionModel = TranscriptionModel.GPT_4O_TRANSCRIBE,
    ):
        """
        Initialize the AudioToText processor.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env variable.
            default_model: Default transcription model to use.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.default_model = default_model

    def transcribe(
        self,
        audio_file: Union[str, Path, BinaryIO],
        model: Optional[TranscriptionModel] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: ResponseFormat = ResponseFormat.JSON,
        temperature: float = 0.0,
        timestamp_granularities: Optional[List[TimestampGranularity]] = None,
        stream: bool = False,
        include_logprobs: bool = False,
    ) -> Union[TranscriptionResult, Generator[StreamEvent, None, None]]:
        """
        Transcribe audio to text.

        Args:
            audio_file: Path to audio file or file-like object.
            model: Transcription model to use.
            language: ISO-639-1 language code (e.g., 'en', 'es').
            prompt: Optional prompt to improve transcription quality.
            response_format: Output format (json, text, srt, verbose_json, vtt).
            temperature: Sampling temperature (0.0 to 1.0).
            timestamp_granularities: List of timestamp types (word, segment) - whisper-1 only.
            stream: Whether to stream the response (gpt-4o models only).
            include_logprobs: Include log probabilities in response.

        Returns:
            TranscriptionResult or Generator of StreamEvent if streaming.

        Example:
            # Basic transcription
            result = audio.transcribe("meeting.mp3")
            print(result.text)

            # With model and language
            result = audio.transcribe(
                "meeting.mp3",
                model=TranscriptionModel.GPT_4O_TRANSCRIBE,
                language="es",
                prompt="This is a business meeting about Q4 results."
            )
        """
        model = model or self.default_model
        file_obj = self._prepare_file(audio_file)

        try:
            if stream:
                return self._transcribe_stream(
                    file_obj,
                    model,
                    language,
                    prompt,
                    response_format,
                    temperature,
                    include_logprobs,
                )

            # Build request parameters
            params: Dict[str, Any] = {
                "file": file_obj,
                "model": model.value,
                "response_format": response_format.value,
                "temperature": temperature,
            }

            if language:
                params["language"] = language

            if prompt:
                params["prompt"] = prompt

            # timestamp_granularities only for whisper-1
            if timestamp_granularities and model == TranscriptionModel.WHISPER_1:
                params["timestamp_granularities"] = [
                    g.value for g in timestamp_granularities
                ]
                # Requires verbose_json format for timestamps
                if response_format != ResponseFormat.VERBOSE_JSON:
                    params["response_format"] = ResponseFormat.VERBOSE_JSON.value

            # Make API call
            response = self.client.audio.transcriptions.create(**params)

            return self._parse_transcription_response(response, model)

        finally:
            if hasattr(file_obj, "close") and not isinstance(audio_file, (str, Path)):
                pass  # Don't close user-provided file objects
            elif hasattr(file_obj, "close"):
                file_obj.close()

    def _transcribe_stream(
        self,
        file_obj: BinaryIO,
        model: TranscriptionModel,
        language: Optional[str],
        prompt: Optional[str],
        response_format: ResponseFormat,
        temperature: float,
        include_logprobs: bool,
    ) -> Generator[StreamEvent, None, None]:
        """Stream transcription results."""
        if model == TranscriptionModel.WHISPER_1:
            raise ValueError("Streaming is not supported for whisper-1 model.")

        params: Dict[str, Any] = {
            "file": file_obj,
            "model": model.value,
            "response_format": response_format.value,
            "temperature": temperature,
            "stream": True,
        }

        if language:
            params["language"] = language

        if prompt and model != TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE:
            params["prompt"] = prompt

        if include_logprobs:
            params["include"] = ["logprobs"]

        stream = self.client.audio.transcriptions.create(**params)

        for event in stream:
            yield self._parse_stream_event(event)

    def transcribe_diarize(
        self,
        audio_file: Union[str, Path, BinaryIO],
        known_speakers: Optional[List[KnownSpeaker]] = None,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.AUTO,
        response_format: ResponseFormat = ResponseFormat.DIARIZED_JSON,
        stream: bool = False,
    ) -> Union[TranscriptionResult, Generator[StreamEvent, None, None]]:
        """
        Transcribe audio with speaker diarization.

        Identifies different speakers in the audio and labels their speech segments.

        Args:
            audio_file: Path to audio file or file-like object.
            known_speakers: List of known speakers with reference audio clips.
            chunking_strategy: How to chunk audio for processing (auto or vad).
            response_format: Output format (json, text, diarized_json).
            stream: Whether to stream the response.

        Returns:
            TranscriptionResult with speaker-labeled segments.

        Example:
            speakers = [
                KnownSpeaker(name="Alice", audio_path="alice_sample.wav"),
                KnownSpeaker(name="Bob", audio_path="bob_sample.wav"),
            ]
            result = audio.transcribe_diarize("meeting.wav", known_speakers=speakers)
            for segment in result.segments:
                print(f"{segment.speaker}: {segment.text}")
        """
        model = TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE
        file_obj = self._prepare_file(audio_file)

        try:
            params: Dict[str, Any] = {
                "file": file_obj,
                "model": model.value,
                "response_format": response_format.value,
                "chunking_strategy": chunking_strategy.value,
            }

            if stream:
                params["stream"] = True

            # Add known speakers if provided
            extra_body: Dict[str, Any] = {}
            if known_speakers:
                speaker_names = []
                speaker_refs = []
                for speaker in known_speakers[:4]:  # Max 4 speakers
                    speaker_names.append(speaker.name)
                    if speaker.audio_data_url:
                        speaker_refs.append(speaker.audio_data_url)
                    elif speaker.audio_path:
                        data_url = self._file_to_data_url(speaker.audio_path)
                        speaker_refs.append(data_url)

                if speaker_names:
                    extra_body["known_speaker_names"] = speaker_names
                if speaker_refs:
                    extra_body["known_speaker_references"] = speaker_refs

            if extra_body:
                params["extra_body"] = extra_body

            if stream:
                stream_response = self.client.audio.transcriptions.create(**params)
                return self._stream_diarize_generator(stream_response)

            response = self.client.audio.transcriptions.create(**params)
            return self._parse_transcription_response(response, model)

        finally:
            if hasattr(file_obj, "close") and isinstance(audio_file, (str, Path)):
                file_obj.close()

    def _stream_diarize_generator(
        self, stream: Any
    ) -> Generator[StreamEvent, None, None]:
        """Generate events from diarization stream."""
        for event in stream:
            yield self._parse_stream_event(event)

    def translate(
        self,
        audio_file: Union[str, Path, BinaryIO],
        prompt: Optional[str] = None,
        response_format: ResponseFormat = ResponseFormat.JSON,
        temperature: float = 0.0,
    ) -> TranscriptionResult:
        """
        Translate audio to English text.

        Takes audio in any supported language and transcribes it to English.
        Only supports whisper-1 model.

        Args:
            audio_file: Path to audio file or file-like object.
            prompt: Optional prompt to improve translation quality.
            response_format: Output format (json, text, srt, verbose_json, vtt).
            temperature: Sampling temperature (0.0 to 1.0).

        Returns:
            TranscriptionResult with English text.

        Example:
            # Translate German audio to English
            result = audio.translate("german_audio.mp3")
            print(result.text)  # "Hello, my name is Wolfgang..."
        """
        file_obj = self._prepare_file(audio_file)

        try:
            params: Dict[str, Any] = {
                "file": file_obj,
                "model": TranscriptionModel.WHISPER_1.value,
                "response_format": response_format.value,
                "temperature": temperature,
            }

            if prompt:
                params["prompt"] = prompt

            response = self.client.audio.translations.create(**params)

            result = self._parse_transcription_response(
                response, TranscriptionModel.WHISPER_1
            )
            result.task = "translate"
            return result

        finally:
            if hasattr(file_obj, "close") and isinstance(audio_file, (str, Path)):
                file_obj.close()

    def transcribe_large_file(
        self,
        audio_file: Union[str, Path],
        model: Optional[TranscriptionModel] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        chunk_duration_ms: int = None,
        overlap_ms: int = 0,
    ) -> TranscriptionResult:
        """
        Transcribe a large audio file by splitting it into chunks.

        For files larger than 25MB, splits the audio and transcribes each chunk.
        Uses the previous chunk's transcription as context for the next.

        Args:
            audio_file: Path to audio file.
            model: Transcription model to use.
            language: ISO-639-1 language code.
            prompt: Initial prompt for the first chunk.
            chunk_duration_ms: Duration of each chunk in milliseconds.
            overlap_ms: Overlap between chunks to avoid cutting sentences.

        Returns:
            Combined TranscriptionResult from all chunks.

        Requires:
            pip install pydub

        Example:
            result = audio.transcribe_large_file(
                "long_meeting.mp3",
                chunk_duration_ms=10 * 60 * 1000  # 10 minutes
            )
        """
        if not PYDUB_AVAILABLE:
            raise ImportError(
                "PyDub is required for large file handling. "
                "Install with: pip install pydub"
            )

        model = model or self.default_model
        chunk_duration_ms = chunk_duration_ms or self.DEFAULT_CHUNK_MS

        # Load audio file
        audio_path = Path(audio_file)
        file_ext = audio_path.suffix.lower().lstrip(".")

        if file_ext in ("mp3",):
            audio = AudioSegment.from_mp3(audio_path)
        elif file_ext in ("wav",):
            audio = AudioSegment.from_wav(audio_path)
        elif file_ext in ("m4a", "mp4"):
            audio = AudioSegment.from_file(audio_path, format="mp4")
        else:
            audio = AudioSegment.from_file(audio_path)

        # Calculate chunks
        duration_ms = len(audio)
        chunks = []
        start = 0

        while start < duration_ms:
            end = min(start + chunk_duration_ms, duration_ms)
            chunk = audio[start:end]
            chunks.append(chunk)
            start = end - overlap_ms if overlap_ms > 0 else end

        # Transcribe each chunk
        all_text = []
        all_segments = []
        all_words = []
        running_offset = 0.0
        current_prompt = prompt or ""

        for i, chunk in enumerate(chunks):
            # Export chunk to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as temp_file:
                chunk.export(temp_file.name, format="mp3")
                temp_path = temp_file.name

            try:
                result = self.transcribe(
                    temp_path,
                    model=model,
                    language=language,
                    prompt=current_prompt,
                    response_format=ResponseFormat.VERBOSE_JSON
                    if model == TranscriptionModel.WHISPER_1
                    else ResponseFormat.JSON,
                )

                all_text.append(result.text)

                # Adjust segment timestamps
                for seg in result.segments:
                    seg.start += running_offset
                    seg.end += running_offset
                    all_segments.append(seg)

                # Adjust word timestamps
                for word in result.words:
                    word.start += running_offset
                    word.end += running_offset
                    all_words.append(word)

                # Update running offset
                chunk_duration_sec = len(chunk) / 1000.0
                running_offset += chunk_duration_sec

                # Use last 224 tokens of transcript as context for next chunk
                # This helps maintain context across chunks
                if model == TranscriptionModel.WHISPER_1:
                    # Whisper uses last 224 tokens
                    current_prompt = result.text[-500:]  # Approximate token limit
                else:
                    current_prompt = result.text

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

        return TranscriptionResult(
            text=" ".join(all_text),
            model=model.value,
            segments=all_segments,
            words=all_words,
            language=language,
            duration=duration_ms / 1000.0,
            task="transcribe",
        )

    def _prepare_file(self, audio_file: Union[str, Path, BinaryIO]) -> BinaryIO:
        """Prepare file for API request."""
        if isinstance(audio_file, (str, Path)):
            path = Path(audio_file)
            if not path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

            # Check file extension
            ext = path.suffix.lower().lstrip(".")
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported file format: {ext}. "
                    f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
                )

            # Check file size
            file_size = path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                raise ValueError(
                    f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds "
                    f"maximum of 25MB. Use transcribe_large_file() instead."
                )

            return open(path, "rb")

        return audio_file

    def _file_to_data_url(self, file_path: Union[str, Path]) -> str:
        """Convert audio file to data URL for speaker references."""
        path = Path(file_path)
        ext = path.suffix.lower().lstrip(".")

        mime_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "mp4": "audio/mp4",
            "webm": "audio/webm",
            "mpeg": "audio/mpeg",
            "mpga": "audio/mpeg",
        }

        mime_type = mime_types.get(ext, "audio/mpeg")

        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime_type};base64,{data}"

    def _parse_transcription_response(
        self, response: Any, model: TranscriptionModel
    ) -> TranscriptionResult:
        """Parse API response into TranscriptionResult."""
        # Handle string response (text format)
        if isinstance(response, str):
            return TranscriptionResult(
                text=response,
                model=model.value,
            )

        # Handle object response
        text = getattr(response, "text", "")
        segments = []
        words = []
        language = getattr(response, "language", None)
        duration = getattr(response, "duration", None)

        # Parse segments if available
        if hasattr(response, "segments"):
            for seg in response.segments:
                segments.append(
                    TranscriptionSegment(
                        text=getattr(seg, "text", ""),
                        start=getattr(seg, "start", 0.0),
                        end=getattr(seg, "end", 0.0),
                        speaker=getattr(seg, "speaker", None),
                        segment_id=getattr(seg, "id", None),
                    )
                )

        # Parse words if available
        if hasattr(response, "words"):
            for word in response.words:
                words.append(
                    TranscriptionWord(
                        word=getattr(word, "word", ""),
                        start=getattr(word, "start", 0.0),
                        end=getattr(word, "end", 0.0),
                    )
                )

        return TranscriptionResult(
            text=text,
            model=model.value,
            segments=segments,
            words=words,
            language=language,
            duration=duration,
            task="transcribe",
        )

    def _parse_stream_event(self, event: Any) -> StreamEvent:
        """Parse streaming event."""
        event_type = getattr(event, "type", "unknown")

        if event_type == "transcript.text.delta":
            return StreamEvent(
                event_type=event_type,
                delta=getattr(event, "delta", None),
                segment_id=getattr(event, "segment_id", None),
                logprobs=getattr(event, "logprobs", None),
            )
        elif event_type == "transcript.text.done":
            return StreamEvent(
                event_type=event_type,
                text=getattr(event, "text", None),
            )
        elif event_type == "transcript.text.segment":
            return StreamEvent(
                event_type=event_type,
                text=getattr(event, "text", None),
                speaker=getattr(event, "speaker", None),
                start=getattr(event, "start", None),
                end=getattr(event, "end", None),
                segment_id=getattr(event, "id", None),
            )
        else:
            return StreamEvent(event_type=event_type)


# Convenience functions for quick access
_default_processor: Optional[AudioToText] = None


def get_audio_processor(api_key: Optional[str] = None) -> AudioToText:
    """
    Get or create a default AudioToText processor.

    Args:
        api_key: Optional API key. Uses OPENAI_API_KEY if not provided.

    Returns:
        AudioToText instance.
    """
    global _default_processor
    if _default_processor is None:
        _default_processor = AudioToText(api_key=api_key)
    return _default_processor


def transcribe(
    audio_file: Union[str, Path, BinaryIO],
    model: Optional[TranscriptionModel] = None,
    language: Optional[str] = None,
    prompt: Optional[str] = None,
) -> TranscriptionResult:
    """
    Quick transcription of an audio file.

    Args:
        audio_file: Path to audio file or file-like object.
        model: Transcription model to use.
        language: ISO-639-1 language code.
        prompt: Optional prompt to improve quality.

    Returns:
        TranscriptionResult with the transcribed text.

    Example:
        result = transcribe("meeting.mp3", language="en")
        print(result.text)
    """
    processor = get_audio_processor()
    return processor.transcribe(
        audio_file, model=model, language=language, prompt=prompt
    )


def translate(audio_file: Union[str, Path, BinaryIO]) -> TranscriptionResult:
    """
    Quick translation of audio to English.

    Args:
        audio_file: Path to audio file or file-like object.

    Returns:
        TranscriptionResult with English text.

    Example:
        result = translate("spanish_audio.mp3")
        print(result.text)
    """
    processor = get_audio_processor()
    return processor.translate(audio_file)


def transcribe_with_speakers(
    audio_file: Union[str, Path, BinaryIO],
    known_speakers: Optional[List[KnownSpeaker]] = None,
) -> TranscriptionResult:
    """
    Quick transcription with speaker diarization.

    Args:
        audio_file: Path to audio file.
        known_speakers: Optional list of known speakers.

    Returns:
        TranscriptionResult with speaker-labeled segments.

    Example:
        result = transcribe_with_speakers("meeting.wav")
        for seg in result.segments:
            print(f"{seg.speaker}: {seg.text}")
    """
    processor = get_audio_processor()
    return processor.transcribe_diarize(audio_file, known_speakers=known_speakers)


# Export all public classes and functions
__all__ = [
    # Main class
    "AudioToText",
    # Enums
    "TranscriptionModel",
    "ResponseFormat",
    "TimestampGranularity",
    "ChunkingStrategy",
    # Data classes
    "TranscriptionResult",
    "TranscriptionSegment",
    "TranscriptionWord",
    "StreamEvent",
    "KnownSpeaker",
    # Convenience functions
    "get_audio_processor",
    "transcribe",
    "translate",
    "transcribe_with_speakers",
    # Constants
    "OPENAI_AVAILABLE",
    "PYDUB_AVAILABLE",
]
