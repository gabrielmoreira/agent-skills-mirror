---
name: tdd-guide
description: Test-driven development wrapper for vibe coding flow. Enforces RED -> GREEN -> REFACTOR and >=80% coverage target.
---

# tdd-guide (Codex Compatibility)

Use this skill for all feature work, bug fixes, and refactors that change behavior.

## Core Rule

No production code before a failing test.

## Workflow

1. RED
- Write one failing test for one behavior.
- Confirm the failure is expected.

2. GREEN
- Implement the minimal code to pass.
- Re-run tests and keep scope narrow.

3. REFACTOR
- Improve structure/naming without changing behavior.
- Keep all tests green.

4. COVERAGE
- Verify coverage target (recommended >=80% for lines/functions/branches).
- Add missing tests for edge/error paths.

## Minimum Test Set

- Unit: public functions and core logic.
- Integration: API/data/service boundaries.
- E2E: critical user path only when relevant.

## Required Edge Cases

- Null/undefined input
- Empty values
- Invalid types
- Boundary values
- Error paths (network/DB/file)
- Concurrency-sensitive behavior

## Vibe Integration

- Primary coding skill in M-grade flow.
- Compatible fallback target for `everything-claude-code:tdd-guide`.
- For richer TDD patterns, combine with `test-driven-development`.