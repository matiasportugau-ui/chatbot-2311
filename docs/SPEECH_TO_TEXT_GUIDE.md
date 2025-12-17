# Speech-to-Text API Guide

This guide explains how to use the OpenAI Speech-to-Text API integration in this project.

## Overview

The Speech-to-Text module (`utils/speech_to_text.py`) provides a comprehensive interface to OpenAI's Audio API, supporting:

- **Transcriptions**: Convert audio to text in the original language
- **Translations**: Convert audio to English text
- **Streaming**: Real-time transcription streaming
- **Speaker Diarization**: Identify different speakers in audio
- **Timestamps**: Word and segment-level timestamps
- **Prompting**: Improve accuracy with context prompts

## Installation

Ensure you have the required dependencies:

```bash
pip install openai>=1.0.0 python-dotenv
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-your-key-here
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
```

## Quick Start

### Basic Transcription

```python
from utils.speech_to_text import SpeechToTextClient, TranscriptionModel, ResponseFormat

# Initialize client
client = SpeechToTextClient()

# Transcribe audio file
result = client.transcribe(
    audio_file="path/to/audio.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

print(result["text"])
```

### Using Convenience Functions

```python
from utils.speech_to_text import transcribe_audio, TranscriptionModel, ResponseFormat

result = transcribe_audio(
    audio_file="path/to/audio.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

print(result["text"])
```

## Supported Models

### Transcription Models

1. **`whisper-1`** (Legacy)
   - Supports: json, text, srt, verbose_json, vtt
   - Supports timestamps and translations
   - No streaming support

2. **`gpt-4o-transcribe`** (Recommended)
   - Higher quality transcriptions
   - Supports: json, text
   - Supports prompting and streaming
   - No timestamps

3. **`gpt-4o-mini-transcribe`** (Cost-effective)
   - Faster and cheaper
   - Supports: json, text
   - Supports prompting and streaming
   - No timestamps

4. **`gpt-4o-transcribe-diarize`** (Speaker identification)
   - Identifies different speakers
   - Supports: json, text, diarized_json
   - Requires `chunking_strategy` for audio > 30 seconds
   - Supports streaming

## Response Formats

- **`json`**: JSON object with text field (default)
- **`text`**: Plain text string
- **`srt`**: SubRip subtitle format (whisper-1 only)
- **`verbose_json`**: Detailed JSON with segments (whisper-1 only)
- **`vtt`**: WebVTT subtitle format (whisper-1 only)
- **`diarized_json`**: JSON with speaker segments (gpt-4o-transcribe-diarize only)

## Examples

### 1. Basic Transcription

```python
from utils.speech_to_text import SpeechToTextClient, TranscriptionModel, ResponseFormat

client = SpeechToTextClient()

result = client.transcribe(
    audio_file="lecture.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

print(result["text"])
```

### 2. Transcription with Prompt

Improve accuracy by providing context:

```python
client = SpeechToTextClient()

result = client.transcribe(
    audio_file="lecture.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
    prompt="The following conversation is a lecture about OpenAI, GPT-4.5 and the future of AI.",
)
```

### 3. Word-Level Timestamps

```python
client = SpeechToTextClient()

result = client.transcribe(
    audio_file="audio.mp3",
    model=TranscriptionModel.WHISPER_1,  # Only whisper-1 supports timestamps
    response_format=ResponseFormat.VERBOSE_JSON,
    timestamp_granularities=["word"],
)

# Access word-level timestamps
for word in result["words"]:
    print(f"{word['word']}: {word['start']}s - {word['end']}s")
```

### 4. Speaker Diarization

Identify different speakers in a meeting:

```python
client = SpeechToTextClient()

# Optional: Provide speaker reference clips
agent_ref = client.to_data_url("agent_sample.wav")

result = client.transcribe(
    audio_file="meeting.wav",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE,
    response_format=ResponseFormat.DIARIZED_JSON,
    chunking_strategy=ChunkingStrategy.AUTO,  # Required for audio > 30s
    known_speaker_names=["agent"],
    known_speaker_references=[agent_ref],
)

# Access speaker segments
for segment in result["segments"]:
    print(f"{segment['speaker']}: {segment['text']} ({segment['start']}s - {segment['end']}s)")
```

### 5. Streaming Transcription

Get results as they become available:

