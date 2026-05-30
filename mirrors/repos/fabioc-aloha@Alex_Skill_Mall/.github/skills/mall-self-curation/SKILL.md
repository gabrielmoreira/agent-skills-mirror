---
name: mall-self-curation
description: How the Plugin Mall scans, scores, and prunes itself. The Mall is a self-curating repo; this skill is its operational playbook for the weekly catalog refresh and trust scoring. Use when working on the scan pipeline, debugging a stuck weekly PR, or onboarding to Mall internals.
lastReviewed: 2026-05-29
---

# Mall Self-Curation

The Plugin Mall is self-curating. Day-to-day operations (inventory, scoring, catalog publishing, staleness pruning) run inside this repo's `.github/workflows/scan-sources.yml`. This skill is the operational playbook for that pipeline.

## When to Use

- Authoring or debugging anything under `scripts/scan-sources.cjs` / `normalize-frontmatter.cjs` / `compute-trust.cjs` / `list-refs.cjs` / `render-catalog.cjs`
- Weekly catalog-refresh PR (`catalog-refresh/YYYY-MM-DD`) is stuck or producing surprising deltas
- New source added to `sources/supported-stores.json` — verifying it flows through the pipeline
- New plugin shape encountered (frontmatter convention we haven't seen before)
- Onboarding to Mall internals

## The pipeline (per `.github/workflows/scan-sources.yml`)

```text
  bootstrap-sources.cjs            ─┐
  scan-sources.cjs                  │
  normalize-frontmatter.cjs         ├─▶ catalog/index.json
  list-refs.cjs                     │   catalog/stores/*.json
  compute-trust.cjs                 │   scoring/trust-audit.{json,md}
  render-catalog.cjs               ─┘   catalog/INDEX.md + per-store + per-category
                                        README.md (storefront)
```

Each step is idempotent: re-running with no upstream changes produces byte-identical output.

| Step | Owns | Reads | Writes |
|---|---|---|---|
| `bootstrap-sources.cjs` | Source-repo clones into `$SOURCES_DIR` | `sources/supported-stores.json` | `$SOURCES_DIR/<name>/` (one shallow clone per third-party store; `plugin-mall` is excluded — it's this repo) |
| `scan-sources.cjs` | Per-plugin metadata extraction | `sources/supported-stores.json` + `$SOURCES_DIR/<name>/<pluginDir>/<plugin>/` + this repo's `plugins/<category>/<name>/` (for plugin-mall self-scan) | `catalog/stores/<store>.json` (without trust scores yet) |
| `normalize-frontmatter.cjs` | Standard + extended + raw three-layer schema | `catalog/stores/<store>.json` (plugins[*].frontmatter.raw) | `catalog/stores/<store>.json` (plugins[*].frontmatter.standard + extended) |
| `list-refs.cjs` | Per-plugin version discovery | `$SOURCES_DIR/<name>/.git/` + plugin source_path | `catalog/stores/<store>.json` (plugins[*].available_refs) |
| `compute-trust.cjs` | Trust score (provenance + 5 signals) | `catalog/stores/*.json` + `scoring/github-stats.json` | `catalog/stores/*.json` (store_trust + plugins[*].trust_score) + `scoring/trust-audit.{json,md}` |
| `render-catalog.cjs` | JSON → MD rendering | `catalog/stores/*.json` | `catalog/index.json` + `catalog/INDEX.md` + `catalog/stores/<store>.md` (one per store) + `catalog/categories/<cat>.md` (one per category) + `README.md` (storefront) + `sources/SOURCES.md` (rendered registry) |

## The `plugin-mall` self-entry — load-bearing rule

`sources/supported-stores.json` includes one entry with `name: "plugin-mall"` and `provenance: true`. This entry refers to **this repo itself** and is the mechanism that puts Mall-curated plugins in the same catalog as third-party plugins.

Two rules govern it:

1. **Bootstrap MUST skip `plugin-mall`.** This repo is already checked out; cloning it from itself is wasteful and could cause race conditions during the workflow. `bootstrap-sources.cjs` filters by `name !== "plugin-mall"`.
2. **Scan MUST include `plugin-mall`.** The scan walks `$REPO_ROOT/plugins/` (not `$SOURCES_DIR/plugin-mall/`) and produces `catalog/stores/plugin-mall.json` like any other store. `scan-sources.cjs` resolves the path conditionally: third-party stores use `$SOURCES_DIR/<name || local_dir_name>/<pluginDir>`; `plugin-mall` uses `$REPO_ROOT/<pluginDir>`.

Crossing this boundary (cloning self in bootstrap, or skipping self in scan) is the most common source of bugs in this pipeline.

## Trust scoring formula

Computed by `compute-trust.cjs`; signals published alongside score so readers can audit *why* a score is what it is.

| Signal | Range | Source | Mall-as-store | Third-party typical |
|---|---|---|---|---|
| **Provenance** | 0 or +50 | `supported-stores.json` `provenance` field | +50 | 0 |
| **Store maintenance** | 0–15 | `scoring/github-stats.json` `last_commit` recency | 15 | 0–15 |
| **Store adoption** | 0–10 | GitHub stars + contributors via `scoring/github-stats.json` | 10 | 0–10 |
| **License clarity** | 0–10 | OSI-approved=10, clear non-permissive=7, ambiguous=0 | 7 (PolyForm-NC) | 0–10 |
| **Frontmatter completeness** | 0–10 | description + version + lastReviewed presence | 10 | 0–10 |
| **README presence** | 0–5 | README ≥ 200 chars | 5 | 0–5 |

**Mall-as-store ceiling: 97/100.** Third-party stores cap at 50 by construction (no provenance). Per-plugin score adds up to +20 from plugin-specific signals on top of store score.

If the formula drifts from this table, update this skill in the same commit. Changes to the weights or signals are `[behaviour]`-class commits; changes that alter what the published-signal contract guarantees are `[constitutional]`.

## Workflow + cadence

- **Weekly cron**: Mondays 11:00 UTC per `.github/workflows/scan-sources.yml`
- **PR-back**: only when `catalog/`, `scoring/`, `README.md`, or `sources/SOURCES.md` change (timestamp-only deltas filtered)
- **Manual dispatch**: `workflow_dispatch` available for ad-hoc re-scans (e.g., after adding a store to `supported-stores.json`)
- **Editorial review on PR**: each catalog-refresh PR is the human surface for any deltas — score changes, new plugins, staleness flags

## What the Mall does vs out-of-scope

| Concern | Owner |
|---|---|
| Add / remove a source store from `supported-stores.json` | **Mall** (this skill + source-inventory) |
| Tune trust score weights | **Mall** (this skill + compute-trust.cjs) |
| Scan / score / render / publish pipeline | **Mall** |
| Decide a plugin earns a slot in any consumer project's baseline | **Out of scope** (consumer-owned decision) |
| Coherence with a specific consumer project | **Out of scope** (consumer-owned audit) |
| Reframe what counts as "curated" | **Out of scope** (editorial decision, not pipeline) |
| Periodic review of how the catalog is consumed downstream | **Out of scope** (consumer-owned)  |

If a question crosses the line into editorial or downstream policy, route it out of the workflow. Don't self-modify cross-repo policy from inside the Mall.

## Curation log

Every editorial Mall decision lands in `docs/curation-log.md` in this repo (Mall's own append-only log). Decisions ship with re-eval dates; routine refreshes do not need log entries unless they triggered a curation action.

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Editing brain files (skills/instructions/prompts/agents) under `plugins/` during the workflow | The workflow MUST NOT modify `plugins/` — editorial changes ship via PR review only. The workflow only writes to `catalog/`, `scoring/`, `README.md`, `sources/SOURCES.md`. |
| Bootstrap re-cloning `plugin-mall` from itself | `bootstrap-sources.cjs` MUST filter `name !== "plugin-mall"`. |
| Scan skipping `plugin-mall` | `scan-sources.cjs` MUST include `plugin-mall` (walks `$REPO_ROOT/plugins/`, not bootstrapped sources). |
| Trust score without published signals | Every score MUST come with its signal breakdown in `catalog/stores/<store>.json` `trust_signals` field. |
| Hardcoded "curated" tier flag in code | There is NO tier flag in the schema. Curation bias emerges from `provenance: true` in `supported-stores.json`. |
| Quietly fudging the license signal so Mall scores 100 | Score honestly. PolyForm-NC = 7/10. The provenance +50 already carries the first-party trust weight. |

## Falsifiability

This skill needs revision if any of the following occur by **2026-08-29** (90 days):

- The workflow modifies a file outside `catalog/`, `scoring/`, `README.md`, `sources/SOURCES.md` ≥1 time
- Trust scores cluster oddly (e.g., third-party score consistently > 60 — provenance bonus undercalibrated)
- Mall-curated plugins fail to rank #1 in `/mall-search` for the same name as a third-party entry (provenance signal not flowing)
- A new source-shape (frontmatter convention) breaks `normalize-frontmatter.cjs` ≥2 times without surfacing in `scoring/trust-audit.md`
- The boundary table (what the Mall does vs out-of-scope) produces wrong-routing decisions ≥2 times in a quarter

Track in `docs/curation-log.md` tagged `[MALL-SELF-CURATION]`.

## Related

- [source-inventory/SKILL.md](../source-inventory/SKILL.md) — managing `supported-stores.json`
- [store-evaluation/SKILL.md](../store-evaluation/SKILL.md) — scoring a candidate store before adding it
- [staleness-discipline/SKILL.md](../staleness-discipline/SKILL.md) — pruning stale entries
- [mall-maintenance-rules.instructions.md](../../instructions/mall-maintenance-rules.instructions.md) — always-on routing for this skill
