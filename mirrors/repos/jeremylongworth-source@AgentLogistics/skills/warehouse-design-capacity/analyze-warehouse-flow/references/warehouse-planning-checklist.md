# Analyze Warehouse Flow Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `analyze-warehouse-flow` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- current or proposed layout context
- process steps, movement paths, handoffs, and source or destination areas
- product, order, equipment, and labor flow evidence
- observed delays, crossings, congestion, or service constraints

## Workflow Checks

- Confirm process boundary and flow direction.
- Map product, people, equipment, and information handoffs.
- Identify crossings, backtracking, bottlenecks, queues, and control breaks.
- Quantify travel, touches, or delay only when source data supports it.
- Return flow findings and handoffs to zoning, congestion, slotting, or layout planning.

## Validation Checks

- process boundary and path assumptions are explicit
- layout observations are separated from calculated metrics
- cross-traffic and safety-sensitive flow issues are escalated for site review
- future-state recommendations are tied to constraints

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- receive-to-ship flow map
- cross-traffic identification
- travel metric with supplied distances
- missing layout evidence behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
