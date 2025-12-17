#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify speech-to-text module imports and basic functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from utils.speech_to_text import (
            SpeechToTextService,
            TranscriptionModel,
            ResponseFormat,
            ChunkingStrategy,
            TranscriptionResult,
            DiarizedSegment,
            DiarizedTranscriptionResult,
            get_speech_to_text_service,
            transcribe_audio,
            translate_audio,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_enums():
    """Test enum values"""
    print("\nTesting enums...")
    
    try:
        from utils.speech_to_text import TranscriptionModel, ResponseFormat, ChunkingStrategy
        
        # Test TranscriptionModel
        assert TranscriptionModel.WHISPER_1.value == "whisper-1"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE.value == "gpt-4o-transcribe"
        assert TranscriptionModel.GPT_4O_MINI_TRANSCRIBE.value == "gpt-4o-mini-transcribe"
        assert TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE.value == "gpt-4o-transcribe-diarize"
        print("✅ TranscriptionModel enum values correct")
        
        # Test ResponseFormat
        assert ResponseFormat.JSON.value == "json"
        assert ResponseFormat.TEXT.value == "text"
        assert ResponseFormat.DIARIZED_JSON.value == "diarized_json"
        print("✅ ResponseFormat enum values correct")
        
        # Test ChunkingStrategy
        assert ChunkingStrategy.AUTO.value == "auto"
        print("✅ ChunkingStrategy enum values correct")
        
        return True
    except AssertionError as e:
        print(f"❌ Enum value assertion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing enums: {e}")
        return False


def test_service_initialization():
    """Test service initialization"""
    print("\nTesting service initialization...")
    
    try:
        from utils.speech_to_text import SpeechToTextService
        import os
        
        # Test with API key from env
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            service = SpeechToTextService(api_key=api_key)
            print("✅ Service initialized with API key")
            return True
        else:
            print("⚠️ OPENAI_API_KEY not set, skipping initialization test")
            print("   (This is OK - service will fail at runtime if key is missing)")
            return True
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions exist"""
    print("\nTesting convenience functions...")
    
    try:
        from utils.speech_to_text import get_speech_to_text_service, transcribe_audio, translate_audio
        
        assert callable(get_speech_to_text_service)
        assert callable(transcribe_audio)
        assert callable(translate_audio)
        print("✅ All convenience functions exist")
        return True
    except Exception as e:
        print(f"❌ Error testing convenience functions: {e}")
        return False


def test_utils_export():
    """Test that utils module exports speech-to-text components"""
    print("\nTesting utils module exports...")
    
    try:
        from utils import (
            SpeechToTextService,
            TranscriptionModel,
            ResponseFormat,
            get_speech_to_text_service,
            transcribe_audio,
            translate_audio,
        )
        print("✅ Utils module exports speech-to-text components")
        return True
    except ImportError as e:
        print(f"❌ Utils export error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Speech-to-Text Module Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Enums", test_enums()))
    results.append(("Service Initialization", test_service_initialization()))
    results.append(("Convenience Functions", test_convenience_functions()))
    results.append(("Utils Exports", test_utils_export()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
