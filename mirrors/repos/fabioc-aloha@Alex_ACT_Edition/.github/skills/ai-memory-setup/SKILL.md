---
type: skill
lifecycle: stable
inheritance: inheritable
name: ai-memory-setup
description: "Detect, create, and manage the AI-Memory fleet communication channel. Fires on bootstrap, session start (announcements), and feedback writes."
tier: standard
applyTo: '**/AI-Memory/**,**/cognitive-config*,**/*feedback*,**/*announcement*,**/*fleet*,**/*memory-setup*'
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# AI-Memory Setup

AI-Memory is the shared folder on the user's cloud drive where ACT heirs exchange feedback, announcements, and registry data. This skill covers detection, creation, path resolution, and ongoing read/write operations.

## Supported Cloud Providers

| Provider | Folder patterns detected | Notes |
| --- | --- | --- |
| OneDrive | `OneDrive`, `OneDrive - *` (personal, family, business) | Most common; multiple accounts create multiple folders |
| iCloud | `iCloudDrive`, `iCloud Drive`, `iCloud~com~apple~CloudDocs` | macOS and Windows variants |
| Dropbox | `Dropbox`, `Dropbox (Personal)`, `Dropbox (Business)` | Personal and business variants |
| Google Drive | `Google Drive`, `My Drive` | Drive for Desktop sync folder |
| Box | `Box`, `Box Sync` | Enterprise cloud storage |
| MEGA | `MEGA`, `MEGAsync` | Encrypted cloud storage |
| pCloud | `pCloud`, `pCloud Drive` | European cloud storage |
| Nextcloud | `Nextcloud` | Self-hosted cloud |

Discovery scans the user's HOME directory for any folder matching these patterns. Unknown cloud drives are ignored (the user can still point to them manually via `ai_memory_root`).

## Path Resolution Algorithm

Resolve the AI-Memory root in this order:

1. **Config override**: read `.github/config/cognitive-config.json`. If `ai_memory_root` is set, use `<HOME>/<ai_memory_root>/AI-Memory`.
2. **Auto-discovery**: scan `<HOME>` for folders matching known cloud provider patterns. Skip any folder listed in `ai_memory_exclude`. Among matches, prefer drives that already contain an `AI-Memory/` subfolder.
3. **Local fallback**: `~/AI-Memory` (no cloud sync, still functional)
4. **Exclusion list**: `ai_memory_exclude` in cognitive-config.json lists folder names to skip (e.g., `["OneDrive - Microsoft"]` to avoid the work account).

The resolution order matches `_registry.cjs` (the muscle used by `bootstrap-heir.cjs` and `upgrade-self.cjs`). LLM heirs and scripts must agree on the same path.

## Folder Structure

```text
<cloud-drive>/AI-Memory/
  README.md                           # Channel overview
  feedback/
    README.md
    alex-act/                         # Heir feedback inbox
      README.md
  announcements/
    alex-act/                         # Fleet-wide announcements
      README.md
  heirs/
    registry.json                     # Fleet registry (auto-maintained)
  knowledge/                          # Shared knowledge base (see index.json)
  insights/                           # Analytical insights
```

### Knowledge Packages

`AI-Memory/knowledge/` contains reference material installed from the Plugin Mall. These are **not** loaded into the brain -- they are consulted on demand when a task matches their domain.

Read `AI-Memory/knowledge/index.json` to discover available packages. Each entry has `name`, `keywords`, `use_phase`, and `path`. When a task involves a matching phase (planning, audit, review, implementation) or keyword, read the referenced `reference.md` for guidance.

This costs zero tokens until you actually read it.

## Operations

### Detect (session start)

On every session start, resolve the AI-Memory root. If found:

1. Check `announcements/alex-act/` for unread files
2. Report any new announcements to the user (one line each)
3. Do NOT read or report feedback (that's the Supervisor's job)

If not found: note it silently. Do not prompt the user unless they explicitly ask about fleet communication.

### Create (first time setup)

When AI-Memory is needed but doesn't exist (bootstrap, first feedback write):

1. Discover which cloud drives exist:

   ```bash
   node .github/scripts/_registry.cjs --discover
   ```

   Output lists all detected cloud drives with provider name and whether AI-Memory exists.

2. If multiple drives found, ask the user which one to use. If only one, use it. If none, offer `~/AI-Memory` as local fallback.

