# Plan Shipping Stage Warehouse Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_06_WAREHOUSE_CORE_READY
```

## Purpose

This reference keeps `plan-shipping-stage` aligned with the AL-06 warehouse-operator flow.

## Input Checks

- order, shipment, carrier, route, packing, staging, or outbound scope.
- picked or packed contents, labels, documents, and status evidence.
- cutoffs, staging capacity, carrier handoff, or verification requirements.
- exceptions, holds, or review flags when present.


## Workflow Checks

- Confirm outbound scope, service window, and shipment status.
- Compare order, pick, pack, label, document, and staging evidence.
- Identify ready, hold, mismatch, missing-evidence, or review-required work.
- Plan or verify handoff to staging, dock, carrier, or exception workflow.
- Return outbound result with assumptions, risks, and next action.


## Output Checks

- Include the requested shipping staging plan.
- Include inputs used, evidence gaps, assumptions, and validation notes.
- Preserve the next warehouse-operator handoff.
- Mark qualified-review requirements when safety or regulated work appears.

## Handoff

When this skill is used inside `skillsets/warehouse-operator/`, preserve process
state, evidence gaps, exceptions, and next required skill so the receive-to-ship
flow can continue without losing context.
