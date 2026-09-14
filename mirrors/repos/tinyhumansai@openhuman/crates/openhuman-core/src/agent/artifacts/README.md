# artifacts

Metadata store and lifecycle for agent-generated files (presentations,
documents, images) under `<workspace_dir>/artifacts/`. Producer tools
(`tools/impl/presentation`, `tools/impl/document`) call this module to
reserve an artifact directory, write their bytes, and flip the record to
`Ready` or `Failed`; the module publishes the matching bus events, persists
`meta.json` / `args.json`, and exposes `ai.*` RPC controllers plus three
agent tools for listing, fetching, deleting, and regenerating. It never
renders artifact content itself.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | `mod` decls and re-exports: `ArtifactKind` / `ArtifactMeta` / `ArtifactStatus`, the producer API (`create_artifact`, `finalize_artifact`, `fail_artifact`, `read_artifact_bytes`), and `all_artifacts_controller_schemas` / `all_artifacts_registered_controllers`. |
| `types.rs` | `ArtifactKind` (presentation/document/image/other), `ArtifactStatus` (pending/ready/failed), `ArtifactMeta`. Enums serialize lowercase; `parse` is case-insensitive and never errors (unknown kind → `Other`, unknown status → `Pending`). `ArtifactMeta.error` and `.thread_id` are optional, `skip_serializing_if` none. |
| `store.rs` | All filesystem I/O over `tokio::fs`: `artifacts_root`, `create_artifact`, `finalize_artifact`, `fail_artifact`, `read_artifact_bytes` (`pub`); `save_artifact_meta`, `save_artifact_args`, `read_artifact_args`, `list_artifacts`, `get_artifact`, `delete_artifact` (`pub(crate)`); `validate_artifact_id` / `assert_within_root` sandboxing; the `REGENERATE_TARGET_ID` task-local; `sanitize_filename_stem`. |
| `ops.rs` | RPC business logic returning `RpcOutcome<Value>`: `ai_list_artifacts`, `ai_get_artifact`, `ai_delete_artifact`, `ai_regenerate`. `DEFAULT_LIMIT = 50`, `MAX_LIMIT = 200`. The regenerate path that re-runs `PresentationTool` is `#[cfg(feature = "documents")]`; without the feature `ai_regenerate` returns an error. |
| `schemas.rs` | `ControllerSchema`s and `handle_*` fns for the four `ai.*` controllers; param helpers `read_required`, `read_optional_u64`, `read_optional_string` (whitespace-only → absent), `type_name`. |
| `tools.rs` | `ArtifactListTool`, `ArtifactGetTool`, `ArtifactDeleteTool` — shims over `ops` that unwrap the `RpcOutcome` and return `outcome.value` as the `ToolResult` string. |
| `*_tests.rs` | Sibling test files for each of the above (`#[path]`). |

## Public surface

- `ArtifactKind`, `ArtifactMeta`, `ArtifactStatus`.
- Producer API, `pub` and re-exported from `mod.rs`:
  - `create_artifact(workspace_dir, kind, title, extension) -> (ArtifactMeta, PathBuf)` — mints a UUID (or reuses `REGENERATE_TARGET_ID`), creates `<root>/<id>/`, writes a `Pending` `meta.json`, publishes `ArtifactPending`, and returns the absolute path the producer should write to (`<id>/<sanitized-title>.<ext>`).
  - `finalize_artifact(workspace_dir, id, size_bytes)` — `Pending → Ready`, publishes `ArtifactReady`; no-op if already `Ready` with the same size.
  - `fail_artifact(workspace_dir, id, reason)` — `→ Failed`, stores `meta.error`, publishes `ArtifactFailed`. Logs only `reason.len()`, not the reason.
  - `read_artifact_bytes(workspace_dir, id)` — the one sanctioned id → bytes path; refuses non-`Ready` records.
- `store::save_artifact_args` is `pub(crate)` and called directly by the producers right after `create_artifact` (best-effort; failure only forfeits regeneration).
- `all_artifacts_controller_schemas` / `all_artifacts_registered_controllers`.

## RPC / controllers

Namespace `ai`. Registered in `core/all.rs` under `DomainGroup::Agent` via
`all_artifacts_registered_controllers()`; `all_artifacts_controller_schemas()`
is used by `schemas_tests.rs` to check every function has a schema and a
handler. Handlers load config through `config::rpc::load_config_with_timeout()`
and trim string params.

