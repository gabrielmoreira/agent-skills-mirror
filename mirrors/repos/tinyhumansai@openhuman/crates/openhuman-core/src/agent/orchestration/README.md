# orchestration

`agent::orchestration` is the control plane for coordinating multiple agent
workers from one parent session: agent teams, background command-center views,
declarative multi-phase workflows, git-worktree isolation for parallel coding
workers, and the tool surface LLMs call to spawn/steer/wait-on sub-agents. The
lower-level `agent::harness` remains the execution engine: prompt
construction, policy-filtered tools, model selection, and the sub-agent run
loop itself.

The generic coordination model lives in `tinyagents-orchestration`: team and
workflow types, validation, run-ledger services, workflow execution, member
prompt construction, message watermark delivery, and parallel task
staging/fanout. OpenHuman imports those APIs directly. This module retains the
product adapters: Config and root-parent construction, model/tool selection,
`run_subagent`, progress and BUS events, RPC/tool formatting, and OpenHuman's
worktree policy.

## Responsibilities

- Register, wait on, and cancel child agent runs ([`ops.rs`](./ops.rs),
  `AgentOrchestrationSession`) as thin wrappers over TinyAgents'
  `DetachedTaskRegistry`, including its ordered batch wait and shared deadline.
- Host adapters for durable teams and workflows: RPC schemas, root-parent
  worker execution, model selection, durable lifecycle CAS, and BUS/progress
  integration. Their host-neutral types, storage services, workflow scheduling,
  prompt composition, and delivery bookkeeping are in `tinyagents-orchestration`.
- A read-only command-center view over background agent runs plus stop/retry/
  continue/follow-up control verbs (`command_center/`).
- OpenHuman's `OpenHumanWorktreeIsolation` adapter and RPC surface; generic
  worktree operations are used directly from `tinyagents_harness::workspace`.
- User-driven cancel/steer of detached (`spawn_async_subagent`) background
  sub-agents from the frontend background-tasks drawer ([`subagent_control.rs`](./subagent_control.rs)).
- Mirroring detached sub-agent lifecycle into a TinyAgents task store, batching
  finished background results back into chat, and settling run-ledger rows
  from the global bus regardless of the parent turn's lifecycle
  (`running_subagents*.rs`, [`background_completions.rs`](./background_completions.rs),
  [`background_completions/store_adapter.rs`](./background_completions/store_adapter.rs),
  [`completion_notice.rs`](./completion_notice.rs),
  [`background_delivery.rs`](./background_delivery.rs),
  [`delivery_events.rs`](./delivery_events.rs)). Generic retry,
  give-up, replay, and router caching belong to TinyAgents' completion owner;
  OpenHuman keeps its thread session delivery and synchronous durable give-up
  writer. AgentRun status projection lives in
  [`agent_runs/subagent_finalize.rs`](../../agent_runs/subagent_finalize.rs),
  because that product ledger is separate from TinyAgents' task store. The delivery turn runs
  on the originating thread's cached chat session via
  `web_chat::run_system_turn_on_thread`, never on a throwaway host.
- A shared root `ParentExecutionContext` builder for surfaces that spawn real
  sub-agents from a background task with no enclosing agent turn on the stack
  ([`parent_context/builder.rs`](./parent_context/builder.rs)).

## Key files

- [`mod.rs`](./mod.rs): module wiring and re-exports.
- `ops.rs` / [`types.rs`](./types.rs): `AgentOrchestrationSession`, `OrchestrationError`,
  `AgentSnapshot`, `OrchestrationTaskStatus`, `SpawnAgentRequest`/`Response`,
  `WaitAgentOptions`/`Response`.
- `agent_teams/`: OpenHuman's member-worker adapter for TinyAgents'
  `TeamService::start_member_with_started`. The host supplies Config, the root
  parent context, model/tool execution and product failure events; the owner
  handles claim, active state, completion, and token-scoped cleanup.
- `command_center/`: read-only grouped view of background agent runs
  (`ops.rs`) plus stop/retry/continue/follow-up transitions (`control.rs`).
- `workflow_runs/`: OpenHuman's workflow RPC and executor adapters. The
  `WorkflowRunSupervisor` owns live generation/cancellation state; OpenHuman
  commits durable revision-CAS lifecycle transitions inside the owner's
  generation handoff, while retaining policy admission, root-parent
  construction and origin propagation. Pre-drive setup errors use the captured
  lifecycle revision; drive errors rely on engine lease-fenced lifecycle writes.
