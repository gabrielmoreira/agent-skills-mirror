# Optimize Pick Path Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `optimize-pick-path` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- pick list, order lines, or SKU-location sequence to route
- location map, coordinates, aisle sequence, or travel-distance basis
- constraints such as zones, equipment, one-way aisles, heavy items, batch rules, or priority stops
- objective such as shortest travel, fewer touches, safer sequence, or better zone handoff

## Workflow Checks

- Confirm the routing scope, location basis, and movement constraints.
- Validate that all pick locations can be mapped.
- Sequence picks using the simplest method supported by the data and constraints.
- Compare travel or handling impact against a baseline when supplied.
- Return route recommendation, assumptions, exceptions, and safety boundaries.

## Validation Checks

- all pick locations resolve to the map or distance basis
- constraints are applied before distance minimization
- heavy, fragile, hazardous, equipment, and traffic constraints are visible
- baseline and proposed distances use the same method

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- route sequence from location list
- baseline versus proposed travel distance
- unmapped location exception
- safety constraint overriding shortest path

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
