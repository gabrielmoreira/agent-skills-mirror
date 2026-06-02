# Semantic Risk Taxonomy

Use these seven categories during planning. Mark only the categories that truly apply.

## data_volume

- Trigger heuristics: large datasets, batch jobs, pagination, broad reads or writes
- Planning action: separate data-shape discovery from implementation; define limits and validation data

## performance

- Trigger heuristics: hot paths, query fan-out, N+1 risks, expensive loops, cache changes
- Planning action: call out expected bottlenecks and how you will verify them

## concurrency

- Trigger heuristics: parallel workers, shared mutable state, background jobs, race windows
- Planning action: make ownership and ordering explicit; avoid hand-wavy "should be safe"

## access_control

- Trigger heuristics: auth, permissions, visibility, tenancy, role changes
- Planning action: name the affected actors and what access should or should not change

## migration_rollback

- Trigger heuristics: schema changes, data transforms, file-format changes, irreversible rewrites
- Planning action: add rollback or recovery notes and approval gating

## dependency

- Trigger heuristics: external APIs, new packages, version upgrades, CLI contract changes
- Planning action: confirm the contract source and capture compatibility assumptions

## operability

- Trigger heuristics: deployment, monitoring, CI, background services, observability
- Planning action: include operational validation, not just unit-level correctness
