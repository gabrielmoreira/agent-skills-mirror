---
name: archi-diff
description: Run diff-based architecture analysis with Architec. Use when the user asks whether current changes are architecturally safe, what the current git diff impacts, whether a patch should be blocked for structural reasons, or which changed components carry maintainability risk.
---

# Archi Diff

Use this skill for change-scoped architecture review.

## Workflow

1. Inspect the local command shape:

```bash
(ccb-archi --help || archi --help)
```

2. Run incremental review.

If help includes `--full`, use:

```bash
ccb-archi || archi
```

If help lacks `--full` but includes `--diff`, use:

```bash
ccb-archi --diff . || archi --diff .
```

3. Read outputs:

- `.architec/architec-summary.md`
- `.architec/architec-analysis.json`

Focus on incremental score, changed-component concerns, boundary pressure,
duplication, hotspots, and recommendations.

## Output

Lead with the verdict:

```text
Verdict
- diff status:
- incremental score:

Blocking Issues
- ...

Impacted Areas
- ...

Required Changes
- ...
```

Do not paste raw JSON. Use direct code references for findings that need
engineering action.

