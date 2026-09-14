# tools

Agent-facing memory tools: `Tool` implementations the model can call directly
(as opposed to [`memory/ops/`](../ops/), the RPC handlers used by the app and
CLI). The module file for this directory is [`memory/tools.rs`](../tools.rs)
— there is no `tools/mod.rs` — so start there when tracing what is declared
where.

## Layout

`memory/tools.rs` declares five private submodules that live directly in this
directory (`collapsed`, `doctor`, `forget`, `recall`, `store`) plus one
`pub(crate)` module (`flavour`, kept crate-visible because
`crate::flows::tinyflows::memory_adapter` calls `flavour::lookup_flavour`
directly — see that module's doc comment). Four more are `pub mod` and came
back from `tinymemory-core` when the memory subsystem was extracted; their
directory names track their origin in that crate: `raw_store` was
`store/tools/`, `search` was `search/tools/`, `tool_memory` was
`tool_memory/tools/`, and `goals` was that domain's `tools.rs`. Finally,
`memory/tools.rs` re-exports [`memory/query/`](../query/) (`pub use
crate::memory::query::*`), so the consolidated `memory_tree` tool and its
per-mode structs are also reachable through this module.

| File / dir | Tool struct | `name()` |
| --- | --- | --- |
| `collapsed.rs` | `MemoryTool` | `MEMORY_TOOL_NAME` (`"memory"`) |
| `doctor.rs` | `MemoryDoctorTool` | `memory_doctor` |
| `flavour.rs` | `MemoryFlavourTool` | `memory_flavour` |
| `forget.rs` | `MemoryForgetTool` | `memory_forget` |
| `recall.rs` | `MemoryRecallTool` | `memory_recall` |
| `store.rs` | `MemoryStoreTool` | `memory_store` |
| `goals.rs` | `GoalsTool` | `goals` |
| `raw_store/kinds.rs` | `MemoryStoreKindsTool` | `memory_store_kinds` |
| `raw_store/raw_chunks.rs` | `MemoryStoreRawChunksTool` | `memory_store_raw_chunks` |
| `raw_store/raw_search.rs` | `MemoryStoreRawSearchTool` | `memory_store_raw_search` |
| `search/chunk_context.rs` | `MemoryChunkContextTool` | `memory_chunk_context` |
| `search/hybrid_search.rs` | `MemoryHybridSearchTool` | `memory_hybrid_search` |
| `search/vector_search.rs` | `MemoryVectorSearchTool` | `memory_vector_search` |
| `tool_memory/list.rs` | `MemoryToolsListTool` | `memory_tools_list` |
| `tool_memory/put.rs` | `MemoryToolsPutTool` | `memory_tools_put` |

`tool_memory/` here (agent tools for reading/writing tool-scoped rules) is
distinct from [`memory/tool_memory/`](../tool_memory/) (the rule store and
prompt rendering it calls into) — same name, different layer, do not confuse
the two when grepping.

## Wiring

[`tools/mod.rs`](../../tools/mod.rs) re-exports this module twice: `pub use
crate::memory::agent::tools::*;` (the `call_memory_agent` tool, a sibling
domain) and `pub use crate::memory::tools::goals::*; pub use
crate::memory::tools::*;` — the latter glob brings every struct above, plus
the re-exported `query/` tools, into `crate::tools::*`.

Registration happens in `tools/ops.rs`, which constructs the concrete tool
list for a session: `MemoryStoreTool`, `MemoryRecallTool`,
`MemoryForgetTool`, `MemoryDoctorTool`, `MemoryFlavourTool`,
`MemoryVectorSearchTool`, `MemoryChunkContextTool`, `MemoryHybridSearchTool`,
`MemoryStoreRawSearchTool`, `MemoryStoreRawChunksTool`,
`MemoryStoreKindsTool`, and `GoalsTool` are all boxed and pushed there (grep
`ops.rs` for each name to find the call site; the name-to-`Capability` match
further down the same file decides which of them disappear when the bound
driver does not advertise a family). Three exported structs have no
registration call site anywhere in the crate as of this writing:
`MemoryTool` (the collapsed `memory` action-dispatcher over the eleven
`memory_*` tools, which `ops.rs` still registers individually),
`MemoryToolsListTool`, and `MemoryToolsPutTool` — flagged here rather than
assumed wired.

`store.rs`'s `MemoryStoreTool` and `forget.rs`'s `MemoryForgetTool` take an
`Arc<SecurityPolicy>` and call
`enforce_tool_operation(ToolOperation::Act, "<tool name>")` before writing:
that is the autonomy read-only tier check plus the hourly action budget,
nothing content-specific. Neither overrides `permission_level`, so both
still declare the `ReadOnly` default to the approval gate — `collapsed.rs`'s
module doc records that as pre-existing and deliberately left alone. The
read tools in this directory take no policy handle.

## Tests

Every tool file except `search/chunk_context.rs` has a colocated
`*_tests.rs` (`collapsed_tests.rs`, `doctor_tests.rs`, `goals_tests.rs`, …,
and one per file under `raw_store/` and `tool_memory/`);
`raw_store/mod_tests.rs` and `tool_memory/mod_tests.rs` pin each exported
struct's `name()` string.
