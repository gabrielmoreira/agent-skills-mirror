# src/tools/smartfetch/

## Responsibility

- Implement the built-in `webfetch` tool: fetch remote documents, enforce redirect/origin policy, probe `llms.txt` when useful, and return normalized text/markdown/html output (`tool.ts`, `network.ts`).
- Handle content shaping around that fetch step: HTML extraction, conditional status-header rendering, heading cleanup, cache keying, and binary persistence (`utils.ts`, `cache.ts`, `binary.ts`).

## Design Patterns and Decisions

- **One orchestration entrypoint:** `createWebfetchTool` in `tool.ts` owns permission prompts, cache lookup, llms.txt probing, binary-vs-text branching, and the conditional status header.
- **Transport/policy split from rendering:** `network.ts` focuses on URL normalization, same-origin credential-free redirects, charset/body decoding, header extraction, and llms.txt probing, while `utils.ts` focuses on turning fetched content into cleaned text/markdown/html plus frontmatter and user-facing messages.
- **Cache keyed by fetch shape:** `cache.ts` keys pages by URL and request options (`format`, `save_binary`). Pages negotiate different `Accept` headers; llms.txt uses its own text `Accept` and a format-independent key, shared across output formats.
- **Minimal model-visible surface:** the text body carries only decision-changing keys (`title`, `final_url` when it differs, `truncated`, non-empty `quality_signals`); fetch observability goes to `ctx.metadata` for the UI channel. `format: html` returns the raw page with no header.
- **Graceful degradation:** missing/invalid `llms.txt`, blocked redirects, and metadata-only binary responses all return a usable result instead of throwing away the fetched content.
- **Warning-scoped JSDOM construction:** any new JSDOM construction or css-tree trigger point must be wrapped in `withCssTreeWarningsSuppressed` (see `utils.ts`) so css-tree lexer warnings never leak into the host process stderr.

## Data & Control Flow

1. `createWebfetchTool` normalizes the requested URL, derives permission patterns, asks for `webfetch` permission, and computes the cache key (`tool.ts`, `network.ts`, `cache.ts`).

2. For docs-like domains, `probeLlmsText` tries `/llms-full.txt` then `/llms.txt`, following only permitted redirects and rejecting HTML/login-wall responses (`network.ts`).

3. When the tool falls back to the page itself, `fetchWithUpgradeFallback` handles HTTPS upgrade fallback and redirect enforcement; the tool then detects binaries and reads bodies within limits. Stale pages send stored validators; a `304` at the same final URL refreshes the cached body, while a changed redirect target requires an unconditional refetch. Stale llms.txt is probed again (`network.ts`, `cache.ts`, `tool.ts`).

4. Text/HTML payloads are decoded and normalized through `extractFromHtml` (Readability runs for `markdown`/`text`; `html` keeps the raw page), `cleanFetchedMarkdown`, and `frontmatter`; binary payloads persist via `saveBinary` or degrade to a kind+size guidance line (`utils.ts`, `binary.ts`, `tool.ts`).

## Integration Points

- `src/index.ts` registers the tool under the public name `webfetch`, so agents can call it alongside council and AST-grep tools.
- `src/tools/smartfetch/index.ts` exports only the tool factory; internal types and description stay in their respective modules.
- `cache.ts`, `network.ts`, and `utils.ts` are intentionally reusable seams for tests: cache behavior, redirect policy, llms probing, heading extraction, and render/metadata helpers can be verified without hitting the full tool entrypoint.
