---
name: subagent-driven-review
description: Use parallel subagents to scale large reviews, with an honest model of where the speedup actually comes from (LLM reasoning, not API throughput)
when_to_use: Large literature searches (50+ papers), parallel paper screening, deep dive analysis on multiple papers, citation network exploration, when main context is getting full
version: 2.0.0
---

# Subagent-Driven Literature Review

> **RC native tools** — this skill's pipeline ships as four built-in RC tools. Call them directly; do **not** shell out to any `rp.py` script or write curl:
> - `rp_search({ query, limit?, min_year? })` — Scopus relevance search enriched with OpenAlex abstracts + OA PDF links. The Elsevier key is built in.
> - `rp_abstracts({ dois })` — batch abstracts + OA links for a DOI list (OpenAlex, no key).
> - `rp_cite({ doi, direction?, limit? })` — citation traversal (`direction`: `both` / `backward` / `forward`).
> - `rp_fulltext({ doi, out? })` — OA full text (Elsevier ScienceDirect OA → OpenAlex OA fallback); pass `out` to also save the text to a file.
>
> Results return inline as JSON (there is no `--json <file>` flag). To persist a result set, save the returned JSON with the workspace file tools.


## Overview

**Core principle:** Fresh subagent per batch + consolidation between batches = parallel
reasoning with quality control.

For large reviews (50+ papers), subagents help in two real ways:

1. **Context management** — each subagent reads abstracts / full text in its own context,
   so the main context stays clean for consolidation and decisions.
2. **Parallel LLM reasoning** — scoring, extraction, and summarizing happen concurrently.

## What subagents do NOT speed up: API throughput

**Read this before claiming "5x faster."** All subagents egress from the **same IP** and
share the **same server-side rate limits** (Scopus weekly quota; OpenAlex polite-pool
~10 req/s). Splitting work across 5 subagents does **not** give you 5x the API calls — the
publisher counts them together.

Worse: `rp_lib`'s rate limiter is **per-process**. Parallel subagents each run their own
limiter and do **not** coordinate, so naïvely fanning out 10 subagents all calling
`rp_search` can collectively blow past the per-IP ceiling and trigger 429s.

What *does* hold up under parallelism:
- The **disk cache** is shared on the filesystem. If two subagents request the same DOI,
  the second hits cache. Pre-warming the cache (see below) makes fan-out safe.
- `rp_lib` retries 429/5xx with exponential backoff, so bursts degrade gracefully rather
  than failing — but that's damage control, not throughput.

**Honest mental model:** *API-bound* steps (search, abstract fetch, citation fetch) are
capped by the server, so keep the number of subagents doing live API calls small (≤3–4).
*Reasoning-bound* steps (scoring an abstract you already have, extracting from full text
already on disk) parallelize freely — fan those out widely.

### The pattern that actually scales: fetch once, fan out reasoning

```
Main agent (1 process, respects the rate limiter):
  1. rp_search ...           -> candidates with abstracts (cached to disk)
  2. rp_abstracts <dois>     -> fill any gaps (cached to disk)
Now every abstract is on disk. Dispatch N subagents to SCORE in parallel —
they read from cache, do no (or minimal) live API calls, and can't 429 each other.
```

This converts an API-bound problem into a reasoning-bound one, which is the only kind
subagents genuinely accelerate.

## When to Use

Use the subagent approach when:
- **Large searches:** 50+ candidates to screen
- **Parallelizable reasoning:** papers scored/extracted independently
- **Deep dive:** multiple papers need detailed extraction from full text
- **Context pressure:** main context filling up

**Do NOT use when:**
- Small searches (<20 papers) — overhead not worth it
- You need real-time visibility into every paper
- Papers require cross-comparison *during* screening

## Use Cases

### 1. Parallel Scoring (most common)

**Scenario:** Scopus search returned 100 candidates (abstracts already attached by
`rp_search`).

