# App State

Aggregator that the React shell polls every few seconds to render the OS-level chrome (auth user, autocomplete status, local-AI status, service health, onboarding tasks). Owns the on-disk `app-state.json`, an in-memory current-user cache, and the merge/patch surface for shell-managed local fields. Does NOT own any of the underlying domain state — it only assembles snapshots from peer domains and persists shell-side onboarding metadata.

## Public surface

- `pub struct AppStateSnapshot` — `ops.rs` — composite payload returned to the shell (auth user, runtime status, autocomplete, local AI, onboarding).
- `pub struct RuntimeSnapshot` — `ops.rs` — runtime sub-section of the snapshot.
- `pub struct StoredAppState` — `ops.rs` — disk schema persisted to `<workspace>/app-state.json`.
- `pub struct StoredAppStatePatch` — `ops.rs` — partial-update payload used by `update_local_state`.
- `pub struct StoredOnboardingTasks` — `ops.rs:42-50` — shell-tracked onboarding completion flags (accessibility permission, local model consent, etc.).
- `pub async fn snapshot() -> Result<RpcOutcome<AppStateSnapshot>, String>` — `ops.rs` — collect the full snapshot.
- `pub async fn update_local_state(...)` — `ops.rs` — apply a `StoredAppStatePatch`.
- RPC `app_state.{snapshot, update_local_state}` — `schemas.rs:20-37` (re-exported via `all_app_state_controller_schemas` / `all_app_state_registered_controllers`).

## Calls into

- `crates/openhuman-core/src/config/` — `config_rpc::*` for `Config` reads and the workspace dir resolver.
- `crates/openhuman-core/src/autocomplete/` — `AutocompleteStatus` snapshot.
- `crates/openhuman-core/src/inference/local/` — `LocalAiStatus` snapshot.
- `crates/openhuman-core/src/platform/service/` — `ServiceState` / `ServiceStatus` runtime info.
- `crates/openhuman-core/src/security/credentials/` — `session_support::build_session_state` for the auth slice.
- `crates/openhuman-core/src/api/{config,jwt}` — backend base URL + bearer token used by the cached current-user fetch.

## Called by

- `crates/openhuman-core/src/agent/harness/session/builder.rs` — agent builder reads cached app state when resolving identity.
- `crates/openhuman-core/src/core/all.rs` — registers `all_app_state_*` controllers; the shell hits these via `core_rpc_relay`.
- `app/src/` — Tauri shell consumes the snapshot in its polling loops (out of scope for this README).

## Tests

- Snapshot behavior is covered by `ops_tests.rs` and schema tests in `schemas.rs`; integration coverage runs through the JSON-RPC harness in `tests/json_rpc_e2e.rs`.
