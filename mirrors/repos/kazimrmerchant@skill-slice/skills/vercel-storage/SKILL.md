---
name: vercel-storage
description: "Selects and configures Vercel storage: Blob, Edge Config, and Marketplace Neon/Upstash/Supabase/Prisma/Mongo/Convex/Turso, including sunset @vercel/postgres and @vercel/kv migrations. Use when choosing or debugging data stores on Vercel. Not for Neon branch types (neon-postgres-branches), Supabase Auth wiring (nextjs-supabase-auth), or Vercel env var CLI (env-vars)."
version: 1.0.1
metadata:
  priority: 7
  docs:
    - "https://vercel.com/docs/storage"
    - "https://vercel.com/docs/vercel-blob"
    - "https://vercel.com/docs/edge-config"
    - "https://vercel.com/marketplace"
    - "https://vercel.com/docs/integrations"
    - "https://github.com/vercel/storage"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'lib/blob/**'
    - 'lib/storage/**'
    - 'src/lib/blob/**'
    - 'src/lib/storage/**'
    - 'lib/blob.*'
    - 'lib/storage.*'
    - 'lib/edge-config.*'
    - 'src/lib/blob.*'
    - 'src/lib/storage.*'
    - 'src/lib/edge-config.*'
    - 'supabase/**'
    - 'lib/supabase.*'
    - 'src/lib/supabase.*'
    - 'prisma/schema.prisma'
    - 'prisma/**'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/blob\b'
    - '\byarn\s+add\s+[^\n]*@vercel/blob\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/edge-config\b'
    - '\byarn\s+add\s+[^\n]*@vercel/edge-config\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@neondatabase/serverless\b'
    - '\byarn\s+add\s+[^\n]*@neondatabase/serverless\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@upstash/redis\b'
    - '\byarn\s+add\s+[^\n]*@upstash/redis\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/kv\b'
    - '\byarn\s+add\s+[^\n]*@vercel/kv\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/postgres\b'
    - '\byarn\s+add\s+[^\n]*@vercel/postgres\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@supabase/supabase-js\b'
    - '\byarn\s+add\s+[^\n]*@supabase/supabase-js\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@supabase/ssr\b'
    - '\byarn\s+add\s+[^\n]*@supabase/ssr\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@prisma/client\b'
    - '\byarn\s+add\s+[^\n]*@prisma/client\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bmongodb\b'
    - '\byarn\s+add\s+[^\n]*\bmongodb\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bconvex\b'
    - '\byarn\s+add\s+[^\n]*\bconvex\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@libsql/client\b'
    - '\byarn\s+add\s+[^\n]*@libsql/client\b'
  importPatterns:
    - "@vercel/blob"
    - "@vercel/edge-config"
    - "@neondatabase/serverless"
    - "@upstash/redis"
    - "@vercel/kv"
    - "@vercel/postgres"
    - "@supabase/supabase-js"
    - "@prisma/client"
---

# Vercel Storage

You are an expert in Vercel's storage options. Know which products are active, which are sunset, and when to use each.

## When to Use

Trigger this skill when the user is:

- Choosing a storage provider for a Vercel/Next.js application
- Installing or configuring `@vercel/blob`, `@vercel/edge-config`, `@neondatabase/serverless`, `@upstash/redis`, `@supabase/supabase-js`, `@prisma/client`, `mongodb`, `convex`, or `@libsql/client`
- Migrating away from the **sunset** `@vercel/postgres` or `@vercel/kv` packages
- Debugging Vercel Marketplace integration env var provisioning
- Working in `lib/blob/**`, `lib/storage/**`, `prisma/**`, `supabase/**`, or similar storage code paths
- Setting up Drizzle, Prisma, or Neon with lazy initialization to survive `next build`

## Prerequisites

- A Vercel project linked locally (`vercel link`) so `vercel env pull` works
- Vercel CLI installed (`npm i -g vercel`) for Marketplace provisioning
- Node.js 19+ when using `@neondatabase/serverless`
- Windows host is primary — use PowerShell. On Windows, `source` is unavailable; use `dotenv-cli` or PowerShell `$env:` variable injection for scripts that need `.env.local`

## Procedure

### 1. Choose the Storage Provider

Use the decision matrix to pick the right product before writing any code.

