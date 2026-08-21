---
name: neon-functions
description: "Deploys long-running Node.js 24 HTTP functions onto a Neon branch via neon.ts slugs and neon deploy, with DATABASE_URL injected beside Postgres. Use when hosting an API, SSE/WebSocket server, or streaming agent that must outlast lambda timeouts in us-east-2. Do not use for static hosting, scheduled background workers, or compute outside the us-east-2 preview."
version: 1.0.1
---

# Neon Functions

Neon Functions are long-running Node.js HTTP handlers deployed onto a Neon branch. Each function gets a public HTTPS URL, runs in the same region as your database (`us-east-2`), and — if the branch has Postgres — gets `DATABASE_URL` injected automatically. Deploy and manage them through the same Neon CLI, `neon.ts`, and API you already use.

> **Preview feature.** Only available on **new** projects in **`us-east-2`**. Cannot be enabled on existing projects. Usage is not billed during the private preview. If the user lacks access, point them to: https://neon.com/blog/were-building-backends#access

## When to Use

Reach for Neon Functions when the workload is a request/response handler that benefits from staying alive and staying close to the data:

- **Long-running request/response flows** that outlast lambda-style limits (~10–60s). Agents making multiple LLM calls, image/video generation, etc. The handler must _start_ responding within 15 minutes; an open stream stays alive as long as bytes keep flowing.
- **Stateful streaming** — SSE endpoints or WebSocket servers held open in-process. No external state store (Redis) needed. Module-scope state (a `pg` pool, in-memory counter) persists across requests on the same isolate.
- **Compute next to Postgres** — runs in the branch's region; no cross-region round trips. `DATABASE_URL` injected for you.
- **A backend that branches with your data** — each branch runs its own function version at its own URL against its own isolated database. Preview deployments, CI, and dev environments each get a self-contained backend.
- **Webhooks, bots, post-response work** — fan-out DB writes, Discord/WebSocket bots, fire-and-forget follow-ups via `waitUntil`.

**Do NOT use when:** the workload is a pure static site, a cron/background job needing its own lifecycle and cancellation, or anything that must run outside `us-east-2` today.

## Prerequisites

- A **new** Neon project in **`us-east-2`** (Functions cannot be enabled on existing projects).
- Neon CLI installed and authenticated (`neon` command available).
- Node.js 24 runtime (Functions run on Node.js 24; memory fixed at 2048 MiB during preview).
- `@neon/config` package for `neon.ts` infrastructure-as-code.
- For Postgres-connected functions: the branch must have Postgres enabled (otherwise `DATABASE_URL` is not injected).

## Procedure

### 1. Declare functions in `neon.ts`

Add `@neon/config` and declare functions under `preview.functions`, keyed by **slug**:

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  preview: {
    functions: {
      todos: {
        // slug: ^[a-z0-9]{1,20}$ — lowercase letters/digits, no hyphens
        name: "todo api", // display label only
        source: "src/index.ts", // entry file, relative to neon.ts
      },
    },
  },
});
```

**HARD RULE:** The slug is the function's permanent identity (appears in the invocation URL and CLI commands) and **cannot be changed** after the first deploy. Use `name` for a human-readable label. Slugs must match `^[a-z0-9]{1,20}$`.

### 2. Write the function handler

A function is any default export with a `fetch(request)` method returning a `Response` (Workers/WinterTC-compatible). A Hono app exports exactly that shape, so `export default app` just works.

Minimal example — Hono app querying Postgres via injected `DATABASE_URL`:

```typescript
// src/index.ts
import { Hono } from "hono";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { parseEnv } from "@neon/env";
import config from "../neon";
import { todos } from "./db/schema";

const env = parseEnv(config);
const pool = new Pool({ connectionString: env.postgres.databaseUrl, max: 5 });
const db = drizzle(pool);

const app = new Hono();
app.get("/", (c) => c.text("Neon + Hono + Drizzle"));
app.post("/todos", async (c) => {
  const { text } = await c.req.json<{ text: string }>();
  const [row] = await db.insert(todos).values({ text }).returning();
  return c.json(row, 201);
});
app.get("/todos", async (c) => c.json(await db.select().from(todos)));

export default app;
```

**HARD RULE:** Create the `pg` pool **once at module scope** and reuse it across requests. Do NOT open a connection per request. Keep `max` small (e.g. `5`) — each isolate keeps its own pool, so total connections scale with the number of live isolates.

**HARD RULE:** Use Drizzle (or another ORM) on top of `node-postgres` (`pg`) — **not** Neon's serverless driver. Functions are long-running and reuse an isolate across many requests, so a persistent `pg` pool is the right fit.

To scope `parseEnv` to only the keys you need:

```typescript
const { postgres } = parseEnv(config, ["DATABASE_URL"]);
const pool = new Pool({ connectionString: postgres.databaseUrl, max: 5 });
```

Reading `process.env.DATABASE_URL` directly also works everywhere.

### 3. Develop locally

```bash
neon dev      # serves every function in neon.ts with hot reload; injects DATABASE_URL & friends
```

`neon dev` injects `NEON_BRANCH`, `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and other Neon-managed vars into your local dev environment so local runs mirror the deployed runtime.

