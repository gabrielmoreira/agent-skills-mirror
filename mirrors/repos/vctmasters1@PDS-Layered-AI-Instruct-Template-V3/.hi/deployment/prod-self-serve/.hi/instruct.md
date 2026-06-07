# Deployment Mode: `prod-self-serve`

**Scope**: Authoritative for all work when `DEPLOY_MODE=prod-self-serve`
**Last Updated**: 2026-06-03

> **Authority**: DEEP — when this mode is active, this file is authoritative over the parent `.ai/instruct.md`. See [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) for the depth-priority hierarchy and [`../README.md`](../../README.md) for the deployment-mode convention.

---

## Contents

| Section | What's here |
|---|---|
| [Mode Overview](#mode-overview) | What `prod-self-serve` is and when to use it |
| [Prerequisites](#prerequisites) | Required hardware and accounts |
| [Quick Start](#quick-start) | First-time deploy |
| [What Runs](#what-runs) | Services and containers |
| [Access URLs](#access-urls) | Public-facing URLs |
| [TLS Certificate Management](#tls-certificate-management) | Let's Encrypt auto-renewal |
| [DDNS / IP Management](#ddns--ip-management) | Dynamic DNS configuration |
| [Operational Tasks](#operational-tasks) | Common day-to-day commands |
| [Security Notes](#security-notes) | Threat model and limits |
| [Troubleshooting](#troubleshooting) | Common issues and fixes |
| [Operational Checklist](#operational-checklist) | Mode-switch checklist |
| [Next Steps](#next-steps) | Post-deploy actions |
| [Files in This Mode](#files-in-this-mode) | What lives in this directory |

## Mode Overview

`prod-self-serve` is public-internet deployment on hardware you control, with auto-renewing HTTPS from Let's Encrypt and a Dynamic DNS provider for changing residential/SMB IPs.

| Aspect | Value |
|---|---|
| **Primary URL** | `https://[DDNS_DOMAIN]` |
| **Access** | Public internet |
| **TLS** | Let's Encrypt (auto-renewing, no warnings) |
| **Database** | `[DB_ENGINE]` in Docker (persisted volume) |
| **Reverse proxy** | Caddy |
| **IP management** | DDNS provider (`[DDNS_PROVIDER]`) updated every 5 min |
| **Use case** | Production deployment with proper HTTPS on owned hardware |
| **Setup time** | ~30 minutes (DDNS + router + first cert) |
| **Cost** | $0 software (DDNS free tier); your hardware + bandwidth |

---

## Prerequisites

- [ ] Static or DDNS-capable public IP (most home/SMB ISPs qualify)
- [ ] DDNS account at `[DDNS_PROVIDER]` (free tiers exist at Dynu, DuckDNS, No-IP, Cloudflare)
- [ ] DDNS hostname registered (e.g., `[DDNS_DOMAIN]`)
- [ ] Router admin access (to forward ports 80 + 443)
- [ ] Workstation/server with Docker Desktop or Docker Engine running
- [ ] Ports 80 and 443 reachable from the public internet

---

## Quick Start

### 1. Configure DDNS

1. Sign up at `[DDNS_PROVIDER]`.
2. Register or claim the hostname `[DDNS_DOMAIN]`.
3. Generate an API token (used by the auto-update script).

### 2. Configure `.env`

```env
DEPLOY_MODE=prod-self-serve
NODE_ENV=production
PORT=[BACKEND_PORT]
DATABASE_URL=[DB_PROTOCOL]://[DB_USER]:[DB_PASSWORD]@db:[DB_PORT]/[DB_NAME]
JWT_SECRET=[GENERATED_HEX]
POSTGRES_PASSWORD=[STRONG_PASSWORD]
DDNS_DOMAIN=[DDNS_DOMAIN]
DDNS_TOKEN=[DDNS_API_TOKEN]
```

Generate `JWT_SECRET`:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
# or
python -c "import secrets; print(secrets.token_hex(48))"
```

### 3. Forward router ports

In the router admin (typically `http://192.168.1.1`):

```
External 80   → [LAN_IP]:80
External 443  → [LAN_IP]:443
```

### 4. Start the stack

```[SHELL]
[SET_ENV] DEPLOY_MODE=prod-self-serve
docker compose up -d
docker compose logs caddy   # watch the first Let's Encrypt request
```

Caddy issues a real cert on first run (10–30 s) using the HTTP-01 challenge — port 80 must be reachable.

### 5. Schedule the DDNS updater (optional but recommended)

```powershell
# Windows
.\[DDNS_UPDATE_SCRIPT] -RegisterTask
```

```bash
# Linux (systemd timer)
sudo cp [DDNS_UPDATE_SCRIPT].service /etc/systemd/system/
sudo systemctl enable --now [DDNS_UPDATE_SCRIPT].timer
```

---

## What Runs

| Service | Technology | Access | Port |
|---|---|---|---|
| Database | `[DB_ENGINE]` | Internal | `[DB_PORT]` |
| API | `[BACKEND_FRAMEWORK]` | Caddy | `[BACKEND_PORT]` (internal) |
| Reverse proxy | `caddy:2-alpine` | Public | 443 (HTTPS) + 80 (HTTP-01 + redirect) |
| Frontend | `[FRONTEND_FRAMEWORK]` (built) | Caddy | — |
| DDNS updater | Script + scheduler | Outbound only | — |

---

## Access URLs

- **HTTPS**: `https://[DDNS_DOMAIN]`  ← share this
- **HTTP**: redirects to HTTPS
- **Direct IP**: works but cert is bound to the DDNS hostname; use the hostname

---

## TLS Certificate Management

Caddy handles everything:

1. Requests a cert from Let's Encrypt before expiration (typically 30 days early).
2. Uses the HTTP-01 challenge (port 80 must be public).
3. Stores certs in the `caddy-data` Docker volume; persists across restarts.

```bash
# Confirm cert
openssl s_client -connect [DDNS_DOMAIN]:443 -servername [DDNS_DOMAIN] </dev/null 2>/dev/null | openssl x509 -noout -dates

# Force a renewal cycle
docker compose exec caddy caddy reload
```

---

## DDNS / IP Management

### Automatic updates

The `[DDNS_UPDATE_SCRIPT]` runs every 5 minutes and updates the registered hostname only when the public IP changes.

```bash
# View the update log
tail -f [DDNS_LOG_FILE]
```

### Manual update

```bash
[DDNS_UPDATE_SCRIPT] --once
```

### Verify DNS

```bash
nslookup [DDNS_DOMAIN]
# Should resolve to the current public IP
```

---

## Operational Tasks

### View logs

```bash
docker compose logs -f app
docker compose logs -f caddy
docker compose logs -f db
```

### Database

```bash
docker compose exec db [DB_CLIENT_COMMAND]
```

### Persistent storage

```bash
docker volume ls | grep [PROJECT_NAME]
# Includes: postgres-data, caddy-data, caddy-config
```

### Stop / restart

```bash
docker compose down                # data persists
docker compose down -v             # ⚠️ destroys volumes — see .ai/maintenance.md
docker compose restart app
```

---

## Security Notes

- The API and database are reachable only from inside the Docker network. Caddy is the only public listener.
- All secrets live in `.env`; treat the file like a private key. `DDNS_TOKEN` is sensitive — leakage allows IP hijack.
- Rotate JWT and DB credentials per [`.ai/credentials.md`](../../../.ai/credentials.md).
- Keep the host OS patched and the Docker daemon updated.

---

## Troubleshooting

**Domain does not resolve**

- `nslookup [DDNS_DOMAIN]` — should show the current public IP.
- Verify the DDNS account is active and the API token is correct.
- Run the updater manually: `[DDNS_UPDATE_SCRIPT] --once`.

**Cert never issued / not renewing**

```bash
docker compose logs caddy | grep -i "lets encrypt\|acme"
```

- Port 80 must be publicly reachable for HTTP-01.
- The DDNS hostname must resolve to the current public IP at challenge time.
- Firewalls (host or router) must not block Let's Encrypt's callback.

**Public IP changed and stale**

- Run the updater manually.
- Confirm the scheduled task / systemd timer is enabled and not failing.

**Users cannot connect**

```bash
docker compose ps
docker compose logs app
nslookup [DDNS_DOMAIN]
curl -sSf https://[DDNS_DOMAIN]/health   # if you have a health endpoint
```

---

## Operational Checklist

- [ ] `nslookup [DDNS_DOMAIN]` returns the current public IP
- [ ] Router forwards external 80 + 443 to `[LAN_IP]`
- [ ] `docker compose ps` shows `db`, `app`, `caddy` healthy
- [ ] Cert valid for ≥30 days: `openssl s_client …` (see above)
- [ ] DDNS updater scheduled and recent in `[DDNS_LOG_FILE]`
- [ ] No app errors in `docker compose logs app`
- [ ] `https://[DDNS_DOMAIN]` loads with no cert warning

---

## Next Steps

- LAN-only dev → [`dev-lan`](../../dev-lan/.ai/instruct.md)
- Managed cloud (no router setup) → [`prod-railway`](../../prod-railway/.ai/instruct.md)

---

## Files in This Mode

| File | Purpose |
|---|---|
| `docker-compose.yml` | Full production stack |
| `[CADDYFILE_PROD]` | Caddy config with `tls [LE_EMAIL]` for Let's Encrypt |
| `[DDNS_UPDATE_SCRIPT]` | DDNS auto-update script |
| `[DDNS_UPDATE_SCRIPT].service`, `.timer` (Linux) | systemd unit files |
| `.env` | Production secrets (gitignored) |
| `[DDNS_LOG_FILE]` | DDNS updater log |
