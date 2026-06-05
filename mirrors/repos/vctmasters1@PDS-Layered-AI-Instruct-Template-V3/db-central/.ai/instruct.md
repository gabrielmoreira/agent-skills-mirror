# db-central — AI-INSTRUCT

**Scope**: DEEP — Authoritative for all work inside `db-central/`
**Last Updated**: 2026-06-03

> **Consumer pattern**: db-central is NOT an npm package. It is a shared source directory consumed via tsconfig path alias `@db-central/*` pointing to `../../db-central/src/*` in each service. Do **not** add `@pds/db-central` to any consumer's `package.json` — that will break. Path must be **lowercase `db-central`** (all three consumers were fixed from `DB-Central` during consolidation). See [How Consuming Services Use db-central](#how-consuming-services-use-db-central).
>
> **Shared PostgreSQL**: WEB-HMI, WEB-Marketplace, and WEB-FwServer all connect to the same Railway PostgreSQL instance. All entities live here. `synchronize: false` — migrations only.

---

## Contents

| § | What's here |
|---|-------------|
| [What db-central Is](#what-db-central-is) | Purpose and non-purpose |
| [What db-central Is Not](#what-db-central-is-not) | Hard boundaries |
| [Directory Structure](#directory-structure) | Canonical layout |
| [Entity Ownership Model](#entity-ownership-model) | Who owns what, which services consume what |
| [User Entity & Service Permissions](#user-entity--service-permissions) | The single authoritative User + access flags |
| [How Consuming Services Use db-central](#how-consuming-services-use-db-central) | tsconfig path alias, import pattern |
| [Migration Strategy](#migration-strategy) | synchronize: false, one runner, run order |
| [Database Isolation & Safety](#database-isolation--safety) | Same code different DBs, critical safety rules, dev vs prod data hygiene |
| [Seeding & Fixture Data](#seeding--fixture-data) | Idempotent data population, mode-aware seeds, test data vs production data |
| [Startup Flow](#startup-flow) | What happens when services start (migration → seed → ready) |
| [Idempotency Patterns](#idempotency-patterns) | How to write safe migrations and seeds |
| [WEB-Resume Integration](#web-resume-integration) | Current status, Phase 2 plan |
| [Docker Compose Ownership](#docker-compose-ownership) | Dev PostgreSQL lives here |
| [Service Integration Status](#service-integration-status) | Per-service migration state |
| [Rules for Adding Entities or Columns](#rules-for-adding-entities-or-columns) | Change discipline |

---

## What db-central Is

db-central is the **single authoritative TypeScript source** for all TypeORM entities, migrations, and shared DB types used by every backend service in this monorepo.

It is a **shared source directory** — not a service, not a package, not a running process. It has no `main()`, no HTTP server, no runtime process of its own. It is `.ts` files that TypeScript compiles **inline** as part of each consuming service's build. Nothing here is ever deployed independently.

**Why it exists:** The monorepo has a single Railway PostgreSQL instance shared by WEB-Marketplace, WEB-HMI, WEB-FwServer, and (Phase 2) WEB-Resume. Without a single entity source, schema drift and sync collisions are inevitable — and have already occurred.

---

## What db-central Is Not

| It is NOT | Why it matters |
|-----------|----------------|
| An npm package | No publish step, no version tags, no npm registry |
| A workspace (npm/yarn/pnpm) | No `workspaces` config in root `package.json` |
| A service | Never has a process running; never has a Railway deployment |
| A place for business logic | Route handlers, middleware, validation — all stay in their service |
| A place for service-specific config | `DataSource` config, `.env` parsing — stays in each service |
| The owner of a service's DataSource | Each service creates its own TypeORM `DataSource` pointing at db-central entities |

---

## Directory Structure

```
db-central/
├── AI-INSTRUCT.md              ← This file
├── docker-compose.yml          ← Dev PostgreSQL (pds_marketplace on :5432)
├── tsconfig.json               ← Strict TypeScript config — used as reference by services
│
└── src/
    ├── index.ts                ← Barrel: re-exports all entities and enums
    │
    ├── entities/
    │   ├── index.ts
    │   │
    │   │── user.ts             ← PLATFORM-LEVEL — single authoritative User
    │   │
    │   │   ── Marketplace entities ──
    │   ├── designer.ts
    │   ├── producer.ts
    │   ├── product.ts
    │   ├── service.ts
    │   ├── order.ts
    │   ├── order-item.ts
    │   ├── bid.ts
    │   ├── bulletin-card.ts
    │   ├── dispute.ts
    │   ├── favorite.ts
    │   ├── invoice.ts
    │   ├── message.ts
    │   ├── message-fee.ts
    │   ├── messaging-fee-waiver.ts
    │   ├── notification.ts
    │   ├── notification-preference.ts
    │   ├── payment-milestone.ts
    │   ├── payout.ts
    │   ├── portfolio-image.ts
    │   ├── report.ts
    │   ├── review.ts
    │   ├── site-settings.ts
    │   ├── waitlist-entry.ts
    │   ├── audit-log.ts
    │   ├── email-verification-token.ts
    │   ├── password-reset-token.ts
    │   ├── search.ts
    │   │
    │   │   ── HMI / Device entities ──
    │   ├── device.ts
    │   ├── device-config.ts
    │   ├── telemetry-log.ts
    │   │
    │   │   ── FwServer entities ──
    │   └── firmware.ts
    │
    └── migrations/
        ├── index.ts            ← Ordered migration list (import order = run order)
        └── [timestamp]-[description].ts
```

---

## Entity Ownership Model

"Ownership" means: **this service is the authority on what columns exist and is responsible for writing migrations for that entity.** Non-owning services may read any entity — they simply import it from db-central.

| Entity | Logical Owner | Also Read By |
|--------|--------------|--------------|
| `User` | db-central (platform) | All services |
| `Designer`, `Producer` | WEB-Marketplace | — |
| `Product`, `Service`, `Order`, `OrderItem` | WEB-Marketplace | — |
| `Bid`, `BulletinCard`, `Dispute`, `Favorite` | WEB-Marketplace | — |
| `Invoice`, `Message`, `Notification` | WEB-Marketplace | — |
| `PaymentMilestone`, `Payout` | WEB-Marketplace | — |
| `SiteSettings`, `AuditLog` | WEB-Marketplace | — |
| `EmailVerificationToken`, `PasswordResetToken` | WEB-Marketplace | — |
| `WaitlistEntry`, `Report`, `Review`, `Search` | WEB-Marketplace | — |
| `Device`, `DeviceConfig`, `TelemetryLog` | WEB-HMI | — |
| `Firmware` | WEB-FwServer | WEB-HMI (read-only) |

**Platform-level entities** (owned by db-central itself, not by any one service) are entities that cross all service boundaries and have no single service home. Currently only `User`. These are the responsibility of whoever works on the platform at a cross-service level.

---

## User Entity & Service Permissions

`User` is the one entity every service touches. It has a dual role:

1. **Identity** — auth credentials, contact info, role, soft-delete audit trail
2. **Service access control** — boolean flags that gate which products/features a user can access

### Current permission flags on User

The existing `activeDesigner / activeProducer / activeMaterials / activeAuthor / activeGizmo` flags are the established pattern — they control marketplace tab visibility. Service access flags extend that pattern:

```typescript
// ── Service access flags ──────────────────────────────────────────────────
// These mirror WEB-Resume's `resume_access` column (which predates db-central).
// Admin sets these flags. Each service's auth middleware checks its own flag.

@Column({ default: false })
resumeAccess: boolean;       // Can access WEB-Resume AI tools

// Future examples (add when the feature exists):
// @Column({ default: false }) hmiAccess: boolean;
```

### Rules

- **Never** gate access via `role` alone for service-level products (role defines marketplace role; flags define product subscriptions)
- **Admin sets flags** — the `/api/admin/users` endpoint in each service should expose these flags
- **Adding a new flag** requires: (1) adding the column to `user.ts` here, (2) writing a migration, (3) adding a setter to the admin route of the relevant service
- `isStaff` / `staffRole` continue to control internal PDS employee access across all services

---

## How Consuming Services Use db-central

### Step 1 — tsconfig path alias

In each consuming service's `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@db-central/*": ["../../db-central/src/*"]
    }
  }
}
```

Adjust the relative path depth to match the service's location in the repo.

### Step 2 — Import entities

```typescript
import { User, UserRole }   from '@db-central/entities/user.js';
import { Device }           from '@db-central/entities/device.js';
import { Firmware }         from '@db-central/entities/firmware.js';
```

### Step 3 — DataSource stays in the service

Each service creates its **own** TypeORM `DataSource`. It points to the db-central entities, but the connection config (host, credentials, pool settings) lives in the service:

```typescript
// WEB-HMI/api/src/database.ts
import { User }         from '@db-central/entities/user.js';
import { Device }       from '@db-central/entities/device.js';
import { DeviceConfig } from '@db-central/entities/device-config.js';
import { TelemetryLog } from '@db-central/entities/telemetry-log.js';
import { Firmware }     from '@db-central/entities/firmware.js';

export const AppDataSource = new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  synchronize: false,                    // NEVER true once db-central is live
  entities: [User, Device, DeviceConfig, TelemetryLog, Firmware],
  migrations: [],                        // Services do not run migrations themselves
});
```

**Key rule:** A service only registers the entities it actually uses in its `DataSource`. It does not register all db-central entities — only its subset.

### Step 4 — Do not run migrations from the service

All migrations are run by the **db-central migration runner** (see below). Services set `migrations: []` and `migrationsRun: false`.

---

## Migration Strategy

### The Problem with `synchronize: true`

TypeORM `synchronize: true` runs `ALTER TABLE` statements on startup based on the current entity definitions. When two services start up against the same schema with different entity definitions (or ordering), destructive conflicts occur. **This is what caused the null email collision.**

### The Rule

> `synchronize: false` in every service, always, once db-central is live.

### How Migrations Work

1. **Schema changes start here** — add/change a column in `db-central/src/entities/`
2. **Write a migration** — create a timestamped file in `db-central/src/migrations/`
3. **Run migrations once** — use the db-central migration runner script (not any service's startup)
4. **Services inherit the schema** — they start up, find the schema already matches their entities, and proceed

### Migration runner

```
db-central/
└── run-migrations.ts    ← Standalone script: npx ts-node run-migrations.ts
```

This script creates a temporary `DataSource` with **all** entities and runs pending migrations. It is the only thing that mutates the schema.

### Migration file naming

`{timestamp}-{description}.ts` — e.g. `20260521001-add-resume-access-to-user.ts`

Use TypeORM's `QueryRunner` API. Never use raw `synchronize`. Never drop columns without a matching migration to preserve or backfill data.

---

---

## Database Isolation & Safety

### The Core Rule: Same Code, Different Databases

All deployment modes use **identical migration and entity code**, but point to **different PostgreSQL instances**. This is the firewall against data contamination.

| Deployment Mode | Database Instance | Connection String | Data Lifecycle |
|-----------------|-------------------|-------------------|-----------------|
| **dev-local** | Local Docker (fresh) | `postgresql://resumesuite:devpassword@localhost:5433/resumesuite` | Ephemeral — safe to `docker compose down -v` |
| **dev-lan** | Local Docker (persistent) | `postgresql://resumesuite:devpassword@localhost:5432/resumesuite_dev` | Persistent — survives restart |
| **prod-self-serve** | Local Docker (persistent) | `postgresql://resumesuite:prodpassword@localhost:5432/resumesuite_prod` | Persistent staging data — do not contaminate |
| **prod-railway** | Railway-managed PostgreSQL | `postgresql://<user>:<pwd>@<railway-host>:5432/railway` | **LIVE CUSTOMER DATA** — never delete, never reset |

### Critical Safety Rules

**🚨 NEVER run destructive operations without explicit confirmation:**
- Never `DROP TABLE` without a migration
- Never `DROP DATABASE` without explicit intent
- Never `TRUNCATE` any table
- Never `DELETE FROM` without a `WHERE` clause
- Never run `synchronize: true` (use migrations instead)

**Database credentials isolation:**
- Dev credentials go in `.env` (local file, never committed)
- Prod credentials live in Railway env vars (never in source code)
- Always verify `DATABASE_URL` before running migrations: `echo $DATABASE_URL`

**Before any migration run:**
```bash
# Confirm target database
echo "Current DATABASE_URL:"
echo $DATABASE_URL
# If it contains production server name → STOP and investigate
# If it contains "localhost" → safe to proceed
```

---

## Seeding & Fixture Data

### What Seeds Are

Seeds are **idempotent data-population scripts** separate from migrations. They run **after** migrations complete and are **mode-aware** — different seeds run in different deployment modes.

```
db-central/src/
├── migrations/              ← Schema (CREATE TABLE, ALTER TABLE)
│   └── [timestamp]*.ts
│
└── seeds/                   ← Data (INSERT, UPDATE)
    ├── index.ts             ← Seed runner & orchestrator
    ├── dev-only/            ← Only runs in dev-local / dev-lan
    │   ├── test-users.ts    ← Test user accounts (admin@dev, user@dev)
    │   ├── test-devices.ts  ← Mock device fixtures
    │   └── test-products.ts ← Sample marketplace products
    ├── staging-only/        ← Only runs in prod-self-serve
    │   ├── demo-users.ts    ← Demo creator profiles
    │   ├── demo-devices.ts  ← Demo device data
    │   └── demo-products.ts ← Demo product listings
    └── production/          ← Only runs in prod-railway (rarely)
        └── admin-user.ts    ← Bootstrap admin account (manual trigger)
```

### Idempotent Seed Pattern

Every seed **checks before inserting**. If data exists, skip.

```typescript
// Good: safe to run multiple times
export async function seedTestUsers(ds: DataSource) {
  const userRepo = ds.getRepository(User);
  
  const exists = await userRepo.findOne({
    where: { email: 'admin@dev' },
  });
  
  if (!exists) {
    await userRepo.insert({
      email: 'admin@dev',
      password: hashPassword('dev-password'),
      isStaff: true,
    });
    console.log('✓ Created admin@dev');
  } else {
    console.log('✓ admin@dev already exists, skipped');
  }
}

// Bad: will error on second run
export async function seedTestUsers_BAD(ds: DataSource) {
  await ds.getRepository(User).insert({
    email: 'admin@dev',
    password: hashPassword('dev-password'),
  });
  // ↑ ERROR on second run: unique constraint violation
}
```

### Seed Orchestrator

```typescript
// db-central/src/seeds/index.ts
export async function runSeeds(
  dataSource: DataSource,
  deployMode: string
) {
  const logger = console;
  
  logger.log(`\n[Seeds] Running seeds for mode: ${deployMode}`);
  
  // Always run platform seeds (safe for all modes)
  try {
    await seedAdminUser(dataSource);
  } catch (err) {
    logger.error('Platform seed failed:', err);
    throw err;
  }
  
  // Mode-specific seeds
  if (deployMode === 'dev-local' || deployMode === 'dev-lan') {
    try {
      await seedTestUsers(dataSource);
      await seedTestDevices(dataSource);
      await seedTestProducts(dataSource);
      logger.log('[Seeds] ✓ Dev seeds applied');
    } catch (err) {
      logger.error('Dev seed failed:', err);
      throw err;
    }
  }
  
  if (deployMode === 'prod-self-serve') {
    try {
      await seedDemoUsers(dataSource);
      await seedDemoDevices(dataSource);
      logger.log('[Seeds] ✓ Staging seeds applied');
    } catch (err) {
      logger.error('Staging seed failed:', err);
      throw err;
    }
  }
  
  if (deployMode === 'prod-railway') {
    logger.log('[Seeds] Skipped (production auto-seed disabled)');
  }
}
```

---

## Startup Flow

### What Happens When a Service Starts

```
1. Service reads .env file
   ↓ DATABASE_URL = postgresql://user:pwd@host:5432/database

2. Service creates TypeORM DataSource
   ├─ Connects to PostgreSQL
   ├─ Verifies connection
   └─ Loads entities from db-central

3. Migration runner executes
   ├─ Reads pending migrations from db-central/src/migrations/
   ├─ Runs only migrations not yet in the `migrations` table
   └─ Each migration: CREATE TABLE IF NOT EXISTS, ALTER TABLE ... IF NOT EXISTS
   └─ Result: schema matches db-central entities (no-op if already matches)

4. Seed runner executes (if enabled for this mode)
   ├─ Checks if test data exists
   ├─ Inserts only missing records
   ├─ Result: idempotent — safe to run repeatedly
   └─ SKIPPED in prod-railway

5. Service is ready
   └─ API listens on port, database is locked and ready
```

**Key safety property**: Every service that starts against the same database will see an identical schema, because all migrations are cumulative and idempotent.

### On Fresh Start (Clean Volume)

```
docker compose down -v                  # Remove volumes (= fresh empty DB)
docker compose up -d                    # Start with blank PostgreSQL

Then for each service:
├─ Migrations run: CREATE TABLE IF NOT EXISTS (first time: creates)
└─ Seeds run: INSERT IF NOT EXISTS (first time: populates)

Result: all services see identical schema + same test data
```

### On Restart (Persistent Volume)

```
docker compose up -d                    # Restart container, volume persists

Then for each service:
├─ Migrations run: CREATE TABLE IF NOT EXISTS (no-op: table exists)
└─ Seeds run: INSERT IF NOT EXISTS (no-op: data exists)

Result: all data intact, no loss
```

### On Prod Deploy (Railway)

```
git push                                # Trigger Railway deploy
Railway:
├─ Starts PostgreSQL (existing data intact)
├─ Runs migrations: CREATE TABLE IF NOT EXISTS (no-op if schema exists)
├─ Runs app with synchronize: false
└─ Services restore their DB connection pooling

Result: zero data loss, zero destructive operations
```

---

## Idempotency Patterns

### Migrations: IF NOT EXISTS

Every migration must be **fully replayable** on the same database without errors.

**Pattern — CREATE TABLE:**
```typescript
export class Migration_20260601_CreateDevices {
  async up(queryRunner) {
    await queryRunner.createTable(
      new Table({
        name: 'devices',
        columns: [
          { name: 'id', type: 'uuid', isPrimary: true },
          { name: 'created_at', type: 'timestamp', default: 'now()' },
        ],
      }),
      true  // ← ifNotExists: true
    );
  }
}
```

**Pattern — ALTER TABLE ADD COLUMN:**
```typescript
export class Migration_20260602_AddDeviceLocation {
  async up(queryRunner) {
    const table = await queryRunner.getTable('devices');
    
    // Check if column already exists
    if (!table?.findColumnByName('location')) {
      await queryRunner.addColumn(
        'devices',
        new TableColumn({
          name: 'location',
          type: 'varchar',
          isNullable: true,
        })
      );
    }
  }
}
```

**Pattern — Backfill with safety:**
```typescript
export class Migration_20260603_PopulateDefaultLocation {
  async up(queryRunner) {
    // Only update rows that have NULL location
    await queryRunner.query(`
      UPDATE devices 
      SET location = 'unknown' 
      WHERE location IS NULL
    `);
  }
}
```

### Seeds: Check Before Insert

Every seed must be **replayable** without unique constraint violations.

```typescript
// Pattern: Check existence by unique constraint
async function seedUser(ds: DataSource, email: string, password: string) {
  const repo = ds.getRepository(User);
  
  const existing = await repo.findOne({
    where: { email },
  });
  
  if (existing) {
    console.log(`User ${email} exists, skipped`);
    return existing;
  }
  
  const newUser = repo.create({
    email,
    password: hashPassword(password),
  });
  
  return await repo.save(newUser);
}
```

---

## WEB-Resume Integration

WEB-Resume (`ResumeServer/`) is currently **out-of-band** — it uses:
- Raw SQL (pg Pool), not TypeORM
- A separate PostgreSQL database
- SERIAL integer PK on `users` (not UUID)
- Its own `resume_access` boolean column

### Phase 1 (current): Loose coupling

The `resumeAccess` flag on db-central's `User` entity allows Marketplace admin to grant/revoke Resume access without touching the Resume service. Resume itself continues to use its own DB and its own auth.

This means WEB-Resume does **not** yet use db-central. It is documented here so the gap is explicit.

### Phase 2 (future): Full integration

1. Migrate Resume's PostgreSQL to the shared `pds` database
2. Migrate `users.id` from `SERIAL` to `UUID` (requires data migration + foreign key updates on `listings`, `workflow_jobs`, `artifacts`)
3. Replace Resume's `users` table with a read-view of db-central's `User`, adding Resume-specific columns (`listings`, `workflow_jobs`, `artifacts`) as child tables keyed on UUID
4. Replace Resume's raw SQL auth with JWT token validation against db-central's shared JWT secret

**Do not begin Phase 2 until Marketplace and HMI are fully migrated to db-central.**

---

## Docker Compose Ownership

The dev PostgreSQL container is defined in `db-central/docker-compose.yml` and is the single source of truth for local database infrastructure.

**Container name**: `db-central` (renamed from `pds-marketplace-db` on 2026-05-28)
**Volume**: `db-central_db-central-pgdata` (Docker-managed, fresh — not migrated from old `api_pgdata`)
**Database**: `pds_marketplace` — credentials: `pds / pds_dev_password`

```powershell
# Start (from db-central/ or anywhere):
docker compose -f k:/PDS-Master-001/db-central/docker-compose.yml up -d

# Stop:
docker compose -f k:/PDS-Master-001/db-central/docker-compose.yml down

# Destroy and start fresh (loses all data):
docker compose -f k:/PDS-Master-001/db-central/docker-compose.yml down -v
docker compose -f k:/PDS-Master-001/db-central/docker-compose.yml up -d
```

**Schema population**: The database starts empty. Schema is built by running each service's migrations in order:
1. `cd web-marketplace/api && npm run db:migrate` — creates all marketplace tables (15 migrations)
2. `cd web-hmi/api` — HMI runs its own migrations at startup (2 migrations for device tables)

Do **not** use `synchronize: true` to rebuild schema — that bypasses migration history and will diverge from production. Always use migrations.

**Legacy**: The old `pds-marketplace-db` container and `api_pgdata` volume came from `web-marketplace/api/docker-compose.yml`. That file is now a stub warning. The old `api_pgdata` Docker volume can be removed once you confirm the new schema is correct: `docker volume rm api_pgdata`.

---

## Service Integration Status

| Service | db-central entities? | synchronize | Notes |
|---------|---------------------|-------------|-------|
| WEB-Marketplace/api | ✅ Complete | `false` | `User`, `Designer`, `Producer`, `Product`, `Service` are re-export shims (`export … from "@db-central/entities/…"`); remaining 23 entities are local copies keyed to the same schema |
| WEB-HMI/api | ✅ Complete | `false` | All 5 entity files are re-export shims (`export … from "@db-central/entities/…"`); `synchronize: false` |
| WEB-FwServer/api | ⬜ Not yet | unknown | Has local stub `User` + local `Firmware` definition |
| WEB-Resume/ResumeServer | ⬜ Phase 2 | N/A (raw SQL) | Separate DB, loose coupling only |

Migration order: Marketplace → FwServer → Resume (Phase 2). HMI is done.

### WEB-HMI/api — legacy migration files

Two migration files remain in `WEB-HMI/api/src/migrations/` as historical records — they have already been applied and are tracked in the `migrations` table. They will not re-run. Future device-schema changes must go through db-central migrations.

---

## Rules for Adding Entities or Columns

1. **New entity** → create the `.ts` file in `db-central/src/entities/`, add it to `src/entities/index.ts` and `src/index.ts`, write a migration, update this table in [Entity Ownership Model](#entity-ownership-model)

2. **New column on an existing entity** → edit the entity file here first, then write the migration. Do not edit the entity in any consuming service.

3. **Column removal** → write a migration with a data-preservation plan (backfill or archive) before dropping. Document the reason in the migration file.

4. **Never** edit entities in a consuming service's `src/entities/` directory once that service is migrated to db-central. Those local entity files become dead code and should be deleted.

5. **Breaking changes** (enum rename, PK type change) require a multi-step migration with a backfill pass. Coordinate with all consuming services before executing.

6. **AI-INSTRUCT.md maintenance**: Any entity addition, column addition, or permission flag addition requires updating the relevant section(s) of this file in the same operation.
