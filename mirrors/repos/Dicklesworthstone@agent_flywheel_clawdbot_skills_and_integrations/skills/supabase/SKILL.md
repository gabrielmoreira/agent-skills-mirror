---
name: supabase
description: >-
  Configure Supabase for Next.js SaaS: Drizzle + pooler, Google-only Auth, RLS,
  cost optimization. Use when setting up Supabase, connecting Drizzle, SSR auth,
  or optimizing costs.
---

# Supabase for Next.js SaaS

> **Core Insight:** Two lanes: user-scoped data via Supabase client (RLS-enforced), server-scoped via Drizzle (privileged). Use `getClaims()` not `getSession()`. Transaction pooler requires `prepare: false`.

## Table of Contents

- [THE EXACT PROMPT](#the-exact-prompt)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Workflow Checklist](#workflow-checklist)
- [Critical Gotchas](#critical-gotchas)
- [Quick Commands](#quick-commands)
- [AGENTS.md Blurb](#agentsmd-blurb)
- [References](#references)

---

## THE EXACT PROMPT

```
Set up Supabase for a Next.js SaaS with:
1. Auth: Google OAuth only
2. ORM: Drizzle with Supabase pooler (IPv4)
3. Environment: [Vercel / Cloudflare / local dev]
4. Cost tier: [Free / Pro with Spend Cap / Team]

Follow supabase-guide skill patterns.
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TWO-LANE DATA ACCESS MODEL                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   LANE A: User-scoped (RLS-enforced)                                │
│   ══════════════════════════════════                                │
│   @supabase/ssr → PostgREST Data API                                │
│   • Browser + Server Components                                     │
│   • JWT validated via getClaims()                                   │
│   • Multi-tenant reads/writes obey RLS "naturally"                  │
│                                                                     │
│   LANE B: Server-scoped (privileged)                                │
│   ══════════════════════════════════                                │
│   Drizzle → postgres.js → Supavisor pooler                          │
│   • Migrations, admin tasks, billing webhooks                       │
│   • Transaction mode (port 6543): prepare: false                    │
│   • Session mode (port 5432): migrations only                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Why this split:** Browser access uses Data API with RLS. Server/serverless uses pooler. IPv4-only environments (Vercel/GH Actions) cannot use direct connections (IPv6).

---

## Quick Start

### 1. Drizzle + Pooler (Transaction Mode)

```typescript
// src/db/index.ts
import postgres from "postgres"
import { drizzle } from "drizzle-orm/postgres-js"
import * as schema from "./schema"

const g = globalThis as unknown as { __sql?: ReturnType<typeof postgres> }

export const sql = g.__sql ?? postgres(process.env.DATABASE_URL!, {
  prepare: false,  // REQUIRED for transaction pooler
  max: process.env.NODE_ENV === "production" ? 5 : 1,
})

if (process.env.NODE_ENV !== "production") g.__sql = sql

export const db = drizzle(sql, { schema })
```

### 2. Supabase SSR Clients

```typescript
// src/lib/supabase/client.ts
import { createBrowserClient } from "@supabase/ssr"

export function supabaseBrowser() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  )
}
```

```typescript
// src/lib/supabase/server.ts
import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"

export function supabaseServer() {
  const store = cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll: () => store.getAll(),
        setAll: (toSet) => {
          try { toSet.forEach(({ name, value, options }) => store.set(name, value, options)) }
          catch {}
        },
      },
    }
  )
}
```

### 3. Middleware (Token Refresh)

```typescript
// middleware.ts
import { createServerClient } from "@supabase/ssr"
import { NextResponse, type NextRequest } from "next/server"

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request: { headers: request.headers } })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (toSet) => {
          toSet.forEach(({ name, value }) => request.cookies.set(name, value))
          response = NextResponse.next({ request: { headers: request.headers } })
          toSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
        },
      },
    }
  )

  await supabase.auth.getClaims()  // NOT getSession()
  return response
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
}
```

---

## Environment Variables

```bash
# Supabase Auth / API
NEXT_PUBLIC_SUPABASE_URL="https://<project_ref>.supabase.co"
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY="sb_publishable_..."  # or anon key during transition
SUPABASE_SERVICE_ROLE_KEY="..."  # server-only, NEVER ship to client

# Postgres: app runtime (transaction pooler, port 6543)
DATABASE_URL="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"

# Postgres: migrations (session pooler, port 5432)
DATABASE_URL_MIGRATIONS="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require"
```

**Username format:** `postgres.<project_ref>` — the dot is real, copy from Dashboard → Connect button.

---

## Workflow Checklist

### Phase 1: Project Setup
- [ ] Create prod + staging Supabase projects (blast-radius isolation)
- [ ] Copy connection strings from Connect button (not guessed)
- [ ] Set env vars: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `DATABASE_URL`, `DATABASE_URL_MIGRATIONS`
- [ ] Enable Spend Cap (Pro plan) — [COST-OPTIMIZATION.md](references/COST-OPTIMIZATION.md)

### Phase 2: Auth (Google-only)
- [ ] Enable Google provider in Dashboard → Auth → Providers
- [ ] Disable email/password, magic links, phone
- [ ] Add redirect URI in Google Cloud Console: `https://<project_ref>.supabase.co/auth/v1/callback`
- [ ] Set up SSR clients + middleware — [AUTH-SSR.md](references/AUTH-SSR.md)
- [ ] Create OAuth callback route — [GOOGLE-OAUTH.md](references/GOOGLE-OAUTH.md)

