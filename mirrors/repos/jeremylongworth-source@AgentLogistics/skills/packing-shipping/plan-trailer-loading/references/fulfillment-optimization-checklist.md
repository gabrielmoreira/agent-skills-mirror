# Plan Trailer Loading Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `plan-trailer-loading` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- shipment, pallet, carton, or load list with dimensions, weight, and units
- trailer or container dimensions, usable space, and stated capacity limits
- route, stop sequence, delivery priority, or unload constraints
- equipment, dock, staging, and loading window constraints

## Workflow Checks

- Confirm trailer scope, units, and loading objective.
- Check shipment eligibility, dimensions, weights, stop sequence, and special handling constraints.
- Estimate cube, floor position, and weight use from supplied data.
- Sequence load by stop, stability, accessibility, and operational constraints.
- Return a loading plan with unresolved safety and compliance review points.

## Validation Checks

- trailer and load units are compatible
- stop sequence and accessibility constraints are preserved
- cube, floor, and weight limits are checked separately
- load securement, axle, legal weight, and safety compliance are qualified-review items

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- cube and weight utilization
- multi-stop load sequence
- oversize pallet exception
- load-securement approval boundary

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
