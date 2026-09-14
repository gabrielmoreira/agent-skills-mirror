# `openhuman-rpc`

Shared JSON-RPC / CLI wire contracts for OpenHuman: response envelopes,
structured error encoding, and the authenticated HTTP client used to reach a
core's `/rpc` endpoint. It is its own crate so the side that produces
envelopes (`openhuman-core`, via `crate::rpc`) and the sides that decode them
(the Tauri shell's HTTP relay in `crates/openhuman-app`, the TUI in
`crates/openhuman-tui`) compile the same definition, and so that definition
depends on nothing in the core — only `serde`/`serde_json`, plus the optional
HTTP client.

## Public surface

- `pub struct RpcOutcome<T>` / `fn new` / `fn single_log` / `fn into_cli_compatible_json` — `lib.rs` — handler result plus its log lines; the type domain `ops.rs` operations return (see `AGENTS.md`'s module-shape table).
- `pub fn apply_log_envelope(value, logs) -> Value` — `lib.rs` — single definition of the bare-vs-wrapped response-shape rule; see its doc comment before touching it.
- `pub fn unwrap_rpc(value: &Value) -> &Value` — `lib.rs` — client-side unwrapping of nested `result`/`data` envelopes.
- `pub struct StructuredRpcError` / `pub const STRUCTURED_RPC_ERROR_SENTINEL` — `structured_error.rs` — typed error envelope, sentinel-encoded into the controller `Result<_, String>` channel and decoded by `crates/openhuman-core/src/core/jsonrpc.rs`.
- `pub struct HttpRpcResponse` — `client.rs` (feature `http-client`) — verbatim status + body from an OpenHuman RPC endpoint.
- `pub fn post_json_rpc(url, token, body) -> Result<HttpRpcResponse, String>` — `client.rs` (feature `http-client`) — POST a JSON-RPC body with a 30s timeout; disables redirects when a bearer token is set.
- `pub fn bearer_header(token: Option<&str>) -> Option<String>` — `client.rs` (feature `http-client`) — normalize a token into an `Authorization` header value.
- `pub fn redact_url_for_log(url: &str) -> String` — `client.rs` (feature `http-client`) — strip credentials, path, query and fragment before logging a URL.

## Feature flags

- `http-client` (default-on in this crate) pulls in `log`, `reqwest`
  (`rustls-tls`, no default features) and `url`, and adds `client.rs`'s
  surface. Without it the crate is `serde`/`serde_json` only.
- The root workspace declares `openhuman-rpc = { path = ..., default-features
  = false }`, so a consumer gets `http-client` only by asking for it.
  `crates/openhuman-app/Cargo.toml` (outside the workspace) enables it
  explicitly: `openhuman-rpc = { path = "../openhuman-rpc", features =
  ["http-client"] }`. `crates/openhuman-core/Cargo.toml` and
  `crates/openhuman-tui/Cargo.toml` use `openhuman-rpc.workspace = true` and
  therefore build the crate with **no** features — they only need the
  envelope and error types. `cargo tree -p openhuman -e normal -f "{p} [{f}]"
  --depth 1` shows `openhuman-rpc [...] []` for both; the app's tree shows
  `[default,http-client]`.

## Consumers

- `crates/openhuman-core/src/lib.rs` — `pub use openhuman_rpc as rpc;`, so
  domain `ops.rs` files return `RpcOutcome<T>` through this crate rather than
  a locally defined type.
- `crates/openhuman-app/src/core_rpc.rs` — imports (`pub(crate) use`, renamed
  to `relay_bearer_header` / `RelayHttpResponse`) `bearer_header`,
  `HttpRpcResponse` and `redact_url_for_log`, and wraps `post_json_rpc` in
  its own `post_json_rpc` / `relay_http_rpc` to reach both the embedded core
  and self-hosted runtimes from the Rust host (see the mixed-content note in
  that file, #3865).
- `crates/openhuman-tui/src/cockpit.rs` — `pub use openhuman_rpc::unwrap_rpc;`
  is the TUI's decode point; `controls.rs`, `app.rs` and `state.rs` read RPC
  responses through it.

## Rules

- Contract-only: no domain types, no dependency on `openhuman-core`, no
  `tokio` of its own (`post_json_rpc` is `async` over `reqwest` but never
  owns or spawns a runtime), and no I/O outside `client.rs`.
- `apply_log_envelope`'s bare-vs-wrapped rule is a wire contract with a known
  defect (#6080), preserved deliberately:

  ```text
  logs.is_empty()  ->  value                            (bare)
  otherwise        ->  { "result": value, "logs": … }   (wrapped)
  ```

  A controller's wire shape is decided by its log vector, not its schema, so
  a handler that later gains a log line silently changes its own response
  shape. Do not "fix" this here — it needs a maintainer ruling because
  normalizing it is a wire change across every controller. See the doc
  comment on `apply_log_envelope` for the full rationale.

## Tests

`#[cfg(test)] mod tests` blocks in `src/lib.rs` and
`src/structured_error.rs` cover the envelope rule and the sentinel
encode/decode round trip. Run with:

```bash
cargo test -p openhuman-rpc
```
