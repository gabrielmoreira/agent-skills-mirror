---
name: expo-api-routes
description: "Creates Expo Router server endpoints as +api.ts files on EAS Hosting for secrets, database calls, third-party proxies, webhooks, and rate limits. Use when the user needs API routes, server functions, or EAS Hosting in an Expo Router app. Not for public client-side fetch, realtime sockets, direct file uploads, or Convex/Firebase as the backend."
version: 1.0.1
risk: unknown
source: https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-api-routes
source_repo: expo/skills
source_type: official
date_added: 2026-07-01
license: MIT
license_source: https://github.com/expo/skills/blob/main/LICENSE
---

## When to Use

Use this skill when the task involves creating server-side endpoints in an Expo Router project via `+api.ts` files. Trigger keywords: "API route", "Expo API", "EAS Hosting", "server function", "backend endpoint", "webhook", "proxy API", "server-side secret".

Use API routes when you need:

- **Server-side secrets** — API keys, database credentials, or tokens that must never reach the client
- **Database operations** — Direct database queries that shouldn't be exposed
- **Third-party API proxies** — Hide API keys when calling external services (OpenAI, Stripe, etc.)
- **Server-side validation** — Validate data before database writes
- **Webhook endpoints** — Receive callbacks from services like Stripe or GitHub
- **Rate limiting** — Control access at the server level
- **Heavy computation** — Offload processing that would be slow on mobile

## When NOT to Use

Avoid API routes when:

- **Data is already public** — Use direct fetch to public APIs instead
- **No secrets required** — Static data or client-safe operations
- **Real-time updates needed** — Use WebSockets or services like Supabase Realtime
- **Simple CRUD** — Consider Firebase, Supabase, or Convex for managed backends
- **File uploads** — Use direct-to-storage uploads (S3 presigned URLs, Cloudflare R2)
- **Authentication only** — Use Clerk, Auth0, or Firebase Auth instead

## Prerequisites

- An Expo Router project with an `app/` directory
- Expo SDK with API route support
- For deployment: `eas-cli` installed and an Expo/EAS account

Install EAS CLI globally (Windows PowerShell):

```powershell
npm install -g eas-cli
eas login
```

## Procedure

### 1. Create the API route file

API routes live in the `app` directory with the `+api.ts` suffix. The file path maps to the URL path.

```
app/
  api/
    hello+api.ts          -> GET /api/hello
    users+api.ts          -> /api/users
    users/[id]+api.ts     -> /api/users/:id
  (tabs)/
    index.tsx
```

Create a basic route:

```ts
// app/api/hello+api.ts
export function GET(request: Request) {
  return Response.json({ message: "Hello from Expo!" });
}
```

### 2. Define HTTP methods

Export named functions for each HTTP method you want to support:

```ts
// app/api/items+api.ts
export function GET(request: Request) {
  return Response.json({ items: [] });
}

export async function POST(request: Request) {
  const body = await request.json();
  return Response.json({ created: body }, { status: 201 });
}

export async function PUT(request: Request) {
  const body = await request.json();
  return Response.json({ updated: body });
}

export async function DELETE(request: Request) {
  return new Response(null, { status: 204 });
}
```

### 3. Handle dynamic routes

```ts
// app/api/users/[id]+api.ts
export function GET(request: Request, { id }: { id: string }) {
  return Response.json({ userId: id });
}
```

### 4. Read query parameters

```ts
export function GET(request: Request) {
  const url = new URL(request.url);
  const page = url.searchParams.get("page") ?? "1";
  const limit = url.searchParams.get("limit") ?? "10";

  return Response.json({ page, limit });
}
```

### 5. Read headers and authorize

```ts
export function GET(request: Request) {
  const auth = request.headers.get("Authorization");

  if (!auth) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  return Response.json({ authenticated: true });
}
```

### 6. Parse JSON body

```ts
export async function POST(request: Request) {
  const { email, password } = await request.json();

  if (!email || !password) {
    return Response.json({ error: "Missing fields" }, { status: 400 });
  }

  return Response.json({ success: true });
}
```

### 7. Use environment variables for secrets

Use `process.env` for server-side secrets. NEVER expose API keys or secrets in client code.

```ts
// app/api/ai+api.ts
export async function POST(request: Request) {
  const { prompt } = await request.json();

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await response.json();
  return Response.json(data);
}
```

Set environment variables:

- **Local**: Create a `.env` file (never commit it)
- **EAS Hosting**: Use `eas env:create` or the Expo dashboard

```powershell
eas env:create --name OPENAI_API_KEY --value YOUR_KEY --environment production
```

### 8. Add CORS headers for web clients

```ts
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}

export function GET() {
  return Response.json({ data: "value" }, { headers: corsHeaders });
}
```

### 9. Handle errors gracefully

```ts
export async function POST(request: Request) {
  try {
    const body = await request.json();
    // Process...
    return Response.json({ success: true });
  } catch (error) {
    console.error("API error:", error);
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
```

### 10. Test locally

Start the development server with API route support:

```powershell
npx expo serve
```

This starts a local server at `http://localhost:8081` with full API route support.

Test with curl (PowerShell):

```powershell
curl http://localhost:8081/api/hello
curl -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{\"name\":\"Test\"}'
```