### 4. Deploy

```bash
neon deploy   # bundles with esbuild, uploads, and applies neon.ts to the linked branch
```

Deploy a single function without `neon.ts`:

```bash
neon functions deploy <slug> --path . --entry src/index.ts
```

Retrieve the public URL:

```bash
neon functions get <slug>
# Look for the invocation_url field:
# https://<branch_id>-<slug>.compute.c-1.us-east-2.aws.neon.tech
```

Manage functions:

```bash
neon functions list
neon functions get <slug>
neon functions delete <slug>
```

### 5. Infrastructure-as-code with `neon.ts`

```bash
neon config status   # print the branch's live config (deployed functions)
neon config plan     # dry-run diff of what apply would change
neon config apply    # bundle + deploy the declared functions (neon deploy is an alias)
```

**HARD RULE:** Functions are **branch-scoped**. When `neon.ts` is present, `neon checkout` applies the policy as it _creates_ a branch. Checking out an _existing_ branch does **not** re-deploy — run `neon deploy` explicitly.

Per-branch deploy tuning (e.g. `runtime`) lives in the `branch` closure:

```typescript
export default defineConfig({
  preview: {
    functions: { todos: { name: "todo api", source: "src/index.ts" } },
  },
  branch: (branch) => ({
    preview: { functions: { todos: { runtime: "nodejs24" } } },
  }),
});
```

### 6. Environment variables

**Neon-injected (automatic, do not declare or pass at deploy time):**

| Variable | Notes |
|---|---|
| `NEON_BRANCH` | Branch name (e.g. `main`, `preview/foo`). Injected on every branch. |
| `DATABASE_URL` | Pooled connection string. Use for most queries. Present only if branch has Postgres. |
| `DATABASE_URL_UNPOOLED` | Direct connection. Use for migrations, `LISTEN`/`NOTIFY`, multi-round-trip transactions. |
| `NEON_AUTH_BASE_URL` | Present when Neon Auth is enabled. |
| `NEON_DATA_API_URL` | Present when Data API is enabled. |

Object storage (`AWS_*`) and AI Gateway (`OPENAI_*`, `NEON_AI_GATEWAY_*`) vars are also injected when those services are declared.

**Your own secrets** — set with `--env KEY=VALUE` on deploy (repeatable; `--env KEY=` deletes a key; unmentioned keys carry over), or declare in `neon.ts`:

```typescript
functions: {
  todos: {
    name: "todo api",
    source: "src/index.ts",
    env: { OPENAI_API_KEY: process.env.OPENAI_API_KEY! },
  },
}
```

Load a `.env` before deploy: `neon deploy --env .env.production`

Pull branch vars for local dev: `neon env pull` (`link`/`checkout` do this automatically; pass `--no-env-pull` to skip).

**HARD RULE — Env limits:** ≤1,000 vars, ≤64 KiB total, and the `NEON_` prefix is reserved.

### 7. Connecting to Postgres

