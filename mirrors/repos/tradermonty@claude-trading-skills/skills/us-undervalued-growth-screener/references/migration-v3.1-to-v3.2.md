# Migration v3.1 → v3.2

## Why v3.2 Exists

A v3.1 live run produced `ranking_status=final` and `no_qualifying_candidates` while 15 candidate-pool rows remained in an enrichment queue and `candidate_pool_exhausted=false`. The direct cause was a completion shortcut based on minimum attempted/evaluable counts. The same run also failed to advance strong cyclical/high-growth rows, treated growth guidelines as mechanical cutoffs, hid broad-screen review/failure rows in Markdown, and accepted universe/macro freshness evidence that was too weak.

v3.2 removes those paths.

## Version Changes

```text
Skill version: 3.2.0
Top-level snapshot schema: 3
Screening audit schema: 3
Screening contract revision: 3.2
```

## Breaking Audit Changes

v3.1 broad-screen audit artifacts are not valid v3.2 evidence. Regenerate:

```text
universe-audit-results.jsonl
broad-screen-results.jsonl
enrichment-queue.json
broad-screen-audit.json
broad-screen-shortlist.json
```

### New scope proof

`scope.enumeration` is required:

```json
{
  "verified": true,
  "provider_reported_total": 1786,
  "rows_fetched": 1786,
  "pages_fetched": 18,
  "pagination_exhausted": true,
  "band_audit": [],
  "bands_verified": false
}
```

### New enrichment proof

```json
{
  "attempted_count": 120,
  "resolved_count": 118,
  "unresolved_count": 2,
  "resolution_pct": 98.3333,
  "all_rows_resolved": false,
  "candidate_pool_exhaustion_declared": false,
  "candidate_pool_exhausted": false,
  "candidate_pool_covers_in_scope": false,
  "queue_count": 2,
  "queue_symbols": ["BBB", "CCC"]
}
```

Attempted is not resolved.

### New candidate-pool coverage proof

A market-wide no-candidates conclusion requires the economic candidate pool to represent every in-scope listing symbol:

```json
{
  "in_scope_covered_count": 1786,
  "in_scope_missing_count": 0,
  "in_scope_missing_symbols": [],
  "coverage_complete": true
}
```

`candidate_pool_exhaustion_declared=true` is an operator/agent declaration. `candidate_pool_exhausted=true` is emitted only after the script independently confirms full in-scope coverage and zero unresolved rows.

### New candidate-pool statuses

```text
sufficient
sufficient_pending_enrichment
no_qualifying_candidates
insufficient_data
```

A final no-candidates outcome requires coverage of every in-scope listing symbol, explicit pool exhaustion, zero unresolved rows, an empty queue, all final dispositions, and at least one economically assessable row.

## Candidate Decision Changes

- Growth and preferred valuation thresholds are soft guidelines.
- `near_miss_review` may advance when valuation and per-share growth justify deeper work.
- P/E 21–30 high-growth exceptions remain eligible.
- Cyclical normalization is nonblocking for broad selection; the selected deep dive must calculate mid-cycle economics before ranking.
- Bank/REIT/BDC/MLP valuation and auto-dealer floorplan-adjusted leverage remain blocking.
- `unavailable_after_enrichment` requires a specific reason and resolving source IDs.
- Enrichment queue ordering is GARP-priority based, with liquidity only a tiebreaker.

## Source and Market-Context Changes

- Dynamic market fields use `data_as_of` or publication date for freshness.
- Policy, Treasury, inflation, and GDP require official support.
- Market-implied rate-path statements require explicit source support or a sourced analyst inference.

## Report Changes

Markdown now separates:

- broad selected,
- deferred by budget,
- unresolved/review,
- unavailable after enrichment,
- broad screened out,
- broad excluded,
- deep-dive ranked/review/screened-out/excluded.

An empty deep-dive set no longer hides nonzero broad-stage dispositions.

## Upgrade Procedure

1. Replace the complete `skills/us-undervalued-growth-screener/` directory. Do not mix v3.1 and v3.2 scripts or assets.
2. Replace the committed `.skill` package with the package generated from the same v3.2 source tree.
3. Add/update the `skills-index.yaml` entry from `snippets/skills-index-entry.yaml`.
4. Discard or migrate old run-state/audit artifacts; do not resume a v3.1 broad-screen audit.
5. Re-enumerate the listing universe with pagination/band exhaustion proof.
6. Rebuild and enrich the bounded candidate pool.
7. Run the v3.2 tests and strict final smoke test.
8. Verify standalone and overlay-embedded `.skill` SHA-256 values are identical.
