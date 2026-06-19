---
name: traversing-citations
description: Backward (references) and forward (citing papers) traversal via OpenAlex, with relevance filtering and deduplication
when_to_use: After finding a relevant paper (score >= 7). When you need related work. When following references or citing papers. When building a citation graph.
version: 2.0.0
---

# Traversing Citation Networks

> **RC native tools** — this skill's pipeline ships as four built-in RC tools. Call them directly; do **not** shell out to any `rp.py` script or write curl:
> - `rp_search({ query, limit?, min_year? })` — Scopus relevance search enriched with OpenAlex abstracts + OA PDF links. The Elsevier key is built in.
> - `rp_abstracts({ dois })` — batch abstracts + OA links for a DOI list (OpenAlex, no key).
> - `rp_cite({ doi, direction?, limit? })` — citation traversal (`direction`: `both` / `backward` / `forward`).
> - `rp_fulltext({ doi, out? })` — OA full text (Elsevier ScienceDirect OA → OpenAlex OA fallback); pass `out` to also save the text to a file.
>
> Results return inline as JSON (there is no `--json <file>` flag). To persist a result set, save the returned JSON with the workspace file tools.


## Overview

Follow citations **backward** (a paper's references) and **forward** (papers citing it)
through **OpenAlex**, driven by `rp_cite`.

**Core principle:** Only expand papers that already scored >= 7, and only enqueue
citations that pass relevance filtering. Filter before traversing to avoid explosion.

> **Why OpenAlex, not Scopus or Semantic Scholar:** the personal Scopus key cannot return
> references or run forward-citation (`REFEID`) searches — both 403. Semantic Scholar was
> dropped from this pipeline: in testing it returned `data: null` for the references of
> papers it had clearly indexed (e.g. it reported 18 references but served none), failing
> silently. OpenAlex returned the full reference list for those same papers. OpenAlex is
> the single citation source here.

## How to Traverse

### One command, both directions

```bash
rp_cite "10.1056/NEJMoa2300696" --direction both --limit 50 \
   
```

Returns:
```json
{
  "seed": {"doi": "...", "title": "...", "openalex_id": "W..."},
  "backward": [ {normalized work: doi,title,year,abstract,cited_by,oa_pdf_url}, ... ],
  "forward":  [ {normalized work, sorted by cited_by desc}, ... ]
}
```

- **backward** = `referenced_works` (what this paper cites), resolved to full metadata
  with abstracts in batch.
- **forward** = papers whose `cites` field includes the seed, sorted by citation count
  (most-cited citing papers first — usually the highest-signal follow-ups).

Both arrays already carry abstracts, so you can score immediately with
`evaluating-paper-relevance` without another fetch.

### Filtering before enqueue

For each returned citation, score for relevance to the query (use the same rubric as
`evaluating-paper-relevance`). Cheap pre-filter signals already in the record:

- Title contains query keywords  → strong
- Abstract contains query terms  → strong
- Recent (forward citations < 3 yrs old)  → prioritize
- High `cited_by`  → prioritize

**Only enqueue citations scoring >= 5.** Then evaluate enqueued papers normally.

### Deduplicate

Before enqueuing, check `papers-reviewed.json` by DOI; skip if present. **After**
evaluating any traversed paper, add it to `papers-reviewed.json` regardless of score, so
it is never re-processed from another seed.

Record the relationship in `citations/citation-graph.json`:
```json
{ "10.1056/nejmoa2300696": { "references": ["10.x/...", ...], "cited_by": ["10.y/...", ...] } }
```
Use **only** `citation-graph.json` for relationships and `SUMMARY.md` for findings — do
not create ad-hoc files like `forward_citation_dois.txt`.

## Smart Traversal Limits

- Expand only seeds scoring >= 7.
- Enqueue only citations scoring >= 5.
- Depth <= 2 levels (seed → its citations → their citations, then stop).
- Checkpoint with the user after every 50 total papers.
- `--limit` caps each direction per call; raise deliberately, not by default.

## Coverage Notes (honest limits)

- **OpenAlex reference coverage** is high but not universal — a few works expose no
  `referenced_works`. When `backward` is empty for a paper that clearly has references,
  note it (`⚠️ No references in OpenAlex`) and continue; do not assume zero references.
- Forward-citation counts track OpenAlex's graph, which can lag the very newest papers by
  weeks.

## Common Mistakes

- **Hand-writing curl / using Semantic Scholar** → use `rp_cite` (OpenAlex). SS is removed.
- **Following all citations** → exponential blow-up; filter to >= 5 first.
- **Not deduping** → check `papers-reviewed.json` before and after; add every evaluated paper.
- **Going too deep** → cap at 2 levels and checkpoint at 50 papers.
- **Treating empty `backward` as truth** → may be a coverage gap; flag it.

## Next Steps

Evaluate enqueued papers with `evaluating-paper-relevance`; update `SUMMARY.md` and
`citation-graph.json`; checkpoint at 50 papers.
