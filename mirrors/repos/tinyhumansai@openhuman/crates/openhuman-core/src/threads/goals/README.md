# goals

Compatibility surface for OpenHuman thread-goal callers.

The goal model and behavior are owned by `tinyagents_graph::goals`: types,
lifecycle (active / paused / budget-limited / complete), the durable KV store,
budget accounting, and prompt rendering. Types and business logic are not
redeclared here — `ThreadGoal` and `ThreadGoalStatus` are re-exported from the
crate.

OpenHuman keeps this module to preserve app-specific integration:

- `store.rs` adapts the historical `store::*(workspace_dir, …)` call surface
  onto the crate's `graph.goals` KV store, resolving the store from
  `workspace_dir` and flattening the crate's `TinyAgentsError` to `String`.
  `clear` also deletes any leftover legacy file for the thread.
- `ops.rs` wraps the store in `RpcOutcome` handlers shared by RPC and CLI, and
  publishes `DomainEvent::ThreadGoalUpdated` / `ThreadGoalCleared` on mutation.
- `schemas.rs` exposes `openhuman.thread_goals_<function>` JSON-RPC: `get`,
  `set`, `complete`, `pause`, `resume`, `clear`. Handlers load the active
  config for `workspace_dir` and delegate to `ops`.
- `tools.rs` adapts tinyagents' model-facing goal controls to OpenHuman's
  `Tool` trait: `goal_get`, `goal_set`, `goal_complete` (asymmetric ownership —
  pause/resume/budget-limit are system-driven, with no model tool). Each tool
  resolves its target thread from the ambient `current_thread_id`, never from
  an argument.
- `continuation.rs` is the heartbeat adapter that injects one autonomous
  continuation turn when an active goal's thread goes idle, gated by
  `heartbeat.goal_continuation_enabled`, one-shot suppression, and a
  process-wide `Semaphore(1)`. `run_continuation_tick` currently has no
  production caller; only its unit tests invoke it.
- `runtime.rs` offers `load/resume/pause/complete/clear_for_current_thread`
  over the ambient thread, folds completed-turn usage into the active goal
  (`account_turn_against_goal`), and implements `GoalBudgetStopHook`, a
  `StopHook` that pauses an in-flight turn once running usage would exceed the
  goal's budget.
- `migration.rs` imports the retired file-backed `thread_goals/<hex>.json`
  store into the crate's `graph.goals` namespace at startup; existing
  tinyagents values are never replaced.

Callers: `agent::harness::session::turn` (load/resume on turn start,
`GoalBudgetStopHook`, post-turn accounting), `agent::orchestration::tools`
(`store::set_if_absent` during context preparation), `tools::ops` (registers
the three `goal_*` tools), `core::all` (controller registry), and
`core::runtime::services` (awaits `migrate_legacy_goals` at startup). The
external `thread_goals.*` RPC namespace and `goal_*` tool names remain stable.
