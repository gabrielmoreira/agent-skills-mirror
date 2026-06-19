---
name: searching-literature
description: Scopus relevance search (main) enriched with OpenAlex abstracts and OA links, via the rp_* tools pipeline
when_to_use: When starting literature search. When user asks about papers, publications, studies. When building the initial candidate list for a research question.
version: 2.0.0
---

# Searching Scientific Literature

> **RC native tools** — this skill's pipeline ships as four built-in RC tools. Call them directly; do **not** shell out to any `rp.py` script or write curl:
> - `rp_search({ query, limit?, min_year? })` — Scopus relevance search enriched with OpenAlex abstracts + OA PDF links. The Elsevier key is built in.
> - `rp_abstracts({ dois })` — batch abstracts + OA links for a DOI list (OpenAlex, no key).
> - `rp_cite({ doi, direction?, limit? })` — citation traversal (`direction`: `both` / `backward` / `forward`).
> - `rp_fulltext({ doi, out? })` — OA full text (Elsevier ScienceDirect OA → OpenAlex OA fallback); pass `out` to also save the text to a file.
>
> Results return inline as JSON (there is no `--json <file>` flag). To persist a result set, save the returned JSON with the workspace file tools.


## Overview

Discovery runs on **one backbone: Scopus** (relevance-ranked, all-publisher coverage,
real citation counts), with **OpenAlex** layered on only to supply the data Scopus's
personal-key tier withholds (abstracts, OA full-text links). Both are driven by the
`the rp_* tools` tool — you do not hand-write curl.

**Core principle:** Scopus decides *what* and *in what order*; OpenAlex fills in *abstracts*.

> **Key entitlement reality (tested):** a personal Scopus API key exposes the STANDARD
> search view only — title, DOI, EID, citation count, year, OA flag. It does **not**
> return abstracts, references, or forward citations. That is why abstracts come from
> OpenAlex and citation traversal lives in `traversing-citations` (also OpenAlex). Do
> not try to pull abstracts/refs from Scopus; the calls 403.

## How to Search

### 1. Build the Scopus query

Scopus query syntax (richer than plain keywords — use it):

- `TITLE-ABS-KEY( ... )` — search title, abstract, keywords (the default workhorse)
- `AND` / `OR` / `AND NOT` — boolean
- `W/n` — proximity (e.g. `BTK W/3 selectivity`)
- `PUBYEAR > 2018` — date constraint
- `DOCTYPE(ar)` — article type (ar=article, re=review)

Examples:
```
TITLE-ABS-KEY(("BTK" OR "Bruton tyrosine kinase") AND inhibitor AND (selectivity OR "off-target"))
TITLE-ABS-KEY("CRISPR" AND cardiomyocyte) AND PUBYEAR > 2019
```

### 2. Run the search

```bash
rp_search "TITLE-ABS-KEY(BTK inhibitor selectivity)" \
    --limit 50 --min-year 2015
```

This single command:
1. Pages Scopus by relevancy (citation counts included).
2. Batch-fetches OpenAlex by DOI (50/call) to attach `abstract`, `oa_status`, `oa_pdf_url`.
3. Writes candidate records ready for scoring.

Each record:
```json
{
  "scopus_id": "85...", "eid": "2-s2.0-85...", "doi": "10.1016/...",
  "title": "...", "year": "2023", "cited_by": 42, "oa": true,
  "source": "Journal of Medicinal Chemistry",
  "abstract": "We report ...", "openalex_id": "W...",
  "oa_status": "gold", "oa_pdf_url": "https://..."
}
```

### 3. Report

Announce: `🔎 Scopus: N papers · M with abstracts (OpenAlex)`.
Then hand the candidate list to `evaluating-paper-relevance` for scoring.

## Coverage Notes (honest limits)

- **Abstract gaps:** OpenAlex lacks abstracts for some closed papers (notably parts of
  Elsevier/ACS). Expect roughly 50–80% abstract coverage. Papers with `"abstract": ""`
  must be scored from **title + journal + citation count** only, or deferred — never
  silently dropped. Flag them: `⚠️ No abstract (score from title)`.
- **Scopus quota:** 20,000 search results/week on the personal key. The pipeline paginates
  25/call, so a 50-result search costs 2 calls. Budget accordingly for large sweeps.
- **No Scopus abstracts/refs/fulltext-search** on this key — by design, see above.

## Quick Reference

| Task | Command |
|------|---------|
| Search + enrich | `rp_search "<scopus query>" --limit N` |
| Narrow | add `AND`, `PUBYEAR > Y`, `DOCTYPE(ar)`, more specific `TITLE-ABS-KEY` |
| Broaden | use `OR`, drop constraints, add synonyms |

## Common Mistakes

- **Hand-writing curl to Scopus** → use `the rp_* tools`; it handles paging, rate limits, caching.
- **Expecting abstracts from Scopus** → they come from OpenAlex; some will be missing.
- **Dropping abstract-less papers** → score them from title/citations or defer, don't hide them.
- **Ignoring the weekly quota** → 20k Scopus results/week; don't burn it on over-broad sweeps.

## Next Steps

After search: score with `evaluating-paper-relevance`; expand high scorers with
`traversing-citations`.
