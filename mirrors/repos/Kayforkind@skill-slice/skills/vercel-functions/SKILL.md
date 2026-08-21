---
name: vercel-functions
description: Guides Vercel Functions compute covering Node serverless, Edge isolates, Fluid Compute, streaming, Cron, waitUntil/after, and vercel.json runtime config. Use when editing api routes, App Router route handlers, or debugging FUNCTION_INVOCATION_FAILED and vercel logs. Not for Blob or Edge Config storage (vercel-storage), monorepo task graphs (turborepo), or Next.js SEO indexing.
version: 1.0.1
metadata:
  priority: 8
  docs:
    - "https://vercel.com/docs/functions"
    - "https://vercel.com/docs/functions/runtimes"
    - "https://vercel.com/docs/fluid-compute"
    - "https://vercel.com/docs/functions/streaming"
    - "https://vercel.com/docs/cron-jobs"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'api/**/*.*'
    - 'pages/api/**'
    - 'src/pages/api/**'
    - 'app/**/route.*'
    - 'src/app/**/route.*'
    - 'apps/*/api/**/*.*'
    - 'apps/*/app/**/route.*'
    - 'apps/*/src/app/**/route.*'
    - 'apps/*/pages/api/**'
    - 'vercel.json'
    - 'apps/*/vercel.json'
  bashPatterns:
    - '\bvercel\s+dev\b'
    - '\bvercel\s+logs\b'
---

# Vercel Functions

Expert guidance for the Vercel Functions compute layer — covering Serverless Functions (Node.js), Edge Functions (V8 Isolates), Fluid Compute, streaming, Cron Jobs, and runtime configuration.

## When to Use

Activate this skill when any of the following are true:

- You are creating or editing files under `api/**`, `pages/api/**`, `src/pages/api/**`, `app/**/route.*`, or `src/app/**/route.*`.
- You are editing `vercel.json` or any `apps/*/vercel.json`.
- You are running `vercel dev`, `vercel logs`, or debugging a deployment function.
- You see errors such as `FUNCTION_INVOCATION_FAILED`, `EDGE_FUNCTION_INVOCATION_TIMEOUT`, or `504 Gateway Timeout`.
- You need to choose between Node.js, Edge, Bun, or Rust runtimes.
- You are configuring Cron Jobs, streaming responses, or `waitUntil` / `after` background processing.

## Prerequisites

- **Vercel CLI** installed and authenticated:
  ```powershell
  npm i -g vercel
  vercel login
  ```
- **Node.js 24 LTS** is GA on Vercel for both builds and functions (V8 13.6, global `URLPattern`, Undici v7, npm v11).
- **Local env sync** before running `vercel dev`:
  ```powershell
  vercel env pull .env.local
  ```
  This pulls production/preview/development environment variables into `.env.local` for local development.
- **Windows host (PowerShell)** is the primary development environment. Use PowerShell-compatible commands throughout.

## Procedure

### 1. Choose the Right Runtime

| Need | Runtime | Why |
|------|---------|-----|
| Full Node.js APIs, npm packages | `nodejs` | Full compatibility |
| Lower latency, CPU-bound work | `nodejs` + Bun | ~28% latency reduction |
| Ultra-low latency, simple logic | `edge` | <1ms cold start, global |
| Database connections, heavy deps | `nodejs` | Edge lacks full Node.js |
| Auth/redirect at the edge | `edge` | Fastest response |
| AI streaming | Either | Both support streaming |
| Systems-level performance | `rust` (beta) | Native speed, Fluid Compute |

#### Serverless Functions (Node.js)

- Full Node.js runtime; all npm packages available.
- Default for Next.js API routes, Server Actions, Server Components.
- Cold starts: 800ms–2.5s (with DB connections).
- Max duration: 10s (Hobby legacy), 300s (Pro default), 800s (Fluid Compute Pro/Enterprise).

```ts
// app/api/hello/route.ts
export async function GET() {
  return Response.json({ message: 'Hello from Node.js' })
}
```

#### Edge Functions (V8 Isolates)

- Lightweight V8 runtime; Web Standard APIs only.
- Ultra-low cold starts (<1ms globally).
- Limited API surface — no `fs`, no native modules, limited `crypto`.
- **25s hard timeout limit** — not configurable.

```ts
// app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return new Response('Hello from the Edge')
}
```

#### Bun Runtime (Public Beta)

