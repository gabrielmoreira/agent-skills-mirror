---
name: safe-change
description: Safe-change workflow for documented codebases. Use for bug fixes, feature work, refactoring, risk-fix passes, test-only work, and docs-only work. Every workflow starts with preflight, then design/diagnosis, approval gate, implementation, validation, and semantic docs update only when needed.
---

# Safe Change

Goal: make changes in an existing documented codebase without architecture drift.

## Task/Focus Arguments

Prompt arguments may include a target, focus, or scope. Use these to limit investigation and implementation to a module, package, app, service, directory, user flow, risk cluster, or bounded domain area. In monorepos, prefer scoped preflight/design first, then broader consolidation only when durable docs need repo-level reconciliation.

## Core Rules

- Preflight comes first for every non-trivial task.
- Do not edit code during preflight/design/diagnosis unless explicitly asked.
- Separate bug fixing, feature work, and refactoring. Never combine in one pass.
- Prefer smallest safe change inside affected slice/module.
- Preserve public behavior unless task requires changing it.
- Add regression/characterization tests when behavior is risky or uncovered.
- Run focused validation first, then relevant broader validation.
- Update docs only when durable semantics changed: architecture, data model, invariants, dependency rules, public contracts, change workflow, or known risks.
- Do not explicitly read `AGENTS.md`; The harness injects root `AGENTS.md` automatically.

## Universal Preflight

Read first:
- `docs/agent/CHANGE_GUIDE.md` if present

Then read only docs relevant to task:
- `docs/agent/ARCHITECTURE.md` for module/flow changes
- `docs/agent/DATA_MODEL.md` for data changes
- `docs/agent/INVARIANTS.md` for rule-sensitive changes
- `docs/agent/DEPENDENCY_RULES.md` for imports/module boundaries
- `docs/agent/RISK_REGISTER.md` for risky areas
- `docs/agent/DESIGN_ISSUES.md` for refactoring/design work

Before editing code, produce:
1. Task classification: bug fix / feature / refactoring / risk-fix / test-only / docs-only
2. Relevant docs read
3. Affected slice/module/user flow
4. Expected files to inspect
5. Invariants/contracts at risk
6. Existing tests/validation commands
7. Whether implementation should proceed now or wait for approval

## Bug Diagnosis

After preflight, diagnose bug before editing.

Tasks:
1. Reproduce or locate bug.
2. Identify expected behavior.
3. Identify violated invariant, contract, or public behavior.
4. Identify affected files/modules.
5. Explain likely root cause.
6. Propose minimal fix plan.
7. Propose regression test and validation commands.

Stop unless user approved implementation.

## Bug Implementation

Continue from approved bug-fix plan.

Rules:
- Follow approved plan.
- Change production code only where necessary.
- Add/update regression test unless impossible; explain if impossible.
- Do not opportunistically refactor.
- Run focused test first, then relevant broader suite.
- Update `docs/agent/RISK_REGISTER.md` if bug corresponds to known/new risk.
- Update `docs/agent/INVARIANTS.md`, `docs/agent/DATA_MODEL.md`, or `docs/agent/CHANGE_GUIDE.md` only if fix clarifies/changes durable rules.

Output:
- Files changed
- Root cause fixed
- Tests added/updated
- Validation results
- Documentation updates
- Remaining risks/follow-up

## Feature Design

After preflight, design before implementation.

Tasks:
1. Feature summary
2. Affected user/execution flow
3. Affected modules/files
4. Data model impact
5. Invariants affected or introduced
6. Side effects needed and boundaries
7. Dependency rule impact
8. Risks
9. Test plan
10. Minimal implementation plan
11. Documentation update plan
12. Blocking open questions only

Rules:
- Prefer extending existing concepts over new abstractions.
- Keep side effects at existing side-effect boundaries.
- Do not introduce global/shared utilities unless justified.
- Stop unless user approved implementation.

## Feature Implementation

Continue from approved feature design.

Rules:
- Follow approved design.
- Keep changes inside affected slice/module when possible.
- No unrelated refactoring.
- Add/update tests according to test plan.
- Preserve existing invariants.
- Keep side effects behind existing boundaries.
- Update docs only for durable semantic changes.
- Run focused tests, then broader validation.

Output:
- Files changed
- Feature behavior implemented
- Data model changes
- Invariants added/changed
- Tests added/updated
- Validation results
- Documentation updates
- Remaining risks/limitations

## Refactoring Design

After preflight, design refactor before edits.

Rules:
- No behavior change.
- Treat refactoring as separate use case.
- Identify smell/design issue precisely with evidence.
- Identify tests protecting behavior.
- If tests insufficient, propose characterization tests first.
- Prefer staged refactorings over rewrites.
- Do not introduce new architecture style unless explicitly requested.

Output:
- Refactoring goal
- Current design problem
- Evidence
- Behavior to preserve
- Affected files/modules
- Invariants to preserve
- Required characterization tests
- Refactoring stages
- Validation plan
- Rollback strategy
- Documentation update plan

Stop unless user approved implementation.

## Refactoring Implementation

Continue from approved refactoring design, one smallest safe stage.

Rules:
- Preserve behavior.
- Do not combine with feature work.
- Do not fix unrelated bugs unless they block refactor.
- Add characterization tests before behavior-sensitive changes.
- Keep each change mechanically understandable.
- Run tests after each meaningful stage.
- Update docs only if durable structure/dependency/change guidance changed.

Output:
- Stage completed
- Files changed
- Behavior preserved
- Tests added/updated
- Validation results
- Documentation updates
- Remaining stages

## Risk-Fix Pass

Use when risk-derived tests fail or `RISK_REGISTER.md` identifies actionable risks.

Read first:
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/RISK_REGISTER.md`
- `docs/agent/INVARIANTS.md`
- `docs/agent/DATA_MODEL.md`

Rules:
- Do not fix all failing tests at once.
- Select one failing test or tightly related risk cluster.
- Prioritize: critical data corruption, security/safety, persistence/state inconsistency, public API/schema breakage, incorrect domain behavior, architecture boundary violation, performance/cleanup.
- Explain violated invariant.
- Identify minimal production-code change.
- Do not change test unless demonstrably wrong.
- Do not refactor unrelated code.
- Run focused test first, then surrounding suite.
- Update `docs/agent/RISK_REGISTER.md` status.

Output:
- Selected failing test/risk cluster
- Root cause
- Invariant violated
- Minimal fix plan
- Files changed
- Validation result
- Remaining failing tests/risks
