#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the AudioProcessor module.

Run with: pytest tests/test_audio_processor.py -v
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_processor import (
    AudioProcessor,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWord,
    StreamEvent,
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE,
    transcribe,
    translate,
    transcribe_with_timestamps,
)


class TestTranscriptionModel:
    """Test TranscriptionModel enum"""
    
    def test_model_values(self):
        assert TranscriptionModel.WHISPER_1.value == "whisper-1"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE.value == "gpt-4o-transcribe"
        assert TranscriptionModel.GPT_4O_MINI_TRANSCRIBE.value == "gpt-4o-mini-transcribe"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value == "gpt-4o-transcribe-diarize"
    
    def test_model_from_string(self):
        model = TranscriptionModel("whisper-1")
        assert model == TranscriptionModel.WHISPER_1


class TestResponseFormat:
    """Test ResponseFormat enum"""
    
    def test_format_values(self):
        assert ResponseFormat.JSON.value == "json"
        assert ResponseFormat.TEXT.value == "text"
        assert ResponseFormat.SRT.value == "srt"
        assert ResponseFormat.VERBOSE_JSON.value == "verbose_json"
        assert ResponseFormat.VTT.value == "vtt"
        assert ResponseFormat.DIARIZED_JSON.value == "diarized_json"


class TestTimestampGranularity:
    """Test TimestampGranularity enum"""
    
    def test_granularity_values(self):
        assert TimestampGranularity.WORD.value == "word"
        assert TimestampGranularity.SEGMENT.value == "segment"


class TestTranscriptionResult:
    """Test TranscriptionResult dataclass"""
    
    def test_basic_result(self):
        result = TranscriptionResult(text="Hello world")
        assert result.text == "Hello world"
        assert result.language is None
        assert result.segments == []
        assert result.words == []
    
    def test_result_with_segments(self):
        segment = TranscriptionSegment(
            id=0,
            text="Hello",
            start=0.0,
            end=1.0,
            speaker="speaker_0"
        )
        result = TranscriptionResult(
            text="Hello",
            language="en",
            duration=1.0,
            segments=[segment],
            model="gpt-4o-transcribe"
        )
        assert result.language == "en"
        assert len(result.segments) == 1
        assert result.segments[0].speaker == "speaker_0"
    
    def test_to_dict(self):
        result = TranscriptionResult(
            text="Test",
            language="en",
            duration=5.0,
            model="whisper-1"
        )
        d = result.to_dict()
        assert d["text"] == "Test"
        assert d["language"] == "en"
        assert d["duration"] == 5.0
        assert d["model"] == "whisper-1"


