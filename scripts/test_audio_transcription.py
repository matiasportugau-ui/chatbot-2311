#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Audio Transcription Module
====================================

Unit tests for the audio transcription functionality.

Run with: pytest test_audio_transcription.py -v
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audio_transcription import (
    AudioTranscriber,
    TranscriptionResult,
    TranscriptionSegment,
    transcribe_file,
    translate_file,
)


class TestAudioTranscriber:
    """Tests for AudioTranscriber class."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        transcriber = AudioTranscriber(api_key="test-key")
        assert transcriber.client is not None
    
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            transcriber = AudioTranscriber()
            assert transcriber.client is not None
    
    def test_validate_file_not_found(self):
        """Test validation with non-existent file."""
        transcriber = AudioTranscriber(api_key="test-key")
        with pytest.raises(FileNotFoundError):
            transcriber._validate_file("/nonexistent/file.mp3")
    
    def test_validate_file_unsupported_format(self):
        """Test validation with unsupported format."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not audio")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported format"):
                transcriber._validate_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_supported_formats(self):
        """Test validation accepts all supported formats."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        for fmt in ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]:
            with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as f:
                f.write(b"fake audio data")
                temp_path = f.name
            
            try:
                result = transcriber._validate_file(temp_path)
                assert result == Path(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_file_to_data_url(self):
        """Test data URL conversion."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"test audio data")
            temp_path = f.name
        
        try:
            data_url = transcriber._file_to_data_url(temp_path)
            assert data_url.startswith("data:audio/wav;base64,")
            assert "dGVzdCBhdWRpbyBkYXRh" in data_url  # base64 of "test audio data"
        finally:
            os.unlink(temp_path)
    
    def test_parse_response_text(self):
        """Test parsing text response."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        mock_response = Mock(spec=["text"])
        mock_response.text = "Hello, world!"
        
        result = transcriber._parse_response(mock_response, "gpt-4o-transcribe")
        
        assert result.text == "Hello, world!"
        assert result.model == "gpt-4o-transcribe"
    
    def test_parse_response_with_segments(self):
        """Test parsing response with segments."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        mock_segment = Mock(spec=["text", "start", "end", "speaker"])
        mock_segment.text = "Segment text"
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_segment.speaker = "Speaker1"
        
        mock_response = Mock(spec=["text", "segments"])
        mock_response.text = "Full text"
        mock_response.segments = [mock_segment]
        
        result = transcriber._parse_response(mock_response, "gpt-4o-transcribe-diarize")
        
        assert result.text == "Full text"
        assert len(result.segments) == 1
        assert result.segments[0].text == "Segment text"
        assert result.segments[0].speaker == "Speaker1"
    
    def test_parse_response_with_words(self):
        """Test parsing response with word timestamps."""
        transcriber = AudioTranscriber(api_key="test-key")
        
        mock_word = Mock(spec=["word", "start", "end"])
        mock_word.word = "Hello"
        mock_word.start = 0.0
        mock_word.end = 0.5
        
        mock_response = Mock(spec=["text", "words"])
        mock_response.text = "Hello"
        mock_response.words = [mock_word]
        
        result = transcriber._parse_response(mock_response, "whisper-1")
        
        assert result.words is not None
        assert len(result.words) == 1
        assert result.words[0]["word"] == "Hello"
    
    @patch("audio_transcription.OpenAI")
    def test_transcribe_basic(self, mock_openai):
        """Test basic transcription call."""
        mock_client = Mock()
        mock_response = Mock(spec=["text"])
        mock_response.text = "Transcribed text"
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake audio")
            temp_path = f.name
        
        try:
            result = transcriber.transcribe(temp_path)
            
            assert result.text == "Transcribed text"
            mock_client.audio.transcriptions.create.assert_called_once()
        finally:
            os.unlink(temp_path)
    
    @patch("audio_transcription.OpenAI")
    def test_transcribe_with_prompt(self, mock_openai):
        """Test transcription with prompt."""
        mock_client = Mock()
        mock_response = Mock(spec=["text"])
        mock_response.text = "Transcribed text"
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake audio")
            temp_path = f.name
        
        try:
            result = transcriber.transcribe(
                temp_path,
                prompt="Technical meeting about AI"
            )
            
            call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
            assert call_kwargs["prompt"] == "Technical meeting about AI"
        finally:
            os.unlink(temp_path)
    
    @patch("audio_transcription.OpenAI")
    def test_translate_basic(self, mock_openai):
        """Test basic translation call."""
        mock_client = Mock()
        mock_response = Mock(spec=["text"])
        mock_response.text = "English translation"
        mock_client.audio.translations.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake audio")
            temp_path = f.name
        
        try:
            result = transcriber.translate(temp_path)
            
            assert result.text == "English translation"
            mock_client.audio.translations.create.assert_called_once()
            
            call_kwargs = mock_client.audio.translations.create.call_args[1]
            assert call_kwargs["model"] == "whisper-1"
        finally:
            os.unlink(temp_path)
    
    @patch("audio_transcription.OpenAI")
    def test_transcribe_stream_whisper_not_supported(self, mock_openai):
        """Test that streaming raises error for whisper-1."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"fake audio")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Streaming is not supported"):
                list(transcriber.transcribe_stream(temp_path, model="whisper-1"))
        finally:
            os.unlink(temp_path)


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""
    
    def test_create_empty_result(self):
        """Test creating empty result."""
        result = TranscriptionResult(text="")
        
        assert result.text == ""
        assert result.segments == []
        assert result.words is None
        assert result.language is None
    
    def test_create_full_result(self):
        """Test creating result with all fields."""
        segment = TranscriptionSegment(
            text="Hello",
            start=0.0,
            end=1.0,
            speaker="Speaker1"
        )
        
        result = TranscriptionResult(
            text="Hello world",
            segments=[segment],
            words=[{"word": "Hello", "start": 0.0, "end": 0.5}],
            language="en",
            duration=1.5,
            model="gpt-4o-transcribe"
        )
        
        assert result.text == "Hello world"
        assert len(result.segments) == 1
        assert result.segments[0].speaker == "Speaker1"
        assert result.language == "en"
        assert result.duration == 1.5


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    @patch("audio_transcription.AudioTranscriber")
    def test_transcribe_file(self, mock_transcriber_class):
        """Test transcribe_file convenience function."""
        mock_transcriber = Mock()
        mock_result = Mock()
        mock_result.text = "Transcribed"
        mock_transcriber.transcribe.return_value = mock_result
        mock_transcriber_class.return_value = mock_transcriber
        
        result = transcribe_file("test.mp3")
        
        assert result == "Transcribed"
        mock_transcriber.transcribe.assert_called_once()
    
    @patch("audio_transcription.AudioTranscriber")
    def test_translate_file(self, mock_transcriber_class):
        """Test translate_file convenience function."""
        mock_transcriber = Mock()
        mock_result = Mock()
        mock_result.text = "Translated"
        mock_transcriber.translate.return_value = mock_result
        mock_transcriber_class.return_value = mock_transcriber
        
        result = translate_file("test.mp3")
        
        assert result == "Translated"
        mock_transcriber.translate.assert_called_once()


class TestAudioChunker:
    """Tests for AudioChunker class (when pydub is available)."""
    
    def test_get_file_info(self):
        """Test getting file info."""
        # Create a test file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            # Write some data to test file size
            f.write(b"x" * 1000)
            temp_path = f.name
        
        try:
            from audio_chunking import AudioChunker
            chunker = AudioChunker()
            info = chunker.get_file_info(temp_path)
            
            assert info["file_size_bytes"] == 1000
            assert info["file_size_mb"] == 1000 / (1024 * 1024)
            assert info["needs_chunking"] is False
        except ImportError:
            pytest.skip("audio_chunking module not available")
        finally:
            os.unlink(temp_path)
    
    def test_combine_transcripts(self):
        """Test combining transcripts."""
        try:
            from audio_chunking import AudioChunker
            chunker = AudioChunker()
            
            transcripts = [
                "Hello, this is the first part.",
                "This is the second part.",
                "And this is the end."
            ]
            
            combined = chunker.combine_transcripts(transcripts)
            
            assert "first part" in combined
            assert "second part" in combined
            assert "the end" in combined
        except ImportError:
            pytest.skip("audio_chunking module not available")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
