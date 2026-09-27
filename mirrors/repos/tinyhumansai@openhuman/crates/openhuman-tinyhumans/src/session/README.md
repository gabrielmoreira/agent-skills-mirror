# session

TinyHumans login and backend-session ownership for OpenHuman hosts. The core
(`openhuman`) only holds and uses a backend credential, a session JWT or a
TinyHumans API key, and never obtains, validates, exchanges or refreshes one
itself. Everything that talks to the backend's auth endpoints lives here
instead, shared by every host that drives a user login: the Tauri shell
(over the core's HTTP JSON-RPC) and the TUI (over an in-process
`CoreRuntime`). This module absorbed the standalone `openhuman-session`
crate; see `AGENTS.md`'s "Backend API" section for the boundary it keeps.

## Contents

- `client.rs`: `SessionClient`: the actual backend calls, login-token
  exchange and `GET /auth/me`, plus `ClientHeaders`. Carries the store-time
  timeout, retry and transient-failure policy. Errors are
  `SessionClientError` / `FetchMeError`.
- `cache.rs`: `CurrentUserCache` / `CachedUser`: the last `/auth/me` answer,
  served fresh or stale-while-revalidate, with bounded backoff while the
  backend is unreachable.
- `link.rs`: `CoreLink` / `CoreAuthState`: how a resolved credential is
  pushed into whichever core the host owns, through `auth.set_credential` /
  `auth.clear_credential` / `auth.get_state`. This is the only door into a
  core from this module.
- `manager.rs`: `SessionManager`, the host-facing orchestration over the
  three pieces above: login, store, logout, current user, state, and change
  events (`SessionEvent`, `SessionState`, `SessionError`).
- `credential.rs`: `Credential` / `CredentialKind` and the JWT helpers
  (`decode_jwt_exp`, `jwt_is_live`, `user_id_from_jwt_claims`,
  `user_id_from_profile_payload`).
- `identity.rs`: process-global identity state read by synchronous Sentry
  hooks that cannot await a cache lookup.
- `test_support.rs`: fixtures shared by this module's own tests.

## What this module must not do

It may use core utilities (`util::tls`, `api::product`,
`openhuman_rpc::unwrap_rpc`) but must never call `openhuman_core::security::*`
directly, and must never dispatch into a core except through `CoreLink`. The
host owns the login; the core only takes the resulting credential.

## Where to look next

- `AGENTS.md`, "Tool, harness, and runtime boundaries" and "Backend API":
  why login ownership sits here and not in the core.
- [`gitbooks/developing/tinyhumans-api-key.md`](../../../../gitbooks/developing/tinyhumans-api-key.md):
  the API-key alternative to a session login for library and headless
  hosts, which does not go through this module.
- [`../transport/README.md`](../transport/README.md): the transport a
  resolved credential ultimately authenticates.
