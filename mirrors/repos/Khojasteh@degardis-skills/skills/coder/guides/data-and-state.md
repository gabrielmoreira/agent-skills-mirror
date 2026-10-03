---
title: Data and state
applicability:
- When correctness depends on data or state that persists beyond the operation that wrote it
---

Identify every reader and writer of the state, the versions and malformed or partially written records already present, the transaction or consistency boundary, and the authority that may mutate real data. Establish the transaction's actual boundary from code, including writes through another connection, service, queue, cache, or background task and what a retry repeats. Name the concrete paths that can race rather than reporting a theoretical conflict. A code change and applying a migration are separate actions.

Define forward and backward readability, defaults for missing values, validation, partial-failure state, atomicity, uniqueness, ordering, concurrent updates, idempotency, retry safety, and rollback before changing representation. Account for rows predating a new invariant and state already damaged by a defect. Preserve unknown fields or values where the contract requires round trips. Do not add a constraint, required field, or narrowed type until representative existing data is shown to satisfy it; schema acceptance alone is not proof. Never use production data as a casual test fixture or expose it in diagnostics.

Separate schema change, data rewrite, and code deployment; state their order and what must keep working between stages. Define mapping, backfill, validation, reconciliation, retention, cleanup, and any dual-read or dual-write behavior before data moves; dual reads and writes are coexistence under [[guide:temporary-coexistence]]. Make a migration rerunnable and reversible, or state why it is not and what recovery requires. Never assume an application rollback reverses persisted data.

Exercise the transformation on an isolated representative copy that includes old, boundary, malformed, and partial states rather than only data created by the new work. Verify old-to-new behavior, mixed-version reads and writes, retries, interruption, cleanup, rollback or forward repair, and the application behavior that consumes the result. Compare meaning through keys, invariants, aggregates, and representative records; counts or a successful import do not prove equivalence. Destructive or irreversible application requires explicit bounded authority, safe ordering, a bound on affected records, validation, backup or recovery, and a current observation before authority changes.
