#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Chunking Utility
======================

Handles splitting of large audio files for processing with OpenAI's Audio API.

The OpenAI Audio API has a 25 MB file size limit. This module provides utilities
to split larger audio files into manageable chunks while preserving context.

Features:
- Split audio files by duration or file size
- Preserve sentence boundaries when possible
- Export chunks in various formats
- Combine transcriptions from multiple chunks

Requires: pydub (pip install pydub)
Optional: ffmpeg for format conversion
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Generator
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AudioChunk:
    """Represents a chunk of audio."""
    index: int
    file_path: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int


class AudioChunker:
    """
    Split large audio files into smaller chunks for API processing.
    
    Example usage:
        >>> from audio_chunker import AudioChunker
        >>> chunker = AudioChunker()
        >>> chunks = chunker.split_by_duration("long_audio.mp3", chunk_duration_ms=10*60*1000)
        >>> for chunk in chunks:
        ...     print(f"Chunk {chunk.index}: {chunk.file_path}")
    """
    
    # Default chunk duration: 10 minutes in milliseconds
    DEFAULT_CHUNK_DURATION_MS = 10 * 60 * 1000
    
    # Maximum file size for API (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    # Overlap between chunks to preserve context (5 seconds)
    DEFAULT_OVERLAP_MS = 5 * 1000
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the AudioChunker.
        
        Args:
            output_dir: Directory for output chunks. Defaults to temp directory.
        """
        self.output_dir = output_dir or "/tmp/audio_chunks"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_audio(self, file_path: str):
        """Load audio file using pydub."""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError(
                "pydub is required for audio chunking. "
                "Install it with: pip install pydub"
            )
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        extension = path.suffix.lower().lstrip(".")
        
        # Load based on format
        if extension == "mp3":
            return AudioSegment.from_mp3(file_path)
        elif extension == "wav":
            return AudioSegment.from_wav(file_path)
        elif extension in ("mp4", "m4a"):
            return AudioSegment.from_file(file_path, format="mp4")
        elif extension == "webm":
            return AudioSegment.from_file(file_path, format="webm")
        elif extension in ("mpeg", "mpga"):
            return AudioSegment.from_file(file_path, format="mp3")
        else:
            return AudioSegment.from_file(file_path)
    
    def get_audio_info(self, file_path: str) -> dict:
        """
        Get information about an audio file.
        
        Args:
            file_path: Path to audio file.
        
        Returns:
            Dict with audio information.
        """
        audio = self._load_audio(file_path)
        path = Path(file_path)
        
        return {
            "file_path": str(path.absolute()),
            "file_size_bytes": path.stat().st_size,
            "file_size_mb": path.stat().st_size / 1024 / 1024,
            "duration_ms": len(audio),
            "duration_seconds": len(audio) / 1000,
            "duration_minutes": len(audio) / 1000 / 60,
            "channels": audio.channels,
            "sample_width": audio.sample_width,
            "frame_rate": audio.frame_rate,
            "needs_chunking": path.stat().st_size > self.MAX_FILE_SIZE,
        }
    
    def split_by_duration(
        self,
        file_path: str,
        chunk_duration_ms: int = None,
        overlap_ms: int = None,
        output_format: str = "mp3",
        preserve_file_prefix: bool = True,
    ) -> List[AudioChunk]:
        """
        Split audio file by duration.
        
        Args:
            file_path: Path to input audio file.
            chunk_duration_ms: Duration of each chunk in milliseconds.
            overlap_ms: Overlap between chunks for context preservation.
            output_format: Output format for chunks (mp3, wav, etc.).
            preserve_file_prefix: Use original filename as prefix.
        
        Returns:
            List of AudioChunk objects.
        """
        chunk_duration_ms = chunk_duration_ms or self.DEFAULT_CHUNK_DURATION_MS
        overlap_ms = overlap_ms if overlap_ms is not None else self.DEFAULT_OVERLAP_MS
        
        audio = self._load_audio(file_path)
        total_duration = len(audio)
        
        if total_duration <= chunk_duration_ms:
            logger.info("Audio is shorter than chunk duration, no splitting needed")
            return [AudioChunk(
                index=0,
                file_path=file_path,
                start_time_ms=0,
                end_time_ms=total_duration,
                duration_ms=total_duration
            )]
        
        # Calculate prefix for output files
        prefix = Path(file_path).stem if preserve_file_prefix else "chunk"
        
        chunks = []
        chunk_index = 0
        start = 0
        
        while start < total_duration:
            end = min(start + chunk_duration_ms, total_duration)
            
            # Extract chunk
            chunk_audio = audio[start:end]
            
            # Generate output path
            chunk_filename = f"{prefix}_chunk_{chunk_index:03d}.{output_format}"
            chunk_path = os.path.join(self.output_dir, chunk_filename)
            
            # Export chunk
            chunk_audio.export(chunk_path, format=output_format)
            
            chunks.append(AudioChunk(
                index=chunk_index,
                file_path=chunk_path,
                start_time_ms=start,
                end_time_ms=end,
                duration_ms=end - start
            ))
            
            logger.info(f"Created chunk {chunk_index}: {start/1000:.1f}s - {end/1000:.1f}s")
            
            # Move to next chunk with overlap
            start = end - overlap_ms
            chunk_index += 1
            
            # Avoid tiny chunks at the end
            if total_duration - start < overlap_ms:
                break
        
        logger.info(f"Split audio into {len(chunks)} chunks")
        return chunks
    
    def split_by_size(
        self,
        file_path: str,
        max_size_mb: float = 24.0,
        output_format: str = "mp3",
    ) -> List[AudioChunk]:
        """
        Split audio file to ensure each chunk is under the size limit.
        
        Uses binary search to find optimal chunk duration for the target size.
        
        Args:
            file_path: Path to input audio file.
            max_size_mb: Maximum size per chunk in MB.
            output_format: Output format for chunks.
        
        Returns:
            List of AudioChunk objects.
        """
        audio = self._load_audio(file_path)
        total_duration = len(audio)
        file_size = Path(file_path).stat().st_size
        
        if file_size <= max_size_mb * 1024 * 1024:
            logger.info("Audio is under size limit, no splitting needed")
            return [AudioChunk(
                index=0,
                file_path=file_path,
                start_time_ms=0,
                end_time_ms=total_duration,
                duration_ms=total_duration
            )]
        
        # Estimate chunk duration based on file size ratio
        size_ratio = (max_size_mb * 1024 * 1024) / file_size
        estimated_chunk_duration = int(total_duration * size_ratio * 0.9)  # 90% for safety
        
        return self.split_by_duration(
            file_path,
            chunk_duration_ms=estimated_chunk_duration,
            output_format=output_format
        )
    
    def iter_chunks(
        self,
        file_path: str,
        chunk_duration_ms: int = None,
        output_format: str = "mp3",
    ) -> Generator[AudioChunk, None, None]:
        """
        Iterate over audio chunks without loading all into memory.
        
        Args:
            file_path: Path to input audio file.
            chunk_duration_ms: Duration of each chunk.
            output_format: Output format for chunks.
        
        Yields:
            AudioChunk objects one at a time.
        """
        chunks = self.split_by_duration(
            file_path,
            chunk_duration_ms=chunk_duration_ms,
            output_format=output_format
        )
        
        for chunk in chunks:
            yield chunk
    
    def cleanup_chunks(self, chunks: List[AudioChunk]) -> None:
        """
        Remove chunk files from disk.
        
        Args:
            chunks: List of AudioChunk objects to clean up.
        """
        for chunk in chunks:
            try:
                if os.path.exists(chunk.file_path):
                    os.remove(chunk.file_path)
                    logger.debug(f"Removed chunk: {chunk.file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove chunk {chunk.file_path}: {e}")


class LongAudioTranscriber:
    """
    Transcribe long audio files by chunking and combining results.
    
    Example:
        >>> from audio_chunker import LongAudioTranscriber
        >>> transcriber = LongAudioTranscriber()
        >>> text = transcriber.transcribe_long_audio("long_meeting.mp3")
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the long audio transcriber.
        
        Args:
            api_key: OpenAI API key.
        """
        from audio_to_text import AudioToText
        self.processor = AudioToText(api_key=api_key)
        self.chunker = AudioChunker()
    
    def transcribe_long_audio(
        self,
        file_path: str,
        model: str = "gpt-4o-transcribe",
        chunk_duration_minutes: int = 10,
        language: Optional[str] = None,
        use_previous_as_prompt: bool = True,
        cleanup: bool = True,
    ) -> str:
        """
        Transcribe a long audio file by splitting into chunks.
        
        Args:
            file_path: Path to the audio file.
            model: Transcription model to use.
            chunk_duration_minutes: Duration of each chunk in minutes.
            language: Language code (optional).
            use_previous_as_prompt: Use previous transcription as prompt for context.
            cleanup: Remove chunk files after transcription.
        
        Returns:
            Combined transcription text.
        """
        info = self.chunker.get_audio_info(file_path)
        logger.info(f"Transcribing: {info['file_path']}")
        logger.info(f"Duration: {info['duration_minutes']:.1f} minutes")
        logger.info(f"Size: {info['file_size_mb']:.2f} MB")
        
        if not info["needs_chunking"]:
            result = self.processor.transcribe(file_path, model=model, language=language)
            return result.text
        
        # Split into chunks
        chunk_duration_ms = chunk_duration_minutes * 60 * 1000
        chunks = self.chunker.split_by_duration(
            file_path,
            chunk_duration_ms=chunk_duration_ms
        )
        
        transcriptions = []
        previous_text = ""
        
        try:
            for chunk in chunks:
                logger.info(f"Transcribing chunk {chunk.index + 1}/{len(chunks)}")
                
                # Use last 224 tokens of previous transcription as prompt
                prompt = None
                if use_previous_as_prompt and previous_text:
                    # Approximate: ~4 chars per token, 224 tokens = ~900 chars
                    prompt = previous_text[-900:] if len(previous_text) > 900 else previous_text
                
                result = self.processor.transcribe(
                    chunk.file_path,
                    model=model,
                    language=language,
                    prompt=prompt
                )
                
                transcriptions.append(result.text)
                previous_text = result.text
                
        finally:
            if cleanup:
                self.chunker.cleanup_chunks(chunks)
        
        # Combine transcriptions
        combined = self._combine_transcriptions(transcriptions)
        return combined
    
    def _combine_transcriptions(self, transcriptions: List[str]) -> str:
        """
        Combine transcriptions from multiple chunks.
        
        Handles overlap regions by detecting and removing duplicate text.
        
        Args:
            transcriptions: List of transcription texts.
        
        Returns:
            Combined text.
        """
        if not transcriptions:
            return ""
        
        if len(transcriptions) == 1:
            return transcriptions[0]
        
        combined = transcriptions[0]
        
        for i in range(1, len(transcriptions)):
            current = transcriptions[i]
            
            # Try to find overlap and remove duplicates
            overlap_removed = self._remove_overlap(combined, current)
            combined = overlap_removed
        
        return combined.strip()
    
    def _remove_overlap(self, text1: str, text2: str, min_overlap: int = 20) -> str:
        """
        Remove overlapping text between two transcriptions.
        
        Args:
            text1: First transcription.
            text2: Second transcription.
            min_overlap: Minimum overlap length to consider.
        
        Returns:
            Combined text with overlap removed.
        """
        # Get the end of text1
        end_words = text1.split()[-20:] if len(text1.split()) > 20 else text1.split()
        
        # Look for matching start in text2
        text2_words = text2.split()
        
        for i in range(min(len(end_words), 10)):
            search_phrase = " ".join(end_words[-(i+3):]) if i+3 <= len(end_words) else " ".join(end_words)
            
            if search_phrase in text2:
                # Find where the overlap ends in text2
                overlap_pos = text2.find(search_phrase)
                overlap_end = overlap_pos + len(search_phrase)
                
                # Return text1 + remaining text2 after overlap
                return text1 + " " + text2[overlap_end:].strip()
        
        # No overlap found, just concatenate
        return text1 + " " + text2


def split_audio(file_path: str, chunk_minutes: int = 10) -> List[str]:
    """
    Quick function to split audio into chunks.
    
    Args:
        file_path: Path to audio file.
        chunk_minutes: Duration of each chunk in minutes.
    
    Returns:
        List of chunk file paths.
    """
    chunker = AudioChunker()
    chunks = chunker.split_by_duration(
        file_path,
        chunk_duration_ms=chunk_minutes * 60 * 1000
    )
    return [c.file_path for c in chunks]


def transcribe_long_audio(file_path: str, **kwargs) -> str:
    """
    Quick function to transcribe long audio.
    
    Args:
        file_path: Path to audio file.
        **kwargs: Additional arguments for LongAudioTranscriber.
    
    Returns:
        Transcribed text.
    """
    transcriber = LongAudioTranscriber()
    return transcriber.transcribe_long_audio(file_path, **kwargs)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_chunker.py <audio_file> [chunk_minutes]")
        print("\nExample:")
        print("  python audio_chunker.py long_recording.mp3 10")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    chunk_minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    try:
        chunker = AudioChunker()
        
        # Get audio info
        info = chunker.get_audio_info(audio_file)
        print(f"\nAudio Information:")
        print(f"  File: {info['file_path']}")
        print(f"  Size: {info['file_size_mb']:.2f} MB")
        print(f"  Duration: {info['duration_minutes']:.1f} minutes")
        print(f"  Needs chunking: {info['needs_chunking']}")
        
        if info['needs_chunking']:
            print(f"\nSplitting into {chunk_minutes}-minute chunks...")
            chunks = chunker.split_by_duration(
                audio_file,
                chunk_duration_ms=chunk_minutes * 60 * 1000
            )
            print(f"\nCreated {len(chunks)} chunks:")
            for chunk in chunks:
                print(f"  Chunk {chunk.index}: {chunk.file_path}")
                print(f"    Time: {chunk.start_time_ms/1000:.1f}s - {chunk.end_time_ms/1000:.1f}s")
        else:
            print("\nNo chunking needed - file is under 25 MB")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
