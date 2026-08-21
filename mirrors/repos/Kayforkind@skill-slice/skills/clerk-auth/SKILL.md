---
name: clerk-auth
description: "Implements Clerk on Next.js App Router: ClerkProvider, clerkMiddleware/auth.protect(), organizations, Svix user-sync webhooks, and server auth()/client hooks. Use when the user mentions Clerk, ClerkProvider, sign-in/sign-up, organizations, SSO, or Clerk webhooks on Next.js 14/15. Not for Auth.js, NextAuth, Firebase Auth, or Clerk on non-Next stacks. Never trust middleware alone (CVE-2025-29927); re-check auth() in the handler."
version: 1.0.1
risk: safe
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Clerk Authentication

Expert patterns for Clerk auth implementation in Next.js 14/15 App Router: provider setup, middleware route protection, server/client component auth, organizations, webhook user sync, and API route protection.

## When to Use

Activate this skill when the user mentions or implies any of:

- Adding authentication to a Next.js app
- Clerk auth, ClerkProvider, or Clerk components
- User authentication, sign-in, sign-up flows
- User management or session handling
- Multi-tenancy or Clerk Organizations
- SSO / single sign-on
- Webhook-based user sync to a database
- Route protection via middleware

## Prerequisites

- Next.js 14 or 15 with App Router enabled
- A Clerk application created at clerk.com (publishable key + secret key)
- `@clerk/nextjs` installed: `npm install @clerk/nextjs`
- `svix` installed if using webhooks: `npm install svix`
- Environment variables configured in `.env.local` (never commit real keys)

## Procedure

### 1. Configure Environment Variables

Create `.env.local` with Clerk keys. The secret key must **never** have the `NEXT_PUBLIC_` prefix.

```bash
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY
CLERK_SECRET_KEY=sk_test_YOUR_KEY
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

### 2. Wrap the App with ClerkProvider

`ClerkProvider` must live in the root layout — never inside a page component.

```tsx
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### 3. Add Sign-In and Sign-Up Pages

Use Clerk's pre-built components with catch-all routes.

```tsx
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <SignIn />
    </div>
  );
}
```

```tsx
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <SignUp />
    </div>
  );
}
```

### 4. Add a Header with Auth Controls

```tsx
// components/Header.tsx
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';

export function Header() {
  return (
    <header className="flex justify-between p-4">
      <h1>My App</h1>
      <SignedOut>
        <SignInButton />
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </header>
  );
}
```

### 5. Set Up Middleware Route Protection

Place a **single** `middleware.ts` at the project root. Use `createRouteMatcher` for route groups and `auth.protect()` for explicit protection.

```ts
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/settings(.*)',
  '/api/private(.*)',
]);

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }

  // Role-based protection
  if (req.nextUrl.pathname.startsWith('/admin')) {
    await auth.protect({ role: 'org:admin' });
  }

  // Permission-based protection
  if (req.nextUrl.pathname.startsWith('/premium')) {
    await auth.protect({ permission: 'org:premium:access' });
  }
});

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

### 6. Access Auth in Server Components

Use `auth()` for quick checks (userId, orgId, orgRole). Use `currentUser()` only when you need the full User object — it counts toward rate limits.

```tsx
// app/dashboard/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const { userId } = await auth();

  if (!userId) {
    redirect('/sign-in');
  }

  const user = await currentUser();

  return (
    <div>
      <h1>Welcome, {user?.firstName}!</h1>
      <p>Email: {user?.emailAddresses[0]?.emailAddress}</p>
    </div>
  );
}
```

Server Actions also use `auth()`:

```ts
// app/actions/posts.ts
'use server';
import { auth } from '@clerk/nextjs/server';

export async function createPost(formData: FormData) {
  const { userId } = await auth();

  if (!userId) {
    throw new Error('Unauthorized');
  }

  const title = formData.get('title') as string;

  const post = await prisma.post.create({
    data: { title, authorId: userId },
  });

  return post;
}
```

### 7. Access Auth in Client Components

Always check `isLoaded` before reading user/auth state.

```tsx
// components/UserProfile.tsx
'use client';
import { useUser, useAuth } from '@clerk/nextjs';

