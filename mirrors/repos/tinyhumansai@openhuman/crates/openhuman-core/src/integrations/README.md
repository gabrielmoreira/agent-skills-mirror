# integrations

Shared HTTP client, backend-proxied agent tools, and the Composio and
task-source sub-domains for third-party providers.

Search provider implementations live under `crates/openhuman-core/src/search/`. This module
keeps the backend-proxied integration client, the connector (Composio) and
task-source sub-domains, and the remaining non-search tool families.

## Responsibilities

- Provide `IntegrationClient`, a shared `reqwest` HTTP client for backend-proxied integrations: backend URL sanitization, bearer auth, `{success,data,error}` envelope parsing, bounded error-detail extraction, and pricing cache.
- Build the client from root config (`build_client`), resolving backend URL and app-session JWT; return `None` when the user is not signed in.
- Fetch per-integration pricing from `/agent-integrations/pricing`, with a Composio direct-mode short-circuit (`pricing_for_config`).
- Implement and export non-search, non-connector tools: Google Places, stock/market data, and Twilio.
- Own the [`composio`](composio/README.md) connector sub-domain and the [`task_sources`](task_sources/README.md) sub-domain as child modules.
- Own the [`file_storage`](file_storage/README.md) managed cloud file-storage tool family as a child module.
- Classify transport and user-state failures through `core::observability::report_error_or_expected`.

Every request `IntegrationClient` sends through the `tinyhumans-sdk` client
carries the sanitized `x-sdk-name` product identity
(`crate::api::product::product_identity_headers()` applied via
`with_default_headers` in `client/construct.rs`; asserted by
`integration_requests_carry_the_default_product_identity` in
`client_error_propagation_tests.rs`). The one deliberate exception, per AGENTS.md
"Backend API", is `get_bytes`: it uses a separate untagged `download_client`
because the file-storage download route answers a 302 to a presigned S3 URL
and reqwest keeps custom headers across the cross-host redirect.

## Members

| Path | Role |
| --- | --- |
| `client.rs` + `client/` (`construct.rs`, `requests.rs`, `download.rs`, `pricing.rs`, `errors.rs`) | `IntegrationClient`: `post`/`get`/`get_bytes`/`patch`/`delete`/`upload_multipart`/`pricing`, backend URL sanitization, and client construction. |
| `types.rs` | Shared serde types for backend envelopes and pricing. |
| `tools.rs` + `tools/` | Non-search, non-connector agent tools: `tools/google_places.rs` (search + details), `tools/stock_prices.rs` (quote, exchange rate, options, crypto series, commodity via backend financial APIs), `tools/twilio.rs` (outbound calls). `tools.rs` only declares and re-exports them. |
| [`file_storage/`](file_storage/README.md) | Managed cloud file-storage agent tools (`Storage*Tool`), backed by the backend's S3-based `file_storage` provider. |
| [`composio/`](composio/README.md) | Composio connector integration: catalogs, connections, triggers, direct-auth fallback, and the `tinyconnectors` module bridge. |
| [`task_sources/`](task_sources/README.md) | Normalizes external task feeds (via the Composio providers) into agent-facing list/fetch/filter tools. |
| `test_support.rs` + `test_support_backend.rs` | In-process axum fake of the integration backend (`spawn_fake_integration_backend`, records every request). Not a `mod` of this module: `crates/openhuman-core/src/tools/ops_tests.rs` pulls it in with `#[path = "../integrations/test_support.rs"]` for its split test modules (`ops_tests_capability_gating_tests.rs`, `ops_tests_default_registry_tests.rs`, `ops_tests_domain_family_tests.rs`, `ops_tests_execution_and_serde_tests.rs`). |

## Search Boundary

Search-owned tools are in `crates/openhuman-core/src/search/tools/`, including Parallel,
Brave, Querit, SearXNG, Seltz, TinyFish, and the managed `WebSearchTool`.
The search registry in `crates/openhuman-core/src/search/registry.rs` decides which search
tool surface is active for `search.engine`.

## Public Surface

From `crates/openhuman-core/src/integrations/mod.rs`:

- `IntegrationClient`
- `build_client(&Config) -> Option<Arc<IntegrationClient>>`
- `pricing_for_config(&IntegrationClient, &Config) -> IntegrationPricing`
- Types: `BackendResponse<T>`, `IntegrationPricing`, `IntegrationPricingEntry`, `PricingIntegrations`, `ToolScope`
- Non-search, non-connector tool structs via `tools.rs`

## Agent Tools

From `tools.rs`: `GooglePlacesDetailsTool`, `GooglePlacesSearchTool`,
`StockCommodityTool`, `StockCryptoSeriesTool`, `StockExchangeRateTool`,
`StockOptionsTool`, `StockQuoteTool`, `TwilioCallTool`. These are constructed
and registered by `crates/openhuman-core/src/tools/ops.rs`, gated by
`config.integrations.<provider>.is_active()`.

The `file_storage/` tools (see [its README](file_storage/README.md)) are
built separately via `build_file_storage_tools` (also called from
`tools/ops.rs`, around line 905) because they need `action_dir` and a
`SecurityPolicy` rather than a provider config flag.

Composio connector tools and task-source tools live in and are documented by
their own sub-domains; all three tool families are re-exported into the
global agent tool registry through `tools/mod.rs`:

```rust
pub use crate::integrations::composio::tools::*;
pub use crate::integrations::task_sources::tools::*;
pub use crate::integrations::tools::*;
```

Search tools, including TinyFish, are governed by `crates/openhuman-core/src/search/`.

## Notes

- Backend-proxied tools never see provider API keys; the backend holds them.
- Direct search APIs such as SearXNG, Brave, Querit, and Seltz are intentionally
  outside this module in `crates/openhuman-core/src/search/`.
- `IntegrationClient::new` re-runs backend URL sanitization as defense in depth.
- `IntegrationClient::pricing()` returns empty pricing on network error so tool
  registration does not fail.
</content>
