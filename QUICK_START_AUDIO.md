# 🚀 Quick Start: Audio-to-Text Transcription

Get started with audio transcription in 5 minutes!

## Prerequisites

- Python 3.8+
- OpenAI API key

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set API Key

### Option A: Environment Variable

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

### Option B: .env File

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## Step 3: Test the Setup

```bash
python test_audio_demo.py
```

You should see:
```
✅ Audio transcription service initialized successfully
✅ Audio configuration loaded
✅ Audio file manager initialized
```

## Step 4: Transcribe Your First Audio

### Using Python Script

```python
from services.audio_transcription import AudioTranscriptionService

# Initialize
service = AudioTranscriptionService()

# Transcribe
result = service.transcribe("your_audio.mp3")

# Print result
print(result.text)
```

### Using Command Line

```bash
python test_audio_demo.py your_audio.mp3
```

## Step 5: Enable WhatsApp Integration (Optional)

### Set WhatsApp Credentials

Add to your `.env` file:

```bash
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_ID=your-phone-id
WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### Start WhatsApp Server

```python
from python-scripts.integracion_whatsapp import IntegracionWhatsApp
from ia_conversacional_integrada import IAConversacionalIntegrada

# Initialize
ia = IAConversacionalIntegrada()
whatsapp = IntegracionWhatsApp(ia, enable_audio=True)

# Start server
whatsapp.iniciar_servidor()
```

Now voice messages will be automatically transcribed!

## Common Use Cases

### 1. Quick Transcription

```python
from services import AudioTranscriptionService

service = AudioTranscriptionService()
result = service.transcribe("audio.mp3")
print(result.text)
```

### 2. Spanish Audio

```python
from services import (
    AudioTranscriptionService,
    TranscriptionConfig,
    TranscriptionModel
)

service = AudioTranscriptionService()
config = TranscriptionConfig(
    model=TranscriptionModel.GPT4O_MINI_TRANSCRIBE,
    language="es"
)

result = service.transcribe("audio_es.mp3", config)
print(result.text)
```

### 3. Meeting with Speakers

```python
from services import AudioTranscriptionService

service = AudioTranscriptionService()
result = service.transcribe_with_diarization(
    "meeting.wav",
    known_speakers={
        "manager": "manager_voice.wav",
        "developer": "dev_voice.wav"
    }
)

for segment in result.segments:
    print(f"{segment['speaker']}: {segment['text']}")
```

### 4. Batch Processing

```python
from pathlib import Path
from services import AudioTranscriptionService

service = AudioTranscriptionService()
audio_dir = Path("audio_files")

for audio_file in audio_dir.glob("*.mp3"):
    result = service.transcribe(audio_file)
    print(f"{audio_file.name}: {result.text[:100]}...")
```

## Troubleshooting

### Issue: API Key Not Found

```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set it if missing
export OPENAI_API_KEY='sk-your-key-here'
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install openai python-dotenv
```

### Issue: File Format Not Supported

Supported formats: MP3, WAV, M4A, MP4, MPEG, MPGA, WebM

Convert your file:
```bash
# Using ffmpeg
ffmpeg -i input.ogg output.mp3
```

### Issue: File Too Large

Maximum file size is 25MB. For larger files:

```python
from utils.audio_utils import AudioChunker

chunker = AudioChunker(max_chunk_size_mb=24)
chunks = chunker.chunk_audio_file("large_file.mp3")

for chunk in chunks:
    result = service.transcribe(chunk)
    print(result.text)
```

## Next Steps

1. **Read Full Documentation**: [docs/AUDIO_TO_TEXT_GUIDE.md](docs/AUDIO_TO_TEXT_GUIDE.md)
2. **Explore Examples**: Check `test_audio_demo.py` for more examples
3. **Run Tests**: `pytest tests/test_audio_transcription.py -v`
4. **Configure**: Edit `config/audio_config.json` for custom settings

## Getting Help

- 📖 Full docs: [docs/AUDIO_TO_TEXT_GUIDE.md](docs/AUDIO_TO_TEXT_GUIDE.md)
- 🧪 Test suite: `tests/test_audio_transcription.py`
- 🎯 Demo: `test_audio_demo.py`
- 📝 README: [README_AUDIO_TRANSCRIPTION.md](README_AUDIO_TRANSCRIPTION.md)

## Tips

1. **Use Fast Model for Testing**: `gpt-4o-mini-transcribe` is fast and cheap
2. **Add Prompts for Accuracy**: Provide context about the audio content
3. **Specify Language**: Set `language="es"` for better Spanish transcription
4. **Monitor Costs**: Check your OpenAI usage dashboard

## Example Project Structure

```
your-project/
├── audio_files/           # Place audio files here
│   ├── meeting.mp3
│   └── voice_message.wav
├── .env                   # API keys
├── test_transcribe.py     # Your script
└── transcriptions/        # Save results here
```

Example script (`test_transcribe.py`):

```python
from pathlib import Path
from services import AudioTranscriptionService
import json

# Initialize service
service = AudioTranscriptionService()

# Process all audio files
audio_dir = Path("audio_files")
results = {}

for audio_file in audio_dir.glob("*"):
    if audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a']:
        print(f"Processing {audio_file.name}...")
        result = service.transcribe(audio_file)
        results[audio_file.name] = result.text

# Save results
output_dir = Path("transcriptions")
output_dir.mkdir(exist_ok=True)

with open(output_dir / "results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Processed {len(results)} files")
```

---

**Ready to go?** Run `python test_audio_demo.py` and start transcribing!
