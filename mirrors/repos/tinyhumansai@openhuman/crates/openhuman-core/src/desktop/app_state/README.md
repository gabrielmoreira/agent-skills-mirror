# App State

Aggregator that the React shell polls every few seconds (`openhuman.app_state_snapshot`) to render the OS-level chrome: auth user, local-AI status, service health, onboarding tasks, keyring status, config-recovery notice. Owns the on-disk `app-state.json`, the in-memory current-user cache (positive result, negative backoff record, last-success timestamp), and the merge/patch surface for shell-managed local fields. Does NOT own any of the underlying domain state — it assembles snapshots from peer domains and persists shell-side onboarding metadata.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | `pub use ops::*`, `recovery_signal::{config_recovered_this_session, latch_from_config}`, and the `all_app_state_*` / `app_state_schemas` controller aggregators. |
| `ops.rs` | Aggregator only: declares the submodules below and attaches the sibling test files. |
| `ops/types.rs` | Serde types (`StoredOnboardingTasks`, `StoredAppState`, `AppStateSnapshot`, `RuntimeSnapshot`, `StoredAppStatePatch`). |
| `ops/state_file.rs` | `app-state.json` load/save with corruption quarantine (`load_stored_app_state`, `save_app_state`). |
| `ops/current_user_fetch.rs` | The current-user HTTP fetch (`fetch_current_user`). |
| `ops/current_user.rs` | `fetch_current_user_cached` (5s TTL + failure backoff capped at 60s) and `peek_cached_current_user_identity`. |
| `ops/snapshot.rs` | `snapshot()` and `update_local_state()`. |
| `ops/auth_timeout.rs` | `OPENHUMAN_AUTH_FETCH_TIMEOUT_SECS` parsing, clamped to 2–12s (default 5s). |
| `ops/staleness.rs` | `LAST_CURRENT_USER_SUCCESS`, feeding `current_user_stale` / `current_user_stale_seconds` (#5930). |
| `ops/current_user_generation.rs` | `CURRENT_USER_GENERATION` counter, `CURRENT_USER_SESSION_MUTATION_LOCK`, `forget_current_user_caches` (sign-out invalidation). |
| `recovery_signal.rs` | Process-lifetime latch for "config.toml was recovered from corruption this session" (#5167). |
| `schemas.rs` | `app_state` controller schemas and thin handlers. |
| `*_tests.rs` | Sibling test files attached with `#[cfg(test)] #[path = ...] mod`. |

## Public surface

- `AppStateSnapshot` — composite payload: `auth`, `session_token`, `current_user`, `onboarding_completed`, `chat_onboarding_completed`, `analytics_enabled`, `local_state`, `keyring_status`, `runtime` (`RuntimeSnapshot { local_ai: LocalAiStatus, service: ServiceStatus }`), `health`, `config_recovered`, `current_user_stale`, `current_user_stale_seconds`.
- `StoredAppState` — disk schema persisted to `<workspace_dir>/state/app-state.json` (`encryption_key`, `onboarding_tasks`, `keyring_consent`). `StoredOnboardingTasks` holds the shell-tracked onboarding flags plus `enabled_tools` and `connected_sources`.
- `StoredAppStatePatch` — partial update (`Option<Option<_>>` per field) applied by `update_local_state`.
- `pub async fn snapshot() -> Result<RpcOutcome<AppStateSnapshot>, String>` — full snapshot; runtime sub-snapshot is cached for 10s and single-flighted (#4249).
- `pub async fn update_local_state(StoredAppStatePatch) -> Result<RpcOutcome<StoredAppState>, String>` — merge under `APP_STATE_FILE_LOCK` and save atomically.
- `pub(crate) fn load_stored_app_state(&Config)` / `pub fn save_app_state(&Config, &StoredAppState)` — direct disk access; a corrupt file is renamed to `app-state.json.corrupted.<ts>` and replaced with defaults.
- `pub fn peek_cached_current_user_identity() -> Option<UserIdentity>` — id/name/email from the cache, ignoring the TTL; never returns tokens.
- `pub fn forget_current_user_caches()` and `pub static CURRENT_USER_SESSION_MUTATION_LOCK` — sign-out hooks used by the credentials domain.
- `latch_from_config(&Config)` / `config_recovered_this_session()` — recovery latch.
- Auth-fetch timeout constants and `parse_auth_fetch_timeout_secs`.
- RPC `app_state.{snapshot, update_local_state}` via `all_app_state_controller_schemas` / `all_app_state_registered_controllers`.

## Calls into

- `crate::config` — `config::rpc::load_config_with_timeout`, `read_active_user_id` / `write_active_user_id`, `default_root_openhuman_dir`.
- `crate::security::credentials` — `session_support::{load_app_session_profile, session_state_from_profile, session_token_from_profile, is_local_session_token}`, `AuthService`, `start_login_gated_services` / `stop_login_gated_services`, `sentry_scope`; `crate::security::keyring_consent` for `KeyringStatus` / `ConsentPreference`.
- `crate::api::{config, jwt, rest, product}` — backend base URL, bearer header, profile-payload user id, and the `x-sdk-name` product identity headers for the `GET /auth/me` fetch (built on `crate::util::tls::tls_client_builder`).
- `crate::inference` — `LocalAiStatus` via `inference::rpc::inference_status`.
- `crate::platform::service` — `ServiceState` / `ServiceStatus`; `crate::platform::health::snapshot`.
- `crate::cron::scheduler_gate::set_signed_out`, `crate::cron::seed::prune_retired_jobs`, `crate::memory::conversations::{purge_threads, register_conversation_persistence_subscriber}`, and `CoreContext::rebind_default_workspace` when a pending session is validated or a deferred rejection is cleaned up.

## Called by

- `crates/openhuman-core/src/core/all.rs` — registers `all_app_state_registered_controllers()`; the shell reaches them through `coreRpcClient` → `relay_http_rpc`.
- `crates/openhuman-core/src/core/jsonrpc.rs` — `latch_from_config` at runtime bootstrap.
- `crates/openhuman-core/src/agent/harness/session/builder/factory.rs` — `load_stored_app_state` to read `onboarding_tasks.enabled_tools` for tool filtering.
- `peek_cached_current_user_identity` — `agent/harness/session/turn/context.rs`, `agent/tinyagents/host/context_composer.rs`, `agent/tinyagents/payload_summarizer.rs`, `web_chat/progress_bridge.rs`, and the Sentry `before_send` filters in `main.rs` and `crates/openhuman-app/src/lib.rs`.
- `crates/openhuman-core/src/security/credentials/ops/session_query.rs` — takes `CURRENT_USER_SESSION_MUTATION_LOCK` and calls `forget_current_user_caches` on sign-out.
- `crates/openhuman-core/src/security/keyring_consent/ops.rs` — persists the consent choice through `update_local_state`.

## Tests

- `ops_tests.rs`, `ops_current_user_backoff_tests.rs`, `ops_snapshot_latency_tests.rs`, `ops_signout_cache_tests.rs`, `recovery_signal_tests.rs`, `schemas_tests.rs`.
- JSON-RPC shape: `tests/json_rpc_e2e.rs` (`json_rpc_app_state_snapshot_returns_runtime_shape`) and `tests/config_auth_app_state_connectivity_e2e.rs`.
