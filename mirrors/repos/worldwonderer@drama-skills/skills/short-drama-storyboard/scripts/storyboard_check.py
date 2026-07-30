#!/usr/bin/env python3
"""Check the two storyboard invariants that are pure bookkeeping.

`SHT-16` is arithmetic over shot durations and `SHT-17` is a structural claim
about which boundary a keyframe freezes. Neither needs a reading of the drama,
so leaving both to a reviewer spends judgment on work a script does exactly.
Everything requiring judgment stays in the reference documents.

The script reads accepted creator files and writes nothing.
"""

from __future__ import annotations

import argparse
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
BOUNDARY_FIELD = {"start": "/start_boundary", "end": "/end_boundary"}
PLACEHOLDER = re.compile(r"^<.*>$")


class CheckError(ValueError):
    """The inputs cannot be checked at all, as opposed to failing a check."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CheckError(f"unreadable JSON: {path}") from error


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


def _is_template(value: Any) -> bool:
    """Template files ship placeholder strings; they are not project data."""

    return isinstance(value, str) and bool(PLACEHOLDER.match(value.strip()))


def _finding(code: str, message: str, **detail: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **detail}


def _duration_of(shot: dict[str, Any]) -> float | None:
    value = shot.get("duration_seconds")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _covered_shot_ids(coverage: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    dispositions = coverage.get("dispositions")
    if not isinstance(dispositions, list):
        return ids
    for disposition in dispositions:
        if not isinstance(disposition, dict):
            continue
        for ref in disposition.get("shot_refs") or []:
            if isinstance(ref, dict) and isinstance(ref.get("record_id"), str):
                ids.append(ref["record_id"])
    return ids


def check_episode_duration(
    coverage: dict[str, Any],
    shots: list[dict[str, Any]],
    target_seconds: float | None,
) -> list[dict[str, Any]]:
    """SHT-16: the total is arithmetic, and no shot may leave it silently."""

    findings: list[dict[str, Any]] = []
    duration = coverage.get("episode_duration")
    if not isinstance(duration, dict):
        return [_finding("SHT16_RECORD_MISSING", "coverage carries no episode_duration")]

    by_id = {
        shot["shot_id"]: shot
        for shot in shots
        if isinstance(shot.get("shot_id"), str)
    }
    counted = duration.get("counted_shot_ids")
    unresolved = duration.get("unresolved_durations")
    if not isinstance(counted, list) or not isinstance(unresolved, list):
        return [
            _finding(
                "SHT16_RECORD_INCOMPLETE",
                "episode_duration needs counted_shot_ids and unresolved_durations",
            )
        ]
    counted_ids = [value for value in counted if isinstance(value, str)]
    unresolved_ids = [value for value in unresolved if isinstance(value, str)]

    overlap = sorted(set(counted_ids) & set(unresolved_ids))
    if overlap:
        findings.append(
            _finding(
                "SHT16_SHOT_COUNTED_AND_UNRESOLVED",
                "a shot cannot be both counted and unresolved",
                shot_ids=overlap,
            )
        )

    accounted = set(counted_ids) | set(unresolved_ids)
    missing = sorted(set(_covered_shot_ids(coverage)) - accounted)
    if missing:
        findings.append(
            _finding(
                "SHT16_SHOT_LEFT_THE_TOTAL",
                "coverage lists shots that neither contribute nor are suspended",
                shot_ids=missing,
            )
        )
    unknown = sorted(accounted - set(by_id))
    if unknown:
        findings.append(
            _finding(
                "SHT16_SHOT_UNRESOLVABLE",
                "episode_duration names shots that are not in the shot file",
                shot_ids=unknown,
            )
        )

    total = 0.0
    for shot_id in counted_ids:
        shot = by_id.get(shot_id)
        if shot is None:
            continue
        seconds = _duration_of(shot)
        if seconds is None:
            findings.append(
                _finding(
                    "SHT16_COUNTED_SHOT_HAS_NO_DURATION",
                    "a counted shot carries no numeric duration_seconds",
                    shot_id=shot_id,
                )
            )
            continue
        total += seconds
    for shot_id in unresolved_ids:
        shot = by_id.get(shot_id)
        if shot is not None and _duration_of(shot) is not None:
            findings.append(
                _finding(
                    "SHT16_SUSPENDED_SHOT_HAS_A_DURATION",
                    "a shot listed as unresolved already carries a duration",
                    shot_id=shot_id,
                )
            )

    stated = duration.get("shot_seconds_total")
    if isinstance(stated, bool) or not isinstance(stated, (int, float)):
        findings.append(
            _finding("SHT16_TOTAL_MISSING", "shot_seconds_total is not a number")
        )
    elif abs(float(stated) - total) > 1e-6:
        findings.append(
            _finding(
                "SHT16_TOTAL_IS_NOT_THE_SUM",
                "shot_seconds_total does not equal the sum of the counted shots",
                stated=float(stated),
                computed=round(total, 6),
            )
        )

    if target_seconds is None:
        if duration.get("disposition") not in (None, "no_target_declared"):
            findings.append(
                _finding(
                    "SHT16_DISPOSITION_CLAIMS_A_TARGET",
                    "no target is declared, so the disposition cannot judge one",
                )
            )
        return findings

    delta = duration.get("delta_seconds")
    expected = total - target_seconds
    if isinstance(delta, bool) or not isinstance(delta, (int, float)):
        findings.append(
            _finding("SHT16_DELTA_MISSING", "a declared target needs a signed delta")
        )
    elif abs(float(delta) - expected) > 1e-6:
        findings.append(
            _finding(
                "SHT16_DELTA_IS_WRONG",
                "delta_seconds does not equal total minus target",
                stated=float(delta),
                computed=round(expected, 6),
            )
        )
    if duration.get("disposition") not in {
        "within_creator_tolerance",
        "creator_accepted_overrun",
        "to_revise",
    }:
        findings.append(
            _finding(
                "SHT16_DISPOSITION_MISSING",
                "a declared target needs a disposition for its delta",
            )
        )
    return findings


def check_keyframe_boundaries(
    keyframes: list[dict[str, Any]],
    shots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """SHT-17: say which boundary is frozen, and bind that shot's field."""

    findings: list[dict[str, Any]] = []
    shot_ids = {
        shot["shot_id"] for shot in shots if isinstance(shot.get("shot_id"), str)
    }
    seen: dict[tuple[str, str], str] = {}
    for keyframe in keyframes:
        keyframe_id = keyframe.get("keyframe_id")
        if not isinstance(keyframe_id, str):
            findings.append(
                _finding("SHT17_KEYFRAME_HAS_NO_ID", "a keyframe record has no id")
            )
            continue
        role = keyframe.get("boundary_role")
        if role not in BOUNDARY_FIELD:
            findings.append(
                _finding(
                    "SHT17_BOUNDARY_ROLE_MISSING",
                    "boundary_role must be start or end",
                    keyframe_id=keyframe_id,
                )
            )
            continue
        ref = keyframe.get("boundary_ref")
        if not isinstance(ref, dict):
            findings.append(
                _finding(
                    "SHT17_BOUNDARY_REF_MISSING",
                    "a keyframe must bind the boundary it projects",
                    keyframe_id=keyframe_id,
                )
            )
            continue
        if ref.get("field") != BOUNDARY_FIELD[role]:
            findings.append(
                _finding(
                    "SHT17_BOUNDARY_REF_DISAGREES_WITH_ROLE",
                    "boundary_ref.field does not match the declared role",
                    keyframe_id=keyframe_id,
                    role=role,
                    field=ref.get("field"),
                )
            )
        shot_id = ref.get("record_id")
        if not isinstance(shot_id, str) or shot_id not in shot_ids:
            findings.append(
                _finding(
                    "SHT17_BOUNDARY_REF_UNRESOLVABLE",
                    "boundary_ref does not resolve to a shot in the shot file",
                    keyframe_id=keyframe_id,
                    record_id=shot_id,
                )
            )
            continue
        previous = seen.get((shot_id, role))
        if previous is not None:
            findings.append(
                _finding(
                    "SHT17_DUPLICATE_BOUNDARY_KEYFRAME",
                    "one shot boundary cannot have two keyframes",
                    shot_id=shot_id,
                    role=role,
                    keyframe_ids=[previous, keyframe_id],
                )
            )
            continue
        seen[(shot_id, role)] = keyframe_id
    return findings


