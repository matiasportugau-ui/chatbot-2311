#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Audio Transcription Service
"""

import os
import sys
from pathlib import Path
import tempfile
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat,
    TranscriptionResult,
    create_audio_transcription_service
)
from utils.audio_utils import AudioFileManager, AudioFileInfo


class TestAudioTranscriptionService:
    """Test audio transcription service"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        return AudioTranscriptionService(api_key=api_key)
    
    @pytest.fixture
    def sample_audio_path(self):
        """Create a sample audio file for testing"""
        # Note: In real tests, you would use an actual audio file
        # This is a placeholder
        audio_path = Path(tempfile.gettempdir()) / "test_audio.mp3"
        if not audio_path.exists():
            pytest.skip("Sample audio file not available")
        return audio_path
    
    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service is not None
        assert service.client is not None
        assert service.SUPPORTED_FORMATS == {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}
        assert service.MAX_FILE_SIZE_MB == 25
    
    def test_validate_audio_file_format(self, service):
        """Test audio file format validation"""
        # Create temporary test files
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'test')
            valid_file = Path(f.name)
        
        try:
            assert service.validate_audio_file(valid_file)
        finally:
            valid_file.unlink()
    
    def test_unsupported_format_raises_error(self, service):
        """Test that unsupported format raises error"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'test')
            invalid_file = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Unsupported audio format"):
                service.validate_audio_file(invalid_file)
        finally:
            invalid_file.unlink()
    
    def test_file_not_found_raises_error(self, service):
        """Test that non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            service.validate_audio_file("nonexistent.mp3")
    
    def test_transcription_config_defaults(self):
        """Test default transcription configuration"""
        config = TranscriptionConfig()
        assert config.model == TranscriptionModel.GPT4O_TRANSCRIBE
        assert config.response_format == ResponseFormat.JSON
        assert config.temperature == 0.0
        assert config.stream is False
    
    def test_transcription_config_custom(self):
        """Test custom transcription configuration"""
        config = TranscriptionConfig(
            model=TranscriptionModel.WHISPER_1,
            response_format=ResponseFormat.TEXT,
            language="es",
            prompt="Transcribe en español",
            temperature=0.2
        )
        assert config.model == TranscriptionModel.WHISPER_1
        assert config.response_format == ResponseFormat.TEXT
        assert config.language == "es"
        assert config.prompt == "Transcribe en español"
        assert config.temperature == 0.2
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_transcribe_audio(self, service, sample_audio_path):
        """Test audio transcription (requires real audio file)"""
        config = TranscriptionConfig(
            model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
            response_format=ResponseFormat.TEXT
        )
        
        result = service.transcribe(sample_audio_path, config)
        
        assert isinstance(result, TranscriptionResult)
        assert result.text is not None
        assert len(result.text) > 0
        assert result.model == TranscriptionModel.GPT4O_MINI_TRANSCRIBE.value


class TestAudioFileManager:
    """Test audio file manager"""
    
    @pytest.fixture
    def manager(self):
        """Create manager instance"""
        return AudioFileManager()
    
    def test_manager_initialization(self, manager):
        """Test manager initialization"""
        assert manager is not None
        assert manager.temp_dir.exists()
        assert manager.SUPPORTED_FORMATS == {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}
    
    def test_get_file_info(self, manager):
        """Test getting file information"""
        # Create test file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'test audio data')
            test_file = Path(f.name)
        
        try:
            info = manager.get_file_info(test_file)
            
            assert isinstance(info, AudioFileInfo)
            assert info.path == test_file
            assert info.size_bytes > 0
            assert info.size_mb > 0
            assert info.format == 'mp3'
            assert 'audio' in info.mime_type.lower()
            assert len(info.checksum) == 64  # SHA256 hex length
        finally:
            test_file.unlink()
    
    def test_calculate_checksum(self, manager):
        """Test checksum calculation"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b'test data')
            test_file = Path(f.name)
        
        try:
            checksum1 = manager.calculate_checksum(test_file)
            checksum2 = manager.calculate_checksum(test_file)
            
            assert checksum1 == checksum2
            assert len(checksum1) == 64
        finally:
            test_file.unlink()
    
    def test_validate_audio_file(self, manager):
        """Test audio file validation"""
        # Valid file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b'a' * 1000)  # Small file
            valid_file = Path(f.name)
        
        try:
            is_valid, message = manager.validate_audio_file(valid_file)
            assert is_valid
            assert "Valid" in message
        finally:
            valid_file.unlink()
    
    def test_validate_unsupported_format(self, manager):
        """Test validation of unsupported format"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'test')
            invalid_file = Path(f.name)
        
        try:
            is_valid, message = manager.validate_audio_file(invalid_file)
            assert not is_valid
            assert "Unsupported" in message
        finally:
            invalid_file.unlink()
    
    def test_save_audio_from_bytes(self, manager):
        """Test saving audio from bytes"""
        audio_data = b'test audio data'
        
        saved_path = manager.save_audio_from_bytes(audio_data, 'mp3')
        
        try:
            assert saved_path.exists()
            assert saved_path.suffix == '.mp3'
            assert saved_path.read_bytes() == audio_data
        finally:
            if saved_path.exists():
                saved_path.unlink()
    
    def test_cleanup_temp_files(self, manager):
        """Test cleanup of temporary files"""
        # Create some test files
        test_files = []
        for i in range(3):
            path = manager.temp_dir / f"test_{i}.mp3"
            path.write_bytes(b'test')
            test_files.append(path)
        
        # Cleanup (use 0 hours to delete all)
        manager.cleanup_temp_files(older_than_hours=0)
        
        # Files should be deleted
        for path in test_files:
            assert not path.exists()


class TestFactoryFunctions:
    """Test factory functions"""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_create_audio_transcription_service(self):
        """Test service factory function"""
        service = create_audio_transcription_service()
        
        assert isinstance(service, AudioTranscriptionService)
        assert service.client is not None


if __name__ == "__main__":
    # Run tests
    print("Running Audio Transcription Tests")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Some tests will be skipped.")
    
    # Run pytest
    pytest.main([__file__, "-v", "-s"])
