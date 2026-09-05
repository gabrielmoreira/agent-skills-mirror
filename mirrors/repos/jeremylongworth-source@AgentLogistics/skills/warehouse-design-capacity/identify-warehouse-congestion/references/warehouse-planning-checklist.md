# Identify Warehouse Congestion Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `identify-warehouse-congestion` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- congested area or process scope
- volume, queue, delay, equipment, labor, or observation evidence
- time window and operating condition when congestion appears
- layout, zone, dock, aisle, staging, or pick-face context

## Workflow Checks

- Define congestion scope and observation window.
- Separate physical blockage, queue delay, equipment conflict, labor imbalance, and process handoff issues.
- Quantify congestion severity when volumes, queue lengths, delays, or utilization values are supplied.
- Rank candidate drivers by evidence strength.
- Return actions, missing evidence, and safety-review boundaries.

## Validation Checks

- time window and operating condition are identified
- congestion evidence is separated from assumptions
- candidate causes are evidence-ranked
- safety-sensitive traffic or blocked egress concerns are escalated

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- dock queue congestion
- pick-face congestion
- equipment path conflict
- safety escalation boundary

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
