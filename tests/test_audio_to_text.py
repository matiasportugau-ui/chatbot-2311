#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for audio_to_text module
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add workspace root to path
import sys
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from utils.audio_to_text import (
    AudioToTextProcessor,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    create_correction_prompt,
)


class TestAudioToTextProcessor(unittest.TestCase):
    """Test cases for AudioToTextProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        with patch.dict(os.environ, {"OPENAI_API_KEY": self.api_key}):
            self.processor = AudioToTextProcessor()
    
    def test_initialization_with_env_var(self):
        """Test initialization with environment variable"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            processor = AudioToTextProcessor()
            self.assertIsNotNone(processor.client)
    
    def test_initialization_with_api_key(self):
        """Test initialization with explicit API key"""
        processor = AudioToTextProcessor(api_key="explicit-key")
        self.assertIsNotNone(processor.client)
    
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AudioToTextProcessor()
    
    def test_validate_audio_file_not_found(self):
        """Test validation with non-existent file"""
        is_valid, error = self.processor.validate_audio_file("nonexistent.mp3")
        self.assertFalse(is_valid)
        self.assertIn("not found", error.lower())
    
    def test_validate_audio_file_unsupported_format(self):
        """Test validation with unsupported format"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            temp_path = f.name
        
        try:
            is_valid, error = self.processor.validate_audio_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("unsupported", error.lower())
        finally:
            os.unlink(temp_path)
    
    def test_validate_audio_file_too_large(self):
        """Test validation with file too large"""
        # Create a file larger than 25 MB
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            # Write 26 MB of data
            f.write(b"0" * (26 * 1024 * 1024))
            temp_path = f.name
        
        try:
            is_valid, error = self.processor.validate_audio_file(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("too large", error.lower())
        finally:
            os.unlink(temp_path)
    
    def test_validate_audio_file_valid(self):
        """Test validation with valid file"""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"test audio data")
            temp_path = f.name
        
        try:
            is_valid, error = self.processor.validate_audio_file(temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
        finally:
            os.unlink(temp_path)
    
    @patch('utils.audio_to_text.OpenAI')
    def test_transcribe_basic(self, mock_openai_class):
        """Test basic transcription"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock transcription response
        mock_response = MagicMock()
        mock_response.text = "This is a test transcription"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        processor = AudioToTextProcessor(api_key="test-key")
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"test audio")
            temp_path = f.name
        
        try:
            config = TranscriptionConfig(
                model=TranscriptionModel.GPT_4O_TRANSCRIBE,
                response_format=ResponseFormat.TEXT,
            )
            result = processor.transcribe(temp_path, config)
            self.assertEqual(result.text, "This is a test transcription")
        finally:
            os.unlink(temp_path)
    
    def test_to_data_url(self):
        """Test converting audio file to data URL"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"test audio data")
            temp_path = f.name
        
        try:
            data_url = self.processor.to_data_url(temp_path)
            self.assertTrue(data_url.startswith("data:audio/wav;base64,"))
            self.assertIn("dGVzdCBhdWRpbyBkYXRh", data_url)  # base64 of "test audio data"
        finally:
            os.unlink(temp_path)
    
    def test_create_correction_prompt(self):
        """Test creating correction prompt"""
        prompt = create_correction_prompt(
            company_name="TestCompany",
            product_names=["Product1", "Product2"],
            additional_instructions="Test instructions",
        )
        
        self.assertIn("TestCompany", prompt)
        self.assertIn("Product1", prompt)
        self.assertIn("Product2", prompt)
        self.assertIn("Test instructions", prompt)


class TestTranscriptionConfig(unittest.TestCase):
    """Test cases for TranscriptionConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = TranscriptionConfig()
        self.assertEqual(config.model, TranscriptionModel.GPT_4O_TRANSCRIBE)
        self.assertEqual(config.response_format, ResponseFormat.JSON)
        self.assertIsNone(config.language)
        self.assertIsNone(config.prompt)
        self.assertEqual(config.temperature, 0.0)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = TranscriptionConfig(
            model=TranscriptionModel.WHISPER_1,
            response_format=ResponseFormat.TEXT,
            language="es",
            prompt="Test prompt",
            temperature=0.5,
        )
        
        self.assertEqual(config.model, TranscriptionModel.WHISPER_1)
        self.assertEqual(config.response_format, ResponseFormat.TEXT)
        self.assertEqual(config.language, "es")
        self.assertEqual(config.prompt, "Test prompt")
        self.assertEqual(config.temperature, 0.5)


class TestEnums(unittest.TestCase):
    """Test enum classes"""
    
    def test_transcription_model_enum(self):
        """Test TranscriptionModel enum"""
        self.assertEqual(TranscriptionModel.WHISPER_1.value, "whisper-1")
        self.assertEqual(TranscriptionModel.GPT_4O_TRANSCRIBE.value, "gpt-4o-transcribe")
    
    def test_response_format_enum(self):
        """Test ResponseFormat enum"""
        self.assertEqual(ResponseFormat.TEXT.value, "text")
        self.assertEqual(ResponseFormat.JSON.value, "json")
    
    def test_timestamp_granularity_enum(self):
        """Test TimestampGranularity enum"""
        self.assertEqual(TimestampGranularity.WORD.value, "word")
        self.assertEqual(TimestampGranularity.SEGMENT.value, "segment")


if __name__ == "__main__":
    unittest.main()
