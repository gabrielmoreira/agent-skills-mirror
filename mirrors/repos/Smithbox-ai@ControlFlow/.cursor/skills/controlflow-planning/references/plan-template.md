# Plan: {Task Title}

**Status:** `READY_FOR_EXECUTION` | `ABSTAIN` | `REPLAN_REQUIRED`  
**Agent:** `Planner`  
**Schema Version:** `1.2.0`  
**Complexity Tier:** `TRIVIAL` | `SMALL` | `MEDIUM` | `LARGE`  
**Confidence:** `0.0-1.0`  
**Abstain:** `is_abstaining: false` or `true` with reasons  
**Summary:** One concise paragraph describing the task and approach.

## Context & Analysis

- Verified repository facts, not guesses.
- Requirements, constraints, and exclusions that shape the plan.
- Architecture observations that affect files, ownership, tests, or risk.

## Design Decisions

### Architectural Choices

- Primary design choices and why they are appropriate.

### Boundary & Integration Points

- Boundary changes, new actors, modified contracts, or integration points.
- If none: `No boundary changes identified.`

### Temporal Flow

- Execution order, approval gates, review loops, retries, or waves.
- `MEDIUM` and `LARGE` plans should include plain Mermaid source when flow is non-trivial.

### Constraints & Trade-offs

- Constraints that materially shape the design.
- Trade-offs considered and why the chosen direction is safer or simpler.

## Implementation Phases

### Phase 1 - {Phase Title}

- **Objective:** What this phase accomplishes.
- **Owner:** `local` | `subagent` | concrete executor description.
- **Wave:** Execution wave number.
- **Dependencies:** Prior phases, files, or decisions this phase depends on.
- **Files:** Concrete files to create, modify, review, or reference.
- **Tests:** Tests to add, update, or run.
- **Acceptance Criteria:** Observable signals that define success.
- **Quality Gates:** Explicit gates such as `tests_pass`, `lint_clean`, `schema_valid`, `safety_clear`, `human_approved_if_required`.
- **Failure Expectations:** Likely failure modes and whether they are `transient`, `fixable`, `needs_replan`, or `escalate`.
- **Steps:** Numbered implementation steps.

### Phase N - {Phase Title}

- Repeat the same structure for each phase.

## Inter-Phase Contracts

- **From Phase -> To Phase:** Deliverable or interface.
- **Format:** Expected shape of the upstream result.
- **Validation:** How the downstream phase confirms the contract.

## Open Questions

- Questions still requiring clarification before or during execution.

## Risks

- Plan risks and mitigations.

## Semantic Risk Review

Every plan must include all seven categories exactly once.

| Category | Applicability | Impact | Evidence Source | Disposition |
| --- | --- | --- | --- | --- |
| data_volume | applicable / not_applicable / uncertain | HIGH / MEDIUM / LOW / UNKNOWN | file, command, or repo evidence | resolved / open_question / research_phase_added / not_applicable |
| performance | ... | ... | ... | ... |
| concurrency | ... | ... | ... | ... |
| access_control | ... | ... | ... | ... |
| migration_rollback | ... | ... | ... | ... |
| dependency | ... | ... | ... | ... |
| operability | ... | ... | ... | ... |

## Success Criteria

- Measurable criteria for calling the plan complete.

## Handoff

- **Target:** `controlflow-orchestration`
- **Review Before Execution:** `controlflow-plan-audit` for `SMALL+`; add `controlflow-assumption-verifier` for `MEDIUM+` and unresolved `HIGH` risk; add `controlflow-executability-verifier` for `LARGE`.
- **Prompt:** Concise handoff that points to the saved artifact path and requests review followed by execution.

## Notes for Orchestration

- Recommended execution order.
- Parallelization opportunities and collision risks.
- Approval-sensitive steps.
- Retry or replan hints by phase or wave.

## Progress

- Phase-by-phase progress notes updated during execution.

## Discoveries

- Unexpected findings, environment constraints, or scope changes discovered during execution.

## Decision Log

- Key decisions made during execution with rationale.

## Outcomes

- Final outcomes, deferred work, and residual risks.

## Idempotence & Recovery

- Which phases are safe to re-run and how to recover from interruption or failure.

## Architecture Visualization

- Plans with 3+ phases should include a Mermaid `flowchart TD` as plain source, not a fenced code block.
- `MEDIUM` plans with non-trivial orchestration should also include a `sequenceDiagram`; `LARGE` plans should include both.

## Rules

- No code blocks inside the plan body.
- No manual-only verification steps.
- Each phase must be incremental and testable.
- Prefer 3-10 phases except for truly trivial work.
- Keep the lifecycle headings above exactly as written for strict-plan validation.

## Terminal Non-Ready Outcome Artifact

Use this shape only when status is `ABSTAIN` or `REPLAN_REQUIRED`.

### Resolved Scope

- What was confidently understood.

### Blockers / Invalidated Assumptions

- What prevents safe execution.

### Missing Evidence

- Specific missing files, facts, or confirmations.

### Recovery Next Step

- The highest-value next action to unblock planning.
