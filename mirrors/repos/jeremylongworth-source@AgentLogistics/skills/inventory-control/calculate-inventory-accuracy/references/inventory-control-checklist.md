# Calculate Inventory Accuracy Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `calculate-inventory-accuracy` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- count scope such as SKU, location, batch, facility, or item group
- system quantity and counted quantity in the same inventory unit
- accuracy tolerance or exact-match rule
- count date or snapshot time

## Workflow Checks

- Confirm the count snapshot and inventory unit.
- Normalize the count scope by SKU, location, status, lot, serial, or expiration where relevant.
- Calculate line variances and classify each line as accurate or inaccurate using the stated tolerance.
- Calculate line accuracy, quantity accuracy, and value-weighted accuracy only from compatible denominators.
- Return the accuracy result with variance drivers, missing evidence, and adjustment-review boundaries.

## Output Checks

- count scope and snapshot time
- accuracy tolerance
- line-level variance table
- line accuracy, quantity accuracy, and value accuracy when supported
- exceptions, assumptions, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- exact-match accuracy
- tolerance-based accuracy
- zero denominator handling
- mixed-unit rejection

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