export function UserProfile() {
  const { user, isLoaded, isSignedIn } = useUser();
  const { signOut } = useAuth();

  if (!isLoaded) return <div>Loading...</div>;
  if (!isSignedIn) return <div>Not signed in</div>;

  return (
    <div>
      <img src={user.imageUrl} alt={user.fullName ?? ''} />
      <h2>{user.fullName}</h2>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}
```

Organization switcher:

```tsx
// components/OrgSwitcher.tsx
'use client';
import { useOrganization, useOrganizationList } from '@clerk/nextjs';

export function OrgSwitcher() {
  const { organization, membership } = useOrganization();
  const { setActive, userMemberships } = useOrganizationList({
    userMemberships: { infinite: true },
  });

  if (!organization) return <p>No organization selected</p>;

  return (
    <div>
      <p>Current: {organization.name}</p>
      <p>Role: {membership?.role}</p>
      <select
        onChange={(e) => setActive?.({ organization: e.target.value })}
        value={organization.id}
      >
        {userMemberships.data?.map((mem) => (
          <option key={mem.organization.id} value={mem.organization.id}>
            {mem.organization.name}
          </option>
        ))}
      </select>
    </div>
  );
}
```

### 8. Implement Organizations and Multi-Tenancy

Use Clerk's pre-built organization components and always scope database queries by `orgId`.

```tsx
// app/create-org/page.tsx
import { CreateOrganization } from '@clerk/nextjs';

export default function CreateOrgPage() {
  return (
    <div className="flex justify-center">
      <CreateOrganization afterCreateOrganizationUrl="/dashboard" />
    </div>
  );
}
```

```tsx
// app/org-settings/page.tsx
import { OrganizationProfile } from '@clerk/nextjs';

export default function OrgSettingsPage() {
  return <OrganizationProfile />;
}
```

```tsx
// components/Header.tsx (with org switcher)
import { OrganizationSwitcher, UserButton } from '@clerk/nextjs';

export function Header() {
  return (
    <header className="flex justify-between p-4">
      <OrganizationSwitcher
        hidePersonal
        afterCreateOrganizationUrl="/dashboard"
        afterSelectOrganizationUrl="/dashboard"
      />
      <UserButton />
    </header>
  );
}
```

Org-scoped data access in Server Components:

```tsx
// app/dashboard/page.tsx
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { prisma } from '@/lib/prisma';

export default async function DashboardPage() {
  const { orgId } = await auth();

  if (!orgId) {
    redirect('/select-org');
  }

  const projects = await prisma.project.findMany({
    where: { organizationId: orgId },
  });

  return (
    <div>
      <h1>Projects</h1>
      {projects.map((p) => (
        <div key={p.id}>{p.name}</div>
      ))}
    </div>
  );
}
```

Role-based UI with `<Protect>`:

```tsx
'use client';
import { useOrganization, Protect } from '@clerk/nextjs';

export function AdminPanel() {
  return (
    <Protect role="org:admin" fallback={<p>Admin access required</p>}>
      <div>Admin content here</div>
    </Protect>
  );
}
```

### 9. Sync Users via Webhooks

Create a webhook endpoint that verifies the Svix signature and handles `user.created`, `user.updated`, and `user.deleted` events. Use `upsert` to handle race conditions.

```ts
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { WebhookEvent } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;

  if (!WEBHOOK_SECRET) {
    throw new Error('Missing CLERK_WEBHOOK_SECRET');
  }

  const headerPayload = await headers();
  const svix_id = headerPayload.get('svix-id');
  const svix_timestamp = headerPayload.get('svix-timestamp');
  const svix_signature = headerPayload.get('svix-signature');

  if (!svix_id || !svix_timestamp || !svix_signature) {
    return new Response('Missing svix headers', { status: 400 });
  }

  const payload = await req.json();
  const body = JSON.stringify(payload);

  const wh = new Webhook(WEBHOOK_SECRET);
  let evt: WebhookEvent;

  try {
    evt = wh.verify(body, {
      'svix-id': svix_id,
      'svix-timestamp': svix_timestamp,
      'svix-signature': svix_signature,
    }) as WebhookEvent;
  } catch (err) {
    console.error('Webhook verification failed:', err);
    return new Response('Verification failed', { status: 400 });
  }

  const eventType = evt.type;

  if (eventType === 'user.created' || eventType === 'user.updated') {
    const { id, email_addresses, first_name, last_name, image_url } = evt.data;

    await prisma.user.upsert({
      where: { clerkId: id },
      create: {
        clerkId: id,
        email: email_addresses[0]?.email_address,
        firstName: first_name,
        lastName: last_name,
        imageUrl: image_url,
      },
      update: {
        email: email_addresses[0]?.email_address,
        firstName: first_name,
        lastName: last_name,
        imageUrl: image_url,
      },
    });
  }

  if (eventType === 'user.deleted') {
    const { id } = evt.data;
    await prisma.user.delete({ where: { clerkId: id! } });
  }

  return new Response('Webhook processed', { status: 200 });
}
```

Corresponding Prisma schema:

```prisma
// prisma/schema.prisma
model User {
  id        String   @id @default(cuid())
  clerkId   String   @unique
  email     String   @unique
  firstName String?
  lastName  String?
  imageUrl  String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  posts     Post[]
  @@index([clerkId])
}
```

### 10. Protect API Route Handlers

Middleware provides initial protection, but always verify `auth()` inside the handler too — middleware can be bypassed (CVE-2025-29927).

```ts
// app/api/projects/route.ts
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';
import { NextResponse } from 'next/server';

