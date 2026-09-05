# Select Picking Strategy Warehouse Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_06_WAREHOUSE_CORE_READY
```

## Purpose

This reference keeps `select-picking-strategy` aligned with the AL-06 warehouse-operator flow.

## Input Checks

- order, SKU, pick-face, replenishment, or picking scope.
- demand, inventory, order profile, labor, equipment, or method data.
- locations, units, service window, and status constraints.
- output needed: plan, strategy, priority, or metric.


## Workflow Checks

- Confirm demand window, item scope, and process boundary.
- Normalize units, statuses, and order or inventory definitions.
- Compare need, method, capacity, and service constraints.
- Identify shortages, congestion, errors, and missing evidence.
- Return the plan, strategy, or metric with assumptions and handoff notes.


## Output Checks

- Include the requested picking strategy recommendation.
- Include inputs used, evidence gaps, assumptions, and validation notes.
- Preserve the next warehouse-operator handoff.
- Mark qualified-review requirements when safety or regulated work appears.

## Handoff

When this skill is used inside `skillsets/warehouse-operator/`, preserve process
state, evidence gaps, exceptions, and next required skill so the receive-to-ship
flow can continue without losing context.
