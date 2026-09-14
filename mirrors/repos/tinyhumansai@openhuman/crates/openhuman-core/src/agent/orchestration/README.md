# Agent Orchestration

`agent::orchestration` is the control plane for coordinating multiple agent
workers from one parent session: agent teams, background command-center views,
declarative multi-phase workflows, git-worktree isolation for parallel coding
workers, and the tool surface LLMs call to spawn/steer/wait-on sub-agents. The
lower-level `agent::harness` remains the execution engine — prompt
construction, policy-filtered tools, model selection, and the sub-agent run
loop itself.

Execution fans out on TinyAgents **graphs**: `workflow_runs` schedules phase
DAGs on a graph engine, `agent_teams` routes members through a
conditional-routing graph, `delegation` wires the durable
plan→execute⇄review→finalize graph, and parallel fanout goes through
`tinyagents_graph::parallel::map_reduce`. What stays in this module is the
product layer: durable SQL/JSON run ledgers, validation, cancellation
semantics, compatibility events, and JSON-RPC/tool response formatting.

## Responsibilities

- Register, wait on, and cancel child agent runs (`ops.rs`,
  `AgentOrchestrationSession`) as thin wrappers over TinyAgents'
  `DetachedTaskRegistry`.
- Durable multi-agent models with their own run-ledger tables: agent teams
  (`agent_teams/`), declarative phase-graph workflows (`workflow_runs/`), and
  the plan→execute⇄review→finalize graph (`delegation.rs`).
- A read-only command-center view over background agent runs plus stop/retry/
  continue/follow-up control verbs (`command_center/`).
- Git-worktree isolation so parallel coding workers never clobber the same
  checkout (`worktree.rs`, `worktree_schemas.rs`).
- User-driven cancel/steer of detached (`spawn_async_subagent`) background
  sub-agents from the frontend background-tasks drawer (`subagent_control.rs`).
- Mirroring detached sub-agent lifecycle into a TinyAgents task store, batching
  finished background results back into chat, and settling run-ledger rows
  from the global bus regardless of the parent turn's lifecycle
  (`running_subagents*.rs`, `background_completions.rs`,
  `background_delivery.rs`, `run_ledger_finalize.rs`).
- A shared root `ParentExecutionContext` builder for surfaces that spawn real
  sub-agents from a background task with no enclosing agent turn on the stack
  (`parent_context/builder.rs`).

## Key files

- `mod.rs` — module wiring and re-exports.
- `ops.rs` / `types.rs` — `AgentOrchestrationSession`, `OrchestrationError`,
  `AgentSnapshot`, `OrchestrationTaskStatus`, `SpawnAgentRequest`/`Response`,
  `WaitAgentOptions`/`Response`.
