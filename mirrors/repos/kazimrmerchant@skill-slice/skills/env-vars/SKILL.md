---
name: env-vars
description: "Manages Vercel/Next.js environment variables: .env load order, vercel env pull/add/ls/rm, VERCEL_OIDC_TOKEN (~12h local), and production/preview/development scoping. Use when editing .env.local, running vercel env, or debugging expired OIDC on a linked project. Not for Netlify env (netlify-cli-and-deploy), Wrangler secrets, or dotenv without Vercel. Never put secrets on NEXT_PUBLIC_ keys; vercel env pull replaces the whole file."
version: 1.0.1
metadata:
  priority: 7
  docs:
    - "https://vercel.com/docs/environment-variables"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - '.env'
    - '.env.*'
    - '.env.local'
    - '.env.production'
    - '.env.development'
    - '.env.test'
    - '.env.production.local'
    - '.env.development.local'
    - '.env.test.local'
    - '.env.example'
  bashPatterns:
    - '\bvercel\s+env\s+pull\b'
    - '\bvercel\s+env\s+add\b'
    - '\bvercel\s+env\s+rm\b'
    - '\bvercel\s+env\s+ls\b'
---

# Vercel Environment Variables

Expert guidance for Vercel environment variable management — `.env` file conventions, the `vercel env` CLI, OIDC token lifecycle, and environment-specific configuration.

## When to Use

Activate this skill when any of the following are true:

- You are editing, creating, or reviewing `.env`, `.env.local`, `.env.production`, `.env.development`, `.env.test`, or `.env.example` files
- You need to run `vercel env pull`, `vercel env add`, `vercel env rm`, or `vercel env ls`
- You are troubleshooting OIDC token errors (`VERCEL_OIDC_TOKEN` missing or expired)
- You are bootstrapping a fresh clone or new machine and need to provision environment variables
- You are scoping variables to production, preview, or development environments
- You are configuring Git-branch-specific preview variables

## Prerequisites

- **Vercel CLI** installed and authenticated (`vercel login`)
- **Node.js** project with a `package.json` (Next.js or otherwise)
- **PowerShell** as the primary shell on Windows
- Project linked to a Vercel project (`vercel link`) before pulling variables
- `.env.example` committed to the repository with all required variable names (values empty or placeholder)

## Procedure

### 1. Understand the `.env` File Hierarchy

Vercel and Next.js load environment variables in a specific order. Later files override earlier ones:

| File | Purpose | Git-tracked? |
|------|---------|-------------|
| `.env` | Default values for all environments | Yes |
| `.env.local` | Local overrides and secrets | **No** (gitignored) |
| `.env.development` | Development-specific defaults | Yes |
| `.env.development.local` | Local dev overrides | **No** |
| `.env.production` | Production-specific defaults | Yes |
| `.env.production.local` | Local prod overrides | **No** |
| `.env.test` | Test-specific defaults | Yes |
| `.env.test.local` | Local test overrides | **No** |

**Load order (Next.js):**

1. `.env` (lowest priority)
2. `.env.[environment]` (development, production, or test)
3. `.env.local` (skipped in test environment)
4. `.env.[environment].local` (highest priority, skipped in test)

**Critical rules:**

- **Never commit secrets** to `.env`, `.env.development`, or `.env.production` — use `.local` variants or Vercel environment variables
- `.env.local` is always gitignored by Next.js — this is where `vercel env pull` writes secrets
- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser bundle — **never** put secrets in `NEXT_PUBLIC_` vars
- All other variables are server-only (API routes, Server Components, middleware)

### 2. Pull Environment Variables

```powershell
# Pull all env vars for the current environment into .env.local
vercel env pull .env.local

# Pull for a specific environment
vercel env pull .env.local --environment=production
vercel env pull .env.local --environment=preview
vercel env pull .env.local --environment=development

# Overwrite existing file without prompting
vercel env pull .env.local --yes

# Pull to a custom file
vercel env pull .env.production.local --environment=production
```

### 3. Add Environment Variables

```powershell
# Interactive — prompts for value and environments
vercel env add MY_SECRET

# Non-interactive (PowerShell pipeline)
"secret-value" | vercel env add MY_SECRET production

# Add to multiple environments
"secret-value" | vercel env add MY_SECRET production preview development

# Add a sensitive variable (encrypted, not shown in logs)
vercel env add MY_SECRET --sensitive
```

