#!/usr/bin/env python3
"""Unit tests for read_journal.py."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from read_journal import (
    discover_pending_session_ids,
    read_journal_evidence,
    read_review_selection,
    read_selection_session_ids,
    review_receipt,
)


class ReadJournalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        (self.home / "pending").mkdir()
        (self.home / "journal").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def write_marker(self, session_id: str, skills: list[str]) -> Path:
        path = self.home / "pending" / f"{session_id}.json"
        path.write_text(
            json.dumps(
                {
                    "sessionId": session_id,
                    "skills": skills,
                    "friction": {skill: 2 for skill in skills},
                    "candidate": True,
                    "journalVersion": 1,
                }
            ),
            encoding="utf-8",
        )
        return path

    def write_journal(self, session_id: str) -> Path:
        path = self.home / "journal" / f"{session_id}.json"
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessionId": session_id,
                    "observedSkills": ["example-skill", "unselected-skill"],
                    "friction": {
                        "example-skill": {
                            "count": 2,
                            "signals": {"tool_failure": 1, "tool_retry": 1},
                        },
                        "unselected-skill": {
                            "count": 99,
                            "signals": {"tool_failure": 99},
                        },
                    },
                    "endedAt": "2026-08-04T12:00:00.000Z",
                    "reason": "complete",
                    "capture": {
                        "inFlightTools": {
                            "deadbeefdeadbeefdeadbeef": {
                                "shape": "private-derived-value",
                            }
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def receipt_for_marker(path: Path) -> str:
        marker = json.loads(path.read_text(encoding="utf-8"))
        journal_path = path.parent.parent / "journal" / path.name
        journal = (
            json.loads(journal_path.read_text(encoding="utf-8"))
            if journal_path.exists()
            else None
        )
        return review_receipt(marker["sessionId"], marker, journal)

    def mark_active(self, session_id: str) -> None:
        active = self.home / "active"
        active.mkdir(exist_ok=True)
        (active / f"{session_id}.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessionId": session_id,
                    "pid": os.getpid(),
                }
            ),
            encoding="utf-8",
        )

    def test_reads_only_marker_selected_value_free_evidence(self):
        marker = self.write_marker("opaque-session", ["example-skill"])
        self.write_journal("opaque-session")

        result = read_journal_evidence(
            ["opaque-session"],
            home=self.home,
        )

        self.assertEqual(result["invalid"], 0)
        self.assertEqual(result["missing"], 0)
        self.assertEqual(
            result["sessions"],
            [
                {
                    "receipt": self.receipt_for_marker(marker),
                    "skills": ["example-skill"],
                    "friction": {
                        "example-skill": {
                            "count": 2,
                            "signals": {
                                "tool_failure": 1,
                                "tool_retry": 1,
                            },
                        }
                    },
                    "reason": "complete",
                    "ended": True,
                    "journal": True,
                }
            ],
        )
        rendered = json.dumps(result)
        self.assertNotIn("opaque-session", rendered)
        self.assertNotIn("unselected-skill", rendered)
        self.assertNotIn("private-derived-value", rendered)

    def test_discovers_safe_pending_markers_for_id_free_review(self):
        marker = self.write_marker("opaque-session", ["example-skill"])
        self.write_journal("opaque-session")
        outside = self.home / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (self.home / "pending" / "linked.json").symlink_to(outside)

        result = read_journal_evidence(
            discover_pending_session_ids(self.home),
            home=self.home,
        )

        self.assertEqual(len(result["sessions"]), 1)
        self.assertEqual(
            result["sessions"][0]["receipt"],
            self.receipt_for_marker(marker),
        )
        self.assertNotIn("opaque-session", json.dumps(result))

    def test_trusted_selection_limits_pending_scope(self):
        selected = self.write_marker("selected-session", ["example-skill"])
        self.write_journal("selected-session")
        self.write_marker("unselected-session", ["example-skill"])
        self.write_journal("unselected-session")
        token = "a" * 32
        selections = self.home / "selections"
        selections.mkdir()
        (selections / f"{token}.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "token": token,
                    "markers": [
                        {
                            "sessionId": "selected-session",
                            "skills": ["example-skill"],
                            "markerDigest": hashlib.sha256(
                                selected.read_bytes()
                            ).hexdigest(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        selection = read_review_selection(self.home, token)
        session_ids = read_selection_session_ids(self.home, token)
        result = read_journal_evidence(
            session_ids or [],
            home=self.home,
            selection=selection,
        )

        self.assertEqual(len(result["sessions"]), 1)
        self.assertEqual(
            result["sessions"][0]["receipt"],
            self.receipt_for_marker(selected),
        )

    def test_selection_enforces_skill_subset_and_marker_digest(self):
        marker = self.write_marker(
            "selected-session",
            ["example-skill", "excluded-skill"],
        )
        self.write_journal("selected-session")
        token = "b" * 32
        selections = self.home / "selections"
        selections.mkdir()
        selection_path = selections / f"{token}.json"
        selection_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "token": token,
                    "markers": [
                        {
                            "sessionId": "selected-session",
                            "skills": ["example-skill"],
                            "markerDigest": hashlib.sha256(
                                marker.read_bytes()
                            ).hexdigest(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        selection = read_review_selection(self.home, token)
        result = read_journal_evidence(
            ["selected-session"],
            home=self.home,
            selection=selection,
        )
        self.assertEqual(result["sessions"][0]["skills"], ["example-skill"])

        marker.write_text(
            marker.read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )
        changed = read_journal_evidence(
            ["selected-session"],
            home=self.home,
            selection=selection,
        )
        self.assertEqual(changed["sessions"], [])
        self.assertEqual(changed["invalid"], 1)

    def test_active_session_is_excluded_from_discovery_and_reading(self):
        self.write_marker("active-session", ["example-skill"])
        self.write_journal("active-session")
        self.mark_active("active-session")

        self.assertEqual(discover_pending_session_ids(self.home), [])
        result = read_journal_evidence(["active-session"], home=self.home)
        self.assertEqual(result["sessions"], [])
        self.assertEqual(result["invalid"], 1)

    def test_requires_matching_trusted_marker(self):
        self.write_journal("orphan-session")

        result = read_journal_evidence(["orphan-session"], home=self.home)

        self.assertEqual(result["sessions"], [])
        self.assertEqual(result["missing"], 1)

    def test_missing_journal_returns_consumable_marker_fallback(self):
        marker = self.write_marker("legacy-session", ["example-skill"])

        result = read_journal_evidence(["legacy-session"], home=self.home)

        self.assertEqual(result["missing"], 1)
        self.assertEqual(result["invalid"], 0)
        self.assertEqual(
            result["sessions"],
            [
                {
                    "receipt": self.receipt_for_marker(marker),
                    "skills": ["example-skill"],
                    "friction": {
                        "example-skill": {
                            "count": 2,
                            "signals": {},
                        }
                    },
                    "reason": "unknown",
                    "ended": False,
                    "journal": False,
                }
            ],
        )

    def test_sanitizes_unexpected_end_reason(self):
        self.write_marker("opaque-session", ["example-skill"])
        journal = self.write_journal("opaque-session")
        data = json.loads(journal.read_text(encoding="utf-8"))
        data["reason"] = "private runtime detail"
        journal.write_text(json.dumps(data), encoding="utf-8")

        result = read_journal_evidence(["opaque-session"], home=self.home)

        self.assertEqual(result["sessions"][0]["reason"], "unknown")
        self.assertNotIn("private runtime detail", json.dumps(result))

    def test_rejects_symlinks_and_mismatched_documents(self):
        outside = self.home / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        (self.home / "pending" / "linked.json").symlink_to(outside)
        self.write_marker("mismatch", ["example-skill"])
        journal = self.write_journal("mismatch")
        data = json.loads(journal.read_text(encoding="utf-8"))
        data["sessionId"] = "different"
        journal.write_text(json.dumps(data), encoding="utf-8")

        result = read_journal_evidence(
            ["linked", "mismatch", "../outside"],
            home=self.home,
        )

        self.assertEqual(result["sessions"], [])
        self.assertEqual(result["invalid"], 3)

    def test_rejects_symlinked_control_directory(self):
        pending = self.home / "pending"
        pending.rmdir()
        outside = self.home / "outside-pending"
        outside.mkdir()
        pending.symlink_to(outside, target_is_directory=True)

        result = read_journal_evidence(["opaque-session"], home=self.home)

        self.assertEqual(result["sessions"], [])
        self.assertEqual(result["invalid"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
