# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

World Intelligence MCP Server: 139 tools across 30+ domains providing real-time global intelligence from free public APIs. Serves four interfaces: MCP stdio (for Claude Code/Cursor), a live Starlette dashboard with SSE, a Click CLI with Rich output, and a collector daemon for 24/7 vector store population. Python 3.11+, built with hatchling.

## Commands

```bash
# Install
pip install -e ".[dev,dashboard]"

# Run MCP server (stdio mode)
world-intel-mcp

# Run tests (pytest-asyncio, auto mode)
pytest
pytest --cov=world_intel_mcp
pytest src/world_intel_mcp/tests/test_sources.py::test_fetch_market_quotes -v  # single test

# CLI
intel markets                    # stock indices
intel earthquakes --min-mag 5.0  # USGS quakes
intel status                     # cache + circuit breaker health

# Dashboard (requires [dashboard] extra)
intel-dashboard --port 8501
# Or with .env auto-loaded:
./run-dashboard.sh
```

## Architecture

Three consumers share the same source modules and infrastructure stack:

```
server.py (MCP stdio)  ─┐                                              ┌─ VectorStore (Qdrant)
cli.py (Click CLI)      ├─> sources/*.py ─> Fetcher ─> CircuitBreaker ─┤
dashboard/app.py (SSE)  ─┘    analysis/*.py                            └─ Cache (SQLite)
collector.py (daemon)  ──┘
```

**Infrastructure layer** (`fetcher.py`, `cache.py`, `circuit_breaker.py`):
- `Fetcher`: Centralized async HTTP client (httpx). All external calls go through `get_json()`, `get_text()`, or `get_xml()`. Handles retries (2 max), per-source rate limiting, and stale-data fallback (never returns blank if old data exists).
- `CircuitBreaker`: Per-source tracking. 3 consecutive failures trips the breaker for 5 minutes. Each RSS feed gets its own breaker (`rss:bbc_world`).
- `Cache`: SQLite WAL-mode TTL cache. `get()` returns live data, `get_stale()` returns expired data for fallback.

**Tool registry** (`tools/*.py` + `runtime.py`, Phase 26): server.py is a thin shell; the 139 tools live in 12 domain modules under `tools/`, each exporting `TOOLS` (list of Tool definitions) and `HANDLERS` (tool name -> `async def h(arguments)`). Shared infrastructure (cache, circuit breaker, AOI store, vector store, fetcher) is constructed once in `runtime.py`; handlers reach it as `runtime.fetcher` etc. `tools/aggregate()` enforces TOOLS/HANDLERS parity and cross-module name uniqueness at import time — a drifted registry refuses to start.

**Source modules** (`sources/*.py`): Each module exports `async def fetch_*(fetcher: Fetcher, **kwargs) -> dict`. Pure data fetching — no MCP awareness. 30+ modules covering markets, seismology, military, cyber, health, tech, environmental, etc.

