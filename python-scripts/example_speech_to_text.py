#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of the Speech-to-Text service.

This script demonstrates various features of the OpenAI Audio API:
- Basic transcriptions
- Translations
- Speaker diarization
- Streaming transcriptions
- Post-processing with GPT-4
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.speech_to_text import (
    SpeechToTextService,
    TranscriptionModel,
    ResponseFormat,
    ChunkingStrategy,
    get_speech_to_text_service,
    transcribe_audio,
    translate_audio,
)


def example_basic_transcription():
    """Example: Basic transcription"""
    print("\n=== Example 1: Basic Transcription ===")
    
    # Replace with your audio file path
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        print("   Please update the audio_file path in the script.")
        return
    
    try:
        service = get_speech_to_text_service()
        result = service.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"Transcription: {result.text}")
        if result.language:
            print(f"Detected language: {result.language}")
            
    except Exception as e:
        print(f"Error: {e}")


def example_transcription_with_prompt():
    """Example: Transcription with prompt for better accuracy"""
    print("\n=== Example 2: Transcription with Prompt ===")
    
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        service = get_speech_to_text_service()
        result = service.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
            prompt="The following conversation is a lecture about the recent developments around OpenAI, GPT-4.5 and the future of AI.",
        )
        
        print(f"Transcription: {result.text}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_translation():
    """Example: Translate audio to English"""
    print("\n=== Example 3: Translation to English ===")
    
    audio_file = "path/to/your/german.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        service = get_speech_to_text_service()
        result = service.translate(
            audio_file=audio_file,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"English translation: {result.text}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_diarization():
    """Example: Speaker diarization"""
    print("\n=== Example 4: Speaker Diarization ===")
    
    audio_file = "path/to/your/meeting.wav"
    agent_ref = "path/to/agent_reference.wav"  # 2-10 second reference clip
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        service = get_speech_to_text_service()
        
        known_speaker_refs = None
        known_speaker_names = None
        
        if Path(agent_ref).exists():
            known_speaker_refs = [agent_ref]
            known_speaker_names = ["agent"]
        
        result = service.transcribe_with_diarization(
            audio_file=audio_file,
            known_speaker_names=known_speaker_names,
            known_speaker_references=known_speaker_refs,
            chunking_strategy=ChunkingStrategy.AUTO,
        )
        
        print(f"Full transcription: {result.text}\n")
        print("Speaker segments:")
        for segment in result.segments:
            print(f"  [{segment.start:.2f}s - {segment.end:.2f}s] {segment.speaker}: {segment.text}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_streaming():
    """Example: Streaming transcription"""
    print("\n=== Example 5: Streaming Transcription ===")
    
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        service = get_speech_to_text_service()
        
        print("Streaming transcription events:")
        for event in service.transcribe_stream(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        ):
            print(f"  Event: {event}")
            
    except Exception as e:
        print(f"Error: {e}")


def example_post_processing():
    """Example: Transcription with GPT-4 post-processing"""
    print("\n=== Example 6: Post-Processing with GPT-4 ===")
    
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    # System prompt for correcting specific words/acronyms
    system_prompt = """
You are a helpful assistant for the company ZyntriQix. Your task is to correct 
any spelling discrepancies in the transcribed text. Make sure that the names of 
the following products are spelled correctly: ZyntriQix, Digique Plus, 
CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal 
Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T. Only add necessary 
punctuation such as periods, commas, and capitalization, and use only the 
context provided.
"""
    
    try:
        service = get_speech_to_text_service()
        corrected_text = service.transcribe_with_post_processing(
            audio_file=audio_file,
            system_prompt=system_prompt,
            correction_model="gpt-4o-mini",
            temperature=0.0,
        )
        
        print(f"Corrected transcription: {corrected_text}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_word_timestamps():
    """Example: Transcription with word-level timestamps"""
    print("\n=== Example 7: Word-Level Timestamps ===")
    
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        service = get_speech_to_text_service()
        result = service.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.WHISPER_1,
            response_format=ResponseFormat.VERBOSE_JSON,
            timestamp_granularities=["word"],
        )
        
        print(f"Transcription: {result.text}\n")
        if result.words:
            print("Word-level timestamps:")
            for word in result.words[:10]:  # Show first 10 words
                print(f"  {word.get('word', '')}: {word.get('start', 0):.2f}s - {word.get('end', 0):.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")


def example_convenience_function():
    """Example: Using convenience function"""
    print("\n=== Example 8: Convenience Function ===")
    
    audio_file = "path/to/your/audio.mp3"
    
    if not Path(audio_file).exists():
        print(f"⚠️ Audio file not found: {audio_file}")
        return
    
    try:
        # Simple one-liner transcription
        result = transcribe_audio(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"Transcription: {result.text}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Speech-to-Text Examples")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ Warning: OPENAI_API_KEY environment variable not set.")
        print("   Please set it before running examples.")
        print("   Example: export OPENAI_API_KEY='sk-...'")
        return
    
    # Run examples
    example_basic_transcription()
    example_transcription_with_prompt()
    example_translation()
    example_diarization()
    example_streaming()
    example_post_processing()
    example_word_timestamps()
    example_convenience_function()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
