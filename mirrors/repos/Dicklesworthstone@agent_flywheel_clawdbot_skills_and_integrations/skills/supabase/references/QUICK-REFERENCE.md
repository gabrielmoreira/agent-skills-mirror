# Quick Reference

Copy-paste patterns for common Supabase + Next.js + Drizzle operations.

---

## Environment Variables Template

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL="https://<project_ref>.supabase.co"
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY="sb_publishable_..."
SUPABASE_SERVICE_ROLE_KEY="sb_secret_..."

# Transaction pooler (runtime) - port 6543
DATABASE_URL="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"

# Session pooler (migrations) - port 5432
DATABASE_URL_MIGRATIONS="postgresql://postgres.<project_ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require"
```

---

## Drizzle Client (Transaction Pooler)

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

---

## Drizzle Config (Session Pooler for Migrations)

```typescript
// drizzle.config.ts
import "dotenv/config"
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./supabase/migrations",
  dbCredentials: { url: process.env.DATABASE_URL_MIGRATIONS! },
})
```

---

## Supabase Browser Client

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

---

## Supabase Server Client

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

---

## Middleware (Token Refresh)

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

  await supabase.auth.getClaims()  // NOT getSession()!
  return response
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
}
```

---

## OAuth Callback Route

```typescript
// app/auth/callback/route.ts
import { NextResponse } from "next/server"
import { supabaseServer } from "@/lib/supabase/server"

export async function GET(request: Request) {
  const url = new URL(request.url)
  const code = url.searchParams.get("code")

  if (code) {
    const supabase = supabaseServer()
    await supabase.auth.exchangeCodeForSession(code)
  }

  const forwardedHost = request.headers.get("x-forwarded-host")
  const origin = forwardedHost ? `https://${forwardedHost}` : url.origin

  return NextResponse.redirect(`${origin}/dashboard`)
}
```

---

## Login Button (Google OAuth)

```tsx
// components/login-button.tsx
"use client"
import { supabaseBrowser } from "@/lib/supabase/client"

export function LoginButton() {
  const handleLogin = async () => {
    const supabase = supabaseBrowser()
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    })
  }

  return <button onClick={handleLogin}>Continue with Google</button>
}
```

---

## Get Authenticated User (Server)

```typescript
// In Server Component or Route Handler
import { supabaseServer } from "@/lib/supabase/server"

export async function getUser() {
  const supabase = supabaseServer()
  const { data: { user } } = await supabase.auth.getUser()
  return user
}
```

---

## User Profiles Table + RLS

```sql
-- Create table
CREATE TABLE public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "read own profile" ON public.user_profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "update own profile" ON public.user_profiles
  FOR UPDATE USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, display_name, avatar_url)
  VALUES (
    new.id,
    new.email,
    COALESCE(new.raw_user_meta_data->>'name', new.email),
    new.raw_user_meta_data->>'avatar_url'
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN new;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

---

## Multi-Tenant RLS Pattern

```sql
-- Organizations table
CREATE TABLE public.organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  owner_id UUID REFERENCES auth.users(id)
);

-- Memberships table
CREATE TABLE public.org_memberships (
  org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member',
  PRIMARY KEY (org_id, user_id)
);

-- RLS on org-scoped data
CREATE POLICY "org members can read"
  ON public.some_table
  FOR SELECT
  USING (
    org_id IN (
      SELECT org_id FROM public.org_memberships
      WHERE user_id = auth.uid()
    )
  );

-- Index for RLS performance
CREATE INDEX idx_org_memberships_user ON public.org_memberships(user_id);
```

---

## Env Validation (Zod)

```typescript
// src/env.ts
import { z } from "zod"

export const env = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: z.string().min(10),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(10).optional(),
  DATABASE_URL: z.string().min(20),
  DATABASE_URL_MIGRATIONS: z.string().min(20),
}).parse(process.env)
```

---

## CLI Commands

```bash
# Link project
supabase login
supabase link --project-ref $PROJECT_REF

# Migrations
supabase migration new <name>
supabase db push

# Drizzle
drizzle-kit generate
drizzle-kit migrate
drizzle-kit studio

# Secrets
supabase secrets set --env-file .env
supabase secrets list

# Inspect
supabase inspect db unused-indexes
supabase inspect db table-sizes
```
