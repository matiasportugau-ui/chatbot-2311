#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Integrator
Supports OpenAI Audio API for transcriptions and translations.
"""

import os
import logging
from typing import Dict, Optional, Any, List, Union, BinaryIO
from enum import Enum
import json

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Provider availability checks
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed")

class AudioModel(str, Enum):
    """Supported Audio Models"""
    WHISPER_1 = "whisper-1"
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    GPT_4O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"

class AudioResponseFormat(str, Enum):
    """Supported Response Formats"""
    JSON = "json"
    TEXT = "text"
    SRT = "srt"
    VERBOSE_JSON = "verbose_json"
    VTT = "vtt"
    DIARIZED_JSON = "diarized_json"

class AudioIntegrator:
    """
    Integrator for OpenAI Audio API
    """
    
    def __init__(self, api_key: Optional[str] = None, organization: Optional[str] = None, project: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORGANIZATION_ID")
        self.project = project or os.getenv("OPENAI_PROJECT_ID")
        
        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                organization=self.organization,
                project=self.project
            )
            logger.info("✅ OpenAI Audio client initialized")
        else:
            logger.warning("⚠️ OpenAI client not initialized. Check OPENAI_API_KEY.")

    def transcribe(
        self,
        file: Union[str, BinaryIO],
        model: Union[str, AudioModel] = AudioModel.WHISPER_1,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Union[str, AudioResponseFormat] = AudioResponseFormat.JSON,
        temperature: float = 0,
        timestamp_granularities: Optional[List[str]] = None,
        chunking_strategy: Optional[str] = None,
        extra_body: Optional[Dict] = None,
    ) -> Any:
        """
        Transcribe audio to text.
        
        Args:
            file: Path to file or file-like object
            model: Model to use (whisper-1, gpt-4o-transcribe, etc.)
            language: ISO-639-1 language code (optional)
            prompt: Optional text to guide the model's style or continue a previous audio segment
            response_format: Format of the response (json, text, srt, verbose_json, vtt, diarized_json)
            temperature: Sampling temperature (0-1)
            timestamp_granularities: ['word'] or ['segment'] or both (only for verbose_json with whisper-1)
            chunking_strategy: "auto" or other strategy (required for diarization if long)
            extra_body: Additional parameters (e.g. known_speaker_names for diarization)
            
        Returns:
            Transcription result (string or object depending on response_format)
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        if isinstance(model, AudioModel):
            model = model.value
        
        if isinstance(response_format, AudioResponseFormat):
            response_format = response_format.value

        # Handle file opening if path provided
        should_close_file = False
        file_obj = file
        if isinstance(file, str):
            if not os.path.exists(file):
                raise FileNotFoundError(f"Audio file not found: {file}")
            file_obj = open(file, "rb")
            should_close_file = True

        try:
            params = {
                "file": file_obj,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
            }

            if language:
                params["language"] = language
            if prompt:
                params["prompt"] = prompt
            if timestamp_granularities:
                params["timestamp_granularities"] = timestamp_granularities
            if chunking_strategy:
                params["chunking_strategy"] = chunking_strategy
            if extra_body:
                params["extra_body"] = extra_body

            logger.info(f"Transcribing audio with model {model}...")
            transcription = self.client.audio.transcriptions.create(**params)
            
            return transcription

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise e
        finally:
            if should_close_file:
                file_obj.close()

    def translate(
        self,
        file: Union[str, BinaryIO],
        model: Union[str, AudioModel] = AudioModel.WHISPER_1,
        prompt: Optional[str] = None,
        response_format: Union[str, AudioResponseFormat] = AudioResponseFormat.JSON,
        temperature: float = 0,
    ) -> Any:
        """
        Translate audio into English text.
        
        Args:
            file: Path to file or file-like object
            model: Model to use (only whisper-1 supported currently)
            prompt: Optional text to guide the model
            response_format: Format of the response
            temperature: Sampling temperature
            
        Returns:
            Translation result
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        if isinstance(model, AudioModel):
            model = model.value
            
        if isinstance(response_format, AudioResponseFormat):
            response_format = response_format.value

        # Handle file opening
        should_close_file = False
        file_obj = file
        if isinstance(file, str):
            if not os.path.exists(file):
                raise FileNotFoundError(f"Audio file not found: {file}")
            file_obj = open(file, "rb")
            should_close_file = True

        try:
            params = {
                "file": file_obj,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
            }
            
            if prompt:
                params["prompt"] = prompt

            logger.info(f"Translating audio with model {model}...")
            translation = self.client.audio.translations.create(**params)
            
            return translation

        except Exception as e:
            logger.error(f"Error during translation: {e}")
            raise e
        finally:
            if should_close_file:
                file_obj.close()

# Example usage
if __name__ == "__main__":
    # Simple test if executed directly
    integrator = AudioIntegrator()
    if integrator.client:
        print("Audio Integrator ready.")
    else:
        print("Audio Integrator not initialized (check API key).")
