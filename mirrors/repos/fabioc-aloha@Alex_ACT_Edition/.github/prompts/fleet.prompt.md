---
description: "List all heirs registered in AI-Memory/heirs/registry.json — heir IDs, edition versions, last sync, repo paths"
mode: agent
lastReviewed: 2026-04-30
---

# Fleet

Show every heir the user has bootstrapped across machines, ranked by which ones are behind on Edition.

## Steps

1. **Resolve AI-Memory root** using the standard algorithm: check `cognitive-config.json` for `ai_memory_root` override, then auto-discover cloud drives, skip `ai_memory_exclude` entries, pick the first with `AI-Memory/`. CLI: `node .github/scripts/_registry.cjs --resolve .`

2. **Read the registry** at `<root>/heirs/registry.json`. If missing, report: "No heirs registered yet. The registry is populated automatically by `bootstrap-heir.cjs` and `upgrade-self.cjs` (when `opt_in.fleet_inventory: true` in the heir's marker)."

3. **Find the latest Edition version** — best effort: read `.github/VERSION` from the current cwd if it exists and looks like an Edition repo; otherwise treat the highest version among registered heirs as the floor.

4. **Display table**, sorted by `last_sync_at` ascending (oldest first):

   ```
   heir_id              edition  last_sync         repo_path
   ───────────────────  ───────  ────────────────  ────────────────────────────
   acme-billing         0.1.0    14 days ago       C:\dev\acme-billing
   research-vault       0.2.0    2 hours ago       C:\dev\research-vault
   ```

5. **Surface signals**:
   - Heirs with `edition_version` lower than the fleet max → "behind on Edition, run `/upgrade` from those heirs"
   - Heirs with `last_sync_at` older than 30 days → "stale"
   - Total count + how many are current

6. **Refuse if** AI-Memory root cannot be resolved (offer guidance to set up shared storage)

## Notes

- This is read-only — never modifies the registry
- Heirs that opted out of `fleet_inventory` won't appear (by design, privacy-first)
- The registry is user-scope, lives in shared `AI-Memory/`, visible to all your AI surfaces
