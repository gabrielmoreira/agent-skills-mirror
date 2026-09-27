# tls

Platform-conditional TLS backend selection for `reqwest` HTTP clients. A single tiny utility that centralizes the `#[cfg(target_os = "windows")]` guard so every HTTP-client construction site picks the right TLS backend in one line, and future policy changes live in exactly one place.

## Responsibilities

- Provide one canonical `reqwest::ClientBuilder` factory pre-configured with the platform-appropriate TLS backend.
- Encode the cross-platform TLS policy:
  - Windows uses `native-tls` (schannel). It honors the Windows certificate store, including corporate, AV, or TLS-inspecting-proxy CAs. `rustls` plus webpki-roots only knows Mozilla CAs and fails such environments with `UnknownIssuer`.
  - macOS and Linux use `rustls` plus webpki-roots, which avoids the OpenSSL runtime dependency on Linux and has historically been more reliable than `native-tls` on macOS staging TLS handshakes.

## Key files

| File | Role |
| --- | --- |
| `crates/openhuman-core/src/util/tls/mod.rs` | Entire module: module docstring (policy) plus the single `tls_client_builder()` function. No `mod`/`pub mod` declarations, no submodules. |

## Public surface

- `tls_client_builder() -> reqwest::ClientBuilder`: returns a `reqwest::Client::builder()` with `.use_native_tls()` on Windows and `.use_rustls_tls()` elsewhere, selected at compile time via `cfg`. It is the starting point for any client reaching external HTTPS endpoints; callers chain `.timeout(...)`, `.http1_only()`, proxy config, and so on, then `.build()`.

No RPC surface, agent tools, bus events, or persistence. It is a stateless factory function.

## Dependencies

Only the external crate `reqwest` (and its `native-tls` / `rustls` feature backends). No `use crate::*` or `use crate::core::*` imports; this is a leaf utility module with zero internal dependencies.

## Used by

Every HTTP-client construction site that talks to external HTTPS endpoints, including:

- `crates/openhuman-core/src/config/schema/proxy.rs`: proxy-aware client builders (primary and fallback).
- `crates/openhuman-core/src/integrations/client/construct.rs` and `crates/openhuman-core/src/integrations/composio/client/connections.rs`.
- `crates/openhuman-core/src/search/tools/*.rs` (`tavily`, `exa`, `brave`, `searxng`, `querit`, `seltz`): search-tool HTTP clients.
- `crates/openhuman-core/src/api/headers.rs`: the shared authenticated-client builder used by the backend REST client.

Declared via `pub mod tls;` in `crates/openhuman-core/src/util/mod.rs`; not re-exported at the `util` root, so callers spell `crate::util::tls::tls_client_builder`.

## Notes and gotchas

- Backend choice is compile-time (`cfg(target_os = ...)`), not runtime. You cannot switch backends at runtime without recompiling for the target.
- Always start from `tls_client_builder()` rather than `reqwest::Client::builder()` directly, otherwise Windows corporate-CA environments will fail with `UnknownIssuer`.
- The doctest in the docstring is `rust,ignore`.
