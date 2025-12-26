#!/usr/bin/env python3
"""
Audio Transcription Module using OpenAI API
Supports:
- Transcriptions (whisper-1, gpt-4o-transcribe)
- Translations (whisper-1)
- Diarization (gpt-4o-transcribe-diarize)
- File chunking for large files (placeholder for now)
"""

import os
import argparse
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Try to import pydub for chunking
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Load environment variables
load_dotenv()

class AudioTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            # Try loading from .env if not found (although load_dotenv should have handled it)
            # This is just a fallback check
            pass

    def transcribe(self, 
                   file_path: str, 
                   model: str = "gpt-4o-transcribe", 
                   prompt: Optional[str] = None,
                   response_format: str = "json") -> Dict[str, Any]:
        """
        Transcribe audio file.
        Models: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as audio_file:
            kwargs = {
                "model": model,
                "file": audio_file,
                "response_format": response_format
            }
            if prompt:
                kwargs["prompt"] = prompt
            
            transcription = self.client.audio.transcriptions.create(**kwargs)
            
            # Handling return types based on response_format
            if response_format == "text":
                return {"text": transcription}
            elif response_format in ["json", "verbose_json"]:
                 if hasattr(transcription, "text"):
                     return {"text": transcription.text}
                 elif hasattr(transcription, "model_dump"):
                     return transcription.model_dump()
                 else:
                     return dict(transcription)
            return transcription

    def transcribe_with_diarization(self,
                                  file_path: str) -> Dict[str, Any]:
        """
        Transcribe with speaker diarization using gpt-4o-transcribe-diarize.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="gpt-4o-transcribe-diarize",
                file=audio_file,
                response_format="diarized_json",
                chunking_strategy="auto"
            )
            
            return transcript.model_dump()

    def translate(self, file_path: str, model: str = "whisper-1") -> Dict[str, Any]:
        """
        Translate audio to English.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as audio_file:
            translation = self.client.audio.translations.create(
                model=model,
                file=audio_file
            )
            return {"text": translation.text}

def main():
    parser = argparse.ArgumentParser(description="Audio Transcriber using OpenAI")
    parser.add_argument("file", help="Path to audio file")
    parser.add_argument("--mode", choices=["transcribe", "diarize", "translate"], default="transcribe", help="Operation mode")
    parser.add_argument("--model", default="gpt-4o-transcribe", help="Model to use (for transcribe mode)")
    parser.add_argument("--prompt", help="Optional prompt for context")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        return

    try:
        transcriber = AudioTranscriber()
        
        if args.mode == "transcribe":
            result = transcriber.transcribe(args.file, model=args.model, prompt=args.prompt)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.mode == "diarize":
            result = transcriber.transcribe_with_diarization(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.mode == "translate":
            result = transcriber.translate(args.file)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
