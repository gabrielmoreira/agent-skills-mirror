# Auth SSR

Next.js App Router authentication with Supabase SSR package.

---

## Critical Security Rule

**Always use `getClaims()`, never trust `getSession()` in server code.**

| Method | Safe for Server? | Why |
|--------|------------------|-----|
| `getClaims()` | Yes | Validates JWT signature against Supabase public keys every time |
| `getSession()` | No | Reads from cookies without validation; cookies can be spoofed |
| `getUser()` | Yes (network call) | Makes request to auth server; confirms session is still valid |

`getClaims()` is the right balance: validates JWT locally (fast) without network roundtrip.

---

## Installation

```bash
bun add @supabase/supabase-js @supabase/ssr
```

---

## Browser Client

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

## Server Client

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
        getAll() {
          return store.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              store.set(name, value, options)
            })
          } catch {
            // Server Component can't set cookies - middleware handles this
          }
        },
      },
    }
  )
}
```

---

## Middleware (Token Refresh)

**Why middleware?** Server Components can't write cookies. Middleware intercepts requests, refreshes expired tokens, and sets new cookies on the response.

```typescript
// middleware.ts
import { createServerClient } from "@supabase/ssr"
import { NextResponse, type NextRequest } from "next/server"

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: { headers: request.headers },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          // Set on request (for downstream Server Components)
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          // Create new response with updated headers
          response = NextResponse.next({
            request: { headers: request.headers },
          })
          // Set on response (for browser)
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // This refreshes the token if expired and validates it
  await supabase.auth.getClaims()

  return response
}

export const config = {
  matcher: [
    // Skip static files and images
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
```

---

## Protecting Pages

### Server Component

```typescript
// app/dashboard/page.tsx
import { redirect } from "next/navigation"
import { supabaseServer } from "@/lib/supabase/server"

export default async function DashboardPage() {
  const supabase = supabaseServer()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect("/login")
  }

  return <div>Welcome, {user.email}</div>
}
```

### Route Handler

```typescript
// app/api/protected/route.ts
import { NextResponse } from "next/server"
import { supabaseServer } from "@/lib/supabase/server"

export async function GET() {
  const supabase = supabaseServer()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  return NextResponse.json({ message: "Protected data", userId: user.id })
}
```

### Server Action

```typescript
// app/actions.ts
"use server"

import { supabaseServer } from "@/lib/supabase/server"

export async function updateProfile(formData: FormData) {
  const supabase = supabaseServer()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    throw new Error("Unauthorized")
  }

  // Use Supabase client for RLS-protected operations
  await supabase.from("user_profiles").update({
    display_name: formData.get("name") as string,
  }).eq("id", user.id)
}
```

---

## Auth State in Client Components

```typescript
// hooks/use-user.ts
"use client"

import { useEffect, useState } from "react"
import { User } from "@supabase/supabase-js"
import { supabaseBrowser } from "@/lib/supabase/client"

export function useUser() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const supabase = supabaseBrowser()

    // Get initial session
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  return { user, loading }
}
```

---

## Logout

```typescript
// components/logout-button.tsx
"use client"

import { useRouter } from "next/navigation"
import { supabaseBrowser } from "@/lib/supabase/client"

export function LogoutButton() {
  const router = useRouter()

  const handleLogout = async () => {
    const supabase = supabaseBrowser()
    await supabase.auth.signOut()
    router.push("/")
    router.refresh()  // Refresh server components
  }

  return <button onClick={handleLogout}>Sign Out</button>
}
```

---

## Common Issues

### Users randomly logged out

**Cause:** Middleware not calling `getClaims()` to refresh tokens

**Fix:** Ensure middleware runs on auth-protected routes and calls `getClaims()`

### "cookies() can only be called in Server Component"

**Cause:** Calling `supabaseServer()` from client component

**Fix:** Use `supabaseBrowser()` for client components

### Session not available in Server Component

**Cause:** Missing middleware or wrong matcher pattern

**Fix:**
1. Check middleware.ts exists at project root
2. Verify matcher includes your routes
3. Ensure `getClaims()` is called in middleware

### Auth state out of sync between client/server

**Cause:** Not calling `router.refresh()` after auth state change

**Fix:** Call `router.refresh()` after login/logout to refresh server components
