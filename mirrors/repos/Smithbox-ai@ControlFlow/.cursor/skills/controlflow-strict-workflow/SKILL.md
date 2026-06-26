---
name: controlflow-strict-workflow
description: "Use for non-trivial Cursor work: saved plan, tiered pre-execution review, phased execution, and final review with durable artifacts under plans/."
---

# ControlFlow Strict Workflow (Cursor)

## Overview

Use this entry point in Cursor Agent mode for the full ControlFlow workflow: plan, pre-execution review, execution, final review, and durable artifacts. Read and follow sibling skills under `.cursor/skills/` (or project skills path).

## Workflow

1. Route the task if needed — follow `controlflow-router` skill.
2. Write a saved plan — follow `controlflow-planning` at `plans/<task-slug>-plan.md`.
3. Pre-execution review by complexity:
   - `TRIVIAL`: optional strict review
   - `SMALL`: delegate `controlflow-plan-auditor` or follow `controlflow-plan-audit` skill
   - `MEDIUM`: plan audit + `controlflow-assumption-verifier` agent or skill
   - `LARGE`: add `controlflow-executability-verifier` agent or skill
   - unresolved `HIGH` semantic risk: include assumption verifier; consider executability verifier
4. Save reviewer outputs in `plans/artifacts/<task-slug>/`.
5. If review blocks, revise the plan before execution.
6. Execute — follow `controlflow-orchestration` skill; delegate implementer phases to `.cursor/agents/controlflow-*-implementer` when Task is available.
7. Final review — `controlflow-code-reviewer` agent or `controlflow-review` skill.
8. Long sessions — `controlflow-memory-hygiene` as needed.

## Cursor Subagent Delegation

When the Task tool is available, delegate isolated review/research with:

```text
Task(subagent_type="controlflow-plan-auditor", description="Plan audit", prompt="...")
```

Use `subagent_type` matching the filename in `.cursor/agents/` (without `.md`). The prompt must include plan path, tier, trace_id, and expected report sections.

**Fallback:** If Task is unavailable, run the matching skill in this session and save Markdown under `plans/artifacts/<task-slug>/`. Do not claim isolation was enforced.

## Verification Story

Every phase claim needs evidence: command output, artifact path, review result, test result, or documented skip reason. See `controlflow-planning` references for anti-rationalization rules.

## Default Artifact Set

- `plans/<task-slug>-plan.md`
- `plans/artifacts/<task-slug>/plan-audit.md`
- `plans/artifacts/<task-slug>/assumption-verifier.md`
- `plans/artifacts/<task-slug>/executability-verifier.md`

## Completion Gate

Run the repository verification command when defined (e.g. `cd evals && npm test` in ControlFlow repo). Update lifecycle sections: `## Progress`, `## Discoveries`, `## Decision Log`, `## Outcomes`, `## Idempotence & Recovery`.

## References

- `plugins/controlflow-cursor/USAGE.md`
- `docs/agent-engineering/CURSOR-SUPPORT.md`
- `plugins/controlflow-cursor/templates/`
