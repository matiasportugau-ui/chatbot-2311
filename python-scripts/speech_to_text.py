#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Speech-to-text CLI using the OpenAI Audio API.

Supports:
- Transcriptions: whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe,
  gpt-4o-transcribe-diarize
- Translations (to English): whisper-1

Examples:
  python3 python-scripts/speech_to_text.py transcribe ./audio.mp3 \
    --model gpt-4o-transcribe --response-format text

  python3 python-scripts/speech_to_text.py translate ./german.mp3

  python3 python-scripts/speech_to_text.py transcribe ./meeting.wav \
    --model gpt-4o-transcribe-diarize --response-format diarized_json \
    --chunking-strategy auto --known-speaker agent:./agent.wav
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI


MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True)
class KnownSpeaker:
    name: str
    reference_path: Path


def _guess_audio_mime(path: Path) -> str:
    # mimetypes is conservative but good enough for data URLs.
    mime, _ = mimetypes.guess_type(str(path))
    if mime:
        return mime

    # Minimal fallback mapping.
    ext = path.suffix.lower()
    return {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".mpga": "audio/mpeg",
        ".mpeg": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
    }.get(ext, "application/octet-stream")


def _to_data_url(path: Path) -> str:
    mime = _guess_audio_mime(path)
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _parse_known_speakers(values: list[str]) -> list[KnownSpeaker]:
    speakers: list[KnownSpeaker] = []
    for raw in values:
        if ":" not in raw:
            raise ValueError(
                "Invalid --known-speaker value. Use name:/path/to/reference.wav"
            )
        name, path_str = raw.split(":", 1)
        path = Path(path_str).expanduser().resolve()
        if not name.strip():
            raise ValueError("Known speaker name cannot be empty")
        if not path.exists():
            raise FileNotFoundError(f"Known speaker reference not found: {path}")
        speakers.append(KnownSpeaker(name=name.strip(), reference_path=path))

    if len(speakers) > 4:
        raise ValueError("At most 4 known speakers are supported")
    return speakers


def _warn_if_too_large(path: Path) -> None:
    try:
        size = path.stat().st_size
    except OSError:
        return

    if size > MAX_UPLOAD_BYTES:
        mb = size / (1024 * 1024)
        print(
            f"WARNING: audio file is {mb:.1f} MB; API uploads are limited to 25 MB.",
            file=sys.stderr,
        )


def _write_output(text: str, out_path: str | None) -> None:
    if out_path:
        Path(out_path).write_text(text, encoding="utf-8")
        return
    print(text)


def transcribe(args: argparse.Namespace) -> int:
    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 2

    _warn_if_too_large(audio_path)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    known_speakers = _parse_known_speakers(args.known_speaker)

    extra_body: dict[str, Any] = {}
    if known_speakers:
        extra_body["known_speaker_names"] = [s.name for s in known_speakers]
        extra_body["known_speaker_references"] = [_to_data_url(s.reference_path) for s in known_speakers]

    create_kwargs: dict[str, Any] = {
        "model": args.model,
        "file": audio_path.open("rb"),
    }

    if args.response_format:
        create_kwargs["response_format"] = args.response_format

    if args.prompt:
        create_kwargs["prompt"] = args.prompt

    if args.language:
        create_kwargs["language"] = args.language

    if args.chunking_strategy is not None:
        create_kwargs["chunking_strategy"] = args.chunking_strategy

    if extra_body:
        create_kwargs["extra_body"] = extra_body

    if args.stream:
        create_kwargs["stream"] = True

        stream = client.audio.transcriptions.create(**create_kwargs)
        # Stream yields events; print deltas when available.
        for event in stream:
            event_type = getattr(event, "type", None) or (event.get("type") if isinstance(event, dict) else None)
            if event_type == "transcript.text.delta":
                delta = getattr(event, "delta", None) or (event.get("delta") if isinstance(event, dict) else None)
                if delta:
                    sys.stdout.write(str(delta))
                    sys.stdout.flush()
            elif event_type in {"transcript.text.segment", "transcript.text.done"}:
                # For segment/done events, keep default behavior silent; users can
                # rerun without --stream to get full structured output.
                continue
            else:
                # Fallback: print unknown events as JSON line.
                try:
                    print(json.dumps(event, ensure_ascii=False))
                except TypeError:
                    print(str(event))
        if sys.stdout.isatty():
            print()
        return 0

    result = client.audio.transcriptions.create(**create_kwargs)

    # Prefer structured diarization output if present.
    if args.response_format == "diarized_json" and hasattr(result, "segments"):
        payload = {"text": getattr(result, "text", ""), "segments": result.segments}
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        _write_output(text, args.out)
        return 0

    text = getattr(result, "text", None)
    if text is None:
        # Last-resort: stringify whole object.
        _write_output(str(result), args.out)
        return 0

    _write_output(text, args.out)
    return 0


def translate(args: argparse.Namespace) -> int:
    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 2

    _warn_if_too_large(audio_path)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    create_kwargs: dict[str, Any] = {
        "model": "whisper-1",
        "file": audio_path.open("rb"),
    }

    result = client.audio.translations.create(**create_kwargs)

    text = getattr(result, "text", None)
    if text is None:
        _write_output(str(result), args.out)
        return 0

    _write_output(text, args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Speech-to-text with OpenAI Audio API")
    sub = parser.add_subparsers(dest="command", required=True)

    p_transcribe = sub.add_parser("transcribe", help="Transcribe audio to text")
    p_transcribe.add_argument("audio", help="Path to audio file")
    p_transcribe.add_argument(
        "--model",
        default="gpt-4o-transcribe",
        help=(
            "Transcription model (e.g. gpt-4o-transcribe, gpt-4o-mini-transcribe, "
            "gpt-4o-transcribe-diarize, whisper-1)"
        ),
    )
    p_transcribe.add_argument(
        "--response-format",
        default=None,
        help=(
            "Response format. For whisper-1: json/text/srt/verbose_json/vtt. "
            "For gpt-4o-* transcribe: json/text. For diarize: json/text/diarized_json."
        ),
    )
    p_transcribe.add_argument("--prompt", default=None, help="Optional transcription prompt")
    p_transcribe.add_argument(
        "--language",
        default=None,
        help="Optional language hint (ISO code, when supported)",
    )
    p_transcribe.add_argument(
        "--stream",
        action="store_true",
        help="Stream transcript deltas (supported for GPT-4o transcribe models)",
    )
    p_transcribe.add_argument(
        "--chunking-strategy",
        default=None,
        help=(
            "Chunking strategy (required for diarize when audio > 30s). "
            "Use 'auto' unless you have a VAD config."
        ),
    )
    p_transcribe.add_argument(
        "--known-speaker",
        action="append",
        default=[],
        help=(
            "Map diarization speakers to known references. Repeatable. "
            "Format: name:/path/to/reference.wav (2-10 seconds recommended)."
        ),
    )
    p_transcribe.add_argument("--out", default=None, help="Write output to file instead of stdout")
    p_transcribe.set_defaults(func=transcribe)

    p_translate = sub.add_parser("translate", help="Translate audio to English (whisper-1)")
    p_translate.add_argument("audio", help="Path to audio file")
    p_translate.add_argument("--out", default=None, help="Write output to file instead of stdout")
    p_translate.set_defaults(func=translate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
