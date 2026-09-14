# OpenHuman TokenJuice Adapter

The reusable compression engine ships as the separately released `tinyjuice`
TinyBus module. It is not linked into OpenHuman's dependency graph. This
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

Do not add the `tinyjuice` crate back to OpenHuman. Runtime services, settings
persistence, JSON-RPC, tools, pricing, and the optional ML callback stay here;
engine behavior stays behind the loadable module boundary.

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
  (`"retrieve_tool_output"`) are recognized aliases only.
- Contract crate: `tinyjuice-bus` (`vendor/tinyjuice/crates/tinyjuice-bus`,
  path dependency in `crates/openhuman-core/Cargo.toml`).
