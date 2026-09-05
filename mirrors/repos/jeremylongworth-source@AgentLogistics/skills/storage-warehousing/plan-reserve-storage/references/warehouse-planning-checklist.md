# Plan Reserve Storage Warehouse Planning Checklist

Completion token:

```text
AGENTLOGISTICS_AL_08_WAREHOUSE_PLANNING_READY
```

## Purpose

This reference keeps `plan-reserve-storage` aligned with the AL-08 warehouse-planner foundation and the `warehouse-planner` skillset.

## Input Checks

- warehouse, zone, storage area, SKU group, flow, or planning scope
- source records, assumptions, and unit basis for any quantity, space, cube, distance, or time value
- inventory profile by SKU, load unit, quantity, velocity, and storage requirement
- reserve storage area, location type, or capacity evidence
- replenishment need or forward-pick relationship
- movement, accessibility, rotation, and control requirements

## Workflow Checks

- Confirm reserve scope and which inventory is excluded from forward pick.
- Classify reserve inventory by storage requirement, movement frequency, and control attribute.
- Compare reserve demand to location, pallet, cube, or position capacity.
- Define replenishment triggers and handoffs to forward pick.
- Return reserve placement rules, capacity gaps, and review needs.

## Validation Checks

- reserve and forward-pick quantities are not double-counted
- storage requirement and control attributes are preserved
- capacity basis is named before calculations
- replenishment triggers are separated from storage placement rules

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve capacity, cube, density, slotting, zoning, congestion, and layout constraints when relevant.
- Keep conceptual planning separate from engineering, code, rack, floor, fire, permit, and safety approval.

## Acceptance Checks

- reserve versus forward allocation
- reserve capacity gap
- controlled-inventory placement rule
- missing replenishment cadence behavior

## Handoff

When this skill is used inside `skillsets/warehouse-planner/`, preserve the facility scope, area or cube basis, product and order profile, storage method assumptions, capacity limits, congestion evidence, and qualified-review needs so downstream planning skills can continue without losing context.
