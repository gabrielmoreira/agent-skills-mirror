# Analyze Inventory Shrinkage Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `analyze-inventory-shrinkage` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- analysis period and inventory scope
- book inventory, verified physical count, or approved variance records
- adjustment history and reason codes
- SKU, location, status, or category fields for pattern analysis

## Workflow Checks

- Confirm the shrinkage period, scope, and source records.
- Calculate shrinkage quantity or value only from verified variance or adjustment evidence.
- Segment shrinkage by SKU, location, status, reason code, process area, and time period when fields are present.
- Check for data-quality, receiving, picking, damage, return, and adjustment patterns before ranking candidate causes.
- Return controls, missing evidence, and escalation boundaries without accusations.

## Output Checks

- scope and analysis period
- shrinkage quantity, value, and rate when supported
- segmentation by SKU, location, reason code, or time
- evidence-ranked candidate causes and controls
- missing evidence and escalation boundaries
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- quantity shrinkage calculation
- value shrinkage rate
- single-variance routing to investigation
- non-accusatory suspected-loss handling

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
