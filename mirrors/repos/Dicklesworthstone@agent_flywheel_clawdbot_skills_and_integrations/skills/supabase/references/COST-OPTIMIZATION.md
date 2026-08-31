# Cost Optimization

Strategies to keep Supabase costs predictable and low.

---

## What You're Paying For

| Item | Free Quota | Pro Overage | Notes |
|------|------------|-------------|-------|
| MAU | 50,000 | $0.00325/MAU | Monthly Active Users |
| Database Disk | 500MB → 8GB | $0.125/GB | Auto-scales |
| Egress | 5GB → 250GB | $0.09/GB | Cached is cheaper |
| Storage | 1GB → 100GB | $0.021/GB | |
| Edge Function Invocations | 500K → 2M | $2/1M | |
| Realtime Messages | 2M → 5M | $2.50/1M | |
| Realtime Peak Connections | 200 → 500 | $10/1000 | |

**Not covered by Spend Cap:** Compute, read replicas, PITR, IPv4 add-on, extra IOPS.

---

## #1: Enable Spend Cap (Pro Plan)

The single most important cost guardrail.

**Dashboard → Organization → Billing → Spend Cap: ON**

When enabled:
- Usage is disallowed (not charged) when quota exceeded
- Features restrict until next billing cycle
- You don't get surprise bills

---

## #2: Use the Right Pooler Mode

| Mode | Use For | Port |
|------|---------|------|
| Transaction | Serverless runtime | 6543 |
| Session | Migrations, long jobs | 5432 |

Transaction mode multiplexes connections efficiently, reducing connection overhead.

---

## #3: Reduce Egress

### Enable Smart CDN

Dashboard → Settings → Smart CDN: Enable

Cached egress is cheaper than uncached. Smart CDN increases cache hit rate.

### Set High Cache-Control on Storage

```typescript
const { error } = await supabase.storage
  .from('avatars')
  .upload('avatar.png', file, {
    cacheControl: '31536000',  // 1 year
    upsert: true,
  })
```

### Limit Upload Size

```sql
-- Bucket-level size limit
UPDATE storage.buckets
SET file_size_limit = 5242880  -- 5MB
WHERE name = 'avatars';
```

### Gzip Log Drains

If using log drains, enable gzip compression on the receiving end.

---

## #4: Index RLS Columns

RLS policies scan rows. Without indexes, this is slow and expensive.

```sql
-- Index columns used in RLS
CREATE INDEX idx_user_data_user_id ON public.user_data(user_id);
CREATE INDEX idx_projects_org_id ON public.projects(org_id);
```

Use Index Advisor:
```bash
supabase inspect db unused-indexes
```

---

## #5: Harden Data API

### Move Sensitive Tables to Private Schema

```sql
CREATE SCHEMA IF NOT EXISTS private;

CREATE TABLE private.billing_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ...
);

-- Not exposed via PostgREST
```

### Or Expose Explicit API Schema

```sql
-- In config.toml
[api]
schemas = ["api"]  -- Not "public"
```

---

## #6: Be Deliberate with Realtime

Realtime messages and peak connections are billable.

**Do:**
- Subscribe only when needed
- Unsubscribe when component unmounts
- Use specific channel filters

**Don't:**
- Subscribe everyone to global channels
- Keep connections open unnecessarily

```typescript
// Good: Specific subscription
const channel = supabase
  .channel('project-123')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'projects',
    filter: 'id=eq.project-123'
  }, handleChange)
  .subscribe()

// Cleanup
useEffect(() => {
  return () => { supabase.removeChannel(channel) }
}, [])
```

---

## #7: Cron Rollups for Analytics

For event-heavy workloads (A/B tests, analytics), use rollups to control disk growth.

### Pattern

1. Write raw events to staging table
2. Cron job aggregates into rollup tables
3. Cron job deletes old raw events

### Implementation

