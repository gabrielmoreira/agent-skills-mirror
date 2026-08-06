#!/usr/bin/env python3
"""Consume reviewed pending markers and their journals without exposing session ids."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import time
from pathlib import Path
from typing import Iterable, Optional

from read_journal import (
    active_session_ids,
    control_directory_status,
    discover_pending_session_ids,
    read_control_json,
    review_receipt,
)

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,160}$")
_REVIEW_RECEIPT_RE = re.compile(r"^[a-f0-9]{32}$")
_LOCK_TOKEN_RE = re.compile(r"^[a-f0-9]{32}$")
_MAX_LOCK_ACQUIRE_ATTEMPTS = 50
_LOCK_RETRY_DELAY_SECONDS = 0.01


def _default_home() -> Path:
    configured = os.environ.get("SKILL_REFLECT_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".skill-reflect"


def _pid_is_live(pid: object) -> bool:
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


def _read_session_lock(lock_path: Path, session_id: str) -> dict | None:
    document = read_control_json(lock_path)
    if (
        not document
        or document.get("version") != 1
        or document.get("sessionId") != session_id
        or not isinstance(document.get("pid"), int)
        or isinstance(document.get("pid"), bool)
        or document["pid"] <= 0
        or not isinstance(document.get("token"), str)
        or not _LOCK_TOKEN_RE.fullmatch(document["token"])
        or not isinstance(document.get("choosing"), bool)
        or not isinstance(document.get("number"), int)
        or isinstance(document.get("number"), bool)
        or document["number"] < 0
        or document["number"] > 9_007_199_254_740_991
    ):
        return None
    return document


def _ensure_locks_directory(root: Path) -> Path | None:
    locks = root / "locks"
    status = control_directory_status(locks)
    if status == "missing":
        try:
            locks.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError:
            return None
        status = control_directory_status(locks)
    return locks if status == "ok" else None


def _atomic_lock_write(lock_path: Path, document: dict, *, create: bool) -> bool:
    temporary = lock_path.with_name(
        f"{lock_path.name}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(temporary, flags, 0o600)
        payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("short lock write")
            offset += written
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        if create:
            os.link(temporary, lock_path, follow_symlinks=False)
            temporary.unlink()
        else:
            os.replace(temporary, lock_path)
        return True
    except OSError:
        return False
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            temporary.unlink()
        except OSError:
            pass


def _list_session_lock_claims(
    locks: Path,
    session_id: str,
) -> list[tuple[Path, dict]] | None:
    try:
        entries = list(locks.iterdir())
    except OSError:
        return None
    prefix = f"{session_id}."
    claims: list[tuple[Path, dict]] = []
    for lock_path in entries:
        if not lock_path.name.startswith(prefix) or not lock_path.name.endswith(".json"):
            continue
        claim = _read_session_lock(lock_path, session_id)
        if (
            claim is None
            or lock_path.name
            != f"{session_id}.{claim['pid']}.{claim['token']}.json"
        ):
            return None
        if not _pid_is_live(claim["pid"]):
            try:
                lock_path.unlink()
            except OSError:
                pass
            continue
        claims.append((lock_path, claim))
    return claims


def _abandon_session_lock(
    lock: tuple[Path, str, int],
    session_id: str,
) -> None:
    lock_path, token, _ = lock
    owner = _read_session_lock(lock_path, session_id)
    if not owner or owner["token"] != token:
        return
    try:
        lock_path.unlink()
    except OSError:
        pass


def _acquire_session_lock(
    root: Path,
    session_id: str,
) -> tuple[Path, str, int] | None:
    locks = _ensure_locks_directory(root)
    if locks is None:
        return None
    token = secrets.token_hex(16)
    lock_path = locks / f"{session_id}.{os.getpid()}.{token}.json"
    initial_lock = (lock_path, token, 0)
    if not _atomic_lock_write(
        lock_path,
        {
            "version": 1,
            "sessionId": session_id,
            "pid": os.getpid(),
            "token": token,
            "choosing": True,
            "number": 0,
        },
        create=True,
    ):
        return None

    claims = _list_session_lock_claims(locks, session_id)
    if claims is None:
        _abandon_session_lock(initial_lock, session_id)
        return None
    number = max((claim["number"] for _, claim in claims), default=0) + 1
    lock = (lock_path, token, number)
    if not _atomic_lock_write(
        lock_path,
        {
            "version": 1,
            "sessionId": session_id,
            "pid": os.getpid(),
            "token": token,
            "choosing": False,
            "number": number,
        },
        create=False,
    ):
        _abandon_session_lock(lock, session_id)
        return None

    for _ in range(_MAX_LOCK_ACQUIRE_ATTEMPTS):
        current_claims = _list_session_lock_claims(locks, session_id)
        owner = _read_session_lock(lock_path, session_id)
        if (
            current_claims is None
            or owner is None
            or owner["token"] != token
            or owner["number"] != number
            or owner["choosing"]
        ):
            _abandon_session_lock(lock, session_id)
            return None
        blocked = any(
            claim["token"] != token
            and (
                claim["choosing"]
                or (
                    claim["number"] > 0
                    and (
                        claim["number"] < number
                        or (
                            claim["number"] == number
                            and claim["token"] < token
                        )
                    )
                )
            )
            for _, claim in current_claims
        )
        if not blocked:
            return lock
        time.sleep(_LOCK_RETRY_DELAY_SECONDS)

    _abandon_session_lock(lock, session_id)
    return None


def _release_session_lock(
    lock: tuple[Path, str, int],
    session_id: str,
) -> None:
    _abandon_session_lock(lock, session_id)


def consume_pending(
    session_ids: Iterable[str] = (),
    *,
    receipts: Iterable[str] = (),
    home: Optional[Path] = None,
) -> dict[str, int]:
    root = home or _default_home()
    pending = root / "pending"
    journal = root / "journal"
    result = {"consumed": 0, "journalsConsumed": 0, "missing": 0, "invalid": 0}
    selected_session_ids: list[str] = []
    expected_receipts: dict[str, str] = {}
    valid_receipts: list[str] = []

    for session_id in dict.fromkeys(session_ids):
        if (
            not isinstance(session_id, str)
            or session_id in {".", ".."}
            or not _SESSION_ID_RE.fullmatch(session_id)
        ):
            result["invalid"] += 1
            continue
        selected_session_ids.append(session_id)

    for receipt in dict.fromkeys(receipts):
        if not isinstance(receipt, str) or not _REVIEW_RECEIPT_RE.fullmatch(receipt):
            result["invalid"] += 1
            continue
        valid_receipts.append(receipt)

    root_status = control_directory_status(root)
    pending_status = (
        control_directory_status(pending) if root_status == "ok" else root_status
    )
    if pending_status != "ok":
        result["invalid" if pending_status == "invalid" else "missing"] += (
            len(selected_session_ids) + len(valid_receipts)
        )
        return result

    journal_status = control_directory_status(journal)
    if active_session_ids(root) is None:
        result["invalid"] += len(selected_session_ids) + len(valid_receipts)
        return result
    receipt_map: dict[str, list[str]] = {}
    for session_id in discover_pending_session_ids(root):
        marker_path = pending / f"{session_id}.json"
        marker = read_control_json(marker_path)
        if marker is None:
            continue
        if marker.get("sessionId") != session_id:
            continue
        journal_data = None
        if journal_status == "invalid":
            continue
        if journal_status == "ok":
            journal_path = journal / f"{session_id}.json"
            if journal_path.exists() or journal_path.is_symlink():
                journal_data = read_control_json(journal_path)
                if (
                    journal_data is None
                    or journal_data.get("version") != 1
                    or journal_data.get("sessionId") != session_id
                ):
                    continue
        receipt_map.setdefault(
            review_receipt(session_id, marker, journal_data),
            [],
        ).append(
            session_id
        )
    for receipt in valid_receipts:
        matches = receipt_map.get(receipt, [])
        if not matches:
            result["missing"] += 1
            continue
        if len(matches) != 1:
            result["invalid"] += 1
            continue
        selected_session_ids.append(matches[0])
        expected_receipts[matches[0]] = receipt

    for session_id in dict.fromkeys(selected_session_ids):
        lock = _acquire_session_lock(root, session_id)
        if lock is None:
            result["invalid"] += 1
            continue
        try:
            active = active_session_ids(root)
            if active is None or session_id in active:
                result["invalid"] += 1
                continue
            marker_path = pending / f"{session_id}.json"
            marker_exists = marker_path.exists() or marker_path.is_symlink()
            marker = read_control_json(marker_path)
            if marker is None:
                result["invalid" if marker_exists else "missing"] += 1
                continue
            if marker.get("sessionId") != session_id:
                result["invalid"] += 1
                continue
            journal_path = journal / f"{session_id}.json"
            journal_exists = (
                journal_status == "ok"
                and (journal_path.exists() or journal_path.is_symlink())
            )
            if journal_status == "invalid":
                result["invalid"] += 1
                continue
            if journal_exists:
                journal_data = read_control_json(journal_path)
                if (
                    journal_data is None
                    or journal_data.get("version") != 1
                    or journal_data.get("sessionId") != session_id
                ):
                    result["invalid"] += 1
                    continue
            else:
                journal_data = None
            expected_receipt = expected_receipts.get(session_id)
            if (
                expected_receipt
                and review_receipt(session_id, marker, journal_data)
                != expected_receipt
            ):
                result["invalid"] += 1
                continue

            if journal_exists:
                try:
                    journal_path.unlink()
                except OSError:
                    result["invalid"] += 1
                    continue
                else:
                    result["journalsConsumed"] += 1

            try:
                marker_path.unlink()
            except FileNotFoundError:
                result["missing"] += 1
            except OSError:
                result["invalid"] += 1
            else:
                result["consumed"] += 1
        finally:
            _release_session_lock(lock, session_id)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Consume reviewed pending markers and matching capture journals. "
            "Output contains counts only."
        )
    )
    parser.add_argument(
        "--session-id",
        action="append",
        dest="session_ids",
        help="Opaque reviewed session id (repeatable)",
    )
    parser.add_argument(
        "--receipt",
        action="append",
        dest="receipts",
        help="Value-free receipt returned by read_journal.py (repeatable)",
    )
    parser.add_argument(
        "--home",
        type=Path,
        help="Override SKILL_REFLECT_HOME (primarily for tests)",
    )
    args = parser.parse_args()
    if not args.session_ids and not args.receipts:
        parser.error("provide --session-id or --receipt")

    result = consume_pending(
        args.session_ids or (),
        receipts=args.receipts or (),
        home=args.home,
    )
    print(json.dumps(result, sort_keys=True))
    return 1 if result["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
