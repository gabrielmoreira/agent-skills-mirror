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

| Domain | Skill File | Applicable Agents | Keywords |
| -------- | ----------- | ------------------- | ---------- |
| Testing | `skills/patterns/tdd-patterns.md` | CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent | test, TDD, coverage, assertion, spec |
| Error Handling | `skills/patterns/error-handling-patterns.md` | CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | error, exception, retry, fallback, boundary |
| Security | `skills/patterns/security-patterns.md` | CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | auth, input validation, injection, XSS, CSRF, secrets |
| Performance | `skills/patterns/performance-patterns.md` | CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | query, N+1, pagination, cache, batch, index |
| Completeness | `skills/patterns/completeness-traceability.md` | Planner, PlanAuditor-subagent, CodeReviewer-subagent | requirements, coverage, traceability, orphan, RTM, scope |
| Integration | `skills/patterns/integration-validator.md` | Planner, PlanAuditor-subagent, CoreImplementer-subagent | dependency, contract, interface, collision, compatibility, wave |
| Orchestration Audit | `skills/patterns/orchestration-audit-playbook.md` | Planner, Orchestrator, CodeMapper-subagent, Researcher-subagent, PlanAuditor-subagent, AssumptionVerifier-subagent, ExecutabilityVerifier-subagent, CodeReviewer-subagent, TechnicalWriter-subagent | orchestration, audit, traceability, schema, prompt, grants, hidden-defect, validation, approval, phase-boundary |
| Idea-to-Prompt | `skills/patterns/idea-to-prompt.md` | Planner | idea, vague, abstract, brainstorm, concept, interview |
| LLM Behavior | `skills/patterns/llm-behavior-guidelines.md` | CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, Planner, PlatformEngineer-subagent | overengineering, bloat, abstraction, assumption, surgical, scope drift, simplicity |
| PreFlect | `skills/patterns/preflect-core.md` | All agents | preflect, pre-action, gate, risk class, scope drift, schema drift, missing evidence, safety |
| Reflection Loop | `skills/patterns/reflection-loop.md` | Orchestrator, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | reflection, pre-retry, fix hint, root cause, failure analysis |
| Budget Tracking | `skills/patterns/budget-tracking.md` | Orchestrator, Planner, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | budget, token cap, wall-clock, cost, early stop, resource cap |
| Memory Hygiene | `skills/patterns/repo-memory-hygiene.md` | Orchestrator, Planner, PlanAuditor-subagent, CodeReviewer-subagent | memory, pollution, dedup, NOTES.md, archive, repo-memory |
| Memory Promotion | `skills/patterns/memory-promotion-candidates.md` | Orchestrator, Planner | memory, candidate, promotion, transcript, classification |
| Security Review Discipline | `skills/patterns/security-review-discipline.md` | CodeReviewer-subagent | security, vulnerability, confidence, exclusion, false-positive |

## Loading Protocol

- **Planning/Review phase:** Planner, PlanAuditor-subagent, and CodeReviewer-subagent load referenced planning/review skills when performing planning or review-scoped work. Planner includes `skill_references: ["skills/patterns/<domain>.md"]` in phase definition.
- **Execution phase:** Implementation agent reads each referenced skill file via `read/readFile` before starting work.
- **Review phase:** CodeReviewer-subagent and PlanAuditor-subagent reference applicable skills when evaluating implementation quality.

## Adding New Skills

1. Create a new pattern file in `skills/patterns/`.
2. Add an entry to the Domain Mapping table above.
3. Run `evals/validate.mjs` to verify consistency.
