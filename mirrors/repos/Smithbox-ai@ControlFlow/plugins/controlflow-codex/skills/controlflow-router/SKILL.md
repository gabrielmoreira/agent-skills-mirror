---
name: controlflow-router
description: "Use when a task broadly matches ControlFlow for Codex and you need to decide whether to start with strict workflow, strict planning, pre-execution plan review, orchestration, code review, or memory hygiene, or whether to combine several of those skills in sequence."
---

# ControlFlow Router

## Overview

Route work to the right ControlFlow-Codex skill instead of loading all of them by default. Use this as the entry point when the user wants "ControlFlow discipline" but has not said which mode is needed first.

## When to Skip the Router

Do not use this router for `TRIVIAL` work where a direct Codex response is enough:

- single-line fixes or obvious corrections
- single-file edits with no architectural impact
- exploratory prototypes or throwaway scripts
- cases where the user already named the exact skill, such as `$controlflow-review`

For simple work, prompt Codex directly or invoke only the one specific `$controlflow-*` skill that applies.

## Routing Rules

Start with `controlflow-planning` when:
- the user asks for a plan
- the task is medium or large
- the file scope or architecture is still fuzzy
- the change includes migrations, cross-cutting edits, or explicit risk review

Start with `controlflow-strict-workflow` when:
- you want the full ControlFlow-Codex process as one default path
- the task should move from planning through plan review and execution
- you do not want to manually choose each ControlFlow skill yourself

Start with `controlflow-plan-audit` when:
- a saved plan exists and should be reviewed before coding
- you want architecture, rollback, dependency, or test-strategy criticism
- the task is at least `SMALL`

Start with `controlflow-assumption-verifier` when:
- a saved plan may contain invented paths, APIs, versions, integrations, or hidden assumptions
- the task is `MEDIUM` or `LARGE`
- unresolved `HIGH` semantic risk remains in the plan

Start with `controlflow-executability-verifier` when:
- a saved plan may still be too vague for a fresh executor
- the task is `LARGE`
- you want a cold-start simulation before implementation begins

Start with `controlflow-orchestration` when:
- a plan already exists
- the task should be executed in phases
- approvals, retries, or handoff discipline matter
- the user wants structured progress through several steps

Start with `controlflow-review` when:
- the user asks for a review
- there is a diff, patch, PR, or completed phase to inspect
- the highest-value output is bugs, regressions, and validation gaps

Start with `controlflow-memory-hygiene` when:
- the task spans many turns or phases
- repo-persistent notes need cleanup
- the conversation risks relying on stale memory

## Combined Flows

- For a new non-trivial task: `controlflow-planning` -> `controlflow-plan-audit` -> `controlflow-orchestration`
- For the easiest default path: `controlflow-strict-workflow`
- For a medium task: `controlflow-planning` -> `controlflow-plan-audit` + `controlflow-assumption-verifier` -> `controlflow-orchestration`
- For a large task: `controlflow-planning` -> `controlflow-plan-audit` + `controlflow-assumption-verifier` + `controlflow-executability-verifier` -> `controlflow-orchestration`
- For a long-running implementation: `controlflow-memory-hygiene` + `controlflow-orchestration`
- For sign-off after implementation: `controlflow-review`
- For a large or messy task: `controlflow-router` first, then load only the skills that genuinely apply

## Common Mistakes

- Loading every ControlFlow skill up front.
- Starting orchestration before a stable plan exists.
- Skipping plan review for `SMALL+` work.
- Using review mode to do planning.
- Treating memory hygiene as a substitute for re-reading the repository.
