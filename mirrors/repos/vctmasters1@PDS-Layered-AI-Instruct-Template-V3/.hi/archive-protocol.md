# Archive Protocol — Never Delete, Always Replace-with-Archive

**Version**: 2.0.0
**Last Updated**: 2026-06-05
**Scope**: Mandatory archive-first pattern for all file replacements and removals

---

## Contents

| Section | What's here |
|---------|-------------|
| [Core Rule](#core-rule) | Never delete — always archive |
| [Archive Paths](#archive-paths) | Where archives live (parent `.archive/`) |
| [Archive Operations](#archive-operations) | Step-by-step archive procedure |
| [Archive Retention & Cleanup](#archive-retention--cleanup) | 180-day threshold, deletion approval |
| [When to Archive](#when-to-archive) | Triggers and decision criteria |
| [What NOT to Archive](#what-not-to-archive) | Exclusions |
| [Tools & Integration](#tools--integration) | Archive tool, cleanup agent, hooks |
| [Examples](#examples) | Worked examples |
| [Reviewer Responsibility](#reviewer-responsibility) | Verification checklist |
| [Related Files](#related-files) | Cross-references |
| [YAML Frontmatter (if attached to AI instruction)](#yaml-frontmatter-if-attached-to-ai-instruction) | Embedding metadata |

---

## Core Rule

**Never delete a file directly. Archive it first.**

When a file becomes stale, orphaned, superseded, or must be removed:
1. Move it into the `.archive/` directory inside its own **parent** folder
2. For snapshots, add a `YYYYMMDD` subdirectory inside that `.archive/`
3. Leave a pointer/README explaining why it was archived
4. Commit the archive operation in Git before committing any replacement

> **Use the tool — don't compute the path by hand.** Run `python .hi/engine/archive.py <path>`.
> It computes the destination, refuses unsafe targets, uses `git mv` for tracked files, and writes
> the pointer automatically. See the [archiving skill](skills/archiving/SKILL.md).

---

## Archive Paths

**The destination is always the `.archive/` directory inside the item's own parent folder.**
There is **no path-mirroring** — because the archive sits right next to where the item lived, the
original location is self-evident. This keeps archives local to each subtree so a project built
from this template can be layered inside another project and still carry its own archives.

```
<parent>/thing          → <parent>/.archive/thing
<parent>/thing  (dated) → <parent>/.archive/YYYYMMDD/thing
```

### Examples

```
src/legacy_handler.js       → src/.archive/legacy_handler.js
config/old_settings.yaml    → config/.archive/old_settings.yaml
.dev-docs/deprecated-api.md → .dev-docs/.archive/deprecated-api.md
.hi/agents/old-agent.md     → .hi/agents/.archive/old-agent.md
.hi/knowledge/old-sheet.md  → .hi/knowledge/.archive/old-sheet.md
config.yaml  (at repo root) → .archive/config.yaml
```

The `.hi/` segment only appears when the archived item already lives inside a `.hi/` folder — the
`.archive/` is simply created as a child of whatever folder currently holds the item.

---

## Archive Operations

### Preferred: the archive tool

```bash
# Preview the destination, change nothing
python .hi/engine/archive.py <path> --dry-run

# Archive it (uses git mv for tracked files, writes a README pointer)
python .hi/engine/archive.py <path> --reason "why"

# Snapshot a subsystem under a YYYYMMDD subdirectory
python .hi/engine/archive.py <path> --dated --reason "why"
```

The tool refuses to delete, refuses targets already inside an `.archive/`, refuses protected paths
like `.git/`, and refuses to overwrite an existing archived item.

### Manual fallback (only if Python is unavailable)

Compute `<parent>/.archive/` yourself and move the item there:

```bash
mkdir -p "$(dirname "$file")/.archive"
mv "$file" "$(dirname "$file")/.archive/"
```

PowerShell:
```powershell
$dest = Join-Path (Split-Path $file -Parent) '.archive'
New-Item -Path $dest -ItemType Directory -Force | Out-Null
Move-Item -Path $file -Destination $dest
```

For a tracked file use `git mv` so history follows it. Then leave a `.archive/README.md` pointer
and commit the move before committing any replacement.

---

## Archive Retention & Cleanup

### Retention Period

- Archives older than **180 days** may be deleted (per [`.hi/knowledge/.cleanup-policy.md`](../.hi/knowledge/.cleanup-policy.md))
- Archives in user files: retain for **1 year minimum** unless explicitly deprecated
- Archives in `.hi/knowledge/`: follow cleanup policy (180-day threshold)

### Cleanup Procedure

Use the `memory_hygiene.py` engine (if KB-related):

```bash
python .hi/engine/memory_hygiene.py . --older-than 180 --dry-run
python .hi/engine/memory_hygiene.py . --older-than 180 --archive
```

For user files, manual review before deletion is required.

---

## When to Archive

### Superseded by another file

Move old version to archive; keep both until new version is confirmed working.

**Example:**
```
db/schema_v1.sql → db/.archive/schema_v1.sql
# New version: db/schema_v2.sql is now active
```

### Deprecated module or subsystem

Archive the entire module or subsystem structure as a dated snapshot:

```
api/deprecated-endpoint/ → api/.archive/20250115/deprecated-endpoint/
```

### Failed experiment or branch code

Archive code that didn't make it to production:

```
experiments/new-auth.py → experiments/.archive/new-auth.py
```

### Renamed or moved file

Archive the old location; create at new location:

```
config/settings.yaml → config/.archive/settings.yaml
# New location: .config/app-settings.yaml
```

### Temporary or debug files

Archive after task complete:

```
.hi/debug/test-run.log → .hi/debug/.archive/test-run.log
```

---

## What NOT to Archive

- **Git objects** (`.git/` contents) — never touch directly
- **Live log files** (if actively being written) — rotate first, then archive
- **Runtime temp files** (`.hi/foresight/`, `.hi/logs/` during active session) — let them age naturally
- **Build artifacts** (ignored by `.gitignore`) — delete directly, no archive needed
- **Personal VS Code settings** (`.vscode/settings.local.json`) — gitignored, not archived

---

## Tools & Integration

### Archive Tool (CLI)

The canonical tool is [`.hi/engine/archive.py`](engine/archive.py):

```bash
python .hi/engine/archive.py <path> [--dated] [--reason "why"] [--dry-run] [--no-git]
```

Or drive it through the prompt / agent:

```bash
/hip-archive <filepath>  # previews, confirms, archives, and creates the pointer
```

The [`cleanup` agent](agents/tier-2/specialists/hia-cleanup.agent.md) uses the same tool.

### Validator Checks (Automated)

The [Reviewer](agents/tier-2/workers/hia-reviewer.agent.md) verifies:
- Archive-first was used (no direct deletions in change set)
- Archived items landed in the `.archive/` of their own parent folder
- Dated snapshots use the `YYYYMMDD` format

---

## Examples

### Example 1: Replacing a config file

**Before:**
```
config/app.yaml (v1, now broken)
```

**Operation:**
```bash
python .hi/engine/archive.py config/app.yaml --reason "replaced by v2"
# Create new config/app.yaml (v2)
git commit -m "archive: replace config/app.yaml with v2 (v1 in archive)"
```

**After:**
```
config/app.yaml (v2, active)
config/.archive/app.yaml (v1, archived)
```

### Example 2: Archiving an agent that's no longer used

**Before:**
```
.hi/agents/hia-legacy-processor.agent.md (obsolete)
```

**Operation:**
```bash
python .hi/engine/archive.py .hi/agents/hia-legacy-processor.agent.md --reason "merged into Router"
git commit -m "archive: retire hia-legacy-processor.agent.md"
```

**After:**
```
.hi/agents/.archive/hia-legacy-processor.agent.md (archived, reference only)
```

### Example 3: Archiving a KB entry that's no longer relevant

**Before:**
```
.hi/knowledge/cheat-sheets/old-framework.md (outdated)
```

**Operation:**
```bash
python .hi/engine/archive.py .hi/knowledge/cheat-sheets/old-framework.md --reason "framework retired"
```

**Result:**
```
.hi/knowledge/cheat-sheets/.archive/old-framework.md (archived)
```

---

## Reviewer Responsibility

The [Reviewer](agents/tier-2/workers/hia-reviewer.agent.md) (stage 5) **must verify**:
- ✓ Every file removal was preceded by an archive
- ✓ Each archived item is in the `.archive/` of its own parent folder
- ✓ Dated snapshots use the `YYYYMMDD` format
- ✓ Pointer or README left (the tool does this automatically)
- ✗ No direct deletions without archive

If any rule violated: **FAIL** stage 5; send back to Generator.

---

## Related Files

- [`.hi/maintenance.md`](maintenance.md) — never-delete rules
- [`.hi/knowledge/.cleanup-policy.md`](knowledge/.cleanup-policy.md) — KB archival policy (180-day threshold)
- [`.hi/agents/hia-cleanup.agent.md`](agents/tier-2/specialists/hia-cleanup.agent.md) — cleanup worker agent
- [`.hi/agents/hia-reviewer.agent.md`](agents/tier-2/workers/hia-reviewer.agent.md) — archive-first verification

---

## YAML Frontmatter (if attached to AI instruction)

```yaml
---
rule_name: archive-first-protocol
enforcement: mandatory
applies_to:
  - file-replacement
  - file-removal
  - feature-deprecation
  - module-retirement
checkpoints:
  - validator: hia-reviewer.agent.md (stage 5)
    condition: every removal must have corresponding archive
---
```