| Need | Use | Package |
|------|-----|---------|
| File uploads, media, documents | Vercel Blob | `@vercel/blob` |
| Feature flags, A/B config, edge routing rules | Edge Config | `@vercel/edge-config` |
| Relational data, SQL queries | Neon Postgres | `@neondatabase/serverless` |
| Key-value cache, sessions, rate limiting | Upstash Redis | `@upstash/redis` |
| Postgres + auth + realtime + storage | Supabase | `@supabase/supabase-js` |
| Type-safe ORM with migrations | Prisma | `@prisma/client` |
| Document database, flexible schemas | MongoDB Atlas | `mongodb` |
| Reactive backend with real-time sync | Convex | `convex` |
| Edge-native SQLite with replicas | Turso | `@libsql/client` |
| Full-text search | Neon Postgres (`pg_trgm`) or Elasticsearch (Marketplace) | varies |
| Vector embeddings | Neon Postgres (`pgvector`) or Pinecone (Marketplace) | varies |

### 2. Provision via Marketplace (Preferred Path)

**Preferred**: Vercel-managed Neon/Upstash/Supabase/etc. through the Vercel Marketplace. This auto-provisions accounts/resources and injects environment variables into the linked Vercel project.

```powershell
# Install a storage integration (auto-provisions env vars)
vercel integration add neon
vercel integration add upstash
vercel integration add supabase
vercel integration add prisma
vercel integration add mongodb-atlas
vercel integration add turso

# List installed integrations
vercel integration list
```

Browse additional options at `https://vercel.com/marketplace` or the dashboard at `https://vercel.com/dashboard/{team}/stores`.

After Marketplace provisioning, pull env vars locally:

```powershell
vercel env pull .env.local --yes
```

### 3. Fallback: Manual / Provider CLI Provisioning

Use the fallback path **only** when Marketplace is unavailable or you must use an existing external account.

1. Create the resource via the provider's CLI or dashboard (e.g., Neon CLI, Upstash CLI, Supabase dashboard).
2. Copy the connection string / URL / token into Vercel project env vars (dashboard or `vercel env add`).
3. Pull locally: `vercel env pull .env.local --yes`

**Neon CLI fallback note**: For **Vercel-managed Neon projects**, CLI operations require a **Neon API key**; do not rely on the normal browser-auth login flow alone.

### 4. Install the Client Package

```powershell
# Blob
npm install @vercel/blob

# Edge Config
npm install @vercel/edge-config

# Neon Postgres (requires Node.js 19+)
npm install @neondatabase/serverless

# Upstash Redis
npm install @upstash/redis

# Supabase
npm install @supabase/supabase-js @supabase/ssr

# Prisma
npm install prisma @prisma/client
npx prisma init

# MongoDB Atlas
npm install mongodb

# Convex
npm install convex
npx convex dev

# Turso
npm install @libsql/client
```

### 5. Write Storage Code

#### Vercel Blob — File Storage

```ts
import { put, del, list, get } from '@vercel/blob'

// Upload from server (public)
const blob = await put('images/photo.jpg', file, {
  access: 'public',
})
// blob.url → public URL

// Upload private file
const privateBlob = await put('docs/secret.pdf', file, {
  access: 'private',
})
// Read private file back
const privateFile = await get(privateBlob.url) // returns ReadableStream + metadata

// Client upload (up to 5 TB)
import { upload } from '@vercel/blob/client'
const blob = await upload('video.mp4', file, {
  access: 'public',
  handleUploadUrl: '/api/upload', // Your token endpoint
})

// List blobs
const { blobs } = await list()

// Conditional get with ETags
const response = await get('images/photo.jpg', {
  ifNoneMatch: previousETag,
})
if (response.statusCode === 304) {
  // Not modified, use cached version
}

// Delete
await del('images/photo.jpg')
```

**Private Storage** (public beta): Use `access: 'private'` for files that should not be publicly accessible. Read them back with `get()`. Do NOT use private access for files that need to be served publicly — it leads to slow delivery and high egress costs.

**Blob Data Transfer**: Vercel Blob uses two delivery strategies — **Fast Data Transfer** (94 cities, latency-optimized) and **Blob Data Transfer** (18 hubs, volume-optimized for large assets). The system automatically routes via the optimal path.

**Use when**: Media files, user uploads, documents, any large unstructured data.

#### Vercel Edge Config — Global Configuration

Ultra-low-latency key-value store for application configuration. Not a database — designed for config data that must be read instantly at the edge.

```ts
import { get, getAll, has } from '@vercel/edge-config'

// Read a single value (< 1ms at the edge)
const isFeatureEnabled = await get('feature-new-ui')

// Read multiple values
const config = await getAll(['feature-new-ui', 'ab-test-variant', 'redirect-rules'])

// Check existence
const exists = await has('maintenance-mode')
```

**Use when**: Feature flags, A/B testing config, dynamic routing rules, maintenance mode toggles. Anything that must be read at the edge with near-zero latency.

