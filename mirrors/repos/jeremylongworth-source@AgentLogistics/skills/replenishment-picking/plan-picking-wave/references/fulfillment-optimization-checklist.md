# Plan Picking Wave Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `plan-picking-wave` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- order pool with service deadlines, cutoffs, order lines, units, or routes
- labor, equipment, zone, or pick-method capacity
- replenishment readiness and inventory availability
- wave objective such as ship cutoff, productivity, congestion control, or priority service

## Workflow Checks

- Confirm order pool, service windows, and release objective.
- Segment orders by cutoff, route, carrier, zone, pick method, and readiness.
- Estimate workload and compare it to labor, equipment, replenishment, pack, and stage capacity.
- Identify orders that should be held, split, expedited, or released later.
- Return the wave plan with release checks and handoffs.

## Validation Checks

- order cutoff and wave time window are explicit
- released and held orders are separated
- inventory and replenishment readiness are checked before release
- labor and equipment capacity use compatible time units

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- carrier-cutoff wave
- capacity-limited wave
- replenishment-not-ready hold
- mixed-method order pool

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