**Pattern:**
```
Main agent:
1. rp_search "<query>" --limit 100
   (abstracts now cached on disk for every hit)
2. Split the 100 records into 5 batches of 20
3. Dispatch 5 subagents IN PARALLEL — each SCORES its batch from the records
   it's handed (no live API calls needed; abstracts are already in the JSON)
4. Main agent consolidates into papers-reviewed.json
```

The speedup here is real *because the scoring is reasoning-bound* — the API work was
already done once by the main agent.

**Prompt template for a scoring subagent:**
```
Score these 20 candidate papers for relevance to [QUERY].

Records (each has title, journal, year, cited_by, abstract):
[paste the 20 JSON records from initial-search-results.json]

Use the evaluating-paper-relevance rubric:
  Keywords (0-3) + Data type (0-4) + Specificity (0-3) = score 0-10.
Score from the abstract in the record. If a record has "abstract": "",
score from title + journal + cited_by and flag it.

Return JSON only (do NOT touch papers-reviewed.json):
{
  "scored": [
    {"doi": "10.x/...", "score": 8, "status": "relevant", "reason": "...", "no_abstract": false},
    ...
  ],
  "stats": {"highly_relevant": 3, "relevant": 5, "not_relevant": 12}
}
```

### 2. Deep Dive on Priority Papers

**Scenario:** Screening flagged 15 papers (score ≥8); extract data from each.

These subagents *do* make live calls (`rp_fulltext`), so cap concurrency at ~3–4 and
let the shared disk cache + 429 backoff absorb collisions.

**Prompt template:**
```
Deep dive on DOI [10.xxxx/yyyy] for [QUERY].

1. Run: rp_fulltext "10.xxxx/yyyy" --out papers/<slug>.xml
   - source "elsevier-oa": text saved to disk, grep/scan it
   - source "openalex-oa": fetch the returned pdf_url (free copy) and read it
   - available:false: no OA copy exists -> extract from abstract only
2. Extract, by domain: data tables/measurements, methods, key results,
   data-availability (GEO/SRA accession, code repo).

Return JSON only (do NOT touch papers-reviewed.json):
{
  "doi": "10.xxxx/yyyy",
  "full_text_source": "elsevier-oa" | "openalex-oa" | "paywalled",
  "data_sources": ["Table 1", "Figure 3", "Supplementary Data"],
  "key_measurements": ["..."],
  "methods_summary": "...",
  "key_findings": ["..."],
  "data_availability": "GEO: GSE12345" | "Code: github.com/..." | null
}
```

### 3. Citation Network Exploration

**Scenario:** One strong seed; explore both directions.

`rp_cite <doi> --direction both` already returns backward + forward in a **single
call** with abstracts attached, so you usually do **not** need two subagents per seed —
one subagent per seed runs the call and scores both lists. Fan out across *seeds*, not
across directions.

**Prompt template:**
```
Explore citations for seed DOI [10.xxxx/yyyy], relevant to [QUERY].

1. Run: rp_cite "10.xxxx/yyyy" --direction both --limit 50 \
       
2. Score every returned backward + forward record (abstracts are included).
3. Return only papers scoring >= 5 (the enqueue threshold):

{
  "seed_doi": "10.xxxx/yyyy",
  "backward_relevant": [{"doi": "...", "score": 8, "title": "...", "reason": "..."}],
  "forward_relevant":  [{"doi": "...", "score": 7, "title": "...", "reason": "..."}]
}

Do NOT touch papers-reviewed.json — return results only.
```

### 4. Domain-Specific Extraction

Adapt the deep-dive prompt's extraction list to the domain:

- **Genomics:** GEO/SRA/ENA accessions, sample sizes, sequencing method, DE results
- **Computational:** algorithm, code repo, benchmark datasets, performance metrics
- **Clinical:** study design, N + demographics, intervention, primary outcomes, stats
- **Ecology:** sites/coordinates, sampling method, taxa, environmental measurements

## Workflow: Parallel Scoring

1. **Fetch once (main agent):** `rp_search` → abstracts cached. Fill gaps with
   `rp_abstracts` if needed.
