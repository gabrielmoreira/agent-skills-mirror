# Migration from Schema Version 1 to Version 2

## Breaking Change

Schema version 2 is intentionally fail-closed. A version 1 input cannot be converted by relabeling `schema_version`; it lacks evidence and period semantics needed to prevent false rankings.

## Required Changes

### 1. Add run metadata and funnel

Add `run_metadata`, `screening_funnel`, and explicit `partial`/`complete` status.

### 2. Replace self-attestation

Remove reliance on `research_completeness`. Add:

- candidate-level `evidence` map,
- resolving `sources` rows,
- field-specific source IDs.

A Boolean claim such as `forecast_bridge_verified: true` no longer earns quality credit.

### 3. Add corporate-action preflight

Create `corporate_action_check` with listing status, M&A status, active-symbol flag, timestamp, latest material event, and source IDs.

### 4. Normalize capex sign and TTM period semantics

Replace ambiguous `capex_ttm` with non-negative `capex_cash_outflow`. Select one TTM method:

- `reported_ttm`
- `sum_4_discrete`
- `fy_plus_current_ytd_minus_prior_ytd`

Do not sum overlapping YTD periods.

### 5. Separate standard and company-adjusted FCF

Use `cash_flow_ttm.standard_fcf` for OCF minus capex. Keep `company_adjusted_fcf` and its definition separate.

### 6. Classify cash

Replace a single cash value with:

- `corporate_cash`
- `marketable_securities`
- `customer_or_settlement_funds`
- `restricted_cash`

### 7. Replace flat valuation fields with period objects

Version 1:

```json
{
  "metric_basis": "gaap",
  "current_metric": 3.0,
  "year_2_metric": 4.2,
  "year_3_metric": 5.0
}
```

Version 2:

```json
{
  "periods": {
    "current": {"metric": 3.0, "metric_basis": "gaap", "period_kind": "fy1"},
    "year_2": {"metric": 4.2, "metric_basis": "gaap", "period_kind": "fy2", "years": 2},
    "year_3": {"metric": 5.0, "metric_basis": "gaap", "period_kind": "fy3", "years": 3}
  }
}
```

Add source type, retrieval timestamp, source IDs, analyst count, and estimate range to each period.

### 8. Add arithmetic forecast bridge

For each future metric, provide numerator, denominator, operating drivers, metric basis, and source IDs.

### 9. Reconcile adjusted metrics to GAAP

For every `company_adjusted` or `analyst_normalized` period, provide the GAAP metric plus labeled adjustment rows and sources.

### 10. Use the four-status model

- `eligible`
- `review_required`
- `screened_out`
- `excluded`

Ordinary economic screen failures belong in `screened_out`; completed M&A or inactive listing belongs in `excluded`.

## Migration Procedure

1. Preserve the original v1 JSON for audit.
2. Re-run corporate-action checks and quote freshness.
3. Re-read cash-flow periods and normalize capex signs.
4. Re-query consensus with explicit GAAP/adjusted basis.
5. Build forecast and reconciliation evidence.
6. Create v2 candidate checkpoints.
7. Run strict evaluation.

There is no automatic migration script because missing evidence cannot be reconstructed safely from a v1 file alone.
