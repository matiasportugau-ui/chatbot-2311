# Audio-to-Text Transcription Guide

Complete guide for using audio transcription features in the chatbot system.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Setup](#setup)
4. [Usage](#usage)
5. [WhatsApp Integration](#whatsapp-integration)
6. [Configuration](#configuration)
7. [API Reference](#api-reference)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The audio-to-text transcription system integrates OpenAI's powerful audio transcription models to convert voice messages and audio files into text. This feature is fully integrated with the WhatsApp chatbot, allowing automatic transcription of voice messages.

### Supported Models

| Model | Description | Best For |
|-------|-------------|----------|
| `whisper-1` | Legacy Whisper model | General purpose, all output formats |
| `gpt-4o-transcribe` | High-quality GPT-4o | Accurate transcriptions |
| `gpt-4o-mini-transcribe` | Fast and cost-effective | Quick processing, lower cost |
| `gpt-4o-transcribe-diarize` | Speaker identification | Meetings, multiple speakers |

### Supported Audio Formats

- MP3 (`.mp3`)
- MP4 Audio (`.mp4`, `.m4a`)
- MPEG (`.mpeg`, `.mpga`)
- WAV (`.wav`)
- WebM (`.webm`)

### Limitations

- Maximum file size: **25 MB**
- For files larger than 25MB, automatic chunking is available

---

## Features

### ✅ Core Features

- **Multiple Models**: Choose from 4 different transcription models
- **Multiple Formats**: Support for all major audio formats
- **Streaming**: Real-time transcription results
- **Timestamps**: Word-level and segment-level timestamps
- **Speaker Diarization**: Identify and label different speakers
- **Translation**: Translate audio to English (Whisper-1 only)
- **Custom Prompts**: Improve accuracy with context
- **WhatsApp Integration**: Automatic voice message transcription

### 🎯 Advanced Features

- **Chunking**: Automatic splitting of large files
- **Caching**: Avoid re-transcribing same files
- **Error Handling**: Robust retry logic
- **File Management**: Automatic cleanup of temporary files
- **Configuration**: Flexible JSON-based configuration
- **Logging**: Comprehensive logging and monitoring

---

## Setup

### 1. Prerequisites

```bash
# Python 3.8 or higher required
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-api-key-here

# WhatsApp Configuration (for WhatsApp integration)
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_ID=your-phone-id
WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### 3. Verify Setup

Run the demo script to verify everything is working:

```bash
python test_audio_demo.py
```

---

## Usage

### Basic Transcription

```python
from services.audio_transcription import AudioTranscriptionService

# Initialize service
service = AudioTranscriptionService()

# Transcribe audio file
result = service.transcribe("audio.mp3")

print(result.text)
```

### With Configuration

```python
from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat
)

# Create service
service = AudioTranscriptionService()

# Configure transcription
config = TranscriptionConfig(
    model=TranscriptionModel.GPT4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
    language="es",  # Spanish
    prompt="Transcribe este mensaje de voz en español"
)

# Transcribe
result = service.transcribe("voice_message.mp3", config)
print(result.text)
```

### Streaming Transcription

```python
config = TranscriptionConfig(
    model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
    stream=True
)

result = service.transcribe("audio.mp3", config)
print(result.text)
```

### Speaker Diarization

```python
# Transcribe with speaker identification
result = service.transcribe_with_diarization(
    "meeting.wav",
    known_speakers={
        "agent": "agent_voice_sample.wav",
        "customer": "customer_voice_sample.wav"
    }
)

# Access speaker segments
for segment in result.segments:
    print(f"{segment['speaker']}: {segment['text']}")
```

### Translation to English

```python
# Translate non-English audio to English
result = service.translate("spanish_audio.mp3")
print(result.text)  # Text in English
```

---

## WhatsApp Integration

### Automatic Voice Message Transcription

The WhatsApp integration automatically transcribes voice messages:

```python
from python-scripts.integracion_whatsapp import IntegracionWhatsApp
from ia_conversacional_integrada import IAConversacionalIntegrada

# Create IA instance
ia = IAConversacionalIntegrada()

# Create WhatsApp integration with audio support
whatsapp = IntegracionWhatsApp(ia, enable_audio=True)

# Start server
whatsapp.iniciar_servidor()
```

When a user sends a voice message:
1. Audio is automatically downloaded from WhatsApp
2. Audio is transcribed using configured model
3. Transcription is processed by the IA
4. Response is sent back to the user

### Manual Audio Processing

```python
from services.whatsapp_audio_handler import create_whatsapp_audio_integration

# Create integration
integration = create_whatsapp_audio_integration()

# Process webhook message
transcribed_text = integration.handle_webhook_message(
    message_data,
    custom_handler=lambda phone, text, msg: print(f"From {phone}: {text}")
)
```

---

## Configuration

### Configuration File

Edit `config/audio_config.json` to customize behavior:

```json
{
  "audio_transcription": {
    "enabled": true,
    "default_model": "gpt-4o-mini-transcribe",
    "whatsapp": {
      "enabled": true,
      "auto_transcribe": true,
      "auto_reply": true,
      "model_preference": "gpt-4o-mini-transcribe"
    },
    "processing": {
      "temperature": 0.0,
      "language": "es",
      "enable_prompts": true,
      "default_prompt": "Transcribe el siguiente mensaje"
    }
  }
}
```

### Load Configuration

```python
from services.audio_config_loader import load_audio_config, load_whatsapp_config

# Load audio configuration
audio_config = load_audio_config()

# Load WhatsApp configuration
whatsapp_config = load_whatsapp_config()
```

---

## API Reference

### AudioTranscriptionService

Main service for audio transcription.

#### Methods

##### `transcribe(audio_file_path, config=None)`

Transcribe audio file to text.

**Parameters:**
- `audio_file_path` (str|Path): Path to audio file
- `config` (TranscriptionConfig, optional): Transcription configuration

**Returns:**
- `TranscriptionResult`: Result with transcribed text

**Example:**
```python
result = service.transcribe("audio.mp3")
```

##### `translate(audio_file_path, model="whisper-1", ...)`

Translate audio to English.

**Parameters:**
- `audio_file_path` (str|Path): Path to audio file
- `model` (str): Translation model (default: "whisper-1")
- `prompt` (str, optional): Context prompt
- `response_format` (str): Output format (default: "json")
- `temperature` (float): Sampling temperature (default: 0.0)

**Returns:**
- `TranscriptionResult`: Result with translated text

##### `transcribe_with_diarization(audio_file_path, known_speakers=None, prompt=None)`

Transcribe with speaker identification.

**Parameters:**
- `audio_file_path` (str|Path): Path to audio file
- `known_speakers` (dict, optional): Map of speaker names to reference audio files
- `prompt` (str, optional): Context prompt

**Returns:**
- `TranscriptionResult`: Result with speaker-labeled segments

##### `transcribe_with_timestamps(audio_file_path, granularity="word", prompt=None)`

Transcribe with word or segment timestamps.

**Parameters:**
- `audio_file_path` (str|Path): Path to audio file
- `granularity` (str): "word" or "segment"
- `prompt` (str, optional): Context prompt

**Returns:**
- `TranscriptionResult`: Result with timestamp information

### TranscriptionConfig

Configuration for transcription.

**Attributes:**
- `model` (TranscriptionModel): Model to use
- `response_format` (ResponseFormat): Output format
- `language` (str, optional): Language code (e.g., "es", "en")
- `prompt` (str, optional): Context prompt
- `temperature` (float): Sampling temperature (0.0-1.0)
- `timestamp_granularities` (list, optional): Timestamp levels
- `chunking_strategy` (ChunkingStrategy, optional): For diarization
- `stream` (bool): Enable streaming (default: False)

### TranscriptionResult

Result from transcription.

**Attributes:**
- `text` (str): Transcribed text
- `model` (str): Model used
- `duration` (float, optional): Audio duration
- `language` (str, optional): Detected language
- `segments` (list, optional): Speaker segments (diarization)
- `words` (list, optional): Word-level timestamps
- `confidence` (float, optional): Confidence score

---

## Examples

### Example 1: Basic Transcription

```python
from services.audio_transcription import AudioTranscriptionService

service = AudioTranscriptionService()
result = service.transcribe("meeting.mp3")
print(result.text)
```

### Example 2: Spanish Voice Message

```python
from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel
)

service = AudioTranscriptionService()

config = TranscriptionConfig(
    model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
    language="es",
    prompt="Mensaje de voz de WhatsApp en español"
)

result = service.transcribe("whatsapp_voice.opus", config)
print(f"Transcripción: {result.text}")
```

### Example 3: Meeting with Speaker Labels

```python
service = AudioTranscriptionService()

result = service.transcribe_with_diarization(
    "meeting.wav",
    known_speakers={
        "manager": "manager_sample.wav",
        "developer": "developer_sample.wav"
    },
    prompt="Meeting discussion about project timeline"
)

# Print conversation
for segment in result.segments:
    speaker = segment['speaker']
    text = segment['text']
    start = segment['start']
    end = segment['end']
    print(f"[{start:.1f}s - {end:.1f}s] {speaker}: {text}")
```

### Example 4: Batch Processing

```python
from pathlib import Path
from services.audio_transcription import AudioTranscriptionService

service = AudioTranscriptionService()

# Process all audio files in directory
audio_dir = Path("audio_files")
results = {}

for audio_file in audio_dir.glob("*.mp3"):
    print(f"Processing {audio_file.name}...")
    result = service.transcribe(audio_file)
    results[audio_file.name] = result.text

# Save results
import json
with open("transcriptions.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

### Example 5: WhatsApp Integration with Custom Handler

```python
from services.whatsapp_audio_handler import create_whatsapp_audio_integration

def process_transcription(phone_number, transcribed_text, message_data):
    """Custom handler for transcriptions"""
    print(f"📱 Received from {phone_number}")
    print(f"📝 Text: {transcribed_text}")
    
    # Save to database, process with AI, etc.
    # ...

# Create integration
integration = create_whatsapp_audio_integration(auto_reply=False)

# Process message with custom handler
integration.handle_webhook_message(
    message_data,
    custom_handler=process_transcription
)
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:** `ValueError: OpenAI API key is required`

**Solution:**
```bash
# Set environment variable
export OPENAI_API_KEY='sk-your-key-here'

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

#### 2. Unsupported Audio Format

**Error:** `ValueError: Unsupported audio format`

**Solution:**
- Convert audio to supported format (mp3, wav, m4a, etc.)
- Check file extension matches actual format
- Use `ffmpeg` for conversion if needed

#### 3. File Too Large

**Error:** `ValueError: Audio file too large`

**Solution:**
```python
from utils.audio_utils import AudioChunker

# Automatically chunk large files
chunker = AudioChunker(max_chunk_size_mb=24)
chunks = chunker.chunk_audio_file("large_audio.mp3")

# Transcribe each chunk
for chunk in chunks:
    result = service.transcribe(chunk)
    print(result.text)
```

#### 4. WhatsApp Audio Not Downloading

**Error:** Download fails or times out

**Solution:**
- Check WhatsApp token is valid
- Verify network connectivity
- Ensure WhatsApp media URL hasn't expired (URLs expire after ~15 minutes)
- Check file size limits

#### 5. Poor Transcription Quality

**Solutions:**
- Use higher quality model (GPT-4o instead of GPT-4o-mini)
- Add context with prompt parameter
- Ensure audio quality is good
- Specify correct language
- Use appropriate model for use case

### Debug Mode

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Performance Tips

1. **Use appropriate model:**
   - `gpt-4o-mini-transcribe`: Fast, cost-effective
   - `gpt-4o-transcribe`: High accuracy
   - `whisper-1`: When you need special formats (SRT, VTT)

2. **Optimize file size:**
   - Compress audio files when possible
   - Use efficient formats (opus, mp3)
   - Remove silence from recordings

3. **Batch processing:**
   - Process multiple files in parallel
   - Use async/await for concurrent requests

4. **Caching:**
   - Cache transcriptions by file hash
   - Avoid re-transcribing same files

---

## Best Practices

### 1. Error Handling

Always wrap transcription calls in try-except:

```python
try:
    result = service.transcribe(audio_file)
    print(result.text)
except FileNotFoundError:
    print("Audio file not found")
except ValueError as e:
    print(f"Invalid audio file: {e}")
except Exception as e:
    print(f"Transcription error: {e}")
```

### 2. File Cleanup

Clean up temporary files after processing:

```python
from utils.audio_utils import AudioFileManager

manager = AudioFileManager()

# Process audio
audio_path = manager.save_audio_from_bytes(audio_data, 'mp3')
result = service.transcribe(audio_path)

# Clean up
manager.delete_file(audio_path)
```

### 3. Configuration Management

Use configuration files instead of hardcoding:

```python
from services.audio_config_loader import load_audio_config

config = load_audio_config()

# Use config values
service = AudioTranscriptionService()
result = service.transcribe(
    audio_file,
    TranscriptionConfig(
        model=config.default_model,
        temperature=config.temperature
    )
)
```

### 4. Monitoring

Log all transcriptions for monitoring:

```python
import logging

logger = logging.getLogger(__name__)

result = service.transcribe(audio_file)
logger.info(f"Transcribed {audio_file}: {len(result.text)} chars")
```

---

## Additional Resources

### Documentation

- [OpenAI Audio API Docs](https://platform.openai.com/docs/guides/speech-to-text)
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)

### Related Files

- `services/audio_transcription.py` - Main transcription service
- `services/whatsapp_audio_handler.py` - WhatsApp integration
- `utils/audio_utils.py` - Audio utilities
- `config/audio_config.json` - Configuration file
- `tests/test_audio_transcription.py` - Test suite

### Support

For issues or questions:
1. Check this documentation
2. Review test files for examples
3. Check logs for error messages
4. Consult OpenAI API documentation

---

## Version History

- **v1.0.0** (2024-12) - Initial release
  - Support for all OpenAI transcription models
  - WhatsApp integration
  - Configuration system
  - Comprehensive error handling
  - Test suite and documentation

---

*Last updated: December 2024*
