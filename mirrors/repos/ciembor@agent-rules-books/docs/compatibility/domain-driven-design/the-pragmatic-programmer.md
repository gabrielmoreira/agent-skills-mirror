# Domain-Driven Design vs The Pragmatic Programmer

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Book B Pressure

- The Pragmatic Programmer should drive tasks where ownership, DRY knowledge, orthogonality, reversibility, tracer feedback, automation, and contracts dominate.
- Evidence: `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.

## Complementary Forces

- Claim: Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure; The Pragmatic Programmer contributes ownership, DRY-knowledge, orthogonality, reversibility, tracer-feedback, automation, and contract pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Use Together When

- Use together when one change simultaneously involves model language, invariants, lifecycle rules, and Bounded Contexts and ownership, DRY knowledge, orthogonality, feedback, automation, contracts, and pragmatic stopping points; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 7-9: corrects local-edit and ritual optimization by owning outcomes, reducing duplicated knowledge, keeping concerns independent, proving assumptions early, automating repeated work, and making intent clear.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Review Notes

- External context was not used as decisive evidence for Domain-Driven Design vs The Pragmatic Programmer; the verdict is based on the cited local `mini` line ranges.
