---
name: controlflow-plan-audit
description: "Use when a saved implementation plan should be adversarially reviewed before coding, especially for small, medium, or large tasks that may contain architecture flaws, scope gaps, destructive risk, weak rollback, weak tests, or dependency conflicts."
---

# ControlFlow Plan Audit

## Overview

Adversarially review a saved implementation plan before coding. Look for architecture
defects, dependency mistakes, missing rollback, scope gaps, weak tests, and first-phase
executability problems.

Invoke this skill via `/controlflow-claude-code:controlflow-plan-audit`.

## Local Contract

- Read the actual plan artifact and cross-check it against repository files, tests,
  commands, architecture, and dependencies.
- Use [references/audit-checklist.md](references/audit-checklist.md) for audit coverage
  and [../controlflow-planning/references/llm-behavior-guidelines.md](../controlflow-planning/references/llm-behavior-guidelines.md)
  for generic evidence discipline.
- Save the verdict to `plans/artifacts/<task-slug>/plan-audit.md` using
  [../../templates/plan-audit-report-template.md](../../templates/plan-audit-report-template.md).
- Tie findings to plan sections or repository facts.

## Workflow

1. Read the saved plan artifact first, not a summary.
2. Check file/path reality, available tests and validation commands,
   architecture/dependency surfaces, rollback, acceptance quality, contract completeness,
   and first-phase executability.
3. Return one verdict: `APPROVED`, `NEEDS_REVISION`, `REJECTED`, or `ABSTAIN`.
4. For non-approval, classify as `fixable`, `needs_replan`, or `escalate`.
5. Save and summarize evidence-backed findings.

## Spec-Before-Plan Health Check

For non-trivial work, confirm the plan is anchored to explicit requirements, acceptance
criteria, constraints, exclusions, and verification gates rather than inferred chat
context.

## Audit-Specific Failure Checks

- Do not approve a detailed plan that lacks a spec artifact or equivalent requirements
  section.
- Do not approve vague success criteria; require measurable acceptance and gates.
- Do not downplay rollback gaps; classify them by blast radius.
- Do not accept plausible repository claims without checking current paths and commands.

## Output Shape

- **Status**
- **Findings**
- **Risk Summary**
- **Recommendation**
- **Failure Classification** when needed
- **Confidence**

## References

- `references/audit-checklist.md`
- `../../templates/plan-audit-report-template.md`
- `../controlflow-review/references/security-review-discipline.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
