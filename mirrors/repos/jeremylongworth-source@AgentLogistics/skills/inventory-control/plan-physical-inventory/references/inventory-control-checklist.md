# Plan Physical Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `plan-physical-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- facility, zone, SKU, status, or location count scope
- planned count date and operating freeze window
- source system balance snapshot time
- count method, count team capacity, and reconciliation owner

## Workflow Checks

- Define scope, system snapshot, and freeze boundary.
- Map pre-count cleanup, open transaction closure, count execution, recount, reconciliation, and restart steps.
- Assign count zones, roles, evidence records, and escalation points.
- Estimate count workload and compare it to labor and time windows when productivity data is available.
- Return an event plan with controls that prevent transaction leakage and unsupported adjustments.

## Output Checks

- scope, date, snapshot, and freeze rules
- pre-count readiness checklist
- count execution and recount plan
- reconciliation and adjustment-review workflow
- restart criteria and unresolved risks
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- full facility count plan
- zone-limited physical inventory
- open transaction exception handling
- missing freeze window behavior

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
