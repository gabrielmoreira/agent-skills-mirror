"""
Batch-convert a directory of documents to Markdown for LLM consumption.

Usage:
    python batch_convert.py ./documents                           # convert all supported files
    python batch_convert.py ./docs -o ./markdown_output           # separate output directory
    python batch_convert.py ./docs -r                             # include subdirectories
    python batch_convert.py ./docs -f docx,pdf                    # only Word and PDF
    python batch_convert.py ./docs --dry-run                      # preview what would be converted
    python batch_convert.py ./docs --overwrite                    # overwrite existing .md files

Supported formats: .docx, .doc, .xlsx, .xls, .csv, .pptx, .ppt, .pdf, .html, .epub,
    .png, .jpg, .jpeg, .gif, .bmp, .tiff, .mp3, .wav, .m4a, .ipynb, .zip, .msg,
    .mpp, .mspdi, .mpx (MS Project — requires Java 11+)
Requires: pip install markitdown (or pip install 'markitdown[all]' for OCR)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".pptx", ".ppt", ".pdf", ".html", ".htm", ".epub",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff",
    ".mp3", ".wav", ".m4a",
    ".ipynb", ".zip", ".msg",
    ".mpp", ".mspdi", ".mpx",  # MS Project
}


def build_frontmatter(input_path: Path) -> str:
    source = input_path.name
    date = datetime.now().strftime("%Y-%m-%d")
    fmt = input_path.suffix.lstrip(".").lower()
    return f'---\nsource: "{source}"\nconverted: "{date}"\nformat: "{fmt}"\n---\n\n'


_MPP_EXTENSIONS = {".mpp", ".mspdi", ".mpx"}


def convert_file(md_converter, input_path: Path) -> str:
    if input_path.suffix.lower() in _MPP_EXTENSIONS:
        from convert import convert_mpp
        return convert_mpp(input_path)
    result = md_converter.convert(str(input_path))
    return result.text_content


def collect_files(
    input_dir: Path,
    recursive: bool,
    formats: set[str] | None,
) -> list[Path]:
    allowed = formats if formats else SUPPORTED_EXTENSIONS
    if recursive:
        files = [f for f in input_dir.rglob("*") if f.is_file() and f.suffix.lower() in allowed]
    else:
        files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in allowed]
    return sorted(files)


def resolve_output_path(
    input_file: Path,
    input_dir: Path,
    output_dir: Path,
) -> Path:
    relative = input_file.relative_to(input_dir)
    return output_dir / relative.with_suffix(".md")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-convert a directory of documents to Markdown for LLM consumption."
    )
    parser.add_argument("input_dir", help="Source directory to scan")
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as input, files alongside originals)",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="Scan subdirectories",
    )
    parser.add_argument(
        "-f", "--formats",
        help="Comma-separated list of extensions to include (e.g., docx,pdf)",
    )
    parser.add_argument(
        "--no-frontmatter", action="store_true",
        help="Skip YAML frontmatter generation",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List files that would be converted without actually converting",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing .md files (default: skip)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    if not input_dir.is_dir():
        print(f"Error: directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_dir

    formats: set[str] | None = None
    if args.formats:
        formats = {
            ext if ext.startswith(".") else f".{ext}"
            for ext in args.formats.split(",")
        }
        unsupported = formats - SUPPORTED_EXTENSIONS
        if unsupported:
            print(
                f"Warning: unsupported format(s) ignored: {', '.join(sorted(unsupported))}",
                file=sys.stderr,
            )
            formats = formats & SUPPORTED_EXTENSIONS
            if not formats:
                print("Error: no valid formats specified.", file=sys.stderr)
                sys.exit(1)

    files = collect_files(input_dir, args.recursive, formats)

    if not files:
        print("No supported files found.")
        sys.exit(0)

    # Dry run mode
    if args.dry_run:
        print(f"Dry run — {len(files)} file(s) would be converted:\n")
        for f in files:
            out = resolve_output_path(f, input_dir, output_dir)
            exists = " (exists, would skip)" if out.exists() and not args.overwrite else ""
            print(f"  {f.relative_to(input_dir)} → {out.relative_to(output_dir)}{exists}")
        return

    # Import markitdown only when actually converting
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("Error: markitdown is not installed. Run: pip install markitdown", file=sys.stderr)
        sys.exit(1)

    md = MarkItDown()
    converted = 0
    failed: list[tuple[str, str]] = []
    skipped = 0

    for f in files:
        out_path = resolve_output_path(f, input_dir, output_dir)

        if out_path.exists() and not args.overwrite:
            skipped += 1
            continue

        try:
            content = convert_file(md, f)
            if not args.no_frontmatter:
                content = build_frontmatter(f) + content

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            converted += 1
            print(f"  ✓ {f.relative_to(input_dir)}")
        except Exception as e:
            failed.append((str(f.relative_to(input_dir)), str(e)))
            print(f"  ✗ {f.relative_to(input_dir)}: {e}")

    # Summary
    print(f"\n{'='*40}")
    print(f"Converted: {converted}")
    if skipped:
        print(f"Skipped (already exists): {skipped}")
    if failed:
        print(f"Failed: {len(failed)}")
        for name, err in failed:
            print(f"  ✗ {name}: {err}")
    print(f"Total files found: {len(files)}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
