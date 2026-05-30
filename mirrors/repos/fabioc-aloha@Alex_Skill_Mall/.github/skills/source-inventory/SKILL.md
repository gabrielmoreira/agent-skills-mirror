---
name: source-inventory
description: "Maintain the source registry in sources/supported-stores.json — add a new third-party plugin store, retire one, refresh metadata, validate the schema. Use when proposing a registry change, after the weekly cron flags a source as unhealthy, or when a candidate store needs evaluation before adding."
lastReviewed: 2026-05-29
---

# Source Inventory

Maintain `sources/supported-stores.json` — the single source of truth for which upstream plugin repos the Mall scans.

The Mall does NOT keep persistent local clones of source repos. The weekly cron clones each registered source into a workflow temp directory (`$SOURCES_DIR`), scans it, scores it, and discards the clone. The registry file is the only persistent record.

## When to Use

- Proposing a new source store (run [store-evaluation](../store-evaluation/SKILL.md) first)
- Retiring a source store (run [staleness-discipline](../staleness-discipline/SKILL.md) first; use `/prune-source`)
- A weekly cron PR flags a source as unhealthy (broken remote, archived, license drift)
- Schema validation after editing `supported-stores.json`

## The registry: `sources/supported-stores.json`

```jsonc
{
  "$schema": "./supported-stores.schema.json",
  "schema_version": "2.0",
  "stores": [
    {
      "name": "plugin-mall",                       // unique kebab-case; matches catalog/stores/<name>.json
      "remote": "https://github.com/<org>/<repo>", // upstream URL (informational; not cloned for plugin-mall)
      "pluginDir": "plugins",                      // where plugins live in the upstream repo
      "quality": "first-party",                    // tier tag — see § Quality tiers
      "provenance": true,                          // true ONLY for plugin-mall (drives +50 trust signal)
      "license": "PolyForm-Noncommercial-1.0.0",   // SPDX id, or null if unknown
      "added_at": "2026-05-29"
    },
    {
      "name": "awesome-copilot",
      "remote": "https://github.com/github/awesome-copilot",
      "pluginDir": "skills",
      "quality": "official",
      "provenance": false,
      "license": "MIT",
      "added_at": "2026-04-15"
    }
  ]
}
```

### Required fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Kebab-case, ≤32 chars, unique across the registry; produces `catalog/stores/<name>.json` |
| `remote` | string | Upstream URL (HTTPS). For `plugin-mall`, this is informational; for everyone else, it's what `bootstrap-sources.cjs` clones |
| `pluginDir` | string | Path under the upstream repo where plugins live (`.`, `plugins`, `skills`, `agents`, etc.). Use `.` if plugins live at the repo root. |
| `quality` | enum | See § Quality tiers below |
| `provenance` | bool | `true` ONLY for `plugin-mall` (drives the +50 trust signal). `false` for all third-party stores. |
| `license` | string or null | SPDX identifier (e.g., `MIT`, `Apache-2.0`, `PolyForm-Noncommercial-1.0.0`). `null` if unknown — license signal will score 0. |
| `added_at` | string | `YYYY-MM-DD` of registry add |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `local_dir_name` | string | Override the directory name used inside `$SOURCES_DIR` when bootstrapping. Defaults to `name`. Use when the upstream repo has a different conventional folder name. |
| `note` | string | Human-readable note (audit trail) |
| `pruned_at` | string | `YYYY-MM-DD` of removal (use during the two-step prune; final delete removes the entry entirely) |

## Quality tiers

| Tier | Meaning | Examples of fit |
|---|---|---|
| `first-party` | The Mall's own curated plugins (`plugin-mall` only) | `plugin-mall` |
| `official` | Maintained by a major platform vendor with editorial standards | `awesome-copilot` (GitHub), `microsoft-skills` |
| `community-curated` | Community repo with explicit curation standards | `awesome-mcp-servers`, `awesome-claude-code` |
| `community` | Individual or small-team plugin collections | personal skill repos |
| `domain` | Vertical-specific plugin collections | game-dev, marketing, healthcare |
| `reference` | High-signal individual contributors | named researchers, well-known authors |

