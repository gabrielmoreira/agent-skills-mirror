# memory

Host layer over the memory stack. The substance of the memory subsystem was
extracted into [`tinymemory-core`](https://github.com/tinyhumansai/tinymemory): the
SQLite/vector store, the markdown summary tree, the provider sync pipelines,
ingestion, recall/query/search, the ingest queue, conversations, people,
goals and the tool-memory rules. That crate names no OpenHuman type — see
[its README](https://github.com/tinyhumansai/tinymemory#readme) for the extracted
side of this split.

Links to the extracted crate point at GitHub rather than into
`vendor/tinymemory/`: CI checks out this repository without submodule
contents, so a relative link into that directory resolves to nothing on the
runner and fails the link check.

What stays here, per that split:

- **RPC surface** — [`schemas/`](schemas/) + [`schema/`](schema/), the
  memory\_\* controller registrations, and [`read_rpc/`](read_rpc/) for reads.
- **Agent tools** — [`tools/`](tools/), [`agent/`](agent/) (the memory agent
  + prompt), and the consolidated `memory_query` agent tool in
  [`query/`](query/) (it came back from the extracted crate because the
  engine crate cannot name the `Tool` trait).
- **Guard** — [`guard/`](guard/), the taint/scope/budget policy gate over
  every provider call.
- **Driver binding** — [`binding.rs`](binding.rs) (`memory::binding::for_config`,
  the workspace-keyed driver binding the Layer rules below reference) and
  [`driver/`](driver/), which provider backs a workspace. The built-in driver
  is the compiled TinyMemory TinyBus module; there is no in-process engine
  driver any more.
- **Ops** — [`ops/`](ops/), RPC handlers that delegate into the core.
- **Contract facade** — [`api.rs`](api.rs) (`memory::api`), the selective
  re-export of `tinymemory-api` that is the bus vocabulary — see its own
  module docs for what it excludes and why.
- **Seam impls** — [`host.rs`](host.rs) — `install_memory_event_sink` and
  `MemoryHostConfig for Config`. Its sibling `host_impls.rs` held the half that
  only an in-process engine could use, and went with the engine when the test
  build stopped linking one (openhuman#6161).
- **Host-owned wire shapes** — [`rpc_models.rs`](rpc_models.rs) /
  [`ingestion_models.rs`](ingestion_models.rs), the RPC request/response
  shapes that used to live in `tinymemory_core::rpc_models`, re-exported flat
  from [`mod.rs`](mod.rs) (`pub use rpc_models::*`).
- **Host-only policy modules**, each with its own reasoning for why it is not
  the engine's:
  - [`auto_recall/`](auto_recall/) — Lane C, the gated, bounded pre-turn
    recall of facts about the user (#6040).
  - [`safety.rs`](safety.rs) — the host-side secret/PII scrubbers applied to
    anything this host persists or hands on.
  - [`source_scope.rs`](source_scope.rs) — the host-side per-turn
    memory-source allowlist.
  - [`obsidian_registry.rs`](obsidian_registry.rs) — is the memory content
    root a vault Obsidian already knows about.
  - [`exit.rs`](exit.rs), [`sync_activity.rs`](sync_activity.rs),
    [`sync_events_bridge.rs`](sync_events_bridge.rs),
    [`preferences/`](preferences/) — smaller host-side seams; see each file's
    own doc comment.

This module used to be mostly a **re-export** of the engine crate — a wall of
`pub use tinymemory_core::{chat, global, ingest_pipeline, ingestion,
preferences, remember, rpc_models, store, sync_events, traits, util, …}` in
[`mod.rs`](mod.rs), so the ~550 `crate::memory::…` paths elsewhere
in this crate kept resolving after the extraction. Those re-exports are gone
with the engine: `tinymemory-core` left the product build in openhuman#5560 and
the test build in openhuman#6161, and it is now in neither this crate's normal
nor its dev dependency graph.

**Prefer `tinymemory_api::…` in new code, never `tinymemory_core::…`.** The
contract crate is what both this host and the loaded TinyMemory module compile
against; the engine crate is what the module carries and this binary does not
link. `memory::api` is the re-export of the contract, and its own module docs
explain which parts of `tinymemory-api` are the *bus* surface and which are the
host's own use of the crate — they are not the same set.

## Wiring

`core/all.rs` registers the nine schema families behind the `all_memory_*_registered_controllers`
aliases re-exported from [`mod.rs`](mod.rs) — `core_recall`, `documents`,
`ingest`, `files`, `kv_graph`, `sync`, `learn`, `provider`, `tool_memory` —
plus [`goals`](goals/)'s, [`people`](people/)'s, and
[`tree`](tree/)'s own `all_memory_tree_*`, `all_retrieval_*`, and
`all_tree_summarizer_*` registered-controller functions,
[`sync/sync_status/`](sync/sync_status/)'s `all_memory_sync_status_registered_controllers`,
[`sources`](sources/)'s `all_memory_sources_registered_controllers`, and the
Slack pair in [`sync/composio/providers/slack/`](sync/composio/providers/slack/)
(`all_slack_memory_registered_controllers`, reached through the
`integrations::composio::providers::slack` re-export).

Agent tools are re-exported into the crate-wide tool surface by
[`tools/mod.rs`](../tools/mod.rs): `pub use crate::memory::tools::*`,
`crate::memory::tools::goals::*`, and `crate::memory::agent::tools::*`.

`memory::rpc` is an alias of [`ops`](ops/) (`pub use ops as rpc;` in
[`mod.rs`](mod.rs)) kept for callers that predate the extraction.

## Domains that kept their RPC surface here

Each (bar `conversations/`, which is a host-owned store) is the RPC surface
for a family the *driver* serves: the handler and schema modules that name
`RpcOutcome` and `ControllerSchema`, resolving through the bound provider
rather than through a linked engine. Before the engine left, each was a thin
wrapper over `pub use tinymemory_core::<domain>::*;` as well.

| Module                          | Role                                                     |
| -------------------------------- | --------------------------------------------------------- |
| [`conversations/`](conversations/) | Workspace-backed thread/message store + `core::bus` subscriber; no RPC surface of its own (see its README). |
| [`goals/`](goals/)               | Goal tracking RPC.                                       |
| [`people/`](people/)             | People/contacts RPC.                                     |
| [`sources/`](sources/)           | Source-registration RPC.                                 |
| [`sync/`](sync/)                 | `composio/` bus subscribers + providers (incl. Slack), and `sync_status/` — per-connection sync status/progress RPC. |
| [`tool_memory/`](tool_memory/)   | Tool-scoped rules + agent read/write tools.               |
| [`tree/`](tree/)                 | Tree walk/retrieval RPC.                                  |

## What lives in the extracted crate (for reference)

See [`vendor/tinymemory/crates/tinymemory-core/src/`](https://github.com/tinyhumansai/tinymemory/tree/1d6b997874a06600ba0c4922708b5613497c9ffe/crates/tinymemory-core/src) for
the storage primitives (`store/`), ingestion queue (`ingestion/`), sync
lifecycle types (`sync_events.rs`), remember classification (`remember.rs`),
ingest orchestration (`ingest_pipeline.rs`), the `Memory`/`MemoryEntry`/etc.
traits (`traits.rs`), preferences (`preferences.rs`), and shared RPC shapes
(`rpc_models.rs`). Source → canonical markdown (chat / email / document)
lives in [`tinycortex::memory::ingest::canonicalize`](https://github.com/tinyhumansai/tinycortex/tree/main/src/memory/ingest/canonicalize),
owned by TinyCortex and used at ingest time.

## Layer rules

- **No storage in this module.** All persistence goes through the bound
  driver — `memory::binding::for_config(..)` and the `MemoryProvider`
  capability families behind it. If you are tempted to open a SQLite
  connection here, it belongs on the other side of that contract, in whatever
  engine the driver fronts. This crate does not link one.
- **RPC + tools + guard live here.** Domain logic belongs behind the contract;
  this module surfaces it over `/rpc` and to agents, and owns the policy that
  is genuinely the host's — the taint/scope/budget guard, the approval gate,
  and the workspace a binding is keyed on.
- **Surface high-level tool calls** that route to the right submodule;
  don't expose internals at the call site.
