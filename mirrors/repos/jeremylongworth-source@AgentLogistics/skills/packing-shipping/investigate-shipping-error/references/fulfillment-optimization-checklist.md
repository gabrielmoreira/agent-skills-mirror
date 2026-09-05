# Investigate Shipping Error Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `investigate-shipping-error` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- order, shipment, carton, pallet, label, or tracking scope
- order, pick, pack, label, manifest, scan, carrier, delivery, or customer evidence
- time window and handoff points from pack through carrier pickup or delivery
- reported error type and service impact

## Workflow Checks

- Freeze the shipment scope and reported error.
- Build a source-by-source evidence table for order, pick, pack, label, staging, load, carrier, and customer records.
- Order events into a chronology and identify the first unsupported or conflicting handoff.
- Rank candidate causes by cited evidence strength.
- Return missing evidence, containment checks, customer or carrier handoffs, and review boundaries.

## Validation Checks

- warehouse and carrier handoff evidence are separated
- labels, tracking, manifest, BOL, and proof-of-delivery evidence are not treated as interchangeable
- chronology is built before candidate causes
- customer, carrier, claim, credit, and legal decisions remain review-only

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- wrong-label investigation
- short-shipment investigation
- carrier handoff conflict
- claim liability boundary

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
