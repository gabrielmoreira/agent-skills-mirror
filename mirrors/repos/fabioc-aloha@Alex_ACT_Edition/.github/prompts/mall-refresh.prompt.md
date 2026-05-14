---
description: "Audit installed Mall plugins for upstream drift, then update or remove with explicit user consent"
mode: agent
lastReviewed: 2026-05-13
---

# /mall refresh

Audit this heir's installed Mall plugins for upstream drift, then apply updates and removals only after explicit consent.

## Steps

1. **Run mechanical drift check**:

   ```bash
   node .github/muscles/audit-mall-drift.cjs --json
   ```

   If the command fails because catalog is not found, retry with:

   ```bash
   node .github/muscles/audit-mall-drift.cjs --allow-gh --json
   ```

2. **If no actionable drift** (`UPDATED_UPSTREAM`, `DEPRECATED_UPSTREAM`, `UNMANAGED_LOCAL_PLUGIN` all zero):
   - Report "all local Mall plugins are in sync" and stop.

3. **Summarize proposed actions**:
   - `CURATED_SUBSET`: plugin is intentionally a reduced local subset with tracked upstream snapshot (informational, no action).
   - `UPDATED_UPSTREAM`: plugin metadata changed upstream.
   - `DEPRECATED_UPSTREAM`: plugin removed/deprecated upstream; candidate for removal.
   - `UNMANAGED_LOCAL_PLUGIN`: local folder without plugin.json; manual review needed.

4. **Ask for explicit approval before any write**:
   - Updates: ask once for batch approval.
   - Removals: ask per plugin name. Never remove in bulk without explicit yes.

5. **If approved, apply updates for `UPDATED_UPSTREAM` plugins**:
   - Read `source_path` from drift report (e.g. `plugins/<category>/<name>`).
   - Fetch upstream `plugin.json` and overwrite local `.github/skills/local/<name>/plugin.json`.
   - For each file listed in `artifacts`, fetch from Plugin Mall and write to local paths according to `install_paths` in plugin.json.
   - Also refresh local `README.md` copy for that plugin if upstream has it.

6. **If approved, remove each `DEPRECATED_UPSTREAM` plugin**:
   - Read local `.github/skills/local/<name>/plugin.json`.
   - If `install_paths` exists, remove each installed artifact path from the repo.
   - Remove the local plugin directory under `.github/skills/local/<name>/`.
   - If `install_paths` is missing, ask before fallback deletion of only the local plugin directory.

7. **Handle `UNMANAGED_LOCAL_PLUGIN` safely**:
   - Do not delete automatically.
   - Ask user whether to keep as custom local content or remove manually.

8. **Re-run drift check and report final state**:

   ```bash
   node .github/muscles/audit-mall-drift.cjs
   ```

   Include counts by state and list any remaining action items.

9. **Stage but do not commit**:
   - Show `git status --short`.
   - Suggest commit message: `chore: refresh local Mall plugins (updates + deprecations)`.

## Boundaries

- Never remove deprecated plugins without explicit user consent.
- Never delete unrelated local files outside plugin install paths.
- If a fetch fails for one plugin, continue with the rest and report partial completion.
- This command manages only locally installed Mall plugins (`.github/skills/local/*`).
