---
name: vercel-deployment
description: "Operates a linked Next.js app on Vercel: CLI link, per-environment secrets, Edge versus Node runtimes, vercel --prod, custom domains, ISR/revalidate, function timeouts, and CORS. Trigger on Vercel env vars, edge functions, preview versus production, NEXT_PUBLIC_ leaks, or custom domains. Not a generic preview-link deploy of any framework (deploy-to-vercel)."
version: 1.0.1
risk: safe
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

## When to Use

Use this skill when the user:
- Mentions or implies **Vercel**, **deploy**, **deployment**, **hosting**, or **production**
- Needs to configure **environment variables** for Vercel (development, preview, production)
- Is creating **API routes** or **middleware** and needs to choose between Edge and Serverless runtimes
- Wants to optimize **build size** or **cold start** performance
- Is setting up **preview deployments**, **custom domains**, or **CI/CD** with Vercel
- Encounters **CORS**, **timeout**, **stale cache**, or **secret exposure** issues on Vercel

**Trigger keywords:** vercel, deploy, deployment, hosting, production, environment variables, edge function, serverless function, preview deployment, custom domain, cold start, ISR, revalidate.

## Prerequisites

- **Required skill:** `nextjs-app-router` — load it first if the task involves Next.js App Router patterns, server components, or middleware.
- A Vercel account and a linked project (or willingness to create one).
- Node.js installed locally (for `vercel` CLI and local dev).
- Windows host is primary; commands below assume **PowerShell** unless noted. On macOS/Linux, adapt path separators.

## Procedure

### 1. Install and Authenticate the Vercel CLI

```powershell
npm install -g vercel
vercel login
```

Follow the browser prompt to authenticate. Verify:

```powershell
vercel whoami
```

### 2. Link the Project (if not already linked)

From the project root:

```powershell
vercel link
```

This creates `.vercel/project.json`. Confirm the scope and project name when prompted.

### 3. Configure Environment Variables

Vercel has three environments:
- **Development** — local (`vercel dev`), also stored in `.env.local`
- **Preview** — PR deployments and non-production branches
- **Production** — `main` branch deployments

**Via Dashboard:** Settings → Environment Variables

**Via CLI:**

```powershell
# Public (browser-exposed) — safe to expose
vercel env add NEXT_PUBLIC_SUPABASE_URL production preview development
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production preview development

# Private (server-only) — NEVER use NEXT_PUBLIC_ prefix
vercel env add SUPABASE_SERVICE_ROLE_KEY production
vercel env add DATABASE_URL production preview
```

**Per-environment strategy:**

| Variable | Production | Preview | Development |
|---|---|---|---|
| `DATABASE_URL` | `postgresql://prod-host/prod-db` | `postgresql://staging-host/staging-db` | `.env.local` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://prod-xxx.supabase.co` | `https://staging-xxx.supabase.co` | `.env.local` |

**Detect environment in code:**

```typescript
const isProduction = process.env.VERCEL_ENV === 'production'
const isPreview = process.env.VERCEL_ENV === 'preview'
```

### 4. Choose Runtime: Edge vs Serverless

**Edge runtime** — fast cold starts, limited APIs. Good for auth checks, redirects, simple transforms.

```typescript
// app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return Response.json({ message: 'Hello from Edge!' })
}
```

Middleware is always Edge:

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  // Fast auth checks here
}
```

**Serverless (Node.js)** — full Node APIs, slower cold start. Good for DB queries, file ops, heavy computation.

```typescript
// app/api/users/route.ts
export const runtime = 'nodejs' // Default, can omit

export async function GET() {
  const users = await db.query('SELECT * FROM users')
  return Response.json(users)
}
```

**Edge-supported APIs:** `fetch`, `Request`, `Response`, `crypto.subtle` (Web Crypto), `TextEncoder`, `TextDecoder`, `URL`, `URLSearchParams`, `Headers`, `FormData`, `setTimeout`, `setInterval`.

**NOT supported in Edge:** `fs`, `path`, `os`, `Buffer` (use `Uint8Array`), `crypto.createHash` (use `crypto.subtle`), most npm packages with native deps.

**Crypto hashing in Edge:**

```typescript
async function hash(message: string) {
  const encoder = new TextEncoder()
  const data = encoder.encode(message)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}
```

### 5. Optimize the Build

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // For Docker/self-hosting

  images: {
    remotePatterns: [
      { hostname: 'your-cdn.com' },
    ],
  },

  // Bundle analyzer (dev only)
  // npm install @next/bundle-analyzer
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
      config.plugins.push(new BundleAnalyzerPlugin())
      return config
    },
  }),
}

module.exports = nextConfig
```

