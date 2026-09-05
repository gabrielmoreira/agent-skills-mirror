# Prioritize Replenishment Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `prioritize-replenishment` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- replenishment task list or SKU/location demand list
- pick-face stock status, demand due, and service deadline
- reserve availability and replenishment path or source location
- labor, equipment, cutoff, or operating constraint that affects priority

## Workflow Checks

- Confirm priority objective and service window.
- Calculate or accept stockout risk, demand due, and replenishment need for each task.
- Score urgency using supplied service, demand, labor, equipment, and reserve constraints.
- Separate blocked tasks from executable tasks.
- Return a priority queue with rationale, exceptions, and escalation needs.

## Validation Checks

- priority criteria are stated before ranking
- blocked or unavailable reserve stock is not treated as executable
- labor and equipment constraints are visible
- customer, route, or service-risk flags are evidence-based

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- deadline-driven priority queue
- stockout-risk priority queue
- blocked reserve task handling
- missing scoring weights behavior

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
