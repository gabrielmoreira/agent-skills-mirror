---
description: >
  Archive a file or directory the safe, deterministic way in this project. Use whenever you would
  otherwise delete, remove, `rm`, `del`, `Remove-Item`, or `git rm` something — or when the user
  asks to archive, retire, deprecate, or move something out of the way. Never compute the archive
  path by hand; run the archive tool, which puts the item in the `.archive/` of its own parent.
---

# Skill: Archiving

This project **never deletes**. Retired files and directories are moved into an `.archive/`
directory located **inside the parent folder of the item being archived**. The destination is
computed by a tool so it is always correct, regardless of how deep the item is nested.

## Contents

| Section | What's here |
|---------|-------------|
| [The Rule](#the-rule) | Where archived items go |
| [Protocol](#protocol) | How to run the archive tool |
| [Examples](#examples) | Example archive commands |
| [Exit Codes](#exit-codes) | Tool exit code meanings |
| [Read-Only Reference](#read-only-reference) | Archives are read-only |

---

## The Rule

```
some/dir/thing          ->  some/dir/.archive/thing
some/dir/thing  (dated) ->  some/dir/.archive/YYYYMMDD/thing
```

The `.archive/` is created in the item's **parent** folder. This keeps archives local to each
subtree, so a project built from this template can be layered inside another project and still
carry its own archives with it. Never archive into a single project-wide container.

## Protocol

1. **Do not hand-compute the path and do not `mv`/`Move-Item` manually.** Run the tool:

   ```bash
   python .hi/engine/archive.py <path>
   ```

2. **Options**:
   - `--dated` — place under a `YYYYMMDD/` subdirectory (use for subsystems or point-in-time snapshots)
   - `--reason "text"` — record why, in the archive's `README.md`
   - `--dry-run` — print the destination and change nothing (use this first if unsure)
   - `--no-git` — force a plain move even when the file is git-tracked

3. **What the tool guarantees**:
   - Destination = `<parent>/.archive/[YYYYMMDD/]<name>`, computed in code
   - Uses `git mv` automatically when the file is tracked, so history follows it
   - Refuses to delete — it only moves
   - Refuses unsafe targets (anything already inside an `.archive/`, or protected paths like `.git/`)
   - Refuses to overwrite an existing archived item (exit code 2)
   - Appends a dated pointer line to `<archive>/README.md`

4. **After archiving** (the tool does not do these for you):
   - Update any `.hi/instruct.md` that referenced the now-archived path
   - Update `.hi/index.md` if an instruction section was archived
   - Note the archival in the nearest `.dev-docs/index.md` with a reason and date

## Examples

```bash
# Preview where a file would go
python .hi/engine/archive.py src/legacy/auth.py --dry-run

# Archive a single file (git mv if tracked)
python .hi/engine/archive.py src/legacy/auth.py --reason "replaced by oauth.py"

# Archive a whole subsystem as a dated snapshot
python .hi/engine/archive.py api/v1/ --dated --reason "v2 is now canonical"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or dry-run) |
| 1 | Target does not exist |
| 2 | Destination already occupied |
| 3 | Refused (target is inside an `.archive/`, or is a protected path) |

## Read-Only Reference

Treat everything under any `.archive/` as **read-only**. Do not modify archived files, do not cite
them as current practice, and ignore them in searches unless the user explicitly asks.
