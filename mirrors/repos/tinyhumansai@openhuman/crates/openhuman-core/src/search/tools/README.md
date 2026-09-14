# Search Tools

Agent-facing `Tool` implementations for every search provider. One file per
provider family; `mod.rs` re-exports the full public surface with
`pub use crate::search::tools::*` consumed from `tools/mod.rs`.

## Providers

| File | Exported tools | `name()` | Transport |
| --- | --- | --- | --- |
| `brave.rs` | `BraveWebSearchTool`, `BraveNewsSearchTool`, `BraveImageSearchTool`, `BraveVideoSearchTool` | `web_search_tool`, `brave_news_search`, `brave_image_search`, `brave_video_search` | Direct to `api.search.brave.com`, `X-Subscription-Token` header |
| `exa.rs` | `ExaSearchTool`, `ExaFindSimilarTool`, `ExaGetContentsTool` | `exa_search` or `web_search_tool` (constructor-selected), `exa_find_similar`, `exa_get_contents` | BYOK, direct to `api.exa.ai`, `x-api-key` header — never proxied |
| `parallel.rs` (+ `parallel/` — `search.rs`, `extract.rs`, `chat.rs`, `research.rs`, `enrich.rs`, `dataset.rs`) | `ParallelSearchTool`, `ParallelExtractTool`, `ParallelChatTool`, `ParallelResearchTool`, `ParallelEnrichTool`, `ParallelDatasetTool` | `parallel_search`, `parallel_extract`, `parallel_chat`, `parallel_research`, `parallel_enrich`, `parallel_dataset` | Backend-proxied via `crate::integrations::IntegrationClient` (`/agent-integrations/parallel/*`) |
| `querit.rs` | `QueritSearchTool` | `querit_search` or `web_search_tool` (constructor-selected) | Direct to `api.querit.ai`, `Authorization: Bearer` header |
| `searxng.rs` | `SearxngSearchTool`, plus `normalize_categories`, `SearxngSearchArgs`, `SearxngSearchResponse`, `MAX_RESULTS` (re-exported as `SEARXNG_MAX_RESULTS`) | `searxng_search` | Direct to a user-configured, self-hosted SearXNG instance (`GET /search?format=json`) |
| `seltz.rs` | `SeltzSearchTool` | `seltz_search` | Direct to `api.seltz.ai`, `x-api-key` header |
| `tavily.rs` (+ `tavily/` — `client.rs`, `search_tool.rs`, `extract_tool.rs`, `types.rs`) | `TavilySearchTool`, `TavilyExtractTool` | `tavily_search` or `web_search_tool` (constructor-selected), `tavily_extract` | BYOK, direct to `api.tavily.com`, `Authorization: Bearer` header — never proxied |
| `tinyfish.rs` | `TinyFishSearchTool`, `TinyFishFetchTool`, `TinyFishAgentRunTool` | `tinyfish_search`, `tinyfish_fetch`, `tinyfish_agent_run` | Backend-proxied via `IntegrationClient` (`/agent-integrations/tinyfish/*`); search/fetch are read-oriented, agent-run drives goal-based browser automation |
| `web_search.rs` | `WebSearchTool` (+ crate-internal `resolve_managed_provider`) | `web_search_tool` | Backend-proxied managed search (`POST /agent-integrations/parallel/search` via `IntegrationClient`); `resolve_managed_provider` labels the response with the provider the backend reports, falling back to `Exa`, for UI attribution. `with_direct_search(Option<SeltzSearchTool>)` can short-circuit the proxy, but only `web_search_tests.rs` uses it |

Several providers construct their primary tool with a `tool_name` field so the
same struct can register under either its own name (e.g. `exa_search`,
`querit_search`, `tavily_search`) or the canonical `web_search_tool` slot when
that engine is the active `search.engine` — see `exa.rs`, `querit.rs`, and
`tavily/search_tool.rs`.

## Registration

Most families are selected by `search::registry::build_search_tools` based on
`Config.search.effective_engine()`, via `search/engines/`
([README](../README.md)). `tinyfish.rs` tools are pushed separately by
`registry.rs` (`build_backend_search_tools`) on top of whichever engine is
active, provided the engine is not `disabled`, an `IntegrationClient` can be
built (user signed in), and `config.integrations.tinyfish.is_active()`.

`SearxngSearchTool` and `SeltzSearchTool` are not reachable through the engine
registry at all — they are constructed per call by the `tools.searxng_search`
(`handle_searxng_search`) and `tools.seltz_search` (`handle_seltz_search`)
RPC handlers, both in `crates/openhuman-core/src/tools/schemas/web_search.rs`.
Those handlers take the query and `max_results` from the RPC
params but read endpoint, key, timeout, and the `enabled` gate from the
top-level `config.searxng` / `config.seltz` sections, not from
`Config.search`. `SEARXNG_MAX_RESULTS` and `normalize_categories` are also
reused by `mcp/server/tools/` to keep the MCP SearXNG surface consistent with
the RPC handler.

## Tests

Each provider has a sibling `*_tests.rs` (`brave_tests.rs`, `exa_tests.rs`,
etc.) wired in via `#[cfg(test)] #[path = "<provider>_tests.rs"] mod tests;`.
No test hits the network: `web_search_tests.rs` starts an in-process axum
router (`start_mock_backend`) and points an `IntegrationClient` at it; the
other backend-proxied families build their client against an unreachable
`http://test` base and only exercise schema and response parsing.