**Do NOT use for**: User data, session state, frequently written data. Edge Config is optimized for reads, not writes.

**Next.js 16**: `@vercel/edge-config@^1.4.3` supports `cacheComponents` and the renamed `proxy.ts` (formerly `middleware.ts`).

#### Neon Postgres (replaces @vercel/postgres)

Serverless Postgres with branching, auto-scaling, and connection pooling. The driver is GA at `@neondatabase/serverless@^1.0.2` and requires **Node.js 19+**.

```ts
// Direct Neon usage
import { neon } from '@neondatabase/serverless'

const sql = neon(process.env.DATABASE_URL!)
const users = await sql`SELECT * FROM users WHERE id = ${userId}`

// With Drizzle ORM
import { drizzle } from 'drizzle-orm/neon-http'
import { neon } from '@neondatabase/serverless'

const sql = neon(process.env.DATABASE_URL!)
const db = drizzle(sql)
```

**Build-time safety — CRITICAL**: The `neon()` call above throws if `DATABASE_URL` is not set. Since Next.js evaluates top-level module code at build time, this will crash `next build` when env vars aren't yet configured (e.g., first deploy before Marketplace provisioning). Use lazy initialization:

```ts
// src/db/index.ts — lazy initialization (safe for build time)
import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import * as schema from './schema'

function createDb() {
  const sql = neon(process.env.DATABASE_URL!)
  return drizzle(sql, { schema })
}

let _db: ReturnType<typeof createDb> | null = null

export function getDb() {
  if (!_db) _db = createDb()
  return _db
}
```

**HARD RULE — Do NOT use JavaScript `Proxy` wrappers around the DB client.** A common pattern is wrapping `db` in a `Proxy` for lazy initialization. This breaks libraries like NextAuth/Auth.js that inspect the DB adapter object (e.g., checking method existence, iterating properties). The Proxy intercepts those checks and breaks the auth request chain, causing hangs with no error. Use a plain `getDb()` function or a simple module-level lazy `let` instead.

**Drizzle Kit migrations**: `drizzle-kit` and `tsx` do NOT auto-load `.env.local`. Source env vars manually or use `dotenv`:

```bash
# Option 1: Source env vars before running (Linux/macOS only)
source <(grep -v '^#' .env.local | sed 's/^/export /') && npx drizzle-kit push

# Option 2: Use dotenv-cli (recommended, cross-platform)
npm install -D dotenv-cli
npx dotenv -e .env.local -- npx drizzle-kit push
npx dotenv -e .env.local -- npx tsx seed.ts
```

```powershell
# Windows PowerShell equivalent (Option 2 — dotenv-cli, recommended)
npm install -D dotenv-cli
npx dotenv -e .env.local -- npx drizzle-kit push
npx dotenv -e .env.local -- npx tsx seed.ts
```

This applies to **any** Node script that needs Vercel-provisioned env vars — only Next.js auto-loads `.env.local`.

#### Upstash Redis (replaces @vercel/kv)

```ts
import { Redis } from '@upstash/redis'

const redis = Redis.fromEnv() // Uses UPSTASH_REDIS_REST_URL & TOKEN

// Basic operations
await redis.set('session:abc', { userId: '123' }, { ex: 3600 })
const session = await redis.get('session:abc')

// Rate limiting
import { Ratelimit } from '@upstash/ratelimit'
const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '10s'),
})
const { success } = await ratelimit.limit('user:123')
```

#### Supabase (Marketplace Native)

```ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

const { data, error } = await supabase.from('users').select('*')
```

Install via Vercel Marketplace: `vercel integration add supabase`

#### Prisma ORM (Marketplace Native)

```ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()
const users = await prisma.user.findMany()
```

Install via Vercel Marketplace: `vercel integration add prisma`

#### MongoDB Atlas

```ts
import { MongoClient } from 'mongodb'

const client = new MongoClient(process.env.MONGODB_URI!)
const db = client.db('myapp')
const users = await db.collection('users').find({}).toArray()
```

Install via Vercel Marketplace: `vercel integration add mongodb-atlas`

#### Convex

```ts
import { query } from './_generated/server'
import { v } from 'convex/values'

export const getUsers = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query('users').collect()
  },
})
```

#### Turso (libSQL)

```ts
import { createClient } from '@libsql/client'

const turso = createClient({
  url: process.env.TURSO_DATABASE_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
})

const result = await turso.execute('SELECT * FROM users')
```

Install via Vercel Marketplace: `vercel integration add turso`

### 6. Migrate from Sunset Packages

