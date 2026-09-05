# Plan Warehouse Expansion Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `plan-warehouse-expansion` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- current capacity and forecast capacity requirement
- capacity gap, horizon, or growth trigger
- constraints such as building, lease, operations, staffing, service, storage, and implementation disruption
- candidate options or permission to generate planning options

## Workflow Checks

- Confirm expansion driver, horizon, and capacity basis.
- Quantify the gap between forecast requirement and effective capacity.
- Generate or compare expansion options from lowest disruption to larger footprint change.
- Identify phasing, operational risk, and review requirements.
- Return an expansion planning brief without lease, capital, construction, or engineering approval.

## Validation Checks

- forecast and capacity use the same unit basis
- near-term operational options are separated from capital or lease commitments
- phasing and service disruption are visible
- engineering, permitting, lease, capex, and construction approvals are excluded

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- capacity-gap expansion brief
- density option versus new space
- growth sensitivity
- approval boundary for capex and construction

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
