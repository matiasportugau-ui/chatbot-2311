#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI tool for audio-to-text transcription
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from utils.audio_to_text import (
    AudioToTextProcessor,
    TranscriptionConfig,
    TranscriptionModel,
    ResponseFormat,
    TimestampGranularity,
    create_correction_prompt,
)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files to text using OpenAI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription
  python audio_to_text_cli.py audio.mp3

  # Transcription with prompt
  python audio_to_text_cli.py audio.mp3 --prompt "This is a lecture about AI"

  # Transcription with timestamps
  python audio_to_text_cli.py audio.mp3 --timestamps word --format verbose_json

  # Speaker diarization
  python audio_to_text_cli.py meeting.wav --diarize --speaker-refs agent:agent.wav customer:customer.wav

  # Translation to English
  python audio_to_text_cli.py german.mp3 --translate

  # Post-process with GPT-4
  python audio_to_text_cli.py audio.mp3 --post-process --company "MyCompany" --products "Product1,Product2"
        """
    )
    
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to audio file to transcribe",
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe", "gpt-4o-transcribe-diarize"],
        default="gpt-4o-transcribe",
        help="Model to use for transcription",
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "srt", "verbose_json", "vtt", "diarized_json"],
        default="text",
        help="Response format",
    )
    
    parser.add_argument(
        "--language",
        type=str,
        help="Language code (e.g., 'en', 'es', 'fr'). If not specified, auto-detected.",
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt to improve transcription accuracy",
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for transcription (0.0-1.0)",
    )
    
    parser.add_argument(
        "--timestamps",
        type=str,
        choices=["word", "segment"],
        nargs="+",
        help="Include timestamps at word or segment level",
    )
    
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Translate audio to English (only works with whisper-1)",
    )
    
    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Enable speaker diarization",
    )
    
    parser.add_argument(
        "--speaker-refs",
        type=str,
        nargs="+",
        help="Speaker reference files (format: name:path)",
    )
    
    parser.add_argument(
        "--chunking-strategy",
        type=str,
        default="auto",
        help="Chunking strategy for diarization (default: auto)",
    )
    
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream transcription results",
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (if not specified, prints to stdout)",
    )
    
    parser.add_argument(
        "--post-process",
        action="store_true",
        help="Post-process transcript with GPT-4",
    )
    
    parser.add_argument(
        "--company",
        type=str,
        help="Company name for post-processing",
    )
    
    parser.add_argument(
        "--products",
        type=str,
        help="Comma-separated list of product names for post-processing",
    )
    
    parser.add_argument(
        "--gpt-model",
        type=str,
        default="gpt-4",
        help="GPT model to use for post-processing",
    )
    
    parser.add_argument(
        "--split",
        type=int,
        metavar="MINUTES",
        help="Split audio file into chunks of specified minutes before processing",
    )
    
    args = parser.parse_args()
    
    # Validate audio file
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        processor = AudioToTextProcessor()
        
        # Handle audio splitting if requested
        audio_files = [args.audio_file]
        if args.split:
            print(f"Splitting audio into {args.split}-minute chunks...")
            audio_files = processor.split_audio_file(args.audio_file, args.split)
            print(f"Created {len(audio_files)} chunks")
        
        # Process each audio file
        all_results = []
        
        for audio_file in audio_files:
            print(f"\nProcessing: {audio_file}")
            
            # Handle translation
            if args.translate:
                result = processor.translate(audio_file, model="whisper-1")
                all_results.append(result.text)
                continue
            
            # Build configuration
            model = TranscriptionModel(args.model)
            
            # Override model for diarization
            if args.diarize:
                model = TranscriptionModel.GPT_4O_TRANSCRIBE_DIARIZE
                args.format = "diarized_json"
            
            config = TranscriptionConfig(
                model=model,
                response_format=ResponseFormat(args.format),
                language=args.language,
                prompt=args.prompt,
                temperature=args.temperature,
                stream=args.stream,
            )
            
            # Add timestamps if requested
            if args.timestamps:
                granularities = []
                if "word" in args.timestamps:
                    granularities.append(TimestampGranularity.WORD)
                if "segment" in args.timestamps:
                    granularities.append(TimestampGranularity.SEGMENT)
                config.timestamp_granularities = granularities
            
            # Handle speaker diarization
            if args.diarize:
                speaker_refs = None
                if args.speaker_refs:
                    speaker_refs = {}
                    for ref in args.speaker_refs:
                        if ":" not in ref:
                            print(f"Warning: Invalid speaker reference format: {ref}. Use 'name:path'", file=sys.stderr)
                            continue
                        name, path = ref.split(":", 1)
                        if not os.path.exists(path):
                            print(f"Warning: Speaker reference file not found: {path}", file=sys.stderr)
                            continue
                        speaker_refs[name] = path
                
                config.chunking_strategy = args.chunking_strategy
                result = processor.transcribe_with_diarization(
                    audio_file,
                    speaker_references=speaker_refs,
                )
            else:
                # Handle streaming
                if args.stream:
                    print("Streaming transcription...")
                    events = []
                    for event in processor.transcribe_stream(audio_file, config):
                        events.append(event)
                        event_type = event.get('type', 'unknown')
                        if 'delta' in event:
                            print(event['delta'], end='', flush=True)
                        elif event_type == 'transcript.text.done':
                            print()  # New line after done
                    
                    # Extract final text from events
                    final_event = events[-1] if events else {}
                    result_text = final_event.get('text', '')
                    all_results.append(result_text)
                    continue
                else:
                    result = processor.transcribe(audio_file, config)
            
            # Post-process if requested
            if args.post_process:
                print("Post-processing with GPT-4...")
                system_prompt = create_correction_prompt(
                    company_name=args.company or "Company",
                    product_names=args.products.split(",") if args.products else [],
                )
                
                transcript_text = result.text if isinstance(result, type(result)) else str(result)
                corrected = processor.post_process_with_gpt4(
                    transcript_text,
                    system_prompt,
                    model=args.gpt_model,
                )
                all_results.append(corrected)
            else:
                # Format output based on response format
                if args.format == "json" or args.format == "verbose_json" or args.format == "diarized_json":
                    if isinstance(result, type(result)) and hasattr(result, 'raw_response'):
                        all_results.append(json.dumps(result.raw_response, indent=2, ensure_ascii=False))
                    else:
                        all_results.append(json.dumps({"text": result.text}, indent=2, ensure_ascii=False))
                else:
                    all_results.append(result.text)
        
        # Combine results if multiple files
        final_output = "\n\n".join(all_results) if len(all_results) > 1 else all_results[0]
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"\n✓ Results saved to: {args.output}")
        else:
            print("\n" + "="*60)
            print("TRANSCRIPTION RESULT")
            print("="*60)
            print(final_output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
