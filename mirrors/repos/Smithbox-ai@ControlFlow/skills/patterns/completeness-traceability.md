# Completeness Traceability Patterns

## Purpose
Verify that every requirement is addressed by a task and every task is justified by a requirement. Use during plan review and implementation verification.

## Requirements Traceability Matrix (RTM)

Build a two-column cross-reference before implementation begins:

| Requirement ID | Covering Task(s) | Status |
|---|---|---|
| REQ-001 | Phase 2 Step 3 | Covered |
| REQ-002 | Phase 1 Step 1, Phase 3 Step 2 | Covered |
| REQ-003 | — | **Orphaned** |

Rules:
- Every item in Scope IN must appear as a requirement.
- Every item in Scope OUT must have zero covering tasks.
- Any requirement with no covering task is an **orphaned requirement** — BLOCKING.

## Orphaned Requirement Detection

Signal: a scope item that has no corresponding file path, function change, or test in any phase.

Detection steps:
1. List all items from Scope IN (or Success Criteria if no explicit scope).
2. For each item, grep plan phases for file or function references that address it.
3. Items with zero matches are orphaned.

Emit a MAJOR finding for each orphaned requirement.

## Reverse Trace (Task Justification)

Every planned task must trace to at least one requirement:
- Phase X, Step Y modifies `foo.ts` → which requirement does this satisfy?
- If no requirement maps to a task, the task is **scope creep** — MINOR finding unless it modifies a file not in the approved scope.

## Out-of-Scope Absence Verification

For each item listed in Scope OUT, verify that no phase steps modify those files or behaviors. Any phase touching an out-of-scope item is a scope leak — MAJOR finding.

## Coverage Percentage

```
coverage = (requirements with ≥1 covering task) / (total requirements) × 100
```

- ≥ 95%: Completeness dimension score 5
- 85–94%: Score 3–4
- < 85%: Score ≤ 2 — flag as Completeness gap

## Acceptance Criteria Mapping

Every success criterion in the plan must map to at least one acceptance test:

| Success Criterion | Test Location | Test Type |
|---|---|---|
| "No stale references in governance docs" | Phase 1 Tests section | grep / validate.mjs check |
| "7 skill files in index" | Phase 2 Tests section | validate.mjs Pass 5 |

Missing test coverage for a success criterion → MINOR finding.
