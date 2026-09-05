# Identify Dead Stock Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `identify-dead-stock` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- dead-stock policy threshold or no-demand period
- demand or movement history for the analysis period
- on-hand quantity and inventory unit
- SKU, item group, location, or status scope

## Workflow Checks

- Confirm the policy threshold and analysis period.
- Calculate no-demand or no-movement age from the chosen evidence date.
- Exclude or flag inventory with known future demand, holds, projects, or active commitments.
- Estimate value exposure when cost is available.
- Return candidate list with evidence and required business review before disposition.

## Output Checks

- analysis scope and threshold
- dead-stock candidate table
- evidence fields and exclusions
- quantity and value exposure
- recommended review path and missing inputs
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- no-move candidate identification
- future-demand exclusion
- missing threshold behavior
- write-off approval boundary

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
