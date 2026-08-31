# Migration v3.3 → v3.4

## Why this release is breaking

A live v3.3 run exposed five discovery/orchestration defects:

1. the default USD 500M–20B request was silently rewritten to USD 3B–4B;
2. one session's volume was labeled as average daily dollar volume;
3. a pre-operating company without FY1 estimates appeared at roughly 4x using distant outer-year EPS;
4. five deterministic selections were later proposed to be reduced to two without rerunning the screen;
5. the workflow again asked the user for a separate “continue” turn.

v3.4 makes these conditions fail closed.

## Required input changes

### Liquidity

Discovery rows need one of the supported 20+ session average-liquidity forms, plus source IDs:

```json
{
  "average_daily_dollar_volume": 12000000,
  "average_daily_dollar_volume_method": "provider_average_dollar_volume",
  "average_volume_period_days": 20,
  "liquidity_source_ids": ["quote-source"]
}
```

Raw single-session `volume` is ignored for ADDV.

### Current forward valuation

`forward_pe` alone is no longer accepted. Use `normalize_estimates.py` or supply dated NTM/FY1 metadata, positive EPS, analyst count, source IDs, and price/EPS reconciliation.

### Scope

The default user request remains USD 500M–20B. Internal budget pressure cannot turn a single band into the request. A genuinely narrower user request needs explicit authorization evidence and matching requested/executed bounds.

### Selected-set commitment

Every Broad Screen-selected symbol must receive a verified terminal candidate record. Change the deep-dive budget only by rerunning `screen_universe.py`; omitted eligible names then become `deferred_by_budget` deterministically.

## Upgrade steps

1. Replace the full `skills/us-undervalued-growth-screener/` directory.
2. Replace `skill-packages/us-undervalued-growth-screener.skill`.
3. Remove stale installed/cached copies of the same skill name.
4. Verify the five runtime entry points with `--version`.
5. Rebuild discovery liquidity from provider average volume or a 20+ session series.
6. Normalize dated annual estimates through `normalize_estimates.py`.
7. Discard v3.3 audits, checkpoints, and snapshots.
8. Run the skill tests, index validation, package-drift checks, and repository CI.
