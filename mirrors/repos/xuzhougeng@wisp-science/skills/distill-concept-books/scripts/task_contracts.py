#!/usr/bin/env python3
"""Deterministic product-task contract and drift checks.

This module deliberately checks explicit IDs, mappings, and byte hashes.  It
does not attempt fuzzy or LLM-based semantic comparison.  Remaining semantic
conflicts belong in the human Gate review package.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required; do not install it without approval.") from exc


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
FULL_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
GATE1_TASK_CONTRACT = "gate1-task-contract-snapshot:v1"
GATE3_TASK_CONTRACT = "gate3-approval-snapshot:v2"
GATE3_LEGACY_CONTRACT = "gate3-approval-snapshot:v1"
TASK_MODES = {"source-contained", "method-transfer"}
TASK_STATUSES = {"active", "deferred", "rejected"}
COVERAGE_STATUSES = {"covered", "deferred", "rejected"}
PROVENANCE_LAYERS = {
    "method-source-evidence",
    "target-material-evidence",
    "analogy-hypothesis",
}
METHOD_RUBRIC_DIMENSIONS = {
    "provenance-layer-separation",
    "anti-forced-analogy",
}
METHOD_FATAL_FAILURE = "method-source-fact-as-target-fact"
UNFAMILIARITY_DIMENSIONS = {"domain", "case", "mechanism", "method"}


class _UniqueKeySafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate mapping key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class TaskIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass
class TaskGovernanceResult:
    summary: dict[str, Any] = field(default_factory=dict)
    errors: list[TaskIssue] = field(default_factory=list)
    warnings: list[TaskIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, code: str, path: str, message: str) -> None:
        self.errors.append(TaskIssue(code, path, message))

    def warning(self, code: str, path: str, message: str) -> None:
        self.warnings.append(TaskIssue(code, path, message))


def _load_yaml(path: Path) -> Mapping[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeySafeLoader)
    if not isinstance(value, dict):
        raise ValueError("YAML root must be a mapping")
    return value


def _load_json(path: Path) -> Mapping[str, Any]:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-JSON numeric constant {value!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _records(document: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _strings(value: Any, *, nonempty: bool = False) -> list[str] | None:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item or item != item.strip() for item in value
    ):
        return None
    if len(value) != len(set(value)) or (nonempty and not value):
        return None
    return list(value)


def _id(value: Any) -> bool:
    return isinstance(value, str) and bool(ID_RE.fullmatch(value))


def _canonical_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    if "\\" in value or "\x00" in value:
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        return None
    return value


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _contract_path_version(relative: str) -> int | None:
    if relative == "task-contract.yml":
        return 1
    match = re.fullmatch(r"task-contract\.v([2-9][0-9]*)\.yml", relative)
    return int(match.group(1)) if match is not None else None


def _current_decisions(
    decisions: Sequence[Mapping[str, Any]], gate: str, candidate_id: str | None
) -> list[Mapping[str, Any]]:
    return [
        item
        for item in decisions
        if item.get("gate") == gate
        and item.get("candidate_id") == candidate_id
        and item.get("is_current") is True
    ]


def _validate_contract(
    result: TaskGovernanceResult,
    contract: Mapping[str, Any],
    *,
    expected_distillation_id: Any,
) -> tuple[
    dict[str, Mapping[str, Any]],
    list[str],
    dict[str, dict[str, str]],
    dict[str, str],
]:
    path = "task-contract"
    if contract.get("schema_version") != 1 or isinstance(
        contract.get("schema_version"), bool
    ):
        result.error("TASK_CONTRACT_INVALID", f"{path}.schema_version", "must be integer 1")
    if contract.get("distillation_id") != expected_distillation_id:
        result.error(
            "TASK_CONTRACT_INVALID",
            f"{path}.distillation_id",
            "must match the governance distillation_id",
        )
    for field_name in ("task_contract_id", "product_goal"):
        if not _id(contract.get(field_name)) if field_name.endswith("_id") else not isinstance(contract.get(field_name), str) or not contract.get(field_name).strip():
            result.error("TASK_CONTRACT_INVALID", f"{path}.{field_name}", "must be non-empty")
    version = contract.get("contract_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        result.error("TASK_CONTRACT_INVALID", f"{path}.contract_version", "must be a positive integer")
    if contract.get("status") not in {"draft", "frozen"}:
        result.error("TASK_CONTRACT_INVALID", f"{path}.status", "must be draft or frozen")
    if _strings(contract.get("audience"), nonempty=True) is None:
        result.error("TASK_CONTRACT_INVALID", f"{path}.audience", "must be a unique non-empty string list")

    input_types: dict[str, str] = {}
    for index, record in enumerate(_records(contract, "input_types")):
        item_path = f"{path}.input_types[{index}]"
        input_id = record.get("input_type_id")
        if not _id(input_id) or input_id in input_types:
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.input_type_id", "must be a unique stable ID")
            continue
        description = record.get("description")
        if not isinstance(description, str) or not description.strip():
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.description", "must be non-empty")
        input_types[input_id] = str(record.get("provenance_role") or "")
    if not input_types:
        result.error("TASK_CONTRACT_INVALID", f"{path}.input_types", "at least one input type is required")

    capability = contract.get("execution_capability")
    if capability is not None:
        cap_path = f"{path}.execution_capability"
        if not isinstance(capability, dict):
            result.error("TASK_CONTRACT_INVALID", cap_path, "must be a mapping when present")
        else:
            input_handling = capability.get("input_handling")
            if not isinstance(input_handling, list) or not input_handling:
                result.error(
                    "TASK_CONTRACT_INVALID",
                    f"{cap_path}.input_handling",
                    "execution_capability requires a non-empty input_handling list when declared",
                )
            else:
                for cap_index, cap_record in enumerate(input_handling):
                    item_path = f"{cap_path}.input_handling[{cap_index}]"
                    if not isinstance(cap_record, dict):
                        result.error("TASK_CONTRACT_INVALID", item_path, "must be a mapping")
                        continue
                    input_id = cap_record.get("input_type_id")
                    if not _id(input_id) or input_id not in input_types:
                        result.error(
                            "TASK_CONTRACT_INVALID",
                            f"{item_path}.input_type_id",
                            "must reference a declared input type",
                        )
                    for field_name in ("carrier", "modality_strategy", "degradation_rule"):
                        value = cap_record.get(field_name)
                        if not isinstance(value, str) or not value.strip():
                            result.error(
                                "TASK_CONTRACT_INVALID",
                                f"{item_path}.{field_name}",
                                "must be a non-empty string",
                            )
                    modality = cap_record.get("modality_strategy")
                    if isinstance(modality, str) and modality not in {
                        "unimodal-text",
                        "multimodal-text-image",
                    }:
                        result.error(
                            "TASK_CONTRACT_INVALID",
                            f"{item_path}.modality_strategy",
                            "must be unimodal-text or multimodal-text-image",
                        )
            notes = capability.get("notes")
            if notes is not None and (not isinstance(notes, str) or not notes.strip()):
                result.error(
                    "TASK_CONTRACT_INVALID",
                    f"{cap_path}.notes",
                    "must be a non-empty string when present",
                )

    acceptance_questions: dict[str, str] = {}
    for index, record in enumerate(_records(contract, "acceptance_questions")):
        item_path = f"{path}.acceptance_questions[{index}]"
        question_id = record.get("acceptance_question_id")
        if not _id(question_id) or question_id in acceptance_questions:
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.acceptance_question_id", "must be a unique stable ID")
            continue
        question = record.get("question")
        if not isinstance(question, str) or not question.strip():
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.question", "must be non-empty")
        acceptance_questions[question_id] = str(question or "")

    tasks: dict[str, Mapping[str, Any]] = {}
    active: list[str] = []
    example_index: dict[str, dict[str, str]] = {}
    for index, record in enumerate(_records(contract, "stable_tasks")):
        item_path = f"{path}.stable_tasks[{index}]"
        task_id = record.get("stable_task_id")
        if not _id(task_id) or task_id in tasks:
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.stable_task_id", "must be a unique stable ID")
            continue
        tasks[task_id] = record
        if record.get("task_mode") not in TASK_MODES:
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.task_mode", "unsupported task mode")
        status = record.get("status")
        if status not in TASK_STATUSES:
            result.error("TASK_CONTRACT_INVALID", f"{item_path}.status", "unsupported task status")
        elif status == "active":
            active.append(task_id)
        for field_name in ("statement",):
            if not isinstance(record.get(field_name), str) or not record[field_name].strip():
                result.error("TASK_CONTRACT_INVALID", f"{item_path}.{field_name}", "must be non-empty")
        for field_name in (
            "required_input_types",
            "required_outputs",
            "non_negotiable_constraints",
            "acceptance_question_ids",
        ):
            values = _strings(record.get(field_name), nonempty=True)
            if values is None:
                result.error("TASK_CONTRACT_INVALID", f"{item_path}.{field_name}", "must be a unique non-empty string list")
                continue
            if field_name == "required_input_types":
                for value in values:
                    if value not in input_types:
                        result.error("TASK_CONTRACT_INVALID", f"{item_path}.{field_name}", f"unknown input type {value!r}")
            if field_name == "acceptance_question_ids":
                for value in values:
                    if value not in acceptance_questions:
                        result.error("TASK_CONTRACT_INVALID", f"{item_path}.{field_name}", f"unknown acceptance question {value!r}")
        for examples_key, polarity in (("positive_examples", "positive"), ("negative_examples", "negative")):
            examples = _records(record, examples_key)
            if not examples:
                result.error("TASK_CONTRACT_INVALID", f"{item_path}.{examples_key}", "at least one stable example is required")
            for example_number, example in enumerate(examples):
                example_path = f"{item_path}.{examples_key}[{example_number}]"
                example_id = example.get("example_id")
                if not _id(example_id) or example_id in example_index:
                    result.error("TASK_CONTRACT_INVALID", f"{example_path}.example_id", "must be globally unique")
                    continue
                if example.get("input_type_id") not in input_types:
                    result.error("TASK_CONTRACT_INVALID", f"{example_path}.input_type_id", "must reference an input type")
                if not isinstance(example.get("statement"), str) or not example["statement"].strip():
                    result.error("TASK_CONTRACT_INVALID", f"{example_path}.statement", "must be non-empty")
                example_index[example_id] = {
                    "polarity": polarity,
                    "stable_task_id": task_id,
                    "input_type_id": str(example.get("input_type_id") or ""),
                }
        provenance = record.get("provenance_requirements")
        if not isinstance(provenance, dict):
            result.error(
                "TASK_CONTRACT_INVALID",
                f"{item_path}.provenance_requirements",
                "every stable task requires a structured provenance contract",
            )
        else:
            layers = _strings(provenance.get("required_output_layers"), nonempty=True)
            if layers is None:
                result.error(
                    "TASK_CONTRACT_INVALID",
                    f"{item_path}.provenance_requirements.required_output_layers",
                    "must be a unique non-empty stable layer list",
                )
            if provenance.get("missing_target_evidence") not in {
                "stop", "lower-conclusion-strength"
            }:
                result.error(
                    "TASK_CONTRACT_INVALID",
                    f"{item_path}.provenance_requirements.missing_target_evidence",
                    "must stop or lower conclusion strength",
                )
            forbidden = _strings(provenance.get("forbidden_transfers"))
            if forbidden is None:
                result.error(
                    "TASK_CONTRACT_INVALID",
                    f"{item_path}.provenance_requirements.forbidden_transfers",
                    "must be a unique stable ID list",
                )
            if record.get("task_mode") == "method-transfer":
                layers = _strings(provenance.get("required_output_layers"), nonempty=True)
                if layers is None or set(layers) != PROVENANCE_LAYERS:
                    result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"{item_path}.provenance_requirements.required_output_layers", "must contain exactly the three provenance layers")
                if provenance.get("target_source_role") != "target-material":
                    result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"{item_path}.provenance_requirements.target_source_role", "must be target-material")
                if provenance.get("missing_target_evidence") not in {"stop", "lower-conclusion-strength"}:
                    result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"{item_path}.provenance_requirements.missing_target_evidence", "must stop or lower conclusion strength")
                forbidden = _strings(provenance.get("forbidden_transfers"), nonempty=True)
                if forbidden is None or METHOD_FATAL_FAILURE not in forbidden:
                    result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"{item_path}.provenance_requirements.forbidden_transfers", f"must include {METHOD_FATAL_FAILURE}")
    if not tasks:
        result.error("TASK_CONTRACT_INVALID", f"{path}.stable_tasks", "at least one stable task is required")
    exclusions: set[str] = set()
    for index, record in enumerate(_records(contract, "exclusions")):
        item_path = f"{path}.exclusions[{index}]"
        exclusion_id = record.get("exclusion_id")
        if not _id(exclusion_id) or exclusion_id in exclusions:
            result.error(
                "TASK_CONTRACT_INVALID",
                f"{item_path}.exclusion_id",
                "must be a unique stable ID",
            )
            continue
        exclusions.add(exclusion_id)
        if not isinstance(record.get("statement"), str) or not record["statement"].strip():
            result.error(
                "TASK_CONTRACT_INVALID",
                f"{item_path}.statement",
                "must be non-empty",
            )
    if not exclusions:
        result.error(
            "TASK_CONTRACT_INVALID",
            f"{path}.exclusions",
            "at least one explicit exclusion is required",
        )
    return tasks, active, example_index, input_types


def inspect_task_governance(
    root: Path | str,
    sources_manifest: Path | str | None = None,
) -> TaskGovernanceResult:
    root = Path(root)
    result = TaskGovernanceResult(summary={
        "status": "unknown",
        "task_contract_path": None,
        "task_contract_hash": None,
        "task_contract_id": None,
        "contract_version": None,
        "current_gate1_decision_id": None,
        "active_stable_task_ids": [],
        "covered_stable_task_ids": [],
        "uncovered_stable_task_ids": [],
        "deferred_stable_task_ids": [],
        "rejected_stable_task_ids": [],
        "candidate_stable_task_ids": {},
        "task_contract_drift": "unknown",
        "gate3_contract_binding": "not-applicable",
        "legacy_contract_review_required": False,
        "current_stage_objective": None,
        "temporary_operational_constraints": [],
    })
    try:
        capability = _load_yaml(root / "capability-rules.yml")
        gates = _load_yaml(root / "gate-decisions.yml")
        evidence = _load_yaml(root / "evidence-ledger.yml")
        eval_runs_document = _load_yaml(root / "eval-runs.yml")
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        result.error("TASK_CONTRACT_INVALID", str(root), f"cannot load governing files: {exc}")
        result.summary["status"] = "invalid"
        return result
    decisions = _records(gates, "gate_decisions")

    # Every previously Gate-1-bound contract is an immutable audit anchor.
    # A newer current Gate 1 selects the current contract but never permits an
    # older versioned file to disappear or drift.
    historical_contract_paths: dict[int, str] = {}
    for index, decision in enumerate(decisions):
        if decision.get("gate") != "gate-1":
            continue
        historical_snapshot = decision.get("task_contract_snapshot")
        if not isinstance(historical_snapshot, dict):
            continue
        snapshot_path = _canonical_relative_path(
            historical_snapshot.get("task_contract_path")
        )
        version = _contract_path_version(snapshot_path) if snapshot_path else None
        item_path = f"gate-decisions.yml.gate_decisions[{index}].task_contract_snapshot"
        if (
            historical_snapshot.get("contract") != GATE1_TASK_CONTRACT
            or snapshot_path is None
            or version is None
            or historical_snapshot.get("contract_version") != version
        ):
            result.error(
                "TASK_CONTRACT_SNAPSHOT_MISMATCH",
                item_path,
                "every versioned Gate 1 snapshot must use the canonical filename/version contract",
            )
            continue
        prior_path = historical_contract_paths.get(version)
        if prior_path is not None and prior_path != snapshot_path:
            result.error(
                "TASK_CONTRACT_SNAPSHOT_MISMATCH",
                item_path,
                f"contract version {version} is already bound to {prior_path!r}",
            )
        historical_contract_paths[version] = snapshot_path
        historical_file = root.joinpath(*PurePosixPath(snapshot_path).parts)
        if not historical_file.is_file() or historical_file.is_symlink():
            result.error(
                "TASK_CONTRACT_MISSING",
                snapshot_path,
                "a Gate-1-bound historical task contract must be retained as an ordinary file",
            )
            continue
        try:
            historical_document = _load_yaml(historical_file)
            historical_hash = _sha256(historical_file)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            result.error("TASK_CONTRACT_INVALID", snapshot_path, str(exc))
            continue
        if (
            historical_snapshot.get("task_contract_hash") != historical_hash
            or historical_snapshot.get("task_contract_id")
            != historical_document.get("task_contract_id")
            or historical_snapshot.get("contract_version")
            != historical_document.get("contract_version")
        ):
            result.error(
                "TASK_CONTRACT_SNAPSHOT_MISMATCH",
                item_path,
                "historical contract bytes/identity no longer match the Gate 1 snapshot",
            )

    current_gate1 = _current_decisions(decisions, "gate-1", None)
    gate1 = current_gate1[0] if len(current_gate1) == 1 else None
    if gate1 is not None:
        result.summary["current_gate1_decision_id"] = gate1.get("decision_id")
    snapshot = gate1.get("task_contract_snapshot") if isinstance(gate1, dict) else None
    positive_gate1 = gate1 is not None and gate1.get("decision") in {"approved", "approved-with-conditions"}
    if not isinstance(snapshot, dict):
        if positive_gate1:
            result.error("LEGACY_TASK_CONTRACT_REVIEW_REQUIRED", "gate-decisions.yml.current_gate1.task_contract_snapshot", "current positive Gate 1 predates the task-contract snapshot")
            result.summary["legacy_contract_review_required"] = True
            result.summary["task_contract_drift"] = "legacy-missing"
            result.summary["status"] = "legacy-contract-review-required"
        else:
            result.error("TASK_CONTRACT_MISSING", "task-contract.yml", "a task contract is required before Gate 1 approval")
            result.summary["task_contract_drift"] = "missing"
            result.summary["status"] = "missing"
        return result
    if snapshot.get("contract") != GATE1_TASK_CONTRACT:
        result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", "gate-decisions.yml.current_gate1.task_contract_snapshot.contract", f"must be {GATE1_TASK_CONTRACT}")
    relative = _canonical_relative_path(snapshot.get("task_contract_path"))
    if relative is None or _contract_path_version(relative) is None:
        result.error("TASK_CONTRACT_INVALID", "gate-decisions.yml.current_gate1.task_contract_snapshot.task_contract_path", "must be task-contract.yml or task-contract.vN.yml")
        result.summary["status"] = "invalid"
        return result
    contract_path = root.joinpath(*PurePosixPath(relative).parts)
    result.summary["task_contract_path"] = relative
    if not contract_path.is_file() or contract_path.is_symlink():
        result.error("TASK_CONTRACT_MISSING", relative, "bound task contract is missing or unsafe")
        result.summary["task_contract_drift"] = "missing"
        result.summary["status"] = "invalid"
        return result
    try:
        contract = _load_yaml(contract_path)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        result.error("TASK_CONTRACT_INVALID", relative, str(exc))
        result.summary["status"] = "invalid"
        return result
    contract_hash = _sha256(contract_path)
    result.summary.update({
        "task_contract_hash": contract_hash,
        "task_contract_id": contract.get("task_contract_id"),
        "contract_version": contract.get("contract_version"),
    })
    if snapshot.get("task_contract_hash") != contract_hash:
        result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", f"{relative}.sha256", "contract bytes no longer match Gate 1")
    for key in ("task_contract_id", "contract_version"):
        if snapshot.get(key) != contract.get(key):
            result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", f"gate-decisions.yml.current_gate1.task_contract_snapshot.{key}", "does not match the bound contract")
    if contract.get("contract_version") != _contract_path_version(relative):
        result.error(
            "TASK_CONTRACT_INVALID",
            f"{relative}.contract_version",
            "contract_version must match task-contract.yml/vN filename",
        )
    tasks, active, example_index, input_types = _validate_contract(
        result, contract, expected_distillation_id=capability.get("distillation_id")
    )
    result.summary["active_stable_task_ids"] = active
    if snapshot.get("active_stable_task_ids") != active:
        result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", "gate-decisions.yml.current_gate1.task_contract_snapshot.active_stable_task_ids", "must exactly follow active tasks in contract order")
    if positive_gate1 and contract.get("status") != "frozen":
        result.error("TASK_CONTRACT_INVALID", f"{relative}.status", "a positive Gate 1 may bind only a frozen contract")
    task_decisions = _records(gate1, "stable_task_decisions") if gate1 else []
    decision_map = {item.get("stable_task_id"): item for item in task_decisions if _id(item.get("stable_task_id"))}
    if positive_gate1 and (
        set(decision_map) != set(tasks)
        or len(task_decisions) != len(tasks)
        or len(decision_map) != len(task_decisions)
    ):
        result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", "gate-decisions.yml.current_gate1.stable_task_decisions", "must decide every stable task exactly once")
    for task_id, task in tasks.items():
        decision = decision_map.get(task_id)
        if decision is not None:
            if decision.get("decision") != task.get("status"):
                result.error("TASK_CONTRACT_SNAPSHOT_MISMATCH", "gate-decisions.yml.current_gate1.stable_task_decisions", f"task {task_id!r} status does not match the contract")
            if positive_gate1 and (
                not isinstance(decision.get("rationale"), str)
                or not decision["rationale"].strip()
            ):
                result.error(
                    "TASK_CONTRACT_SNAPSHOT_MISMATCH",
                    "gate-decisions.yml.current_gate1.stable_task_decisions",
                    f"task {task_id!r} requires a non-empty human rationale",
                )

    coverage_path = root / "task-coverage.yml"
    coverage_rows: dict[str, Mapping[str, Any]] = {}
    if not coverage_path.is_file() or coverage_path.is_symlink():
        result.error("TASK_COVERAGE_INVALID", "task-coverage.yml", "task coverage is missing or unsafe")
    else:
        try:
            coverage = _load_yaml(coverage_path)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            result.error("TASK_COVERAGE_INVALID", "task-coverage.yml", str(exc))
            coverage = {}
        if coverage.get("schema_version") != 1 or coverage.get("distillation_id") != capability.get("distillation_id"):
            result.error("TASK_COVERAGE_INVALID", "task-coverage.yml", "schema_version/distillation_id mismatch")
        reference = coverage.get("task_contract")
        expected_reference = {
            "path": relative,
            "sha256": contract_hash,
            "task_contract_id": contract.get("task_contract_id"),
            "contract_version": contract.get("contract_version"),
        }
        if reference != expected_reference:
            result.error("TASK_COVERAGE_INVALID", "task-coverage.yml.task_contract", "must exactly bind the current task contract")
        for index, row in enumerate(_records(coverage, "coverage")):
            row_path = f"task-coverage.yml.coverage[{index}]"
            task_id = row.get("stable_task_id")
            if not _id(task_id) or task_id in coverage_rows or task_id not in tasks:
                result.error("TASK_COVERAGE_INVALID", f"{row_path}.stable_task_id", "must uniquely reference a contract task")
                continue
            coverage_rows[task_id] = row
            status = row.get("coverage_status")
            if status not in COVERAGE_STATUSES:
                result.error("TASK_COVERAGE_INVALID", f"{row_path}.coverage_status", "unsupported coverage status")
            task_status = tasks[task_id].get("status")
            if task_status == "active" and status != "covered":
                result.error("STABLE_TASK_UNCOVERED", row_path, "active stable task must be covered")
            if task_status in {"deferred", "rejected"}:
                if status != task_status or row.get("gate1_decision_id") != gate1.get("decision_id") or not isinstance(row.get("rationale"), str) or not row.get("rationale").strip():
                    result.error("TASK_COVERAGE_INVALID", row_path, "deferred/rejected coverage must match and cite current Gate 1")
            if status == "covered":
                for field_name in (
                    "candidate_ids", "capability_rule_ids", "trigger_case_ids",
                    "nontrigger_case_ids", "task_eval_case_ids", "holdout_case_ids",
                    "rubric_dimension_ids",
                ):
                    if _strings(row.get(field_name), nonempty=True) is None:
                        result.error("STABLE_TASK_UNCOVERED", f"{row_path}.{field_name}", "covered task requires a unique non-empty mapping")
        if set(coverage_rows) != set(tasks):
            result.error("STABLE_TASK_UNCOVERED", "task-coverage.yml.coverage", "every stable task must have exactly one row")

    candidates = _records(capability, "skill_candidates")
    rules = _records(capability, "capability_rules")
    candidate_map = {item.get("candidate_id"): item for item in candidates if _id(item.get("candidate_id"))}
    rule_map = {item.get("rule_id"): item for item in rules if _id(item.get("rule_id"))}
    result.summary["candidate_stable_task_ids"] = {
        candidate_id: candidate.get("stable_task_ids", [])
        for candidate_id, candidate in candidate_map.items()
    }
    for kind, records_map in (("candidate", candidate_map), ("rule", rule_map)):
        for record_id, record in records_map.items():
            ids = _strings(record.get("stable_task_ids"), nonempty=True)
            if ids is None:
                result.error("CANDIDATE_TASK_MISMATCH", f"capability-rules.yml.{kind}[{record_id}].stable_task_ids", "must be a unique non-empty list")
                continue
            unknown = [item for item in ids if item not in tasks or tasks[item].get("status") != "active"]
            if unknown:
                result.error("STABLE_TASK_UNKNOWN", f"capability-rules.yml.{kind}[{record_id}].stable_task_ids", f"unknown or non-active task IDs: {unknown}")

    # Load materialized v2 case metadata once.  v1 remains parseable elsewhere,
    # but cannot satisfy current task-contract eligibility.
    eval_by_candidate: dict[str, dict[str, Any]] = {}
    for candidate_id, candidate in candidate_map.items():
        current_gate3 = _current_decisions(decisions, "gate-3", candidate_id)
        gate3 = current_gate3[0] if len(current_gate3) == 1 else None
        if gate3 is None or gate3.get("decision") != "approved-for-eval":
            continue
        approval = gate3.get("approval_snapshot")
        if not isinstance(approval, dict) or approval.get("contract") == GATE3_LEGACY_CONTRACT:
            result.error("LEGACY_TASK_CONTRACT_REVIEW_REQUIRED", f"gate-decisions.yml.gate3[{candidate_id}].approval_snapshot", "current Gate 3 v1 cannot authorize new materialization or Gate 4")
            result.summary["legacy_contract_review_required"] = True
            result.summary["gate3_contract_binding"] = "legacy-contract-review-required"
            continue
        if approval.get("contract") != GATE3_TASK_CONTRACT:
            result.error("GATE3_TASK_CONTRACT_MISMATCH", f"gate-decisions.yml.gate3[{candidate_id}].approval_snapshot.contract", f"new/current approval must use {GATE3_TASK_CONTRACT}")
            continue
        expected = {
            "current_gate1_decision_id": gate1.get("decision_id") if gate1 else None,
            "task_contract": {
                "path": relative,
                "sha256": contract_hash,
                "task_contract_id": contract.get("task_contract_id"),
                "contract_version": contract.get("contract_version"),
                "active_stable_task_ids": active,
            },
            "task_coverage": {
                "path": "task-coverage.yml",
                "sha256": _sha256(coverage_path) if coverage_path.is_file() else None,
            },
            "candidate_stable_task_ids": candidate.get("stable_task_ids"),
        }
        for key, value in expected.items():
            if approval.get(key) != value:
                result.error("GATE3_TASK_CONTRACT_MISMATCH", f"gate-decisions.yml.gate3[{candidate_id}].approval_snapshot.{key}", "does not match current contract/coverage/candidate")
        result.summary["gate3_contract_binding"] = "matches" if not any(issue.code == "GATE3_TASK_CONTRACT_MISMATCH" for issue in result.errors) else "mismatch"
        candidate_path = _canonical_relative_path(approval.get("candidate_path"))
        if candidate_path is None:
            continue
        try:
            trigger = _load_json(root.joinpath(*PurePosixPath(candidate_path).parts, "evals", "trigger-cases.json"))
            task_definition = _load_json(root.joinpath(*PurePosixPath(candidate_path).parts, "evals", "task-cases.json"))
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            result.error("TASK_COVERAGE_INVALID", f"{candidate_path}/evals", f"cannot load v2 eval definitions: {exc}")
            continue
        if trigger.get("schema_version") != 2 or task_definition.get("schema_version") != 2:
            result.error("TASK_COVERAGE_INVALID", f"{candidate_path}/evals", "Gate 3 v2 requires eval definition schema_version 2")
        cases: dict[str, Mapping[str, Any]] = {}
        case_task_ids: dict[str, set[str]] = {}
        trigger_ids: set[str] = set()
        nontrigger_ids: set[str] = set()
        for key, polarity in (("should_trigger", "positive"), ("should_not_trigger", "negative")):
            for case in _records(trigger, key):
                case_id = case.get("case_id")
                case_path = f"{candidate_path}/evals/{key}[{case_id}]"
                if not _id(case_id):
                    result.error(
                        "TASK_COVERAGE_INVALID",
                        case_path,
                        "case_id must be a stable ID",
                    )
                    continue
                if case_id in cases:
                    result.error(
                        "TASK_COVERAGE_INVALID",
                        case_path,
                        "case_id must be unique across trigger and nontrigger definitions",
                    )
                    continue
                cases[case_id] = case
                (trigger_ids if polarity == "positive" else nontrigger_ids).add(case_id)
                task_ids = _strings(case.get("stable_task_ids"), nonempty=True)
                input_ids = _strings(case.get("input_type_ids"), nonempty=True)
                positive_ids = _strings(
                    case.get("positive_example_ids"),
                    nonempty=polarity == "positive",
                )
                negative_ids = _strings(
                    case.get("negative_example_ids"),
                    nonempty=polarity == "negative",
                )
                if (
                    task_ids is None
                    or input_ids is None
                    or positive_ids is None
                    or negative_ids is None
                    or (polarity == "positive" and negative_ids)
                    or (polarity == "negative" and positive_ids)
                ):
                    result.error(
                        "TASK_COVERAGE_INVALID",
                        case_path,
                        "v2 trigger/nontrigger case requires stable task/input IDs and explicit polarity-separated example IDs",
                    )
                    continue
                case_task_ids[case_id] = set(task_ids)
                unknown_tasks = [
                    item for item in task_ids
                    if item not in tasks
                    or tasks[item].get("status") != "active"
                    or item not in (candidate.get("stable_task_ids") or [])
                ]
                unknown_inputs = [item for item in input_ids if item not in input_types]
                if unknown_tasks:
                    result.error(
                        "STABLE_TASK_UNKNOWN",
                        f"{case_path}.stable_task_ids",
                        f"unknown, non-active, or candidate-unbound task IDs: {unknown_tasks}",
                    )
                if unknown_inputs:
                    result.error(
                        "TASK_COVERAGE_INVALID",
                        f"{case_path}.input_type_ids",
                        f"unknown input type IDs: {unknown_inputs}",
                    )
                selected_examples = positive_ids if polarity == "positive" else negative_ids
                for example_id in selected_examples:
                    metadata = example_index.get(example_id)
                    if (
                        metadata is None
                        or metadata["polarity"] != polarity
                        or metadata["stable_task_id"] not in task_ids
                    ):
                        result.error(
                            "CANDIDATE_TASK_MISMATCH",
                            f"{case_path}.{polarity}_example_ids",
                            f"{polarity} example {example_id!r} has the wrong stable task or polarity",
                        )
        task_cases: dict[str, Mapping[str, Any]] = {}
        for case in _records(task_definition, "tasks"):
            case_id = case.get("case_id")
            case_path = f"{candidate_path}/evals/tasks[{case_id}]"
            if not _id(case_id):
                result.error("TASK_COVERAGE_INVALID", case_path, "case_id must be a stable ID")
                continue
            if case_id in task_cases or case_id in cases:
                result.error(
                    "TASK_COVERAGE_INVALID",
                    case_path,
                    "case_id must be unique across every eval case type",
                )
                continue
            task_cases[case_id] = case
            task_ids = _strings(case.get("stable_task_ids"), nonempty=True)
            input_ids = _strings(case.get("input_type_ids"), nonempty=True)
            positive_ids = _strings(case.get("positive_example_ids"), nonempty=True)
            negative_ids = _strings(case.get("negative_example_ids"), nonempty=True)
            if (
                task_ids is None
                or input_ids is None
                or positive_ids is None
                or negative_ids is None
            ):
                result.error(
                    "TASK_COVERAGE_INVALID",
                    case_path,
                    "v2 task requires stable_task_ids, input_type_ids, and positive/negative example IDs",
                )
                continue
            case_task_ids[case_id] = set(task_ids)
            unknown_tasks = [
                item for item in task_ids
                if item not in tasks
                or tasks[item].get("status") != "active"
                or item not in (candidate.get("stable_task_ids") or [])
            ]
            unknown_inputs = [item for item in input_ids if item not in input_types]
            if unknown_tasks:
                result.error(
                    "STABLE_TASK_UNKNOWN",
                    f"{case_path}.stable_task_ids",
                    f"unknown, non-active, or candidate-unbound task IDs: {unknown_tasks}",
                )
            if unknown_inputs:
                result.error(
                    "TASK_COVERAGE_INVALID",
                    f"{case_path}.input_type_ids",
                    f"unknown input type IDs: {unknown_inputs}",
                )
            for field_name, polarity, example_ids in (
                ("positive_example_ids", "positive", positive_ids),
                ("negative_example_ids", "negative", negative_ids),
            ):
                for example_id in example_ids:
                    metadata = example_index.get(example_id)
                    if (
                        metadata is None
                        or metadata["polarity"] != polarity
                        or metadata["stable_task_id"] not in task_ids
                    ):
                        result.error(
                            "CANDIDATE_TASK_MISMATCH",
                            f"{case_path}.{field_name}",
                            f"{polarity} example {example_id!r} has the wrong stable task or polarity",
                        )
        rubric = task_definition.get("comparison_protocol", {}).get("rubric", {}) if isinstance(task_definition.get("comparison_protocol"), dict) else {}
        dimension_ids = {
            item.get("dimension_id") for item in rubric.get("dimensions", [])
            if isinstance(item, dict) and _id(item.get("dimension_id"))
        } if isinstance(rubric, dict) else set()
        fatal_ids = {
            item.get("failure_id") for item in rubric.get("fatal_failures", [])
            if isinstance(item, dict) and _id(item.get("failure_id"))
        } if isinstance(rubric, dict) else set()
        for field_name, actual_ids in (
            ("trigger_case_ids", trigger_ids),
            ("nontrigger_case_ids", nontrigger_ids),
            ("task_case_ids", set(task_cases)),
        ):
            registered = _strings(candidate.get(field_name), nonempty=True)
            if registered is None or set(registered) != actual_ids:
                result.error(
                    "CANDIDATE_TASK_MISMATCH",
                    f"capability-rules.yml.candidate[{candidate_id}].{field_name}",
                    "candidate must explicitly register the complete eval case ID set",
                )
        eval_by_candidate[candidate_id] = {
            "cases": cases, "tasks": task_cases,
            "trigger_ids": trigger_ids, "nontrigger_ids": nontrigger_ids,
            "case_task_ids": case_task_ids,
            "dimension_ids": dimension_ids, "fatal_ids": fatal_ids,
        }

    for task_id, row in coverage_rows.items():
        if row.get("coverage_status") != "covered":
            continue
        for candidate_id in row.get("candidate_ids", []):
            candidate = candidate_map.get(candidate_id)
            if candidate is None or task_id not in (candidate.get("stable_task_ids") or []):
                result.error("CANDIDATE_TASK_MISMATCH", f"task-coverage.yml[{task_id}].candidate_ids", f"candidate {candidate_id!r} does not bind task")
        for rule_id in row.get("capability_rule_ids", []):
            rule = rule_map.get(rule_id)
            if rule is None or task_id not in (rule.get("stable_task_ids") or []):
                result.error("CANDIDATE_TASK_MISMATCH", f"task-coverage.yml[{task_id}].capability_rule_ids", f"rule {rule_id!r} does not bind task")
        available = [eval_by_candidate.get(cid) for cid in row.get("candidate_ids", []) if eval_by_candidate.get(cid)]
        if not available:
            continue
        all_triggers = {cid for item in available for cid in item["trigger_ids"]}
        all_nontriggers = {cid for item in available for cid in item["nontrigger_ids"]}
        all_tasks = {cid for item in available for cid in item["tasks"]}
        all_dimensions = {did for item in available for did in item["dimension_ids"]}
        for field_name, pool in (("trigger_case_ids", all_triggers), ("nontrigger_case_ids", all_nontriggers), ("task_eval_case_ids", all_tasks), ("holdout_case_ids", all_tasks), ("rubric_dimension_ids", all_dimensions)):
            unknown = set(row.get(field_name, [])) - pool
            if unknown:
                result.error("TASK_COVERAGE_INVALID", f"task-coverage.yml[{task_id}].{field_name}", f"unknown IDs: {sorted(unknown)}")
            if field_name != "rubric_dimension_ids":
                wrong_task = {
                    case_id for case_id in row.get(field_name, [])
                    if not any(
                        task_id in item["case_task_ids"].get(case_id, set())
                        for item in available
                    )
                }
                if wrong_task:
                    result.error(
                        "TASK_COVERAGE_INVALID",
                        f"task-coverage.yml[{task_id}].{field_name}",
                        f"case IDs do not bind this stable task: {sorted(wrong_task)}",
                    )
        for holdout_id in row.get("holdout_case_ids", []):
            matching = next((item["tasks"].get(holdout_id) for item in available if holdout_id in item["tasks"]), None)
            if matching is not None and matching.get("holdout") is not True:
                result.error("TASK_COVERAGE_INVALID", f"task-coverage.yml[{task_id}].holdout_case_ids", f"{holdout_id!r} is not a holdout")

    sources: dict[str, Mapping[str, Any]] = {}
    if sources_manifest is not None:
        try:
            source_document = _load_yaml(Path(sources_manifest))
            sources = {item.get("id"): item for item in _records(source_document, "sources") if _id(item.get("id"))}
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", str(sources_manifest), f"cannot load sources manifest: {exc}")
    method_tasks = {task_id: task for task_id, task in tasks.items() if task.get("status") == "active" and task.get("task_mode") == "method-transfer"}
    if method_tasks and sources_manifest is None:
        result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", "--sources-manifest", "method-transfer validation requires an explicit sources manifest")
    evidence_source_ids = {item.get("source_id") for item in _records(evidence, "evidence") if _id(item.get("source_id"))}
    if method_tasks and sources_manifest is not None and not any(
        source_id in evidence_source_ids
        and source.get("provenance_role") == "method-source"
        for source_id, source in sources.items()
    ):
        result.error(
            "METHOD_TRANSFER_PROVENANCE_REQUIRED",
            str(sources_manifest),
            "method-transfer requires at least one extracted method-source in the explicit manifest",
        )
    for candidate_id, candidate in candidate_map.items():
        linked_method = set(candidate.get("stable_task_ids") or []) & set(method_tasks)
        if not linked_method:
            continue
        provenance = candidate.get("provenance_contract")
        if not isinstance(provenance, dict) or set(provenance.get("output_layers", [])) != PROVENANCE_LAYERS or provenance.get("missing_target_evidence") not in {"stop", "lower-conclusion-strength"}:
            result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"capability-rules.yml.candidate[{candidate_id}].provenance_contract", "candidate must preserve the three output layers and missing-evidence behavior")
        eval_meta = eval_by_candidate.get(candidate_id)
        if eval_meta is None:
            continue
        if not METHOD_RUBRIC_DIMENSIONS.issubset(eval_meta["dimension_ids"]) or METHOD_FATAL_FAILURE not in eval_meta["fatal_ids"]:
            result.error("METHOD_TRANSFER_PROVENANCE_REQUIRED", f"{candidate_id}.eval-rubric", "method-transfer rubric lacks required dimensions/fatal failure")
        for task_id in linked_method:
            row = coverage_rows.get(task_id, {})
            required_inputs = set(method_tasks[task_id].get("required_input_types", []))
            covered_inputs: set[str] = set()
            external_found = False
            for holdout_id in row.get("holdout_case_ids", []):
                case = eval_meta["tasks"].get(holdout_id)
                if not isinstance(case, dict):
                    continue
                holdout_contract = case.get("holdout_contract")
                if not isinstance(holdout_contract, dict):
                    continue
                if holdout_contract.get("used_for_rule_extraction") is not False:
                    continue
                if (
                    not isinstance(holdout_contract.get("isolation"), str)
                    or not holdout_contract["isolation"].strip()
                ):
                    continue
                dimensions = _strings(holdout_contract.get("unfamiliarity_dimensions"), nonempty=True)
                if dimensions is None or not set(dimensions).issubset(UNFAMILIARITY_DIMENSIONS):
                    continue
                target_ids = _strings(holdout_contract.get("target_source_ids"), nonempty=True) or []
                hashes = holdout_contract.get("target_source_hashes")
                for source_id in target_ids:
                    source = sources.get(source_id)
                    expected_hash = hashes.get(source_id) if isinstance(hashes, dict) else None
                    if source is not None and source.get("provenance_role") == "target-material" and FULL_SHA256_RE.fullmatch(str(expected_hash or "")) and expected_hash == source.get("checksum") and source_id not in evidence_source_ids:
                        external_found = True
                covered_inputs.update(case.get("input_type_ids", []))
            if not external_found or not required_inputs.issubset(covered_inputs):
                result.error("METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED", f"task-coverage.yml[{task_id}].holdout_case_ids", "method-transfer requires external isolated target material covering all required input types")

        current_gate4 = _current_decisions(decisions, "gate-4", candidate_id)
        gate4 = current_gate4[0] if len(current_gate4) == 1 else None
        if gate4 is not None and gate4.get("decision") == "accepted":
            accepted_run_ids = set(gate4.get("eval_run_ids", []))
            actual_inputs: set[str] = set()
            actual_external = False
            for run in _records(eval_runs_document, "eval_runs"):
                if (
                    run.get("eval_run_id") not in accepted_run_ids
                    or run.get("candidate_id") != candidate_id
                    or run.get("case_type") != "task"
                    or run.get("holdout") is not True
                    or run.get("status") != "completed"
                    or run.get("outcome") != "pass"
                ):
                    continue
                run_target_ids = _strings(run.get("target_source_ids"), nonempty=True) or []
                run_hashes = run.get("target_source_hashes")
                run_inputs = _strings(run.get("input_type_ids"), nonempty=True) or []
                run_unfamiliarity = _strings(run.get("unfamiliarity_dimensions"), nonempty=True)
                if (
                    run.get("used_for_rule_extraction") is not False
                    or not isinstance(run.get("isolation"), str)
                    or not run["isolation"].strip()
                    or run_unfamiliarity is None
                    or not set(run_unfamiliarity).issubset(UNFAMILIARITY_DIMENSIONS)
                ):
                    continue
                actual_inputs.update(run_inputs)
                for source_id in run_target_ids:
                    source = sources.get(source_id)
                    recorded_hash = run_hashes.get(source_id) if isinstance(run_hashes, dict) else None
                    if (
                        source is not None
                        and source.get("provenance_role") == "target-material"
                        and recorded_hash == source.get("checksum")
                        and source_id not in evidence_source_ids
                    ):
                        actual_external = True
            required_all = {
                input_id for task_id in linked_method
                for input_id in method_tasks[task_id].get("required_input_types", [])
            }
            if not actual_external or not required_all.issubset(actual_inputs):
                result.error(
                    "METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED",
                    f"gate-decisions.yml.gate4[{candidate_id}].eval_run_ids",
                    "Gate 4 acceptance requires completed/pass external target holdout runs covering every required input type",
                )

    checkpoint_path = root / "context-checkpoint.yml"
    if checkpoint_path.exists() or checkpoint_path.is_symlink():
        try:
            checkpoint = _load_yaml(checkpoint_path)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            result.error("CHECKPOINT_PRODUCT_CONTRACT_CONFLICT", "context-checkpoint.yml", str(exc))
            checkpoint = {}
        anchor = checkpoint.get("product_contract_anchor")
        expected_anchor = {
            "path": relative,
            "sha256": contract_hash,
            "task_contract_id": contract.get("task_contract_id"),
            "contract_version": contract.get("contract_version"),
            "active_stable_task_ids": active,
        }
        if anchor != expected_anchor:
            result.error("CHECKPOINT_PRODUCT_CONTRACT_CONFLICT", "context-checkpoint.yml.product_contract_anchor", "checkpoint must re-anchor to the current product contract")
        stage = checkpoint.get("current_stage_objective")
        if not isinstance(stage, dict):
            result.error("CHECKPOINT_PRODUCT_CONTRACT_CONFLICT", "context-checkpoint.yml.current_stage_objective", "must be a mapping")
        else:
            stage_ids = _strings(stage.get("stable_task_ids"), nonempty=True)
            if stage_ids is None or not set(stage_ids).issubset(active) or stage.get("supersedes_product_contract") is not False or stage.get("excluded_stable_task_ids") not in (None, []):
                result.error("CHECKPOINT_PRODUCT_CONTRACT_CONFLICT", "context-checkpoint.yml.current_stage_objective", "stage objective may select active work but may not supersede or exclude product tasks")
            result.summary["current_stage_objective"] = stage
        constraints = checkpoint.get("temporary_operational_constraints")
        if _strings(constraints) is None:
            result.error("CHECKPOINT_PRODUCT_CONTRACT_CONFLICT", "context-checkpoint.yml.temporary_operational_constraints", "must be a string list")
        else:
            result.summary["temporary_operational_constraints"] = constraints

    covered = [task_id for task_id, row in coverage_rows.items() if row.get("coverage_status") == "covered"]
    deferred = [task_id for task_id, row in coverage_rows.items() if row.get("coverage_status") == "deferred"]
    rejected = [task_id for task_id, row in coverage_rows.items() if row.get("coverage_status") == "rejected"]
    result.summary.update({
        "covered_stable_task_ids": covered,
        "uncovered_stable_task_ids": [item for item in active if item not in covered],
        "deferred_stable_task_ids": deferred,
        "rejected_stable_task_ids": rejected,
        "task_contract_drift": "matches" if not any(issue.code in {"TASK_CONTRACT_MISSING", "TASK_CONTRACT_INVALID", "TASK_CONTRACT_SNAPSHOT_MISMATCH"} for issue in result.errors) else "mismatch",
        "status": "valid" if result.ok else ("legacy-contract-review-required" if result.summary["legacy_contract_review_required"] else "invalid"),
    })
    return result
