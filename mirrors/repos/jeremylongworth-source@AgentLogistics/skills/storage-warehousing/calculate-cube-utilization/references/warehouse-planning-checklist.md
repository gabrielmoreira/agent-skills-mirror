# Calculate Cube Utilization Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `calculate-cube-utilization` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- usable cube or the dimensions needed to calculate it
- occupied cube or SKU/load dimensions and quantities
- unit basis for length, volume, quantity, and storage scope
- exclusions such as aisles, clearance, unusable height, blocked areas, or non-storage zones

## Workflow Checks

- Confirm the storage scope and cube unit.
- Calculate or accept usable cube after named exclusions.
- Calculate occupied cube from load dimensions and quantities.
- Calculate utilization and separate raw cube from operationally usable cube.
- Return the calculation with constraints that affect practical storage use.

## Validation Checks

- length and volume units are compatible
- usable cube denominator is positive
- excluded cube is named and not double-counted
- pallet, case, and each conversions use supplied pack hierarchy

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- straight cube utilization calculation
- unit-conversion example
- excluded-cube deduction
- missing pack hierarchy behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
