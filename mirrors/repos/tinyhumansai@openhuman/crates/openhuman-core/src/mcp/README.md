# mcp — MCP host

Host-side half of Model Context Protocol support. Both transports, the
static config-declared server set, the dynamic (Smithery/official-catalog)
registry with its store, its reconnect supervisor and browser sign-in, and
the write-audit log moved out to [`tinymcp`](https://github.com/tinyhumansai/tinymcp).
What is here is what belongs to this application: the one holder of that
library's services, the RPC surface over it, the agent-facing tools, and the
`openhuman mcp` server that exposes this application's own tools to external
MCP hosts.

## Responsibilities

- Hold the `tinymcp` service — one per workspace — and open it at boot
  ([`host`]).
- Expose the `mcp_clients` and `mcp_setup` RPC namespaces, the agent-facing
  `mcp_registry_*` tools, and the prompt-injection scan over remote tool
  definitions ([`registry`]).
- Expose the RPC surface over the write-audit log ([`audit`]).
- Run the `openhuman mcp` stdio/HTTP server that serves this application's
  own tools to external MCP clients ([`server`]) — the *server* side, which
  did not move because it is bound to the tool registry, the permission
  model and the agent turn machinery.

## Where the boundary fell

Three things stayed here on purpose, each because it is host policy rather
than protocol:

- **Prompt-injection detection** over remote tool definitions
  (`registry::tools_safe_for_agent`). The detector, its rules, and what a hit
  means belong to this application's threat model. The *lexical* half —
  control characters, prompt-template fences, length caps — lives in the
  contract instead, applied by the display accessors on every remote
  description.
- **Events.** `tinymcp` reports what happened in its return values;
  translating that into a `DomainEvent` happens here, where the vocabulary is
  known (`registry::ops`/`setup_ops` for the RPC-driven lifecycle events,
  `registry::supervisor_events` for what the reconnect supervisor observed,
  `registry::tools_safe_for_agent` for `McpToolRejected`). `audit` publishes
  nothing.
- **The proxy decision.** Whether a proxy applies to MCP traffic is decided
  by this application's proxy scope setting, per-service list and no-proxy
  list — `host::proxy_for_mcp` consults them and hands `tinymcp` the answer.

## Key files

| Path | Purpose |
| --- | --- |
| `mod.rs` | Family root, entry points, and the two re-export facades below. |
| `host.rs` / `host_tests.rs` | The per-workspace `tinymcp` service holder — see [its own doc comment](host.rs) for the shape (`HOSTS` map, `McpHost`, `for_config`/`try_service`/`init`, `client_config`, `proxy_for_mcp`). |
| [`registry/README.md`](registry/README.md) | `mcp_clients`/`mcp_setup` RPC, agent tools, reconnect-supervisor events. |
| [`audit/README.md`](audit/README.md) | `mcp_audit` RPC over the write-audit log. |
| [`server/README.md`](server/README.md) | The `openhuman mcp` server (this application as an MCP host's target). |

## The two re-export modules

`mcp::http_client` and `mcp::config_servers` are not directories — they no
longer hold transport source, only `pub use` re-exports of `tinymcp`:

- `http_client` (ungated) — the Streamable HTTP transport:
  `tinymcp::transport::http::{McpHttpClient, McpHttpClientBuilder}`,
  `tinymcp::Error` as `McpError`, `redact_endpoint`, `render_tool_result`, and
  the `tinymcp_bus` wire types (`McpRemoteTool`, `McpServerToolResult`,
  `McpSseEvent`, the OAuth challenge/metadata types). Always compiled because
  the ungated `gitbooks` tool (`tools/impl/network/gitbooks.rs`) dials
  `McpHttpClient`; `mcp::server`'s test-only HTTP round-trip names it too.
- `config_servers` (`mcp` feature) — the statically declared, TOML-configured
  server set: `tinymcp::transport::stdio::McpStdioClient`,
  `McpRegistrySource`, `McpServerDefinition`, `McpServerRegistry`,
  `McpTransportClient`, and `tinymcp_bus::McpAuthConfig` re-exported as
  `McpDefinitionAuth` (distinct from this application's own
  `config::McpAuthConfig`, which the TOML file declares).

Neither module implements a transport, a handshake, or OAuth discovery any
more — that all lives in `tinymcp` now. Read
[the tinymcp repo](https://github.com/tinyhumansai/tinymcp) for that half.

## Startup wiring

`mcp::start(config)` initializes the registry's bus subscriber and opens the
host service; it never fails (MCP being unavailable must not stop the core
coming up). `mcp::start_boot_jobs(config)` additionally spawns the
installed-server boot pass and the reconnect supervisor. Both are called from
`core/jsonrpc.rs` (`start` on the RPC-enable path) and
`core/runtime/services.rs` (`start_boot_jobs` on the boot path); each is
idempotent so the two callers can't double-register or double-spawn.

## Compile-time gate (`mcp` feature)

`pub mod mcp;` is always compiled — the family root is a facade. `host` and
`http_client` are ungated because the startup path and always-on consumers
reach them unconditionally. `registry`, `audit`, and `server` keep
their own gate and their own `stub.rs`, so a build without the feature still
serves `/rpc` without those namespaces; `config_servers` is simply
`#[cfg(feature = "mcp")]` with no stub.

## Dependencies

- `tinymcp` (path dependency on `vendor/tinymcp`, `default-features = false`)
  — the extracted client library.
- `tinymcp-bus` — the wire contract: payload types and member names, with no
  transport and no runtime, also used to generate the desktop settings
  schema.
- `crate::config` — `McpClientConfig`/`McpServerConfig`/`McpAuthConfig` and
  the runtime proxy config `host::client_config`/`proxy_for_mcp` convert
  from.
- `crate::core::bus` / `crate::core::events` — `DomainEvent` publishing for
  everything that stayed host-side.

See `Cargo.toml` (`crates/openhuman-core/Cargo.toml`, the `tinymcp` block)
for why this stays a path dependency rather than the pinned release, and
`crates/openhuman-core/src/modules/registry/records_mcp_connectors.rs` for
the release version this application does pin for the loadable-module path.
