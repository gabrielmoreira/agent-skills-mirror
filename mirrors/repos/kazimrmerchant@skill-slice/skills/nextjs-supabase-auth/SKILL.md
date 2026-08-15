---
name: nextjs-supabase-auth
description: "Wires Supabase Auth to Next.js App Router with @supabase/ssr: browser/server clients, middleware refresh, OAuth callbacks, and getUser() session checks. Use when adding login, signup, OAuth, or route protection. Not for RLS/schema design, generic App Router routing, or Vercel storage product choice (vercel-storage)."
version: 1.0.1
---

# Next.js + Supabase Auth

Production-grade integration of Supabase Auth with Next.js App Router using `@supabase/ssr`. Covers browser/server client setup, middleware session refresh, OAuth callback handling, Server Action auth flows, and Server Component user access.

## When to Use

Trigger this skill when the user mentions or implies any of:

- "supabase auth next" / "authentication next.js" / "login supabase"
- "auth middleware" / "protected route" / "route protection"
- "auth callback" / "OAuth callback" / "Google login" / "GitHub login"
- "session management" / "get user server component" / "server action login"
- "sign out" / "sign up" / "password reset" with Supabase

Do **not** use this skill for database schema, RLS policies, or table design — delegate to `supabase-backend`. Do not use for generic Next.js routing questions without an auth component — delegate to `nextjs-app-router`.

## Prerequisites

- **Required skills**: `nextjs-app-router`, `supabase-backend`
- Next.js project using App Router (`app/` directory)
- Supabase project with Auth enabled and URL + anon key available
- `@supabase/ssr` package installed
- Environment variables set (no live secrets in code — use placeholders):

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

Install the SSR package if not present:

```powershell
npm install @supabase/ssr @supabase/supabase-js
```

## Procedure

### 1. Create the browser client

Used in Client Components (`'use client'`).

```ts
// lib/supabase/client.ts
'use client'
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

### 2. Create the server client

Used in Server Components, Route Handlers, and Server Actions. The `cookies()` API is async in Next.js 15+ — always `await` it.

```ts
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options)
          })
        },
      },
    }
  )
}
```

### 3. Add middleware for session refresh and route protection

Middleware runs on every matched request, refreshes the session cookie, and gates protected paths.

```ts
// middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  // Refresh session if expired — always call getUser() in middleware
  const { data: { user } } = await supabase.auth.getUser()

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard') && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

### 4. Add the OAuth callback route

Required when using OAuth providers (Google, GitHub, etc.). Exchanges the `code` query param for a session.

```ts
// app/auth/callback/route.ts
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/auth/error`)
}
```

### 5. Create Server Actions for sign in / sign out

```ts
// app/actions/auth.ts
'use server'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function signIn(formData: FormData) {
  const supabase = await createClient()
  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  redirect('/dashboard')
}

export async function signOut() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  revalidatePath('/', 'layout')
  redirect('/')
}
```

### 6. Access the user in a Server Component

```tsx
// app/dashboard/page.tsx
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div>
      <h1>Welcome, {user.email}</h1>
    </div>
  )
}
```

## Pitfalls

**HARD RULE: Never use `getSession()` for security-critical auth checks.** `getSession()` reads the JWT from the cookie without verifying it. Always use `supabase.auth.getUser()` — it makes a network request to Supabase and validates the token server-side.

- **OAuth without callback route**: If you configure an OAuth provider in the Supabase dashboard but omit `app/auth/callback/route.ts`, the redirect will fail silently. Always create the callback route.
- **Browser client in server context**: `createBrowserClient` will throw or produce stale sessions when used in Server Components or Server Actions. Always use `createServerClient` from `@supabase/ssr` on the server.
- **Protected routes without middleware**: Client-side route guards cause a flash of protected content before redirect. Move protection to `middleware.ts`.
- **Hardcoded redirect URLs**: Never hardcode `http://localhost:3000` in redirect logic. Use `origin` from the request URL or `process.env.NEXT_PUBLIC_SITE_URL`.
- **Missing error handling**: Every auth call returns `{ data, error }`. Always destructure and handle the error case — unhandled errors surface as opaque failures.
- **Missing `revalidatePath` after auth mutations**: Without `revalidatePath('/', 'layout')` after sign in / sign out, cached layouts may show stale auth state.
- **Forgetting to `await cookies()`**: In Next.js 15+, `cookies()` returns a Promise. Omitting `await` causes a type error or runtime failure.
- **Middleware matcher too broad**: Exclude static assets (`_next/static`, `_next/image`, `favicon.ico`) to avoid unnecessary auth calls on every asset request.

## Verification

1. **Check that all required files exist**:

```powershell
Test-Path lib/supabase/client.ts
Test-Path lib/supabase/server.ts
Test-Path middleware.ts
Test-Path app/auth/callback/route.ts
Test-Path app/actions/auth.ts
```

All should return `True`.

2. **Type-check the project**:

```powershell
npx tsc --noEmit
```

No errors expected if clients are wired correctly.

3. **Run the dev server and test auth flow**:

```powershell
npm run dev
```

- Navigate to `/login`, submit credentials, confirm redirect to `/dashboard`.
- Navigate to `/dashboard` while logged out — confirm redirect to `/login`.
- If using OAuth: trigger sign-in with provider, confirm callback at `/auth/callback` exchanges code and redirects.

4. **Verify session refresh in middleware**: Open browser DevTools → Application → Cookies. After session expiry, navigating to any matched route should refresh the `sb-*-auth-token` cookie automatically.

5. **Verify no `getSession()` usage in security-critical paths**:

```powershell
Select-String -Path "app\**\*.tsx","app\**\*.ts","middleware.ts" -Pattern "getSession\(\)" -SimpleMatch
```

If results appear in auth-gating logic, replace with `getUser()`.

## Related Skills

- `nextjs-app-router` — App Router routing, layouts, and Server Component patterns
- `supabase-backend` — Database schema, RLS policies, and query patterns
- `vercel-deployment` — Production deployment and environment variable configuration
- `stripe-integration` — Customer sync and subscription gating on top of authenticated users
