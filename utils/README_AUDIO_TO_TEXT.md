# Audio to Text Module

Comprehensive speech-to-text processing using OpenAI's Audio API.

## Quick Start

```python
from utils.audio_to_text import AudioToTextProcessor, TranscriptionConfig, TranscriptionModel, ResponseFormat

# Initialize processor
processor = AudioToTextProcessor()

# Transcribe audio
config = TranscriptionConfig(
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)
result = processor.transcribe("audio.mp3", config)
print(result.text)
```

## CLI Usage

```bash
# Basic transcription
python scripts/audio_to_text_cli.py audio.mp3

# With options
python scripts/audio_to_text_cli.py audio.mp3 --model gpt-4o-transcribe --output transcript.txt
```

## Features

- ✅ Basic transcriptions
- ✅ Translations to English
- ✅ Speaker diarization
- ✅ Word-level timestamps
- ✅ Streaming transcriptions
- ✅ Prompting for accuracy
- ✅ Post-processing with GPT-4
- ✅ Audio file splitting

## Documentation

See `docs/SPEECH_TO_TEXT_GUIDE.md` for complete documentation.

## Examples

See `python-scripts/audio_to_text_example.py` for usage examples.

## Requirements

- `openai>=1.0.0`
- `pydub` (optional, for audio splitting)
