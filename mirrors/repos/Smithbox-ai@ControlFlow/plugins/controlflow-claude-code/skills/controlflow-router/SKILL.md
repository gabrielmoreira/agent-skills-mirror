---
name: controlflow-router
description: "Use when a task broadly matches ControlFlow and you need to decide whether to start with spec capture, strict workflow, planning, pre-execution plan review, orchestration, code review, or memory hygiene, or whether to combine several of those skills in sequence."
---

# ControlFlow Router

## Overview

Route work to the right ControlFlow Claude Code skill instead of loading all of them by default.
Use this as the entry point when the user wants ControlFlow discipline but has not said which mode
is needed first.

Invoke this skill via `/controlflow-claude-code:controlflow-router`.

## Available Routes

- `/controlflow-claude-code:controlflow-spec`
- `/controlflow-claude-code:controlflow-planning`
- `/controlflow-claude-code:controlflow-strict-workflow`
- `/controlflow-claude-code:controlflow-plan-audit`
- `/controlflow-claude-code:controlflow-assumption-verifier`
- `/controlflow-claude-code:controlflow-executability-verifier`
- `/controlflow-claude-code:controlflow-orchestration`
- `/controlflow-claude-code:controlflow-review`
- `/controlflow-claude-code:controlflow-memory-hygiene`

## When to Skip the Router

Do not use this router for TRIVIAL work where a direct response is enough:

- single-line fixes or obvious corrections
- single-file edits with no architectural impact
- exploratory prototypes or throwaway scripts
- cases where the user already named the exact skill

For simple work, respond directly or invoke only the one specific skill that applies.

## Routing Rules

Start with `/controlflow-claude-code:controlflow-spec` when:
- the request is a new feature, migration, policy change, or other non-trivial task and no saved spec exists
- requirements, acceptance criteria, constraints, or success metrics are still ambiguous
- planning would need to infer scope boundaries or out-of-scope exclusions from chat context
- the user asks for requirements capture, spec-first work, or clarification before planning

After spec produces a spec artifact, route to `/controlflow-claude-code:controlflow-planning`
with the spec path and intended plan path.

Start with `/controlflow-claude-code:controlflow-planning` when:
- the user asks for a plan
- the task is MEDIUM or LARGE
- the file scope or architecture is still fuzzy
- the change includes migrations, cross-cutting edits, or explicit risk review
- a spec artifact already exists and should be converted into an implementation plan

Start with `/controlflow-claude-code:controlflow-strict-workflow` when:
- you want the full ControlFlow process as one default path
- the task should move from planning through plan review and execution
- you do not want to manually choose each skill yourself

Start with `/controlflow-claude-code:controlflow-plan-audit` when:
- a saved plan exists and should be reviewed before coding
- you want architecture, rollback, dependency, or test-strategy criticism
- the task is at least SMALL

Start with `/controlflow-claude-code:controlflow-assumption-verifier` when:
- a saved plan may contain invented paths, APIs, versions, integrations, or hidden assumptions
- the task is MEDIUM or LARGE
- unresolved HIGH semantic risk remains in the plan

Start with `/controlflow-claude-code:controlflow-executability-verifier` when:
- a saved plan may still be too vague for a fresh executor
- the task is LARGE
- you want a cold-start simulation before implementation begins

Start with `/controlflow-claude-code:controlflow-orchestration` when:
- a plan already exists
- the task should be executed in phases
- approvals, retries, or handoff discipline matter
- the user wants structured progress through several steps

Start with `/controlflow-claude-code:controlflow-review` when:
- the user asks for a review
- there is a diff, patch, or completed phase to inspect
- the highest-value output is bugs, regressions, and validation gaps

Start with `/controlflow-claude-code:controlflow-memory-hygiene` when:
- the task spans many turns or phases
- repo-persistent notes need cleanup
- the conversation risks relying on stale memory

## Combined Flows

- New non-trivial task without a saved spec:
  spec -> planning -> plan-audit -> orchestration
- New non-trivial task with a saved spec:
  planning -> plan-audit -> orchestration
- Easiest default path:
  `/controlflow-claude-code:controlflow-strict-workflow`
- MEDIUM task:
  planning -> plan-audit + assumption-verifier -> orchestration
- LARGE task:
  planning -> plan-audit + assumption-verifier + executability-verifier -> orchestration
- Long-running implementation:
  memory-hygiene + orchestration
- Sign-off after implementation:
  review
- Large or messy task:
  router first, then load only the skills that genuinely apply

## Common Mistakes

- Loading all skills at once for a small task instead of routing.
- Skipping the router for a genuinely large task and jumping to orchestration without a reviewed plan.
- Treating the router decision as irreversible; you can switch skills when the situation changes.
