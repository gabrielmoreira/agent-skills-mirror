# Clean Code vs Refactoring

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

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 30-37: fires on mixed function phases, explanatory comments, mutation-query mixing, flags, duplicated concepts, boundary leakage, concurrency, behavior changes, and spreading cleanup.
  - `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.

## Use Together When

- Use together when existing code must be reshaped toward Clean Code goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 30-37: fires on mixed function phases, explanatory comments, mutation-query mixing, flags, duplicated concepts, boundary leakage, concurrency, behavior changes, and spreading cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
- `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Refactoring; the verdict is based on the cited local `mini` line ranges.
