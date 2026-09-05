# Plan Warehouse Zones Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `plan-warehouse-zones` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- processes that need zones and their flow sequence
- facility dimensions or available area by function
- SKU, order, equipment, and handling requirements that affect zoning
- constraints such as docks, columns, doors, offices, utilities, traffic, and safety review points

## Workflow Checks

- Confirm process scope and flow sequence.
- List required zones and adjacency priorities.
- Allocate zones using capacity, handling, traffic, and handoff requirements.
- Identify congestion, crossing, and expansion constraints.
- Return zoning concept, alternatives, and review needs.

## Validation Checks

- zone functions and adjacencies match the process flow
- inbound, outbound, returns, storage, and support conflicts are visible
- MHE and pedestrian paths are treated as constraints
- approval-sensitive building and safety assumptions are flagged

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- receiving-to-storage adjacency
- pick-pack-stage zoning
- returns isolation need
- approval boundary for layout safety

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
