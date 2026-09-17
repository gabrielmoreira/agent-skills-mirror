# openhuman-session

Login and backend-session ownership for OpenHuman **hosts**. The core
(`openhuman`) only holds and uses a backend credential — a TinyHumans session
JWT or API key — and never obtains, validates, exchanges or refreshes one. This
crate is where those steps live, shared by the Tauri shell
(`crates/openhuman-app`, over the core's loopback JSON-RPC) and the TUI
(`crates/openhuman-tui`, over an in-process `CoreRuntime`).

No `openhuman` dependency: the shell's own Cargo world must be able to build it,
and core policy must not leak back in through it.

## Pieces

| Module | Role |
| --- | --- |
| `credential` | `Credential` / `CredentialKind` (`session`, `api-key`, `local`), local-session shape detection, JWT `exp` decode, subject-claim and `/auth/me`-payload user-id extraction. |
| `client` | `SessionClient`: `POST /auth/login-token/consume`, `GET /auth/me`, and `validate_for_store` (12 s budget, one retry, transient classification). Sends `x-sdk-name` / `x-core-version` / `x-tauri-version` from `ClientHeaders`. schannel on Windows, rustls elsewhere. |
| `cache` | `CurrentUserCache`: 5 s TTL, stale-while-revalidate, negative cache with a bounded backoff, keyed on `(base_url, secret)`. |
| `link` | `CoreLink` trait (`invoke(method, params)`) plus the `auth.set_credential` / `auth.clear_credential` / `auth.get_state` / `auth.get_session_token` / `config.resolve_api_url` helpers. |
| `manager` | `SessionManager<L: CoreLink>`: `login_with_token`, `store_session_token`, `store_api_key`, `logout`, `current_user`, `state`, and a broadcast of `SessionEvent::{Changed, Expired}`. |
| `identity` | Process-global `peek_user_id()` for synchronous Sentry hooks. |

## Flow

```
login token ──consume──▶ JWT ──validate (/auth/me)──▶ auth.set_credential {token, kind, userId, user}
                                    │ rejected: nothing stored (REJECTED)
                                    │ unreachable + live exp + subject: stored with
                                    │   {pendingBackendValidation:true}, revalidated in the background
current_user ──cache──▶ /auth/me ──rejected──▶ auth.clear_credential + SessionEvent::Expired
```

The core is the store of record; the manager keeps no copy of the secret and
reads it back through the link when it needs to refresh.

## Environment

- `OPENHUMAN_AUTH_ME_TIMEOUT_MS` — store-time validation budget (default 12000; the legacy `OPENHUMAN_AUTH_ME_STORE_TIMEOUT_MS` is still honoured).
- `OPENHUMAN_AUTH_FETCH_TIMEOUT_SECS` — current-user refresh budget (2–12, default 5).

## Tests

`cargo test -p openhuman-session` — in-process axum stubs for the backend and a
fake `CoreLink`; no network, no core.
