# Maintenance — Archive, Never-Delete, and Database Safety Rules

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-05-25

> This file is the **single source of truth** for file preservation, archiving, and database safety rules.
> Never duplicate these rules — link here from any `.ai/instruct.md` that needs them.

---

## Contents

| Section | What's here |
|---|-------------|
| [Never Delete Rule](#never-delete-rule) | Why and how to archive instead of deleting |
| [Archive Patterns](#archive-patterns) | Directory and file naming for archives |
| [Never Reset Databases](#never-reset-databases) | Protecting production and development data |
| [Stale Instruction Files](#stale-instruction-files) | How to retire outdated instruction files |
| [What AI Can Do Without Asking](#what-ai-can-do-without-asking) | Pre-approved local reversible actions |

---

## Never Delete Rule

**Never permanently delete project files.** Archive instead.

**Rationale**: Deleted files lose history, context, and recovery paths. The cost of preserved disk space is less than the cost of lost knowledge — especially for a project where AI reads these files as instructions.

| Instead of deleting... | Do this |
|------------------------|---------|
| Any retired source file or subsystem | Move to `.archive/` mirroring the original path |
| Superseded dev docs | Move to `.dev-docs/.old/` |

**AI Rule**: Never use `rm`, `Remove-Item`, `git rm`, `del`, or any destructive file operation without **explicit user confirmation**. When in doubt — move, don't delete.

---

## Archive Patterns

All archived content lives under a single `.archive/` directory at the appropriate level.

### Path Mirroring Rule

When moving a file or directory into `.archive/`, **preserve its path relative to the project root**. This makes the original location self-evident without modifying the archived file.

**Example**: archiving `src/components/button.tsx`:

```
.archive/src/components/button.tsx
```

Restoring is trivial — copy the file back to the path shown in `.archive/`.

### Dated Snapshot

When archiving a whole subsystem or capturing a point-in-time state, use a date-prefixed subdirectory:

```
.archive/YYYYMMDD/[original-path]
```

This preserves the original path under the date stamp and makes ordering unambiguous.

### Single-File In-Place Archives

For a single file that doesn't warrant moving, rename it in place:

| Pattern | When to use |
|---------|-------------|
| `filename.old.ext` | No longer active; kept for quick in-place reference |

### Other Archive Locations

| Location | Purpose |
|----------|---------|
| `.dev-docs/.old/` | Stale **development documentation** only |

**AI behavior for archived locations**:
- Treat all contents of `.archive/` as **read-only reference only**
- Do not modify files in `.archive/`
- Do not suggest patterns from `.archive/` as current practice
- Ignore `.archive/` in searches unless the user explicitly asks to look there

---

> **→ [`.dev-docs` Convention](conventions.md#dev-docs-convention)** — dev documentation subdirectory structure, `index.md` format, and AI ignore rules for `.old/`.

---

## Never Reset Databases

**Never drop, truncate, or reset a database without explicit written confirmation from the user.**

This applies to:
- `DROP DATABASE`, `DROP TABLE`, `TRUNCATE TABLE`
- `DELETE FROM [table]` without a `WHERE` clause
- Migration rollbacks that destroy data
- Docker volume removal (`docker volume rm`, `docker-compose down -v`)
- Any ORM method that wipes a table or resets sequences
- Seeding commands that clear before inserting (check the script before running)

**Safe operations** (allowed without confirmation):
- `SELECT` queries of any kind
- `INSERT`, `UPDATE`, `DELETE` with a specific `WHERE` clause targeting known rows
- Running **forward** migrations (adding tables or columns)
- Creating new databases or schemas

**When asked to "reset" or "clean" a database**: ask the user to confirm:
1. Which environment (dev / staging / production)?
2. Which tables or schemas?
3. Should users and their data be preserved?
4. Is there a backup in place?

Never assume. Never proceed without answers.

---

## Stale Instruction Files

When a `.ai/instruct.md` becomes outdated due to a refactor or module removal:

1. Do **not** delete it
2. Add a deprecation banner at the very top:
   ```markdown
   > ⚠️ **DEPRECATED** — This file is superseded by [`new/path/.ai/instruct.md`](new/path/.ai/instruct.md).
   > Preserved for reference. Do not apply these rules to new work.
   ```
3. If the directory the file lived in still exists, leave the deprecated `instruct.md` in place. If that directory no longer exists, move the file to the **nearest surviving ancestor**'s `.dev-docs/.old/` (or to the root `.dev-docs/.old/` as a last resort)
4. Update `.ai/index.md` to remove it or mark it deprecated

---

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
| Run builds and tests | Safe if they don't modify external state |

**Always ask before**:

| Action | Why |
|--------|-----|
| Deleting any file permanently | Irreversible |
| Running database migration rollbacks | Data loss risk |
| `docker-compose down -v` | Destroys volumes |
| `git push`, `git reset --hard`, `git push --force` | Affects shared history |
| Dropping or truncating tables | Data loss |
| Sending any external request (email, webhook, API call to production) | External side effect |
