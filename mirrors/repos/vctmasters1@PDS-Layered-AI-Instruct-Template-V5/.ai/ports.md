# Port Registry — Service Port Allocation

> **Authority**: This file is the single source of truth for all service ports in this project.
>
> **Maintenance**: When adding a new service or changing a port, update this file **first**, then update the service configuration. The [`pds-man-ports`](../.github/agents/pds-man-ports.agent.md) agent watches for drift.

---

## Contents

| Section | What's here |
|---------|-------------|
| [Quick Reference](#quick-reference) | At-a-glance port list |
| [Development Environment Ports](#development-environment-ports) | Local dev allocations |
| [Production Environment Ports](#production-environment-ports) | Production allocations |
| [Port Allocation Guidelines](#port-allocation-guidelines) | Ranges and conflicts |
| [Proxy Routes (if applicable)](#proxy-routes-if-applicable) | Reverse-proxy mapping |
| [Local Development Launch Commands](#local-development-launch-commands) | How to start services |
| [Environment-Specific Configuration](#environment-specific-configuration) | Per-env overrides |
| [Validation & Drift Detection](#validation--drift-detection) | Agent automation |
| [Notes](#notes) | Additional context |

---

## Quick Reference

| Service/Component | Port | Protocol | Environment | Notes |
|---|---|---|---|---|
| *Add rows below* | | | | |

---

## Development Environment Ports

### Frontend (UI Layer)

| Service | Port | Type | Notes |
|---|---|---|---|
| Main App (if Vite/React) | *port* | HTTP | Dev server with hot reload |

### Backend APIs

| Service | Port | Type | Notes |
|---|---|---|---|
| *Add your backend services* | *port* | HTTP/gRPC | Description |

### Databases & Cache

| Service | Port | Type | Notes |
|---|---|---|---|
| PostgreSQL (if used) | 5432 | TCP | Default shared DB |
| Redis (if used) | 6379 | TCP | Optional caching/sessions |
| MongoDB (if used) | 27017 | TCP | If document DB used |

### Special Services

| Service | Port | Type | Notes |
|---|---|---|---|
| *WebSockets, real-time, etc.* | *port* | WSS/TCP | Low-latency services |

---

## Production Environment Ports

| Service | Port | Platform | Notes |
|---|---|---|---|
| *Same as above, but deployed to cloud* | *port* | Railway/AWS/GCP | Use environment variables, not hardcoded |

---

## Port Allocation Guidelines

Reserve ranges to prevent collisions:

| Range | Service Type | Usage |
|---|---|---|
| 3000–3099 | Primary Backend APIs | Express, FastAPI, etc. |
| 3100–3199 | Secondary/Auxiliary APIs | Worker services, webhooks |
| 3300–3399 | Real-time Services | WebSockets, gRPC, signaling |
| 5000–5099 | Databases | PostgreSQL, SQLite, etc. |
| 5100–5199 | Cache Layers | Redis, Memcached |
| 5173–5273 | Frontend Dev Servers | Vite, Webpack, etc. |
| 8000–8099 | Admin/Debug Tools | Swagger UI, GraphQL Playground, monitoring |

---

## Proxy Routes (if applicable)

Document proxy setups here (e.g., Vite dev server proxying to backend APIs):

```
Frontend (http://localhost:5173)
  /api/*        → http://localhost:3000  (main backend)
  /workers/*    → http://localhost:3100  (worker service)
  /ws/*         → ws://localhost:3300    (real-time)
```

---

## Local Development Launch Commands

If your project has multiple services, document the startup sequence:

```bash
# Terminal 1: Backend
npm run dev --cwd api/

# Terminal 2: Frontend
npm run dev --cwd web/

# Terminal 3: Workers (if applicable)
npm run dev --cwd workers/
```

Or use a launch script (if available):
```bash
pwsh .github/scripts/dev-launch.ps1
```

---

## Environment-Specific Configuration

If you use deployment modes, each mode may have different ports:

### `.deployment/dev-local/.ai/ports.md`
All ports are on localhost; no TLS needed.

### `.deployment/prod-railway/.ai/ports.md`
Services run on Railway; use environment variables for port discovery.

---

## Validation & Drift Detection

The [`pds-man-ports`](../.github/agents/pds-man-ports.agent.md) agent automatically:

- ✓ Scans `docker-compose.yml`, `.env.example`, scripts for hardcoded ports
- ✓ Detects port conflicts (same port assigned to multiple services)
- ✓ Warns if ports are outside allocation ranges
- ✓ Finds new services not yet in this registry
- ✓ Reports divergence (e.g., code says port 3001 but registry says 3000)

**To manually validate:**
```powershell
python .ai/engine/port_validator.py .
```

---

## Notes

- **Dev vs. Prod**: Development uses hardcoded localhost ports; production uses environment variables
- **Conflicts**: Always check this file before assigning a new port
- **Documentation**: Keep descriptions brief but clear (1 line per service)
- **Changes**: Update this file, commit, then notify the team (if shared project)
