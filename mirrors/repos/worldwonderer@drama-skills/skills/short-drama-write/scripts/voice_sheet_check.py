#!/usr/bin/env python3
"""Prove a voice record sheet is still a projection of the screenplay.

The sheet exists to be carried into a recording session, which is exactly the
moment nobody can check it against the script. A line edited in the sheet, or a
script revised after the sheet was built, both read as a perfectly ordinary
sheet — so the comparison has to be mechanical: resolve each line's block in
the derived index, slice those exact bytes out of the screenplay, and compare.

The script reads accepted creator files and writes nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


# Creators run these scripts on whatever interpreter their machine provides, so
# an unsupported version must say so instead of failing inside an import.
MINIMUM_PYTHON = (3, 10)
if sys.version_info < MINIMUM_PYTHON:
    raise SystemExit(
        "short-drama needs Python {}.{} or newer; this interpreter is {}.{}".format(
            *MINIMUM_PYTHON, sys.version_info.major, sys.version_info.minor
        )
    )

SCHEMA_VERSION = "1.0.0"
CHANNELS = {"sync", "dubbed", "VO", "OS"}
# `角色（可表演提示）：台词` — the cue is optional and never part of the line.
DIALOGUE = re.compile(
    r"^(?P<speaker>[^（(：:]+)(?:[（(](?P<cue>[^）)]*)[）)])?\s*[：:]\s*(?P<line>.*)$",
    re.DOTALL,
)


class CheckError(ValueError):
    """The inputs cannot be checked at all, as opposed to failing a check."""


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise CheckError(f"unreadable JSONL: {path}") from error
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise CheckError(f"invalid JSONL at {path.name}:{number}") from error
        if not isinstance(record, dict):
            raise CheckError(f"JSONL needs one object per line: {path.name}:{number}")
        records.append(record)
    return records


def _finding(code: str, message: str, **detail: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **detail}


def _blocks_by_id(index: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        record["block_id"]: record
        for record in index
        if record.get("record_type") == "block"
        and isinstance(record.get("block_id"), str)
    }


def check(
    sheet: list[dict[str, Any]],
    index: list[dict[str, Any]],
    screenplay: bytes,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    blocks = _blocks_by_id(index)
    seen: set[str] = set()

    for record in sheet:
        line_id = record.get("line_id")
        if not isinstance(line_id, str):
            findings.append(_finding("VOICE_LINE_HAS_NO_ID", "a line record has no id"))
            continue
        if line_id in seen:
            findings.append(
                _finding("VOICE_LINE_ID_REPEATS", "line_id must be unique", line_id=line_id)
            )
            continue
        seen.add(line_id)

        channel = record.get("channel")
        if channel not in CHANNELS:
            findings.append(
                _finding(
                    "VOICE_CHANNEL_INVALID",
                    "channel must be sync, dubbed, VO, or OS",
                    line_id=line_id,
                    channel=channel,
                )
            )

        ref = record.get("source_ref")
        if not isinstance(ref, dict) or not isinstance(ref.get("record_id"), str):
            findings.append(
                _finding(
                    "VOICE_SOURCE_REF_MISSING",
                    "a line must bind the screenplay block it projects",
                    line_id=line_id,
                )
            )
            continue
        block = blocks.get(ref["record_id"])
        if block is None:
            findings.append(
                _finding(
                    "VOICE_SOURCE_REF_UNRESOLVABLE",
                    "source_ref names a block that is not in the index",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )
            continue
        if block.get("kind") != "dialogue":
            findings.append(
                _finding(
                    "VOICE_SOURCE_IS_NOT_DIALOGUE",
                    "a voice line must project a dialogue block",
                    line_id=line_id,
                    record_id=ref["record_id"],
                    kind=block.get("kind"),
                )
            )
            continue

        start, end = block.get("byte_start"), block.get("byte_end")
        if (
            not isinstance(start, int)
            or not isinstance(end, int)
            or not 0 <= start < end <= len(screenplay)
        ):
            findings.append(
                _finding(
                    "VOICE_BLOCK_SPAN_INVALID",
                    "the indexed block span does not fit this screenplay",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )
            continue
        raw = screenplay[start:end]
        if hashlib.sha256(raw).hexdigest() != block.get("content_sha256"):
            findings.append(
                _finding(
                    "VOICE_INDEX_IS_STALE_AGAINST_SCREENPLAY",
                    "the index no longer matches the screenplay bytes; rebuild it",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )
            continue

        match = DIALOGUE.match(raw.decode("utf-8").strip())
        if match is None:
            findings.append(
                _finding(
                    "VOICE_BLOCK_IS_UNPARSEABLE",
                    "the dialogue block does not use the documented line grammar",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )
            continue
        if record.get("line_text") != match.group("line"):
            findings.append(
                _finding(
                    "VOICE_LINE_TEXT_DIVERGED",
                    "line_text is not the screenplay wording; change the screenplay",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )
        indexed_speaker = block.get("speaker")
        if isinstance(indexed_speaker, str) and record.get("speaker_display") not in (
            None,
            indexed_speaker,
        ):
            findings.append(
                _finding(
                    "VOICE_SPEAKER_DIVERGED",
                    "speaker_display disagrees with the indexed speaker",
                    line_id=line_id,
                    record_id=ref["record_id"],
                )
            )

    dialogue_blocks = {
        block_id for block_id, block in blocks.items() if block.get("kind") == "dialogue"
    }
    projected = {
        record["source_ref"]["record_id"]
        for record in sheet
        if isinstance(record.get("source_ref"), dict)
        and isinstance(record["source_ref"].get("record_id"), str)
    }
    # Reported, never a finding: a sheet may legitimately cover one actor or one
    # scene, so an incomplete sheet is a scope decision, not a defect.
    uncovered = sorted(dialogue_blocks - projected)

    return {
        "schema_version": SCHEMA_VERSION,
        "lines": len(sheet),
        "dialogue_blocks": len(dialogue_blocks),
        "uncovered_dialogue_blocks": uncovered,
        "findings": findings,
        "status": "pass" if not findings else "fail",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check a voice record sheet against its screenplay and index."
    )
    parser.add_argument("sheet", type=Path, help="the voice record sheet JSONL")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--screenplay", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = check(
            _load_jsonl(args.sheet),
            _load_jsonl(args.index),
            args.screenplay.read_bytes(),
        )
    except (CheckError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
