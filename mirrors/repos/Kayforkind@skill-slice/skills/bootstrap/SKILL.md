---
name: bootstrap
description: "Orchestrates first-run setup for Vercel-linked repos: vercel link, env pull, AUTH_SECRET, then db:push/seed/dev in that order (next-forge uses pnpm migrate). Use when cloning or repairing a project that depends on Neon, Auth, Blob, or other Vercel integrations. Not for the CSS Bootstrap framework or UI component libraries. Do not use to author CI deploy workflows (deployments-cicd) or to mint throwaway neon.new databases (claimable-postgres)."
version: 1.0.1
metadata:
  priority: 8
  docs:
    - "https://vercel.com/docs/getting-started-with-vercel"
    - "https://nextjs.org/docs/getting-started/installation"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - '.env.example'
    - '.env.sample'
    - '.env.template'
    - 'README*'
    - 'docs/**/setup*'
    - 'package.json'
    - 'drizzle.config.*'
    - 'prisma/schema.prisma'
    - 'auth.*'
    - 'src/**/auth.*'
  bashPatterns:
    - '\bcp\s+\.env\.(?:example|sample|template)\s+\.env\.local\b'
    - '\b(?:npm|pnpm|bun|yarn)\s+run\s+db:(?:push|seed|migrate|generate)\b'
    - '\b(?:npm|pnpm|bun|yarn)\s+run\s+dev\b'
    - '\bvercel\s+link\b'
    - '\bvercel\s+integration\s+(?:add|install)\b'
    - '\bvercel\s+env\s+pull\b'
  importPatterns:
    - '@neondatabase/serverless'
    - 'drizzle-orm'
    - '@upstash/redis'
    - '@vercel/blob'
    - '@vercel/edge-config'
    - 'next-auth'
    - '@auth/core'
    - 'better-auth'
---

# Project Bootstrap Orchestrator

Execute bootstrap in strict order. Do not run migrations or development server until project linking and environment verification are complete.

## When to Use

Use this skill when:
- Setting up a freshly cloned repository that depends on Vercel-linked resources (Postgres, Auth, Blob, Edge Config, Upstash, etc.).
- Repairing a repo whose environment or database state is broken or incomplete.
- You detect `.env.example`, `.env.sample`, `.env.template`, `drizzle.config.*`, `prisma/schema.prisma`, `auth.*`, or `next-forge` workspace markers.
- The user asks to "bootstrap", "set up", "link", "pull env", or "get the project running".
- Bash patterns like `vercel link`, `vercel env pull`, `npm run db:push`, or `npm run dev` appear in instructions.

## Prerequisites

- **Vercel CLI** installed and authenticated (`vercel --version`, `vercel whoami`).
- **Node.js** runtime available for secret generation (`node -e`).
- **Package manager** detected from repo lockfiles (`package-lock.json` → npm, `pnpm-workspace.yaml` → pnpm, `bun.lockb` → bun, `yarn.lock` → yarn).
- **Windows host (primary)**: PowerShell is the default shell. Commands below are POSIX-style for cross-platform Vercel CLI and Node; adapt quoting for PowerShell where noted. The library path on the authoring machine is `~\agent-skills\library\bootstrap\SKILL.md`.

## Procedure

### 0. Hard Rules (do not violate)

- **Never** run `db:push`, `db:migrate`, `db:seed`, or `dev` until Vercel linking is complete and env keys are verified.
- **Prefer** Vercel-managed provisioning (`vercel integration ...`) for shared resources. Use provider CLIs only as fallback when the Vercel integration flow is unavailable.
- **Never** echo secret values in terminal output, logs, or summaries. Key names only.
- **Never** delete `.env.local` or `.vercel/project.json` without explicit user confirmation.
- Use the repository's package manager (`npm`, `pnpm`, `bun`, or `yarn`) and run only scripts that exist in `package.json`.

### 1. Preflight — Vercel CLI & Linkage

1. Confirm Vercel CLI is installed and authenticated:

```bash
vercel --version
vercel whoami
```

2. Confirm repo linkage by checking `.vercel/project.json`:

```bash
cat .vercel/project.json
```

3. If not linked, inspect available teams/projects before asking the user to choose:

```bash
vercel teams ls
vercel projects ls --scope <team>
vercel link --yes --scope <team> --project <project>
```

4. Find the env template in priority order: `.env.example`, `.env.sample`, `.env.template`.

5. Create local env file if missing:

```bash
cp .env.example .env.local
```

> **PowerShell note:** Use `Copy-Item .env.example .env.local` if `cp` is not aliased.

### 2. Resource Setup — Postgres (Neon)

#### Preferred path (Vercel-managed Neon)

1. Read integration setup guidance:

```bash
vercel integration guide neon
```

2. Add Neon integration to the Vercel scope:

```bash
vercel integration add neon --scope <team>
```

3. Verify expected environment variable names exist in Vercel and pull locally:

```bash
vercel env ls
vercel env pull .env.local --yes
```

#### Fallback path 1 (Dashboard)

1. Provision Neon through the Vercel dashboard integration UI.
2. Re-run `vercel env pull .env.local --yes`.

#### Fallback path 2 (Neon CLI)

Use Neon CLI **only** when Vercel-managed provisioning is unavailable. After creating resources, add required env vars in Vercel and pull again:

```bash
vercel env pull .env.local --yes
```

### 3. AUTH_SECRET Generation

Generate a high-entropy secret **without printing it**, then store it in Vercel and refresh local env:

```bash
AUTH_SECRET="$(node -e "console.log(require('node:crypto').randomBytes(32).toString('base64url'))")"
printf "%s" "$AUTH_SECRET" | vercel env add AUTH_SECRET development preview production
unset AUTH_SECRET
vercel env pull .env.local --yes
```

