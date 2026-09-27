# embedding_host

Turns text into vectors for semantic memory search, and lets the provider
that does it be swapped by config rather than by code change. This is the
embeddings half of OpenHuman's pluggable-engine story (see
[gitbooks/developing/engines.md](../../../../../gitbooks/developing/engines.md)):
the same pattern used for chat model providers in [`../provider`](../provider/README.md),
applied to embeddings.

## Providers

Declared in `mod.rs` and resolved by `factory.rs`:

- **Managed** (default): routed through the OpenHuman backend's
  `POST /openai/v1/embeddings` (Voyage-backed). Works on a fresh install with
  no local Ollama daemon required.
- **Voyage**: direct Voyage AI API with the user's own key.
- **OpenAI**: cloud embeddings via the OpenAI API.
- **Cohere**: Cohere's embed API with the user's own key.
- **Ollama**: a local Ollama server, for offline-only setups.
- **Custom**: any OpenAI-compatible endpoint.
- **Noop**: a fallback that produces no vectors, used when nothing else can
  be built, so memory degrades to keyword-only search instead of failing.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Module docs and re-exports. Declares the provider list above. |
| `provider_trait.rs` | Re-exports `EmbeddingProvider` and `format_embedding_signature` from `tinymemory_api::host`, and defines `TinyInferenceEmbeddingProvider`, the adapter from a TinyInference `EmbeddingModel` to the memory host's trait. |
| `factory.rs` | OpenHuman's binding onto TinyInference's embedding factory: `create_embedding_provider_with_credentials`, `create_embedding_provider_with_config`, and `default_embedding_provider_with_config` (falls back to a `Noop` model if the configured provider fails to build). |
| `cloud_adapter.rs` | `OpenHumanCloudEmbeddingModel`: the managed-provider transport, with OpenHuman's own bearer-token and egress-guard wiring around the crate-owned `CloudEmbeddingModel`. |
| `rpc.rs` + `rpc/` (`api_keys.rs`, `embed.rs`, `settings.rs`) | The `embeddings` RPC handlers: get/update settings, set/clear API key, embed text, test a connection. |
| `schemas.rs` | Controller schemas and thin handlers for the `embeddings` RPC namespace, registered as `all_embeddings_controller_schemas` / `all_embeddings_registered_controllers`. |

## Why the trait lives here, not in the engine

`EmbeddingProvider` is defined in `tinymemory_api::host` and only re-exported
by `provider_trait.rs`, because the extracted memory subsystem takes an
`Arc<dyn EmbeddingProvider>` from this host and both sides need to name the
same type. `TinyInferenceEmbeddingProvider` is the adapter that wraps a
TinyInference `EmbeddingModel` (what `factory.rs` and `cloud_adapter.rs`
build) to satisfy that trait. The signature format itself is not
re-derived here: `format_embedding_signature` stays the contract's, so a
vector written before this module existed and one written after land in the
same embedding space.

## How it fits

`memory::api` and the wider memory subsystem call through
`default_embedding_provider_with_config` (or `provider_from_config` in
`rpc.rs`, used by domains like `codegraph` that need a provider without a
JSON-RPC round trip) to get a working embedder without caring which provider
is configured. The RPC surface lets the frontend read and change that
configuration, store or clear provider API keys, and run a one-off
connection test.

## Where to look next

See [`../provider`](../provider/README.md) for the equivalent story on the
chat-model side, and [`../README.md`](../README.md) for how this fits into
the wider `inference` domain.
