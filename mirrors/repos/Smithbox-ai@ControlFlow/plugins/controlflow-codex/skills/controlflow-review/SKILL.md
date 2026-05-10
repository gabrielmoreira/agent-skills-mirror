---
name: controlflow-review
description: "Use when asked to review code, a diff, or a completed phase, especially when the result should emphasize bugs, regressions, validation status, and evidence-backed findings instead of style commentary."
---

# ControlFlow Review

## Overview

Review changes by prioritizing correctness, regression risk, and evidence over style. Use this for code or completed-phase review; use `controlflow-plan-audit` or `controlflow-assumption-verifier` for pre-execution plan review.

## Local Contract

- Findings first, ordered by severity, with file/line evidence and confidence.
- Distinguish validated blockers from hypotheses; state validation gaps explicitly.
- Compare implementation to the plan when one exists; scope drift is a review issue.
- Use [references/review-checklist.md](references/review-checklist.md), [references/validation-status.md](references/validation-status.md), and [../controlflow-planning/references/llm-behavior-guidelines.md](../controlflow-planning/references/llm-behavior-guidelines.md) for shared checklist and evidence discipline.

## Workflow

1. Check correctness, regressions, security, data integrity, performance, and contract drift before style.
2. Validate feasible suspicions with commands, file reads, or schema checks.
3. Label each finding with severity, confidence, file, line, and user impact.
4. Present findings first; if there are none, say so and name residual risks or test gaps.
5. Use structured text, not raw JSON.

## Review Axes

Check correctness/functionality, security, architecture/design, maintainability/style, and test quality/coverage. Style comments should support behavioral risk, not bury it.

## Soft Comment Labels

Use `Nit`, `Optional`, and `FYI` only after blocking findings. These are not severity levels and must not hide correctness, security, or test coverage defects.

## Change Size Caution

Large reviews lose signal. When a diff is much larger than roughly 100 changed lines or mixes unrelated concerns, ask for a split or review by file area and risk axis with an explicit confidence limit.

## Review-Specific Failure Checks

- Do not lead with nits before behavior checks.
- Do not mark missing tests as `FYI` when the untested behavior can regress.
- Do not state a blocker without validation evidence or an explicit unconfirmed-risk label.

## References

- `references/evidence-discipline.md`
- `references/review-checklist.md`
- `references/validation-status.md`
- `references/security-review-discipline.md`
- `../controlflow-orchestration/references/tdd-patterns.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
