# web-gateway - Nginx Reverse Proxy 
 
**Authority**: DEEP - Authoritative for all work inside `web-gateway/`** 
**Last Updated**: 2026-05-28
 
> **Railway topology**: This is the single public Railway service for `pipedreamsystems.com`. All web-* services except WEB-FwServer are routed through here. WEB-FwServer is **not** in the gateway — it is accessed internally by other services (WEB-HMI API proxies firmware downloads to devices via the internal secret bypass). All services share Railway private networking; host/port for each service is set via Railway env vars (see Environment Variables below).

## Routing Table

| Public URL prefix      | Strips prefix | Routes to             | Notes                              |
|------------------------|---------------|-----------------------|------------------------------------|
| `/hmi/api/`            | Yes           | hmi-service `/`       | HMI REST API; WebSocket upgrade    |
| `/hmi/`                | Yes           | hmi-service `/`       | React SPA static assets            |
| `/marketplace/api/`    | Yes           | marketplace-service `/` | Marketplace REST + Socket.IO    |
| `/marketplace/`        | Yes           | marketplace-service `/` | Vanilla JS static assets        |
| `/health`              | —             | Nginx itself          | Railway health check               |
| `/`                    | —             | 302 → `/marketplace/` | Root redirect                      |

FwServer is **not** in the gateway — it is accessed internally by other services only.

## How It Works

Nginx starts from `nginx.conf.template`. The container CMD runs `envsubst` to substitute `${HMI_HOST}`, `${HMI_PORT}`, `${MKT_HOST}`, `${MKT_PORT}` into the template, producing `/etc/nginx/nginx.conf`, then starts Nginx.

The envsubst variable list is explicit — nginx's own variables (`$host`, `$remote_addr`, etc.) are **not** in the list and are therefore left untouched.

## Environment Variables

Set these in the Railway dashboard after enabling **Private Networking** on all services:

| Variable   | Example value                          | Where to find |
|------------|----------------------------------------|---------------|
| `HMI_HOST` | `hmi-service.railway.internal`         | Railway → hmi-service → Networking tab |
| `HMI_PORT` | `3001`                                 | Railway → hmi-service → Networking tab |
| `MKT_HOST` | `marketplace-service.railway.internal` | Railway → marketplace-service → Networking tab |
| `MKT_PORT` | `3000`                                 | Railway → marketplace-service → Networking tab |

## Adding a New Route

1. Add the new `location` block(s) to `nginx.conf.template`
2. Add new `${NEW_VAR}` placeholders for the new service's host/port
3. Update the envsubst variable list in `Dockerfile` CMD
4. Update the Railway dashboard with the new env vars
5. Update this file's routing table

---

## Local Dev Stack

The full local production stack (Nginx + 3 APIs + Postgres) is orchestrated via `docker-compose.dev.yml`. This is the canonical way to run the web components locally.

### Start

```powershell
cd k:\PDS-Master-001\web-gateway
docker compose -f docker-compose.dev.yml up --build    # first run or after code changes
docker compose -f docker-compose.dev.yml up            # start without rebuilding
```

Nginx listens on port 80. Open `http://localhost` — the root redirects to `/marketplace/`.

### Stop

```powershell
docker compose -f docker-compose.dev.yml down          # stop containers
docker compose -f docker-compose.dev.yml down -v       # also delete DB volume (fresh start)
```

### Build Paradigm

**All three API images build from source inside Docker via `npm ci + tsc`.** No pre-built artifacts are needed on the host.

- Build context is the monorepo root (`..` relative to `web-gateway/`).
- Each Dockerfile uses a multi-stage build: `builder` stage runs `npm ci` + `npm run build`, the runtime stage copies only the outputs.
- Native addons (`bcrypt` in HMI + Marketplace; `sharp` in Marketplace) compile fresh on Linux Alpine — no Windows binary issues.
- React/Vite frontends also build inside Docker (`npm ci && npm run build`).
- This matches Railway's Nixpacks build exactly. A build that works locally here will work on Railway.

**Why not copy host node_modules?** Windows-compiled native addons (`.node` files) are not runnable on Linux Alpine. There's no reliable way to patch them post-hoc. Building from source inside Docker is the only approach that's correct, portable, and doesn't require patching.

**Build times are longer** (3–10 min for full `--build --no-cache` depending on hardware). Docker layer caching makes subsequent builds fast — only layers after a changed `package.json` or `src/` are rebuilt.

### Service Layout

| Service name | Port (internal) | Notes |
|---|---|---|
| `db` | 5432 | Postgres 16 Alpine; volume `dev-pgdata` |
| `hmi-api` | 3001 | WEB-HMI API; TypeORM auto-syncs schema on first start |
| `marketplace-api` | 3000 | WEB-Marketplace API; TypeORM auto-syncs schema on first start |
| `fwserver-api` | 3002 | WEB-FirmwareServer API; standalone (no db-central) |
| `gateway` | 80 (host) | Nginx reverse proxy |

### First-Start DB Bootstrap

On first start against a fresh `dev-pgdata` volume:
- TypeORM `synchronize: true` (active when `NODE_ENV=development`) auto-creates all tables.
- No manual schema step needed.
- To create a dev user:

```powershell
# Generate bcrypt hash for password "PdsLocal!Dev1"
docker exec web-gateway-marketplace-api-1 node -e "require('bcrypt').hash('PdsLocal!Dev1', 10).then(h => console.log(h))"
# Copy the hash, then insert the user (replace <hash> below)
docker exec web-gateway-db-1 psql -U pds -d pds_marketplace -c "INSERT INTO users (email, password, role) VALUES ('dev@pds.local', '<hash>', 'admin');"
```

### Environment

All three APIs run with `NODE_ENV=development` in the local stack. This:
- Disables SSL enforcement on Postgres connections (plain dev Postgres has no TLS)
- Skips the Stripe secret key check in Marketplace
- Enables TypeORM `synchronize` (auto-creates/updates tables)

Do **not** change this to `production` locally — it will fail without real SSL + Stripe keys.

### Volume Isolation

`dev-pgdata` is completely isolated from `api_pgdata` (the old standalone `pds-marketplace-db` container). Deleting the dev stack or its volume has no effect on any other local data.

### Key @db-central Resolution

`@db-central` is not a package.json dependency. It is resolved:
- **At compile time**: tsconfig `paths` → `../../db-central/src/*` (TypeScript finds source files)
- **At runtime**: `module-alias` in package.json `_moduleAliases` → `../../db-central/dist`

The Dockerfiles preserve this directory layout:
```
/workspace/
  db-central/dist/            ← runtime target of @db-central alias
  web-hmi/api/dist/           ← __dirname at runtime (module-alias uses process.cwd)
  web-marketplace/api/dist/
```

### @pds/pipeline Resolution (HMI only)

`pds-pipeline` is a `file:../../pds-pipeline` dep in `web-hmi/api/package.json`. During `npm ci` inside Docker, npm resolves this path against the monorepo root (the build context), finds `/workspace/pds-pipeline/`, and installs it as a real directory (not a symlink). No special Dockerfile handling needed.

**Last Updated**: 2026-05-28
