---
name: controlflow-plan-audit
description: "Use when a saved implementation plan should be adversarially reviewed before coding, especially for small, medium, or large tasks that may contain architecture flaws, scope gaps, destructive risk, weak rollback, weak tests, or dependency conflicts."
---

# ControlFlow Plan Audit

## Overview

Review a saved plan before implementation begins. This skill is the Codex analogue of ControlFlow's PlanAuditor: it looks for architecture defects, dependency mistakes, missing rollback, scope gaps, and weak execution details.

## Workflow

1. Read the saved plan artifact first, not a summary of it.
2. Cross-check the plan against the actual repository:
   - files and paths
   - existing tests and validation commands
   - architecture and dependency surfaces
3. Audit these dimensions:
   - security and destructive risk
   - architecture and phase boundaries
   - dependency conflicts
   - test coverage and acceptance quality
   - rollback and migration safety
   - contract completeness
   - executability of the first few phases with no hidden context
4. Use [references/audit-checklist.md](references/audit-checklist.md) to avoid shallow review.
5. Save the verdict to `plans/artifacts/<task-slug>/plan-audit.md` using `../../templates/plan-audit-report-template.md`.
6. Return a structured text verdict:
   - `APPROVED`
   - `NEEDS_REVISION`
   - `REJECTED`
   - `ABSTAIN`
7. When the verdict is not approval, classify the failure as:
   - `fixable`
   - `needs_replan`
   - `escalate`
8. Findings should be evidence-backed and tied to specific plan sections or repository facts.

## Output Shape

- **Status**
- **Findings**
- **Risk Summary**
- **Recommendation**
- **Failure Classification** when needed
- **Confidence**

## Common Mistakes

- Auditing a plan summary instead of the actual saved artifact.
- Calling out vague “concerns” without plan-section evidence.
- Treating missing rollback as a minor issue when data or contracts can be damaged.
- Using this skill as a replacement for post-implementation code review.

## References

- `references/audit-checklist.md`
- `../../templates/plan-audit-report-template.md`
- `../controlflow-review/references/security-review-discipline.md`
- `../controlflow-planning/references/llm-behavior-guidelines.md`
