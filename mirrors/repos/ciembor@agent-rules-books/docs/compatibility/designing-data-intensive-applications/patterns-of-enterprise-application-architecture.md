# Designing Data-Intensive Applications vs Patterns of Enterprise Application Architecture

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 35%
Complementarity: 80%

## Loading Decision

Use together when the task changes state, events, schemas, queues, projections, caches, consistency, or ownership while also needing Patterns of Enterprise Application Architecture pressure.

## Book A Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Book B Pressure

- Patterns of Enterprise Application Architecture should drive tasks where enterprise pattern forces across workflow, persistence, transactions, integration, session state, or remoting dominate.
- Evidence: `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.

## Complementary Forces

- Claim: Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure; Patterns of Enterprise Application Architecture contributes enterprise-pattern pressure across presentation, workflow, domain logic, persistence, transactions, integration, state, and remoting. Together they are useful only where both scopes are active.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 34-43: fires on domain behavior in presentation/SQL/glue, collapsed responsibilities, Transaction Script complexity, table-shaped rich domains, scattered persistence/transactions/external access, lazy-load/N+1/identity issues, concurrency/stale locks, chatty remote APIs, unclear session state, and pass-through/generic repository/ORM/controller workflow blockers.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Conflicts

- Claim: The tension is over-modeling: the non-data rule set may improve structure, but DDIA requires explicit data semantics before abstractions hide source-of-truth or failure behavior.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
  - `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 34-43: fires on domain behavior in presentation/SQL/glue, collapsed responsibilities, Transaction Script complexity, table-shaped rich domains, scattered persistence/transactions/external access, lazy-load/N+1/identity issues, concurrency/stale locks, chatty remote APIs, unclear session state, and pass-through/generic repository/ORM/controller workflow blockers.

## Use Together When

- Use together when the other design concern changes source of truth, consistency, schema evolution, event flow, replay, derived data, partitions, or ownership boundaries.

## Prefer One When

- Prefer DDIA when consistency, schemas, replay, ordering, source of truth, or distributed data failure is the hard part; prefer the other book when those data semantics are not in scope.

## Source Basis

- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 3-5: applies to enterprise code crossing presentation, workflow, domain, persistence, transactions, concurrency, integration, session state, or remote boundaries.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 7-9: corrects inventing architecture for every feature and letting frameworks, ORMs, schemas, or transports choose the design.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 34-43: fires on domain behavior in presentation/SQL/glue, collapsed responsibilities, Transaction Script complexity, table-shaped rich domains, scattered persistence/transactions/external access, lazy-load/N+1/identity issues, concurrency/stale locks, chatty remote APIs, unclear session state, and pass-through/generic repository/ORM/controller workflow blockers.
- `patterns-of-enterprise-application-architecture/patterns-of-enterprise-application-architecture.mini.md` lines 47-54: checks intentional separation of enterprise responsibilities, business logic pattern fit, persistence pattern fit, explicit transactions/concurrency/loading, remote/integration boundaries, session-state ownership, and responsibility-aligned tests.

## Review Notes

- External context was not used as decisive evidence for Designing Data-Intensive Applications vs Patterns of Enterprise Application Architecture; the verdict is based on the cited local `mini` line ranges.
