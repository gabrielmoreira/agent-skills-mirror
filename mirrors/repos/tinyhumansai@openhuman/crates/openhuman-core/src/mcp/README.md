# mcp

The host half of Model Context Protocol support. The MCP client itself (both
transports, the config-declared server set, the dynamic server registry with
its store, reconnect supervisor and browser sign-in, and the write-audit log)
lives in the vendored `tinymcp` library. This folder holds what belongs to
OpenHuman: the one `tinymcp` service per workspace, the RPC surface over it,
the agent-facing tools, the prompt-injection screen over remote tool
definitions, and the `openhuman-core mcp` server that exposes OpenHuman's own
tools to external MCP hosts such as Claude Desktop or Cursor.

## How it works

There are two directions. As a client, OpenHuman connects to MCP servers the
user declared and lets its agents call their tools. As a server, it answers
other MCP hosts that call into it.

```text
          client side                               server side
 +-------------------------------+        +------------------------------+
 | agent tools                   |        | external MCP host            |
 |  mcp_registry_*  (registry/)  |        | (Claude Desktop, Cursor,     |
 |  mcp_<server>_<tool>          |        |  sandboxed claude subprocess)|
 |  installed-server actions     |        +--------------+---------------+
 |  mcp_list_servers/... (tools/ |                       | stdio or HTTP
 |   impl/network, static set)   |                       v
 +---------------+---------------+        +------------------------------+
                 |                        | server/  OpenHumanMcpHandler |
 RPC mcp_clients.*, mcp_audit.*           |  over tinymcp::server        |
                 |                        +--------------+---------------+
                 v                                       |
 +-------------------------------+                       v
 | host.rs  McpHost per workspace|        registered core RPC methods
 |  dynamic()  static_servers()  |        (memory, agent, search, ...)
 |  audit()                      |        under SecurityPolicy, with
 +---------------+---------------+        writes recorded to the audit log
                 |
                 v
          vendor/tinymcp
```

### The service holder

[`host.rs`](./host.rs) keeps a process-wide map (`HOSTS`) from workspace path to one
`McpHost`. An `McpHost` wraps the `tinymcp` service and exposes its three
parts: `dynamic()` (the user-declared registry), `static_servers()` (the
TOML-declared set) and `audit()` (the write-audit store). The library holds no
globals of its own, so two hosts in one process do not share connections;
this holder is the one place that decides there is one per workspace.

`host::init` opens the service at boot. A caller that arrives earlier gets
`None` from `try_service` rather than a service built on a configuration
nobody chose. `for_config` opens or returns the host for a specific
workspace, and `all_hosts` lets the supervisor walk every workspace opened so
far. `client_config` converts OpenHuman's `[mcp_client]` config into
`tinymcp`'s `McpClientConfig`.

### Startup

```text
 core/runtime/subscribers.rs (RPC enable path)   core/runtime/services.rs
                 |                                         |
                 v                                         v
            mcp::start                        mcp::start_boot_jobs
   registry::bus::init()                        mcp::start
   host::init() (failure logged, ignored)       spawn installed-server boot
                                                spawn configured tool-cache
                                                  refresh
                                                spawn reconnect supervisor
                                                  (Once)
```

Both entry points are idempotent, so the two startup paths can both call
them. `mcp::start` never fails: MCP being unavailable must not stop the core
coming up. The boot jobs dial installed servers, refresh every configured
server's cached tool list once per app load, and start the reconnect
supervisor exactly once per process. Between loads the tool cache changes
only on an MCP change (connect, credentials, disable, uninstall, an edited
definition).

### What stayed host-side, and why

Three things are host policy rather than protocol:

- Prompt-injection detection over remote tool definitions.
  `registry::tools_safe_for_agent` ([`registry/mod.rs`](./registry/mod.rs)) drops a tool whose
  description trips a rule, and logs and publishes `McpToolRejected` with the
  rule code only, never the offending text. The lexical half (control
  characters, prompt-template fences, length caps) lives in the
  `tinymcp-bus` contract and is applied by its display accessors.
