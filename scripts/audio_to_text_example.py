#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio to Text Processing Examples

This script demonstrates various ways to use the AudioToText module
for speech-to-text conversion using OpenAI's API.

Requirements:
    pip install openai
    pip install pydub  # Optional, for large file handling

Usage:
    python scripts/audio_to_text_example.py

Environment:
    Set OPENAI_API_KEY environment variable or pass directly.
"""

import os
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.audio_to_text import (
    AudioToText,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    ChunkingStrategy,
    KnownSpeaker,
    transcribe,
    translate,
    transcribe_with_speakers,
    PYDUB_AVAILABLE,
)


def example_basic_transcription():
    """
    Basic transcription example.
    
    This is the simplest way to transcribe an audio file.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Transcription")
    print("=" * 60)
    
    # Using convenience function
    print("\nUsing convenience function:")
    print(">>> result = transcribe('audio.mp3')")
    print(">>> print(result.text)")
    
    # Using class directly
    print("\nUsing class directly:")
    print("""
>>> from utils.audio_to_text import AudioToText
>>> 
>>> audio = AudioToText()
>>> result = audio.transcribe("path/to/audio.mp3")
>>> print(result.text)
""")


def example_with_model_selection():
    """
    Example showing different model options.
    """
    print("\n" + "=" * 60)
    print("Example 2: Model Selection")
    print("=" * 60)
    
    print("""
Available Models:
- whisper-1: Original Whisper model
  - Supports: json, text, srt, verbose_json, vtt formats
  - Supports: word/segment timestamps
  
- gpt-4o-transcribe: Higher quality model
  - Supports: json, text formats
  - Supports: prompts, streaming, logprobs
  
- gpt-4o-mini-transcribe: Faster variant
  - Same features as gpt-4o-transcribe
  
- gpt-4o-transcribe-diarize: Speaker diarization
  - Supports: json, text, diarized_json formats
  - Identifies different speakers

Code Example:
>>> from utils.audio_to_text import AudioToText, TranscriptionModel
>>> 
>>> audio = AudioToText()
>>> 
>>> # Use whisper for timestamps
>>> result = audio.transcribe(
...     "audio.mp3",
...     model=TranscriptionModel.WHISPER_1,
...     timestamp_granularities=[TimestampGranularity.WORD]
... )
>>> 
>>> # Use gpt-4o for higher quality
>>> result = audio.transcribe(
...     "audio.mp3",
...     model=TranscriptionModel.GPT_4O_TRANSCRIBE,
...     prompt="This is a business meeting about quarterly results."
... )
""")


def example_with_language():
    """
    Example with language specification.
    """
    print("\n" + "=" * 60)
    print("Example 3: Language Specification")
    print("=" * 60)
    
    print("""
Supported Languages (ISO 639-1 codes):
- English (en), Spanish (es), French (fr), German (de)
- Portuguese (pt), Italian (it), Dutch (nl), Polish (pl)
- Russian (ru), Chinese (zh), Japanese (ja), Korean (ko)
- Arabic (ar), Hindi (hi), and many more...

Code Example:
>>> result = audio.transcribe(
...     "spanish_audio.mp3",
...     language="es",  # Spanish
...     prompt="La siguiente conversación es sobre productos."
... )
>>> print(result.text)
""")


def example_translation():
    """
    Example of audio translation to English.
    """
    print("\n" + "=" * 60)
    print("Example 4: Translation to English")
    print("=" * 60)
    
    print("""
The translate() function converts audio in any supported language to English.
Only whisper-1 model is supported for translation.

Code Example:
>>> from utils.audio_to_text import translate
>>> 
>>> # Translate German audio to English
>>> result = translate("german_audio.mp3")
>>> print(result.text)  # Output is in English
>>> 
>>> # With more options
>>> audio = AudioToText()
>>> result = audio.translate(
...     "spanish_audio.mp3",
...     prompt="This is a conversation about thermal insulation.",
...     response_format=ResponseFormat.TEXT
... )
""")


