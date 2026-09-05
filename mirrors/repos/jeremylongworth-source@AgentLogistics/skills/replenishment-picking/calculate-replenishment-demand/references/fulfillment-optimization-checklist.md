# Calculate Replenishment Demand Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `calculate-replenishment-demand` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- SKU, pick face, zone, wave, or service-window scope
- forecast demand or released order demand with quantity, unit, and time window
- pick-face on-hand, allocated, held, or unavailable quantity
- replenishment unit, case pack, pallet multiple, or rounding policy

## Workflow Checks

- Confirm demand window, SKU scope, and inventory unit.
- Normalize forecast demand, released demand, pick-face stock, reserve stock, and replenishment unit.
- Calculate gross demand, usable pick-face stock, net replenishment need, and rounded replenishment quantity.
- Compare replenishment quantity to pick-face capacity, reserve availability, labor capacity, and service window.
- Return replenishment demand with shortages, assumptions, and priority handoff.

## Validation Checks

- demand and stock use the same inventory unit or a supplied pack hierarchy
- demand window and service window are aligned
- usable stock exclusions are supported by evidence
- reserve availability and open replenishment are not double-counted

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- same-unit replenishment demand
- case-pack rounding
- capacity overflow warning
- missing pack hierarchy behavior

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
