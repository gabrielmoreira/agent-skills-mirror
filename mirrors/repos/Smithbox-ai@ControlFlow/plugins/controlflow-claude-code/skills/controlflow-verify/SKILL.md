---
name: controlflow-verify
description: "Use after /controlflow-claude-code:controlflow-plan produces a plan, before implementation. Runs adversarial pre-execution verification inline in the main context (zero subagents): structural audit, assumption/mirage detection, and executability cold-start simulation. Emits APPROVED / NEEDS_REVISION / REJECTED with evidence."
---

# ControlFlow Verify

## Overview

Verify a plan before execution. Runs entirely inline in the main conversation context —
no plugin subagents are spawned. Because inline review lacks the isolation of a fresh
subagent context, this skill is adversarial by construction: it tries to refute the plan
and defaults to a flagged finding when uncertain. The goal is to catch mirages and
unexecutable plans cheaply, without the token cost of spawning verifier subagents.

Invoke this skill via `/controlflow-claude-code:controlflow-verify`.

## Input

The plan artifact path (default `plans/<task-slug>-plan.md`). Read it from disk; do not
work from a chat-embedded copy.

## Tier gating (advisory)

| Tier | Phases to run |
|------|---------------|
| TRIVIAL | skip |
| SMALL | phase 1 |
| MEDIUM | phases 1–2 |
| LARGE | phases 1–3 |

Any unresolved HIGH-impact semantic risk → run all three regardless of tier.

## Adversarial Framing (apply to every phase)

- Your job is to break the plan, not to defend it. Steelman the rejection.
- Default to `flagged` when evidence is insufficient — do not rationalize a pass.
- For each claim, ask: "What would make this false?" then check that.
- Distinguish validated blockers from hypotheses; state validation gaps explicitly.
- See [references/adversarial-framing.md](references/adversarial-framing.md).

## Phase 1 — Structural Audit

Confirm the artifact conforms to `schemas/planner.plan.schema.json` and
`plans/templates/plan-document-template.md`:

1. YAML header present; `Status` is one of `READY_FOR_EXECUTION`, `ABSTAIN`, `REPLAN_REQUIRED`;
   `Agent: Planner`; `Schema Version: 1.2.0`; `Confidence` is numeric.
2. All 10 sections present in order; 5 lifecycle sections present and ordered for SMALL+.
3. Section 7 has exactly seven risk categories, each once.
4. Every phase declares one `executor_agent` from the schema enum; quality gates use only the
   five standard values.
5. Acceptance criteria include at least one measurable observable outcome per phase.
6. LARGE tier includes `flowchart TD` + `sequenceDiagram`; each ≤30 lines.

Structural failure → `NEEDS_REVISION` immediately.

## Phase 2 — Assumption / Mirage Check

Try to refute the plan's factual claims:

1. Every referenced file/path/symbol is real — open or grep for it. A referenced file that
   does not exist is a mirage and a blocker.
2. Every assumption is bounded in scope, not a hidden scope decision.
3. Dependencies and version constraints are pinned or explicitly flagged.
4. No "should be safe" hand-waving on concurrency or shared mutable state — ownership and
   ordering are explicit.
5. Data-volume concerns documented where applicable (bulk ops, pagination).

See [references/mirage-patterns.md](references/mirage-patterns.md) for the full mirage taxonomy (P1–P10 presence mirages, A11–A17 absence mirages) and [references/verify-phases.md](references/verify-phases.md) for the detailed phase checklists.

## Phase 3 — Executability Cold-Start Simulation

Simulate a fresh executor starting Phase 1 with only the plan in hand:

1. Can Phase 1 execute without asking the user a question? If yes → fine; if no → flag the
   ambiguity as a Phase 1 blocker.
2. Are verification commands concrete enough to run as-is (no guessing)?
3. Does each destructive or migration-heavy phase have rollback/recovery guidance? HIGH
   blast radius → require `human_approved_if_required`; MEDIUM → `safety_clear`.
4. Is the inter-phase contract deliverable format explicit, and does the downstream phase
   know how to validate it?

## Confidence Score and Verdict

Score each applicable checklist item `confirmed` / `uncertain` / `refuted`.

```
confidence = confirmed_count / total_items_with_any_actionable_question
```

- uncertain ≥ 2 → cap confidence at 0.85.
- Any HIGH-impact open question → cap at 0.7.
- All checks pass, Phase 1 actionable, criteria measurable → **APPROVED**.
- Ambiguous Phase 1, no rollback on destructive change, unverified paths, vague criteria →
  **NEEDS_REVISION** (list each finding with the exact section reference; re-audit after fix).
- Structural flaw; scope not deliverable as authored → **REJECTED** (explain blockers, ask
  the user for direction; do not start coding).

Write a compact verdict to `plans/artifacts/<task-slug>/verify-verdict.md` for auditability.
Present the verdict and the findings that justify it to the user before implementation.

## Verify-Specific Failure Checks

- Do not pass a plan you have not read from disk.
- Do not mark a finding resolved without re-checking the evidence.
- Do not let the planner's confidence value substitute for your own scoring.
- Do not collapse the three phases into a single skim for a "small" plan — run the phase(s)
  the tier requires.

## References

- `references/adversarial-framing.md`
- `references/verify-phases.md`
- `references/mirage-patterns.md`