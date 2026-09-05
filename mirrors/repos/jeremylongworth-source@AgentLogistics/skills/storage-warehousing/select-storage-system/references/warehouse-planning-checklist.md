# Select Storage System Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `select-storage-system` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- SKU or load profile including unit dimensions, weight, stackability, and handling requirements
- velocity, order profile, or access-frequency evidence
- building or area constraints such as footprint, clear height, docks, columns, and obstructions
- service, selectivity, storage-density, or cost objective

## Workflow Checks

- Confirm the storage scope, load unit, and operating objective.
- Classify product and storage requirements before comparing systems.
- Compare feasible systems against selectivity, density, throughput, access, handling, and risk criteria.
- Name assumptions and constraints that require engineering, fire, rack, safety, or vendor review.
- Return a ranked recommendation matrix and next planning checks.

## Validation Checks

- load dimensions, weights, and storage units are stated
- building constraints and access requirements are identified
- comparison criteria and weights are visible when scoring is used
- safety, rack, fire, floor, and code assumptions are flagged for qualified review

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- selective rack versus bulk floor comparison
- high-SKU selectivity tradeoff
- dense storage with access constraint
- qualified-review boundary for rack and building assumptions

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
