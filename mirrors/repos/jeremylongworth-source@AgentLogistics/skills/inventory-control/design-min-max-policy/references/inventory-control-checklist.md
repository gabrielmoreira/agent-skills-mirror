# Design Min Max Policy Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `design-min-max-policy` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- item or item-group scope and inventory unit
- average demand rate and demand time basis
- replenishment lead time
- safety stock or approved safety-stock method
- review cadence or order cycle policy for the maximum level

## Workflow Checks

- Confirm the item scope, inventory unit, and planning period.
- Calculate or accept the minimum level from lead-time demand plus safety stock.
- Calculate the maximum level from min plus cycle stock or demand through the review period.
- Apply MOQ, order multiple, storage, and shelf-life constraints as separate operating adjustments.
- Return policy settings with trigger logic, ordering logic, assumptions, and review boundaries.

## Output Checks

- policy scope and planning basis
- minimum level and calculation
- maximum or order-up-to level and calculation
- order constraints and rounded operating values
- review cadence, assumptions, and approval boundary
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- min from reorder point
- max from review-period demand
- MOQ and order-multiple adjustment
- max below min exception

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
