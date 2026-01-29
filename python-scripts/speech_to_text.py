#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Speech-to-text CLI (OpenAI Audio API).

Supports:
- Transcriptions: whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
- Diarized transcriptions: gpt-4o-transcribe-diarize
- Translations (to English): whisper-1

Examples:
  python3 python-scripts/speech_to_text.py transcribe path/to/audio.mp3
  python3 python-scripts/speech_to_text.py transcribe path/to/audio.mp3 --model gpt-4o-transcribe --response-format text
  python3 python-scripts/speech_to_text.py diarize meeting.wav --chunking-strategy auto --known-speaker agent=agent.wav
  python3 python-scripts/speech_to_text.py translate german.mp3

Auth:
- Uses OPENAI_API_KEY from environment or unified_credentials_manager if available.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _try_get_openai_key() -> Optional[str]:
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    try:
        # Optional repo helper; falls back gracefully.
        from unified_credentials_manager import get_credential  # type: ignore

        return get_credential("OPENAI_API_KEY")
    except Exception:
        return None


def _to_data_url(path: str) -> str:
    p = Path(path)
    raw = p.read_bytes()
    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "application/octet-stream"
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _human_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(n)
    for u in units:
        if size < 1024 or u == units[-1]:
            return f"{size:.1f}{u}" if u != "B" else f"{int(size)}{u}"
        size /= 1024
    return f"{size:.1f}GB"


def _as_jsonable(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool, list, dict)):
        return obj
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        try:
            return dict(obj.__dict__)
        except Exception:
            pass
    return str(obj)


def _extract_text(resp: Any) -> str:
    # OpenAI SDK objects typically have .text
    t = getattr(resp, "text", None)
    if isinstance(t, str):
        return t
    if isinstance(resp, dict) and isinstance(resp.get("text"), str):
        return resp["text"]
    if isinstance(resp, str):
        return resp
    return str(resp)


