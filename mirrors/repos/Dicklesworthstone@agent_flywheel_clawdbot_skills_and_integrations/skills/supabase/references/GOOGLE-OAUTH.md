# Google OAuth

Setting up Google-only authentication with Supabase.

---

## Overview

Flow:
1. User clicks "Continue with Google"
2. Browser calls `signInWithOAuth({ provider: "google" })`
3. Supabase redirects to Google
4. Google redirects to Supabase callback (`/auth/v1/callback`)
5. Supabase redirects to your app's callback route (`/auth/callback`)
6. Your callback exchanges code for session

---

## Step 1: Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Go to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth client ID**
5. Select **Web application**
6. Add authorized redirect URIs:
   ```
   https://<project_ref>.supabase.co/auth/v1/callback
   http://127.0.0.1:54321/auth/v1/callback  (for local dev)
   ```
7. Copy **Client ID** and **Client Secret**

---

## Step 2: Supabase Dashboard

1. Go to **Authentication → Providers**
2. Enable **Google**
3. Paste Client ID and Client Secret
4. **Disable all other providers** (for Google-only auth):
   - Email/Password: OFF
   - Magic Link: OFF
   - Phone: OFF

---

## Step 3: Redirect URLs in Supabase

1. Go to **Authentication → URL Configuration**
2. Add to **Redirect URLs**:
   ```
   http://localhost:3000/auth/callback
   https://yourdomain.com/auth/callback
   ```

---

## Step 4: Login Button

```tsx
// components/login-button.tsx
"use client"

import { supabaseBrowser } from "@/lib/supabase/client"

export function LoginButton() {
  const handleLogin = async () => {
    const supabase = supabaseBrowser()
    const origin = window.location.origin

    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${origin}/auth/callback`,
        queryParams: {
          access_type: "offline",  // Get refresh token
          prompt: "consent",       // Always show consent screen
        },
      },
    })
  }

  return (
    <button
      onClick={handleLogin}
      className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50"
    >
      <GoogleIcon />
      Continue with Google
    </button>
  )
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  )
}
```

---

## Step 5: Callback Route Handler

```typescript
// app/auth/callback/route.ts
import { NextResponse } from "next/server"
import { supabaseServer } from "@/lib/supabase/server"

export async function GET(request: Request) {
  const url = new URL(request.url)
  const code = url.searchParams.get("code")
  const next = url.searchParams.get("next") ?? "/dashboard"
  const error = url.searchParams.get("error")

  // Handle OAuth errors
  if (error) {
    return NextResponse.redirect(
      `${url.origin}/login?error=${encodeURIComponent(error)}`
    )
  }

  if (code) {
    const supabase = supabaseServer()
    const { error } = await supabase.auth.exchangeCodeForSession(code)

    if (error) {
      return NextResponse.redirect(
        `${url.origin}/login?error=${encodeURIComponent(error.message)}`
      )
    }
  }

  // Handle proxied environments (Vercel, etc.)
  const forwardedHost = request.headers.get("x-forwarded-host")
  const origin = forwardedHost ? `https://${forwardedHost}` : url.origin

  return NextResponse.redirect(`${origin}${next}`)
}
```

---

## Step 6: Auto-Create User Profile

When a user signs up via Google, their profile info is available in `raw_user_meta_data`:

```sql
-- Trigger to create profile on signup
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
  ON CONFLICT (id) DO UPDATE SET
    display_name = COALESCE(EXCLUDED.display_name, user_profiles.display_name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, user_profiles.avatar_url),
    updated_at = now();

  RETURN new;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

---

## Accessing User Data

### From Server Component

```typescript
import { supabaseServer } from "@/lib/supabase/server"

export default async function ProfilePage() {
  const supabase = supabaseServer()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) return <div>Not logged in</div>

  return (
    <div>
      <img src={user.user_metadata.avatar_url} alt="Avatar" />
      <h1>{user.user_metadata.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

### From Client Component

```typescript
"use client"

import { useEffect, useState } from "react"
import { supabaseBrowser } from "@/lib/supabase/client"

export function UserAvatar() {
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null)

  useEffect(() => {
    const supabase = supabaseBrowser()
    supabase.auth.getUser().then(({ data: { user } }) => {
      setAvatarUrl(user?.user_metadata.avatar_url ?? null)
    })
  }, [])

  if (!avatarUrl) return null
  return <img src={avatarUrl} alt="Avatar" className="w-8 h-8 rounded-full" />
}
```

---

## Local Development

1. Start local Supabase:
   ```bash
   supabase start
   ```

2. Update `config.toml` (in `supabase/` folder):
   ```toml
   [auth.external.google]
   enabled = true
   client_id = "YOUR_CLIENT_ID"
   secret = "YOUR_CLIENT_SECRET"
   redirect_uri = "http://127.0.0.1:54321/auth/v1/callback"
   ```

3. Ensure Google Cloud Console has redirect URI:
   ```
   http://127.0.0.1:54321/auth/v1/callback
   ```

4. Update `.env.local`:
   ```
   NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=eyJ...  # from supabase start output
   ```

---

## Common Issues

### "redirect_uri_mismatch"

**Cause:** Google OAuth redirect URI doesn't match

**Fix:** Add exact URI to Google Cloud Console:
- Production: `https://<project_ref>.supabase.co/auth/v1/callback`
- Local: `http://127.0.0.1:54321/auth/v1/callback` (not localhost!)

### User stuck in redirect loop

**Cause:** Callback route not exchanging code for session

**Fix:** Ensure `exchangeCodeForSession(code)` is called and succeeds

### Profile data missing

**Cause:** Google didn't return profile data or trigger failed

**Fix:**
1. Check `raw_user_meta_data` in auth.users table
2. Verify trigger exists and has no errors
3. Ensure `prompt: "consent"` in signInWithOAuth options

### "Email not confirmed" error

**Cause:** Email confirmation required but Google emails are trusted

**Fix:** In Supabase Dashboard → Authentication → Settings, ensure "Confirm email" is OFF for OAuth providers
