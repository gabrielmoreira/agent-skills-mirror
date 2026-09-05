# Investigate Picking Error Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `investigate-picking-error` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- order, line, SKU, location, and error scope
- ordered, picked, packed, shipped, or audited evidence
- scanner, WMS, pick ticket, or operator event history
- time window and process handoff points

## Workflow Checks

- Freeze the order line, SKU, location, and event time window.
- Build a source-by-source evidence table for order, pick, scan, pack, ship, and customer records.
- Order events into a chronology and identify the first conflicting handoff.
- Rank candidate causes by cited evidence rather than confidence.
- Return missing evidence, containment checks, and corrective-action handoffs.

## Validation Checks

- order, pick, pack, ship, and claim sources are separated
- chronology is built before candidate causes
- quantity and SKU identity evidence use compatible units and identifiers
- personnel conclusions are excluded without qualified investigation

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- wrong-SKU investigation
- short-pick investigation
- pack-versus-pick source conflict
- no guessed personnel fault

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
