from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from hash_candidate_tree import CandidateTreeError, candidate_tree_sha256
from inspect_distillation_state import (
    StateInspectionError,
    inspect_distillation_state,
    main,
)
from test_validate_distillation import (
    FIXTURE_CANDIDATE_PATH,
    FIXTURE_SKILL,
    FIXTURE_TASK_DEFINITION,
    FIXTURE_TRIGGER_DEFINITION,
    set_rule_pending,
    sync_task_contract_snapshot,
    sync_current_gate3_approval_snapshot,
    valid_documents,
    valid_sources_manifest,
)
from validate_distillation import validate_distillation as run_validator


class DistillationStateInspectionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.candidate = self.root / FIXTURE_CANDIDATE_PATH
        self.candidate.mkdir(parents=True)
        (self.candidate / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
        eval_dir = self.candidate / "evals"
        eval_dir.mkdir()
        (eval_dir / "trigger-cases.json").write_text(
            json.dumps(FIXTURE_TRIGGER_DEFINITION, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (eval_dir / "task-cases.json").write_text(
            json.dumps(FIXTURE_TASK_DEFINITION, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.documents = valid_documents()
        self._refresh_recorded_hash()
        self.manifest = self.root / "sources.yml"
        self.manifest.write_text(
            yaml.safe_dump(valid_sources_manifest(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.write_documents()

    def tearDown(self):
        self.tempdir.cleanup()

    def _refresh_recorded_hash(self):
        materializations = self.documents["gate-decisions.yml"]["materializations"]
        if materializations:
            candidate_hash = candidate_tree_sha256(
                self.root, FIXTURE_CANDIDATE_PATH
            )
            materializations[0]["candidate_hash"] = candidate_hash
            materializations[0]["quick_validation"]["candidate_hash"] = candidate_hash

    def write_documents(self, *, sync_approval_snapshot=True):
        sync_task_contract_snapshot(self.documents, self.root)
        for name in (
            "evidence-ledger.yml",
            "concept-map.yml",
            "capability-rules.yml",
        ):
            document = self.documents[name]
            (self.root / name).write_text(
                yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        if sync_approval_snapshot:
            sync_current_gate3_approval_snapshot(self.documents, self.root)
        for name, document in self.documents.items():
            if name in {
                "evidence-ledger.yml",
                "concept-map.yml",
                "capability-rules.yml",
                "task-contract.yml",
                "task-coverage.yml",
            }:
                continue
            (self.root / name).write_text(
                yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

    def inspect(self, *, with_manifest=True):
        return inspect_distillation_state(
            self.root,
            "candidate-001",
            FIXTURE_CANDIDATE_PATH,
            self.manifest if with_manifest else None,
        )

    def assert_fixture_valid(self):
        report = run_validator(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_exact_match_is_only_gate4_eligible_not_behavior_pass(self):
        self.assert_fixture_valid()
        report = self.inspect()
        self.assertEqual("gate4-eligible", report["activation_state"])
        self.assertEqual(["materialization-001"], report["materializations"]["matching"])
        self.assertFalse(report["truth_assessed"])
        self.assertFalse(report["behavior_effectiveness_assessed"])
        self.assertFalse(report["gate4_accepted"])
        self.assertEqual(0, report["completed_pass_eval_count"])
        snapshot = report["current_gate3"]["approval_snapshot"]
        self.assertTrue(snapshot["present"])
        self.assertEqual(FIXTURE_CANDIDATE_PATH, snapshot["candidate_path"])
        self.assertEqual(
            report["candidate"]["computed_hash"], snapshot["candidate_hash"]
        )
        self.assertTrue(
            report["current_gate3"]["approval_snapshot_matches_candidate"]
        )
        product = report["authoritative_product_contract"]
        self.assertEqual("matches", product["task_contract_drift"])
        self.assertEqual(["stable-task-001"], product["active_stable_task_ids"])
        self.assertEqual("gate4-eligible", report["continuation_mode"])

    def test_legacy_gate3_reports_review_repair_only(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["approval_snapshot"] = {
            key: value for key, value in gate3["approval_snapshot"].items()
            if key in {"contract", "candidate_path", "candidate_hash", "governance_hashes"}
        }
        gate3["approval_snapshot"]["contract"] = "gate3-approval-snapshot:v1"
        self.write_documents(sync_approval_snapshot=False)
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertEqual("review-repair-only", report["continuation_mode"])
        self.assertIn("review", report["allowed_actions"])

    def test_checkpoint_cannot_supersede_product_contract(self):
        gate1 = self.documents["gate-decisions.yml"]["gate_decisions"][0]
        snapshot = gate1["task_contract_snapshot"]
        checkpoint = {
            "schema_version": 1,
            "distillation_id": "validator-test-v1",
            "checkpoint_id": "checkpoint-001",
            "created_at": "2026-08-07",
            "product_contract_anchor": {
                "path": snapshot["task_contract_path"],
                "sha256": snapshot["task_contract_hash"],
                "task_contract_id": snapshot["task_contract_id"],
                "contract_version": snapshot["contract_version"],
                "active_stable_task_ids": snapshot["active_stable_task_ids"],
            },
            "current_stage_objective": {
                "gate": "gate-3",
                "statement": "Exclude the external task after compression.",
                "stable_task_ids": ["stable-task-001"],
                "supersedes_product_contract": True,
                "excluded_stable_task_ids": ["stable-task-001"],
            },
            "temporary_operational_constraints": ["Review only."],
        }
        (self.root / "context-checkpoint.yml").write_text(
            yaml.safe_dump(checkpoint, sort_keys=False), encoding="utf-8"
        )
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertEqual("review-repair-only", report["continuation_mode"])
        self.assertTrue(any(
            item["code"] == "CHECKPOINT_PRODUCT_CONTRACT_CONFLICT"
            for item in report["blockers"]
        ))

    def test_report_and_cli_output_are_deterministic(self):
        first = json.dumps(self.inspect(), ensure_ascii=False, indent=2, sort_keys=True)
        second = json.dumps(self.inspect(), ensure_ascii=False, indent=2, sort_keys=True)
        self.assertEqual(first, second)

        outputs = []
        for _ in range(2):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = main([
                    str(self.root),
                    "--candidate-id", "candidate-001",
                    "--candidate-path", FIXTURE_CANDIDATE_PATH,
                    "--sources-manifest", str(self.manifest),
                ])
            self.assertEqual(0, status)
            outputs.append(stdout.getvalue())
        self.assertEqual(outputs[0], outputs[1])

    def test_pending_revise_or_rejected_gate3_is_review_only(self):
        for decision in ("pending", "revise", "rejected"):
            with self.subTest(decision=decision):
                documents = valid_documents()
                set_rule_pending(documents)
                gate3 = documents["gate-decisions.yml"]["gate_decisions"][2]
                gate3["decision"] = decision
                if decision == "pending":
                    gate3.update({
                        "reviewer_type": None,
                        "reviewer": None,
                        "decided_at": None,
                    })
                else:
                    gate3.update({
                        "reviewer_type": "user",
                        "reviewer": "project-user",
                        "decided_at": "2026-08-04",
                        "rationale": f"Gate 3 {decision} for the synthetic fixture.",
                    })
                self.documents = documents
                self.write_documents()
                self.assert_fixture_valid()
                self.assertEqual("review-only", self.inspect()["activation_state"])

    def test_approval_without_materialization_requires_materialization(self):
        self.documents["gate-decisions.yml"]["materializations"] = []
        self.write_documents()
        self.assert_fixture_valid()
        report = self.inspect()
        self.assertEqual("materialization-required", report["activation_state"])
        self.assertEqual([], report["materializations"]["matching"])

    def test_missing_tree_after_approval_is_invalid_even_before_materialization(self):
        self.documents["gate-decisions.yml"]["materializations"] = []
        self.write_documents()
        shutil.rmtree(self.candidate)
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIsNone(report["candidate"]["computed_hash"])
        self.assertEqual("not-yet-materialized", report["candidate"]["tree_status"])
        self.assertIn(
            "APPROVAL_SNAPSHOT_CANDIDATE_HASH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )

    def test_invalidated_or_legacy_materialization_is_historical_only(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        for status in ("invalidated", "legacy-quarantined"):
            with self.subTest(status=status):
                materialization["status"] = status
                self.write_documents()
                self.assert_fixture_valid()
                report = self.inspect()
                self.assertEqual("materialization-required", report["activation_state"])
                self.assertEqual([], report["materializations"]["matching"])

    def test_candidate_byte_change_never_remains_eligible(self):
        (self.candidate / "SKILL.md").write_text(
            FIXTURE_SKILL + "\nChanged.\n", encoding="utf-8"
        )
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "MATERIALIZATION_CANDIDATE_HASH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )
        self.assertIn(
            "APPROVAL_SNAPSHOT_CANDIDATE_HASH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )

    def test_missing_or_malformed_approval_snapshot_is_invalid(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        for snapshot in (None, [], {"contract": "wrong"}):
            with self.subTest(snapshot=repr(snapshot)):
                self.documents = valid_documents()
                self._refresh_recorded_hash()
                self.write_documents()
                gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
                if snapshot is None:
                    gate3.pop("approval_snapshot", None)
                else:
                    gate3["approval_snapshot"] = snapshot
                self.write_documents(sync_approval_snapshot=False)
                report = self.inspect()
                self.assertEqual("invalid", report["activation_state"])
                self.assertIn(
                    "APPROVAL_SNAPSHOT_INVALID",
                    {item["code"] for item in report["blockers"]},
                )

    def test_cli_candidate_path_must_exactly_match_approval_snapshot(self):
        alternative_path = "alternate/review-book-task"
        alternative = self.root / alternative_path
        shutil.copytree(self.candidate, alternative)
        report = inspect_distillation_state(
            self.root,
            "candidate-001",
            alternative_path,
            self.manifest,
        )
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "APPROVAL_SNAPSHOT_CANDIDATE_PATH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )

    def test_failed_quick_validation_is_invalid(self):
        quick = self.documents["gate-decisions.yml"]["materializations"][0][
            "quick_validation"
        ]
        quick["status"] = "fail"
        self.write_documents()
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "MATERIALIZATION_QUICK_VALIDATION_REQUIRED",
            {item["code"] for item in report["blockers"]},
        )

    def test_gate4_eligibility_requires_explicit_manifest(self):
        report = self.inspect(with_manifest=False)
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "SOURCES_MANIFEST_REQUIRED_FOR_GATE4",
            {item["code"] for item in report["blockers"]},
        )
        self.assertFalse(report["validation"]["sources_manifest_provided"])

    def test_governance_hash_drift_is_invalid(self):
        evidence_path = self.root / "evidence-ledger.yml"
        evidence_path.write_bytes(evidence_path.read_bytes() + b"\n")
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "GATE3_APPROVAL_GOVERNANCE_HASH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )

    def test_completed_materialization_must_match_approval_snapshot(self):
        alternative_path = "alternate/review-book-task"
        shutil.copytree(self.candidate, self.root / alternative_path)
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["candidate_path"] = alternative_path
        self.write_documents()
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "MATERIALIZATION_APPROVAL_PATH_MISMATCH",
            {item["code"] for item in report["blockers"]},
        )

    def test_nonreview_lifecycle_never_routes_to_gate4(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        for lifecycle in ("draft", "rejected", "deprecated"):
            with self.subTest(lifecycle=lifecycle):
                candidate["lifecycle"] = lifecycle
                self.write_documents()
                report = self.inspect()
                self.assertEqual("invalid", report["activation_state"])
                self.assertIn(
                    "CANDIDATE_LIFECYCLE_NOT_REVIEW",
                    {item["code"] for item in report["blockers"]},
                )

    def test_malformed_rule_ids_returns_invalid_instead_of_crashing(self):
        self.documents["gate-decisions.yml"]["materializations"][0]["rule_ids"] = [
            ["rule-001"]
        ]
        self.write_documents()
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "approved-rule-set-mismatch",
            report["materializations"]["stale_completed"][0]["reasons"],
        )

    def test_duplicate_yaml_key_is_rejected(self):
        gate_path = self.root / "gate-decisions.yml"
        text = gate_path.read_text(encoding="utf-8")
        text = text.replace(
            "  decision: approved-for-eval\n",
            "  decision: rejected\n  decision: approved-for-eval\n",
            1,
        )
        gate_path.write_text(text, encoding="utf-8")
        with self.assertRaises(StateInspectionError) as caught:
            self.inspect()
        self.assertEqual("YAML_PARSE", caught.exception.code)

    def test_governance_change_during_validation_fails_closed(self):
        original = run_validator

        def mutate_then_validate(root, manifest):
            set_rule_pending(self.documents)
            self.write_documents()
            return original(root, manifest)

        with patch(
            "inspect_distillation_state.validate_distillation",
            side_effect=mutate_then_validate,
        ):
            report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "INSPECTION_SNAPSHOT_CHANGED",
            {item["code"] for item in report["blockers"]},
        )

    def test_write_restore_cannot_mix_routing_and_validator_snapshots(self):
        original = run_validator
        tracked_paths = [self.root / name for name in self.documents]
        original_bytes = {path: path.read_bytes() for path in tracked_paths}

        def switch_to_b_validate_then_restore(root, manifest):
            extra = copy.deepcopy(
                self.documents["evidence-ledger.yml"]["evidence"][0]
            )
            extra["evidence_id"] = "ev-002"
            self.documents["evidence-ledger.yml"]["evidence"].append(extra)
            self.write_documents()
            try:
                return original(root, manifest)
            finally:
                for path, payload in original_bytes.items():
                    path.write_bytes(payload)

        with patch(
            "inspect_distillation_state.validate_distillation",
            side_effect=switch_to_b_validate_then_restore,
        ):
            report = self.inspect()
        self.assertEqual("gate4-eligible", report["activation_state"])
        self.assertEqual(1, report["validation"]["metrics"]["evidence_count"])

    def test_external_manifest_write_restore_uses_frozen_bytes(self):
        original = run_validator
        with tempfile.TemporaryDirectory() as external_dir:
            manifest = Path(external_dir) / "manifests" / "sources.yml"
            manifest.parent.mkdir()
            manifest.write_text(
                yaml.safe_dump(
                    valid_sources_manifest(), allow_unicode=True, sort_keys=False
                ),
                encoding="utf-8",
            )
            original_bytes = manifest.read_bytes()

            def switch_manifest_then_restore(root, snapshot_manifest):
                changed = valid_sources_manifest()
                changed["sources"][0]["id"] = "different-book"
                manifest.write_text(
                    yaml.safe_dump(changed, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
                try:
                    return original(root, snapshot_manifest)
                finally:
                    manifest.write_bytes(original_bytes)

            with patch(
                "inspect_distillation_state.validate_distillation",
                side_effect=switch_manifest_then_restore,
            ):
                report = inspect_distillation_state(
                    self.root,
                    "candidate-001",
                    FIXTURE_CANDIDATE_PATH,
                    manifest,
                )
        self.assertEqual("gate4-eligible", report["activation_state"])
        self.assertTrue(report["validation"]["ok"])

    def test_markdown_source_write_restore_uses_frozen_bytes(self):
        original = run_validator
        source_text = "# Policy\n\n## Review Gate\n\nStable policy text.\n"
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["locator"] = {
            "source_id": "book-001",
            "locator_type": "markdown-section",
            "anchor": "docs/policy.md:5#review-gate",
            "content_hash": hashlib.sha256(
                b"Stable policy text."
            ).hexdigest()[:12],
        }
        evidence["raw_text"] = "Stable policy text."
        evidence["normalized_text"] = "Stable policy text."
        self.write_documents()

        with tempfile.TemporaryDirectory() as external_dir:
            project = Path(external_dir) / "project"
            manifest = project / "manifests" / "sources.yml"
            source = project / "docs" / "policy.md"
            manifest.parent.mkdir(parents=True)
            source.parent.mkdir(parents=True)
            manifest_data = valid_sources_manifest()
            manifest_data["sources"][0].update({
                "local_path": "docs/policy.md",
                "related_local_paths": [],
            })
            manifest.write_text(
                yaml.safe_dump(manifest_data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            source.write_text(source_text, encoding="utf-8")
            original_source = source.read_bytes()

            def switch_source_then_restore(root, snapshot_manifest):
                source.write_text("# Policy\n\nChanged text.\n", encoding="utf-8")
                try:
                    return original(root, snapshot_manifest)
                finally:
                    source.write_bytes(original_source)

            with patch(
                "inspect_distillation_state.validate_distillation",
                side_effect=switch_source_then_restore,
            ):
                report = inspect_distillation_state(
                    self.root,
                    "candidate-001",
                    FIXTURE_CANDIDATE_PATH,
                    manifest,
                )
        self.assertEqual("gate4-eligible", report["activation_state"])
        self.assertTrue(report["validation"]["ok"])

    def test_old_gate_or_rule_mismatch_is_invalid(self):
        variants = (
            ("gate3_decision_id", "gate-decision-old"),
            ("rule_ids", ["rule-missing"]),
        )
        for field, value in variants:
            with self.subTest(field=field):
                self.documents = valid_documents()
                self._refresh_recorded_hash()
                self.documents["gate-decisions.yml"]["materializations"][0][field] = value
                self.write_documents()
                self.assertEqual("invalid", self.inspect()["activation_state"])

    def test_duplicate_exact_materializations_are_ambiguous(self):
        duplicate = copy.deepcopy(
            self.documents["gate-decisions.yml"]["materializations"][0]
        )
        duplicate["materialization_id"] = "materialization-002"
        self.documents["gate-decisions.yml"]["materializations"].append(duplicate)
        self.write_documents()
        self.assert_fixture_valid()
        report = self.inspect()
        self.assertEqual("invalid", report["activation_state"])
        self.assertIn(
            "AMBIGUOUS_COMPLETED_MATERIALIZATION",
            {item["code"] for item in report["blockers"]},
        )

    def test_unknown_candidate_and_unsafe_path_fail_closed(self):
        with self.assertRaises(StateInspectionError) as caught:
            inspect_distillation_state(
                self.root, "candidate-missing", FIXTURE_CANDIDATE_PATH
            )
        self.assertEqual("CANDIDATE_SELECTION_ERROR", caught.exception.code)

        with self.assertRaises(CandidateTreeError):
            inspect_distillation_state(
                self.root, "candidate-001", "../review-book-task"
            )

    def test_candidate_path_must_end_with_candidate_name(self):
        wrong = self.root / "candidates" / "different-name"
        wrong.mkdir()
        (wrong / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
        with self.assertRaises(StateInspectionError) as caught:
            inspect_distillation_state(
                self.root, "candidate-001", "candidates/different-name"
            )
        self.assertEqual("CANDIDATE_PATH_NAME_MISMATCH", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
