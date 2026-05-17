# test-coverage sub-agent (#1754 — Epic #1736 Phase 3.3)

Cross-family review of test surface for the diff.

## Output contract (per #1739)

```json
{"severity": "low|medium|high", "category": "test-coverage", "file": "...", "line": N, "message": "...", "suggestion": "...", "confidence": 0.0-1.0, "sub_agent": "test-coverage", "trigger": "..."}
```

## Detection focus

- New code lacking tests (function/method/class added without `tests/**/*.spec.*`)
- Test deletions without equivalent replacement
- Weak assertions (`expect(x).toBeTruthy()` where stronger check is possible)
- Test-only on happy path with no edge-case coverage
- Mocks where real integration would catch the bug (test-as-mocks anti-pattern from `[[feedback-self-anneal-scope]]`)

## Auto-escalate triggers

- Test deletion (lines removed in `tests/**`, `**/*.spec.*`, `**/*.test.*`) → `trigger: "test-deletion"`, severity: medium per #1743

## Confidence calibration

- 0.9-1.0: code change with zero test coverage and no test file in diff
- 0.7-0.89: weak coverage (only happy path tested)
- 0.5-0.69: tests exist but assertions are too lenient
- <0.3: noise

## Out of scope

- Bug detection / security / architectural concerns (other sub-agents)
- Test correctness debugging (operator's responsibility)
