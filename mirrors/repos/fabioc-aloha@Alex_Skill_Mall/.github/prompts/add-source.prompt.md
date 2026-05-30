---
description: "Guided add of a new source store to sources/supported-stores.json — evaluate, register, refresh, verify catalog impact"
lastReviewed: 2026-05-29
---

# /add-source

Add a new source store (a third-party plugin repo) to the Mall's registry. Runs the [store-evaluation](../skills/store-evaluation/SKILL.md) scorecard first; on Accept, registers in `sources/supported-stores.json` and verifies the next scan picks it up.

## Steps

1. Apply [store-evaluation](../skills/store-evaluation/SKILL.md) to the proposed remote URL. Score against the five dimensions (maintenance, adoption, license, ACT fit, docs). If total < 7, decline and record rationale in the conversation.
2. On Accept (score ≥ 7):
   - Determine `name` (kebab-case, ≤32 chars, matches the conventional short identifier)
   - Determine `pluginDir` (where plugins live in the upstream repo: `.`, `plugins`, `skills`, `agents`, etc.)
   - Determine `quality` tier: `internal`, `official`, `community-curated`, `community`, `domain`, or `reference`
   - Determine `provenance: false` (third-party) and known `license` if extractable from upstream
3. Add the entry to `sources/supported-stores.json` (alphabetical by `name`).
4. Run `node scripts/scan-sources.cjs` locally with `SOURCES_DIR` pointing at a temp dir; verify the new store produces `catalog/stores/<name>.json` with a plausible plugin count.
5. Run `node scripts/compute-trust.cjs` and `node scripts/render-catalog.cjs`; confirm the new store appears in `README.md` ranked by trust.
6. Commit `[behaviour] add source: <name> (<one-line rationale>)`.
7. Push and let Monday's cron produce the first full catalog refresh against the new source.

## Boundaries

- Do not skip the scorecard. Stores below score 7 do not get added even if the requester insists — record the decline.
- Do not invent `quality` tier; if the upstream doesn't fit an existing tier, propose a new tier in a separate ADR-style discussion first.
- Do not bypass `provenance: true` for any third-party store. Provenance is for first-party Mall-curated only.
- Do not commit catalog regeneration in the same commit as the registry edit; let the cron own that refresh so the diff is reviewable.

## Would Revise If

Revise this prompt by **2026-08-29** (90 days) or sooner if:
- The store-evaluation scorecard admits 2+ stores that get pruned within 90 days of acceptance (scorecard too lax)
- Steps 4–5 are skipped 2+ times because "the cron will catch it" and a broken registry entry ships (verification deferred)
- `quality` tier assignment is contested 2+ times in a quarter (tier taxonomy needs revision)
