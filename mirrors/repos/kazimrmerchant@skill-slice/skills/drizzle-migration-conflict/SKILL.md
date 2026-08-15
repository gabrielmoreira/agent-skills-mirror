---
name: drizzle-migration-conflict
description: "Classifies and repairs Drizzle Kit clashes in _journal.json, snapshots, and generated SQL after pull, merge, or rebase, including non-commutative drizzle-kit check failures. Use when migration artifacts conflict or a team needs regenerate-from-merged-schema plus CI policy. Do not use for schema modeling, drizzle-kit push as the production fix, or migrate against an unconfirmed database."
version: 1.0.1
category: databases
risk: critical
source: community
source_repo: chaunsin/agent-skills
source_type: community
date_added: "2026-06-29"
tags: [drizzle, migrations, database, ci, merge-conflicts]
tools: [git, python, rg]
license: "Apache-2.0"
license_source: "https://github.com/chaunsin/agent-skills/blob/master/LICENSE"
---

# Drizzle Migration Conflict

Diagnose, repair, and prevent Drizzle Kit migration conflicts in a multi-developer repository. Drizzle migrations encode both SQL and migration snapshots, so the safe answer depends on the current migration directory shape, the Drizzle Kit version, and the git state.

## When to Use

- Drizzle migration files, `_journal.json`, or `snapshot.json` conflict after a pull, merge, rebase, or PR update.
- `drizzle-kit check` reports non-commutative migrations or migration folder conflicts.
- A team wants a safe repair flow for generated Drizzle migrations after schema changes converge.
- Designing CI or merge-queue policy to prevent repeated Drizzle migration conflicts.
- Transitioning from legacy flat layout to folder-based migrations and encountering conflicts mid-transition.

## Prerequisites

- Git repository with Drizzle Kit migrations (`drizzle-kit` and `drizzle-orm` installed).
- Python 3 available if using the helper script (read-only, no DB connection).
- `rg` (ripgrep) for file discovery.
- Windows host primary (PowerShell). Adjust path separators and quoting for PowerShell vs. bash when running commands.

## Procedure

### Step 1 — Classify the mode

Determine the task mode before taking any action:

1. **Diagnose** — The user has a conflict or failed `drizzle-kit check` and wants to understand it. Read-only only.
2. **Repair** — The user explicitly asks to fix or regenerate migration files. Adds file writes and `drizzle-kit generate`/`check` execution, each gated by safety rules and explicit confirmation.
3. **CI hardening** — The user wants to prevent future conflicts in PRs or merge queues. Adds proposing or editing CI/workflow files. Do not run migration commands against the user's database.
4. **Explain** — The user wants a conceptual answer or a team playbook. No commands beyond optional read-only inspection.

When the mode is not explicit, choose **Diagnose**.

Mode boundaries — do not cross without an explicit upgrade:

| Mode | Allowed actions |
|------|----------------|
| Diagnose | `git status`, `git ls-files -u`, helper script, file inspection. No `drizzle-kit check`, typechecks, tests, or writes. |
| Repair | Adds file writes and `drizzle-kit generate`/`check`, each gated by safety rules + explicit confirmation of exact files and side (`ours`/`theirs`). |
| CI hardening | Adds CI/workflow file edits. Validate workflow syntax and logic only — no DB-backed migration commands. |
| Explain | Conceptual only. Optional read-only inspection. |

### Step 2 — Repository discovery (read-only)

Collect repo facts before giving commands. On Windows PowerShell, use these directly; on bash, they work as-is:

```powershell
git status --short
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git ls-files -u
rg --files -g 'drizzle.config.*' -g 'package.json' -g 'pnpm-lock.yaml' -g 'yarn.lock' -g 'package-lock.json'
```

Then inspect the relevant files:

- `drizzle.config.*` for `out`, `schema`, dialect, and config shape.
- `package.json` scripts for the project-approved `generate`, `check`, and `migrate` commands.
- `package.json` dependencies or lockfile snippets for `drizzle-kit` and `drizzle-orm` versions.
- The migration output directory — from config or common names like `drizzle/`, `migrations/`, or `src/db/migrations/`.

### Step 3 — Run the helper script (if available)

If this skill's helper script is available, run it in read-only mode:

```powershell
python3 <skill-dir>/scripts/check_drizzle_migrations.py --root .
```

Resolve `<skill-dir>` to the installed skill directory. Check these locations in order and use the first that contains `scripts/check_drizzle_migrations.py`:

1. The target repository's vendored copy: `<repo-root>/skills/drizzle-migration-conflict`
2. The Claude Code skills directory: `~/.claude/skills/drizzle-migration-conflict`
3. Any other install location reported by the user's environment.

If none resolve, fall back to the manual `git`/`rg` inspection commands above and tell the user the helper script was not found. Use `--config <file>` and `--migrations-dir <dir>` when the project has multiple Drizzle configs or outputs. The script never connects to a database and never writes files; it only reads migration directories and reports structural issues.

### Step 4 — Identify migration structure

Determine the structure before proposing a fix:

- **Legacy structure**: `<out>/meta/_journal.json`, `<out>/meta/*_snapshot.json`, and root-level migration SQL files such as `<out>/0003_name.sql`.
- **Folder-based structure**: each migration is a directory containing `migration.sql` and `snapshot.json`.
- **Unknown or mixed structure**: stop and report ambiguity. Do not guess a destructive repair.

### Step 5 — Load reference files as needed

