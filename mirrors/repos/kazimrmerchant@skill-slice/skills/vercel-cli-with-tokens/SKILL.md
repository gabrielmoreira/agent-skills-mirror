---
name: vercel-cli-with-tokens
description: "Deploys and manages Vercel projects via CLI authenticated by VERCEL_TOKEN in the environment (never --token on the command line): preview deploy, env vars, inspect, domains. Use when CI or an agent must deploy without vercel login. Not for interactive vercel login, Blob/Edge Config/database storage (vercel-storage), or git push."
version: 1.0.1
risk: safe
source: "https://github.com/vercel-labs/agent-skills"
date_added: "2026-06-02"
---

# Vercel CLI with Tokens

Deploy and manage projects on Vercel using the CLI with token-based authentication, without relying on `vercel login`. The CLI reads `VERCEL_TOKEN` from the environment natively — never pass it as a `--token` flag.

## When to Use

- Deploying or managing a Vercel project via CLI when an access token is available (not interactive login).
- Setting up a new Vercel project link from a local repository.
- Adding, listing, pulling, or removing environment variables on Vercel.
- Inspecting deployments, viewing build/runtime logs, or listing recent deployments.
- Managing domains attached to a Vercel project.
- Trigger phrases: "deploy to vercel", "set up vercel", "add environment variables to vercel", "vercel preview deploy", "vercel production deploy", "link vercel project".

## Prerequisites

1. **Node.js** installed (for `npm install -g vercel`).
2. **Vercel CLI** installed and up to date:
   ```bash
   npm install -g vercel
   vercel --version
   ```
3. **A Vercel access token** — obtainable at `vercel.com/account/tokens`. Tokens typically start with `vca_`.
4. **Windows host (PowerShell) is primary.** Adapt bash-style commands below for PowerShell where needed (e.g. `$env:VERCEL_TOKEN` instead of `export VERCEL_TOKEN`). On Windows PowerShell:
   ```powershell
   $env:VERCEL_TOKEN = "YOUR_TOKEN"
   $env:VERCEL_ORG_ID = "YOUR_ORG_ID"
   $env:VERCEL_PROJECT_ID = "YOUR_PROJECT_ID"
   ```
5. On bash/zsh (WSL, CI, or Linux):
   ```bash
   export VERCEL_TOKEN="YOUR_TOKEN"
   export VERCEL_ORG_ID="YOUR_ORG_ID"
   export VERCEL_PROJECT_ID="YOUR_PROJECT_ID"
   ```

## Procedure

### Step 1: Locate the Vercel Token

Work through these scenarios in order before running any Vercel CLI command.

#### A) `VERCEL_TOKEN` already set in the environment

```bash
[ -n "${VERCEL_TOKEN:-}" ] && printf 'VERCEL_TOKEN is set\n'
```

If this reports a configured token, skip to Step 2.

#### B) Token is in a `.env` file under `VERCEL_TOKEN`

```bash
grep -q '^VERCEL_TOKEN=' .env 2>/dev/null && printf 'VERCEL_TOKEN is present in .env\n'
```

If found, export it:

```bash
VERCEL_TOKEN="$(sed -n 's/^VERCEL_TOKEN=//p' .env | tail -n 1)"
export VERCEL_TOKEN
```

#### C) Token is in a `.env` file under a different name

Vercel tokens typically start with `vca_`. Search for any variable that looks like a Vercel token:

```bash
grep -Eio '^[A-Z0-9_]*VERCEL[A-Z0-9_]*(?==)' .env 2>/dev/null
```

Inspect the output, identify which variable holds the token, then export it as `VERCEL_TOKEN`:

```bash
vercel_var="<VARIABLE_NAME>"
VERCEL_TOKEN="$(sed -n "s/^${vercel_var}=//p" .env | tail -n 1)"
export VERCEL_TOKEN
```

#### D) No token found — ask the user

If none of the above yield a token, ask the user to provide one. They can create a Vercel access token at `vercel.com/account/tokens`.

> **HARD RULE:** Once `VERCEL_TOKEN` is exported as an environment variable, the Vercel CLI reads it natively — **do not pass it as a `--token` flag**. Putting secrets in command-line arguments exposes them in shell history and process listings.

```bash
# BAD — token visible in shell history and process listings
vercel deploy --token "vca_abc123"

# GOOD — CLI reads VERCEL_TOKEN from the environment
[ -n "${VERCEL_TOKEN:-}" ] || { echo "Set VERCEL_TOKEN first" >&2; exit 1; }
vercel deploy
```

### Step 2: Locate the Project and Team

Check for the project ID and team scope. These let the CLI target the right project without needing `vercel link`.

