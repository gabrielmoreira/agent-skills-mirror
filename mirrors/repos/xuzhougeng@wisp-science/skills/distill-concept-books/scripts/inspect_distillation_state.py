#!/usr/bin/env python3
"""Inspect Gate 3/materialization routing without modifying a distillation.

The result is deliberately narrow.  It reports whether a review candidate is
review-only, requires materialization, or is structurally eligible to enter
Gate 4.  It does not assess knowledge truth, copyright permission, or behavior
effectiveness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

# Importing sibling helpers must not create bytecode inside a materialized tree.
sys.dont_write_bytecode = True

from hash_candidate_tree import (  # noqa: E402
    CandidateTreeError,
    candidate_tree_sha256,
    canonical_candidate_path,
)
from validate_distillation import (  # noqa: E402
    APPROVAL_SNAPSHOT_GOVERNANCE_FILES,
    DistillationInputError,
    GATE3_APPROVAL_SNAPSHOT_CONTRACT,
    REQUIRED_FILES,
    distillation_read_snapshot,
    snapshot_validation_inputs,
    validate_distillation,
)
from task_contracts import inspect_task_governance  # noqa: E402

try:
    import yaml
except ImportError as exc:  # pragma: no cover - minimal runtimes only
    raise SystemExit(
        "PyYAML is required to inspect governance YAML. "
        "Do not install it without the user's approval."
    ) from exc


APPROVED_RULE_DECISIONS = {"accepted", "revised"}


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(self, node, deep=False):  # type: ignore[override]
        self.flatten_mapping(node)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable mapping key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


class StateInspectionError(RuntimeError):
    """Raised when the requested candidate cannot be selected safely."""

    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise StateInspectionError("MISSING_FILE", str(path), "required YAML file is missing")
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeySafeLoader)
    except (OSError, UnicodeError) as exc:
        raise StateInspectionError("READ_ERROR", str(path), str(exc)) from exc
    except (yaml.YAMLError, RecursionError) as exc:
        raise StateInspectionError("YAML_PARSE", str(path), str(exc)) from exc
    if not isinstance(value, dict):
        raise StateInspectionError("ROOT_TYPE", str(path), "YAML root must be a mapping")
    return value


def _snapshot_digests(
    root: Path, sources_manifest: Path | str | None
) -> dict[str, str]:
    """Hash all files whose bytes can affect routing or validation."""
    paths = [root / name for name in REQUIRED_FILES]
    overlay = root / "correction-overlay.yml"
    if overlay.exists() or overlay.is_symlink():
        paths.append(overlay)
    if sources_manifest is not None:
        paths.append(Path(sources_manifest))
    for path in sorted(root.glob("task-contract*.yml")):
        paths.append(path)
    for name in ("task-coverage.yml", "context-checkpoint.yml"):
        path = root / name
        if path.exists() or path.is_symlink():
            paths.append(path)
    result: dict[str, str] = {}
    for path in paths:
        try:
            if path.is_symlink():
                raise StateInspectionError(
                    "GOVERNANCE_FILE_SYMLINK",
                    str(path),
                    "governance and manifest files must not be symlinks",
                )
            data = path.read_bytes()
        except StateInspectionError:
            raise
        except OSError as exc:
            raise StateInspectionError("READ_ERROR", str(path), str(exc)) from exc
        result[str(path.resolve())] = hashlib.sha256(data).hexdigest()
    return result


def _is_unique_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
        and len(value) == len(set(value))
    )


def _records(document: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _approved_rule_ids(decision: Mapping[str, Any] | None) -> list[str]:
    if decision is None:
        return []
    result: list[str] = []
    for item in _records(decision, "rule_decisions"):
        rule_id = item.get("rule_id")
        if item.get("decision") in APPROVED_RULE_DECISIONS and isinstance(rule_id, str):
            result.append(rule_id)
    return result


def _approval_snapshot_summary(
    decision: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Return only bounded scalar snapshot fields safe for deterministic JSON."""
    if decision is None:
        return None
    snapshot = decision.get("approval_snapshot")
    if not isinstance(snapshot, dict):
        return {
            "present": False,
            "contract": None,
            "candidate_path": None,
            "candidate_hash": None,
            "governance_hashes": {
                filename: None for filename in APPROVAL_SNAPSHOT_GOVERNANCE_FILES
            },
        }
    governance = snapshot.get("governance_hashes")
    return {
        "present": True,
        "contract": (
            snapshot.get("contract")
            if isinstance(snapshot.get("contract"), str)
            else None
        ),
        "candidate_path": (
            snapshot.get("candidate_path")
            if isinstance(snapshot.get("candidate_path"), str)
            else None
        ),
        "candidate_hash": (
            snapshot.get("candidate_hash")
            if isinstance(snapshot.get("candidate_hash"), str)
            else None
        ),
        "governance_hashes": {
            filename: (
                governance.get(filename)
                if isinstance(governance, dict)
                and isinstance(governance.get(filename), str)
                else None
            )
            for filename in APPROVAL_SNAPSHOT_GOVERNANCE_FILES
        },
        "current_gate1_decision_id": snapshot.get("current_gate1_decision_id"),
        "task_contract": snapshot.get("task_contract"),
        "task_coverage": snapshot.get("task_coverage"),
        "candidate_stable_task_ids": snapshot.get("candidate_stable_task_ids"),
    }


