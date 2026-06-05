# Maintenance — Archive, Never-Delete, and Database Safety Rules

**Scope**: `web-marketplace/` module reference
**Last Updated**: 2026-05-27

> **→ Root [`.ai/maintenance.md`](../../.ai/maintenance.md)** — This file is authoritative for all directories in this project.

## What AI Can Do Without Asking

These are pre-approved local, reversible actions — no confirmation needed:

| Action | Notes |
|--------|-------|
| Read any file | Always safe |
| Create new files | Safe; creation is reversible by deletion |
| Edit existing files | Safe for source/config; always show diff |
| Move files to `.archive/` or `.dev-docs/.old/` | Safe; reversible |
| Update `Last Updated` date in `.ai/instruct.md` files | Pre-approved; part of every instruction file edit |
| Run read-only terminal commands (`ls`, `cat`, `grep`) | Safe |

## What Requires Confirmation

| Action | Why |
|--------|-----|
| Deleting any file permanently | Irreversible |
| Running database migration rollbacks | Data loss risk |
| `docker-compose down -v` | Destroys volumes |
| `git push --force` | Affects shared history |
| Dropping or truncating tables | Data loss |

---

## Archive Pattern

All archived content lives under `.archive/`. Use **path mirroring** to preserve original structure:

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
- Creating new databases/schemas

Always ask before:
- Dropping/truncating tables
- Running migration rollbacks
- Removing Docker volumes