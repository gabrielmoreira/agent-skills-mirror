# ControlFlow Agent System — Shared Policies

## Continuity
Use `plans/project-context.md` as the stable reference for agent roster, complexity tiers, semantic risk taxonomy, and shared conventions.

## Build and Test
```sh
cd evals && npm test              # full offline suite: schema + behavior + orchestration + drift
npm run test:structural           # schema/P.A.R.T structure only (faster)
npm run test:behavior             # prompt-behavior + orchestration-handoff regressions only
```
Scenarios are in `evals/scenarios/`. Validate against matching schemas in `schemas/`.

## Failure Classification
When status is `FAILED`, `NEEDS_INPUT`, `NEEDS_REVISION`, or `REJECTED`, include `failure_classification`:
- `transient` — Flaky test, network timeout, or temporary tool unavailability; retry with identical scope.
- `fixable` — Small correctable issue (typo, missing import, config value); retry with fix hint.
- `needs_replan` — Architecture mismatch or missing dependency; delegate to Planner for targeted replan.
- `escalate` — Security vulnerability, data integrity risk, or unresolvable blocker; stop and await human approval.

## NOTES.md
Maintain/update `NOTES.md` for persistent state across context resets:
- Active objective and current phase.
- Blockers and unresolved risks.
- Remove stale entries when superseded.
- Keep within the 20-line budget (enforced by `evals/validate.mjs` Pass 7, style drift checked via `validateNotesMdStyle` in `evals/drift-checks.mjs`).

See `docs/agent-engineering/MEMORY-ARCHITECTURE.md` for the canonical three-layer memory model (session / task-episodic / repo-persistent). `NOTES.md` holds repo-persistent active-objective state only; task-specific history lives in `plans/artifacts/<task-slug>/`.

Before writing to `/memories/repo/` or updating `NOTES.md` at a phase boundary, load and follow `skills/patterns/repo-memory-hygiene.md` (dedup checklist + prune routine).

To identify plans ready for archival: `cd evals && npm run archive:dry`. To execute: `npm run archive:apply`.

## Governance Docs
Agent engineering policies are in `docs/agent-engineering/`:
- `PART-SPEC.md` — P.A.R.T. specification (mandatory section order: **Prompt → Archive → Resources → Tools**).
- `RELIABILITY-GATES.md` — Verification gate requirements (build/tests/lint).
- `CLARIFICATION-POLICY.md` — When to invoke `vscode/askQuestions` vs. return `NEEDS_INPUT`.
- `TOOL-ROUTING.md` — Routing rules for external tools (fetch, githubRepo, MCP).
- `SCORING-SPEC.md` — Quantitative scoring reference.
- `MIGRATION-CORE-FIRST.md` — Shared implementation backbone pattern and consolidation exit criteria.
- `PROMPT-BEHAVIOR-CONTRACT.md` — Behavioral invariants complementing P.A.R.T structural rules.

## Conventions
- Agent files live at repo root: `<Name>.agent.md` or `<Name>-subagent.agent.md`.
- Artifacts: plans → `plans/`, schemas → `schemas/`, skill patterns → `skills/patterns/`.
- All agent outputs use **structured text**. Do NOT output raw JSON to chat — it wastes context tokens.
- Skill library is at `skills/index.md`. Planner selects ≤3 skills per plan phase.
- `skills/patterns/llm-behavior-guidelines.md` is a meta-skill for preventing systematic agent anti-patterns (scope drift, over-abstraction, silent assumptions, weak success criteria). CoreImplementer, UIImplementer, CodeReviewer, and Planner load it on non-trivial tasks.
- Failure taxonomy applies to all agents; PlanAuditor and AssumptionVerifier exclude `transient`.
- P.A.R.T. section order in every agent file: **Prompt → Archive → Resources → Tools** (see `PART-SPEC.md`).
- Orchestrator and Planner must delegate only to project-internal agents documented in `plans/project-context.md`; external/third-party agents are strictly prohibited.
- Adding/editing agents or skills: follow the 4-step process in `CONTRIBUTING.md` (create agent file, schema, eval scenarios, register in `plans/project-context.md`).
- Tool and agent permission grants are in `governance/` (`agent-grants.json`, `tool-grants.json`, `runtime-policy.json`, `rename-allowlist.json`). Update these when changing an agent's tool profile.

## Agent System
13 agents in the ControlFlow system:
- **Orchestration:** Orchestrator
- **Planning:** Planner
- **Adversarial Review:** PlanAuditor-subagent, AssumptionVerifier-subagent
- **Executability Verification:** ExecutabilityVerifier-subagent
- **Implementation:** CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent
- **Review:** CodeReviewer-subagent
- **Research:** Researcher-subagent, CodeMapper-subagent
- **Documentation:** TechnicalWriter-subagent
- **Testing:** BrowserTester-subagent

Complexity tiers: TRIVIAL / SMALL / MEDIUM / LARGE — see `plans/project-context.md`.

**Agent entry points:**
| Scenario | Agent |
|----------|-------|
| Vague goal or idea | `@Planner` — runs idea interview, produces phased plan |
| Detailed task with clear requirements | `@Orchestrator` — dispatches subagents, manages gates |
| Deep research question | `@Researcher` — evidence-based investigation |
| Quick codebase exploration | `@CodeMapper` — read-only discovery |

> After `@Planner` produces a plan artifact, reviewed execution (PLAN_REVIEW, approvals, todo lifecycle, execution gating) continues through `@Orchestrator`. Planner authors plans; Orchestrator governs their review and execution.
