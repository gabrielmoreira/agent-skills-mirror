# Conventions — Naming & File Organization

**Scope**: `pds-board-editor/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/conventions.md`](../../.ai/conventions.md)** — This file is authoritative for all directories in this project.

## Project-Specific Rules

### Directory Naming

- Dev documentation: `.dev-docs/`
- AI instructions: `.ai/`

### File Naming

| Context | Case | Example |
|---------|------|---------|
| TypeScript files | `camelCase.ts`, `PascalCase.tsx` | `main.tsx`, `client.ts` |
| Python scripts | `snake_case.py` | `blob_packer.py` |

### Documentation

- User-facing guides: numbered `kebab-case.md`
- Root meta-files: `UPPER-KEBAB-CASE.md`

---

## Code Organization

| Layer | Responsibility |
|-------|----------------|
| `boards/` | Board specification JSON files |
| `css/` | Component styles |
| `js/` | JavaScript utilities |

### Technology Stack

- **Primary**: React 18 + Vite
- **Format**: Single-page application with HTML exports

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
Set-Location "k:\PDS-Master-001\pds-board-editor"
npm install
npm run dev
```

### Production

Builds to `dist/` directory. The generated HTML files are used as standalone web applications.