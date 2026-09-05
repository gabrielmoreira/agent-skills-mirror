# Plan Dock Capacity Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `plan-dock-capacity` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- inbound and outbound load volume by period
- average dwell, unload, load, check-in, staging, or turn time
- available dock doors and operating hours
- appointment, labor, yard, staging, or carrier constraints

## Workflow Checks

- Confirm dock scope, load types, and operating period.
- Calculate door-hour demand from load volume and dwell time.
- Compare demand to available door-hours and peak-period capacity.
- Identify constraints from staging, labor, yard, paperwork, and carrier windows.
- Return dock plan, capacity gaps, and safety or site-review boundaries.

## Validation Checks

- time period and dwell-time basis are aligned
- usable doors are separated from total physical doors
- peak and average demand are not blended
- yard, traffic, staging, and safety constraints are visible

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- door-hour calculation
- required door count
- peak overlap constraint
- site safety review boundary

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
