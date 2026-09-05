# Analyze Stockout Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `analyze-stockout` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- SKU or item-group scope and stockout date or window
- demand, orders, picks, allocations, and backorders during the event window
- on-hand, inventory position, open replenishment, and receipt evidence
- lead time or replenishment promise evidence

## Workflow Checks

- Define the stockout scope, time window, and demand event.
- Build an event timeline from inventory position, orders, allocations, picks, replenishments, and receipts.
- Calculate the quantity gap and identify when available inventory fell below demand.
- Compare actual policy, lead time, and replenishment events to expected behavior.
- Return evidence-ranked causes, prevention checks, and missing evidence.

## Output Checks

- stockout scope and event window
- demand, supply, and allocation timeline
- quantity gap and affected orders
- candidate causes ranked by evidence
- prevention checks, assumptions, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- demand spike stockout
- late replenishment stockout
- allocation-driven stockout
- missing timeline evidence behavior

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
