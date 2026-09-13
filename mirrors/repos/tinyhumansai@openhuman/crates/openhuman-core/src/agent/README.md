# Agent

Multi-agent orchestration domain. Owns the LLM tool-calling loop, sub-agent dispatch, conversation transcripts, the trigger-triage pipeline that classifies incoming external events, and the bundled prompt assets in `agent/prompts/`. Does NOT own provider HTTP transport (`providers/`), tool implementations (`tools/`), prompt section assembly (lives in `context/` — which re-exports from `agent::prompts` via `context::prompt`), or memory storage (`memory/`).

## Public surface

- `pub struct Agent` / `pub struct AgentBuilder` — `harness/session/types.rs` — top-level conversation runtime; entry point for any chat turn.
- `pub mod harness::session::{builder, runtime, turn}` — `harness/session/mod.rs:23-27` — turn lifecycle, fluent builder, `run_single` / `run_interactive`.
- `pub fn run_subagent` / `pub struct SubagentRunOptions` / `pub enum SubagentRunError` — `harness/subagent_runner/` — execute a hierarchical sub-agent from a parent tool loop.
- `pub struct AgentDefinition` / `pub struct AgentDefinitionRegistry` / `pub enum SandboxMode` / `pub enum ToolScope` — `harness/definition.rs` — sub-agent archetypes loaded from built-ins + workspace TOML.
- `pub mod harness::fork_context` — `harness/fork_context.rs` — task-local parent context for KV-cache reuse.
- `pub trait ToolDispatcher` / `pub struct ParsedToolCall` / `pub struct ToolExecutionResult` — `dispatcher.rs:14-50` — pluggable tool-call format (XML / JSON / P-Format).
- `pub mod triage` (`run_triage`, `apply_decision`, `TriggerEnvelope`, `TriageDecision`, `TriageAction`) — `triage/mod.rs:34-45` — classify external triggers, escalate to sub-agents.
- `pub mod prompts::SystemPromptBuilder` — `prompts/` — system-prompt section composer.
- Built-in archetypes live in `crates/openhuman-core/src/agent/registry/agents/`; this module stays focused on harness/runtime behavior.
- RPC `agent.chat`, `agent.chat_simple`, `agent.server_status`, `agent.list_definitions`, `agent.get_definition`, `agent.reload_definitions`, `agent.triage_evaluate` — `schemas.rs:17-158`.

## Calls into

- `crates/openhuman-core/src/providers/` — `ChatMessage`, `ChatResponse` send/receive against LLMs.
- `crates/openhuman-core/src/tools/` — `Tool` / `ToolSpec` execution surface invoked from the tool loop.
- `crates/openhuman-core/src/memory/` — episodic indexing + memory-loader context injection.
- `crates/openhuman-core/src/agent/context/` — prompt sections, tool-call format selection.
- `crates/openhuman-core/src/inference/local/` — `agent_chat` / `agent_chat_simple` execution backend.
- `crates/openhuman-core/src/config/` — runtime config load via `config::rpc::load_config_with_timeout`.
- `crates/openhuman-core/src/core/event_bus/` — emits `DomainEvent::Agent(*)` and `Trigger*` events; subscribers in `agent/bus.rs`.

## Called by

- `crates/openhuman-core/src/channels/runtime/dispatch.rs` and `web_chat/` — drive chat turns from inbound channel messages.
- `crates/openhuman-core/src/cron/scheduler.rs` — fire scheduled triggers through `triage::run_triage` + `apply_decision`.
- `crates/openhuman-core/src/skills/webhooks/ops.rs` — webhook ingestion routes through triage.
- `crates/openhuman-core/src/integrations/composio/bus.rs` — Composio trigger envelopes go through `agent::triage`.
- `crates/openhuman-core/src/desktop/notifications/rpc.rs` — surfaces agent runs to the UI.
- `crates/openhuman-core/src/agent/learning/{reflection,tool_tracker,user_profile}.rs` — read transcripts + tool outcomes.
- `crates/openhuman-core/src/agent/orchestration/tools/{dispatch,spawn_subagent}.rs` — `spawn_subagent` tool delegates here.
- `crates/openhuman-core/src/core/all.rs` — controller registry wires `all_agent_registered_controllers`.

## Tests

- Unit: `mod.rs` `#[cfg(test)] mod tests;`, `tests.rs`, `multimodal_tests.rs`, `dispatcher_tests.rs`, plus `*_tests.rs` files under `harness/`, `harness/session/`, `triage/`.
- Integration: `tests/agent_builder_public.rs`, `tests/agent_harness_public.rs`, `tests/agent_memory_loader_public.rs`, `tests/agent_multimodal_public.rs`.
- Schema regression: `schemas.rs:393-410` (`controller_schema_inventory_is_stable`).
