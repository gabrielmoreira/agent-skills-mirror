# Clean Code vs Code Complete

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 30%
Overlap: 78%
Complementarity: 45%

## Loading Decision

Choose one construction-quality rule set. Clean Code is a tighter local readability and cleanup guide; Code Complete is broader construction discipline covering requirements, architecture fit, data, control flow, errors, debugging, reviews, and tuning. Loading both together mostly duplicates implementation hygiene and review pressure.

## Book A Pressure

- Clean Code drives local readability, naming, small focused functions, side-effect clarity, boundary hygiene, tests, and scoped cleanup.
- Evidence: `clean-code/clean-code.mini.md` lines 3-9 and 13-26.

## Book B Pressure

- Code Complete drives broad construction quality: requirements clarity, data choices, control flow, validation, errors, reviews, debugging, refactoring, tuning, tools, layout, and comments.
- Evidence: `code-complete/code-complete.mini.md` lines 3-9 and 13-32.

## Complementary Forces

- Claim: Code Complete can supply broader construction checks around requirements, defensive programming, debugging, and tuning that Clean Code does not emphasize as strongly.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: local clean-code delivery, naming, functions, side effects, boundaries, tests, and cleanup.
  - `code-complete/code-complete.mini.md` lines 13-15 and 27-30: requirements, architecture fit, risk, reviews, debugging, performance evidence, and tool leverage.

## Overlap

- Claim: The overlap is dominant in everyday coding: both push readable code, cohesive routines/modules, explicit data and control flow, comments that add value, tests, and reviewability.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 14-24: local reasoning, names, focused functions, parameters, side effects, representation, APIs, comments, and tests.
  - `code-complete/code-complete.mini.md` lines 15-25 and 31-32: clarity, cohesive routines, explicit data, simple control flow, boundary validation, error handling, focused modules, complexity reduction, and useful comments.

## Conflicts

- Claim: The conflict is mainly granularity and planning style. Clean Code's "let design emerge" can underweight Code Complete's upfront construction checks when risk is high; Code Complete's broader checklist can slow a small local cleanup.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 25-26: design emerges through tests, duplication removal, expressiveness, and minimal structure with smallest safe cleanup.
  - `code-complete/code-complete.mini.md` lines 13-14 and 35: before large construction, verify requirements, architecture, major risks, conventions, and success constraints.

## Use Together When

- Use together only if Code Complete is primary for risk/construction planning and Clean Code is limited to local readability in touched code.

## Prefer One When

- Prefer Clean Code for small implementation/review changes where local reasoning is the main problem.
- Prefer Code Complete for larger production construction, defensive programming, debugging, validation, or performance-sensitive work.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-9: local readability scope.
- `clean-code/clean-code.mini.md` lines 13-26: Clean Code implementation guidance.
- `code-complete/code-complete.mini.md` lines 3-9: construction-discipline scope.
- `code-complete/code-complete.mini.md` lines 13-32: Code Complete construction guidance.
- External context: Microsoft Press positions `Code Complete` around practical software construction: https://www.oreilly.com/library/view/code-complete-second/0735619670/
- External context: Clean Code is commonly positioned as readability and maintainability guidance around everyday code shape: https://www.oreilly.com/library/view/clean-code-a/9780136083238/

## Review Notes

- Keep as overlap. Code Complete is broader, but for active agent rules on one implementation task it often duplicates Clean Code's construction layer.
