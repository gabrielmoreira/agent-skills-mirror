---
name: staleness-discipline
description: "Detect, classify, and prune stale source stores in the Mall — define what stale means and how to remove gracefully without breaking downstream consumers."
lastReviewed: 2026-05-29
---

# Staleness Discipline

Define what "stale" means for a source store in the Mall, and how to remove an entry from `sources/supported-stores.json` without breaking downstream consumers.

The Mall is read-mostly: downstream agents install from upstream at pinned refs. Pruning a source from the registry stops new catalog entries from that source but does not retroactively break existing installs (those still resolve to their pinned SHA). The discipline below keeps the catalog honest.

## When to Use

- Weekly catalog-refresh PR shows a store with degraded signals (no recent commits, broken license signal, archived upstream)
- A reviewer flags a store as no longer fit during PR review
- `/prune-source` invocation

## What "stale" means

An entry is stale if **any** of these apply:

| Signal | Threshold | Where it shows up |
|---|---|---|
| Remote unreachable | `bootstrap-sources.cjs` clone fails in 2+ consecutive cron runs | Workflow log |
| Upstream archived | `fetch-github-stats.cjs` returns `archived: true` | `scoring/github-stats.json` |
| No upstream activity | `last_commit` older than 18 months | `scoring/github-stats.json` + maintenance signal = 0 |
| License changed unfavorably | SPDX id changed to NOASSERTION or to a more restrictive license | `scoring/github-stats.json` `license` field |
| Replaced by superior alternative | Another source covers the same domain better with higher trust scores | Per-store trust delta in `scoring/trust-audit.md` |
| Persistent scan failure | `scan-sources.cjs` produces 0 plugins for 2+ consecutive runs after previously producing >0 | `catalog/stores/<name>.json` `plugins` array shrinks to 0 |
| Schema or shape drift | `normalize-frontmatter.cjs` warns or errors on >50% of plugins from that source | Normalize log |

## Classification

| Stale signal | Action |
|---|---|
| Remote unreachable, but upstream still alive on GitHub | Refresh — fix `remote` URL, don't prune |
| Upstream archived but plugins still valuable | Keep (note `archived` in PR review); catalog continues to surface them with degraded maintenance score |
| Upstream archived + no activity for years | Prune |
| License changed to unclear or restrictive | Surface in PR review; user decides whether to keep with degraded license signal or prune |
| Replaced by superior alternative | Prune the worse entry; downstream consumers can opt into the better one via `--from-store` override |
| Persistent scan failure with no clear cause | Investigate `pluginDir` first — upstream may have renamed the folder. Only prune after fix attempts fail. |

## Pruning procedure

Pruning is **always reversible by re-add**. The two-step removal (comment-out → observe → delete) is the safety net. Run via `/prune-source`.

1. Confirm at least one staleness signal above fires
2. Comment out the entry in `sources/supported-stores.json` and add `// pruned-pending: YYYY-MM-DD reason: <reason>` above it
3. Commit `[behaviour] prune source (pending): <name> — <reason>`
4. Wait one weekly cron cycle and verify the catalog-refresh PR shows:
   - The store missing from `catalog/stores/`
   - Plugin count drops by the right amount in `catalog/index.json`
   - No other unintended diffs
5. After a clean cycle, delete the commented-out entry and commit `[behaviour] prune source (delete): <name>`
6. Record the decision in `docs/curation-log.md`

## Re-add procedure

If a pruned store revives (un-archived, link restored, license clarified):

1. Run full [store-evaluation](../store-evaluation/SKILL.md) — past acceptance does not transfer
2. If it passes, add a fresh entry via `/add-source`
3. Record the re-add in `docs/curation-log.md`

## Pruning anti-patterns

| Anti-pattern | Correction |
|---|---|
| Hard-deleting the entry in one commit | Always use the two-step (comment-out → observe → delete) so the catalog refresh PR can verify the impact cleanly |
| Skipping the observation cycle | Without one clean cron run, you don't know whether the catalog-refresh PR will surface only the expected diffs |
| Pruning multiple stores in one commit | Each prune is a decision; bundle wastes the audit trail and makes one bad prune undoable without reverting the others |
| Pruning for "I don't like the maintainer" or subjective reasons | The staleness signals are the bar; the commit message must cite the firing signal |
| Pruning `plugin-mall` itself | Constitutional to this Mall — would break the catalog's ability to surface first-party plugins |

## Output template (PR comment for a prune proposal)

```markdown
**Prune candidate: `<store-name>`**

Staleness signals firing:
- [x] <signal 1>: <evidence from workflow log / github-stats / trust-audit>
- [ ] ...

Action: comment-out now, delete after one clean cron cycle.

Downstream impact: <known consumers, if any; otherwise "no known consumers; downstream agents that depend on this store can pin to a specific SHA before deletion">
```

## Falsifiability

This skill is wrong if any of the following occur by **2026-08-29** (90 days):

- Pruned stores are re-added within 30 days ≥2 times in a quarter (staleness signals miscalibrated — pruning prematurely)
- A store flagged as stale by these signals is still being actively used by a known downstream consumer (signals threshold too aggressive)
- The two-step procedure causes a registry-vs-catalog drift that ships ≥1 time (the reversible pattern is leaking)

Track outcomes in `docs/curation-log.md` tagged `[STALENESS]`.

## Related

- [source-inventory](../source-inventory/SKILL.md) — adding and editing registry entries
- [store-evaluation](../store-evaluation/SKILL.md) — gate for re-add
- [mall-self-curation](../mall-self-curation/SKILL.md) — the pipeline this discipline keeps clean
- [mall-maintenance-rules](../../instructions/mall-maintenance-rules.instructions.md) — always-on routing
- `/prune-source` prompt
