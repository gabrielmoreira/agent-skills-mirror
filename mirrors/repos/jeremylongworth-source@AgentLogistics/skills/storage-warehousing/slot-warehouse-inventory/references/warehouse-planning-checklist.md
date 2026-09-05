# Slot Warehouse Inventory Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `slot-warehouse-inventory` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- SKU list with velocity, demand, order lines, cube, weight, or handling attributes
- available locations with capacity, zone, equipment, and access attributes
- slotting objective such as travel reduction, capacity balance, replenishment reduction, or affinity placement
- constraints such as heavy-item placement, temperature, lot, serial, expiration, hazard, or security controls

## Workflow Checks

- Confirm the slotting objective and source data period.
- Classify SKUs by velocity, cube, weight, pick unit, control need, and affinity.
- Match SKU requirements to location capacity, access, zone, and handling attributes.
- Rank candidate moves by expected benefit, risk, and implementation burden.
- Return slot assignments, constraints, and validation checks before execution.

## Validation Checks

- SKU and location units are compatible
- fast movers, heavy items, controlled items, and high-cube items are not ranked on one factor only
- location capacity and access constraints are checked
- travel and affinity claims are tied to data

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- fast-mover near-pack placement
- heavy-item ergonomic constraint
- affinity placement tradeoff
- missing location capacity behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
