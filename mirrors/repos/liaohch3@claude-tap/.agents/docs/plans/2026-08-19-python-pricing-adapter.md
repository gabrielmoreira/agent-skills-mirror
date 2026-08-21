---
status: active
---

# TODO: Move cost analysis into a Python pricing adapter

**Date:** 2026-08-19
**Priority:** High
**Status:** In progress

## Background

PR #436 computed per-turn cost in JavaScript with a hand-maintained price table.
The repository owner rejected that ownership split on 2026-08-19 and asked for:

1. a unified pricing adapter in Python,
2. `cost`, `uncached_cost` and `saved` computed per entry in Python,
3. the price source and version written into viewer metadata,
4. JavaScript reduced to display and summation of precomputed values,
5. no duplicated price table or cost math in JavaScript,
6. tests for long-context pricing and embedded cache token formats.

The hand-maintained table also carried two defects the adapter has to fix: the
Sonnet 4 long-context tier (`>200K` input is billed at 2x) was missing, and the
lazy viewer billed cached tokens twice for OpenAI-shaped usage.

Price source: LiteLLM `model_prices_and_context_window.json`.

## Design

### Vendored price data

The upstream file is 1.76 MB / 3055 entries, most of it irrelevant (embeddings,
rerankers, image models, providers claude-tap never proxies). A refresh script
prunes it to chat models from the providers claude-tap can capture, keeping only
the cost, tier and context fields. That lands near 200 KB, comparable to the
existing `viewer_i18n.json` + `viewer_assets/` package data, and keeps the viewer
working offline with no new runtime dependency.

- `claude_tap/model_prices.json` — pruned dataset plus a `__meta__` block
  recording source URL, upstream commit and fetch date.
- `scripts/refresh_model_prices.py` — regenerates it; the only way it changes.

### Cache-embedding provenance

`normalize_usage` derives `cache_read_input_tokens` from four different shapes
without recording which one it saw. Anthropic reports cache reads as a bucket
*separate* from `input_tokens`; OpenAI-shaped gateways report them *inside* it.
Without that flag the cached tokens are billed once at the full input rate and
again at the cache-read rate. `normalize_usage` will set
`cache_read_in_input: bool` so the adapter can subtract before pricing. This is
the root-cause fix for the double-billing.

### WebSocket records

`splitWebSocketResponseEvents` splits one raw record into one entry per
`response.created`…`response.completed` pair, and JS suffixes the id
(`base:2`). Python currently reads usage from the *last* `response.completed`
only, so a multi-response WS record already under-reports tokens. The cost
index therefore groups WS events the same way Python-side and emits a key per
group, so every client entry id resolves.

### Delivery to the viewer

Two shapes, because the four generation paths differ in what they embed:

- lazy/metadata path: cost fields go directly on each metadata record.
- compact-bundle and records paths: a `EMBEDDED_COST_INDEX` keyed by
  `request_id`, since those paths embed raw records and build entries in JS.

Both paths also get `EMBEDDED_PRICING_META` (source, version, as-of date).
Drag-and-drop traces never reach Python, so JS shows the tokens it always did
and omits the cost stats rather than guessing.

## TODO

- [x] `claude_tap/pricing.py` adapter with tier + cache-TTL resolution
- [x] Vendored pruned dataset and refresh script
- [x] `cache_read_in_input` provenance in `normalize_usage`
- [x] Per-entry `cost` / `uncached_cost` / `saved` in viewer metadata
- [x] `EMBEDDED_COST_INDEX` + `EMBEDDED_PRICING_META` injection
- [x] JS display-and-sum only, no price table
- [x] Tests: long-context tier, cache TTL, every embedded cache shape
- [x] Real-trace screenshot evidence