**Reduce serverless function size:**
- Use dynamic imports for heavy libs: `const sharp = await import('sharp')`
- Move heavy processing to external services (Cloudinary, imgix, Browserless.io)
- Check bundle: `npx @next/bundle-analyzer`
- Split into multiple functions (queue + status pattern)

### 6. Deploy

**Preview deployment:**

```powershell
vercel
```

**Production deployment:**

```powershell
vercel --prod
```

### 7. Set Up Preview Deployment Workflow

- Every PR automatically gets a unique preview URL (with Vercel GitHub integration).
- Protect preview deployments: Vercel Dashboard → Settings → Deployment Protection.
- Use different env vars for preview vs production (see step 3).
- Detect preview in code:

```typescript
if (process.env.VERCEL_ENV === 'preview') {
  // Show "Preview" banner
  // Use test payment processor
  // Disable analytics
}
```

### 8. Configure Custom Domains

**Via Dashboard:** Settings → Domains

Add domains:
- `example.com` (apex/root)
- `www.example.com` (subdomain)

**DNS configuration at your registrar:**

| Type | Name | Value |
|---|---|---|
| A | @ | `76.76.21.21` |
| CNAME | www | `cname.vercel-dns.com` |

Vercel handles www→apex redirects automatically.

**Custom redirects in `next.config.js`:**

```javascript
module.exports = {
  async redirects() {
    return [
      {
        source: '/old-page',
        destination: '/new-page',
        permanent: true, // 308
      },
    ]
  },
}
```

### 9. Handle Timeouts

Vercel timeout limits:
- **Hobby:** 10 seconds
- **Pro:** 60 seconds (can increase to 300)
- **Enterprise:** 900 seconds

**Increase timeout via `vercel.json`:**

```json
{
  "functions": {
    "app/api/slow/route.ts": {
      "maxDuration": 60
    }
  }
}
```

**For long operations:** return early and queue for background processing (Inngest, Trigger.dev), or use streaming responses.

### 10. Handle CORS

```typescript
// app/api/data/route.ts
export async function GET(request: Request) {
  const data = await fetchData()
  return Response.json(data, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}

export async function OPTIONS() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

**Or globally in `next.config.js`:**

```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
        ],
      },
    ]
  },
}
```

### 11. Control Caching

```typescript
// Force no caching (always fresh)
export const dynamic = 'force-dynamic'
export const revalidate = 0

// ISR — revalidate every 60 seconds
export const revalidate = 60
```

**On-demand revalidation:**

```typescript
import { revalidatePath, revalidateTag } from 'next/cache'

async function updatePost(id: string) {
  await db.post.update({ /* ... */ })
  revalidatePath(`/posts/${id}`)
  revalidateTag('posts')
}
```

## Pitfalls

### CRITICAL: NEXT_PUBLIC_ exposes secrets to the browser

**Symptoms:** Secrets visible in browser DevTools → Sources; security audit finds exposed keys; unexpected API access.

**Why:** Variables prefixed with `NEXT_PUBLIC_` are inlined into the JS bundle at build time. Anyone can view them.

**Safe to use `NEXT_PUBLIC_`:**
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (anon key is designed to be public)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` (`pk_live_...`)
- `NEXT_PUBLIC_GA_ID`

**NEVER use `NEXT_PUBLIC_`:**
- `SUPABASE_SERVICE_ROLE_KEY` — full database access
- `STRIPE_SECRET_KEY` (`sk_live_...`) — can charge cards
- `DATABASE_URL` — direct DB access
- `JWT_SECRET` — can forge tokens

**Fix:** Remove the `NEXT_PUBLIC_` prefix and access only in Server Components, API Routes, Server Actions (`'use server'`), or `getServerSideProps`.

### HIGH: Preview deployments using production database

**Symptoms:** Test data in production; production data corrupted after PR merge; users seeing test accounts.

**Why:** Preview deployments run untested code. A bug in a PR can corrupt production data.

**Fix:** Set up separate databases per environment. Use branching databases (Neon, PlanetScale, Supabase all support branch databases that auto-create a preview DB for each PR).

### HIGH: Serverless function too large / slow cold starts

**Symptoms:** First request takes 3–10+ seconds; function size limit exceeded error; deployment fails.

**Why:** Vercel serverless functions have a **50MB limit (compressed)**. Heavy dependencies (puppeteer, sharp) cause large bundles and slow cold starts.

**Fix:**
1. Use dynamic imports: `const sharp = await import('sharp')`
2. Move heavy processing to Edge runtime or external services
3. Check bundle: `npx @next/bundle-analyzer`
4. Split into multiple functions (queue + status pattern)

### HIGH: Edge runtime missing Node.js APIs

**Symptoms:** `X is not defined` at runtime; `Cannot find module fs`; works locally, fails deployed; middleware crashes.

**Why:** Edge runtime runs on V8, not Node.js. `fs`, `path`, `crypto` (partial), `child_process`, and most native modules are unavailable.

