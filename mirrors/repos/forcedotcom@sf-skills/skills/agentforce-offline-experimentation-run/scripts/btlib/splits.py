"""Session splits (--val-fraction, --split) and excluded sessions (--exclude-sessions).

A unit's split depends on its session alone: sha256 of the salt and the session ID, read as a
number in [0, 1), gives "val" below the val fraction and "test" otherwise. So every step of a
session lands in one split, a session keeps its split when other sessions are added or
removed, and another salt gives an independent split.
"""

import csv
import hashlib
import io
import json
import re
from collections import Counter

from . import stdm

DEFAULT_SALT = "bt-split/1"
SPLITS = ("test", "val")


class SplitError(ValueError):
    pass


def session_split(session_id, val_fraction, salt=DEFAULT_SALT):
    h = hashlib.sha256(f"{salt}\0{session_id}".encode("utf-8")).hexdigest()
    return "val" if int(h[:13], 16) / 16 ** 13 < val_fraction else "test"


def label(units, val_fraction, salt=DEFAULT_SALT):
    """Set each unit's split; returns {split: [sessions, units]}. Units that already carry
    another split (an earlier run's labels) are refused: relabelling would mix the sets."""
    new = [session_split(u["session_id"], val_fraction, salt) for u in units]
    clash = sum(1 for u, s in zip(units, new) if u.get("split") not in (None, s))
    if clash:
        raise SplitError(f"{clash} units already carry another split (labelled with another salt or "
                         "fraction); use those, or split anew from --details")
    for u, s in zip(units, new):
        u["split"] = s
    sessions = {u["session_id"]: u["split"] for u in units}
    counts = Counter(sessions.values())
    return {s: [counts[s], new.count(s)] for s in SPLITS}


def read_session_ids(path):
    """Session IDs from a file that names sessions:
    - one ID per line (blank lines and '#' comments skipped);
    - JSONL with a session_id on each line: units.jsonl, results.jsonl;
    - JSON: a list of objects with a session_id (bt_fetch's sessions.json or details.json, the
      Apex class's output, also as an `sf apex run --json` file), or the old replay's
      replay_results.json. Not a list of strings: step and generation IDs look like session IDs;
    - CSV with a session_id column: replay_results_sfap.csv, the old replay's too.
    Any other file is refused, so that it never passes as a list of IDs that excludes nothing. So is
    an ID that is not letters, digits, '_', '.' and '-': matched exactly, " s1" would exclude nothing.
    """
    with open(path, encoding="utf-8-sig") as f:  # -sig: a CSV saved by Excel starts with a BOM
        text = f.read()
    lines = [(n, s.strip()) for n, s in enumerate(text.split("\n"), 1)]
    lines = [(n, s) for n, s in lines if s and not s.startswith("#")]
    if not lines:
        return set()
    first = lines[0][1]
    if first[0] in "[{":
        try:
            doc = json.loads(text)
        except ValueError as e:
            if first[0] == "[":
                raise SplitError(f"not valid JSON ({e})") from None
            return _jsonl_ids(lines)
        return _document_ids(doc)
    if "," in first or first == "session_id":
        return _csv_ids(text)
    for n, s in lines:
        if not _SESSION_ID.match(s):
            raise SplitError(f"line {n} is not a session ID, and the file is not JSON, JSONL or CSV")
    return {s for _, s in lines}


_SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def _jsonl_ids(lines):
    ids = set()
    for n, s in lines:
        try:
            row = json.loads(s)
        except ValueError:
            raise SplitError(f"line {n}: not JSON") from None
        ids.add(_session_id(row.get("session_id") if isinstance(row, dict) else None, f"line {n}"))
    return ids


def _document_ids(doc):
    if isinstance(doc, list):
        items = doc
    elif not isinstance(doc, dict):
        raise SplitError("JSON that is neither a list nor an object")
    else:
        try:
            found = stdm.parse_sf_output(doc, "sf apex run output")
        except stdm.StdmError as e:
            raise SplitError(str(e)) from None
        if found is not None:  # an `sf apex run --json` file
            if not found:
                raise SplitError("an sf apex run output without an STDM_RESULT line")
            items = [x for payload in found.values() for x in (payload if isinstance(payload, list) else [payload])]
        elif isinstance(doc.get("rows"), list):  # the old replay's replay_results.json
            items = [{"session_id": r.get("AiAgentSessionId")} if isinstance(r, dict) else r for r in doc["rows"]]
        else:
            items = [doc]
    ids = set()
    for i, item in enumerate(items, 1):
        if isinstance(item, str):
            raise SplitError(f"item {i} is a string, not an object with a session_id (step IDs look the "
                             "same); write a list of session IDs one per line")
        ids.add(_session_id(item.get("session_id") if isinstance(item, dict) else None, f"item {i}"))
    return ids


def _csv_ids(text):
    rows = csv.DictReader(io.StringIO(text))
    if "session_id" not in (rows.fieldnames or ()):
        raise SplitError("a CSV without a session_id column")
    ids = set()
    for i, row in enumerate(rows, 1):
        ids.add(_session_id((row.get("session_id") or "").strip(), f"CSV row {i}"))
    return ids


def _session_id(value, where):
    if not isinstance(value, str) or not value:
        raise SplitError(f"{where}: no session_id")
    if not _SESSION_ID.match(value):
        raise SplitError(f"{where}: its session_id is not a session ID")
    return value
