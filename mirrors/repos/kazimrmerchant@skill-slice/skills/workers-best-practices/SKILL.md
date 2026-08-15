---
name: workers-best-practices
description: "Reviews and authors Cloudflare Workers against current best practices (streaming, floating promises, global state, secrets, wrangler.jsonc, bindings). Use when writing or reviewing Workers or wrangler config. Not for Durable Objects details (durable-objects), Wrangler CLI reference (wrangler), or Cloudflare Workflows rules."
version: 1.0.1
---

Your knowledge of Cloudflare Workers APIs, types, and configuration may be outdated. **Prefer retrieval over pre-training** for any Workers code task — writing or reviewing.

## When to Use

Load this skill when:
- Writing new Cloudflare Workers code or scaffolding a new Worker project
- Reviewing existing Worker code in a PR, audit, or refactor
- Configuring `wrangler.jsonc` / `wrangler.toml` — bindings, compatibility flags, observability
- Diagnosing common Workers anti-patterns: floating promises, global mutable state, unbounded `await response.text()`, hardcoded secrets, REST API calls from inside a Worker
- Checking binding access patterns in platform base classes (`DurableObject`, `WorkerEntrypoint`, `Workflow`)

Do **not** load this skill for:
- Durable Objects specifics — load the `durable-objects` skill instead
- Wrangler CLI command reference — load the `wrangler` skill
- Workflows rules — see [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)

## Prerequisites

- Node.js and npm installed on the host
- `wrangler` available locally (`node_modules/.bin/wrangler`) or globally
- PowerShell as the primary shell on Windows host
- Internet access for fetching Cloudflare docs and `npm pack`

## Procedure

### Step 1 — Fetch Latest References Before Writing or Reviewing

Before reviewing or writing Workers code, retrieve the current best practices page and relevant type definitions. If the project's `node_modules` has an older version, **prefer the latest published version**.

**Fetch the canonical best practices page:**

```powershell
# Fetch the Workers best practices page
Invoke-WebRequest -Uri "https://developers.cloudflare.com/workers/best-practices/workers-best-practices/" -OutFile "$env:TEMP\workers-best-practices.html"
```

**Fetch the latest `@cloudflare/workers-types` package:**

```powershell
# Create temp dir and fetch latest workers types
New-Item -ItemType Directory -Force -Path "$env:TEMP\workers-types-latest"
npm pack @cloudflare/workers-types --pack-destination "$env:TEMP\workers-types-latest"
# Extract the tarball
$tarball = Get-ChildItem "$env:TEMP\workers-types-latest\cloudflare-workers-types-*.tgz" | Select-Object -First 1
tar -xzf $tarball.FullName -C "$env:TEMP\workers-types-latest"
# Types at $env:TEMP\workers-types-latest\package\index.d.ts
```

**Check the local wrangler config schema:**

```powershell
# If wrangler is installed locally, the schema is available at:
# node_modules\wrangler\config-schema.json
# Use it to validate config fields, binding shapes, and allowed values
Test-Path "node_modules\wrangler\config-schema.json"
```

### Step 2 — Load Reference Files

Load these reference files at the right time during review:

| Reference file | When to load |
|---------------|--------------|
| `references/rules.md` | Before flagging any anti-pattern — contains all best practice rules with correct code examples and anti-pattern side-by-side |
| `references/review.md` | During type validation and config validation steps — contains type validation steps, config validation, binding access patterns, and the full review process |

### Step 3 — Retrieve Latest Docs for Any Uncertain API

If unsure about an API signature, config field, or binding shape, fetch the docs first:

```powershell
# Search Cloudflare Workers docs
Invoke-WebRequest -Uri "https://developers.cloudflare.com/workers/" -UseBasicParsing
```

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Workers best practices | Fetch `https://developers.cloudflare.com/workers/best-practices/workers-best-practices/` | Canonical rules, patterns, anti-patterns |
| Workers types | See `references/review.md` for retrieval steps | API signatures, handler types, binding types |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` | Config fields, binding shapes, allowed values |
| Cloudflare docs | Search tool or `https://developers.cloudflare.com/workers/` | API reference, compatibility dates/flags |

