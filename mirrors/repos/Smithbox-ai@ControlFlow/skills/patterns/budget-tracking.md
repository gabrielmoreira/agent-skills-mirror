# Budget Tracking — Orthogonal Resource Caps

## Purpose
Define optional, orthogonal resource budgets that bound *resource consumption* (tokens, wall-clock, cost) on a delegated task. Budgets are **independent** from `retry_budgets`, which bound *attempt counts*. Reaching a resource cap is **not** a failed attempt; it is a terminal `escalate` condition.

## The Three Orthogonal Axes
All three are optional. Any axis with `null` is unbounded for that task.

| Axis | Unit | Governance key | Semantic |
|------|------|----------------|----------|
| `token_cap` | integer tokens | `budget_defaults.token_cap` | Sum of prompt + completion tokens across the task |
| `wall_clock_s` | integer seconds | `budget_defaults.wall_clock_s` | Elapsed seconds from dispatch to terminal status |
| `cost_usd` | float USD | `budget_defaults.cost_usd` | Accumulated billed cost |

Defaults live in `governance/runtime-policy.json → budget_defaults` and are `null` (unbounded) by default.

## Early-Stop Classification
- Hitting any cap → task terminates with status `FAILED` and `failure_classification: escalate`.
- Aligns with the four-class failure taxonomy in `docs/agent-engineering/RELIABILITY-GATES.md` and `.github/copilot-instructions.md`.
- Escalation stops further dispatch and surfaces accumulated evidence to the conductor.

## Non-Overlap with `retry_budgets` (Emphatic)
- `retry_budgets` counts **attempts** (`transient_max`, `fixable_max`, `needs_replan_max`).
- `budget_defaults` counts **consumption** (tokens, seconds, dollars).
- **Never compounded.** Reaching a resource cap does NOT increment any retry counter. An exhausted retry counter does NOT consume resource budget beyond what was actually used.
- A task may exit via either mechanism independently; whichever fires first wins.

## Propagation
- Orchestrator attaches the active `budget_context` to every delegation payload:
  ```
  budget_context: {
    token_cap: <int|null>,
    wall_clock_s: <int|null>,
    cost_usd: <float|null>,
    tokens_used_so_far: <int>,
    wall_clock_elapsed_s: <int>,
    cost_usd_so_far: <float>
  }
  ```
- Subagents propagate this context unchanged into any nested delegations.
- The `trace_id` (see `docs/agent-engineering/OBSERVABILITY.md`) correlates budget accounting across the task.

## Runtime Hook
- Per-agent hook is **optional**. Absence ⇒ unbounded (current behavior preserved).
- When present, the hook checks caps **before** issuing the next LLM call or tool invocation; it does not pre-empt work in flight.
- Hook emits a gate event of type `budget_cap_reached` on early-stop.

## Defaults and Enablement
- `budget_defaults.enabled: false` by default — caps are inert until explicitly enabled per deployment.
- Flipping `enabled: true` without setting any cap still results in unbounded behavior; caps must be set individually.
- See `governance/runtime-policy.json` for the authoritative current defaults.

## References
- `governance/runtime-policy.json` — `budget_defaults` block.
- `docs/agent-engineering/RELIABILITY-GATES.md` — failure taxonomy.
- `docs/agent-engineering/OBSERVABILITY.md` — `trace_id` correlation for budget accounting.
- `skills/patterns/reflection-loop.md` — also orthogonal to both `retry_budgets` and `budget_defaults`.
