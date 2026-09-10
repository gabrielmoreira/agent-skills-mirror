# Designing Data-Intensive Applications vs Implementing Domain-Driven Design

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 35%
Complementarity: 80%

## Loading Decision

Use together when the task changes state, events, schemas, queues, projections, caches, consistency, or ownership while also needing Implementing Domain-Driven Design pressure.

## Book A Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Book B Pressure

- Implementing Domain-Driven Design should drive tasks where DDD implementation choices around contexts, aggregates, repositories, events, services, and translations dominate.
- Evidence: `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.

## Complementary Forces

- Claim: Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure; Implementing Domain-Driven Design contributes implementation-level DDD pressure around contexts, aggregates, repositories, events, services, and translation. Together they are useful only where both scopes are active.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Conflicts

- Claim: The tension is over-modeling: the non-data rule set may improve structure, but DDIA requires explicit data semantics before abstractions hide source-of-truth or failure behavior.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
  - `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 35-44: fires on ambiguous terms, imports across contexts, foreign or infrastructure shapes in domain code, aggregate transaction pressure, external mutation of aggregates, CRUD repositories, command-like events, application-service business branching, representation pressure, and simple CRUD vs real lifecycle complexity.

## Use Together When

- Use together when the other design concern changes source of truth, consistency, schema evolution, event flow, replay, derived data, partitions, or ownership boundaries.

## Prefer One When

- Prefer DDIA when consistency, schemas, replay, ordering, source of truth, or distributed data failure is the hard part; prefer the other book when those data semantics are not in scope.

## Source Basis

- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 3-5: applies when DDD implementation choices affect contexts, language, aggregates, repositories, events, application services, package structure, or cross-context integration.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 7-9: corrects renamed CRUD by requiring operational domain modeling inside an explicit context with local language, small invariant boundaries, identity references, and translation.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 13-31: requires context-first interpretation, consistent local language, Core Domain protection, explicit context interactions and translations, small invariant-driven Aggregates with identity references, Entities/Value Objects/Domain Services/Repositories/Domain Events/Event Sourcing/Application Services by rule, Bounded Context modules, DTO/projection/query separation, CQRS where justified, model-walk code generation, and direct domain/boundary tests.
- `implementing-domain-driven-design/implementing-domain-driven-design.mini.md` lines 48-57: checks explicit context, consistent local terms, protected Core Domain, visible translations, small invariant-driven Aggregates, behavior-bearing Entities/Value Objects, aggregate-root repositories, meaningful events/event sourcing only when right, coordinating application services, and external representations outside the domain.

## Review Notes

- External context was not used as decisive evidence for Designing Data-Intensive Applications vs Implementing Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
