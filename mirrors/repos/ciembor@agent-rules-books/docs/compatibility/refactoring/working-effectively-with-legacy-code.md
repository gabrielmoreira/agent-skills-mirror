# Refactoring vs Working Effectively with Legacy Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 58%
Complementarity: 76%

## Loading Decision

Use together for risky existing-code changes: use legacy-code control to create observation/seams, then use refactoring discipline for the behavior-preserving structural move.

## Book A Pressure

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Book B Pressure

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 30-39: fires on structural friction before features, unclear bug code, absent tests, third duplication, mixed responsibilities, shotgun surgery, repeated conditionals, UI/domain mixing, patch intent mixing, and rewrite temptation.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.

## Conflicts

- Claim: The tension is sequencing: refactoring pressure must wait until characterization or a safe seam exists in weakly tested code.
- Evidence:
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward Refactoring goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
- `refactoring/refactoring.mini.md` lines 30-39: fires on structural friction before features, unclear bug code, absent tests, third duplication, mixed responsibilities, shotgun surgery, repeated conditionals, UI/domain mixing, patch intent mixing, and rewrite temptation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 31-39: fires on uncertain behavior, excessive test setup, hard runtime boundaries, large methods/classes, database/UI/framework/API-boundary code, magical seams, repeated edits, and rewrite temptation.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.

## Review Notes

- External context was not used as decisive evidence for Refactoring vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
