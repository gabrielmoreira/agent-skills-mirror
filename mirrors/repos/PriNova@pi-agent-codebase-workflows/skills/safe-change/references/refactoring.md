# Refactoring Workflow

Use for behavior-preserving structure changes, design cleanup, decomposition, dependency direction cleanup, or reducing drift. Do not combine refactoring with feature work or unrelated bug fixes.

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