### Step 4 — Review Workflow

Follow this ordered process for every Workers code review:

1. **Retrieve** — fetch latest best practices page, workers types, and wrangler schema (Step 1 above)
2. **Read full files** — not just diffs; context matters for binding access patterns
3. **Check types** — binding access, handler signatures, no `any`, no unsafe casts (see `references/review.md`)
4. **Check config** — `compatibility_date`, `nodejs_compat`, `observability`, secrets, binding-code consistency
5. **Check patterns** — streaming, floating promises, global state, serialization boundaries
6. **Check security** — crypto usage, secret handling, timing-safe comparisons, error handling
7. **Validate with tools** — `npx tsc --noEmit`, lint for `no-floating-promises`
8. **Reference rules** — see `references/rules.md` for each rule's correct pattern

### Step 5 — Apply Configuration Rules

| Rule | Summary | How to verify |
|------|---------|---------------|
| Compatibility date | Set `compatibility_date` to today on new projects; update periodically on existing ones | Check `wrangler.jsonc` for `compatibility_date` field |
| nodejs_compat | Enable the `nodejs_compat` flag — many libraries depend on Node.js built-ins | Check `compatibility_flags` array in config |
| wrangler types | Run `wrangler types` to generate `Env` — never hand-write binding interfaces | Run `npx wrangler types` and check for generated `worker-configuration.d.ts` |
| Secrets | Use `wrangler secret put`, never hardcode secrets in config or source | Search source for `YOUR_KEY`-style literals; check for `wrangler secret` usage |
| wrangler.jsonc | Use JSONC config for non-secret settings — newer features are JSON-only | Verify config file is `wrangler.jsonc` not `wrangler.toml` |

### Step 6 — Apply Request & Response Handling Rules

| Rule | Summary |
|------|---------|
| Streaming | Stream large/unknown payloads — never `await response.text()` on unbounded data |
| waitUntil | Use `ctx.waitUntil()` for post-response work; do not destructure `ctx` |

### Step 7 — Apply Architecture Rules

| Rule | Summary |
|------|---------|
| Bindings over REST | Use in-process bindings (KV, R2, D1, Queues) — not the Cloudflare REST API |
| Queues & Workflows | Move async/background work off the critical path |
| Service bindings | Use service bindings for Worker-to-Worker calls — not public HTTP |
| Hyperdrive | Always use Hyperdrive for external PostgreSQL/MySQL connections |

### Step 8 — Apply Observability Rules

| Rule | Summary |
|------|---------|
| Logs & Traces | Enable `observability` in config with `head_sampling_rate`; use structured JSON logging |

### Step 9 — Apply Code Pattern Rules

| Rule | Summary |
|------|---------|
| No global request state | Never store request-scoped data in module-level variables |
| Floating promises | Every Promise must be `await`ed, `return`ed, `void`ed, or passed to `ctx.waitUntil()` |

### Step 10 — Apply Security Rules

| Rule | Summary |
|------|---------|
| Web Crypto | Use `crypto.randomUUID()` / `crypto.getRandomValues()` — never `Math.random()` for security |
| No passThroughOnException | Use explicit try/catch with structured error responses |

## Pitfalls

### Anti-Patterns to Flag

