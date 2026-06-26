---
name: controlflow-review
description: "Use after implementation when a ControlFlow plan exists and review should focus on plan conformance, scope drift, evidence-backed correctness findings, and residual validation gaps rather than duplicating native Codex /review."
---

# ControlFlow Review

## Overview

Add the ControlFlow-specific layer after implementation: compare the aggregate diff to the
approved plan, reconcile scope drift, and require evidence-backed findings. Native host
review remains the preferred mechanical and general code-review pass; in Codex, use
`/review`.

Select the skill explicitly. In Codex, invoke it with `$controlflow-review`.

## Local Contract

- Read the approved plan and aggregate diff.
- If native review results are available, consume them rather than repeating the same
  mechanical/style pass.
- If native review has not run, recommend it separately and keep this pass focused on
  ControlFlow-specific concerns.
- Findings come first, ordered by severity, with file/line evidence and confidence.
- Distinguish validated blockers from hypotheses and state validation gaps.

## Workflow

1. Map each planned phase, file, acceptance criterion, quality gate, and deferred item.
2. Compare the aggregate diff and test evidence to that map.
3. Classify differences as approved follow-through, justified deviation, or blocking scope
   drift.
4. Search for correctness, security, data-integrity, rollback, and error-path defects that
   the plan said it would handle.
5. Validate feasible suspicions with commands, file reads, or schema checks.
6. Apply a novelty filter against earlier findings and recheck verified items affected by
   later revisions.
7. Present findings first. If none exist, state residual risks and unverified areas.

## Review Axes

Prioritize plan conformance, correctness, security, data integrity, regression risk, and
test evidence. Leave formatting and rote style findings to native host review.

## Soft Comment Labels

Use `Nit`, `Optional`, and `FYI` only after blocking findings. These are not severity levels and must not hide correctness, security, or test coverage defects.

## Change Size Caution

Large reviews lose signal. When a diff is much larger than roughly 100 changed lines or mixes unrelated concerns, ask for a split or review by file area and risk axis with an explicit confidence limit.

## Review-Specific Failure Checks

- Do not lead with nits before behavior checks.
- Do not mark missing tests as `FYI` when the untested behavior can regress.
- Do not state a blocker without validation evidence or an explicit unconfirmed-risk label.
- Do not duplicate native host review's mechanical findings.
- Do not skip plan comparison when an approved plan exists.

## References

- `references/evidence-discipline.md`
- `references/review-checklist.md`
- `references/validation-status.md`
- `references/security-review-discipline.md`
- `../controlflow-plan/references/llm-behavior-guidelines.md`
