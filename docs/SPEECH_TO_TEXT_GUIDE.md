# Speech-to-Text Guide

This guide explains how to use the speech-to-text functionality powered by OpenAI's Audio API.

## Overview

The speech-to-text module provides comprehensive audio transcription capabilities including:

- **Basic Transcriptions**: Convert audio to text in any supported language
- **Translations**: Translate audio to English
- **Speaker Diarization**: Identify and label different speakers
- **Timestamps**: Get word-level or segment-level timestamps
- **Streaming**: Receive transcription results in real-time
- **Prompting**: Improve accuracy with context prompts
- **Post-processing**: Correct transcripts using GPT-4

## Installation

Ensure you have the required dependencies:

```bash
pip install openai>=1.0.0
```

For audio splitting (optional):

```bash
pip install pydub
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

## Supported Audio Formats

- MP3 (`.mp3`)
- MP4 (`.mp4`)
- MPEG (`.mpeg`)
- MPGA (`.mpga`)
- M4A (`.m4a`)
- WAV (`.wav`)
- WebM (`.webm`)

**File Size Limit**: 25 MB per file

## Quick Start

### Basic Transcription

```python
from utils.audio_to_text import AudioToTextProcessor, TranscriptionConfig, TranscriptionModel, ResponseFormat

processor = AudioToTextProcessor()

