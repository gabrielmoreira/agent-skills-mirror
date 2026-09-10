# Designing Data-Intensive Applications vs Refactoring

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Designing Data-Intensive Applications should drive tasks where source of truth, consistency, durability, replay, schemas, replication, partitioning, or distributed failure dominate.
- Evidence: `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.

## Book B Pressure

- Refactoring should drive tasks where behavior-preserving structural change and current-smell scope control dominate.
- Evidence: `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.

## Complementary Forces

- Claim: Designing Data-Intensive Applications contributes source-of-truth, consistency, replay, schema-evolution, partitioning, and distributed-failure pressure; Refactoring contributes behavior-preserving, small-step, test-backed refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
  - `refactoring/refactoring.mini.md` lines 30-39: fires on structural friction before features, unclear bug code, absent tests, third duplication, mixed responsibilities, shotgun surgery, repeated conditionals, UI/domain mixing, patch intent mixing, and rewrite temptation.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
  - `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
  - `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.

## Use Together When

- Use together when existing code must be reshaped toward Designing Data-Intensive Applications goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 3-5: applies where correctness depends on data ownership, consistency, durability, replication, partitioning, schema evolution, event flow, replay, or derived data.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 7-9: corrects local-happy-path thinking about writes, reads, queues, caches, replicas, clocks, and downstream side effects.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 13-30: requires explicit source of truth, failure semantics, workload facts, data ownership, storage/index choices, derived-data lag and repair, write visibility, idempotent retry/replay, ordering scope, evolving schemas, replication/partitioning/transactions, fault models, coordination costs, recoverable batch/stream processing, and service boundaries by data ownership.
- `designing-data-intensive-applications/designing-data-intensive-applications.mini.md` lines 46-55: checks source of truth, consistency/durability/staleness/conflicts, retry/replay/reordering, safe evolution, workload-matched storage, invariant-protecting isolation, rebuildable streams/projections, ownership-aligned services, observability, and no exactly-once wishful thinking.
- `refactoring/refactoring.mini.md` lines 3-5: applies when changing existing code, preparing a feature/bug fix, reviewing cleanup, or reducing structural friction without changing observable behavior.
- `refactoring/refactoring.mini.md` lines 7-9: corrects cleanup turning into rewrite, hidden feature change, or speculative architecture.
- `refactoring/refactoring.mini.md` lines 30-39: fires on structural friction before features, unclear bug code, absent tests, third duplication, mixed responsibilities, shotgun surgery, repeated conditionals, UI/domain mixing, patch intent mixing, and rewrite temptation.
- `refactoring/refactoring.mini.md` lines 43-49: checks behavior preservation, separated structural/behavior/test updates, safety net, real friction removed, clearer ownership/control/data/interfaces, reviewable runnable patch, and stopped cleanup.

## Review Notes

- External context was not used as decisive evidence for Designing Data-Intensive Applications vs Refactoring; the verdict is based on the cited local `mini` line ranges.
