# Analyze Space Utilization Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `analyze-space-utilization` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- facility or zone area measurements and units
- functional area categories such as storage, aisles, receiving, packing, staging, returns, and support space
- occupied and usable area or cube basis
- analysis period or snapshot date

## Workflow Checks

- Confirm facility scope and area or cube basis.
- Classify each area by function and availability.
- Calculate utilization percentages by function and identify constraints.
- Compare space use to throughput, storage, and flow needs when data is supplied.
- Return findings and planning handoffs for zoning, layout, or density work.

## Validation Checks

- area categories sum to the stated scope or differences are explained
- usable and gross areas are not mixed
- unavailable, blocked, and temporary space is separated
- percent denominators are nonzero

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- functional area utilization
- storage occupancy percentage
- gross versus usable area distinction
- missing category behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
