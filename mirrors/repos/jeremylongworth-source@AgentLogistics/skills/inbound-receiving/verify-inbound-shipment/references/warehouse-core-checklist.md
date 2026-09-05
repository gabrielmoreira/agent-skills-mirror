# Verify Inbound Shipment Warehouse Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_06_WAREHOUSE_CORE_READY
```

## Purpose

This reference keeps `verify-inbound-shipment` aligned with the AL-06 warehouse-operator flow.

## Input Checks

- shipment, receipt, appointment, or inbound process scope.
- PO, ASN, BOL, packing list, label, or source record evidence.
- received goods, item identifiers, quantities, and units.
- condition, exception, hold, or putaway status when relevant.


## Workflow Checks

- Confirm inbound scope and source documents.
- Compare expected, shipped, received, inspected, and accepted facts.
- Identify document, quantity, identity, condition, and status exceptions.
- Route exceptions to hold, recount, discrepancy, or putaway workflow.
- Return the inbound result with evidence gaps and handoff notes.


## Output Checks

- Include the requested verification result.
- Include inputs used, evidence gaps, assumptions, and validation notes.
- Preserve the next warehouse-operator handoff.
- Mark qualified-review requirements when safety or regulated work appears.

## Handoff

When this skill is used inside `skillsets/warehouse-operator/`, preserve process
state, evidence gaps, exceptions, and next required skill so the receive-to-ship
flow can continue without losing context.
