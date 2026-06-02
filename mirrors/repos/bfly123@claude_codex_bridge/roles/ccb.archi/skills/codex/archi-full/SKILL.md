---
name: archi-full
description: Run full-project architecture analysis with Architec. Use when the user asks for an overall architecture score, full hotspot review, package topology diagnosis, structural weaknesses, architecture baseline, or main maintainability risks across the whole codebase.
---

# Archi Full

Use this skill for full-project baseline architecture review.

## Workflow

1. Inspect command shape:

```bash
(ccb-archi --help || archi --help)
```

2. Run full review.

If help includes `--full`, use:

```bash
ccb-archi --full || archi --full
```

If help lacks `--full`, use:

```bash
ccb-archi . || archi .
```

3. Refresh Hippo inputs only when the user asks for a fresh rebuild or stale
snapshot diagnosis:

```bash
ccb-archi --refresh-from-hippo --full || archi --refresh-from-hippo --full
```

4. Read outputs:

- `.architec/architec-summary.md`
- `.architec/architec-analysis.json`
- `.architec/architec-viz.html` when visualization is useful

## Output

```text
Score
- overall:
- key reading:

Problems
- ...

Improvements
- ...

Verification
- ...
```

Do not turn full review into task-goal planning. Use `archi-advice` when the
user wants a refactor roadmap.

