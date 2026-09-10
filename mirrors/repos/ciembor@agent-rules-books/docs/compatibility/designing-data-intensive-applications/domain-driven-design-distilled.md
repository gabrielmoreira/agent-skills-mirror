# Designing Data-Intensive Applications vs Domain-Driven Design Distilled

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 35%
Complementarity: 80%

## Loading Decision

Use together when the task changes state, events, schemas, queues, projections, caches, consistency, or ownership while also needing Domain-Driven Design Distilled pressure.

## Book A Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Book B Pressure

- Domain-Driven Design Distilled should drive tasks where selective DDD, subdomain importance, Bounded Contexts, local language, and justified tactical patterns dominate.
- Evidence: `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.

## Complementary Forces

- Claim: Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure; Domain-Driven Design Distilled contributes selective-DDD, subdomain, Bounded-Context, local-language, and justified-pattern pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Conflicts

- Claim: The tension is over-modeling: the non-data rule set may improve structure, but DDIA requires explicit data semantics before abstractions hide source-of-truth or failure behavior.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
  - `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 34-44: fires on fuzzy language, core drift, one model spreading across separate concerns, upstream/technical shape defining the domain, Shared Kernel/ACL/event/aggregate misuse, business decisions in services/controllers, primitive domain concepts, and delivery pressure skipping design.

## Use Together When

- Use together when the other design concern changes source of truth, consistency, schema evolution, event flow, replay, derived data, partitions, or ownership boundaries.

## Prefer One When

- Prefer DDIA when consistency, schemas, replay, ordering, source of truth, or distributed data failure is the hard part; prefer the other book when those data semantics are not in scope.

## Source Basis

- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 3-5: applies when business software has domain complexity, language ambiguity, strategic differentiation, or integration risk but needs smallest effective DDD rather than ceremony.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 7-9: corrects starting from tactical patterns, frameworks, persistence, APIs, or class shapes before business capability, subdomain, context, and language.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 13-30: requires capability/subdomain/context/language first, Core Domain investment, selective DDD, explicit Bounded Context ownership, term translation, deliberate context relationships, integration style by coupling/failure semantics, separate integration contracts, local domain terms, justified Entities/Value Objects/Aggregates/Domain Events/Application Services, infrastructure-free domain model, code that teaches the model, timeboxed modeling aids, and planning from modeling uncertainty.
- `domain-driven-design-distilled/domain-driven-design-distilled.mini.md` lines 48-56: checks subdomain investment, explicit context relationship, visible Ubiquitous Language, tested translations, justified tactical patterns, small Aggregates, coordinating application services, infrastructure-free domain model, and captured modeling discoveries.

## Review Notes

- External context was not used as decisive evidence for Designing Data-Intensive Applications vs Domain-Driven Design Distilled; the verdict is based on the cited local `mini` line ranges.
