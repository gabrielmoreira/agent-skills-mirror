# Design Cycle Count Program Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `design-cycle-count-program` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- inventory classes or classification basis
- SKU, location, or item-group population to count
- available count capacity by day, week, or period
- target count frequency or accuracy objective

## Workflow Checks

- Confirm the count population and classification inputs.
- Assign count frequency by class, risk, value, movement, or control requirement.
- Estimate count workload and compare it to available count capacity.
- Define count selection, blind count, recount, reconciliation, and adjustment-review controls.
- Return a count calendar or scheduling rule with assumptions and capacity gaps.

## Output Checks

- program scope and count population
- frequency by class or risk group
- count workload and capacity comparison
- count controls, reconciliation path, and review boundaries
- implementation notes and missing inputs
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- ABC frequency schedule
- capacity-constrained count plan
- missing classification behavior
- controlled-inventory escalation

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
