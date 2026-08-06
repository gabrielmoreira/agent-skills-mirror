#!/usr/bin/env python3
"""Read minimal Copilot auto-capture journals selected by trusted pending markers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Iterable, Optional

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,160}$")
_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")
_SELECTION_TOKEN_RE = re.compile(r"^[a-f0-9]{32}$")
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_SIGNALS = frozenset(
    {
        "tool_failure",
        "tool_rejected",
        "tool_denied",
        "tool_timeout",
        "tool_retry",
        "subagent_failure",
        "model_failure",
        "system_error",
    }
)
_MAX_CONTROL_FILE_BYTES = 128 * 1024
_MAX_SELECTION_SESSIONS = 256
_SESSION_END_REASONS = frozenset(
    {"complete", "error", "abort", "timeout", "user_exit", "unknown"}
)


def _default_home() -> Path:
    configured = os.environ.get("SKILL_REFLECT_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".skill-reflect"


def _safe_session_id(value: object) -> str | None:
    if not isinstance(value, str) or value in {".", ".."}:
        return None
    return value if _SESSION_ID_RE.fullmatch(value) else None


def review_receipt(
    session_id: str,
    marker: dict,
    journal: dict | None,
) -> str:
    """Return a value-free handle bound to this exact marker and journal state."""

    control_payload = json.dumps(
        {"marker": marker, "journal": journal},
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(
        f"skill-reflect-review-v2\0{session_id}\0{control_payload}".encode("utf-8")
    ).hexdigest()[:32]


def control_directory_status(path: Path) -> str:
    """Return ok, missing, or invalid without following a directory symlink."""

    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "invalid"
    return "ok" if stat.S_ISDIR(mode) and not stat.S_ISLNK(mode) else "invalid"


def _pid_is_alive(pid: object) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def active_session_ids(home: Path) -> set[str] | None:
    """Return live session ids, or None when the active control directory is unsafe."""

    active = home / "active"
    status = control_directory_status(active)
    if status == "missing":
        return set()
    if status != "ok":
        return None
    try:
        entries = list(active.iterdir())
    except OSError:
        return None

    sessions: set[str] = set()
    for path in entries:
        session_id = _safe_session_id(path.stem) if path.suffix == ".json" else None
        if not session_id:
            return None
        document = read_control_json(path)
        if (
            not document
            or document.get("version") != 1
            or document.get("sessionId") != session_id
            or not isinstance(document.get("pid"), int)
            or isinstance(document.get("pid"), bool)
            or document["pid"] <= 0
        ):
            return None
        if _pid_is_alive(document["pid"]):
            sessions.add(session_id)
    return sessions


def read_selection_session_ids(home: Path, token: object) -> list[str] | None:
    """Read session ids from an opaque, extension-created marker selection."""

    selection = read_review_selection(home, token)
    return list(selection) if selection is not None else None


def read_review_selection(home: Path, token: object) -> dict[str, dict] | None:
    """Read a marker-digest-bound, skill-filtered review selection."""

    if not isinstance(token, str) or not _SELECTION_TOKEN_RE.fullmatch(token):
        return None
    if control_directory_status(home) != "ok":
        return None
    selections = home / "selections"
    if control_directory_status(selections) != "ok":
        return None
    document = read_control_json(selections / f"{token}.json")
    if (
        not document
        or document.get("version") != 1
        or document.get("token") != token
        or not isinstance(document.get("markers"), list)
        or len(document["markers"]) > _MAX_SELECTION_SESSIONS
    ):
        return None
    selection: dict[str, dict] = {}
    for raw_marker in document["markers"]:
        if not isinstance(raw_marker, dict):
            return None
        session_id = _safe_session_id(raw_marker.get("sessionId"))
        skills = _safe_skill_names(raw_marker.get("skills"))
        marker_digest = raw_marker.get("markerDigest")
        if (
            not session_id
            or not skills
            or not isinstance(marker_digest, str)
            or not _SHA256_RE.fullmatch(marker_digest)
            or session_id in selection
        ):
            return None
        selection[session_id] = {
            "skills": skills,
            "markerDigest": marker_digest,
        }
    return selection


def discover_pending_session_ids(home: Path) -> list[str]:
    """Enumerate safe regular marker filenames without returning them to the caller."""

    pending = home / "pending"
    if (
        control_directory_status(home) != "ok"
        or control_directory_status(pending) != "ok"
    ):
        return []
    try:
        entries = list(pending.iterdir())
    except OSError:
        return []
    active = active_session_ids(home)
    if active is None:
        return []
    session_ids: list[str] = []
    for path in sorted(entries):
        try:
            if path.is_symlink() or not path.is_file() or path.suffix != ".json":
                continue
        except OSError:
            continue
        session_id = _safe_session_id(path.stem)
        if session_id and session_id not in active:
            session_ids.append(session_id)
    return session_ids


def read_control_json(path: Path) -> dict | None:
    try:
        if control_directory_status(path.parent) != "ok":
            return None
        file_stat = path.lstat()
        if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
            return None
        if file_stat.st_size > _MAX_CONTROL_FILE_BYTES:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def control_file_digest(path: Path) -> str | None:
    try:
        if control_directory_status(path.parent) != "ok":
            return None
        file_stat = path.lstat()
        if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
            return None
        if file_stat.st_size > _MAX_CONTROL_FILE_BYTES:
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, OSError):
        return None


def _safe_skill_names(values: object) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {
        value
        for value in values
        if isinstance(value, str) and _SKILL_NAME_RE.fullmatch(value)
    }


def _safe_count(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _sanitize_friction(
    raw: object,
    *,
    allowed_skills: set[str],
) -> dict[str, dict]:
    if not isinstance(raw, dict):
        return {}
    sanitized: dict[str, dict] = {}
    for skill in sorted(allowed_skills):
        entry = raw.get(skill)
        if not isinstance(entry, dict):
            continue
        count = _safe_count(entry.get("count"))
        raw_signals = entry.get("signals")
        if count is None or not isinstance(raw_signals, dict):
            continue
        signals: dict[str, int] = {}
        for signal, value in sorted(raw_signals.items()):
            signal_count = _safe_count(value)
            if signal in _SIGNALS and signal_count and signal_count > 0:
                signals[signal] = signal_count
        if sum(signals.values()) != count:
            continue
        sanitized[skill] = {"count": count, "signals": signals}
    return sanitized


def _sanitize_marker_friction(
    raw: object,
    *,
    allowed_skills: set[str],
) -> dict[str, dict]:
    if not isinstance(raw, dict):
        return {}
    sanitized: dict[str, dict] = {}
    for skill in sorted(allowed_skills):
        count = _safe_count(raw.get(skill))
        if count is not None:
            sanitized[skill] = {"count": count, "signals": {}}
    return sanitized


def _marker_only_evidence(session_id: str, marker: dict, skills: set[str]) -> dict:
    return {
        "receipt": review_receipt(session_id, marker, None),
        "skills": sorted(skills),
        "friction": _sanitize_marker_friction(
            marker.get("friction"),
            allowed_skills=skills,
        ),
        "reason": (
            marker.get("reason")
            if marker.get("reason") in _SESSION_END_REASONS
            else "unknown"
        ),
        "ended": isinstance(marker.get("endedAt"), str),
        "journal": False,
    }


def read_journal_evidence(
    session_ids: Iterable[str],
    *,
    home: Optional[Path] = None,
    selection: Optional[dict[str, dict]] = None,
) -> dict:
    """Return value-free journal evidence without exposing opaque session ids."""

    root = home or _default_home()
    result = {"source": "copilot-auto-journal-v1", "sessions": [], "missing": 0, "invalid": 0}
    unique_session_ids = []
    for raw_session_id in dict.fromkeys(session_ids):
        session_id = _safe_session_id(raw_session_id)
        if session_id:
            unique_session_ids.append(session_id)
        else:
            result["invalid"] += 1
    root_status = control_directory_status(root)
    pending_status = (
        control_directory_status(root / "pending")
        if root_status == "ok"
        else root_status
    )
    if pending_status != "ok":
        result["invalid" if pending_status == "invalid" else "missing"] += len(
            unique_session_ids
        )
        return result

    journal_status = control_directory_status(root / "journal")
    active = active_session_ids(root)
    if active is None:
        result["invalid"] += len(unique_session_ids)
        return result

    for session_id in unique_session_ids:
        if session_id in active:
            result["invalid"] += 1
            continue
        marker_path = root / "pending" / f"{session_id}.json"
        marker_exists = marker_path.exists() or marker_path.is_symlink()
        marker = read_control_json(marker_path)
        if marker is None:
            result["invalid" if marker_exists else "missing"] += 1
            continue
        if marker.get("sessionId") != session_id:
            result["invalid"] += 1
            continue

        marker_skills = _safe_skill_names(marker.get("skills"))
        selected = selection.get(session_id) if selection else None
        if selected:
            if control_file_digest(marker_path) != selected["markerDigest"]:
                result["invalid"] += 1
                continue
            marker_skills &= selected["skills"]
        if not marker_skills:
            result["invalid"] += 1
            continue

        if journal_status == "missing":
            result["missing"] += 1
            result["sessions"].append(
                _marker_only_evidence(session_id, marker, marker_skills)
            )
            continue
        if journal_status == "invalid":
            result["invalid"] += 1
            continue

        journal_path = root / "journal" / f"{session_id}.json"
        journal_exists = journal_path.exists() or journal_path.is_symlink()
        journal = read_control_json(journal_path)
        if journal is None:
            if journal_exists:
                result["invalid"] += 1
            else:
                result["missing"] += 1
                result["sessions"].append(
                    _marker_only_evidence(session_id, marker, marker_skills)
                )
            continue
        if journal.get("version") != 1 or journal.get("sessionId") != session_id:
            result["invalid"] += 1
            continue

        journal_skills = _safe_skill_names(journal.get("observedSkills"))
        selected_skills = marker_skills & journal_skills
        friction = _sanitize_friction(
            journal.get("friction"),
            allowed_skills=selected_skills,
        )
        if not selected_skills or set(friction) != selected_skills:
            result["invalid"] += 1
            continue
        result["sessions"].append(
            {
                "receipt": review_receipt(session_id, marker, journal),
                "skills": sorted(selected_skills),
                "friction": friction,
                "reason": (
                    journal.get("reason")
                    if journal.get("reason") in _SESSION_END_REASONS
                    else "unknown"
                ),
                "ended": isinstance(journal.get("endedAt"), str),
                "journal": True,
            }
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read value-free Copilot capture journals selected by trusted pending markers. "
            "Output never includes session ids."
        )
    )
    parser.add_argument(
        "--session-id",
        action="append",
        dest="session_ids",
        help="Opaque session id loaded from trusted pending state (repeatable)",
    )
    parser.add_argument(
        "--all-pending",
        action="store_true",
        help=(
            "Read all trusted local pending markers and return per-session review "
            "receipts instead of session ids"
        ),
    )
    parser.add_argument(
        "--selection",
        help=(
            "Opaque trusted marker selection emitted by skill-reflect-auto; "
            "never include it in user-facing output"
        ),
    )
    parser.add_argument(
        "--home",
        type=Path,
        help="Override SKILL_REFLECT_HOME (primarily for tests)",
    )
    args = parser.parse_args()
    if not args.session_ids and not args.all_pending and not args.selection:
        parser.error("provide --session-id, --selection, or --all-pending")
    session_ids = list(args.session_ids or [])
    selection = None
    if args.selection:
        selection = read_review_selection(
            args.home or _default_home(),
            args.selection,
        )
        if selection is None:
            print(
                json.dumps(
                    {
                        "source": "copilot-auto-journal-v1",
                        "sessions": [],
                        "missing": 0,
                        "invalid": 1,
                    },
                    sort_keys=True,
                )
            )
            return 1
        session_ids.extend(selection)
    if args.all_pending:
        session_ids.extend(discover_pending_session_ids(args.home or _default_home()))

    result = read_journal_evidence(
        session_ids,
        home=args.home,
        selection=selection,
    )
    print(json.dumps(result, sort_keys=True))
    return 1 if result["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
