# CLAUDE.md — ControlFlow for Claude Code

## Overview

`AGENTS.md` manages Copilot-agent contracts in VS Code (P.A.R.T. format, model routing, governance).
This file `CLAUDE.md` controls Claude Code behavior for this repository.
When both are active: follow the source matching your tool — AGENTS.md for Copilot agents, CLAUDE.md for Claude Code sessions.

---

## When to Generate a Plan

Generate a structured plan **before** implementation when the task is MEDIUM/LARGE:

| Tier | Criteria | Action |
|------|----------|--------|
| TRIVIAL | 1–2 files, single concern, low blast radius | No plan artifact (describe steps inline) |
| SMALL | 3–5 files, one subsystem | Plan + plan-audit |
| MEDIUM | 6–14 files or multiple concerns | Full plan + audit + assumption-verifier |
| LARGE | 15+ files OR any high-impact risk | Full plan + all three verifiers |

**Override rule:** if ANY unresolved semantic risk is both *applicable* and *HIGH impact*, treat as LARGE regardless of file count.

---

## Plan Generation Contract (v2)

Save every non-trivial plan at: `plans/<task-slug>-plan.md` (kebab-case, under 4 words).

### YAML Header (exact fields — no fence)

```yaml
Status: READY_FOR_EXECUTION | ABSTAIN | REPLAN_REQUIRED
Agent: controlflow-planning
Schema Version: 2.0.0
Complexity Tier: TRIVIAL | SMALL | MEDIUM | LARGE
Confidence: 0.0–1.0 (computed; below 0.87 auto-NEEDS_REVISION)
Abstain: is_abstaining: false or [ true, reasons: [...] ]
Summary: One paragraph describing task and approach
```

### Sections (in order — never skip or reorder)

| # | Section | Mandatory for | Key requirements |
|---|---------|---------------|-----------------|
| 1 | Context & Analysis | ALL | Verified facts only; separate assumptions clearly with bounded scope statement |
| 2 | Design Decisions | MEDIUM+ | Arch choices + rejected alternatives, boundary/integration points, constraints/trade-offs, temporal flow diagram (sequenceDiagram for non-trivial orchestration) |
| 3 | Implementation Phases | ALL | Phase count: 3–10. Each phase: Objective, Executor Agent, Wave#, Dependencies, Files create/modify, Tests add/update, Acceptance Criteria (measurable), Quality Gates, Failure Expectations + mitigation |
| 4 | Inter-Phase Contracts | MEDIUM+ | Deliverable format from upstream + exactly how downstream validates it |
| 5 | Open Questions | ALL | Explicitly listed; if any could change scope → stop and ask user |
| 6 | Risks | ALL | Table: Risk \| Impact \| Likelihood \| Mitigation |
| 7 | Semantic Risk Review | ALL (all 7 rows) | data_volume, performance, concurrency, access_control, migration_rollback, dependency, operability — every row present, even if `not_applicable` with justification |
| 8 | Architecture Visualization | MEDIUM+ | Flowchart TD DAG base; sequenceDiagram for non-trivial orchestration; each ≤30 lines source |
| 9 | Success Criteria | ALL | Measurable system-level indicators tied back to phase acceptance criteria |
| 10 | Handoff & Execution Notes | ALL | Target Agent, Prompt, execution order, parallelization opportunities, max parallel agents (default: 3) |

**Lifecycle Sections** (append for SMALL+ only): Progress → Discoveries → Decision Log → Outcomes → Idempotence & Recovery. One sentence per entry, evidence-backed. Omit for draft/abandoned plans.

### Non-negotiable rules

- Steps in numbered prose — **no code blocks** inside plan document
- Acceptance criteria MUST include at least one measurable condition referencing observable outcome (test pass, file produced, CI check clears)
- Every phase declares exactly one `executor_agent` from: `CodeMapper-subagent`, `Researcher-subagent`, `CoreImplementer-subagent`, `UIImplementer-subagent`, `PlatformEngineer-subagent`, `TechnicalWriter-subagent`
- All verification must be automatable — no manual testing steps
- Quality Gates use standard values only: `tests_pass`, `lint_clean`, `schema_valid`, `safety_clear`, `human_approved_if_required`

