# Manage Lot Controlled Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `manage-lot-controlled-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- lot IDs or batch IDs
- SKU, quantity, unit, location, and status for each lot
- movement, receipt, shipment, adjustment, or count event being reviewed
- traceability objective such as reconcile, rotate, hold, release, or investigate

## Workflow Checks

- Confirm lot scope, SKU, unit, status, and location granularity.
- Trace each lot through receipts, moves, counts, picks, shipments, returns, and adjustments.
- Reconcile lot quantities to item-level and location-level balances.
- Identify holds, status conflicts, mixed lots, missing traceability, or rotation risks.
- Return a lot-control action packet without releasing or approving controlled stock.

## Output Checks

- lot scope and source records
- lot balance and status table
- movement trace or reconciliation notes
- holds, conflicts, missing evidence, and next checks
- qualified-review boundaries
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- lot movement trace
- lot balance reconciliation
- status conflict handling
- quality release boundary

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
