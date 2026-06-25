---
name: controlflow-plan
description: "Use when a repository task needs a high-quality ControlFlow plan before coding — small, medium, or large scope, cross-file edits, risky migrations, architectural uncertainty, or any work that should produce a saved Markdown plan artifact in plans/. Single-sources the plan format from schemas/planner.plan.schema.json and the plan template."
---

# ControlFlow Plan

## Overview

Produce a durable, execution-ready plan in the shared ControlFlow format. The format is
not restated here: it is single-sourced from `schemas/planner.plan.schema.json` (the
machine-enforced contract) and `plans/templates/plan-document-template.md` (the human
document skeleton). Read both at invoke time and conform to them; do not paraphrase the
contract from memory.

Invoke this skill via `/controlflow-plan`.

## Local Contract

- Read the repository before phase decomposition; keep verified facts separate from
  assumptions with a bounded scope statement.
- The saved artifact defines scope, risks, files, phases, validation, review route, and
  handoff without depending on plugin-host runtime contracts.
- Apply [references/llm-behavior-guidelines.md](references/llm-behavior-guidelines.md) for
  assumption, simplicity, scope, and verification discipline.
- Ask the user directly when an answer changes file scope, user-visible behavior,
  architecture, or destructive-risk handling; otherwise record a bounded assumption.

## Workflow

1. Create a saved plan when the user asks for one or when work is SMALL, MEDIUM, or LARGE;
   skip only for truly TRIVIAL work. Save to `plans/<task-slug>-plan.md` unless the user
   names another path.
2. Read `schemas/planner.plan.schema.json` and
   `plans/templates/plan-document-template.md` — these are the authoritative format. Use
   [references/plan-format.md](references/plan-format.md) as a compact checklist, not a
   substitute for them.
3. Map likely files, tests, commands, dependencies, and change boundaries before phase
   decomposition.
4. Read [references/complexity-tiers.md](references/complexity-tiers.md); assign one tier.
   Any unresolved HIGH-impact semantic risk forces LARGE regardless of file count.
5. Fill all seven semantic risk categories (see
   [references/plan-format.md](references/plan-format.md)); never skip a row — use
   `not_applicable` with justification.
6. Write the artifact using the template's header, 10 sections in order, and the five
   lifecycle sections (`## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`,
   `## Idempotence & Recovery`) for SMALL+ plans.
7. Every phase declares exactly one `executor_agent` from the schema enum, lists concrete
   files, tests, acceptance criteria, quality gates, and failure expectations, and keeps
   steps in numbered prose with NO code blocks.
8. Add Mermaid diagrams per tier: `sequenceDiagram` for MEDIUM+ non-trivial orchestration;
   `flowchart TD` + `sequenceDiagram` for LARGE. Each diagram ≤30 lines.
9. Set `status: ABSTAIN` or `REPLAN_REQUIRED` when confidence is below 0.9 or evidence is
   insufficient; include the terminal-outcome structure from the template.
10. Add a research or spike phase before implementation when a HIGH-impact risk is
    unresolved.
11. For `READY_FOR_EXECUTION`, include a Handoff section pointing execution to
    `plans/<task-slug>-plan.md` — do NOT inline the plan in chat. See
    [references/inline-execution.md](references/inline-execution.md) for how execution
    treats waves, the context packet, and optional delegation.

## Review Route (tier-gated, runs after this skill)

Hand non-TRIVIAL plans to `/controlflow-verify`, which runs inline adversarial verification:
SMALL → phase 1; MEDIUM → phases 1–2; LARGE → phases 1–3.

## Planning-Specific Failure Checks

- Do not plan from chat memory when reading the repo would change scope.
- Do not skip a semantic risk category because the tier feels low.
- Do not decompose phases before mapping likely files and tests.
- Do not mark READY_FOR_EXECUTION without a review route and artifact destination.
- Do not restate the schema/template in the artifact — conform to them.

## References

- `references/plan-format.md`
- `references/complexity-tiers.md`
- `references/inline-execution.md`
- `references/llm-behavior-guidelines.md`