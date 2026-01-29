#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Audio Integrator
Generates a dummy WAV file and tests the transcription API.
"""

import os
import wave
import struct
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from audio_integrator import AudioIntegrator, AudioModel, AudioResponseFormat

def create_dummy_wav(filename: str, duration: float = 1.0):
    """Create a dummy WAV file with a simple tone"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        # Generate a 440Hz sine wave
        for i in range(n_samples):
            value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)
            
    print(f"Created dummy audio file: {filename}")

def main():
    print("=" * 60)
    print("Audio Transcription Test")
    print("=" * 60)
    
    # Initialize integrator
    integrator = AudioIntegrator()
    if not integrator.client:
        print("❌ OpenAI client not initialized. Skipping test.")
        return

    # Create a test file
    test_file = "test_audio.wav"
    try:
        create_dummy_wav(test_file, duration=2.0)
        
        # Test standard transcription
        print(f"\n🧪 Testing transcription with {AudioModel.WHISPER_1}...")
        try:
            result = integrator.transcribe(
                test_file,
                model=AudioModel.WHISPER_1,
                response_format=AudioResponseFormat.JSON
            )
            print("✅ Success!")
            print(f"   Result type: {type(result)}")
            if hasattr(result, 'text'):
                print(f"   Transcript: {result.text}")
            else:
                print(f"   Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Test GPT-4o transcription (if available)
        print(f"\n🧪 Testing transcription with {AudioModel.GPT_4O_MINI_TRANSCRIBE}...")
        try:
            result = integrator.transcribe(
                test_file,
                model=AudioModel.GPT_4O_MINI_TRANSCRIBE,
                response_format=AudioResponseFormat.TEXT
            )
            print("✅ Success!")
            print(f"   Transcript: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up {test_file}")

if __name__ == "__main__":
    main()
