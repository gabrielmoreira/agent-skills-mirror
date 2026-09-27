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

## Pluggable engines, and how far that goes today

Memory is one of this project's pluggable-engine subsystems, and the config
shape for it already exists: `[subsystems.memory] driver` (or the
`OPENHUMAN_MEMORY_DRIVER` env override) names which driver a workspace should
bind to. `tinymemory-api` (vendored at `vendor/tinymemory/`) defines a
driver-neutral `MemoryProvider` trait and ships adapter crates for six remote
engines under `vendor/tinymemory/crates/tinymemory-remote/`: Supermemory,
Mem0, Cognee, CortexDB, AgentMemory, and LivingBrain.

What `binding::admit` actually accepts is narrower than that adapter list. It
only binds the compiled TinyMemory module (registry id `tinymemory`, with
`tinycortex` kept as a legacy config alias) or the `null` fallback provider. A
driver id configured under `[subsystems.memory.drivers.<id>]` for one of the
remote engines above is refused with "external driver transport is not
implemented yet." TinyCortex is the memory engine every OpenHuman install
actually runs; the config surface for the rest is in place ahead of the
wiring that will make it switch engines. See
[engines.md](../../../../../gitbooks/developing/engines.md) for how engine
selection works across subsystems.

## Where next

- [`memory/README.md`](../README.md) for the full split between this host and
  the extracted `tinymemory-core` engine crate.
- [`memory/binding.rs`](../binding.rs) for the workspace-to-driver cache and
  its fail-closed rules (`docs/specs/kernel.md` §3.1, §3.4, §3.7).
- [`modules/memory`](../../modules/memory/README.md) for the module-loading
  side: how the TinyMemory `cdylib` is admitted and reached over the bus.