3. Create the folder structure:

   ```bash
   node .github/scripts/_registry.cjs --init "<drive-name>"
   ```

   Or during bootstrap, use the `--ai-memory` flag:

   ```bash
   node bootstrap-heir.cjs --target . --heir-id my-project --ai-memory "Dropbox" --apply
   ```

4. The choice is automatically persisted in `.github/config/cognitive-config.json`:

   ```json
   {
     "ai_memory_root": "Dropbox",
     "ai_memory_exclude": ["OneDrive - Microsoft"]
   }
   ```

5. Verify: `node .github/scripts/_registry.cjs --resolve .` should return the AI-Memory path.

### Write Feedback

When the heir observes friction worth surfacing:

1. Resolve AI-Memory root
2. Write one markdown file per item to `feedback/alex-act/`
3. Filename format: `YYYY-MM-DD-<short-slug>.md`
4. Strip project specifics per `cross-project-isolation.instructions.md`
5. Required frontmatter: Date, Category (bug/friction/feature-request/success), Severity (critical/high/medium/low), Heir (redacted), Edition version

### Read Announcements

On session start (triggered by `greeting-checkin.instructions.md`):

1. Resolve AI-Memory root
2. List files in `announcements/alex-act/` (skip README.md)
3. For each unread file, report the title and date
4. Do NOT delete announcement files (they persist for all heirs)

## Multi-Cloud-Drive Disambiguation

Users may have multiple OneDrive accounts (personal + work). The `ai_memory_exclude` field prevents heirs from writing to the wrong drive.

| Scenario | Resolution |
| --- | --- |
| One OneDrive | Auto-detected, no config needed |
| Two OneDrives, AI-Memory in one | `ai_memory_root` pins the correct one |
| Two OneDrives, AI-Memory in both | `ai_memory_exclude` blocks the wrong one |
| No OneDrive, has iCloud | iCloud candidate resolves |
| No cloud drive at all | `~/AI-Memory` local fallback |

## Configuration Reference

`cognitive-config.json` fields (heir-owned, not overwritten on upgrade):

| Field | Type | Default | Purpose |
| --- | --- | --- | --- |
| `ai_memory_root` | string | (auto-detect) | Cloud drive folder name to use |
| `ai_memory_exclude` | string[] | [] | Folder names to skip during detection |

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Hardcoding an absolute path | Use the resolution algorithm; paths differ per user and OS |
| Creating AI-Memory in `OneDrive - Microsoft` (work account) | Personal cloud drive only; work drives may have retention policies |
| Writing feedback without stripping project context | Always apply `cross-project-isolation` before writing |
| Reading feedback as a heir | Feedback is for the Supervisor; heirs read announcements only |
| Creating AI-Memory on every session | Create once on bootstrap; subsequent sessions just resolve |

## Muscle Reference

The `_registry.cjs` script (shipped with Edition) provides both a programmatic API and a CLI:

### Programmatic API

| Function | Purpose |
| --- | --- |
| `resolveAiMemoryRoot(heirRoot?)` | Returns the AI-Memory path or null; honors cognitive-config.json |
| `discoverCloudDrives(heirRoot?)` | Scans HOME for cloud drive folders; returns `[{ name, path, provider, hasAiMemory }]` |
| `initAiMemory(driveName)` | Creates full folder structure + READMEs |
| `upsertHeir(marker, repoPath)` | Updates `heirs/registry.json` |

### CLI

```bash
node .github/scripts/_registry.cjs --discover          # List cloud drives
node .github/scripts/_registry.cjs --init "<name>"     # Create AI-Memory in named drive
node .github/scripts/_registry.cjs --resolve [dir]     # Resolve AI-Memory root
```

### Bootstrap Flag

```bash
node .github/scripts/bootstrap-heir.cjs --ai-memory "<drive-name>" ...
```

Overrides auto-selection during bootstrap. Persists to cognitive-config.json.

## Falsifiability

- This skill has failed if heirs report AI-Memory not loading, cross-project contamination, or irrelevant search results within 30 days of following the setup procedure
- The folder structure convention is wrong if OneDrive sync conflicts corrupt the knowledge store on multi-device setups
- The bootstrap sequence is stale if the cognitive-config.json schema changes and this skill references obsolete fields
