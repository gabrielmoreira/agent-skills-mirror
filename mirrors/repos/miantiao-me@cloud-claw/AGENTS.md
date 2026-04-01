# Agent Development Guidelines

Development guidelines for AI coding agents working on Cloud Claw.

## Project Overview

Cloud Claw is a TypeScript project running on Cloudflare Workers + Containers. It uses Durable Objects with `@cloudflare/containers` to manage containerized AI assistant workloads.A Worker handles routing/auth, forwards requests to a singleton container running an OpenClaw gateway instance, and proxies Chrome DevTools Protocol (CDP) sessions via Cloudflare Browser bindings.

**Tech Stack:** Cloudflare Workers, TypeScript (ES2024), pnpm (v10.28.2)

## Commands

```bash
pnpm install          # Install dependencies
pnpm dev              # Start local dev server (binds 0.0.0.0)
pnpm deploy           # Deploy to Cloudflare
pnpm lint             # Run formatter (oxfmt) + linter (oxlint)
pnpm cf-typegen       # Regenerate Cloudflare type definitions
npx oxfmt             # Format only
npx oxlint            # Lint only
```

**No test suite configured.** Validate changes with `pnpm lint` and `pnpm dev`.

## Project Structure

```
src/
├── index.ts          # Workers entry point (ExportedHandler), routing, basic auth
├── container.ts      # AgentContainer class (extends Container), WebSocket gateway
└── cdp.ts            # Chrome DevTools Protocol proxy (chunked binary WebSocket framing)

wrangler.jsonc        # Wrangler config (containers, bindings, placement)
tsconfig.json         # TypeScript config (ES2024, strict, bundler resolution)
Dockerfile            # Container image: OpenClaw gateway + TigrisFS S3 mount
worker-configuration.d.ts  # Auto-generated Cloudflare bindings (DO NOT EDIT)
.oxfmtrc.json         # Formatter config (single quotes, no semicolons, spaces)
```

## Code Style

### Formatting (oxfmt — `.oxfmtrc.json`)

- **Single quotes**, **no semicolons**, **spaces for indentation** (oxfmt overrides `.editorconfig`)
- **LF line endings**, always insert **final newline**
- Run `pnpm lint` before committing

### TypeScript

- **Target**: ES2024, **Module**: ES2022, **Resolution**: Bundler
- **Strict mode**: Enabled — **No emit** (Wrangler bundles)

### Imports

```typescript
// 1. Cloudflare imports first
import { env } from 'cloudflare:workers'
import { Container } from '@cloudflare/containers'
// 2. Local imports
import { proxyCdp } from './cdp'
// 3. Re-exports from index.ts
export { AgentContainer } from './container'
```

Use **named imports**; avoid default exports except the main handler.

### Naming Conventions

| Element    | Convention       | Example                    |
| ---------- | ---------------- | -------------------------- |
| Files      | kebab-case       | `my-file.ts`               |
| Classes    | PascalCase       | `AgentContainer`           |
| Functions  | camelCase        | `handleFetch`              |
| Constants  | camelCase/UPPER  | `PORT`, `textEncoder`      |
| Env vars   | UPPER_SNAKE_CASE | `SERVER_PASSWORD`          |
| Interfaces | PascalCase       | `ContainerConfig` (no `I`) |

### Type Patterns

```typescript
const value = env.MY_VAR  // typed as Cloudflare.Env
export default { fetch: handleFetch } satisfies ExportedHandler<Cloudflare.Env>
async function handleFetch(request: Request): Promise<Response> { ... }
```

### Error Handling

```typescript
// HTTP errors — return Response, no exceptions
return new Response('Unauthorized', { status: 401 })

// Guard clauses with early returns
const authError = verifyBasicAuth(request)
if (authError) return authError

// Logging: console.error (errors), console.warn (warnings), console.info (info)
// Bare catch for non-critical errors: try { JSON.parse(data) } catch {}
// Reconnection: setTimeout(() => this.watchContainer(), 30_000)
```

### Cloudflare Patterns

```typescript
// Durable Object Container
export class AgentContainer extends Container {
  sleepAfter = '10m'
  defaultPort = 6658
  envVars = { ... }
  override async onStart(): Promise<void> { ... }
}

// Singleton pattern
const id = env.AGENT_CONTAINER.idFromName('cf-singleton-container')
const container = env.AGENT_CONTAINER.get(id, { locationHint: 'wnam' })

// WebSocket from container
const res = await this.containerFetch(url, { headers: { Upgrade: 'websocket' } })
res.webSocket.accept()

// Browser binding (CDP proxy)
const res = await browser.fetch('http://cloudflare.browser/v1/acquire')
```

## Environment Variables

| Variable                 | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| `SERVER_USERNAME`        | Basic auth username                         |
| `SERVER_PASSWORD`        | Basic auth password (empty = auth disabled) |
| `OPENCLAW_GATEWAY_TOKEN` | Gateway access token                        |
| `WORKER_URL`             | Worker's public URL (for CDP proxy config)  |
| `S3_ENDPOINT`            | S3-compatible storage endpoint              |
| `S3_BUCKET`              | S3 bucket name                              |
| `S3_ACCESS_KEY_ID`       | S3 access key                               |
| `S3_SECRET_ACCESS_KEY`   | S3 secret key                               |
| `S3_PREFIX`              | S3 key prefix (optional)                    |

**Bindings** (in `wrangler.jsonc`):

| Binding           | Type           | Purpose                        |
| ----------------- | -------------- | ------------------------------ |
| `AGENT_CONTAINER` | Durable Object | Container lifecycle management |
| `BROWSER`         | Browser remote | Cloudflare Browser Rendering   |

## Language Requirements

**All code content MUST be in English:** commit messages, comments, logs, variable names.

## Best Practices

1. **Keep handlers thin** — Delegate to focused functions
2. **Use early returns** — For auth and validation checks
3. **Avoid over-engineering** — Simple, readable code; small focused project
4. **Comments explain why** — Not what the code does
5. **Regenerate types** — Run `pnpm cf-typegen` after changing `wrangler.jsonc` bindings
6. **Numeric separators** — Use `30_000` not `30000`
7. **No unused code** — oxlint will catch it

## Common Tasks

**Adding an env variable:** Update `wrangler.jsonc` → `pnpm cf-typegen` → Use via `env.NEW_VAR`

**Container behavior:** Edit `src/container.ts` — properties: `sleepAfter`, `defaultPort`, `envVars`; method: `onStart()`

**Request routing:** Edit `src/index.ts` — `handleFetch()` dispatches by URL pattern

**CDP proxy:** Edit `src/cdp.ts` — chunked binary WebSocket framing between client and Browser binding

**Handler pattern:** `export default { fetch: handleFetch } satisfies ExportedHandler<Cloudflare.Env>`
