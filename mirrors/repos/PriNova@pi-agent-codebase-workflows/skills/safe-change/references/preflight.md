# Universal Preflight

Preflight comes before every non-trivial safe-change task.

Read first:
- `docs/agent/CHANGE_GUIDE.md` if present
- `docs/agent/SCOPES.md` if present; then apply `references/scoped-docs.md`
- matching scoped `REPO_INVENTORY.md` or top-level `docs/agent/REPO_INVENTORY.md` if present, for entry points, commands, and external boundaries
- matching scoped `VALIDATION_BASELINE.md` or top-level `docs/agent/VALIDATION_BASELINE.md` if present, for known-good validation commands and blockers

If scoped docs match the task, read nearest scoped `README.md` only if present and only task-relevant scoped docs first. Then read only missing or repo-wide top-level docs relevant to task:
- `docs/agent/PROJECT_INTENT.md` or scoped `PROJECT_INTENT.md` for scope, non-goals, users, journeys, and product constraints
- `docs/agent/ARCHITECTURE.md` or scoped `ARCHITECTURE.md` for module/flow changes
- `docs/agent/DATA_FLOW.md` or scoped `DATA_FLOW.md` for user journeys, pipelines, transformations, side effects, and error states
- `docs/agent/DATA_MODEL.md` or scoped `DATA_MODEL.md` for data changes
- `docs/agent/INVARIANTS.md` or scoped `INVARIANTS.md` for rule-sensitive changes
- `docs/agent/DEPENDENCY_RULES.md` or scoped `DEPENDENCY_RULES.md` for imports/module boundaries
- `docs/agent/RISK_REGISTER.md` or scoped `RISK_REGISTER.md` for risky areas
- `docs/agent/DESIGN_ISSUES.md` or scoped `DESIGN_ISSUES.md` for refactoring/design work
- `docs/agent/TESTING_STRATEGY.md` or scoped `TESTING_STRATEGY.md` for test design and validation approach
- scoped `CONTRACTS.md` files for touched cross-scope APIs, shared types, schemas, events, generated clients, or persistence boundaries

When artifact headers exist, treat `planned` docs as intent and verify implementation-sensitive claims against source evidence.

Before editing code, produce:
1. Task classification: bug fix / feature / refactoring / risk-fix / test-only / docs-only
2. Relevant docs read
3. Affected slice/module/user flow
4. Expected files to inspect
5. Invariants/contracts at risk
6. Existing tests/validation commands
7. Whether implementation should proceed now or wait for approval
