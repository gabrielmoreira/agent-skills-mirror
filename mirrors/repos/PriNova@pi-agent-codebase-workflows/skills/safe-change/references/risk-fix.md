# Risk-Fix Workflow

Use when risk-derived tests fail or `RISK_REGISTER.md` / scoped `RISK_REGISTER.md` identifies actionable risks.

Read first:
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/SCOPES.md` if present; then apply `references/scoped-docs.md`
- matching scoped risk/invariant/data docs when applicable
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
- Update `docs/agent/RISK_REGISTER.md` or scoped `RISK_REGISTER.md` status.

Output:
- Selected failing test/risk cluster
- Root cause
- Invariant violated
- Minimal fix plan
- Files changed
- Validation result
- Remaining failing tests/risks