**`@vercel/postgres` and `@vercel/kv` are SUNSET.** These packages no longer exist as first-party Vercel products. Use the marketplace replacements.

#### From @vercel/postgres → Neon

```diff
- import { sql } from '@vercel/postgres'
+ import { neon } from '@neondatabase/serverless'
+ const sql = neon(process.env.DATABASE_URL!)
```

**Drop-in replacement**: For minimal migration effort, use `@neondatabase/vercel-postgres-compat` which provides API-compatible wrappers for `@vercel/postgres` imports.

#### From @vercel/kv → Upstash Redis

```diff
- import { kv } from '@vercel/kv'
- await kv.set('key', 'value')
- const value = await kv.get('key')
+ import { Redis } from '@upstash/redis'
+ const redis = Redis.fromEnv()
+ await redis.set('key', 'value')
+ const value = await redis.get('key')
```

## Pitfalls

1. **`next build` crashes with missing `DATABASE_URL`**: The `neon()` call throws at module-eval time. Always use lazy initialization (`getDb()` pattern) — never call `neon()` at top-level scope.
2. **Proxy wrappers break NextAuth/Auth.js**: Wrapping the DB client in a JS `Proxy` for lazy init causes auth libraries to hang silently. Use a plain function or `let` variable instead. This is a HARD RULE.
3. **`drizzle-kit` / `tsx` don't read `.env.local`**: Only Next.js auto-loads `.env.local`. Use `dotenv-cli` (`npx dotenv -e .env.local -- ...`) for all standalone Node scripts. On Windows, `source` is not available — use `dotenv-cli` exclusively.
4. **Using Blob private access for public files**: Leads to slow delivery and high egress costs. Only use `access: 'private'` for files that should not be publicly accessible.
5. **Edge Config used as a database**: Edge Config is optimized for reads, not writes. Do NOT use it for user data, session state, or frequently written data.
6. **Vercel-managed Neon CLI auth**: CLI operations on Vercel-managed Neon projects require a Neon API key — the browser-auth login flow alone is insufficient.
7. **Forgetting `vercel env pull` after Marketplace provisioning**: After adding an integration, always run `vercel env pull .env.local --yes` locally so the new env vars are available for local dev.
8. **Node.js version mismatch**: `@neondatabase/serverless` requires Node.js 19+. Check `node -v` before installing.
9. **Next.js 16 proxy.ts rename**: `@vercel/edge-config@^1.4.3` supports the renamed `proxy.ts` (formerly `middleware.ts`) and `cacheComponents`. Ensure you are on `^1.4.3` or later.

## Verification

1. **Confirm integration is installed**:
   ```powershell
   vercel integration list
   ```
   Expected: the storage integration (e.g., `neon`, `upstash`) appears in the list.

2. **Confirm env vars were provisioned and pulled**:
   ```powershell
   vercel env pull .env.local --yes
   ```
   Then inspect `.env.local` for the expected keys (e.g., `DATABASE_URL`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `BLOB_READ_WRITE_TOKEN`, `EDGE_CONFIG`). Use `YOUR_KEY` placeholders when sharing examples — never commit real secrets.

3. **Verify Blob upload works**:
   ```ts
   import { put } from '@vercel/blob'
   const blob = await put('test.txt', 'hello', { access: 'public' })
   console.log(blob.url) // should print a vercel-storage.com URL
   ```

4. **Verify Edge Config read**:
   ```ts
   import { get } from '@vercel/edge-config'
   const val = await get('test-key')
   console.log(val)
   ```

5. **Verify Neon query** (with lazy init):
   ```ts
   import { getDb } from '@/db'
   const db = getDb()
   const result = await db.execute('SELECT 1 AS ok')
   console.log(result) // [{ ok: 1 }]
   ```

6. **Verify Upstash Redis**:
   ```ts
   import { Redis } from '@upstash/redis'
   const redis = Redis.fromEnv()
   await redis.set('ping', 'pong')
   console.log(await redis.get('ping')) // 'pong'
   ```

7. **Verify `next build` succeeds without env vars** (lazy init check):
   ```powershell
   # Temporarily unset DATABASE_URL and build — should NOT crash
   $env:DATABASE_URL = $null
   npx next build
   ```
   If the build crashes with a `neon()` error, the lazy initialization pattern is not correctly applied.

## Related skills

- **vercel-deploy** — Vercel project linking, env var management, deployment workflow
- **nextjs** — Next.js App Router, `proxy.ts`/`middleware.ts`, `cacheComponents`
- **drizzle-orm** — Drizzle schema, migrations, `drizzle-kit push`
