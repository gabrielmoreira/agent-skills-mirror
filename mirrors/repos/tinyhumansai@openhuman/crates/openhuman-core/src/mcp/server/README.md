# mcp/server

Opt-in **Model Context Protocol (MCP) server** that exposes a curated, security-gated slice of OpenHuman's tool surface (memory-tree reads/writes, core/agent introspection, subagent execution, SearXNG search) and bundled prompt assets to external MCP clients (Claude Desktop, Cursor, Windsurf, …). Started via `openhuman-core mcp` — stdio transport by default, or `--transport http` for Streamable HTTP + SSE on a local bind address. It is a JSON-RPC dispatcher, not a registered RPC domain: it has no `schemas.rs`/controllers and is wired only through `crates/openhuman-core/src/core/cli.rs`, translating each MCP `tools/call` into an existing registered core RPC method.

## Responsibilities

- Implement the MCP JSON-RPC server lifecycle: `initialize`, `ping`, `tools/list`, `tools/call`, `resources/list`, `resources/templates/list`, `resources/read`, plus notifications (`notifications/initialized`, `notifications/cancelled`).
- Advertise a fixed catalog of MCP tools (`tool_specs`) with input JSON-schemas and MCP `ToolAnnotations` (`readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint`).
- Validate/normalize tool arguments at the MCP layer (explicit rejection over silent clamping), map them to registered core RPC params, and dispatch via `all::try_invoke_registered_rpc`.
- Enforce `SecurityPolicy` per call: read tools require `ToolOperation::Read`; `agent.run_subagent` and the three write tools require `ToolOperation::Act`.
- Run write tools (`memory.store`, `memory.note`, `tree.tag`) through a dedicated write-dispatch + audit pipeline that records every attempt (success and rejection) to the MCP write-audit log.
- Serve bundled prompt assets (`IDENTITY.md`, `SOUL.md`, `USER.md`, and each built-in subagent's `prompt.md`) as static MCP resources under the `openhuman://prompts/...` URI scheme.
- Provide two transports — newline-delimited JSON-RPC over stdio, and Axum-based Streamable HTTP + SSE with session-id + protocol-version handshakes and optional bearer auth.
- Capture client provenance from `initialize` `clientInfo.name` into a per-session `source_type` (e.g. `mcp:claude-desktop`) used for audit attribution.

## Key files

| File | Role |
| --- | --- |
| `crates/openhuman-core/src/mcp/server/mod.rs` | Module docstring + private submodule decls; re-exports `run_http`/`run_http_reporting`/`HttpServerConfig`, `run_stdio_from_cli`, `ensure_local_http`/`LocalMcpEndpoint`, `current_subagent_depth`/`HEADER_SUBAGENT_DEPTH`, `tool_specs`/`McpToolSpec`. |
| `crates/openhuman-core/src/mcp/server/protocol.rs` | JSON-RPC 2.0 dispatch core: parses lines/values (single + batch), routes `initialize`/`ping`/`tools/*`/`resources/*`, builds success/error envelopes, negotiates protocol version. |
| `crates/openhuman-core/src/mcp/server/tools/` | Tool catalog and dispatch, split into `mod.rs` (facade), `types.rs` (`McpToolSpec`, `ToolCallError`, the limit/tag constants — stays ungated so `McpToolSpec` is one real type in both builds), `specs.rs` (`tool_specs`/`base_tool_specs`/`searxng_tool_spec` builders), `params.rs` (argument parsing/validation → RPC params), `dispatch.rs` (`call_tool`/`list_tools_result`, act-policy enforcement, subagent handlers). |
| `crates/openhuman-core/src/mcp/server/write_dispatch.rs` | Write/audit pipeline for `memory.store`/`memory.note`/`tree.tag`: config load, act-policy enforcement, RPC dispatch to `openhuman.memory_doc_put`, audit-record write (success/rejection) via `crate::mcp::audit::record_write`, PII-redacting arg summaries. |
| `crates/openhuman-core/src/mcp/server/resources.rs` | Static `RESOURCE_CATALOG` of compile-time-embedded (`include_str!`) prompt markdown; `resources/list`, `resources/templates/list` (always empty), `resources/read`. Test cross-checks catalog vs `agent::agents::BUILTINS`. |
| `crates/openhuman-core/src/mcp/server/session.rs` | `McpSession` — captures + normalizes client name from `initialize` into a `source_type`; first observation locks the value. |
| `crates/openhuman-core/src/mcp/server/http.rs` | Axum Streamable HTTP + SSE transport (`run_http`, `HttpServerConfig`): POST/GET/DELETE on `/`, session map, protocol-version checks, optional `Authorization: Bearer`, SSE keep-alive, session-id redaction. Gated on `all(feature = "mcp", feature = "http-server")` — the transport is axum-only. |
| `crates/openhuman-core/src/mcp/server/local.rs` | Lazily-started, process-wide in-process loopback HTTP MCP server (`ensure_local_http`, `LocalMcpEndpoint`). Lets the sandboxed `claude` subprocess (Claude Code provider) reach OpenHuman's memory/tools over loopback without the MCP server inheriting Claude Code's OS jail; a per-process random bearer token stops any other local process from talking to it. |
| `crates/openhuman-core/src/mcp/server/subagent_depth.rs` | Per-delegation-chain depth tracking for `agent.run_subagent`, propagated across the loopback MCP HTTP hop via the `X-OpenHuman-Subagent-Depth` header so nested Claude Code subagent calls are bounded without penalizing unrelated parallel callers. |
| `crates/openhuman-core/src/mcp/server/stdio.rs` | CLI entry `run_stdio_from_cli` (arg parse: `--transport`/`--host`/`--port`/`--auth-token`/`-v`/`--help`), logging init, stdio read/write loop (`run_stdio`). |
| `crates/openhuman-core/src/mcp/server/stub.rs` | The `mcp`-less mirror of `run_stdio_from_cli`, `ensure_local_http`/`LocalMcpEndpoint`, and `tool_specs` — disabled-error / empty-catalog bodies so always-on callers (`core/cli.rs`, the Claude Code driver, `tools/registry/ops.rs`) keep a stable surface. |
| `crates/openhuman-core/src/mcp/server/tools_tests.rs` | Sibling `#[cfg(test)]` suite for `tools/` (via `#[path]`). |

## Public surface

Re-exported from `mod.rs`:

- `run_stdio_from_cli(args: &[String]) -> Result<()>` — CLI entry point; builds its own tokio runtime and selects stdio vs HTTP transport.
- `run_http(config: HttpServerConfig) -> Result<()>`, `run_http_reporting` (the same, plus a oneshot that reports the bound address; `local.rs` uses it), and `HttpServerConfig { bind_addr, auth_token }` — HTTP/SSE server (`mcp` + `http-server`).
- `ensure_local_http() -> Result<LocalMcpEndpoint>` and `LocalMcpEndpoint { addr, token }` — the loopback in-process server for the Claude Code driver.
- `current_subagent_depth()` / `HEADER_SUBAGENT_DEPTH` — the delegation-depth hop for `agent.run_subagent`.
- `tool_specs() -> Vec<McpToolSpec>` and `McpToolSpec { name, title, description, rpc_method, input_schema, annotations }` — the advertised tool catalog.

## RPC / controllers

This module exposes **no** registered core RPC methods (no `schemas.rs`, no controllers, no `openhuman.mcp_server_*` namespace). It is the **client/server-of-MCP**, not an RPC domain. Instead it *consumes* existing registered RPC methods, mapping each MCP tool to one via `all::try_invoke_registered_rpc` after validating against `all::schema_for_rpc_method`:

| MCP tool | Mapped core RPC method |
| --- | --- |
| `memory.search` | `openhuman.memory_tree_search` |
| `memory.recall` | `openhuman.memory_tree_recall` |
| `tree.read_chunk` | `openhuman.memory_tree_get_chunk` |
| `tree.browse` | `openhuman.memory_tree_list_chunks` |
| `tree.top_entities` | `openhuman.memory_tree_top_entities` |
| `tree.list_sources` | `openhuman.memory_tree_list_sources` |
| `memory.store` / `memory.note` / `tree.tag` | `openhuman.memory_doc_put` |
| `searxng_search` | `openhuman.tools_searxng_search` |
| `core.list_tools` / `core.tool_instructions` / `agent.list_subagents` / `agent.run_subagent` | (no RPC mapping — handled in-process via `Agent` / `AgentDefinitionRegistry`) |

## Agent tools

It does **not** own any agent tools in the `tools.rs`/`crates/openhuman-core/src/tools` sense. The "tools" here are **MCP-protocol tools** advertised to external clients:

- Read-only (`ToolOperation::Read`): `core.list_tools`, `core.tool_instructions`, `agent.list_subagents`, `memory.search`, `memory.recall`, `tree.read_chunk`, `tree.browse`, `tree.top_entities`, `tree.list_sources`, `searxng_search` (config-gated on `searxng.enabled`).
- Act-policy (`ToolOperation::Act`): `agent.run_subagent` (annotated destructive/open-world; rejects `integrations_agent`), and the write tools `memory.store`, `memory.note`, `tree.tag` (annotated destructive/idempotent, local-only).

Argument bounds enforced in-layer: `k`/limits capped at `MAX_LIMIT` (50), default 10; `tree.tag` capped at 50 tags / 128 bytes per tag; SearXNG `max_results` capped at `SEARXNG_MAX_RESULTS`. Write tools derive deterministic upsert keys (`mcp-store-<slug>`, `mcp-note-<chunk_id>`, `mcp-tag-<chunk_id>`).

## Events

None. This module publishes/subscribes no `DomainEvent`s and has no `bus.rs`.

## Persistence

No `store.rs`. The only durable side effect is the **MCP write-audit log**, written via `crate::mcp::audit::record_write` (the sibling `mcp::audit` domain) for every write-tool attempt — including pre-dispatch rejections. Audit rows store a PII-redacted `args_summary` (titles truncated to 128 chars; `content`/`note_text` bodies omitted, only lengths/counts kept), `client_info`, success flag, and resulting `document_id`. Audit inserts run off the hot path via `spawn_blocking` (or a thread fallback). HTTP session records (`Mcp-Session-Id` → negotiated protocol version) are kept in an in-memory map only.

## Dependencies

- `crate::core::all` — `try_invoke_registered_rpc`, `schema_for_rpc_method`, `validate_params`: dispatch MCP tool calls into the registered core RPC layer and validate params against controller schemas.
- `crate::core::logging` (`CliLogDefault`, `init_for_cli_run`) — install the stderr tracing subscriber for the MCP subprocess.
- `crate::config` (`Config`, `rpc::load_config_with_timeout`, `McpAuthConfig`/`McpClientIdentityConfig` in tests) — load config for policy/searxng gating and per-call config.
- `crate::security` (`SecurityPolicy`, `ToolOperation`) — enforce read/act autonomy policy per tool call.
- `crate::agent` (`Agent`, `registry::agents::BUILTINS`, `harness::AgentDefinitionRegistry`, `tinyagents::convert::spec_to_schema`) — build the orchestrator agent for `core.list_tools`/`core.tool_instructions`, list/run subagents, and cross-check the resource catalog.
- `tinyagents_harness::tool::prompt_tool_instructions` — render the markdown tool-use instructions block for `core.tool_instructions`.
- `crate::tools` (`SEARXNG_MAX_RESULTS`, `normalize_categories`) — SearXNG bounds + category normalization for `searxng_search`.
- `crate::mcp::audit` (`record_write`, `NewMcpWriteRecord`, list/query helpers in tests) — durable write-audit log.
- `crate::mcp::http_client::McpHttpClient` — round-trip test harness for the HTTP transport (test-only).
- External crates: `axum`/`tokio`/`tokio-stream` (HTTP+SSE), `serde_json`, `uuid`, `sha2`/`hex` (session-id redaction, slug fallback hash), `chrono` (audit timestamps).

## Used by

- `crates/openhuman-core/src/core/cli.rs` — dispatches `mcp` / `mcp-server` subcommands to `run_stdio_from_cli`; the only production entry point for the stdio/HTTP transports. `crates/openhuman-core/src/platform/about_app/catalog_conversation_intelligence.rs` lists it as `intelligence.mcp_server`.
- `crates/openhuman-core/src/inference/provider/claude_code/driver.rs` — calls `ensure_local_http` on each Claude Code turn to hand the sandboxed `claude` subprocess a loopback MCP endpoint.
- `crates/openhuman-core/src/tools/registry/ops.rs` — reads `McpToolSpec`/`tool_specs()` (via `crate::mcp::server::McpToolSpec`) to fold this server's advertised tools into the agent tool registry catalog.
- The other `mcp/` members (`mcp::host`, `mcp::registry`, `mcp::audit`) are siblings in the broader MCP feature set, not consumers of this server's code paths. `mcp::http_client` is a re-export module of `tinymcp`, used here only by the test-only `McpHttpClient` HTTP round-trip.

## Notes / gotchas

- **Not a controller-registry domain.** Don't look for `schemas.rs`/`all_controller_schemas` — exposure is via the CLI only, and tool calls re-enter the registry through `core::all`.
- **`ToolCallError` variant → JSON-RPC code is deliberate:** `InvalidParams` → `-32602` (client-actionable, including policy denials so the reason text surfaces), `Internal` → `-32603` (config load / platform failures). Policy denials are intentionally `InvalidParams`, not `Internal`.
- **Explicit rejection over silent clamping** throughout: over-cap `k`, oversize/over-count tags, blank required strings, and unexpected arguments all error rather than being trimmed/dropped.
- **Write audit is fire-and-forget but mandatory:** rejections are audited even before config is loaded (`audit_write_rejection_without_config`), and `dispatch_write_tool` returns `Ok(tool_error(...))` (not `Err`) on RPC-handler failure so the client gets an MCP `isError` result while the failure is still recorded.
- **Protocol negotiation:** supports `2024-11-05`, `2025-03-26`, `2025-06-18`, and `2025-11-25` (`LATEST_PROTOCOL_VERSION`); unknown requested versions fall back to latest. HTTP enforces an exact session protocol-version match on subsequent requests.
- **HTTP security:** bearer auth is optional (`--auth-token`); session ids are SHA-256-redacted in logs; default bind is `127.0.0.1:9300`.
- **Resource catalog parity is CI-enforced:** `resources.rs` content is `include_str!`-embedded at compile time and the `catalog_mirrors_builtins` test fails if a built-in subagent lacks a matching `openhuman://prompts/agents/<id>` entry.
- **`agent.run_subagent` limits:** rejects `integrations_agent` (toolkit binding not yet supported over first-level MCP) and runs a fresh single-turn agent session tagged with an `mcp:<agent_id>:<uuid>` event context.
- **stdio logging defaults to `warn`** on stderr (so failures surface in client UIs); `--verbose` → `debug`; a user-set `RUST_LOG` always wins. Stdout is reserved for protocol messages only.
