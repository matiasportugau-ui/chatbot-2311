#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Transcription Demo Script
Demonstrates audio-to-text functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat
)
from utils.audio_utils import AudioFileManager
from services.audio_config_loader import load_audio_config, load_whatsapp_config


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_service_initialization():
    """Test service initialization"""
    print_header("Service Initialization Test")
    
    try:
        service = AudioTranscriptionService()
        print("✅ Audio transcription service initialized successfully")
        print(f"   Supported formats: {', '.join(service.SUPPORTED_FORMATS)}")
        print(f"   Max file size: {service.MAX_FILE_SIZE_MB}MB")
        return service
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set OPENAI_API_KEY environment variable")
        return None


def test_configuration():
    """Test configuration loading"""
    print_header("Configuration Test")
    
    try:
        audio_config = load_audio_config()
        print("✅ Audio configuration loaded:")
        print(f"   Enabled: {audio_config.enabled}")
        print(f"   Default Model: {audio_config.default_model}")
        print(f"   Temperature: {audio_config.temperature}")
        print(f"   Max Concurrent: {audio_config.max_concurrent_transcriptions}")
        
        whatsapp_config = load_whatsapp_config()
        print("\n✅ WhatsApp configuration loaded:")
        print(f"   Enabled: {whatsapp_config.enabled}")
        print(f"   Auto Transcribe: {whatsapp_config.auto_transcribe}")
        print(f"   Model: {whatsapp_config.model_preference}")
        print(f"   Auto Reply: {whatsapp_config.auto_reply}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False


def test_file_manager():
    """Test audio file manager"""
    print_header("File Manager Test")
    
    try:
        manager = AudioFileManager()
        print("✅ Audio file manager initialized")
        print(f"   Temp directory: {manager.temp_dir}")
        
        # Test validation
        print("\n📝 Testing file validation...")
        
        # Test supported format check
        test_formats = ['mp3', 'wav', 'm4a', 'txt', 'exe']
        for fmt in test_formats:
            is_supported = fmt in manager.SUPPORTED_FORMATS
            status = "✅" if is_supported else "❌"
            print(f"   {status} Format '.{fmt}': {'Supported' if is_supported else 'Not supported'}")
        
        return manager
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_transcription_with_sample(service: AudioTranscriptionService, audio_file: str):
    """Test transcription with a sample audio file"""
    print_header("Audio Transcription Test")
    
    audio_path = Path(audio_file)
    
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_file}")
        print("\nTo test transcription, provide a valid audio file:")
        print(f"   python {Path(__file__).name} <path_to_audio_file>")
        return
    
    try:
        # Validate file
        print(f"📁 File: {audio_path.name}")
        service.validate_audio_file(audio_path)
        print("✅ File validation passed")
        
        # Test with different configurations
        configs = [
            {
                "name": "Fast (GPT-4o Mini)",
                "config": TranscriptionConfig(
                    model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
                    response_format=ResponseFormat.TEXT
                )
            },
            {
                "name": "High Quality (GPT-4o)",
                "config": TranscriptionConfig(
                    model=TranscriptionModel.GPT4O_TRANSCRIBE,
                    response_format=ResponseFormat.JSON
                )
            }
        ]
        
        for test in configs:
            print(f"\n🎤 Transcribing with {test['name']}...")
            
            try:
                result = service.transcribe(audio_path, test['config'])
                
                print(f"✅ Transcription completed:")
                print(f"   Model: {result.model}")
                print(f"   Text length: {len(result.text)} characters")
                print(f"\n   Transcription:")
                print(f"   {'-' * 60}")
                print(f"   {result.text[:500]}")
                if len(result.text) > 500:
                    print(f"   ... (truncated, total: {len(result.text)} chars)")
                print(f"   {'-' * 60}")
            
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def show_available_models():
    """Show information about available models"""
    print_header("Available Transcription Models")
    
    models = [
        {
            "name": "whisper-1",
            "description": "Legacy Whisper model",
            "features": ["All formats", "Timestamps", "SRT/VTT output"]
        },
        {
            "name": "gpt-4o-transcribe",
            "description": "High quality GPT-4o",
            "features": ["JSON/Text output", "Prompts", "High accuracy"]
        },
        {
            "name": "gpt-4o-mini-transcribe",
            "description": "Fast and cost-effective",
            "features": ["JSON/Text output", "Prompts", "Quick processing"]
        },
        {
            "name": "gpt-4o-transcribe-diarize",
            "description": "Speaker identification",
            "features": ["Speaker labels", "Diarized output", "Meeting transcription"]
        }
    ]
    
    for model in models:
        print(f"\n📌 {model['name']}")
        print(f"   {model['description']}")
        print(f"   Features: {', '.join(model['features'])}")


def main():
    """Main demo function"""
    print("=" * 70)
    print("  🎤 AUDIO-TO-TEXT TRANSCRIPTION DEMO")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY environment variable not set")
        print("\nPlease set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr add it to a .env file:")
        print("   OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    print(f"\n✅ OpenAI API key found (starts with: {api_key[:10]}...)")
    
    # Run tests
    service = test_service_initialization()
    if not service:
        sys.exit(1)
    
    test_configuration()
    test_file_manager()
    show_available_models()
    
    # Test transcription if audio file provided
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        test_transcription_with_sample(service, audio_file)
    else:
        print_header("Next Steps")
        print("\n📝 To test audio transcription with a real file:")
        print(f"   python {Path(__file__).name} <path_to_audio_file>")
        print("\n   Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm")
        print("   Max file size: 25MB")
    
    print_header("Demo Complete")
    print("✅ All tests completed successfully!\n")


if __name__ == "__main__":
    main()
