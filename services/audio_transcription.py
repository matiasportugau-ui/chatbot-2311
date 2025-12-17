#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Transcription Service
Integrates with OpenAI's Audio API for speech-to-text conversion
Supports multiple models: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize
"""

import os
import base64
import json
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TranscriptionModel(str, Enum):
    """Available transcription models"""
    WHISPER_1 = "whisper-1"
    GPT4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"


class ResponseFormat(str, Enum):
    """Available response formats"""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"


class ChunkingStrategy(str, Enum):
    """Chunking strategies for diarization"""
    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class TranscriptionConfig:
    """Configuration for audio transcription"""
    model: TranscriptionModel = TranscriptionModel.GPT4O_TRANSCRIBE
    response_format: ResponseFormat = ResponseFormat.JSON
    language: Optional[str] = None
    prompt: Optional[str] = None
    temperature: float = 0.0
    timestamp_granularities: Optional[List[str]] = None
    
    # Diarization-specific settings
    chunking_strategy: Optional[ChunkingStrategy] = None
    known_speaker_names: Optional[List[str]] = None
    known_speaker_references: Optional[List[str]] = None
    
    # Streaming settings
    stream: bool = False
    include_logprobs: bool = False


@dataclass
class TranscriptionResult:
    """Result from audio transcription"""
    text: str
    model: str
    duration: Optional[float] = None
    language: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    words: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class AudioTranscriptionService:
    """Service for transcribing audio using OpenAI's API"""
    
    SUPPORTED_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}
    MAX_FILE_SIZE_MB = 25
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the audio transcription service
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("Audio transcription service initialized")
    
    def validate_audio_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate audio file format and size
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if valid, raises exception otherwise
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Check file extension
        file_extension = file_path.suffix.lower().lstrip('.')
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"Audio file too large: {file_size_mb:.2f}MB. "
                f"Maximum size: {self.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(f"Audio file validated: {file_path} ({file_size_mb:.2f}MB)")
        return True
    
    def transcribe(
        self,
        audio_file_path: Union[str, Path],
        config: Optional[TranscriptionConfig] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            config: Transcription configuration
            
        Returns:
            TranscriptionResult with transcribed text and metadata
        """
        if config is None:
            config = TranscriptionConfig()
        
        # Validate audio file
        audio_file_path = Path(audio_file_path)
        self.validate_audio_file(audio_file_path)
        
        logger.info(f"Transcribing audio file: {audio_file_path}")
        logger.info(f"Using model: {config.model.value}")
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                # Prepare transcription parameters
                params = {
                    "model": config.model.value,
                    "file": audio_file,
                    "response_format": config.response_format.value,
                }
                
                # Add optional parameters
                if config.language:
                    params["language"] = config.language
                
                if config.prompt:
                    params["prompt"] = config.prompt
                
                if config.temperature != 0.0:
                    params["temperature"] = config.temperature
                
                # Model-specific parameters
                if config.model == TranscriptionModel.WHISPER_1:
                    if config.timestamp_granularities:
                        params["timestamp_granularities"] = config.timestamp_granularities
                
                elif config.model == TranscriptionModel.GPT4O_TRANSCRIBE_DIARIZE:
                    if config.chunking_strategy:
                        params["chunking_strategy"] = config.chunking_strategy.value
                    
                    extra_body = {}
                    if config.known_speaker_names:
                        extra_body["known_speaker_names"] = config.known_speaker_names
                    
                    if config.known_speaker_references:
                        extra_body["known_speaker_references"] = config.known_speaker_references
                    
                    if extra_body:
                        params["extra_body"] = extra_body
                
                # Streaming
                if config.stream:
                    params["stream"] = True
                    return self._transcribe_stream(params)
                
                # Regular transcription
                transcription = self.client.audio.transcriptions.create(**params)
                
                # Parse result based on response format
                return self._parse_transcription_result(transcription, config)
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def _parse_transcription_result(
        self,
        transcription: Any,
        config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Parse transcription result based on format"""
        
        if config.response_format == ResponseFormat.TEXT:
            return TranscriptionResult(
                text=str(transcription),
                model=config.model.value
            )
        
        elif config.response_format == ResponseFormat.JSON:
            return TranscriptionResult(
                text=transcription.text,
                model=config.model.value
            )
        
        elif config.response_format == ResponseFormat.VERBOSE_JSON:
            result = TranscriptionResult(
                text=transcription.text,
                model=config.model.value,
                language=getattr(transcription, 'language', None),
                duration=getattr(transcription, 'duration', None)
            )
            
            if hasattr(transcription, 'segments'):
                result.segments = transcription.segments
            
            if hasattr(transcription, 'words'):
                result.words = transcription.words
            
            return result
        
        elif config.response_format == ResponseFormat.DIARIZED_JSON:
            segments = []
            if hasattr(transcription, 'segments'):
                for segment in transcription.segments:
                    segments.append({
                        'speaker': segment.speaker,
                        'text': segment.text,
                        'start': segment.start,
                        'end': segment.end
                    })
            
            return TranscriptionResult(
                text=transcription.text if hasattr(transcription, 'text') else "",
                model=config.model.value,
                segments=segments
            )
        
        else:
            # For SRT, VTT, or other formats
            return TranscriptionResult(
                text=str(transcription),
                model=config.model.value
            )
    
    def _transcribe_stream(self, params: Dict[str, Any]) -> TranscriptionResult:
        """Handle streaming transcription"""
        logger.info("Starting streaming transcription")
        
        stream = self.client.audio.transcriptions.create(**params)
        
        full_text = ""
        for event in stream:
            if hasattr(event, 'text'):
                full_text += event.text
                logger.debug(f"Received chunk: {event.text}")
        
        return TranscriptionResult(
            text=full_text,
            model=params["model"]
        )
    
    def translate(
        self,
        audio_file_path: Union[str, Path],
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0
    ) -> TranscriptionResult:
        """
        Translate audio to English
        
        Args:
            audio_file_path: Path to audio file
            model: Translation model (only whisper-1 supported)
            prompt: Optional prompt for context
            response_format: Format of response
            temperature: Sampling temperature
            
        Returns:
            TranscriptionResult with translated text
        """
        audio_file_path = Path(audio_file_path)
        self.validate_audio_file(audio_file_path)
        
        logger.info(f"Translating audio file: {audio_file_path}")
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                params = {
                    "model": model,
                    "file": audio_file,
                    "response_format": response_format,
                    "temperature": temperature,
                }
                
                if prompt:
                    params["prompt"] = prompt
                
                translation = self.client.audio.translations.create(**params)
                
                if response_format == "text":
                    text = str(translation)
                else:
                    text = translation.text
                
                return TranscriptionResult(
                    text=text,
                    model=model
                )
        
        except Exception as e:
            logger.error(f"Error translating audio: {e}")
            raise
    
    def transcribe_with_diarization(
        self,
        audio_file_path: Union[str, Path],
        known_speakers: Optional[Dict[str, str]] = None,
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio with speaker diarization
        
        Args:
            audio_file_path: Path to audio file
            known_speakers: Dict mapping speaker names to audio reference file paths
            prompt: Optional prompt for context
            
        Returns:
            TranscriptionResult with speaker-labeled segments
        """
        config = TranscriptionConfig(
            model=TranscriptionModel.GPT4O_TRANSCRIBE_DIARIZE,
            response_format=ResponseFormat.DIARIZED_JSON,
            chunking_strategy=ChunkingStrategy.AUTO,
            prompt=prompt
        )
        
        # Add known speakers if provided
        if known_speakers:
            config.known_speaker_names = list(known_speakers.keys())
            config.known_speaker_references = []
            
            for name, ref_path in known_speakers.items():
                # Convert reference audio to data URL
                data_url = self._audio_to_data_url(ref_path)
                config.known_speaker_references.append(data_url)
        
        return self.transcribe(audio_file_path, config)
    
    def _audio_to_data_url(self, file_path: Union[str, Path]) -> str:
        """Convert audio file to data URL for speaker reference"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Reference audio file not found: {file_path}")
        
        # Determine MIME type from extension
        extension = file_path.suffix.lower().lstrip('.')
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'mp4': 'audio/mp4',
            'm4a': 'audio/mp4',
            'webm': 'audio/webm'
        }
        
        mime_type = mime_types.get(extension, 'audio/mpeg')
        
        with open(file_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        return f"data:{mime_type};base64,{audio_data}"
    
    def transcribe_with_timestamps(
        self,
        audio_file_path: Union[str, Path],
        granularity: str = "word",
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio with word-level or segment-level timestamps
        
        Args:
            audio_file_path: Path to audio file
            granularity: "word" or "segment"
            prompt: Optional prompt for context
            
        Returns:
            TranscriptionResult with timestamp information
        """
        config = TranscriptionConfig(
            model=TranscriptionModel.WHISPER_1,
            response_format=ResponseFormat.VERBOSE_JSON,
            timestamp_granularities=[granularity],
            prompt=prompt
        )
        
        return self.transcribe(audio_file_path, config)


def create_audio_transcription_service(api_key: Optional[str] = None) -> AudioTranscriptionService:
    """
    Factory function to create audio transcription service
    
    Args:
        api_key: OpenAI API key (optional)
        
    Returns:
        AudioTranscriptionService instance
    """
    return AudioTranscriptionService(api_key=api_key)


if __name__ == "__main__":
    # Example usage
    print("Audio Transcription Service")
    print("=" * 50)
    
    try:
        service = create_audio_transcription_service()
        print("✅ Service initialized successfully")
        print(f"Supported formats: {', '.join(service.SUPPORTED_FORMATS)}")
        print(f"Max file size: {service.MAX_FILE_SIZE_MB}MB")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set OPENAI_API_KEY environment variable")
