# sources

The registry of connectors a workspace ingests from (Composio, folders,
GitHub repos, RSS, web pages, Twitter queries), the readers that pull items
out of them, per-source sync status, and the `memory_sources_*` JSON-RPC
surface over all three. See `mod.rs` for the #5560 rationale (why this used
to glob `tinymemory_core::sources::*` and what came home versus stayed
upstream) — this file is a map of the directory, not a repeat of that
history.

The vocabulary is the engine-neutral `tinymemory-sources` crate: `pub mod
types { pub use tinymemory_sources::types::{ContentType,
MemorySourceEntry, SourceContent, SourceItem, SourceKind}; }` at the bottom
of `mod.rs`.

## Files

| File | Role |
| ---- | ---- |
| `registry.rs` | Config discovery and write-locking around the source registry's CRUD. Reads/rewrites `[[memory_sources]]` in the host's own config file; the registry type itself is `tinymemory_sources::registry::SourceRegistry`. |
| `rpc.rs` + `rpc/` (`registry_crud.rs`, `source_sync.rs`, `apply_all.rs`, `coding_sessions.rs`, `cost_reporting.rs`, `status_toolkits.rs`) | RPC handler implementations for memory sources. |
| `schemas.rs` + `schemas/` (`registry_schemas.rs`, `sync_schemas.rs`, `apply_all_schemas.rs`, `coding_session_schemas.rs`, `cost_schemas.rs`, `status_schemas.rs`) | Controller-registry schemas for `openhuman.memory_sources_*`. |
| `status.rs` | Per-source sync status: the chunk-key prefix (derived from the registry entry) and freshness label are host-side; in-flight/chunk counts go through `MemoryChunks::source_ingest_status`. |
| `sync.rs` | `derive_scopes` — which tree scope and raw-archive id a configured source maps onto; the only production-reached piece of the old engine sync pipeline. |
| `reconcile.rs` | Startup/list-time reconciliation of active Composio connections into the registry, built on `memory::sync::composio::scan_active_sync_targets`. |
| `readers/mod.rs` | `SourceReader` trait (takes `&Config`, unlike the crate's `&Path` trait) plus one implementation per `SourceKind`: `composio`, `conversation`, `folder`, `github`, `rss`, `twitter`, `web_page`. This module's `reader_for` hands out all seven, network kinds included, because its callers are RPC handlers acting on an explicit user request; the crate's `reader_for` returns `None` for network kinds. Do not call it from a polling loop. |

## RPC surface (`memory_sources.*`)

`list`, `get`, `add`, `update`, `remove`, `list_items`, `read_item`, `sync`,
`reconcile`, `status_list`, `supported_toolkits`, `sync_audit_log`,
`estimate_sync_cost`, `monthly_cost_summary`, `apply_all_in`,
`coding_session_status`, `ingest_coding_sessions`.

## Wiring

`crates/openhuman-core/src/core/all.rs` (around line 844) registers this
family through `crate::memory::sources::all_memory_sources_registered_controllers()`,
re-exported from `schemas::all_registered_controllers`.

## Related modules

- [`../sync/`](../sync/) — the bus-driven side: the Composio trigger and
  config-changed subscribers, `list_sync_targets` (which reads this registry
  first, then falls back to a live scan), the Slack RPC pair, and
  `sync_status/` for per-connection progress. The data movement itself is
  `integrations::composio::ops::providers_ops::run_sync_pass`. `sources/`
  owns *which* connectors are configured and *what* they map onto.
- [`../read_rpc/`](../read_rpc/) — the Memory tab's read RPCs
  (list/inspect/search over the tree, under the `memory_tree` namespace).
  `memory_sources.status_list` is the one status read that lives here
  instead, because it is keyed on the registry.

## Tests

`rpc_tests.rs`, `rpc_budget_tests_tests.rs`, `rpc_filter_tests_tests.rs`,
`rpc_monthly_summary_tests_tests.rs`, `rpc_supported_toolkits_tests_tests.rs`,
`schemas_tests.rs`, `status_tests.rs`, `sync_tests.rs`, `reconcile_tests.rs`,
and per-reader tests under `readers/` (`composio_tests.rs`,
`twitter_tests.rs`).
