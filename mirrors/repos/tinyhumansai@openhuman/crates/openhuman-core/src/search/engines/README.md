# Search engines

One file per search engine, each picked by the `search.engine` config
setting. This is where OpenHuman's pluggable web search model lives: a
managed engine that proxies through the TinyHumans backend, plus a set of
BYOK engines that call a provider's API directly with the user's own key.

## Files

- `mod.rs`: declares the seven engine modules and nothing else.
- `managed.rs`: the default. Builds a single `WebSearchTool` that posts to
  the backend's `/agent-integrations/parallel/search`.
- `parallel.rs`: registers the full Parallel family (`ParallelSearchTool`,
  `ParallelExtractTool`, `ParallelChatTool`, `ParallelResearchTool`,
  `ParallelEnrichTool`, `ParallelDatasetTool`) plus `WebSearchTool`, all
  backend-proxied. Falls back to a client-less `WebSearchTool` if no backend
  client can be built.
- `brave.rs`: registers `BraveWebSearchTool`, `BraveNewsSearchTool`,
  `BraveImageSearchTool`, and `BraveVideoSearchTool` from
  `root_config.search.brave.api_key`. BYOK, direct to Brave's API.
- `querit.rs`: registers `QueritSearchTool` under both the `web_search_tool`
  and `querit_search` names, from `root_config.search.querit.api_key`. BYOK,
  direct to Querit's API.
- `exa.rs`: registers `ExaSearchTool` (as `web_search_tool` and as
  `exa_search`), `ExaFindSimilarTool`, and `ExaGetContentsTool`, from
  `root_config.search.exa.api_key`. The module doc comment says every tool
  here calls `https://api.exa.ai` directly and nothing routes through the
  managed backend.
- `tavily.rs`: registers `TavilySearchTool` (as `web_search_tool` and as
  `tavily_search`) and `TavilyExtractTool`, from
  `root_config.search.tavily.api_key`. Same BYOK, direct-to-`api.tavily.com`
  shape as `exa.rs`.
- `disabled.rs`: returns an empty tool vector and logs that search is off.

## Key types

Every file exports one function with the same signature:

```rust
pub(crate) fn build(root_config: &Config, params: SearchToolParams) -> Vec<Box<dyn Tool>>
```

`SearchToolParams` (`registry.rs`) is a small `Copy` struct carrying
`max_results` and `timeout_secs`, already clamped by
`registry::build_search_tools` before any engine sees them. `engines` is
declared `pub(crate) mod engines;` in `search/mod.rs`, so nothing outside
the search domain names these modules directly.

## How it fits

`registry::build_search_tools` reads `Config.search.effective_engine()` and
matches it to exactly one `build` function above. If the resolved engine is
not `Disabled`, the registry then layers the TinyFish tools on top
(`build_backend_search_tools`), independent of which engine was chosen, as
long as an `IntegrationClient` can be built and
`config.integrations.tinyfish.is_active()`. TinyFish therefore has no file
here; it is not one of the selectable engines, just an add-on.

SearXNG and Seltz also have no file here. Both bypass engine selection
entirely and are constructed per RPC call from `config.searxng` /
`config.seltz`, not from `Config.search.engine`. See
[`../README.md`](../README.md) for that wiring and
[`../tools/README.md`](../tools/README.md) for the full provider-to-tool
table, including SearXNG, Seltz, and TinyFish.

A BYOK engine configured with no key still resolves to the managed
`WebSearchTool` rather than registering nothing, so setting `search.engine`
to `exa` or `tavily` before a key is saved behaves the same as `managed`.

## Where next

- `search/registry.rs` for the dispatch and the TinyFish add-on logic.
- `search/tools/` for the `Tool` implementations these `build` functions
  construct.
- `crates/openhuman-core/src/config/schema/` for the `SearchEngine` enum and
  the per-provider config sections (`search.brave`, `search.exa`, and so on)
  these files read.
- `gitbooks/developing/engines.md` for how web search fits alongside the
  other pluggable engines (LLM providers, embeddings, memory).
