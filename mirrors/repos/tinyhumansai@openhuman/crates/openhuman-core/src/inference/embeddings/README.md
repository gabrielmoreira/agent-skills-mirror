# embeddings

Host policy and RPC surface for vector embeddings. Concrete OpenAI-compatible,
Cohere, Voyage, Ollama, cloud-transport, retry, and rate-limit implementations
live in `tinyinference::embeddings` (vendored at
`vendor/tinyagents/vendor/tinyinference`); this domain selects and adapts
those models for OpenHuman.

## Host-owned responsibilities

- `factory.rs`: provider slug/model/dimension selection and construction of
  `tinyinference` embedding models. Also owns `MODELS_SUPPORTING_DIMENSIONS`,
  the list of models allowed to request a non-default dimension.
- `provider_trait.rs`: re-exports the `EmbeddingProvider` contract and
  `format_embedding_signature` from `tinymemory_api::host`, and defines
  `TinyAgentsEmbeddingProvider`, the one adapter from a `tinyinference`
  `EmbeddingModel` to that contract.
- `cloud_adapter.rs` (module `cloud`): `OpenHumanCloudEmbedding`, which wraps
  `tinyinference`'s `CloudEmbeddingModel` with OpenHuman session-token
  resolution, egress disclosure, and local-only privacy enforcement.
- `catalog.rs`, `rpc.rs`, `schemas.rs`: Settings catalog, credentials, JSON-RPC,
  connection tests, and re-embed/wipe policy.
- `noop.rs`: re-export of `tinymemory_api::host::NoopEmbedding` so the host and
  the memory module share one type when embeddings are switched off.
- `rate_limit` and `retry_after` (in `mod.rs`): thin re-exports of the
  `tinyinference` limiter and 429 backoff helpers under their older names.

Provider HTTP behavior and its tests belong in `tinyinference`. Do not add new
per-provider clients here.

The canonical embedding-space signature is
`provider={name};model={model};dims={dims}`. Configuration-derived and live
provider signatures must remain byte-identical or stored vectors split into
incompatible spaces.

The separately compiled TinyMemory module reaches this factory through the
`EmbeddingHost` bus interface in `modules/memory_host.rs`, whose `embed`
method resolves the API key via `resolve_api_key` and calls
`create_embedding_provider_with_config` on every request. The module's tree
stores fixed 1024-dimension vectors (`EMBEDDING_DIM` in tinymemory-core's
`tree::score::embed`), so `modules::ops` hands it
`MODELS_SUPPORTING_DIMENSIONS` at load time and the module omits the
`dimensions` parameter for any model not on that list.

## Wiring

- Controllers are registered from `all_embeddings_registered_controllers()`,
  pushed under `DomainGroup::Inference` in `core/all.rs`.
- `schemas.rs` declares the `embeddings` namespace functions (`get_settings`,
  `update_settings`, `set_api_key`, `clear_api_key`, `embed`,
  `test_connection`) and dispatches to the handlers in `rpc.rs`
  (`rpc/settings.rs`, `rpc/api_keys.rs`, `rpc/embed.rs`, `rpc/probe.rs`, `rpc/served_models.rs`).
- See `mod.rs` for the current provider set (Managed default via the backend's
  `POST /openai/v1/embeddings`, Voyage, OpenAI, Cohere, Ollama, Custom, Noop)
  and `tinyinference::embeddings` for their concrete implementations.
