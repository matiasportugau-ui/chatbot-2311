#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Audio to Text Processing Module

Run with: pytest tests/test_audio_to_text.py -v
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import pytest

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.audio_to_text import (
    AudioToText,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    ChunkingStrategy,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWord,
    StreamEvent,
    KnownSpeaker,
    get_audio_processor,
    OPENAI_AVAILABLE,
    PYDUB_AVAILABLE,
)


class TestTranscriptionModel:
    """Tests for TranscriptionModel enum."""

    def test_all_models_defined(self):
        """Verify all supported models are defined."""
        assert TranscriptionModel.WHISPER_1.value == "whisper-1"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE.value == "gpt-4o-transcribe"
        assert TranscriptionModel.GPT_4O_MINI_TRANSCRIBE.value == "gpt-4o-mini-transcribe"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value == "gpt-4o-transcribe-diarize"


class TestResponseFormat:
    """Tests for ResponseFormat enum."""

    def test_all_formats_defined(self):
        """Verify all response formats are defined."""
        assert ResponseFormat.JSON.value == "json"
        assert ResponseFormat.TEXT.value == "text"
        assert ResponseFormat.SRT.value == "srt"
        assert ResponseFormat.VERBOSE_JSON.value == "verbose_json"
        assert ResponseFormat.VTT.value == "vtt"
        assert ResponseFormat.DIARIZED_JSON.value == "diarized_json"


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""

    def test_basic_result(self):
        """Test creating a basic transcription result."""
        result = TranscriptionResult(
            text="Hello, world!",
            model="gpt-4o-transcribe",
        )
        assert result.text == "Hello, world!"
        assert result.model == "gpt-4o-transcribe"
        assert result.segments == []
        assert result.words == []
        assert result.task == "transcribe"

    def test_result_with_segments(self):
        """Test result with speaker segments."""
        segments = [
            TranscriptionSegment(
                text="Hello from Alice",
                start=0.0,
                end=2.0,
                speaker="Alice",
            ),
            TranscriptionSegment(
                text="Hello from Bob",
                start=2.5,
                end=4.0,
                speaker="Bob",
            ),
        ]
        result = TranscriptionResult(
            text="Hello from Alice Hello from Bob",
            model="gpt-4o-transcribe-diarize",
            segments=segments,
        )
        assert len(result.segments) == 2
        assert result.segments[0].speaker == "Alice"
        assert result.segments[1].speaker == "Bob"

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = TranscriptionResult(
            text="Test",
            model="whisper-1",
            language="en",
            duration=10.5,
        )
        d = result.to_dict()
        assert d["text"] == "Test"
        assert d["model"] == "whisper-1"
        assert d["language"] == "en"
        assert d["duration"] == 10.5


class TestKnownSpeaker:
    """Tests for KnownSpeaker dataclass."""

    def test_speaker_with_path(self):
        """Test creating speaker with audio path."""
        speaker = KnownSpeaker(
            name="Alice",
            audio_path="/path/to/alice.wav",
        )
        assert speaker.name == "Alice"
        assert speaker.audio_path == "/path/to/alice.wav"
        assert speaker.audio_data_url is None

    def test_speaker_with_data_url(self):
        """Test creating speaker with data URL."""
        speaker = KnownSpeaker(
            name="Bob",
            audio_data_url="data:audio/wav;base64,AAAA...",
        )
        assert speaker.name == "Bob"
        assert speaker.audio_path is None
        assert speaker.audio_data_url.startswith("data:audio/wav")


