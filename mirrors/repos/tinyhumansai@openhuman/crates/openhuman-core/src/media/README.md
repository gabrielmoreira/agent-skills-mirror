# Media

Family root for media-related agent tool contracts. Agent-tools-only: no
controller, store, or bus subscriber is tagged `DomainGroup::Media`; the only
thing the group tags is the `media_*` tool names (`tool_group()` in
`crates/openhuman-core/src/tools/ops.rs`), which is what the runtime
`DomainSet::media` flag filters.

## Members

- [`generation`](generation/mod.rs) — the `media_generate_*` agent tools
  (image/video via GMI, proxied through the TinyHumans backend). Wired: built
  by `build_media_tools()` and registered from
  `crates/openhuman-core/src/tools/ops.rs` under `#[cfg(feature = "media")]`.
  The builder returns no tools when `integrations::build_client()` yields no
  `IntegrationClient` for the config.
- [`image`](image/README.md) — image tool contracts scaffold
  (`image_generation`, `view_image`). Currently unwired (#2997); nothing
  outside `media/image/` references its types.

## Gate

Both children are wholly gated behind the `media` feature
(`#[cfg(feature = "media")] pub mod media;` in
`crates/openhuman-core/src/lib.rs`). `media` is a default feature
(`crates/openhuman-core/Cargo.toml`) and is forwarded explicitly from
`crates/openhuman-app/Cargo.toml` and listed in
`scripts/ci/product-features.txt`, per the feature-forwarding rule in
`AGENTS.md`.

It is a **surface-only** gate: media generation is backend-proxied through the
shared `IntegrationClient`/`reqwest`, and `image` is a dependency-free contract
layer, so disabling the feature sheds no exclusive dependency.

## `generation`

The backend (`/agent-integrations/media-generation/{images,videos,models}` and
`.../requests/{requestId}`) owns provider keys, billing, and the standardized
response envelope (`types.rs`). The tools submit a request, poll
`requests/{id}` every `POLL_INTERVAL` (4 s) until a terminal status or the
per-modality wait budget elapses, download the resulting media into
`generated-media/` under the agent's `action_dir` (`GENERATED_MEDIA_DIR` in
`download.rs`), and return the local artifact paths.

Exported tools (`tools.rs`):

- `MediaGenerateImageTool` — `name() == "media_generate_image"`
- `MediaGenerateVideoTool` — `name() == "media_generate_video"`
- `MediaListModelsTool` — `name() == "media_list_models"`

Tests: `generation/download_tests.rs` (file-extension derivation from
content type, URL, then kind), `generation/tools_tests.rs` (tool schemas and
metadata, empty-prompt rejection without network, and submit/poll/download
flows against a `wiremock` server).

## Related docs

- [`image/README.md`](image/README.md)
- [`gitbooks/features/native-tools/media-generation.md`](../../../../gitbooks/features/native-tools/media-generation.md)