export async function GET() {
  const { userId, orgId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const projects = await prisma.project.findMany({
    where: orgId
      ? { organizationId: orgId }
      : { userId, organizationId: null },
  });

  return NextResponse.json(projects);
}

export async function POST(req: Request) {
  const { userId, orgId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await req.json();

  const project = await prisma.project.create({
    data: {
      name: body.name,
      userId,
      organizationId: orgId ?? null,
    },
  });

  return NextResponse.json(project, { status: 201 });
}
```

Role-checked admin route:

```ts
// app/api/admin/users/route.ts
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';
import { NextResponse } from 'next/server';

export async function GET() {
  const { userId, orgRole } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  if (orgRole !== 'org:admin') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const users = await prisma.user.findMany();
  return NextResponse.json(users);
}
```

## Pitfalls

### CRITICAL: CVE-2025-29927 — Middleware Bypass

Middleware can be bypassed (CVE-2025-29927). **Never trust middleware alone** for security-critical checks. Always verify `auth()` inside the route handler or Server Component as well.

### HIGH: Multiple middleware.ts Files

Having more than one `middleware.ts` causes conflicts and redirect loops. Use a single `middleware.ts` at the project root with `createRouteMatcher` for all route groups.

### HIGH: 4 KB Session Token Cookie Limit

Clerk session tokens are stored in cookies. If the token exceeds 4 KB (large organizations, many roles/permissions), cookies may be silently truncated. Keep organization roles and permissions lean.

### HIGH: auth() Requires clerkMiddleware

`auth()` and `currentUser()` only work when `clerkMiddleware` is configured in `middleware.ts`. Without it, `auth()` returns null/undefined even for signed-in users.

### HIGH: Organization Data Not Scoped by orgId

Failing to filter database queries by `orgId` causes cross-organization data leaks. Always use `where: { organizationId: orgId }` in multi-tenant queries.

### MEDIUM: Webhook Race Conditions

`user.created` may arrive after `user.updated` (or vice versa). Use `upsert` instead of `create`/`update` to handle out-of-order events gracefully.

### MEDIUM: auth() is Async in App Router

In the App Router, `auth()` returns a Promise. Failing to `await` it silently returns undefined. Always use `const { userId } = await auth()`.

### MEDIUM: Middleware Blocks Webhook Endpoints

Webhooks originate from Clerk's servers, not authenticated users. If middleware protects `/api/webhooks(.*)`, webhooks will fail with 401. Add webhook routes to the public route matcher.

### MEDIUM: Accessing Auth State Before isLoaded

In Client Components, auth state is undefined during hydration. Always check `isLoaded` before reading `user`, `userId`, or any auth property.

### MEDIUM: Manual Redirects Cause Double Redirects

Handling redirects in page components instead of middleware leads to double redirects and missed routes. Centralize all redirect logic in `middleware.ts`.

### ERROR: Clerk Secret Key in Client Code

`CLERK_SECRET_KEY` must never have the `NEXT_PUBLIC_` prefix. If it does, it is exposed to the browser. Only `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` should be public.

### ERROR: Hardcoded Clerk API Keys

Never hardcode Clerk keys in source files. Always use environment variables.

### ERROR: Clerk Hooks in Server Components

`useUser`, `useAuth`, `useSession`, `useOrganization` only work in Client Components. In Server Components, use `auth()` and `currentUser()`.

## Verification

Run these checks after implementing Clerk auth:

1. **Verify middleware exists and is singular:**
   ```powershell
   Get-ChildItem -Path . -Recurse -Filter "middleware.ts" | Measure-Object | Select-Object -ExpandProperty Count
   ```
   Expected output: `1`

2. **Verify no NEXT_PUBLIC prefix on secret key:**
   ```powershell
   Select-String -Path .env.local -Pattern "NEXT_PUBLIC_CLERK_SECRET_KEY"
   ```
   Expected: no matches. The secret key line should be `CLERK_SECRET_KEY=sk_test_YOUR_KEY`.

3. **Verify auth() is awaited in all server files:**
   ```powershell
   Get-ChildItem -Recurse -Include "*.ts","*.tsx" | Select-String -Pattern "auth\(\)" | Where-Object { $_.Line -notmatch "await" -and $_.Line -notmatch "import" -and $_.Line -notmatch "//" }
   ```
   Expected: no lines where `auth()` appears without `await` (excluding imports and comments).

4. **Verify webhook route is public:**
   ```powershell
   Select-String -Path middleware.ts -Pattern "api/webhooks"
   ```
   Expected: at least one match in the public route matcher.

5. **Verify svix verification in webhook handler:**
   ```powershell
   Select-String -Path "app/api/webhooks/clerk/route.ts" -Pattern "wh.verify"
   ```
   Expected: at least one match.

6. **Verify orgId scoping in multi-tenant queries:**
   ```powershell
   Get-ChildItem -Recurse -Include "*.ts","*.tsx" | Select-String -Pattern "prisma\." | Select-String -Pattern "organizationId"
   ```
   Expected: queries touching org-scoped models include `organizationId` in the `where` clause.

7. **Verify isLoaded checks in client components:**
   ```powershell
   Get-ChildItem -Recurse -Include "*.tsx" | Select-String -Pattern "useUser|useAuth|useSession|useOrganization" | ForEach-Object { $f=$_; Get-Content $_.Path | Select-String "isLoaded" | Select-Object -First 1 } 
   ```
   Expected: files using Clerk hooks also reference `isLoaded`.

8. **Runtime check — start dev server and visit a protected route:**
   ```powershell
   npm run dev
   ```
   Navigate to `/dashboard` while signed out — should redirect to `/sign-in`. Sign in, then navigate back — should render the dashboard.

## Related Skills

- **postgres-wizard** — User table with `clerkId` for webhook sync
- **stripe-integration** — Customer linked to Clerk user ID
- **algolia-search** — Secured API keys per user
- **segment-cdp** — User identification via Clerk userId
- **resend-email** — Transactional emails triggered by auth events
