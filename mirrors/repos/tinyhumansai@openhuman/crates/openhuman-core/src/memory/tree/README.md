# tree

Host layer over the memory tree engine, which now lives in the TinyMemory
module (see [`memory/README.md`](../README.md) for the extraction). Every
handler and schema here names OpenHuman's `RpcOutcome` and `ControllerSchema`,
which the engine crate cannot see, so this directory is what stayed behind:
RPC surface, not tree mechanics.

`mod.rs` carries the module's own #5560 accounting for why the old `pub use
tinymemory_core::tree::*` glob was deleted — read it there rather than here
for that history. What resolves under `memory::tree::…` today is the four
submodules below plus the controller-registry re-exports `mod.rs` aggregates
from them (they cannot live in the extracted crate alongside the rest of
`tree`, since aggregation is inherently host-side).

## Submodules

| Module | Role |
| --- | --- |
| [`tree/`](tree/) | Host surface over what used to be `tinymemory_core::tree::tree`: the `memory_tree` write/status handlers in `rpc.rs` (`ingest_rpc`, `list_chunks_rpc`, `get_chunk_rpc`, `backfill_status_rpc`, `pipeline_status_rpc`, `doctor_rpc`, `retry_failed_rpc`, `set_enabled_rpc`), and the canonical chat/email/document ingest payload shapes in `canonicalize_types.rs`. Called from [`memory/schema/handlers.rs`](../schema/handlers.rs). |
| [`tree_runtime/`](tree_runtime/) | The markdown time tree's host surface: JSON-RPC handlers (`ops.rs`, `schemas.rs`), the `tree-summarizer` CLI (`cli.rs`), and an event subscriber (`bus.rs`). Reaches the tree through the contract's six runtime doors (`runtime_buffer_write`, `runtime_read_node`, `runtime_read_children`, `runtime_tree_status`, `runtime_summarize`, `runtime_rebuild`) rather than building an engine config host-side. |
| [`retrieval/`](retrieval/) | Host layer over `tinymemory_core::tree::retrieval`: the retrieval primitives (`query_source`, `cover_window`, `search_entities`, `drill_down`, `fetch_leaves`) as `memory_tree.*` JSON-RPC methods. `rpc.rs` calls the contract's `MemoryRetrieval` family on the **unguarded** `binding.provider()`, so it passes `source_scope::as_bus_scope()` explicitly on every scoped call — read its module doc before touching a scope argument. |
| [`health/`](health/) | The pipeline failure taxonomy (`FailureCode`, `FailureClass`, `PipelineFailure`, `DegradedState`) and the `user_error` wire payload for a web channel, plus the doctor `report` that reads the bound driver's `MemoryMaintenance::{diagnose, degraded_state}`. Not to be confused with `tinymemory_api::health::MemoryHealth` (driver liveness) — see the module doc for the name collision. |

## Registered RPC namespaces

`mod.rs` re-exports three controller registries, wired into `core/all.rs`:

- `all_memory_tree_registered_controllers` (from [`memory/schema/`](../schema/),
  `mod.rs`'s `pub use crate::memory::schema::{...}`) — the core `memory_tree`
  namespace: `ingest`, `list_chunks`, `get_chunk`, `pipeline_status`,
  `set_enabled`, `doctor`, `retry_failed`, `memory_backfill_status`,
  `smart_walk`, plus every [`memory/read_rpc/`](../read_rpc/) method.
- `all_retrieval_registered_controllers` (`retrieval/schemas.rs`) — Phase 4
  retrieval tools, also under the `memory_tree` namespace (kept in the same
  namespace deliberately, "to keep the tool surface tightly grouped with the
  Phase 1-3 ingest controllers"): `query_source`, `cover_window`,
  `search_entities`, `drill_down`, `fetch_leaves`.
- `all_tree_summarizer_registered_controllers` (`tree_runtime/schemas.rs`) —
  the `tree_summarizer` namespace: `ingest`, `run`, `query`, `status`,
  `rebuild`.

All three are registered in `crates/openhuman-core/src/core/all.rs` alongside
the rest of the RPC registry.

## Related surfaces

- [`memory/query/`](../query/) is the agent-facing `memory_tree` tool
  (`MemoryQueryTool`). It reuses `retrieval/rpc.rs`'s request DTOs but does
  not call its handlers: the read modes go through the *guarded* driver
  (`crate::memory::ops::guard::active_memory_guard`) and the `ingest_document`
  mode calls `tree::rpc::ingest_rpc`.
- [`memory/read_rpc/`](../read_rpc/) is the Memory tab dashboard's read
  surface; it shares the `memory_tree` namespace with the controllers
  registered here rather than defining its own.
