# Calculate Safety Stock Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `calculate-safety-stock` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- selected safety-stock method or source policy
- average demand and demand time unit when method uses demand
- lead time and lead-time unit when method uses lead time
- variability inputs and service factor when a statistical method is requested

## Workflow Checks

- Identify the safety-stock method requested or supplied by policy.
- Normalize demand, lead time, and variability units.
- Check that the method's required variables are present before calculating.
- Calculate safety stock and report intermediate values.
- Return method limits, sensitivity notes, and how the result may feed reorder point or min-max policy.

## Output Checks

- method and source policy
- input values and normalized units
- intermediate variability or max-average terms
- raw and rounded safety stock
- assumptions, sensitivity, and review requirements
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- fixed safety-stock policy
- average-maximum method
- demand-variability method
- missing service-factor behavior

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
