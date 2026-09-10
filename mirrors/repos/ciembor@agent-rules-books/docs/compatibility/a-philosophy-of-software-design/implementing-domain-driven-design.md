# A Philosophy of Software Design vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- A Philosophy of Software Design should drive tasks that need module-depth, API-shape, information-hiding, and complexity-reduction judgment.
- Evidence: `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.

## Book B Pressure

- Implementing Domain-Driven Design should drive tasks where DDD implementation choices around contexts, aggregates, repositories, events, services, and translations dominate.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Complementary Forces

- Claim: A Philosophy of Software Design contributes module-depth, API-shape, information-hiding, and complexity-reduction pressure; Implementing Domain-Driven Design contributes implementation-level DDD pressure around contexts, aggregates, repositories, events, services, and translation. Together they are useful only where both scopes are active.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.

## Use Together When

- Use together when one change simultaneously involves module/API depth, information hiding, and complexity reduction and DDD implementation choices around aggregates, repositories, events, services, and translations; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 3-5: applies to module design, API changes, decomposition, refactoring, naming, comments, tests, performance work, and changes where complexity spreads.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 7-10: corrects the false belief that small pieces, wrappers, patterns, or documentation are simple when they increase cognitive load.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 13-20: makes reduced complexity, deep modules, caller-oriented interfaces, hidden volatile details, downward-pulled complexity, right-sized generality, and complexity-based split/merge decisions central.
- `a-philosophy-of-software-design/a-philosophy-of-software-design.mini.md` lines 42-46: finishes by checking understanding effort, interface value, localized decisions, protected internals, and non-duplicative names/comments.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Review Notes

- External context was not used as decisive evidence for A Philosophy of Software Design vs Implementing Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
