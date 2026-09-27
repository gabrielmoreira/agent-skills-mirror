# runtime

Code-execution runtimes: the client side.

Agents, skills, and flows run untrusted-ish code (JavaScript, Python) on top
of this module. The actual machinery, everything that downloads a toolchain,
verifies it, unpacks it, caches it, or keeps a warm worker in front of it,
lives in the `tinyruntime` module behind `crate::modules::runtime`. What is
here adapts that module's answers onto the types the rest of the core already
names, so a migration of the machinery did not turn into a migration of every
caller.

## Contents

- [`client`](client/README.md): the single import point the clients below use
  to reach `modules::runtime`, with a compile-time stand-in for builds that
  have the `modules` feature off.
- [`node`](node/README.md): the Node.js toolchain client, plus an unrelated
  tool bridge that exposes the full agent tool registry over JSON-RPC.
- [`javascript`](javascript/README.md): a thin re-export facade giving the
  rest of the core a stable `javascript` import path over the `node` client.
- [`python`](python/README.md): the Python interpreter client, plus the
  process-launch helper for long-lived Python children.
- [`python_server`](python_server/README.md): the persistent Python worker
  process that backs spaCy extraction and the Kompress text compressor.
- [`pool`](pool/README.md): pooled inline execution, plus the fallback
  classification that decides whether a failed job is safe to retry.

## Key types

Each toolchain client follows the same shape: a `resolve()` that asks the
module for a runtime and adapts the reply (`ResolvedNode`, `ResolvedPython`),
and a non-blocking `try_cached()` the shell can call on every command without
awaiting a bus round trip. `runtime::client::RuntimeCallError` (`Unavailable`,
`InvalidRequest`, `Failed`) is the shared error shape both `node` and `python`
build on.

## How it fits

`runtime/` is the host half of the split described in `crate::modules::runtime`:
interpreter discovery, managed installs, and pooled workers are module
concerns; deciding what to run and adapting the result onto core types is a
`runtime/` concern. Callers such as the `node_exec`, `python_exec`, and `shell`
tools (`crates/openhuman-core/src/tools/impl/system/`) hold an `Arc` to a
toolchain client rather than talking to the module directly.

## Where next

- [`modules/registry`](../modules/registry/README.md) for how `tinyruntime` and
  its language providers get loaded and admitted.
- `gitbooks/developing/performance.md` for how pooling and in-process
  execution contribute to the project's density and cold-start numbers.