Add `"bunVersion": "1.x"` to `vercel.json` to run Node.js functions on Bun instead. ~28% lower latency for CPU-bound workloads. Supports Next.js, Express, Hono, Nitro.

```json
{
  "bunVersion": "1.x"
}
```

#### Rust Runtime (Public Beta)

Rust functions run on Fluid Compute with HTTP streaming and Active CPU pricing. Built on the community Rust runtime. Supports environment variables up to 64 KB.

### 2. Configure via vercel.json

**Deprecation notice**: Support for the legacy `now.json` config file will be removed on **March 31, 2026**. Rename `now.json` to `vercel.json` (no content changes required).

```json
{
  "functions": {
    "app/api/heavy/**": {
      "maxDuration": 300,
      "memory": 1024
    },
    "app/api/edge/**": {
      "runtime": "edge"
    }
  }
}
```

### 3. Understand Fluid Compute

Fluid Compute is the unified execution model for all Vercel Functions (both Node.js and Edge).

Key benefits:
- **Optimized concurrency**: Multiple invocations on a single instance — up to 85% cost reduction for high-concurrency workloads.
- **Extended durations**: Default 300s for all plans; up to 800s on Pro/Enterprise.
- **Active CPU pricing**: Charges only while CPU is actively working, not during idle/await time. Enabled by default for all plans. Memory-only periods billed at a significantly lower rate.
- **Background processing**: `waitUntil` / `after` for post-response tasks.
- **Dynamic scaling**: Automatic during traffic spikes.
- **Bytecode caching**: Reduces cold starts via Rust-based runtime with pre-compiled function code.
- **Multi-region failover**: Default for Enterprise when Fluid is activated.

#### Instance Sizes

| Size | CPU | Memory |
|------|-----|--------|
| Standard (default) | 1 vCPU | 2 GB |
| Performance | 2 vCPU | 4 GB |

Hobby projects use Standard CPU. The Basic CPU instance has been removed.

#### Timeout Limits

All plans now default to 300s execution time with Fluid Compute.

| Plan | Default | Max |
|------|---------|-----|
| Hobby | 300s | 300s |
| Pro | 300s | 800s |
| Enterprise | 300s | 800s |

### 4. Implement Background Processing

#### Using `waitUntil` (Vercel Functions)

```ts
import { waitUntil } from '@vercel/functions'

export async function POST(req: Request) {
  const data = await req.json()

  // Send response immediately
  const response = Response.json({ received: true })

  // Continue processing in background
  waitUntil(async () => {
    await processAnalytics(data)
    await sendNotification(data)
  })

  return response
}
```

#### Using `after` (Next.js equivalent)

```ts
import { after } from 'next/server'

export async function POST(req: Request) {
  const data = await req.json()

  after(async () => {
    await logToAnalytics(data)
  })

  return Response.json({ ok: true })
}
```

### 5. Implement Streaming

Zero-config streaming for both runtimes. Essential for AI applications.

```ts
export async function POST(req: Request) {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of data) {
        controller.enqueue(encoder.encode(chunk))
        await new Promise(r => setTimeout(r, 100))
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
}
```

For AI streaming, use the AI SDK's `toUIMessageStreamResponse()` (for chat UIs with `useChat`) which handles SSE formatting automatically.

### 6. Configure Cron Jobs

Schedule function invocations via `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/daily-report",
      "schedule": "0 8 * * *"
    },
    {
      "path": "/api/cleanup",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

The cron endpoint receives a normal HTTP request. Always verify it is from Vercel:

```ts
export async function GET(req: Request) {
  const authHeader = req.headers.get('authorization')
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 })
  }
  // Do scheduled work
  return Response.json({ ok: true })
}
```

### 7. Run Locally and Deploy

```powershell
# Pull environment variables for local dev
vercel env pull .env.local

