# Speech-to-Text Module

Comprehensive speech-to-text functionality using OpenAI's Audio API, integrated with the WhatsApp chatbot system.

## Features

- ✅ **Multiple Models Support**: whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe, gpt-4o-transcribe-diarize
- ✅ **Transcriptions**: Convert audio to text in any language
- ✅ **Translations**: Translate audio to English
- ✅ **Speaker Diarization**: Identify and label different speakers in audio
- ✅ **Streaming**: Real-time transcription as audio is processed
- ✅ **Post-Processing**: Improve accuracy with GPT-4 correction
- ✅ **Audio Splitting**: Handle large audio files (>25MB)
- ✅ **WhatsApp Integration**: Automatic transcription of voice messages

## Installation

```bash
pip install openai pydub python-dotenv
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or add to `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

## Quick Start

### Basic Transcription

```python
from speech_to_text import SpeechToText, TranscriptionModel

# Initialize
stt = SpeechToText(model=TranscriptionModel.GPT_4O_TRANSCRIBE)

# Transcribe
result = stt.transcribe('audio.mp3')
print(result.text)
```

### Translation to English

```python
# Translate any language audio to English
result = stt.translate('spanish_audio.mp3')
print(result.text)  # Output in English
```

### Speaker Diarization

```python
# Identify different speakers
segments = stt.transcribe_with_diarization(
    'meeting.wav',
    known_speakers=[
        {'name': 'agent', 'reference_audio_path': 'agent.wav'},
        {'name': 'customer', 'reference_audio_path': 'customer.wav'}
    ]
)

for segment in segments:
    print(f"{segment.speaker}: {segment.text} ({segment.start}s - {segment.end}s)")
```

### Streaming Transcription

```python
# Get transcription as it's processed
for event in stt.transcribe_streaming('audio.mp3', include_logprobs=True):
    if event['event'] == 'transcript.text.delta':
        print(event['data'].get('delta', ''), end='', flush=True)
    elif event['event'] == 'transcript.text.done':
        print(f"\n\nFull transcript: {event['data'].get('text', '')}")
```

### Post-Processing for Accuracy

```python
# Improve transcription accuracy with GPT-4
corrected = stt.transcribe_with_post_processing(
    'product_demo.mp3',
    correction_terms=['ZyntriQix', 'Digique Plus', 'GPT-3', 'DALL·E'],
    gpt_model='gpt-4o'
)
print(corrected)
```

### Large Audio Files

```python
# Split large files into chunks
chunks = stt.split_audio_file(
    'long_recording.mp3',
    output_dir='audio_chunks',
    chunk_duration_minutes=10
)

# Transcribe each chunk
for chunk_path in chunks:
    result = stt.transcribe(chunk_path)
    print(f"{chunk_path}: {result.text[:100]}...")
```

## Models

### whisper-1
- **Best for**: General purpose transcription
- **Formats**: json, text, srt, verbose_json, vtt
- **Features**: Timestamps, translations
- **Limitations**: No streaming, limited prompting

### gpt-4o-transcribe
- **Best for**: High-quality transcriptions
- **Formats**: json, text
- **Features**: Prompting, logprobs, streaming
- **Limitations**: More expensive

### gpt-4o-mini-transcribe
- **Best for**: Cost-effective transcriptions
- **Formats**: json, text
- **Features**: Prompting, logprobs, streaming
- **Limitations**: Slightly lower quality than gpt-4o-transcribe

### gpt-4o-transcribe-diarize
- **Best for**: Multi-speaker audio
- **Formats**: json, text, diarized_json
- **Features**: Speaker identification, known speaker mapping
- **Limitations**: Requires chunking_strategy for >30s audio, no prompting

## Advanced Usage

### Using Prompts

Prompts help improve transcription quality:

```python
# Correct specific terms
result = stt.transcribe(
    'lecture.mp3',
    prompt='This lecture discusses OpenAI, GPT-4, DALL·E, and ChatGPT technologies.'
)

# Preserve context from previous segments
previous_transcript = "The previous segment discussed..."
result = stt.transcribe(
    'segment2.mp3',
    prompt=previous_transcript
)

# Improve punctuation
result = stt.transcribe(
    'speech.mp3',
    prompt='Hello, welcome to my lecture.'
)
```

