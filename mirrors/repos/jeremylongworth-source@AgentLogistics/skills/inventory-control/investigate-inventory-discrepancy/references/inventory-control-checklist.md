# Investigate Inventory Discrepancy Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `investigate-inventory-discrepancy` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- SKU, location, status, lot, serial, or other exact discrepancy scope
- receiving quantity or receipt evidence
- WMS or ERP balance snapshot
- physical count or recount result
- picking, shipment, transfer, and adjustment history for the investigation period

## Workflow Checks

- Freeze the investigation scope, time window, system snapshot, and physical count evidence.
- Build a source-by-source evidence table for receiving quantity, WMS balance, physical count, picking transactions, and adjustment history.
- Order receipts, putaway, moves, picks, shipments, transfers, counts, and adjustments into a chronology.
- Build a quantity bridge from starting balance through known transactions to expected ending balance.
- List every unresolved conflict and rank candidate causes only by cited evidence strength.
- Return missing evidence, controls to protect the record, and reviewer actions before adjustment or process change.

## Output Checks

- investigation scope and time window
- source-by-source evidence table
- transaction chronology
- quantity reconciliation bridge
- conflict list and evidence-ranked candidate causes
- missing evidence, next checks, and adjustment-review boundary
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- conflicting receiving, WMS, physical count, picking, and adjustment evidence
- missing evidence behavior
- unit or status mismatch rejection
- no guessed root-cause invariant

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
