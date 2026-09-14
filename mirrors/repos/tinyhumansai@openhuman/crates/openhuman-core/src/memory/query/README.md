# query

The consolidated `memory_tree` agent tool (`MemoryQueryTool`, an alias of
`MemoryTreeTool`) and the eight retrieval/write modes it dispatches to.

This directory lives under `memory/query` rather than in
[`memory/tree/`](../tree/) so that module can stay focused on generic tree
structure, policy, summarisation, and read/write mechanics; `query/` is the
LLM-facing surface on top of it. It exists as OpenHuman code (not in the
extracted `tinymemory-core` engine crate) because, per [`memory/README.md`](../README.md),
the engine crate cannot name the `Tool` trait — a tool that dispatches by
`mode` has to live on the host side of that split.

## The tool

`MemoryTreeTool` (`memory/query/mod.rs`) implements `Tool` with `name()` ==
`"memory_tree"`. Its `mode` argument selects one of eight operations:

| Mode | File | Struct |
| --- | --- | --- |
| `search_entities` | `search_entities.rs` | `MemoryTreeSearchEntitiesTool` |
| `query_source` | `query_source.rs` | `MemoryTreeQuerySourceTool` |
| `drill_down` | `drill_down.rs` | `MemoryTreeDrillDownTool` |
| `cover_window` | `cover_window.rs` | `MemoryTreeCoverWindowTool` |
| `fetch_leaves` | `fetch_leaves.rs` | `MemoryTreeFetchLeavesTool` |
| `ingest_document` | `ingest_document.rs` | `MemoryTreeIngestDocumentTool` |
| `walk` / `smart_walk` | `fast_walk.rs` | `fast_walk::run_fast_walk` (deterministic E2GraphRAG retrieval, no per-mode struct) |

`mod.rs` dispatches on `mode` in `MemoryTreeTool::execute`: every mode except
`walk`/`smart_walk` delegates to the matching struct's own `execute`; `walk`
and `smart_walk` both go to `fast_walk::run_fast_walk`. All six per-mode
structs are re-exported from this module (and re-exported again, flat,
through [`memory/tools.rs`](../tools.rs) via `pub use crate::memory::query::*`)
so callers that want a single mode directly — rather than going through the
`mode`-dispatching wrapper — can still register or call them individually.
Each per-mode struct has its own `name()` (`memory_tree_search_entities`,
`memory_tree_ingest_document`, …), which is why the capability match in
`tools/ops.rs` has a `starts_with("memory_tree_")` fallback arm.

`backend.rs` holds the shared read primitives `query_source`, `drill_down`
and `fetch_leaves` call into (`query_source_scope`, `query_source_kind`,
`drill_down`, `fetch_leaves`). It resolves the bound driver through
`crate::memory::ops::guard::active_memory_guard()` and calls the
`MemoryRetrieval` family on the returned `MemoryGuard`, rather than reaching
into `tinymemory_core::tree::retrieval` directly — see the module doc in
`backend.rs` (the spec it cites is not checked in). Every
`scope` argument passed to the guard is `None`; the guard intersects that with
the ambient per-turn allowlist, so this can only narrow what a turn may see,
never widen it. `search_entities`, `cover_window` and `fast_walk` call
`active_memory_guard()` themselves; `ingest_document` is the one write mode
and goes through `crate::memory::tree::tree::rpc::ingest_rpc` instead. The
request DTOs (`QuerySourceRequest`, `CoverWindowRequest`, …) are borrowed from
[`memory/tree/retrieval/rpc.rs`](../tree/retrieval/rpc.rs); the RPC handlers
there are not called.

## Wiring

- `memory/tools.rs` re-exports this module's contents (`pub use
  crate::memory::query::*`), and [`tools/mod.rs`](../../tools/mod.rs)
  re-exports `crate::memory::tools::*`, so the tool types resolve as
  `crate::tools::MemoryQueryTool` etc. from anywhere in the crate.
- Registration is in `tools/ops.rs`: `Box::new(MemoryQueryTool)` registers the
  single consolidated tool; the per-mode structs are not separately
  registered there today (the capability match in the same file calls
  `MemoryQueryTool` "the one registered tree tool").
- The `memory_tree` name gates on `Capability::Tree` in the same file's
  capability-to-tool-name match, alongside `memory_flavour`.
- The built-in memory agent's `agent.toml` (`memory/agent/agent/agent.toml`)
  allowlists `memory_tree` by that same name.

## Tests

Each mode has a colocated `*_tests.rs` (`cover_window_tests.rs`,
`drill_down_tests.rs`, `fast_walk_tests.rs`, `fetch_leaves_tests.rs`,
`ingest_document_tests.rs`, `query_source_tests.rs`,
`search_entities_tests.rs`); dispatcher-level behavior (mode routing, unknown
mode error) is in `mod_memory_tree_dispatcher_tests_tests.rs`.
`test_workspace.rs` (`cfg(test)` only) provides `WorkspaceEnvGuard`, which
tests must hold before touching `OPENHUMAN_WORKSPACE` so parallel tests in
this tree do not race over the same env var.
