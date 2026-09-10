# A Philosophy of Software Design vs Working Effectively with Legacy Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- A Philosophy of Software Design should drive tasks that need module-depth, API-shape, information-hiding, and complexity-reduction judgment.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.

## Book B Pressure

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: A Philosophy of Software Design contributes module-depth, API-shape, information-hiding, and complexity-reduction pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward A Philosophy of Software Design goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Review Notes

- External context was not used as decisive evidence for A Philosophy of Software Design vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
