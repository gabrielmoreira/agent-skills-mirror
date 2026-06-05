# Conventions — Naming & File Organization

**Scope**: `web-firmware-server/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/conventions.md`](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Project-Specific Rules

### Directory Naming

- Dev documentation: `.dev-docs/`
- AI instructions: `.ai/`
- Storage (firmware binaries): `storage/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| TypeScript files | `camelCase.ts`, `PascalCase.tsx` | `main.tsx`, `client.ts` |
| Python scripts | `snake_case.py` | `blob_packer.py` |
| C/C++ headers | `snake_case.h` | `pds_core.h` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `/api/src/` | Express backend, TypeORM entities, migrations |
| `/storage/` | Firmware binaries (gitignored) |

### Database

- **Authoritative source**: `../../db-central/AI-INSTRUCT.md`
- **Owner**: All services share one PostgreSQL database (`pds_marketplace`)
- **Table ownership**: This service owns `firmwares` table only

---

## Credential Management

> **→ Root [`.ai/credentials.md`](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ❌ | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ✅ | Template with placeholder values |

---

## Build & Deployment

### Development

```powershell
Set-Location "k:\PDS-Master-001\WEB-FwServer\api"
npm install
npm run dev
```

Service starts on port `3002`. Requires the same PostgreSQL instance as `WEB-Marketplace` and `WEB-HMI`.

### Production

- Railway: separate service (`fwserver-service`)
- Internal only - NOT public-facing
- Path prefix: none (private network only)