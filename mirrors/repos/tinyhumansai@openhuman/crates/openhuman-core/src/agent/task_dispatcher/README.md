# task_dispatcher

The single executor for task-board cards. Turns a `TaskBoardCard` into work:
claims it via a compare-and-set (`Todo`/`Ready` → `in_progress`, so a
stale/concurrent re-dispatch is rejected), runs one autonomous agent turn
toward the card's objective, and writes the outcome back — `done` + evidence
on success, `blocked` + reason on failure.

Two dispatch paths converge on `dispatch_card`, so the claim is what keeps
them from racing:

- the **board poller** (`poller.rs`, `start_board_poller`) — a periodic sweep
  catching cards that arrive without a proactive trigger. Spawned from both
  `core/runtime/services.rs` (under `ServiceSet::proactive_task_pollers`) and
  `channels/runtime/startup/start_channels.rs`; a `OnceLock` makes the second call a
  no-op.
- **proactive triage** (`agent::triage::escalation`, `apply_decision` →
  `dispatch_linked_card`) — dispatches a card once triage has decided to act
  on it.

The poller sweeps only two boards: `user-tasks` (always, but only cards with
an `assigned_agent`, so a human's manually-created card is never auto-run)
and `task-sources` (only when `config.task_sources.enabled`). It never sweeps
conversation-thread boards; a chat-turn plan is gated on the turn itself
instead (see `agent::plan_review`).

## Files

- `mod.rs` — module doc, public re-exports, and `run_system_turn_on_thread`
  (a one-off system turn streamed into an existing chat thread, used by
  `agent::orchestration::background_delivery` to surface a finished detached
  sub-agent result back into the chat).
- `dispatch.rs` — `dispatch_card`: the plan-approval gate, the atomic claim,
  spawning the detached run, and registering it for cancellation.
- `executor.rs` — `resolve_executor` (a card's `assigned_agent` → personality,
  skill, or built-in agent, degrading to the default `orchestrator`),
  `run_autonomous` (builds the agent, pins the task-run iteration cap, streams
  progress into the session thread), and `write_back` (deterministic
  done/blocked board write-back; respects a card the run already
  self-blocked via `update_task`).
- `poller.rs` — `start_board_poller`: idempotent periodic sweep with
  diminishing-returns backoff, gated on `cron::scheduler_gate` capacity;
  reclaims stale runs before picking the highest-urgency dispatchable card.
- `prompt.rs` — `build_task_prompt` / `build_progress_instruction`: thin
  binding of `tinyagents_graph::todos::dispatch::prompt` to OpenHuman's tool
  names (`memory_recall`, `update_task`).
- `registry.rs` — in-flight run registry keyed by session `thread_id`;
  `cancel_session` / `cancel_session_scoped` abort a detached run and drive its
  cancellation write-back. `web_chat` calls the scoped variant as the
  `channel_web_cancel` fallback when no web-channel turn matched the thread.
- `types.rs` — `DispatchOutcome` (`Running` / `AwaitingApproval`),
  `ResolvedExecutor`, and the crate-backed `ActiveRun` alias.

## Related

- `agent::task_board` re-exports the board types
  (`tinyagents_graph::todos::{TaskBoard, TaskBoardCard, TaskCardStatus, ...}`)
  used throughout this module.
- `threads::todos/` is the compatibility surface that maps `BoardLocation`
  onto the TinyAgents stores, exposes the `openhuman.todos_*` RPC and
  `todo_*` tools, and owns the run ledger (`runs.rs`) this dispatcher reads
  and writes through.
- Selection and backoff policy (`pick_next_card`, `requires_plan_approval`,
  `PollCadence`) live in `tinyagents_graph::todos::dispatch::select`; this
  crate only tunes and wires them.
