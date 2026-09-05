# Plan Zone Picking Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `plan-zone-picking` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- zone map or zone definitions
- order lines by SKU, location, zone, or pick path
- labor, equipment, or capacity by zone
- handoff rule such as pick-and-pass, consolidation, pack handoff, or zone completion

## Workflow Checks

- Confirm zone definitions and eligible order pool.
- Map order lines to zones and identify cross-zone orders.
- Balance workload by zone and service deadline.
- Define handoff, consolidation, exception, and verification rules.
- Return zone plan with capacity gaps and review boundaries.

## Validation Checks

- zones and handoff rules are explicit
- cross-zone orders are identified
- zone labor and equipment capacity are not assumed
- controlled, bulky, fragile, or hazardous items are routed to exceptions when needed

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- pick-and-pass plan
- parallel zone workload balance
- cross-zone order handling
- missing handoff rule behavior

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
