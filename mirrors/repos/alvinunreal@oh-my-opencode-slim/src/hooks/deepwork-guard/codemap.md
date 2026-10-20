# src/hooks/deepwork-guard/

## Responsibility

Machine evidence for the deepwork contract's acceptance protocol (#1389/#1390).
Two pieces, all silent when passing — the cost is code, not context:

- **Receipts**: every write into a task directory (`.slim/deepwork/<slug>/`)
  is recorded as a structured receipt line (path, bytes, first-bytes hash,
  sessionID) under `.slim/deepwork/.runtime/receipts/<slug>.jsonl`. Witness
  only — never blocks, never mutates tool output.
- **Completion gate**: a progress file flipping INTO `status: completed`
  (flip detection — re-edits of an already-completed file are not flips) is
  validated against receipts — every artifact the tombstone references must
  have a receipt. Write completions carry the full content in args; edit
  completions are simulated from the current content (plain string
  replacement, mirroring the edit tool's semantics) — both are blocked
  before they land (enforce) or logged as would-denies (shadow). The after
  phase is the safety net for anything the simulation misses: it gates
  landed flips from the landed file, prunes receipts on pass, and on missing keeps them as evidence while the alert
  rides the tool output (an after-hook throw would be swallowed by the
  per-hook error isolation). The gate targets the task progress file —
  the contract's completion ritual. The router head's status flip (a
  root-level file) is a session-hold state with no artifacts to validate;
  deliverables in repo paths are receipted by git itself.

## Design

### Core Abstraction
Factory `createDeepworkGuardHook(ctx)` returns `tool.execute.before` +
`tool.execute.after` handlers, dispatched from the plugin's wrapped chains
(rejecting before-hooks run before recording ones; after-hooks are
error-isolated).

- `tool.execute.before`: resolves the write's task slug, gates completion
  flips, captures the path for the after phase.
- `tool.execute.after`: stats the captured file and appends the receipt.
  The before/after coupling is a `Map<callID, CapturedWrite>` capped at
  256 entries (oldest evicted).

### State Management
- All state is on disk under `.slim/deepwork/.runtime/` (machine-owned
  bookkeeping; the workflow never reads it). No in-memory session state
  beyond the callID capture map.

### Configuration
- Off switch: the existing `disabled_hooks` key (`"deepwork-guard"` entry,
  enum single-sourced in `src/config/schema.ts`).
- Mode: `deepworkGuardMode: "shadow" | "enforce"` (default shadow); hot-read
  per call; the schema rejects invalid values (same as `image_routing`).
- Config is hot-read per call via `loadPluginConfig(directory, { silent:
  true })`; an absent or unreadable config keeps the guard on in shadow.

### Failure Behavior
- Receipts: fail-open (a stat/read failure records nothing, logs).
- Completion gate: fail-closed only in enforce mode; shadow never blocks.
- The deny message states the violated rule, lists the unverified artifacts,
  and names the config escape (`deepworkGuardMode: "shadow"`).

### Non-Goals (per the multi-seat review)
- No path-shape deny guard (phase 3, evidence-gated graduation).
- No context injection (the SKILL.md contract already carries the lane
  rules — injection would be prompt engineering by code).
- No lock/lease primitives (atomic `wx`/mkdir + mtime renewal suffice;
  Trellis has none either).
- No session-end auto-flip (no clean end event; misfires kill live tasks).
