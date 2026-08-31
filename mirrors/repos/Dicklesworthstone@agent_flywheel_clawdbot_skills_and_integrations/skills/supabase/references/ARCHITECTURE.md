# Architecture

The two-lane data access model for Supabase + Next.js SaaS.

---

## Two-Lane Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TWO-LANE DATA ACCESS MODEL                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   LANE A: User-scoped (RLS-enforced)                                │
│   ══════════════════════════════════                                │
│   @supabase/ssr → PostgREST Data API                                │
│                                                                     │
│   When to use:                                                      │
│   • Multi-tenant reads/writes that should obey RLS                  │
│   • Browser queries (supabase.from(...))                            │
│   • Server Components needing user-scoped data                      │
│                                                                     │
│   How it works:                                                     │
│   1. JWT validated via getClaims() (signature + expiry)             │
│   2. JWT claims (auth.uid()) available in RLS policies              │
│   3. RLS enforced automatically by PostgREST                        │
│                                                                     │
│   LANE B: Server-scoped (privileged)                                │
│   ══════════════════════════════════                                │
│   Drizzle → postgres.js → Supavisor pooler                          │
│                                                                     │
│   When to use:                                                      │
│   • Migrations                                                      │
│   • Admin dashboards (aggregations, cross-tenant)                   │
│   • Billing webhooks (Stripe/PayPal)                                │
│   • Cron jobs (rollups, cleanup)                                    │
│   • Background workers                                              │
│                                                                     │
│   Security model:                                                   │
│   • Uses postgres user (or app-specific role)                       │
│   • RLS bypassed OR enforced via application-level checks           │
│   • NEVER expose connection string to client                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Why This Split?

| Concern | Lane A (Supabase Client) | Lane B (Drizzle) |
|---------|--------------------------|------------------|
| RLS enforcement | Automatic via JWT | Manual or bypassed |
| Connection model | HTTP (PostgREST) | Postgres TCP (pooled) |
| Serverless-friendly | Yes (stateless) | Yes (with transaction pooler) |
| Prepared statements | N/A | Must disable (`prepare: false`) |
| Best for | User-facing CRUD | Admin/background tasks |

---

## Connection Topology

```
Browser
   │
   └──► Supabase Data API (PostgREST)
         • HTTPS, stateless
         • JWT in header
         • RLS policies evaluated

Next.js Server Components / Route Handlers
   │
   ├──► Supabase Server Client (@supabase/ssr)
   │     • Same as browser, but server-side
   │     • getClaims() validates JWT
   │
   └──► Drizzle (postgres.js)
         • TCP to Supavisor pooler
         • Transaction mode (port 6543) for serverless
         • Session mode (port 5432) for migrations

Background Workers / Cron
   │
   └──► Drizzle (postgres.js)
         • Can use session mode for long-running jobs
         • Or transaction mode for short jobs
```

---

## Schema Organization

```
Postgres
├── public schema (exposed via Data API)
│   ├── user_profiles    [RLS: auth.uid() = id]
│   ├── organizations    [RLS: membership-based]
│   ├── projects         [RLS: org membership]
│   └── ...
│
├── private schema (NOT exposed, server-only)
│   ├── billing_events   [Accessed via Drizzle only]
│   ├── audit_logs       [Accessed via Drizzle only]
│   └── ...
│
└── auth schema (Supabase-managed)
    └── users            [Read-only, triggers available]
```

**Key insight:** Tables in `private` schema are invisible to Data API. Use this for:
- Billing/payment data
- Admin-only tables
- Sensitive logs
- Internal system tables

To create:
```sql
CREATE SCHEMA IF NOT EXISTS private;
-- Tables here won't be exposed via PostgREST
```

---

## Advanced: User-Scoped RLS via Drizzle

If you need RLS semantics through direct Postgres connections (Drizzle), you can set JWT claims per transaction:

```typescript
// Advanced pattern - not usually needed
async function withUserContext<T>(userId: string, fn: () => Promise<T>): Promise<T> {
  return await db.transaction(async (tx) => {
    // Set claims for this transaction
    await tx.execute(sql`
      SELECT set_config('request.jwt.claims', '{"sub": "${userId}"}', true);
      SET LOCAL ROLE authenticated;
    `)
    return await fn()
  })
}
```

**Warning:** This is complex and error-prone. Prefer using the Supabase client for user-scoped data.

---

## Cost Model Awareness

The architecture should optimize for:

1. **Egress** — Cached egress is cheaper than uncached
   - Use Smart CDN
   - Set high `cache-control` on Storage assets

2. **Connections** — Pooler reduces connection overhead
   - Transaction mode for serverless
   - Keep `max` pool size small (pooler is the real pool)

3. **Compute** — Queries hit project compute
   - Index RLS columns
   - Use `EXPLAIN ANALYZE` to catch slow queries
   - Consider cron rollups for analytics

4. **MAU** — Monthly Active Users are billed
   - Don't create unnecessary auth sessions

See [COST-OPTIMIZATION.md](COST-OPTIMIZATION.md) for detailed strategies.
