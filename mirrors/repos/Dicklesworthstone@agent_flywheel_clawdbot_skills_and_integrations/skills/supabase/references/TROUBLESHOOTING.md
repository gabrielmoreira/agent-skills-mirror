# Troubleshooting

Common errors and their solutions.

---

## Connection Errors

### ENETUNREACH / Network Unreachable

```
Error: connect ENETUNREACH 2600:... - network unreachable
```

**Cause:** Direct connection uses IPv6; environment only supports IPv4.

**Fix:** Use pooler connection string (session or transaction mode).

```bash
# Change from direct:
postgresql://postgres:<pw>@db.<ref>.supabase.co:5432/postgres

# To pooler:
postgresql://postgres.<ref>:<pw>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

---

### Prepared Statement Does Not Exist

```
Error: prepared statement "s1" does not exist
```

**Cause:** Transaction pooler doesn't support prepared statements.

**Fix:** Disable prepared statements in your driver.

```typescript
// postgres.js
const sql = postgres(url, { prepare: false })

// Prisma - add to connection string
?pgbouncer=true
```

---

### Tenant or User Not Found

```
Error: Tenant or user not found
Error: FATAL: password authentication failed
```

**Cause:** Wrong connection string format.

**Fix:**
1. Copy exact string from Dashboard → Connect
2. Verify username includes `.project_ref`
3. Check password is correct

---

### Too Many Connections

```
Error: remaining connection slots are reserved
Error: sorry, too many clients already
```

**Cause:** Exceeding connection limit or pool too large.

**Fix:**
1. Use transaction pooler for serverless
2. Reduce client pool size
3. Add `globalThis` caching for dev mode

```typescript
const g = globalThis as unknown as { __sql?: ReturnType<typeof postgres> }
export const sql = g.__sql ?? postgres(url, { prepare: false, max: 5 })
if (process.env.NODE_ENV !== "production") g.__sql = sql
```

---

## Authentication Errors

### Users Randomly Logged Out

**Cause:** Token not refreshing in middleware.

**Fix:** Ensure middleware calls `getClaims()`:

```typescript
// middleware.ts
await supabase.auth.getClaims()  // NOT getSession()
```

---

### Invalid JWT / JWT Expired

```
Error: Invalid JWT
Error: JWT expired
```

**Cause:** Token expired and not refreshed.

**Fix:**
1. Verify middleware is running (check matcher pattern)
2. Ensure `getClaims()` is called in middleware
3. Check cookie settings allow refresh

---

### Email Not Confirmed

```
Error: Email not confirmed
```

**Cause:** Email confirmation required but using OAuth.

**Fix:** For OAuth providers, email is already verified.

Dashboard → Authentication → Settings → Disable "Confirm email" for OAuth.

---

### OAuth Redirect Mismatch

```
Error: redirect_uri_mismatch
```

**Cause:** Redirect URI in Google Cloud Console doesn't match.

**Fix:** Add exact URI to Google Cloud Console:
- `https://<project_ref>.supabase.co/auth/v1/callback`
- `http://127.0.0.1:54321/auth/v1/callback` (local, note: 127.0.0.1 not localhost)

---

## RLS Errors

### Permission Denied

```
Error: permission denied for table xxx
Error: new row violates row-level security policy
```

**Cause:** RLS policy blocking access.

**Debug:**
```sql
-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'xxx';

-- Test as user
SET request.jwt.claims = '{"sub": "user-uuid"}';
SET ROLE authenticated;
SELECT * FROM public.xxx;
RESET ROLE;
```

---

### RLS Not Blocking (Table Exposed)

**Cause:** RLS not enabled on table.

**Fix:**
```sql
ALTER TABLE public.xxx ENABLE ROW LEVEL SECURITY;
```

---

### Slow Queries with RLS

**Cause:** Missing indexes on RLS filter columns.

**Fix:**
```sql
CREATE INDEX idx_xxx_user_id ON public.xxx(user_id);
```

**Debug:**
```sql
EXPLAIN ANALYZE SELECT * FROM public.xxx WHERE user_id = 'xxx';
```

---

## Database Errors

### Relation Does Not Exist

```
Error: relation "xxx" does not exist
```

**Cause:** Table not created or wrong schema.

**Fix:**
1. Run migrations: `drizzle-kit migrate` or `supabase db push`
2. Check you're connected to correct project
3. Verify schema (public vs private)

---

### Column Does Not Exist

```
Error: column "xxx" does not exist
```

**Cause:** Schema out of sync.

**Fix:**
1. Pull latest schema: `drizzle-kit pull`
2. Generate and apply migration
3. Regenerate types: `supabase gen types typescript`

---

### Deadlock Detected

```
Error: deadlock detected
```

**Cause:** Concurrent transactions waiting on each other.

**Fix:**
1. Review transaction order (access tables in consistent order)
2. Reduce transaction scope
3. Use row-level locks explicitly where needed

---

## Storage Errors

### Object Not Found

```
Error: Object not found
```

**Cause:** File doesn't exist or wrong bucket.

**Fix:**
1. Verify bucket name
2. Check file path (case-sensitive)
3. Verify file was uploaded successfully

---

### Bucket Not Found

```
Error: Bucket not found
```

**Cause:** Bucket doesn't exist.

**Fix:**
```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('avatars', 'avatars', true);
```

---

### Storage Access Denied

```
Error: new row violates row-level security policy for table "objects"
```

**Cause:** Storage RLS policy blocking access.

**Fix:** Add policy to `storage.objects`:
```sql
CREATE POLICY "allow uploads"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'avatars' AND auth.uid() IS NOT NULL);
```

---

## Edge Function Errors

### CPU Time Exceeded

```
Error: Worker exceeded CPU time limit
```

**Cause:** Function doing too much CPU work.

**Fix:**
1. Optimize algorithm
2. Use Rust/WASM for heavy compute
3. Move work to background job

---

### Memory Limit Exceeded

```
Error: Worker exceeded memory limit
```

**Cause:** Function using > 256MB memory.

**Fix:**
1. Process data in chunks
2. Stream instead of buffering
3. Move to background worker

---

## Debugging Tools

### Check Database Status

```bash
supabase status
supabase inspect db table-sizes
supabase inspect db unused-indexes
```

### Check Auth Configuration

Dashboard → Authentication → Providers

### Check RLS Policies

```sql
SELECT * FROM pg_policies WHERE schemaname = 'public';
```

### Check Connection Info

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'postgres';
```

### Enable Query Explain

```sql
ALTER ROLE authenticator SET pgrst.db_plan_enabled TO 'true';
NOTIFY pgrst, 'reload config';
```

Then use `.explain()` in queries:
```typescript
const { data, error } = await supabase.from('table').select().explain()
```

---

## Getting Help

1. Check [Supabase Status](https://status.supabase.com/)
2. Search [GitHub Discussions](https://github.com/orgs/supabase/discussions)
3. Check [Supabase Docs Troubleshooting](https://supabase.com/docs/guides/troubleshooting)
