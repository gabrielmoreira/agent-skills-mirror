# Conventions — Naming & File Organization

**Scope**: `web-marketplace/` module reference
**Last Updated**: 2026-05-27

> **? Root [``.ai/conventions.md``](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Contents

| Section | Description |
|---------|-------------|
| [Project-Specific Rules](#project-specific-rules) | Directory naming, file naming, and documentation conventions for web-marketplace module |
| [Code Organization](#code-organization) | Layer structure including /api/src/ and /frontend/src/ directories |
| [Credential Management](#credential-management) | Guidelines for handling secrets and credential files |
| [Build & Deployment](#build--deployment) | Development and production deployment processes |
| [Search Sort Order](#search-sort-order) | Search results default to distance-first ordering |

## Project-Specific Rules

### Directory Naming

- All modules use `kebab-case` directory names
- Dev documentation: ``.dev-docs/`
- AI instructions: ``.ai/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| TypeScript files | `camelCase.ts`, `PascalCase.tsx` | `main.tsx`, `client.ts` |
| Python scripts | `snake_case.py` | `blob_packer.py` |
| C/C++ headers | `snake_case.h` | `pds_core.h` |

### Documentation

- User-facing guides: numbered `kebab-case.md` (`01-getting-started.md`)
- Root meta-files: `UPPER-KEBAB-CASE.md` (`CHANGELOG.md`, `README.md`)

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `/api/src/` | Express backend, TypeORM entities, migrations |
| `/frontend/src/` | React 18 SPA with TypeScript |

### Database

- **Authoritative source**: `../../db-central/AI-INSTRUCT.md`
- **Owner**: All services share one PostgreSQL database (`pds_marketplace`)
- **Entities**: `User`, `Designer`, `Producer`, `Product`, `Service`, `Order`, `Bid`, etc.

---

## Credential Management

> **? Root [``.ai/credentials.md``](../../.ai/credentials.md)** — Global credential rules apply.

| File | Commit? | Notes |
|------|---------|-------|
| `.env` | ? | Secrets (DATABASE_URL, JWT_SECRET) |
| `.env.example` | ? | Template with placeholder values |
| `.gitignore` | ? | Must include `*.local.*` pattern |

---

## Build & Deployment

### Development

```powershell
# Backend API (port 3000)
Set-Location "k:\PDS-Master-001\web-marketplace\api
npm install
npm run dev

# Frontend (Vite dev server, port 5174)
Set-Location k:\PDS-Master-001\web-marketplace\frontend
npm install
npm run dev
```

### Production

- Railway: single monolithic service (`web-marketplace/api`)
- Frontend built with Vite and served via `express.static`
- Path prefix: `/marketplace` (frontend), `/marketplace/api` (API)

---

## Search Sort Order

**All creator, product, and materials search results default to distance-first** whenever user location is available.

See root ``.ai/instruct.md`` for full implementation details.

