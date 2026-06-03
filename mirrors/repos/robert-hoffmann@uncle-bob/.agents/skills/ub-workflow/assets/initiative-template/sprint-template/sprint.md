---
artifact_id          : REPLACE_SPRINT_ARTIFACT_ID
artifact_type        : sprint_plan
status               : draft
context_tier         : T3
updated_at           : REPLACE_UPDATED_AT
summary_budget_lines : 480
---

# Sprint: REPLACE_SPRINT_TITLE

## Objective

REPLACE_SPRINT_OBJECTIVE

## Source

- Accepted discovery or reviewed preview: REPLACE_SPRINT_SOURCE

## Routing Preflight

- Trigger categories considered: Replace with autonomy, authority,
  runtime-boundary, policy, evidence, interoperability, agent-behavior changes,
  agent loops, harnesses, loop continuation, goal judgment, budgets,
  checkpoints, or `none`.
- Triggered categories: Replace with the triggered categories, or `none`.
- Fail-closed result: Replace with `discovery_required` when triggered
  evidence may change route, contract, scope, validation, runtime boundary, or
  implementation path; use `preview_ok` only when the route is already decided
  and trigger evidence cannot change those decisions.

## Discovery Triage

- Outcome: Replace with `preview_ok`, `discovery_required`,
  `operator_decision_needed`, or `not_triggered`.
- Outside evidence trigger: Replace with relevant standards, best practices,
  official docs, current primary research, analogous systems, source packs,
  user evidence, or operator evidence; use `not triggered` only with a
  concrete reason.
- Trigger-presumed check: Replace with whether autonomy, authority,
  runtime-boundary, policy, evidence, interoperability, or agent-behavior
  changes are in scope.
- Promotion rule: If triage outcome is `discovery_required` or
  `operator_decision_needed`, do not start implementation; create discovery or
  get the operator decision first.

## Why Preview Instead Of Discovery

- Routing trigger: Replace with why the triage outcome permits preview, or
  promote this candidate to discovery before implementation.
- Discovery trigger check: Replace with remaining route-changing
  uncertainties, or `none`.
- Promotion rule: If preview work finds sequence, scope, appetite, product
  direction, contract, runtime-boundary, or path-selection uncertainty, stop
  and create discovery before start.

## Product Increment Contribution

- Contribution type: Replace with `direct`, `enabling`, or `audit`.
- Visible increment unblocked: Replace with the product increment this sprint ships or unblocks.
- Why not direct: Replace with reason if enabling or audit, otherwise `n/a`.
- Enabling-chain check: Replace with whether this is the second consecutive enabling or prerequisite sprint.

## Bet Framing

- Appetite: REPLACE_APPETITE
- Success evidence: REPLACE_SUCCESS_EVIDENCE
- Circuit breaker: REPLACE_CIRCUIT_BREAKER
- Non-goals: REPLACE_NON_GOALS
- Deferral path: REPLACE_DEFERRAL_PATH

## Scope

1. Replace with exact scope.

## Scope Completion Rule

When this sprint uses words like `smallest`, `narrow`, or `only as needed`,
they mean the smallest objective-complete vertical slice. Every named owned
surface, required evidence gate, and exit criterion remains in scope unless
the operator explicitly changes the objective.

## Operational Surface Preflight

- Triggered: Replace with `yes` or `no`.
- Surfaces: Replace with repo-owned operational surfaces introduced or changed,
  or `none`.
- Owner and lifecycle: Replace with owner module/artifact and lifecycle, or
  `not triggered`.
- Visibility and safety: Replace with user/operator/API visibility plus safety,
  secrecy, policy, or authority rules, or `not triggered`.
- Inventory impact: Replace with inventory, topology, registry, route map, or
  analogous owner document to update, or `none`.
- Validation path: Replace with tests, checks, live gates, or evidence proving
  the surface, or `not triggered`.
- Promotion rule: If ownership, lifecycle, safety policy, validation, or
  inventory impact may change scope, architecture, risk, or acceptance
  criteria, promote discovery before execution.

## Execution Slices

1. Replace with slice objective, acceptance, verification, dependencies, and likely touched areas.

## Validation Plan

1. Replace with concrete validation commands or checks.

## Live Validation Matrix

| Gate | Status | Command | Credentials / env | Evidence path | Pass criteria | Redaction |
| --- | --- | --- | --- | --- | --- | --- |
| `provider_live_smoke` | out of scope | `n/a` | `n/a` | `n/a` | Not touched by this sprint. | No raw prompts, responses, secrets, or raw tool arguments. |
| `external_agent_live_probe` | out of scope | `n/a` | `n/a` | `n/a` | Not touched by this sprint. | No credentials, transcripts, prompts, or raw command arguments. |

## User Or Operator Evidence

- Status: Replace with `used`, `not triggered`, or `deferred`.
- Evidence: Replace with user/operator input, operator decision, or `n/a`.
- Decision impact: Replace with how the evidence changes the sprint path, or why it does not.

## Reviewed-Mode Start Checkpoint

This sprint has not started yet. In reviewed mode, preview the path and wait
for later explicit approval before implementation.

## Context Receipt

Replace with loaded artifacts, skipped surfaces, source-pack fanout, and budget exceptions.

## Exit Criteria

1. Every accepted objective claim has fresh named passing proof.
2. Required validation and live gates pass after the final relevant change.
3. Evidence is routed through `evidence/index.md`, with required objective
   gates separated from optional, not-triggered, blocked, out-of-scope, or
   operator-deferred checks.
4. Required objective proof is not deferred while closing the original
   objective as passed.
5. Decision log and closeout are current, including the closeout outcome and
   learning review.