**Fix:** Use `export const runtime = 'nodejs'` if you need Node.js APIs. For crypto hashing in Edge, use `crypto.subtle.digest` instead of `crypto.createHash`.

### MEDIUM: Function timeout causes incomplete operations

**Symptoms:** `Task timed out after X seconds`; incomplete DB operations; partial file uploads; function killed mid-execution.

**Fix:** Return early and queue for background processing, use streaming responses, or increase `maxDuration` in `vercel.json` (Pro plan).

### MEDIUM: Environment variable present at build but missing at runtime

**Symptoms:** Env var undefined in production; value doesn't change after updating in dashboard; works in dev, wrong value in production.

**Why:** `NEXT_PUBLIC_*` variables and values read in `next.config.js`, `generateStaticParams`, or static pages are baked into the bundle at build time.

**Fix:** Use `export const dynamic = 'force-dynamic'` to force runtime reading. Don't use `NEXT_PUBLIC_` for values that must be read at runtime — read on the server and pass to client.

### MEDIUM: CORS errors calling API routes from different domain

**Symptoms:** CORS policy error in browser console; no `Access-Control-Allow-Origin` header; works in Postman but not browser.

**Fix:** Add CORS headers to API routes (see step 10 above) or configure globally in `next.config.js`.

### MEDIUM: Page shows stale data after deployment

**Symptoms:** Old content shows after deploy; changes not visible immediately; different users see different versions.

**Why:** Vercel caches aggressively at the edge. Static pages are cached; even dynamic pages may be cached if not configured properly.

**Fix:** Use `export const dynamic = 'force-dynamic'` and `export const revalidate = 0` for always-fresh pages. Use `revalidatePath` / `revalidateTag` for on-demand revalidation after mutations. Check `x-vercel-cache` response header: `HIT` = served from cache, `MISS` = freshly generated.

## Verification

### Verify deployment succeeded

```powershell
vercel ls
```

Check the latest deployment status is `READY`.

### Verify environment variables are set

```powershell
vercel env ls
```

Confirm each variable exists in the correct environments (production, preview, development).

### Verify no secrets are exposed to the browser

Open the deployed site in a browser → DevTools → Sources. Search for sensitive key patterns (`sk_live_`, `eyJ...` service role keys, `postgresql://`). If found, a `NEXT_PUBLIC_` variable is leaking a secret — fix immediately.

### Verify runtime selection

Check response headers on deployed API routes:

```powershell
curl -I https://your-deployment.vercel.app/api/hello
```

Edge functions respond with near-zero cold start; Node.js functions may show a brief delay on first request.

### Verify caching behavior

```powershell
curl -I https://your-site.vercel.app/posts
```

Check the `x-vercel-cache` header:
- `HIT` — served from cache
- `MISS` — freshly generated

### Verify custom domain SSL

```powershell
curl -I https://example.com
```

Confirm `HTTP/2 200` and a valid SSL certificate (Vercel provisions automatically).

### Validation checklist

| Check | Severity | Action |
|---|---|---|
| Secret in `NEXT_PUBLIC_` variable | CRITICAL | Remove prefix; access only server-side |
| Hardcoded Vercel URL | WARNING | Use `process.env.VERCEL_URL` or `NEXT_PUBLIC_VERCEL_URL` |
| Node.js API in Edge runtime | ERROR | Use `runtime = 'nodejs'` or remove Node deps |
| API route without CORS headers | WARNING | Add `Access-Control-Allow-Origin` if cross-origin |
| API route without error handling | WARNING | Wrap in try/catch; return appropriate error responses |
| Secret read in static context | WARNING | Move to runtime code or use `NEXT_PUBLIC_` for public values only |
| Large package import | WARNING | Use `lodash-es`, `date-fns` instead of `moment`, `@aws-sdk/client-*` instead of `aws-sdk` |
| Dynamic page without revalidation config | WARNING | Add `export const revalidate = 60` for ISR, or `0` for no cache |

## Related Skills

- **`nextjs-app-router`** — load first for App Router patterns, server components, middleware
- **`supabase-backend`** — load when deployment needs database configuration
- **`nextjs-supabase-auth`** — load when deployment needs auth config
- **`analytics-architecture`** — load when deployment needs monitoring/logs/analytics
- **`devops`** — load for CI/CD pipeline configuration
- **`qa-engineering`** — load for test automation before deployment

**Production launch workflow:**
1. App configuration (`nextjs-app-router`)
2. Database setup (`supabase-backend`)
3. Auth config (`nextjs-supabase-auth`)
4. Deploy (`vercel-deployment`)

**CI/CD pipeline workflow:**
1. Test automation (`qa-engineering`)
2. Pipeline config (`devops`)
3. Deploy strategy (`vercel-deployment`)
