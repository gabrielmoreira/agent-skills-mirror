# Maintenance — Archive, Never-Delete, and Database Safety Rules

**Scope**: `web-firmware-server/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/maintenance.md`](../../.ai/maintenance.md)** — This file is authoritative for all directories in this project.

## What AI Can Do Without Asking

| Action | Notes |
|--------|-------|
| Read any file | Always safe |
| Create new files | Safe; creation is reversible by deletion |
| Edit existing files | Safe for source/config; always show diff |
| Move files to `.archive/` or `.dev-docs/.old/` | Safe; reversible |

## What Requires Confirmation

| Action | Why |
|--------|-----|
| Deleting any file permanently | Irreversible |
| Running database migration rollbacks | Data loss risk |
| `docker-compose down -v` | Destroys volumes |
| `git push --force` | Affects shared history |

---

## Archive Pattern

All archived content lives under `.archive/`. Use **path mirroring**:

```
.archive/[original-path]
```

For date-prefixed snapshots:

```
.archive/YYYYMMDD/[original-path]
```

---

## Never Reset Databases

**Never drop, truncate, or reset a database without explicit written confirmation from the user.**

Safe operations:
- `SELECT` queries
- Forward migrations (adding tables/columns)

Always ask before:
- Dropping/truncating tables
- Running migration rollbacks