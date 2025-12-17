#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Speech-to-Text Module using OpenAI Audio API
Supports transcriptions, translations, speaker diarization, and streaming
"""

import os
import base64
import json
from typing import Dict, List, Any, Optional, Union, Iterator
from dataclasses import dataclass, asdict
from enum import Enum
import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not installed. Install with: pip install openai")


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
class TranscriptionResult:
    """Result of a transcription"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    segments: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    response_format: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None


@dataclass
class DiarizedSegment:
    """Speaker diarization segment"""
    speaker: str
    text: str
    start: float
    end: float
    segment_id: Optional[str] = None


class SpeechToText:
    """Speech-to-Text service using OpenAI Audio API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-transcribe"):
        """
        Initialize Speech-to-Text service
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Default model to use for transcriptions
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = model
        self.max_file_size_mb = 25
    
    def transcribe(
        self,
        audio_file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
        logprobs: Optional[bool] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            model: Model to use (whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize)
            language: Language code (ISO 639-1 or 639-3)
            prompt: Optional prompt to improve transcription quality
            response_format: Format of response (json, text, srt, verbose_json, vtt, diarized_json)
            temperature: Sampling temperature (0-1)
            timestamp_granularities: List of granularities (word, segment)
            logprobs: Include log probabilities (for gpt-4o models)
            **kwargs: Additional parameters
            
        Returns:
            TranscriptionResult object
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Check file size
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.2f} MB) exceeds maximum ({self.max_file_size_mb} MB). "
                "Split the audio file or use a compressed format."
            )
        
        model = model or self.default_model
        
        # Prepare parameters
        params = {
            "model": model,
            "file": open(audio_file_path, "rb"),
            "response_format": response_format
        }
        
        if language:
            params["language"] = language
        if prompt:
            params["prompt"] = prompt
        if temperature is not None:
            params["temperature"] = temperature
        if timestamp_granularities:
            params["timestamp_granularities"] = timestamp_granularities
        if logprobs is not None:
            params["logprobs"] = logprobs
        
        # Add extra parameters for diarization
        if model == TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE:
            if "chunking_strategy" not in kwargs:
                # Auto chunking for files longer than 30 seconds
                params["chunking_strategy"] = "auto"
            else:
                params["chunking_strategy"] = kwargs["chunking_strategy"]
            
            if "known_speaker_names" in kwargs and "known_speaker_references" in kwargs:
                params["extra_body"] = {
                    "known_speaker_names": kwargs["known_speaker_names"],
                    "known_speaker_references": kwargs["known_speaker_references"]
                }
        
        try:
            response = self.client.audio.transcriptions.create(**params)
            
            # Parse response based on format
            if response_format == "text":
                text = str(response)
            elif isinstance(response, dict):
                text = response.get("text", "")
            else:
                text = response.text if hasattr(response, "text") else str(response)
            
            result = TranscriptionResult(
                text=text,
                model=model,
                response_format=response_format,
                timestamp=datetime.datetime.now()
            )
            
            # Extract additional data if available
            if isinstance(response, dict):
                result.language = response.get("language")
                result.duration = response.get("duration")
                result.words = response.get("words")
                result.segments = response.get("segments")
            elif hasattr(response, "language"):
                result.language = response.language
            if hasattr(response, "words"):
                result.words = response.words
            if hasattr(response, "segments"):
                result.segments = response.segments
            
            return result
            
        finally:
            if isinstance(params["file"], type(open(__file__))):
                params["file"].close()
    
    def transcribe_streaming(
        self,
        audio_file_path: str,
        model: Optional[str] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "text",
        include_logprobs: bool = False,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream transcription results as they become available
        
        Args:
            audio_file_path: Path to audio file
            model: Model to use (must support streaming: gpt-4o-transcribe, gpt-4o-mini-transcribe)
            language: Language code
            prompt: Optional prompt
            response_format: Format (text, json, diarized_json)
            include_logprobs: Include log probabilities
            **kwargs: Additional parameters
            
        Yields:
            Dictionary with event data (transcript.text.delta, transcript.text.segment, transcript.text.done)
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        model = model or self.default_model
        
        # Streaming is not supported for whisper-1
        if model == TranscriptionModel.WHISPER_1:
            raise ValueError("Streaming is not supported for whisper-1. Use gpt-4o-transcribe or gpt-4o-mini-transcribe.")
        
        params = {
            "model": model,
            "file": open(audio_file_path, "rb"),
            "response_format": response_format,
            "stream": True
        }
        
        if language:
            params["language"] = language
        if prompt:
            params["prompt"] = prompt
        
        include_params = []
        if include_logprobs:
            include_params.append("logprobs")
        if include_params:
            params["include"] = include_params
        
        # Add diarization parameters if needed
        if model == TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE:
            if "chunking_strategy" not in kwargs:
                params["chunking_strategy"] = "auto"
            else:
                params["chunking_strategy"] = kwargs["chunking_strategy"]
        
        try:
            stream = self.client.audio.transcriptions.create(**params)
            
            for event in stream:
                yield self._parse_stream_event(event)
                
        finally:
            if isinstance(params["file"], type(open(__file__))):
                params["file"].close()
    
    def _parse_stream_event(self, event) -> Dict[str, Any]:
        """Parse streaming event"""
        if hasattr(event, "event"):
            return {
                "event": event.event,
                "data": event.model_dump() if hasattr(event, "model_dump") else str(event)
            }
        return {"event": "unknown", "data": str(event)}
    
    def translate(
        self,
        audio_file_path: str,
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None
    ) -> TranscriptionResult:
        """
        Translate and transcribe audio to English
        
        Args:
            audio_file_path: Path to audio file
            model: Model to use (only whisper-1 supported for translations)
            prompt: Optional prompt
            response_format: Format (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature
            
        Returns:
            TranscriptionResult object with English translation
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        if model != TranscriptionModel.WHISPER_1:
            raise ValueError("Translations API only supports whisper-1 model")
        
        params = {
            "model": model,
            "file": open(audio_file_path, "rb"),
            "response_format": response_format
        }
        
        if prompt:
            params["prompt"] = prompt
        if temperature is not None:
            params["temperature"] = temperature
        
        try:
            response = self.client.audio.translations.create(**params)
            
            text = response.text if hasattr(response, "text") else str(response)
            
            return TranscriptionResult(
                text=text,
                model=model,
                response_format=response_format,
                timestamp=datetime.datetime.now()
            )
            
        finally:
            if isinstance(params["file"], type(open(__file__))):
                params["file"].close()
    
    def transcribe_with_diarization(
        self,
        audio_file_path: str,
        known_speakers: Optional[List[Dict[str, str]]] = None,
        chunking_strategy: str = "auto",
        **kwargs
    ) -> List[DiarizedSegment]:
        """
        Transcribe audio with speaker diarization
        
        Args:
            audio_file_path: Path to audio file
            known_speakers: List of dicts with 'name' and 'reference_audio_path' for known speakers
            chunking_strategy: Chunking strategy (auto or VAD config)
            **kwargs: Additional transcription parameters
            
        Returns:
            List of DiarizedSegment objects
        """
        params = {
            "model": TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE,
            "response_format": ResponseFormat.DIARIZED_JSON,
            "chunking_strategy": chunking_strategy,
            **kwargs
        }
        
        # Process known speakers
        if known_speakers:
            speaker_names = []
            speaker_references = []
            
            for speaker in known_speakers:
                name = speaker.get("name")
                ref_path = speaker.get("reference_audio_path")
                
                if name and ref_path:
                    speaker_names.append(name)
                    # Convert reference audio to data URL
                    ref_data_url = self._audio_to_data_url(ref_path)
                    speaker_references.append(ref_data_url)
            
            if speaker_names and speaker_references:
                params["known_speaker_names"] = speaker_names
                params["known_speaker_references"] = speaker_references
        
        result = self.transcribe(audio_file_path, **params)
        
        # Parse diarized segments
        segments = []
        if result.segments:
            for seg in result.segments:
                segments.append(DiarizedSegment(
                    speaker=seg.get("speaker", "unknown"),
                    text=seg.get("text", ""),
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    segment_id=seg.get("segment_id")
                ))
        
        return segments
    
    def _audio_to_data_url(self, audio_path: str) -> str:
        """
        Convert audio file to data URL format
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Data URL string
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Reference audio file not found: {audio_path}")
        
        # Determine MIME type from extension
        ext = os.path.splitext(audio_path)[1].lower()
        mime_types = {
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".mp4": "audio/mp4",
            ".m4a": "audio/mp4",
            ".webm": "audio/webm",
            ".mpeg": "audio/mpeg",
            ".mpga": "audio/mpeg"
        }
        mime_type = mime_types.get(ext, "audio/wav")
        
        # Read and encode file
        with open(audio_path, "rb") as f:
            audio_data = f.read()
            base64_data = base64.b64encode(audio_data).decode("utf-8")
        
        return f"data:{mime_type};base64,{base64_data}"
    
    def transcribe_with_post_processing(
        self,
        audio_file_path: str,
        system_prompt: Optional[str] = None,
        correction_terms: Optional[List[str]] = None,
        model: Optional[str] = None,
        gpt_model: str = "gpt-4o",
        temperature: float = 0.0,
        **kwargs
    ) -> str:
        """
        Transcribe audio and post-process with GPT-4 for improved accuracy
        
        Args:
            audio_file_path: Path to audio file
            system_prompt: System prompt for GPT-4 post-processing
            correction_terms: List of terms to correct (product names, acronyms, etc.)
            model: Transcription model to use
            gpt_model: GPT model for post-processing
            temperature: Temperature for GPT model
            **kwargs: Additional transcription parameters
            
        Returns:
            Corrected transcription text
        """
        # First, transcribe the audio
        transcription_result = self.transcribe(audio_file_path, model=model, **kwargs)
        raw_transcript = transcription_result.text
        
        # Build system prompt if not provided
        if not system_prompt:
            system_prompt = "You are a helpful assistant. Your task is to correct any spelling discrepancies in the transcribed text."
            
            if correction_terms:
                terms_str = ", ".join(correction_terms)
                system_prompt += f" Make sure that the following terms are spelled correctly: {terms_str}."
            
            system_prompt += " Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided."
        
        # Post-process with GPT-4
        try:
            response = self.client.chat.completions.create(
                model=gpt_model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_transcript}
                ]
            )
            
            corrected_text = response.choices[0].message.content
            return corrected_text
            
        except Exception as e:
            print(f"Warning: Post-processing failed: {e}. Returning raw transcript.")
            return raw_transcript
    
    def split_audio_file(
        self,
        audio_file_path: str,
        output_dir: str,
        chunk_duration_minutes: int = 10
    ) -> List[str]:
        """
        Split large audio file into chunks
        
        Args:
            audio_file_path: Path to audio file
            output_dir: Directory to save chunks
            chunk_duration_minutes: Duration of each chunk in minutes
            
        Returns:
            List of paths to chunk files
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for audio splitting. Install with: pip install pydub")
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load audio
        audio = AudioSegment.from_file(audio_file_path)
        
        # Calculate chunk duration in milliseconds
        chunk_duration_ms = chunk_duration_minutes * 60 * 1000
        
        # Split audio
        chunks = []
        base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        ext = os.path.splitext(audio_file_path)[1]
        
        for i, start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
            chunk = audio[start_ms:start_ms + chunk_duration_ms]
            chunk_path = os.path.join(output_dir, f"{base_name}_chunk_{i+1:03d}{ext}")
            chunk.export(chunk_path, format=ext[1:])  # Remove dot from extension
            chunks.append(chunk_path)
        
        return chunks


def main():
    """Example usage"""
    if not OPENAI_AVAILABLE:
        print("OpenAI package not installed. Install with: pip install openai")
        return
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Example usage
    stt = SpeechToText()
    
    print("Speech-to-Text Module")
    print("=" * 50)
    print("\nAvailable models:")
    for model in TranscriptionModel:
        print(f"  - {model.value}")
    
    print("\nExample usage:")
    print("  stt = SpeechToText()")
    print("  result = stt.transcribe('audio.mp3', model='gpt-4o-transcribe')")
    print("  print(result.text)")


if __name__ == "__main__":
    main()
