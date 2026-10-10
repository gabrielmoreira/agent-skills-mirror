# runtime/client

The single import point the `runtime/` clients use to reach the `tinyruntime`
module (`modules::runtime`).

## Why this exists

`crate::modules` sits behind the `modules` Cargo feature, but `runtime/` does
not: `ShellTool` holds an `Option<Arc<NodeBootstrap>>` as a plain field and is
kernel code, so the toolchain clients (`runtime::node`, `runtime::python`) have
to compile whether or not `modules` is on. If those clients imported
`modules::runtime` directly, turning the feature off would break the build
instead of just disabling the managed runtimes.

So `node` and `python` import `execute`, `pool_stats`, `resolve`, and
`RuntimeCallError` from here instead of from `modules::runtime` directly. With
`modules` on, this re-exports the real client. With it off, it re-exports
`disabled`, a stand-in that answers every call with
`RuntimeCallError::Unavailable`. Callers cannot tell the two apart, which is
the point: a build without the module bus should look like a runtime that
simply is not there, not like a missing symbol.

## Key files

| File | Role |
| --- | --- |
| [`mod.rs`](./mod.rs) | The feature-gated re-export: `modules::runtime`'s `execute`, `pool_stats`, `resolve`, `RuntimeCallError` when `modules` is on, `disabled`'s copies when it is off. |
| [`disabled.rs`](./disabled.rs) | The `modules`-off stand-in. Same three-variant `RuntimeCallError` as the real client, so callers match identically in both builds; every function returns `Unavailable` with a message naming the missing feature. |

## Public surface

`pub(crate)` only: `execute`, `pool_stats`, `resolve`, `RuntimeCallError`. This
is a facade for `runtime/`'s own use, not a public API, and it re-exports only
what `runtime/` actually calls. `modules::runtime` has more surface (a
`Languages` listing, for one) that the stub deliberately does not mirror.

## Used by

- `crates/openhuman-core/src/runtime/node/bootstrap.rs` and
  `crates/openhuman-core/src/runtime/python/bootstrap.rs`: call `resolve` to
  get a toolchain and `execute` to run inline code on it.
- `crates/openhuman-core/src/runtime/pool/`: calls `execute` and `pool_stats`
  for pooled inline execution.

## Where next

- [`modules/registry`](../../modules/registry/README.md) for how the real
  `tinyruntime` module gets loaded and admitted.
- [`runtime/node`](../node/README.md) and [`runtime/python`](../python/README.md)
  for the toolchain clients that sit on top of this facade.

## Further reading

- [Parent module (`runtime`)](../README.md)
- [tinyruntime submodule](../../../../../vendor/tinyruntime/README.md)
- [System and utilities tools](../../../../../gitbooks/features/native-tools/system-and-utilities.md)
- [Loadable modules](../../../../../gitbooks/developing/loadable-modules.md)
