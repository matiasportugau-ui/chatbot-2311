#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Utilities
Helper functions for audio file processing, conversion, and management
"""

import os
import tempfile
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AudioFileInfo:
    """Information about an audio file"""
    path: Path
    size_bytes: int
    size_mb: float
    format: str
    mime_type: str
    checksum: str


class AudioFileManager:
    """Manager for audio file operations"""
    
    SUPPORTED_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}
    MAX_FILE_SIZE_MB = 25
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize audio file manager
        
        Args:
            temp_dir: Directory for temporary files (defaults to system temp)
        """
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "audio_transcription"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audio file manager initialized with temp dir: {self.temp_dir}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> AudioFileInfo:
        """
        Get information about an audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioFileInfo with file details
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        file_format = file_path.suffix.lower().lstrip('.')
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = f"audio/{file_format}"
        
        # Calculate checksum
        checksum = self.calculate_checksum(file_path)
        
        return AudioFileInfo(
            path=file_path,
            size_bytes=size_bytes,
            size_mb=size_mb,
            format=file_format,
            mime_type=mime_type,
            checksum=checksum
        )
    
    def calculate_checksum(self, file_path: Union[str, Path]) -> str:
        """
        Calculate SHA256 checksum of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal checksum string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def validate_audio_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate audio file format and size
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            info = self.get_file_info(file_path)
            
            # Check format
            if info.format not in self.SUPPORTED_FORMATS:
                return False, (
                    f"Unsupported format: {info.format}. "
                    f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
                )
            
            # Check size
            if info.size_mb > self.MAX_FILE_SIZE_MB:
                return False, (
                    f"File too large: {info.size_mb:.2f}MB. "
                    f"Maximum: {self.MAX_FILE_SIZE_MB}MB"
                )
            
            return True, "Valid audio file"
        
        except FileNotFoundError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def save_audio_from_bytes(
        self,
        audio_data: bytes,
        file_format: str = "mp3",
        filename: Optional[str] = None
    ) -> Path:
        """
        Save audio data to a temporary file
        
        Args:
            audio_data: Audio file content as bytes
            file_format: File format/extension
            filename: Optional filename (generated if not provided)
            
        Returns:
            Path to saved file
        """
        if not filename:
            # Generate unique filename
            timestamp = hashlib.md5(audio_data[:1024]).hexdigest()[:8]
            filename = f"audio_{timestamp}.{file_format}"
        
        file_path = self.temp_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        logger.info(f"Saved audio file: {file_path} ({len(audio_data)} bytes)")
        return file_path
    
    def download_audio_from_url(
        self,
        url: str,
        file_format: Optional[str] = None
    ) -> Path:
        """
        Download audio from URL
        
        Args:
            url: URL to download from
            file_format: Expected file format (auto-detected if not provided)
            
        Returns:
            Path to downloaded file
        """
        import requests
        
        logger.info(f"Downloading audio from URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Determine format from URL or content-type
            if not file_format:
                content_type = response.headers.get('content-type', '')
                if 'audio/' in content_type:
                    file_format = content_type.split('/')[-1].split(';')[0]
                else:
                    # Try to get from URL
                    file_format = Path(url).suffix.lstrip('.') or 'mp3'
            
            return self.save_audio_from_bytes(response.content, file_format)
        
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """
        Clean up temporary audio files older than specified hours
        
        Args:
            older_than_hours: Delete files older than this many hours
        """
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        deleted_count = 0
        total_size = 0
        
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file():
                file_age = file_path.stat().st_mtime
                if file_age < cutoff_time:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    total_size += file_size
        
        if deleted_count > 0:
            logger.info(
                f"Cleaned up {deleted_count} temporary files "
                f"({total_size / (1024 * 1024):.2f}MB)"
            )
    
    def delete_file(self, file_path: Union[str, Path]):
        """
        Delete an audio file
        
        Args:
            file_path: Path to file to delete
        """
        file_path = Path(file_path)
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted audio file: {file_path}")
        else:
            logger.warning(f"File not found for deletion: {file_path}")


class AudioChunker:
    """Split large audio files into smaller chunks"""
    
    def __init__(self, max_chunk_size_mb: int = 24):
        """
        Initialize audio chunker
        
        Args:
            max_chunk_size_mb: Maximum chunk size in MB
        """
        self.max_chunk_size_mb = max_chunk_size_mb
    
    def needs_chunking(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file needs to be chunked
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if file is larger than max chunk size
        """
        file_path = Path(file_path)
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb > self.max_chunk_size_mb
    
    def chunk_audio_file(
        self,
        file_path: Union[str, Path],
        output_dir: Optional[Path] = None
    ) -> list[Path]:
        """
        Split audio file into chunks
        
        Note: This is a basic implementation. For production use, consider
        using audio processing libraries like pydub for proper audio splitting
        at silence points.
        
        Args:
            file_path: Path to audio file
            output_dir: Directory for output chunks
            
        Returns:
            List of paths to chunk files
        """
        file_path = Path(file_path)
        
        if not self.needs_chunking(file_path):
            return [file_path]
        
        if output_dir is None:
            output_dir = file_path.parent / f"{file_path.stem}_chunks"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chunk_size_bytes = self.max_chunk_size_mb * 1024 * 1024
        chunk_paths = []
        
        with open(file_path, 'rb') as f:
            chunk_number = 1
            
            while True:
                chunk_data = f.read(chunk_size_bytes)
                if not chunk_data:
                    break
                
                chunk_path = output_dir / f"{file_path.stem}_chunk_{chunk_number:03d}{file_path.suffix}"
                
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                chunk_paths.append(chunk_path)
                chunk_number += 1
        
        logger.info(f"Split audio into {len(chunk_paths)} chunks")
        return chunk_paths


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2:30" or "1:05:30")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def is_supported_audio_format(file_path: Union[str, Path]) -> bool:
    """
    Check if audio file format is supported
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if format is supported
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower().lstrip('.')
    return extension in AudioFileManager.SUPPORTED_FORMATS


def get_audio_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type for audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        MIME type string
    """
    file_path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if not mime_type:
        extension = file_path.suffix.lower().lstrip('.')
        mime_type = f"audio/{extension}"
    
    return mime_type


if __name__ == "__main__":
    # Example usage
    print("Audio Utilities Module")
    print("=" * 50)
    
    manager = AudioFileManager()
    print(f"✅ Audio file manager initialized")
    print(f"   Temp directory: {manager.temp_dir}")
    print(f"   Supported formats: {', '.join(manager.SUPPORTED_FORMATS)}")
    print(f"   Max file size: {manager.MAX_FILE_SIZE_MB}MB")
