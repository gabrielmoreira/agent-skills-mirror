# Clean Code vs Working Effectively with Legacy Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Clean Code should drive tasks where local readability, naming, function shape, side effects, tests, and scoped cleanup dominate.
- Evidence: `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.

## Book B Pressure

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward Clean Code goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
