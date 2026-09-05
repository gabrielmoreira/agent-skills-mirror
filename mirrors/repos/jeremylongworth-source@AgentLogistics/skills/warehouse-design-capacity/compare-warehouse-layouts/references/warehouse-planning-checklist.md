# Compare Warehouse Layouts Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `compare-warehouse-layouts` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- two or more layout alternatives
- comparison criteria such as capacity, travel, throughput, safety, cost, disruption, or expansion
- source assumptions for each alternative
- decision objective and constraints

## Workflow Checks

- Confirm alternatives, decision objective, and criteria.
- Normalize assumptions and metric bases across alternatives.
- Compare capacity, flow, travel, congestion, dock, storage, and expansion implications.
- Call out criteria that need qualified review before selection.
- Return ranked alternatives, tradeoffs, and decision gaps.

## Validation Checks

- all alternatives use comparable assumptions
- weighted criteria are supplied or clearly labeled as draft
- hard constraints are separated from preference scores
- approval-sensitive assumptions remain review-only

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- two-layout comparison
- weighted score with hard constraint
- capacity and travel tradeoff
- missing assumptions behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
