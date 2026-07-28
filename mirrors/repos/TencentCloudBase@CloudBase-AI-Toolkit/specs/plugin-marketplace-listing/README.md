# Plugin Marketplace Listing

Maintainer tooling to track AI IDE / agent plugin markets and CloudBase listing readiness.

## Files

| Path | Role |
|------|------|
| `markets.yaml` | Machine-readable matrix (source of truth) |
| `reports/latest.md` | Human report (generated) |
| `reports/latest.json` | Machine report (generated) |
| `requirements.md` / `design.md` / `tasks.md` | Spec |

## Commands

```bash
# Offline analysis (default)
npm run analyze:plugin-marketplaces

# Custom paths
node scripts/analyze-plugin-marketplace.mjs --out specs/plugin-marketplace-listing/reports

# Fail if packaging-critical local evidence is missing/invalid
node scripts/analyze-plugin-marketplace.mjs --strict

# Optional URL reachability probes
node scripts/analyze-plugin-marketplace.mjs --online
```

## How to update the matrix

1. Edit `markets.yaml` only — do not hardcode market IDs in the script.
2. Set each `listing_statuses.*` to one of: `listed` | `submittable` | `blocked` | `not_applicable` | `unknown`.
3. Prefer explicit `unknown` over guessing.
4. Bump `last_reviewed_at` (YYYY-MM-DD) when you re-check a market.
5. Use `priority_hint` only when automatic classification is wrong.
6. Re-run the analyzer and commit updated `reports/latest.*` if you want the snapshot in git.

## Manual submissions

See [`submission-checklist.md`](./submission-checklist.md) for ready-to-submit market steps.

## Reading the report

Priority groups:

- `ready_to_submit` — can start manual submission now
- `needs_packaging_or_manifest` — missing local packaging (e.g. Cursor `.cursor-plugin`)
- `needs_partner_outreach` — no public self-serve path (or unclear)
- `listed` — already discoverable / built-in / self-marketplace ready
- `not_applicable` — wrong channel (e.g. Trae `.vsix` store)
- `unknown` — needs another research pass

**This tooling never auto-submits.**

## Tests

```bash
npx vitest run tests/plugin-marketplace-listing.test.js
```
