# Forecast Capacity Requirements Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `forecast-capacity-requirements` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- current capacity and current utilization basis
- forecast horizon and growth assumptions
- inventory, order, receipt, throughput, or SKU growth driver
- target utilization or service constraint

## Workflow Checks

- Confirm forecast horizon, growth driver, and capacity basis.
- Normalize current capacity and current demand or inventory baseline.
- Apply growth and peak assumptions to forecast required capacity.
- Compare forecast requirement to effective capacity and identify gap timing.
- Return scenarios, sensitivities, and decision-review boundaries.

## Validation Checks

- forecast horizon and growth period are aligned
- capacity basis matches the forecast driver
- peak and average requirements are not blended
- lease, capex, staffing, and construction decisions remain review-only

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- compound growth forecast
- peak factor forecast
- capacity gap timing
- basis mismatch behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
