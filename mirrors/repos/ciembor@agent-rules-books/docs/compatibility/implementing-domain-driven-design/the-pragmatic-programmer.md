# Implementing Domain-Driven Design vs The Pragmatic Programmer

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- Implementing Domain-Driven Design should drive tasks where DDD implementation choices around contexts, aggregates, repositories, events, services, and translations dominate.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Book B Pressure

- The Pragmatic Programmer should drive tasks where ownership, DRY knowledge, orthogonality, reversibility, tracer feedback, automation, and contracts dominate.
- Evidence: `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.

## Complementary Forces

- Claim: Implementing Domain-Driven Design contributes implementation-level DDD pressure around contexts, aggregates, repositories, events, services, and translation; The Pragmatic Programmer contributes ownership, DRY-knowledge, orthogonality, reversibility, tracer-feedback, automation, and contract pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
  - `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.

## Use Together When

- Use together when one change simultaneously involves DDD implementation choices around aggregates, repositories, events, services, and translations and ownership, DRY knowledge, orthogonality, feedback, automation, contracts, and pragmatic stopping points; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 3-5: applies as a general engineering operating style for accountable delivery, adaptability, fast feedback, and easy-to-change code.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 7-9: corrects local-edit and ritual optimization by owning outcomes, reducing duplicated knowledge, keeping concerns independent, proving assumptions early, automating repeated work, and making intent clear.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 13-35: requires pragmatic non-dogmatic choices, ownership of risks, future maintenance awareness, one authoritative knowledge representation, orthogonality, reversible volatile decisions, useful domain vocabulary, tracer bullets, prototypes, real requirements, automation, feedback loops, explicit contracts/failure categories/resource ownership, plain text/open formats, visible shared state/async costs, understood tooling, fact-based debugging, small increments, communicative artifacts, team responsibility, and broken-window containment.
- `the-pragmatic-programmer/the-pragmatic-programmer.mini.md` lines 56-65: checks authoritative knowledge, independent concerns and reversible choices, feedback, accepted prototype/tool behavior, contracts/failures/resources, visible state/coupling, automation, relevant tests, communicative artifacts, and touched-area improvement/containment.

## Review Notes

- External context was not used as decisive evidence for Implementing Domain-Driven Design vs The Pragmatic Programmer; the verdict is based on the cited local `mini` line ranges.
