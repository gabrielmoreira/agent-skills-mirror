# Deployment Mode: `prod-railway`

**Scope**: Authoritative for all work when `DEPLOY_MODE=prod-railway`
**Last Updated**: 2026-06-03

> **Authority**: DEEP — when this mode is active, this file is authoritative over the parent `.ai/instruct.md`. See [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) for the depth-priority hierarchy and [`../README.md`](../../README.md) for the deployment-mode convention.

---

## Contents

| Section | What's here |
|---|---|
| [Mode Overview](#mode-overview) | What `prod-railway` is and when to use it |
| [Prerequisites](#prerequisites) | Required accounts and CLI tools |
| [Quick Start](#quick-start) | First-time deploy |
| [What Runs](#what-runs) | Services on Railway |
| [Access URLs](#access-urls) | Public-facing URLs |
| [Environment Variables](#environment-variables) | Required Railway env vars |
| [Deployment Workflow](#deployment-workflow) | CI/CD and manual deploy |
| [Database Management](#database-management) | Migrations and backups |
| [Operational Tasks](#operational-tasks) | Common day-to-day commands |
| [Security Notes](#security-notes) | Threat model and limits |
| [Cost & Limits](#cost--limits) | Billing and quota |
| [Troubleshooting](#troubleshooting) | Common issues and fixes |
| [Operational Checklist](#operational-checklist) | Mode-switch checklist |
| [Next Steps](#next-steps) | Post-deploy actions |
| [Resources](#resources) | External links |
| [Files in This Mode](#files-in-this-mode) | What lives in this directory |

## Mode Overview

`prod-railway` is fully managed cloud deployment via [Railway](https://railway.app) — no port forwarding, no DDNS, no server admin. Railway builds from the project's `Dockerfile` (or buildpack) and handles TLS, database, and DNS.

| Aspect | Value |
|---|---|
| **Primary URL** | `https://[PROJECT_NAME].railway.app` |
| **Access** | Public internet |
| **TLS** | Railway-managed (Let's Encrypt, auto-renew) |
| **Database** | Railway-managed `[DB_ENGINE]` |
| **Reverse proxy** | Railway edge (no Caddy) |
| **IP management** | n/a (Railway DNS) |
| **Use case** | Hands-off cloud hosting, tight CI/CD loop |
| **Setup time** | ~10 minutes (account + first deploy) |
| **Cost** | Free tier with monthly limits, paid plans scale |

---

## Prerequisites

- [ ] Railway account ([railway.app](https://railway.app))
- [ ] GitHub repository for the project
- [ ] [Railway CLI](https://docs.railway.app/develop/cli) installed (`railway --version`)
- [ ] GitHub connected to the Railway account
- [ ] `Dockerfile` (or compatible buildpack) at the deployable module's root
- [ ] All required env vars known — see [`.ai/config-vars.md`](../../../.ai/config-vars.md)

---

## Quick Start

### 1. Initialize the Railway project

```bash
[SET_ENV] DEPLOY_MODE=prod-railway
railway init        # follow prompts; pick "Empty Project" or link to existing
railway link        # if the project already exists
```

### 2. Set environment variables

```bash
railway variables --set DEPLOY_MODE=prod-railway \
                  --set NODE_ENV=production \
                  --set JWT_SECRET=[GENERATED_HEX] \
                  --set POSTGRES_PASSWORD=[STRONG_PASSWORD] \
                  --set [OTHER_VARS]=[VALUES]
```

Generate `JWT_SECRET`:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
# or
python -c "import secrets; print(secrets.token_hex(48))"
```

### 3. Deploy

```bash
railway up           # builds from Dockerfile, deploys
# or
git push origin main # if Railway auto-deploy on push is configured
```

### 4. Visit the deployed app

```bash
railway open
```

---

## What Runs

| Service | Managed by | Tech |
|---|---|---|
| Database | Railway | `[DB_ENGINE]` |
| API | Railway | `[BACKEND_FRAMEWORK]` |
| Frontend | Railway | Served via API static or separate Railway service |
| TLS | Railway | Let's Encrypt (automatic) |
| DNS | Railway | `*.railway.app` subdomain (custom domain optional) |

---

## Access URLs

- **HTTPS (Railway domain)**: `https://[PROJECT_NAME].railway.app`
- **Custom domain** (optional): configured in the Railway dashboard

---

## Environment Variables

In `prod-railway`, the local `.env` file is **not** consulted. All variables live in Railway:

```bash
# View all variables
railway variables

# Set / update
railway variables --set NAME=value

# Remove
railway variables --remove NAME
```

The same variables documented in [`.ai/config-vars.md`](../../../.ai/config-vars.md) apply — only the storage location changes.

---

## Deployment Workflow

### From the CLI

```bash
railway up                       # from project root
cd [DEPLOYABLE_MODULE]
railway up                       # from a specific service
```

### From Git

If GitHub auto-deploy is enabled, every push to `main` (or the configured branch) triggers a build and deploy. Verify in the Railway dashboard under Project → Settings → Deployments.

### Logs

```bash
railway logs                     # recent
railway logs --tail 50 -f        # follow
```

### Status

```bash
railway status
railway services
```

---

## Database Management

### Connect

```bash
# Get the connection string
railway variables | grep DATABASE_URL

# Connect locally (requires the DB client installed)
[DB_CLIENT_COMMAND] "$DATABASE_URL"
```

### Backups

Railway auto-backs up managed databases. Restore via the dashboard: PostgreSQL service → Backups → Restore.

---

## Operational Tasks

### Update the app

```bash
git add .
git commit -m "<change>"
git push origin main
# Railway auto-builds and deploys, or:
railway up
```

### View real-time logs

```bash
railway logs -f --tail 100
```

### Roll back

```bash
# Via dashboard: Deployments → pick a previous one → Redeploy
```

### Custom domain

```bash
# Dashboard: Project Settings → Domains → Add custom domain
# Update DNS records as instructed
```

---

## Security Notes

- All secrets live in Railway variables, **not** in `.env` and **not** in source.
- Railway-managed TLS is automatic and uses Let's Encrypt; do not attempt to override.
- Minimize the public attack surface: only the API/frontend services should be public; DB and internal services stay private.
- Rotate `JWT_SECRET` and DB credentials periodically — see [`.ai/credentials.md`](../../../.ai/credentials.md).

---

## Cost & Limits

- **Free tier**: includes monthly compute credits. Suitable for low-traffic apps.
- **Paid plans**: scale automatically; monitor usage in the dashboard.
- **Cost optimization**: stop unused services (`railway services` → stop in dashboard); avoid running tests against production DB.

---

## Troubleshooting

**Build fails**

```bash
railway logs
# Look for: missing env var, Dockerfile error, runtime mismatch with .github/dev-specs.md
```

**App crashes after deploy**

```bash
railway logs -f
# Common: missing DB migration, missing env var, port mismatch
# Railway sets PORT — the app must read process.env.PORT, not a hardcoded value
```

**DB connection refused**

```bash
railway variables | grep DATABASE_URL
# If missing or wrong, regenerate via dashboard and redeploy
```

**Custom domain not resolving**

- DNS records may take up to 24 h to propagate. The Railway dashboard shows expected vs observed records.

---

## Operational Checklist

- [ ] `railway status` shows the service running
- [ ] `https://[PROJECT_NAME].railway.app` returns 200
- [ ] All variables from [`.ai/config-vars.md`](../../../.ai/config-vars.md) are set in Railway
- [ ] `railway logs` is clean
- [ ] DB backups are enabled (default) and last backup is recent

---

## Next Steps

- Back to LAN dev → [`dev-lan`](../../dev-lan/.ai/instruct.md)
- Public internet self-hosted → [`prod-self-serve`](../../prod-self-serve/.ai/instruct.md)

---

## Resources

- [Railway docs](https://docs.railway.app/)
- [Railway CLI reference](https://docs.railway.app/develop/cli)
- [Railway pricing](https://railway.app/pricing)

---

## Files in This Mode

| File | Purpose |
|---|---|
| `Dockerfile` | Container image definition consumed by Railway |
| `railway.json` (optional) | Railway-specific deploy config (root command, healthcheck path) |
| `.dockerignore` | Excludes dev artefacts from the image |
