#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for speech-to-text transcription
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from speech_to_text import (
        SpeechToText,
        TranscriptionModel,
        ResponseFormat,
        TimestampGranularity
    )
except ImportError:
    print("Error: speech_to_text module not found.")
    print("Make sure you're running from the python-scripts directory.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI Audio API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription
  python transcribe_cli.py audio.mp3
  
  # Use specific model
  python transcribe_cli.py audio.mp3 --model gpt-4o-transcribe
  
  # Translate to English
  python transcribe_cli.py audio.mp3 --translate
  
  # Speaker diarization
  python transcribe_cli.py meeting.wav --diarize
  
  # Output to file
  python transcribe_cli.py audio.mp3 --output transcript.txt
  
  # With prompt
  python transcribe_cli.py lecture.mp3 --prompt "This is a lecture about AI"
  
  # Word-level timestamps
  python transcribe_cli.py audio.mp3 --timestamps word
        """
    )
    
    parser.add_argument(
        'audio_file',
        type=str,
        help='Path to audio file (mp3, wav, mp4, etc.)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['whisper-1', 'gpt-4o-transcribe', 'gpt-4o-mini-transcribe', 'gpt-4o-transcribe-diarize'],
        default='gpt-4o-mini-transcribe',
        help='Model to use for transcription (default: gpt-4o-mini-transcribe)'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        help='Language code (ISO 639-1 or 639-3). Auto-detected if not specified.'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        help='Optional prompt to improve transcription quality'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'text', 'srt', 'verbose_json', 'vtt', 'diarized_json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--translate',
        action='store_true',
        help='Translate to English (only works with whisper-1)'
    )
    
    parser.add_argument(
        '--diarize',
        action='store_true',
        help='Enable speaker diarization (requires gpt-4o-transcribe-diarize)'
    )
    
    parser.add_argument(
        '--timestamps',
        type=str,
        choices=['word', 'segment'],
        help='Include timestamps (word or segment level)'
    )
    
    parser.add_argument(
        '--post-process',
        action='store_true',
        help='Post-process transcription with GPT-4 for improved accuracy'
    )
    
    parser.add_argument(
        '--correction-terms',
        type=str,
        nargs='+',
        help='Terms to correct during post-processing (e.g., --correction-terms GPT-3 DALL·E)'
    )
    
    parser.add_argument(
        '--gpt-model',
        type=str,
        default='gpt-4o',
        help='GPT model for post-processing (default: gpt-4o)'
    )
    
    parser.add_argument(
        '--stream',
        action='store_true',
        help='Stream transcription results (not supported for whisper-1)'
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Set it with: export OPENAI_API_KEY='sk-your-key'")
        sys.exit(1)
    
    # Check file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    # Initialize STT
    try:
        model = TranscriptionModel(args.model)
        stt = SpeechToText(model=model.value)
    except Exception as e:
        print(f"Error initializing SpeechToText: {e}")
        sys.exit(1)
    
    # Handle translation
    if args.translate:
        if args.model != 'whisper-1':
            print("Warning: Translation only works with whisper-1. Switching model...")
            args.model = 'whisper-1'
        
        try:
            result = stt.translate(
                args.audio_file,
                prompt=args.prompt,
                response_format=args.format
            )
            output_text = result.text
        except Exception as e:
            print(f"Error during translation: {e}")
            sys.exit(1)
    
    # Handle diarization
    elif args.diarize:
        if args.model != 'gpt-4o-transcribe-diarize':
            print("Warning: Diarization requires gpt-4o-transcribe-diarize. Switching model...")
            args.model = 'gpt-4o-transcribe-diarize'
        
        try:
            segments = stt.transcribe_with_diarization(
                args.audio_file,
                chunking_strategy='auto'
            )
            
            # Format output
            output_lines = []
            for segment in segments:
                output_lines.append(
                    f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.speaker}: {segment.text}"
                )
            output_text = '\n'.join(output_lines)
        except Exception as e:
            print(f"Error during diarization: {e}")
            sys.exit(1)
    
    # Handle streaming
    elif args.stream:
        if args.model == 'whisper-1':
            print("Error: Streaming not supported for whisper-1")
            sys.exit(1)
        
        try:
            print("Streaming transcription...")
            output_text = ""
            for event in stt.transcribe_streaming(
                args.audio_file,
                model=args.model,
                language=args.language,
                prompt=args.prompt,
                response_format=args.format
            ):
                if event['event'] == 'transcript.text.delta':
                    delta = event['data'].get('delta', '')
                    print(delta, end='', flush=True)
                    output_text += delta
                elif event['event'] == 'transcript.text.done':
                    full_text = event['data'].get('text', '')
                    output_text = full_text
                    print()  # New line after streaming
        except Exception as e:
            print(f"\nError during streaming: {e}")
            sys.exit(1)
    
    # Handle post-processing
    elif args.post_process:
        try:
            output_text = stt.transcribe_with_post_processing(
                args.audio_file,
                system_prompt=None,
                correction_terms=args.correction_terms,
                model=args.model,
                gpt_model=args.gpt_model
            )
        except Exception as e:
            print(f"Error during post-processing: {e}")
            sys.exit(1)
    
    # Standard transcription
    else:
        try:
            timestamp_granularities = None
            if args.timestamps:
                timestamp_granularities = [args.timestamps]
            
            result = stt.transcribe(
                args.audio_file,
                model=args.model,
                language=args.language,
                prompt=args.prompt,
                response_format=args.format,
                timestamp_granularities=timestamp_granularities
            )
            
            # Format output based on format
            if args.format == 'verbose_json' and result.words:
                output_lines = []
                for word in result.words:
                    output_lines.append(
                        f"{word.get('word', '')} [{word.get('start', 0):.2f}s - {word.get('end', 0):.2f}s]"
                    )
                output_text = '\n'.join(output_lines)
            else:
                output_text = result.text
                
        except Exception as e:
            print(f"Error during transcription: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Output result
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"\n✅ Transcription saved to: {args.output}")
    else:
        print("\n" + "="*60)
        print("TRANSCRIPTION RESULT")
        print("="*60)
        print(output_text)
        print("="*60)


if __name__ == "__main__":
    main()