The `quality` tier is informational — it does NOT directly affect the trust score. Trust is computed from the six published signals (provenance, maintenance, adoption, license, frontmatter, README). Quality tier helps reviewers triage; the signals do the scoring.

## Adding a new source

Use the `/add-source` prompt. Sequence:

1. Run [store-evaluation](../store-evaluation/SKILL.md) first (scorecard ≥ 7 required)
2. Determine `name`, `pluginDir`, `quality`, `license`
3. Add the entry to `supported-stores.json` (alphabetical by `name`)
4. Run `node scripts/scan-sources.cjs` locally with `SOURCES_DIR` pointing at a temp dir
5. Verify the new store produces a plausible `catalog/stores/<name>.json`
6. Commit `[behaviour] add source: <name>` and let Monday's cron produce the first full catalog refresh

## Retiring a source

Use the `/prune-source` prompt. Sequence:

1. Run [staleness-discipline](../staleness-discipline/SKILL.md) to confirm a staleness signal fires
2. Add a `// pruned-pending: YYYY-MM-DD reason: <reason>` line above the entry and comment the entry out
3. Commit `[behaviour] prune source (pending): <name>`
4. Wait one weekly cron cycle to verify the catalog refresh PR shows the expected removal cleanly
5. Delete the commented-out entry in the next commit
6. Commit `[behaviour] prune source (delete): <name>`

## Health checks (run during PR review)

When reviewing a weekly catalog-refresh PR, sanity-check each store:

| Check | Pass | Action on fail |
|---|---|---|
| `bootstrap-sources.cjs` cloned the remote successfully | Workflow log shows clone success | Investigate remote; remote may have moved or repo may be deleted — surface in PR comments |
| `scan-sources.cjs` produced a non-zero plugin count | Plugin count > 0 in `catalog/stores/<name>.json` | Check `pluginDir` — upstream may have renamed the plugins folder |
| `fetch-github-stats.cjs` returned data | Stars / contributors / last_commit populated in `scoring/github-stats.json` | API rate-limit hit, OR repo is archived/private — surface in PR |
| `compute-trust.cjs` produced a non-null score | `trust_score` populated in `catalog/stores/<name>.json` | A signal is missing or unparseable — check `scoring/trust-audit.md` for the per-store breakdown |

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Adding a source without running store-evaluation | The scorecard is the bar; skip it and stale stores accumulate |
| Setting `provenance: true` for a third-party store | Provenance is for `plugin-mall` only — it drives the +50 first-party trust signal, not "I trust this maintainer" |
| Hand-editing `catalog/stores/<name>.json` | Catalog is generated; the only thing you edit is the registry |
| Deleting a registry entry in one commit | Always use the two-step prune so one cron cycle can verify the catalog refresh PR is clean |
| Skipping the schema validation step | The schema catches simple errors (typo'd field name, wrong enum value, malformed URL) before they break the workflow |

## Falsifiability

This skill is wrong if any of the following occur by **2026-08-29** (90 days):

- A registry entry that passed `/add-source` review gets pruned within 30 days (scorecard bar too lax)
- A pruned store gets re-added within 30 days (staleness signals miscalibrated)
- The schema lets through an invalid entry that breaks the workflow ≥1 time
- The quality-tier taxonomy needs revision ≥2 times in a quarter (taxonomy is wrong shape)

Track outcomes in `docs/curation-log.md` tagged `[SOURCE-INVENTORY]`.

## Related

- [store-evaluation](../store-evaluation/SKILL.md) — gate before adding
- [staleness-discipline](../staleness-discipline/SKILL.md) — gate before pruning
- [mall-self-curation](../mall-self-curation/SKILL.md) — the pipeline this registry feeds
- `/add-source` prompt
- `/prune-source` prompt
- `sources/supported-stores.schema.json` — JSON schema
