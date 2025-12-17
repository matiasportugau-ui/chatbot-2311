# Speech-to-Text Module Documentation

This module provides a comprehensive interface to OpenAI's Audio API for speech-to-text operations.

## Features

- ✅ **Transcriptions** - Convert audio to text in the original language
- ✅ **Translations** - Translate audio to English
- ✅ **Speaker Diarization** - Identify and label different speakers
- ✅ **Streaming** - Real-time transcription streaming
- ✅ **Timestamps** - Word and segment-level timestamps
- ✅ **Prompting** - Improve accuracy with context prompts
- ✅ **Post-processing** - GPT-4 correction for improved reliability

## Supported Models

- `whisper-1` - Open source Whisper model
- `gpt-4o-transcribe` - Higher quality transcription
- `gpt-4o-mini-transcribe` - Faster, cost-effective transcription
- `gpt-4o-transcribe-diarize` - Transcription with speaker diarization

## Supported File Formats

- `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`
- Maximum file size: 25 MB

## Quick Start

### Basic Transcription

```python
from utils.speech_to_text import transcribe_audio, TranscriptionModel, ResponseFormat

# Simple transcription
result = transcribe_audio(
    audio_file="path/to/audio.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)

print(result.text)
```

### Using the Service Class

```python
from utils.speech_to_text import SpeechToTextService, TranscriptionModel, ResponseFormat

# Initialize service
service = SpeechToTextService()

# Transcribe with options
result = service.transcribe(
    audio_file="audio.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.JSON,
    language="es",  # Optional: specify language
    prompt="This is a lecture about AI.",  # Optional: improve accuracy
)

print(f"Text: {result.text}")
print(f"Language: {result.language}")
```

## Examples

### 1. Basic Transcription

```python
from utils.speech_to_text import get_speech_to_text_service, TranscriptionModel, ResponseFormat

service = get_speech_to_text_service()
result = service.transcribe(
    audio_file="speech.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
)
print(result.text)
```

### 2. Transcription with Prompt

Use prompts to improve accuracy for specific words, acronyms, or context:

```python
result = service.transcribe(
    audio_file="lecture.mp3",
    model=TranscriptionModel.GPT_4O_TRANSCRIBE,
    prompt="The following conversation is a lecture about OpenAI, GPT-4.5 and the future of AI.",
)
```

### 3. Translation to English

```python
from utils.speech_to_text import translate_audio

result = translate_audio(
    audio_file="german_speech.mp3",
    response_format=ResponseFormat.TEXT,
)
print(result.text)  # English translation
```

### 4. Speaker Diarization

Identify different speakers in a conversation:

```python
from utils.speech_to_text import ChunkingStrategy

result = service.transcribe_with_diarization(
    audio_file="meeting.wav",
    known_speaker_names=["agent", "customer"],
    known_speaker_references=["agent_ref.wav", "customer_ref.wav"],  # 2-10 sec clips
    chunking_strategy=ChunkingStrategy.AUTO,
)

for segment in result.segments:
    print(f"[{segment.start:.2f}s-{segment.end:.2f}s] {segment.speaker}: {segment.text}")
```

### 5. Streaming Transcription

Get transcription results as they become available:

```python
for event in service.transcribe_stream(
    audio_file="long_audio.mp3",
    model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
    response_format=ResponseFormat.TEXT,
):
    print(event)
    # Events include: transcript.text.delta, transcript.text.segment, transcript.text.done
```

### 6. Word-Level Timestamps

Get precise timestamps for each word:

```python
result = service.transcribe(
    audio_file="audio.mp3",
    model=TranscriptionModel.WHISPER_1,
    response_format=ResponseFormat.VERBOSE_JSON,
    timestamp_granularities=["word"],
)

for word in result.words:
    print(f"{word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
```

### 7. Post-Processing with GPT-4

Improve transcription accuracy by correcting uncommon words/acronyms:

```python
system_prompt = """
You are a helpful assistant for the company ZyntriQix. Your task is to correct 
any spelling discrepancies in the transcribed text. Make sure that the names of 
the following products are spelled correctly: ZyntriQix, Digique Plus, 
CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal 
Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T.
"""

corrected_text = service.transcribe_with_post_processing(
    audio_file="product_demo.mp3",
    system_prompt=system_prompt,
    correction_model="gpt-4o-mini",
    temperature=0.0,
)
```

## API Reference

### SpeechToTextService

Main service class for speech-to-text operations.

#### Methods

- `transcribe()` - Transcribe audio to text
- `translate()` - Translate audio to English
- `transcribe_with_diarization()` - Transcribe with speaker labels
- `transcribe_stream()` - Stream transcription results
- `transcribe_with_post_processing()` - Transcribe and correct with GPT-4

### TranscriptionModel Enum

- `WHISPER_1` - Open source Whisper model
- `GPT_4O_TRANSCRIBE` - High quality transcription
- `GPT_4O_MINI_TRANSCRIBE` - Fast, cost-effective
- `GPT_4O_TRANSCRIBE_DIARIZE` - With speaker diarization

### ResponseFormat Enum

- `JSON` - JSON format with text field
- `TEXT` - Plain text
- `SRT` - SubRip subtitle format (whisper-1 only)
- `VERBOSE_JSON` - Detailed JSON with segments (whisper-1 only)
- `VTT` - WebVTT subtitle format (whisper-1 only)
- `DIARIZED_JSON` - JSON with speaker segments (diarize model only)

### TranscriptionResult

Result object containing:

- `text` - Transcribed text
- `language` - Detected language (if available)
- `duration` - Audio duration (if available)
- `words` - Word-level timestamps (if requested)
- `segments` - Segment-level timestamps (if available)
- `raw_response` - Raw API response

### DiarizedTranscriptionResult

Result object for diarized transcriptions:

- `text` - Full transcription text
- `segments` - List of `DiarizedSegment` objects
- `raw_response` - Raw API response

### DiarizedSegment

- `speaker` - Speaker identifier
- `text` - Segment text
- `start` - Start time in seconds
- `end` - End time in seconds

## Best Practices

### 1. Model Selection

- Use `gpt-4o-transcribe` for highest quality
- Use `gpt-4o-mini-transcribe` for cost optimization
- Use `whisper-1` for compatibility with all features (SRT, VTT, timestamps)
- Use `gpt-4o-transcribe-diarize` for multi-speaker scenarios

### 2. Prompting

- Include context about the audio content
- List important words/acronyms that might be misrecognized
- For `whisper-1`, keep prompts under 224 tokens
- For GPT-4o models, prompts can be longer and more detailed

### 3. Handling Long Audio

- Files must be under 25 MB
- For longer files, split using PyDub or similar tools
- Avoid splitting mid-sentence to preserve context
- Use `chunking_strategy="auto"` for diarization of long audio

### 4. Speaker References

- Provide 2-10 second reference clips for known speakers
- Use same audio format as main file
- Encode as data URLs when using multipart form data

### 5. Post-Processing

- Use GPT-4 post-processing for:
  - Correcting uncommon words/acronyms
  - Improving punctuation
  - Preserving filler words
  - Language-specific formatting (e.g., simplified vs traditional Chinese)

## Error Handling

The module integrates with the project's logging and request tracking:

```python
from utils.speech_to_text import get_speech_to_text_service

try:
    service = get_speech_to_text_service()
    result = service.transcribe(audio_file="audio.mp3")
except FileNotFoundError as e:
    print(f"Audio file not found: {e}")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Requirements

- `openai>=1.0.0`
- Python 3.8+

## Environment Variables

- `OPENAI_API_KEY` - Required: Your OpenAI API key

## See Also

- [OpenAI Audio API Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- Example script: `python-scripts/example_speech_to_text.py`
