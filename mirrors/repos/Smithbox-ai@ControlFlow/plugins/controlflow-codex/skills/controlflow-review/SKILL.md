---
name: controlflow-review
description: "Use when asked to review code, a diff, or a completed phase, especially when the result should emphasize bugs, regressions, validation status, and evidence-backed findings instead of style commentary."
---

# ControlFlow Review

## Overview

Review changes the ControlFlow way: prioritize correctness, regression risk, and evidence over style. This skill adapts the repo's review discipline into a Codex-friendly checklist and reporting shape.

Use this for code and implementation review. For pre-execution plan review, use `controlflow-plan-audit` or `controlflow-assumption-verifier`.

## Workflow

1. Start with correctness, regressions, security, data integrity, performance, and contract drift. Ignore nits until the behavioral risks are understood.
2. If a plan exists, compare the implementation against the promised files, phases, and user-facing outcomes. Scope drift is a review issue.
3. Every finding should include severity, confidence, file, line, and why the issue matters.
4. Distinguish confirmed blockers from hypotheses. Run validation commands when feasible, and say explicitly when you could not validate a suspicion.
5. Use [references/review-checklist.md](references/review-checklist.md) to avoid skipping concurrency, migration, or operability concerns.
6. Use [references/validation-status.md](references/validation-status.md) to label findings accurately.
7. Present findings first. If there are no findings, say so clearly and then call out residual risks or testing gaps.
8. Use structured text, not raw JSON.

## Common Mistakes

- Reviewing for style before checking behavior.
- Reporting vague issues without file or line evidence.
- Treating unvalidated hunches as confirmed defects.
- Forgetting to say what was not tested.

## References

- `references/evidence-discipline.md`
- `references/review-checklist.md`
- `references/validation-status.md`
- `references/security-review-discipline.md`
- `../controlflow-orchestration/references/tdd-patterns.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
