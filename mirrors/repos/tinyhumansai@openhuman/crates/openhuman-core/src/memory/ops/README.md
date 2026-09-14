# ops

RPC handlers for the memory system — each returns `RpcOutcome<T>`
(`crate::rpc::RpcOutcome`, `openhuman_rpc::RpcOutcome` re-exported through
`pub use openhuman_rpc as rpc;` in `crates/openhuman-core/src/lib.rs`).
`memory::ops` is re-exported flat from `crate::memory::mod` (`pub use
ops::*;`), and `memory::rpc` is an alias of this module (`pub use ops as
rpc;`) kept for call sites that predate the tinymemory-core extraction.

## Submodules

| Module | RPC family |
| ------ | ---------- |
| `envelope.rs` | `ApiEnvelope`/`ApiError` wrapping shared by every envelope-style handler (init, list_documents, query_namespace, recall_*, ai_*_memory_file). |
| `helpers.rs` | Formatting, default constants, path validators, and `current_workspace_dir`. It used to own `active_memory_client`, the unguarded engine lookup; that is gone (#5560) and the file carries a note where it stood. |
| `guard.rs` | `active_memory_guard` — how a handler reaches the guarded driver (`CoreContext::memory()` under dispatch, a `binding::for_workspace` fallback for pre-context tests). Handlers that need the binding itself use `memory::binding::for_config`. |
| `documents.rs` | Document/namespace direct API and the envelope-style façade (`memory_init`, `memory_list_documents`, `memory_query_namespace`, `recall_*`). |
| `kv_graph.rs` | Key-value and knowledge-graph handlers. |
| `sync.rs` | `memory_sync_*` and `memory_ingestion_status`. |
| `learn.rs` | `memory_learn_all`. |
| `provider.rs` | `memory_provider_status` / `memory_subsystem_status` — reports what the memory driver slot is bound to; its health probe deliberately uses `unguarded_provider()` (a liveness probe is not product code; allowlisted in `../bypass_allowlist_tests.rs`). |
| `files.rs` | `ai_*_memory_file` handlers (`tokio::fs`). |
| `maintenance.rs` | Scheduler-driven housekeeping against the `Maintenance` capability family. |
| `tool_memory.rs` | Tool-scoped rule read/write handlers. |
| `test_support/` | `shared_memory_test_workspace` — one shared, leaked workspace so concurrent family tests agree on a path instead of racing to bind different ones. |

## The ops ↔ schemas mirror

The seven handler families (`documents`, `kv_graph`, `sync`, `learn`,
`provider`, `files`, `tool_memory`) each have a twin in
[`memory::schemas`](../schemas/); `envelope`, `helpers`, `guard` and
`maintenance` are ops-only. `schemas` defines the wire-facing
`ControllerSchema`s and thin handler glue; `ops` holds the logic each handler
calls into. On the schema side `documents` is partitioned three ways
(`core_recall` / `documents` / `ingest`), which is why nine
`all_<family>_controller_schemas()` / `all_<family>_registered_controllers()`
pairs come out of seven files — so `core::all` can register one capability
family at a time rather than the namespace as a whole.

Do not confuse `memory/schemas/` (this mirror) with `memory/schema/`
(singular) — that is the `memory_tree` namespace's controller schemas
(`definitions.rs` / `handlers.rs` / `registry.rs`: chunk store, entities,
graph and maintenance methods), deliberately kept as one registry and
re-exported through `memory::tree::all_memory_tree_*`, which `core/all.rs`
registers from the tree domain's own push site.

## Wiring

`crates/openhuman-core/src/core/all.rs` (around lines 730–790) registers each
family behind its own alias re-exported from `memory::mod`:
`all_memory_core_recall_registered_controllers`,
`all_memory_documents_registered_controllers`,
`all_memory_ingest_registered_controllers`,
`all_memory_files_registered_controllers`,
`all_memory_kv_graph_registered_controllers`,
`all_memory_sync_registered_controllers`,
`all_memory_learn_registered_controllers`,
`all_memory_provider_registered_controllers`, and
`all_memory_tool_memory_registered_controllers`. Each push is tagged with the
`Capability` the family needs (`Core`, `Documents`, `Ingest`, `Graph`,
`Sources`, `Tree`, `ToolMemory`) so dispatch drops it when the bound driver
does not advertise that capability; `files` (host file I/O) and `provider`
(the RPC that *reports* the capability set) are pushed untagged.

## Tests

Each family has a `*_tests.rs` sibling (`documents_tests.rs`,
`envelope_tests.rs`, `files_tests.rs`, `guard_tests.rs`, `helpers_tests.rs`,
`kv_graph_tests.rs`, `learn_tests.rs`, `maintenance_tests.rs`,
`provider_tests.rs`, `sync_tests.rs`, `tool_memory_tests.rs`), plus the
legacy `../ops_tests.rs` (gated on `feature = "modules"`) that predates the
per-family split and exercises private helpers via `super::*`. Tests that
touch the shared workspace serialize on `GLOBAL_MEMORY_TEST_LOCK` (lock order
is that lock first, then `documents_tests.rs`'s env-var lock).
