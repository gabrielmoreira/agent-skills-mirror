# Optimize Storage Density Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `optimize-storage-density` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- current capacity and occupied inventory by position, location, cube, or area
- storage method and access requirements
- SKU mix, load profile, movement frequency, and handling constraints
- growth, service, selectivity, or target utilization objective

## Workflow Checks

- Confirm density objective and current utilization basis.
- Identify constraints that limit practical density.
- Generate density options such as consolidation, slotting, alternative storage method, reserve policy, or layout changes.
- Estimate capacity impact and tradeoffs where data supports it.
- Return ranked options with qualified-review boundaries.

## Validation Checks

- current and proposed capacity use the same basis
- selectivity and accessibility tradeoffs are stated
- handling, rack, floor, fire, and egress assumptions are not approved by the skill
- growth and peak profiles are considered when supplied

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- position-density improvement
- cube-density tradeoff
- selectivity constraint
- qualified-review boundary for dense rack options

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
