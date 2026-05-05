---
name: controlflow-planning
description: "Use when a repository task needs a strict ControlFlow-style implementation plan before coding, especially for small, medium, or large scope, cross-file edits, risky migrations, architectural uncertainty, or any work that should produce a saved Markdown plan artifact in plans/."
---

# ControlFlow Planning

## Overview

Turn a fuzzy or risky coding request into a durable, execution-ready plan for Codex. This skill adapts the strongest planning ideas from ControlFlow while stripping out VS Code Copilot-specific runtime assumptions.

## Workflow

1. Decide whether a saved plan artifact is mandatory.
   - If the user explicitly asks for a plan, always create one.
   - If the task is `SMALL`, `MEDIUM`, or `LARGE`, create one even if the user did not ask.
   - Only skip the file artifact for truly `TRIVIAL` work when the user did not request a saved plan.
2. Save the plan to `plans/<task-slug>-plan.md` by default. Use another path only when the user explicitly asks for it.
3. Clarify only when the answer changes file scope, user-visible behavior, top-level architecture, or destructive-risk handling. Otherwise state the assumption and continue.
4. Map the likely files, tests, commands, dependencies, and change boundaries before phase decomposition. Read the repository first; do not plan from memory.
5. Read [references/complexity-tiers.md](references/complexity-tiers.md) and [references/semantic-risk-taxonomy.md](references/semantic-risk-taxonomy.md). Assign exactly one complexity tier and fill all 7 semantic risk categories.
6. Write the artifact using [references/plan-template.md](references/plan-template.md). Treat that template as the default contract, not a loose suggestion.
7. For non-trivial Codex plans (`SMALL`, `MEDIUM`, `LARGE`), include the five fixed lifecycle sections in this exact order and with these exact headings: `## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, `## Idempotence & Recovery`. These headings are required by `scripts/validate-strict-artifacts.ps1` and must match the template and any fixtures exactly — do not use alternative names or omit any of them.
8. When confidence is below `0.9`, or evidence is insufficient for safe decomposition, use `ABSTAIN` or `REPLAN_REQUIRED` rather than pretending the plan is ready.
9. Add research or spike phases before implementation when a `HIGH`-impact risk is unresolved. Do not bury uncertainty inside coding phases.
10. Keep phases incremental, testable, and explicit about files, dependencies, quality gates, and failure expectations.
11. Before handing the plan off for execution, route it through strict plan review:
   - `SMALL`: `controlflow-plan-audit`
   - `MEDIUM` and `LARGE`: `controlflow-plan-audit` plus `controlflow-assumption-verifier`
   - Any unresolved `HIGH` risk: include `controlflow-assumption-verifier` regardless of raw size
12. Sanity-check the finished artifact against [references/controlflow-portability.md](references/controlflow-portability.md) so the plan stays faithful to ControlFlow structure without depending on Codex-incompatible runtime magic.

## Mandatory Output Contract

- Prefer structured text over raw JSON.
- Default plan file path: `plans/<task-slug>-plan.md`.
- Use the ControlFlow-style header and section order from `references/plan-template.md`.
- Write `Agent: Planner` in the artifact so the document matches the original conceptual role even though the implementation is a Codex skill.
- Record assumptions separately from verified facts.
- For `READY_FOR_EXECUTION` plans, include a clear handoff section that points execution to orchestration.

## Common Mistakes

- Writing a phase list before understanding the current file map.
- Treating every large task as sequential when some phases are independent.
- Folding unresolved research into implementation.
- Saving the plan in an ad-hoc path when `plans/<task-slug>-plan.md` would work.
- Dropping required sections from the strict template because the task "seems simple."

## References

- `references/plan-template.md`
- `references/complexity-tiers.md`
- `references/semantic-risk-taxonomy.md`
- `references/controlflow-portability.md`
- `references/planner-output-contract.md`
- `references/llm-behavior-guidelines.md`
