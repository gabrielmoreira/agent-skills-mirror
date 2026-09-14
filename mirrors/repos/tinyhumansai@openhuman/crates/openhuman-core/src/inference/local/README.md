# local

Local AI runtime manager: `ollama serve` and Piper sub-process lifecycle,
LM Studio reachability over HTTP (LM Studio is never spawned), plus the RPC
surface used to prompt/summarize/embed against the active local model. Was previously `local_ai/` (pre-consolidation
single-crate layout); see `../README.md` for the wider `inference` domain.

## Key files

| File / dir | Role |
| --- | --- |
| `mod.rs` | Re-exports `super::{device, model_ids, parse, paths, presets, sentiment, types}` under `local::` (compatibility for files migrated from `local_ai/`); `pub use core::*`, `pub use ops as rpc`, `pub use service::LocalAiService`. |
| `core.rs` | `LocalAiService` singleton (`global`/`try_global`), `model_artifact_path`. |
| `ops.rs` + `ops/` (`runtime_ops.rs`, `chat.rs`, `agent_chat.rs`, `reactions.rs`, `turn_guards.rs`) | RPC entry points: `local_ai_status/prompt/summarize/vision_prompt/embed/transcribe[_bytes]/tts/chat`, `agent_chat[_simple]`, `local_ai_should_react` (`ReactionDecision`), assets/downloads status. |
| `schemas.rs` | Local-runtime `inference.*` controller schemas + handlers (see RPC below); exported as `all_local_inference_controller_schemas` / `all_local_inference_registered_controllers`. |
| `ollama.rs` | Ollama HTTP JSON types, `DEFAULT_OLLAMA_BASE_URL`, `ollama_base_url[_from_config]`, `validate_ollama_url`. |
| `lm_studio.rs` | LM Studio OpenAI-compatible wire types, `lm_studio_base_url[_from_local_ai]`, URL normalisation and auth header; the daemon is only probed, never started. |
| `install.rs`, `install_piper.rs`, `voice_install_common.rs` | Ollama/Piper download and install; shared download-progress plumbing. No Whisper install any more — local STT was retired (`config/migrations/retire_local_whisper_stt.rs`). |
| `model_requirements.rs` | `MIN_CONTEXT_TOKENS`, `evaluate_context`, `ContextEligibility` — minimum-context-window floor enforcement. |
| `profile.rs` | `LocalProviderProfile` per-provider-type capability metadata (tool-dispatch strategy, context-window defaults, request-body extras like `options.num_ctx`, `think` suppression) consulted by the factory and agent harness. |
| `process_util.rs` | Shared subprocess helpers (`pub(crate)`, notably the Windows `CREATE_NO_WINDOW` flag) reused by `agent::host_runtime`. |
| `provider.rs` | `pub(crate)` `LocalAiProvider` (Ollama / LM Studio), `normalize_provider`, `provider_from_config`; `omlx` is preserved as a slug for the factory rather than collapsed to Ollama. |
| `service/` | `LocalAiService` impl, split by concern (below). |

## `service/` split

| File | Role |
| --- | --- |
| `mod.rs` | `LocalAiService` struct (`status`, `bootstrap_lock`, `http`, `owned_ollama`), `has_owned_ollama`, `inject_owned_ollama` (test bridge). |
| `bootstrap.rs` | `new`, `bootstrap` (first-use detect/spawn/adopt behind `bootstrap_lock`), and the `LocalAiStatus` state machine (`idle` → `loading` → `ready` / `degraded` / `disabled`; a `degraded` service is not retried automatically). |
| `lm_studio.rs`, `model_rpc.rs` | LM Studio-specific and generic model-RPC plumbing. |
| `public_infer.rs` | Chat/vision/summarize/embed entry points called from `ops.rs`. |
| `speech.rs` | `transcribe`, `transcribe_with_prompt`, `tts` — delegates STT to `crate::voice::create_stt_provider` (cloud/engine-configurable) and TTS to the local Piper install. |
| `transcription.rs` | `TranscriptionResult` — provider-neutral transcription result type. It outlived the bundled whisper.cpp engine that introduced it; the shape is still the contract with `channels::host::adapters`. |
| `vision_embed.rs` | Vision-prompt and embedding entry points. |
| `spawn_marker.rs` | Writes a marker file (PID, binary, owning process) for each `ollama serve` this process spawned so a daemon orphaned by a crash can be reclaimed (`ollama_admin/server.rs::reclaim_orphan_if_ours`) instead of leaked or blanket-killed. |
| `assets.rs` + `assets/` (`status.rs`, `progress.rs`, `download.rs`, `tts_download.rs`) | Asset status and download-progress tracking. |
| `ollama_admin/` | Ollama daemon lifecycle, split by concern: `binary` (`resolve_or_install_ollama_binary`), `diagnostics`, `health` (`ollama_healthy*`, `has_model*`, `kill_ollama_server`, `shutdown_owned_ollama`), `model_pull`, `server` (`ensure_ollama_server[_fresh]`, `reclaim_orphan_if_ours`, `start_and_wait_for_server` — adopt vs own), `util` (`test_ollama_connection`, the only item re-exported from `ollama_admin/mod.rs`). |

