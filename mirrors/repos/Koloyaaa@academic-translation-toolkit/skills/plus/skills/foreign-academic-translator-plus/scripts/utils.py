"""Shared text-file encoding helper."""

from pathlib import Path

import chardet


def detect_encoding(file_path: Path) -> str:
    """Detect a text file's encoding, defaulting to UTF-8 when unavailable."""
    with open(file_path, "rb") as stream:
        raw_data = stream.read(10000)
    result = chardet.detect(raw_data)
    return result.get("encoding", "utf-8") if result else "utf-8"