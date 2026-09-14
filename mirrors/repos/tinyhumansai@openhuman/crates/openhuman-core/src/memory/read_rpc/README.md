# read_rpc

Read RPCs that back the Memory tab dashboard: list / inspect / search /
recall / score / delete methods for a human browsing their stored memory,
not for an LLM tool loop. All methods share the existing `memory_tree`
JSON-RPC namespace with the rest of [`memory/tree/`](../tree/), so they get
the same authentication, telemetry, and discovery.

Distinct from [`memory::ops`](../ops/) (re-exported as `memory::rpc`: the
`memory_*` document/KV/graph handlers) and [`memory::tree::retrieval`](../tree/retrieval/)
(LLM-callable retrieval primitives) — see `mod.rs`'s module doc for how the
three surfaces divide the space.

## Files

| File | Exports |
| --- | --- |
| `admin.rs` | `backfill_connector_trees_rpc`, `delete_source_rpc`, `flush_now_rpc`, `flush_source_tree_rpc`, `reset_tree_rpc`, `wipe_all_rpc` |
| `chunks.rs` | `list_chunks_rpc`, `list_sources_rpc`, `recall_rpc`, `search_rpc`, plus the `display_name_for_source` / `read_chunk_row` helpers |
| `entities.rs` | `chunk_score_rpc`, `chunks_for_entity_rpc`, `delete_chunk_rpc`, `entity_index_for_rpc`, `top_entities_rpc` |
| `graph.rs` | `graph_export_rpc` (summary-forest + leaf-chunk graph for the Memory tab, built from `MemoryTree::{summary_forest, recent_leaves}` and `MemoryChunks`/`MemoryEntities` reads — not the contract's key/value `MemoryGraph`) |
| `vault.rs` | `obsidian_vault_status_rpc`, `vault_health_check_rpc` (filesystem probes behind `spawn_blocking`, delegating the registration check to `crate::memory::obsidian_registry`) |
| `types.rs` | Wire DTOs shared across the above (`ChunkRow`, `ChunkFilter`, `EntityRef`, `Source`, the `*Response` types, and size limits like `MAX_LIST_LIMIT`) |

`mod.rs` re-exports everything so callers and the test file can `use
super::*;`.

## Wiring

Handlers are registered in [`memory/schema/handlers.rs`](../schema/handlers.rs),
which calls each `read_rpc::*_rpc` function under the `memory_tree.*`
controller schemas defined in [`memory/schema/`](../schema/) — for example
`read_rpc::list_chunks_rpc`, `read_rpc::graph_export_rpc`,
`read_rpc::wipe_all_rpc`. There is no separate `read_rpc`-only namespace or
registry; it rides the same `memory_tree` controller set as the rest of
`memory/tree/`.

## Tests

Each file has a colocated `*_tests.rs` (`admin_tests.rs`, `chunks_tests.rs`,
`entities_tests.rs`, `graph_tests.rs`, `vault_tests.rs`). `read_rpc_tests.rs`
at the `memory/` root is mounted as this module's `tests` via `#[path]` and
drives cross-file behavior with `use super::*;`; `mod.rs` re-exports `Config`
and `SourceKind` under `#[cfg(test)]` for it.
