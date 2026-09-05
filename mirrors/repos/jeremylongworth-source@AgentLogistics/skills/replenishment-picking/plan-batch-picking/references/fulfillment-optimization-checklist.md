# Plan Batch Picking Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `plan-batch-picking` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- order lines with SKU, quantity, unit, and order identifier
- batching objective such as travel reduction, common SKU picks, or cutoff grouping
- container, tote, cart, or batch capacity
- sort or put-wall method for separating orders after batch pick

## Workflow Checks

- Confirm batch-picking objective and eligible order pool.
- Group lines by common SKU, location, zone, route, carrier, or cutoff using supplied criteria.
- Check container capacity, sort method, and accuracy controls.
- Identify exclusions such as bulky, fragile, high-value, hazardous, or controlled items.
- Return batch groups with pick, sort, and verification handoffs.

## Validation Checks

- each batched line remains traceable to its customer order
- container capacity and sort method are sufficient for the batch
- cutoff, priority, and controlled-item exclusions are respected
- batch savings are not claimed without comparable baseline data

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- common-SKU batch plan
- container-capacity constraint
- sort-method missing behavior
- controlled-item exclusion

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
