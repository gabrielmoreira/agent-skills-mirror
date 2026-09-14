# Config

Authoritative TOML-backed configuration layer. Owns the `Config` schema (every domain section: agent, channels, memory, autonomy, voice, scheduler, observability, etc.), env-variable overrides, the per-user openhuman directory layout, runtime proxy settings, the daemon descriptor, and the settings CLI. ~870 files under `crates/openhuman-core/src/` reference `crate::config` — almost every other domain reads `Config` here.

## Layout

| Path | Purpose |
| --- | --- |
| `schema/` | The `Config` struct, every section type, loading/saving, env overrides, migrations trigger point — see [schema/README.md](schema/README.md) |
| `ops/` | RPC/CLI mutation surface (`config::rpc`) built on the schema — see [ops/README.md](ops/README.md) |
| `schemas/` | Controller schemas + thin RPC handlers for the `config` namespace (`controllers.rs` with submodules `controllers/{agent,inference,integrations,registry,voice,workspace}.rs`, `helpers.rs`, `schema_defs.rs` with submodules `schema_defs/{agent,inference,integrations,voice,workspace}.rs`); the method list is in the `//!` header of `schemas/mod.rs` |
| `migrations/` | Automatic, schema-version-gated startup data migrations — see [migrations/README.md](migrations/README.md) |
| `migration_helpers/` | User-triggered `migrate.{openclaw,hermes}` RPCs importing memory from other assistants — see [migration_helpers/README.md](migration_helpers/README.md) |
| `workspace/` | Workspace bootstrap + editable Persona Pack (`SOUL.md`/`IDENTITY.md`) file RPCs — see [workspace/README.md](workspace/README.md) |
| `daemon.rs` | `DaemonConfig` — Tauri-supervisor bundle of `data_dir`/`workspace_dir` plus `autonomy`/`security`/`reliability`/`secrets`/`audit` sections (`from_app_data_dir`) |
| `settings_cli.rs` | `openhuman settings ...` CLI section-slicing helper |
| `tools.rs` | Read-only LLM-callable wrappers over config (snapshot, autonomy, search, runtime flags, data paths) |
| `workspace_handle.rs` | Opaque, stable digest identity for a workspace directory, used on the wire (Event Log, notification broadcast) so paths never leak |

## Public surface

- `pub struct Config` — `schema/types.rs` (re-exported from `mod.rs`) — top-level user settings.
- Per-domain config structs and enums — re-exported from `mod.rs`; see [schema/README.md](schema/README.md) for the full section → struct table.
- Model constants: `DEFAULT_MODEL`, `MODEL_AGENTIC_V1`, `MODEL_CODING_V1`, `MODEL_REASONING_V1`, and others in `schema/types/model_ids.rs`.
- `pub struct DaemonConfig` — `daemon.rs` — Tauri-supervisor config wrapper (see Layout).
- `pub fn apply_runtime_proxy_to_builder` / `pub fn build_runtime_proxy_client` / `pub fn build_runtime_proxy_client_with_timeouts` / `pub fn runtime_proxy_config` / `pub fn set_runtime_proxy_config` — `schema/proxy.rs`.
- Workspace identity helpers: `pub fn clear_active_user`, `default_root_openhuman_dir`, `pre_login_user_dir`, `read_active_user_id`, `user_openhuman_dir`, `write_active_user_id`, `PRE_LOGIN_USER_ID` — `schema/load/dirs.rs`.
- `pub mod ops` (re-exported as `rpc`) — `ops/` — RPC handlers and settings mutation; see [ops/README.md](ops/README.md).
- `pub mod settings_cli` — `settings_cli.rs` — `openhuman settings ...` CLI surface.
- RPC namespace `config` — 42 methods (`get_config`, `update_model_settings`, `update_autonomy_settings`, `set_privacy_mode`, `reset_local_data`, ...) — `schemas/`; the full list is the `//!` header of `schemas/mod.rs` and `all_controller_schemas()` in `schemas/controllers/registry.rs`.

## Calls into

- Std + serde TOML for serialization.
- `crates/openhuman-core/src/security/keyring/` indirectly when secrets sections need at-rest crypto (`schema/load/secrets.rs`).
- Filesystem under `~/.openhuman/<user-id>/` via `schema/load/dirs.rs`.

## Called by

- ~870 files under `crates/openhuman-core/src/` pull `Config` for their slice.
- Hot consumers: `crates/openhuman-core/src/agent/` (model + autonomy), `crates/openhuman-core/src/channels/` (provider tokens), `crates/openhuman-core/src/memory/` (storage paths), `crates/openhuman-core/src/cron/` (scheduler poll), `crates/openhuman-core/src/inference/local/` (Ollama / device routing), `crates/openhuman-core/src/security/` (sandbox backend, autonomy policy), `crates/openhuman-core/src/voice/`, `crates/openhuman-core/src/desktop/notifications/`, `crates/openhuman-core/src/tools/`.
- `crates/openhuman-core/src/core/all.rs` — registers `all_config_registered_controllers()` under `DomainGroup::Config`.
- `crates/openhuman-core/src/tools/mod.rs` — `pub use crate::config::tools::*` re-exports the read-only config tools.

## Tests

- Unit: `ops_tests.rs` (+ `ops_agent_paths_tests.rs`, `ops_loader_and_search_tests.rs`, `ops_model_and_local_ai_tests.rs`, `ops_voice_and_autonomy_tests.rs`, mounted from `ops/mod.rs`) and `ops/privacy_tests.rs` / `ops/loader_*_tests.rs`; `schemas_tests.rs` (mounted from `schemas/mod.rs`) and `schemas/controllers_tests.rs`; per-section `*_tests.rs` under `schema/` (`channels_tests.rs`, `proxy_tests.rs`, etc.) and `load_tests.rs` (+ `load_active_user_and_dirs_tests.rs`, `load_backup_tests.rs`, `load_corruption_recovery_tests.rs`, `load_env_overlay_tests.rs`, `load_migration_tests.rs`, mounted from `schema/load/mod.rs`); `daemon_tests.rs`, `settings_cli_tests.rs`, `tools_tests.rs`, `workspace_handle_tests.rs`, `mod_tests.rs` beside their sources.
- `TEST_ENV_LOCK` (`mod.rs`) is shared with sibling test modules that mutate `OPENHUMAN_WORKSPACE`.