class TestAudioToText:
    """Tests for AudioToText class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch("utils.audio_to_text.OpenAI") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="API key required"):
                AudioToText(api_key=None)

    def test_initialization_with_api_key(self, mock_openai_client):
        """Test initialization with API key."""
        processor = AudioToText(api_key="test-key")
        assert processor.api_key == "test-key"
        assert processor.default_model == TranscriptionModel.GPT_4O_TRANSCRIBE

    def test_supported_formats(self):
        """Test supported file formats."""
        expected = ("mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm")
        assert AudioToText.SUPPORTED_FORMATS == expected

    def test_max_file_size(self):
        """Test max file size constant."""
        assert AudioToText.MAX_FILE_SIZE == 25 * 1024 * 1024  # 25 MB


class TestStreamEvent:
    """Tests for StreamEvent dataclass."""

    def test_delta_event(self):
        """Test creating a delta event."""
        event = StreamEvent(
            event_type="transcript.text.delta",
            delta="Hello",
            segment_id="seg-1",
        )
        assert event.event_type == "transcript.text.delta"
        assert event.delta == "Hello"
        assert event.segment_id == "seg-1"

    def test_done_event(self):
        """Test creating a done event."""
        event = StreamEvent(
            event_type="transcript.text.done",
            text="Hello, world!",
        )
        assert event.event_type == "transcript.text.done"
        assert event.text == "Hello, world!"

    def test_segment_event(self):
        """Test creating a segment event with speaker."""
        event = StreamEvent(
            event_type="transcript.text.segment",
            text="Hello from Alice",
            speaker="Alice",
            start=0.0,
            end=2.0,
        )
        assert event.event_type == "transcript.text.segment"
        assert event.speaker == "Alice"
        assert event.start == 0.0
        assert event.end == 2.0


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_audio_processor_caches(self):
        """Test that get_audio_processor returns cached instance."""
        # Reset the global processor
        import utils.audio_to_text as module
        
        # Create a mock processor and set it
        mock_processor = Mock(spec=AudioToText)
        module._default_processor = mock_processor

        # Get processor should return the cached instance
        proc1 = get_audio_processor(api_key="test")
        proc2 = get_audio_processor(api_key="test")

        # Both should be the same cached instance
        assert proc1 is proc2
        assert proc1 is mock_processor
        
        # Clean up
        module._default_processor = None


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI not installed")
class TestIntegration:
    """Integration tests (require OpenAI API key)."""

    @pytest.fixture
    def sample_audio_file(self, tmp_path):
        """Create a sample audio file for testing."""
        # Create a minimal valid WAV file header
        # This won't be actual audio, just for file handling tests
        wav_path = tmp_path / "test.wav"
        with open(wav_path, "wb") as f:
            # WAV header for empty audio
            f.write(b"RIFF")
            f.write((36).to_bytes(4, "little"))  # File size - 8
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write((16).to_bytes(4, "little"))  # Subchunk1 size
            f.write((1).to_bytes(2, "little"))   # Audio format (PCM)
            f.write((1).to_bytes(2, "little"))   # Num channels
            f.write((16000).to_bytes(4, "little"))  # Sample rate
            f.write((32000).to_bytes(4, "little"))  # Byte rate
            f.write((2).to_bytes(2, "little"))   # Block align
            f.write((16).to_bytes(2, "little"))  # Bits per sample
            f.write(b"data")
            f.write((0).to_bytes(4, "little"))   # Subchunk2 size
        return wav_path

    def test_file_validation(self, sample_audio_file):
        """Test file validation logic."""
        with patch("utils.audio_to_text.OpenAI"):
            processor = AudioToText(api_key="test-key")

            # Test with valid file
            file_obj = processor._prepare_file(sample_audio_file)
            assert file_obj is not None
            file_obj.close()

    def test_unsupported_format_rejected(self, tmp_path):
        """Test that unsupported formats are rejected."""
        with patch("utils.audio_to_text.OpenAI"):
            processor = AudioToText(api_key="test-key")

            # Create file with unsupported extension
            bad_file = tmp_path / "test.txt"
            bad_file.write_text("not audio")

            with pytest.raises(ValueError, match="Unsupported file format"):
                processor._prepare_file(bad_file)

    def test_file_not_found(self):
        """Test that non-existent files raise error."""
        with patch("utils.audio_to_text.OpenAI"):
            processor = AudioToText(api_key="test-key")

            with pytest.raises(FileNotFoundError):
                processor._prepare_file("/nonexistent/audio.mp3")


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
class TestRealAPI:
    """Real API tests (only run if API key is available)."""

    def test_api_connection(self):
        """Test that we can connect to OpenAI API."""
        processor = AudioToText()
        assert processor.client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
