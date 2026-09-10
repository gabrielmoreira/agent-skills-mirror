# Designing Data-Intensive Applications vs Domain-Driven Design

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 35%
Complementarity: 80%

## Loading Decision

Use together when the task changes state, events, schemas, queues, projections, caches, consistency, or ownership while also needing Domain-Driven Design pressure.

## Book A Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Book B Pressure

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Complementary Forces

- Claim: Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure; Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Conflicts

- Claim: The tension is over-modeling: the non-data rule set may improve structure, but DDIA requires explicit data semantics before abstractions hide source-of-truth or failure behavior.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
  - `domain-driven-design/domain-driven-design.mini.md` lines 31-39: fires on awkward terminology, business decisions in technical surfaces, technical models shaping domain concepts, cross-module changes, lifecycle/persistence leaks, hard-to-explain behavior, cross-model integration, invariant changes, and generic mechanisms obscuring core value.

## Use Together When

- Use together when the other design concern changes source of truth, consistency, schema evolution, event flow, replay, derived data, partitions, or ownership boundaries.

## Prefer One When

- Prefer DDIA when consistency, schemas, replay, ordering, source of truth, or distributed data failure is the hard part; prefer the other book when those data semantics are not in scope.

## Source Basis

- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.

## Review Notes

- External context was not used as decisive evidence for Designing Data-Intensive Applications vs Domain-Driven Design; the verdict is based on the cited local `mini` line ranges.
