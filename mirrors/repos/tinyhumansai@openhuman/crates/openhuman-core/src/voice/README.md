# voice

Speech-to-text (STT) and text-to-speech (TTS) domain. Exposes the `voice_*` RPC
namespace for transcription, synthesis, availability checks, provider
configuration, agent reply-speech (with mascot lip-sync visemes), a realtime
ElevenLabs Agents bootstrap, and a standalone voice **dictation server**
(hotkey → record → transcribe → insert text). Routing between the hosted
backend proxy, local Piper, and third-party providers is decided by a provider
factory driven by config. The low-level inference implementations (cloud STT,
local speech, streaming, postprocess) live under `crate::inference::voice` and
are re-exported through this module's surface for back-compat.

**There is no local STT engine.** The bundled whisper.cpp engine was removed
(`config::migrations::retire_local_whisper_stt`); all STT is either the hosted
backend proxy or a third-party API via the voice provider registry. TTS still
has a local option (Piper) alongside the hosted proxy and third-party APIs.

## Compile-time gate (`voice` feature)

`pub mod voice` is always compiled — it is a facade. The real implementation
(the submodules below and the `inference::voice` re-exports) is gated behind
the default-ON `voice` Cargo feature. When the feature is off, [`stub`] takes
its place and mirrors the subset of the public surface that always-on / other
gated callers depend on (`server`, `dictation_listener`, `streaming`,
`reply_speech`, `cloud_transcribe`, `always_on`, `cli`,
`create_stt_provider`, `effective_stt_provider`,
`publish_ptt_transcript_committed`) with no-op / disabled-error bodies. `compile_status::VOICE_COMPILED_IN` is
deliberately ungated so a consumer that requires voice (the desktop shell) can
assert at compile time that it did not silently get the stub build (#4901).
Keeping the two surfaces in lockstep is enforced by the disabled-build check
(`cargo check --no-default-features --features "<all-but-voice>"`).

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Module docstring, feature gate, and exports; re-exports inference-side voice submodules (`cloud_transcribe`, `local_speech`, `postprocess`, `streaming`); defines `cloud_transcribe_default_model()` (`"whisper-v1"`). |
| `types.rs` | RPC DTOs: `VoiceSpeechResult`, `VoiceTtsResult`, `VoiceStatus` + `From<LocalAi*>` conversions. |
| `ops.rs` | Business logic returning `RpcOutcome<T>`: `voice_status`, `voice_transcribe`, `voice_transcribe_bytes`, `voice_tts`, `normalize_extension`. |
| `factory/` | `SttProvider` / `TtsProvider` traits; cloud/piper/external implementations; `create_stt_provider` / `create_tts_provider`; `effective_*_provider`; slug:model parsing; `DEFAULT_STT_MODEL`, `DEFAULT_PIPER_VOICE`. Split into `entry.rs` (public entry points + constants), `traits.rs`, `stt_providers.rs` (`CloudSttProvider`, `ExternalSttProvider`), `tts_providers.rs` (`CloudTtsProvider`, `PiperTtsProvider`, `ExternalTtsProvider`), `helpers.rs` (`split_slug_model`, `effective_*_provider`, slug-keyed lookup in `config.voice_providers`). |
| `schemas/` | Controller schemas, registry exports, and all `handle_voice_*` / `handle_overlay_stt_notify` RPC handlers. Split into `registry.rs`, `params.rs`, `helpers.rs`, `handlers.rs` (+ `handlers/provider_server.rs`, `handlers/transcribe_tts.rs`). |
| `server.rs` (+ `server/runtime.rs`, `server/pipeline.rs`, `server/hotkey_listener.rs`, `server/singleton.rs`, `server/types.rs`) | The `VoiceServer` dictation runtime: hotkey event loop, recording lifecycle, duration/silence/hallucination gates, background processing, global singleton (`global_server` / `try_global_server` / `start_if_enabled` / `run_standalone`, all in `server/singleton.rs`). |
| `always_on.rs` (+ `always_on/processor.rs`, `always_on/capture.rs`, `always_on/lock_watcher.rs`, `always_on/transcribe.rs`) | Phase 2 always-on listening: keeps the mic open continuously and uses VAD to carve utterances instead of gating on a hotkey. Owns the `cpal` stream and thread discipline; everything else (VAD session, resample, energies, WAV encode, wake-word gate, command/intent routing) runs in the `tinyvoice` module. Opt-in (`config.voice_server.always_on_enabled`); pauses while the screen is locked (macOS only — other platforms have no lock signal yet). |
| `bus.rs` | Publishes `DomainEvent::Voice(VoiceEvent::PttTranscriptCommitted)` via `publish_ptt_transcript_committed`. |
| `compile_status.rs` | `VOICE_COMPILED_IN` — see the gate section above. |
| `hotkey.rs` | rdev-based global hotkey listener; `ActivationMode` (Tap/Push), `HotkeyEvent`, `HotkeyCombination`, `parse_hotkey`, `start_listener`. |
| `audio_capture.rs` | cpal mic capture → 16 kHz mono WAV bytes; `RecordingHandle`, silence-gate ring buffer, peak-RMS reporting. Delegates framing/resample/energy math to `crate::modules::voice` (the `tinyvoice` module). |
| `audio_toolkit/` | Podcast generation + email delivery (`audio_toolkit` RPC namespace), gated by the same `voice` feature. See its own [README](audio_toolkit/README.md). |
| `text_input.rs` | Clipboard-paste text insertion (`insert_text`) — writes clipboard then simulates Cmd/Ctrl+V via enigo, restoring prior clipboard. |
| `dictation_listener.rs` | Core-side dictation broadcast bus: `DictationEvent`, `publish_dictation_event` / `subscribe_dictation_events`, `publish_transcription` / `subscribe_transcription_results`, rdev listener lifecycle (`start_if_enabled` / `stop`), `normalize_hotkey_for_rdev`. |
| `reply_speech.rs` | Agent reply synthesis via backend `/openai/v1/audio/speech`; `ReplySpeechResult`, `VisemeFrame`, `AlignmentFrame`, `ReplySpeechOptions`, `synthesize_reply`, tolerant response normalization. |
| `realtime.rs` | Mints a short-lived signed WebSocket URL from the backend's `/voice-agent/get-signed-url` so the desktop client can open an ElevenLabs Agents session directly (#5399); the provider API key never leaves the server. |
| `realtime_harness.rs` (+ `realtime_harness/turn_handler.rs`, `realtime_harness/chat_delivery.rs`, `realtime_harness/agent.rs`, `realtime_harness/prompt.rs`) | `voice:harness` socket turn handler for realtime sessions: runs the local orchestrator agent (same brain as chat/meet) on each turn the backend relays from the ElevenLabs Custom-LLM proxy, streaming `voice:harness:delta` / `:done` / `:error` back. |
| `stub.rs` | Disabled-voice facade compiled when `voice` is OFF; mirrors the real public surface with no-op / error bodies. |
| `cli.rs` | `openhuman voice` / `openhuman dictate` subcommand adapter — runs a blocking standalone dictation server (domain-owned, since it blocks forever and doesn't fit the controller registry). |
| `*_tests.rs` | Sibling test suites wired via `#[path = ...]` (no inline `#[cfg(test)] mod` blocks — `pnpm rust:layout` rejects them): `always_on_tests.rs`, `audio_capture_tests.rs`, `bus_tests.rs`, `compile_status_tests.rs`, `dictation_listener_tests.rs`, `hotkey_tests.rs`, `ops_tests.rs`, `realtime_harness_tests.rs`, `realtime_tests.rs`, `reply_speech_tests.rs`, `schemas_tests.rs` (wired from `schemas/mod.rs`), `server_tests.rs`, `text_input_tests.rs`, `types_tests.rs`, `factory/factory_tests.rs`, `factory/stt_providers_tests.rs`, `audio_toolkit/ops_tests.rs`. |

## Public surface

- Types: `VoiceSpeechResult`, `VoiceStatus`, `VoiceTtsResult` (from `types`).
- Ops (`pub use ops::*`): `voice_status`, `voice_transcribe`, `voice_transcribe_bytes`, `voice_tts`.
- Factory: `create_stt_provider`, `create_tts_provider`, `default_stt_provider`, `default_tts_provider`, `effective_stt_provider`, `effective_tts_provider`, traits `SttProvider` / `TtsProvider`, `SttResult`, `ExternalSttProvider`, `ExternalTtsProvider`, constants `DEFAULT_PIPER_VOICE`, `DEFAULT_STT_MODEL`.
- Schemas: `all_voice_controller_schemas`, `all_voice_registered_controllers`, `voice_schemas`.
- Events: `publish_ptt_transcript_committed` (from `bus`).
- Compile status: `VOICE_COMPILED_IN` (from `compile_status`, always available regardless of the feature gate).
- Re-exported inference submodules: `cloud_transcribe`, `local_speech`, `postprocess`, and `streaming` (only when `http-server` is also enabled).
- Submodules `server`, `hotkey`, `dictation_listener`, `reply_speech`, `text_input`, `audio_capture`, `factory`, `always_on`, `bus`, `realtime`, `realtime_harness`, `audio_toolkit` are `pub`.

## RPC / controllers

Namespace `voice` (registered in `all_voice_registered_controllers`):

| RPC method | Purpose |
| --- | --- |
| `voice.status` | Availability without executing anything: STT = the effective provider constructs and (for non-hosted slugs) has a credential; TTS = Piper binary + voice model resolve. |
| `voice.agent_signed_url` | Mint a short-lived signed WebSocket URL for a realtime ElevenLabs Agents session. |
| `voice.transcribe` | Transcribe a file path, optional LLM cleanup. |
| `voice.transcribe_bytes` | Transcribe raw audio bytes (writes temp file), with hallucination filter + cleanup. |
| `voice.tts` | Synthesize speech to a file via Piper. |
| `voice.reply_synthesize` | Synthesize an agent reply through the effective TTS provider; returns base64 audio + visemes. |
| `voice.cloud_transcribe` | Transcribe base64 audio via the hosted backend STT proxy (back-compat path). |
| `voice.stt_dispatch` | Factory-dispatched STT (cloud / `<slug>:<model>`); returns `{ text, provider }`. |
| `voice.tts_dispatch` | Factory-dispatched TTS (cloud / piper / `<slug>:<voice>`); returns `ReplySpeechResult`. |
| `voice.set_providers` | Persist STT/TTS provider + model/voice into `config.local_ai.*`. |
| `voice.update_provider_settings` | Persist the voice provider registry + routing strings (mirrors inference model settings). |
| `voice.list_models` | List models/voices for a provider (static presets for built-in slugs). |
| `voice.test_provider` | Test/validate a provider endpoint (silent-WAV STT, "Hello" TTS, or key-only validate). `validate_only` is a dry run for **both** workloads and accepts an `api_key` to check a candidate credential without storing it. |
| `voice.server_start` / `voice.server_stop` / `voice.server_status` | Control the global dictation server. |
| `voice.overlay_stt_notify` | Bridge chat-button STT state transitions into the dictation/transcription buses. |

Provider strings follow the grammar `cloud` / `openhuman` / `backend` (hosted
proxy; `create_tts_provider` matches only `cloud` / `openhuman`), `piper`
(local TTS), `<slug>` or `<slug>:<model|voice>` (registry lookup in
`config.voice_providers`). `"whisper"` and `"local"` used to select
the bundled whisper.cpp engine; that engine is gone, so both strings now fall
through to the slug lookup and error by name — `config::migrations` rewrites
persisted configs so a user never reaches that error.

## Events

`bus.rs` publishes `DomainEvent::Voice(VoiceEvent::PttTranscriptCommitted)`
(thread id, session id, text length, held-ms, watchdog flag — never the raw
transcript, per the PII-safe logging rule) through the process-wide `BUS`.

Separately, `dictation_listener` owns two process-global `tokio::sync::broadcast`
channels that predate the typed event bus:
- `DictationEvent` (`pressed`/`released`) — `publish_dictation_event` / `subscribe_dictation_events`.
- transcription text — `publish_transcription` / `subscribe_transcription_results`.

`crates/openhuman-core/src/core/socketio.rs` subscribes to both broadcast
channels and forwards them to Socket.IO clients (so dictation hotkeys and
results reach the frontend without Tauri-side shortcut registration).

## Contract crates

- `tinyvoice-bus` (`crates/openhuman-core/Cargo.toml`, optional, gated by the
  `voice` feature) — the wire contract for the loaded `tinyvoice` module.
- `crate::modules::voice` — the host-side wrapper over the loaded `tinyvoice`
  native module (the `voice` feature pulls in `modules` for it). `audio_capture.rs`
  and `always_on.rs` call it (imported as `tinyvoice`) for frame preparation,
  resample, per-frame energies, WAV encoding, the VAD session, wake-word
  detection and command/intent routing; `ops.rs` and `server.rs` call
  `is_hallucinated` (`HallucinationMode::{Conversation,Dictation}`). This crate
  owns only the `cpal` stream and policy decisions, not the audio or transcript
  math.

## Persistence

No dedicated `store.rs`. State is persisted into the shared TOML `Config` via
the config domain: `config.local_ai.{stt,tts}_provider`,
`config.local_ai.{stt_model_id,tts_voice_id}`, top-level
`config.{stt,tts}_provider`, `config.voice_server.*` (`stt_engine`,
`always_on_enabled`, `wake_word`, hotkey, gates), and `config.voice_providers`
(the registry). The
dictation `VoiceServer` keeps in-memory runtime state only (state machine,
transcription count, rolling recent-transcript buffer for context) behind a
`OnceCell` singleton.

## Dependencies

- `crate::inference` — local AI runtime (`local::global`, model id/path resolution) and the relocated voice inference impls (`inference::voice::{cloud_transcribe, local_speech, postprocess, streaming}`); also `inference::provider::factory::lookup_key_for_slug` for provider API keys.
- `crate::config` — `Config`, `config::rpc::load_config_with_timeout`, voice-server / dictation config sections, and `config::schema::voice_providers` (`VoiceProviderCreds`, capability/auth/API-style enums).
- `crate::desktop::accessibility` (macOS only) — focused-text inspection (`focused_text_context_verbose`) and the Swift globe-key listener (`globe_listener_start` / `globe_listener_poll`) used in place of rdev for the Fn key.
- `crate::api` — `BackendOAuthClient`, `effective_backend_api_url`, `get_session_token` for backend-proxied reply-speech and the realtime signed-URL bootstrap.
- `crate::modules::voice` (`tinyvoice`) — see Contract crates above.
- `crate::core::all` (`ControllerFuture`, `RegisteredController`), `crate::core::{ControllerSchema, FieldSchema, TypeSchema}`, `crate::core::bus::BUS` + `crate::core::events` (event publishing), `crate::core::logging` (CLI run init), and `crate::rpc::RpcOutcome`.
- External crates: `cpal` (capture), `rdev` (hotkeys), `enigo` + `arboard` (paste insertion), `reqwest` (external provider HTTP + realtime bootstrap), `tokio`/`tokio-util`, `once_cell`.

## Used by

- `crates/openhuman-core/src/core/all.rs` — registers the `voice` and `audio_toolkit` controllers (gated) and the `openhuman voice` CLI adapter (ungated, so the stub answers with a "voice disabled" error).
- `crates/openhuman-core/src/core/socketio.rs` — subscribes to the dictation/transcription broadcast buses and forwards them to Socket.IO clients.
- `crates/openhuman-core/src/core/jsonrpc.rs` — WebSocket upgrade for streaming dictation (`streaming::handle_dictation_ws`).
- `crates/openhuman-core/src/platform/socket/event_handlers.rs` — spawns `realtime_harness::handle_voice_harness_turn` for each `voice:harness` socket event.
- `crates/openhuman-core/src/web_chat/run_task.rs` — synthesizes agent reply speech and publishes PTT transcript-committed events.
- `crates/openhuman-core/src/channels/host/adapters.rs` — channel-side STT provider dispatch and reply synthesis.
- `crates/openhuman-core/src/security/credentials/ops/login_services.rs` — starts/stops the dictation server, dictation listener, and always-on listener when credentials that gate them change.
- `crates/openhuman-core/src/config/schemas/controllers/voice.rs` — re-applies `always_on::start_if_enabled` live after voice-server settings are saved.
- `crates/openhuman-core/src/inference/local/service/speech.rs` — the local-AI service's STT path resolves and constructs the provider through `effective_stt_provider` / `create_stt_provider`.
- `crates/openhuman-core/src/inference/local/install_piper.rs` — references `DEFAULT_PIPER_VOICE`.
- `crates/openhuman-core/src/tools/mod.rs` — re-exports `voice::audio_toolkit::tools::*` into the agent tool catalog.
- `crates/openhuman-app/src/lib.rs` — `const` asserts `VOICE_COMPILED_IN`.

## Notes / gotchas

- **macOS hotkey safety (#2677):** rdev's CGEventTap callback calls `TSMGetInputSourceProperty` off the main thread, which crashes with `EXC_BREAKPOINT` on macOS 26. So on macOS the core-side `dictation_listener::start_if_enabled` is a no-op and the voice server only supports the `fn` (Globe) key via the Swift globe listener; all other keys return an error. Non-macOS uses rdev for all keys.
- **Two server instances:** `global_server` registers the singleton observed by the `voice.server_*` RPCs; `run_standalone` (CLI) deliberately creates an isolated, unregistered `VoiceServer`.
- **Reply-speech and realtime approval-gate classification is "internal"** — if `reply_speech` is ever wrapped in a `Tool`, `external_effect()` MUST stay `false` so the approval gate never prompts on TTS (see file docstring + #1339/#1206). `realtime_harness` turns are classified `ExternalChannel` instead, since they originate as user speech over a channel.
- **Provider precedence:** `effective_tts_provider` prefers the top-level `config.tts_provider`, falls back to `config.local_ai.tts_provider`, then `"cloud"`. `effective_stt_provider` walks `config.stt_provider` → `config.local_ai.stt_provider` but only accepts one that names a *specific* provider; `""`/`cloud`/`openhuman`/`backend` defer to `config.voice_server.stt_engine.provider_string()` so an engine picked in Settings is not shadowed by the legacy `"cloud"` default.
- **Piper-voice guard:** dispatch handlers only default to `DEFAULT_PIPER_VOICE` when the active provider is `piper`; sending a Piper voice id to a cloud/external endpoint would be invalid.
- **Dictation pipeline gates** (in `server/pipeline.rs` and `server/runtime.rs`): minimum duration → peak-RMS silence threshold → hallucination filter (`tinyvoice::is_hallucinated`) / empty-text — each drops the recording before delivery. A `session_generation` counter discards stale state transitions from superseded recordings.
- **Kokoro TTS is intentionally not implemented** in this cut; the doc in `factory/entry.rs` describes how to add it as a new branch + sibling module.
- **No local STT branch:** `"whisper"`/`"local"` provider strings are legacy and error rather than silently falling back — a real misconfiguration should surface, not degrade quietly (see `factory/entry.rs::create_stt_provider`).
