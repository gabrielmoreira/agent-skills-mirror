# Migration from Schema v2 to v3

## Breaking Changes

Schema v3 makes the research run—not just each candidate—auditable and finalizable.

### New top-level requirements

- `market_context` must contain current numeric context and source IDs.
- `global_sources` must use the strict source ledger schema.
- `screening_audit` must reference or embed a hash-verifiable row-level universe artifact.
- `run_metadata.status = complete` is valid only when every selected broad-screen symbol has a candidate record.

### Source ledger

`supports` changed from an informal string to a required array:

```json
{"supports": ["latest_earnings", "financials.cash_flow_ttm"]}
```

Source `kind` and `tier` must be compatible. Third-party transcripts are not company IR.

### Latest earnings

Replace a single mixed record with separate records:

```json
{
  "latest_report_type": "annual",
  "quarter": {"period_type": "quarter", "period": "Q4 FY2026"},
  "full_year": {"period_type": "full_year", "period": "FY2026"}
}
```

### Formal valuation basis

The current formal period must be `ntm` or `fy1`. A TTM metric may be supplemental but cannot drive the constant-multiple ranking scenario.

### Estimate breadth

A consensus horizon with fewer than the configured minimum analysts is supplemental unless accompanied by a fully sourced independent model.

### Cash and EV/FCF

EV now uses:

```text
market cap + total debt - corporate cash - eligible marketable securities
```

Customer/settlement funds and restricted cash are excluded from shareholder-available cash.

### New sector controls

- Commercial biopharma concentration may be derived from product and total revenue.
- Near-LOE concentrated franchises receive 6x and 8x stress scenarios.
- Auto dealerships require floorplan-adjusted leverage.
- Payments require corporate/settlement cash separation.

### New scripts and flags

- `screen_universe.py`: complete row-level broad-screen audit.
- `research_contract.py`: schema-v3 validation.
- `evaluate_candidates.py --require-final`: exit 2 for a provisional or globally invalid run after writing diagnostics.

## Migration Procedure

1. Create current market context and global source files.
2. Run the broad-screen audit script.
3. Initialize a new v3 run; do not mutate a v2 state directory in place.
4. Convert earnings records and forward periods.
5. Correct source `supports` types and source classifications.
6. Reconcile cash/debt and forward forecast bases.
7. Save every selected candidate.
8. Run strict evaluation with `--require-final`.
