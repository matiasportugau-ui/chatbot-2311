#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speech-to-Text Processing Module
Implements OpenAI Audio API for transcriptions and translations

Supports:
- Basic transcriptions
- Translations
- Speaker diarization
- Timestamps (word and segment level)
- Streaming transcriptions
- Prompting for better accuracy
- Post-processing with GPT-4
"""

import os
import base64
import json
from typing import Optional, List, Dict, Any, Union, Iterator
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    from openai import OpenAI
    from openai.types.audio import Transcription
except ImportError:
    raise ImportError("openai package is required. Install with: pip install openai>=1.0.0")


class TranscriptionModel(str, Enum):
    """Available transcription models"""
    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Available response formats"""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"


class TimestampGranularity(str, Enum):
    """Timestamp granularity options"""
    WORD = "word"
    SEGMENT = "segment"


@dataclass
class TranscriptionConfig:
    """Configuration for transcription requests"""
    model: TranscriptionModel = TranscriptionModel.GPT_4O_TRANSCRIBE
    response_format: ResponseFormat = ResponseFormat.JSON
    language: Optional[str] = None
    prompt: Optional[str] = None
    temperature: float = 0.0
    timestamp_granularities: Optional[List[TimestampGranularity]] = None
    chunking_strategy: Optional[str] = None  # "auto" or VAD config
    known_speaker_names: Optional[List[str]] = None
    known_speaker_references: Optional[List[str]] = None
    stream: bool = False
    include_logprobs: bool = False


@dataclass
class TranscriptionResult:
    """Result of a transcription"""
    text: str
    segments: Optional[List[Dict[str, Any]]] = None
    words: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    duration: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None


