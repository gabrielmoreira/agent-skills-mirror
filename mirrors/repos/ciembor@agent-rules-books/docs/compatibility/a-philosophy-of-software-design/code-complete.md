# A Philosophy of Software Design vs Code Complete

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 20%
Overlap: 50%
Complementarity: 62%

## Loading Decision

Use together when broad design judgment and local construction discipline are both active: let A Philosophy of Software Design govern govern module depth, API shape, information hiding, and complexity reduction, and let Code Complete govern reduce defects through disciplined construction, data clarity, defensive checks, evidence-based debugging, and reviewable increments.

## Book A Pressure

- A Philosophy of Software Design should drive tasks that need module-depth, API-shape, information-hiding, and complexity-reduction judgment.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.

## Book B Pressure

- Code Complete should drive tasks where defect reduction, data clarity, defensive checks, evidence-based debugging, and reviewability dominate.
- Evidence: `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.

## Complementary Forces

- Claim: A Philosophy of Software Design contributes module-depth, API-shape, information-hiding, and complexity-reduction pressure; Code Complete contributes defect-reduction, data-clarity, defensive-check, evidence-based-debugging, and reviewability pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
  - `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
  - `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.

## Conflicts

- Claim: The main risk is duplicate general guidance; choose a primary rule set when both try to govern the same local code-shape decision.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
  - `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.

## Use Together When

- Use together when construction choices need Code Complete defect-risk checks and APoSD must decide whether the resulting routines, data types, and interfaces reduce total complexity.

## Prefer One When

- Prefer A Philosophy of Software Design or Code Complete according to which scope statement is actually triggered by the task.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
- `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.
- `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
- `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
- `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.

## Review Notes

- External context was not used as decisive evidence for A Philosophy of Software Design vs Code Complete; the verdict is based on the cited local `mini` line ranges.