- Events. `tinymcp` reports outcomes in return values. Turning them into
  `DomainEvent`s happens here: [`registry/ops.rs`](./registry/ops.rs) for RPC-driven lifecycle
  events, [`registry/supervisor_events.rs`](./registry/supervisor_events.rs) for what the reconnect supervisor
  observed, and `tools_safe_for_agent` for rejections. `audit/` publishes
  nothing.
- The proxy decision. `host::proxy_for_mcp` applies OpenHuman's proxy scope
  setting, per-service list and no-proxy list, and hands `tinymcp` a resolved
  proxy (or none).

### Two server sets

The static set is declared in config TOML (`[[mcp_client.servers]]`) and is
reached through `mcp::config_servers` and the `mcp_list_servers`,
`mcp_list_tools` and `mcp_call_tool` bridge tools plus per-tool
`mcp_<server>_<tool>` tools in [`tools/impl/network/`](../tools/impl/network/). The dynamic set is the
user's `mcp.json` document, edited through `mcp_clients.config_get` and
`config_set`, browsed from the Smithery and official catalogs, and reached
through the `mcp_registry_*` tools and installed-server actions. Both are
compiled out with the `mcp` feature.

## Layout

| Path | What it does |
| --- | --- |
| [`mod.rs`](./mod.rs) | Family root: `start`, `start_boot_jobs`, the configured tool-cache refresh, the supervisor spawn, and the `http_client` and `config_servers` re-export modules. |
| `host.rs` | The per-workspace `McpHost` holder, config conversion (`client_config`, `static_registry`), `oauth_redirect_uri`, `proxy_for_mcp`. |
| [`registry/`](registry/README.md) | The `mcp_clients` RPC namespace (including `mcp.json`), the `mcp_registry_*` agent tools, installed-server action tools (`action_tool.rs`), supervisor event translation, the injection screen, and the `boot`, `supervisor`, `oauth` and `connections` helpers. |
| [`audit/`](audit/README.md) | The `mcp_audit` RPC namespace over the write-audit log. |
| [`server/`](server/README.md) | The `openhuman-core mcp` stdio and Streamable HTTP server, its tool catalog and dispatch, the write-audit pipeline, prompt resources, and the in-process loopback endpoint used by the sandboxed Claude Code provider. |

`mcp::http_client` and `mcp::config_servers` are modules in `mod.rs`, not
directories, and hold only `pub use` re-exports of `tinymcp`:

- `http_client` (ungated): the Streamable HTTP transport
  (`McpHttpClient`, `McpHttpClientBuilder`), `tinymcp::Error` as `McpError`,
  `redact_endpoint`, `render_tool_result`, and `tinymcp_bus` wire types
  (`McpRemoteTool`, `McpServerToolResult`, `McpSseEvent`, the OAuth challenge
  and metadata types). It is always compiled because the ungated `gitbooks`
  tool ([`tools/impl/network/gitbooks.rs`](../tools/impl/network/gitbooks.rs)) dials `McpHttpClient`.
- `config_servers` (`mcp` feature): `McpStdioClient`, `McpRegistrySource`,
  `McpServerDefinition`, `McpServerRegistry`, `McpTransportClient`, and
  `tinymcp_bus::McpAuthConfig` re-exported as `McpDefinitionAuth`. That is a
  different type from OpenHuman's own `config::McpAuthConfig`, which is what
  the TOML declares.

## Key types and entry points

- `McpHost` (`host.rs`) and `host::{init, for_config, try_service, service,
  all_hosts}`.
- `host::client_config`, `host::static_registry`, `host::proxy_for_mcp`.
- `mcp::start`, `mcp::start_boot_jobs` (`mod.rs`).
- `registry::connections::{connected_overview,
  connected_overview_for_config}`: the connected-server view the tool
  registry and diagnostics read.
