---
name: "omh-todo-checklist"
description: "[omh] Hermes adaptation for declaring and advancing the metadata-only plan todo checklist the OMH HUD renders above the prompt input, in an ordinary session with no delivery engine running. Use when the user says: todo-checklist, plan checklist, todo checklist, phase checklist, declare a plan checklist, declare the plan todo, show the plan todo, clear the plan todo."
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
- Every write sent the whole list back, so no item was dropped by omission.
- Item states are described as declarations; observed results are cited separately or named as missing.
- A stopped plan names which of the two reasons applies -- an item that cannot proceed, or a person steering elsewhere.

## Recovery Notes

- If items disappeared after a write, the write sent a partial list; re-send every item, since `action=set` replaces rather than merges.
- If the panel shows nothing, read the current projection with `action=show` before re-declaring, so an existing checklist is not overwritten.
- If the user redirects the session away from the plan, record that on the write rather than deleting the checklist or marking its items done.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `live-incident-response`, `automation-blueprint`, `github-event-ops`, `github-issue-intake`, `buzz`, `+37 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when the user wants a declared, HUD-visible plan checklist for the work at hand, or wants to read, advance, or clear one, without starting a delivery engine.

    Strong routing signals: `todo-checklist`, `$todo`, `plan checklist`, `todo checklist`, `phase checklist`, `declare a plan checklist`, `declare the plan todo`, `show the plan todo`, `clear the plan todo`

## Catalog Metadata

Category: `operator`
Phase: `observability`
Hermes role: `tracker`
Quality tier: `evidence-gated`
Reasoning demand: `light`

Quality bar:

- Items are plan declarations and never execution evidence: marking one done records that you say it is done, which is not an observed result and never substitutes for one.
- Keep exactly one item active. Two active items make the HUD unable to say where the run is, which is the only thing the panel exists to answer.
- `action=set` replaces the whole list: send every item back on every write, including the ones that did not change, or the omitted ones are silently dropped. There is no partial update.
- The checklist belongs to the session that declared it -- another TUI, Slack, or Discord session neither sees nor overwrites it -- so do not tell a user their checklist is visible somewhere it is not.
- Two different things stop a plan advancing and they are not interchangeable: an item that cannot proceed carries `blocked_reason`, and a person steering the session elsewhere is `deferred_reason` on the write. Load `references/checklist-discipline.md` before using either.

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

- Do not present checklist states as execution, verification, review, CI, or merge evidence; an item marked done records a declaration, not an observed result.
- Do not declare a checklist for work that is one step, already finished, or answerable directly; the checklist costs a tool call and a panel, and buys nothing on work that does not span turns.

## Runtime Evidence

Preferred harness for this skill: `coding-handling`.

```sh
omh runtime record --skill todo-checklist --harness coding-handling --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