class AudioToTextProcessor:
    """Main class for processing audio to text using OpenAI API"""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
    
    # Maximum file size (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Audio to Text processor
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        self.client = OpenAI(api_key=api_key)
    
    def validate_audio_file(self, file_path: Union[str, Path]) -> tuple:
        """
        Validate that the audio file is supported
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {path.suffix}. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
        
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large: {file_size / 1024 / 1024:.2f} MB. Maximum: {self.MAX_FILE_SIZE / 1024 / 1024} MB"
        
        return True, None
    
    def transcribe(
        self,
        audio_file: Union[str, Path],
        config: Optional[TranscriptionConfig] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file
            config: Transcription configuration
            
        Returns:
            TranscriptionResult object
        """
        config = config or TranscriptionConfig()
        
        # Validate file
        is_valid, error = self.validate_audio_file(audio_file)
        if not is_valid:
            raise ValueError(error)
        
        # Prepare request parameters
        params = {
            "model": config.model.value,
            "file": open(audio_file, "rb"),
        }
        
        if config.response_format:
            params["response_format"] = config.response_format.value
        
        if config.language:
            params["language"] = config.language
        
        if config.prompt:
            params["prompt"] = config.prompt
        
        if config.temperature is not None:
            params["temperature"] = config.temperature
        
        if config.timestamp_granularities:
            params["timestamp_granularities"] = [g.value for g in config.timestamp_granularities]
        
        if config.chunking_strategy:
            params["chunking_strategy"] = config.chunking_strategy
        
        if config.stream:
            params["stream"] = True
        
        include_params = []
        if config.include_logprobs:
            include_params.append("logprobs")
        if include_params:
            params["include"] = include_params
        
        # Handle speaker diarization
        extra_body = {}
        if config.known_speaker_names and config.known_speaker_references:
            extra_body["known_speaker_names"] = config.known_speaker_names
            extra_body["known_speaker_references"] = config.known_speaker_references
            params["extra_body"] = extra_body
        
        try:
            # Make API call
            response = self.client.audio.transcriptions.create(**params)
            
            # Parse response
            if isinstance(response, str):
                # Text format
                return TranscriptionResult(text=response)
            elif hasattr(response, 'text'):
                # JSON format
                result = TranscriptionResult(text=response.text)
                
                # Extract additional fields if available
                if hasattr(response, 'segments'):
                    result.segments = [dict(seg) for seg in response.segments]
                
                if hasattr(response, 'words'):
                    result.words = [dict(word) for word in response.words]
                
                if hasattr(response, 'language'):
                    result.language = response.language
                
                if hasattr(response, 'duration'):
                    result.duration = response.duration
                
                result.raw_response = response.model_dump() if hasattr(response, 'model_dump') else str(response)
                
                return result
            else:
                return TranscriptionResult(text=str(response))
        
        finally:
            # Close file if it was opened
            if 'file' in params and hasattr(params['file'], 'close'):
                params['file'].close()
    
    def transcribe_stream(
        self,
        audio_file: Union[str, Path],
        config: Optional[TranscriptionConfig] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream transcription results as they become available
        
        Args:
            audio_file: Path to audio file
            config: Transcription configuration (stream will be set to True automatically)
            
        Yields:
            Transcription events as dictionaries
        """
        config = config or TranscriptionConfig()
        config.stream = True
        
        # Validate file
        is_valid, error = self.validate_audio_file(audio_file)
        if not is_valid:
            raise ValueError(error)
        
        # Prepare request parameters
        params = {
            "model": config.model.value,
            "file": open(audio_file, "rb"),
            "stream": True,
        }
        
        if config.response_format:
            params["response_format"] = config.response_format.value
        
        if config.prompt:
            params["prompt"] = config.prompt
        
        include_params = []
        if config.include_logprobs:
            include_params.append("logprobs")
        if include_params:
            params["include"] = include_params
        
        try:
            stream = self.client.audio.transcriptions.create(**params)
            
            for event in stream:
                yield event.model_dump() if hasattr(event, 'model_dump') else dict(event)
        
        finally:
            if 'file' in params and hasattr(params['file'], 'close'):
                params['file'].close()
    
    def translate(
        self,
        audio_file: Union[str, Path],
        model: str = "whisper-1",
    ) -> TranscriptionResult:
        """
        Translate and transcribe audio file to English
        
        Args:
            audio_file: Path to audio file
            model: Model to use (only whisper-1 supported for translations)
            
        Returns:
            TranscriptionResult object with English text
        """
        # Validate file
        is_valid, error = self.validate_audio_file(audio_file)
        if not is_valid:
            raise ValueError(error)
        
        try:
            with open(audio_file, "rb") as f:
                response = self.client.audio.translations.create(
                    model=model,
                    file=f,
                )
            
            if isinstance(response, str):
                return TranscriptionResult(text=response)
            elif hasattr(response, 'text'):
                return TranscriptionResult(text=response.text)
            else:
                return TranscriptionResult(text=str(response))
        
        except Exception as e:
            raise RuntimeError(f"Translation failed: {str(e)}")
    
    def to_data_url(self, audio_file: Union[str, Path]) -> str:
        """
        Convert audio file to data URL for speaker reference
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Data URL string
        """
        path = Path(audio_file)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {audio_file}")
        
        # Determine MIME type
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.mp4': 'audio/mp4',
            '.m4a': 'audio/mp4',
            '.webm': 'audio/webm',
        }
        
        mime_type = mime_types.get(path.suffix.lower(), 'audio/wav')
        
        # Read and encode file
        with open(path, "rb") as f:
            audio_data = f.read()
        
        base64_data = base64.b64encode(audio_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
    
    def transcribe_with_diarization(
        self,
        audio_file: Union[str, Path],
        speaker_references: Optional[Dict[str, Union[str, Path]]] = None,
        chunking_strategy: str = "auto",
    ) -> TranscriptionResult:
        """
        Transcribe audio with speaker diarization
        
        Args:
            audio_file: Path to audio file
            speaker_references: Dictionary mapping speaker names to audio file paths
            chunking_strategy: Chunking strategy ("auto" or VAD config)
            
        Returns:
            TranscriptionResult with speaker segments
        """
        config = TranscriptionConfig(
            model=TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE,
            response_format=ResponseFormat.DIARIZED_JSON,
            chunking_strategy=chunking_strategy,
        )
        
        # Convert speaker references to data URLs if provided
        if speaker_references:
            known_speaker_names = []
            known_speaker_references = []
            
            for name, ref_path in speaker_references.items():
                known_speaker_names.append(name)
                known_speaker_references.append(self.to_data_url(ref_path))
            
            config.known_speaker_names = known_speaker_names
            config.known_speaker_references = known_speaker_references
        
        return self.transcribe(audio_file, config)
    
    def post_process_with_gpt4(
        self,
        transcript: str,
        system_prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.0,
    ) -> str:
        """
        Post-process transcript using GPT-4 to correct spelling and improve quality
        
        Args:
            transcript: Raw transcript text
            system_prompt: System prompt with instructions for correction
            model: GPT model to use
            temperature: Temperature for generation
            
        Returns:
            Corrected transcript
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"Post-processing failed: {str(e)}")
    
    def split_audio_file(
        self,
        audio_file: Union[str, Path],
        chunk_duration_minutes: int = 10,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> List[Path]:
        """
        Split large audio file into chunks
        
        Note: Requires pydub package. Install with: pip install pydub
        
        Args:
            audio_file: Path to audio file
            chunk_duration_minutes: Duration of each chunk in minutes
            output_dir: Directory to save chunks (defaults to same directory as input)
            
        Returns:
            List of paths to chunk files
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for audio splitting. Install with: pip install pydub")
        
        path = Path(audio_file)
        output_dir = Path(output_dir) if output_dir else path.parent
        
        # Load audio
        audio = AudioSegment.from_file(str(path))
        
        # Calculate chunk duration in milliseconds
        chunk_duration_ms = chunk_duration_minutes * 60 * 1000
        
        # Split into chunks
        chunks = []
        for i, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
            chunk = audio[start_ms:start_ms + chunk_duration_ms]
            
            # Generate output filename
            chunk_path = output_dir / f"{path.stem}_chunk_{i+1:03d}{path.suffix}"
            
            # Export chunk
            chunk.export(str(chunk_path), format=path.suffix[1:])
            chunks.append(chunk_path)
        
        return chunks


def create_correction_prompt(
    company_name: str,
    product_names: List[str],
    additional_instructions: Optional[str] = None,
) -> str:
    """
    Create a system prompt for GPT-4 post-processing
    
    Args:
        company_name: Name of the company
        product_names: List of product names to ensure correct spelling
        additional_instructions: Additional instructions for correction
        
    Returns:
        System prompt string
    """
    products_str = ", ".join(product_names)
    
    prompt = f"""You are a helpful assistant for the company {company_name}. Your task is to correct any spelling discrepancies in the transcribed text. Make sure that the names of the following products are spelled correctly: {products_str}. Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided."""
    
    if additional_instructions:
        prompt += f"\n\n{additional_instructions}"
    
    return prompt


# Example usage functions
def example_basic_transcription():
    """Example: Basic transcription"""
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format=ResponseFormat.TEXT,
    )
    
    result = processor.transcribe("audio.mp3", config)
    print(result.text)


def example_transcription_with_prompt():
    """Example: Transcription with prompt for better accuracy"""
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format=ResponseFormat.TEXT,
        prompt="The following conversation is a lecture about the recent developments around OpenAI, GPT-4.5 and the future of AI.",
    )
    
    result = processor.transcribe("lecture.mp3", config)
    print(result.text)


def example_transcription_with_timestamps():
    """Example: Transcription with word-level timestamps"""
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.WHISPER_1,
        response_format=ResponseFormat.VERBOSE_JSON,
        timestamp_granularities=[TimestampGranularity.WORD],
    )
    
    result = processor.transcribe("audio.mp3", config)
    
    if result.words:
        for word in result.words:
            print(f"{word['word']}: {word['start']}s - {word['end']}s")


def example_speaker_diarization():
    """Example: Transcription with speaker diarization"""
    processor = AudioToTextProcessor()
    
    speaker_refs = {
        "agent": "agent_reference.wav",
        "customer": "customer_reference.wav",
    }
    
    result = processor.transcribe_with_diarization(
        "meeting.wav",
        speaker_references=speaker_refs,
    )
    
    if result.segments:
        for segment in result.segments:
            print(f"{segment['speaker']}: {segment['text']} ({segment['start']}s - {segment['end']}s)")


def example_streaming_transcription():
    """Example: Streaming transcription"""
    processor = AudioToTextProcessor()
    
    for event in processor.transcribe_stream("audio.mp3"):
        print(event)


def example_translation():
    """Example: Translate audio to English"""
    processor = AudioToTextProcessor()
    
    result = processor.translate("german_audio.mp3")
    print(result.text)


def example_post_processing():
    """Example: Post-process transcript with GPT-4"""
    processor = AudioToTextProcessor()
    
    # First, transcribe
    config = TranscriptionConfig(
        model=TranscriptionModel.WHISPER_1,
        response_format=ResponseFormat.TEXT,
    )
    raw_transcript = processor.transcribe("audio.mp3", config).text
    
    # Then, correct with GPT-4
    system_prompt = create_correction_prompt(
        company_name="ZyntriQix",
        product_names=[
            "ZyntriQix",
            "Digique Plus",
            "CynapseFive",
            "VortiQore V8",
        ],
    )
    
    corrected = processor.post_process_with_gpt4(
        raw_transcript,
        system_prompt,
        model="gpt-4",
    )
    
    print("Original:", raw_transcript)
    print("Corrected:", corrected)


if __name__ == "__main__":
    print("Audio to Text Processing Module")
    print("=" * 50)
    print("\nThis module provides comprehensive speech-to-text functionality.")
    print("See the example functions for usage patterns.")
    print("\nAvailable features:")
    print("- Basic transcriptions")
    print("- Translations")
    print("- Speaker diarization")
    print("- Timestamps (word and segment level)")
    print("- Streaming transcriptions")
    print("- Prompting for better accuracy")
    print("- Post-processing with GPT-4")
