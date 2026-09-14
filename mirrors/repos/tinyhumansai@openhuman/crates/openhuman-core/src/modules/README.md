# modules

The native loadable-module host. A module is a first-party `cdylib` — `tinydocs`,
`tinywallet`, `tinymemory`, `tinyjuice`, `tinyvoice`, `tinyruntime` (+
`tinyruntime-nodejs` / `tinyruntime-python`), `tinymcp`, `tinyconnectors` — that
speaks the tinybus module ABI. It is downloaded from a pinned GitHub release,
verified against a digest compiled into [`registry.rs`](registry.rs), admitted
through tinybus's ABI/manifest gates, and attached to a private in-process
broker as an ordinary bus peer. The core then calls it like any other service.
See [`mod.rs`](mod.rs)'s own `//!` for the full "what this buys, what it costs"
argument; this file is the navigation layer over it.

Feature-gated as `modules`, and unusually load-bearing for a feature: it is ON
in both the contributor default set and the shipped product set, because the
memory subsystem's module-backed driver is not optional at test time (see the
comment above `default = [...]` in `crates/openhuman-core/Cargo.toml`).
`documents`, `web3`, and `voice` each imply `modules` and each turn a
per-module host half on inside this directory (`documents.rs`, `wallet.rs`,
`voice.rs`) but do not gate the directory itself; `lib.rs` gates the whole
directory on `modules`.

## Layout

