# Calculate EOQ Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `calculate-eoq` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- annual demand quantity in inventory units
- ordering cost per order in a named currency
- annual holding cost per unit in the same currency
- item or item-group scope

## Workflow Checks

- Confirm the demand period is annual or normalize it to annual demand with user approval.
- Confirm ordering cost and holding cost use the same currency and cost basis.
- Calculate raw EOQ using the classic square-root model.
- Apply operational rounding, MOQ, or order multiple separately from the raw formula result.
- Return the EOQ result with assumptions and constraints that may invalidate the model.

## Output Checks

- scope and annual demand
- ordering cost and holding cost inputs
- raw EOQ
- rounded or constraint-adjusted order quantity
- assumptions, limits, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- standard EOQ calculation
- holding-rate-derived H
- MOQ or order-multiple adjustment
- invalid zero or negative input rejection

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
