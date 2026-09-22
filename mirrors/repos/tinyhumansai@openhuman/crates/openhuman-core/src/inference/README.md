# inference

OpenHuman's inference integration domain. Reusable model, provider transport,
embedding, capability, temperature, and failure behavior belongs to
`tinyinference`; this domain owns product configuration, credentials, access
policy, local process lifecycle (Ollama / LM Studio), RPC/controller
surfaces, OpenAI/Codex subscription OAuth, and the OpenAI-compatible HTTP
endpoint. The RPC surface is `inference.*`; older `local_ai_*` method names are
compatibility aliases in `crates/openhuman-core/src/core/legacy_aliases.rs`.

## Responsibilities

- Resolve workload names (`chat`, `reasoning`, `agentic`, `coding`, `memory`, `embeddings`, `heartbeat`, `learning`, etc.) and provider strings (`openhuman`, `cloud`, `ollama:<model>`, `lmstudio:<model>`, `claude_agent_sdk:<model>`, `claude-code:<model>`, `<slug>:<model>[@<temp>]`) to a concrete `Arc<dyn tinyinference_llm::ChatModel<()>>` + model id.
- Manage the local AI runtime: detect/spawn/adopt `ollama serve`, probe LM Studio over HTTP (never spawned), select OpenHuman-owned artifact paths, invoke TinyInference's Ollama/Piper installers, and enforce a minimum-context-window floor. Local STT (whisper.cpp) was retired; STT is now cloud/engine-configurable via `voice_server.stt_engine` (see `config/migrations/retire_local_whisper_stt.rs`).
- Provide chat, vision (multimodal), summarization, embeddings, sentiment, and "should react" inference operations.
- Preserve product-specific config-rejection, billing, and authentication policy while TinyInference owns provider-failure classification and TinyAgents owns model-call retry execution.
- Resolve abstract tier names (`hint:reasoning`, `hint:agentic`, `hint:coding`, etc.) through the TinyAgents `ModelRouter` in `crates/openhuman-core/src/agent/tinyagents/routes.rs` and the provider factory here.
- Run ChatGPT/Codex OAuth (PKCE) for the `openai` cloud slug and persist tokens in the encrypted auth-profile store.
- Expose an OpenAI-compatible `/v1/*` HTTP endpoint guarded by a stable user-managed external bearer.
- Detect device hardware profile and recommend/apply local model presets/tiers.
- Maintain the built-in BYOK provider preset catalog used by Connections → API keys → LLM.
  The current matrix is `tinymemory_api::host::cloud_providers`, re-exported through
  `config/schema/cloud_providers.rs`; credentials are stored under `provider:<slug>` in the auth-profile store.

## Key files

