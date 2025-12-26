#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio to Text Examples
======================

Example scripts demonstrating various use cases for the audio-to-text module.

Run any example with:
    python audio_examples.py <example_name> <audio_file>

Available examples:
    - basic: Basic transcription
    - translate: Translation to English
    - diarize: Speaker diarization
    - timestamps: Word-level timestamps
    - stream: Streaming transcription
    - long: Long audio transcription
    - correct: Post-processing with GPT-4
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_basic_transcription(audio_file: str):
    """
    Basic transcription example.
    
    Transcribes audio using gpt-4o-transcribe model.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("BASIC TRANSCRIPTION EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Simple transcription
    result = processor.transcribe(
        audio_file,
        model="gpt-4o-transcribe",
        response_format="json"
    )
    
    print(f"\nTranscribed text:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)
    
    if result.language:
        print(f"Language: {result.language}")
    if result.duration:
        print(f"Duration: {result.duration:.2f} seconds")


def example_translation(audio_file: str):
    """
    Translation example.
    
    Translates audio in any language to English using whisper-1.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("TRANSLATION EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Translate to English
    result = processor.translate(
        audio_file,
        response_format="json"
    )
    
    print(f"\nEnglish translation:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)


def example_diarization(audio_file: str):
    """
    Speaker diarization example.
    
    Identifies different speakers in the audio.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("SPEAKER DIARIZATION EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Transcribe with speaker diarization
    result = processor.transcribe_with_diarization(
        audio_file,
        chunking_strategy="auto",
        response_format="diarized_json"
    )
    
    print(f"\nFull text:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)
    
    if result.segments:
        print(f"\nSpeaker segments ({len(result.segments)} total):")
        print("-" * 40)
        for segment in result.segments:
            time_str = f"[{segment.start:.1f}s - {segment.end:.1f}s]"
            print(f"{segment.speaker} {time_str}: {segment.text}")


def example_diarization_with_speakers(audio_file: str, speaker_ref_file: str = None):
    """
    Diarization with known speakers example.
    
    Identifies speakers using reference audio clips.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("DIARIZATION WITH KNOWN SPEAKERS")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Prepare known speakers if reference provided
    known_names = None
    known_refs = None
    
    if speaker_ref_file and os.path.exists(speaker_ref_file):
        known_names = ["Speaker_A"]
        known_refs = [processor._to_data_url(speaker_ref_file)]
        print(f"Using reference: {speaker_ref_file}")
    
    result = processor.transcribe_with_diarization(
        audio_file,
        chunking_strategy="auto",
        known_speaker_names=known_names,
        known_speaker_references=known_refs,
        response_format="diarized_json"
    )
    
    print(f"\nSpeaker segments:")
    print("-" * 40)
    for segment in result.segments:
        print(f"{segment.speaker}: {segment.text}")


def example_timestamps(audio_file: str):
    """
    Word-level timestamps example.
    
    Gets precise timing for each word (useful for subtitles, video editing).
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("WORD TIMESTAMPS EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Transcribe with word timestamps
    result = processor.transcribe_with_timestamps(
        audio_file,
        granularities=["word", "segment"]
    )
    
    print(f"\nFull text:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)
    
    if result.words:
        print(f"\nWord timestamps ({len(result.words)} words):")
        print("-" * 40)
        for word_info in result.words[:20]:  # Show first 20 words
            print(f"  {word_info['word']:15} [{word_info['start']:.2f}s - {word_info['end']:.2f}s]")
        
        if len(result.words) > 20:
            print(f"  ... and {len(result.words) - 20} more words")
    
    if result.segments:
        print(f"\nSegment timestamps ({len(result.segments)} segments):")
        print("-" * 40)
        for segment in result.segments[:5]:  # Show first 5 segments
            print(f"  [{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text[:60]}...")


def example_streaming(audio_file: str):
    """
    Streaming transcription example.
    
    Receives transcription results as they become available.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("STREAMING TRANSCRIPTION EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    print("\nStreaming transcription:")
    print("-" * 40)
    
    full_text = ""
    
    for event in processor.transcribe_stream(
        audio_file,
        model="gpt-4o-mini-transcribe",
        response_format="text"
    ):
        event_type = event.get("type", "unknown")
        data = event.get("data")
        
        if hasattr(data, "delta"):
            print(data.delta, end="", flush=True)
            full_text += data.delta
        elif event_type == "transcript.text.done":
            print("\n")
            print("-" * 40)
            print("Streaming complete!")


def example_long_audio(audio_file: str):
    """
    Long audio transcription example.
    
    Handles files larger than 25 MB by chunking.
    """
    from audio_chunker import LongAudioTranscriber, AudioChunker
    
    print("=" * 60)
    print("LONG AUDIO TRANSCRIPTION EXAMPLE")
    print("=" * 60)
    
    # First, get audio info
    chunker = AudioChunker()
    
    try:
        info = chunker.get_audio_info(audio_file)
        print(f"\nAudio Information:")
        print(f"  File: {info['file_path']}")
        print(f"  Size: {info['file_size_mb']:.2f} MB")
        print(f"  Duration: {info['duration_minutes']:.1f} minutes")
        print(f"  Needs chunking: {info['needs_chunking']}")
    except ImportError:
        print("\nNote: pydub not installed, proceeding with direct transcription")
        info = {"needs_chunking": False}
    
    # Transcribe (with chunking if needed)
    transcriber = LongAudioTranscriber()
    
    print("\nTranscribing...")
    text = transcriber.transcribe_long_audio(
        audio_file,
        model="gpt-4o-transcribe",
        chunk_duration_minutes=10
    )
    
    print(f"\nTranscribed text:")
    print("-" * 40)
    print(text)
    print("-" * 40)


def example_post_processing(audio_file: str):
    """
    Post-processing with GPT-4 example.
    
    Corrects transcription using GPT-4 for domain-specific terms.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("POST-PROCESSING EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # First, get raw transcription
    print("\n1. Getting raw transcription...")
    result = processor.transcribe(
        audio_file,
        model="whisper-1"  # Using whisper for raw transcription
    )
    
    print(f"\nRaw transcription:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)
    
    # Define correction context for BMC Uruguay
    correction_context = """
    You are a helpful assistant for BMC Uruguay, a company specializing in 
    thermal insulation products. Your task is to correct any spelling 
    discrepancies in the transcribed text.
    
    Make sure the following terms are spelled correctly:
    - Products: Isodec, Poliestireno, Lana de Roca, Poliuretano, Fibra de Vidrio
    - Company: BMC Uruguay
    - Terms: aislamiento térmico, cotización, espesor, metros cuadrados
    
    Only add necessary punctuation and capitalization. Use only the context provided.
    Maintain the original meaning and don't add information not in the original text.
    """
    
    # Correct transcription
    print("\n2. Correcting with GPT-4...")
    corrected = processor.correct_transcription(
        result.text,
        correction_context,
        model="gpt-4.1",
        temperature=0.0
    )
    
    print(f"\nCorrected transcription:")
    print("-" * 40)
    print(corrected)
    print("-" * 40)


def example_with_prompt(audio_file: str):
    """
    Transcription with prompt example.
    
    Uses prompt to improve accuracy for specific domains.
    """
    from audio_to_text import AudioToText
    
    print("=" * 60)
    print("TRANSCRIPTION WITH PROMPT EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Define domain-specific prompt
    prompt = """
    The following audio is about thermal insulation products and construction.
    Key terms include: Isodec, poliestireno, lana de roca, poliuretano,
    aislamiento térmico, BMC Uruguay, cotización, presupuesto.
    """
    
    result = processor.transcribe(
        audio_file,
        model="gpt-4o-transcribe",
        prompt=prompt
    )
    
    print(f"\nTranscription with domain prompt:")
    print("-" * 40)
    print(result.text)
    print("-" * 40)


def example_batch_processing(audio_dir: str):
    """
    Batch processing example.
    
    Processes multiple audio files in a directory.
    """
    from audio_to_text import AudioToText
    from pathlib import Path
    
    print("=" * 60)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 60)
    
    processor = AudioToText()
    
    # Get all audio files in directory
    audio_extensions = {".mp3", ".wav", ".m4a", ".mp4", ".webm"}
    audio_files = [
        f for f in Path(audio_dir).iterdir()
        if f.suffix.lower() in audio_extensions
    ]
    
    if not audio_files:
        print(f"No audio files found in {audio_dir}")
        return
    
    print(f"\nFound {len(audio_files)} audio files")
    print("-" * 40)
    
    results = {}
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\nProcessing {i}/{len(audio_files)}: {audio_file.name}")
        
        try:
            result = processor.transcribe(str(audio_file))
            results[audio_file.name] = {
                "status": "success",
                "text": result.text
            }
            print(f"  ✓ Transcribed ({len(result.text)} chars)")
        except Exception as e:
            results[audio_file.name] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"Successful: {success_count}/{len(audio_files)}")
    
    for filename, result in results.items():
        status = "✓" if result["status"] == "success" else "✗"
        print(f"  {status} {filename}")


# Map of example names to functions
EXAMPLES = {
    "basic": example_basic_transcription,
    "translate": example_translation,
    "diarize": example_diarization,
    "timestamps": example_timestamps,
    "stream": example_streaming,
    "long": example_long_audio,
    "correct": example_post_processing,
    "prompt": example_with_prompt,
    "batch": example_batch_processing,
}


def main():
    """Main entry point for examples."""
    if len(sys.argv) < 3:
        print("Audio to Text Examples")
        print("=" * 40)
        print("\nUsage: python audio_examples.py <example_name> <audio_file>")
        print("\nAvailable examples:")
        for name, func in EXAMPLES.items():
            doc = func.__doc__.split("\n")[1].strip() if func.__doc__ else ""
            print(f"  {name:12} - {doc}")
        print("\nExample:")
        print("  python audio_examples.py basic recording.mp3")
        print("  python audio_examples.py diarize meeting.wav")
        print("  python audio_examples.py batch ./audio_folder/")
        sys.exit(1)
    
    example_name = sys.argv[1].lower()
    audio_input = sys.argv[2]
    
    if example_name not in EXAMPLES:
        print(f"Unknown example: {example_name}")
        print(f"Available examples: {', '.join(EXAMPLES.keys())}")
        sys.exit(1)
    
    # Check for OPENAI_API_KEY
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Run the example
    try:
        EXAMPLES[example_name](audio_input)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
