---
name: controlflow-review
description: "Use after implementation to review a diff or completed phase. A thin ControlFlow layer over Claude Code's native /code-review: adds plan-vs-implementation scope-drift comparison, evidence discipline, and proactive vulnerability/error search. Does not duplicate native review — delegates mechanical/style review to /code-review."
---

# ControlFlow Review

## Overview

ControlFlow Review is a **layer over** Claude Code's native review capabilities, not a
replacement. Mechanical and style review (lint-class issues, formatting, rote pattern
checks) belong to native `/code-review` and `security-review`. This skill adds only what
native review does not provide: plan-vs-implementation scope-drift comparison,
evidence-backed finding discipline, and proactive vulnerability/error search.

Invoke this skill via `/controlflow-claude-code:controlflow-review`.

## Local Contract

- Run native `/code-review` (or `security-review` for security-focused work) first for the
  mechanical pass; this skill consumes and augments its output rather than duplicating it.
- Compare the implementation to the plan when one exists — scope drift is a review issue,
  not a style preference.
- Findings first, ordered by severity, with file/line evidence and confidence.
- Distinguish validated blockers from hypotheses; state validation gaps explicitly.
- Use [references/review-checklist.md](references/review-checklist.md),
  [references/validation-status.md](references/validation-status.md),
  [references/evidence-discipline.md](references/evidence-discipline.md), and
  [references/security-review-discipline.md](references/security-review-discipline.md)
  for shared checklist and evidence discipline, and
  [../controlflow-plan/references/llm-behavior-guidelines.md](../controlflow-plan/references/llm-behavior-guidelines.md)
  for generic anti-rationalization discipline.

## Workflow

1. If a plan exists at `plans/<task-slug>-plan.md`, read it. Track every phase acceptance
   criterion and file the plan said it would touch — anything implemented but not planned,
   or planned but not implemented, is a scope-drift finding.
2. Delegate the mechanical/style pass: invoke native `/code-review` (or `security-review`)
   and collect its findings.
3. Add the ControlFlow layer:
   - **Plan comparison** — does the diff match the plan's phases, files, and acceptance
     criteria? Flag scope drift, missing phases, extra-phased work, and unmet acceptance
     criteria.
   - **Vulnerability / error search** — proactively hunt for bugs, regressions, data
     integrity issues, and security defects the mechanical pass may miss. Validate
     suspicions with commands, file reads, or schema checks.
   - **Evidence discipline** — label each finding with severity, confidence, file, line,
     user impact, and validation method.
4. Present findings first, ordered by severity. If there are none, say so and name residual
   risks or test gaps. Use structured text, not raw JSON.

## Review Axes (ControlFlow layer)

Prioritize correctness/functionality, security, data integrity, regression risk, and
contract drift before style. Maintainability/style comments should support a behavioral
risk, not bury one — and the mechanical side of style is native `/code-review`'s job.

## Proactive Vulnerability / Error Search

Go beyond reactive review of the diff:

- Trace new data flows to their endpoints; check validation at each boundary.
- Look for error paths the implementation skipped (absence mirages A11–A13).
- Check for missing migrations or rollback for schema/contract changes (A16).
- Check for missing security boundaries on sensitive operations (A17).
- Where the plan declared failure expectations, confirm the implementation handles them.

## Soft Comment Labels

Use `Nit`, `Optional`, and `FYI` only after blocking findings. These are not severity
levels and must not hide correctness, security, or test-coverage defects.

## Change Size Caution

Large reviews lose signal. When a diff is much larger than roughly 100 changed lines or
mixes unrelated concerns, ask for a split or review by file area and risk axis with an
explicit confidence limit.

## Review-Specific Failure Checks

- Do not lead with nits before behavior checks.
- Do not mark missing tests as `FYI` when the untested behavior can regress.
- Do not state a blocker without validation evidence or an explicit unconfirmed-risk label.
- Do not duplicate native `/code-review`'s mechanical pass — delegate it.
- Do not skip the plan comparison when a plan artifact exists.

## References

- `references/review-checklist.md`
- `references/validation-status.md`
- `references/evidence-discipline.md`
- `references/security-review-discipline.md`
- `../controlflow-plan/references/llm-behavior-guidelines.md`