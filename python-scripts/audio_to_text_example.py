#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script demonstrating audio-to-text functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.audio_to_text import (
    AudioToTextProcessor,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    create_correction_prompt,
)


def example_basic_transcription(audio_file: str):
    """Example: Basic transcription"""
    print("\n" + "="*60)
    print("Example 1: Basic Transcription")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format=ResponseFormat.TEXT,
    )
    
    print(f"Transcribing: {audio_file}")
    result = processor.transcribe(audio_file, config)
    print(f"\nTranscript:\n{result.text}")


def example_transcription_with_prompt(audio_file: str):
    """Example: Transcription with prompt for better accuracy"""
    print("\n" + "="*60)
    print("Example 2: Transcription with Prompt")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.GPT_4O_TRANSCRIBE,
        response_format=ResponseFormat.TEXT,
        prompt="The following conversation is a lecture about the recent developments around OpenAI, GPT-4.5 and the future of AI.",
    )
    
    print(f"Transcribing with context prompt: {audio_file}")
    result = processor.transcribe(audio_file, config)
    print(f"\nTranscript:\n{result.text}")


def example_transcription_with_timestamps(audio_file: str):
    """Example: Transcription with word-level timestamps"""
    print("\n" + "="*60)
    print("Example 3: Transcription with Word-Level Timestamps")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    config = TranscriptionConfig(
        model=TranscriptionModel.WHISPER_1,
        response_format=ResponseFormat.VERBOSE_JSON,
        timestamp_granularities=[TimestampGranularity.WORD],
    )
    
    print(f"Transcribing with timestamps: {audio_file}")
    result = processor.transcribe(audio_file, config)
    
    print(f"\nFull transcript: {result.text}")
    
    if result.words:
        print("\nWord-level timestamps:")
        for word in result.words[:20]:  # Show first 20 words
            word_text = word.get('word', '')
            start = word.get('start', 0)
            end = word.get('end', 0)
            print(f"  {word_text:20s} {start:6.2f}s - {end:6.2f}s")
        if len(result.words) > 20:
            print(f"  ... ({len(result.words) - 20} more words)")


def example_speaker_diarization(audio_file: str, speaker_refs: dict = None):
    """Example: Transcription with speaker diarization"""
    print("\n" + "="*60)
    print("Example 4: Speaker Diarization")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    print(f"Transcribing with speaker diarization: {audio_file}")
    
    try:
        result = processor.transcribe_with_diarization(
            audio_file,
            speaker_references=speaker_refs,
        )
        
        print(f"\nFull transcript: {result.text}")
        
        if result.segments:
            print("\nSpeaker segments:")
            for segment in result.segments[:10]:  # Show first 10 segments
                speaker = segment.get('speaker', 'Unknown')
                text = segment.get('text', '')
                start = segment.get('start', 0)
                end = segment.get('end', 0)
                print(f"  [{speaker}] ({start:.2f}s - {end:.2f}s): {text}")
            if len(result.segments) > 10:
                print(f"  ... ({len(result.segments) - 10} more segments)")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Speaker diarization requires gpt-4o-transcribe-diarize model")


def example_streaming_transcription(audio_file: str):
    """Example: Streaming transcription"""
    print("\n" + "="*60)
    print("Example 5: Streaming Transcription")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    print(f"Streaming transcription: {audio_file}")
    print("\nReceiving events...")
    
    event_count = 0
    for event in processor.transcribe_stream(audio_file):
        event_count += 1
        event_type = event.get('type', 'unknown')
        print(f"  Event {event_count}: {event_type}")
        
        if 'delta' in event:
            print(f"    Delta: {event['delta']}")
        if 'text' in event:
            print(f"    Text: {event['text']}")
        
        # Limit output for demo
        if event_count >= 10:
            print("  ... (truncated)")
            break


def example_translation(audio_file: str):
    """Example: Translate audio to English"""
    print("\n" + "="*60)
    print("Example 6: Translation to English")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    print(f"Translating to English: {audio_file}")
    result = processor.translate(audio_file)
    print(f"\nTranslated text:\n{result.text}")


def example_post_processing(audio_file: str):
    """Example: Post-process transcript with GPT-4"""
    print("\n" + "="*60)
    print("Example 7: Post-Processing with GPT-4")
    print("="*60)
    
    processor = AudioToTextProcessor()
    
    # First, transcribe
    print(f"Step 1: Transcribing {audio_file}")
    config = TranscriptionConfig(
        model=TranscriptionModel.WHISPER_1,
        response_format=ResponseFormat.TEXT,
    )
    raw_transcript = processor.transcribe(audio_file, config).text
    print(f"\nRaw transcript:\n{raw_transcript[:200]}...")
    
    # Then, correct with GPT-4
    print("\nStep 2: Post-processing with GPT-4")
    system_prompt = create_correction_prompt(
        company_name="ZyntriQix",
        product_names=[
            "ZyntriQix",
            "Digique Plus",
            "CynapseFive",
            "VortiQore V8",
            "EchoNix Array",
            "OrbitalLink Seven",
        ],
        additional_instructions="Preserve filler words like 'um', 'uh', 'like' if they appear in the original.",
    )
    
    try:
        corrected = processor.post_process_with_gpt4(
            raw_transcript,
            system_prompt,
            model="gpt-4",
        )
        print(f"\nCorrected transcript:\n{corrected[:200]}...")
    except Exception as e:
        print(f"Error during post-processing: {e}")
        print("Note: This requires GPT-4 access")


def main():
    """Main function to run examples"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Audio to Text Examples")
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to audio file to transcribe",
    )
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="Example number to run (1-7). If not specified, runs all examples.",
    )
    parser.add_argument(
        "--speaker-refs",
        type=str,
        nargs="+",
        help="Speaker reference files for diarization (format: name:path)",
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    # Parse speaker references if provided
    speaker_refs = None
    if args.speaker_refs:
        speaker_refs = {}
        for ref in args.speaker_refs:
            if ":" in ref:
                name, path = ref.split(":", 1)
                speaker_refs[name] = path
            else:
                print(f"Warning: Invalid speaker reference format: {ref}. Use 'name:path'")
    
    examples = {
        1: lambda: example_basic_transcription(args.audio_file),
        2: lambda: example_transcription_with_prompt(args.audio_file),
        3: lambda: example_transcription_with_timestamps(args.audio_file),
        4: lambda: example_speaker_diarization(args.audio_file, speaker_refs),
        5: lambda: example_streaming_transcription(args.audio_file),
        6: lambda: example_translation(args.audio_file),
        7: lambda: example_post_processing(args.audio_file),
    }
    
    if args.example:
        print(f"\nRunning Example {args.example}...")
        examples[args.example]()
    else:
        print("Running all examples...")
        print("Note: Some examples may fail if the audio file format or content doesn't match the example.")
        for i, example_func in examples.items():
            try:
                example_func()
            except Exception as e:
                print(f"\nExample {i} failed: {e}")
                print("Continuing with next example...\n")


if __name__ == "__main__":
    main()
