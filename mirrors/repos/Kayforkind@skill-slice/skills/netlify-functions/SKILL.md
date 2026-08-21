---
name: netlify-functions
description: "Writes Netlify serverless functions with the default-export plus Config pattern (Web Request/Response): API paths, background (15 min), scheduled, and streaming handlers. Use when adding server-side logic beside a Netlify site without a framework adapter. Not for Astro/Next/Nuxt/SvelteKit/TanStack Start adapters that emit their own functions; never use the legacy exports.handler signature."
version: 1.0.1
---

# Netlify Functions

## Overview

Netlify Functions are serverless handlers deployed alongside your site. They use the modern **default export + `Config`** pattern, receive a standard Web API `Request`, and return a `Response`. This skill covers TypeScript syntax, path routing, method routing, background functions, scheduled functions, streaming, and the `Context` object.

> **Hard rule:** Always use the modern default export + `Config` pattern. Never use the legacy `exports.handler` or named `handler` export.

## When to Use

Use this skill when you need to:

- Create standalone API endpoints (e.g., `/api/items`, `/api/users/:id`)
- Add background processing (long-running tasks up to 15 minutes)
- Run scheduled/cron tasks
- Stream responses (SSE, large payloads up to 20 MB)
- Build server-side logic for client-side-only frameworks (Vite + React SPA, vanilla JS)
- Add background or scheduled tasks to any project
- Build standalone API endpoints outside a framework's routing

**Do NOT** use this skill when the project uses a framework with its own serverless adapter (Astro, Next.js, Nuxt, SvelteKit, TanStack Start). Those frameworks generate their own functions. See the **netlify-frameworks** skill for adapter setup.

## Prerequisites

- A Netlify site or local project linked to Netlify
- Node.js installed
- `@netlify/functions` package available (for TypeScript types)
- Netlify CLI (`netlify` command) for local dev and deployment (optional but recommended)

## Procedure

### 1. Create the function file

Place functions in `netlify/functions/`. Use `.ts` or `.mts` extensions.

```
netlify/functions/
  _shared/           # Non-function shared code (underscore prefix)
    auth.ts
    db.ts
  items.ts           # -> /.netlify/functions/items (or custom path via config)
  users/index.ts     # -> /.netlify/functions/users
```

> **Hard rule:** If both `.ts` and `.js` exist with the same name, the `.js` file takes precedence.

### 2. Write the handler using modern syntax

```typescript
import type { Context, Config } from "@netlify/functions";

export default async (req: Request, context: Context) => {
  return new Response("Hello, world!");
};

export const config: Config = {
  path: "/api/hello",
};
```

The handler receives a standard Web API `Request` and returns a `Response`. The second argument is a Netlify `Context` object.

### 3. Configure path routing

Define custom paths via the `config` export:

```typescript
export const config: Config = {
  path: "/api/items",                        // Static path
  // path: "/api/items/:id",                // Path parameter
  // path: ["/api/items", "/api/items/:id"], // Multiple paths
  // excludedPath: "/api/items/special",     // Excluded paths
  // preferStatic: true,                    // Don't override static files
};
```

> **Hard rule:** Without a `path` config, functions are available at `/.netlify/functions/{name}`. Setting a `path` makes the function available **only** at that path.

Access path parameters via `context.params`:

```typescript
// config: { path: "/api/items/:id" }
export default async (req: Request, context: Context) => {
  const { id } = context.params;
  // ...
};
```

### 4. Add method routing

```typescript
export default async (req: Request, context: Context) => {
  switch (req.method) {
    case "GET":    return handleGet(context.params.id);
    case "POST":   return handlePost(await req.json());
    case "DELETE": return handleDelete(context.params.id);
    default:       return new Response("Method not allowed", { status: 405 });
  }
};

export const config: Config = {
  path: "/api/items/:id",
  method: ["GET", "POST", "DELETE"],
};
```

### 5. Background functions (long-running tasks)

For long-running tasks (up to 15 minutes). The client receives an immediate `202` response; return values are ignored.

> **Hard rule:** Name the file with a `-background` suffix.

```
netlify/functions/process-background.ts
```

Store results externally (Netlify Blobs, database) for later retrieval.

### 6. Scheduled functions (cron)

Run on a cron schedule (UTC timezone):

```typescript
export default async (req: Request) => {
  const { next_run } = await req.json();
  console.log("Next invocation at:", next_run);
};

export const config: Config = {
  schedule: "@hourly", // or cron: "0 * * * *"
};
```