---

## Embedded Audit Pipeline (v2)

### Pre-flight Check (run once at top of Step 1)

| Action | Command / Method | Why |
|--------|-----------------|-----|
| Unfinished plans | `ls plans/` — flag any non-APPROVED/non-REJECTED files | May interfere with current work |
| Branch divergence | `git log --oneline -5 && git status --short` | Flag early as open question if dirty |
| Dependency conflicts | Read manifest vs what plan proposes to modify | Version mismatches = risk items |

If clean: log "No interference detected" and continue.

### Step 1: Spec Capture & Fact Verification

Confirm scope by anchoring to explicit requirements:
- What user-visible behavior changes?
- Which files, functions, tables, APIs are affected? (read relevant manifest or import chain)
- What constraints exist — dependencies, coding standards, API contracts?

If vague on any → **ask the user**. Do not infer scope from chat alone.

### Step 2: Structural Validation (before adversarial review)

1. Header keys present; Status is one of exactly `READY_FOR_EXECUTION`, `ABSTAIN`, or `REPLAN_REQUIRED`
2. Sections 1–10 exist in order; lifecycle sections in exact specified order (if present)
3. Section 7 has exactly seven categories — no more, no fewer
4. All gate values are from the standard set of five
5. Executor agents match ControlFlow sub-agent enum strings
6. LARGE tier requires both flowchart + sequenceDiagram; each ≤30 lines

If any check fails → `NEEDS_REVISION` immediately (structural layer).

### Step 3: Adversarial Review — 10-Point Safety Checklist

| # | Check | Verdict criterion |
|---|-------|------------------|
| 1 | All referenced files/paths real? | Verified in repo |
| 2 | Clear objectives, no scope overlap between same-wave phases? | Each phase independent |
| 3 | Acceptance criteria objectively testable? | Not vague ("handle errors", "make it secure") |
| 4 | Verification commands concrete enough for fresh executor? | No guessing required |
| 5 | Destructive/migration-heavy phase has rollback/recovery guidance? | HIGH blast radius → `human_approved_if_required`; MEDIUM → `safety_clear` |
| 6 | Missing dependency assumptions, version constraints, unpinned APIs? | All pinned or flagged |
| 7 | Data volume concerns documented (bulk ops, pagination)? | If applicable |
| 8 | Concurrency surface: shared mutable state, race windows? | Ownership/ordering explicit; no "should be safe" hand-waving |
| 9 | Fresh executor blocked by ambiguity in Phase 1–3? | Should execute Phase 1 without asking |
| 10 | Security/operability (permissions, auth, deploy configs, monitoring)? | Stronger gates if needed |

**Deep dimensions:** data_volume triggers → add discovery step; performance hot paths → name expected bottleneck + verification method; concurrency → explicit locking order map.

### Step 4: Confidence Scoring & Verdict

Score each checklist item as `confirmed` / `uncertain` / `refuted`.

```
confidence = confirmed_count / total_items_with_any_actionable_question
Round to two decimal digits.
```

**Capping rules:**
- If uncertain ≥ 2 → auto-cap at 0.85; insert research phases for those items
- Any HIGH-impact row marked `open_question` → cap at 0.7 + add research spike phase
- confirmed < 6 out of ≥10 total → NEEDS_REVISION (insufficient evidence)

**Verdict:**

| Condition | Verdict | Action |
|-----------|---------|--------|
| All checks pass, first-phase fully actionable, criteria measurable | `APPROVED` | Proceed to execution with handoff section |
| Critical gap: ambiguous Phase 1, no rollback on destructive change, unverified paths, vague criteria | `NEEDS_REVISION` | Update plan sections listed by finding; re-audit until pass or escalation threshold breached |
| Structural flaw in architecture; scope not deliverable as authored | `REJECTED` | Explain blockers; ask user for direction. Do NOT start coding. |

### Step 5: Resolution & Handoff

