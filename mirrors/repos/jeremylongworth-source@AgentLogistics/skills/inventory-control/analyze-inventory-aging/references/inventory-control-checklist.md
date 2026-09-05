# Analyze Inventory Aging Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `analyze-inventory-aging` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- as-of date for the aging snapshot
- receipt date, production date, last movement date, or other age basis
- on-hand quantity and inventory unit
- aging buckets or policy thresholds

## Workflow Checks

- Confirm the age basis and as-of date.
- Normalize receipt, movement, lot, and status evidence by SKU or item group.
- Calculate age and assign inventory to aging buckets.
- Summarize quantity and value exposure by bucket.
- Return aging findings, policy triggers, missing fields, and recommended next analysis.

## Output Checks

- age basis and as-of date
- aging bucket summary
- SKU, lot, location, or status detail
- quantity and value exposure
- policy triggers, assumptions, and next checks
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- receipt-date aging
- last-movement aging
- aging bucket boundary
- missing cost behavior

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
