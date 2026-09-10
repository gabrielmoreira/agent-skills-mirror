# Clean Code vs Refactoring.Guru

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

- Refactoring.Guru should drive tasks where smell diagnosis, smallest treatment choice, behavior verification, and stop conditions dominate.
- Evidence: `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.

## Complementary Forces

- Claim: Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure; Refactoring.Guru contributes smell-diagnosis, smallest-treatment, behavior-verification, and stop-condition pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 30-37: fires on mixed function phases, explanatory comments, mutation-query mixing, flags, duplicated concepts, boundary leakage, concurrency, behavior changes, and spreading cleanup.
  - `refactoring-guru/refactoring-guru.mini.md` lines 13-37: requires separating behavior changes, diagnosing smell/cost/scope/end state/verification/stop condition, smallest treatment first, runnable small transformations, checks after risky moves, Rule of Three, debt paid by current cost, smell categories, bloaters/switch/change/coupler/dispensable treatments, comments vs code fixes, behavior with data, no getter/setter-only encapsulation, no speculative abstractions, public compatibility, extraction/movement/condition/data/generalization prechecks, and deliberate exceptions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
  - `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
  - `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.

## Use Together When

- Use together when existing code must be reshaped toward Clean Code goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 30-37: fires on mixed function phases, explanatory comments, mutation-query mixing, flags, duplicated concepts, boundary leakage, concurrency, behavior changes, and spreading cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.
- `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.
- `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.
- `refactoring-guru/refactoring-guru.mini.md` lines 13-37: requires separating behavior changes, diagnosing smell/cost/scope/end state/verification/stop condition, smallest treatment first, runnable small transformations, checks after risky moves, Rule of Three, debt paid by current cost, smell categories, bloaters/switch/change/coupler/dispensable treatments, comments vs code fixes, behavior with data, no getter/setter-only encapsulation, no speculative abstractions, public compatibility, extraction/movement/condition/data/generalization prechecks, and deliberate exceptions.
- `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.

## Review Notes

- External context was not used as decisive evidence for Clean Code vs Refactoring.Guru; the verdict is based on the cited local `mini` line ranges.
