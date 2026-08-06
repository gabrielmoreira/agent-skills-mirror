#!/usr/bin/env python3
"""Unit tests for consume_pending.py (stdlib unittest)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from consume_pending import consume_pending
from read_journal import review_receipt


class ConsumePendingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.pending = self.home / "pending"
        self.pending.mkdir()
        self.journal = self.home / "journal"
        self.journal.mkdir()
        self.addCleanup(self._tmp.cleanup)

    def write_marker(self, session_id: str, marker_id: str | None = None) -> Path:
        path = self.pending / f"{session_id}.json"
        path.write_text(
            json.dumps(
                {
                    "sessionId": marker_id or session_id,
                    "skills": ["example-skill"],
                    "candidate": True,
                }
            ),
            encoding="utf-8",
        )
        return path

    def write_journal(self, session_id: str, journal_id: str | None = None) -> Path:
        path = self.journal / f"{session_id}.json"
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessionId": journal_id or session_id,
                    "observedSkills": ["example-skill"],
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

    def test_consumes_matching_markers_once(self):
        first = self.write_marker("session-one")
        second = self.write_marker("session-two")
        first_journal = self.write_journal("session-one")
        second_journal = self.write_journal("session-two")

        result = consume_pending(
            ["session-one", "session-two", "session-one"],
            home=self.home,
        )

        self.assertEqual(
            result,
            {
                "consumed": 2,
                "journalsConsumed": 2,
                "missing": 0,
                "invalid": 0,
            },
        )
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())
        self.assertFalse(first_journal.exists())
        self.assertFalse(second_journal.exists())

    def test_rejects_unsafe_or_mismatched_ids(self):
        outside = self.home / "outside.json"
        outside.write_text("keep", encoding="utf-8")
        mismatched = self.write_marker("safe-id", marker_id="different-id")

        result = consume_pending(["../outside", "safe-id"], home=self.home)

        self.assertEqual(
            result,
            {
                "consumed": 0,
                "journalsConsumed": 0,
                "missing": 0,
                "invalid": 2,
            },
        )
        self.assertTrue(outside.exists())
        self.assertTrue(mismatched.exists())

    def test_consumes_only_markers_selected_by_review_receipt(self):
        reviewed = self.write_marker("session-one")
        reviewed_journal = self.write_journal("session-one")
        pending = self.write_marker("session-two")
        pending_journal = self.write_journal("session-two")

        result = consume_pending(
            receipts=[self.receipt_for_marker(reviewed)],
            home=self.home,
        )

        self.assertEqual(
            result,
            {
                "consumed": 1,
                "journalsConsumed": 1,
                "missing": 0,
                "invalid": 0,
            },
        )
        self.assertFalse(reviewed.exists())
        self.assertFalse(reviewed_journal.exists())
        self.assertTrue(pending.exists())
        self.assertTrue(pending_journal.exists())

    def test_rejects_invalid_or_missing_review_receipts(self):
        result = consume_pending(
            receipts=["not-a-receipt", "0" * 32],
            home=self.home,
        )

        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["missing"], 1)

    def test_receipt_does_not_consume_a_changed_marker(self):
        marker = self.write_marker("session-one")
        receipt = self.receipt_for_marker(marker)
        data = json.loads(marker.read_text(encoding="utf-8"))
        data["friction"] = {"example-skill": 3}
        marker.write_text(json.dumps(data), encoding="utf-8")

        result = consume_pending(receipts=[receipt], home=self.home)

        self.assertEqual(result["missing"], 1)
        self.assertTrue(marker.exists())

    def test_receipt_does_not_consume_a_changed_journal(self):
        marker = self.write_marker("session-one")
        journal = self.write_journal("session-one")
        receipt = self.receipt_for_marker(marker)
        data = json.loads(journal.read_text(encoding="utf-8"))
        data["observedSkills"].append("new-unreviewed-skill")
        journal.write_text(json.dumps(data), encoding="utf-8")

        result = consume_pending(receipts=[receipt], home=self.home)

        self.assertEqual(result["missing"], 1)
        self.assertTrue(marker.exists())
        self.assertTrue(journal.exists())

    def test_marker_only_fallback_is_consumable_by_receipt(self):
        marker = self.write_marker("legacy-session")

        result = consume_pending(
            receipts=[self.receipt_for_marker(marker)],
            home=self.home,
        )

        self.assertEqual(
            result,
            {
                "consumed": 1,
                "journalsConsumed": 0,
                "missing": 0,
                "invalid": 0,
            },
        )
        self.assertFalse(marker.exists())

    def test_missing_marker_is_not_an_error(self):
        self.assertEqual(
            consume_pending(["missing-id"], home=self.home),
            {
                "consumed": 0,
                "journalsConsumed": 0,
                "missing": 1,
                "invalid": 0,
            },
        )

    def test_invalid_journal_preserves_marker(self):
        marker = self.write_marker("safe-id")
        journal = self.write_journal("safe-id", journal_id="different-id")

        result = consume_pending(["safe-id"], home=self.home)

        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["consumed"], 0)
        self.assertTrue(marker.exists())
        self.assertTrue(journal.exists())

    def test_journal_is_removed_before_marker_for_recoverability(self):
        marker = self.write_marker("safe-id")
        journal = self.write_journal("safe-id")

        def controlled_unlink(path: Path, missing_ok: bool = False) -> None:
            if path == marker:
                raise OSError("simulated marker unlink failure")
            os.unlink(path)

        with mock.patch.object(Path, "unlink", autospec=True, side_effect=controlled_unlink):
            result = consume_pending(["safe-id"], home=self.home)

        self.assertEqual(result["consumed"], 0)
        self.assertEqual(result["journalsConsumed"], 1)
        self.assertEqual(result["invalid"], 1)
        self.assertTrue(marker.exists())
        self.assertFalse(journal.exists())

    def test_rejects_symlinked_control_directory(self):
        self.pending.rmdir()
        outside = self.home / "outside-pending"
        outside.mkdir()
        self.pending.symlink_to(outside, target_is_directory=True)

        result = consume_pending(["safe-id"], home=self.home)

        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["consumed"], 0)

    def test_active_session_cannot_be_consumed(self):
        marker = self.write_marker("active-session")
        journal = self.write_journal("active-session")
        receipt = self.receipt_for_marker(marker)
        self.mark_active("active-session")

        result = consume_pending(
            ["active-session"],
            receipts=[receipt],
            home=self.home,
        )

        self.assertGreaterEqual(result["invalid"], 1)
        self.assertTrue(marker.exists())
        self.assertTrue(journal.exists())

    def test_rechecks_active_state_while_holding_session_lock(self):
        marker = self.write_marker("racing-session")
        journal = self.write_journal("racing-session")

        with mock.patch(
            "consume_pending.active_session_ids",
            side_effect=[set(), {"racing-session"}],
        ):
            result = consume_pending(["racing-session"], home=self.home)

        self.assertEqual(result["invalid"], 1)
        self.assertTrue(marker.exists())
        self.assertTrue(journal.exists())

    def test_live_session_lock_blocks_consumption(self):
        marker = self.write_marker("locked-session")
        journal = self.write_journal("locked-session")
        locks = self.home / "locks"
        locks.mkdir()
        token = "a" * 32
        (
            locks / f"locked-session.{os.getpid()}.{token}.json"
        ).write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessionId": "locked-session",
                    "pid": os.getpid(),
                    "token": token,
                    "choosing": False,
                    "number": 1,
                }
            ),
            encoding="utf-8",
        )

        result = consume_pending(["locked-session"], home=self.home)

        self.assertEqual(result["invalid"], 1)
        self.assertTrue(marker.exists())
        self.assertTrue(journal.exists())

    def test_stale_session_lock_is_reclaimed(self):
        marker = self.write_marker("stale-lock-session")
        journal = self.write_journal("stale-lock-session")
        locks = self.home / "locks"
        locks.mkdir()
        token = "b" * 32
        lock_path = (
            locks / f"stale-lock-session.99999999.{token}.json"
        )
        lock_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessionId": "stale-lock-session",
                    "pid": 99_999_999,
                    "token": token,
                    "choosing": False,
                    "number": 1,
                }
            ),
            encoding="utf-8",
        )

        result = consume_pending(["stale-lock-session"], home=self.home)

        self.assertEqual(result["consumed"], 1)
        self.assertEqual(result["journalsConsumed"], 1)
        self.assertFalse(marker.exists())
        self.assertFalse(journal.exists())
        self.assertFalse(lock_path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
