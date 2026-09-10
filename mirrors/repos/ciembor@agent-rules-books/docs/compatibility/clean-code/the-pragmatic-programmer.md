# Clean Code vs The Pragmatic Programmer

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 24%
Overlap: 68%
Complementarity: 54%

## Loading Decision

Choose one primary general coding rule set. Clean Code is local code-shape guidance; The Pragmatic Programmer is broader engineering operating style. They can be read together, but as active agent guidance they overlap on leaving code better, duplication, boundaries, feedback, tests, comments, names, and responsibility.

## Book A Pressure

- Clean Code pushes local readability, focused functions, command/query separation, boundary hygiene, tests, and scoped cleanup.
- Evidence: `clean-code/clean-code.mini.md` lines 3-9 and 13-26.

## Book B Pressure

- The Pragmatic Programmer pushes accountable delivery, DRY knowledge ownership, orthogonality, reversible choices, tracer bullets, prototypes, automation, feedback, contracts, diagnostics, and communication.
- Evidence: `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-9 and 13-35.

## Complementary Forces

- Claim: PragProg adds workflow, uncertainty, automation, feedback, and responsibility guidance beyond Clean Code's local code hygiene.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 13-26: local delivery, naming, functions, side effects, boundaries, tests, emergent design, and cleanup.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 20-24 and 31-35: tracer bullets, prototypes, requirements, automation, feedback, debugging, increments, communication, teams, and broken windows.

## Overlap

- Claim: Both guard against local decay, duplicated knowledge, poor boundaries, weak feedback, unclear names/comments, and unverified changes.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 14-26 and 41-47: local reasoning, names, functions, boundaries, tests, cleanup, and running checks.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 15-17, 23-25, 33, and 56-65: leave touched areas better, DRY, orthogonality, automation, feedback, contracts, communication, tests, and touched-area improvement.

## Conflicts

- Claim: The tension is dogma versus pragmatism. Clean Code can push fixed local forms, while PragProg says choose the practice and stopping point that improves real outcomes.
- Evidence:
  - `clean-code/clean-code.mini.md` lines 16-18: small focused functions, few parameters, command/query separation, and explicit side effects.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-14 and 52-65: be pragmatic rather than dogmatic, surface tradeoffs, and improve touched areas only where cost is low or containment is explicit.

## Use Together When

- Use together only if PragProg is the operating-style frame and Clean Code is limited to local code readability checks.

## Prefer One When

- Prefer Clean Code for local code review and implementation hygiene.
- Prefer The Pragmatic Programmer for uncertainty, feedback loops, automation, DRY knowledge, orthogonality, debugging, delivery process, and team-level engineering behavior.

## Source Basis

- `clean-code/clean-code.mini.md` lines 3-9: local clean-code scope.
- `clean-code/clean-code.mini.md` lines 13-26: local code-shape rules.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-9: broad engineering operating-style scope.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: pragmatic delivery, DRY, orthogonality, feedback, automation, contracts, errors, and communication.
- External context: The Pragmatic Bookshelf positions `The Pragmatic Programmer` as broad professional software-development guidance rather than only code formatting or routine design: https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/
- External context: Clean Code is commonly positioned around readable, maintainable code shape: https://www.oreilly.com/library/view/clean-code-a/9780136083238/

## Review Notes

- This is overlap, not direct contradiction. For active agent loading, using both is usually redundant unless their roles are explicitly separated.
