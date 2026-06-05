---
mode: agent
description: Validate port registry against project code. Detect collisions, drift, range violations, unregistered services.
---

# /ai-ports-check — Validate Port Registry

Check if your project's ports are correctly registered and free from conflicts.

## Quick Start

```powershell
# Validate and show report
python .ai/engine/port_validator.py . --report

# Validate and export findings to JSON
python .ai/engine/port_validator.py . --json

# Both report and JSON
python .ai/engine/port_validator.py . --report --json
```

## What It Checks

The validator scans for hardcoded ports in:
- `docker-compose*.yml` files (ports: fields)
- `.env.example`, `.env*` files (PORT_ variables)
- PowerShell and shell scripts (`*.ps1`, `*.sh`)
- Config files (`vite.config.js`, `webpack.config.js`)
- `package.json` scripts

And compares against:
- `.ai/ports.md` registry (authoritative list)
- Port allocation guidelines (3000–3099 for APIs, etc.)

## Findings

### Error (blocks builds)
- **Port Collision**: Two services on same port
  - Action: Manually reassign one service

### Warning (should fix)
- **Range Violation**: Port outside allocation guidelines
  - Action: Reassign to correct range (e.g., 3000–3099)
- **Orphaned Entry**: Registry entry with no code
  - Action: Remove from registry or add service

### Info (optional)
- **Unregistered Service**: Service in code but not in registry
  - Action: Add to registry or confirm it's external

## Creating the Registry

If `.ai/ports.md` doesn't exist, create it:

```powershell
# Copy the template
Copy-Item .ai/ports.example.md .ai/ports.md

# Edit with your services
code .ai/ports.md
```

## Registry Format

The registry is a markdown table in `.ai/ports.md`:

```markdown
| Service/Component | Port | Protocol | Environment | Notes |
|---|---|---|---|---|
| Backend API | 3001 | HTTP | dev | Express server |
| Frontend (Vite) | 5173 | HTTP | dev | React + HMR |
| PostgreSQL | 5432 | TCP | dev | Shared database |
```

**Key rules:**
- One service per port (no collisions)
- Keep descriptions brief (1 line)
- Follow allocation guidelines:
  - 3000–3099: Primary Backend APIs
  - 3100–3199: Secondary/Auxiliary APIs
  - 3300–3399: Real-time Services (WebSockets, gRPC)
  - 5000–5099: Databases
  - 5100–5199: Cache (Redis, etc.)
  - 5173–5273: Frontend Dev Servers
  - 8000–8099: Admin/Debug Tools

## Multi-Service Projects

If your project has multiple services (Node.js backend, Python API, React frontend, databases):

1. **Document all services** in `.ai/ports.md`
2. **Create launch script** (e.g., `.github/scripts/dev-launch.ps1`) that starts them in order
3. **Run validator** to confirm no conflicts
4. **Share with team** (commit `.ai/ports.md`; never commit live `.env`)

Example launch script:

```powershell
# .github/scripts/dev-launch.ps1

# Terminal 1: Database (PostgreSQL)
Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd db; docker-compose up'

# Terminal 2: Backend API
Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd api; npm run dev'

# Terminal 3: Frontend
Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd web; npm run dev'

Write-Host "All services launched. See .ai/ports.md for port assignments."
```

## Integration with Import Tool

When importing a project via `/ai-import-project`, the fixer will:
1. Create `.ai/ports.md` if missing
2. Scan for hardcoded ports
3. Run `/ai-ports-check` to detect collisions early

If collisions are found, the import **pauses** and requires manual port reassignment.

## Deployment Modes

If your project uses deployment modes (`.deployment/dev-local/`, `.deployment/prod-railway/`, etc.):

Each mode can have its own port registry:

```
.deployment/dev-local/.ai/ports.md       ← localhost ports
.deployment/prod-railway/.ai/ports.md    ← Railway/cloud ports
```

The validator checks both when in mode-specific directories.

## See Also

- [`.ai/ports.md`](../../.ai/ports.md) — Port registry template
- [`.github/agents/pds-man-ports.agent.md`](../agents/pds-man-ports.agent.md) — Port manager agent
- [`.ai/engine/port_validator.py`](../../.ai/engine/port_validator.py) — Validator implementation
