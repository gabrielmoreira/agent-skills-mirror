---
name: dde-ext-python-testing
description: "DDE subordinate extension. Python pytest-based test design/execution workflow with strict DDE write gating."
---

# DDE Extension: Python Testing

Skill Version: v0.1

## Authority Chain
- Commander: `dde-bootstrap`
- Write gate: `dde-code-guard`
- This skill is execution-capable but write-constrained.

## When to Use
- Add/fix pytest coverage for Python modules
- Reproduce and lock regressions with tests
- Validate Python behavior after refactor

## Execution Scope
Allowed:
- Analyze test topology and coverage gaps
- Design pytest cases/fixtures/markers
- Run pytest and summarize failures

Write-sensitive actions:
- Modifying `*.py`, `tests/*.py`, pytest configs
- Must be handed off to `dde-code-guard`

## Mandatory Flow
1. Define behavior to protect.
2. Inspect existing tests and gaps.
3. Run targeted tests, then broader checks.
4. If file edits needed, emit handoff:

`DDE_EXTENSION_HANDOFF_REQUIRED`

Fields:
- Reason
- Target files
- New/updated test intent
- Risk and rollback note

5. Wait for `[APPROVED]` in guard flow before write.

## Output Contract
- Coverage gap summary
- Failure clusters
- Minimal test patch proposal
- Handoff block when write is needed