class TestAudioProcessor:
    """Test AudioProcessor class"""
    
    @pytest.fixture
    def mock_openai(self):
        """Create a mock OpenAI client"""
        with patch('audio_processor.OpenAI') as mock:
            mock_client = MagicMock()
            mock.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def processor(self, mock_openai):
        """Create an AudioProcessor with mocked OpenAI"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            return AudioProcessor()
    
    @pytest.fixture
    def temp_audio_file(self):
        """Create a temporary audio file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            # Write some dummy content
            f.write(b"dummy audio content")
            f.flush()
            yield Path(f.name)
        # Cleanup
        os.unlink(f.name)
    
    def test_init_without_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            # Clear OPENAI_API_KEY if it exists
            os.environ.pop("OPENAI_API_KEY", None)
            with patch('audio_processor.OpenAI'):
                with pytest.raises(ValueError, match="API key is required"):
                    AudioProcessor()
    
    def test_init_with_api_key(self, mock_openai):
        """Test initialization with explicit API key"""
        processor = AudioProcessor(api_key="explicit-key")
        assert processor.api_key == "explicit-key"
    
    def test_validate_file_not_found(self, processor):
        """Test validation fails for non-existent file"""
        with pytest.raises(FileNotFoundError):
            processor._validate_file("/nonexistent/file.mp3")
    
    def test_validate_file_unsupported_format(self, processor):
        """Test validation fails for unsupported format"""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"content")
            f.flush()
            try:
                with pytest.raises(ValueError, match="Unsupported file format"):
                    processor._validate_file(f.name)
            finally:
                os.unlink(f.name)
    
    def test_validate_file_success(self, processor, temp_audio_file):
        """Test successful file validation"""
        result = processor._validate_file(temp_audio_file)
        assert result == temp_audio_file
    
    def test_get_valid_response_formats_whisper(self, processor):
        """Test valid formats for whisper-1"""
        formats = processor._get_valid_response_formats(TranscriptionModel.WHISPER_1)
        assert "json" in formats
        assert "text" in formats
        assert "srt" in formats
        assert "verbose_json" in formats
        assert "vtt" in formats
    
    def test_get_valid_response_formats_gpt4o(self, processor):
        """Test valid formats for gpt-4o-transcribe"""
        formats = processor._get_valid_response_formats(TranscriptionModel.GPT_4O_TRANSCRIBE)
        assert formats == ["json", "text"]
    
    def test_get_valid_response_formats_diarize(self, processor):
        """Test valid formats for gpt-4o-transcribe-diarize"""
        formats = processor._get_valid_response_formats(TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE)
        assert "json" in formats
        assert "text" in formats
        assert "diarized_json" in formats
    
    def test_transcribe_basic(self, processor, mock_openai, temp_audio_file):
        """Test basic transcription"""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "Hello world"
        mock_response.language = "en"
        mock_response.duration = 5.0
        mock_response.segments = []
        mock_response.words = []
        mock_response.task = "transcribe"
        
        mock_openai.audio.transcriptions.create.return_value = mock_response
        
        result = processor.transcribe(temp_audio_file)
        
        assert result.text == "Hello world"
        assert result.language == "en"
        mock_openai.audio.transcriptions.create.assert_called_once()
    
    def test_transcribe_with_prompt(self, processor, mock_openai, temp_audio_file):
        """Test transcription with prompt"""
        mock_response = Mock()
        mock_response.text = "OpenAI GPT-4"
        mock_response.language = "en"
        mock_response.duration = 3.0
        mock_response.segments = []
        mock_response.words = []
        mock_response.task = "transcribe"
        
        mock_openai.audio.transcriptions.create.return_value = mock_response
        
        result = processor.transcribe(
            temp_audio_file,
            prompt="The following is about OpenAI and GPT-4."
        )
        
        call_args = mock_openai.audio.transcriptions.create.call_args
        assert call_args.kwargs.get("prompt") == "The following is about OpenAI and GPT-4."
    
    def test_transcribe_invalid_format_for_model(self, processor, temp_audio_file):
        """Test that invalid format for model raises error"""
        with pytest.raises(ValueError, match="not supported"):
            processor.transcribe(
                temp_audio_file,
                model=TranscriptionModel.GPT_4O_TRANSCRIBE,
                response_format=ResponseFormat.SRT  # Not supported for gpt-4o-transcribe
            )
    
    def test_translate_basic(self, processor, mock_openai, temp_audio_file):
        """Test basic translation"""
        mock_response = Mock()
        mock_response.text = "Hello, my name is Wolfgang"
        mock_response.language = None
        mock_response.duration = 3.0
        mock_response.segments = []
        mock_response.words = []
        mock_response.task = "translate"
        
        mock_openai.audio.translations.create.return_value = mock_response
        
        result = processor.translate(temp_audio_file)
        
        assert result.text == "Hello, my name is Wolfgang"
        mock_openai.audio.translations.create.assert_called_once()
    
    def test_transcribe_stream_not_supported_whisper(self, processor, temp_audio_file):
        """Test streaming raises error for whisper-1"""
        with pytest.raises(ValueError, match="Streaming is not supported"):
            list(processor.transcribe_stream(
                temp_audio_file,
                model=TranscriptionModel.WHISPER_1
            ))
    
    def test_file_to_data_url(self, processor, temp_audio_file):
        """Test file to data URL conversion"""
        data_url = processor._file_to_data_url(temp_audio_file)
        
        assert data_url.startswith("data:audio/mpeg;base64,")
        # Verify it's valid base64
        import base64
        base64_part = data_url.split(",")[1]
        decoded = base64.b64decode(base64_part)
        assert decoded == b"dummy audio content"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @patch('audio_processor.AudioProcessor')
    def test_transcribe_function(self, mock_processor_class):
        """Test quick transcribe function"""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_result = TranscriptionResult(text="Test transcription")
        mock_processor.transcribe.return_value = mock_result
        
        result = transcribe("test.mp3", api_key="test-key")
        
        assert result == "Test transcription"
        mock_processor.transcribe.assert_called_once()
    
    @patch('audio_processor.AudioProcessor')
    def test_translate_function(self, mock_processor_class):
        """Test quick translate function"""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_result = TranscriptionResult(text="English translation")
        mock_processor.translate.return_value = mock_result
        
        result = translate("german.mp3", api_key="test-key")
        
        assert result == "English translation"
        mock_processor.translate.assert_called_once()
    
    @patch('audio_processor.AudioProcessor')
    def test_transcribe_with_timestamps_function(self, mock_processor_class):
        """Test transcribe with timestamps function"""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_result = TranscriptionResult(
            text="Test",
            words=[TranscriptionWord(word="Test", start=0.0, end=0.5)]
        )
        mock_processor.transcribe.return_value = mock_result
        
        result = transcribe_with_timestamps("test.mp3", api_key="test-key")
        
        assert len(result.words) == 1
        mock_processor.transcribe.assert_called_once()


class TestSupportedFormats:
    """Test supported format constants"""
    
    def test_supported_formats(self):
        """Verify all documented formats are supported"""
        expected = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
        assert SUPPORTED_FORMATS == expected
    
    def test_max_file_size(self):
        """Verify max file size is 25MB"""
        assert MAX_FILE_SIZE == 25 * 1024 * 1024


class TestTranscriptionSegment:
    """Test TranscriptionSegment dataclass"""
    
    def test_basic_segment(self):
        segment = TranscriptionSegment(
            id=0,
            text="Hello",
            start=0.0,
            end=1.0
        )
        assert segment.id == 0
        assert segment.text == "Hello"
        assert segment.speaker is None
    
    def test_segment_with_speaker(self):
        segment = TranscriptionSegment(
            id=1,
            text="How are you?",
            start=1.0,
            end=2.5,
            speaker="speaker_1"
        )
        assert segment.speaker == "speaker_1"


class TestStreamEvent:
    """Test StreamEvent dataclass"""
    
    def test_delta_event(self):
        event = StreamEvent(
            event_type="transcript.text.delta",
            delta="Hello",
            segment_id=0
        )
        assert event.event_type == "transcript.text.delta"
        assert event.delta == "Hello"
    
    def test_done_event(self):
        event = StreamEvent(
            event_type="transcript.text.done",
            text="Hello world"
        )
        assert event.event_type == "transcript.text.done"
        assert event.text == "Hello world"
    
    def test_segment_event(self):
        event = StreamEvent(
            event_type="transcript.text.segment",
            text="Hello",
            speaker="speaker_0",
            start=0.0,
            end=1.0
        )
        assert event.speaker == "speaker_0"


# Integration tests (require actual API key)
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
class TestIntegration:
    """Integration tests requiring actual API access"""
    
    def test_real_transcription(self):
        """Test real transcription if API key is available"""
        # This test would require an actual audio file
        # Skipping for now as it requires real audio
        pytest.skip("Requires real audio file")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
