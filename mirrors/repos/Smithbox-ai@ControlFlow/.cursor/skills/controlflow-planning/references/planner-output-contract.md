# Planner Output Contract

Use this strict contract when writing plan artifacts.

## Default Path

- `plans/<task-slug>-plan.md`

## Default Role Label

- `Agent: Planner`

## Allowed Status Values

- `READY_FOR_EXECUTION`
- `ABSTAIN`
- `REPLAN_REQUIRED`

## Review Pipeline Before Execution

- `TRIVIAL`: may execute directly if the user did not ask for a saved plan review
- `SMALL`: run `controlflow-plan-audit`
- `MEDIUM`: run `controlflow-plan-audit` and `controlflow-assumption-verifier`
- `LARGE`: run `controlflow-plan-audit`, `controlflow-assumption-verifier`, and `controlflow-executability-verifier`
- unresolved `HIGH` semantic risk: always include `controlflow-assumption-verifier`

## Non-Negotiables

- Do not inline the entire plan in chat when a file artifact is required.
- Do not skip any of the 7 semantic risk categories.
- Do not mark a plan `READY_FOR_EXECUTION` when confidence is below `0.9`.