def _current_decisions(
    decisions: Sequence[Mapping[str, Any]], gate: str, candidate_id: str
) -> list[Mapping[str, Any]]:
    return [
        item
        for item in decisions
        if item.get("gate") == gate
        and item.get("candidate_id") == candidate_id
        and item.get("is_current") is True
    ]


def _materialization_mismatch_reasons(
    record: Mapping[str, Any],
    *,
    candidate_id: str,
    candidate_path: str | None,
    candidate_hash: str | None,
    gate3_decision_id: str | None,
    approved_rule_ids: Sequence[str],
) -> list[str]:
    reasons: list[str] = []
    if record.get("candidate_id") != candidate_id:
        reasons.append("candidate-id-mismatch")
    if record.get("gate3_decision_id") != gate3_decision_id:
        reasons.append("gate3-decision-mismatch")
    if record.get("candidate_path") != candidate_path:
        reasons.append("candidate-path-mismatch")
    if candidate_hash is None or record.get("candidate_hash") != candidate_hash:
        reasons.append("candidate-hash-mismatch")
    rule_ids = record.get("rule_ids")
    if (
        not _is_unique_string_list(rule_ids)
        or set(rule_ids) != set(approved_rule_ids)
    ):
        reasons.append("approved-rule-set-mismatch")
    quick_validation = record.get("quick_validation")
    if (
        not isinstance(quick_validation, dict)
        or quick_validation.get("status") != "pass"
        or quick_validation.get("candidate_hash") != candidate_hash
    ):
        reasons.append("quick-validation-not-pass")
    return reasons


