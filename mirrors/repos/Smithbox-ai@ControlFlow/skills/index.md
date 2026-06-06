# Skill Library Index

## Purpose

Reusable domain-specific patterns for agent consumption. Planner selects relevant skills during planning and includes them as `skill_references` in phase definitions. Implementation agents load referenced skills before starting work.

## Discovery Protocol

1. Planner reads this index during planning (Step 5 — after Complexity Gate).
2. Match task domain keywords against the Domain column below.
3. Select ≤3 most relevant skills based on task context.
4. Include selected skill file paths in each applicable phase's `skill_references` array.
5. Implementation agents read referenced skill files before executing phase tasks.

## Domain Mapping

> **Binding legend — read before using the "Applicable Agents" column.** This column is a routing hint, not a guarantee. Two binding modes apply:
> - **HARD-REFERENCED** — the skill is statically loaded by the named agent because it is cited directly in that agent's `## Resources` / prompt body. Currently only: `preflect-core` (all agents), `repo-memory-hygiene` (Orchestrator, CodeReviewer-subagent, PlanAuditor-subagent), `memory-promotion-candidates` (Orchestrator), `security-review-discipline` (CodeReviewer-subagent), `idea-to-prompt` (Planner), `spec-driven-development` (Planner, as a "consider" reference), `source-grounding` (Researcher-subagent; Planner considers it), `decision-challenge` (Planner, as a "consider" reference), and `llm-behavior-guidelines` (CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, Planner).
> - **PLANNER-INJECTED** — all other skills are not statically bound to any agent. Planner selects them dynamically at planning time (≤3 per phase) and injects them via `skill_references`. The agents listed for these rows indicate *likely consumers when injected*, not agents that load the skill unconditionally.

| Domain | Skill File | Applicable Agents (binding; routing hint) | Keywords |
| -------- | ----------- | ------------------- | ---------- |
| Testing | `skills/patterns/tdd-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent | test, TDD, coverage, assertion, spec |
| Spec-Driven Development | `skills/patterns/spec-driven-development.md` | HARD-REFERENCED: Planner (consider). PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent | spec, requirements, scope, acceptance-criteria, before-planning |
| Debugging Discipline | `skills/patterns/debugging-discipline.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent, BrowserTester-subagent | debug, triage, stop-the-line, root-cause, regression |
| Code Simplification | `skills/patterns/code-simplification.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent | simplify, refactor, chesterton, dead-code, behavior-preservation |
| Error Handling | `skills/patterns/error-handling-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | error, exception, retry, fallback, boundary |
| Security | `skills/patterns/security-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | auth, input validation, injection, XSS, CSRF, secrets |
| Performance | `skills/patterns/performance-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | query, N+1, pagination, cache, batch, index |
| Completeness | `skills/patterns/completeness-traceability.md` | PLANNER-INJECTED: Planner, PlanAuditor-subagent, CodeReviewer-subagent | requirements, coverage, traceability, orphan, RTM, scope |
| Integration | `skills/patterns/integration-validator.md` | PLANNER-INJECTED: Planner, PlanAuditor-subagent, CoreImplementer-subagent | dependency, contract, interface, collision, compatibility, wave |
| Orchestration Audit | `skills/patterns/orchestration-audit-playbook.md` | PLANNER-INJECTED: Planner, Orchestrator, CodeMapper-subagent, Researcher-subagent, PlanAuditor-subagent, AssumptionVerifier-subagent, ExecutabilityVerifier-subagent, CodeReviewer-subagent, TechnicalWriter-subagent | orchestration, audit, traceability, schema, prompt, grants, hidden-defect, validation, approval, phase-boundary |
| Idea-to-Prompt | `skills/patterns/idea-to-prompt.md` | HARD-REFERENCED: Planner | idea, vague, abstract, brainstorm, concept, interview |
| LLM Behavior | `skills/patterns/llm-behavior-guidelines.md` | HARD-REFERENCED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, Planner. PLANNER-INJECTED: PlatformEngineer-subagent | overengineering, bloat, abstraction, assumption, surgical, scope drift, simplicity |
| PreFlect | `skills/patterns/preflect-core.md` | HARD-REFERENCED: All agents | preflect, pre-action, gate, risk class, scope drift, schema drift, missing evidence, safety |
| Reflection Loop | `skills/patterns/reflection-loop.md` | PLANNER-INJECTED: Orchestrator, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | reflection, pre-retry, fix hint, root cause, failure analysis |
| Budget Tracking | `skills/patterns/budget-tracking.md` | PLANNER-INJECTED: Orchestrator, Planner, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | budget, token cap, wall-clock, cost, early stop, resource cap |
| Memory Hygiene | `skills/patterns/repo-memory-hygiene.md` | HARD-REFERENCED: Orchestrator, CodeReviewer-subagent, PlanAuditor-subagent. PLANNER-INJECTED: Planner | memory, pollution, dedup, NOTES.md, archive, repo-memory |
| Memory Promotion | `skills/patterns/memory-promotion-candidates.md` | HARD-REFERENCED: Orchestrator. PLANNER-INJECTED: Planner | memory, candidate, promotion, transcript, classification |
| Security Review Discipline | `skills/patterns/security-review-discipline.md` | HARD-REFERENCED: CodeReviewer-subagent | security, vulnerability, confidence, exclusion, false-positive |
| Source Grounding | `skills/patterns/source-grounding.md` | HARD-REFERENCED: Researcher-subagent; Planner (consider) | official, source, provenance, external, framework, API, unverified, license |
| Decision Challenge | `skills/patterns/decision-challenge.md` | HARD-REFERENCED: Planner (consider). PLANNER-INJECTED: PlanAuditor-subagent, CodeReviewer-subagent | high-risk, architecture, irreversible, counterargument, alternative, decision |

## Loading Protocol

- **Planning/Review phase:** Planner, PlanAuditor-subagent, and CodeReviewer-subagent load referenced planning/review skills when performing planning or review-scoped work. Planner includes `skill_references: ["skills/patterns/<domain>.md"]` in phase definition.
- **Execution phase:** Implementation agent reads each referenced skill file via `read/readFile` before starting work.
- **Review phase:** CodeReviewer-subagent and PlanAuditor-subagent reference applicable skills when evaluating implementation quality.

## Adding New Skills

1. Create a new pattern file in `skills/patterns/`.
2. Add an entry to the Domain Mapping table above.
3. Run `evals/validate.mjs` to verify consistency.
