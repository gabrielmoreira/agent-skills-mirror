# Analyze Pick Accuracy Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `analyze-pick-accuracy` aligned with the AL-09 fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- facility, wave, order pool, zone, SKU, shipment, or fulfillment scope
- source records, timestamps, units, and status fields used for the work
- pick or audit population and time period
- ordered quantity and picked or audited quantity by line
- error definitions such as wrong item, wrong quantity, short, over, damage, or substitution
- scope such as SKU, zone, picker, shift, method, or customer channel

## Workflow Checks

- Confirm audit scope, period, and error definitions.
- Compare ordered, picked, audited, packed, or claimed values by line.
- Calculate line accuracy, quantity accuracy, and error rate only from compatible denominators.
- Segment errors by SKU, location, zone, picker, shift, method, and order profile when fields are present.
- Return patterns, likely process handoffs, and review boundaries.

## Validation Checks

- audit population and denominator are explicit
- error categories are defined before classification
- claims, returns, and audit evidence are not blended without source labels
- sample size and bias are visible

## Output Checks

- Include scope, source records, unit basis, assumptions, missing evidence, and review boundaries.
- Preserve order profile, replenishment, picking, packing, staging, loading, shipping, and service-window constraints when relevant.
- Keep optimization recommendations separate from system changes, carrier claims, load-securement approvals, financial approvals, and safety decisions.

## Acceptance Checks

- line accuracy calculation
- quantity accuracy calculation
- error segmentation
- unaudited denominator warning

## Handoff

When this skill is used inside `skillsets/fulfillment-optimizer/`, preserve the order profile, demand window, inventory readiness, pick method, labor and equipment constraints, pack and stage capacity, shipment handoff, exceptions, and qualified-review needs so downstream fulfillment skills can continue without losing context.
