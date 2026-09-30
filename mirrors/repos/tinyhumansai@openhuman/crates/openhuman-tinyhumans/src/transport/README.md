# transport

The SDK-backed `BackendTransport` implementation: every hosted-backend
request the core makes rides the vendored `tinyhumans-sdk`'s HTTP primitive,
which owns route policy (its unexposed-route registry) and the credential
header shapes the backend expects.

## Contents

- `mod.rs`: `SdkBackendTransport`. It holds one `reqwest::Client` per
  `TransportProfile` (`Api`, `Integrations`), each built from the core's
  `api::headers::build_backend_client` so TLS, timeouts and the attribution
  headers (`x-core-version`, `x-tauri-version`, `x-sdk-name`) match exactly
  what the core specifies. `send_json` and `send_multipart` build a
  `TinyHumansClient` per request, attach the resolved credential
  (`BackendCredential::Session` as a bearer token, `BackendCredential::ApiKey`
  as `x-api-key`), and forward to the SDK's `raw()` client. `name()` returns
  `"tinyhumans-sdk"`.
- `error.rs`: `map_sdk_error`, translating `tinyhumans_sdk::Error` for a
  given method and path into the core's `BackendTransportError` variants. A
  `404` on `…/channels/<p>/messages/<id>` becomes `ChannelMessageRouteMissing`
  (a `PATCH` with no matching route: the backend has no edit route, #5230) or
  `ChannelMessageNotFound` (the message is gone), using
  `tinyhumans_sdk::classify`. The core maps them onto its typed
  `BackendApiError` recovery states and never reads the body itself.
  `channel_404_tests.rs` pins this against a mock backend.

## Installing it

`SdkBackendTransport::shared()` returns an `Arc<dyn BackendTransport>` ready
for `openhuman_core::backend::install_backend_transport`.
`openhuman_tinyhumans::install()` does this for every host that boots a core
connected to TinyHumans (the Tauri shell, the TUI, the CLI); a core with no
transport installed still runs agents, memory, tools and RPC, and answers
any backend-touching call with `BackendApiError::BackendUnavailable` /
`BACKEND_UNAVAILABLE:` instead.

## Why this lives outside the core

The core does not depend on `tinyhumans-sdk`; the port it programs against
(`BackendTransport`, `BackendRequest`, `BackendTransportError`) lives in
`crates/openhuman-core/src/api/transport/`. This crate is the only one
allowed to depend on the SDK (`cargo tree -p openhuman -i tinyhumans-sdk`
must stay empty). A missing backend route belongs in the vendored SDK's
route registry, named from the core; this transport should never grow a
route implementation of its own.

## Where to look next

- `AGENTS.md`, "Backend API": the full port/adapter boundary and the header
  rules every authenticated request must follow.
- [`../session/README.md`](../session/README.md): where the credential this
  transport attaches comes from.
- [`../hosted/README.md`](../hosted/README.md): the RPC proxy domains built
  on top of this transport.
