# socket/medulla

The Medulla **harness plane**: binds the backend's `medulla:*` Socket.IO
events to an OpenHuman agent session so a Medulla operator running in the
backend can drive this core as a delegated sub-agent, probe its capabilities,
and read or author its saved workflow graphs.

It rides the existing authenticated backend socket owned by
`crate::platform::socket::SocketManager`; transport, handshake auth, and
reconnection live there. Inbound events are dispatched from
`crates/openhuman-core/src/platform/socket/event_handlers.rs`; outbound events
go through `global_socket_manager().emit`.

Not to be confused with `crates/openhuman-core/src/medulla/`, which is
OpenHuman as a Medulla **client** (HTTP/SSE to the Medulla backend). This
directory is the opposite direction: OpenHuman as a Medulla **worker**. One
binary can be both.

## Key files

| File | Role |
| --- | --- |
| `crates/openhuman-core/src/platform/socket/medulla/mod.rs` | `MedullaTaskManager` (`start_task` / `steer_task` / `abort_task` / `abort_all`), the per-task driver, `emit_register_agents`, `handle_capabilities_request`, and the `emit` helpers. |
| `crates/openhuman-core/src/platform/socket/medulla/payloads.rs` | Serde wire types for every event (camelCase on the wire) and the `EVENT_*` name constants. |
| `crates/openhuman-core/src/platform/socket/medulla/envelope.rs` | `HarnessEnvelope` / `HarnessEventKind` and `progress_to_event_kind`, mapping `AgentProgress` onto the Medulla harness envelope (`tinyplace.harness.session.v2`). |
| `crates/openhuman-core/src/platform/socket/medulla/workflows.rs` | The workflow plane: the host-supplied `WorkflowBridge` trait, `set_workflow_bridge` / `clear_workflow_bridge`, `emit_register_workflows`, `handle_workflow_request`, and the bridge/connection generation tokens. |
| `*_tests.rs` | Sibling test suites, included via `#[path]`. |

## Protocol

Down (backend → OpenHuman), matched by name in `event_handlers::handle_sio_event`:

| Event | Payload | Handler |
| --- | --- | --- |
| `medulla:task_run` | `TaskRun { task_id, cycle_id, session_id?, instruction, agent_id?, timeout_ms }` | `MedullaTaskManager::start_task` |
| `medulla:task_send` | `TaskSend { task_id, input }` | `MedullaTaskManager::steer_task` |
| `medulla:task_abort` | `TaskAbort { task_id }` | `MedullaTaskManager::abort_task` |
| `medulla:capabilities_request` | `CapabilitiesRequest { probe_id, agent_id }` | `handle_capabilities_request` |
| `medulla:workflow_request` | `WorkflowRequest { request_id, op, workflow_id?, kind?, instruction?, agent_id? }` | `workflows::handle_workflow_request` |

Up (OpenHuman → backend):

| Event | Payload | When |
| --- | --- | --- |
| `medulla:task_envelope` | `TaskEnvelope { task_id, envelope }` | Each mapped `AgentProgress` item during a task, plus terminal error envelopes. |
| `medulla:task_result` | `TaskResult { task_id, ok, reply, usage?, error? }` | Once per task, always. |
| `medulla:register_agents` | `RegisterAgents { agents }` | On every socket `ready` (`agent::registry::default_agents`); the backend drops the roster on disconnect. |
| `medulla:register_workflows` | `RegisterWorkflows` | On every `ready` and whenever a `WorkflowBridge` is (re)installed or the flows store changes; same lifetime as the roster. |
| `medulla:capabilities_result` | `CapabilitiesResult { probe_id, capabilities }` | Answer to a probe: `ready`, `summary`, `cwd` (bridge `action_dir`), advertised `workflows`. |
| `medulla:workflow_result` | `WorkflowResult { request_id, ok, data?, error? }` | Answer to a workflow round trip, `ok: false` with a readable message on any failure. |

