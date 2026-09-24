# OpenHuman TokenJuice Adapter

The reusable compression engine ships as the separately released `tinyjuice`
TinyBus module. Its stateful half — the router, the CCR cache, the rule engine,
ranged retrieval — runs there and is reached only over the bus; its stateless
content transforms are linked directly (see "What is linked" below). This
directory is the host adapter and shared wire-contract layer.

OpenHuman-owned files:

| Path | Role |
| --- | --- |
| `mod.rs` | TinyBus calls (through `tinyjuice_bus::names::methods` constants), config installation, pass-through fallback, and savings wiring. |
| `types.rs` | Re-export of the `tinyjuice-bus` contract (`tinyjuice_bus::types::{AgentTokenjuiceCompression, CompressOptions, CompressedOutput, CompressorKind, ContentHint, ContentKind}` and `tinyjuice_bus::wire::{CacheStats, CompactResponse, InstallRequest, RangeUnit, RetrieveRange}`) under the paths ~40 call sites in this crate already use. |
| `schemas.rs` | JSON-RPC controller schemas and handlers. |
| `config_patch.rs` | Partial update shape for the `[tokenjuice]` config block. |
| `tools.rs` | OpenHuman agent tool implementation for the retrieve tool (`RETRIEVE_TOOL_NAME = "tinyjuice_retrieve"`; `"tokenjuice_retrieve"` is a recognized recovery-tool alias, not the tool's registered name — see `RECOVERY_TOOL_NAMES`). |
| `ml/` | Bridge from TinyJuice's optional ML callback into the shared `runtime::python_server` Kompress backend (ModernBERT token/sentence salience); opt-in via `config.tokenjuice.ml_compression_enabled` (default off), degrades gracefully when the flag is off or the runtime server is unavailable. |
| `savings.rs` | OpenHuman model-pricing attribution and persisted dashboard stats. |

TinyJuice-owned engine pieces:

| TinyJuice repository path | Role |
| --- | --- |
| `src/compress.rs` | Content router entry point. |
| `src/compressors/` | JSON, code, log, search, diff, HTML, ML slot, and generic compressors. |
| `src/cache/` | CCR store, retrieval markers, disk tier, ranged retrieval helpers. |
| `src/rules/` | Rule loader/compiler and embedded rule table. |
| `src/vendor/rules/*.json` | Vendored upstream rule JSON files. |
| `src/detect/`, `text/`, `tokens.rs`, `types.rs` | Detection, text helpers, token estimates, public types. |

## What is linked, and what stays behind the module boundary

The rule is no longer "the crate is never linked" — it is **stateful engine
behavior stays behind the module boundary; stateless content transforms do
not.**

`openhuman-core` depends on `tinyjuice` directly, with
`default-features = false` (dropping `tinyjuice-treesitter` and its three
tree-sitter grammars, which serve the code compressor). The only thing it calls
is the pure half:

| Linked and called directly | Why it may be |
| --- | --- |
| `compressors::html::html_to_markdown` | Pure `&str -> String`. `web_fetch` runs it on every HTML response so the model reads a page's prose, headings and links instead of its minified JS. |

Everything with state stays where it was, reached only through TinyBus:

| Behind the module boundary | Why it stays |
| --- | --- |
| `compress::route` / `compress_content` | Picks a compressor from the rule engine and records savings. |
| `cache/` — the CCR store, retrieval markers, disk tier, ranged retrieval | Owns a disk tier and a marker vocabulary (`⟦tj:<hash>⟧`) the module must resolve. `tinyjuice_retrieve` is the model-facing half and is unchanged. |
| `rules/`, `reduce/`, `ml/` | Rule tables, execution reduction, the ModernBERT callback. |

Why a content transform is not allowed to go through the bus: reaching it there
needs the `modules` feature, a loaded cdylib, and `config.tokenjuice` /
`context.compaction_enabled` — which defaults to `false`. A core tool's default
output would then depend on whether an optional module happened to load, so the
same URL would come back as Markdown on one install and as raw markup on
another. That is not a defensible way to decide what a fetched page looks like.

Why the transform is not reimplemented in OpenHuman instead: TinyJuice owns
content handling, a second copy would drift from the first, and its scanner
already handles CDATA sections, `>` inside quoted attribute values, and
unterminated quotes. A host-side rewrite was prototyped and thrown away in
favour of extending `html_to_markdown` upstream.

Anything beyond a pure transform still belongs behind the boundary: runtime
services, settings persistence, JSON-RPC, tools, pricing, and the optional ML
callback stay here.

## Wiring

- `mod.rs::proxy` (behind the `modules` feature) loads the module via
  `crate::modules::ensure_loaded(config, "tinyjuice")`, looks it up with
  `crate::modules::registry::find("tinyjuice")`, and calls through
  `crate::modules::host::runtime()`; without the feature `proxy` errors and the
  pass-through fallback applies.
- Controllers are registered from `crate::inference::tokenjuice::all_tokenjuice_registered_controllers()`,
  called by `core/all.rs`.
- `tools/ops.rs` registers `crate::inference::tokenjuice::TokenjuiceRetrieveTool::new()`
  in the agent tool catalog (it is not re-exported through `tools/mod.rs`) and
  treats every `RECOVERY_TOOL_NAMES` entry as a recovery tool. The registered
  tool name is `RETRIEVE_TOOL_NAME` (`"tinyjuice_retrieve"`);
  `"tokenjuice_retrieve"` and `LEGACY_RETRIEVE_TOOL_NAME`
  (`"retrieve_tool_output"`) are recognized aliases only. Only
  `RECOVERY_TOOL_VISIBLE` (the live tool) is force-added to a curated
  `ToolScope::Named` belt (`session_host/builder/mod.rs::ensure_recovery_tool_visible`);
  the aliases stay registered for transcript replay but off the wire. It is
  added when compaction is on or the agent's results can be summarized
  (`summarizes_tool_output`), since a summary's footer names it too.
- Contract crate: `tinyjuice-bus` (`vendor/tinyjuice/crates/tinyjuice-bus`,
  path dependency in `crates/openhuman-core/Cargo.toml`).
