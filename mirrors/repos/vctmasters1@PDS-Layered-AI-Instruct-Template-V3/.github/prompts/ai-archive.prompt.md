---
mode: agent
description: Archive a file or directory using the project's convention instead of deleting it. Always ask for confirmation before moving anything.
---

# Archive File

Archive the specified file or directory following the **Never Delete Rule**.

> **→ [Never Delete Rule](../../.ai/maintenance.md#never-delete-rule)** — never permanently delete; always archive.
> **→ [Archive Patterns](../../.ai/maintenance.md#archive-patterns)** — canonical naming patterns for archives.

## Steps

1. Identify what is being archived (file, directory, dev doc, or entire subsystem)

2. Determine the appropriate archive pattern:
   | What | Destination |
   |------|-------------|
   | Single outdated source file | Rename to `filename.old.ext` in-place |
   | Stale dev doc | Move to `.dev-docs/.old/` in the same directory |
   | Any file or directory | Move to `.archive/[original-path]` — mirror the path from project root |
   | Point-in-time subsystem snapshot | Move to `.archive/YYYYMMDD/[original-path]` |

3. **Ask the user to confirm** the archive destination before moving anything

4. Perform the move (never use delete/remove). Preferred commands:
   - **Tracked file or directory**: `git mv <src> <dest>` so history follows the file.
   - **Untracked file**: `Move-Item` (PowerShell) or `mv` (POSIX).
   - Never use `rm`, `del`, `Remove-Item`, or `git rm` for archival.

5. After archiving:
   - Update any `.ai/instruct.md` that referenced the now-archived path
   - Update `.ai/index.md` if an instruction section was archived
   - Note the archival in the nearest `.dev-docs/index.md` with a reason and date
