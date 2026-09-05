# Calculate Storage Capacity Warehouse Core Checklist

Completion token:

```text
AGENTLOGISTICS_AL_06_WAREHOUSE_CORE_READY
```

## Purpose

This reference keeps `calculate-storage-capacity` aligned with the AL-06 warehouse-operator flow.

## Input Checks

- storage area, SKU, load, or location scope.
- dimensions, units, status, capacity, or storage-method data.
- handling, access, rotation, or control requirements.
- constraints that affect storage eligibility or capacity.


## Workflow Checks

- Confirm storage scope and unit basis.
- Normalize dimensions, counts, statuses, and location terms.
- Classify storage requirements or calculate capacity where applicable.
- Flag constraints, blocked capacity, and review boundaries.
- Return storage findings with assumptions and next actions.


## Output Checks

- Include the requested storage capacity calculation.
- Include inputs used, evidence gaps, assumptions, and validation notes.
- Preserve the next warehouse-operator handoff.
- Mark qualified-review requirements when safety or regulated work appears.

## Handoff

When this skill is used inside `skillsets/warehouse-operator/`, preserve process
state, evidence gaps, exceptions, and next required skill so the receive-to-ship
flow can continue without losing context.
