# data-layer — Module AI Instructions (Example)

**Scope**: Authoritative for everything inside `.hi/examples/data-layer/`
**Last Updated**: 2026-05-25

> Example module. See [`.hi/examples/README.md`](../../README.md) for context.

---

## Contents

| Section | What's here |
|---|-------------|
| [Module Overview](#module-overview) | Purpose and exposed surface |
| [Directory Structure](#directory-structure) | How entities, repositories, and migrations are organized |
| [Module-Specific Rules](#module-specific-rules) | Entity, repository, transaction rules |
| [Migration Rules](#migration-rules) | Sequencing, irreversibility, never-reset |
| [Global Rules Reference](#global-rules-reference) | Cross-references |

---

## Module Overview

`data-layer` owns the database schema and is the **only** module allowed to define TypeORM entities and migrations. Every other module imports entities and the `Repository<T>` base from this package and never declares its own.

- **Entry point**: `src/index.ts` (re-exports the public surface)
- **Public exports**: entity classes, `BaseRepository<T>`, `withTransaction()`, the `DataSource` factory
- **Internal-only**: migration files, seed scripts, raw SQL helpers
- **External dependencies**: PostgreSQL 16+

---

## Directory Structure

```
data-layer/
├── .hi/instruct.md
├── .dev-docs/index.md
├── src/
│   ├── index.ts                 ← curated re-exports only
│   ├── entities/                ← one class per table; PascalCase filenames
│   ├── repositories/            ← BaseRepository<T> + per-entity repositories
│   ├── migrations/              ← timestamped: 1700000000000-add-users.ts
│   ├── seeds/                   ← idempotent dev/test data
│   └── lib/
│       ├── data-source.ts       ← the ONE DataSource for the whole app
│       └── transaction.ts       ← withTransaction() helper
└── test/
```

---

## Module-Specific Rules

### Entities

1. **One entity per file**, filename matches class name in `PascalCase.ts` (the *only* place in the repo where `.ts` files are PascalCase — see [File Naming](../../../conventions.md#file-naming)).
2. Every entity has `id: string` (UUID v7), `createdAt`, `updatedAt`. The `BaseEntity` mixin provides these — use it.
3. **No business logic on entities.** No methods other than getters that derive from existing columns. Business logic lives in the consumer module's service layer.
4. Foreign-key columns are explicit (`userId: string`) **and** carry the relation decorator. Never rely on lazy relations in production code.

### Repositories

1. **One repository per entity**, extending `BaseRepository<T>`.
2. Repositories return entities or `null`. They **never** throw `HTTP*` errors. Domain errors live in the consumer module.
3. **No `find()` with raw user input.** Use named methods (`findByEmail`, `findActiveById`); arbitrary `where` from outside the module is rejected at code review.
4. All queries that return lists are paginated. The base method `paginate({ limit, cursor })` is the only allowed list path.

### Transactions

1. Any operation that writes to **more than one table** must run inside `withTransaction()`.
2. `withTransaction()` is the only place that touches `DataSource.transaction` directly — never call the ORM transaction API from elsewhere.

---

## Migration Rules

1. **Filenames** are `<unix-ms>-<kebab-case-description>.ts`. Use `pnpm migration:generate` to scaffold; never rename a generated file.
2. **Migrations are append-only**: once committed to `main`, never edit. A bug in a shipped migration is fixed by a *new* migration.
3. Every migration provides a meaningful `down()`. If a change is truly irreversible (data loss), `down()` throws with a message that says so explicitly — never silently skip.
4. **Never reset the database** to "fix" a migration conflict. See [Never Reset Databases](../../../maintenance.md#never-reset-databases) — this is a hard rule and the AI must refuse.
5. Schema changes touching production tables (`users`, `sessions`, `payments`) require an `ALTER` strategy review in the PR description.

---

## Global Rules Reference

> **→ [No-Duplication Rule](../../../conventions.md#no-duplication-rule)** — instructions live in one place.
> **→ [Never Delete Rule](../../../maintenance.md#never-delete-rule)** — archive migrations/entities instead of deleting.
> **→ [Never Reset Databases](../../../maintenance.md#never-reset-databases)** — confirmation required.
> **→ [.env File Convention](../../../credentials.md#env-file-convention)** — `DATABASE_URL` lives in the consumer module's env, not this module.