def _declared_target(project: Path | None) -> float | None:
    if project is None:
        return None
    document = _load_json(project)
    if not isinstance(document, dict):
        raise CheckError("project file must be a JSON object")
    value = document.get("format", {}).get("target_seconds_per_episode")
    if value is None or _is_template(value):
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CheckError("target_seconds_per_episode must be a number or null")
    return float(value)


def check(
    coverage_path: Path,
    shots_path: Path,
    keyframes_path: Path | None,
    project_path: Path | None,
) -> dict[str, Any]:
    coverage = _load_json(coverage_path)
    if not isinstance(coverage, dict):
        raise CheckError("coverage must be a JSON object")
    shots = _load_jsonl(shots_path)
    findings = check_episode_duration(coverage, shots, _declared_target(project_path))
    if keyframes_path is not None:
        findings.extend(check_keyframe_boundaries(_load_jsonl(keyframes_path), shots))
    return {
        "schema_version": SCHEMA_VERSION,
        "episode_id": coverage.get("episode_id"),
        "checked": {
            "shots": len(shots),
            "keyframes": None if keyframes_path is None else len(_load_jsonl(keyframes_path)),
        },
        "findings": findings,
        "status": "pass" if not findings else "fail",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check storyboard duration arithmetic and keyframe boundary roles."
    )
    parser.add_argument("coverage", type=Path, help="the episode coverage JSON")
    parser.add_argument("--shots", type=Path, required=True)
    parser.add_argument("--keyframes", type=Path)
    parser.add_argument(
        "--project",
        type=Path,
        help="short-drama.json, so a declared per-episode target is compared",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = check(args.coverage, args.shots, args.keyframes, args.project)
    except CheckError as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
