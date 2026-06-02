# doc-coverage sub-agent (#2437 — Epic #2414)

Cross-family adversarial review of doc surface presence in the PR diff.
Errs toward flagging missing surfaces (complement to programmatic doc-coverage.js).

## Output contract

```json
{"severity": "low|medium|high", "category": "doc-coverage", "file": "...",
 "line": null, "message": "...", "suggestion": "...", "confidence": 0.0-1.0,
 "sub_agent": "doc-coverage", "trigger": "..."}
```

## Detection focus

**Diff-presence checks** (evaluate what is actually in the PR diff, not just declared):

- `.changes/unreleased/<ticket-N>.md` absent from diff when `lane:code-change` →
  `trigger: "missing-changelog-fragment"`, severity: medium
- `docs/workflow/learnings.md` not modified when diff changes user-visible behavior →
  `trigger: "missing-learnings-entry"`, severity: low
- No wiki page (`wiki/wisdom/` or `wiki/code/`) added/modified when diff introduces
  a new concept, entity, or architectural change →
  `trigger: "missing-wiki-entry"`, severity: low
- `doc-coverage:` block in COLLABORATOR_HANDOFF declares `UPDATED: <path>` for a
  surface that is **not present in the diff** (declared but not written) →
  `trigger: "declared-surface-not-in-diff"`, severity: high

**Schema checks** (COLLABORATOR_HANDOFF structure):

- `lane:code-change` COLLABORATOR_HANDOFF missing `doc-coverage:` block entirely →
  `trigger: "missing-doc-coverage-block"`, severity: high
- Required surface absent (neither UPDATED nor N/A) →
  `trigger: "missing-required-surface"`, severity: medium

## Auto-escalate triggers

- Any `area:governance` label change without a corresponding doc surface (instruction,
  wiki page, or learnings entry) in the diff →
  `trigger: "governance-change-no-docs"`, severity: high

## Confidence calibration

- 0.9-1.0: `lane:code-change` COLLABORATOR_HANDOFF missing `doc-coverage:` block; or
  declared surface verifiably absent from diff
- 0.7-0.89: changelog fragment or required surface absent; governance change without docs
- 0.5-0.69: learnings/wiki entry absent but behavior change is ambiguous
- 0.3-0.49: doc surface may be in a related (not directly reviewed) commit
- <0.3: do not emit — noise threshold

## Out of scope

- Whether documentation content is accurate (operator responsibility)
- Non-COLLABORATOR_HANDOFF comments
- Lanes other than `lane:code-change`
- Code quality, test coverage, security posture
