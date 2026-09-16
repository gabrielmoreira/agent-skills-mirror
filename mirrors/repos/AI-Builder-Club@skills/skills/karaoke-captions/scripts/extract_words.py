#!/usr/bin/env python3
"""Extract word-level timestamps from audio or video using mlx-whisper.

Usage:
  python extract_words.py input.mp4 [output.json] [--model MODEL] [--language LANG]
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract word timestamps with mlx-whisper")
    parser.add_argument("input", help="Path to input audio or video file")
    parser.add_argument("output", nargs="?", default="words.json", help="Output JSON path (default: words.json)")
    parser.add_argument("--model", default="mlx-community/whisper-large-v3-turbo", help="Model repo or path")
    parser.add_argument("--language", default=None, help="Language code (e.g., en, zh)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.exit(f"Error: input file not found: {input_path}")

    try:
        import mlx_whisper
    except ImportError:
        sys.exit("Error: mlx_whisper is not installed. Run: pip install mlx-whisper")

    print(f"Transcribing {input_path} with {args.model}...")
    kwargs = {
        "word_timestamps": True,
        "verbose": False,
    }
    if args.language:
        kwargs["language"] = args.language

    result = mlx_whisper.transcribe(str(input_path), path_or_hf_repo=args.model, **kwargs)

    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            word_str = w.get("word", "").strip()
            if not word_str:
                continue
            words.append({
                "word": word_str,
                "start": round(float(w["start"]), 2),
                "end": round(float(w["end"]), 2),
            })

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"words": words}, f, ensure_ascii=False, indent=1)

    print(f"Extracted {len(words)} words -> {out_path}")


if __name__ == "__main__":
    main()
