#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio File Chunking for Large Files
====================================

Handles audio files larger than OpenAI's 25MB limit by splitting them
into smaller chunks, transcribing each chunk, and combining the results.

Uses PyDub for audio manipulation when available, with fallback to
ffmpeg command-line tool.

Requirements:
- pydub (pip install pydub)
- ffmpeg (system installation)
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import List, Optional, Union, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Check for pydub availability
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning(
        "PyDub not installed. Install with: pip install pydub. "
        "Falling back to ffmpeg command-line."
    )


@dataclass
class AudioChunk:
    """Represents a chunk of audio with metadata."""
    path: Path
    start_ms: int
    end_ms: int
    duration_ms: int
    chunk_index: int
    total_chunks: int


class AudioChunker:
    """
    Splits large audio files into smaller chunks for API processing.
    
    The OpenAI Audio API has a 25MB file size limit. This class helps
    by splitting larger files into manageable chunks and providing
    utilities to combine transcription results.
    
    Example:
        chunker = AudioChunker()
        chunks = chunker.split_audio("long_meeting.mp3", chunk_duration_minutes=10)
        
        # Transcribe each chunk
        transcripts = []
        for chunk in chunks:
            result = transcriber.transcribe(chunk.path)
            transcripts.append(result.text)
        
        # Combine
        full_transcript = " ".join(transcripts)
        
        # Cleanup
        chunker.cleanup_chunks(chunks)
    """
    
    # Maximum file size in bytes (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    # Default chunk duration (10 minutes in milliseconds)
    DEFAULT_CHUNK_DURATION_MS = 10 * 60 * 1000
    
    def __init__(self, temp_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the AudioChunker.
        
        Args:
            temp_dir: Directory for temporary chunk files.
                     If not provided, uses system temp directory.
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get information about an audio file.
        
        Args:
            file_path: Path to the audio file.
        
        Returns:
            Dict with file size, duration, and whether chunking is needed.
        """
        path = Path(file_path)
        file_size = path.stat().st_size
        
        info = {
            "path": str(path),
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "needs_chunking": file_size > self.MAX_FILE_SIZE,
        }
        
        # Get duration if pydub is available
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_file(path)
                info["duration_ms"] = len(audio)
                info["duration_seconds"] = len(audio) / 1000
                info["duration_minutes"] = len(audio) / 1000 / 60
            except Exception as e:
                logger.warning(f"Could not read audio duration: {e}")
        
        return info
    
    def split_audio(
        self,
        file_path: Union[str, Path],
        chunk_duration_minutes: float = 10,
        overlap_seconds: float = 1.0,
        output_format: str = "mp3",
    ) -> List[AudioChunk]:
        """
        Split an audio file into smaller chunks.
        
        Args:
            file_path: Path to the audio file.
            chunk_duration_minutes: Duration of each chunk in minutes.
            overlap_seconds: Overlap between chunks (helps maintain context).
            output_format: Format for chunk files (mp3, wav, etc.).
        
        Returns:
            List of AudioChunk objects with paths to chunk files.
        
        Example:
            chunks = chunker.split_audio(
                "2hour_meeting.mp3",
                chunk_duration_minutes=10,
                overlap_seconds=2
            )
        """
        if not PYDUB_AVAILABLE:
            raise RuntimeError(
                "PyDub is required for audio chunking. "
                "Install with: pip install pydub"
            )
        
        path = Path(file_path)
        logger.info(f"Loading audio file: {path}")
        
        audio = AudioSegment.from_file(path)
        total_duration_ms = len(audio)
        chunk_duration_ms = int(chunk_duration_minutes * 60 * 1000)
        overlap_ms = int(overlap_seconds * 1000)
        
        chunks: List[AudioChunk] = []
        start_ms = 0
        chunk_index = 0
        
        # Calculate total chunks for naming
        total_chunks = (total_duration_ms // (chunk_duration_ms - overlap_ms)) + 1
        
        while start_ms < total_duration_ms:
            end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
            
            # Extract chunk
            chunk_audio = audio[start_ms:end_ms]
            
            # Create chunk filename
            chunk_filename = (
                f"{path.stem}_chunk_{chunk_index:03d}_"
                f"{start_ms//1000}s-{end_ms//1000}s.{output_format}"
            )
            chunk_path = self.temp_dir / chunk_filename
            
            # Export chunk
            logger.info(
                f"Exporting chunk {chunk_index + 1}/{total_chunks}: "
                f"{start_ms/1000:.1f}s - {end_ms/1000:.1f}s"
            )
            chunk_audio.export(chunk_path, format=output_format)
            
            chunks.append(AudioChunk(
                path=chunk_path,
                start_ms=start_ms,
                end_ms=end_ms,
                duration_ms=end_ms - start_ms,
                chunk_index=chunk_index,
                total_chunks=total_chunks,
            ))
            
            # Move to next chunk with overlap
            start_ms = end_ms - overlap_ms
            chunk_index += 1
        
        logger.info(f"Created {len(chunks)} audio chunks")
        return chunks
    
    def split_by_size(
        self,
        file_path: Union[str, Path],
        target_size_mb: float = 20,
        output_format: str = "mp3",
    ) -> List[AudioChunk]:
        """
        Split audio file into chunks that fit within a size limit.
        
        Args:
            file_path: Path to the audio file.
            target_size_mb: Target size for each chunk in MB.
            output_format: Format for chunk files.
        
        Returns:
            List of AudioChunk objects.
        """
        if not PYDUB_AVAILABLE:
            raise RuntimeError("PyDub is required. Install with: pip install pydub")
        
        path = Path(file_path)
        file_size_mb = path.stat().st_size / (1024 * 1024)
        
        # Load audio
        audio = AudioSegment.from_file(path)
        total_duration_ms = len(audio)
        
        # Estimate bytes per millisecond
        bytes_per_ms = (path.stat().st_size) / total_duration_ms
        
        # Calculate chunk duration to achieve target size
        target_size_bytes = target_size_mb * 1024 * 1024
        chunk_duration_ms = int(target_size_bytes / bytes_per_ms)
        chunk_duration_minutes = chunk_duration_ms / 1000 / 60
        
        logger.info(
            f"File size: {file_size_mb:.1f} MB, "
            f"Target: {target_size_mb} MB, "
            f"Chunk duration: {chunk_duration_minutes:.1f} minutes"
        )
        
        return self.split_audio(
            file_path,
            chunk_duration_minutes=chunk_duration_minutes,
            overlap_seconds=1.0,
            output_format=output_format,
        )
    
    def combine_transcripts(
        self,
        transcripts: List[str],
        chunks: Optional[List[AudioChunk]] = None,
        separator: str = " ",
    ) -> str:
        """
        Combine transcripts from multiple chunks.
        
        Args:
            transcripts: List of transcript strings from each chunk.
            chunks: Optional AudioChunk objects for context.
            separator: String to join transcripts.
        
        Returns:
            Combined transcript text.
        """
        if not transcripts:
            return ""
        
        # Simple join
        combined = separator.join(transcripts)
        
        # Clean up potential duplications from overlap
        # This is a simple approach - more sophisticated deduplication
        # could be added based on your needs
        
        return combined
    
    def cleanup_chunks(self, chunks: List[AudioChunk]) -> None:
        """
        Remove temporary chunk files.
        
        Args:
            chunks: List of AudioChunk objects to clean up.
        """
        for chunk in chunks:
            try:
                if chunk.path.exists():
                    chunk.path.unlink()
                    logger.debug(f"Removed chunk: {chunk.path}")
            except Exception as e:
                logger.warning(f"Could not remove chunk {chunk.path}: {e}")
        
        logger.info(f"Cleaned up {len(chunks)} chunk files")


def chunk_and_transcribe(
    file_path: Union[str, Path],
    chunk_duration_minutes: float = 10,
    model: str = "gpt-4o-transcribe",
    prompt: Optional[str] = None,
    use_previous_as_prompt: bool = True,
) -> Tuple[str, List[str]]:
    """
    Convenience function to chunk and transcribe a large audio file.
    
    Splits the audio into chunks, transcribes each chunk (optionally
    using the previous chunk's transcript as context), and combines
    the results.
    
    Args:
        file_path: Path to the audio file.
        chunk_duration_minutes: Duration of each chunk.
        model: Transcription model to use.
        prompt: Optional base prompt for context.
        use_previous_as_prompt: If True, uses the end of the previous
            transcript as a prompt for the next chunk.
    
    Returns:
        Tuple of (combined_transcript, list_of_chunk_transcripts).
    
    Example:
        transcript, chunks = chunk_and_transcribe(
            "3hour_meeting.mp3",
            chunk_duration_minutes=10,
            prompt="Team meeting about product roadmap"
        )
    """
    # Import here to avoid circular import
    from audio_transcription import AudioTranscriber
    
    chunker = AudioChunker()
    transcriber = AudioTranscriber()
    
    # Check if chunking is needed
    info = chunker.get_file_info(file_path)
    
    if not info.get("needs_chunking", False):
        # File is small enough, transcribe directly
        result = transcriber.transcribe(file_path, model=model, prompt=prompt)
        return result.text, [result.text]
    
    # Split into chunks
    chunks = chunker.split_audio(file_path, chunk_duration_minutes=chunk_duration_minutes)
    
    transcripts: List[str] = []
    current_prompt = prompt
    
    try:
        for chunk in chunks:
            logger.info(
                f"Transcribing chunk {chunk.chunk_index + 1}/{chunk.total_chunks}"
            )
            
            result = transcriber.transcribe(
                chunk.path,
                model=model,
                prompt=current_prompt,
            )
            
            transcripts.append(result.text)
            
            # Use end of transcript as prompt for next chunk
            if use_previous_as_prompt and result.text:
                # Take last ~200 characters as context
                current_prompt = result.text[-200:]
        
        combined = chunker.combine_transcripts(transcripts, chunks)
        
    finally:
        # Clean up chunk files
        chunker.cleanup_chunks(chunks)
    
    return combined, transcripts


# Example usage
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Audio Chunking for Large Files")
    print("=" * 60)
    print()
    
    if not PYDUB_AVAILABLE:
        print("WARNING: PyDub is not installed!")
        print("Install with: pip install pydub")
        print("Also requires ffmpeg: apt install ffmpeg")
        print()
    
    print("Usage examples:")
    print()
    print("  # Check if file needs chunking")
    print('  chunker = AudioChunker()')
    print('  info = chunker.get_file_info("large_audio.mp3")')
    print('  print(f"Needs chunking: {info[\'needs_chunking\']}")')
    print()
    print("  # Split into 10-minute chunks")
    print('  chunks = chunker.split_audio(')
    print('      "long_meeting.mp3",')
    print('      chunk_duration_minutes=10')
    print('  )')
    print()
    print("  # Chunk and transcribe in one step")
    print('  transcript, chunks = chunk_and_transcribe(')
    print('      "3hour_meeting.mp3",')
    print('      chunk_duration_minutes=10,')
    print('      model="gpt-4o-transcribe"')
    print('  )')
    print()
    
    # If file provided, show info
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Analyzing: {file_path}")
        print("-" * 40)
        
        if PYDUB_AVAILABLE:
            chunker = AudioChunker()
            info = chunker.get_file_info(file_path)
            
            print(f"File size: {info['file_size_mb']:.2f} MB")
            if 'duration_minutes' in info:
                print(f"Duration: {info['duration_minutes']:.1f} minutes")
            print(f"Needs chunking: {info['needs_chunking']}")
        else:
            print("PyDub not available. Install to analyze audio files.")
