#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Speech-to-Text functionality
Demonstrates various features of the speech-to-text module
"""

import os
import sys
from speech_to_text import (
    SpeechToText,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity
)


def test_basic_transcription():
    """Test basic transcription"""
    print("\n" + "="*60)
    print("TEST 1: Basic Transcription")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText(model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE)
    
    # Example: You would use a real audio file here
    print("To test transcription, provide an audio file path:")
    print("  result = stt.transcribe('path/to/audio.mp3')")
    print("  print(result.text)")


def test_translation():
    """Test translation to English"""
    print("\n" + "="*60)
    print("TEST 2: Translation to English")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText()
    
    print("To test translation, provide an audio file path:")
    print("  result = stt.translate('path/to/audio.mp3')")
    print("  print(result.text)")


def test_diarization():
    """Test speaker diarization"""
    print("\n" + "="*60)
    print("TEST 3: Speaker Diarization")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText()
    
    print("To test diarization, provide an audio file path:")
    print("  segments = stt.transcribe_with_diarization(")
    print("      'meeting.wav',")
    print("      known_speakers=[")
    print("          {'name': 'agent', 'reference_audio_path': 'agent.wav'}")
    print("      ]")
    print("  )")
    print("  for segment in segments:")
    print("      print(f'{segment.speaker}: {segment.text} ({segment.start}-{segment.end})')")


def test_streaming():
    """Test streaming transcription"""
    print("\n" + "="*60)
    print("TEST 4: Streaming Transcription")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText()
    
    print("To test streaming, provide an audio file path:")
    print("  for event in stt.transcribe_streaming('audio.mp3'):")
    print("      print(event)")


def test_post_processing():
    """Test post-processing with GPT-4"""
    print("\n" + "="*60)
    print("TEST 5: Post-Processing with GPT-4")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText()
    
    print("To test post-processing, provide an audio file path:")
    print("  corrected = stt.transcribe_with_post_processing(")
    print("      'audio.mp3',")
    print("      correction_terms=['ZyntriQix', 'Digique Plus', 'GPT-3']")
    print("  )")
    print("  print(corrected)")


def test_audio_splitting():
    """Test audio file splitting"""
    print("\n" + "="*60)
    print("TEST 6: Audio File Splitting")
    print("="*60)
    
    try:
        from pydub import AudioSegment
        print("✅ pydub is available")
    except ImportError:
        print("❌ pydub not installed. Install with: pip install pydub")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Skipping test.")
        return
    
    stt = SpeechToText()
    
    print("To test audio splitting, provide an audio file path:")
    print("  chunks = stt.split_audio_file(")
    print("      'long_audio.mp3',")
    print("      output_dir='chunks',")
    print("      chunk_duration_minutes=10")
    print("  )")
    print("  print(f'Split into {len(chunks)} chunks')")


def show_usage_examples():
    """Show usage examples"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    
    examples = """
# Basic transcription
from speech_to_text import SpeechToText, TranscriptionModel

stt = SpeechToText(model=TranscriptionModel.GPT_4O_TRANSCRIBE)
result = stt.transcribe('audio.mp3')
print(result.text)

# Transcription with prompt
result = stt.transcribe(
    'lecture.mp3',
    prompt='This is a lecture about OpenAI, GPT-4, and AI developments.',
    response_format='text'
)

# Translation to English
result = stt.translate('german_audio.mp3')
print(result.text)  # Output will be in English

# Speaker diarization
segments = stt.transcribe_with_diarization(
    'meeting.wav',
    known_speakers=[
        {'name': 'agent', 'reference_audio_path': 'agent.wav'},
        {'name': 'customer', 'reference_audio_path': 'customer.wav'}
    ]
)

for segment in segments:
    print(f'{segment.speaker}: {segment.text}')

# Streaming transcription
for event in stt.transcribe_streaming('audio.mp3', include_logprobs=True):
    if event['event'] == 'transcript.text.delta':
        print(event['data'].get('delta', ''), end='', flush=True)
    elif event['event'] == 'transcript.text.done':
        print(f\"\\n\\nFull transcript: {event['data'].get('text', '')}\")

# Post-processing for accuracy
corrected = stt.transcribe_with_post_processing(
    'product_demo.mp3',
    correction_terms=['ZyntriQix', 'Digique Plus', 'GPT-3', 'DALL·E'],
    gpt_model='gpt-4o'
)

# Split large audio file
chunks = stt.split_audio_file(
    'long_recording.mp3',
    output_dir='audio_chunks',
    chunk_duration_minutes=10
)

# Transcribe each chunk
for chunk_path in chunks:
    result = stt.transcribe(chunk_path)
    print(f'{chunk_path}: {result.text[:100]}...')
"""
    
    print(examples)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SPEECH-TO-TEXT TEST SUITE")
    print("="*60)
    
    # Check environment
    print("\nEnvironment Check:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    
    try:
        from openai import OpenAI
        print("  OpenAI package: ✅ Installed")
    except ImportError:
        print("  OpenAI package: ❌ Not installed")
        print("  Install with: pip install openai")
        return
    
    # Run tests
    test_basic_transcription()
    test_translation()
    test_diarization()
    test_streaming()
    test_post_processing()
    test_audio_splitting()
    show_usage_examples()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print("\nNote: These are demonstration tests.")
    print("To run actual tests, provide audio files and uncomment the test code.")


if __name__ == "__main__":
    main()
