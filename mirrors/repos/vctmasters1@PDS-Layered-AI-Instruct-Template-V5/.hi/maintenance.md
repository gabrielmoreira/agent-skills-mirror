# Maintenance — Archive, Never-Delete, and Database Safety Rules

**Scope**: Project-wide canonical reference
**Last Updated**: 2026-05-25

> This file is the **single source of truth** for file preservation, archiving, and database safety rules.
> Never duplicate these rules — link here from any `.hi/instruct.md` that needs them.

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
| Any retired source file or subsystem | Move it into the `.archive/` directory inside its own parent folder |
| Superseded dev docs | Move to `.dev-docs/.archive/` |

**AI Rule**: Never use `rm`, `Remove-Item`, `git rm`, `del`, or any destructive file operation without **explicit user confirmation**. When in doubt — move, don't delete.

---

## Archive Patterns

**Canonical rule: archive into the `.archive/` directory inside the *parent folder* of the item being archived.** Never archive into a single project-wide container — keeping archives local to each subtree means a project built from this template can be layered inside another project and still carry its own archives with it.

### The `.archive/` Rule

When archiving `some/dir/thing`, move it to `some/dir/.archive/thing` — the `.archive/` directory is created inside the item's **parent** folder.

> **Use the tool, don't hand-compute the path.** Run `python .hi/engine/archive.py <path>` (add `--dated` for a snapshot). The script computes the destination, refuses unsafe targets, uses `git mv` when the file is tracked, and records a pointer in the archive's `README.md`. See the **archiving** skill.

**Example**: archiving `src/components/button.tsx`:

```
src/components/button.tsx  →  src/components/.archive/button.tsx
```

Restoring is trivial — move the file back up one level out of `.archive/`.

### Dated Snapshot

When archiving a whole subsystem or capturing a point-in-time state, add a date-stamped subdirectory inside the `.archive/`:

```
some/dir/thing  ->  some/dir/.archive/YYYYMMDD/thing
```

### Other Archive Locations

| Location | Purpose |
|----------|---------|
| `.dev-docs/.archive/` | Stale **development documentation** (the `.archive/` inside the `.dev-docs/` folder) |

**AI behavior for archived locations**:
- Treat all contents of any `.archive/` as **read-only reference only**
- Do not modify files in `.archive/`
- Do not suggest patterns from `.archive/` as current practice
- Ignore `.archive/` in searches unless the user explicitly asks to look there

---

> **→ [`.dev-docs` Convention](conventions.md#dev-docs-convention)** — dev documentation subdirectory structure, `index.md` format, and AI ignore rules for `.archive/`.

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

When a `.hi/instruct.md` becomes outdated due to a refactor or module removal:

1. Do **not** delete it
2. Add a deprecation banner at the very top:
   ```markdown
   > ⚠️ **DEPRECATED** — This file is superseded by [`new/path/.hi/instruct.md`](new/path/.hi/instruct.md).
   > Preserved for reference. Do not apply these rules to new work.
   ```
3. If the directory the file lived in still exists, leave the deprecated `instruct.md` in place. If that directory no longer exists, move the file to the **nearest surviving ancestor**'s `.dev-docs/.archive/` (or to the root `.dev-docs/.archive/` as a last resort)
4. Update `.hi/index.md` to remove it or mark it deprecated

---

## What AI Can Do Without Asking

These are pre-approved local, reversible actions — no confirmation needed:

| Action | Notes |
|--------|-------|
| Read any file | Always safe |
| Create new files | Safe; creation is reversible by deletion |
| Edit existing files | Safe for source/config; always show diff |
| Move files to `.archive/` or `.dev-docs/.archive/` | Safe; reversible |
| Update `Last Updated` date in `.hi/instruct.md` files | Pre-approved; part of every instruction file edit |
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
