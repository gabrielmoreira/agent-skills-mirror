# Migration v3.4 → v3.5

## Breaking changes

1. Runtime identity is now `3.5.0 / contract 3.5 / ug-v3.5-multilane-quality-bundle-20260828`.
2. Default deep-dive budget is five and uses multi-lane selection.
3. Candidate metrics must retain `average_volume` and `liquidity_source_ids`.
4. Provider-side share-volume filters prevent a full-listing enumeration claim.
5. Forecast bridges require `construction_method=independent_driver_model` and per-driver provenance with `target_solved=false`.
6. Discrete/YTD/reported TTM cash-flow evidence requires exact support paths.
7. Recent spin-offs and transformative M&A use `corporate_transition`, not `identity.special_case`.
8. Formal eligibility has score, FCF, ROIC, leverage, dilution, low-case, and LOE quality gates. A new `conditional` status is available.
9. Final-three categories are nullable and use category-specific thresholds.
10. Final publication requires `prepublish_audit.py` and `bundle_run_artifacts.py`.

## Candidate migration

Add driver provenance under every year-2/year-3 bridge:

```json
{
  "construction_method": "independent_driver_model",
  "driver_provenance": {
    "revenue": {
      "origin": "market_consensus",
      "source_ids": ["consensus-source"],
      "target_solved": false
    }
  }
}
```

Add exact cash-flow supports to source rows:

```text
financials.cash_flow_periods.<period-end>
financials.ttm_reconstruction.<component>
financials.cash_flow_ttm.reported_ttm
```

## Run migration

Discard v3.4 audits/checkpoints; their fingerprint is intentionally incompatible. Re-run runtime preflight, Broad Screen, candidate verification, strict evaluation, prepublication audit, and bundle generation.