- `DATABASE_URL` — **pooled** (through Neon's connection pooler). Use for normal request/response traffic. Every Postgres ORM reads `DATABASE_URL` by default.
- `DATABASE_URL_UNPOOLED` — **direct**. Use for migrations, `LISTEN`/`NOTIFY`, long multi-statement transactions.

```typescript
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
const db = drizzle(pool);
```

You do NOT need to close the pool on shutdown — when the runtime evicts an isolate it sends `SIGINT`/`SIGTERM`, and Neon's pooler reclaims connections automatically.

### 8. WebSocket servers

A function's default export is normally `{ fetch }`. To accept WebSockets, export an `upgrade` method alongside it — the runtime routes plain HTTP to `fetch` and the WebSocket handshake to `upgrade`:

```typescript
export default {
  fetch(request: Request): Response | Promise<Response> { /* HTTP */ },
  async upgrade(req: IncomingMessage, socket: Duplex, head: Buffer) { /* WS handshake */ },
};
```

Simple example with `ws` library and token auth:

```typescript
// src/index.ts
import type { IncomingMessage } from "node:http";
import type { Duplex } from "node:stream";
import { WebSocketServer, type WebSocket } from "ws";

const clients = new Set<WebSocket>();
const wss = new WebSocketServer({ noServer: true });

export default {
  fetch: () => new Response("WebSocket endpoint — connect with ?token=<jwt>"),
  async upgrade(req: IncomingMessage, socket: Duplex, head: Buffer) {
    const url = new URL(req.url ?? "/", "http://localhost");
    const identity = await verifyToken(url.searchParams.get("token"));
    if (!identity) {
      socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
      socket.destroy();
      return;
    }
    wss.handleUpgrade(req, socket, head, (ws) => {
      clients.add(ws);
      ws.on("close", () => clients.delete(ws));
      ws.on("message", (data) => broadcast(data.toString()));
    });
  },
};
```

**HARD RULE — Heartbeat:** A connection stays open only while bytes flow. Neon evicts a silent stream after 15 minutes, and intermediary proxies are often stricter (tens of seconds). Send a periodic ping:

```typescript
const HEARTBEAT_MS = 25_000;

const beat = setInterval(() => {
  for (const ws of clients) if (ws.readyState === ws.OPEN) ws.ping();
}, HEARTBEAT_MS);
beat.unref?.();
```

**HARD RULE — Fan-out across isolates:** Under load, the runtime runs several isolates in parallel, each with its own copy of module state. An in-memory `Set<WebSocket>` only covers the current isolate. For true fan-out (broadcasting to all clients across all isolates), use Postgres `LISTEN`/`NOTIFY` or a shared pub/sub layer. Do NOT skip this if you need broadcast semantics.

**HARD RULE — Client must reconnect:** The platform may evict/restart for operational reasons (maintenance, moving compute). Treat eviction like a process restart — WebSocket/SSE clients must reconnect. The platform sends `SIGINT` before evicting.

**HARD RULE — No header-modifying middleware on `upgradeWebSocket` routes:** CORS or similar middleware that rewrites headers will throw when combined with Hono's `upgradeWebSocket()` helper.

**When to load reference files:**
- **`references/hono-websockets.md`** — Load when the user wants to declare WebSocket routes _inside_ a Hono app using `app.get("/ws", upgradeWebSocket(...))` with `onOpen`/`onMessage`/`onClose` lifecycle. Contains a self-contained `createNeonWebSocket(app)` adapter (depends only on `hono` and `ws`; no deprecated `@hono/node-ws` package).

### 9. Server-sent events (SSE)

SSE works naturally — return a `Response` with `Content-Type: text/event-stream` and keep writing chunks. The stream stays alive as long as bytes flow (15-minute heartbeat applies).

### 10. Functions as an agent backend

**HARD RULE — Never proxy a long agent stream through your app backend.** Platforms like Vercel/Netlify/Cloudflare cap serverless/edge execution at ~10–60s (sometimes up to ~300s). A long agent stream gets cut off mid-response even though the Neon Function would keep going.

```
Browser ──(Authorization: Bearer <JWT>)──▶  Neon Function (agent)   ✅ no host timeout
Browser ──▶ your app backend ──▶ Neon Function                       ❌ host cuts the stream
```

**HARD RULE — A Neon Function has a public HTTPS URL reachable by anyone.** A direct client→function call means no app backend gates access. You **must** authenticate the function yourself: verify a JWT (against your app's JWKS), check a shared secret/API key, or validate a session token at the top of the handler. **Never deploy an unauthenticated agent.**

```typescript
// src/index.ts — verify the caller before doing any work
import { createRemoteJWKSet, jwtVerify } from "jose";

const jwks = createRemoteJWKSet(new URL(`${process.env.AUTH_BASE_URL}/api/auth/jwks`));

export default {
  async fetch(request: Request) {
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(request) });

    const auth = request.headers.get("authorization");
    if (!auth?.toLowerCase().startsWith("bearer ")) {
      return new Response("Unauthorized", { status: 401, headers: cors(request) });
    }
    try {
      const { payload } = await jwtVerify(auth.slice(7), jwks, {
        issuer: process.env.AUTH_BASE_URL,
        audience: process.env.AUTH_BASE_URL,
      });
      const userId = payload.sub; // scope the agent to this user
      // ... run the agent, return result.toUIMessageStreamResponse({ headers: cors(request) })
    } catch {
      return new Response("Unauthorized", { status: 401, headers: cors(request) });
    }
  },
};
```

**When to load reference files:**
- **`references/ai-sdk.md`** — Load when the user wants a complete Vercel AI SDK agent running as a Function (streaming `toUIMessageStreamResponse`, multi-step tool calling next to Postgres, persisting generated images to Object Storage).
- **`references/mastra-studio.md`** — Load when the user wants to run a Mastra agent on a function and ship traces to Mastra Studio (Mastra Cloud) for observability.
- **`references/sentry.md`** — Load when the user needs error monitoring/observability for a long-running function.

## Pitfalls

1. **Slug is permanent.** The slug appears in the invocation URL and CLI commands and cannot be changed after the first deploy. Choose carefully. Must match `^[a-z0-9]{1,20}$` — lowercase letters/digits only, no hyphens.

2. **Opening a DB connection per request.** This exhausts Postgres connections under load. Create the `pg` pool once at module scope with `max: 5` and reuse it.

3. **Using Neon's serverless driver instead of `pg`.** Functions are long-running and reuse isolates — a persistent `pg` pool is the correct choice, not the HTTP-based serverless driver.

4. **No heartbeat on WebSocket/SSE.** Silent streams are evicted after 15 minutes (proxies often sooner, tens of seconds). Send a ping every ~25 seconds.

5. **Assuming module state is shared across isolates.** Under load, multiple isolates run in parallel, each with its own copy of module state. In-memory data structures (like a `Set<WebSocket>`) are per-isolate. Persist anything that must survive eviction or be shared in Postgres.

6. **Proxying agent streams through the app backend.** Host platforms cut the stream at their serverless limits. Call the Neon Function directly from the client with a short-lived JWT.

7. **Deploying an unauthenticated function.** The public HTTPS URL is reachable by anyone. Always verify a JWT/API key/session token at the top of the handler.

8. **Forgetting CORS for direct client→function calls.** Handle `OPTIONS` preflight and set `Access-Control-Allow-Origin`/`-Headers` so the browser can reach the function cross-origin.

9. **Expecting `neon checkout` to redeploy on existing branches.** It only applies the policy when _creating_ a branch. Run `neon deploy` explicitly after checking out an existing branch.

10. **Using `NEON_` prefix for your own env vars.** This prefix is reserved. Also respect limits: ≤1,000 vars, ≤64 KiB total.

11. **Putting CORS/header-modifying middleware on `upgradeWebSocket` routes.** The helper rewrites headers internally and will throw.

12. **Not treating eviction as a process restart.** The platform may evict/restart for operational reasons. WebSocket/SSE clients must reconnect. Use `process.on("SIGINT", ...)` for last-minute cleanup if needed (not needed for closing Postgres connections — the pooler reclaims those).

## Verification

1. **Check function is deployed and get its URL:**
   ```bash
   neon functions get <slug>
   ```
   Expected output includes `invocation_url` of the form:
   ```
   https://<branch_id>-<slug>.compute.c-1.us-east-2.aws.neon.tech
   ```

2. **List all deployed functions:**
   ```bash
   neon functions list
   ```

3. **Check live config matches `neon.ts`:**
   ```bash
   neon config status
   ```

4. **Dry-run a deploy to see what would change:**
   ```bash
   neon config plan
   ```

5. **Test the function endpoint:**
   ```bash
   curl -s https://<branch_id>-<slug>.compute.c-1.us-east-2.aws.neon.tech/
   ```
   Expected: `Neon + Hono + Drizzle` (or your handler's response).

6. **Verify local dev serves the function:**
   ```bash
   neon dev
   # Then curl the local URL printed in the output
   ```

7. **Verify against official docs** (source of truth, Functions is evolving rapidly):
   - Docs index: https://neon.com/docs/llms.txt
   - Overview: https://neon.com/docs/compute/functions/overview.md
   - Get started: https://neon.com/docs/compute/functions/get-started.md
   - Deploy: https://neon.com/docs/compute/functions/deploy.md
   - Environment variables: https://neon.com/docs/compute/functions/environment-variables.md
   - `neon.ts` reference: https://neon.com/docs/compute/functions/reference/neon-ts.md
   - Runtime limits: https://neon.com/docs/compute/functions/reference/runtime-limits.md
   - Preview access: https://neon.com/docs/compute/functions/preview-access.md

   Any doc page can be fetched as markdown by appending `.md` to the URL or requesting `Accept: text/markdown`.

## Timeouts and Runtime Limits

| Limit | Value |
|---|---|
| Time to first byte | 15 minutes (handler must begin responding) |
| Heartbeat (WebSocket/SSE) | 15 minutes (must send at least one byte to keep a quiet stream alive) |
| `waitUntil` | 15 minutes (for cleanup like analytics/audit logs, NOT a background job runner; currently a stub during preview) |
| Runtime | Node.js 24 |
| Memory | 2048 MiB (fixed during preview) |
| Slug pattern | `^[a-z0-9]{1,20}$` |
| Env vars | ≤1,000 vars, ≤64 KiB total, `NEON_` prefix reserved |
| Region | `us-east-2` only (preview) |

An isolate is reused across many requests — multiple requests can be in flight on the same isolate at once (interleaved on Node's single-threaded event loop). Under load, several isolates run in parallel, each with its own copy of module state. State held in module scope is per-isolate and in-memory only.

## Related skills

- **`neon`** — Branch-first workflow and `neon.ts` basics.
- **`neon-object-storage`** — Object storage service (`AWS_*` env vars injected when declared).
- **`neon-ai-gateway`** — AI Gateway service (`OPENAI_*`, `NEON_AI_GATEWAY_*` env vars; one credential across every model).