# Run functions locally
vercel dev

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs for a deployment
vercel logs [deployment-url]
```

## Pitfalls

1. **Cold starts with DB connections**: Use connection pooling (e.g., Neon's `@neondatabase/serverless`). DB connections at module scope cause 800ms–2.5s cold starts.
2. **Edge limitations**: No `fs`, no native modules, limited `crypto`. Use Node.js runtime if you need full Node.js APIs.
3. **Edge Function timeout**: Hard 25s limit — not configurable. Move heavy computation to Node.js Serverless Functions. Use streaming to start response early and `waitUntil` for background work.
4. **Timeout exceeded on Node.js**: Use Fluid Compute for long-running tasks (up to 800s on Pro/Enterprise). For processes lasting hours/days, use Workflow DevKit (DurableAgent or workflow steps).
5. **Bundle size**: Python runtime supports up to 500MB; Node.js has smaller limits. Audit imports, use dynamic imports, tree-shake.
6. **Environment variables**: Available in all functions automatically. Use `vercel env pull` for local dev. Compare `.env.local` against Vercel dashboard settings when debugging.
7. **`FUNCTION_INVOCATION_FAILED`**: Usually memory exceeded (increase `memory` in `vercel.json`, up to 3008 MB on Pro) or crashed during init (check top-level await or heavy imports at module scope).
8. **Package in wrong section**: Verify the package is in `dependencies`, not `devDependencies` — production builds do not install devDependencies.
9. **Legacy `now.json`**: Support removed March 31, 2026. Rename to `vercel.json` with no content changes.
10. **Basic CPU instance removed**: Hobby projects use Standard CPU (1 vCPU, 2 GB). Do not reference Basic CPU in configurations.

## Verification

### Verify local dev server

```powershell
vercel dev
# Expected: Local dev server starts on http://localhost:3000
# Test endpoint:
curl http://localhost:3000/api/hello
```

### Verify environment variables are synced

```powershell
vercel env pull .env.local
# Expected: .env.local created/updated with all Vercel env vars
# Verify file exists:
Test-Path .env.local
# Expected: True
```

### Verify deployment and logs

```powershell
vercel --prod
# Expected: Production deployment URL returned

vercel logs [deployment-url]
# Expected: Real-time log stream; check for 500 errors or FUNCTION_INVOCATION_FAILED
```

### Verify runtime selection

Check that `export const runtime = 'edge'` is present in Edge Function files. For Node.js functions, no runtime export is needed (default).

### Verify cron authentication

```powershell
# Test cron endpoint without auth (should return 401):
curl https://your-deployment.vercel.app/api/daily-report
# Expected: 401 Unauthorized

# Test with correct secret:
curl -H "Authorization: Bearer YOUR_CRON_SECRET" https://your-deployment.vercel.app/api/daily-report
# Expected: 200 OK with JSON response
```

### Diagnostic Decision Trees

#### 504 Gateway Timeout

```
504 Gateway Timeout?
├─ All plans default to 300s with Fluid Compute
├─ Pro/Enterprise: configurable up to 800s
├─ Long-running task?
│  ├─ Under 5 min → Use Fluid Compute with streaming
│  ├─ Up to 15 min → Use Vercel Functions with `maxDuration` in vercel.json
│  └─ Hours/days → Use Workflow DevKit (DurableAgent or workflow steps)
└─ DB query slow? → Add connection pooling, check cold start, use Edge Config
```

#### 500 Internal Server Error

```
500 Internal Server Error?
├─ Check Vercel Runtime Logs (Dashboard → Deployments → Functions tab)
├─ Missing env vars? → Compare `.env.local` against Vercel dashboard settings
├─ Import error? → Verify package is in `dependencies`, not `devDependencies`
└─ Uncaught exception? → Wrap handler in try/catch, use `after()` for error reporting
```

#### FUNCTION_INVOCATION_FAILED

```
"FUNCTION_INVOCATION_FAILED"?
├─ Memory exceeded? → Increase `memory` in vercel.json (up to 3008 MB on Pro)
├─ Crashed during init? → Check top-level await or heavy imports at module scope
└─ Edge Function crash? → Check for Node.js APIs not available in Edge runtime
```

#### Cold Start Latency > 1s

```
Cold start latency > 1s?
├─ Using Node.js runtime? → Consider Edge Functions for latency-sensitive routes
├─ Large function bundle? → Audit imports, use dynamic imports, tree-shake
├─ DB connection in cold start? → Use connection pooling (Neon serverless driver)
└─ Enable Fluid Compute to reuse warm instances across requests
```

#### EDGE_FUNCTION_INVOCATION_TIMEOUT

```
"EDGE_FUNCTION_INVOCATION_TIMEOUT"?
├─ Edge Functions have 25s hard limit (not configurable)
├─ Move heavy computation to Node.js Serverless Functions
└─ Use streaming to start response early, process in background with `waitUntil`
```

## Related Skills

- **nextjs-app-router** — Next.js App Router route handlers and server actions
- **vercel-cron** — Cron job scheduling and management
- **ai-streaming** — AI SDK streaming patterns for chat UIs
