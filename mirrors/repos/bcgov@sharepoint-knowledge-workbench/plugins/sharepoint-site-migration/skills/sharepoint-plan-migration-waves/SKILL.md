---
name: sharepoint-plan-migration-waves
plugin: sharepoint-site-migration
description: Computes a deployment wave plan by topologically sorting a caller-supplied, dependency-annotated list of deployment objects, grouping them into ordered stages where every dependency is satisfied by a strictly earlier stage, and honestly reporting cycles or unresolved dependencies instead of guessing an order. Use when you have objects (site columns, content types, lists, or any caller-defined type) with declared dependencies and need a provably correct order. Pure computation, no tenant I/O.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from wave_planning import plan_waves; print(plan_waves(objects).to_dict())\""
---

# Plan SharePoint Deployment Waves

Compute a safe deployment order from a dependency graph instead of hand-maintaining a step list that silently drifts.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Computes ORDER only. It plans or applies no field, content-type or list change; feed its order into `sharepoint-site-build-and-publish`'s own planning, in stage order.
- Declare dependencies by object `name` only, never by a numbered stage: a stage number standing in for its contents goes stale silently.
- Never raise on a bad graph, and never drop or guess an order for an unresolvable object. A cycle or an unresolved dependency is a `FAILED` plan with a specific finding.
- No tenant I/O. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from wave_planning import DeploymentObject, plan_waves
objects = [
    DeploymentObject(name="SiteColumnA", object_type="SiteColumn"),
    DeploymentObject(name="ContentTypeB", object_type="ContentType", depends_on=("SiteColumnA",)),
]
print(plan_waves(objects).to_dict())
```

## Workflow

1. Build `DeploymentObject`s with `name`, `object_type` and `depends_on` (names of other objects).
2. Call `plan_waves(objects)`.
3. Report the outcome (`EMPTY`, `OBSERVED` or `FAILED`) and, on success, the ordered stages; on `FAILED`, the exact `blocking_findings`.

## Verification

`OBSERVED` means every dependency resolved and a full stage order exists. Confirm no object appears in a stage before a dependency of it.

## References

- [Wave planning details](references/deployment-wave-planning-details.md): read for the motivation, outcome table, usage and the 2026-08-08 move from `sharepoint-site-build-and-publish`.