### 4. List Environment Variables

```powershell
# List all environment variables
vercel env ls

# Filter by environment
vercel env ls production
```

### 5. Remove Environment Variables

```powershell
# Remove from specific environment
vercel env rm MY_SECRET production

# Remove from all environments
vercel env rm MY_SECRET
```

### 6. Bootstrap Flow (Fresh Clone / New Machine)

Use this sequence when setting up a project from scratch:

```powershell
# 1) Link first so pulls target the correct Vercel project
vercel link --yes --project <name-or-id> --scope <team>

# 2) Pull env vars into .env.local
vercel env pull .env.local --yes

# 3) Verify required keys from .env.example exist in .env.local
Get-Content .env.example | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=') {
        $key = $Matches[1]
        if (-not (Select-String -Path .env.local -Pattern "^$key=" -Quiet)) {
            Write-Output "Missing in .env.local: $key"
        }
    }
}
```

**Temporary path — run with Vercel envs without writing a file:**

```powershell
vercel env run -- npm run dev
```

This is useful for quick validation during bootstrap, but still pull `.env.local` for a normal local workflow.

**Re-pull after secret or provisioning changes:**

After creating/updating secrets (`vercel env add`, dashboard changes) or provisioning integrations that add env vars (for example Neon/Upstash), re-run:

```powershell
vercel env pull .env.local --yes
```

### 7. Manage OIDC Token Lifecycle

Vercel uses **OIDC (OpenID Connect)** tokens for secure, keyless authentication between your app and Vercel services (AI Gateway, storage, etc.).

**How it works:**

1. **On Vercel deployments**: `VERCEL_OIDC_TOKEN` is automatically injected as a short-lived JWT and auto-refreshed — zero configuration needed
2. **Local development**: `vercel env pull .env.local` provisions a `VERCEL_OIDC_TOKEN` valid for ~12 hours
3. **Token expiry**: When the local OIDC token expires, re-run `vercel env pull .env.local --yes` to get a fresh one. Consider re-pulling at the start of each dev session to avoid mid-session auth failures

**Common OIDC patterns:**

```ts
// The @vercel/oidc package reads VERCEL_OIDC_TOKEN automatically
import { getVercelOidcToken } from '@vercel/oidc'

// AI Gateway uses OIDC by default — no manual token handling needed
import { gateway } from 'ai'
const result = await generateText({
  model: gateway('openai/gpt-5.2'),
  prompt: 'Hello',
})
```

**OIDC troubleshooting:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `VERCEL_OIDC_TOKEN` missing locally | Haven't pulled env vars | `vercel env pull .env.local` |
| Auth errors after ~12h locally | Token expired | `vercel env pull .env.local --yes` |
| Works on Vercel, fails locally | Token not in `.env.local` | `vercel env pull .env.local` |
| `AI_GATEWAY_API_KEY` vs OIDC | Both set, key takes priority | Remove `AI_GATEWAY_API_KEY` to use OIDC |

### 8. Configure Environment Scoping

**Vercel Dashboard vs `.env` files:**

| Use Case | Where to Set |
|----------|-------------|
| Secrets (API keys, tokens) | Vercel Dashboard (`https://vercel.com/{team}/{project}/settings/environment-variables`) or `vercel env add` |
| Public config (site URL, feature flags) | `.env` or `.env.[environment]` files |
| Local-only overrides | `.env.local` |
| CI/CD secrets | Vercel Dashboard (`https://vercel.com/{team}/{project}/settings/environment-variables`) with environment scoping |

Variables set in the Vercel Dashboard can be scoped to:

- **Production** — only `vercel.app` production deployments
- **Preview** — branch/PR deployments
- **Development** — `vercel dev` and `vercel env pull`

A variable can be assigned to one, two, or all three environments.

**Git branch overrides:**

```powershell
# Add a variable only for the "staging" branch
"staging-value" | vercel env add DATABASE_URL preview --git-branch=staging
```

### 9. Handle Scripts That Don't Auto-Load `.env.local`

Only Next.js auto-loads `.env.local`. Standalone scripts (`drizzle-kit`, `tsx`, custom Node scripts) need explicit loading:

```powershell
# Use dotenv-cli
npm install -D dotenv-cli
npx dotenv -e .env.local -- npx drizzle-kit push
npx dotenv -e .env.local -- npx tsx seed.ts
```

