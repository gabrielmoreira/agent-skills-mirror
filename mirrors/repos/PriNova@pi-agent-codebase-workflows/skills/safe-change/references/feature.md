# Feature Workflow

Use for new behavior, API capability, UI behavior, data flow, integration, or user-facing functionality.

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
