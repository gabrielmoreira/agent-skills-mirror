# Backend

The core's side of reaching a hosted backend it knows nothing about: request
plumbing, the authenticated JSON client, error classification, and
budget-exhaustion detection.

The core has **no dependency on `tinyhumans-sdk`**. It reaches the backend
only through the port in `transport/` (`BackendTransport`); the SDK-backed
implementation lives in `crates/openhuman-tinyhumans`, which hosts install
once per process. A core with no transport installed runs agents, memory,
tools and RPC as normal and answers every backend-touching call with the
typed `BackendApiError::BackendUnavailable` / `BACKEND_UNAVAILABLE:`
sentinel, which `core::observability` demotes.

Routes are named here (and in the domains that call `authed_json`); the SDK
still owns route *policy* (its unexposed-route registry) inside the
transport. Add a missing backend route to `vendor/tinyhumans-sdk` so the
policy tables know it, then name it from the core as usual.

The core also holds no hosted URL, default, environment variable, header
policy or product identity of its own any more — those live with the
transport implementation (`crates/openhuman-tinyhumans/src/backend/`) and are
asked for through the helpers in `mod.rs`.

## Layout

| File | Purpose |
| --- | --- |
| `transport/` | `BackendTransport` port, `BackendRequest`, `BackendTransportError`, process-global install/resolve; `transport/plain.rs` is the `cfg(test)`-only reqwest fallback — production has no fallback, a host installs the transport from `openhuman-tinyhumans` |
| `client.rs` | `BackendClient`: authenticated JSON calls over the port, the typed `BackendApiError` results domains recover from, and `flatten_authed_error`, the chokepoint that turns them into the `SESSION_EXPIRED:` / `API_KEY_REJECTED:` / `BACKEND_UNAVAILABLE:` sentinels `core::observability` classifies |
| `client_tests.rs` | Tests for `client.rs` (included via `#[path]`) |
| `classify.rs` | `is_budget_exhausted_message` — backend/provider budget-exhaustion body classification shared by inference, agent loop guards, scheduler, web chat and telemetry |
| `mod.rs` | `base_url`, `require_base_url`, `inference_base_url`, `product_identity`, `attribution_headers` — thin helpers that ask the installed transport; there is no local URL, header or identity state here |

## `transport/`

`BackendTransport` is the one HTTP primitive every hosted-backend call rides:

```rust
async fn send_json(&self, req: BackendRequest<'_>) -> Result<Value, BackendTransportError>;
async fn send_multipart(&self, req: BackendRequest<'_>, form: Form) -> Result<Value, BackendTransportError>;
fn http_client(&self, profile: TransportProfile) -> reqwest::Client;
fn base_url(&self, configured: Option<&str>, purpose: BaseUrlPurpose) -> String;
fn product_identity(&self) -> String;
fn attribution_headers(&self) -> reqwest::header::HeaderMap;
fn name(&self) -> &'static str;
```

`BaseUrlPurpose::ControlPlane` resolves the origin for auth, billing,
integrations, channels, voice and sockets; `BaseUrlPurpose::Inference`
resolves the managed OpenAI-compatible proxy, honouring an `api_url` override
that points at an inference endpoint. `product_identity` and
`attribution_headers` answer the `x-sdk-name` value and the full attribution
header set (`x-core-version`, `x-tauri-version`, `x-sdk-name`) the installed
host attributes traffic to; both are empty/default without a transport.

`BackendRequest` carries the profile (`Api` for control-plane REST,
`Integrations` for `/agent-integrations/*`), base URL, method, path, query,
JSON body, the `BackendCredential` (session JWT → `Authorization: Bearer`,
API key → `x-api-key`) and whether the `{success,data}` envelope is unwrapped.
`BackendTransportError` mirrors the variants the classifiers match on
(`Http`, `Status`, `Envelope`, `RouteNotExposed`, …) plus `Unavailable`.

Resolution (`resolve_backend_transport`), first hit wins: the transport bound
to the ambient `CoreContext` (`CoreBuilder::backend_transport`, inherited by
`derive_with`) → the process global (`install_backend_transport`, what the
desktop shell, TUI and CLI use because they boot the core through
`run_server_embedded_with_ready` / `run_core_from_args`) → under `cfg(test)`
only, `PlainHttpTransport` → `Err(Unavailable)`. Production has no implicit
fallback.

## `client.rs`

`BackendClient` (renamed from `BackendOAuthClient`) holds the backend origin
(base URL stripped to its origin) and sends every request through the
process `BackendTransport` (`TransportProfile::Api`: attribution headers,
platform TLS, timeouts — all specified by the transport implementation). Key
surface:

