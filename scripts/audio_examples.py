#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Transcription Examples
============================

Comprehensive examples demonstrating all features of the audio transcription module.

Run this script to see usage examples and test the transcription functionality.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from audio_transcription import (
    AudioTranscriber,
    transcribe_file,
    translate_file,
    TranscriptionResult,
)


def example_basic_transcription():
    """
    Example 1: Basic Transcription
    
    The simplest way to transcribe an audio file.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Transcription")
    print("=" * 60)
    
    code = '''
    from audio_transcription import transcribe_file
    
    # Quick one-liner transcription
    text = transcribe_file("meeting.mp3")
    print(text)
    
    # Or use the class for more control
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    result = transcriber.transcribe("meeting.mp3")
    print(result.text)
    '''
    print(code)


def example_model_selection():
    """
    Example 2: Choosing the Right Model
    
    Different models for different use cases.
    """
    print("\n" + "=" * 60)
    print("Example 2: Model Selection")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # gpt-4o-transcribe: Best quality (default)
    result = transcriber.transcribe(
        "interview.mp3",
        model="gpt-4o-transcribe"
    )
    
    # gpt-4o-mini-transcribe: Faster, more cost-effective
    result = transcriber.transcribe(
        "quick_note.mp3",
        model="gpt-4o-mini-transcribe"
    )
    
    # whisper-1: Original Whisper, more output format options
    result = transcriber.transcribe(
        "podcast.mp3",
        model="whisper-1",
        response_format="srt"  # Subtitle format
    )
    
    # gpt-4o-transcribe-diarize: With speaker identification
    result = transcriber.transcribe_with_diarization("meeting.wav")
    '''
    print(code)


def example_prompting():
    """
    Example 3: Using Prompts for Better Accuracy
    
    Prompts help with domain-specific vocabulary, proper nouns,
    and maintaining context for chunked transcriptions.
    """
    print("\n" + "=" * 60)
    print("Example 3: Prompting for Better Accuracy")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # Technical vocabulary prompt
    result = transcriber.transcribe(
        "tech_meeting.mp3",
        model="gpt-4o-transcribe",
        prompt="""
        Technical meeting about Kubernetes, Docker, and microservices.
        Key terms: API gateway, load balancer, CI/CD pipeline, 
        Terraform, Helm charts, service mesh, Istio.
        """
    )
    
    # Company/product names prompt  
    result = transcriber.transcribe(
        "sales_call.mp3",
        prompt="""
        Sales call discussing our products: DataSync Pro, 
        CloudVault Enterprise, and the new AISuite platform.
        Competitors mentioned: Snowflake, Databricks.
        """
    )
    
    # Maintaining punctuation and style
    result = transcriber.transcribe(
        "interview.mp3",
        prompt="Hello, welcome to the interview. "
               "Let's begin with your introduction."
    )
    '''
    print(code)


def example_diarization():
    """
    Example 4: Speaker Diarization
    
    Identify different speakers in a conversation or meeting.
    """
    print("\n" + "=" * 60)
    print("Example 4: Speaker Diarization")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # Basic diarization (unknown speakers)
    result = transcriber.transcribe_with_diarization("meeting.wav")
    
    for segment in result.segments:
        print(f"[{segment.start:.1f}s - {segment.end:.1f}s]")
        print(f"  {segment.speaker}: {segment.text}")
        print()
    
    # With known speaker references (2-10 second voice samples)
    result = transcriber.transcribe_with_diarization(
        "team_meeting.wav",
        known_speakers={
            "Alice (Manager)": "alice_sample.wav",
            "Bob (Engineer)": "bob_sample.wav",
            "Carol (Designer)": "carol_sample.wav",
        }
    )
    
    # Format as conversation
    current_speaker = None
    for segment in result.segments:
        if segment.speaker != current_speaker:
            current_speaker = segment.speaker
            print(f"\\n{current_speaker}:")
        print(f"  {segment.text}")
    '''
    print(code)


def example_translation():
    """
    Example 5: Translation to English
    
    Translate audio from any supported language to English.
    """
    print("\n" + "=" * 60)
    print("Example 5: Translation to English")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber, translate_file
    
    # Quick translation
    english_text = translate_file("german_podcast.mp3")
    print(english_text)
    
    # With more control
    transcriber = AudioTranscriber()
    result = transcriber.translate(
        "spanish_interview.mp3",
        prompt="Interview about renewable energy in Spain"
    )
    print(result.text)
    
    # Supported languages include:
    # Spanish, French, German, Italian, Portuguese, Dutch,
    # Japanese, Chinese, Korean, Russian, Arabic, Hindi,
    # and 50+ more languages
    '''
    print(code)


def example_timestamps():
    """
    Example 6: Word and Segment Timestamps
    
    Get precise timing information for video editing, subtitles, etc.
    """
    print("\n" + "=" * 60)
    print("Example 6: Timestamps")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # Word-level timestamps (whisper-1 only)
    result = transcriber.transcribe(
        "video_narration.mp3",
        model="whisper-1",
        timestamp_granularities=["word"]
    )
    
    for word_info in result.words:
        print(f"{word_info['word']} ({word_info['start']:.2f}s - {word_info['end']:.2f}s)")
    
    # Segment-level timestamps
    result = transcriber.transcribe(
        "lecture.mp3",
        model="whisper-1",
        timestamp_granularities=["segment"]
    )
    
    for segment in result.segments:
        print(f"[{segment.start:.1f}s] {segment.text}")
    '''
    print(code)


def example_streaming():
    """
    Example 7: Streaming Transcription
    
    Get real-time transcription output as it's generated.
    """
    print("\n" + "=" * 60)
    print("Example 7: Streaming Transcription")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # Stream transcription events
    print("Transcribing... ", end="", flush=True)
    
    full_text = ""
    for event in transcriber.transcribe_stream("lecture.mp3"):
        # Delta events contain partial text
        if hasattr(event, 'delta'):
            print(event.delta, end="", flush=True)
            full_text += event.delta
        
        # Done event signals completion
        if hasattr(event, 'type') and event.type == 'transcript.text.done':
            print("\\n\\nTranscription complete!")
    
    # With log probabilities for confidence
    for event in transcriber.transcribe_stream(
        "audio.mp3",
        include_logprobs=True
    ):
        if hasattr(event, 'logprobs'):
            # Log probs indicate model confidence
            print(f"Confidence: {event.logprobs}")
    '''
    print(code)


def example_large_files():
    """
    Example 8: Handling Large Files
    
    Files over 25MB need to be chunked before transcription.
    """
    print("\n" + "=" * 60)
    print("Example 8: Large File Handling")
    print("=" * 60)
    
    code = '''
    from audio_chunking import AudioChunker, chunk_and_transcribe
    from audio_transcription import AudioTranscriber
    
    # Quick check if chunking is needed
    chunker = AudioChunker()
    info = chunker.get_file_info("long_meeting.mp3")
    print(f"File size: {info['file_size_mb']:.1f} MB")
    print(f"Needs chunking: {info['needs_chunking']}")
    
    # Method 1: All-in-one convenience function
    full_transcript, chunk_transcripts = chunk_and_transcribe(
        "3hour_meeting.mp3",
        chunk_duration_minutes=10,
        model="gpt-4o-transcribe",
        prompt="Team meeting about Q4 roadmap"
    )
    print(full_transcript)
    
    # Method 2: Manual control over the process
    chunker = AudioChunker()
    chunks = chunker.split_audio(
        "long_podcast.mp3",
        chunk_duration_minutes=10,
        overlap_seconds=2  # Overlap helps maintain context
    )
    
    transcriber = AudioTranscriber()
    transcripts = []
    previous_ending = ""
    
    for chunk in chunks:
        print(f"Processing chunk {chunk.chunk_index + 1}/{chunk.total_chunks}")
        
        # Use end of previous transcript as context
        result = transcriber.transcribe(
            chunk.path,
            model="gpt-4o-transcribe",
            prompt=previous_ending if previous_ending else None
        )
        
        transcripts.append(result.text)
        previous_ending = result.text[-200:]  # Last 200 chars
    
    # Combine and cleanup
    full_text = chunker.combine_transcripts(transcripts, chunks)
    chunker.cleanup_chunks(chunks)
    
    print(full_text)
    '''
    print(code)


def example_output_formats():
    """
    Example 9: Different Output Formats
    
    Various output formats for different use cases.
    """
    print("\n" + "=" * 60)
    print("Example 9: Output Formats")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    
    transcriber = AudioTranscriber()
    
    # Plain text (default for gpt-4o models)
    result = transcriber.transcribe(
        "audio.mp3",
        response_format="text"
    )
    
    # JSON with metadata
    result = transcriber.transcribe(
        "audio.mp3",
        response_format="json"
    )
    
    # SRT subtitle format (whisper-1 only)
    result = transcriber.transcribe(
        "video_audio.mp3",
        model="whisper-1",
        response_format="srt"
    )
    # Returns: 
    # 1
    # 00:00:00,000 --> 00:00:04,500
    # Welcome to this presentation about AI.
    
    # VTT subtitle format (whisper-1 only)
    result = transcriber.transcribe(
        "video_audio.mp3",
        model="whisper-1",
        response_format="vtt"
    )
    
    # Verbose JSON with all metadata (whisper-1 only)
    result = transcriber.transcribe(
        "audio.mp3",
        model="whisper-1",
        response_format="verbose_json"
    )
    # Includes: text, segments, language, duration, task
    
    # Diarized JSON (gpt-4o-transcribe-diarize only)
    result = transcriber.transcribe_with_diarization(
        "meeting.wav",
        response_format="diarized_json"
    )
    '''
    print(code)


def example_error_handling():
    """
    Example 10: Error Handling and Validation
    
    Handle common errors gracefully.
    """
    print("\n" + "=" * 60)
    print("Example 10: Error Handling")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    import logging
    
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    transcriber = AudioTranscriber()
    
    try:
        result = transcriber.transcribe("audio.mp3")
        print(result.text)
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        
    except ValueError as e:
        # Unsupported format or invalid parameters
        print(f"Invalid input: {e}")
        
    except Exception as e:
        # API errors (rate limits, auth, etc.)
        print(f"API error: {e}")
    
    # Validate file before transcribing
    from pathlib import Path
    
    audio_path = Path("audio.mp3")
    
    # Check file exists
    if not audio_path.exists():
        print("File does not exist")
    
    # Check file size (25 MB limit)
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 25:
        print(f"File too large ({file_size_mb:.1f} MB). Use chunking.")
    
    # Check format
    supported = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    if audio_path.suffix.lower().lstrip(".") not in supported:
        print(f"Unsupported format: {audio_path.suffix}")
    '''
    print(code)


def example_post_processing():
    """
    Example 11: Post-Processing with GPT-4
    
    Clean up and enhance transcripts using GPT-4.
    """
    print("\n" + "=" * 60)
    print("Example 11: Post-Processing with GPT-4")
    print("=" * 60)
    
    code = '''
    from audio_transcription import AudioTranscriber
    from openai import OpenAI
    
    transcriber = AudioTranscriber()
    client = OpenAI()
    
    # Get raw transcript
    result = transcriber.transcribe("meeting.mp3")
    raw_transcript = result.text
    
    # Post-process with GPT-4 for cleanup
    system_prompt = """
    You are a helpful assistant that cleans up transcripts.
    Your tasks:
    1. Fix any obvious transcription errors
    2. Correct spelling of technical terms and proper nouns
    3. Add proper punctuation and paragraph breaks
    4. Format lists and key points
    
    Known terms: ACME Corp, TechFlow, DataPipe, Sarah Johnson (CEO)
    
    Return only the cleaned transcript, no explanations.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_transcript}
        ],
        temperature=0.3
    )
    
    clean_transcript = response.choices[0].message.content
    print(clean_transcript)
    
    # Extract action items
    action_prompt = """
    Extract all action items from this meeting transcript.
    Format each as: "- [OWNER] Task description"
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": action_prompt},
            {"role": "user", "content": raw_transcript}
        ]
    )
    
    print("\\nAction Items:")
    print(response.choices[0].message.content)
    '''
    print(code)


def print_all_examples():
    """Print all usage examples."""
    print("\n" + "=" * 60)
    print("AUDIO TRANSCRIPTION EXAMPLES")
    print("OpenAI Speech-to-Text API")
    print("=" * 60)
    
    example_basic_transcription()
    example_model_selection()
    example_prompting()
    example_diarization()
    example_translation()
    example_timestamps()
    example_streaming()
    example_large_files()
    example_output_formats()
    example_error_handling()
    example_post_processing()
    
    print("\n" + "=" * 60)
    print("END OF EXAMPLES")
    print("=" * 60)


if __name__ == "__main__":
    print_all_examples()
