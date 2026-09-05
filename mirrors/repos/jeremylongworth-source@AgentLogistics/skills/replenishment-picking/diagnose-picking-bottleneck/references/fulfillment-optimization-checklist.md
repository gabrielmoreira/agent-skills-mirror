# Diagnose Picking Bottleneck Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `diagnose-picking-bottleneck` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- picking process scope and time window
- workload, completed picks, open backlog, or productivity evidence
- labor, equipment, travel, replenishment, congestion, error, or zone evidence
- service impact such as missed cutoff, late wave, or order backlog

## Workflow Checks

- Confirm bottleneck scope, period, and affected service window.
- Map the pick process from release through pick completion and handoff.
- Calculate supported productivity, queue, travel, replenishment, congestion, or error metrics.
- Rank candidate bottleneck drivers by source evidence.
- Return immediate checks, improvement options, and review boundaries.

## Validation Checks

- time window and workload denominator are explicit
- labor hours and system timestamps use the same period
- upstream replenishment and downstream pack or stage constraints are checked
- candidate causes are evidence-ranked

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- low productivity diagnosis
- replenishment-driven pick delay
- congestion bottleneck
- missing labor-hours behavior

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