| Path | Purpose |
| --- | --- |
| `mod.rs` | Module rustdoc for the whole loading model; re-exports |
| `registry.rs` (+ `registry/records_docs_wallet.rs`, `registry/records_mcp_connectors.rs`, `registry/records_memory_juice.rs`, `registry/records_runtime.rs`, `registry/records_voice.rs`) | The compiled-in table: every `ModuleRecord`, its per-platform digests, and `find`/`ALL` |
| `platform.rs` | Which published artifact (`ubuntu-24.04-x86_64`, `macos-15-arm64`, ...) belongs to this host, newest-compatible first |
| `types.rs` | `LoadPolicy`, `ModuleRecord`, `ModuleSource`, `ModuleState`, `ModuleStatus`, `PlatformAsset` |
| `host.rs` | The module broker: a dedicated process-lifetime tokio runtime, its `ModuleHost`, and the host's own `Connection` for calling into loaded modules |
| `resolution.rs` | One resolution slot per module id, replacing a single global lock so unrelated modules never queue behind each other |
| `ops.rs` | `ensure_loaded` / `ensure_loaded_within` / `state_of` / `LoadError`; the release cache under `install_dir`; failure caching |
| `boot.rs` | What loads at startup: search-path artifacts, then every `LoadPolicy::Eager` record — deliberately not every registry entry |
| `schemas.rs` | The `modules` RPC namespace (`list`, `status`, `load`) |
| `documents.rs` | Host half of `tinydocs` (feature `documents`): the three document operations |
| `wallet.rs` | Host half of `tinywallet` (feature `web3`): confidential and split transaction-signing flows |
| `voice.rs` | Host half of `tinyvoice` (feature `voice`): the voice primitives |
| `memory/` (`provider.rs`, `core_provider.rs`, `capabilities.rs`, `documents_tree.rs`, `entities_graph_diff.rs`, `goals_tools_sources.rs`, `ingest_answer.rs`, `people_chunks_retrieval.rs`, `sync_sessions_episodic.rs`) | `ModuleMemoryProvider`, forwarding `MemoryProvider` calls to the loaded `tinymemory` module via `tinymemory-api` |
| `memory_host.rs` | Host-owned callbacks served *to* the TinyMemory module: `EmbeddingHost`, `ChatHost`, `ComposioHost`, and `RuntimeHost` (event publishing, error reporting, scheduler policy, spaCy); sole survivor of the `host_impls` pair after the in-process engine left (openhuman#6161) |
| `runtime.rs` | Host half of `tinyruntime`: resolving a language runtime (via `tinyruntime-nodejs`/`-python`) and running code on it |
| `connectors.rs` | Reaching `tinyconnectors`; egress policy, route selection, and webhook delivery stay in this crate even though scope enforcement moved into the module |
| `tokenjuice_host.rs` | Host-owned ML callback served to the `tinyjuice` module |
| `*_tests.rs` | Focused tests beside each file above |

## Loading pipeline

1. `registry::find(id)` looks up the compiled-in `ModuleRecord`.
2. `resolution::table().claim(id)` gives the caller `Run`, `Wait`, or `Done` —
   the first caller for a module resolves it as a process-lifetime task;
   everyone else waits on a watch channel (`ops.rs`).
3. Resolution order is cheapest first: already serving on the host's broker,
   a developer's `modules.overrides` (or a `*_TEST_MODULE` env var), the
   module search path (`OPENHUMAN_MODULE_PATH`, then platform data dirs), then
   the release cache.
4. `platform::host_candidates()` picks the ordered list of artifact keys this
   host can run; `ops::load_cached` tries each until one is admitted.
5. The release cache (`tinybus::module::CachedRelease`) downloads if
   `modules.allow_download`, fetches the release's own `checksum.toml`, checks
   it against the digest pinned in `registry.rs`, hashes the archive, extracts,
   and `dlopen`s — on the module runtime's blocking pool so a cold download
   never stalls another task.
6. tinybus's ABI descriptor, manifest, and dependency gates decide whether the
   artifact is *admitted*; a faulted or refused module is recorded as
   `Resolution::Failed` in the resolution table (surfaced as
   `LoadError::Failed`) and never retried in this process — restart is the
   only recovery, because tinybus never unloads a library.

`boot::load_declared_modules` does two things at startup: it loads search-path
artifacts directly through the host, then calls `ensure_loaded` for every
`LoadPolicy::Eager` record (currently only `tinymemory`, and only when
`memory::binding::admit` selects the module-backed driver; its host callbacks
are installed first). It never fails the boot. Everything else is
`LoadPolicy::Lazy` and resolves on first `ensure_loaded` call — deliberately
not eager, so a user who never touches a feature never pays its download.

## Contract crates

Each loadable module has a small `*-bus` contract crate for interface names,
method constants, request/response types, and its contract version:

| Contract | Feature or role |
| --- | --- |
| `tinydocs-bus` | `documents` |
| `tinyvoice-bus` | `voice` |
| `tinyjuice-bus` | inference kernel |
| `tinyruntime-bus` | runtime clients |
| `tinywallet-bus` | `web3` |
| `tinymcp-bus` | `mcp` |
| `tinychannels-bus` | channel vocabulary |
| `tinymemory-api` | memory (selectively re-exported as `crate::memory::api`, not copied or widened) |
| `tinymemory-bus` | memory method names (`names::methods`, used throughout `memory/`, e.g. `memory/provider.rs`) |
| `tinyconnectors-bus` | `tinyconnectors` names and the Composio types `memory_host.rs` forwards |

Rules: never redeclare a contract type in OpenHuman; call members through
contract constants, not string literals; contract crates stay synchronous and
free of I/O and runtime dependencies; shared wire behavior belongs in the
contract, runtime/config/security policy stays in this host.

## Security and operational invariants

A loaded module shares this process's address space, privileges, and crash
domain — it is first-party code that happens to ship separately, not a
sandbox boundary. From `AGENTS.md`, do not weaken these:

- Only the compiled registry (`registry.rs`) may select which artifacts can
  load. There is no RPC method to name an arbitrary path.
- Pin release checksums verbatim from the release's own `checksum.toml`. Never
  compute a replacement digest from a local build — that would make the check
  agree with whatever was served instead of with what the release published.
- Keep the ABI, manifest, dependency, and digest admission checks intact.
- Never unload or repeatedly retry a faulted module in the same process; a
  refused or crashed module is terminal until restart.
- Untrusted code belongs in a separate process, not in a module.
- Never enable the `modules` feature directly on the unconditional `tinybus`
  dependency; forward it from OpenHuman's own `modules` feature
  (`modules = ["tinybus/modules"]`), so a `--no-default-features` build without
  `modules` does not pull in tinybus's loader.
- Initialize recursive submodules before building:
  `git submodule update --init --recursive vendor/`.

## Used by

- `crate::runtime::client` — the ungated facade re-exporting `resolve`,
  `execute`, `pool_stats`, and `RuntimeCallError` from `modules::runtime`, so
  a build without `modules` still compiles.
- `memory::binding` — binds `ModuleMemoryProvider` when the memory driver
  selects the module-backed class.
- `core::all::all_registered_controllers` — wires the `modules` RPC namespace
  (`crate::modules::all_registered_controllers()`).
- `config::schema::modules::ModulesConfig` — `enabled`, `allow_download`,
  `install_dir`, and `overrides` control only whether (and from where) the
  compiled-in modules in this directory load, never what is loadable.
- The per-module host halves are called from their domains:
  `web3/wallet/chains/*` and `web3/x402` (`wallet.rs`),
  `tools/impl/{document,presentation}` (`documents.rs`), `voice/` and
  `inference/voice` (`voice.rs`), `integrations/composio/module_client.rs`
  (`connectors.rs`), and `inference/tokenjuice`, which `ensure_loaded`s
  `tinyjuice` and is called back through `tokenjuice_host.rs`.
