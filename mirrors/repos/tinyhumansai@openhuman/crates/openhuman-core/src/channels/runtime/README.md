# Runtime

Boots every enabled channel, keeps their listeners alive, and dispatches inbound messages into the agent loop. `mod.rs` exports only `start_channels`; `dispatch` and `supervision` internals are `pub(crate)` for `channels/tests/` under `#[cfg(test)]`.

## Files

| Path | Purpose |
| --- | --- |
| `startup.rs` (+ `startup/` — `start_channels.rs`, `credentials.rs`, `chat_workload.rs`, `prompt.rs`, `relay.rs`) | `start_channels` — builds the `channels::host` capability surface, hydrates secrets that live outside `config.toml` (`hydrate_channel_credentials`: email password, Yuanbao app secret, via `security::credentials::AuthService`), calls `tinychannels::build_channels`, registers the startup bus subscribers, spawns a supervised listener per channel and the optional relay runtime, then runs the dispatch loop |
| `supervision.rs` | `spawn_supervised_listener` — re-runs `Channel::listen` in a loop with exponential backoff plus full jitter, publishing `DomainEvent::ChannelConnected` / `ChannelDisconnected` / `HealthRestarted`; re-exports `tinychannels::runtime::compute_max_in_flight_messages` |
| `dispatch/` | The inbound pipeline that turns a `RuntimeChannelMessage` into an agent turn and a reply |
| `test_support.rs` | `#[cfg(any(test, debug_assertions))]` dispatch harness (`run_dispatch_harness`, `DispatchHarnessOptions`) used by `channels/tests/` and raw coverage |

## Inbound path

1. Each provider listener (`spawn_supervised_listener`, one per channel from `tinychannels::build_channels`) sends `traits::ChannelMessage`s on a bounded `mpsc` (capacity 100). A bridge task in `startup/start_channels.rs` wraps each into `RuntimeChannelMessage` and forwards it to the dispatch queue (also capacity 100). The relay runtime (`start_relay_runtime`) writes `RuntimeChannelMessage`s to that queue directly so relay inbound keeps its original TinyChannels envelope.
2. `run_message_dispatch_loop` (`dispatch/processor/dispatch_loop.rs`) drains the queue under a semaphore sized by `compute_max_in_flight_messages(listener_count)` and spawns a worker per message that calls `process_channel_runtime_message` (`processor/turn.rs`). `process_channel_message` is the `traits::ChannelMessage` wrapper for the same pipeline.
3. `process_channel_runtime_message` publishes `DomainEvent::ChannelMessageReceived`, then: if `channel_has_approval_surface` and `try_route_approval_reply` claims the message as a yes/no answer to a parked approval, stops there; otherwise starts typing, sends the ACK reaction (`select_acknowledgment_reaction`, threaded messages only), opens a streaming draft when the channel supports it, resolves scoping (`resolve_target_agent` + `build_visible_tool_set`), dispatches the turn over `BUS.native()` to the `agent.run_turn` handler (`agent::bus::register_agent_handlers`), sends the reply, and publishes `DomainEvent::ChannelMessageProcessed`.

## `dispatch/`

| Path | Purpose |
| --- | --- |
| `helpers.rs` | Stateless helpers: per-turn context block for non-web channels, deterministic ACK-emoji picker, worker join logging, scoped typing task |
| `routing.rs` | `AgentScoping`, `resolve_target_agent`, `build_visible_tool_set`, `connected_with_fallback` — picks the active agent for the channel and its visible/delegation tool surface from `Config`, `AgentDefinitionRegistry`, and the connected-integrations snapshot |
| `processor.rs` (+ `processor/` — `message.rs`, `approval.rs`, `turn.rs`, `dispatch_loop.rs`) | `RuntimeChannelMessage`, `channel_has_approval_surface`, `try_route_approval_reply`, `process_channel_message`, `process_channel_runtime_message`, `run_message_dispatch_loop` |
| `mod.rs` | Declares the three submodules and the `#[cfg(test)]` / `#[cfg(any(test, debug_assertions))]` re-exports the test modules reach through `super::*` |

Two policy points here: `channel_has_approval_surface` is `true` only for `TELEGRAM_APPROVAL_CLIENT_ID`, so other channels still run in the legacy "no chat context, silently allow" state until they get a surface subscriber; and scoping is per channel (`resolve_target_agent(&msg.channel)`), falling back to `AgentScoping::unscoped()` (every registered tool visible) when the registry is not initialised or the target agent is unknown.

## Called by

`channels::start_channels` is re-exported from `channels/mod.rs` and spawned by `spawn_channels_service` in `crates/openhuman-core/src/core/runtime/services.rs`, unless `OPENHUMAN_DISABLE_CHANNEL_LISTENERS` is set or `channels_config.has_listening_integrations()` is false. Web-chat-only desktop cores therefore never run it; `bus::ChannelInboundSubscriber` and the web-only proactive subscriber are registered on the always-on boot path in `core/jsonrpc.rs` instead.

## Tests

- `startup_tests.rs`, `startup_email_secret_tests_tests.rs`, `startup_yuanbao_secret_tests_tests.rs` (secret hydration precedence).
- `supervision_tests.rs`.
- `dispatch_tests.rs` (helpers: ACK reaction categories, context block shape), `dispatch/mod_scoping_tests_tests.rs` (`build_visible_tool_set` / `AgentScoping`), `dispatch/mod_approval_surface_gating_tests_tests.rs` (`channel_has_approval_surface`), `dispatch/routing_connected_fallback_tests_tests.rs` (`connected_with_fallback`: authoritative snapshot vs cached fallback on unavailable/timeout).
- End-to-end dispatch coverage lives in `channels/tests/` (`runtime_dispatch`, `runtime_tool_calls`, `discord_integration`, `telegram_integration`, `health`).