| File / dir                                                                        | Role                                                                                                                                                                                                                                               |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mod.rs`                                                                          | Domain root; module decls + re-exports; wires `inference.*` controller schemas/controllers.                                                                                                                                                        |
| `ops.rs`                                                                          | Canonical handler file — `inference_*` business logic returning `RpcOutcome<T>`; delegates to `local`, `provider`, `sentiment`, `device`, `presets`, `openai_oauth`. Includes Sentry-noise suppression for expected provider/user-config failures. |
| `schemas.rs` + `schemas/` (`catalog.rs`, `prompt_handlers.rs`, `oauth_handlers.rs`, `claude_code_handlers.rs`, `settings_handlers.rs`) | `inference.*` controller schemas + `handle_*` fns + param DTOs.                                                                                                                                                                                    |
| `tinyinference_llm::{classification,completion,sentiment}` | Reusable language-model parsing and classification called directly by the host. |
| `tinyinference_local::device`; `tinyinference_core::sanitize` | Shared hardware detection and credential-safe diagnostic formatting. |
| `tinyinference_llm::model::model_id_supports_vision`                                  | Upstream capability hint used directly for local model ids when the runtime cannot return an authoritative profile.                                                                                                                               |
| `tinyinference_llm::model::effective_temperature`                                     | Applies unsupported-model glob patterns and overrides before provider serialization.                                                                                                                                                              |
| `types.rs`                                                                        | Serde DTOs: `LocalAiStatus`, `LocalAiAssetsStatus`, `LocalAiDownloadsProgress`, `LocalAiEmbeddingResult`, `LocalAiSpeechResult`, `LocalAiTtsResult`, etc.                                                                                          |
| `model_context.rs`                                                                | Known model context-window sizes (`context_window_for_model`) for pre-dispatch budgeting.                                                                                                                                                          |
| `config/ops/local_ai_presets.rs`                                                  | OpenHuman `LocalAiConfig` mapping for `tinyinference_local::presets`; reusable tiers, recommendations, and preset data live upstream.                                                                                                             |
| `paths.rs`                                                                        | Host-owned on-disk model artifact paths. Completion and sentiment parsing live in `tinyinference`. |
| `local/`                                                                          | Local runtime manager (was `local_ai/`). See `local/README.md`.                                                                                                                                                                                    |
| `local/core.rs`                                                                   | `LocalAiService` singleton (`global`/`try_global`), `model_artifact_path`.                                                                                                                                                                         |
| `local/ops.rs` + `local/ops/` (`runtime_ops.rs`, `chat.rs`, `agent_chat.rs`, `reactions.rs`, `turn_guards.rs`)                                       | Local RPC entrypoints (`local_ai_status/prompt/summarize/vision_prompt/embed/should_react`, `ReactionDecision`); re-exported as `local::rpc`.                                                                                                      |
| `local/schemas.rs`                                                                | Local-runtime `inference.*` controller schemas + handlers.                                                                                                                                                                                         |
| `tinyinference_local`                                                            | Ollama/LM Studio wire types, URL handling, model requirements, runtime profiles, provider selection, process flags, spawn-marker persistence, Ollama installation, and Piper binary/voice installation. |
| `local/service/`                                                                  | `LocalAiService` impl split: `bootstrap`, `assets`, `lm_studio`, `model_rpc`, `public_infer`, `speech`, `transcription`, `vision_embed`, `spawn_marker`, `ollama_admin/`.                                                                          |
| `local/service/ollama_admin/`                                                    | Ollama daemon lifecycle split by concern: `binary`, `diagnostics`, `health`, `model_pull`, `server`, `util` (`test_ollama_connection`).                                                                                                            |
| `provider/`                                                                       | Native TinyAgents model construction plus host provider configuration, auth, error taxonomy, DTOs, and RPC helpers (was `providers/`). See `provider/README.md`.                                                                                  |
| `provider/types.rs`                                                               | Host request/response, streaming delta, tool-call, and usage DTOs retained at product/RPC boundaries.                                                                                                                                              |
| `provider/factory.rs` + `provider/factory/` (`routing.rs`, `tiers.rs`, `turn_model.rs`, `subprocess_providers.rs`, `access_gates.rs`, `chat_model.rs`, `cloud_slug.rs`, `credentials.rs`, `local_runtime.rs`, `managed_backend.rs`, `primary_cloud.rs`) | `create_chat_model*`, `provider_for_role`, provider-string grammar, access gates, and local/cloud/CLI model construction; `BYOK_INCOMPLETE_SENTINEL`.                                                                                              |
| `tinyinference_llm::providers::{openai,anthropic}`                                    | OpenAI-compatible and Anthropic model builders, including Codex metadata and local-runtime construction. |
| `provider/openhuman_backend_model.rs`                                             | Managed OpenHuman backend `ChatModel` with session JWT, billing metadata, and thread context.                                                                                                                                                      |
| `provider/openai_codex.rs`                                                        | `pub(crate)` Codex routing metadata (`OpenAiCodexRouting`, `resolve_openai_codex_routing`): re-targets the `openai` slug at the ChatGPT Codex backend with account/originator headers when Codex OAuth tokens exist. Not a `ChatModel` itself.    |
| `tinyagents_harness::providers::claude_agent_sdk`                                | Claude Agent SDK subprocess provider and prompt-guided tool adapter. |
| `tinyagents_harness::providers::claude_code`                                     | Claude Code CLI provider (`claude-code:<model>`), stream-json parser/driver, auth probes, settings, and subprocess lifecycle. OpenHuman supplies only its MCP endpoint and product routing.                                                        |
| `provider/error_classify.rs`                                                      | OpenHuman policy layered on the reusable classifiers in `tinyinference_llm::classification`. |
| `tinyinference_llm::providers::openai::AuthStyle`                                     | Wire auth style consumed directly by crate-native builders.                                                                                                                                                                                        |
| `provider/ops/`                                                                   | Host HTTP policy, model catalog RPC, and provider configuration; reusable sanitization lives in `tinyinference_core::sanitize`. |
| `provider/schemas.rs`                                                             | Defines a `providers.list_models` controller that is **not** wired into `core/all.rs`; the live method is `inference.list_models` (`openhuman.providers_list_models` survives only as a legacy alias).                                             |
| `voice/`                                                                          | Inference implementations imported by `crate::voice`.                                                                                                                                                                                   |
| `voice/cloud_transcribe.rs`, `voice/local_speech.rs`                              | Hosted STT and local Piper TTS.                                                                                                                                                                                                                 |
| `voice/streaming.rs`, `voice/postprocess.rs`                                     | Streaming transcription and post-processing.                                                                                                                                                                                                       |
| `openai_oauth/`                                                                   | ChatGPT/Codex OAuth: `config.rs` (Codex OAuth config), `flow.rs` (start/complete/status/disconnect), `store.rs` (token persistence).                                                                                                               |
| `http/`                                                                           | OpenAI-compatible endpoint: `server.rs` (`router()`, gated on the `http-server` feature), `types.rs`; `EXTERNAL_OPENAI_COMPAT_PROVIDER` bearer id stays ungated because `core::auth` reads it.                                                     |
| `embeddings/`                                                                     | Embedding provider selection/RPC. See `embeddings/README.md`.                                                                                                                                                                                     |
| `tokenjuice/`                                                                     | Host adapter for the separately released TinyJuice token-compression module. See `tokenjuice/README.md`.                                                                                                                                          |

## Public surface

From `mod.rs` re-exports:

- `model_context::context_window_for_model`
- `types::{LocalAiStatus, LocalAiAssetStatus, LocalAiAssetsStatus, LocalAiDownloadProgressItem, LocalAiDownloadsProgress, LocalAiEmbeddingResult, LocalAiSpeechResult, LocalAiTtsResult}`
- `local::all_local_inference_controller_schemas` / `local::all_local_inference_registered_controllers` (legacy export names; registered schemas are in the `inference` namespace)
- `rpc` (alias for `ops`) and `all_inference_controller_schemas` / `all_inference_registered_controllers`

Provider-layer (via `provider::`): `ChatRequest`, `ChatResponse`, `ProviderDelta`, `ToolCall`, `UsageInfo`, `create_chat_model*`, `provider_for_role`, `BYOK_INCOMPLETE_SENTINEL`, `OpenHumanBackendModel`, plus error classifiers. Local runtime: `local::{global, try_global}` → `Arc<LocalAiService>`.

## RPC / controllers

One namespace is wired into the controller registry (`crates/openhuman-core/src/core/all.rs`).

`inference.*` (`schemas.rs`, `local/schemas.rs`): `resolve_model`, `status`, `get_client_config`, `update_model_settings`, `update_local_settings`, `list_models`, `provider_auth_errors`, `device_profile`, `presets`, `apply_preset`, `diagnostics`, `openai_oauth_start`, `openai_oauth_complete`, `openai_oauth_import_codex_cli`, `openai_oauth_status`, `openai_oauth_disconnect`, `summarize`, `prompt`, `vision_prompt`, `test_provider_model`, `should_react`, `analyze_sentiment`, `claude_code_status`, `claude_code_auth_status`, `claude_code_settings`, `claude_code_set_full_access`, `agent_chat`, `agent_chat_simple`, `transcribe`, `transcribe_bytes`, `tts`, `assets_status`, `downloads_progress`, `download_asset`, `install_piper`, `piper_install_status`, `test_connection`.

Legacy `openhuman.local_ai_*` and `openhuman.update_local_ai_settings` method names are rewritten to canonical `openhuman.inference_*` methods by `crates/openhuman-core/src/core/legacy_aliases.rs` and `app/src/services/rpcMethods.ts`.

Also exposes a non-RPC HTTP router (`http::router()`) nested at `/v1` by `crates/openhuman-core/src/core/jsonrpc.rs` (`/v1/chat/completions`, `/v1/models`), accepting either the core bearer or a stable external API key.

## Events

- Publishes `DomainEvent::SessionExpired` from `provider/ops/http_error/auth_failure.rs` (`publish_backend_session_expired`) and `provider/openhuman_backend_model.rs` when the managed backend rejects a session, so the credentials layer can clear/refresh it.
- Publishes `DomainEvent::ProviderApiKeyRejected` once per provider from `provider/ops/http_error/auth_failure.rs` the first time a BYO key is rejected (401/403), gated by the OpenHuman-owned `auth_error_registry`.
- No `bus.rs` / `EventHandler` subscribers in this domain.

## Persistence

- `openai_oauth/store.rs` persists OAuth tokens via the credentials auth-profile store (`AuthProfilesStore`, `auth-profiles.json`, encrypted at rest) under profile key `provider:openai` / profile `oauth`.
- `LocalAiService` holds in-process runtime state (status, owned `ollama serve` child) via the `local::global` `OnceCell` singleton — process-lifetime, not durably persisted.
- Model artifacts live under `<root>/models/local-ai/` (`local/core.rs::model_artifact_path`); OpenHuman selects the Piper root and passes it to `tinyinference_local::piper::PiperInstall`.
- Routing/provider/local settings persisted through `config` (no dedicated `store.rs`).

## Dependencies

- `crate::config` — `Config`, `config::rpc` (load/save, `ModelSettingsPatch`, `LocalAiSettingsPatch`), cloud-provider schema (`AuthStyle`, slug reservation, id generation), abstract tier model constants. Heaviest dependency.
- `crate::security::credentials` — `AuthService`, `AuthProfilesStore`/`AuthProfile`/`TokenSet`, state dir — for OAuth token storage and provider auth resolution.
- `crate::tools` — tool schemas and product tool metadata projected into TinyAgents requests.
- `crate::agent::tinyagents` — native model, route, message, usage, and thread-context seams used by the agent harness.
- `crate::voice` — voice RPC/audio layer that imports these inference STT/TTS implementations (also a consumer).
- `crate::security::prompt_injection` — prompt-injection handling on the inference path.
- `crate::util` — small shared helpers.
- `crate::core::all` — `ControllerFuture`, `RegisteredController` (controller registry).
- `crate::core::types` — `ControllerSchema`, `FieldSchema`, `TypeSchema`.
- `crate::core::bus` (`BUS.publish`) / `crate::core::events::DomainEvent` — `SessionExpired` / `ProviderApiKeyRejected` publishing on auth failure.
- `crate::security::live_policy` + `crate::security::egress` — Privacy-Mode `LocalOnly` enforcement and egress descriptors at the chat-factory chokepoint (`enforce_local_only_inference`, `emit_inference_egress` in `provider/factory/access_gates.rs`).
- `crate::core::observability` — `expected_error_kind` for Sentry-noise classification.
- `crate::core::jsonrpc` — endpoint mounting reference for `/v1`.
- `crate::core::auth` — bearer auth for the OpenAI-compatible endpoint.
- External: `sysinfo` (device profile), `reqwest`.

## Used by

Widely depended on by the agent layer, voice, memory, channels, web chat,
flows, scheduling, threads, credentials, runtime shutdown, and configuration.
Reusable embedding and local-runtime behavior is consumed directly from the
TinyInference crates; `host_runtime` retains OpenHuman policy and RPC wiring.

## Notes / gotchas

- TinyInference owns effective chat, vision, embedding, STT, TTS, and
  quantization resolution; OpenHuman implements its configuration view and
  calls `tinyinference_local::models` directly.
- Provider strings carry an optional `@<temp>` suffix that pins a per-workload temperature; the suffix is stripped before the model id is sent upstream.
- `update_model_settings` silently drops reserved cloud-provider slugs (`openhuman`/`cloud`/`pid` built-ins the frontend echoes back); `apply_model_settings` re-injects them from stored config so they aren't lost.
- `ops.rs` deliberately demotes known provider/user-config failures (unknown cloud provider, 401/429, model-not-found) to `warn!` to keep them out of Sentry; only unclassified failures escalate to `error!`.
- `apply_preset` is MVP-gated: only the 1B local preset (`ram_2_4gb`) and `disabled` are accepted; `custom` cannot be applied via this path.
- `diagnostics` returns its payload unwrapped (no `{result, logs}` envelope) to match the legacy `local_ai_diagnostics` shape that `json_rpc_e2e` asserts against.
- Adopted (externally started) `ollama serve` daemons are never killed on exit; only the child OpenHuman itself spawned (`owned_ollama`) is.
- `local::global` lazily initialises the `LocalAiService` singleton; use `try_global()` on shutdown paths to avoid creating it just to no-op.
- The `/v1/*` endpoint uses a stable external bearer (`EXTERNAL_OPENAI_COMPAT_PROVIDER`) separate from the core launch bearer, so external OpenAI-compatible harnesses can call it.
- Tests serialize through `inference_test_guard()` (a process-global mutex) since the runtime singleton and config are shared.
