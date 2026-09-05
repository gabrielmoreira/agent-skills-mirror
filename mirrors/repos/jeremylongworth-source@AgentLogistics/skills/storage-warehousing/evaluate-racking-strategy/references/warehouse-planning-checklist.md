# Evaluate Racking Strategy Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `evaluate-racking-strategy` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- load profile including pallet dimensions, weight, stackability, and variability
- SKU count, selectivity need, velocity, and storage density objective
- building constraints such as clear height, floor condition, columns, sprinklers, doors, and aisles
- MHE type and turning/access constraints

## Workflow Checks

- Confirm the racking decision is a planning comparison, not an approval.
- Map load, selectivity, density, throughput, and MHE requirements.
- Compare rack families against the supplied requirements and constraints.
- Flag all engineering, code, fire, seismic, floor, permit, and vendor review needs.
- Return a comparison table and next information needed for qualified review.

## Validation Checks

- load and building assumptions are explicit
- selectivity and density tradeoffs are not collapsed into one score
- MHE and aisle assumptions are visible
- engineering, code, fire, seismic, and permit approval are excluded

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- selective rack comparison
- dense rack selectivity tradeoff
- MHE constraint handling
- structural approval boundary

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
