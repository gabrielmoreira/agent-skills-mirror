# Plan Multi Stop Shipment Transportation Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_11_TRANSPORTATION_CORE_READY
```

## Purpose

This reference keeps `plan-multi-stop-shipment` aligned with the AL-11 transportation and freight core and the `transportation-coordinator` skillset.

## Input Checks

- Confirm the request is planning, calculation, comparison, audit support, document interpretation, KPI analysis, or claim preparation, not live tendering or approval.
- Identify whether the work concerns truckload, LTL, parcel, rail, ocean, air, intermodal, domestic, international, or mixed transportation.
- Identify source records for rates, contracts, tariffs, quotes, invoices, BOLs, PODs, manifests, claims, shipment facts, dimensions, weights, accessorials, free time, and carrier performance.
- Preserve missing evidence and source conflicts instead of filling gaps with typical carrier rules.

## Workflow Checks

- Separate truckload, LTL, and parcel reasoning when all three are relevant.
- Keep domestic, international, customs, dangerous-goods, carrier-specific, tariff, contract, insurance, and jurisdiction-specific rules from becoming universal assumptions.
- Calculate only from supplied facts, supplied source rules, or explicitly labeled assumptions.
- Hand off booking, tendering, dispatch, invoice payment, claim filing, customs, dangerous-goods, legal, regulatory, insurance, contract, and safety approvals to qualified reviewers.

## Output Checks

- Include scope, source records, mode, lane, shipment profile, calculations, assumptions, missing evidence, and review boundaries.
- Distinguish recommendations and calculations from live system actions, carrier commitments, legal interpretations, payment approvals, or claim filings.
- Mark regulated, international, hazardous, high-value, customer-critical, financially material, or contractually critical decisions as review-required.
- Preserve enough context for downstream transportation mode, shipment plan, carrier, rate, cost, utilization, consolidation, multi-stop, performance, audit, accessorial, claim, detention, demurrage, BOL, and KPI skills.

## Skillset Handoff

When this skill is used inside `skillsets/transportation-coordinator/`, preserve shipment mode, domestic/international boundary, lane, service window, shipment dimensions, weight, cube, rate basis, carrier evidence, accessorial evidence, document evidence, free-time source, claim evidence, KPI denominator, missing evidence, and qualified-review needs so downstream transportation skills can continue without losing context.