```python
client = SpeechToTextClient()

for event in client.transcribe_stream(
    audio_file="long_audio.mp3",
    model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
):
    event_type = event.get("type")
    if event_type == "transcript.text.delta":
        print(event.get("data", {}).get("delta", ""), end="", flush=True)
    elif event_type == "transcript.text.done":
        print("\n✅ Complete!")
        break
```

### 6. Translation to English

```python
client = SpeechToTextClient()

result = client.translate(
    audio_file="german_speech.mp3",
    response_format=ResponseFormat.TEXT,
)

print(result["text"])  # Output is always in English
```

## Supported Audio Formats

- mp3
- mp4
- mpeg
- mpga
- m4a
- wav
- webm

**File size limit**: 25 MB per file

## Best Practices

### 1. Using Prompts

Prompts can significantly improve transcription quality:

- **Correct specific words/acronyms**: Include correct spellings in the prompt
- **Preserve context**: When splitting long files, include previous transcript
- **Add punctuation**: Include punctuation examples in prompt
- **Keep filler words**: Include filler words in prompt if you want them preserved
- **Language style**: Use prompt to specify writing style (simplified vs traditional Chinese)

Example:

```python
prompt = (
    "The transcript is about OpenAI which makes technology like DALL·E, "
    "GPT-3, and ChatGPT with the hope of one day building an AGI system."
)
```

### 2. Handling Long Audio Files

For files longer than 25 MB:

1. **Compress the audio** to reduce file size
2. **Split into chunks** (avoid splitting mid-sentence)
3. **Use prompts** to maintain context between chunks

Example with PyDub:

```python
from pydub import AudioSegment

song = AudioSegment.from_mp3("long_audio.mp3")
ten_minutes = 10 * 60 * 1000  # milliseconds

first_10_minutes = song[:ten_minutes]
first_10_minutes.export("chunk_1.mp3", format="mp3")
```

### 3. Post-Processing with GPT-4

For better accuracy with uncommon words, use GPT-4 for post-processing:

```python
from openai import OpenAI

# First, transcribe
transcript = client.transcribe(audio_file, ...)

# Then, correct with GPT-4
gpt_client = OpenAI()
system_prompt = """
You are a helpful assistant. Your task is to correct any spelling 
discrepancies in the transcribed text. Make sure that the names of 
the following products are spelled correctly: ZyntriQix, Digique Plus, 
CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, 
DigiFractal Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T.
"""

response = gpt_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript["text"]},
    ],
)

corrected_text = response.choices[0].message.content
```

## Error Handling

The module includes comprehensive error handling:

```python
from utils.speech_to_text import SpeechToTextClient

try:
    client = SpeechToTextClient()
    result = client.transcribe("audio.mp3")
except FileNotFoundError:
    print("Audio file not found")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## API Reference

### SpeechToTextClient

Main client class for speech-to-text operations.

#### Methods

- `transcribe()`: Transcribe audio to text
- `transcribe_stream()`: Stream transcription results
- `translate()`: Translate audio to English
- `to_data_url()`: Convert audio file to data URL for speaker references

### Enums

- `TranscriptionModel`: Available transcription models
- `ResponseFormat`: Supported response formats
- `ChunkingStrategy`: Chunking strategies for long audio

### Convenience Functions

- `transcribe_audio()`: Quick transcription function
- `translate_audio()`: Quick translation function

## Testing

Run the example script to test the functionality:

```bash
python test_speech_to_text.py
```

This interactive script demonstrates all features with your audio files.

## Supported Languages

The API supports 98+ languages. Languages with <50% word error rate include:

Afrikaans, Arabic, Armenian, Azerbaijani, Belarusian, Bosnian, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Galician, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kannada, Kazakh, Korean, Latvian, Lithuanian, Macedonian, Malay, Marathi, Maori, Nepali, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Tamil, Thai, Turkish, Ukrainian, Urdu, Vietnamese, and Welsh.

## Limitations

1. **File size**: Maximum 25 MB per file
2. **Streaming**: Not supported for `whisper-1` model
3. **Timestamps**: Only available with `whisper-1` model
4. **Translations**: Only supported with `whisper-1` model
5. **Diarization**: Requires `chunking_strategy` for audio > 30 seconds

## Additional Resources

- [OpenAI Audio API Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference/audio)
- [Whisper Model](https://openai.com/blog/whisper/)
