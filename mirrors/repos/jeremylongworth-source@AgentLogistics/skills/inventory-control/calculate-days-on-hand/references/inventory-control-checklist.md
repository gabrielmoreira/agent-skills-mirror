# Calculate Days On Hand Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `calculate-days-on-hand` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- on-hand quantity or value
- average daily demand, usage, issue rate, or daily COGS on the same basis
- as-of date or inventory snapshot time
- inventory scope and unit

## Workflow Checks

- Confirm whether the calculation uses physical on hand, available stock, or inventory value.
- Normalize average demand to a daily basis.
- Exclude held, damaged, quarantined, or allocated inventory only when the user supplies those fields.
- Calculate days on hand and show the demand basis.
- Return the result with stockout-risk notes and missing data that would change interpretation.

## Output Checks

- scope and snapshot time
- on-hand or available quantity
- average daily demand calculation
- days on hand
- interpretation notes, assumptions, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- quantity-based days on hand
- value-based days on hand
- period-to-daily conversion
- zero-demand behavior

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
