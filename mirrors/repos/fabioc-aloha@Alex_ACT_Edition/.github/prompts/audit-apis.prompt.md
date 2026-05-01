---
description: "Detect drift in external APIs (model versions, endpoints, deprecations) and propose registry + downstream skill updates"
mode: agent
lastReviewed: 2026-04-30
---

# Audit External APIs

Refresh `.github/EXTERNAL-API-REGISTRY.md` and surface drift in skills/scripts that depend on it. The mechanical part (date arithmetic, URL reachability) runs in a muscle. The semantic part (deciding what changed, what to update) is **your job** — do not skip it.

## Steps

1. **Check registry exists** — confirm `.github/EXTERNAL-API-REGISTRY.md` is present. If missing, refuse and suggest a `/upgrade`.

2. **Run mechanical drift check**:

   ```sh
   node .github/muscles/audit-api-drift.cjs --probe
   ```

   Capture the report. Exit codes: 0 = all fresh, 1 = stale, 2 = expired or unreachable. The report groups entries into FRESH / STALE / EXPIRED / UNPARSABLE / UNREACHABLE.

3. **If everything is fresh** — say so and stop. No further work. (Empty registry is also "all fresh".)

4. **For each STALE / EXPIRED / UNREACHABLE entry, do the LLM job**:
   - Visit the `Source URL` (use a web fetch tool if available; otherwise ask the user to paste the current contents).
   - Compare against the row's `Latest Models` / `Endpoints` cell.
   - Identify any of:
     - New model versions (e.g., `flux-2-pro` → `flux-3-pro`)
     - Deprecated models or endpoints
     - Pricing or rate-limit changes that affect documented patterns
     - Breaking API changes
   - Note which `Brain Files` (skills, instructions, scripts) reference this entry.

5. **Propose a unified change set** — one message, grouped by entry. For each, list:
   - Registry row updates (new models list, new `Last Checked` = today's ISO date)
   - Skill / instruction / script edits implied by the change (file path + brief rationale; do not paste full files)
   - Any patterns that became incorrect (e.g., a SKILL.md's example uses a model that no longer exists)

6. **Confirm before applying** — wait for the user to approve. After approval:
   - Update the registry rows in-place. Use ISO `YYYY-MM-DD` for `Last Checked`.
   - Apply the proposed downstream edits.
   - Re-run `node .github/muscles/audit-api-drift.cjs` to verify all entries are fresh.

7. **Report** — one-line summary: how many entries were updated, how many downstream files changed.

## Boundaries

- **The muscle never patches scripts or skills.** It only detects drift. All semantic edits flow through this prompt with user approval.
- **Do not invent entries.** If the registry has no rows for a category, do not add one unless the user installs a skill that requires it.
- **Probe failures are not always drift.** A 403 or rate-limit means "couldn't check", not "deprecated". Flag for the user; do not auto-update those rows.
- **ISO dates only.** Convert any legacy `Apr 2026`-style entries to `YYYY-MM-DD` when you touch them.
