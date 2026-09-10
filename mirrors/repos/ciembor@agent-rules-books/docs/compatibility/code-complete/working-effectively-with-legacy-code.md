# Code Complete vs Working Effectively with Legacy Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Code Complete should drive tasks where defect reduction, data clarity, defensive checks, evidence-based debugging, and reviewability dominate.
- Evidence: `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.

## Book B Pressure

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: Code Complete contributes defect-reduction, data-clarity, defensive-check, evidence-based-debugging, and reviewability pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward Code Complete goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.
- `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
- `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
- `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Review Notes

- External context was not used as decisive evidence for Code Complete vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
