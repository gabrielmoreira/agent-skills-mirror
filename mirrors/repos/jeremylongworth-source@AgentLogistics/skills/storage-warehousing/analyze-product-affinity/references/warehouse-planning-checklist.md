# Analyze Product Affinity Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `analyze-product-affinity` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- order-line, pick-line, basket, or shipment history for the analysis period
- SKU identifiers and product group fields
- current locations or planned slotting context
- analysis objective such as reduced travel, fewer splits, or better zone grouping

## Workflow Checks

- Confirm the transaction population and period.
- Build SKU pair or group co-occurrence counts from the supplied order or pick data.
- Calculate affinity metrics where denominators are valid.
- Identify placement implications and conflicts with velocity, weight, cube, or control constraints.
- Return affinity groups, caveats, and slotting handoff notes.

## Validation Checks

- order or pick population is defined
- SKU IDs are consistent across lines
- low-count pairings are flagged as weak evidence
- affinity recommendations do not override safety, weight, expiration, or controlled-inventory constraints

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- co-order pair frequency
- support and confidence calculation
- low-sample warning
- affinity versus weight constraint

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