| Method | Inputs | Output |
| --- | --- | --- |
| `ai.list_artifacts` | `offset?: u64` (default 0), `limit?: u64` (default 50, cap 200), `thread_id?: string` | `{ artifacts: ArtifactMeta[], total, offset, limit }` — `total` is the count after the `thread_id` filter |
| `ai.get_artifact` | `artifact_id: string` | flat `ArtifactMeta` fields + `absolute_path` (root joined with `meta.path`) |
| `ai.delete_artifact` | `artifact_id: string` | `{ artifact_id, deleted: true }` |
| `ai.regenerate` | `artifact_id`, `thread_id`, `client_id` (all required) | `{ artifact_id, regenerated: true, is_error }` |

`ai.regenerate` only accepts `kind == presentation`, reloads `args.json`,
and re-runs `PresentationTool` inside `REGENERATE_TARGET_ID.scope(id, ..)`
and `APPROVAL_CHAT_CONTEXT.scope({thread_id, client_id}, ..)` so the same id
is reused and the Pending/Ready/Failed events route back to the originating
chat. The RPC result is an ack; the card state comes from the socket events.
When `thread_id` is given to `list_artifacts`, legacy records with no
`thread_id` are excluded.

## Agent tools

Constructed in `tools/ops.rs` (unconditionally) and re-exported through
`tools/mod.rs` (`pub use crate::agent::artifacts::tools::*`).

| Tool | Permission | Behavior |
| --- | --- | --- |
| `artifact_list` | default | `ops::ai_list_artifacts(.., thread_id = None)` — always the whole workspace; the per-thread filter is RPC-only. `offset` / `limit` args. Concurrency-safe. |
| `artifact_get` | default | `ops::ai_get_artifact`; `artifact_id` required. Concurrency-safe. |
| `artifact_delete` | `Dangerous` | `ops::ai_delete_artifact`. Default-OFF: listed as its own `ToolFamily` (`id: "artifact_delete"`, `default_enabled: false`) in `TOOL_FAMILIES` in `tools/user_filter.rs`; `artifact_list` / `artifact_get` are deliberately not in that map so they cannot be toggled off. |

There is no regenerate tool; regeneration is RPC-only.

## Events

Published by `store.rs` on `crate::core::bus::BUS` (no `bus.rs`; this module
subscribes to nothing):

- `DomainEvent::ArtifactPending` — from `create_artifact`.
- `DomainEvent::ArtifactReady` — from `finalize_artifact` on a real transition.
- `DomainEvent::ArtifactFailed` — from `fail_artifact`.

All three carry `thread_id` / `client_id` read from the
`security::approval::APPROVAL_CHAT_CONTEXT` task-local; outside a chat turn
(CLI, cron, sub-agents) both are `None` and the
`web_chat::artifact_surface` subscriber (`web_chat/event_bus.rs`) drops the
event.

## Persistence

- Root `<workspace_dir>/artifacts/`, created on demand by `artifacts_root`.
- `<root>/<id>/meta.json` — pretty-printed `ArtifactMeta`.
- `<root>/<id>/args.json` — verbatim producer-tool args, written by the
  producer via `save_artifact_args`, read by `ai_regenerate`. Absent for
  artifacts created before it existed, which makes them non-regenerable.
- `<root>/<id>/<stem>.<ext>` — the artifact bytes; `meta.path` is the
  `<id>/<filename>` relative path.
- `list_artifacts` scans root subdirectories, sorts by `created_at`
  descending, applies the `thread_id` filter before pagination, and skips
  entries whose `meta.json` is missing or corrupt (`warn!`, not an error).
- Regeneration reuses the existing directory and preserves the original
  `created_at` so the artifact keeps its position in the sorted list.

## Used by

- `tools/impl/presentation/mod.rs` and `tools/impl/document/mod.rs`
  (`documents` feature; in `scripts/ci/product-features.txt`, not in Cargo
  defaults) — the only producers. Presentation also uses
  `read_artifact_bytes` for its image pipeline.
- `web_chat/event_bus.rs` — bridges the three events to web-channel
  `artifact_*` events.
- `core/all.rs` — controller registry.

## Notes / gotchas

- Path-traversal hardening is layered: `validate_artifact_id` rejects
  empty, `.`, `..`, anything containing `/` or `\`, absolute paths, and
  `X:` drive-letter prefixes; `assert_within_root` re-checks every resolved
  path; `ai_get_artifact` and `read_artifact_bytes` additionally re-check
  that a stored `meta.path` does not escape the root.
- `create_artifact` rejects empty titles/extensions and extensions
  containing `/`, `\`, or `.`. Filename stems are lowercased ASCII
  `[a-z0-9_-]`, capped at 80 chars, fallback `artifact`.
- `store.rs` keeps a dead-code `_assert_status_used` helper so
  `ArtifactStatus` is referenced outside tests.
- Log prefix is `[artifacts]` (`[tool][artifacts]` in `tools.rs`).
