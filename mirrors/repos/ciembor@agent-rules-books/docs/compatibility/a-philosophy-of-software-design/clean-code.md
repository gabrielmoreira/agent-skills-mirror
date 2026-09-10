# A Philosophy of Software Design vs Clean Code

Status: reviewed
Research basis: mini-plus-external

Verdict: 🔁 Overlap

Conflict: 55%
Overlap: 72%
Complementarity: 42%

## Loading Decision

Choose one as the primary design/hygiene rule set. These books both govern everyday design, naming, comments, functions, tests, and readability, but they pull differently on function size and comments. Use APoSD when module depth, information hiding, and API shape are the main risk. Use Clean Code when local readability, touched-code cleanup, and small focused functions are the main risk.

## Book A Pressure

- APoSD optimizes for reduced cognitive load through deep modules, information hiding, stable interfaces, and comments that preserve contracts and rationale.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-25.

## Book B Pressure

- Clean Code optimizes for local reasoning, precise names, small focused functions, side-effect clarity, boundary hygiene, tests, and scoped cleanup.
- Evidence: `clean-code/clean-code.mini.md` lines 13-26.

## Complementary Forces

- Claim: Clean Code's local readability checks can help APoSD implementations stay concrete, while APoSD's deep-module checks prevent Clean Code from splitting code into shallow fragments.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 15-18: prefer deep modules and hide volatile decisions behind simpler contracts.
  - `clean-code/clean-code.mini.md` lines 14-18: optimize for local reasoning, precise names, focused functions, small parameter lists, and explicit side effects.

## Overlap

- Claim: The overlap is high because both rule sets govern the same code-quality layer: names, decomposition, comments, tests, boundaries, side effects, and maintainability.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 20-24: combine/split by complexity, document contracts/rationale, use names as design information, and protect behavior with public-contract tests.
  - `clean-code/clean-code.mini.md` lines 15-24: names, small functions, parameters, side effects, representation, APIs, comments, and tests.

## Conflicts

- Claim: The central conflict is small-function pressure versus deep-module pressure, plus different comment defaults. Equal loading can make an agent split until Clean Code is satisfied while APoSD says the split adds jumps and shallow interfaces.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 15, 20, and 33: reject shallow helper modules, split by total complexity rather than size, and check whether extraction adds jumps.
  - `clean-code/clean-code.mini.md` lines 16, 23, and 30-31: keep functions small and focused, use comments sparingly, and split functions that mix phases.

## Use Together When

- Use together only with an explicit arbiter: APoSD should arbitrate module/API boundaries, while Clean Code can arbitrate local naming, side effects, and touched-code readability.

## Prefer One When

- Prefer APoSD for module design, API changes, decomposition, abstraction, and comment-contract decisions.
- Prefer Clean Code for local implementation hygiene, small-scoped cleanup, naming, side effects, and everyday review.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-25: APoSD design pressure.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 29-38: APoSD trigger rules for awkward design, added boundaries, API leaks, splitting, comments, and testing.
- `clean-code/clean-code.mini.md` lines 13-26: Clean Code design and hygiene pressure.
- `clean-code/clean-code.mini.md` lines 30-37: Clean Code triggers for splitting phases, comments, command/query separation, abstraction, adapters, tests, and cleanup scope.
- External context: Ousterhout's APoSD page explicitly notes added comparisons with Clean Code because there are significant differences, especially around method length and comments: https://web.stanford.edu/~ouster/cgi-bin/book.php

## Review Notes

- This is the clearest non-DDD substitute/tension pair. It should not be marked complementary unless one rule set is explicitly made primary for the disputed decisions.