Shortcuts: `@yearly`, `@monthly`, `@weekly`, `@daily`, `@hourly`.

> **Hard rule:** Scheduled functions have a **30-second timeout** and only run on published deploys.

### 7. Streaming responses

Return a `ReadableStream` body for streamed responses (up to 20 MB):

```typescript
export default async (req: Request) => {
  const stream = new ReadableStream({ /* ... */ });
  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream" },
  });
};
```

### 8. Access environment variables

> **Hard rule:** Use `Netlify.env` (not `process.env`) inside functions.

```typescript
const apiKey = Netlify.env.get("API_KEY");
```

Use `YOUR_KEY` placeholders in examples — never commit live secrets.

### 9. Run locally

```powershell
netlify dev
```

This starts the local dev server and serves functions at `http://localhost:8888/.netlify/functions/{name}`.

### 10. Deploy

```powershell
netlify deploy --prod
```

## Context Object

| Property | Description |
|---|---|
| `context.params` | Path parameters from config |
| `context.geo` | `{ city, country: {code, name}, latitude, longitude, subdivision, timezone, postalCode }` |
| `context.ip` | Client IP address |
| `context.cookies` | `.get()`, `.set()`, `.delete()` |
| `context.deploy` | `{ context, id, published }` |
| `context.site` | `{ id, name, url }` |
| `context.account.id` | Team account ID |
| `context.requestId` | Unique request ID |
| `context.waitUntil(promise)` | Extend execution after response is sent |

## Resource Limits

| Resource | Limit |
|---|---|
| Synchronous timeout | 60 seconds |
| Background timeout | 15 minutes |
| Scheduled timeout | 30 seconds |
| Memory | 1024 MB |
| Buffered payload | 6 MB |
| Streamed payload | 20 MB |

## Pitfalls

- **Legacy export syntax:** Never use `exports.handler` or named `handler` export. Always use default export + `Config`.
- **`.js` precedence:** If both `.ts` and `.js` exist with the same name, the `.js` file takes precedence. Delete the stale `.js` or rename to avoid confusion.
- **Path config replaces default path:** Setting `path` makes the function available **only** at that path — the default `/.netlify/functions/{name}` route no longer works.
- **Scheduled functions only run on published deploys:** Draft/preview deploys will not trigger scheduled invocations.
- **Scheduled timeout is 30 seconds:** Do not run heavy work in scheduled functions; use a background function instead.
- **Background return values are ignored:** The client gets an immediate `202`. Store results in Netlify Blobs or a database.
- **Use `Netlify.env`, not `process.env`:** `process.env` may not populate correctly in the functions runtime.
- **Framework conflicts:** Frameworks with adapters (Astro, Next.js, Nuxt, SvelteKit, TanStack Start) generate their own functions. Writing raw Netlify Functions alongside them can cause routing conflicts. See the **netlify-frameworks** skill.
- **Shared code must use underscore prefix:** Files/folders starting with `_` (e.g., `_shared/`) are not deployed as functions.
- **UTC timezone for cron:** Scheduled functions run in UTC. Adjust expressions accordingly.

## Verification

1. **Check function file location and naming:**

```powershell
Get-ChildItem -Recurse netlify\functions -Filter *.ts
```

Confirm files are under `netlify/functions/` and background functions use the `-background` suffix.

2. **Run locally and hit the endpoint:**

```powershell
netlify dev
```

Then in another terminal:

```powershell
Invoke-RestMethod -Uri "http://localhost:8888/api/hello" -Method Get
```

Expected: `Hello, world!` (or your handler's response).

3. **Verify config export is present:**

Each function file should export `config: Config` with a `path`, `schedule`, or background suffix.

4. **Verify environment variable access uses `Netlify.env`:**

```powershell
Select-String -Path "netlify\functions\*.ts" -Pattern "process\.env"
```

Expected: no matches. All env access should use `Netlify.env.get(...)`.

5. **Verify no legacy exports:**

```powershell
Select-String -Path "netlify\functions\*.ts" -Pattern "exports\.handler"
```

Expected: no matches.

6. **Deploy and verify live:**

```powershell
netlify deploy --prod
Invoke-RestMethod -Uri "https://YOUR_SITE.netlify.app/api/hello" -Method Get
```

## Related skills

- **netlify-frameworks** — adapter setup for Astro, Next.js, Nuxt, SvelteKit, TanStack Start
