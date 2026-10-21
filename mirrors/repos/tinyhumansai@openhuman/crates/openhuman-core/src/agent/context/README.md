# Agent context defaults

This module exposes the host's default for how many recent tool results the
TinyAgents microcompact middleware keeps. Prompt composition belongs to
[`agent::prompts`](../prompts/README.md), configuration is mapped into turn
middleware in [`agent::tinyagents`](../tinyagents/README.md), and the harness
owns transcript reduction and middleware execution.

## Files

| File | Role |
| --- | --- |
| [`mod.rs`](./mod.rs) | Module documentation and `DEFAULT_KEEP_RECENT_TOOL_RESULTS`. |

There is no per-session `ContextManager` here. The former manager, statistics,
session-memory state, tool-result budget constant, and cleared-placeholder
constant were removed as their responsibilities moved to the config schema,
TinyAgents middleware, and `tinyagents-harness`.

## Consumers

- `pipeline.rs`: removed; live context reduction moved to tinyagents middleware, stats state lives in `stats.rs`.
- `guard.rs`: removed; the live 0.90 compression threshold is `SUMMARIZE_THRESHOLD_FRACTION` in `agent/tinyagents/summarize.rs`.
- `microcompact.rs`: removed; live tool-result body clearing is owned by `tinyagents_harness::middleware::MicrocompactMiddleware`, only the shared constants remain in `mod.rs`.
- `tool_result_budget.rs`: removed; UTF-8-safe per-result truncation moved next to action-workspace artifact preview/fallback handling in `agent/harness/tool_result_artifacts`.
- `summarizer.rs`: removed; live summarization moved to `agent/tinyagents/summarize.rs` (`ModelSummarizer`, which also carries the summarizer system prompt).
- `segment_recap_summarizer.rs`: removed; the recap-backed compaction wrapper is gone.
- `summarizer_tests.rs` / `segment_recap_summarizer_tests.rs`: removed along with the files above.

## Public surface

From `mod.rs` re-exports:

- Manager: `ContextManager`, `ContextStats`.
- Microcompact config: `CLEARED_PLACEHOLDER`, `DEFAULT_KEEP_RECENT_TOOL_RESULTS`.
- Prompt: `SystemPromptBuilder`, `PromptSection`, `PromptContext`, `PromptTool`, `ArchetypePromptSection`, `DateTimeSection`, `IdentitySection`, `LearnedContextData`, `RuntimeSection`, `SafetySection`, `ToolsSection`, and `WorkspaceSection` are imported directly from `agent::prompts`.
- Tool-result budget: `DEFAULT_TOOL_RESULT_BUDGET_BYTES` config default only; live truncation is owned by `ToolOutputMiddleware` / `tool_result_artifacts`.

`ContextStatsState` is `pub(crate)` and not re-exported.

## RPC / controllers

None. No `schemas.rs`, no `all_controller_schemas`, no `handle_*`. The `ContextStats` doc comment mentions an "optional `context.get_stats` RPC", but no such schema or handler exists anywhere in the crate.

## Agent tools

None. No `tools.rs`.

## Events

None. No `bus.rs`; no `DomainEvent`s published or subscribed.

## Persistence

No `store.rs`. State is per-session and in-memory:

- `ContextStatsState` holds last token counts and the context window.

## Dependencies

- `crate::config`: `ContextConfig` ([`config/schema/context.rs`](../../config/schema/context.rs)): `enabled`, `microcompact_enabled` / `microcompact_keep_recent`, `autocompact_enabled`, `compaction_trigger_tokens` (absolute summarization trigger for benchmarks; env `OPENHUMAN_COMPACTION_TRIGGER_TOKENS`), `compaction_strategy` (env `OPENHUMAN_COMPACTION_STRATEGY`), `compaction_enabled`, `tool_result_budget_bytes`, `prefer_markdown_tool_output`, `summarizer_model`, and the embedded `session_memory: SessionMemoryConfig`.
- `crate::inference::provider::UsageInfo`: fed into `record_usage`.
- `crate::agent::prompts`: owns prompt rendering; `channels_prompt.rs` uses `inject_inline_content`.
- `crate::skills::Workflow`: `channels_prompt.rs` renders the available-skills section from a `&[Workflow]`.

## Used by

- `agent::harness`: the primary consumer: `session/builder/builder_build.rs` constructs the `ContextManager`; `session/turn/core/harness_turn.rs` reads the budget/compaction getters into the tinyagents turn config; `session/turn/session_io/{transcript_persist,background_tasks}.rs` read `stats()`; `fork_context.rs` and [`../subagent_host/`](../subagent_host/) consume prompt types.
- `agent::tinyagents`: `turn_middleware.rs` reads `CLEARED_PLACEHOLDER` when configuring `MicrocompactMiddleware`; `payload_summarizer.rs` and `host/context_composer.rs` build `PromptContext`s through `agent::prompts`.
- **`agent_registry::agents/*/prompt.rs`**, `skills/*/agent/*/prompt.rs`: archetype prompt modules pull prompt sections/builder through `agent::prompts`.
- `channels`: [`channels/system_prompt.rs`](../../channels/system_prompt.rs) (`ChannelSystemPrompt`, used by [`channels/runtime/startup/start_channels.rs`](../../channels/runtime/startup/start_channels.rs)) calls `channels_prompt::build_system_prompt_with_identity`; [`channels/mod.rs`](../../channels/mod.rs) re-exports `build_system_prompt`; the `channels/tests/*` prompt/identity tests call it directly.
- `agent::triage`, `agent::debug`, `agent::orchestration::tools` (spawn_subagent and friends), `tools::orchestrator_tools`, `integrations::composio`: consume prompt types (`PromptContext`, `PromptSection`, `ToolCallFormat`, `ConnectedIntegration`, …) via `agent::prompts`.

## Notes / gotchas

- **The context stats state issues no LLM calls and does not mutate history.** Live reduction is owned by the tinyagents middleware stack.
- **Tool-result budgeting is not a context pipeline stage.** The tinyagents path applies per-result budgets in `ToolOutputMiddleware` ([`agent/tinyagents/middleware/tool_output.rs`](../tinyagents/middleware/tool_output.rs)), and artifact-preview fallback truncation lives in `agent/harness/tool_result_artifacts`.
- **`autocompact_enabled()` is `config.enabled && config.autocompact_enabled`**, and `microcompact_keep_recent()` is `0` when `microcompact_enabled` is off: the manager folds the config gates so the turn reads one value per knob.
- Prompt rendering does not belong in this module; add it to `agent::prompts`.
- **`channels_prompt::build_system_prompt` deliberately bypasses `SystemPromptBuilder`** to keep production channel prompt bytes stable for prefix-cache hits; it is a standalone free function despite living under `context/`.

## Further reading

- [Parent module README](../README.md)
- [Agent harness architecture](../../../../../docs/gitbooks/en/developing/architecture/agent-harness.md)
- [Smart token compression](../../../../../docs/gitbooks/en/features/token-compression.md)
The TinyAgents host maps configured context options into harness middleware.
Channel and agent prompts use `agent::prompts`; live transcript compaction and
tool-result clearing run in TinyAgents. This module owns no persistence,
controllers, tools, or event subscribers.