- `agent_teams/` — durable lead/worker team coordination (issue #3374):
  atomic task claiming, dependency validation, quality-gated completion, and
  live teammate execution via `start_member`.
- `command_center/` — read-only grouped view of background agent runs
  (`ops.rs`) plus stop/retry/continue/follow-up transitions (`control.rs`).
- `workflow_runs/` — declarative `WorkflowDefinition` phase graphs (issue
  #3375), the builtin "parallel research with cross-checking" workflow,
  structural/agent validation, and the live execution engine (`engine.rs`).
- `delegation.rs` — production worker for TinyAgents' durable
  plan→execute⇄review→finalize graph; every stage runs through `run_subagent`.
- `spawn_parallel_graph.rs` + `spawn_parallel_graph/` (`request.rs`, `staging.rs`,
  `dispatch.rs`, `workers.rs`, `collect.rs`, `graph.rs`, `run.rs`, `types.rs`) —
  the fanout behind
  `spawn_parallel_agents`: request/claim validation, worktree preflight, and the
  bounded `map_reduce` worker run; the tool file only translates `ToolResult`.
- `subagent_events.rs` — the single owner that constructs and publishes
  `DomainEvent::Subagent{Spawned,Completed,Failed,AwaitingUser}`.
- `subagent_control.rs` — manual cancel/steer of detached background
  sub-agents; the manual counterpart to the automatic thread-close
  cancellation in `crate::threads`.
- `worktree.rs` / `worktree_schemas.rs` — `OpenHumanWorktreeIsolation` adapter
  over TinyAgents' host-agnostic git-worktree plumbing, plus the
  list/status/diff/remove RPC surface.
- `subagent_sessions/` — durable subagent session records
  (`DurableSubagentSessionSummary`, `SubagentSessionStore`) used for
  reuse/dedup decisions across turns.
- `parent_context/builder.rs` — `build_root_parent` / `with_root_parent`, the
  single blessed entry point for constructing a root `ParentExecutionContext`
  outside an agent turn.
- `running_subagents.rs` + `running_subagents/` (`registry.rs`, `roster.rs`,
  `resolve.rs`, `cancel.rs`, `steering.rs`, `wait.rs`, `task_ledger.rs`) —
  detached sub-agent registry mirror; `background_completions.rs` /
  `background_delivery.rs` —
  queue and idle-gated, debounced, batched delivery of finished background
  runs back into chat; `run_ledger_finalize.rs` — global-bus subscriber that
  settles ledger rows for runs that outlive their spawning turn.
- `tools.rs` — declares the LLM-callable tool files under `tools/` (see
  [Agent tools](#agent-tools)).

## Public surface

- `AgentOrchestrationSession`, `OrchestrationError` — `ops.rs`.
- `AgentSnapshot`, `OrchestrationTaskStatus`, `SpawnAgentRequest`/`Response`,
  `WaitAgentOptions`/`Response` — `types.rs`.
- `OpenHumanWorktreeIsolation`, `BaseRef`, `WorktreeError`, `WorktreeStatus` —
  `worktree.rs`.
- Controller schema/registration pairs re-exported from `mod.rs`:
  `all_agent_team_*`, `all_command_center_*`, `all_workflow_run_*`,
  `all_worktree_*`, `all_subagent_control_*`.

## RPC

Five controller pairs are registered in `crate::core::all`:

| Namespace | Source | Methods |
| --- | --- | --- |
| `agent_team` | `agent_teams::{all_agent_team_controller_schemas, all_agent_team_registered_controllers}` | `create`, `list`, `get`, `assign_task`, `claim_task`, `message_member`, `list_messages`, `complete_task`, `shutdown_member`, `close`, `start_member` |
| `agent_work` | `command_center::{all_command_center_controller_schemas, all_command_center_registered_controllers}` | `list`, `control` |
| `workflow_run` | `workflow_runs::{all_workflow_run_controller_schemas, all_workflow_run_registered_controllers}` | `list_definitions`, `list`, `get`, `start`, `stop`, `resume` |
| `worktree` | `worktree_schemas::{all_controller_schemas, all_registered_controllers}` | `list`, `status`, `diff`, `remove` |
| `subagent` | `subagent_control::{all_controller_schemas, all_registered_controllers}` | `cancel`, `steer` |

## Agent tools

`tools.rs` declares the `tools/` directory files (via `#[path]`) and
re-exports them through `crate::tools` (`tools/mod.rs`:
`pub use crate::agent::orchestration::tools::*`). LLM-callable tools, by wire
name:

- Spawn: `spawn_subagent`, `spawn_async_subagent`, `spawn_parallel_agents`,
  `spawn_worker_thread`.
- Control: `steer_subagent`, `continue_subagent`, `close_subagent`,
  `wait_subagent`, `wait`, `wait_loop`, `list_subagents`.
- Delegation: `DelegateGraphTool` (`delegate_graph.rs`),
  `ArchetypeDelegationTool` and `SkillDelegationTool` (names set per
  instance, e.g. `delegate_to_integrations_agent`), `CollapsedDelegationTool`
  (`delegate_to`), and `agent_prepare_context`.

`dispatch.rs` (`dispatch_subagent`, the shared spawn path every tool above
calls), `awaiting_user.rs` (the awaiting-user envelope), and
`worker_thread.rs` (worker thread creation) are `pub(crate)` helpers, not
tools. Execution itself routes through `agent::harness::run_subagent`.

## Persistence

- `tinyagents_session::run_ledger` — the `agent_runs`,
  `agent_teams`/`agent_team_members`/`agent_team_tasks`, and `workflow_runs`
  tables plus the shared `run_events` log, backed by
  `{workspace}/session_db/sessions.db` (see `agent/session_db/mod.rs`). Every
  spawn path (`spawn_subagent`, `spawn_async_subagent`,
  `spawn_parallel_agents`, `continue_subagent`, `dispatch`) writes a `running`
  `agent_runs` row; `run_ledger_finalize.rs` settles it from the global event
  bus so detached runs that outlive their spawning turn are not left `running`
  forever.
- `subagent_sessions/` — `SubagentSessionStore` writes
  `{workspace}/.openhuman/subagent_sessions.json` (atomic tmp-file rename).
- `delegation.rs` — checkpoints `DelegationState` through
  `tinyagents_graph::SqliteCheckpointer` in `graph_checkpoints.db` under the
  workspace.

## Policy inheritance

Policy inheritance is delegated to `agent::harness::run_subagent`, which
derives child tools, model routing, sandbox context, spawn depth, and
progress from the parent `ParentExecutionContext`. This module only adds
lineage and lifecycle semantics; it must not widen tool visibility beyond
what the harness exposes to the child.

## Dependencies

- `agent::harness` — `run_subagent`, `fork_context::ParentExecutionContext`,
  `definition::{AgentDefinition, AgentDefinitionRegistry}`.
- `agent::tinyagents::orchestration` — `DetachedTaskRegistry`,
  `OrchestrationTaskStatus`, `TaskId`.
- `tinyagents_session::run_ledger` — durable storage for teams, workflow runs,
  and agent run rows.
- `tinyagents_graph` — the graph engine used for workflow phase scheduling,
  agent-team routing, and parallel map/reduce fanout.
- `core::bus::BUS` — `DomainEvent::AgentOrchestration*` /
  `Subagent*` publication and subscription.
- `web_chat::progress_bridge` — the per-turn progress-channel counterpart to
  `run_ledger_finalize.rs`'s global-bus settlement.

## Used by

- `crate::tools` (`tools/mod.rs`) re-exports every tool in `tools/` for the
  LLM tool-calling loop.
- `threads` — the automatic thread-close cancellation counterpart to
  `subagent_control.rs`'s manual cancel.
- `crate::core::all` — registers the five controller pairs above.

## Notes

- Namespace `agent_team` is distinct from the existing `team` domain (backend
  org/team membership); `workflow_run` is distinct from the `workflows`
  domain (SKILL.md/WORKFLOW.md bundle discovery).
- `wait_agents` prunes an entry once it observes a terminal status — every
  in-tree caller spawns and waits exactly once.
- `worktree.rs` only ever operates on the user's project repo rooted at the
  agent's `action_dir`, never on OpenHuman's own source tree; `remove`
  refuses a dirty worktree unless `force = true`.
