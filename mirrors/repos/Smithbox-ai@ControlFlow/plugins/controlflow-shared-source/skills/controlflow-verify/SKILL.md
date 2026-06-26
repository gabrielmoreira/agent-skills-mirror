---
name: controlflow-verify
description: "Use after a ControlFlow plan is saved and before implementation. Runs tier-gated adversarial verification inline: structural audit, assumption/mirage detection, and cold-start executability simulation."
---

# ControlFlow Verify

## Overview

Verify a saved plan before implementation. The checks run inline in the current host
context with zero subagents shipped by the plugin. This skill combines the useful parts of the former
plan-audit, assumption-verifier, and executability-verifier workflows without reproducing
Codex subagent orchestration.

Select the skill explicitly. In Codex, invoke it with `$controlflow-verify`.

## Input and Contract

- Read the plan from disk; do not verify a chat copy.
- If the active repository provides `schemas/planner.plan.schema.json` and
  `plans/templates/plan-document-template.md`, use them.
- Otherwise use `../controlflow-plan/references/plan-format.md`.

## Tier Gating

| Tier | Verification |
| --- | --- |
| `TRIVIAL` | Skip unless explicitly requested |
| `SMALL` | Phase 1 |
| `MEDIUM` | Phases 1–2 |
| `LARGE` | Phases 1–3 |

Any unresolved applicable `HIGH` semantic risk requires all three phases.

## Phase 1 — Structural Audit

- Check the header, section order, lifecycle headings, all seven semantic-risk rows, phase
  shape, diagrams, exact commands, measurable acceptance criteria, and rollback guidance.
- Verify referenced paths and tests against the repository.
- Apply the Minimum Viable Change Ladder before accepting new abstractions, dependencies,
  or generated surfaces.

## Phase 2 — Assumption and Mirage Check

- Try to refute each factual claim that names a file, symbol, dependency, API, version,
  convention, integration, security boundary, or concurrency assumption.
- Classify claims as `confirmed`, `uncertain`, or `refuted`.
- Use [references/mirage-patterns.md](references/mirage-patterns.md).

## Phase 3 — Cold-Start Executability

- Simulate a fresh executor starting the first phases with only the plan and repository.
- Stop at the first real blocker.
- Require concrete inputs, outputs, commands, test specifics, inter-phase contracts, and
  recovery for destructive work.

## Verdict

- `APPROVED`: all required phases pass and implementation may start.
- `NEEDS_REVISION`: the design is viable but specific plan defects must be fixed.
- `REJECTED`: the scope or architecture is not safely deliverable as written.
- Include `failure_classification: fixable`, `needs_replan`, or `escalate` for non-approval.
- Write a compact verdict to `plans/artifacts/<task-slug>/verify-verdict.md`.
- Do not start implementation until the verdict is `APPROVED`.

## Native Host Boundary

- Do not spawn plugin verifier agents.
- If the user explicitly wants an isolated second opinion, native host review or an
  explicitly requested native subagent can supplement this inline pass. In Codex, `/review`
  is the built-in review command.
- The host owns approvals, sandboxing, retries, and subagent lifecycle.

## References

- `references/adversarial-framing.md`
- `references/verify-phases.md`
- `references/mirage-patterns.md`
