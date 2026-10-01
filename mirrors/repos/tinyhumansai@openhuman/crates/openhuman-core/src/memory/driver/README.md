# memory/driver

The memory-driver namespace. It exists to hold a place in the module tree, not
to hold code: `mod.rs` is five lines, and none of them define a driver.

## Why it is nearly empty

Memory execution is provided by the compiled TinyMemory TinyBus module, the
same native `cdylib` that backs [`crate::modules::memory`](../../modules/memory/README.md).
There is intentionally no in-process engine driver here. Earlier revisions of
this core linked `tinymemory-core` directly and picked between embedded
engines in process; that class of driver is gone, and this directory is what
is left of the namespace it used to occupy.

The host-side contract and binding live one level up, in
[`memory::api`](../api.rs) (the bus vocabulary, re-exported from
`tinymemory_api`) and [`memory::binding`](../binding.rs) (the
workspace-keyed `for_config` lookup that resolves which driver backs a given
workspace, reached through `CoreContext::memory_binding`). Both are described
in the top-level [`memory/README.md`](../README.md#wiring).

## Pluggable engines

`[subsystems.memory] driver` (or the `OPENHUMAN_MEMORY_DRIVER` env override)
names which driver a workspace binds. The user-facing switch is the
`memory.engines_list` / `engine_get` / `engine_set` / `engine_migrate` /
`engine_migrate_status` RPCs (`memory/ops/engine.rs`,
`memory/ops/engine_migrate.rs`), behind the `memory-remote` Cargo gate.

`binding::admit` accepts:

- the compiled TinyMemory module (`tinymemory`, with `tinycortex` kept as a
  legacy alias) and the `null` provider, as before;
- `tinyhumans`, first-party: no `drivers` entry, implicitly trusted, endpoint
  forced to the backend origin, credential a live bearer read from the host's
  API key or session on every request (`memory/binding_remote.rs`);
- `supermemory`, `mem0`, `cognee`, `cortex`, `agentmemory` configured
  `class = "external"` with `trust_state = "trusted"`, endpoint and deployment
  from the entry and the key from the keychain through
  `credential_ref = "keychain:memory-<id>"`.

Everything else, and every external driver in a build without `memory-remote`,
is refused and falls back to `null` loudly (`MemoryDriverBindFailed`, the
fallback in `provider_status`). `binding::rebind` applies a switch in process
and publishes `MemoryDriverChanged`.

### What degrades on a remote engine

The remote engines advertise the three mandatory families plus what their
dialect adds (CortexDB and TinyHumans: document/conversation/learning/event
ingest and `answer`; Mem0: conversation ingest and graph; Cognee: graph). The
module-only surfaces (`documents`, `tree`, `sources`, `entities`, `people`,
`maintenance`, `goals`, `tool_memory`) are absent from those engines. Their RPCs
are capability-gated out of the registry when a context is ambient, and answer
"memory driver does not support the ... family" otherwise. `provider_status`,
the engine RPCs and the mandatory core/recall RPCs are never gated.

Two host lanes read the mandatory recall on such an engine, and an engine that
ranks without scoring (hosted CortexDB) changes what they can do. Auto-recall's
notes leg keeps the engine's first `AUTO_RECALL_UNSCORED_NOTES` hits instead of
flooring similarities that all read 0.0 (`memory/auto_recall`), and a refused
lookup puts its reason in the block (`auto_recall/refusal.rs`). Situational
preferences and the contradiction check (`memory/preferences`) cannot judge
relevance without a score and answer nothing. A connector sync resolves the
Sources sink before it asks the connector for pages, because the connector
saves its cursor as it pages and records fetched for a driver without the
family would never be fetched again.

## Where next

- [`memory/README.md`](../README.md) for the full split between this host and
  the extracted `tinymemory-core` engine crate.
- [`memory/binding.rs`](../binding.rs) for the workspace-to-driver cache and
  its fail-closed rules (`docs/specs/kernel.md` §3.1, §3.4, §3.7).
- [`modules/memory`](../../modules/memory/README.md) for the module-loading
  side: how the TinyMemory `cdylib` is admitted and reached over the bus.