- `authed_json` — send an authenticated request and route the result through
  `finish_authed_json`.
- Typed route helpers (`fetch_client_key`, `send_channel_*`,
  `*_channel_thread`) all go through `authed_json` and are bearer-only: the
  core never obtains, exchanges or validates a session. The account-bound
  routes (link tokens, `/auth/me` link checks, OAuth connect / integrations,
  billing, team, webhook tunnels, announcements) are called by
  `openhuman-tinyhumans` (`hosted/`) on the TinyHumans SDK's typed clients.
- `url_for`, `raw_client` — URL helpers for callers that need to drive a
  non-JSON request (e.g. multipart uploads) without re-implementing TLS/proxy
  setup. `raw_client` returns the transport's `Api`-profile client and fails
  with `BackendUnavailable` when no transport is installed.

`BackendApiError` is the typed-error surface `authed_json` callers should
match on for expected backend states rather than treating as failures:
`Unauthorized` (401 — session lapsed, not a bug), `ApiKeyRejected` (401 on a
library-mode API-key credential, kept distinct from `Unauthorized` so it
does not trigger session-expiry recovery), `MessageNotFound` (404 on a
channel message the provider or backend already deleted),
`ChannelEditUnsupported` (404 because the backend never implemented the
`PATCH` edit route), `BackendUnavailable` (no transport installed).
`flatten_authed_error` maps `Unauthorized` onto the `SESSION_EXPIRED`
JSON-RPC sentinel so the dispatcher classifies it as session expiry instead of
reporting it to Sentry, `ApiKeyRejected` onto `API_KEY_REJECTED:`, and
`BackendUnavailable` onto `BACKEND_UNAVAILABLE:`
(`core::observability::BACKEND_UNAVAILABLE_PREFIX`) for the same reasons.

The private `BackendClient::finish_authed_json` is the error classification
chokepoint for every `authed_json` call: it walks the
`reqwest`/`hyper`/`rustls` error source chain (not just the top-level
message) to distinguish a transient transport failure from one worth
reporting, and turns specific status/path combinations into the typed
`BackendApiError` variants above. `IntegrationClient::map_transport_error`
(`integrations/client/errors.rs`) plays the same role for integrations.
Route new backend calls through those helpers instead of matching
`BackendTransportError` by hand.

Session-token lookup, JWT parsing and `Authorization` header formatting now
live in `security::credentials::jwt` (including
`user_id_from_profile_payload`); `decrypt_handoff_blob` (AES-256-GCM decrypt
for integration token handoff) moved to
`crates/openhuman-tinyhumans/src/hosted/oauth/handoff.rs`; the Socket.IO
handshake URL builder moved to `platform::socket::url::websocket_url`, and
its DTOs to `platform::socket::models`.

## `classify.rs`

`is_budget_exhausted_message` — backend/provider budget-exhaustion body
classification shared by inference, agent loop guards, scheduler, web chat
and telemetry.

## Backend request rules (from `AGENTS.md`)

- Add missing backend routes to `vendor/tinyhumans-sdk`, not to
  `crates/openhuman-core/src/backend/`.
- Every TinyHumans backend request must carry a sanitized `x-sdk-name`, now
  stamped by the installed transport's `attribution_headers`:
  `BackendClient`, `IntegrationClient` (except redirected file downloads),
  the agent's Langfuse/OTLP ingestion request, the managed model catalog
  call, and — outside this crate — the host session owner's
  `POST /auth/login-token/consume` / `GET /auth/me`
  (`openhuman_tinyhumans::session`).
- Never add `x-sdk-name` to third-party endpoints, MCP servers, BYOK
  inference endpoints, or presigned storage redirects.
- When auditing hand-built backend requests, grep for
  `bearer_authorization_value` and `header(AUTHORIZATION`.

## Tests

`client_tests.rs` covers `BackendClient::new` base stripping, `authed_json`
401/404 classification into `BackendApiError` (including the route-absence
vs message-gone split for channel edits), `flatten_authed_error`, and
`backend_api_body_shape`. Transient-transport classification is not unit
tested here; it relies on
`core::observability::contains_transient_transport_phrase`. `transport/`
carries its own tests (`transport_tests.rs`, `mod_tests.rs`); `classify.rs`
carries its own (`classify_tests.rs`).

Product-identity attribution and header-shape tests now live with the
transport implementation:
`crates/openhuman-tinyhumans/src/backend/headers_tests.rs` and
`crates/openhuman-tinyhumans/src/transport/transport_tests.rs`.
