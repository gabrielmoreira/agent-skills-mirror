"""Discovery artifacts must resolve from one run root after set-screening-audit."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import manage_run_state as RUN_STATE  # noqa: E402
import prepublish_audit as PREPUBLISH  # noqa: E402

ASSETS_DIR = SCRIPTS_DIR.parent / "assets"


class ArtifactPathTests(unittest.TestCase):
    def _init_and_attach(self, run_dir: Path) -> dict:
        payload = json.loads((ASSETS_DIR / "candidate-input.example.json").read_text())
        self.assertEqual(
            RUN_STATE.main(
                [
                    "init",
                    "--run-dir",
                    str(run_dir),
                    "--analysis-as-of",
                    payload["analysis_as_of"],
                    "--price-as-of",
                    payload["price_basis"]["as_of"],
                    "--session",
                    "regular_close",
                    "--price-source-id",
                    "quote-20260821",
                    "--config",
                    str(ASSETS_DIR / "screening-config.example.json"),
                    "--market-context",
                    str(ASSETS_DIR / "market-context.example.json"),
                    "--global-sources",
                    str(ASSETS_DIR / "global-sources.example.json"),
                ]
            ),
            0,
        )
        self.assertEqual(
            RUN_STATE.main(
                [
                    "set-screening-audit",
                    "--run-dir",
                    str(run_dir),
                    "--audit",
                    str(ASSETS_DIR / "broad-screen-audit.example.json"),
                    "--universe-artifact",
                    str(ASSETS_DIR / "universe-audit-results.example.jsonl"),
                    "--candidate-artifact",
                    str(ASSETS_DIR / "broad-screen-results.example.jsonl"),
                ]
            ),
            0,
        )
        return json.loads((run_dir / "audit" / "broad-screen-audit.json").read_text())

    def test_enrichment_and_generation_artifacts_are_copied_under_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            audit = self._init_and_attach(run_dir)
            enrichment = audit["enrichment"]
            generation = audit["candidate_pool"].get("generation_audit") or {}
            sections = [audit["universe"], audit["candidate_pool"], enrichment]
            if generation.get("artifact_path"):
                sections.append(generation)
            for section in sections:
                path = section["artifact_path"]
                self.assertTrue(path.startswith("audit/"), path)
                target = run_dir / path
                self.assertTrue(target.is_file(), path)
                self.assertEqual(
                    hashlib.sha256(target.read_bytes()).hexdigest(), section["artifact_sha256"]
                )

    def test_prepublish_resolves_every_artifact_from_the_run_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            audit = self._init_and_attach(run_dir)
            errors: list[str] = []
            PREPUBLISH._verify_artifact(audit["universe"], run_dir, "universe", errors)
            PREPUBLISH._verify_artifact(audit["candidate_pool"], run_dir, "candidate_pool", errors)
            PREPUBLISH._verify_artifact(audit["enrichment"], run_dir, "enrichment", errors)
            generation = audit["candidate_pool"].get("generation_audit") or {}
            if generation.get("artifact_path"):
                PREPUBLISH._verify_artifact(generation, run_dir, "generation", errors)
            self.assertEqual(errors, [])

    def test_prepublish_accepts_audit_relative_bare_names(self) -> None:
        # A discovery audit that was never passed through set-screening-audit
        # still references bare file names relative to audit/.
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "audit").mkdir()
            body = b'{"a": 1}\n'
            (root / "audit" / "enrichment-queue.json").write_bytes(body)
            section = {
                "artifact_path": "enrichment-queue.json",
                "artifact_sha256": hashlib.sha256(body).hexdigest(),
            }
            errors: list[str] = []
            PREPUBLISH._verify_artifact(section, root, "enrichment", errors)
            self.assertEqual(errors, [])
            missing: list[str] = []
            PREPUBLISH._verify_artifact(
                {"artifact_path": "nope.json", "artifact_sha256": "0" * 64}, root, "x", missing
            )
            self.assertEqual(missing, ["x artifact is missing: nope.json"])


if __name__ == "__main__":
    unittest.main()