| Anti-pattern | Why it matters |
|-------------|----------------|
| `await response.text()` on unbounded data | Memory exhaustion — 128 MB limit |
| Hardcoded secrets in source or config | Credential leak via version control |
| `Math.random()` for tokens/IDs | Predictable, not cryptographically secure |
| Bare `fetch()` without `await` or `waitUntil` | Floating promise — dropped result, swallowed error |
| Module-level mutable variables for request state | Cross-request data leaks, stale state, I/O errors |
| Cloudflare REST API from inside a Worker | Unnecessary network hop, auth overhead, added latency |
| `ctx.passThroughOnException()` as error handling | Hides bugs, makes debugging impossible |
| Hand-written `Env` interface | Drifts from actual wrangler config bindings |
| Direct string comparison for secret values | Timing side-channel — use `crypto.subtle.timingSafeEqual` |
| Destructuring `ctx` (`const { waitUntil } = ctx`) | Loses `this` binding — throws "Illegal invocation" at runtime |
| `any` on `Env` or handler params | Defeats type safety for all binding access |
| `as unknown as T` double-cast | Hides real type incompatibilities — fix the design |
| `implements` on platform base classes (instead of `extends`) | Legacy — loses `this.ctx`, `this.env`. Applies to DurableObject, WorkerEntrypoint, Workflow |
| `env.X` inside platform base class | Should be `this.env.X` in classes extending DurableObject, WorkerEntrypoint, etc. |

### Hard Rules

- **Never** hardcode secrets in source or config — always use `wrangler secret put`
- **Never** use `Math.random()` for security-sensitive tokens or IDs
- **Never** store request-scoped data in module-level mutable variables
- **Never** destructure `ctx` — always call `ctx.waitUntil()` directly
- **Never** hand-write the `Env` interface — run `wrangler types` to generate it
- **Never** use `any` on `Env` or handler parameters
- **Never** use `as unknown as T` double-cast — fix the underlying type incompatibility
- **Never** use `implements` on platform base classes — use `extends` instead
- **Never** access `env.X` inside a platform base class — use `this.env.X`
- **Never** use `ctx.passThroughOnException()` as error handling — use explicit try/catch
- **Never** call the Cloudflare REST API from inside a Worker — use in-process bindings
- **Never** `await response.text()` on unbounded data — stream instead

## Verification

### Type Check

```powershell
npx tsc --noEmit
```

Expected: zero errors. If errors appear, check binding access patterns and handler signatures against `references/review.md`.

### Lint for Floating Promises

```powershell
# If using TypeScript ESLint with strict config
npx eslint . --rule '{"no-floating-promises": "error"}'
```

Expected: zero `no-floating-promises` violations.

### Generate Types from Wrangler Config

```powershell
npx wrangler types
```

Expected: generates `worker-configuration.d.ts` (or project-configured output). Verify the generated `Env` interface matches bindings declared in `wrangler.jsonc`.

### Check Config for Required Fields

```powershell
# Verify wrangler.jsonc has compatibility_date, nodejs_compat, and observability
Get-Content "wrangler.jsonc" | Select-String -Pattern "compatibility_date|nodejs_compat|observability|head_sampling_rate"
```

Expected: all four patterns found in the config file.

### Check for Hardcoded Secrets

```powershell
# Search for common secret patterns in source (excluding node_modules)
Get-ChildItem -Recurse -Include "*.ts","*.js","*.jsonc","*.toml" -Exclude "node_modules" | Select-String -Pattern "(?i)(api_key|secret|token|password)\s*[:=]\s*['\""][^'\""]{8,}" | Where-Object { $_.Path -notmatch "node_modules" }
```

Expected: zero matches (or only placeholder values like `YOUR_KEY`).

## Principles

- **Be certain.** Retrieve before flagging. If unsure about an API, config field, or pattern, fetch the docs first.
- **Provide evidence.** Reference line numbers, tool output, or docs links.
- **Focus on what developers will copy.** Workers code in examples and docs gets pasted into production.
- **Correctness over completeness.** A concise example that works beats a comprehensive one with errors.

## Related Skills

- **Durable Objects**: load the `durable-objects` skill for DO-specific patterns
- **Workflows**: see [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)
- **Wrangler CLI commands**: load the `wrangler` skill