```bash
# Check environment
[ -n "${VERCEL_PROJECT_ID:-}" ] && printf 'VERCEL_PROJECT_ID is set\n'
[ -n "${VERCEL_ORG_ID:-}" ] && printf 'VERCEL_ORG_ID is set\n'

# Or check .env
grep -Eio '^[A-Z0-9_]*VERCEL[A-Z0-9_]*(?==)' .env 2>/dev/null
```

**If you have a project URL** (e.g. `https://vercel.com/my-team/my-project`), extract the team slug:

```bash
# e.g. "my-team" from "https://vercel.com/my-team/my-project"
echo "$PROJECT_URL" | sed 's|https://vercel.com/||' | cut -d/ -f1
```

**If you have both `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`**, export them — the CLI will use these automatically and skip any `.vercel/` directory:

```bash
export VERCEL_ORG_ID="<org-id>"
export VERCEL_PROJECT_ID="<project-id>"
```

> **HARD RULE:** `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` must be set **together** — setting only one causes an error.

### Step 3: Deploy a Project

Always deploy as **preview** unless the user explicitly requests production.

#### Quick Deploy (have project ID — no linking needed)

When `VERCEL_TOKEN` and `VERCEL_PROJECT_ID` are set in the environment, deploy directly:

```bash
vercel deploy -y --no-wait
```

With a team scope (either via `VERCEL_ORG_ID` or `--scope`):

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

Production (only when explicitly requested):

```bash
vercel deploy --prod --scope <team-slug> -y --no-wait
```

Check status:

```bash
vercel inspect <deployment-url>
```

#### Full Deploy Flow (no project ID — need to link)

Use this when you have a token and team but no pre-existing project ID.

**Check project state first:**

```bash
# Does the project have a git remote?
git remote get-url origin 2>/dev/null

# Is it already linked to a Vercel project?
cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null
```

**Link the project:**

With git remote (preferred):

```bash
vercel link --repo --scope <team-slug> -y
```

Reads the git remote and connects to the matching Vercel project. Creates `.vercel/repo.json`. More reliable than plain `vercel link`, which matches by directory name.

Without git remote:

```bash
vercel link --scope <team-slug> -y
```

Creates `.vercel/project.json`.

Link to a specific project by name:

```bash
vercel link --project <project-name> --scope <team-slug> -y
```

If the project is already linked, check `orgId` in `.vercel/project.json` or `.vercel/repo.json` to verify it matches the intended team.

**Deploy after linking:**

**A) Git Push Deploy — has git remote (preferred)**

Git pushes trigger automatic Vercel deployments.

1. **Ask the user before pushing.** Never push without explicit approval.
2. Commit and push:
   ```bash
   git add .
   git commit -m "deploy: <description of changes>"
   git push
   ```
3. Vercel builds automatically. Non-production branches get preview deployments.
4. Retrieve the deployment URL:
   ```bash
   sleep 5
   vercel ls --format json --scope <team-slug>
   ```
   Find the latest entry in the `deployments` array.

**B) CLI Deploy — no git remote**

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

Check status:

```bash
vercel inspect <deployment-url>
```

#### Deploying from a Remote Repository (code not cloned locally)

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```
2. Link to Vercel:
   ```bash
   vercel link --repo --scope <team-slug> -y
   ```
3. Deploy via git push (if you have push access) or CLI deploy.

#### About the `.vercel/` Directory

A linked project has either:
- `.vercel/project.json` — from `vercel link`. Contains `projectId` and `orgId`.
- `.vercel/repo.json` — from `vercel link --repo`. Contains `orgId`, `remoteName`, and a `projects` map.

Not needed when `VERCEL_ORG_ID` + `VERCEL_PROJECT_ID` are both set in the environment.

> **HARD RULE:** Do **NOT** run `vercel project inspect` or `vercel link` in an unlinked directory to detect state — they will interactively prompt or silently link as a side-effect. `vercel ls` is safe (in an unlinked directory it defaults to showing all deployments for the scope). `vercel whoami` is safe anywhere.

### Step 4: Manage Environment Variables

```bash
# Set for all environments
echo "value" | vercel env add VAR_NAME --scope <team-slug>

# Set for a specific environment (production, preview, development)
echo "value" | vercel env add VAR_NAME production --scope <team-slug>

# List environment variables
vercel env ls --scope <team-slug>

# Pull env vars to local .env.local file
vercel env pull --scope <team-slug>

# Remove a variable
vercel env rm VAR_NAME --scope <team-slug> -y
```

### Step 5: Inspect Deployments and Logs

```bash
# List recent deployments
vercel ls --format json --scope <team-slug>

# Inspect a specific deployment
vercel inspect <deployment-url>

# View build logs (requires Vercel CLI v35+)
vercel inspect <deployment-url> --logs

# View runtime request logs (follows live by default; add --no-follow for a one-shot snapshot)
vercel logs <deployment-url>
```

### Step 6: Manage Domains

```bash
# List domains
vercel domains ls --scope <team-slug>

