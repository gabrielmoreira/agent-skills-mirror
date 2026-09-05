# Reconcile Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `reconcile-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- item, location, lot, serial, status, or count scope
- system balance snapshot and physical count result
- transaction cutoff time and known transactions around the count
- variance tolerance or escalation rule

## Workflow Checks

- Confirm the reconciliation scope, snapshot, and transaction cutoff.
- Normalize count and system units, status, lot, serial, and location fields.
- Calculate variance by line and value exposure when supported.
- Bridge system balance to physical count using known transactions and adjustments.
- Return reconciled lines, unresolved conflicts, and adjustment-review requirements.

## Output Checks

- reconciliation scope and cutoff
- line variance table
- balance bridge when transaction data is available
- proposed reason categories and unresolved conflicts
- adjustment-review packet and missing evidence
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- system-to-count reconciliation
- balance bridge with receipts and issues
- unit mismatch rejection
- adjustment approval boundary

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