def example_speaker_diarization():
    """
    Example of speaker diarization.
    """
    print("\n" + "=" * 60)
    print("Example 5: Speaker Diarization")
    print("=" * 60)
    
    print("""
Diarization identifies different speakers in the audio.
You can provide reference audio clips for known speakers.

Code Example:
>>> from utils.audio_to_text import (
...     AudioToText, 
...     KnownSpeaker, 
...     transcribe_with_speakers
... )
>>> 
>>> # Basic diarization
>>> result = transcribe_with_speakers("meeting.wav")
>>> for segment in result.segments:
...     print(f"{segment.speaker}: {segment.text}")
>>> 
>>> # With known speakers
>>> speakers = [
...     KnownSpeaker(name="Alice", audio_path="alice_sample.wav"),
...     KnownSpeaker(name="Bob", audio_path="bob_sample.wav"),
... ]
>>> 
>>> audio = AudioToText()
>>> result = audio.transcribe_diarize(
...     "meeting.wav",
...     known_speakers=speakers,
...     response_format=ResponseFormat.DIARIZED_JSON
... )
>>> 
>>> # Output:
>>> # Alice: Hello, let's discuss the project.
>>> # Bob: Sure, I've prepared the slides.
>>> # Alice: Great, please share them.
""")


def example_streaming():
    """
    Example of streaming transcription.
    """
    print("\n" + "=" * 60)
    print("Example 6: Streaming Transcription")
    print("=" * 60)
    
    print("""
Streaming provides real-time transcription results.
Only gpt-4o models support streaming.

Code Example:
>>> audio = AudioToText()
>>> 
>>> # Stream transcription
>>> for event in audio.transcribe("audio.mp3", stream=True):
...     if event.event_type == "transcript.text.delta":
...         print(event.delta, end="", flush=True)
...     elif event.event_type == "transcript.text.done":
...         print(f"\\nFull transcript: {event.text}")
>>> 
>>> # Stream with diarization
>>> for event in audio.transcribe_diarize("meeting.wav", stream=True):
...     if event.event_type == "transcript.text.segment":
...         print(f"{event.speaker}: {event.text}")
""")


def example_large_files():
    """
    Example of processing large audio files.
    """
    print("\n" + "=" * 60)
    print("Example 7: Large File Processing")
    print("=" * 60)
    
    if not PYDUB_AVAILABLE:
        print("\n⚠️  PyDub not installed. Install with: pip install pydub")
    
    print("""
Files larger than 25MB must be split into chunks.
The transcribe_large_file() method handles this automatically.

Requires: pip install pydub

Code Example:
>>> audio = AudioToText()
>>> 
>>> # Transcribe a long recording
>>> result = audio.transcribe_large_file(
...     "long_meeting.mp3",
...     chunk_duration_ms=10 * 60 * 1000,  # 10 minutes
...     overlap_ms=5000,  # 5 second overlap
...     language="en"
... )
>>> 
>>> print(f"Duration: {result.duration} seconds")
>>> print(f"Transcript: {result.text}")
>>> 
>>> # Access segments with timestamps
>>> for segment in result.segments:
...     print(f"[{segment.start:.1f}s] {segment.text}")
""")


def example_timestamps():
    """
    Example of getting word/segment timestamps.
    """
    print("\n" + "=" * 60)
    print("Example 8: Timestamps (whisper-1 only)")
    print("=" * 60)
    
    print("""
Word-level timestamps enable precise synchronization.
Only whisper-1 model supports timestamp granularities.

Code Example:
>>> from utils.audio_to_text import AudioToText, TranscriptionModel, TimestampGranularity
>>> 
>>> audio = AudioToText()
>>> result = audio.transcribe(
...     "audio.mp3",
...     model=TranscriptionModel.WHISPER_1,
...     timestamp_granularities=[
...         TimestampGranularity.WORD,
...         TimestampGranularity.SEGMENT
...     ]
... )
>>> 
>>> # Word-level timestamps
>>> for word in result.words:
...     print(f"[{word.start:.2f}s - {word.end:.2f}s] {word.word}")
>>> 
>>> # Segment timestamps
>>> for segment in result.segments:
...     print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
""")


