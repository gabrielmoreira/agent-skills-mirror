---
name: goal
description: >-
  Outcome contract then autonomous loop. Use when the user runs /goal,
  /goal-loop, “capture goal”, “GOAL.md”, “until done”, or the work spans many
  files/steps and success must be falsifiable. Writes GOAL.md before wandering.
  /goal-loop is a mode of this skill (OBSERVE→PLAN→ACT→VERIFY→RECORD), not a
  third always-on skill. Not /loop (session interval ticks). Not /better
  (quality pass on an existing deliverable).
---

# /goal — Contract, then loop

**Slash:** `/goal` (optional project command file)  
**Templates:** [reference.md](reference.md)  
**Interval ticks (different skill):** Cursor `loop` skill — not this file

Turn an outcome into a **falsifiable contract**, then (when asked) run until the criteria pass or a hard blocker needs the user.

Say once: **“Running /goal.”** (or **“Running /goal-loop.”**)

## Modes

| Invocation | Behavior |
|------------|----------|
| `/goal …` | Author or update `GOAL.md`. Stop at plan if asked (`plan-only`). |
| `/goal-loop` | After a contract exists (or write it first): OBSERVE → PLAN → ACT → VERIFY → RECORD until criteria pass or blocked. |
| `stop goal` / `pause loop` | Halt after the current cycle. Leave `GOAL.md` accurate. |

## When to use

- Outcome spans many files/steps or more than one session
- User says `/goal`, “track this goal”, or wants autonomous completion criteria
- Ambiguous “build X” where success must be checkable

Skip: one-line mechanical edits, a named `/better` pass on an existing artifact, `/scale` volume (use `quality-at-scale`).

## GOAL.md contract (minimum)

Create or update `GOAL.md` at the project-agreed path (default: repo root `GOAL.md`). Fields:

1. **Objective** — one clear outcome sentence
2. **Success criteria** — measurable checks (commands, UI states, tests)
3. **Out of scope** — explicit non-goals
4. **Constraints** — stack, safety, no-touch files, deadlines
5. **Evidence plan** — how each criterion will be proven
6. **Current status** — `not started` \| `in progress` \| `blocked` \| `done`
7. **Next action** — single next step only

Do not mark `done` until success criteria are verified with **fresh** evidence.

Template: [reference.md](reference.md).

## /goal-loop cycle

1. **OBSERVE** — Read `GOAL.md`, repo state, errors, prior evidence. No edits yet if state is unclear.
2. **PLAN** — Smallest next action that advances a success criterion. Max-depth reasoning.
3. **ACT** — Execute only that action. Smallest safe diff.
4. **VERIFY** — Project verify path; capture exit codes / logs / screenshots.
5. **RECORD** — Update `GOAL.md` status, evidence, blockers, and the new **Next action**.

### Loop rules

- Continue until all success criteria pass **or** a hard blocker needs the user
- On failure: diagnose, adjust plan; do not thrash the same failed approach >2 times without a new hypothesis
- On blocker: stop; report exact blocker + hypotheses + what was tried
- Never claim done without VERIFY evidence
- Do not spawn a second parent orchestrator. Delegate by skill (`review-results`, workers) when the procedure says so.

## Compose

| Need | Use |
|------|-----|
| Quality pass on current artifact | `/better` |
| Recurring interval in this session | `/loop` (`skills-cursor/loop`) — not this skill |
| Parallel slices | `/swarm` — parent synthesizes and verifies once |
| Track B / high-signal OSS | `addvalue` after the contract names the target |
| Sensory ship | `/reviewresults` (`review-results`) |

## Must not

- Start `/goal-loop` with no success criteria
- Mark `done` without VERIFY evidence
- Duplicate `/loop` processes for the same purpose
- Swarm dependent steps onto the same mutable files
- Expand risk (push, secrets, paid APIs) without user rules
- Paste this skill into every turn as always-on text — **Read it when `/goal` fires**