### Phase 3: Database + Drizzle
- [ ] Install: `bun add drizzle-orm postgres && bun add -d drizzle-kit`
- [ ] Create `src/db/index.ts` with `prepare: false` — [DRIZZLE-SETUP.md](references/DRIZZLE-SETUP.md)
- [ ] Create `drizzle.config.ts` pointing to session pooler for migrations
- [ ] Run `drizzle-kit generate` and `drizzle-kit migrate`

### Phase 4: RLS + Data Model
- [ ] Create `user_profiles` table keyed by `auth.users.id`
- [ ] Enable RLS on ALL tables in `public` schema
- [ ] Create trigger to auto-create profile on signup
- [ ] Index columns used in RLS policies — [RLS-PATTERNS.md](references/RLS-PATTERNS.md)

### Phase 5: Cost Optimization
- [ ] Use transaction pooler for runtime, session for migrations
- [ ] Harden Data API: move sensitive tables to `private` schema
- [ ] Set up cron rollups for event-heavy tables
- [ ] Configure Smart CDN + cache-control for Storage — [COST-OPTIMIZATION.md](references/COST-OPTIMIZATION.md)

---

## Critical Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ENETUNREACH` / `network unreachable` | Direct connection is IPv6 | Use pooler connection string |
| `prepared statement does not exist` | Transaction pooler + prepared statements | Set `prepare: false` in postgres.js |
| `Tenant or user not found` | Wrong pooler host or username format | Copy exact string from Connect dialog; include `.project_ref` in username |
| Users randomly logged out | Token not refreshing in middleware | Use `getClaims()` in middleware, not `getSession()` |
| RLS policy not blocking | Table missing `enable row level security` | Run `ALTER TABLE x ENABLE ROW LEVEL SECURITY` |
| Slow queries with RLS | No index on RLS filter columns | Add index on `user_id`, `tenant_id` columns |
| Surprise bills | No Spend Cap, uncached egress | Enable Spend Cap; use Smart CDN + high cache-control |

Full troubleshooting: [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)

---

## Security Rules

1. **Use `getClaims()`, not `getSession()`** — cookies can be spoofed; `getClaims()` validates JWT signature every time
2. **Never expose `service_role` key** — bypasses RLS, backend-only
3. **Enable RLS on every table in `public`** — tables without RLS are accessible via anon role
4. **Use `app_metadata` not `user_metadata` for tenant_id** — user_metadata is user-modifiable

---

## Quick Commands

```bash
# Supabase CLI
supabase login
supabase link --project-ref $PROJECT_REF
supabase db pull                        # Pull remote schema
supabase migration new <name>           # Create migration
supabase db push                        # Apply migrations

# Drizzle
drizzle-kit generate                    # Generate migrations
drizzle-kit migrate                     # Apply migrations
drizzle-kit studio                      # Visual browser

# Secrets (Edge Functions)
supabase secrets set --env-file .env    # Push secrets
supabase secrets list                   # Verify
```

---

## AGENTS.md Blurb

Copy this to your project's AGENTS.md:

```markdown
### Supabase

Supabase CLI is installed. Project: `<PROJECT_REF>`.

Auth:

\`\`\`bash
supabase login
supabase link --project-ref $PROJECT_REF
\`\`\`

Database:

\`\`\`bash
supabase db pull           # Pull schema to migrations
supabase migration new <name>
supabase db push           # Apply migrations
\`\`\`

Connection strings:
- **Runtime (Drizzle):** Transaction pooler (port 6543), `prepare: false`
- **Migrations:** Session pooler (port 5432)

Copy exact connection string from Dashboard → Connect button.
```

---

## References

| Topic | Reference |
|-------|-----------|
| Copy-paste patterns | [QUICK-REFERENCE.md](references/QUICK-REFERENCE.md) |
| Two-lane architecture + cost model | [ARCHITECTURE.md](references/ARCHITECTURE.md) |
| Drizzle + pooler setup | [DRIZZLE-SETUP.md](references/DRIZZLE-SETUP.md) |
| Next.js SSR auth with getClaims() | [AUTH-SSR.md](references/AUTH-SSR.md) |
| Google OAuth setup | [GOOGLE-OAUTH.md](references/GOOGLE-OAUTH.md) |
| RLS patterns for SaaS | [RLS-PATTERNS.md](references/RLS-PATTERNS.md) |
| Pooler gotchas (IPv4/IPv6, modes) | [POOLER-GOTCHAS.md](references/POOLER-GOTCHAS.md) |
| Cost optimization (Spend Cap, cron) | [COST-OPTIMIZATION.md](references/COST-OPTIMIZATION.md) |
| Troubleshooting guide | [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) |

---

## Validation

```bash
# After setup, verify:
# 1. Google OAuth flow works (login → callback → dashboard)
# 2. Drizzle can connect: bun run -e "import { db } from './src/db'; console.log('OK')"
# 3. RLS blocks unauthorized access via Data API
# 4. Middleware refreshes tokens (check cookies in DevTools)
```