Every down event is request/response against a server-side deadline (ten
seconds for a probe or workflow read, ten minutes for a `copilot` turn), so
silence is never free. Both request handlers always reply, even when the
answer is an error: an undecodable `capabilities_request` or
`workflow_request` is answered from the raw `probeId` / `requestId` via
`reject_unparsed_capabilities_request` / `workflows::reject_unparsed_request`.
The only path that stays silent is a socket that is already gone, which the
server handles by retiring the waiter on disconnect.

## Task lifecycle

`start_task` registers the task (a latching `CancellationToken` for abort and
an unbounded steering channel) and spawns `drive`:

1. `build_agent` loads config, initialises `AgentDefinitionRegistry`, builds
   `Agent::from_config_for_agent(agent_id)` (default `orchestrator`), tags
   the event context `medulla:<task_id>` / `medulla_harness`, and refreshes
   integrations and delegation tools. A build failure still emits a fatal
   error envelope and a `task_result { ok: false }`.
2. `timeout_ms` is one wall-clock budget for the whole task, not per turn.
   Each turn runs `agent.run_single` under `AgentTurnOrigin::ExternalChannel
   { channel: "medulla_harness", reply_target: task_id }`, raced (`biased`)
   against the abort token and the remaining budget.
3. A forwarder task maps `AgentProgress` to envelopes with a monotonically
   increasing `seq`; `TurnStarted` / `IterationStarted` / `TurnCompleted`
   become `status`, text and thinking deltas become `agent_message` /
   `agent_thinking`, tool calls become `tool_call` / `tool_result`, and
   `SubagentAwaitingUser` becomes `approval_request`. Unmapped variants are
   dropped.
4. After a completed turn, steering input already queued (or arriving within
   `STEER_DRAIN_GRACE`, 50 ms) runs as a follow-up turn on the same session;
   otherwise the task settles with the reply and `take_last_turn_usage_totals`.
5. Abort, timeout, and turn errors settle as `ok: false` with `error` =
   `"aborted"` / `"timeout"` / the error text; timeout and error also emit a
   fatal `error` envelope first.

A `task_run` for an already-running `task_id` is ignored; `task_send` and
`task_abort` for unknown ids are logged and dropped.

## Workflow plane

`WorkflowBridge` is the store side, supplied by the host at startup so this
module never parses a graph, node, or config field; graphs, node-kind
catalogs, and run lists cross as opaque `serde_json::Value`. OpenHuman
installs `crates/openhuman-core/src/flows/medulla_bridge.rs`
(`FlowsWorkflowBridge` over the SQLite flows store) from
`core/runtime/services.rs` at boot and again on the
`socket.connect_with_session` path (`platform/socket/ops.rs`); `flows` also
re-advertises on store changes. Synchronous reads (`get`, `node_kinds`,
`runs`) run on a blocking thread; `copilot` is async because it is a whole
authoring turn, and its outcome is derived from a re-read of the store rather
than the model's claim.

Two cancellation generations guard stale work: a bridge generation (rotated by
`set_workflow_bridge` / `clear_workflow_bridge`) and a connection generation
(begun on `ready`, ended on disconnect), so a registration, probe, or request
spawned against an old bridge or a closed socket is discarded instead of
answered on the wrong connection. `emit_register_workflows` also sequences
its reads so a slower, older snapshot never overwrites a newer advert.

## Dependencies

- `crate::agent::{Agent, progress::AgentProgress, turn_origin, registry, harness::AgentDefinitionRegistry}`
- `crate::platform::socket::{global_socket_manager, SocketManager}` for emits
- `crate::config::rpc::load_config_with_timeout` when building a task agent
- `tokio_util::sync::CancellationToken`, `parking_lot`, `futures` (panic
  isolation around bridge methods)

## Used by

- `crates/openhuman-core/src/platform/socket/event_handlers.rs` — dispatches
  every down event and calls `emit_register_agents` /
  `emit_register_workflows` on `ready`.
- `crates/openhuman-core/src/platform/socket/manager.rs` — ends the
  connection generation on disconnect.
- `crates/openhuman-core/src/flows/medulla_bridge.rs` and
  `flows/ops/definitions.rs` — install the bridge and re-advertise workflows.