**Analysis modules** (`analysis/*.py`): Cross-domain intelligence that consumes outputs from multiple sources. Includes signal aggregation, instability indexing, NLP (entity extraction, classification, clustering, spike detection via Welford's algorithm), and strategic synthesis.

**Static config** (`config/*.py`): Curated datasets — 22 intel hotspots, 70+ military bases, 40 ports, 24 pipelines, 24 nuclear facilities, 34 undersea cables, 48 AI datacenters, 27 spaceports, 27 mineral deposits, 82 stock exchanges, 105 major cities, 28 world leaders, 36 APT groups.

**Vector store** (`vector_store.py`): Optional Qdrant + FastEmbed (BAAI/bge-small-en-v1.5, 384-dim ONNX). Async background worker queue (`asyncio.Queue` + `asyncio.to_thread()`) for non-blocking storage. Fetcher auto-stores on fresh HTTP fetches. 65+ source name → category mappings for filtered search.

**Collector** (`collector.py`): Standalone daemon for 24/7 vector store population. 55 sources organized by domain, with `--daemon`, `--interval`, `--sources` CLI args. Dynamic import via `_import_fetch_fn()`. Per-source timeout overrides in `SOURCE_TIMEOUTS` (the `aoi_digest` sweep gets 240 s; everything else the flat 45 s). Entry point: `intel-collector`.

**Reports** (`reports.py`): PDF/HTML intelligence report generator. Collects 18 domains in parallel, renders styled HTML, converts to PDF via WeasyPrint. Optional dependency: `pip install -e ".[pdf]"`.

**Dashboard** (`dashboard/`): Self-contained Starlette app with a single `index.html` template (no frontend build step). SSE endpoint streams all domains in parallel via `asyncio.gather()`, refreshes every 30 seconds. Loads `.env` from project root on startup. `/api/aois` feeds the AOI geofence layer from the shared AOI store: it opens a fresh `AOIStore` per request (`_open_aoi_store`) because SQLite connections are thread-bound and the handler may run on a different thread than a cached store's creator; it reads stored sweep snapshots and never gathers live. Endpoint tests use Starlette's `TestClient` without the context manager so lifespan (default-path `Cache`) never runs.

## Adding a New Tool

1. Create `sources/your_source.py` with `async def fetch_your_data(fetcher: Fetcher, **kwargs) -> dict`
2. Use `fetcher.get_json(url, source="your-source", cache_key=..., cache_ttl=300)` — this gives you caching, retries, circuit breaking, and rate limiting automatically
3. In the matching `tools/<domain>.py`: append the `Tool(...)` to that module's `TOOLS` and add a handler to its `HANDLERS` (`async def h(arguments)` calling your fetch via `runtime.fetcher`); `tools/aggregate()` fails the import if the two disagree
4. Optionally add to `dashboard/app.py` (SSE endpoint) and `cli.py` (Click command)
5. Add tests using `respx` to mock HTTP (see `tests/test_sources.py` for pattern)

## Key Patterns

- **Source name string**: The `source` parameter in `fetcher.get_json()` identifies the API for circuit breaking and rate limiting. Must match entries in `_SOURCE_RATE_LIMITS` if rate-limited (e.g., `"yahoo-finance"`, `"coingecko"`, `"adsblol"`, `"nominatim"`).
- **GDELT needs its own timeout**: `api.gdeltproject.org` TCP-connects instantly but its TLS handshake runs 17-20 s and sometimes longer (measured 2026-09-02), and the Fetcher's 15 s default counts TLS inside connect. Every GDELT `get_json` call must pass `timeout=GDELT_TIMEOUT` (from `sources/news.py`, 45 s) or it silently fails and serves stale cache.
- **AOI news is geographic** (`sources/geocode.py`): AOI briefs reverse-geocode the area centre with OSM Nominatim and search GDELT for the settlement/county, never the AOI's name. Nominatim policy: 1 req/s (`_SOURCE_RATE_LIMITS`), identifying User-Agent with contact URL, results cached 30 days. Tests must stub `geocode.fetch_place_context` (the shared `_patch_all_domains` helper in `test_aoi.py` does) — a suite that hits Nominatim live gets rate-limited within seconds.
- **Heatmap tools** (`sources/jet_cohort.py`, `analysis/jet_activity.py`): adsb.lol heatmaps are binary (~14 MB); fetch them with `fetcher.get_bytes` (source `adsblol-history`, 2 s floor) and the on-disk `HeatmapDiskCache`, never the SQLite TTL cache. Tests build synthetic heatmaps with the encoder in `tests/test_jet_activity.py` and zero the rate floor via monkeypatch.
- **Tool dispatch**: `server.py` looks the name up in `tools.ALL_HANDLERS` (built by `tools.aggregate()` from each module's `HANDLERS`); there is no `match/case`. Tool names follow the `intel_*` convention, and `test_server_registry.py` fails if README.md's per-tool reference or its counts drift from the registry.
- **UNHCR codes are not ISO** (`sources/migration.py`, `sources/displacement.py`): UNHCR's own `coo`/`coa` codes differ from ISO-3 (its "AUS" is Austria). Send `cf_type=ISO` and read `coo_iso`/`coa_iso`. Without `coo_all=true` the population endpoint returns one global row (`coo_name` "-"). Its country list also carries two non-countries, UNK "Unknown" and XXA "Stateless", which surge rankings must exclude.
- **All source functions take `fetcher` as first arg** — never construct your own httpx client.
- **Tests strip proxy env vars** automatically via `conftest.py` fixture (prevents SOCKS proxy interference). The conftest also resets global fetcher rate-limit locks between tests to avoid cross-event-loop binding.

## Environment Variables

Only these unlock additional data sources (everything else works unauthenticated):
- `ACLED_ACCESS_TOKEN` — conflict events
- `NASA_FIRMS_API_KEY` — satellite wildfire data
- `EIA_API_KEY` — energy prices
- `CLOUDFLARE_API_TOKEN` — internet outage data
- `FRED_API_KEY` — macro economic data
- `OPENSKY_CLIENT_ID` / `OPENSKY_CLIENT_SECRET` — military flight fallback
- `OLLAMA_API_URL` / `OLLAMA_MODEL`: Ollama server and model for AI-generated briefs (default `http://localhost:11434` / `llama3.2`)
- `WORLD_INTEL_AOI_WEBHOOK` / `WORLD_INTEL_AOI_WEBHOOK_FORMAT` — AOI sweep change notifications (collector daemon): POST on non-quiet sweeps; format `json` (default) or `text` (raw markdown + `Title` header for ntfy-style sinks). Delivery record in the digest's `notification` field; a dead sink never fails the sweep.

## Testing

Tests use `respx` to mock httpx responses. Fixtures in `conftest.py` provide `cache` (tmp_path SQLite) and `fetcher` (with clean breaker). Tests are async (`pytest-asyncio` in auto mode). Proxy env vars are stripped automatically.
