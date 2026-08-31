# Migration Guide — v3.0 to v3.1

## Why v3.1 Exists

A v3.0 execution correctly refused to publish a ranking, but it failed operationally because it required near-complete financial coverage for the full market, silently used a reduced USD 10B–20B universe, selected unresolved sector-review rows using equal placeholder scores, and produced inconsistent selected/unprocessed state. The distributed standalone package also differed from the package embedded in the repository overlay.

```text
Top-level snapshot schema: 3
Screening audit schema: 3 / contract revision 3.1
Run-state schema: 2
Skill version: 3.1.0
```

v3.1 keeps the strict primary-source, accounting, and forward-valuation controls while replacing the impossible market-wide financial-completeness requirement with a two-layer coverage model.

## Required Changes

### Screening artifacts

Old single artifact:

```text
broad-screen-results.jsonl
```

v3.1 artifacts:

```text
universe-audit-results.jsonl
broad-screen-results.jsonl
enrichment-queue.json
broad-screen-audit.json
broad-screen-shortlist.json
```

### Audit metadata

```text
audit_schema_version: 3
contract_revision: 3.1
candidate_pool_status: sufficient | no_qualifying_candidates | insufficient_data
selection_outcome: selected | no_candidates | insufficient_data
```

### Checkpoint attachment

Replace the legacy single `--artifact` invocation with:

```bash
--universe-artifact .../universe-audit-results.jsonl \
--candidate-artifact .../broad-screen-results.jsonl
```

### Plan-gated fundamentals

Do not abandon the run or demand a paid endpoint. Build a transparent stratified discovery pool with `build_discovery_pool.py`, enrich that bounded pool with available estimates/fundamentals, and rerun `screen_universe.py`.

### Status migration

| v3.0 behavior | v3.1 behavior |
|---|---|
| Missing full-universe financial fields counted as global audit failure | Missing candidate-pool economics become `needs_enrichment` |
| Review-only rows could share a placeholder score | Review rows use `broad_score=null` and cannot be selected |
| Listing-only pool could be mistaken for no candidates | `insufficient_data`; final no-candidates conclusion prohibited |
| Reduced provider scope could continue | Scope marked incomplete; final contract blocked |
| Selected count could disagree with unprocessed state | `unprocessed = selected - verified` invariant enforced |

## Package Migration

1. Replace the entire skill directory; do not mix v3.0 and v3.1 scripts or assets.
2. Start a new run directory and regenerate both audit layers.
3. Remove the old standalone package.
4. Install only the v3.1 package whose SHA-256 matches the package embedded in the v3.1 overlay.
