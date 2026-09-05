# Plan Forward Pick Storage Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `plan-forward-pick-storage` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- SKU velocity, order lines, picks, units, or demand by SKU
- pick-face capacity by unit, case, carton, pallet, or cube
- replenishment frequency or review cadence
- location constraints such as ergonomics, weight, cube, temperature, lot, serial, or expiration controls

## Workflow Checks

- Confirm the active SKU population and velocity basis.
- Rank SKUs by pick frequency, unit volume, cube, or service risk using supplied data.
- Size pick faces from expected demand between replenishments plus buffer policy.
- Check capacity, replenishment workload, ergonomics, and control constraints.
- Return forward-pick assignments and reserve handoff rules.

## Validation Checks

- velocity period and replenishment interval are aligned
- capacity per face uses the same unit as required quantity
- heavy, fragile, hazardous, expiration, and controlled items are flagged
- face sizing does not assume replenishment labor is available unless supplied

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- fast-mover face sizing
- case-to-each conversion gap
- replenishment frequency tradeoff
- controlled-item forward-pick boundary

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
