# doc-coverage sub-agent (#2437 — Epic #2414)

Cross-family review of doc-coverage block completeness for the diff.

## Output contract (per #1739)

```json
{"severity": "low|medium|high", "category": "doc-coverage", "file": "...",
 "line": null, "message": "...", "suggestion": "...", "confidence": 0.0-1.0,
 "sub_agent": "doc-coverage", "trigger": "..."}
```

## Detection focus

- `COLLABORATOR_HANDOFF` on `lane:code-change` missing `doc-coverage:` block
- Required surfaces (per `config/doc-coverage-matrix.yml`) not declared as
  `UPDATED: <path>` or `N/A: <surface> — <reason>`
- `N/A:` entries missing a reason string after `—`
- Surface paths that don't match any configured `area:*` label for the ticket

## Auto-escalate triggers

- Missing `doc-coverage:` block on `lane:code-change` →
  `trigger: "missing-doc-coverage-block"`, severity: high
- Required surface absent (neither UPDATED nor N/A) →
  `trigger: "missing-required-surface"`, severity: medium

## Confidence calibration

- 0.9-1.0: `lane:code-change` COLLABORATOR_HANDOFF with no `doc-coverage:` block
- 0.7-0.89: block present but required surface(s) missing
- 0.5-0.69: surfaces declared but N/A reason absent
- <0.3: noise or non-code-change lane

## Out of scope

- Whether documentation content is accurate (operator responsibility)
- Non-COLLABORATOR_HANDOFF comments
- Lanes other than `lane:code-change`
