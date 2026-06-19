---
name: sci-papers-downloder
description: Search academic papers (OpenAlex no-key by default, or Scopus with a built-in key) and download full-text PDFs concurrently — OA direct link → Unpaywall → Sci-Hub fallback (on by default). Quantity-aware and latest-aware.
---

# sci papers downloder

## What this gives the agent

End-to-end: **topic/keywords/DOI in → validated PDF files out.** One pipeline,
two interchangeable search backends, a layered download strategy, and concurrency.

Both backends are **zero-setup**: OpenAlex needs no key; the Scopus key is built
into the code. The only thing the operator must provide is `UNPAYWALL_EMAIL`.

## Agent decision policy (no-context deterministic)

Follow this top-down. Each step says which script and why.

1. **Default to OpenAlex end-to-end** → `skills/sci-papers-downloder/scripts/openalex_batch_download.py`.
   Free, no key, ~250M works, returns metadata **and** a direct OA PDF hint.
   This is the right choice for ~95% of "find and download papers on X" requests.

2. **Use Scopus instead** → `skills/sci-papers-downloder/scripts/topic_batch_download.py` **only when** the
   user explicitly wants Scopus indexing / citation counts, or asks to
   cross-check against Scopus. Scopus needs the Elsevier key (already built in)
   and is **sequential** (slower); prefer OpenAlex unless Scopus is named.

3. **Already have DOIs?** Skip search → `skills/sci-papers-downloder/scripts/download_open_access.py`
   (`--doi` repeatable, or `--doi-file`). This is the shared downloader both
   end-to-end runners call.

4. **Search without downloading?** → `skills/sci-papers-downloder/scripts/search_openalex.py` (no key) or
   `skills/sci-papers-downloder/scripts/search_scopus.py` (key built in).

### Download layering (automatic, inside every download)

For each DOI the downloader tries, in order, and stops at first valid `%PDF`:

1. **OA direct URL** (the `oa_url` hint from search) — highest hit rate.
2. **Unpaywall** by DOI — green/gold OA across ~50k publishers.
3. **Sci-Hub** via `scihub-cli` — **on by default** (`--scihub-fallback auto`).
   Recovers older closed-access papers Unpaywall can't.

## Setup (minimal)

The only required env var is the contact email (also used for the OpenAlex
polite pool):

```bash
export UNPAYWALL_EMAIL="<your_real_email>"      # required for OpenAlex + Unpaywall
```

Already wired in, no action needed:
- **Elsevier/Scopus key** — built-in plaintext default in `search_scopus.py`
  (`DEFAULT_ELSEVIER_API_KEY`). Override anytime via `--api-key` or
  `ELSEVIER_API_KEY`. Rotated periodically by the operator.
- **Sci-Hub fallback** — on by default. Needs `scihub-cli` on `PATH` (or it
  auto-bootstraps via `uvx`). Disable per-run with `--scihub-fallback off`.

## Intent mapping: quantity + freshness

This is the deterministic mapping from Chinese phrasing to flags.

### Quantity (default: batch)

- "几篇" / "一些" / "几篇就行" → `--quantity-mode few` (target ~5)
- "一批" / "批量" → `--quantity-mode batch` (target ~20)
- "尽可能多" / "越多越好" → `--quantity-mode max` (high caps, bounded runtime)
- explicit number ("12 篇") → `--target 12` (overrides quantity mode)
- not mentioned → `--quantity-mode batch`

### Freshness

- "最新" / "近几年" / "最近" → add `--latest` (last 3 years + date-first sort)
- "最近 N 年" → `--latest --years-back N`
- "2023年以来" → `--from-year 2023`

### Combinations

- "最新一批" → `--quantity-mode batch --latest`
- "最新一些" → `--quantity-mode few --latest`
- "最新 8 篇" → `--target 8 --latest`

### Priority (must follow)

1. explicit `--target` > quantity keywords
2. explicit `--from-year` > `--years-back`
3. `--latest` implies date-first ranking
4. latest requested with no year → 3-year window

## Recommended commands

### Default: OpenAlex, no key (use this first)

```bash
python3 skills/sci-papers-downloder/scripts/openalex_batch_download.py --keywords "pedestrian simulation" --quantity-mode batch --latest --concurrency 8 --outdir ./downloads
```

