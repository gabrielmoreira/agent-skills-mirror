# Medulla

OpenHuman as a Medulla **client**: the HTTP/SSE surface that talks to the
Medulla orchestration backend, the wire vocabulary it speaks, and the
harness-contract types the client and the harness share. Do not confuse this
with `crates/openhuman-core/src/platform/socket/medulla`, which is the opposite
direction — OpenHuman as a Medulla **worker** answering inbound Socket.IO from
a remote operator. A single binary can be both at once; see `mod.rs` for the
full split.

Gated on the `medulla` Cargo feature and tagged
`DomainGroup::Medulla` (`crate::core::all::DomainGroup`) at runtime. The
feature is in the contributor `default` set of `crates/openhuman-core/Cargo.toml`
and forwarded by `crates/openhuman-embed`, but it is not in
`scripts/ci/product-features.txt`, so the shipped desktop app does not compile
this domain. `contract` and `events` are ungated carve-outs: inert serde/std
types with no coupling to their gated siblings, re-exported unconditionally
from `mod.rs` so a feature-off build shares one definition instead of a
drifting copy. Nothing outside `medulla/` currently imports them.

The `medulla_local` engine (a supervised `medulla-serve` child process) has
been removed; its `subconscious.engine = "medulla"` config keys are still
accepted as inert serde (`config::schema::subconscious`) so existing configs
keep booting while that behaviour is re-ported onto this domain.

## Layout

- `mod.rs` — feature gate, the client/worker split, `RESERVED_TOOL_NAMES` (the
  harness's built-in memory/task-tracker tool names a module author must not
  collide with).
- `contract.rs` — ungated. `WorkerContract` and `VerificationEvidence`: the
  advisory boundaries and completion evidence Medulla transports verbatim for
  a delegated worker lane. `camelCase` wire shapes.
- `events/` — ungated. `SessionEvent` (with an `Unknown` fallback so a newer
  backend never drops rows on an older host) and `EventEnvelope`; `types.rs`
  is the data model, `serde_impl.rs` the compact-JSON codec. Presentation
  (transcript rendering, last-message lookup) deliberately stays out — that's
  the host's concern.
- `client/` — `MedullaClient` / `MedullaClientBuilder`, `DEFAULT_BASE_URL`.
  Unwraps the backend's `{success, data}` envelope; API errors surface as
  `ClientError::Api`, preserving `errorCode`. Submodules: `account`,
  `sessions`, `orchestration`, `routing` (`RoutingStrategy`), `program`,
  `feedback` (the public feedback board), `sse` (event streaming — attaches
  the `x-sdk-name` product-identity header itself in its connect path, since
  the SSE handshake authenticates via `?token=` and never reaches the
  client's normal `authed()` helper), and `types`/`error`.
- `chat/` — on-disk chat thread-tree store (`medulla_chat`), migrated from
  medulla-public. Kept separate from `threads/` and `session_db/`: its on-disk
  format is a live user-data contract, and folding it into an existing store
  would mean migrating every existing chat tree.
- `resolve.rs` — resolves a configured `MedullaClient` from ambient config and
  credentials. There is no `[medulla]` config section: the Medulla API and the
  OpenHuman backend are the same deployment, so `api_url` and the existing
  session token already address it.
  `OPENHUMAN_MEDULLA_BASE_URL` overrides the base URL for pointing a dev host
  at a different Medulla deployment.
- `ops.rs` / `schemas.rs` — the `medulla` RPC namespace (wire methods
  `openhuman.medulla_<function>`): `medulla_status`, `medulla_roster`,
  `medulla_create_session`, `medulla_get_session`, `medulla_list_sessions`,
  `medulla_list_messages`, `medulla_send_message`, `medulla_list_events`,
  `medulla_abort`. Handlers delegate straight to `ops`; a `NotConfigured`
  client or a backend `errorCode` becomes a `StructuredRpcError` whose
  `data.kind` a host can branch on. `medulla_status` never touches the network.

## Wiring

- `crates/openhuman-core/src/core/all.rs` registers
  `all_medulla_registered_controllers()` under `DomainGroup::Medulla` behind
  `#[cfg(feature = "medulla")]`; with the feature off the methods are absent
  from `/schema`, not stubbed.
- `crates/openhuman-embed/src/medulla.rs` — the `Core::medulla()` sub-facade.
  It calls the `openhuman.medulla_*` methods through `CoreRuntime` and
  re-exports `medulla::client` types plus `ops::MedullaStatus` rather than
  mirroring them.
- `tests/raw_coverage/medulla_session_e2e.rs` drives the namespace end to end
  against a mock backend. Note the two `EventEnvelope`s: `events::EventEnvelope`
  is the contract type; `medulla_list_events` returns
  `client::types::WireEventEnvelope`, with `event` left as raw JSON.

Outbound dependencies: `api::product::product_identity_header()` for
`x-sdk-name` (AGENTS.md requires it on every `MedullaClient` request,
including the SSE handshake — `client/sse/mod.rs` `StreamState::connect`),
`api::config::effective_backend_api_url` and
`security::credentials::session_support::get_session_token` in `resolve.rs`.
`crates/openhuman-core/src/flows/medulla_bridge.rs` is not a caller: it backs
the `platform::socket::medulla` worker's `WorkflowBridge` with the `flows::`
store and never imports this domain.

## Tests

`mod_tests.rs`, `resolve_tests.rs`, `ops_tests.rs`, `schemas_tests.rs`,
`chat/chat_tests.rs`, `client/tests/`, `client/routing_routing_strategy_tests_tests.rs`,
`client/feedback/feedback_tests.rs`, `events/tests/`.