- [`delegation.rs`](./delegation.rs): production worker for TinyAgents' durable
  plan→execute⇄review→finalize graph; every stage runs through `run_subagent`.
- `spawn_parallel_agents` stages through
  `tinyagents_orchestration::parallel::Plan::stage_with_preflight` and fans out
  through the crate's `parallel::run`. OpenHuman owns identity/tool/workspace
  policy and its async progress and result projections. Staging only resolves
  definitions and trims prompts before admission; worktree creation and spawn
  events happen after policy and batch arbitration. Results are projected in
  input order after the worker batch completes. The sync-only `RunHooks` cannot
  carry these awaited host callbacks, so the adapter keeps them at the async
  preflight/execution and ordered-collection boundaries.
- [`subagent_events.rs`](./subagent_events.rs): the single owner that constructs and publishes
  `DomainEvent::Subagent{Spawned,Completed,Failed,AwaitingUser}`.
- `subagent_control.rs`: manual cancel/steer of detached background
  sub-agents; the manual counterpart to the automatic thread-close
  cancellation in `crate::threads`.
- [`worktree.rs`](./worktree.rs) / [`worktree_schemas.rs`](./worktree_schemas.rs): `OpenHumanWorktreeIsolation` and the
  list/status/diff/remove RPC surface. They call
  `tinyagents_harness::workspace` directly rather than maintaining aliases.
- `subagent_sessions/`: durable subagent session records
  (`DurableSubagentSessionSummary`, `SubagentSessionStore`) used for
  reuse/dedup decisions across turns.
- `parent_context/builder.rs`: `build_root_parent` / `with_root_parent`, the
  single blessed entry point for constructing a root `ParentExecutionContext`
  outside an agent turn.
- [`running_subagents.rs`](./running_subagents.rs) + `running_subagents/` (`registry.rs`, `roster.rs`,
  `resolve.rs`, `cancel.rs`, `steering.rs`, `wait.rs`, `task_ledger.rs`): the
  detached sub-agent host glue (registry instance and metadata, store path,
  steering, boot reconcile). The status type, wait, ledger helpers, roster and
  session resolution live in `tinyagents_orchestration::subagent`
  (`DetachedSubagentStatus`, `wait_detached`, `SubagentIdentity`, ...); batch
  waits call the owner's ordered `wait_many` API.
  `background_completions.rs` is the host adapter over the harness
  `tinyagents_tasks::CompletionRouter` and its owner pool, with a durable
  `DriverCompletionStore` in the storage backend scoped by profile/workspace;
  the router owns the queue, dedupe, tombstones (collected inline,
  stopped, cancelled thread), attempt counting and give-up, so a completion that
  was never delivered is redelivered after a restart
  (`background_delivery::recover_on_boot`, wired next to the orphaned-task
  reconcile in `core/runtime/bootstrap.rs`). `completion_notice.rs` is the
  `<background_agent_*>` wording (a `CompletionFormatter`) and the
  `[BACKGROUND_DELIVERY_FAILED]` give-up notice. `background_delivery.rs` keeps
  the host policy: idle-gated, debounced (3s), batched delivery of finished
  background runs back into chat and the system turn; its synchronous error
  callback writes the give-up notice before the owner releases its lease. The
  `agent_runs` domain separately subscribes to terminal sub-agent events to
  settle the product ledger for runs that outlive their spawning turn.
