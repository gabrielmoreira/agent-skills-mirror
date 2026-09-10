# Clean Architecture vs Designing Data-Intensive Applications

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 10%
Overlap: 35%
Complementarity: 80%

## Loading Decision

Use together when the task changes state, events, schemas, queues, projections, caches, consistency, or ownership while also needing Clean Architecture pressure.

## Book A Pressure

- Clean Architecture should drive tasks where business policy must stay independent from frameworks, databases, delivery, vendors, and volatile mechanisms.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.

## Book B Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Complementary Forces

- Claim: Clean Architecture contributes policy-independence and replaceable-detail pressure; Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.

## Conflicts

- Claim: The tension is over-modeling: the non-data rule set may improve structure, but DDIA requires explicit data semantics before abstractions hide source-of-truth or failure behavior.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 34-42: fires on write paths, derived data, schema/API/event changes, retries/jobs/queues/replay, replica reads, partitioning, isolation choices, clock/lock/consensus assumptions, and data-intensive review risks.

## Use Together When

- Use together when the other design concern changes source of truth, consistency, schema evolution, event flow, replay, derived data, partitions, or ownership boundaries.

## Prefer One When

- Prefer DDIA when consistency, schemas, replay, ordering, source of truth, or distributed data failure is the hard part; prefer the other book when those data semantics are not in scope.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.
- `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
- `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
- `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.

## Review Notes

- External context was not used as decisive evidence for Clean Architecture vs Designing Data-Intensive Applications; the verdict is based on the cited local `mini` line ranges.
