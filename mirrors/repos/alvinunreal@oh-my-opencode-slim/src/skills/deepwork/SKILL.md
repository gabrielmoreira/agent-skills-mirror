---
name: deepwork
description: High-cost orchestrator workflow for large, high-risk, multi-phase coding efforts with meaningful dependencies and review gates. Do not activate for routine multi-file changes.
---

# Deepwork

Deepwork is an orchestrator workflow for heavy coding sessions: multiple
dependent phases, cross-cutting architectural change, unsafe-to-partially-ship
migration, or sustained coordination across specialist lanes. Never infer it
merely because a task touches multiple files; skip it for trivial edits, quick
docs changes, simple bug fixes, or routine bounded features.

## Core Contract

When deepwork is active, the orchestrator must manage the work as a scheduler,
not as the default implementation worker.

## Setup and Deepwork State

`.slim/deepwork/` holds exactly two shapes: the pinned router head
`.slim/deepwork/<session-id>.md`, and one directory per task,
`.slim/deepwork/<task-slug>/`, for that task's progress file and topic
files. Route content to one address: status, open items, one-line verdicts
→ the progress file; full analyses and verdicts → a topic file;
deliverables (code, specs, data, docs) → real project paths; scratch
intermediates → nowhere. `.slim/deepwork/.runtime/` is machine-written
guard bookkeeping (receipts, claim markers) — never read by the workflow;
guards record in shadow mode by default.

### Pinned Router Head

The activation prompt pins `.slim/deepwork/<session-id>.md`, updated in
place; re-running `/deepwork` reuses it. Never modify
another session's file; only the orchestrator writes it. At most 12 lines:
`status: active` (flip to `status: completed` when the session's work
concludes), then `task:`, `slug:` (its task directory), `phase:`, `next:`,
`blockers:` — one line each. A session without a task keeps only the
`status:` line. The head is a hint: on conflict, the task progress file
wins.

Before creating any deepwork file, ensure `.gitignore` contains
`.slim/deepwork/` and `.ignore` contains `!.slim/deepwork/` plus
`!.slim/deepwork/**`, adding only missing entries.

### Task Progress File

Each task keeps one progress file,
`.slim/deepwork/<task-slug>/progress.md` — at most 80 lines, rewritten in
place, never appended to. Head: one-line fields — `status: active`, current
phase, next step, frozen constraints (a constraint not written here is
gone). Below: an open-items checklist (3–8 items) and a dated log folding
every closed phase or decision into one line — `[x] name: one-line
conclusion (see <file>)`. Update at every phase close, decision, and
review, folding as you go; the head and log-line format are the only fixed
shapes. Claim a task with `mkdir -p .slim/deepwork` then a plain
`mkdir .slim/deepwork/<task-slug>` (no `-p` on the task directory); on
success, write its `slug:` into the pinned head — flipping a
reused head's `status:` back to `active` — before working. If the
directory already exists: a `slug:` in another session's `status: active`
head means claimed; otherwise adopt it by writing the `slug:` yourself.
Full delegated output lands verbatim in
`<task-slug>/<topic>.md` — written by the lane itself when it can write,
transcribed by the orchestrator when it cannot; the progress file gets
only a one-line conclusion plus the path. Never paste
`@council`/`@oracle`/`@librarian` output into a progress file or fork
one. The artifact's first line is the lane's one-line conclusion, the
same line it returns; accept lane completion only after re-reading the
artifact from disk and finding that first line (on miss, re-check once).
Past ~400 lines, consolidate a topic file — one per topic, new versions
overwrite old ones.

### Resuming

On resume or after compaction, read one chain, one file per hop: the
pinned head → the progress file its `slug:` points to → the topic files
its pointers reference. Nothing else. To find an existing task, read task
status lines only (`grep -m1 '^status:' .slim/deepwork/*/progress.md`)
plus the pinned heads' `status:` and `slug:` lines; skip completed tasks,
any task whose slug sits in another session's `status: active` head, and
slug-less heads (legacy — never claimable, noted once); after picking
one, do not read other task directories.

## Planning

- before dispatch, draft a phased implementation/delegation plan: a small number
  of coherent phases from the work's dependencies and natural delivery
  boundaries; do not split work merely to reduce an Oracle review's scope;
- make an `@oracle` review mandatory after each phase; record the phase order,
  specialist ownership, gate order, and one-line gate rationale in the deepwork
  file; share a compact version with the user;

## Phase Execution

- before each implementation phase, decide the execution path: what can run in
  parallel, what must be sequential, which specialists to delegate to, and
  whether to split the same agent into multiple bounded lanes;

### Scheduler Discipline

Use the scheduler model throughout:

- record task/session IDs and ownership boundaries;
- wait for hook-driven background completion before consuming background results;
- avoid blocking Orchestrator lane while background jobs run; if no independent
  work remains, stop briefly and let the completion event resume the workflow;
- do not advance to the next phase while relevant jobs are running or terminal
  results are unreconciled.

## Phase Gate and Commit

- after each planned phase, run relevant validation, update the task progress file,
  then request its planned `@oracle` gate before continuing;
- before its planned Oracle gate, record in the task progress file the phase goal,
  changed paths, validation evidence, the specific decision or risk to review,
  and accepted research with file references, so Oracle reviews established
  context rather than repeating discovery;
- when the phase changes module boundaries, dependency direction, or file
  placement, run an `@explorer` structure scan in parallel with the Oracle gate;
- reconcile review findings, perform one bounded remediation pass for material
  issues, including simplify/readability feedback, and validate that pass with
  focused evidence;
- create a focused commit when the phase is an independently valid delivery
  boundary before starting the next phase;

### Oracle Re-Reviews

Every planned Oracle gate has one initial review and may have at most two
re-reviews. Request a re-review only when the remediation materially changes
the reviewed decision or risk, or when the original concern cannot be verified
with focused evidence. Do not spend a re-review on a mechanical or
already-verified change.

State the attempt in every Oracle prompt, for example:

```text
Gate 2 — review attempt 2 of 3 (1 re-review remaining)
```

For re-reviews, tell Oracle to prioritize unresolved material findings, risks
introduced by remediation, and whether prior findings are resolved. It must not
reopen accepted, unchanged, or resolved concerns. When the two re-reviews are
exhausted, record any remaining material risk or blocker in the task progress file
and ask the user whether to accept the risk, change scope, or authorize an
exceptional additional review.

## Designer Handoff Guardrail

When a deepwork phase includes `@designer`, treat the delivered UI/UX as
accepted design intent for later phases. Record any important design decisions in
the task progress file before continuing.

After designer work:

- preserve layout, rhythm, hierarchy, motion, spacing, color, affordances,
  responsiveness, and component feel;
- review and improve user-facing copy with grounded, normal wording, but do not
  change visual structure or interaction intent;
- route follow-up visual, responsive, motion, hierarchy, polish, or
  component-feel changes back to `@designer`;
- use `@fixer` only for bounded mechanical follow-up that preserves the design
  exactly, such as wiring, tests, type fixes, or non-visual behavior changes;
- if design intent must change, record why in the task progress file before changing
  it.

## Completion

When the work concludes, rewrite the task progress file in place into a
tombstone of at most 15 lines: first line `status: completed`, then the
final conclusion, pointers to key deliverables, surviving frozen
constraints, and the date. Drop the log and checklist. Move nothing; add
no index files or ledgers. A finished task directory is read by nothing
and may be deleted at any time, without record.

- finish with final validation and a concise summary.
