# Classify Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `classify-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- SKU or item-group list with item identifiers and units
- classification basis such as demand, value, criticality, control attribute, or operational risk
- time period used for demand or movement evidence when velocity is part of the classification

## Workflow Checks

- Normalize SKU identifiers, units, and the classification period.
- Choose the classification dimensions supported by the available evidence.
- Calculate value, velocity, or risk bands only when the source fields are present.
- Separate policy classes such as ABC, fast/medium/slow mover, critical item, controlled item, and dead-stock candidate.
- Return a matrix that maps each class to count cadence, planning priority, review trigger, and evidence gaps.

## Output Checks

- classification basis and period
- SKU or item-group classification table
- calculated value or movement fields when available
- policy implications for counts, replenishment, and review
- assumptions, missing fields, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- ABC classification with complete usage and cost data
- velocity classification with a named time period
- missing threshold behavior
- controlled-inventory flag preservation

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
