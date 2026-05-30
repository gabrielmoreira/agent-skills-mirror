---
description: "Always-on routing for Mall maintenance work — fires the right Mall skill at the right moment. Distinguishes Mall-owned automation from out-of-scope editorial work."
applyTo: "**"
lastReviewed: 2026-05-29
---

# Mall Maintenance Rules

The Plugin Mall is self-curating. This always-on rule routes any Mall-internal work to the right skill at the right moment.

## Routing Table

| Trigger | Fire skill |
|---|---|
| Pipeline operations (scan / score / render / publish) | [mall-self-curation](../skills/mall-self-curation/SKILL.md) |
| Add / remove a source store in `supported-stores.json` | [source-inventory](../skills/source-inventory/SKILL.md) |
| Evaluate a candidate store before adding it to the registry | [store-evaluation](../skills/store-evaluation/SKILL.md) |
| Source store appears stale (no upstream activity, broken remote, etc.) | [staleness-discipline](../skills/staleness-discipline/SKILL.md) |
| Catalog refresh PR (`catalog-refresh/YYYY-MM-DD`) needs review | [mall-self-curation](../skills/mall-self-curation/SKILL.md) § Workflow + cadence |
| New plugin shape (frontmatter convention) breaks the scan | [mall-self-curation](../skills/mall-self-curation/SKILL.md) § Anti-Patterns + `normalize-frontmatter.cjs` |
| Trust score formula tuning | [mall-self-curation](../skills/mall-self-curation/SKILL.md) § Trust scoring formula |
| Substantive change worth consolidating | [meditation](../skills/meditation/SKILL.md) |
| Stale brain file (`lastReviewed` expired) | [currency-audit](../skills/currency-audit/SKILL.md) |
| Curated plugin under `plugins/<category>/<name>/` needs editorial change | **Out of automation scope** — editorial changes ship via PR review, not via the workflow |
| Downstream consumer reports a broken plugin reference | **Out of automation scope** — fix the consumer reference first; the Mall does not own consumer policy |

## Hard Rules (cannot be overridden)

1. **The workflow MUST NOT modify `plugins/`.** Mall self-curation is automation over `catalog/`, `scoring/`, `README.md`, `sources/SOURCES.md` only. Editorial changes to curated plugins ship via PR review.
2. **Bootstrap MUST skip `plugin-mall`.** The Mall self-entry in `supported-stores.json` is for scan inclusion, not clone inclusion. `bootstrap-sources.cjs` filters `name !== "plugin-mall"`.
3. **Scan MUST include `plugin-mall`.** The self-scan walks `$REPO_ROOT/plugins/` and produces `catalog/stores/plugin-mall.json` like any other store.
4. **Every commit touching brain artifacts** (skills, instructions, workflow files) carries a severity tag per [severity-tagged-commits](./severity-tagged-commits.instructions.md) — `[typo | clarification | behaviour | constitutional]`. Structural changes to the trust formula or pipeline shape are `[behaviour]`; reframes of the constitutional boundary are `[constitutional]`.
5. **The Mall does not own downstream policy.** If the question is "should a consumer project use this plugin?" the answer comes from that consumer, not from the Mall. The Mall scores; consumers decide.

## What the Mall does vs out-of-scope

| What the Mall does | Out of scope for the Mall |
|---|---|
| Source registry (`supported-stores.json`) maintenance | Editorial decisions on individual curated plugins |
| Scan pipeline (scripts under `scripts/scan-*.cjs`) | Deciding which plugins consumer projects should bundle |
| Trust scoring + published signals | Coherence with any specific consumer project |
| Catalog publishing (`catalog/`, `scoring/`, rendered MD) | Constitutional reframes of what counts as "curated" |
| Staleness detection + pruning of catalog entries | Periodic review of how the catalog is used downstream |

The line is: **the Mall owns mechanical and data-driven operations over its own catalog; everything editorial or downstream is out of scope.**

## Would Revise If

Revise by **2026-08-29** (90 days) or sooner if any of the following fires:

- The routing table sends a Mall-internal operation outside the Mall ≥2 times in a quarter (boundary miscalibrated)
- Hard Rule 1 (workflow does not modify `plugins/`) is violated ≥1 time
- Hard Rule 5 (Mall does not own downstream policy) is violated ≥1 time — Mall self-modifies cross-repo policy
- A new operation surfaces that isn't covered by the routing table ≥2 times in a quarter (table incomplete)

Track in `docs/curation-log.md` tagged `[MALL-ROUTING]`.
