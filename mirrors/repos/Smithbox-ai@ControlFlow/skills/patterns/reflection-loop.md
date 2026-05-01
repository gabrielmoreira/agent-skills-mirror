# Reflection Loop — Pre-Retry Analysis Hook

## Purpose
Add a single-shot structured reflection step **between** a subagent's `FAILED`/`NEEDS_REVISION` return and the existing retry dispatch. Reflection exists to improve the *quality* of the next retry's fix hint — it is **not** a new retry, does **not** introduce a new counter, and does **not** compound existing `retry_budgets`.

## Trigger
- After a subagent returns status `FAILED` or `NEEDS_REVISION`.
- **Before** the Orchestrator selects the retry classification route (`transient` / `fixable` / `needs_replan` / `escalate`).
- Only when `governance/runtime-policy.json → budget_defaults.enable_reflection` is `true` for the task or tier.

## Not a Retry
Reflection is a **pre-retry analysis hook**:
- Exactly one LLM call per failure event.
- Consumes no retry counter.
- Reaching `enable_reflection: false` skips this step entirely (current default behavior).
- The retry that follows reflection consumes the **existing** counters in `retry_budgets`:
  - `transient_max` (default 3)
  - `fixable_max` (default 1)
  - `needs_replan_max` (default 1)
  - `escalate_max` (0 — terminal)
- There is **no** `reflection_max`, `reflection_budget`, or reflection-specific counter anywhere in the system.

## Output Contract
Reflection returns a structured object, fed into the subsequent retry delegation as a `fix_hint`:

```
{
  "root_cause": "<one-sentence causal attribution>",
  "proposed_fix": "<minimal concrete action for the retry>",
  "confidence": 0.0-1.0
}
```

- Low confidence (< 0.5) → Orchestrator prefers `needs_replan` routing over `fixable`.
- High confidence (≥ 0.8) → retry proceeds with the proposed fix as a delegation hint.

## Default State
- `governance/runtime-policy.json → budget_defaults.enable_reflection: false`.
- No ControlFlow agent invokes reflection unless this flag is explicitly flipped.
- Enablement is a per-deployment opt-in, not a per-task decision by subagents.

## When to Enable
- High-ambiguity domains where failure modes are not obviously classifiable (e.g., intermittent semantic regressions, cross-schema drift).
- Early prototyping phases where retry fix quality materially reduces wall-clock cost.
- **Do not** enable when retry budgets are already tight or when the extra LLM call breaches budget caps (see `skills/patterns/budget-tracking.md`).

## Orthogonality Statement
Reflection is orthogonal to:
- `retry_budgets` — attempt counters are unchanged.
- `budget_defaults` — resource caps are unchanged; one reflection call counts against `token_cap`/`cost_usd`/`wall_clock_s` like any other LLM call.

Reaching a retry counter cap with reflection enabled still yields the same terminal routing (`escalate`) as the current system. Reflection cannot rescue an exhausted budget.

## References
- `docs/agent-engineering/RELIABILITY-GATES.md` — retry and gate policy.
- `skills/patterns/error-handling-patterns.md` — failure classification table.
- `skills/patterns/budget-tracking.md` — orthogonal resource caps.