config = TranscriptionConfig(
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

result = processor.transcribe("audio.mp3", config)
print(result.text)
```

### Using the CLI

```bash
# Basic transcription
python scripts/audio_to_text_cli.py audio.mp3

# Save to file
python scripts/audio_to_text_cli.py audio.mp3 --output transcript.txt

# With prompt for better accuracy
python scripts/audio_to_text_cli.py audio.mp3 --prompt "This is a lecture about AI"
```

## Available Models

### whisper-1
- Open source Whisper model
- Supports all response formats: `json`, `text`, `srt`, `verbose_json`, `vtt`
- Supports word-level timestamps
- Good for general use cases

### gpt-4o-transcribe
- Higher quality transcription
- Supports `json` and `text` formats
- Supports prompting and logprobs
- Recommended for most use cases

### gpt-4o-mini-transcribe
- Faster and more cost-effective
- Supports `json` and `text` formats
- Supports prompting and logprobs
- Good for high-volume use cases

### gpt-4o-transcribe-diarize
- Speaker-aware transcription
- Supports `json`, `text`, and `diarized_json` formats
- Requires `chunking_strategy` for audio > 30 seconds
- Does not support prompts or logprobs

## Features

### 1. Basic Transcription

Transcribe audio to text:

```python
from utils.audio_to_text import AudioToTextProcessor, TranscriptionConfig, TranscriptionModel, ResponseFormat

processor = AudioToTextProcessor()

config = TranscriptionConfig(
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

result = processor.transcribe("audio.mp3", config)
print(result.text)
```

### 2. Transcription with Prompt

Improve accuracy by providing context:

```python
config = TranscriptionConfig(
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
    prompt="The following conversation is a lecture about the recent developments around OpenAI, GPT-4.5 and the future of AI.",
)

result = processor.transcribe("lecture.mp3", config)
```

**Use cases for prompting:**
- Correct specific words or acronyms
- Preserve context when splitting files
- Maintain punctuation style
- Keep filler words
- Specify writing style (e.g., simplified vs traditional Chinese)

### 3. Word-Level Timestamps

Get precise timestamps for each word:

```python
config = TranscriptionConfig(
    model=TranscriptionModel.WHISPER_1,
    response_format=ResponseFormat.VERBOSE_JSON,
    timestamp_granularities=[TimestampGranularity.WORD],
)

result = processor.transcribe("audio.mp3", config)

for word in result.words:
    print(f"{word['word']}: {word['start']}s - {word['end']}s")
```

### 4. Speaker Diarization

Identify different speakers in audio:

```python
speaker_refs = {
    "agent": "agent_reference.wav",
    "customer": "customer_reference.wav",
}

result = processor.transcribe_with_diarization(
    "meeting.wav",
    speaker_references=speaker_refs,
    chunking_strategy="auto",
)

for segment in result.segments:
    print(f"{segment['speaker']}: {segment['text']} ({segment['start']}s - {segment['end']}s)")
```

**Speaker Reference Clips:**
- Should be 2-10 seconds long
- Same format as main audio file
- Helps the model identify known speakers

### 5. Streaming Transcription

Receive transcription results as they become available:

```python
for event in processor.transcribe_stream("audio.mp3"):
    event_type = event.get('type', 'unknown')
    
    if 'delta' in event:
        print(event['delta'], end='', flush=True)
    elif event_type == 'transcript.text.done':
        print(f"\nFull transcript: {event.get('text', '')}")
```

### 6. Translation

Translate audio to English:

```python
result = processor.translate("german_audio.mp3")
print(result.text)
```

**Note**: Translation only supports `whisper-1` model and always outputs English.

### 7. Post-Processing with GPT-4

Correct spelling and improve transcript quality:

```python
from utils.audio_to_text import create_correction_prompt

# First, transcribe
config = TranscriptionConfig(
    model=TranscriptionModel.WHISPER_1,
    response_format=ResponseFormat.TEXT,
)
raw_transcript = processor.transcribe("audio.mp3", config).text

# Then, correct with GPT-4
system_prompt = create_correction_prompt(
    company_name="ZyntriQix",
    product_names=[
        "ZyntriQix",
        "Digique Plus",
        "CynapseFive",
    ],
)

corrected = processor.post_process_with_gpt4(
    raw_transcript,
    system_prompt,
    model="gpt-4",
)
```

## Handling Large Files

Files larger than 25 MB need to be split. The module includes a helper function:

```python
chunks = processor.split_audio_file(
    "large_audio.mp3",
    chunk_duration_minutes=10,
    output_dir="chunks",
)

# Process each chunk
for chunk in chunks:
    result = processor.transcribe(chunk)
    # Combine results as needed
```

**Note**: Requires `pydub` package: `pip install pydub`

## CLI Usage

### Basic Commands

```bash
# Basic transcription
python scripts/audio_to_text_cli.py audio.mp3

# Specify model
python scripts/audio_to_text_cli.py audio.mp3 --model whisper-1

# Output format
python scripts/audio_to_text_cli.py audio.mp3 --format json

# Save to file
python scripts/audio_to_text_cli.py audio.mp3 --output transcript.txt
```

### Advanced Features

```bash
# With prompt
python scripts/audio_to_text_cli.py audio.mp3 --prompt "Lecture about AI"

# With timestamps
python scripts/audio_to_text_cli.py audio.mp3 --timestamps word --format verbose_json

# Speaker diarization
python scripts/audio_to_text_cli.py meeting.wav --diarize \
    --speaker-refs agent:agent.wav customer:customer.wav

# Translation
python scripts/audio_to_text_cli.py german.mp3 --translate

# Post-processing
python scripts/audio_to_text_cli.py audio.mp3 --post-process \
    --company "MyCompany" --products "Product1,Product2"

# Split large file
python scripts/audio_to_text_cli.py large_audio.mp3 --split 10
```

## Examples

See `python-scripts/audio_to_text_example.py` for comprehensive examples:

```bash
# Run all examples
python python-scripts/audio_to_text_example.py audio.mp3

# Run specific example
python python-scripts/audio_to_text_example.py audio.mp3 --example 1
```

## Response Formats

### text
Plain text transcript:
```
Imagine the wildest idea that you've ever had...
```

### json
JSON with text field:
```json
{
  "text": "Imagine the wildest idea that you've ever had..."
}
```

### verbose_json
JSON with additional metadata:
```json
{
  "text": "...",
  "language": "en",
  "duration": 10.5,
  "words": [...],
  "segments": [...]
}
```

### diarized_json
JSON with speaker labels:
```json
{
  "text": "...",
  "segments": [
    {
      "speaker": "SPEAKER_00",
      "text": "...",
      "start": 0.0,
      "end": 5.2
    }
  ]
}
```

### srt / vtt
Subtitle formats for video editing.

## Error Handling

The module includes validation for:
- File existence
- Supported formats
- File size limits
- API errors

Example error handling:

```python
try:
    result = processor.transcribe("audio.mp3")
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Use appropriate models**: 
   - `gpt-4o-transcribe` for best quality
   - `gpt-4o-mini-transcribe` for cost efficiency
   - `whisper-1` for timestamps or translations

2. **Provide prompts** for better accuracy:
   - Include context about the audio content
   - List important terms, names, or acronyms
   - Specify desired punctuation style

3. **Use speaker references** for diarization:
   - Provide 2-10 second reference clips
   - Use clear, distinct audio samples

4. **Post-process** when needed:
   - For domain-specific terminology
   - To correct common misrecognitions
   - To improve formatting

5. **Handle large files**:
   - Split files > 25 MB
   - Avoid splitting mid-sentence
   - Combine results appropriately

## Supported Languages

The models support 98+ languages. Languages with <50% word error rate include:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, Welsh.

## API Reference

See `utils/audio_to_text.py` for full API documentation.

### Main Classes

- `AudioToTextProcessor`: Main processing class
- `TranscriptionConfig`: Configuration for transcription requests
- `TranscriptionResult`: Result object with transcript and metadata
- `TranscriptionModel`: Available models enum
- `ResponseFormat`: Available response formats enum
- `TimestampGranularity`: Timestamp options enum

## Troubleshooting

### "File too large" error
- Split the file using `split_audio_file()` method
- Or compress the audio file

### "Unsupported format" error
- Convert to supported format (MP3, WAV, etc.)
- Use `ffmpeg` or similar tool

### Poor transcription quality
- Try a different model (`gpt-4o-transcribe` for better quality)
- Add a prompt with context
- Post-process with GPT-4

### Speaker diarization not working
- Ensure audio is > 30 seconds (requires chunking_strategy)
- Provide speaker reference clips
- Use `gpt-4o-transcribe-diarize` model

### API errors
- Check your API key is set correctly
- Verify you have API credits/quota
- Check network connectivity

## Additional Resources

- [OpenAI Audio API Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [Whisper Model Details](https://github.com/openai/whisper)
- [Supported Languages](https://github.com/openai/whisper#available-models-and-languages)
