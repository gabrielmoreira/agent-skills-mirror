# A Philosophy of Software Design vs Refactoring

Status: reviewed
Research basis: mini-plus-external

Verdict: ✅ Complementary

Conflict: 28%
Overlap: 46%
Complementarity: 74%

## Loading Decision

Load together when changing existing code toward a better design: Refactoring should govern the change process and behavior preservation; APoSD should govern whether the target module/API/decomposition actually reduces complexity. They are complementary only because their active pressures are different: process safety versus design quality.

## Book A Pressure

- APoSD drives reduced complexity, deep modules, information hiding, stable interfaces, comments as contracts/rationale, and design alternatives.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-25.

## Book B Pressure

- Refactoring drives behavior-preserving, small-step, test-backed structural change with explicit stop conditions.
- Evidence: `refactoring/refactoring.mini.md` lines 3-9 and 13-26.

## Complementary Forces

- Claim: APoSD defines what a better design looks like; Refactoring defines how to get there without hidden behavior change or rewrite pressure.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 15-18 and 29-38: deep modules, information hiding, caller simplicity, API leakage, splitting, comments, performance evidence, and public-contract tests.
  - `refactoring/refactoring.mini.md` lines 13-16 and 25-26: preserve observable behavior, work in small testable steps, use safety nets, separate feature work from structure, and stop at the requested friction.

## Overlap

- Claim: Both affect refactoring, naming, tests, boundaries, duplication, and abstraction, so there is noticeable overlap in code-change guidance.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 20-24 and 42-46: split by total complexity, names/comments as design information, tests through public contracts, and final design checks.
  - `refactoring/refactoring.mini.md` lines 17-24 and 43-49: current smell scope, named moves, ownership, explicit contracts, evidence-based abstraction, error semantics, and final review checks.

## Conflicts

- Claim: The tension is that APoSD can justify broader design exploration while Refactoring forbids turning cleanup into redesign. Refactoring must arbitrate sequencing and behavior preservation.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 14 and 29-30: compare alternatives for non-trivial decomposition and prove new boundaries hide complexity.
  - `refactoring/refactoring.mini.md` lines 9, 13, 17, and 26: do not turn cleanup into rewrite, preserve behavior, refactor the current blocking smell, and stop before speculative cleanup.

## Use Together When

- Use together for behavior-preserving refactoring where the target is deeper modules, cleaner interfaces, lower cognitive load, or better information hiding.

## Prefer One When

- Prefer Refactoring when the task is mainly safe structural transformation.
- Prefer APoSD when the task is design judgment for new APIs, modules, abstraction boundaries, or complexity reduction.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-25: APoSD design-quality rules.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 29-38: APoSD triggers around awkward design, APIs, splitting, comments, and tests.
- `refactoring/refactoring.mini.md` lines 3-9: refactoring scope and bias.
- `refactoring/refactoring.mini.md` lines 13-26: refactoring process and stop condition.
- External context: APoSD is positioned around software-design complexity reduction: https://web.stanford.edu/~ouster/cgi-bin/book.php
- External context: Fowler describes refactoring as a disciplined technique for restructuring existing code: https://martinfowler.com/books/refactoring.html

## Review Notes

- This stays complementary, but not because "scope gates solve everything." It is complementary because one book controls the destination and the other controls safe movement.