## Pitfalls

### `vercel env pull` Overwrites Custom Variables

`vercel env pull .env.local` **replaces the entire file** — any manually added variables (custom secrets, local overrides, debug flags) are lost. Always back up or re-add custom vars after pulling:

```powershell
# Save custom vars before pulling (PowerShell)
Get-Content .env.local | Where-Object { $_ -notmatch '^#' -and $_ -notmatch '^(VERCEL_|POSTGRES_|NEXT_PUBLIC_)' } | Set-Content .env.custom.bak
vercel env pull .env.local --yes
Add-Content .env.local (Get-Content .env.custom.bak)
```

Or maintain custom vars in a separate `.env.development.local` file (loaded after `.env.local` by Next.js).

### `NEXT_PUBLIC_` Variables Leak Secrets to the Browser

Any variable prefixed with `NEXT_PUBLIC_` is inlined into the client JavaScript bundle. Never assign a secret value to a `NEXT_PUBLIC_` variable — it will be publicly readable.

### OIDC Token Expiry Mid-Session

The local `VERCEL_OIDC_TOKEN` expires after ~12 hours. If you see auth errors during a long dev session, re-pull:

```powershell
vercel env pull .env.local --yes
```

Consider re-pulling at the start of every dev session as a habit.

### `AI_GATEWAY_API_KEY` Overrides OIDC

If both `AI_GATEWAY_API_KEY` and `VERCEL_OIDC_TOKEN` are set, the API key takes priority and OIDC is bypassed. Remove `AI_GATEWAY_API_KEY` from `.env.local` to use keyless OIDC auth.

### Forgetting `vercel link` Before `vercel env pull`

`vercel env pull` targets whichever Vercel project is linked to the local directory. On a fresh clone, run `vercel link` first or the pull will fail or target the wrong project.

### Standalone Scripts Silently Missing Variables

If a script like `drizzle-kit push` or `tsx seed.ts` fails with connection errors or undefined values, it is likely because `.env.local` was not loaded. Use `dotenv-cli` (see Procedure step 9) to explicitly load the file.

## Verification

### Verify `.env.local` Was Pulled Successfully

```powershell
# Check the file exists and has content
Test-Path .env.local
(Get-Content .env.local | Measure-Object -Line).Lines
```

Expected: file exists with multiple lines containing `KEY=value` entries.

### Verify All Required Keys from `.env.example` Are Present

```powershell
Get-Content .env.example | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=') {
        $key = $Matches[1]
        if (-not (Select-String -Path .env.local -Pattern "^$key=" -Quiet)) {
            Write-Output "Missing in .env.local: $key"
        }
    }
}
```

Expected: no output (all keys present). Any printed line indicates a missing variable.

### Verify OIDC Token Is Present

```powershell
Select-String -Path .env.local -Pattern '^VERCEL_OIDC_TOKEN=' -Quiet
```

Expected: `True`.

### Verify No Secrets Are Committed

```powershell
# Check that .env.local is gitignored
git check-ignore .env.local
```

Expected: prints `.env.local` (confirming it is ignored).

### Verify No `NEXT_PUBLIC_` Variable Contains a Secret

```powershell
Select-String -Path .env.local -Pattern '^NEXT_PUBLIC_.*=' | ForEach-Object {
    $val = ($_ -split '=', 2)[1]
    if ($val -and $val -notmatch '^(YOUR_KEY|placeholder|example|sk-test|pk_)' -and $val.Length -gt 20) {
        Write-Output "WARNING: Long value in NEXT_PUBLIC_ var: $($_ -split '=', 2)[0]"
    }
}
```

Expected: no warnings.

## Best Practices

1. **Use `vercel env pull` as part of your setup workflow** — document it in your README
2. **Never hardcode secrets** — always use environment variables
3. **Scope narrowly** — don't give preview deployments production database access
4. **Rotate OIDC tokens regularly in local dev** — re-pull when you see auth errors
5. **Use `.env.example`** — commit a template with empty values so teammates know which vars are needed
6. **Prefix client-side vars with `NEXT_PUBLIC_`** — and never put secrets in them
7. **Keep custom vars in `.env.development.local`** — protects them from `vercel env pull` overwrites

## Official Documentation

- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Vercel CLI: env](https://vercel.com/docs/cli/env)
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