### Timestamps

Get word-level timestamps:

```python
result = stt.transcribe(
    'audio.mp3',
    model=TranscriptionModel.WHISPER_1,
    response_format=ResponseFormat.VERBOSE_JSON,
    timestamp_granularities=[TimestampGranularity.WORD]
)

for word in result.words:
    print(f"{word['word']}: {word['start']}s - {word['end']}s")
```

### Known Speakers

Provide reference audio for better speaker identification:

```python
segments = stt.transcribe_with_diarization(
    'meeting.wav',
    known_speakers=[
        {
            'name': 'agent',
            'reference_audio_path': 'agent_reference.wav'  # 2-10 seconds
        }
    ]
)
```

## WhatsApp Integration

The module is automatically integrated with the WhatsApp system. When a user sends a voice message:

1. Audio is downloaded from WhatsApp API
2. Transcribed using speech-to-text
3. Processed by the conversational AI
4. Response is sent back to the user

No additional configuration needed if `OPENAI_API_KEY` is set!

## Supported Formats

**Input**: mp3, mp4, mpeg, mpga, m4a, wav, webm

**Output**:
- `json`: JSON with text
- `text`: Plain text
- `srt`: SubRip subtitle format
- `verbose_json`: JSON with timestamps and metadata
- `vtt`: WebVTT subtitle format
- `diarized_json`: JSON with speaker segments

## File Size Limits

- Maximum file size: 25 MB
- For larger files, use `split_audio_file()` to chunk them

## Error Handling

```python
from speech_to_text import SpeechToText

try:
    stt = SpeechToText()
    result = stt.transcribe('audio.mp3')
except FileNotFoundError:
    print("Audio file not found")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Transcription failed: {e}")
```

## Best Practices

1. **Choose the right model**:
   - Use `gpt-4o-mini-transcribe` for cost-effective general use
   - Use `gpt-4o-transcribe` for highest quality
   - Use `gpt-4o-transcribe-diarize` for meetings/interviews
   - Use `whisper-1` for translations

2. **Use prompts** for:
   - Correcting specific terms/acronyms
   - Preserving context across segments
   - Improving punctuation
   - Maintaining style

3. **Post-process** when:
   - Transcription contains domain-specific terms
   - You need high accuracy for product names
   - Multiple corrections are needed

4. **Handle large files**:
   - Split files >25MB
   - Avoid splitting mid-sentence
   - Use compressed formats (mp3) when possible

## Examples

See `test_speech_to_text.py` for comprehensive examples.

## API Reference

### SpeechToText Class

#### Methods

- `transcribe()`: Transcribe audio to text
- `translate()`: Translate audio to English
- `transcribe_with_diarization()`: Transcribe with speaker identification
- `transcribe_streaming()`: Stream transcription results
- `transcribe_with_post_processing()`: Transcribe and correct with GPT-4
- `split_audio_file()`: Split large audio files

### TranscriptionResult

- `text`: Transcribed text
- `language`: Detected language
- `duration`: Audio duration
- `words`: Word-level timestamps (if available)
- `segments`: Segment-level data (if available)
- `model`: Model used
- `timestamp`: When transcription was performed

### DiarizedSegment

- `speaker`: Speaker identifier
- `text`: Transcribed text for segment
- `start`: Start time in seconds
- `end`: End time in seconds
- `segment_id`: Unique segment identifier

## Troubleshooting

### "OpenAI API key is required"
Set `OPENAI_API_KEY` environment variable or pass `api_key` parameter.

### "File size exceeds maximum"
Split the file using `split_audio_file()` or compress it.

### "Streaming is not supported for whisper-1"
Use `gpt-4o-transcribe` or `gpt-4o-mini-transcribe` for streaming.

### "chunking_strategy required"
For `gpt-4o-transcribe-diarize` with audio >30s, set `chunking_strategy="auto"`.

## License

Part of the BMC Uruguay Chatbot System.
