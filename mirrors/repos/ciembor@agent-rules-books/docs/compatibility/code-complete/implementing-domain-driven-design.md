# Code Complete vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 14%
Overlap: 38%
Complementarity: 74%

## Loading Decision

Use together when domain language, invariants, lifecycle, or Bounded Contexts affect the task and the other rule set governs implementation quality, reliability, data, or safe change.

## Book A Pressure

- Code Complete should drive tasks where defect reduction, data clarity, defensive checks, evidence-based debugging, and reviewability dominate.
- Evidence: `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.

## Book B Pressure

- Implementing Domain-Driven Design should drive tasks where DDD implementation choices around contexts, aggregates, repositories, events, services, and translations dominate.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Complementary Forces

- Claim: Code Complete contributes defect-reduction, data-clarity, defensive-check, evidence-based-debugging, and reviewability pressure; Implementing Domain-Driven Design contributes implementation-level DDD pressure around contexts, aggregates, repositories, events, services, and translation. Together they are useful only where both scopes are active.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Conflicts

- Claim: The tension is DDD ceremony: tactical patterns must protect model meaning and should not displace the other rule set's simpler construction, refactoring, data, or operational constraints.
- Evidence:
  - `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.

## Use Together When

- Use together when one change simultaneously involves defect-risk construction, data clarity, defensive checks, and reviewability and DDD implementation choices around aggregates, repositories, events, services, and translations; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer the DDD rule set when language, lifecycle, invariants, or context boundaries drive design; prefer the other book for tasks without visible domain-model pressure.

## Source Basis

- `code-complete/code-complete.mini.md` lines 3-5: applies to implementation, change, review, debugging, refactoring, and tuning of production code.
- `code-complete/code-complete.mini.md` lines 7-9: corrects accidental construction by choosing lower defect risk and easier reasoning over clever idioms.
- `code-complete/code-complete.mini.md` lines 13-31: requires construction prerequisites, small validated slices, clear routines/data/control flow, validated data-driven logic, trust-boundary validation, explicit error semantics, cohesive modules, complexity management, small increments, evidence-based debugging, measured tuning, and useful tooling/comments.
- `code-complete/code-complete.mini.md` lines 51-56: checks requirements, architecture fit, construction approach, readable code structure, deliberate inputs/errors/invariants, inspectable flow, evidence-based validation, and reviewable change size.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Review Notes

- External context was not used as decisive evidence for Code Complete vs Implementing Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
