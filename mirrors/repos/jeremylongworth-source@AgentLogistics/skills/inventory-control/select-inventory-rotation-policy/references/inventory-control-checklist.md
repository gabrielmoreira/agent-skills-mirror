# Select Inventory Rotation Policy Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `select-inventory-rotation-policy` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- SKU or item-group attributes
- age, receipt date, lot, expiration, status, or shelf-life fields that affect rotation
- operational objective such as freshness, age reduction, traceability, service, or storage flow
- constraints such as customer shelf-life rules, holds, or blocked statuses

## Workflow Checks

- Confirm the rotation objective and available control fields.
- Check whether expiry, lot status, quality hold, or customer shelf-life rules override simple age rotation.
- Compare candidate policies such as FIFO, FEFO, lot-specific allocation, and status-first exclusion.
- Define execution controls for receiving, putaway, replenishment, picking, and exception review.
- Return the recommended policy and cases that require owner review.

## Output Checks

- rotation objective and scope
- candidate policy comparison
- selected policy and evidence basis
- execution controls and exception handling
- missing data and review boundaries
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- FIFO selection for non-expiring goods
- FEFO selection for expiry-controlled goods
- status-first exclusion
- system capability gap handling

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
