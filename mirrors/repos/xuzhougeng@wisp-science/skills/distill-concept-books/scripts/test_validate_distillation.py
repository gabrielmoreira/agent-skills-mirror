from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from hash_candidate_tree import CandidateTreeError, candidate_tree_sha256, main as hash_main
from validate_distillation import (
    APPROVAL_SNAPSHOT_GOVERNANCE_FILES,
    DistillationInputError,
    GATE3_APPROVAL_SNAPSHOT_CONTRACT,
    validate_distillation,
)


FIXTURE_CANDIDATE_PATH = "candidates/review-book-task"
FIXTURE_SKILL = (
    "---\n"
    "name: review-book-task\n"
    "description: Test candidate.\n"
    "---\n\n"
    "# Review book task\n\n"
    "Apply the bounded, reviewed method and stop when source context is missing.\n"
)
FIXTURE_DIMENSIONS = [
    "source-layer-separation",
    "traceability",
    "scope-discipline",
    "stopping-behavior",
    "output-usability",
]
FIXTURE_FATAL_FAILURES = [
    "reads without Gate approval",
    "overwrites existing records",
]
FIXTURE_TRIGGER_DEFINITION = {
    "schema_version": 2,
    "skill_name": "review-book-task",
    "should_trigger": [
        {
            "case_id": f"trigger-{index}",
            "prompt": f"Trigger request {index}.",
            "expected_reason": "This request uses the reviewed bounded method.",
            "stable_task_ids": ["stable-task-001"],
            "input_type_ids": ["book-material"],
            "positive_example_ids": ["positive-example-001"],
            "negative_example_ids": [],
        }
        for index in range(1, 4)
    ],
    "should_not_trigger": [
        {
            "case_id": f"nontrigger-{index}",
            "prompt": f"Adjacent request {index}.",
            "expected_reason": "This request is outside the reviewed task boundary.",
            "stable_task_ids": ["stable-task-001"],
            "input_type_ids": ["book-material"],
            "positive_example_ids": [],
            "negative_example_ids": ["negative-example-001"],
        }
        for index in range(1, 4)
    ],
}
FIXTURE_TASK_DEFINITION = {
    "schema_version": 2,
    "skill_name": "review-book-task",
    "comparison_protocol": {
        "required": True,
        "baseline": "Run without loading the candidate.",
        "with_skill": "Run with only the candidate and allowed fixture.",
        "leakage_control": "Withhold expected answers and isolate contexts.",
        "human_review_dimensions": FIXTURE_DIMENSIONS,
        "rubric": {
            "rubric_id": "rubric-001",
            "score_min": 0,
            "score_max_per_dimension": 2,
            "pass_threshold": 8,
            "dimensions": [
                {"dimension_id": item, "description": item.replace("-", " ")}
                for item in FIXTURE_DIMENSIONS
            ],
            "fatal_failures": [
                {"failure_id": f"fatal-{index:03d}", "description": item}
                for index, item in enumerate(FIXTURE_FATAL_FAILURES, 1)
            ],
        },
    },
    "tasks": [
        {
            "case_id": f"task-{index}",
            "title": f"Representative task {index}",
            "holdout": index == 1,
            "rubric_id": "rubric-001",
            "input_profile": "A bounded local source fixture.",
            "request": f"Representative task {index}.",
            "expected_behaviors": ["Stay within the reviewed source scope."],
            "failure_signals": ["Invents unsupported source content."],
            "stable_task_ids": ["stable-task-001"],
            "input_type_ids": ["book-material"],
            "positive_example_ids": ["positive-example-001"],
            "negative_example_ids": ["negative-example-001"],
        }
        for index in range(1, 4)
    ],
}


def valid_documents():
    gate_rule_rationale = "Rule accepted for bounded evaluation."
    candidate_hash = f"sha256:{'0' * 64}"
    accepted_history = [
        {
            "from": None,
            "to": "candidate",
            "decided_by": "project-agent",
            "decided_at": "2026-08-04",
            "rationale": "Initial extraction for review.",
        },
        {
            "from": "candidate",
            "to": "accepted",
            "decided_by": "human-reviewer",
            "decided_at": "2026-08-04",
            "rationale": "Accepted after traceability review.",
        },
    ]
    evidence = {
        "evidence_id": "ev-001",
        "source_id": "book-001",
        "locator": {
            "source_id": "book-001",
            "locator_type": "ooxml-block",
            "heading_path": ["Chapter 1"],
            "ooxml_block_index": 12,
            "content_hash": "abc123def456",
        },
        "evidence_type": "text",
        "raw_text": "Source text.",
        "normalized_text": "Source text.",
        "capture_mode": "excerpt",
        "extraction_confidence": "high",
        "limitations": [],
        "quality_flags": [],
        "status": "accepted",
        "status_history": copy.deepcopy(accepted_history),
    }
    claim = {
        "claim_id": "cl-001",
        "statement": "The book states a bounded method.",
        "claim_type": "method",
        "source_position": "book-assertion",
        "evidence_ids": ["ev-001"],
        "transformation": "T1",
        "scope": ["example task"],
        "limitations": [],
        "importance": "important",
        "status": "accepted",
        "human_decision": None,
        "status_history": copy.deepcopy(accepted_history),
    }
    relation = {
        "relation_id": "rel-001",
        "subject": "method",
        "predicate": "requires",
        "object": "context",
        "qualifiers": ["within the stated scope"],
        "claim_ids": ["cl-001"],
        "evidence_ids": ["ev-001"],
        "relation_status": "explicit",
        "status": "accepted",
        "status_history": copy.deepcopy(accepted_history),
    }
    rule = {
        "rule_id": "rule-001",
        "stable_task_ids": ["stable-task-001"],
        "trigger": {"task": "apply the method", "signals": ["book-based request"]},
        "required_context": ["source material"],
        "checks": ["check scope"],
        "action": ["apply only the supported step"],
        "output": ["auditable result"],
        "stop_conditions": ["missing source context"],
        "claim_ids": ["cl-001"],
        "relation_ids": ["rel-001"],
        "transformation": "T4",
        "status": "accepted",
        "human_decision": {
            "decision": "accepted",
            "reviewer_type": "user",
            "reviewer": "project-user",
            "decided_at": "2026-08-04",
            "rationale": gate_rule_rationale,
            "gate_decision_id": "gate-decision-003",
        },
        "status_history": [
            {
                "from": None,
                "to": "candidate",
                "decided_by": "project-agent",
                "decided_at": "2026-08-04",
                "rationale": "Initial extraction for review.",
            },
            {
                "from": "candidate",
                "to": "accepted",
                "decided_by": "project-user",
                "decided_at": "2026-08-04",
                "rationale": gate_rule_rationale,
            },
        ],
        "semantic_support": {
            "checks": [{"item_index": 0, "claim_ids": ["cl-001"], "relation_ids": []}],
            "action": [{"item_index": 0, "claim_ids": ["cl-001"], "relation_ids": []}],
            "output": [{"item_index": 0, "claim_ids": ["cl-001"], "relation_ids": []}],
            "stop_conditions": [{
                "item_index": 0, "claim_ids": ["cl-001"], "relation_ids": []
            }],
        },
    }
    candidate = {
        "candidate_id": "candidate-001",
        "name": "review-book-task",
        "stable_task": "Apply the reviewed method to a bounded input.",
        "stable_task_ids": ["stable-task-001"],
        "trigger_case_ids": ["trigger-1", "trigger-2", "trigger-3"],
        "nontrigger_case_ids": ["nontrigger-1", "nontrigger-2", "nontrigger-3"],
        "task_case_ids": ["task-1", "task-2", "task-3"],
        "should_trigger": ["request one", "request two", "request three"],
        "should_not_trigger": ["adjacent one", "adjacent two", "adjacent three"],
        "inputs": ["source material"],
        "outputs": ["auditable result"],
        "rule_ids": ["rule-001"],
        "stop_conditions": ["source context missing"],
        "risks": ["overgeneralization"],
        "lifecycle": "review",
        "lifecycle_history": [
            {
                "from": None,
                "to": "draft",
                "decided_by": "project-agent",
                "decided_at": "2026-08-04",
                "rationale": "Candidate specification initialized.",
            },
            {
                "from": "draft",
                "to": "review",
                "decided_by": "project-agent",
                "decided_at": "2026-08-04",
                "rationale": "Candidate prepared for human review.",
            },
        ],
    }
    task_contract = {
        "schema_version": 1,
        "distillation_id": "validator-test-v1",
        "task_contract_id": "task-contract-001",
        "contract_version": 1,
        "status": "frozen",
        "product_goal": "Apply one reviewed source-contained method without task drift.",
        "audience": ["test reviewer"],
        "input_types": [{
            "input_type_id": "book-material",
            "description": "Registered source-book material.",
            "provenance_role": "method-source",
        }],
        "stable_tasks": [{
            "stable_task_id": "stable-task-001",
            "statement": "Apply the reviewed method to bounded book material.",
            "task_mode": "source-contained",
            "required_input_types": ["book-material"],
            "required_outputs": ["auditable-result"],
            "non_negotiable_constraints": ["Preserve traceability."],
            "positive_examples": [{
                "example_id": "positive-example-001",
                "input_type_id": "book-material",
                "statement": "Apply the method to this registered source.",
            }],
            "negative_examples": [{
                "example_id": "negative-example-001",
                "input_type_id": "book-material",
                "statement": "Produce an unsupported summary.",
            }],
            "acceptance_question_ids": ["acceptance-001"],
            "provenance_requirements": {
                "required_output_layers": ["method-source-evidence"],
                "target_source_role": None,
                "missing_target_evidence": "stop",
                "forbidden_transfers": [],
            },
            "status": "active",
        }],
        "exclusions": [{"exclusion_id": "exclusion-001", "statement": "Unreviewed deployment."}],
        "acceptance_questions": [{
            "acceptance_question_id": "acceptance-001",
            "question": "Is the result traceable?",
        }],
    }
    task_coverage = {
        "schema_version": 1,
        "distillation_id": "validator-test-v1",
        "status": "review-ready",
        "task_contract": {},
        "coverage": [{
            "stable_task_id": "stable-task-001",
            "coverage_status": "covered",
            "candidate_ids": ["candidate-001"],
            "capability_rule_ids": ["rule-001"],
            "trigger_case_ids": ["trigger-1"],
            "nontrigger_case_ids": ["nontrigger-1"],
            "task_eval_case_ids": ["task-1"],
            "holdout_case_ids": ["task-1"],
            "rubric_dimension_ids": ["traceability"],
            "gate1_decision_id": "gate-decision-001",
            "rationale": "Complete synthetic coverage.",
        }],
    }
    return {
        "task-contract.yml": task_contract,
        "task-coverage.yml": task_coverage,
        "evidence-ledger.yml": {
            "schema_version": 1, "distillation_id": "validator-test-v1",
            "evidence": [evidence], "claims": [claim]
        },
        "concept-map.yml": {
            "schema_version": 1, "distillation_id": "validator-test-v1",
            "relations": [relation]
        },
        "capability-rules.yml": {
            "schema_version": 1,
            "distillation_id": "validator-test-v1",
            "capability_rules": [rule],
            "skill_candidates": [candidate],
        },
        "gate-decisions.yml": {
            "schema_version": 1,
            "distillation_id": "validator-test-v1",
            "gate_decisions": [
                {
                    "decision_id": "gate-decision-001",
                    "sequence": 1,
                    "supersedes": None,
                    "is_current": True,
                    "gate": "gate-1",
                    "candidate_id": None,
                    "decision": "approved",
                    "scope": ["validator-test-v1"],
                    "reviewer_type": "user",
                    "reviewer": "project-user",
                    "decided_at": "2026-08-04",
                    "rationale": "Requirements frozen for the test fixture.",
                    "conditions": [],
                    "eval_run_ids": [],
                    "rule_decisions": [],
                    "stable_task_decisions": [{
                        "stable_task_id": "stable-task-001",
                        "decision": "active",
                        "rationale": "Task approved as active.",
                    }],
                    "task_contract_snapshot": {},
                },
                {
                    "decision_id": "gate-decision-002",
                    "sequence": 2,
                    "supersedes": None,
                    "is_current": True,
                    "gate": "gate-2",
                    "candidate_id": None,
                    "decision": "approved",
                    "scope": ["book-001"],
                    "reviewer_type": "user",
                    "reviewer": "project-user",
                    "decided_at": "2026-08-04",
                    "rationale": "Source structure approved for bounded extraction.",
                    "conditions": [],
                    "eval_run_ids": [],
                    "rule_decisions": [],
                },
                {
                    "decision_id": "gate-decision-003",
                    "sequence": 3,
                    "supersedes": None,
                    "is_current": True,
                    "gate": "gate-3",
                    "candidate_id": "candidate-001",
                    "decision": "approved-for-eval",
                    "scope": ["candidate-001"],
                    "reviewer_type": "user",
                    "reviewer": "project-user",
                    "decided_at": "2026-08-04",
                    "rationale": "Approved for bounded evaluation.",
                    "conditions": [],
                    "eval_run_ids": [],
                    "rule_decisions": [{
                        "rule_id": "rule-001",
                        "decision": "accepted",
                        "rationale": gate_rule_rationale,
                    }],
                    "approval_snapshot": {
                        "contract": GATE3_APPROVAL_SNAPSHOT_CONTRACT,
                        "candidate_path": FIXTURE_CANDIDATE_PATH,
                        "candidate_hash": candidate_hash,
                        "governance_hashes": {
                            filename: candidate_hash
                            for filename in APPROVAL_SNAPSHOT_GOVERNANCE_FILES
                        },
                    },
                },
            ],
            "materializations": [{
                "materialization_id": "materialization-001",
                "candidate_id": "candidate-001",
                "gate3_decision_id": "gate-decision-003",
                "status": "completed",
                "candidate_path": FIXTURE_CANDIDATE_PATH,
                "candidate_hash": candidate_hash,
                "materialized_at": "2026-08-04",
                "rule_ids": ["rule-001"],
                "quick_validation": {
                    "status": "pass",
                    "validator": "quick_validate.py",
                    "validated_at": "2026-08-04",
                    "candidate_hash": candidate_hash,
                },
            }],
        },
        "eval-runs.yml": {
            "schema_version": 1,
            "distillation_id": "validator-test-v1",
            "eval_runs": [],
        },
    }


