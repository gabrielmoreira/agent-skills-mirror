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

## Review Axes

### Correctness & Functionality

Check whether the change satisfies the request, preserves expected behavior, handles edge cases, and avoids regressions against the plan or contract.

### Security

Look for authorization gaps, secret exposure, unsafe parsing, injection paths, data leakage, destructive actions, and missing guardrails around sensitive operations.

### Architecture & Design

Evaluate whether the change fits existing boundaries, dependencies, data flow, schema contracts, and phase intent without introducing avoidable coupling or scope drift.

### Maintainability & Style

Prefer the repository's existing patterns, clear names, simple control flow, and small diffs. Style concerns should support readability, not distract from behavioral risk.

### Test Quality & Coverage

Check that the riskiest behavior has deterministic coverage, that tests assert observable outcomes, and that verification evidence matches the claimed completion state.

## Soft Comment Labels

Use `Nit`, `Optional`, and `FYI` only as non-blocking prose annotations after the blocking findings are handled. These labels are not severity levels and must not hide correctness, security, or test coverage defects.

## Change Size Caution

Large reviews lose signal. When a diff is much larger than roughly 100 changed lines or spans unrelated concerns, ask for a split or review it in clearly labeled slices by file area and review axis. If a large review is unavoidable, state the confidence limit explicitly.

## Anti-Rationalization Table

| Pattern | Why It Fails | Required Action |
| ------- | ------------ | --------------- |
| Fill the review with nits before behavior checks | Cosmetic feedback can bury blockers and waste revision cycles. | Lead with validated correctness, security, contract, and test risks. |
| Accept a very large mixed diff as one review | Reviewers miss interactions when too many concerns compete for attention. | Request a split or organize findings by axis and file area with confidence notes. |
| Mark missing tests as `FYI` because the code looks simple | Untested behavior can regress even when the implementation is small. | Tie coverage gaps to the behavior risk and severity they create. |
| State a blocker without validation evidence | False positives create churn and weaken trust in the verdict. | Validate when feasible, or label the item as an unconfirmed risk. |

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