def _print_response(resp: Any, response_format: str) -> None:
    if response_format in {"text", "srt", "vtt"}:
        # Even for these, the SDK often returns an object with .text
        sys.stdout.write(_extract_text(resp))
        if not _extract_text(resp).endswith("\n"):
            sys.stdout.write("\n")
        return

    # json / verbose_json / diarized_json
    sys.stdout.write(json.dumps(_as_jsonable(resp), ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _parse_known_speakers(items: Optional[List[str]]) -> Tuple[List[str], List[str]]:
    """Parses ['name=path', ...] into (names, data_urls)."""
    if not items:
        return [], []

    names: List[str] = []
    refs: List[str] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Invalid --known-speaker '{item}'. Use name=/path/to/ref.wav")
        name, path = item.split("=", 1)
        name = name.strip()
        path = path.strip()
        if not name:
            raise SystemExit(f"Invalid --known-speaker '{item}': empty name")
        if not path:
            raise SystemExit(f"Invalid --known-speaker '{item}': empty path")
        if not Path(path).exists():
            raise SystemExit(f"Known-speaker reference file not found: {path}")
        names.append(name)
        refs.append(_to_data_url(path))

    if len(names) > 4:
        raise SystemExit("You can provide up to 4 known speakers.")

    return names, refs


def _validate_response_format(model: str, response_format: str, mode: str) -> None:
    if mode == "translate":
        if model != "whisper-1":
            raise SystemExit("Translations are only supported with model whisper-1")
        if response_format not in {"json", "text"}:
            raise SystemExit("Translations support response formats: json, text")
        return

    if model == "whisper-1":
        allowed = {"json", "text", "srt", "vtt", "verbose_json"}
    elif model in {"gpt-4o-transcribe", "gpt-4o-mini-transcribe"}:
        allowed = {"json", "text"}
    elif model == "gpt-4o-transcribe-diarize":
        allowed = {"json", "text", "diarized_json"}
    else:
        allowed = {"json", "text"}

    if response_format not in allowed:
        raise SystemExit(f"Invalid response format '{response_format}' for model '{model}'. Allowed: {', '.join(sorted(allowed))}")


def _warn_if_large_file(path: str) -> None:
    try:
        size = Path(path).stat().st_size
    except Exception:
        return
    if size > 25 * 1024 * 1024:
        print(
            f"⚠️  File is {_human_size(size)}; Audio API uploads are limited to 25MB.\n"
            "   Consider compressing or splitting into chunks.",
            file=sys.stderr,
        )


def cmd_transcribe(args: argparse.Namespace) -> int:
    key = _try_get_openai_key()
    if not key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    _warn_if_large_file(args.audio)
    _validate_response_format(args.model, args.response_format, mode="transcribe")

    from openai import OpenAI  # imported late to keep script importable without deps

    client = OpenAI(api_key=key)

    with open(args.audio, "rb") as audio_file:
        req: Dict[str, Any] = {
            "model": args.model,
            "file": audio_file,
            "response_format": args.response_format,
        }

        if args.prompt:
            req["prompt"] = args.prompt

        if args.language:
            req["language"] = args.language

        if args.stream:
            req["stream"] = True

        if args.include:
            req["include"] = args.include

        if args.model == "whisper-1" and args.timestamp_granularities:
            req["timestamp_granularities"] = args.timestamp_granularities
            if args.response_format != "verbose_json":
                print("Note: timestamp_granularities are typically used with response_format=verbose_json", file=sys.stderr)

        stream = client.audio.transcriptions.create(**req)

    if args.stream:
        for event in stream:
            sys.stdout.write(json.dumps(_as_jsonable(event), ensure_ascii=False))
            sys.stdout.write("\n")
        return 0

    _print_response(stream, args.response_format)
    return 0


def cmd_diarize(args: argparse.Namespace) -> int:
    key = _try_get_openai_key()
    if not key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    _warn_if_large_file(args.audio)

    model = "gpt-4o-transcribe-diarize"
    response_format = args.response_format
    _validate_response_format(model, response_format, mode="transcribe")

    from openai import OpenAI

    client = OpenAI(api_key=key)

    known_names, known_refs = _parse_known_speakers(args.known_speaker)

    with open(args.audio, "rb") as audio_file:
        req: Dict[str, Any] = {
            "model": model,
            "file": audio_file,
            "response_format": response_format,
        }

        # Required for >30s; safe to always send when set.
        if args.chunking_strategy:
            req["chunking_strategy"] = args.chunking_strategy

        if args.stream:
            req["stream"] = True

        if known_names or known_refs:
            req["extra_body"] = {
                "known_speaker_names": known_names,
                "known_speaker_references": known_refs,
            }

        stream = client.audio.transcriptions.create(**req)

    if args.stream:
        for event in stream:
            sys.stdout.write(json.dumps(_as_jsonable(event), ensure_ascii=False))
            sys.stdout.write("\n")
        return 0

    _print_response(stream, response_format)
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    key = _try_get_openai_key()
    if not key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    _warn_if_large_file(args.audio)

    model = "whisper-1"
    _validate_response_format(model, args.response_format, mode="translate")

    from openai import OpenAI

    client = OpenAI(api_key=key)

    with open(args.audio, "rb") as audio_file:
        req: Dict[str, Any] = {
            "model": model,
            "file": audio_file,
            "response_format": args.response_format,
        }
        if args.prompt:
            req["prompt"] = args.prompt

        resp = client.audio.translations.create(**req)

    _print_response(resp, args.response_format)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Speech-to-text utilities (OpenAI Audio API)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Transcribe
    t = sub.add_parser("transcribe", help="Transcribe audio (same language as input)")
    t.add_argument("audio", help="Path to audio file")
    t.add_argument(
        "--model",
        default="gpt-4o-transcribe",
        choices=["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"],
        help="Model to use",
    )
    t.add_argument(
        "--response-format",
        default="json",
        help="Response format (depends on model). e.g. json, text, srt, vtt, verbose_json",
    )
    t.add_argument("--prompt", default="", help="Optional context prompt")
    t.add_argument("--language", default="", help="Optional language hint (ISO code when supported)")
    t.add_argument("--stream", action="store_true", help="Stream transcript events as JSON lines")
    t.add_argument(
        "--include",
        action="append",
        default=[],
        help="Include fields (repeatable). e.g. --include logprobs",
    )
    t.add_argument(
        "--timestamp-granularities",
        action="append",
        default=[],
        help="Whisper-only: timestamp granularities (repeatable). e.g. --timestamp-granularities word",
    )
    t.set_defaults(func=cmd_transcribe)

    # Diarize
    d = sub.add_parser("diarize", help="Transcribe with speaker diarization")
    d.add_argument("audio", help="Path to audio file")
    d.add_argument(
        "--response-format",
        default="diarized_json",
        choices=["diarized_json", "json", "text"],
        help="Response format",
    )
    d.add_argument(
        "--chunking-strategy",
        default="auto",
        help='Chunking strategy (recommended: "auto"). Required for >30s audio.',
    )
    d.add_argument(
        "--known-speaker",
        action="append",
        default=[],
        help="Optional known speaker mapping (repeatable): name=/path/to/ref.wav",
    )
    d.add_argument("--stream", action="store_true", help="Stream transcript events as JSON lines")
    d.set_defaults(func=cmd_diarize)

    # Translate
    tr = sub.add_parser("translate", help="Translate+transcribe audio into English (whisper-1)")
    tr.add_argument("audio", help="Path to audio file")
    tr.add_argument(
        "--response-format",
        default="json",
        choices=["json", "text"],
        help="Response format",
    )
    tr.add_argument("--prompt", default="", help="Optional context prompt")
    tr.set_defaults(func=cmd_translate)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
