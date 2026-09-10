# Implementing Domain-Driven Design vs Refactoring

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Implementing Domain-Driven Design should drive tasks where DDD implementation choices around contexts, aggregates, repositories, events, services, and translations dominate.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Book B Pressure

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Complementary Forces

- Claim: Implementing Domain-Driven Design contributes implementation-level DDD pressure around contexts, aggregates, repositories, events, services, and translation; Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
  - `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.
  - `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.

## Use Together When

- Use together when existing code must be reshaped toward Implementing Domain-Driven Design goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.
- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 13-26: requires observable behavior preservation, small reversible steps, safety nets, preparatory/follow-up refactoring around feature work, current-smell focus, simplest named moves, intent-revealing names/functions, behavior and state with owners, explicit data/mutation/contracts, honest conditional simplification, evidence-based abstraction, preserved error semantics, reviewable patch intent, and stop conditions.
- `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Review Notes

- External context was not used as decisive evidence for Implementing Domain-Driven Design vs Refactoring; the verdict is based on the cited local `mini` line ranges.
