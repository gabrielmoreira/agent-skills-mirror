---
description: >-
  What a single TinyHumans API key unlocks, how it is resolved, and which
  seams read it.
icon: key
---

# One TinyHumans API key

One TinyHumans credential unlocks every managed backend surface: chat
inference over the OpenRouter model catalogue, web search, embeddings, media
generation, integrations, voice, and the Jev ranker. There's no separate key
per service. The desktop app gets this credential through sign-in; a library
host or a headless process supplies it directly.

## How to get one

Managed inference, search, and the rest of the backend surface all sit behind
one TinyHumans account. Sign in through the desktop app to get a session
credential, or generate an API key (`th_...`) for library and headless use.

## Using it

**Desktop app**: sign in with a TinyHumans account. The app stores a session
credential in the OS-backed auth-profile store and the core resolves it the
same way it resolves an API key, through `security::credentials::api_key` and
`session_support::resolve_backend_credential`.

**Library**: pass the key to `RuntimeBuilder` and it boots connected:

```rust
use openhuman_tinyhumans::{embed::Workspace, RuntimeBuilder};

let runtime = RuntimeBuilder::new()
    .workspace(Workspace::Ephemeral)
    .api_key("th_...")
    .build()
    .await?;
```

`openhuman_tinyhumans::RuntimeBuilder` mirrors `openhuman_embed::RuntimeBuilder`
method for method, then installs the SDK-backed transport and binds it to the
runtime on `build()`.

**Headless**: set `OPENHUMAN_BACKEND_API_KEY` before the core boots. The boot
sequence (`crates/openhuman-core/src/security/credentials/ops/boot_env.rs`)
installs it on a fresh credential store and never overwrites one that's
already there.

## Where it's stored and how it's sent

The key lives in the same auth-profile store as an app session, under its own
provider id (`api-key`), never in `config.toml` and never logged. It's the
only credential a library embedder holds: no login-token exchange, no session
JWT, no `/auth/me` round trip.

Two wire forms, chosen by endpoint:

- **Managed inference** (`{api_url}/openai/v1`): `Authorization: Bearer
  <key>`. `OpenHumanBackendModel::resolve_bearer` prefers the stored API key
  over an app session when both exist.
- **Backend REST** (`BackendClient`, `IntegrationClient`):
  `x-api-key: <key>`.

`crates/openhuman-core/src/security/credentials/api_key.rs` owns storage and
retrieval (`store_api_key`, `get_api_key`, `has_api_key`, `clear_api_key`);
`session_support::BackendCredential` is what resolves either credential form
into the right header at request time.

## BYOK stays available

The API key covers the managed path. Every workload can still be pointed at
your own provider instead, chat and reasoning at a BYOK LLM slug, embeddings
at Voyage or OpenAI or Cohere directly, search at Brave or Exa or Tavily
directly. See [Pluggable engines](engines.md) for the full list and the
config key for each. Running everything BYOK does not require a TinyHumans
key at all; running anything through the managed backend does.
