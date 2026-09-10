# A Philosophy of Software Design vs The Pragmatic Programmer

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 20%
Overlap: 50%
Complementarity: 62%

## Loading Decision

Use together when broad design judgment and local construction discipline are both active: let A Philosophy of Software Design govern govern module depth, API shape, information hiding, and complexity reduction, and let The Pragmatic Programmer govern operate through ownership, DRY knowledge, orthogonality, reversible decisions, tracer feedback, automation, contracts, and pragmatic stopping points.

## Book A Pressure

- A Philosophy of Software Design should drive tasks that need module-depth, API-shape, information-hiding, and complexity-reduction judgment.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.

## Book B Pressure

- The Pragmatic Programmer should drive tasks where ownership, DRY knowledge, orthogonality, reversibility, tracer feedback, automation, and contracts dominate.
- Evidence: `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.

## Complementary Forces

- Claim: A Philosophy of Software Design contributes module-depth, API-shape, information-hiding, and complexity-reduction pressure; The Pragmatic Programmer contributes ownership, DRY-knowledge, orthogonality, reversibility, tracer-feedback, automation, and contract pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Conflicts

- Claim: The main risk is duplicate general guidance; choose a primary rule set when both try to govern the same local code-shape decision.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 7-9: corrects local-edit and ritual optimization by owning outcomes, reducing duplicated knowledge, keeping concerns independent, proving assumptions early, automating repeated work, and making intent clear.

## Use Together When

- Use together when a design decision needs APoSD complexity reduction and PragProg ownership, DRY knowledge, reversibility, feedback, or automation constraints.

## Prefer One When

- Prefer A Philosophy of Software Design or The Pragmatic Programmer according to which scope statement is actually triggered by the task.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 7-9: corrects local-edit and ritual optimization by owning outcomes, reducing duplicated knowledge, keeping concerns independent, proving assumptions early, automating repeated work, and making intent clear.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Review Notes

- External context was not used as decisive evidence for A Philosophy of Software Design vs The Pragmatic Programmer; the verdict is based on the cited local `mini` line ranges.
