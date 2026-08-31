# Pooler Gotchas

Understanding Supavisor connection pooling, IPv4/IPv6, and session vs transaction modes.

---

## Connection Types

| Type | Port | Use Case | Prepared Statements | IPv4 |
|------|------|----------|---------------------|------|
| Direct | 5432 | Long-running servers | Yes | No (IPv6) |
| Session Pooler | 5432 | Persistent clients, migrations | Yes | Yes |
| Transaction Pooler | 6543 | Serverless, edge functions | No | Yes |

---

## The IPv4/IPv6 Problem

**Direct connections use IPv6 by default.** Most serverless environments (Vercel, GitHub Actions, AWS Lambda) only support IPv4.

### Symptoms

```
Error: connect ENETUNREACH 2600:... - network unreachable
Error: getaddrinfo ENOTFOUND db.xxx.supabase.co
```

### Solution

Use Supavisor pooler connection strings (either mode). They resolve to IPv4.

```bash
# Direct (IPv6) - AVOID on serverless
postgresql://postgres:<password>@db.<project_ref>.supabase.co:5432/postgres

# Pooler session mode (IPv4) - OK
postgresql://postgres.<project_ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres

# Pooler transaction mode (IPv4) - BEST for serverless
postgresql://postgres.<project_ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

---

## Session Mode vs Transaction Mode

### Session Mode (Port 5432)

- Connection persists for entire client session
- Supports prepared statements
- Supports `SET` commands that persist
- Queues clients if pool is full (up to 60s)
- Use for: migrations, `pg_dump`, GUI tools, long-running jobs

### Transaction Mode (Port 6543)

- Connection released after each transaction
- **Does NOT support prepared statements**
- `SET` commands don't persist between queries
- Higher throughput for many short connections
- Use for: serverless functions, edge functions, Next.js API routes

---

## Username Format

Pooler usernames include project reference:

```
postgres.<project_ref>
```

The dot is **real and required**. Copy the exact string from Dashboard → Connect.

---

## Prepared Statements Error

### Symptom

```
Error: prepared statement "s1" does not exist
Error: prepared statement already exists
```

### Cause

Using transaction mode with prepared statements enabled.

### Fix

Disable prepared statements in your driver:

**postgres.js (Drizzle)**
```typescript
const sql = postgres(process.env.DATABASE_URL!, {
  prepare: false,  // Required for transaction pooler
})
```

**node-postgres (pg)**
```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})
// Use simple query protocol
const result = await pool.query({ text: 'SELECT * FROM users', rowMode: 'array' })
```

**Prisma**
```
DATABASE_URL="postgresql://...?pgbouncer=true&connection_limit=1"
```

---

## When to Use Which Mode

| Scenario | Mode | Port |
|----------|------|------|
| Next.js API routes | Transaction | 6543 |
| Next.js Server Components | Transaction | 6543 |
| Edge Functions | Transaction | 6543 |
| Drizzle runtime queries | Transaction | 6543 |
| Drizzle migrations | Session | 5432 |
| `supabase db push` | Session | 5432 |
| Database GUI (TablePlus, etc.) | Session | 5432 |
| Background workers (long-running) | Session | 5432 |

---

## Two Connection Strings Pattern

```bash
# Runtime (transaction mode)
DATABASE_URL="postgresql://postgres.<ref>:<pw>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"

# Migrations (session mode)
DATABASE_URL_MIGRATIONS="postgresql://postgres.<ref>:<pw>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require"
```

In drizzle.config.ts:
```typescript
export default defineConfig({
  dbCredentials: { url: process.env.DATABASE_URL_MIGRATIONS! },
})
```

In application code:
```typescript
const sql = postgres(process.env.DATABASE_URL!, { prepare: false })
```

---

## Pool Sizing

Supavisor is the real connection pool. Keep client-side pools small.

```typescript
const sql = postgres(process.env.DATABASE_URL!, {
  prepare: false,
  max: process.env.NODE_ENV === "production" ? 5 : 1,
})
```

### Why small pools?

- Supavisor multiplexes connections efficiently
- Too many client connections = wasted resources
- In dev, use 1 to prevent leaks during hot reload

---

## Connection Limits

| Plan | Direct Connections | Pooler Connections |
|------|--------------------|--------------------|
| Free | 60 | 200 |
| Pro | 60 | 200 |
| Team | 60 | 200 |
| Enterprise | Configurable | Configurable |

**Note:** "Pooler connections" are client connections to Supavisor, not actual Postgres connections.

---

## Tenant/User Not Found Error

### Symptom

```
Error: Tenant or user not found
Error: FATAL: password authentication failed
```

### Causes

1. Wrong username format (missing `.project_ref`)
2. Wrong password
3. Wrong pooler host/region

### Fix

Copy exact connection string from Dashboard → Connect button.

---

## SSL Configuration

Always use SSL:

```bash
?sslmode=require
```

For strict validation:
```bash
?sslmode=verify-full&sslrootcert=/path/to/ca.crt
```

---

## Dedicated Pooler (Paid Plans)

Paid plans can enable a dedicated pooler for better performance:

- Lower latency (co-located with database)
- Higher connection limits
- Uses more project compute resources

Enable in Dashboard → Database → Connection Pooling.

---

## Debugging Connections

### Check active connections

```sql
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  query_start
FROM pg_stat_activity
WHERE datname = 'postgres';
```

### Check pooler stats (Supavisor)

```sql
SELECT * FROM supavisor.pools;
SELECT * FROM supavisor.clients;
```

### Common issues

| Issue | Check |
|-------|-------|
| Too many connections | Reduce client pool size |
| Slow queries | Check for missing indexes |
| Connection refused | Verify firewall/IP allowlist |
| Intermittent failures | Check connection string format |
