#!/usr/bin/env python3
"""Reconcile an episode's delivery containers against its shot set (`VID-15`).

Every container can be correct on its own while the episode is wrong: a shot
packed into two containers bills its seconds twice, and a shot packed into none
disappears although its dialogue, bindings, and keyframe prompts are already
done. Neither error is visible from inside a single container, so the check is
a set comparison at episode scope.

The script reads accepted creator files and writes nothing.
"""

from __future__ import annotations

import argparse
import json
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


def _seconds(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _member_shot_id(member: Any) -> str | None:
    if not isinstance(member, dict):
        return None
    ref = member.get("shot_ref")
    if isinstance(ref, dict) and isinstance(ref.get("record_id"), str):
        return ref["record_id"]
    return None


def reconcile(
    containers: list[dict[str, Any]],
    shots: list[dict[str, Any]],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    durations = {
        shot["shot_id"]: _seconds(shot.get("duration_seconds"))
        for shot in shots
        if isinstance(shot.get("shot_id"), str)
    }
    episode_shots = set(durations)

    owner_of: dict[str, str] = {}
    packed: set[str] = set()
    container_total = 0.0
    for container in containers:
        container_id = container.get("container_id")
        if not isinstance(container_id, str):
            findings.append(
                _finding("VID15_CONTAINER_HAS_NO_ID", "a container record has no id")
            )
            continue
        members = container.get("members")
        if not isinstance(members, list) or not members:
            findings.append(
                _finding(
                    "VID15_CONTAINER_HAS_NO_MEMBERS",
                    "a container carries no members",
                    container_id=container_id,
                )
            )
            continue
        member_total = 0.0
        for member in members:
            shot_id = _member_shot_id(member)
            if shot_id is None:
                findings.append(
                    _finding(
                        "VID15_MEMBER_HAS_NO_SHOT_REF",
                        "a member does not name the shot it packs",
                        container_id=container_id,
                    )
                )
                continue
            if shot_id not in episode_shots:
                findings.append(
                    _finding(
                        "VID15_MEMBER_IS_NOT_AN_EPISODE_SHOT",
                        "a container packs a shot that is not in this episode",
                        container_id=container_id,
                        shot_id=shot_id,
                    )
                )
                continue
            previous = owner_of.get(shot_id)
            if previous is not None:
                findings.append(
                    _finding(
                        "VID15_SHOT_PACKED_TWICE",
                        "a shot belongs to more than one container",
                        shot_id=shot_id,
                        container_ids=sorted({previous, container_id}),
                    )
                )
                continue
            owner_of[shot_id] = container_id
            packed.add(shot_id)
            seconds = durations.get(shot_id)
            if seconds is None:
                findings.append(
                    _finding(
                        "VID15_MEMBER_SHOT_HAS_NO_DURATION",
                        "a packed shot carries no numeric duration",
                        container_id=container_id,
                        shot_id=shot_id,
                    )
                )
                continue
            member_total += seconds
        stated = _seconds(container.get("container_duration"))
        if stated is None:
            findings.append(
                _finding(
                    "VID15_CONTAINER_DURATION_MISSING",
                    "container_duration is not a number",
                    container_id=container_id,
                )
            )
        elif abs(stated - member_total) > 1e-6:
            findings.append(
                _finding(
                    "VID15_CONTAINER_DURATION_IS_NOT_THE_SUM",
                    "container_duration does not equal its members' durations",
                    container_id=container_id,
                    stated=stated,
                    computed=round(member_total, 6),
                )
            )
        container_total += member_total

    loose = sorted(episode_shots - packed)
    # A shot whose duration is still open is a legal state upstream, so it is
    # held out of the arithmetic instead of being reported as an error. Only a
    # shot packed into a container must already have one, because the
    # container's own duration claim depends on it.
    unmeasured = sorted(
        shot_id for shot_id in episode_shots if durations.get(shot_id) is None
    )
    loose_total = sum(
        durations[shot_id] or 0.0 for shot_id in loose if durations.get(shot_id) is not None
    )

    episode_total = sum(value for value in durations.values() if value is not None)
    if abs((container_total + loose_total) - episode_total) > 1e-6:
        findings.append(
            _finding(
                "VID15_EPISODE_TOTAL_DOES_NOT_RECONCILE",
                "containers plus loose shots do not add up to the episode total",
                packed_seconds=round(container_total, 6),
                loose_seconds=round(loose_total, 6),
                episode_seconds=round(episode_total, 6),
            )
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "containers": len(containers),
        "episode_shots": len(episode_shots),
        "packed_shots": len(packed),
        # Loose shots are legal: containers need not cover everything. They are
        # reported so the count is a decision rather than an oversight.
        "loose_shots": loose,
        # Reported, not a finding: these shots are excluded from every total
        # above, so a caller can tell an incomplete episode from a wrong one.
        "unmeasured_shots": unmeasured,
        "packed_seconds": round(container_total, 6),
        "loose_seconds": round(loose_total, 6),
        "episode_seconds": round(episode_total, 6),
        "findings": findings,
        "status": "pass" if not findings else "fail",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reconcile delivery containers with the episode's shot set."
    )
    parser.add_argument("containers", type=Path, help="the episode containers JSONL")
    parser.add_argument("--shots", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = reconcile(_load_jsonl(args.containers), _load_jsonl(args.shots))
    except CheckError as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