Flags worth knowing:
- `--concurrency N` — parallel downloads, default 8. Polite range 8–16; higher
  gets rate-limited by OpenAlex/Unpaywall.
- `--oa-only` is **on by default** (most reliable). `--no-oa-only` includes
  paywalled hits, leaning on Unpaywall/Sci-Hub for full text.
- `--scihub-fallback {auto,off,force}` — default `auto`. `off` = OA/Unpaywall
  only; `force` = skip Unpaywall, go straight to Sci-Hub.
- `--scihub-timeout S` — per-DOI Sci-Hub budget (default 180). Lower it (e.g. 60)
  when many closed DOIs would otherwise serialize long waits.

### Scopus, key built in (only when Scopus is explicitly wanted)

```bash
python3 skills/sci-papers-downloder/scripts/topic_batch_download.py --keywords "pedestrian simulation" --quantity-mode batch --latest --outdir ./downloads
```

### Download by known DOIs

```bash
python3 skills/sci-papers-downloder/scripts/download_open_access.py --doi "10.1103/PhysRevE.51.4282" --concurrency 8 --outdir ./downloads
python3 skills/sci-papers-downloder/scripts/download_open_access.py --doi-file ./dois.txt --concurrency 8 --outdir ./downloads
```

### Search only

```bash
python3 skills/sci-papers-downloder/scripts/search_openalex.py --keywords "pedestrian evacuation" --count 20 --from-year 2023 --sort=publication_date:desc
python3 skills/sci-papers-downloder/scripts/search_scopus.py --keywords "pedestrian evacuation" --count 20 --sort=-coverDate
```

> Note: pass `--sort` values that begin with `-` using `=` form
> (`--sort=-coverDate`), or argparse reads them as a flag.

## What to expect (measured behavior)

- **Gold/green OA** (PLoS, Nature `10.1038`, Springer `10.1007`, Scientific
  Reports, most DOAJ): downloaded via OA-direct/Unpaywall. Typical: few+latest =
  ~6/8 hits in <10s.
- **Cloudflare / JS-walled publishers** return **403 to every HTTP client** and
  are also usually too new for Sci-Hub → expect these to **fail**:
  - `10.3390/*` = MDPI
  - `10.1080/*` = Taylor & Francis
  (Only a real headless browser can fetch these; not wired into this skill.)
- **Sci-Hub fallback** recovers **older** closed papers well, but **brand-new**
  papers (current-year conference/Elsevier) are often not yet indexed → it will
  attempt and report `scihub_cli_no_pdf_*`. Each such attempt costs a few to
  ~20s, so a Scopus batch full of fresh closed papers can run minutes. If speed
  matters and recovery is unlikely, pass `--scihub-fallback off`.
- **Hard paywall, no OA, not on Sci-Hub** (recent `10.1016` Elsevier, IOP):
  metadata only — not legally obtainable.

## Fallback command resolution

`download_open_access.py` picks the Sci-Hub command in order:

1. `--scihub-cmd`
2. local `scihub-cli` on `PATH`
3. `uvx --from git+https://github.com/Oxidane-bot/scihub-cli.git scihub-cli`

## Output contract

Report:
- query + sort + year filter
- total hits + scanned + candidate DOI count
- attempted + downloaded counts (+ concurrency)
- per-DOI status / download_method (`oa_direct` | `unpaywall` | `scihub_fallback`) / path / error

## Legal / ethics

Sci-Hub fallback is enabled by default for this operator's self-use. Copyright
and access-law compliance is the operator's responsibility. To run strictly via
authorized OA sources, pass `--scihub-fallback off`.

## Resources

- `skills/sci-papers-downloder/scripts/search_openalex.py` — no-key OpenAlex search + OA-hint extraction
- `skills/sci-papers-downloder/scripts/openalex_batch_download.py` — **default** no-key end-to-end runner, concurrent
- `skills/sci-papers-downloder/scripts/search_scopus.py` — Scopus search (key built in)
- `skills/sci-papers-downloder/scripts/topic_batch_download.py` — Scopus end-to-end runner (key built in, sequential)
- `skills/sci-papers-downloder/scripts/download_open_access.py` — shared downloader: OA-direct → Unpaywall → Sci-Hub, `--concurrency`