def example_prompting():
    """
    Example of using prompts to improve quality.
    """
    print("\n" + "=" * 60)
    print("Example 9: Prompting for Better Quality")
    print("=" * 60)
    
    print("""
Prompts help the model understand context and specialized vocabulary.

Use Cases:
1. Correct spelling of names/acronyms
2. Maintain context across chunks
3. Add punctuation consistently
4. Handle filler words
5. Specify writing style (traditional/simplified Chinese)

Code Example:
>>> audio = AudioToText()
>>> 
>>> # Example 1: Specialized vocabulary
>>> result = audio.transcribe(
...     "tech_meeting.mp3",
...     prompt="The following discusses OpenAI, GPT-4, DALL·E, and ChatGPT."
... )
>>> 
>>> # Example 2: Include filler words
>>> result = audio.transcribe(
...     "interview.mp3",
...     prompt="Umm, let me think like, hmm... Okay, here's what I'm thinking."
... )
>>> 
>>> # Example 3: Business context
>>> result = audio.transcribe(
...     "call.mp3",
...     model=TranscriptionModel.GPT_4O_TRANSCRIBE,
...     prompt="Customer support call about Isodec thermal insulation products. "
...            "Products: Isodec, Poliestireno, Lana de Roca. "
...            "Company: BMC Uruguay."
... )
""")


def example_integration_with_chatbot():
    """
    Example of integrating with the chatbot system.
    """
    print("\n" + "=" * 60)
    print("Example 10: Integration with Chatbot")
    print("=" * 60)
    
    print("""
Integrate audio transcription with the existing chatbot system.

Code Example:
>>> from utils.audio_to_text import transcribe, TranscriptionModel
>>> from ia_conversacional_integrada import IAConversacionalIntegrada
>>> 
>>> # Initialize chatbot
>>> chatbot = IAConversacionalIntegrada()
>>> 
>>> # Process voice message from WhatsApp
>>> def handle_voice_message(audio_path: str, client_phone: str):
...     # Transcribe the audio
...     result = transcribe(
...         audio_path,
...         model=TranscriptionModel.GPT_4O_MINI_TRANSCRIBE,
...         language="es",
...         prompt="Consulta sobre productos de aislamiento térmico."
...     )
...     
...     # Process transcribed text through chatbot
...     response = chatbot.procesar_mensaje_usuario(
...         mensaje=result.text,
...         telefono_cliente=client_phone
...     )
...     
...     return {
...         "transcription": result.text,
...         "response": response["mensaje"],
...         "confidence": response["confianza"]
...     }
>>> 
>>> # Usage
>>> result = handle_voice_message("voice_note.mp3", "+59899123456")
>>> print(f"User said: {result['transcription']}")
>>> print(f"Bot response: {result['response']}")
""")


def main():
    """Run all examples."""
    print("=" * 60)
    print("  AUDIO TO TEXT - USAGE EXAMPLES")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY not set in environment.")
        print("   Examples show code snippets but won't execute actual API calls.")
        print("   Set the key to run real transcriptions:")
        print("   export OPENAI_API_KEY=sk-your-key-here")
    else:
        print("\n✅ OPENAI_API_KEY detected.")
    
    # Show all examples
    example_basic_transcription()
    example_with_model_selection()
    example_with_language()
    example_translation()
    example_speaker_diarization()
    example_streaming()
    example_large_files()
    example_timestamps()
    example_prompting()
    example_integration_with_chatbot()
    
    print("\n" + "=" * 60)
    print("  END OF EXAMPLES")
    print("=" * 60)
    
    # Quick test if API key is available
    if api_key:
        print("\nWould you like to run a test transcription? [y/N]: ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                print("\nProvide path to an audio file (.mp3, .wav, etc.): ", end="")
                audio_path = input().strip()
                if audio_path and Path(audio_path).exists():
                    print("\nTranscribing...")
                    result = transcribe(audio_path)
                    print(f"\n✅ Transcription successful!")
                    print(f"Text: {result.text[:500]}...")
                    print(f"Model: {result.model}")
                else:
                    print("File not found or invalid path.")
        except (KeyboardInterrupt, EOFError):
            print("\nSkipped test.")


if __name__ == "__main__":
    main()
