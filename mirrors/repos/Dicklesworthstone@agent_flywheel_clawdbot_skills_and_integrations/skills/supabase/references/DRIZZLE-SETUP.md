# Drizzle Setup

Complete guide for Drizzle ORM with Supabase pooler.

---

## Installation

```bash
bun add drizzle-orm postgres
bun add -d drizzle-kit
```

---

## Connection Strings

Copy from Supabase Dashboard → Connect button. **Do not guess hostnames.**

```bash
# Transaction mode (port 6543) - for app runtime
DATABASE_URL="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"

# Session mode (port 5432) - for migrations
DATABASE_URL_MIGRATIONS="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require"
```

**Username format:** `postgres.<project_ref>` — the dot is real.

---

## Database Client

```typescript
// src/db/index.ts
import postgres from "postgres"
import { drizzle } from "drizzle-orm/postgres-js"
import * as schema from "./schema"

// Prevent multiple instances in dev (hot reload)
const g = globalThis as unknown as { __sql?: ReturnType<typeof postgres> }

export const sql = g.__sql ?? postgres(process.env.DATABASE_URL!, {
  prepare: false,  // REQUIRED for transaction pooler
  max: process.env.NODE_ENV === "production" ? 5 : 1,
})

if (process.env.NODE_ENV !== "production") g.__sql = sql

export const db = drizzle(sql, { schema })
```

### Why These Settings?

| Setting | Value | Reason |
|---------|-------|--------|
| `prepare: false` | Required | Transaction pooler doesn't support prepared statements |
| `max: 5` (prod) | Recommended | Supavisor is the real pool; keep client-side small |
| `max: 1` (dev) | Recommended | Prevent connection leaks during hot reload |
| `globalThis` caching | Required | Next.js dev hot reload creates new instances |

---

## Drizzle Config

```typescript
// drizzle.config.ts
import "dotenv/config"
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./supabase/migrations",
  dbCredentials: {
    url: process.env.DATABASE_URL_MIGRATIONS!,  // Session mode for migrations
  },
})
```

**Why session mode for migrations?** Session mode (port 5432) supports prepared statements and long-running operations needed for migrations.

---

## Schema Definition

```typescript
// src/db/schema.ts
import { pgTable, uuid, text, timestamp } from "drizzle-orm/pg-core"

export const userProfiles = pgTable("user_profiles", {
  id: uuid("id").primaryKey(),
  email: text("email"),
  displayName: text("display_name"),
  avatarUrl: text("avatar_url"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
})

export const organizations = pgTable("organizations", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  ownerId: uuid("owner_id"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
})

export const orgMemberships = pgTable("org_memberships", {
  orgId: uuid("org_id").notNull(),
  userId: uuid("user_id").notNull(),
  role: text("role").notNull().default("member"),
})
```

---

## Migration Commands

```bash
# Generate migration from schema changes
drizzle-kit generate

# Apply migrations to database
drizzle-kit migrate

# Open visual studio
drizzle-kit studio

# Pull remote schema to local
drizzle-kit pull
```

---

## Usage Patterns

### Basic Query

```typescript
import { db } from "@/db"
import { userProfiles } from "@/db/schema"
import { eq } from "drizzle-orm"

const user = await db.query.userProfiles.findFirst({
  where: eq(userProfiles.id, userId),
})
```

### Insert

```typescript
await db.insert(userProfiles).values({
  id: userId,
  email: "user@example.com",
  displayName: "User Name",
})
```

### Update

```typescript
await db.update(userProfiles)
  .set({ displayName: "New Name", updatedAt: new Date() })
  .where(eq(userProfiles.id, userId))
```

### Transaction

```typescript
await db.transaction(async (tx) => {
  await tx.insert(organizations).values({ name: "Acme Corp" })
  await tx.insert(orgMemberships).values({ orgId, userId, role: "owner" })
})
```

---

## Common Errors

### "prepared statement does not exist"

**Cause:** Using transaction pooler without `prepare: false`

**Fix:**
```typescript
const sql = postgres(process.env.DATABASE_URL!, {
  prepare: false,  // Add this
})
```

### Connection timeout / ENETUNREACH

**Cause:** Using direct connection (IPv6) in IPv4-only environment

**Fix:** Use pooler connection string from Dashboard → Connect

### "relation does not exist"

**Cause:** Migration not applied or wrong database

**Fix:**
```bash
drizzle-kit migrate
# Or check you're connected to the right project
```

### Too many connections

**Cause:** Pool size too high or connection leaks

**Fix:**
- Reduce `max` to 5 or less
- Add `globalThis` caching for dev
- Check for unclosed connections in error paths

---

## Type Generation

Drizzle generates types from your schema automatically:

```typescript
import { InferSelectModel, InferInsertModel } from "drizzle-orm"
import { userProfiles } from "@/db/schema"

type UserProfile = InferSelectModel<typeof userProfiles>
type NewUserProfile = InferInsertModel<typeof userProfiles>
```

---

## Integration with Supabase Types

If you also use the Supabase client, you can generate types for both:

```bash
# Supabase types (for Data API)
supabase gen types typescript --project-id $PROJECT_REF > src/types/supabase.ts

# Drizzle types come from your schema.ts
```

Use Drizzle types for server-side queries, Supabase types for client-side Data API calls.
