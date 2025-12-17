# Audio to Text Processing

This module provides comprehensive speech-to-text functionality using OpenAI's Audio API.

## Features

- **Transcription** with multiple model support:
  - `whisper-1` - Open source Whisper model
  - `gpt-4o-transcribe` - Higher quality GPT-4o based model
  - `gpt-4o-mini-transcribe` - Faster, cost-effective variant
  - `gpt-4o-transcribe-diarize` - Speaker diarization support

- **Speaker Diarization** - Identify different speakers in audio
- **Translation** - Translate audio from any language to English
- **Streaming** - Receive transcription results in real-time
- **Long Audio Handling** - Automatic chunking for files > 25 MB
- **Post-processing** - Improve accuracy with GPT-4 correction

## Installation

```bash
# Install dependencies
pip install openai>=1.0.0 pydub>=0.25.1

# For audio format conversion (optional but recommended)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Quick Start

### Basic Transcription

```python
from audio_to_text import AudioToText

processor = AudioToText()
result = processor.transcribe("audio.mp3")
print(result.text)
```

### With Convenience Functions

```python
from audio_to_text import transcribe, translate

# Simple transcription
text = transcribe("recording.mp3")

# Translation to English
english_text = translate("german_audio.mp3")
```

## Supported Formats

- `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`
- Maximum file size: 25 MB per request

## Models Comparison

| Model | Speed | Quality | Features |
|-------|-------|---------|----------|
| `whisper-1` | Fast | Good | Timestamps, VTT/SRT output |
| `gpt-4o-mini-transcribe` | Fast | Better | Streaming, Prompts |
| `gpt-4o-transcribe` | Medium | Best | Streaming, Prompts |
| `gpt-4o-transcribe-diarize` | Slower | Best | Speaker labels |

## API Reference

### AudioToText Class

```python
class AudioToText:
    def __init__(self, api_key: Optional[str] = None)
```

Creates a new audio processor instance.

**Parameters:**
- `api_key` - OpenAI API key (defaults to `OPENAI_API_KEY` env variable)

### transcribe()

```python
def transcribe(
    file_path: str,
    model: str = "gpt-4o-transcribe",
    response_format: str = "json",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    temperature: float = 0.0,
    timestamp_granularities: Optional[List[str]] = None,
) -> TranscriptionResult
```

Transcribe an audio file to text.

**Parameters:**
- `file_path` - Path to the audio file
- `model` - Transcription model to use
- `response_format` - Output format (`json`, `text`, `srt`, `verbose_json`, `vtt`)
- `language` - ISO 639-1 language code
- `prompt` - Guide transcription with context
- `temperature` - Sampling temperature (0-1)
- `timestamp_granularities` - `["word"]` and/or `["segment"]` (whisper-1 only)

**Returns:** `TranscriptionResult` with `.text`, `.segments`, `.words`, `.language`, `.duration`

### transcribe_with_diarization()

```python
def transcribe_with_diarization(
    file_path: str,
    chunking_strategy: str = "auto",
    known_speaker_names: Optional[List[str]] = None,
    known_speaker_references: Optional[List[str]] = None,
    response_format: str = "diarized_json",
) -> TranscriptionResult
```

Transcribe with speaker identification.

**Parameters:**
- `file_path` - Path to the audio file
- `chunking_strategy` - `"auto"` or VAD configuration
- `known_speaker_names` - Up to 4 speaker names
- `known_speaker_references` - Data URLs for speaker reference clips (2-10 seconds)

**Returns:** `TranscriptionResult` with speaker-labeled segments

### translate()

```python
def translate(
    file_path: str,
    response_format: str = "json",
    prompt: Optional[str] = None,
    temperature: float = 0.0,
) -> TranscriptionResult
```

Translate audio to English text. Uses `whisper-1` model.

### transcribe_stream()

```python
def transcribe_stream(
    file_path: str,
    model: str = "gpt-4o-mini-transcribe",
    response_format: str = "text",
    prompt: Optional[str] = None,
    include_logprobs: bool = False,
) -> Generator[Dict[str, Any], None, None]
```

Stream transcription results as they become available.

**Note:** Not supported for `whisper-1`.

### transcribe_with_timestamps()

```python
def transcribe_with_timestamps(
    file_path: str,
    granularities: List[str] = ["word"],
    language: Optional[str] = None,
    prompt: Optional[str] = None,
) -> TranscriptionResult
```

Get word or segment-level timestamps (whisper-1 only).

### correct_transcription()

```python
def correct_transcription(
    transcribed_text: str,
    correction_context: str,
    model: str = "gpt-4.1",
    temperature: float = 0.0,
) -> str
```

Post-process transcription using GPT-4 for improved accuracy.

## Examples

### Speaker Diarization

```python
from audio_to_text import AudioToText

