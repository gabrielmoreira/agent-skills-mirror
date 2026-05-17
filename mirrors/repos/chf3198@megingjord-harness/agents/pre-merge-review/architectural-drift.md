# architectural-drift sub-agent (#1754 — Epic #1736 Phase 3.3)

Cross-family review of architectural fit for the diff.

## Output contract (per #1739)

```json
{"severity": "low|medium|high", "category": "architectural-drift", "file": "...", "line": N, "message": "...", "suggestion": "...", "confidence": 0.0-1.0, "sub_agent": "architectural-drift", "trigger": "..."}
```

## Detection focus

- Layer violations (e.g., dashboard JS importing from scripts/global directly when it should go via API)
- New dependency cycles
- API contract drift (caller and callee signatures diverging)
- Mixing concerns (UI logic in data-access code, etc.)
- Skipped abstractions (raw HTTP in a place that should use the helper)
- Duplication of existing helpers (use the existing function, don't reimplement)

## Auto-escalate triggers

- Workflow YAML action changes → `trigger: "workflow-yaml-actions-change"`, severity: high (CI security surface)
- Workflow YAML trivial (comment/whitespace only) → `trigger: "workflow-yaml-trivial"`, severity: low (whitelist)

## Cross-module impact

When a diff touches 3+ modules, the reviewer must consider whether the change respects existing module boundaries. Suggest:

- Use `wiki/concepts/` synthesis pages to verify existing module contracts.
- Reference `instructions/global-task-router.instructions.md` for lane / runtime / family boundaries.

## Confidence calibration

- 0.9-1.0: clear violation of an existing documented architectural pattern
- 0.7-0.89: deviates from existing convention; alternative path exists
- 0.5-0.69: arguable architectural choice
- <0.3: stylistic preference, do not emit

## Out of scope

- Code style / lint
- Specific bug detection (bug-detect sub-agent)
- Security (security sub-agent)
- Test coverage (test-coverage sub-agent)