- [`fleet_tools.rs`](./fleet_tools.rs): decides which fleet-control tools (`wait_subagent`,
  `steer_subagent`, `wait_loop`, `close_subagent`) a given parent agent's
  definition actually exposes, so the delegation prompts and the
  `[active_subagents]` roster text never name a tool the model cannot call
  (#5701).
- [`tools.rs`](./tools.rs): declares the LLM-callable tool files under `tools/` (see
  [Agent tools](#agent-tools)).

## Owner call-site map

The host calls the owner's lifecycle APIs directly; the old generic loops are
removed rather than kept under new names:

- `AgentOrchestrationSession::wait_agents` uses `DetachedTaskRegistry::wait_many`
  for input ordering, one shared deadline and first-error behavior.
- Background delivery uses `CompletionDelivery::recover_on_boot_with_error`
  and `deliver_once_with_error`. TinyAgents owns retry, lease, replay, and
  give-up transitions. OpenHuman's synchronous failure callback appends the
  final notice before the lease is released. The rich awaited completion
  callback still writes workflow-proposal and incomplete-run framing; the plain
  owner status watcher is the sole generic TaskStore mirror.
- `start_member_run` keeps product active-member and claimable-task prechecks,
  then `TeamService::start_member_with_started` owns claim, active state,
  completion and token-scoped cleanup. The host returns the owner's receipt
  over a oneshot before continuing its real worker executor.
- Workflow start/resume/stop use `WorkflowRunSupervisor` generation APIs.
  OpenHuman commits durable start/resume transitions inside
  `start_scoped_with_commit` / `resume_scoped_with_commit`, so the durable CAS
  and generation handoff are serialized by the owner. Policy admission,
  root-parent construction and origin propagation remain host responsibilities.
  Stop captures the current handle before its revision CAS and cancels only
  that generation after the CAS succeeds. Pre-drive setup failures may update
  only their captured revision; once drive begins, the engine's lease-fenced
  lifecycle writes own durable errors, and the host only logs drive failures.
- Parallel dispatch uses `Plan::stage_with_preflight` and `parallel::run`.
  Preflight only resolves definitions and trims prompts; worktree creation and
  spawn events follow admission. Awaited host progress and results stay in the
  adapter, with result projection in input order after collection. Sync-only
  `RunHooks` cannot carry those awaited callbacks or preserve that order.
- The old `run_ledger_finalize` subscriber moved to
  [`agent_runs/subagent_finalize.rs`](../../agent_runs/subagent_finalize.rs):
  it is the product AgentRun projection over bus events, not a TinyAgents task
  status mirror.

## Public surface

- `AgentOrchestrationSession`, `OrchestrationError`: `ops.rs`.
- `AgentSnapshot`, `OrchestrationTaskStatus`, `SpawnAgentRequest`/`Response`,
  `WaitAgentOptions`/`Response`: `types.rs`.
- `OpenHumanWorktreeIsolation`: `worktree.rs`; direct TinyAgents worktree
  types are `GitWorktreeBaseRef`, `GitWorktreeError`, and
  `GitWorktreeStatus` from `tinyagents_harness::workspace`.
- Controller schema/registration pairs re-exported from `mod.rs`:
  `all_agent_team_*`, `all_command_center_*`, `all_workflow_run_*`,
  `all_worktree_*`, `all_subagent_control_*`.

## RPC

Five controller pairs are registered in `crate::core::all`:

| Namespace | Source | Methods |
| --- | --- | --- |
| `agent_team` | `agent_runs::agent_teams::{all_agent_team_controller_schemas, all_agent_team_registered_controllers}` | `create`, `list`, `get`, `assign_task`, `claim_task`, `message_member`, `list_messages`, `complete_task`, `shutdown_member`, `close`, `start_member` |
| `agent_work` | `agent_runs::command_center::{all_command_center_controller_schemas, all_command_center_registered_controllers}` | `list`, `control` |
| `workflow_run` | `agent_runs::workflow_runs::{all_workflow_run_controller_schemas, all_workflow_run_registered_controllers}` | `list_definitions`, `list`, `get`, `start`, `stop`, `resume` |
| `worktree` | `agent_runs::worktree_schemas::{all_controller_schemas, all_registered_controllers}` | `list`, `status`, `diff`, `remove` |
| `subagent` | `agent_runs::subagent_control::{all_controller_schemas, all_registered_controllers}` | `cancel`, `steer` |

## Agent tools

`tools.rs` declares the `tools/` directory files (via `#[path]`) and
re-exports them through `crate::tools` ([`tools/mod.rs`](../../tools/mod.rs):
`pub use crate::agent::orchestration::tools::*`). LLM-callable tools, by wire
name:

- Spawn: `spawn_subagent`, `spawn_async_subagent`, `spawn_parallel_agents`,
  `spawn_worker_thread`.
- Control: `steer_subagent`, `continue_subagent`, `close_subagent`,
  `wait_subagent`, `wait`, `wait_loop`, `list_subagents`.
- Delegation: `DelegateGraphTool` (`delegate_graph.rs`),
  `ArchetypeDelegationTool` (name set per instance, e.g. `research`),
  and `CollapsedDelegationTool` (`delegate_to`).
  There is no integrations delegate: connected Composio actions are
  `Deferred` tools on the orchestrator's own belt, found through
  `tool_search` and called directly ([`tools/orchestrator_tools.rs`](../../tools/orchestrator_tools.rs)).

`dispatch.rs` (the shared spawn path every tool above
calls), `awaiting_user.rs` (the awaiting-user envelope), and
`threads/worker_thread.rs` (worker thread creation) are `pub(crate)` helpers, not
tools. Live harness registrations use typed `ToolDispatch<(),
OpenHumanRunContext>` wrappers and fork the parent carrier for every child,
so cancellation, origin, progress, dispatch state, thread, and workspace stay
attached. `delegate_to` retains its concrete enum-to-agent routing table in
its schema metadata at registration; it never broadens a call by rebuilding
targets from the global agent registry. `delegate_graph` has a dedicated typed
registration for its durable plan→execute→review loop, while the optional
config-driven `delegate` registration preserves the configured executor and
races it against the inherited cancellation token. Execution itself routes through
`agent::subagent_host::run_subagent`.

## Persistence

- `tinyagents_session::run_ledger`: the `agent_runs`,
  `agent_teams`/`agent_team_members`/`agent_team_tasks`, and `workflow_runs`
  tables plus the shared `run_events` log, backed by
  `{workspace}/session_db/sessions.db` (see [`sessions/mod.rs`](../../sessions/mod.rs)). Every
  spawn path (`spawn_subagent`, `spawn_async_subagent`,
  `spawn_parallel_agents`, `continue_subagent`, `dispatch`) writes a `running`
  `agent_runs` row; the `agent_runs` domain settles it from the global event
  bus so detached runs that outlive their spawning turn are not left `running`
  forever.
- `subagent_sessions/`: `SubagentSessionStore` writes
  `{workspace}/.openhuman/subagent_sessions.json` (atomic tmp-file rename), or
  one `subagent_sessions` document per session under the acting agent's scope
  when a storage backend is configured (`store_documents.rs`).
- `running_subagents/task_ledger.rs`: the detached-task ledger is
  `{workspace}/.openhuman/orchestration_tasks.jsonl`, or `orchestration_tasks`
  documents per storage scope when a backend is configured
  (`task_ledger_documents.rs`); the boot orphan sweep is skipped on a shared
  backend.
- `delegation.rs`: checkpoints `DelegationState` through
  `tinyagents_graph::SqliteCheckpointer` in `graph_checkpoints.db` under the
  workspace.

## Policy inheritance

Policy inheritance is delegated to `agent::subagent_host::run_subagent`, which
derives child tools, model routing, sandbox context, spawn depth, and
progress from the parent `ParentExecutionContext`. This module only adds
lineage and lifecycle semantics; it must not widen tool visibility beyond
what the harness exposes to the child.

## Dependencies

- `agent::harness`: `run_subagent`, `fork_context::ParentExecutionContext`,
  `definition::{AgentDefinition, AgentDefinitionRegistry}`.
- `tinyagents_graph::orchestration`: `DetachedTaskRegistry`,
  `OrchestrationTaskStatus`, `TaskId`.
- `tinyagents_session::run_ledger`: durable storage for teams, workflow runs,
  and agent run rows.
- `tinyagents_graph`: the graph engine used for workflow phase scheduling,
  agent-team routing, and parallel map/reduce fanout.
- `core::bus::BUS`: `DomainEvent::AgentOrchestration*` /
  `Subagent*` publication and subscription.
- `web_chat::progress_bridge`: the per-turn progress-channel counterpart to
  `agent_runs::subagent_finalize`'s global-bus settlement.

## Used by

- `crate::tools` (`tools/mod.rs`) re-exports every tool in `tools/` for the
  LLM tool-calling loop.
- `threads`: the automatic thread-close cancellation counterpart to
  `subagent_control.rs`'s manual cancel.
- `crate::core::all`: registers the five controller pairs above.

## Notes

- Namespace `agent_team` is distinct from the existing `team` domain (backend
  org/team membership); `workflow_run` is distinct from the `workflows`
  domain (SKILL.md/WORKFLOW.md bundle discovery).
- `wait_agents` prunes an entry once it observes a terminal status. Every
  in-tree caller spawns and waits exactly once.
- `worktree.rs` only ever operates on the user's project repo rooted at the
  agent's `action_dir`, never on OpenHuman's own source tree; `remove`
  refuses a dirty worktree unless `force = true`.

## Further reading

- [Parent module README](../README.md)
- [Agent harness architecture](../../../../../docs/gitbooks/en/developing/architecture/agent-harness.md)
- [The orchestrator](../../../../../docs/gitbooks/en/features/orchestration.md)
- [Agent coordination tools](../../../../../docs/gitbooks/en/features/native-tools/agent-coordination.md)
