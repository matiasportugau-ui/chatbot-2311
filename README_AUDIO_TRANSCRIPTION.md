# 🎤 Audio-to-Text Transcription

Convert voice messages and audio files to text using OpenAI's powerful transcription models.

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='sk-your-api-key-here'
```

### 2. Run Demo

```bash
# Test the setup
python test_audio_demo.py

# Transcribe an audio file
python test_audio_demo.py your_audio.mp3
```

### 3. Basic Usage

```python
from services.audio_transcription import AudioTranscriptionService

# Create service
service = AudioTranscriptionService()

# Transcribe audio
result = service.transcribe("audio.mp3")
print(result.text)
```

## Features

- ✅ **4 Transcription Models** - From fast to high-accuracy
- ✅ **7 Audio Formats** - MP3, WAV, M4A, WebM, and more
- ✅ **WhatsApp Integration** - Auto-transcribe voice messages
- ✅ **Speaker Diarization** - Identify different speakers
- ✅ **Streaming** - Real-time transcription results
- ✅ **Translation** - Convert to English
- ✅ **Timestamps** - Word and segment-level timing
- ✅ **Custom Prompts** - Improve accuracy with context

## Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gpt-4o-mini-transcribe` | ⚡ Fast | Good | Quick transcriptions |
| `gpt-4o-transcribe` | 🐢 Medium | Excellent | High accuracy needed |
| `whisper-1` | 🐢 Medium | Good | Special formats (SRT, VTT) |
| `gpt-4o-transcribe-diarize` | 🐌 Slow | Excellent | Multiple speakers |

## Examples

### Simple Transcription

```python
from services.audio_transcription import AudioTranscriptionService

service = AudioTranscriptionService()
result = service.transcribe("meeting.mp3")
print(result.text)
```

### Spanish Voice Message

```python
from services.audio_transcription import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel
)

service = AudioTranscriptionService()
config = TranscriptionConfig(
    model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
    language="es"
)

result = service.transcribe("voz.mp3", config)
print(result.text)
```

### Speaker Identification

```python
service = AudioTranscriptionService()

result = service.transcribe_with_diarization(
    "meeting.wav",
    known_speakers={
        "Alice": "alice_voice.wav",
        "Bob": "bob_voice.wav"
    }
)

for segment in result.segments:
    print(f"{segment['speaker']}: {segment['text']}")
```

### WhatsApp Integration

```python
from python-scripts.integracion_whatsapp import IntegracionWhatsApp
from ia_conversacional_integrada import IAConversacionalIntegrada

ia = IAConversacionalIntegrada()
whatsapp = IntegracionWhatsApp(ia, enable_audio=True)
whatsapp.iniciar_servidor()
```

Now voice messages are automatically transcribed!

## Configuration

Edit `config/audio_config.json`:

```json
{
  "audio_transcription": {
    "enabled": true,
    "default_model": "gpt-4o-mini-transcribe",
    "whatsapp": {
      "auto_transcribe": true,
      "auto_reply": true
    }
  }
}
```

## Documentation

📚 **Full Documentation:** [docs/AUDIO_TO_TEXT_GUIDE.md](docs/AUDIO_TO_TEXT_GUIDE.md)

Includes:
- Complete API reference
- Advanced examples
- Troubleshooting guide
- Best practices
- Configuration options

## Testing

```bash
# Run test suite
pytest tests/test_audio_transcription.py -v

# Run demo
python test_audio_demo.py
```

## File Structure

```
services/
├── audio_transcription.py       # Main transcription service
├── whatsapp_audio_handler.py    # WhatsApp integration
└── audio_config_loader.py       # Configuration loader

utils/
└── audio_utils.py               # File management utilities

config/
└── audio_config.json            # Configuration file

tests/
└── test_audio_transcription.py  # Test suite

docs/
└── AUDIO_TO_TEXT_GUIDE.md       # Complete documentation
```

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies in `requirements.txt`

## Supported Formats

- MP3 (`.mp3`)
- MP4 Audio (`.mp4`, `.m4a`, `.mpga`)
- MPEG (`.mpeg`)
- WAV (`.wav`)
- WebM (`.webm`)

Max file size: **25 MB** (automatic chunking available for larger files)

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (for WhatsApp)
WHATSAPP_TOKEN=your-token
WHATSAPP_PHONE_ID=your-phone-id
WEBHOOK_VERIFY_TOKEN=your-verify-token
```

## Troubleshooting

### API Key Not Found

```bash
# Set environment variable
export OPENAI_API_KEY='sk-your-key-here'

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### File Too Large

```python
from utils.audio_utils import AudioChunker

chunker = AudioChunker(max_chunk_size_mb=24)
chunks = chunker.chunk_audio_file("large_audio.mp3")

for chunk in chunks:
    result = service.transcribe(chunk)
    print(result.text)
```

### Poor Quality

- Use `gpt-4o-transcribe` for better accuracy
- Add context with `prompt` parameter
- Specify correct `language`

## Performance

| Model | Speed | Cost | Accuracy |
|-------|-------|------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ | $ | ⭐⭐⭐ |
| `gpt-4o` | ⚡⚡ | $$ | ⭐⭐⭐⭐ |
| `whisper-1` | ⚡⚡ | $ | ⭐⭐⭐ |
| `diarize` | ⚡ | $$$ | ⭐⭐⭐⭐⭐ |

## Contributing

Contributions welcome! Please:
1. Test your changes
2. Update documentation
3. Follow existing code style

## License

Part of the BMC Uruguay chatbot system.

## Support

- 📖 Documentation: [docs/AUDIO_TO_TEXT_GUIDE.md](docs/AUDIO_TO_TEXT_GUIDE.md)
- 🧪 Tests: `tests/test_audio_transcription.py`
- 🎯 Demo: `test_audio_demo.py`

---

**Ready to transcribe?** Run `python test_audio_demo.py` to get started!