### 11. Deploy to EAS Hosting

```powershell
eas deploy
```

This builds and deploys your API routes to EAS Hosting (Cloudflare Workers).

Configure a custom domain in `eas.json` or the Expo dashboard.

### 12. Call API routes from the client

```ts
// From React Native components
const response = await fetch("/api/hello");
const data = await response.json();

// With body
const response = await fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "John" }),
});
```

## EAS Hosting Runtime (Cloudflare Workers)

API routes run on Cloudflare Workers. Respect these limitations:

### Missing/Limited APIs

- **No Node.js filesystem** — `fs` module unavailable
- **No native Node modules** — Use Web APIs or polyfills
- **Limited execution time** — 30 second timeout for CPU-intensive tasks
- **No persistent connections** — WebSockets require Durable Objects
- **fetch is available** — Use standard fetch for HTTP requests

### Use Web APIs instead of Node APIs

```ts
// Use Web Crypto instead of Node crypto
const hash = await crypto.subtle.digest(
  "SHA-256",
  new TextEncoder().encode("data")
);

// Use fetch instead of node-fetch
const response = await fetch("https://api.example.com");

// Use Response/Request (already available)
return new Response(JSON.stringify(data), {
  headers: { "Content-Type": "application/json" },
});
```

### Database options

Since the filesystem is unavailable, use cloud databases:

- **Cloudflare D1** — SQLite at the edge
- **Turso** — Distributed SQLite
- **PlanetScale** — Serverless MySQL
- **Supabase** — Postgres with REST API
- **Neon** — Serverless Postgres

Example with Turso:

```ts
// app/api/users+api.ts
import { createClient } from "@libsql/client/web";

const db = createClient({
  url: process.env.TURSO_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN!,
});

export async function GET() {
  const result = await db.execute("SELECT * FROM users");
  return Response.json(result.rows);
}
```

## Common Patterns

### Authentication middleware

```ts
// utils/auth.ts
export async function requireAuth(request: Request) {
  const token = request.headers.get("Authorization")?.replace("Bearer ", "");

  if (!token) {
    throw new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Verify token...
  return { userId: "123" };
}

// app/api/protected+api.ts
import { requireAuth } from "../../utils/auth";

export async function GET(request: Request) {
  const { userId } = await requireAuth(request);
  return Response.json({ userId });
}
```

### Proxy external API

```ts
// app/api/weather+api.ts
export async function GET(request: Request) {
  const url = new URL(request.url);
  const city = url.searchParams.get("city");

  const response = await fetch(
    `https://api.weather.com/v1/current?city=${city}&key=${process.env.WEATHER_API_KEY}`
  );

  return Response.json(await response.json());
}
```

## Pitfalls

- **NEVER expose API keys or secrets in client code.** Keep them in `process.env` and reference only inside `+api.ts` files.
- **No Node.js `fs` or native modules on EAS Hosting.** The runtime is Cloudflare Workers; use Web APIs (`fetch`, `crypto.subtle`, `Response`, `Request`).
- **30 second CPU timeout.** Long-running computations will be killed; offload or chunk them.
- **No persistent connections / WebSockets** without Durable Objects.
- **Always validate and sanitize user input.** Never trust request bodies or query params.
- **Use correct HTTP status codes**: 200, 201, 400, 401, 404, 500.
- **Wrap handlers in try/catch** and log errors server-side; never leak stack traces to clients.
- **One responsibility per endpoint.** Keep routes focused.
- **`.env` must never be committed.** Add it to `.gitignore`.
- **CORS is required for web clients.** Browser requests will fail without `Access-Control-Allow-Origin` and an `OPTIONS` handler.
- **File path maps to URL.** `app/api/users/[id]+api.ts` becomes `/api/users/:id`; misnamed files silently 404.
- **Use TypeScript for type safety** to catch request/response shape errors at build time.

## Verification

1. Confirm the dev server is running:

```powershell
npx expo serve
```

Expected: server starts at `http://localhost:8081`.

2. Verify a GET route responds:

```powershell
curl http://localhost:8081/api/hello
```

Expected: `{"message":"Hello from Expo!"}`

3. Verify a POST route accepts JSON:

```powershell
curl -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{\"name\":\"Test\"}'
```

Expected: JSON response with status `201`.

4. Verify environment variables are loaded (create a temporary debug route):

```ts
// app/api/debug-env+api.ts
export function GET() {
  return Response.json({ hasKey: !!process.env.OPENAI_API_KEY });
}
```

Expected: `{"hasKey":true}` when `.env` is present. Remove this route before deploying.

5. Verify deployment:

```powershell
eas deploy
```

Expected: build completes and a hosting URL is printed. Fetch `<deployed-url>/api/hello` to confirm.

6. Verify production secrets exist:

```powershell
eas env:list --environment production
```

Expected: `OPENAI_API_KEY` (and others) listed.

## Rules

- NEVER expose API keys or secrets in client code
- ALWAYS validate and sanitize user input
- Use proper HTTP status codes (200, 201, 400, 401, 404, 500)
- Handle errors gracefully with try/catch
- Keep API routes focused — one responsibility per endpoint
- Use TypeScript for type safety
- Log errors server-side for debugging

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
