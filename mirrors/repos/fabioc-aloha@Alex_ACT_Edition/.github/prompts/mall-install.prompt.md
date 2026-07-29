---
description: "Install a plugin from the Plugin Mall catalog using version-aware legacy compatibility rules"
lastReviewed: 2026-07-28
---

# /mall-install

Install a plugin from the Plugin Mall into this heir.

Source of truth: [mall-installation.instructions.md](../instructions/mall-installation.instructions.md)

## Steps

1. Resolve identity:
   - Run `/mall-search <query>` when needed.
   - If multiple stores match, run `/mall-show <name>` and require explicit `(store, name)` choice.
2. Read catalog fields: `name`, `store`, `version`, `shape`, `source_url`, `trust_score`, `provenance`.
3. Build a no-write plan from the shared instruction:
   - detect Mall 3 vs Mall 2 fallback layout,
   - map supported components,
   - classify unsupported components,
   - define exact target paths,
   - define `.install.json` content with exact `component_paths`.
4. Fail closed before writes when unsupported legacy-mode components exist (`hooks`, `extensions`, `lspServers`, unknown).
5. Show plan and request explicit user approval.
6. If approved, write only allowed local targets and merge MCP servers additively with backup.
7. Write `.github/skills/local/<plugin-name>/.install.json` with required fields.
8. Verify all recorded `component_paths` exist.
9. Run drift check:

   ```bash
   node .github/scripts/audit-mall-drift.cjs
   ```

10. Report outcome with installed version, store, detected layout, and installed `component_paths`.

## Safety rules

1. Never write outside allowed local targets.
2. Never guess missing files or guessed delete paths.
3. Never claim success if `.install.json` or `component_paths` verification fails.
4. Never remove pre-existing content on a failed attempt.

## Would Revise If

Revisit by **2026-10-28** if guided installs repeatedly fail on distinct Mall 3 layouts or require deterministic script replacement.
