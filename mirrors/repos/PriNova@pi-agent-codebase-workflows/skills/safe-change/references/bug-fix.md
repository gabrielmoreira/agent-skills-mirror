# Bug Fix Workflow

Use for errors, regressions, failing behavior, or mismatches between expected and actual behavior.

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
- Update `docs/agent/RISK_REGISTER.md` or scoped `RISK_REGISTER.md` if bug corresponds to known/new risk.
- Update `docs/agent/INVARIANTS.md`, `docs/agent/DATA_MODEL.md`, `docs/agent/CHANGE_GUIDE.md`, or scoped equivalents only if fix clarifies/changes durable rules.

Output:
- Files changed
- Root cause fixed
- Tests added/updated
- Validation results
- Documentation updates
- Remaining risks/follow-up
