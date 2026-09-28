# Search Domain

Host policy over the TinySearch module. Provider implementations, tool
schemas, and role dispatch live in `vendor/tinysearch`; this domain owns what
OpenHuman decides about them.

## Model

- **Providers** (`exa`, `gemini`, `tinyfish`, `parallel`, `brave`, `querit`, `tavily`,
  `seltz`, `searxng`; `gemini_deep_research` rides on the Gemini key). Each
  has `enabled` and a route: `managed` (TinyHumans backend, billed to the
  session or API key; supported by `exa`, `gemini`, `tinyfish`) or `direct`
  (the user's own key, or a SearXNG URL).
- **Roles**: `search` → `web_search_tool`, `answer` → `web_answer_tool`
  (grounded answer with citations; `depth: "deep"` uses Gemini Deep Research
  when a key is set), `contents` → `web_contents_tool`. Each role has an
  ordered provider list; the first usable provider serves the call and the
  module falls back on balance, rate-limit and availability errors.
- Config lives in `[search]` (`config/schema/tools/search.rs`): `providers`,
  `roles`, `presentation` (`roles` by default; `all_tools`, `router`,
  `one_provider`). Files from the single-engine era are migrated on load
  (`search_migrate.rs`); Parallel is kept as a direct-only (own key)
  provider, and a keyless managed-Parallel selection is dropped.

## Files

- `providers.rs` — resolves every provider's state (`enabled`, route,
  `managed_available`, `key_configured`, `usable`, status) and each role's
  effective order. Used by the settings RPC (`config/ops/search.rs`), the MCP
  catalog, the RPC precheck, and `modules::search::module_config`.
- `render.rs` — turns an `ExecuteToolResponse` into the model-facing text
  (`… (via Exa)` heading, answer, `Sources:`), optional markdown, and the
  host-only `{"kind":"web_search", …}` metadata the chat UI renders.
- `tools.rs` (`modules` feature) — `TinySearchTool`, the `tinytools::Tool`
  bridge; `build_search_tools` registers one per declared spec. Calls re-read
  the live config and go through `modules::search::execute_tool`; classified
  module errors (`tinysearch.<code>:`) become actionable messages.
- `bus.rs` (`modules` feature) — `search::credential_refresh` refreshes a
  loaded module on `DomainEvent::CredentialChanged`.

## Wiring

- `tools/ops.rs` calls `crate::search::build_search_tools(root_config)`.
- RPC: `tools_web_search`, `tools_web_answer`, `tools_web_contents`, and the
  provider-pinned `tools_searxng_search` (`tools/schemas/web_search.rs`).
- MCP: `web_search`, `web_answer`, `searxng_search`, listed only when a
  provider can serve them (`mcp/server/tools/specs.rs`).
- Resumed threads keep their recorded search role tools even when no provider
  is usable now (`agent/session_host/recorded_tools.rs`).

See [`gitbooks/features/native-tools/web-search.md`](../../../../gitbooks/features/native-tools/web-search.md)
for the user-facing description.
