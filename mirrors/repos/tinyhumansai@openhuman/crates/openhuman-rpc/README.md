# `openhuman-rpc`

JSON-RPC 2.0 for OpenHuman, on both sides of the wire. The core
(`openhuman-core`) owns what a controller *is*: its schema, the
`core::Outcome` it returns, the structured error envelope, the params rules
and in-process dispatch (`core::invoke::invoke_method`). This crate sits
above the core and owns how that is exposed: the JSON-RPC envelopes, the HTTP
client, and the core's HTTP / Socket.IO server.

## Public surface

- `RpcRequest`, `RpcSuccess`, `RpcFailure`, `RpcError`, `JSONRPC_VERSION`,
  `SERVER_ERROR_CODE` (`envelope.rs`): the envelopes the server reads and
  writes. `request_body` / `decode_response` are the client half.
- `unwrap_rpc`: re-exported from `openhuman_core::core`; reaches a handler's
  value through its `result` / `data` envelopes.
- `is_origin_allowed_with_extra`, `ALLOWED_ORIGINS_ENV` (`origin.rs`): the
  browser-origin allowlist for the HTTP API. Pure; the caller reads the env.
- `http-client` feature (`client.rs`): `post_json_rpc`, `bearer_header`,
  `redact_url_for_log`, `HttpRpcResponse`.
- `server` feature (`server/`): the core's JSON-RPC server.
  - `serve(&CoreRuntime, ready_tx, shutdown)` / `EmbeddedReadySignal`
    (`serve.rs`): bind the listener, start the runtime's services, serve
    until shutdown, then run the runtime's exit cleanup.
  - `run_server`, `run_server_headless`, `run_server_embedded`,
    `run_server_embedded_with_ready` (`shims.rs`): build a `CoreRuntime` and
    serve it. The desktop shell uses `run_server_embedded_with_ready`.
  - `build_core_http_router`, `rpc_handler` (`http/`): the axum router, one
    module per route family (`rpc_handler`, `health`, `events`, `dictation`,
    `oauth_mcp`, `cors`, `pages`).
  - `install_cli_server` (`cli.rs`): installs the launcher the core CLI's
    `run` / `serve` subcommands start (`core::server_launcher`).
  - `auth.rs` (bearer route policy), `classify.rs` (how a failed call is
    reported to Sentry), `socketio.rs`, `dev_connect.rs`.

## Feature flags

- `http-client`: pulls in `reqwest` (`rustls-tls`) for `client.rs`.
- `server`: pulls in `axum`, `socketioxide` and the tokio stack, and turns on
  the core's `http-server` gate for the domain-owned routes the router mounts
  (`inference::http`'s `/v1`, the dictation WebSocket).
- `crash-reporting`: forwarded to the core so the Sentry-routing tests run.
- Both `http-client` and `server` are default-on here. The root workspace
  declares the dependency with `default-features = false`, so each consumer
  asks for what it needs: `openhuman-cli` enables `server`, the TUI takes
  neither, and `crates/openhuman-app/Cargo.toml` (outside the workspace)
  enables `["http-client", "server"]`.

## Consumers

- `crates/openhuman-app`: `core_process.rs` runs the embedded server
  (`run_server_embedded_with_ready`); `core_rpc.rs` wraps the client to reach
  the embedded core and self-hosted runtimes (#3865); `session/link.rs` and
  `local_data_reset.rs` build requests with `request_body`; `lib.rs` calls
  `install_cli_server` before `run_core_from_args`.
- `crates/openhuman-cli`: `main.rs` calls `install_cli_server`; the root
  `tests/*.rs` suites build the router with `build_core_http_router`.
- `crates/openhuman-tui`: `unwrap_rpc` is its decode point.

## Socket.IO

`server/socketio.rs` bridges live domain events onto Socket.IO for the desktop
shell's webviews.
`COMPANION_STATE_BUS` is a broadcast channel for shell-originated companion
lifecycle events that still need to reach the native macOS notch WKWebView,
which has no Tauri IPC bridge and connects to the core's Socket.IO endpoint
directly. `spawn_web_channel_bridge` spawns one forwarding task per source:
web-chat events (`web_chat::subscribe_web_channel_events`, delivered to the
initiating client's room and the `thread:<id>` room, not broadcast),
dictation hotkeys and transcription results (`voice::dictation_listener`),
overlay attention bubbles (`desktop::overlay::subscribe_attention_events`,
see `desktop/overlay/README.md`), core notifications
(`desktop::notifications`), and companion state. It also forwards a set of
`DomainEvent`s read straight off `BUS`: session expiry, MCP setup secret
requests, memory sync and tree-build progress, channel listener health, and
active-workspace changes.
Everything except web-chat is broadcast to every connected client, most under
both a colon- and an underscore-separated event name.

## Rules

- No business logic. Controller semantics (results, errors, params,
  dispatch, session expiry) belong to the core; this crate only frames them
  as JSON-RPC and decides transport policy (auth routes, CORS, how loudly a
  failure is reported).
- The core does not depend on this crate. Anything a domain needs belongs in
  the core.

## Tests

Sibling `*_tests.rs` files cover the envelopes (including the exact
server-failure wire bytes), the origin allowlist, failure classification,
the `/rpc` handler's Sentry routing (with `crash-reporting`), CORS, auth
route policy, Socket.IO and `/dev/connect`.

```bash
cargo test -p openhuman-rpc --features crash-reporting
```
