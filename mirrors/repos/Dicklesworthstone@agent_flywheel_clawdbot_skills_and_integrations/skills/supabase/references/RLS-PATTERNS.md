# RLS Patterns

Row Level Security best practices for SaaS multi-tenant applications.

---

## The Non-Negotiables

1. **Enable RLS on ALL tables in `public` schema** — tables without RLS are accessible via anon role
2. **Never use `service_role` key client-side** — it bypasses RLS
3. **Index columns used in RLS policies** — can yield 100x improvement

---

## Basic Patterns

### User-Owned Data

```sql
-- Table
CREATE TABLE public.user_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS
ALTER TABLE public.user_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users can CRUD own documents"
  ON public.user_documents
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Index for RLS performance
CREATE INDEX idx_user_documents_user_id ON public.user_documents(user_id);
```

### Multi-Tenant (Organization-Based)

```sql
-- Organizations
CREATE TABLE public.organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Memberships
CREATE TABLE public.org_memberships (
  org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member',
  PRIMARY KEY (org_id, user_id)
);

-- Org-scoped data
CREATE TABLE public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL
);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- RLS: User must be member of org
CREATE POLICY "org members can read projects"
  ON public.projects
  FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM public.org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Index for RLS performance (critical!)
CREATE INDEX idx_org_memberships_user_id ON public.org_memberships(user_id);
```

---

## Performance Optimization

### 1. Wrap Functions in SELECT

**Bad (evaluated per row):**
```sql
USING (is_admin() OR auth.uid() = user_id)
```

**Good (cached via initPlan):**
```sql
USING ((SELECT is_admin()) OR (SELECT auth.uid()) = user_id)
```

### 2. Index RLS Filter Columns

```sql
-- If your RLS uses user_id
CREATE INDEX idx_tablename_user_id ON public.tablename(user_id);

-- If your RLS uses org_id
CREATE INDEX idx_tablename_org_id ON public.tablename(org_id);
```

### 3. Optimize Membership Lookups

**Bad (subquery per row):**
```sql
USING (
  auth.uid() IN (
    SELECT user_id FROM team_members WHERE team_id = table.team_id
  )
)
```

**Good (inverted lookup):**
```sql
USING (
  team_id IN (
    SELECT team_id FROM team_members WHERE user_id = auth.uid()
  )
)
```

### 4. Use Security Definer Functions

```sql
-- Create function
CREATE OR REPLACE FUNCTION public.user_org_ids()
RETURNS UUID[]
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT ARRAY(
    SELECT org_id FROM public.org_memberships
    WHERE user_id = auth.uid()
  )
$$;

-- Use in RLS
CREATE POLICY "org members can read"
  ON public.projects
  FOR SELECT
  USING (org_id = ANY((SELECT public.user_org_ids())));
```

---

## Role-Based Access

### Using app_metadata (Secure)

```sql
-- Check admin role in app_metadata (can't be modified by user)
CREATE POLICY "admins can manage all"
  ON public.some_table
  FOR ALL
  USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  );
```

### Using Custom Roles Table

```sql
CREATE TABLE public.user_roles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'user'
);

CREATE POLICY "admins can do everything"
  ON public.some_table
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );
```

---

## tenant_id in app_metadata (Performance Pattern)

For high-performance multi-tenant, store tenant_id in JWT:

### 1. Set tenant_id on user creation

```sql
-- Trigger to set tenant_id in app_metadata
CREATE OR REPLACE FUNCTION public.set_user_tenant()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE auth.users
  SET raw_app_meta_data = raw_app_meta_data || jsonb_build_object('tenant_id', new.id)
  WHERE id = new.owner_id;
  RETURN new;
END;
$$;

CREATE TRIGGER on_org_created
  AFTER INSERT ON public.organizations
  FOR EACH ROW EXECUTE PROCEDURE public.set_user_tenant();
```

### 2. RLS using JWT claim (no table lookup)

```sql
CREATE POLICY "tenant isolation"
  ON public.tenant_data
  FOR ALL
  USING (
    tenant_id = (auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid
  );
```

**Why this is fast:** No subquery to memberships table; tenant_id is in JWT.

---

## Common Patterns

### Public Read, Authenticated Write

```sql
CREATE POLICY "anyone can read"
  ON public.blog_posts
  FOR SELECT
  USING (published = true);

CREATE POLICY "authors can write"
  ON public.blog_posts
  FOR INSERT
  USING (auth.uid() IS NOT NULL)
  WITH CHECK (auth.uid() = author_id);
```

### Soft Delete

```sql
-- Only show non-deleted rows
CREATE POLICY "hide deleted"
  ON public.items
  FOR SELECT
  USING (deleted_at IS NULL AND user_id = auth.uid());

-- Allow marking as deleted
CREATE POLICY "soft delete"
  ON public.items
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

### Time-Based Access

```sql
-- Only access items within valid period
CREATE POLICY "time-based access"
  ON public.subscriptions
  FOR SELECT
  USING (
    user_id = auth.uid()
    AND starts_at <= now()
    AND (expires_at IS NULL OR expires_at > now())
  );
```

---

## Debugging RLS

### Check What User Sees

```sql
-- Run as authenticated user
SET request.jwt.claims = '{"sub": "user-uuid-here"}';
SET ROLE authenticated;

SELECT * FROM public.some_table;

-- Reset
RESET ROLE;
```

### View Policies

```sql
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public';
```

### Enable Query Plans

```sql
-- Enable in dev only
ALTER ROLE authenticator SET pgrst.db_plan_enabled TO 'true';
NOTIFY pgrst, 'reload config';

-- Then use .explain() in client
const { data, error } = await supabase
  .from('table')
  .select()
  .explain()
```

---

## Anti-Patterns

### Don't Use user_metadata for Authorization

```sql
-- BAD: user_metadata is user-modifiable!
USING ((auth.jwt() -> 'user_metadata' ->> 'is_admin')::boolean = true)

-- GOOD: use app_metadata (only modifiable server-side)
USING ((auth.jwt() -> 'app_metadata' ->> 'is_admin')::boolean = true)
```

### Don't Rely on RLS for Query Optimization

```sql
-- BAD: Hoping RLS filters are enough
SELECT * FROM large_table;

-- GOOD: Explicit WHERE + RLS as safety net
SELECT * FROM large_table WHERE user_id = auth.uid();
```

### Don't Forget Views and Functions

```sql
-- Views need RLS too!
ALTER VIEW public.my_view SET (security_invoker = on);

-- Functions exposed via RPC need security
CREATE FUNCTION public.my_function()
RETURNS void
LANGUAGE plpgsql
SECURITY INVOKER  -- Uses caller's permissions
AS $$ ... $$;
```
