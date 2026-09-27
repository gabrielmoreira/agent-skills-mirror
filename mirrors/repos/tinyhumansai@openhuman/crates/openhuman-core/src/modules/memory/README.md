# modules/memory

The host half of `ai.tinyhumans.tinymemory.Memory`: the code that lets the
core's `memory` domain talk to the loaded `tinymemory` native module instead
of an in-process engine. The module root is one level up at
[`modules/memory.rs`](../memory.rs); this folder holds its submodules, split
by responsibility rather than by line count.

## What's in it

| File | Role |
| --- | --- |
| `capabilities.rs` | The pinned artifact's advertised capability set (`ARTIFACT_CAPABILITIES`), checked against `Capability::ALL` at each release bump. |
| `provider.rs` | `ModuleMemoryProvider` construction, bus-proxy resolution, and the error-mapping macro plumbing every `Memory*` trait file below builds on. |
| `documents_tree.rs`, `entities_graph_diff.rs`, `goals_tools_sources.rs`, `sync_sessions_episodic.rs`, `people_chunks_retrieval.rs`, `ingest_answer.rs`, `core_provider.rs` | The `Memory*` trait forwarding, one file per memory subsystem family, each mirroring the module's wire surface method for method. |

## Key types

`ModuleMemoryProvider` (`provider.rs`) is the type that implements the core's
`MemoryProvider` trait by forwarding every call over the bus to the loaded
`tinymemory` module. Because the wire surface mirrors the trait one method for
one method, there is no translation layer, only the bus call itself, error
mapping through `tinymemory_api::wire`, and two decisions worth knowing about:

- Construction is synchronous and does no I/O: `memory::binding::build` calls
  `ModuleMemoryProvider::new` from contexts with no tokio runtime, so the
  module is not loaded and the bus is not dialed until first use.
- `capabilities()` is a synchronous trait method that only the module can
  answer asynchronously, so it returns the pinned `ARTIFACT_CAPABILITIES` set
  instead, and `verify()` cross-checks that against the module's own answer on
  first use, logging loudly on disagreement.

## How it fits

This is the module-loading side of memory's pluggable-engine story: the
domain-facing binding and contract live in
[`memory::driver`](../../memory/driver/README.md) and
[`memory::api`](../../memory/api.rs), and resolve to this provider when a
workspace binds to the `tinymemory` driver. `modules::registry` (below) is
what makes the `tinymemory` artifact itself loadable; this folder is what
happens after it is loaded.

## Where next

- [`modules/registry`](../registry/README.md) for how the `tinymemory`
  artifact is admitted (checksum, ABI, manifest).
- [`memory/driver`](../../memory/driver/README.md) for the host-side contract
  and why there is no in-process engine driver anymore.
- [`modules/README.md`](../README.md) for the loading model this provider sits
  on top of.
