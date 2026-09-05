# Calculate Warehouse Capacity Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `calculate-warehouse-capacity` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- building, zone, or storage scope
- dimensions, location counts, pallet positions, cube, or area inputs
- storage method and unit basis
- deductions or constraints such as aisles, docks, offices, obstructions, clearances, and unavailable space

## Workflow Checks

- Confirm capacity scope and unit basis.
- Calculate gross area, cube, positions, or location capacity from supplied dimensions.
- Deduct non-storage and unavailable capacity.
- Apply storage-method or operational constraints separately from gross math.
- Return capacity result with missing inputs and qualified-review requirements.

## Validation Checks

- length, area, cube, position, and count units are not mixed silently
- deductions are named and not double-counted
- target utilization is separate from physical capacity
- structural, floor-load, rack, fire, and code assumptions are review-only

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- area-based warehouse capacity
- cube-based warehouse capacity
- deduction and target utilization
- structural approval boundary

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