def valid_sources_manifest(source_role="primary-book"):
    return {
        "schema_version": 2,
        "sources": [{
            "id": "book-001",
            "source_role": source_role,
            "provenance_role": "method-source",
            "privacy": "private",
            "allow_public_quotes": False,
        }],
    }


def sync_task_contract_snapshot(documents, root):
    contract = documents["task-contract.yml"]
    contract_path = root / "task-contract.yml"
    contract_path.write_text(
        yaml.safe_dump(contract, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    contract_hash = f"sha256:{hashlib.sha256(contract_path.read_bytes()).hexdigest()}"
    coverage = documents["task-coverage.yml"]
    coverage["task_contract"] = {
        "path": "task-contract.yml",
        "sha256": contract_hash,
        "task_contract_id": contract["task_contract_id"],
        "contract_version": contract["contract_version"],
    }
    (root / "task-coverage.yml").write_text(
        yaml.safe_dump(coverage, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    gate1 = next(
        item for item in documents["gate-decisions.yml"]["gate_decisions"]
        if item.get("gate") == "gate-1" and item.get("is_current") is True
    )
    gate1["task_contract_snapshot"] = {
        "contract": "gate1-task-contract-snapshot:v1",
        "task_contract_path": "task-contract.yml",
        "task_contract_hash": contract_hash,
        "task_contract_id": contract["task_contract_id"],
        "contract_version": contract["contract_version"],
        "active_stable_task_ids": [
            item["stable_task_id"] for item in contract["stable_tasks"]
            if item["status"] == "active"
        ],
    }


def sync_current_gate3_approval_snapshot(
    documents,
    root,
    candidate_path=FIXTURE_CANDIDATE_PATH,
):
    """Create a valid synthetic user-approval snapshot from files on disk."""
    candidate_hash = candidate_tree_sha256(root, candidate_path)
    governance_hashes = {
        filename: f"sha256:{hashlib.sha256((root / filename).read_bytes()).hexdigest()}"
        for filename in APPROVAL_SNAPSHOT_GOVERNANCE_FILES
    }
    contract = documents["task-contract.yml"]
    gate1 = next(
        item for item in documents["gate-decisions.yml"]["gate_decisions"]
        if item.get("gate") == "gate-1" and item.get("is_current") is True
    )
    contract_hash = f"sha256:{hashlib.sha256((root / 'task-contract.yml').read_bytes()).hexdigest()}"
    coverage_hash = f"sha256:{hashlib.sha256((root / 'task-coverage.yml').read_bytes()).hexdigest()}"
    for decision in documents["gate-decisions.yml"]["gate_decisions"]:
        if (
            decision.get("gate") == "gate-3"
            and decision.get("is_current") is True
            and decision.get("decision") == "approved-for-eval"
        ):
            decision["approval_snapshot"] = {
                "contract": GATE3_APPROVAL_SNAPSHOT_CONTRACT,
                "candidate_path": candidate_path,
                "candidate_hash": candidate_hash,
                "governance_hashes": governance_hashes,
                "current_gate1_decision_id": gate1["decision_id"],
                "task_contract": {
                    "path": "task-contract.yml",
                    "sha256": contract_hash,
                    "task_contract_id": contract["task_contract_id"],
                    "contract_version": contract["contract_version"],
                    "active_stable_task_ids": gate1["task_contract_snapshot"]["active_stable_task_ids"],
                },
                "task_coverage": {
                    "path": "task-coverage.yml",
                    "sha256": coverage_hash,
                },
                "candidate_stable_task_ids": documents["capability-rules.yml"]["skill_candidates"][0]["stable_task_ids"],
            }


def set_rule_pending(documents):
    rule = documents["capability-rules.yml"]["capability_rules"][0]
    rule["status"] = "candidate"
    rule.pop("status_history", None)
    rule["human_decision"] = {
        "decision": "pending",
        "reviewer_type": None,
        "reviewer": None,
        "decided_at": None,
        "rationale": "",
        "gate_decision_id": None,
    }
    gate3 = next(
        item for item in documents["gate-decisions.yml"]["gate_decisions"]
        if item["gate"] == "gate-3"
    )
    gate3.update({
        "decision": "pending",
        "reviewer_type": None,
        "reviewer": None,
        "decided_at": None,
        "rationale": "Awaiting explicit rule decisions.",
        "rule_decisions": [],
    })
    documents["gate-decisions.yml"]["materializations"] = []


def reject_rule_at_gate3(documents):
    rule = documents["capability-rules.yml"]["capability_rules"][0]
    rationale = "Rule rejected by the Gate 3 user review."
    rule["status"] = "rejected"
    rule["human_decision"] = {
        "decision": "rejected",
        "reviewer_type": "user",
        "reviewer": "project-user",
        "decided_at": "2026-08-04",
        "rationale": rationale,
        "gate_decision_id": "gate-decision-003",
    }
    rule["status_history"] = [
        {
            "from": None, "to": "candidate", "decided_by": "project-agent",
            "decided_at": "2026-08-04", "rationale": "Initial extraction for review.",
        },
        {
            "from": "candidate", "to": "rejected", "decided_by": "project-user",
            "decided_at": "2026-08-04", "rationale": rationale,
        },
    ]
    gate3 = documents["gate-decisions.yml"]["gate_decisions"][2]
    gate3["rule_decisions"] = [{
        "rule_id": "rule-001", "decision": "rejected", "rationale": rationale,
    }]


def accept_candidate(documents, root):
    candidate = documents["capability-rules.yml"]["skill_candidates"][0]
    materialization_hash = documents["gate-decisions.yml"]["materializations"][0][
        "candidate_hash"
    ]
    candidate["lifecycle"] = "accepted"
    candidate["lifecycle_history"].append({
        "from": "review",
        "to": "accepted",
        "decided_by": "human-reviewer",
        "decided_at": "2026-08-04",
        "rationale": "Accepted after the completed Gate 4 evaluation.",
    })
    eval_runs = []
    for run_number, (case_type, case_number) in enumerate(
        (
            ("trigger", 1), ("trigger", 2), ("trigger", 3),
            ("nontrigger", 1), ("nontrigger", 2), ("nontrigger", 3),
            ("task", 1), ("task", 2), ("task", 3),
        ),
        start=1,
    ):
        token = f"{case_type}-{case_number}"
        eval_run_id = f"eval-run-{run_number:03d}"
        if case_type == "trigger":
            case_record = FIXTURE_TRIGGER_DEFINITION["should_trigger"][case_number - 1]
        elif case_type == "nontrigger":
            case_record = FIXTURE_TRIGGER_DEFINITION["should_not_trigger"][case_number - 1]
        else:
            case_record = FIXTURE_TASK_DEFINITION["tasks"][case_number - 1]
        case_hash = "sha256:" + hashlib.sha256(json.dumps(
            case_record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")).hexdigest()
        request = case_record.get("request", case_record.get("prompt"))
        holdout = bool(case_record.get("holdout", False))
        fixture_path = f"fixtures/{token}.json"
        baseline_path = f"outputs/{token}-baseline.json"
        with_skill_path = f"outputs/{token}-with-skill.json"
        leakage_controls = {
            "expected_answer_withheld": True,
            "context_isolated": True,
            "context_differences": ["candidate loaded only in with_skill"],
            "exceptions": [],
        }
        fixture = {
            "schema_version": 1,
            "fixture_id": f"fixture-{run_number:03d}",
            "case_type": case_type,
            "case_id": token,
            "case_definition_hash": case_hash,
            "request": request,
            "source_ids": ["book-001"],
            "holdout": holdout,
            "input_payload": {"source_excerpt": f"bounded input for {token}"},
            "leakage_controls": {
                "expected_answer_withheld": True,
                "context_isolated": True,
                "exceptions": [],
            },
        }
        baseline_output = {
            "schema_version": 1,
            "eval_run_id": eval_run_id,
            "case_id": token,
            "condition": "baseline",
            "response": f"baseline response for {token}",
        }
        with_skill_output = {
            "schema_version": 1,
            "eval_run_id": eval_run_id,
            "case_id": token,
            "condition": "with_skill",
            "response": f"with-Skill response for {token}",
        }
        artifact_payloads = {
            fixture_path: (json.dumps(fixture, sort_keys=True) + "\n").encode(),
            baseline_path: (json.dumps(baseline_output, sort_keys=True) + "\n").encode(),
            with_skill_path: (json.dumps(with_skill_output, sort_keys=True) + "\n").encode(),
        }
        for relative_path, payload in artifact_payloads.items():
            artifact_path = root / relative_path
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_bytes(payload)
        eval_runs.append({
            "eval_run_id": eval_run_id,
            "candidate_id": "candidate-001",
            "materialization_id": "materialization-001",
            "case_type": case_type,
            "case_id": token,
            "case_definition_hash": case_hash,
            "status": "completed",
            "outcome": "pass",
            "fixture_id": f"fixture-{run_number:03d}",
            "fixture_path": fixture_path,
            "fixture_hash": hashlib.sha256(artifact_payloads[fixture_path]).hexdigest(),
            "source_ids": ["book-001"],
            "holdout": holdout,
            "rule_ids": ["rule-001"],
            "candidate_hash": materialization_hash,
            "execution_environment": {"model": "test-model", "tools": []},
            "baseline_output_path": baseline_path,
            "baseline_output_hash": hashlib.sha256(
                artifact_payloads[baseline_path]
            ).hexdigest(),
            "with_skill_output_path": with_skill_path,
            "with_skill_output_hash": hashlib.sha256(
                artifact_payloads[with_skill_path]
            ).hexdigest(),
            "rubric_id": "rubric-001",
            "dimension_scores": {
                FIXTURE_DIMENSIONS[0]: 2,
                FIXTURE_DIMENSIONS[1]: 2,
                FIXTURE_DIMENSIONS[2]: 2,
                FIXTURE_DIMENSIONS[3]: 2,
                FIXTURE_DIMENSIONS[4]: 1,
            },
            "fatal_failures_observed": [],
            "leakage_controls": leakage_controls,
            "score": 9,
            "max_score": 10,
            "pass_threshold": 8,
            "reviewer_type": "human-delegate",
            "reviewer": "evaluation-reviewer",
            "completed_at": "2026-08-04",
            "limitations": [],
        })
    documents["eval-runs.yml"]["eval_runs"] = eval_runs
    documents["gate-decisions.yml"]["gate_decisions"].append(
        {
            "decision_id": "gate-decision-004",
            "sequence": 4,
            "supersedes": None,
            "is_current": True,
            "gate": "gate-4",
            "candidate_id": "candidate-001",
            "decision": "accepted",
            "scope": ["candidate-001"],
            "reviewer_type": "user",
            "reviewer": "project-user",
            "decided_at": "2026-08-04",
            "rationale": "Accepted after reviewing the completed passing run.",
            "conditions": [],
            "eval_run_ids": [item["eval_run_id"] for item in eval_runs],
            "rule_decisions": [],
        },
    )


def add_valid_correction(documents):
    evidence = documents["evidence-ledger.yml"]["evidence"][0]
    claim = documents["evidence-ledger.yml"]["claims"][0]
    claim["correction_ids"] = ["correction-001"]
    documents["correction-overlay.yml"] = {
        "schema_version": 1,
        "distillation_id": "validator-test-v1",
        "overlay_id": "correction-overlay-001",
        "source_id": "book-001",
        "policy": {
            "source_remains_read_only": True,
            "normalized_text_must_remain_semantically_unchanged": True,
        },
        "corrections": [{
            "correction_id": "correction-001",
            "evidence_id": "ev-001",
            "locator": copy.deepcopy(evidence["locator"]),
            "issue_type": "ocr-risk",
            "raw_value": "Source text.",
            "proposed_value": "Corrected source text.",
            "basis": "Human comparison with a reliable local carrier.",
            "status": "accepted",
            "human_decision": {
                "decision": "revised",
                "reviewer_type": "human-delegate",
                "reviewer": "human-reviewer",
                "decided_at": "2026-08-04",
                "rationale": "Verified against the reliable carrier.",
            },
            "applies_to_claim_ids": ["cl-001"],
            "resolved_quality_flags": ["ocr-risk"],
            "resulting_value": "Corrected source text.",
        }],
    }


class DistillationValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.write_candidate_contract()
        self.documents = self.fresh_documents()
        self.write_documents()

    def write_candidate_contract(self):
        candidate_dir = self.root / FIXTURE_CANDIDATE_PATH
        candidate_dir.mkdir(parents=True, exist_ok=True)
        (candidate_dir / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
        eval_dir = candidate_dir / "evals"
        eval_dir.mkdir(exist_ok=True)
        (eval_dir / "trigger-cases.json").write_text(
            json.dumps(FIXTURE_TRIGGER_DEFINITION, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (eval_dir / "task-cases.json").write_text(
            json.dumps(FIXTURE_TASK_DEFINITION, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def fresh_documents(self):
        documents = valid_documents()
        materialization = documents["gate-decisions.yml"]["materializations"][0]
        candidate_hash = candidate_tree_sha256(self.root, FIXTURE_CANDIDATE_PATH)
        materialization["candidate_hash"] = candidate_hash
        materialization["quick_validation"]["candidate_hash"] = candidate_hash
        return documents

    def sync_candidate_hash(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        candidate_hash = candidate_tree_sha256(self.root, FIXTURE_CANDIDATE_PATH)
        materialization["candidate_hash"] = candidate_hash
        materialization["quick_validation"]["candidate_hash"] = candidate_hash

    def write_documents(self, *, sync_approval_snapshot=True):
        # The approval snapshot hashes these exact serialized bytes. Write the
        # three frozen governance documents first, then synthesize the Gate 3
        # decision, then write the remaining records.
        sync_task_contract_snapshot(self.documents, self.root)
        for name in APPROVAL_SNAPSHOT_GOVERNANCE_FILES:
            document = self.documents[name]
            (self.root / name).write_text(
                yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        if sync_approval_snapshot:
            sync_current_gate3_approval_snapshot(self.documents, self.root)
        for name, document in self.documents.items():
            if name in APPROVAL_SNAPSHOT_GOVERNANCE_FILES or name in {
                "task-contract.yml", "task-coverage.yml"
            }:
                continue
            (self.root / name).write_text(
                yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

    def write_manifest(self, source_role="primary-book"):
        manifest = self.root / "sources.yml"
        manifest.write_text(
            yaml.safe_dump(
                valid_sources_manifest(source_role), allow_unicode=True, sort_keys=False
            ),
            encoding="utf-8",
        )
        return manifest

    def configure_markdown_policy(
        self,
        *,
        repository_path="docs/policy.md",
        local_path=None,
        related_local_paths=None,
        source_text="# Policy\n\n## Review Gate（Gate 3）\n\nStable policy text.\n",
        raw_text="Stable policy text.",
        normalized_text=None,
        anchor=None,
        write_source=True,
    ):
        normalized_text = raw_text if normalized_text is None else normalized_text
        local_path = repository_path if local_path is None else local_path
        anchor = anchor or f"{repository_path}:5#review-gate"
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["locator"] = {
            "source_id": "book-001",
            "locator_type": "markdown-section",
            "anchor": anchor,
            "content_hash": hashlib.sha256(
                normalized_text.encode("utf-8")
            ).hexdigest()[:12],
        }
        evidence["raw_text"] = raw_text
        evidence["normalized_text"] = normalized_text
        if write_source:
            source_path = self.root / repository_path
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(source_text, encoding="utf-8")

        manifest_data = valid_sources_manifest()
        source = manifest_data["sources"][0]
        source["local_path"] = local_path
        source["related_local_paths"] = list(related_local_paths or [])
        manifest = self.root / "manifests" / "sources.yml"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            yaml.safe_dump(manifest_data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.write_documents()
        return manifest

    def error_codes(self):
        return {issue.code for issue in validate_distillation(self.root).errors}

    def configure_method_transfer(self, *, include_candidate_provenance=True,
                                  external_holdout=True,
                                  cover_required_input=True):
        contract = self.documents["task-contract.yml"]
        contract["input_types"].append({
            "input_type_id": "external-target-material",
            "description": "Independent unfamiliar target material.",
            "provenance_role": "target-material",
        })
        task = contract["stable_tasks"][0]
        task.update({
            "task_mode": "method-transfer",
            "required_input_types": ["external-target-material"],
            "positive_examples": [{
                "example_id": "positive-example-001",
                "input_type_id": "external-target-material",
                "statement": "Apply the method to unfamiliar target material.",
            }],
            "negative_examples": [{
                "example_id": "negative-example-001",
                "input_type_id": "external-target-material",
                "statement": "Treat a method-source case as a target fact.",
            }],
            "provenance_requirements": {
                "required_output_layers": [
                    "method-source-evidence", "target-material-evidence",
                    "analogy-hypothesis",
                ],
                "target_source_role": "target-material",
                "missing_target_evidence": "stop",
                "forbidden_transfers": ["method-source-fact-as-target-fact"],
            },
        })
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        if include_candidate_provenance:
            candidate["provenance_contract"] = {
                "output_layers": [
                    "method-source-evidence", "target-material-evidence",
                    "analogy-hypothesis",
                ],
                "missing_target_evidence": "stop",
            }
        trigger_path = self.root / FIXTURE_CANDIDATE_PATH / "evals" / "trigger-cases.json"
        trigger_definition = json.loads(trigger_path.read_text(encoding="utf-8"))
        for case in (
            trigger_definition["should_trigger"]
            + trigger_definition["should_not_trigger"]
        ):
            case["input_type_ids"] = ["external-target-material"]
        trigger_path.write_text(
            json.dumps(trigger_definition, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        task_path = self.root / FIXTURE_CANDIDATE_PATH / "evals" / "task-cases.json"
        definition = json.loads(task_path.read_text(encoding="utf-8"))
        rubric = definition["comparison_protocol"]["rubric"]
        rubric["dimensions"].extend([
            {"dimension_id": "provenance-layer-separation", "description": "Separate provenance layers."},
            {"dimension_id": "anti-forced-analogy", "description": "Avoid forced analogy."},
        ])
        rubric["fatal_failures"].append({
            "failure_id": "method-source-fact-as-target-fact",
            "description": "Method-source fact is presented as target fact.",
        })
        rubric["pass_threshold"] = 10
        for case in definition["tasks"]:
            case["input_type_ids"] = ["external-target-material"]
        if not cover_required_input:
            definition["tasks"][0]["input_type_ids"] = ["book-material"]
        if external_holdout:
            definition["tasks"][0]["holdout_contract"] = {
                "target_source_ids": ["target-001"],
                "target_source_hashes": {"target-001": f"sha256:{'1' * 64}"},
                "used_for_rule_extraction": False,
                "unfamiliarity_dimensions": ["domain"],
                "isolation": "Independent synthetic target fixture.",
            }
        task_path.write_text(
            json.dumps(definition, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        coverage = self.documents["task-coverage.yml"]["coverage"][0]
        coverage["rubric_dimension_ids"] = [
            "traceability", "provenance-layer-separation", "anti-forced-analogy"
        ]
        self.sync_candidate_hash()
        self.write_documents()
        manifest = valid_sources_manifest()
        manifest["sources"][0]["provenance_role"] = "method-source"
        manifest["sources"].append({
            "id": "target-001", "source_role": "eval-target",
            "provenance_role": "target-material", "privacy": "private",
            "allow_public_quotes": False, "checksum": f"sha256:{'1' * 64}",
        })
        path = self.root / "method-sources.yml"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        return path

    def test_valid_complete_fixture_passes(self):
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertEqual(1.0, report.metrics["accepted_rule_traceability"])
        self.assertTrue(report.metrics["accepted_rule_traceability_applicable"])
        self.assertEqual(1.0, report.metrics["important_claim_locator_coverage"])
        self.assertFalse(report.as_dict()["truth_assessed"])
        self.assertFalse(report.as_dict()["behavior_effectiveness_assessed"])

    def test_task_contract_hash_drift_fails(self):
        with (self.root / "task-contract.yml").open("a", encoding="utf-8") as handle:
            handle.write("# drift\n")
        codes = self.error_codes()
        self.assertIn("TASK_CONTRACT_SNAPSHOT_MISMATCH", codes)
        self.assertIn("GATE3_TASK_CONTRACT_MISMATCH", codes)

    def test_task_contract_version_must_match_immutable_filename(self):
        self.documents["task-contract.yml"]["contract_version"] = 2
        self.write_documents()
        self.assertIn("TASK_CONTRACT_INVALID", self.error_codes())

    def test_execution_capability_rejects_unknown_input_type(self):
        contract = self.documents["task-contract.yml"]
        contract["execution_capability"] = {
            "input_handling": [{
                "input_type_id": "not-declared",
                "carrier": "pdf-text",
                "modality_strategy": "unimodal-text",
                "degradation_rule": "Fall back to text and state the limitation.",
            }],
        }
        self.write_documents()
        self.assertIn("TASK_CONTRACT_INVALID", self.error_codes())

    def test_execution_capability_rejects_bad_modality(self):
        contract = self.documents["task-contract.yml"]
        contract["execution_capability"] = {
            "input_handling": [{
                "input_type_id": "book-material",
                "carrier": "pdf-text",
                "modality_strategy": "vision-only",
                "degradation_rule": "Fall back to text and state the limitation.",
            }],
        }
        self.write_documents()
        self.assertIn("TASK_CONTRACT_INVALID", self.error_codes())

    def test_execution_capability_valid_when_complete(self):
        contract = self.documents["task-contract.yml"]
        contract["execution_capability"] = {
            "input_handling": [{
                "input_type_id": "book-material",
                "carrier": "pdf-text",
                "modality_strategy": "unimodal-text",
                "degradation_rule": "Fall back to text and state the limitation.",
            }],
            "notes": "Text-only analysis of registered source material.",
        }
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_gate1_duplicate_stable_task_decision_fails(self):
        gate1 = self.documents["gate-decisions.yml"]["gate_decisions"][0]
        gate1["stable_task_decisions"].append(
            copy.deepcopy(gate1["stable_task_decisions"][0])
        )
        self.write_documents()
        self.assertIn("TASK_CONTRACT_SNAPSHOT_MISMATCH", self.error_codes())

    def test_eval_v2_task_requires_positive_and_negative_example_ids(self):
        path = self.root / FIXTURE_CANDIDATE_PATH / "evals" / "task-cases.json"
        definition = json.loads(path.read_text(encoding="utf-8"))
        definition["tasks"][0].pop("negative_example_ids")
        path.write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
        self.sync_candidate_hash()
        self.write_documents()
        codes = self.error_codes()
        self.assertTrue(
            {"MATERIALIZATION_EVAL_DEFINITION_INVALID", "TASK_COVERAGE_INVALID"}
            & codes
        )

    def test_candidate_must_register_complete_eval_case_ids(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["trigger_case_ids"] = candidate["trigger_case_ids"][:-1]
        self.write_documents()
        self.assertIn("CANDIDATE_TASK_MISMATCH", self.error_codes())

    def test_active_task_requires_complete_coverage(self):
        self.documents["task-coverage.yml"]["coverage"][0]["task_eval_case_ids"] = []
        self.write_documents()
        self.assertIn("STABLE_TASK_UNCOVERED", self.error_codes())

    def test_candidate_unknown_or_nonactive_task_fails(self):
        self.documents["capability-rules.yml"]["skill_candidates"][0]["stable_task_ids"] = ["unknown-task"]
        self.write_documents()
        self.assertIn("STABLE_TASK_UNKNOWN", self.error_codes())

    def test_gate3_v2_requires_contract_and_coverage_bindings(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["approval_snapshot"].pop("task_coverage", None)
        self.write_documents(sync_approval_snapshot=False)
        self.assertIn("GATE3_TASK_CONTRACT_MISMATCH", self.error_codes())

    def test_current_gate3_v1_is_legacy_review_required(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["approval_snapshot"] = {
            key: value for key, value in gate3["approval_snapshot"].items()
            if key in {"contract", "candidate_path", "candidate_hash", "governance_hashes"}
        }
        gate3["approval_snapshot"]["contract"] = "gate3-approval-snapshot:v1"
        self.write_documents(sync_approval_snapshot=False)
        self.assertIn("LEGACY_TASK_CONTRACT_REVIEW_REQUIRED", self.error_codes())

    def test_method_transfer_requires_candidate_provenance_contract(self):
        manifest = self.configure_method_transfer(include_candidate_provenance=False)
        codes = {item.code for item in validate_distillation(self.root, manifest).errors}
        self.assertIn("METHOD_TRANSFER_PROVENANCE_REQUIRED", codes)

    def test_method_transfer_requires_external_target_holdout(self):
        manifest = self.configure_method_transfer(external_holdout=False)
        codes = {item.code for item in validate_distillation(self.root, manifest).errors}
        self.assertIn("METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED", codes)

    def test_method_transfer_holdout_must_cover_required_input_type(self):
        manifest = self.configure_method_transfer(cover_required_input=False)
        codes = {item.code for item in validate_distillation(self.root, manifest).errors}
        self.assertIn("METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED", codes)

    def test_method_transfer_holdout_requires_isolation_record(self):
        manifest = self.configure_method_transfer()
        task_path = self.root / FIXTURE_CANDIDATE_PATH / "evals" / "task-cases.json"
        definition = json.loads(task_path.read_text(encoding="utf-8"))
        definition["tasks"][0]["holdout_contract"].pop("isolation")
        task_path.write_text(
            json.dumps(definition, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.sync_candidate_hash()
        self.write_documents()
        codes = {item.code for item in validate_distillation(self.root, manifest).errors}
        self.assertIn("METHOD_TRANSFER_EXTERNAL_HOLDOUT_REQUIRED", codes)

    def test_method_example_positive_case_cannot_be_nontrigger(self):
        trigger_path = self.root / FIXTURE_CANDIDATE_PATH / "evals" / "trigger-cases.json"
        definition = json.loads(trigger_path.read_text(encoding="utf-8"))
        definition["should_not_trigger"][0]["negative_example_ids"] = ["positive-example-001"]
        trigger_path.write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
        self.sync_candidate_hash()
        self.write_documents()
        self.assertIn("CANDIDATE_TASK_MISMATCH", self.error_codes())

    def test_accepted_ocr_evidence_requires_region_locator_and_human_review(self):
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["capture_mode"] = "ocr"
        evidence["ocr_review"] = {
            "decision": "accepted", "reviewer_type": "human-delegate",
            "reviewer": "ocr-reviewer", "decided_at": "2026-08-07",
            "rationale": "Compared with the source image.",
        }
        evidence["locator"] = {
            "source_id": "book-001", "locator_type": "ocr-region",
            "anchor": "figure-001#region-001", "content_hash": "abc123def456",
            "carrier": "docx-image", "image_sha256": f"sha256:{'2' * 64}",
            "ocr_run_id": "ocr-run-001", "ocr_record_id": "ocr-record-001",
            "region_id": "ocr-region-001", "bbox_px": [1, 2, 30, 10],
            "figure_id": "figure-001", "media_occurrence_id": "occurrence-001",
        }
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        evidence.pop("ocr_review")
        self.write_documents()
        self.assertIn("OCR_EVIDENCE_REVIEW_REQUIRED", self.error_codes())

    def test_validation_is_read_only(self):
        def snapshot():
            result = {}
            for path in sorted(self.root.rglob("*")):
                relative = path.relative_to(self.root).as_posix()
                if path.is_symlink():
                    result[relative] = ("symlink", os.readlink(path))
                elif path.is_dir():
                    result[relative] = ("directory", None)
                else:
                    result[relative] = (
                        "file", hashlib.sha256(path.read_bytes()).hexdigest()
                    )
            return result

        before = snapshot()
        validate_distillation(self.root)
        after = snapshot()
        self.assertEqual(before, after)

    def test_rejects_duplicate_ids_across_record_types(self):
        self.documents["concept-map.yml"]["relations"][0]["relation_id"] = "cl-001"
        self.write_documents()
        self.assertIn("DUPLICATE_ID", self.error_codes())

    def test_rejects_missing_foreign_key(self):
        self.documents["evidence-ledger.yml"]["claims"][0]["evidence_ids"] = ["ev-missing"]
        self.write_documents()
        self.assertIn("MISSING_FOREIGN_KEY", self.error_codes())

    def test_rejects_invalid_status(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["status"] = "verified"
        self.write_documents()
        self.assertIn("INVALID_STATUS", self.error_codes())

    def test_rejects_mismatched_distillation_id(self):
        self.documents["concept-map.yml"]["distillation_id"] = "another-v1"
        self.write_documents()
        self.assertIn("DISTILLATION_ID_MISMATCH", self.error_codes())

    def test_candidate_t4_may_have_pending_decision(self):
        set_rule_pending(self.documents)
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertFalse(any(item.code.startswith("T34_DECISION") for item in report.errors))

    def test_accepted_t4_requires_completed_human_decision(self):
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["human_decision"] = {
            "decision": "pending", "reviewer_type": None, "reviewer": None,
            "decided_at": None, "rationale": "", "gate_decision_id": None,
        }
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("T34_DECISION_NOT_ACCEPTED", codes)
        self.assertIn("T34_DECISION_INCOMPLETE", codes)

    def test_accepted_rule_rejects_needs_verification_evidence(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["status"] = "needs-verification"
        self.write_documents()
        self.assertIn("BLOCKED_DEPENDENCY", self.error_codes())

    def test_accepted_rule_rejects_blocking_quality_flag(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["quality_flags"] = [
            "nonblocking-looking-note"
        ]
        self.write_documents()
        self.assertIn("BLOCKED_DEPENDENCY", self.error_codes())

    def test_schema_version_must_be_integer_one(self):
        for invalid in (True, "1", 1.0, 2):
            with self.subTest(invalid=invalid):
                self.documents = self.fresh_documents()
                self.documents["concept-map.yml"]["schema_version"] = invalid
                self.write_documents()
                self.assertIn("SCHEMA_VERSION", self.error_codes())

    def test_rejects_id_surrounding_whitespace(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["evidence_id"] = " ev-001"
        self.write_documents()
        self.assertIn("INVALID_ID", self.error_codes())

    def test_rule_trigger_and_output_must_be_nonempty(self):
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["trigger"] = {"task": "  ", "signals": []}
        rule["output"] = ["  "]
        self.write_documents()
        empty_paths = {
            issue.path for issue in validate_distillation(self.root).errors
            if issue.code == "EMPTY_FIELD"
        }
        self.assertIn("capability-rules.yml.capability_rules[0].trigger", empty_paths)
        self.assertIn("capability-rules.yml.capability_rules[0].output", empty_paths)

    def test_rejects_duplicate_trigger_boundaries(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["should_trigger"] = ["Same", " same ", "third"]
        candidate["should_not_trigger"] = ["one", "one", "three"]
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("DUPLICATE_TRIGGER_CASE", codes)
        self.assertIn("DUPLICATE_NONTRIGGER_CASE", codes)

    def test_rejects_trigger_nontrigger_overlap(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["should_not_trigger"][0] = " REQUEST ONE "
        self.write_documents()
        self.assertIn("TRIGGER_BOUNDARY_OVERLAP", self.error_codes())

    def test_skill_candidates_allowed_only_in_capability_rules(self):
        self.documents["concept-map.yml"]["skill_candidates"] = []
        self.write_documents()
        self.assertIn("MISPLACED_SKILL_CANDIDATES", self.error_codes())

    def test_rejects_plural_locator_fields(self):
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["locators"] = [copy.deepcopy(evidence["locator"])]
        evidence["related_locators"] = [copy.deepcopy(evidence["locator"])]
        self.write_documents()
        issues = [
            item for item in validate_distillation(self.root).errors
            if item.code == "FORBIDDEN_LOCATOR_FIELD"
        ]
        self.assertEqual(2, len(issues))

    def test_every_accepted_record_requires_status_history(self):
        cases = [
            ("evidence-ledger.yml", "evidence"),
            ("evidence-ledger.yml", "claims"),
            ("concept-map.yml", "relations"),
            ("capability-rules.yml", "capability_rules"),
        ]
        for filename, key in cases:
            with self.subTest(filename=filename, key=key):
                self.documents = self.fresh_documents()
                self.documents[filename][key][0].pop("status_history")
                self.write_documents()
                self.assertIn("STATUS_HISTORY_REQUIRED", self.error_codes())

    def test_every_non_draft_candidate_requires_lifecycle_history(self):
        for lifecycle in ("review", "accepted", "deployed", "deprecated", "rejected"):
            with self.subTest(lifecycle=lifecycle):
                self.documents = self.fresh_documents()
                candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
                candidate["lifecycle"] = lifecycle
                candidate.pop("lifecycle_history")
                self.write_documents()
                self.assertIn("LIFECYCLE_HISTORY_REQUIRED", self.error_codes())

    def test_accepted_candidate_requires_accepted_rules(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["lifecycle"] = "accepted"
        candidate["lifecycle_history"].append({
            "from": "review",
            "to": "accepted",
            "decided_by": "human-reviewer",
            "decided_at": "2026-08-04",
            "rationale": "Accepted for the test.",
        })
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["status"] = "candidate"
        rule.pop("status_history")
        rule["human_decision"] = {
            "decision": "pending", "reviewer_type": None, "reviewer": None,
            "decided_at": None, "rationale": "", "gate_decision_id": None,
        }
        self.write_documents()
        self.assertIn("CANDIDATE_RULE_NOT_ACCEPTED", self.error_codes())

    def test_accepted_candidate_requires_at_least_one_rule(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["lifecycle"] = "accepted"
        candidate["lifecycle_history"].append({
            "from": "review", "to": "accepted", "decided_by": "human-reviewer",
            "decided_at": "2026-08-04", "rationale": "Accepted for the test."
        })
        candidate["rule_ids"] = []
        self.write_documents()
        self.assertIn("CANDIDATE_RULES_REQUIRED", self.error_codes())

    def test_no_accepted_rules_reports_not_applicable(self):
        set_rule_pending(self.documents)
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertIsNone(report.metrics["accepted_rule_traceability"])
        self.assertFalse(report.metrics["accepted_rule_traceability_applicable"])

    def test_project_policy_is_valid_source_position(self):
        self.documents["evidence-ledger.yml"]["claims"][0]["source_position"] = "project-policy"
        self.write_documents()
        self.assertNotIn("INVALID_ENUM", self.error_codes())

    def test_sources_manifest_is_opt_in(self):
        report = validate_distillation(self.root)
        self.assertNotIn("UNKNOWN_SOURCE_ID", {item.code for item in report.errors})
        manifest = self.root / "sources.yml"
        manifest_data = valid_sources_manifest()
        manifest_data["sources"][0]["id"] = "another-book"
        manifest.write_text(
            yaml.safe_dump(manifest_data),
            encoding="utf-8",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("UNKNOWN_SOURCE_ID", {item.code for item in report.errors})

    def test_sources_manifest_accepts_known_source(self):
        manifest = self.write_manifest()
        report = validate_distillation(self.root, manifest)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_markdown_locator_resolves_allowed_path_heading_and_hash(self):
        manifest = self.configure_markdown_policy()
        report = validate_distillation(self.root, manifest)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertEqual([], [item.as_dict() for item in report.warnings])
        self.assertEqual(1, report.metrics["markdown_locator_count"])
        self.assertEqual(1, report.metrics["markdown_locator_resolved"])
        self.assertTrue(report.metrics["markdown_locator_resolution_applicable"])

    def test_markdown_locator_accepts_related_path_and_line_range(self):
        manifest = self.configure_markdown_policy(
            repository_path="docs/related.md",
            local_path="docs/policy.md",
            related_local_paths=["docs/related.md"],
            anchor="docs/related.md:5-5#Review-Gate",
        )
        report = validate_distillation(self.root, manifest)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_markdown_locator_accepts_line_only_anchor(self):
        manifest = self.configure_markdown_policy(anchor="docs/policy.md:5")
        report = validate_distillation(self.root, manifest)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_markdown_locator_rejects_path_outside_source_allowlist(self):
        manifest = self.configure_markdown_policy(
            repository_path="docs/other.md",
            local_path="docs/policy.md",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("LOCATOR_PATH_NOT_ALLOWED", {item.code for item in report.errors})

    def test_markdown_locator_rejects_absolute_and_parent_paths(self):
        for anchor in ("/tmp/outside.md:1", "../outside.md:1"):
            with self.subTest(anchor=anchor):
                self.documents = self.fresh_documents()
                manifest = self.configure_markdown_policy(anchor=anchor)
                report = validate_distillation(self.root, manifest)
                self.assertIn(
                    "LOCATOR_ANCHOR_INVALID", {item.code for item in report.errors}
                )

    def test_markdown_locator_rejects_missing_allowed_file(self):
        manifest = self.configure_markdown_policy(write_source=False)
        report = validate_distillation(self.root, manifest)
        self.assertIn(
            "LOCATOR_SOURCE_FILE_MISSING", {item.code for item in report.errors}
        )

    def test_markdown_locator_rejects_non_utf8_source(self):
        manifest = self.configure_markdown_policy()
        (self.root / "docs" / "policy.md").write_bytes(b"\xff\xfe\x00")
        report = validate_distillation(self.root, manifest)
        self.assertIn("LOCATOR_SOURCE_READ_ERROR", {item.code for item in report.errors})

    def test_markdown_locator_rejects_raw_text_drift(self):
        manifest = self.configure_markdown_policy(
            raw_text="Changed policy text.",
            normalized_text="Stable policy text.",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("EVIDENCE_RAW_TEXT_MISMATCH", {item.code for item in report.errors})

    def test_markdown_locator_rejects_normalized_text_drift(self):
        manifest = self.configure_markdown_policy(
            raw_text="Stable policy text.",
            normalized_text="Changed policy text.",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn(
            "EVIDENCE_NORMALIZED_TEXT_MISMATCH",
            {item.code for item in report.errors},
        )

    def test_markdown_locator_requires_both_text_payloads(self):
        manifest = self.configure_markdown_policy()
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence.pop("raw_text")
        self.write_documents()
        report = validate_distillation(self.root, manifest)
        self.assertIn("EVIDENCE_TEXT_MISSING", {item.code for item in report.errors})

    def test_markdown_locator_rejects_source_slice_hash_mismatch(self):
        manifest = self.configure_markdown_policy()
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["locator"]["content_hash"] = "f" * 12
        self.write_documents()
        report = validate_distillation(self.root, manifest)
        self.assertIn("CONTENT_HASH_MISMATCH", {item.code for item in report.errors})

    def test_markdown_locator_rejects_missing_heading(self):
        manifest = self.configure_markdown_policy(
            anchor="docs/policy.md:5#absent-heading"
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("LOCATOR_HEADING_NOT_FOUND", {item.code for item in report.errors})

    def test_markdown_locator_rejects_text_outside_named_section(self):
        source_text = (
            "# Policy\n\n## First Section\nStable policy text.\n\n"
            "## Second Section\nOther text.\n"
        )
        manifest = self.configure_markdown_policy(
            source_text=source_text,
            anchor="docs/policy.md:4#second-section",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("LOCATOR_SECTION_MISMATCH", {item.code for item in report.errors})

    def test_markdown_locator_rejects_ambiguous_exact_text(self):
        source_text = (
            "# Policy\n\n## Review Gate\nStable policy text.\nStable policy text.\n"
        )
        manifest = self.configure_markdown_policy(
            source_text=source_text,
            anchor="docs/policy.md:3#review-gate",
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn("LOCATOR_TEXT_AMBIGUOUS", {item.code for item in report.errors})

    def test_markdown_locator_line_drift_is_warning_not_error(self):
        manifest = self.configure_markdown_policy(anchor="docs/policy.md:4#review-gate")
        report = validate_distillation(self.root, manifest)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertIn(
            "LOCATOR_LINE_HINT_DRIFT", {item.code for item in report.warnings}
        )

    def test_markdown_locator_rejects_out_of_range_line_hint(self):
        manifest = self.configure_markdown_policy(
            anchor="docs/policy.md:999#review-gate"
        )
        report = validate_distillation(self.root, manifest)
        self.assertIn(
            "LOCATOR_LINE_HINT_OUT_OF_RANGE", {item.code for item in report.errors}
        )

    def test_markdown_locator_resolution_remains_manifest_opt_in(self):
        self.configure_markdown_policy(write_source=False)
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertIsNone(report.metrics["markdown_locator_resolved"])
        self.assertFalse(report.metrics["markdown_locator_resolution_applicable"])

    def test_rejects_invalid_status_transition(self):
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["status_history"] = [{
            "from": "accepted",
            "to": "rejected",
            "decided_by": "human-reviewer",
            "decided_at": "2026-08-04",
            "rationale": "Invalid direct terminal transition.",
        }]
        evidence["status"] = "rejected"
        self.write_documents()
        self.assertIn("STATUS_HISTORY_INVALID", self.error_codes())

    def test_rejects_invalid_skill_lifecycle_transition(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["lifecycle_history"] = [{
            "from": "draft",
            "to": "deployed",
            "decided_by": "project-agent",
            "decided_at": "2026-08-04",
            "rationale": "Invalid skipped gates.",
        }]
        candidate["lifecycle"] = "deployed"
        self.write_documents()
        self.assertIn("STATUS_HISTORY_INVALID", self.error_codes())

    def test_rejects_missing_locator_components(self):
        del self.documents["evidence-ledger.yml"]["evidence"][0]["locator"][
            "ooxml_block_index"
        ]
        self.write_documents()
        self.assertIn("LOCATOR_INVALID", self.error_codes())

    def test_missing_required_file_is_input_error(self):
        (self.root / "concept-map.yml").unlink()
        with self.assertRaises(DistillationInputError) as context:
            validate_distillation(self.root)
        self.assertEqual("MISSING_FILE", context.exception.code)

    def test_invalid_yaml_is_input_error(self):
        (self.root / "concept-map.yml").write_text("relations: [\n", encoding="utf-8")
        with self.assertRaises(DistillationInputError) as context:
            validate_distillation(self.root)
        self.assertEqual("YAML_PARSE", context.exception.code)

    def test_gate_and_eval_files_are_required(self):
        for filename in ("gate-decisions.yml", "eval-runs.yml"):
            with self.subTest(filename=filename):
                (self.root / filename).unlink()
                with self.assertRaises(DistillationInputError) as context:
                    validate_distillation(self.root)
                self.assertEqual("MISSING_FILE", context.exception.code)
                self.write_documents()

    def test_accepted_candidate_with_gate_eval_chain_passes(self):
        accept_candidate(self.documents, self.root)
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertEqual(9, report.metrics["eval_run_count"])

    def test_accepted_candidate_requires_sources_manifest(self):
        accept_candidate(self.documents, self.root)
        self.write_documents()
        self.assertIn("SOURCES_MANIFEST_REQUIRED", self.error_codes())

    def test_accepted_candidate_requires_human_gate3_approval(self):
        accept_candidate(self.documents, self.root)
        self.documents["gate-decisions.yml"]["gate_decisions"][2]["reviewer_type"] = None
        self.write_documents()
        codes = {
            item.code for item in validate_distillation(self.root, self.write_manifest()).errors
        }
        self.assertIn("HUMAN_REVIEW_REQUIRED", codes)
        self.assertIn("GATE3_USER_APPROVAL_REQUIRED", codes)

    def test_accepted_candidate_requires_human_gate4_acceptance(self):
        accept_candidate(self.documents, self.root)
        self.documents["gate-decisions.yml"]["gate_decisions"][3]["decision"] = "revise"
        self.write_documents()
        codes = {
            item.code for item in validate_distillation(self.root, self.write_manifest()).errors
        }
        self.assertIn("GATE4_ACCEPTANCE_REQUIRED", codes)

    def test_gate4_rejects_failed_eval_run(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        run["outcome"] = "fail"
        run["score"] = 7
        self.write_documents()
        codes = {
            item.code for item in validate_distillation(self.root, self.write_manifest()).errors
        }
        self.assertIn("GATE4_EVAL_NOT_PASSED", codes)
        self.assertIn("GATE4_EVAL_COVERAGE", codes)

    def test_gate4_requires_three_cases_of_each_type(self):
        accept_candidate(self.documents, self.root)
        runs = self.documents["eval-runs.yml"]["eval_runs"]
        removed = next(item for item in runs if item["case_type"] == "trigger")
        runs.remove(removed)
        gate4 = self.documents["gate-decisions.yml"]["gate_decisions"][3]
        gate4["eval_run_ids"].remove(removed["eval_run_id"])
        self.write_documents()
        codes = {
            item.code for item in validate_distillation(self.root, self.write_manifest()).errors
        }
        self.assertIn("GATE4_EVAL_COVERAGE", codes)

    def test_gate4_requires_holdout_task(self):
        accept_candidate(self.documents, self.root)
        for run in self.documents["eval-runs.yml"]["eval_runs"]:
            run["holdout"] = False
        self.write_documents()
        codes = {
            item.code for item in validate_distillation(self.root, self.write_manifest()).errors
        }
        self.assertIn("GATE4_HOLDOUT_REQUIRED", codes)

    def test_accepted_rule_requires_complete_semantic_support(self):
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule.pop("semantic_support")
        self.write_documents()
        self.assertIn("SEMANTIC_SUPPORT_REQUIRED", self.error_codes())

        self.documents = self.fresh_documents()
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["semantic_support"]["output"] = []
        self.write_documents()
        self.assertIn("SEMANTIC_SUPPORT_INCOMPLETE", self.error_codes())

    def test_semantic_support_requires_existing_declared_foreign_keys(self):
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["semantic_support"]["checks"][0]["claim_ids"] = ["cl-missing"]
        self.write_documents()
        self.assertIn("MISSING_FOREIGN_KEY", self.error_codes())

        self.documents = self.fresh_documents()
        extra_claim = copy.deepcopy(self.documents["evidence-ledger.yml"]["claims"][0])
        extra_claim["claim_id"] = "cl-002"
        self.documents["evidence-ledger.yml"]["claims"].append(extra_claim)
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["semantic_support"]["checks"][0]["claim_ids"] = ["cl-002"]
        self.write_documents()
        self.assertIn("SEMANTIC_SUPPORT_UNDECLARED", self.error_codes())

    def test_accepted_claim_rejects_nonaccepted_evidence_without_rule(self):
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        evidence["status"] = "candidate"
        evidence.pop("status_history")
        relation = self.documents["concept-map.yml"]["relations"][0]
        relation["status"] = "candidate"
        relation.pop("status_history")
        set_rule_pending(self.documents)
        self.write_documents()
        self.assertIn("BLOCKED_DEPENDENCY", self.error_codes())

    def test_accepted_relation_rejects_nonaccepted_claim(self):
        claim = self.documents["evidence-ledger.yml"]["claims"][0]
        claim["status"] = "candidate"
        claim.pop("status_history")
        set_rule_pending(self.documents)
        self.write_documents()
        self.assertIn("BLOCKED_DEPENDENCY", self.error_codes())

    def test_accepted_relation_rejects_direct_nonaccepted_evidence(self):
        risky = copy.deepcopy(self.documents["evidence-ledger.yml"]["evidence"][0])
        risky["evidence_id"] = "ev-002"
        risky["status"] = "needs-verification"
        risky.pop("status_history")
        self.documents["evidence-ledger.yml"]["evidence"].append(risky)
        self.documents["concept-map.yml"]["relations"][0]["evidence_ids"] = ["ev-002"]
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertIn("BLOCKED_DEPENDENCY", {item.code for item in report.errors})
        self.assertLess(report.metrics["accepted_rule_traceability"], 1.0)

    def test_project_policy_claim_requires_controlling_source_role(self):
        self.documents["evidence-ledger.yml"]["claims"][0]["source_position"] = "project-policy"
        self.write_documents()
        wrong = validate_distillation(self.root, self.write_manifest("primary-book"))
        self.assertIn("PROJECT_POLICY_SOURCE_ROLE", {item.code for item in wrong.errors})
        correct = validate_distillation(
            self.root, self.write_manifest("controlling-requirements")
        )
        self.assertTrue(correct.ok, [item.as_dict() for item in correct.errors])

    def test_valid_correction_overlay_and_claim_link_pass(self):
        add_valid_correction(self.documents)
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])
        self.assertEqual(1, report.metrics["correction_count"])

    def test_correction_overlay_requires_existing_evidence_and_matching_locator(self):
        add_valid_correction(self.documents)
        correction = self.documents["correction-overlay.yml"]["corrections"][0]
        correction["evidence_id"] = "ev-missing"
        correction["locator"]["ooxml_block_index"] = 99
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("MISSING_FOREIGN_KEY", codes)

        correction["evidence_id"] = "ev-001"
        self.write_documents()
        self.assertIn("CORRECTION_LOCATOR_MISMATCH", self.error_codes())

    def test_accepted_claim_rejects_pending_correction(self):
        add_valid_correction(self.documents)
        correction = self.documents["correction-overlay.yml"]["corrections"][0]
        correction["status"] = "needs-verification"
        correction["human_decision"] = {
            "decision": "pending", "reviewer": None, "decided_at": None, "rationale": ""
        }
        correction["resulting_value"] = None
        self.write_documents()
        self.assertIn("BLOCKED_CORRECTION", self.error_codes())

    def test_rejects_template_placeholders(self):
        self.documents["evidence-ledger.yml"]["distillation_id"] = "example-concept-book-v1"
        self.write_documents()
        self.assertIn("PLACEHOLDER_VALUE", self.error_codes())

    def test_rejects_duplicate_and_overlong_candidate_names(self):
        duplicate = copy.deepcopy(
            self.documents["capability-rules.yml"]["skill_candidates"][0]
        )
        duplicate["candidate_id"] = "candidate-002"
        self.documents["capability-rules.yml"]["skill_candidates"].append(duplicate)
        self.write_documents()
        self.assertIn("DUPLICATE_SKILL_NAME", self.error_codes())

        self.documents = self.fresh_documents()
        self.documents["capability-rules.yml"]["skill_candidates"][0]["name"] = "a" * 65
        self.write_documents()
        self.assertIn("INVALID_SKILL_NAME", self.error_codes())

    def test_rejects_empty_scope_heading_path_and_bad_content_hash(self):
        claim = self.documents["evidence-ledger.yml"]["claims"][0]
        evidence = self.documents["evidence-ledger.yml"]["evidence"][0]
        claim["scope"] = []
        evidence["locator"]["heading_path"] = []
        evidence["locator"]["content_hash"] = "not-a-hash"
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("EMPTY_FIELD", codes)
        self.assertIn("LOCATOR_INVALID", codes)
        self.assertIn("CONTENT_HASH_INVALID", codes)

    def test_candidate_rule_requires_complete_semantic_support(self):
        set_rule_pending(self.documents)
        self.documents["capability-rules.yml"]["capability_rules"][0].pop(
            "semantic_support"
        )
        self.write_documents()
        self.assertIn("SEMANTIC_SUPPORT_REQUIRED", self.error_codes())

    def test_rejected_rule_may_omit_semantic_support(self):
        reject_rule_at_gate3(self.documents)
        self.documents["gate-decisions.yml"]["materializations"] = []
        self.documents["capability-rules.yml"]["capability_rules"][0].pop(
            "semantic_support"
        )
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_accepted_inferred_relation_requires_user_decision(self):
        relation = self.documents["concept-map.yml"]["relations"][0]
        relation["relation_status"] = "inferred"
        self.write_documents()
        self.assertIn("RELATION_HUMAN_DECISION_REQUIRED", self.error_codes())

        relation["human_decision"] = {
            "decision": "accepted", "reviewer_type": "human-delegate",
            "reviewer": "delegate", "decided_at": "2026-08-04",
            "rationale": "Reviewed inference.",
        }
        self.write_documents()
        self.assertIn("RELATION_HUMAN_DECISION_REQUIRED", self.error_codes())

        relation["human_decision"]["reviewer_type"] = "user"
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_gate4_acceptance_is_checked_before_candidate_acceptance(self):
        accept_candidate(self.documents, self.root)
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["lifecycle"] = "review"
        candidate["lifecycle_history"].pop()
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        run["outcome"] = "fail"
        run["score"] = 7
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("GATE4_EVAL_NOT_PASSED", codes)
        self.assertIn("GATE4_EVAL_COVERAGE", codes)

    def test_gate3_approval_requires_all_rule_decisions_and_user(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["rule_decisions"] = []
        gate3["reviewer_type"] = "human-delegate"
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("GATE3_RULE_DECISIONS_REQUIRED", codes)
        self.assertIn("GATE3_RULE_COVERAGE", codes)
        self.assertIn("GATE3_USER_APPROVAL_REQUIRED", codes)

    def test_gate3_rule_writeback_must_match_authoritative_decision(self):
        rule = self.documents["capability-rules.yml"]["capability_rules"][0]
        rule["status"] = "candidate"
        rule["human_decision"]["gate_decision_id"] = "gate-decision-002"
        rule["status_history"][-1]["decided_by"] = "someone-else"
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("GATE3_RULE_STATE_MISMATCH", codes)
        self.assertIn("GATE3_RULE_DECISION_MISMATCH", codes)
        self.assertIn("GATE3_RULE_HISTORY_MISMATCH", codes)

    def test_current_gate3_approval_requires_complete_snapshot(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3.pop("approval_snapshot")
        self.write_documents(sync_approval_snapshot=False)
        self.assertIn("GATE3_APPROVAL_SNAPSHOT_REQUIRED", self.error_codes())

        malformed_values = (
            [],
            {"contract": GATE3_APPROVAL_SNAPSHOT_CONTRACT},
            {
                "contract": "gate3-approval-snapshot:v999",
                "candidate_path": FIXTURE_CANDIDATE_PATH,
                "candidate_hash": f"sha256:{'A' * 64}",
                "governance_hashes": [],
                "unexpected": True,
            },
        )
        for malformed in malformed_values:
            with self.subTest(malformed=repr(malformed)[:80]):
                self.documents = self.fresh_documents()
                self.write_documents()
                self.documents["gate-decisions.yml"]["gate_decisions"][2][
                    "approval_snapshot"
                ] = malformed
                self.write_documents(sync_approval_snapshot=False)
                report = validate_distillation(self.root)
                self.assertFalse(report.ok)
                self.assertTrue(report.errors)

    def test_gate3_approval_snapshot_rejects_candidate_path_and_hash_drift(self):
        snapshot = self.documents["gate-decisions.yml"]["gate_decisions"][2][
            "approval_snapshot"
        ]
        snapshot["candidate_path"] = "candidates/wrong-name"
        self.write_documents(sync_approval_snapshot=False)
        codes = self.error_codes()
        self.assertIn("GATE3_APPROVAL_CANDIDATE_PATH_MISMATCH", codes)
        self.assertIn("GATE3_APPROVAL_CANDIDATE_TREE_INVALID", codes)

        self.documents = self.fresh_documents()
        self.write_documents()
        (self.root / FIXTURE_CANDIDATE_PATH / "SKILL.md").write_text(
            FIXTURE_SKILL + "\nApproval drift.\n", encoding="utf-8"
        )
        self.assertIn("GATE3_APPROVAL_CANDIDATE_HASH_MISMATCH", self.error_codes())

    def test_gate3_approval_snapshot_rejects_governance_hash_drift(self):
        evidence_path = self.root / "evidence-ledger.yml"
        evidence_path.write_bytes(evidence_path.read_bytes() + b"\n")
        self.assertIn(
            "GATE3_APPROVAL_GOVERNANCE_HASH_MISMATCH", self.error_codes()
        )

    def test_gate3_approval_snapshot_rejects_symlinked_governance_file(self):
        concept_path = self.root / "concept-map.yml"
        target = self.root / "concept-map-target.yml"
        target.write_bytes(concept_path.read_bytes())
        concept_path.unlink()
        try:
            os.symlink(target.name, concept_path)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertIn(
            "GATE3_APPROVAL_GOVERNANCE_FILE_INVALID", self.error_codes()
        )

    def test_historical_gate3_approval_may_omit_snapshot(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["is_current"] = False
        gate3.pop("approval_snapshot", None)
        replacement = copy.deepcopy(gate3)
        replacement.update({
            "decision_id": "gate-decision-004",
            "sequence": 4,
            "supersedes": "gate-decision-003",
            "is_current": True,
        })
        self.documents["gate-decisions.yml"]["gate_decisions"].append(replacement)
        self.documents["capability-rules.yml"]["capability_rules"][0][
            "human_decision"
        ]["gate_decision_id"] = "gate-decision-004"
        self.documents["gate-decisions.yml"]["materializations"][0][
            "gate3_decision_id"
        ] = "gate-decision-004"
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertTrue(report.ok, [item.as_dict() for item in report.errors])

    def test_completed_materialization_must_match_approval_snapshot(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["candidate_path"] = "alternate/review-book-task"
        self.write_documents()
        self.assertIn("MATERIALIZATION_APPROVAL_PATH_MISMATCH", self.error_codes())

        self.documents = self.fresh_documents()
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["candidate_hash"] = f"sha256:{'1' * 64}"
        self.write_documents()
        self.assertIn("MATERIALIZATION_APPROVAL_HASH_MISMATCH", self.error_codes())

    def test_completed_eval_rejects_gate3_rejected_rule(self):
        accept_candidate(self.documents, self.root)
        reject_rule_at_gate3(self.documents)
        self.write_documents()
        self.assertIn("EVAL_RULE_NOT_APPROVED", self.error_codes())

    def test_gate_decision_chain_rejects_bad_sequence_current_and_supersedes(self):
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        replacement = copy.deepcopy(gate3)
        gate3["is_current"] = False
        replacement.update({
            "decision_id": "gate-decision-003b",
            "sequence": 4,
            "supersedes": "gate-decision-001",
            "is_current": True,
            "decision": "pending",
            "reviewer_type": None,
            "reviewer": None,
            "decided_at": None,
            "rule_decisions": [],
        })
        self.documents["gate-decisions.yml"]["gate_decisions"].append(replacement)
        self.write_documents()
        self.assertIn("GATE_SUPERSEDES_INVALID", self.error_codes())

        replacement["sequence"] = 3
        self.write_documents()
        self.assertIn("GATE_SEQUENCE_INVALID", self.error_codes())

        gate3["is_current"] = True
        replacement["sequence"] = 4
        replacement["supersedes"] = "gate-decision-003"
        self.write_documents()
        self.assertIn("GATE_CURRENT_INVALID", self.error_codes())

    def test_completed_eval_requires_current_gate3_approval(self):
        accept_candidate(self.documents, self.root)
        gate3 = self.documents["gate-decisions.yml"]["gate_decisions"][2]
        gate3["is_current"] = False
        replacement = copy.deepcopy(gate3)
        replacement.update({
            "decision_id": "gate-decision-005", "sequence": 5,
            "supersedes": "gate-decision-003", "is_current": True,
            "decision": "pending", "reviewer_type": None, "reviewer": None,
            "decided_at": None, "rule_decisions": [],
        })
        self.documents["gate-decisions.yml"]["gate_decisions"].append(replacement)
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("EVAL_CURRENT_GATE3_REQUIRED", codes)
        self.assertIn("MATERIALIZATION_CURRENT_GATE3_REQUIRED", codes)

    def test_completed_materialization_requires_quick_validation_pass(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["quick_validation"]["status"] = "fail"
        self.write_documents()
        self.assertIn("MATERIALIZATION_QUICK_VALIDATION_REQUIRED", self.error_codes())

    def test_completed_materialization_recomputes_and_matches_tree_hash(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["candidate_hash"] = f"sha256:{'0' * 64}"
        self.write_documents()
        self.assertIn("MATERIALIZATION_CANDIDATE_HASH_MISMATCH", self.error_codes())

        materialization["candidate_hash"] = candidate_tree_sha256(
            self.root, FIXTURE_CANDIDATE_PATH
        ).removeprefix("sha256:")
        self.write_documents()
        self.assertIn("MATERIALIZATION_CANDIDATE_HASH_INVALID", self.error_codes())

    def test_completed_materialization_rejects_unsafe_or_missing_candidate_path(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        for unsafe in ("../review-book-task", "/tmp/review-book-task"):
            with self.subTest(candidate_path=unsafe):
                materialization["candidate_path"] = unsafe
                self.write_documents()
                self.assertIn(
                    "MATERIALIZATION_CANDIDATE_PATH_INVALID", self.error_codes()
                )

        materialization["candidate_path"] = "candidates/missing-review-book-task"
        self.write_documents()
        self.assertIn("MATERIALIZATION_CANDIDATE_PATH_INVALID", self.error_codes())

    def test_completed_materialization_path_must_match_candidate_name(self):
        candidate = self.documents["capability-rules.yml"]["skill_candidates"][0]
        candidate["name"] = "other-book-task"
        self.write_documents()
        self.assertIn("MATERIALIZATION_CANDIDATE_PATH_MISMATCH", self.error_codes())

    def test_completed_materialization_rejects_symlink_and_cache_tree_entries(self):
        candidate_dir = self.root / FIXTURE_CANDIDATE_PATH
        link = candidate_dir / "linked-skill.md"
        try:
            os.symlink(candidate_dir / "SKILL.md", link)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertIn("MATERIALIZATION_CANDIDATE_TREE_INVALID", self.error_codes())
        link.unlink()

        (candidate_dir / "stale.pyc").write_bytes(b"cache")
        self.assertIn("MATERIALIZATION_CANDIDATE_TREE_INVALID", self.error_codes())

    def test_eval_hash_must_match_completed_materialization(self):
        accept_candidate(self.documents, self.root)
        self.documents["eval-runs.yml"]["eval_runs"][0]["candidate_hash"] = "0" * 64
        self.write_documents()
        self.assertIn("EVAL_MATERIALIZATION_MISMATCH", self.error_codes())

    def test_legacy_materialization_cannot_support_completed_eval(self):
        accept_candidate(self.documents, self.root)
        self.documents["gate-decisions.yml"]["materializations"][0][
            "status"
        ] = "legacy-quarantined"
        self.write_documents()
        self.assertIn("EVAL_LEGACY_MATERIALIZATION", self.error_codes())

    def test_duplicate_yaml_mapping_key_is_input_error(self):
        (self.root / "concept-map.yml").write_text(
            "schema_version: 1\n"
            "distillation_id: validator-test-v1\n"
            "relations: []\n"
            "relations: []\n",
            encoding="utf-8",
        )
        with self.assertRaises(DistillationInputError) as context:
            validate_distillation(self.root)
        self.assertEqual("YAML_DUPLICATE_KEY", context.exception.code)

    def test_quick_validation_requires_exact_validator_and_candidate_hash(self):
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["quick_validation"]["validator"] = "another-validator.py"
        self.write_documents()
        self.assertIn("MATERIALIZATION_QUICK_VALIDATION_INVALID", self.error_codes())

        self.documents = self.fresh_documents()
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["quick_validation"]["candidate_hash"] = f"sha256:{'0' * 64}"
        self.write_documents()
        self.assertIn(
            "MATERIALIZATION_QUICK_VALIDATION_HASH_MISMATCH", self.error_codes()
        )

        self.documents = self.fresh_documents()
        materialization = self.documents["gate-decisions.yml"]["materializations"][0]
        materialization["quick_validation"].pop("candidate_hash")
        self.write_documents()
        codes = self.error_codes()
        self.assertIn("MISSING_FIELD", codes)
        self.assertIn("MATERIALIZATION_QUICK_VALIDATION_REQUIRED", codes)

    def test_completed_materialization_requires_valid_skill_contract(self):
        candidate_dir = self.root / FIXTURE_CANDIDATE_PATH
        cases = (
            ("missing", None, "MATERIALIZATION_SKILL_FILE_MISSING"),
            (
                "duplicate-key",
                "---\nname: review-book-task\nname: duplicate\n"
                "description: Test candidate.\n---\n\n# Body\n",
                "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            ),
            (
                "extra-key",
                "---\nname: review-book-task\ndescription: Test candidate.\n"
                "lifecycle: review\n---\n\n# Body\n",
                "MATERIALIZATION_SKILL_FRONTMATTER_INVALID",
            ),
            (
                "name-mismatch",
                "---\nname: another-task\ndescription: Test candidate.\n---\n\n# Body\n",
                "MATERIALIZATION_SKILL_NAME_MISMATCH",
            ),
            (
                "empty-body",
                "---\nname: review-book-task\ndescription: Test candidate.\n---\n",
                "MATERIALIZATION_SKILL_BODY_INVALID",
            ),
        )
        for label, payload, expected_code in cases:
            with self.subTest(label=label):
                self.write_candidate_contract()
                skill_path = candidate_dir / "SKILL.md"
                if payload is None:
                    skill_path.unlink()
                else:
                    skill_path.write_text(payload, encoding="utf-8")
                self.documents = self.fresh_documents()
                self.write_documents()
                self.assertIn(expected_code, self.error_codes())

    def test_completed_materialization_requires_valid_eval_definitions(self):
        trigger_path = (
            self.root / FIXTURE_CANDIDATE_PATH / "evals" / "trigger-cases.json"
        )
        non_json_constant = (
            json.dumps(FIXTURE_TRIGGER_DEFINITION, ensure_ascii=False).rstrip("}")
            + ', "extra": NaN}'
        )
        cases = (
            ("missing", None, "MATERIALIZATION_EVAL_DEFINITION_MISSING"),
            ("invalid-json", "{", "MATERIALIZATION_EVAL_DEFINITION_INVALID"),
            (
                "duplicate-json-key",
                '{"schema_version":1,"skill_name":"review-book-task",'
                '"skill_name":"duplicate","should_trigger":[],"should_not_trigger":[]}',
                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
            ),
            (
                "non-json-constant",
                non_json_constant,
                "MATERIALIZATION_EVAL_DEFINITION_INVALID",
            ),
        )
        for label, payload, expected_code in cases:
            with self.subTest(label=label):
                self.write_candidate_contract()
                if payload is None:
                    trigger_path.unlink()
                else:
                    trigger_path.write_text(payload, encoding="utf-8")
                self.documents = self.fresh_documents()
                self.write_documents()
                self.assertIn(expected_code, self.error_codes())

    def test_completed_eval_artifact_paths_are_confined_regular_files(self):
        linked_path = self.root / "fixtures" / "linked-trigger.json"
        linked_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(self.root / "fixtures" / "trigger-1.json", linked_path)
            symlink_available = True
        except (OSError, NotImplementedError):
            symlink_available = False
        cases = [
            ("parent", "../fixture.json", "EVAL_ARTIFACT_PATH_INVALID"),
            (
                "absolute",
                str((self.root / "fixtures" / "trigger-1.json").resolve()),
                "EVAL_ARTIFACT_PATH_INVALID",
            ),
            ("missing", "fixtures/missing.json", "EVAL_ARTIFACT_MISSING"),
            ("directory", "fixtures", "EVAL_ARTIFACT_NOT_REGULAR"),
        ]
        if symlink_available:
            cases.append(
                ("symlink", "fixtures/linked-trigger.json", "EVAL_ARTIFACT_SYMLINK")
            )
        for label, artifact_path, expected_code in cases:
            with self.subTest(label=label):
                self.documents = self.fresh_documents()
                accept_candidate(self.documents, self.root)
                self.documents["eval-runs.yml"]["eval_runs"][0][
                    "fixture_path"
                ] = artifact_path
                self.write_documents()
                self.assertIn(expected_code, self.error_codes())

    def test_completed_eval_recomputes_full_artifact_hashes(self):
        artifact_hash_keys = (
            "fixture_hash",
            "baseline_output_hash",
            "with_skill_output_hash",
        )
        for hash_key in artifact_hash_keys:
            with self.subTest(hash_key=hash_key, invalid="short"):
                self.documents = self.fresh_documents()
                accept_candidate(self.documents, self.root)
                self.documents["eval-runs.yml"]["eval_runs"][0][hash_key] = "a" * 12
                self.write_documents()
                self.assertIn("EVAL_ARTIFACT_HASH_INVALID", self.error_codes())
            with self.subTest(hash_key=hash_key, invalid="mismatch"):
                self.documents = self.fresh_documents()
                accept_candidate(self.documents, self.root)
                self.documents["eval-runs.yml"]["eval_runs"][0][hash_key] = "0" * 64
                self.write_documents()
                self.assertIn("EVAL_ARTIFACT_HASH_MISMATCH", self.error_codes())

    def test_completed_eval_case_must_match_linked_definition(self):
        cases = (
            ("unknown", "trigger", "unknown-case", None, "EVAL_CASE_NOT_DEFINED"),
            (
                "wrong-type",
                "trigger",
                "nontrigger-1",
                None,
                "EVAL_CASE_TYPE_MISMATCH",
            ),
            (
                "holdout-mismatch",
                "task",
                "task-1",
                False,
                "EVAL_CASE_HOLDOUT_MISMATCH",
            ),
        )
        for label, case_type, case_id, holdout, expected_code in cases:
            with self.subTest(label=label):
                self.documents = self.fresh_documents()
                accept_candidate(self.documents, self.root)
                run = self.documents["eval-runs.yml"]["eval_runs"][0]
                run["case_type"] = case_type
                run["case_id"] = case_id
                if holdout is not None:
                    run["holdout"] = holdout
                self.write_documents()
                self.assertIn(expected_code, self.error_codes())

    def test_noncompleted_eval_does_not_require_replay_artifacts(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        run.update({
            "status": "blocked",
            "outcome": None,
            "fixture_path": "fixtures/missing.json",
            "fixture_hash": None,
            "baseline_output_path": None,
            "baseline_output_hash": None,
            "with_skill_output_path": None,
            "with_skill_output_hash": None,
            "reviewer_type": None,
            "reviewer": None,
            "completed_at": None,
        })
        self.write_documents()
        codes = self.error_codes()
        self.assertFalse(any(code.startswith("EVAL_ARTIFACT_") for code in codes))

    def test_nested_malformed_values_return_errors_instead_of_crashing(self):
        mutations = (
            lambda docs: docs["gate-decisions.yml"]["materializations"][0].update(
                {"rule_ids": [["rule-001"]]}
            ),
            lambda docs: docs["capability-rules.yml"]["skill_candidates"][0].update(
                {"lifecycle": []}
            ),
            lambda docs: docs["gate-decisions.yml"]["gate_decisions"][2].update(
                {"candidate_id": []}
            ),
            lambda docs: docs["evidence-ledger.yml"]["claims"][0].update(
                {"evidence_ids": [["ev-001"]]}
            ),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                self.documents = self.fresh_documents()
                mutate(self.documents)
                self.write_documents()
                report = validate_distillation(self.root)
                self.assertFalse(report.ok)
                self.assertTrue(report.errors)

    def test_recursive_yaml_alias_returns_structured_error(self):
        recursive_scope = []
        recursive_scope.append(recursive_scope)
        self.documents["evidence-ledger.yml"]["claims"][0][
            "scope"
        ] = recursive_scope
        self.write_documents()
        report = validate_distillation(self.root)
        self.assertFalse(report.ok)
        self.assertTrue(report.errors)

    def test_quality_issue_requires_correction_overlay(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["quality_flags"] = [
            "ocr-risk"
        ]
        self.write_documents()
        self.assertIn("CORRECTION_OVERLAY_REQUIRED", self.error_codes())

    def test_accepted_histories_must_start_from_null(self):
        self.documents["evidence-ledger.yml"]["evidence"][0]["status_history"].pop(0)
        self.write_documents()
        self.assertIn("STATUS_HISTORY_INVALID", self.error_codes())

        self.documents = self.fresh_documents()
        accept_candidate(self.documents, self.root)
        self.documents["capability-rules.yml"]["skill_candidates"][0][
            "lifecycle_history"
        ].pop(0)
        self.write_documents()
        self.assertIn("STATUS_HISTORY_INVALID", self.error_codes())


    def test_completed_eval_rejects_placeholder_fixture_even_with_matching_hash(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        payload = b"fixture:trigger-1"
        (self.root / run["fixture_path"]).write_bytes(payload)
        run["fixture_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn(
            "EVAL_FIXTURE_CONTRACT_INVALID", {item.code for item in report.errors}
        )

    def test_completed_eval_rejects_fixture_prompt_embedding_expected_behavior(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][6]  # task-1 (holdout)
        fixture_path = self.root / run["fixture_path"]
        fixture = json.loads(fixture_path.read_text())
        fixture["input_payload"] = {
            "prompt": "Representative task 1. Stay within the reviewed source scope."
        }
        payload = (json.dumps(fixture, sort_keys=True) + "\n").encode()
        fixture_path.write_bytes(payload)
        run["fixture_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn(
            "EVAL_FIXTURE_PROMPT_LEAKAGE", {item.code for item in report.errors}
        )

    def test_completed_eval_rejects_fixture_prompt_embedding_rubric_dimension(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        fixture_path = self.root / run["fixture_path"]
        fixture = json.loads(fixture_path.read_text())
        fixture["input_payload"] = {
            "prompt": "Representative task 1. Please ensure source-layer-separation."
        }
        payload = (json.dumps(fixture, sort_keys=True) + "\n").encode()
        fixture_path.write_bytes(payload)
        run["fixture_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn(
            "EVAL_FIXTURE_PROMPT_LEAKAGE", {item.code for item in report.errors}
        )

    def test_completed_eval_rejects_strict_json_fixture_placeholder(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        fixture_path = self.root / run["fixture_path"]
        fixture = json.loads(fixture_path.read_text())
        fixture["input_payload"] = {"source_excerpt": "TODO"}
        payload = (json.dumps(fixture, sort_keys=True) + "\n").encode()
        fixture_path.write_bytes(payload)
        run["fixture_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn("PLACEHOLDER_VALUE", {item.code for item in report.errors})

    def test_completed_eval_rejects_strict_json_output_placeholder(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        output_path = self.root / run["baseline_output_path"]
        output = json.loads(output_path.read_text())
        output["response"] = "placeholder"
        payload = (json.dumps(output, sort_keys=True) + "\n").encode()
        output_path.write_bytes(payload)
        run["baseline_output_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn("PLACEHOLDER_VALUE", {item.code for item in report.errors})

    def test_completed_eval_rejects_case_definition_hash_mismatch(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        run["case_definition_hash"] = "sha256:" + "f" * 64
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn(
            "EVAL_CASE_DEFINITION_HASH_MISMATCH", {item.code for item in report.errors}
        )

    def test_completed_eval_rejects_unbound_rubric_threshold(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        run["pass_threshold"] = 1
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn("EVAL_RUBRIC_MISMATCH", {item.code for item in report.errors})

    def test_completed_eval_rejects_output_identity_mismatch(self):
        accept_candidate(self.documents, self.root)
        run = self.documents["eval-runs.yml"]["eval_runs"][0]
        output_path = self.root / run["with_skill_output_path"]
        output = json.loads(output_path.read_text())
        output["case_id"] = "different-case"
        payload = (json.dumps(output, sort_keys=True) + "\n").encode()
        output_path.write_bytes(payload)
        run["with_skill_output_hash"] = hashlib.sha256(payload).hexdigest()
        self.write_documents()
        report = validate_distillation(self.root, self.write_manifest())
        self.assertIn(
            "EVAL_OUTPUT_CONTRACT_MISMATCH", {item.code for item in report.errors}
        )

    def test_correction_completed_decision_rejects_agent_or_untyped_reviewer(self):
        add_valid_correction(self.documents)
        correction = self.documents["correction-overlay.yml"]["corrections"][0]
        correction["human_decision"].pop("reviewer_type")
        correction["human_decision"]["reviewer"] = "project-agent"
        self.write_documents()
        self.assertIn("CORRECTION_DECISION_INVALID", self.error_codes())


if __name__ == "__main__":
    unittest.main()
