# Calculate Inventory Turns Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `calculate-inventory-turns` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- analysis period
- COGS, sales usage, issue quantity, or consumption quantity for the period
- average inventory in the same value or quantity basis as the numerator
- item, category, location, or facility scope

## Workflow Checks

- Confirm whether turns will be value-based or quantity-based.
- Normalize the period and inventory scope.
- Calculate average inventory from the supplied method or preserve the supplied average.
- Calculate inventory turns and call out any distortion from stockouts, promotions, or abnormal periods.
- Return the calculation with interpretation limits and comparison notes.

## Output Checks

- scope and period
- basis used: value or quantity
- average inventory calculation
- inventory turns
- interpretation notes and missing evidence
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- value-based turns
- quantity-based turns
- zero average inventory handling
- basis mismatch rejection

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
