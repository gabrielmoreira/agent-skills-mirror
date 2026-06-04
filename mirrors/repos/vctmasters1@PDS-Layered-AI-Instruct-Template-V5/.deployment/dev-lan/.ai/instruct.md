# Deployment Mode: `dev-lan`

**Scope**: Authoritative for all work when `DEPLOY_MODE=dev-lan`
**Last Updated**: 2026-06-03

> **Authority**: DEEP — when this mode is active, this file is authoritative over the parent `.ai/instruct.md`. See [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) for the depth-priority hierarchy and [`../README.md`](../../README.md) for the deployment-mode convention.

---

## Contents

| Section | What's here |
|---|---|
| [Mode Overview](#mode-overview) | What `dev-lan` is and when to use it |
| [Prerequisites](#prerequisites) | Required tools and setup |
| [Quick Start](#quick-start) | Get the stack running |
| [What Runs](#what-runs) | Services and containers |
| [Access URLs](#access-urls) | How to reach each service |
| [Environment Configuration](#environment-configuration) | `.env` keys for this mode |
| [TLS Certificate](#tls-certificate) | Self-signed cert generation and trust |
| [Sharing on the LAN](#sharing-on-the-lan) | Multi-machine access |
| [Operational Tasks](#operational-tasks) | Common day-to-day commands |
| [Security Notes](#security-notes) | Threat model and limits |
| [Troubleshooting](#troubleshooting) | Common issues and fixes |
| [Operational Checklist](#operational-checklist) | Mode-switch checklist |
| [Next Steps](#next-steps) | What to do after setup |
| [Files in This Mode](#files-in-this-mode) | What lives in this directory |

## Mode Overview

`dev-lan` is pseudo-production on the developer's local network — the full Docker stack runs behind a reverse proxy with a self-signed HTTPS certificate. Browsers warn once, then trust the cert per machine.

| Aspect | Value |
|---|---|
| **Primary URL** | `https://[LAN_IP_OR_HOSTNAME]` |
| **Access** | LAN only (or external if port-forwarded) |
| **TLS** | Self-signed (auto-generated, 365-day) |
| **Database** | `[DB_ENGINE]` in Docker (internal only) |
| **Reverse proxy** | Caddy |
| **Use case** | Share with a few people on the same network |
| **Setup time** | ~5 minutes (includes cert generation) |
| **Cost** | $0 |

---

## Prerequisites

- [ ] Docker Desktop running
- [ ] Workstation reachable on the LAN at `[LAN_IP_OR_HOSTNAME]`
- [ ] Ports 80 and 443 free on the workstation
- [ ] `.env` file present per [`.ai/credentials.md`](../../../.ai/credentials.md)
- [ ] Firewall allows inbound TCP 80 and 443

---

## Quick Start

```[SHELL]
# 1. Set the mode
[SET_ENV] DEPLOY_MODE=dev-lan

# 2. Bring up the stack (Caddy generates the self-signed cert on first run)
docker compose up -d

# 3. Confirm
docker compose ps
```

The first request to `https://[LAN_IP_OR_HOSTNAME]` shows a "Your connection is not private" warning — that is expected. Click *Advanced → Proceed*; the cert is then trusted on that machine.

---

## What Runs

| Service | Technology | Access | Port |
|---|---|---|---|
| Frontend | `[FRONTEND_FRAMEWORK]` (built) | Caddy | — |
| API | `[BACKEND_FRAMEWORK]` | Caddy | `[BACKEND_PORT]` (internal) |
| Database | `[DB_ENGINE]` | Internal | `[DB_PORT]` (internal) |
| Reverse proxy | `caddy:2-alpine` | Public on LAN | 443 (HTTPS) + 80 (HTTP→HTTPS redirect) |

---

## Access URLs

- **HTTPS (LAN IP)**: `https://[LAN_IP]`
- **HTTPS (hostname)**: `https://[LAN_HOSTNAME]` (requires entry in viewer's hosts file or LAN DNS)
- **HTTP redirect**: `http://[LAN_IP_OR_HOSTNAME]` → `https://...`

---

## Environment Configuration

```env
DEPLOY_MODE=dev-lan
NODE_ENV=production
PORT=[BACKEND_PORT]
DATABASE_URL=[DB_PROTOCOL]://[DB_USER]:[DB_PASSWORD]@db:[DB_PORT]/[DB_NAME]
JWT_SECRET=[GENERATE_LOCALLY]
LAN_IP=[LAN_IP]
POSTGRES_PASSWORD=[STRONG_PASSWORD]
```

---

## TLS Certificate

- **Location**: `[CERT_DIR]/cert.pem`, `[CERT_DIR]/key.pem`
- **Generated**: On first start (if missing) — see `[CERT_GEN_SCRIPT]` if a manual generator is preferred
- **Validity**: 365 days
- **Regenerate**: delete `[CERT_DIR]/` and restart the stack

---

## Sharing on the LAN

Other machines on the same network reach the app at `https://[LAN_IP]`. They will see the self-signed warning on first visit; the cert is trusted per browser/profile after acceptance.

For limited external access without setting up DDNS:

1. Forward router external 443 → workstation `[LAN_IP]:443`
2. Share `https://<your-public-ip>` (the cert warning still appears).

For proper public deployment, switch to [`prod-self-serve`](../../prod-self-serve/.ai/instruct.md) (DDNS + Let's Encrypt) or [`prod-railway`](../../prod-railway/.ai/instruct.md) (managed cloud).

---

## Operational Tasks

### View logs

```bash
docker compose logs -f app      # API
docker compose logs -f caddy    # Reverse proxy
docker compose logs -f db       # Database
```

### Restart a single service

```bash
docker compose restart app
```

### Connect to the database

```bash
docker compose exec db [DB_CLIENT_COMMAND]
```

### Stop the stack

```bash
docker compose down              # data persists
docker compose down -v           # ⚠️ removes volumes (database wiped) — see .ai/maintenance.md
```

---

## Security Notes

- The API (`[BACKEND_PORT]`) and database are not exposed outside the Docker network — Caddy is the only public surface.
- Self-signed certs do not protect against MITM by anyone with LAN access; treat this mode as **trusted-network development**, not production.
- Never reuse `dev-lan` `JWT_SECRET` values in `prod-*` modes.

---

## Troubleshooting

**Cert not trusted after acceptance**

- Clear the browser cache or open in private/incognito.
- Regenerate: delete `[CERT_DIR]/` and restart.

**External users cannot connect**

- Verify port forward at the router: external 443 → `[LAN_IP]:443`.
- Verify the host firewall allows inbound TCP 80 and 443.
- `docker compose logs caddy` should show requests arriving.

**Cannot reach from another LAN machine**

```powershell
# Confirm the workstation IP
ipconfig | findstr "IPv4 Address"

# Confirm Caddy is listening
netstat -ano | findstr :443
```

---

## Operational Checklist

- [ ] `DEPLOY_MODE=dev-lan` set in the active shell
- [ ] `docker compose ps` shows `db`, `app`, `caddy` healthy
- [ ] Cert files present at `[CERT_DIR]/`
- [ ] `https://[LAN_IP]` loads after one-time accept
- [ ] HTTP redirects to HTTPS
- [ ] No errors in `docker compose logs caddy`

---

## Next Steps

- Back to local-only → [`dev-local`](../../dev-local/.ai/instruct.md)
- Public internet (managed) → [`prod-railway`](../../prod-railway/.ai/instruct.md)
- Public internet (self-hosted, real cert) → [`prod-self-serve`](../../prod-self-serve/.ai/instruct.md)

---

## Files in This Mode

| File | Purpose |
|---|---|
| `docker-compose.yml` | Full stack (db, app, caddy) |
| `[CADDYFILE_LAN]` | LAN reverse-proxy + self-signed cert config |
| `[CERT_DIR]/` | Generated certificate storage |
| `.env` | LAN-specific secrets (gitignored) |
| `[DEV_LAUNCHER_SCRIPT]` (optional) | One-shot launcher script |
