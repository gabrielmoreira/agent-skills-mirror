# Identify Logistics Constraints Warehouse Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_06_WAREHOUSE_CORE_READY
```

## Purpose

This reference keeps `identify-logistics-constraints` aligned with the AL-06 warehouse-operator flow.

## Input Checks

- process or operation boundary.
- source records or observed facts.
- products, orders, locations, systems, and handoffs involved.
- service commitments, constraints, or decision needed.


## Workflow Checks

- Confirm the operation boundary and planning horizon.
- Separate observed facts, assumptions, and missing evidence.
- Structure the goods, information, system, and handoff flow.
- Identify constraints, risks, and downstream skills needed.
- Return the requested assessment with validation notes.


## Output Checks

- Include the requested constraint register.
- Include inputs used, evidence gaps, assumptions, and validation notes.
- Preserve the next warehouse-operator handoff.
- Mark qualified-review requirements when safety or regulated work appears.

## Handoff

When this skill is used inside `skillsets/warehouse-operator/`, preserve process
state, evidence gaps, exceptions, and next required skill so the receive-to-ship
flow can continue without losing context.