processor = AudioToText()

result = processor.transcribe_with_diarization(
    "meeting.wav",
    chunking_strategy="auto",
    known_speaker_names=["Alice", "Bob"],
    known_speaker_references=[
        processor._to_data_url("alice_ref.wav"),
        processor._to_data_url("bob_ref.wav")
    ]
)

for segment in result.segments:
    print(f"{segment.speaker}: {segment.text}")
```

### Streaming Transcription

```python
from audio_to_text import AudioToText

processor = AudioToText()

for event in processor.transcribe_stream("audio.mp3"):
    data = event.get("data")
    if hasattr(data, "delta"):
        print(data.delta, end="", flush=True)
```

### Word-Level Timestamps

```python
from audio_to_text import AudioToText

processor = AudioToText()

result = processor.transcribe_with_timestamps(
    "audio.mp3",
    granularities=["word", "segment"]
)

for word in result.words:
    print(f"{word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
```

### Long Audio Files (> 25 MB)

```python
from audio_chunker import LongAudioTranscriber

transcriber = LongAudioTranscriber()

text = transcriber.transcribe_long_audio(
    "long_meeting.mp3",
    model="gpt-4o-transcribe",
    chunk_duration_minutes=10
)

print(text)
```

### Post-Processing for Accuracy

```python
from audio_to_text import AudioToText

processor = AudioToText()

# Raw transcription
result = processor.transcribe("audio.mp3", model="whisper-1")

# Correction context
context = """
You are a helpful assistant for BMC Uruguay. Correct spelling for:
Products: Isodec, Poliestireno, Lana de Roca
Terms: aislamiento térmico, cotización
Only correct spelling, don't add information.
"""

corrected = processor.correct_transcription(result.text, context)
print(corrected)
```

### With Prompt for Better Accuracy

```python
from audio_to_text import AudioToText

processor = AudioToText()

result = processor.transcribe(
    "lecture.mp3",
    model="gpt-4o-transcribe",
    prompt="This lecture covers OpenAI, GPT-4, DALL·E, and machine learning."
)

print(result.text)
```

## Supported Languages

The Audio API supports 50+ languages including:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, Welsh

## Best Practices

1. **Use prompts** to improve accuracy for domain-specific terms
2. **Post-process with GPT-4** for critical accuracy requirements
3. **Use `gpt-4o-transcribe`** for best quality, `gpt-4o-mini-transcribe` for speed
4. **For meetings**, use speaker diarization with known speaker references
5. **For subtitles**, use word-level timestamps with `whisper-1`
6. **For long files**, use the chunking utilities to stay under 25 MB limit

## Error Handling

```python
from audio_to_text import AudioToText

processor = AudioToText()

try:
    result = processor.transcribe("audio.mp3")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Transcription failed: {e}")
```

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)

Set it in your environment:

```bash
export OPENAI_API_KEY="sk-..."
```

Or in Python:

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

## CLI Usage

```bash
# Basic transcription
python audio_to_text.py recording.mp3

# Run examples
python audio_examples.py basic recording.mp3
python audio_examples.py diarize meeting.wav
python audio_examples.py timestamps lecture.mp3
python audio_examples.py stream podcast.mp3

# Check audio info and chunk if needed
python audio_chunker.py long_recording.mp3 10
```
