---
name: impact-review
description: Assess likely downstream impact, decide what should be reconciled now versus carried forward explicitly, and keep the repository coherent without sweeping every related surface.
---

# Impact Review

Use this skill when:

- a change may affect more than its origin path
- the repository's follow-through policy still needs a concrete decision in the current task
- you need to decide between no action, immediate reconciliation, or explicit follow-up

## Workflow

1. Confirm the originating change and the requested scope.
2. Find the relevant ownership nodes, overlays, and `Follow-Through Triggers`.
3. Build a short list of downstream surfaces that could realistically matter.
4. Inspect only the surfaces whose state could still change the decision.
5. Decide which surfaces need no action, an update now, or explicit carry-forward.
6. Use scripts, CI, or runbooks for exact repeatable checks.
7. Finish by stating what was updated, what was intentionally deferred, and where that follow-through now lives if it matters.

## Guardrails

- Do not enumerate the whole repository by default.
- Do not treat every trigger as a command to widen scope aggressively.
- Do not leave meaningful follow-through implicit if the current pass is not closing it.
- Do not create a new skill per trigger shape when this workflow is still sufficient.