## Singleton lifecycle

`local::global(config)` lazily initializes a process-wide `Arc<LocalAiService>`
behind a `once_cell::sync::OnceCell`; `try_global()` returns `None` instead of
creating it, for shutdown paths that should no-op rather than stand up the
service just to tear it down. An **owned** `ollama serve` child (one this
process spawned) is killed on exit; an **adopted** daemon (already running on
`:11434` when OpenHuman started) is left alone — `LocalAiService::owned_ollama`
tracks the distinction, and `has_owned_ollama`/`inject_owned_ollama` exist so
integration tests can inspect or set up that state without a real Ollama
binary.

Model artifacts live under `<root>/models/local-ai/`
(`core.rs::model_artifact_path`).

## RPC / controllers

`inference.*` controllers registered from this module (`schemas.rs`,
`ops.rs`/`ops/`), aggregated into the domain-wide surface by
`crates/openhuman-core/src/inference/mod.rs` and wired into the registry by
`core/all.rs` (`crate::inference::all_local_inference_registered_controllers()`,
alongside `all_inference_registered_controllers()`): `agent_chat`,
`agent_chat_simple`, `transcribe`, `transcribe_bytes`, `tts`, `assets_status`,
`downloads_progress`, `download_asset`, `install_piper`,
`piper_install_status`, `test_connection`. Chat/vision/summarize/embed and
device/preset RPCs live one level up in `inference/schemas.rs` and delegate
into `local::rpc` (`ops.rs`).

## Consumers

`grep -rn 'inference::local::' crates/openhuman-core/src` shows the main
callers outside this module: `agent/schemas.rs` (registers `agent.chat` /
`agent.chat_simple` over `local::rpc::agent_chat*`), `inference/ops.rs` and
`inference/provider/factory/` (`profile::is_local_provider_string`,
base-url resolution when routing into a local runtime), `inference/embeddings/factory.rs`
(Ollama embedding base url), `agent/learning/reflection.rs` and
`security/credentials/ops/login_services.rs` (`local::global`), `core/runtime/builder.rs`
(`local::try_global` on shutdown), `config/ops/model.rs` (`provider::normalize_provider`,
`validate_ollama_url`), `agent/tinyagents/turn_models.rs` and `agent/triage/routing.rs`
(`profile::is_local_provider_string`), `voice/ops.rs` (`model_ids`, `paths`), and
`agent/host_runtime.rs`, `runtime/python/process.rs`, `runtime/python_server/{kompress,spacy}.rs`
(`process_util::apply_no_window`).

## Tests

- Per-file `*_tests.rs` (`core_tests.rs`, `install_tests.rs`,
  `install_piper_tests.rs`, `lm_studio_tests.rs`, `model_requirements_tests.rs`,
  `ollama_tests.rs`, `ops_tests.rs`, `process_util_tests.rs`, `profile_tests.rs`,
  `provider_tests.rs`, `schemas_tests.rs`, `voice_install_common_tests.rs`).
- `service/*_tests.rs` (`bootstrap_tests.rs`, `model_rpc_tests.rs`,
  `public_infer_tests.rs`, `spawn_marker_tests.rs`, `vision_embed_tests.rs`,
  `ollama_admin_tests*.rs`).
- Tests that touch the runtime singleton or shared config serialize through
  `inference_test_guard()` (a process-global mutex defined in `mod.rs`,
  re-exported through `inference::mod.rs`) since `LocalAiService` and `Config`
  are shared process state.
