# provider

Native TinyAgents `ChatModel` construction plus cloud/local inference policy,
auth, error taxonomy, and RPC helpers for every chat-model transport OpenHuman
supports. Was previously `providers/` (pre-consolidation single-crate
layout); see `../README.md` for how this fits into the wider `inference`
domain.

## Public surface

- **Factory** (`factory.rs` + `factory/` — `routing.rs`, `tiers.rs`, `turn_model.rs`, `subprocess_providers.rs`, `access_gates.rs`, `chat_model.rs`, `cloud_slug.rs`, `credentials.rs`, `local_runtime.rs`, `managed_backend.rs`, `primary_cloud.rs`) — `create_chat_model`,
  `create_chat_model_from_string[_with_model_id]`,
  `create_chat_model_with_model_id`, `provider_for_role`, `role_for_model_tier`,
  `probe_inference_readiness`, `BYOK_INCOMPLETE_SENTINEL`. Parses the
  provider-string grammar (`openhuman`, `cloud`, `ollama:<model>`,
  `lmstudio:<model>`, `mlx:<model>`, `omlx:<model>`, `local-openai:<model>`,
  `claude_agent_sdk[:<model>]`, `claude-code:<model>`, `<slug>:<model>[@<temp>]`)
  and applies the BYOK sentinel, Privacy-Mode `LocalOnly`
  (`enforce_local_only_inference`), and managed-session (`verify_session_active`)
  gates before building a model.
- **Models** — `OpenHumanBackendModel` + `PROVIDER_LABEL`
  (`openhuman_backend_model.rs`), plus the OpenAI-compatible and Anthropic
  crate-native builders (`crate_openai.rs`, `crate_anthropic.rs`).
- **DTOs** (`types.rs`) — `ChatRequest`, `ChatResponse`, `ProviderDelta`,
  `ToolCall`, `UsageInfo`, `AGENT_TURN_MAX_OUTPUT_TOKENS`.
- **Error classifiers** — `billing_error::is_budget_exhausted_message`,
  `chat_template::is_chat_template_rejection_message`,
  `config_rejection::{is_openai_compatible_unknown_model_message,
  is_provider_config_rejection_message}`, `error_code::{BackendErrorCode,
  extract_backend_error_code*, backend_error_code_skips_sentry, ...}`.

## Transports

| Transport | File | Provider-string prefix |
| --- | --- | --- |
| Managed OpenHuman backend | `openhuman_backend_model.rs` | `openhuman` / `cloud` (session JWT + billing metadata) |
| OpenAI-compatible (BYOK cloud slugs, local runtimes) | `crate_openai.rs` | `<slug>:<model>`, `ollama:<model>`, `lmstudio:<model>`, `mlx:<model>`, `omlx:<model>`, `local-openai:<model>` |
| Anthropic Messages API (prompt caching) | `crate_anthropic.rs` | `<slug>:<model>` whose endpoint is the first-party Messages API (`endpoint_is_anthropic_messages`) and native tool calling is on; other Anthropic-keyed endpoints stay on Chat Completions |
| Codex OAuth / Responses API | `openai_codex.rs` (`pub(crate)`, routing metadata only — `OpenAiCodexRouting` applied by the `crate_openai.rs` builder) | the `openai` cloud slug once Codex OAuth tokens exist in the auth-profile store |
| Claude Agent SDK subprocess | `claude_agent_sdk/` (`protocol.rs`, `subprocess.rs`) | `claude_agent_sdk` / `claude_agent_sdk:<model>` |
| Claude Code CLI subprocess | `claude_code/` — see its own [README](claude_code/README.md) | `claude-code:<model>` |

## Calls into

- `tinyinference::model::ChatModel` (`vendor/tinyagents/vendor/tinyinference`)
  — the trait every transport implements.
- `crate::config` — cloud-provider schema (`AuthStyle`, slug reservation),
  `Config::claude_agent_sdk`, abstract tier model constants.
- `crate::security::credentials` — auth-profile store for BYOK keys and OAuth
  tokens.
- `crate::agent::tinyagents::{routes, thread_context}` — workload routing and
  ambient thread-context plumbing consumed while building a model.
