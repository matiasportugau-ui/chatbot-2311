#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script demonstrating OpenAI Speech-to-Text API usage.

This script shows how to:
1. Transcribe audio files
2. Translate audio to English
3. Use different models and response formats
4. Stream transcriptions
5. Perform speaker diarization
6. Use prompts for better accuracy
7. Handle timestamps
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.speech_to_text import (
    SpeechToTextClient,
    TranscriptionModel,
    ResponseFormat,
    ChunkingStrategy,
    transcribe_audio,
    translate_audio,
)


def example_basic_transcription():
    """Example: Basic transcription"""
    print("\n" + "="*60)
    print("Example 1: Basic Transcription")
    print("="*60)
    
    # Replace with your audio file path
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        client = SpeechToTextClient()
        
        result = client.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"\n✅ Transcription successful!")
        print(f"Text: {result.get('text', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_transcription_with_prompt():
    """Example: Transcription with prompt for better accuracy"""
    print("\n" + "="*60)
    print("Example 2: Transcription with Prompt")
    print("="*60)
    
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        client = SpeechToTextClient()
        
        # Example prompt for a lecture about AI
        prompt = (
            "The following conversation is a lecture about the recent developments "
            "around OpenAI, GPT-4.5 and the future of AI."
        )
        
        result = client.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
            prompt=prompt,
        )
        
        print(f"\n✅ Transcription with prompt successful!")
        print(f"Text: {result.get('text', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_verbose_json_with_timestamps():
    """Example: Get detailed transcription with word-level timestamps"""
    print("\n" + "="*60)
    print("Example 3: Verbose JSON with Word Timestamps")
    print("="*60)
    
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        client = SpeechToTextClient()
        
        result = client.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.WHISPER_1,  # Only whisper-1 supports timestamps
            response_format=ResponseFormat.VERBOSE_JSON,
            timestamp_granularities=["word"],
        )
        
        print(f"\n✅ Transcription with timestamps successful!")
        print(f"Full text: {result.get('text', 'N/A')}")
        
        if 'words' in result:
            print(f"\nWord-level timestamps:")
            for word in result['words'][:10]:  # Show first 10 words
                print(f"  {word.get('word')}: {word.get('start')}s - {word.get('end')}s")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_speaker_diarization():
    """Example: Speaker diarization for meeting recordings"""
    print("\n" + "="*60)
    print("Example 4: Speaker Diarization")
    print("="*60)
    
    audio_file = input("Enter path to meeting audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    # Optional: Provide speaker reference clips
    agent_ref = input("Enter path to agent reference audio (optional, press Enter to skip): ").strip()
    
    try:
        client = SpeechToTextClient()
        
        # Prepare speaker references if provided
        known_speaker_names = None
        known_speaker_references = None
        
        if agent_ref and Path(agent_ref).exists():
            known_speaker_names = ["agent"]
            known_speaker_references = [client.to_data_url(agent_ref)]
            print(f"✅ Using speaker reference: {agent_ref}")
        
        result = client.transcribe(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE,
            response_format=ResponseFormat.DIARIZED_JSON,
            chunking_strategy=ChunkingStrategy.AUTO,
            known_speaker_names=known_speaker_names,
            known_speaker_references=known_speaker_references,
        )
        
        print(f"\n✅ Diarization successful!")
        
        if 'segments' in result:
            print(f"\nSpeaker segments:")
            for segment in result['segments']:
                speaker = segment.get('speaker', 'unknown')
                text = segment.get('text', '')
                start = segment.get('start', 0)
                end = segment.get('end', 0)
                print(f"  [{start:.2f}s - {end:.2f}s] {speaker}: {text}")
        else:
            print(f"Text: {result.get('text', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_streaming_transcription():
    """Example: Stream transcription results"""
    print("\n" + "="*60)
    print("Example 5: Streaming Transcription")
    print("="*60)
    
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        client = SpeechToTextClient()
        
        print("🔄 Streaming transcription...")
        print("(Press Ctrl+C to stop)\n")
        
        for event in client.transcribe_stream(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        ):
            event_type = event.get('type', 'unknown')
            print(f"Event: {event_type}")
            if event_type == 'transcript.text.delta':
                data = event.get('data', {})
                if isinstance(data, dict) and 'delta' in data:
                    print(f"  Delta: {data['delta']}")
            elif event_type == 'transcript.text.done':
                data = event.get('data', {})
                if isinstance(data, dict) and 'text' in data:
                    print(f"\n✅ Complete transcription: {data['text']}")
                break
    
    except KeyboardInterrupt:
        print("\n⚠️  Streaming interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_translation():
    """Example: Translate audio to English"""
    print("\n" + "="*60)
    print("Example 6: Translation to English")
    print("="*60)
    
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        client = SpeechToTextClient()
        
        result = client.translate(
            audio_file=audio_file,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"\n✅ Translation successful!")
        print(f"English text: {result.get('text', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_convenience_functions():
    """Example: Using convenience functions"""
    print("\n" + "="*60)
    print("Example 7: Convenience Functions")
    print("="*60)
    
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("⚠️  Skipping - no valid audio file provided")
        return
    
    try:
        # Using convenience function
        result = transcribe_audio(
            audio_file=audio_file,
            model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
            response_format=ResponseFormat.TEXT,
        )
        
        print(f"\n✅ Transcription using convenience function successful!")
        print(f"Text: {result.get('text', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run examples"""
    print("\n" + "="*60)
    print("OpenAI Speech-to-Text API Examples")
    print("="*60)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  or add it to your .env file")
        return
    
    print("\n✅ OpenAI API key found")
    
    examples = {
        "1": ("Basic Transcription", example_basic_transcription),
        "2": ("Transcription with Prompt", example_transcription_with_prompt),
        "3": ("Verbose JSON with Timestamps", example_verbose_json_with_timestamps),
        "4": ("Speaker Diarization", example_speaker_diarization),
        "5": ("Streaming Transcription", example_streaming_transcription),
        "6": ("Translation to English", example_translation),
        "7": ("Convenience Functions", example_convenience_functions),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n" + "-"*60)
    choice = input("Select example number (or 'all' to run all, 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("👋 Goodbye!")
        return
    
    if choice == 'all':
        for name, func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"❌ Error in {name}: {e}")
    elif choice in examples:
        name, func = examples[choice]
        func()
    else:
        print(f"❌ Invalid choice: {choice}")


if __name__ == "__main__":
    main()
