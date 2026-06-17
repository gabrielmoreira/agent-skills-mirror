---
name: controlflow-planning
description: "Use when a repository task needs a strict ControlFlow-style implementation plan before coding, especially for small, medium, or large scope, cross-file edits, risky migrations, architectural uncertainty, or any work that should produce a saved Markdown plan artifact in plans/."
---

# ControlFlow Planning

## Overview

Create a durable, execution-ready Codex plan. Keep the contract local: the saved artifact defines scope, risks, files, phases, validation, review route, and handoff without depending on VS Code agent mode.

## Local Contract

- Read the repository before phase decomposition; keep verified facts separate from assumptions.
- Use [references/plan-template.md](references/plan-template.md) as the plan contract, not a loose outline.
- Apply [references/llm-behavior-guidelines.md](references/llm-behavior-guidelines.md) for generic assumption, simplicity, scope, and verification discipline.
- Keep Codex portable: ask the user directly when a requirement changes scope, or record a bounded assumption when it does not.

## Workflow

1. Create a saved plan when the user asks for one or when work is `SMALL`, `MEDIUM`, or `LARGE`; skip it only for truly `TRIVIAL` work.
2. Save to `plans/<task-slug>-plan.md` unless the user names another path.
3. Clarify only when the answer changes file scope, user-visible behavior, architecture, or destructive-risk handling.
4. Map likely files, tests, commands, dependencies, and change boundaries before phase decomposition.
5. Read [references/complexity-tiers.md](references/complexity-tiers.md) and [references/semantic-risk-taxonomy.md](references/semantic-risk-taxonomy.md); assign one tier and fill all seven risk categories.
6. Write the artifact using [references/plan-template.md](references/plan-template.md).
7. For non-trivial Codex plans (`SMALL`, `MEDIUM`, `LARGE`), include the five fixed lifecycle sections in this exact order and with these exact headings: `## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, `## Idempotence & Recovery`. These headings are required by [../../scripts/validate-strict-artifacts.ps1](../../scripts/validate-strict-artifacts.ps1) and must match the template and fixtures exactly.
8. Use `ABSTAIN` or `REPLAN_REQUIRED` when confidence is below `0.9` or evidence is insufficient.
9. Add research or spike phases before implementation when a `HIGH`-impact risk is unresolved.
10. Keep phases incremental, testable, and explicit about files, dependencies, quality gates, and failure expectations.
11. Route non-trivial plans through strict review: `SMALL` -> `controlflow-plan-audit`; `MEDIUM`/`LARGE` -> add `controlflow-assumption-verifier`; unresolved `HIGH` risk -> include `controlflow-assumption-verifier` regardless of size.
12. Record lightweight revision lineage, iteration state, and verified-item regression evidence without copying the core Planner schema.
13. When a context packet exists, name its artifact path and require wave-boundary refresh instead of repeating discovery.
14. Check [references/controlflow-portability.md](references/controlflow-portability.md) before handoff.

## Spec Capture Handoff

When requirements, acceptance criteria, boundaries, or verification gates are not explicit, use `controlflow-spec` first. Carry its `spec_path`, scope, acceptance criteria, constraints, success metrics, and open risks into the plan. If spec capture is unnecessary, state why the request is already clear enough.

## Planning-Specific Failure Checks

- Do not plan from chat memory when a spec is required; cite the spec artifact or create one.
- Do not skip semantic risk review because the tier feels low; fill every category.
- Do not decompose phases before reading the repository and mapping likely files/tests.
- Do not mark `READY_FOR_EXECUTION` without a strict review route and artifact destination.
- Generic anti-rationalization rules live in [references/llm-behavior-guidelines.md](references/llm-behavior-guidelines.md).

## Mandatory Output Contract

- Prefer structured text over raw JSON.
- Default plan file path: `plans/<task-slug>-plan.md`.
- Use the ControlFlow-style header and section order from [references/plan-template.md](references/plan-template.md).
- Write `Agent: Planner` in the artifact so the document matches the original conceptual role even though the implementation is a Codex skill.
- Record assumptions separately from verified facts.
- For `READY_FOR_EXECUTION` plans, include a clear handoff section that points execution to orchestration.

## References

- `references/plan-template.md`
- `references/complexity-tiers.md`
- `references/semantic-risk-taxonomy.md`
- `references/controlflow-portability.md`
- `references/planner-output-contract.md`
- `references/llm-behavior-guidelines.md`