- Read `references/sources.md` **when the answer depends on current Drizzle behavior, official guidance, or one of the preserved external links.** Re-verify official docs and the most relevant discussion when the project's `drizzle-kit` major version changes, since migration internals (snapshot format, journal shape, `drizzle-kit check` semantics) have shifted between releases.
- Read `references/conflict-resolution.md` **before recommending a repair flow.**
- Read `references/ci-policy.md` **before proposing CI, merge queue, or team workflow changes.**
- Read `references/report-template.md` **before writing a diagnostic report.** Use the conclusion values: `NO_CONFLICT_FOUND`, `SAFE_TO_REGENERATE`, `NEEDS_USER_CONFIRMATION`, or `BLOCKED_BY_AMBIGUITY`.

### Step 6 — Execute repair (Repair mode only, with confirmation)

Recommended repair principles:

1. Resolve schema source conflicts first. The regenerated migration must reflect the merged schema, not one side's stale snapshot.
2. Treat the parent or target branch migration history as the source of truth when repairing a feature branch after updating from that branch.
3. Prefer discarding and regenerating generated migration artifacts over hand-editing journal or snapshot files.
4. After regeneration, validate in tiers:
   - Database-free structural checks first.
   - `drizzle-kit check` only after confirming its config/env cannot point at production.
   - Project tests only after inspecting the scripts and any database targets.
5. If the user asks to apply changes, state exactly which files will be changed before performing the write.

### Step 7 — Report findings

- State the detected migration structure and selected mode.
- Separate confirmed conflicts from assumptions and missing evidence.
- Give a safe default path first, then optional automation or CI hardening.
- For destructive steps, label them as "requires confirmation" and explain what will be lost.
- Use conclusion values from `references/report-template.md`.

## Safety Rules

These are hard rules — never violate them:

- Start in read-only diagnosis mode unless the user explicitly asks to fix files.
- Do not run `drizzle-kit migrate`, `drizzle-kit push`, database seed scripts, or any command that connects to a live database unless the user explicitly requests it and the target is clear.
- Treat `drizzle-kit check`, project typechecks, and tests as command execution that may load project config, environment variables, or scripts. Inspect the project's scripts and drizzle.config (plus env) first, and require an explicit non-production or disposable target before any DB-backed validation.
- Do not delete migration files, rewrite `_journal.json`, or run `git checkout --ours`, `git checkout --theirs`, `git restore`, or `rm` unless the user has confirmed the exact side and files to change.
- Do not recommend `drizzle-kit push` as the production solution for migration conflicts; it skips the auditable migration history that teams need.
- Treat `--ignore-conflicts` as an exception for a known false positive, not as the normal fix.
- Preserve schema source code changes unless the user explicitly asks to discard them. Conflict repair normally discards generated migrations and regenerates them from the merged schema.
- If `ours` and `theirs` could mean different branches depending on merge direction, ask the user to identify the parent branch before suggesting checkout commands.

## Pitfalls

- **Hand-editing `_journal.json` or snapshot files**: Prefer discarding and regenerating. Manual edits to generated files are error-prone and can corrupt the migration chain.
- **Using `drizzle-kit push` for conflict resolution**: It skips the auditable migration history. Never recommend it as the production fix.
- **Running `drizzle-kit check` without inspecting config/env first**: The command may load environment variables that point at a production database. Always inspect `drizzle.config.*` and `.env` first.
- **Assuming `ours`/`theirs` direction**: In a rebase, `ours` is the target branch and `theirs` is the feature branch — the opposite of a merge. Always ask the user to identify the parent branch.
- **Mixed migration structures**: If the repo is mid-transition from legacy flat to folder-based, do not guess. Stop and report `BLOCKED_BY_AMBIGUITY`.
- **`--ignore-conflicts` as default**: This masks real non-commutative migration issues. Reserve it for known false positives only.
- **Config-driven `out` directory**: If `drizzle.config.ts` sets `out` from `process.env.MIGRATIONS_DIR` and the env var is unset, the helper script will report no out directory found. Ask the user to provide the expected path via `--migrations-dir`.
- **Drizzle Kit major version changes**: Snapshot format, journal shape, and `drizzle-kit check` semantics shift between releases. Re-verify against `references/sources.md` when the version changes.

## Verification

After any repair or before reporting, verify with these checkable steps:

1. **Structural check (no DB)**:
   ```powershell
   python3 <skill-dir>/scripts/check_drizzle_migrations.py --root .
   ```
   Confirm the script reports no structural issues (journal entries match files, snapshots present, no gaps).

2. **Git state clean**:
   ```powershell
   git status --short
   ```
   Confirm no unresolved conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) remain in migration files.

3. **`drizzle-kit check` (Repair mode only, after confirming config/env is non-production)**:
   ```powershell
   npx drizzle-kit check
   ```
   Confirm it reports no non-commutative migration conflicts. If it does, do not auto-pass `--ignore-conflicts` — investigate first.

4. **Report conclusion**: Use one of `NO_CONFLICT_FOUND`, `SAFE_TO_REGENERATE`, `NEEDS_USER_CONFIRMATION`, or `BLOCKED_BY_AMBIGUITY` from `references/report-template.md`.

## Output Rules

- Use the user's language when practical, but keep command snippets and file paths literal.
- Never echo secrets. When inspecting `drizzle.config.*`, `.env`, or environment variables, do not include database URLs, passwords, tokens, or connection strings in the report. Reference them as `<redacted>` or describe only whether they point at a production-like target.

## Limitations

- This skill cannot guarantee that a regenerated migration is production-safe without review against the target database state and deployment process.
- It does not run DB-backed migration commands unless the user explicitly confirms the target and the command.
- It is focused on Drizzle Kit migration conflicts, not general schema design or application-query optimization.

## Related Skills

- Database migration CI/CD pipeline skills
- Git merge conflict resolution skills
