---
name: workflow-self-anneal
description: Run a bounded self-annealing review of operating instructions and workflow outcomes. Use this after failures, after long sessions, before merge, or when repeated mismatches appear between intended process and observed execution.
argument-hint: [context: session-start|post-failure|pre-merge|post-release] [scope: workflow|stability|qa|git]
user-invocable: true
disable-model-invocation: false
---

# Workflow Self-Anneal

## Purpose

Perform a **controlled, auditable improvement pass** on instructions and process docs to reduce repeated failures while preserving human control.

This skill optimizes _process reliability_, not model internals.

## Hard safety constraints

1. No unbounded loops or autonomous "improve forever" behavior.
2. Max one anneal pass per invocation; max three proposed doc changes.
3. No deploy/publish success claims without verification evidence.
4. Do not modify security/permission policy automatically; propose only.
5. If evidence insufficient, return `NO_CHANGE` with missing-evidence list.

## Trigger conditions

- Same failure pattern ≥2 times in 7 days.
- Session crash/restart/tooling instability.
- Instructions contradicted by observed actions.
- Pre-merge gate requires hardening evidence.
- Repeated carryover/blocked items across iterations.
- PR/merge latency breaches targets or reopened issues trend up.
- **Commits exist without linked GitHub issues** (process drift).
- **Consultant check registry returns ≥1 FAIL on domain:governance**.
- **Fleet check `fleet-002` (cost-budget) FAIL for ≥2 consecutive cycles**.

## Consultant Integration

Self-anneal may be invoked automatically from `consultant-feedback.js` when `gov-002` (baton-artifact-presence) or `gov-003` (event-emission) FAIL — these are workflow process failures, not implementation bugs.
Check IDs are managed in `scripts/global/consultant-checks.js` (3 domains: governance/tools/fleet).

## Input collection

Collect: execution artifacts (logs, errors, checks), instructions/workflow docs, recent commits/PR notes. If unavailable, declare missing and stop.

## Analysis protocol

1. **Detect mismatch**: expected vs observed behavior.
2. **Classify root cause**: `ambiguity|missing guardrail|stale instruction|tool fragility|human override`.
3. **Assess recurrence risk**: `low|medium|high` by frequency and blast radius.
4. **Detect Agile drift signals**: carryover, blocked age, review/merge latency, reopen rate.
   - **Ticket linkage**: `git log --oneline | wc -l` vs `--grep='#'`. If <80%, flag `ticket-linkage-drift`.
   - **PR coverage**: commits vs `gh pr list --state all`. If 0 PRs, flag `pr-coverage-drift`.
   - **Event gaps**: count events in `.dashboard/events.jsonl` per role transition. If <1 event per baton handoff, flag `event-emission-drift`.
5. **Propose minimal fix**: smallest docs/workflow delta preventing recurrence.
6. **Define verification gate**: objective checks confirming the fix.

## Output format (required)

Return exactly this structure:

```text
SELF_ANNEAL_REPORT
context: <session-start|post-failure|pre-merge|post-release>
scope: <workflow|stability|qa|git>
observation: [...]
expected_behavior: [...]
mismatch: [...]
root_cause: <ambiguity|missing guardrail|stale instruction|tool fragility|human override>
risk: <low|medium|high>
drift_signals:
- metric: <carryover|blocked-age|review-latency|merge-latency|reopen-rate|ticket-linkage|pr-coverage>
   trend: <improving|stable|degrading>  evidence: <artifact>
proposed_changes:
1) file: <path>  change_type: <add|edit|remove>  rationale: <why>
verification_plan:
- check: <objective>  pass_condition: <measurable>
decision: <apply|defer|NO_CHANGE>
missing_evidence: <none or list>
```

## Change targeting guidance

Prioritize: project runbooks/checklists, workflow docs, system-stability docs, learnings docs.

## Stop conditions

Return `NO_CHANGE` if: change cannot be validated objectively, evidence is missing, change expands permissions, or same fix was already applied.

## Quality bar

Good anneal output is: **specific** (concrete artifacts), **minimal** (smallest viable delta), **testable** (pass/fail checks), **traceable** (rationale + risk), **trend-aware** (drift reducing).

## Visual verification rule (publish/UX scope)

For UX-rendered changes: require post-change visual inspection artifact. Do not allow ticket closure from DOM/CI checks alone. If visual evidence is missing, decision must be `defer`.