# Add a domain to the project — linked or env-linked directory (1 arg)
vercel domains add <domain> --scope <team-slug>

# Add a domain — unlinked directory (requires <project> positional)
vercel domains add <domain> <project> --scope <team-slug>
```

### Step 7: Stripe Projects Plan Changes (if applicable)

If this project is managed by Stripe Projects, **ask the user before running any paid or destructive plan change** — upgrades bill a real card, downgrades remove seats.

First run `stripe projects status --json` to confirm the Vercel resource's local name. The examples below assume the default (`vercel-plan`); substitute the actual name if it was renamed at `stripe projects add` time.

- **Upgrade to Pro:** `stripe projects add vercel/pro` (or `stripe projects upgrade vercel-plan pro`)
- **Downgrade to Hobby:** `stripe projects downgrade vercel-plan hobby`

**What Pro gives you:**
- $20/month platform fee, includes $20/month of usage credit.
- Turbo build machines (30 vCPUs, 60 GB memory) by default for new projects — significantly faster builds than Hobby.
- 1 deploying seat + unlimited free Viewer seats (read-only collaborators, preview comments).
- Higher included allocations (1 TB Fast Data Transfer, 10M Edge Requests per month).
- Paid add-ons available: SAML SSO, HIPAA BAA, Flags Explorer, Observability Plus, Speed Insights, Web Analytics Plus.

Full details: https://vercel.com/docs/plans/pro-plan

## Pitfalls

1. **Never pass `VERCEL_TOKEN` as a `--token` flag.** It exposes the secret in shell history and process listings. Always export it as an environment variable.
2. **`VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` must be set together.** Setting only one causes an error.
3. **Do not run `vercel project inspect` or `vercel link` in an unlinked directory** to "detect" state — they interactively prompt or silently link as a side-effect. Use `vercel ls` or `vercel whoami` instead, which are safe in unlinked directories.
4. **Do not modify `.vercel/` files directly.** The CLI manages this directory. Reading them (e.g. to verify `orgId`) is fine.
5. **Do not curl/fetch deployed URLs to verify.** Just return the link to the user.
6. **Default to preview deployments.** Only deploy to production (`--prod`) when the user explicitly asks.
7. **Ask before pushing to git.** Never push commits without the user's explicit approval.
8. **Token may be expired or invalid.** If you see `Authentication required`, verify with `vercel whoami` and ask the user for a fresh token.
9. **Wrong team scope.** Verify with `vercel whoami --scope <team-slug>` before deploying.
10. **Build failures** — common causes: missing dependencies (ensure `package.json` is complete and committed), missing environment variables (add with `vercel env add`), framework misconfiguration (check `vercel.json`; Vercel auto-detects frameworks like Next.js, Remix, Vite from `package.json` — override with `vercel.json` if detection is wrong).
11. **`vercel link` matches by directory name** — use `vercel link --repo` for more reliable matching via git remote.
12. **Interactive prompts block automation** — always use `-y` on commands that prompt for confirmation.

## Verification

1. **Token is valid:**
   ```bash
   vercel whoami
   ```
   Expected: prints the authenticated username/team. If it prints `Authentication required`, the token is missing, expired, or invalid.

2. **CLI is installed and version is current:**
   ```bash
   vercel --version
   ```
   Expected: prints a version number (e.g. `35.0.0` or higher for `--logs` support).

3. **Project is linked correctly:**
   ```bash
   cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null
   ```
   Expected: JSON containing `orgId` and `projectId` (or `remoteName` and `projects` map for repo linking). Verify `orgId` matches the intended team.

4. **Deployment succeeded:**
   ```bash
   vercel inspect <deployment-url>
   ```
   Expected: deployment metadata showing `READY` state. For build logs:
   ```bash
   vercel inspect <deployment-url> --logs
   ```

5. **Environment variables are set:**
   ```bash
   vercel env ls --scope <team-slug>
   ```
   Expected: lists all env vars with their target environments.

6. **Team scope is correct:**
   ```bash
   vercel whoami --scope <team-slug>
   ```
   Expected: confirms the authenticated identity under the specified scope.

## Working Agreement

- **Never pass `VERCEL_TOKEN` as a `--token` flag.** Export it as an environment variable and let the CLI read it natively.
- **Check the environment for tokens before asking the user.** Look in the current env and `.env` files first.
- **Default to preview deployments.** Only deploy to production when explicitly asked.
- **Ask before pushing to git.** Never push commits without the user's approval.
- **Do not modify `.vercel/` files directly.** The CLI manages this directory. Reading them is fine.
- **Do not curl/fetch deployed URLs to verify.** Just return the link to the user.
- **Use `--format json`** when structured output will help with follow-up steps.
- **Use `-y`** on commands that prompt for confirmation to avoid interactive blocking.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