- **APPROVED** → embed handoff prompt into Section 10 of plan artifact
- **NEEDS_REVISION** → list each finding with exact section reference; edit in-place; re-audit
- **REJECTED/ESCALATED** → explain blockers, provide next concrete step to unblock. Pause.

---

## Semantic Risk Review — 7 Mandatory Categories

Each plan MUST include all 7 categories exactly once:

| Category | Applicability | Impact | Evidence Source | Disposition |
|----------|---------------|--------|-----------------|-------------|
| data_volume | applicable / not_applicable / uncertain | HIGH / MEDIUM / LOW / UNKNOWN | file, command, or repo evidence | resolved / open_question / research_phase_added / not_applicable |
| performance | ... | ... | ... | ... |
| concurrency | ... | ... | ... | ... |
| access_control | ... | ... | ... | ... |
| migration_rollback | ... | ... | ... | ... |
| dependency | ... | ... | ... | ... |
| operability | ... | ... | ... | ... |

Never skip a category — if not applicable, set `not_applicable` + justification.

---

## Tier-gated Review Pipeline

Transition from planning → execution requires review per tier:

| Tier | Skill (slash command) |
|------|----------------------|
| TRIVIAL | Skip |
| SMALL | `/controlflow-claude-code:controlflow-plan-audit` |
| MEDIUM | plan-audit + `/controlflow-claude-code:controlflow-assumption-verifier` |
| LARGE | plan-audit + assumption-verifier + `/controlflow-claude-code:controlflow-executability-verifier` |

---

## Workflow Entry Points — Available Skills

Located in `plugins/controlflow-claude-code/skills/`:

| Skill | Purpose |
|-------|---------|
| `controlflow-spec` | Requirements capture before planning (when task is ambiguous) |
| `controlflow-planning` | Plan generation in ControlFlow format |
| `controlflow-plan-audit` | Pre-execution plan audit |
| `controlflow-assumption-verifier` | Mirage detection — assumption verification |
| `controlflow-executability-verifier` | Cold-start simulation for LARGE plans |
| `controlflow-strict-workflow` | Full pipeline (plan → audit → execute → review) |
| `controlflow-orchestration` | Approved plan execution by phase |
| `controlflow-review` | Post-implementation code review |
| `controlflow-memory-hygiene` | Memory cleanup for long sessions |
| `controlflow-router` | Entry point dispatcher (usually inline in CLAUDE.md) |

---

## Artifact Paths

```
plans/<task-slug>-plan.md                     # main plan
plans/artifacts/<task-slug>/plan-audit-report.md   # audit report
plans/artifacts/<task-slug>/assumption-verifier.md     # assumption verification
plans/artifacts/<task-slug>/executability-verifier.md  # executability verification
plans/artifacts/<task-slug>/research-packet.md          # research packet (if applicable)
```

---

## Reference Files

- `plugins/controlflow-shared-source/skills/` — **Source of truth** for all skill distributions (generates claude-code, codex, cursor plugins)
- `schemas/planner.plan.schema.json` — JSON Schema for plan validation (draft 2020-12)
- `schemas/runtime-policy.schema.json` — Runtime execution policy schema
- `plans/templates/plan-document-template.md` — Full plan document template
- `.github/workflows/ci.yml` — CI pipeline runs `evals` suite on push

---

## Changes from v1 → v2

| Change | Reason |
|--------|--------|
| Merged old Steps 4→5 (adversarial review + risk scoring) into unified pipeline with clear sub-steps | Reduced cognitive load; structural validation now a distinct layer before content audit |
| Removed redundant "Plan Quality Standards" section (11 standards) and "Anti-Rationalization Checklist" | Overlap with checklist items; the 10-point safety check covers all 11 + anti-rationalization concerns |
| Moved quality gate enum to inline rules table instead of separate section | One source of truth for gate/agent values |
| Confidence scoring formula simplified (was embedded in prose, now explicit) | Transparency: users see exactly how the number is computed |
| Pre-flight check extracted from Step 1 into its own table | Runs once before any planning; avoids token waste on empty reports |
