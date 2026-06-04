# Deployment Mode: `dev-local`

**Scope**: Authoritative for all work when `DEPLOY_MODE=dev-local`
**Last Updated**: 2026-06-03

> **Authority**: DEEP — when this mode is active, this file is authoritative over the parent `.ai/instruct.md`. See [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) for the depth-priority hierarchy and [`../README.md`](../../README.md) for the deployment-mode convention.

---

## Contents

| Section | What's here |
|---|---|
| [Mode Overview](#mode-overview) | What `dev-local` is and when to use it |
| [Prerequisites](#prerequisites) | Required tools and setup |
| [Quick Start](#quick-start) | Get services running |
| [What Runs](#what-runs) | Services and ports |
| [Access URLs](#access-urls) | How to reach each service |
| [Environment Configuration](#environment-configuration) | `.env` keys for this mode |
| [Operational Tasks](#operational-tasks) | Common day-to-day commands |
| [Security Notes](#security-notes) | Threat model and limits |
| [Troubleshooting](#troubleshooting) | Common issues and fixes |
| [Operational Checklist](#operational-checklist) | Mode-switch checklist |
| [Next Steps](#next-steps) | What to do after setup |
| [Files in This Mode](#files-in-this-mode) | What lives in this directory |

## Mode Overview

`dev-local` is pure local development — every service runs on the developer's machine. HTTP only, no network exposure, no TLS.

| Aspect | Value |
|---|---|
| **Primary URL** | `http://localhost:[FRONTEND_PORT]` |
| **Access** | Localhost only |
| **TLS** | None (HTTP) |
| **Database** | `[DB_ENGINE]` in Docker (exposed on `localhost:[DB_PORT]`) |
| **Reverse proxy** | None |
| **Use case** | Daily development, debugging, fast iteration |
| **Setup time** | < 2 minutes |
| **Cost** | $0 |

---

## Prerequisites

- [ ] `[RUNTIME]` installed (version per [`.github/dev-specs.md`](../../../.github/dev-specs.md))
- [ ] Docker Desktop running (only if a containerized DB is used)
- [ ] Repository cloned and dependencies installed (`[INSTALL_COMMAND]`)
- [ ] `.env` file present per [`.ai/credentials.md`](../../../.ai/credentials.md)

---

## Quick Start

```[SHELL]
# 1. Set the mode
[SET_ENV] DEPLOY_MODE=dev-local

# 2. Start the database (if applicable)
docker compose -f [DEV_COMPOSE_FILE] up -d db

# 3. Start the app
[DEV_START_COMMAND]
```

Terminate with `Ctrl+C` for the app, `docker compose -f [DEV_COMPOSE_FILE] down` for the database.

---

## What Runs

| Service | Technology | Access | Port |
|---|---|---|---|
| Frontend | `[FRONTEND_FRAMEWORK]` | Localhost | `[FRONTEND_PORT]` |
| API | `[BACKEND_FRAMEWORK]` | Localhost | `[BACKEND_PORT]` |
| Database | `[DB_ENGINE]` (Docker) | Localhost (exposed) | `[DB_PORT]` |
| Reverse proxy | (not used) | — | — |

---

## Access URLs

- **Frontend**: `http://localhost:[FRONTEND_PORT]`
- **API**: `http://localhost:[BACKEND_PORT]`
- **Database**: `[DB_PROTOCOL]://localhost:[DB_PORT]` (credentials from `.env`)

---

## Environment Configuration

`.env` template (commit `.env.example`, never `.env` per [`.ai/credentials.md`](../../../.ai/credentials.md)):

```env
DEPLOY_MODE=dev-local
NODE_ENV=development          # if Node.js
PORT=[BACKEND_PORT]
DATABASE_URL=[DB_PROTOCOL]://[DB_USER]:[DB_PASSWORD]@localhost:[DB_PORT]/[DB_NAME]
JWT_SECRET=[GENERATE_LOCALLY]
# Add other vars from .ai/config-vars.md as needed
```

Secrets in this file stay local. Generate `JWT_SECRET` with `[SECRET_GEN_COMMAND]`.

---

## Operational Tasks

### View logs

App logs print directly to the terminal running `[DEV_START_COMMAND]`. Database logs:

```bash
docker compose -f [DEV_COMPOSE_FILE] logs -f db
```

### Connect to the database

```bash
docker compose -f [DEV_COMPOSE_FILE] exec db [DB_CLIENT_COMMAND]
```

### Reset the database (⚠️ data loss — see [`.ai/maintenance.md`](../../../.ai/maintenance.md))

```bash
docker compose -f [DEV_COMPOSE_FILE] down -v
docker compose -f [DEV_COMPOSE_FILE] up -d db
```

### Hot reload

`[DEV_START_COMMAND]` runs in watch mode by default; saving a source file triggers a reload.

---

## Security Notes

- HTTP only — never expose this mode to the LAN or internet.
- The exposed database port is for developer convenience; remove the port mapping in `[DEV_COMPOSE_FILE]` if multiple developers share a machine.
- All secrets live in `.env`; the file is gitignored.

---

## Troubleshooting

**Port already in use**

```powershell
# Windows
netstat -ano | findstr :[FRONTEND_PORT]
taskkill /PID <pid> /F
```

```bash
# POSIX
lsof -i :[FRONTEND_PORT]
kill <pid>
```

**Dependencies missing** — re-run `[INSTALL_COMMAND]` from each module root.

**Database connection refused** — confirm Docker is running, then `docker compose -f [DEV_COMPOSE_FILE] up -d db` and wait a few seconds before retrying.

---

## Operational Checklist

- [ ] `DEPLOY_MODE=dev-local` is set in the current shell
- [ ] `[DEV_COMPOSE_FILE]` is up: `docker compose -f [DEV_COMPOSE_FILE] ps`
- [ ] App responds at `http://localhost:[FRONTEND_PORT]`
- [ ] API responds at `http://localhost:[BACKEND_PORT]`
- [ ] No errors in app or database logs

---

## Next Steps

- LAN sharing with self-signed HTTPS → [`dev-lan`](../../dev-lan/.ai/instruct.md)
- Managed cloud → [`prod-railway`](../../prod-railway/.ai/instruct.md)
- Public internet, self-hosted → [`prod-self-serve`](../../prod-self-serve/.ai/instruct.md)

---

## Files in This Mode

| File | Purpose |
|---|---|
| `[DEV_COMPOSE_FILE]` | Dev-only database container |
| `.env.example` | Environment template (committed) |
| `.env` | Local secrets (gitignored) |
| `[DEV_LAUNCHER_SCRIPT]` (optional) | One-shot launcher script |
