# Skill Library Index

## Purpose

Reusable domain-specific patterns for the slim Copilot-first model. `controlflow-planner` selects relevant patterns during planning and includes them as `skill_references` in phase definitions. The executor role (a conceptual role from the preserved taxonomy, executed inline by native Copilot) loads referenced patterns before starting work.

## Discovery Protocol

1. `controlflow-planner` reads this index during planning (Step 5 — after Complexity Gate).
2. Match task domain keywords against the Domain column below.
3. Select ≤3 most relevant patterns based on task context.
4. Include selected pattern file paths in each applicable phase's `skill_references` array.
5. The executor role (native Copilot) reads referenced pattern files before executing phase tasks.

## Domain Mapping

> **Binding legend — read before using the "Applicable Agents" column.** This column is a routing hint, not a guarantee. In the slim Copilot-first model, `@controlflow-planner` (`.github/agents/controlflow-planner.agent.md`) is the sole shipped agent. The names listed below are the **preserved conceptual role taxonomy** — the 8 `executor_agent` names (CodeMapper-subagent, Researcher-subagent, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent, TechnicalWriter-subagent, BrowserTester-subagent, CodeReviewer-subagent) plus the 3 inline verify roles (PlanAuditor-subagent, AssumptionVerifier-subagent, ExecutabilityVerifier-subagent). These are roles `controlflow-planner` assigns in plan phases and native Copilot executes inline; they are **conceptual roles, not shipped agent files**. The legacy 13-agent dispatch surface (root `*.agent.md`, including `Orchestrator.agent.md`) is retired.
>
> Two binding modes apply:
> - **HARD-REFERENCED** — the pattern is statically cited by name in a shipped ControlFlow surface (the planner agent or a workflow skill's reference section). In the current slim model, no shipped surface statically cites a pattern file, so this mode has no current instances; the HARD-REFERENCED designations below are carried from the legacy 13-agent binding map as historical binding intent and will be re-validated when a shipped ControlFlow surface cites a pattern. Treat every pattern as PLANNER-INJECTED until then.
> - **PLANNER-INJECTED** — `controlflow-planner` selects the pattern dynamically at planning time (≤3 per phase) and injects it via `skill_references`. The roles listed for these rows indicate *likely consumers when injected* (the conceptual role that executes the phase), not shipped agents that load the pattern unconditionally.

| Domain | Skill File | Applicable Agents (binding; routing hint) | Keywords |
| -------- | ----------- | ------------------- | ---------- |
| Testing | `skills/patterns/tdd-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent | test, TDD, coverage, assertion, spec |
| Spec-Driven Development | `skills/patterns/spec-driven-development.md` | HARD-REFERENCED: controlflow-planner (consider). PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent | spec, requirements, scope, acceptance-criteria, before-planning |
| Debugging Discipline | `skills/patterns/debugging-discipline.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent, BrowserTester-subagent | debug, triage, stop-the-line, root-cause, regression |
| Code Simplification | `skills/patterns/code-simplification.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent | simplify, refactor, chesterton, dead-code, behavior-preservation, yagni, stdlib, native, overengineering, dependency |
| Error Handling | `skills/patterns/error-handling-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | error, exception, retry, fallback, boundary |
| Security | `skills/patterns/security-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | auth, input validation, injection, XSS, CSRF, secrets |
| Performance | `skills/patterns/performance-patterns.md` | PLANNER-INJECTED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, PlanAuditor-subagent | query, N+1, pagination, cache, batch, index |
| Completeness | `skills/patterns/completeness-traceability.md` | PLANNER-INJECTED: controlflow-planner, PlanAuditor-subagent, CodeReviewer-subagent | requirements, coverage, traceability, orphan, RTM, scope |
| Integration | `skills/patterns/integration-validator.md` | PLANNER-INJECTED: controlflow-planner, PlanAuditor-subagent, CoreImplementer-subagent | dependency, contract, interface, collision, compatibility, wave |
| Idea-to-Prompt | `skills/patterns/idea-to-prompt.md` | HARD-REFERENCED: controlflow-planner | idea, vague, abstract, brainstorm, concept, interview |
| LLM Behavior | `skills/patterns/llm-behavior-guidelines.md` | HARD-REFERENCED: CoreImplementer-subagent, UIImplementer-subagent, CodeReviewer-subagent, controlflow-planner. PLANNER-INJECTED: PlatformEngineer-subagent | overengineering, bloat, abstraction, assumption, surgical, scope drift, simplicity |
| PreFlect | `skills/patterns/preflect-core.md` | HARD-REFERENCED: controlflow-planner (all conceptual roles) | preflect, pre-action, gate, risk class, scope drift, schema drift, missing evidence, safety |
| Reflection Loop | `skills/patterns/reflection-loop.md` | PLANNER-INJECTED: controlflow-planner, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | reflection, pre-retry, fix hint, root cause, failure analysis |
| Budget Tracking | `skills/patterns/budget-tracking.md` | PLANNER-INJECTED: controlflow-planner, CoreImplementer-subagent, UIImplementer-subagent, PlatformEngineer-subagent | budget, token cap, wall-clock, cost, early stop, resource cap |
| Memory Hygiene | `skills/patterns/repo-memory-hygiene.md` | HARD-REFERENCED: controlflow-planner, CodeReviewer-subagent, PlanAuditor-subagent. PLANNER-INJECTED: controlflow-planner | memory, pollution, dedup, NOTES.md, archive, repo-memory |
| Memory Promotion | `skills/patterns/memory-promotion-candidates.md` | HARD-REFERENCED: controlflow-planner. PLANNER-INJECTED: controlflow-planner | memory, candidate, promotion, transcript, classification |
| Security Review Discipline | `skills/patterns/security-review-discipline.md` | HARD-REFERENCED: CodeReviewer-subagent | security, vulnerability, confidence, exclusion, false-positive |
| Source Grounding | `skills/patterns/source-grounding.md` | HARD-REFERENCED: Researcher-subagent; controlflow-planner (consider) | official, source, provenance, external, framework, API, unverified, license |
| Decision Challenge | `skills/patterns/decision-challenge.md` | HARD-REFERENCED: controlflow-planner (consider). PLANNER-INJECTED: PlanAuditor-subagent, CodeReviewer-subagent | high-risk, architecture, irreversible, counterargument, alternative, decision |

## Loading Protocol

- **Planning/Review phase:** `controlflow-planner` and the `controlflow-verify` review phases (the PlanAuditor and CodeReviewer conceptual roles, performed inline) load referenced planning/review patterns when performing planning or review-scoped work. `controlflow-planner` includes `skill_references: ["skills/patterns/<domain>.md"]` in the phase definition.
- **Execution phase:** The executor role (native Copilot) reads each referenced pattern file before starting work.
- **Review phase:** The CodeReviewer and PlanAuditor conceptual roles (performed inline by `controlflow-verify`) reference applicable patterns when evaluating implementation quality.

## Adding New Patterns

1. Create a new pattern file in `skills/patterns/`.
2. Add an entry to the Domain Mapping table above.
3. Run `cd evals && npm test` to verify consistency (the skill-discoverability suite validates that every `skills/patterns/` file is registered in the index and every index entry resolves to a real file).