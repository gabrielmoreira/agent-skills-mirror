# runtime/javascript

First-class **JavaScript language slot** for the core. This module is a thin
re-export facade: it gives the rest of the codebase a stable
`crate::runtime::javascript` import path that talks to a *language*
(`javascript`) rather than to a concrete backend. Today the implementation
backend is the managed Node.js client in [`crate::runtime::node`](../node/README.md),
which is itself a client for the vendored `tinyruntime` module — the facade
exists so the backend underneath can be swapped without churning callers. It
owns no logic of its own: every symbol it exposes is a `pub use`.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Entire module (26 lines). Module docstring plus `pub use` re-exports, some gated by the `runtime-node` feature. No types, no logic, no tests. |

## Gating (`runtime-node`)

The facade itself is **always compiled** — `ShellTool` and the other exec
tools hold an `Option<Arc<NodeBootstrap>>`, so the bootstrap type surface must
exist in every build:

- Always re-exported: `ExecuteToolOutcome`, `NodeBootstrap`, `NodeSource`,
  `ResolvedNode`. With `runtime-node` off, these come from
  `runtime::node::stub` (`resolve` errors with a build fact; `try_cached` /
  `probe_installed` return `None`).
- Re-exported only behind `runtime-node`: `RuntimeToolSummary`, `execute_tool`,
  `list_tools`, and the controller registry pair
  `all_javascript_controller_schemas` / `all_javascript_registered_controllers`
  (aliases of `all_runtime_node_controller_schemas` /
  `all_runtime_node_registered_controllers`). The controller pair only exists
  with the feature on; the dispatcher behind `execute_tool` / `list_tools`
  (`runtime::node::ops`) is itself always compiled because the ungated `flows`
  `oh:` backend calls it directly — only this facade's alias is gated, since
  its sole consumer here is the gated `runtime::node::rpc` bridge.

## Public surface

- **Types** (always): `ExecuteToolOutcome`, `NodeBootstrap`, `NodeSource`,
  `ResolvedNode`.
- **Types** (`runtime-node`): `RuntimeToolSummary`.
- **Functions** (`runtime-node`): `execute_tool`, `list_tools`.
- **Controller wiring** (`runtime-node`): `all_javascript_controller_schemas`,
  `all_javascript_registered_controllers`.

## RPC / controllers

Namespace `javascript`, defined in `runtime::node::schemas` and surfaced
through this facade's `all_javascript_*` aliases:

| Method | Inputs | Outputs |
| --- | --- | --- |
| `javascript.list_tools` | — | `tools`: array of tool metadata (`name`, `description`, `category`, `permission_level`, `scope`, `supports_markdown`, `parameters`). |
| `javascript.execute_tool` | `tool_name` (required), `args` (optional Json, defaults to `{}`), `prefer_markdown` (optional bool) | `tool_name`, `elapsed_ms` (u64), `result` (MCP-style `ToolResult`: `{content, is_error, markdownFormatted?}`). |

Handlers live in `runtime::node::rpc`, load config via
`config::rpc::load_config_with_timeout`, build the full tool set via
`tools::all_tools_with_runtime`, then list or dispatch a tool by exact name.

## Events

`execute_tool` (in `runtime::node::ops`) publishes on the bus with
`session_id = "javascript"`:

- `DomainEvent::ToolExecutionStarted`
- `DomainEvent::ToolExecutionCompleted` (with `success`, `elapsed_ms`)

## Used by

- `crates/openhuman-core/src/core/all.rs` — wires
  `all_javascript_registered_controllers` into the controller registry.
- `crates/openhuman-core/src/tools/ops.rs` — constructs the shared
  `Arc<NodeBootstrap>` (only when `runtime-node` is on and `config.node.enabled`);
  `tools/impl/system/{shell,node_exec,npm_exec}.rs` hold it for Node binary
  resolution.
- `crates/openhuman-core/src/runtime/node/rpc.rs` — calls back into
  `javascript::{list_tools, execute_tool}` through the facade alias.

## Notes / gotchas

- This is a rename-only facade: no `types.rs` / `ops.rs` / `store.rs` here by
  design. Edit behavior in [`runtime/node`](../node/README.md), not here.
- `javascript.execute_tool` rebuilds the entire tool set on every call — there
  is no persistent tool cache at this layer.
- See [`runtime/node/README.md`](../node/README.md) for everything the facade
  forwards to, including what moved out to the `tinyruntime` module.
