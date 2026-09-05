# Plan Cartonization Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `plan-cartonization` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- order lines with item dimensions, weights, quantities, and units
- available carton set with internal dimensions, usable cube, and weight limits
- packing rules such as orientation, fragile separation, dunnage, stackability, or hazmat exclusion
- output goal such as fewest cartons, lowest cube, weight limit, or pack station readiness

## Workflow Checks

- Confirm item, carton, weight, and dimensional units.
- Check item eligibility and packing restrictions before fit calculations.
- Compare carton candidates by dimensional fit, weight, cube, and packing rules.
- Identify orders that require split cartons, manual review, or special packaging.
- Return carton plan with verification and shipping handoff notes.

## Validation Checks

- item and carton dimensions use compatible units
- weight and cube limits are checked separately
- fragile, orientation, hazardous, temperature, and special-handling rules are preserved
- carrier, dangerous-goods, export, and legal compliance are not claimed

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- single-carton fit
- multi-carton split
- weight-limit exception
- cube-fit caveat for irregular items

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