def _inspect_distillation_snapshot(
    distillation_dir: Path | str,
    candidate_id: str,
    candidate_path: str,
    sources_manifest: Path | str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, read-only activation-state report."""
    root = Path(distillation_dir)
    canonical_path = canonical_candidate_path(candidate_path)
    snapshot_before = _snapshot_digests(root, sources_manifest)

    capability_document = _load_yaml(root / "capability-rules.yml")
    gate_document = _load_yaml(root / "gate-decisions.yml")
    eval_document = _load_yaml(root / "eval-runs.yml")

    candidates = [
        item
        for item in _records(capability_document, "skill_candidates")
        if item.get("candidate_id") == candidate_id
    ]
    if len(candidates) != 1:
        raise StateInspectionError(
            "CANDIDATE_SELECTION_ERROR",
            "capability-rules.yml.skill_candidates",
            f"candidate_id {candidate_id!r} must select exactly one candidate; found {len(candidates)}",
        )
    candidate = candidates[0]
    candidate_name = candidate.get("name")
    if not isinstance(candidate_name, str) or PurePosixPath(canonical_path).name != candidate_name:
        raise StateInspectionError(
            "CANDIDATE_PATH_NAME_MISMATCH",
            candidate_path,
            "candidate_path final component must equal the selected candidate name",
        )

    gate_decisions = _records(gate_document, "gate_decisions")
    gate3_current = _current_decisions(gate_decisions, "gate-3", candidate_id)
    gate4_current = _current_decisions(gate_decisions, "gate-4", candidate_id)
    current_gate3 = gate3_current[0] if len(gate3_current) == 1 else None
    current_gate4 = gate4_current[0] if len(gate4_current) == 1 else None
    gate3_approved = (
        current_gate3 is not None
        and current_gate3.get("decision") == "approved-for-eval"
    )
    approval_snapshot = _approval_snapshot_summary(current_gate3)
    approval_candidate_path = (
        approval_snapshot.get("candidate_path")
        if isinstance(approval_snapshot, dict)
        else None
    )
    approval_candidate_hash = (
        approval_snapshot.get("candidate_hash")
        if isinstance(approval_snapshot, dict)
        else None
    )
    approval_snapshot_shape_present = bool(
        isinstance(approval_snapshot, dict)
        and approval_snapshot.get("present") is True
        and approval_snapshot.get("contract") == GATE3_APPROVAL_SNAPSHOT_CONTRACT
    )
    approved_rule_ids = _approved_rule_ids(current_gate3) if gate3_approved else []
    gate3_id = current_gate3.get("decision_id") if current_gate3 is not None else None

    materialization_records = [
        record
        for record in _records(gate_document, "materializations")
        if record.get("candidate_id") == candidate_id
    ]
    completed_records = [
        record for record in materialization_records if record.get("status") == "completed"
    ]
    tree_issue: dict[str, str] | None = None
    try:
        computed_hash: str | None = candidate_tree_sha256(root, canonical_path)
    except CandidateTreeError as exc:
        computed_hash = None
        # Before first materialization the approved candidate directory may not
        # exist yet.  That is the materialization-required state, not corrupt
        # governance.  A missing tree claimed by a completed record is invalid.
        if (
            exc.code != "CANDIDATE_PATH_MISSING"
            or completed_records
            or gate3_approved
        ):
            tree_issue = {"code": exc.code, "path": exc.path, "message": exc.message}

    try:
        validation = validate_distillation(root, sources_manifest)
    except DistillationInputError as exc:
        raise StateInspectionError(exc.code, str(exc.path), exc.message) from exc
    except Exception as exc:  # defensive fail-closed boundary around the validator
        raise StateInspectionError(
            "VALIDATOR_INTERNAL_ERROR",
            str(root),
            f"{type(exc).__name__}: {exc}",
        ) from exc

    task_governance = inspect_task_governance(root, sources_manifest)

    verification_hash: str | None = None
    verification_tree_issue: dict[str, str] | None = None
    try:
        verification_hash = candidate_tree_sha256(root, canonical_path)
    except CandidateTreeError as exc:
        if (
            exc.code != "CANDIDATE_PATH_MISSING"
            or completed_records
            or gate3_approved
        ):
            verification_tree_issue = {
                "code": exc.code,
                "path": exc.path,
                "message": exc.message,
            }
    snapshot_after = _snapshot_digests(root, sources_manifest)
    snapshot_changed = (
        snapshot_before != snapshot_after or computed_hash != verification_hash
    )

    matching: list[str] = []
    stale: list[dict[str, Any]] = []
    historical: list[dict[str, Any]] = []
    for record in materialization_records:
        materialization_id = record.get("materialization_id")
        status = record.get("status")
        if status != "completed":
            historical.append({"materialization_id": materialization_id, "status": status})
            continue
        reasons = _materialization_mismatch_reasons(
            record,
            candidate_id=candidate_id,
            candidate_path=approval_candidate_path,
            candidate_hash=approval_candidate_hash,
            gate3_decision_id=gate3_id,
            approved_rule_ids=approved_rule_ids,
        )
        approval_matches_cli = (
            approval_snapshot_shape_present
            and approval_candidate_path == canonical_path
            and computed_hash is not None
            and approval_candidate_hash == computed_hash
        )
        if gate3_approved and approval_matches_cli and not reasons:
            matching.append(str(materialization_id))
        else:
            stale.append({
                "materialization_id": materialization_id,
                "reasons": reasons or ["no-current-approved-gate3"],
            })

    blockers = [item.as_dict() for item in validation.errors]
    if tree_issue is not None:
        blockers.append(tree_issue)
    if verification_tree_issue is not None:
        blockers.append(verification_tree_issue)
    if snapshot_changed:
        blockers.append({
            "code": "INSPECTION_SNAPSHOT_CHANGED",
            "path": str(root),
            "message": "governance files or candidate tree changed during state inspection",
        })
    if len(gate3_current) > 1:
        blockers.append({
            "code": "AMBIGUOUS_CURRENT_GATE3",
            "path": "gate-decisions.yml.gate_decisions",
            "message": "candidate has more than one current Gate 3 decision",
        })
    if len(gate4_current) > 1:
        blockers.append({
            "code": "AMBIGUOUS_CURRENT_GATE4",
            "path": "gate-decisions.yml.gate_decisions",
            "message": "candidate has more than one current Gate 4 decision",
        })
    approval_matches_cli = (
        approval_snapshot_shape_present
        and approval_candidate_path == canonical_path
        and computed_hash is not None
        and approval_candidate_hash == computed_hash
    )
    if gate3_approved and not approval_snapshot_shape_present:
        blockers.append({
            "code": "APPROVAL_SNAPSHOT_INVALID",
            "path": "gate-decisions.yml.current_gate3.approval_snapshot",
            "message": "current Gate 3 approval lacks the required versioned snapshot",
        })
    elif gate3_approved:
        if approval_candidate_path != canonical_path:
            blockers.append({
                "code": "APPROVAL_SNAPSHOT_CANDIDATE_PATH_MISMATCH",
                "path": "gate-decisions.yml.current_gate3.approval_snapshot.candidate_path",
                "message": "CLI candidate_path must exactly match the current Gate 3 approval snapshot",
            })
        if computed_hash is None or approval_candidate_hash != computed_hash:
            blockers.append({
                "code": "APPROVAL_SNAPSHOT_CANDIDATE_HASH_MISMATCH",
                "path": "gate-decisions.yml.current_gate3.approval_snapshot.candidate_hash",
                "message": "current candidate tree hash must exactly match the current Gate 3 approval snapshot",
            })
    if len(matching) > 1:
        blockers.append({
            "code": "AMBIGUOUS_COMPLETED_MATERIALIZATION",
            "path": "gate-decisions.yml.materializations",
            "message": "more than one completed materialization exactly matches the current candidate",
        })
    lifecycle = candidate.get("lifecycle")
    if gate3_approved and lifecycle != "review":
        blockers.append({
            "code": "CANDIDATE_LIFECYCLE_NOT_REVIEW",
            "path": "capability-rules.yml.skill_candidates.lifecycle",
            "message": "Gate 4 routing is allowed only while the candidate lifecycle is review",
        })
    if gate3_approved and len(matching) == 1 and sources_manifest is None:
        blockers.append({
            "code": "SOURCES_MANIFEST_REQUIRED_FOR_GATE4",
            "path": "--sources-manifest",
            "message": "Gate 4 eligibility requires explicit source-manifest validation",
        })

    task_blocker_codes = {
        "TASK_CONTRACT_MISSING", "TASK_CONTRACT_INVALID",
        "TASK_CONTRACT_SNAPSHOT_MISMATCH", "TASK_COVERAGE_INVALID",
        "STABLE_TASK_UNKNOWN", "STABLE_TASK_UNCOVERED",
        "CANDIDATE_TASK_MISMATCH", "GATE3_TASK_CONTRACT_MISMATCH",
        "METHOD_TRANSFER_PROVENANCE_REQUIRED",
        "METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED",
        "LEGACY_TASK_CONTRACT_REVIEW_REQUIRED",
        "CHECKPOINT_PRODUCT_CONTRACT_CONFLICT",
    }
    task_repair_required = any(
        item.get("code") in task_blocker_codes for item in blockers
    )
    if blockers:
        activation_state = "invalid"
        allowed_actions = (
            ["review", "repair-task-contract-or-coverage"]
            if task_repair_required
            else ["repair-governance-or-candidate-state"]
        )
    elif not gate3_approved:
        activation_state = "review-only"
        allowed_actions = ["review", "authorized-candidate-maintenance"]
    elif not matching:
        activation_state = "materialization-required"
        allowed_actions = ["materialize", "quick-validate", "record-materialization"]
    else:
        activation_state = "gate4-eligible"
        allowed_actions = ["authorized-gate4-evaluation"]

    matching_id = matching[0] if len(matching) == 1 else None
    completed_pass_evals = 0
    if matching_id is not None:
        completed_pass_evals = sum(
            1
            for run in _records(eval_document, "eval_runs")
            if run.get("candidate_id") == candidate_id
            and run.get("materialization_id") == matching_id
            and run.get("status") == "completed"
            and run.get("outcome") == "pass"
        )

    return {
        "inspection_scope": "gate3-materialization-routing-only",
        "truth_assessed": False,
        "behavior_effectiveness_assessed": False,
        "activation_state": activation_state,
        "continuation_mode": (
            "review-repair-only" if task_repair_required else activation_state
        ),
        "allowed_actions": allowed_actions,
        "blockers": blockers,
        "candidate": {
            "candidate_id": candidate_id,
            "name": candidate_name,
            "lifecycle": lifecycle,
            "candidate_path": canonical_path,
            "computed_hash": computed_hash,
            "tree_status": "present" if computed_hash is not None else "not-yet-materialized",
        },
        "current_gate3": (
            None
            if current_gate3 is None
            else {
                "decision_id": current_gate3.get("decision_id"),
                "decision": current_gate3.get("decision"),
                "approved_rule_ids": approved_rule_ids,
                "approval_snapshot": approval_snapshot,
                "approval_snapshot_matches_candidate": approval_matches_cli,
            }
        ),
        "current_gate4": (
            None
            if current_gate4 is None
            else {
                "decision_id": current_gate4.get("decision_id"),
                "decision": current_gate4.get("decision"),
            }
        ),
        "gate4_accepted": (
            current_gate4 is not None and current_gate4.get("decision") == "accepted"
        ),
        "completed_pass_eval_count": completed_pass_evals,
        "materializations": {
            "matching": matching,
            "stale_completed": stale,
            "historical": historical,
        },
        "validation": {
            "ok": validation.ok,
            "error_count": len(validation.errors),
            "warning_count": len(validation.warnings),
            "warnings": [item.as_dict() for item in validation.warnings],
            "metrics": validation.metrics,
            "sources_manifest_provided": sources_manifest is not None,
        },
        "authoritative_product_contract": task_governance.summary,
        "current_stage_objective": task_governance.summary.get(
            "current_stage_objective"
        ),
        "temporary_operational_constraints": task_governance.summary.get(
            "temporary_operational_constraints", []
        ),
    }


def _candidate_tree_observation(
    root: Path, candidate_path: str
) -> tuple[str | None, tuple[str, str, str] | None]:
    try:
        return candidate_tree_sha256(root, candidate_path), None
    except CandidateTreeError as exc:
        return None, (exc.code, exc.path, exc.message)


def inspect_distillation_state(
    distillation_dir: Path | str,
    candidate_id: str,
    candidate_path: str,
    sources_manifest: Path | str | None = None,
) -> dict[str, Any]:
    """Inspect routing from one shared immutable distillation byte snapshot."""
    root = Path(distillation_dir)
    canonical_path = canonical_candidate_path(candidate_path)
    outer_before = _snapshot_digests(root, sources_manifest)
    candidate_before = _candidate_tree_observation(root, canonical_path)

    try:
        with distillation_read_snapshot(root) as snapshot_root:
            snapshot_manifest = snapshot_validation_inputs(
                snapshot_root, sources_manifest
            )
            report = _inspect_distillation_snapshot(
                snapshot_root,
                candidate_id,
                canonical_path,
                snapshot_manifest,
            )
    except DistillationInputError as exc:
        raise StateInspectionError(exc.code, str(exc.path), exc.message) from exc

    outer_after = _snapshot_digests(root, sources_manifest)
    candidate_after = _candidate_tree_observation(root, canonical_path)
    if outer_before != outer_after or candidate_before != candidate_after:
        blocker = {
            "code": "INSPECTION_SNAPSHOT_CHANGED",
            "path": str(root),
            "message": "source governance files or candidate tree changed during inspection",
        }
        report["blockers"].append(blocker)
        report["activation_state"] = "invalid"
        report["continuation_mode"] = "invalid"
        report["allowed_actions"] = ["repair-governance-or-candidate-state"]
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect one review candidate's Gate 3/materialization routing state."
    )
    parser.add_argument("distillation_dir", help="Owning distillation directory")
    parser.add_argument("--candidate-id", required=True, help="Stable skill candidate ID")
    parser.add_argument(
        "--candidate-path",
        required=True,
        help="Canonical candidate path relative to the distillation directory",
    )
    parser.add_argument(
        "--sources-manifest",
        help="Manifest passed to validation; required before reporting Gate 4 eligibility",
    )
    args = parser.parse_args(argv)
    try:
        report = inspect_distillation_state(
            args.distillation_dir,
            args.candidate_id,
            args.candidate_path,
            args.sources_manifest,
        )
    except (StateInspectionError, CandidateTreeError) as exc:
        result = {
            "inspection_scope": "gate3-materialization-routing-only",
            "truth_assessed": False,
            "behavior_effectiveness_assessed": False,
            "activation_state": "invalid",
            "input_error": {
                "code": exc.code,
                "path": exc.path,
                "message": exc.message,
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["activation_state"] == "invalid" else 0


if __name__ == "__main__":
    sys.exit(main())