- `crate::security::live_policy` + `crate::security::egress` — Privacy-Mode
  `LocalOnly` refusal and `EgressDescriptor` emission at the factory chokepoint
  (`factory/access_gates.rs`).
- `crate::inference::local` — `profile::is_local_provider_string`, Ollama /
  LM Studio base-url resolution for local provider strings.
- `crate::inference::auth_error_registry` — surfaces per-provider auth errors
  back to the UI.
- `crate::core::bus` (`BUS.publish`) / `crate::core::events::DomainEvent` —
  `ops/http_error/auth_failure.rs::publish_backend_session_expired` and
  `openhuman_backend_model.rs` publish `DomainEvent::SessionExpired` when the
  managed backend reports an auth failure, so the credentials layer can
  clear/refresh the session; `ops/http_error/auth_failure.rs` also publishes
  `DomainEvent::ProviderApiKeyRejected` the first time a BYO key is rejected.
- `crate::mcp::server::local` (via `claude_code/driver.rs`) — the Claude Code
  provider points the sandboxed `claude` subprocess at the in-process MCP
  server so it can reach OpenHuman's memory/tools over loopback without the
  MCP server inheriting CC's OS jail.

## Called by

`grep -rn 'inference::provider::' crates/openhuman-core/src` shows the main
consumers: the agent harness (`agent/harness/session/builder/factory.rs`,
`agent/harness/session/runtime*.rs`, `agent/harness/subagent_runner/ops/*`,
`agent/tinyagents/host/model_resolver.rs`), `web_chat/session.rs` and
`web_chat/web_errors/` (`classify.rs`, `budget.rs`, `retry.rs`, `timeout.rs`,
`backend_error_code.rs`, `provider_detail.rs`, `response_predicates.rs`), `voice/factory/{helpers,mod}.rs`,
`inference/ops.rs` / `inference/schemas/` /
`inference/http/server.rs`, `memory/tree/tree_runtime/ops.rs`,
`flows/tinyflows/caps/{llm,prompt,agent}.rs`, `cron/scheduler/failure_classification.rs`
(`is_budget_exhausted_message`), and `threads/ops/usage.rs` (`UsageInfo`).

## Sub-modules

- `ops/` — `sanitize` (secret scrubbing), `http_error` (HTTP error
  classification, Sentry routing, `api_error`), `models`
  (`list_configured_models`), `provider_factory` (`ProviderRuntimeOptions`,
  `list_providers`, `is_qwen_alias`-style China-provider alias helpers).
  Preserves the original `pub use ops::*` contract split out of a single `ops.rs`.
- [`claude_code/`](claude_code/README.md) — Claude Code CLI provider.
- `claude_agent_sdk/` — `ClaudeAgentSdkProvider` (`subprocess.rs`, configured
  from `Config::claude_agent_sdk`; `protocol.rs` wire types).
- `schemas.rs` — a `providers.list_models` controller that is **not**
  registered in `core/all.rs`; the live method is `inference.list_models`
  (`openhuman.providers_list_models` survives only as a legacy alias in
  `core/legacy_aliases.rs`).

## Tests

- `factory_tests.rs`, `factory_crate_native_tests.rs`,
  `factory_egress_fallback_tests.rs`, `factory_route_resolution_tests.rs`,
  `factory_test_provider_override_tests.rs` — provider-string parsing, access
  gates, and model construction.
- `ops_tests.rs`, `ops_tests_error_suppression_tests.rs`,
  `ops_tests_models_parsing_tests.rs`, `ops/http_error_tests.rs`, `ops/models_tests.rs` — error
  classification and model listing.
- `error_classify_tests.rs`, `error_code_tests.rs`, `config_rejection_tests.rs`,
  `billing_error_tests.rs`, `fallback_diagnostics_tests.rs` — per-classifier
  behavior.
- `claude_code/*_tests.rs` — per-file coverage of the CC provider (auth,
  auth status, driver, event mapper, input builder, stream parser, session
  store, settings, version check) plus `mod_tests.rs`.
- `crate_openai_tests.rs`, `crate_anthropic_tests.rs`,
  `openhuman_backend_model_tests.rs`, `openai_codex_tests.rs` — per-transport
  model builders.