- `registry::types`: `InstalledServer`, `McpTool`, `ConnStatus` and the
  catalog types, re-exported from `tinymcp_bus` (the Smithery names are
  aliases for the contract's `Registry*` types).
- `server::{run_stdio_from_cli, run_http, ensure_local_http, tool_specs}`
  (see [server/README.md](server/README.md)).

## RPC surface

Registered through [`core/all.rs`](../core/all.rs):

- `mcp_clients.*` ([`registry/schemas/`](./registry/schemas/)): `registry_search`,
  `registry_get`, `registry_settings_get`, `registry_settings_set`,
  `installed_list`, `config_get`, `config_set`, `update_env`, `uninstall`,
  `set_enabled`, `detect_auth`, `oauth_begin`, `connect`, `disconnect`,
  `status`, `list_tools`, `tool_call`. On the wire these are
  `openhuman.mcp_clients_<function>`.
- `mcp_audit.list` ([`audit/schemas.rs`](./audit/schemas.rs)): rows from the write-audit log.

The `openhuman-core mcp` server is not an RPC domain. It is a CLI entry wired
through [`core/cli.rs`](../core/cli.rs) that translates each MCP `tools/call` into an existing
registered core RPC method.

Agent tools registered from this folder: `mcp_registry_search`,
`mcp_registry_get`, `mcp_registry_installed_list`, `mcp_registry_status`,
`mcp_registry_list_tools`, `mcp_registry_connect`,
`mcp_registry_disconnect`, `mcp_registry_tool_call` and
`mcp_registry_uninstall`, plus deferred per-action tools for installed
servers. There is no install tool: servers are added by the user in
`mcp.json`.

## Boundaries

- `tinymcp` ([`vendor/tinymcp`](../../../../vendor/tinymcp/), repo `tinyhumansai/tinymcp`) owns the
  transports, handshakes, OAuth discovery, the dynamic registry and its
  SQLite store, the supervisor, the write-audit store, and the generic server
  half (`tinymcp::server`). Fix protocol or client behavior there and move the
  gitlink.
- `tinymcp-bus` is the wire contract: payload types and member names with no
  transport or runtime. It also generates the desktop settings schema. Never
  redeclare its types here.
- `crate::config` owns `McpClientConfig`, `McpServerConfig` and
  `McpAuthConfig`, which `host.rs` converts from.
- The `mcp_*` bridge tools over the static set live in
  `tools/impl/network/`; MCP tools in the cross-surface discovery registry
  are assembled by [`tools/registry/`](../tools/registry/).
- `tinymcp` is a path dependency on `vendor/tinymcp` with
  `default-features = false` (see the `tinymcp` block in
  [`crates/openhuman-core/Cargo.toml`](../../Cargo.toml) for why it is not the pinned release).
  The loadable-module release pin is in
  [`modules/registry/records_mcp_connectors.rs`](../modules/registry/records_mcp_connectors.rs).

## Gotchas

- The `mcp` feature gates `registry`, `audit` and `server`, each of which has
  its own `stub.rs` so a build without the feature still serves `/rpc`
  without those namespaces. `host` and `http_client` are ungated because the
  startup path and always-on consumers reach them without a `cfg`.
  `config_servers` is `#[cfg(feature = "mcp")]` with no stub.
- The server's HTTP transport also needs the `http-server` feature, which
  forwards `tinymcp/server-http`.
- `host::try_service` returns `None` before boot. Code that can run early must
  handle an absent service rather than build one.
- Rejected remote tools are published by rule code only. Do not add the
  description text to logs or events; it is the dangerous payload.

## Tests

Each module has a sibling `*_tests.rs` ([`host_tests.rs`](./host_tests.rs), and the suites under
`registry/`, `audit/` and `server/`, including the wire and HTTP golden tests
in `server/`). Run with `cargo test -p openhuman mcp::` or
`pnpm debug rust mcp`, and check the disabled build with
`cargo check --no-default-features`.

## Further reading

- [Parent module README](../../README.md)
- [MCP servers and skills](../../../../gitbooks/features/integrations/mcp-and-skills.md)
- [MCP registry](../../../../gitbooks/developing/architecture/mcp-registry.md)
- [MCP server](../../../../gitbooks/developing/mcp-server.md)
- [tinymcp](../../../../vendor/tinymcp/README.md)
