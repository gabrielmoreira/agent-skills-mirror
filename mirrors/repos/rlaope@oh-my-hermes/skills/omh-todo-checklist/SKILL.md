---
name: "omh-todo-checklist"
description: "[omh] Continue or finish the accepted work from conversation context, preserve rejected ideas, and report evidence-bounded completion. Also declare and advance the metadata-only plan checklist without starting a delivery engine. Use when the user says: todo-checklist, plan checklist, todo checklist, phase checklist, declare a plan checklist, declare the plan todo, show the plan todo, clear the plan todo."
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, operator]
    category: operator
    phase: observability
    role: tracker
    quality_tier: evidence-gated
---

# Todo Checklist

This is a Hermes-native `todo-checklist` workflow skill.

## Why This Exists

`todo-checklist` exists because `omh_todo` is registered on every session while nothing in the skill surface named it: a user who wanted a plan checklist searched for one and found no skill on the subject. The delivery engines declare a checklist as part of starting work, which serves someone running an engine and nobody else.

## Do Not Use When

- The work is one step, already finished, or answerable in this turn; a checklist that never advances is a panel of noise.
- The user wants an accepted implementation plan split into parallel lanes with owners and verification commands; use `ultrawork`.
- The user wants the planning content itself -- options, risks, acceptance criteria before execution; use `ralplan`.
- The user is asking what coding work is running right now rather than what the plan says; use `running-work-board`.

## Examples

Good example:

- Prompt: declare a plan checklist for this migration so I can see where you are
- Expected behavior: Declare numbered phases in delivery order with one task per observable outcome, exactly one active, and update states as work completes.
- Why: The user wants the HUD checklist itself, for work that spans turns, without starting a delivery engine.

Bad example:

- Prompt: add a TODO comment above this function
- Expected behavior: Edit the code; the plan todo panel has nothing to do with a source comment.
- Why: `todo` is an everyday word in a coding session and this use of it is not a plan checklist.

## Completion Checklist

- Exactly one item is active, or the list is complete and every item is done.
- Use `action=advance` or a complete `action=set` list; never drop an item by omission.
- Item states are described as declarations; observed results are cited separately or named as missing.
- Name whether work is blocked or human-deferred.

## Recovery Notes

- After a partial `action=set`, resend every item; use `action=advance` for state changes.
- If the panel shows nothing, read the current projection with `action=show` before re-declaring, so an existing checklist is not overwritten.
- If the user redirects the session away from the plan, record that on the write rather than deleting the checklist or marking its items done.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `live-incident-response`, `automation-blueprint`, `github-event-ops`, `github-issue-intake`, `buzz`, `+39 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants a declared, HUD-visible plan checklist for the work at hand, or wants to read, advance, or clear one, without starting a delivery engine. Also use when the person asks in ordinary language to finish or resume the previously accepted work; infer intent from conversation, not isolated keywords.

    Strong routing signals: `todo-checklist`, `$todo`, `plan checklist`, `todo checklist`, `phase checklist`, `declare a plan checklist`, `declare the plan todo`, `show the plan todo`, `clear the plan todo`

## Catalog Metadata

Category: `operator`
Phase: `observability`
Hermes role: `tracker`
Quality tier: `evidence-gated`
Reasoning demand: `light`

Quality bar:

- A `done` item is a declaration, never observed evidence.
- For accepted multi-turn work, load `references/closing-a-story.md` before checkpoint, recall, explicit resume or recording verification/review/QA declarations. Preserve rejected ideas separately; templates remain optional.
- Current intent overrides old plans. Stop, analysis-only and topic changes take precedence; ask only when scope is ambiguous. Missing, stale or malformed evidence is not clean; waiting for a child remains open.
- Keep exactly one item active so the HUD names the current step.
- Use `action=advance` with item number, text-prefix guard and new state. `action=set` replaces the whole list: send every item or omitted ones are lost.
- The live checklist is session-owned; another TUI, Slack or Discord session cannot see or overwrite it.
- Load `references/checklist-discipline.md`: `blocked_reason` is an item unable to proceed; `deferred_reason` on the write is human redirection. Do not interchange them.
- For spec fitness, load `references/requirements-quality-checklist.md`; its generator may not tick its items.
- Before closing, read `references/closing-a-story.md`, not just ticks: `done` with `blocked_reason` means skipped; OMH never observes landing.

Handoff policy:

Declare and update the checklist directly with `omh_todo`; a checklist item is a plan declaration and never dispatches, executes, or verifies anything.

Required inputs:

- the work to be tracked

Expected outputs:

- a declared checklist with exactly one active item
- explicit states as work completes

Artifact expectations:

- metadata-only `omh_todo/v1` plan todo owned by the declaring session

Safety rules:

- Checklist states never prove execution, verification, review, CI or merge.
- Do not declare a checklist for one-step, finished or directly answerable work.

## Runtime Evidence

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.
Reply in the user's own words and the host's own voice: OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
