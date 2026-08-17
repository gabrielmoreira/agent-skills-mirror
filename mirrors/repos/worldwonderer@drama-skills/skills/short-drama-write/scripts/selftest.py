#!/usr/bin/env python3
"""Offline self-test for screenplay indexing and voice-sheet projection."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

from screenplay_index import build_index
from voice_sheet_check import check

MINIMUM_PYTHON = (3, 10)
if sys.version_info < MINIMUM_PYTHON:
    raise SystemExit("selftest.py requires Python 3.10 or newer")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def codes(result: dict[str, object]) -> set[str]:
    findings = result["findings"]
    assert isinstance(findings, list)
    return {finding["code"] for finding in findings}


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        screenplay = root / "screenplay.md"
        index_path = root / "screenplay-index.jsonl"
        screenplay.write_text(
            "# EP001\n\n## EP001-SC001 内 · 客厅 · 夜\n\n陈予安推开门。\n\n陈予安：我回来了。\n",
            encoding="utf-8",
        )
        summary = build_index(
            screenplay,
            index_path,
            source_ref="剧集/EP001/screenplay.md",
            speakers=["陈予安"],
        )
        require(summary["review_status"] == "clean", "valid screenplay index")
        index_bytes = index_path.read_bytes()
        records = [
            json.loads(line) for line in index_bytes.decode("utf-8").splitlines()
        ]
        dialogue = next(record for record in records if record.get("kind") == "dialogue")

        header = {
            "record_type": "sources",
            "schema_version": "1.0.0",
            "sources": {
                "screenplay-index": {
                    "owner": "short-drama-write",
                    "artifact": "剧集/EP001/screenplay-index.jsonl",
                    "hash": hashlib.sha256(index_bytes).hexdigest(),
                }
            },
        }
        line = {
            "line_id": "LINE-001",
            "channel": "sync",
            "speaker_display": "陈予安",
            "line_text": "我回来了。",
            "source_ref": {"src": "screenplay-index", "record_id": dialogue["block_id"]},
        }
        sheet = [header, line]
        result = check(sheet, records, screenplay.read_bytes())
        require(result["status"] == "pass", "faithful voice sheet")
        require(result["lines"] == 1, "the sources header is not a voice line")

        # A sheet written before the compact form still resolves; real projects
        # hold both spellings and neither is rewritten.
        expanded = [
            dict(
                line,
                source_ref={
                    "owner": "short-drama-write",
                    "artifact": "剧集/EP001/screenplay-index.jsonl",
                    "hash": hashlib.sha256(index_bytes).hexdigest(),
                    "record_id": dialogue["block_id"],
                },
            )
        ]
        require(
            check(expanded, records, screenplay.read_bytes())["status"] == "pass",
            "expanded voice sheet",
        )

        undeclared = [header, dict(line, source_ref={"src": "screenplay", "record_id": "X"})]
        require(
            "VOICE_SOURCE_REF_UNDECLARED"
            in codes(check(undeclared, records, screenplay.read_bytes())),
            "src without a sources entry was not detected",
        )

        unbound = [header, dict(line, source_ref={"record_id": dialogue["block_id"]})]
        require(
            "VOICE_SOURCE_REF_MISSING"
            in codes(check(unbound, records, screenplay.read_bytes())),
            "source_ref naming no upstream snapshot was not detected",
        )

        changed = [header, dict(line, line_text="我走了。")]
        require(
            check(changed, records, screenplay.read_bytes())["status"] == "fail",
            "changed voice line was not detected",
        )

    print("7 self-tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
