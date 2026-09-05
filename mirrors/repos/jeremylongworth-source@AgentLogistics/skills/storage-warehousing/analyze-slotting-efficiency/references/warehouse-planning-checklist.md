# Analyze Slotting Efficiency Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `analyze-slotting-efficiency` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- pick activity by SKU, location, zone, order line, or period
- location assignments and capacity attributes
- travel, replenishment, congestion, or productivity evidence
- analysis period and operating process context

## Workflow Checks

- Confirm the period, location map, and current slot assignments.
- Calculate supported metrics for travel, picks, cube, replenishment, or congestion.
- Identify mismatches between SKU velocity and slot accessibility.
- Rank improvement candidates by evidence and operational impact.
- Return metrics, causes, recommended checks, and implementation boundaries.

## Validation Checks

- pick activity period and location assignments align
- travel distance basis is documented
- replenishment and pick transactions are not double-counted
- metric denominators are nonzero and unit-compatible

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- travel-distance-per-pick calculation
- fast mover in remote slot finding
- replenishment-heavy pick face
- missing coordinate behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