```sql
-- Raw events (short retention)
CREATE TABLE public.raw_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  properties JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Daily rollups (long retention)
CREATE TABLE public.daily_metrics (
  date DATE NOT NULL,
  event_type TEXT NOT NULL,
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (date, event_type)
);

-- Rollup function
CREATE OR REPLACE FUNCTION public.rollup_daily_metrics()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO public.daily_metrics (date, event_type, count)
  SELECT
    DATE(created_at),
    event_type,
    COUNT(*)
  FROM public.raw_events
  WHERE created_at < CURRENT_DATE
  GROUP BY DATE(created_at), event_type
  ON CONFLICT (date, event_type)
  DO UPDATE SET count = daily_metrics.count + EXCLUDED.count;

  DELETE FROM public.raw_events
  WHERE created_at < CURRENT_DATE - INTERVAL '7 days';
END;
$$;

-- Schedule with pg_cron
SELECT cron.schedule(
  'rollup-metrics',
  '0 3 * * *',  -- 3 AM daily
  'SELECT public.rollup_daily_metrics()'
);
```

---

## #8: Storage Performance

### Custom Listing Function

`supabase.storage.list()` can be slow at scale. Use a custom function:

```sql
CREATE OR REPLACE FUNCTION storage.list_objects_fast(bucket_id text, prefix text)
RETURNS TABLE (name text, size bigint, updated_at timestamptz)
LANGUAGE sql STABLE
AS $$
  SELECT name, metadata->>'size'::bigint, updated_at
  FROM storage.objects
  WHERE bucket_id = $1
    AND name LIKE $2 || '%'
  ORDER BY name
  LIMIT 1000;
$$;
```

### Image Transformations

Billed per origin image. Minimize unique transformations:

```typescript
// Good: Standard sizes
const url = supabase.storage.from('images').getPublicUrl('photo.jpg', {
  transform: { width: 200, height: 200 }  // Reuse standard sizes
})

// Bad: Many unique sizes
const url = supabase.storage.from('images').getPublicUrl('photo.jpg', {
  transform: { width: Math.random() * 1000, height: Math.random() * 1000 }
})
```

---

## #9: Edge Functions Limits

| Limit | Free | Paid |
|-------|------|------|
| Wall Clock | 150s | 400s |
| CPU Time | 2s | 2s |
| Memory | 256MB | 256MB |

Edge Functions are for IO-bound tasks, not heavy compute.

**Good use cases:**
- Webhook handlers
- Auth checks
- API orchestration

**Bad use cases:**
- Image processing
- Heavy data transformation
- ML inference

For CPU-intensive work, use Rust/WASM modules.

---

## #10: Backup Strategy

### PITR vs Daily Backups

| | Daily Backups | PITR |
|---|---------------|------|
| Granularity | 24h | 1 second |
| Cost | Included (Pro) | Extra |
| Spend Cap | N/A | Not covered |

**If you enable PITR, daily backups are no longer taken.**

Choose based on RPO (Recovery Point Objective):
- Can lose 24h of data? → Daily backups
- Need point-in-time recovery? → PITR

### Storage Not Included

Database backups do NOT include Storage objects. For storage backup:
- Use R2/S3 as primary for critical assets
- Implement application-level backup for Storage

---

## Monitoring Commands

```bash
# Check table sizes
supabase inspect db table-sizes

# Check unused indexes (remove to save space)
supabase inspect db unused-indexes

# Check index sizes
supabase inspect db index-sizes

# Check slow queries
supabase inspect db long-running-queries
```

---

## Quick Checklist

- [ ] Spend Cap enabled
- [ ] Transaction pooler for serverless
- [ ] RLS columns indexed
- [ ] Smart CDN enabled
- [ ] High cache-control on Storage assets
- [ ] Realtime subscriptions scoped and cleaned up
- [ ] Cron rollups for analytics/events
- [ ] Sensitive tables in private schema
- [ ] PITR decision made (not enabled "just because")