2. **Split:** 15–25 records per subagent. Hand each subagent its records inline.
3. **Dispatch in parallel:** single message, multiple Task calls. Safe to go wide here —
   subagents score from handed-in records, not the network.
4. **Collect:** validate every DOI was scored; check rubric was applied.
5. **Consolidate:** merge, dedupe by DOI, sort by score, write **all** to
   `papers-reviewed.json`:
   ```json
   {
     "10.1234/example.2023": {
       "status": "highly_relevant",
       "score": 9,
       "source": "scopus_search",
       "screened_by": "subagent_batch1",
       "timestamp": "2025-10-11T14:30:00Z",
       "found_data": ["measurements", "methods"]
     }
   }
   ```
6. **Quality check:** if one batch's hit-rate is wildly off from the others, the rubric
   may have been applied inconsistently — re-score that batch.
7. **Summarize:** generate `SUMMARY.md`, sorted by score, flag which papers need deep dive.

## Workflow: Citation Exploration

1. Pick 2–3 strong seeds (score ≥7).
2. Dispatch one subagent per seed running `rp_cite --direction both` (cap ~3–4 live).
3. Consolidate: merge, dedupe, drop DOIs already in `papers-reviewed.json`, build the next
   screening queue.
4. Score the new queue (parallel scoring workflow above).
5. Iterate with stopping criteria: depth ≤2, total ≤200, or diminishing returns.

## Consolidation Patterns

- **JSON aggregation:** subagents return JSON; main agent merges, sorts by score, writes
  `papers-reviewed.json`. Subagents never write tracking files (avoids conflicts).
- **Progressive:** consolidate after each subagent (sequential) — slower, incremental
  visibility.
- **Batch:** dispatch N in parallel, consolidate the batch, repeat — the default balance.

## Common Mistakes

- **Claiming linear speedup from fan-out** → API throughput is server-capped and shared
  across subagents; only reasoning parallelizes. Fetch once, then fan out scoring.
- **Fanning out live API calls** → many subagents each running `rp_search`/`fulltext`
  share one IP and one quota, and `rp_lib`'s limiter is per-process so they don't
  coordinate → 429s. Keep live-API subagents to ≤3–4; pre-warm the disk cache.
- **Subagents writing tracking files** → conflicts. Subagents return JSON; main agent
  writes `papers-reviewed.json`.
- **Inconsistent scoring** → give every subagent the same rubric inline.
- **No quality review** → never blindly trust merged output; spot-check.
- **Duplicate work** → split DOI lists with no overlap; dedupe on merge.
- **Using PubMed/ChEMBL/Unpaywall prompts** → removed. The only data tools are
  `rp_search/abstracts/cite/fulltext` (Scopus + OpenAlex).

## Cost Considerations

Subagents cost tokens. Rough per-subagent: scoring 20 records ~10–15K; deep dive 1 paper
~5–10K; citation exploration ~8–12K. Use subagents for 50+ papers; screen small searches
manually. Parallelize *reasoning*; serialize or cap *API* work.

## Decision Tree

```
Literature review task?
├─ <20 papers?      → screen manually (no subagents)
├─ 20-50 papers?
│  ├─ time-sensitive? → subagents (2-3 scoring batches)
│  └─ not urgent?     → screen manually
└─ 50+ papers?
   ├─ fetch once (main agent: rp_search/abstracts)
   ├─ score          → many parallel subagents (cache-fed, safe to go wide)
   ├─ deep dive      → ≤3-4 live subagents (rp_fulltext)
   └─ citations      → one subagent per seed (rp_cite), ≤3-4 live
```

## Integration with Other Skills

- **searching-literature** (`rp_search`): the main agent runs this once to populate the
  cache before fan-out.
- **evaluating-paper-relevance**: the rubric subagents apply when scoring.
- **traversing-citations** (`rp_cite`): what citation subagents run.

## Next Steps After Subagent Review

1. Review consolidated results for quality/consistency.
2. Identify gaps — expected papers missing?
3. Deep dive on highly relevant papers (≤3–4 live subagents).
4. Generate final `SUMMARY.md` with statistics and key findings.