> **PowerShell note:** The above uses POSIX subshell syntax. In PowerShell, generate and pipe differently:
> ```powershell
> $secret = node -e "console.log(require('node:crypto').randomBytes(32).toString('base64url'))"
> $secret | vercel env add AUTH_SECRET development preview production
> Remove-Variable secret
> vercel env pull .env.local --yes
> ```

### 4. Env Verification

Compare required keys from the template file against `.env.local` keys (**names only, never values**):

```bash
template_file=""
for candidate in .env.example .env.sample .env.template; do
  if [ -f "$candidate" ]; then
    template_file="$candidate"
    break
  fi
done

comm -23 \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$template_file" | cut -d '=' -f 1 | sort -u) \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env.local | cut -d '=' -f 1 | sort -u)
```

**Proceed only when the missing key list is empty.** If keys are missing, add them in Vercel and re-pull.

### 5. App Setup — Database & Dev

After linkage + env verification:

```bash
npm run db:push
npm run db:seed
npm run dev
```

Replace `npm` with the repo's package manager. Run only scripts that exist in `package.json` (check `db:push`, `db:seed`, `db:migrate`, `db:generate` as applicable).

### 6. UI Baseline for Next.js + shadcn Projects

After linkage and env verification, establish the UI foundation before feature work:

1. Add a baseline primitive set:

```bash
npx shadcn@latest add button card input label textarea select switch tabs dialog alert-dialog sheet dropdown-menu badge separator skeleton table
```

2. Apply the Geist font fix in `layout.tsx` and `globals.css`.
3. Confirm the app shell uses `bg-background text-foreground`.
4. Default to dark mode for product, admin, and AI apps unless the repo is clearly marketing-first.

### 7. next-forge Projects

If the project was scaffolded with `npx next-forge init` (detected by `pnpm-workspace.yaml` + `packages/auth` + `packages/database` + `@repo/*` imports):

1. Env files are per-app (`apps/app/.env.local`, `apps/web/.env.local`, `apps/api/.env.local`) plus `packages/database/.env`.
2. Run `pnpm migrate` (**not** `db:push`) — it runs `prisma format` + `prisma generate` + `prisma db push`.
3. Minimum env vars: `DATABASE_URL`, `CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_WEB_URL`, `NEXT_PUBLIC_API_URL`.
4. Optional services (Stripe, Resend, PostHog, etc.) can be skipped initially — but **remove their `@repo/*` imports** from app `env.ts` files to avoid validation errors.
5. Deploy as 3 separate Vercel projects with root directories `apps/app`, `apps/api`, `apps/web`.

> **Related skill:** `next-forge` — Full next-forge monorepo guide.

## Pitfalls

- **Running db commands before linking/env verification** — violates hard rules; can write to wrong database or fail silently. Always complete steps 1–4 first.
- **Echoing secret values** — never print `AUTH_SECRET` or any secret value. Use key names only in summaries and logs.
- **Wrong package manager** — using `npm` in a pnpm/bun workspace causes phantom dependencies and lockfile conflicts. Detect from lockfiles.
- **next-forge `db:push` vs `pnpm migrate`** — next-forge repos must use `pnpm migrate`; running `db:push` directly skips `prisma format` and `prisma generate`.
- **Optional service env validation** — next-forge `env.ts` files validate imported `@repo/*` packages. If you skip Stripe/Resend/PostHog, remove their imports or the app will crash on boot.
- **Multiple `.env.local` files in monorepos** — each app needs its own env file; a root `.env.local` is insufficient.
- **Vercel integration not available** — fall back to dashboard or provider CLI, but always re-run `vercel env pull .env.local --yes` after manual provisioning.
- **PowerShell quoting** — POSIX subshells `$(...)` and process substitution `<(...)` do not work in PowerShell; adapt as noted.
- **Deleting `.vercel/project.json`** — never delete without explicit user confirmation; it breaks linkage and requires re-linking.

## Verification

Confirm each checkpoint before declaring bootstrap complete:

1. **Vercel auth**: `vercel whoami` succeeds (prints username).
2. **Linkage**: `.vercel/project.json` exists and matches chosen project:

```bash
cat .vercel/project.json
```

3. **Postgres integration**: one path completed (Vercel integration, dashboard, or provider CLI fallback).
4. **Env pull**: `vercel env pull .env.local --yes` succeeds (exit code 0).
5. **Required env key diff is empty**:

```bash
comm -23 \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env.example | cut -d '=' -f 1 | sort -u) \
  <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env.local | cut -d '=' -f 1 | sort -u)
```

Output must be empty.

6. **Database commands**: status recorded (`db:push`, `db:seed`, `db:migrate`, `db:generate` as applicable).
7. **Dev server**: `npm run dev` (or equivalent) starts without immediate config/auth/env failure.

If verification fails, **stop** and report the exact failing step plus remediation guidance.

## Summary Format

Return a final bootstrap summary in this format:

```md
## Bootstrap Result
- **Linked Project**: <team>/<project>
- **Resource Path**: vercel-integration-neon | dashboard-neon | neon-cli
- **Env Keys**: <count> required, <count> present, <count> missing
- **Secrets**: AUTH_SECRET set in Vercel (value never shown)
- **Migration Status**: not-run | success | failed (<step>)
- **Dev Result**: not-run | started | failed
```

## Bootstrap Next Steps

- If env keys are still missing, add the missing keys in Vercel and re-run `vercel env pull .env.local --yes`.
- If DB commands fail, fix connectivity/schema issues and re-run only the failed db step.
- If `dev` fails, resolve runtime errors, then restart with your package manager's `run dev`.
