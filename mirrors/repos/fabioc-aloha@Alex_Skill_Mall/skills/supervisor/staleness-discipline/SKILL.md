---
type: skill
lifecycle: stable
inheritance: master-only
name: staleness-discipline
description: Detect, classify, and prune stale entries in Alex_Skill_Mall — define what stale means and how to remove gracefully
tier: standard
applyTo: '"**/Alex_Skill_Mall/STORES.md,**/Alex_Skill_Mall/CATALOG.md"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Staleness Discipline

Define what "stale" means in the Mall and how to remove entries without breaking heirs that depend on them.

## When to Use

- Monthly mall audit (fired by `/audit-mall`)
- A heir reports a broken or outdated entry
- A `/prune-store` invocation
- Coherence-check finds an Edition reference to a Mall entry that should be pruned

## What "Stale" Means

An entry is stale if **any** of these apply:

| Signal | Threshold |
|---|---|
| Link unreachable | HTTP 4xx/5xx for 2+ consecutive checks across 7 days |
| Upstream archived | Repo settings show "Archived" or equivalent |
| No upstream activity | No commits, releases, or issue activity in 18+ months |
| License changed unfavorably | Switched to a more restrictive or unclear license |
| Description drift | Mall description no longer matches upstream README's description |
| Replaced by superior alternative | Another Mall entry covers the same ground better |
| Heir reports persistent breakage | ≥ 2 heirs report the entry doesn't work as documented |

## Classification

| Stale signal | Action |
|---|---|
| Link unreachable, but upstream still active | Refresh (update URL) — not prune |
| Upstream archived but stable | Keep, mark `archived: stable` in entry |
| No activity AND archived | Prune |
| License change | Defer to ACT pass — license escalation may need AlexMaster input |
| Description drift only | Refresh |
| Replaced by superior alternative | Prune the worse entry, update the better one's description |
| Persistent heir breakage | Investigate before pruning — may be a Mall-side fix |

## Pruning Procedure

Pruning is **always reversible by re-add**. Never delete history.

1. Run [mall-curation](../mall-curation/SKILL.md)'s decision tree to confirm prune is correct
2. Check coherence: does any Edition skill or instruction reference the entry being pruned?
   - If yes, fix the Edition reference *first* (open Edition PR), then prune
   - If no, proceed
3. Comment out the entry in STORES.md and CATALOG.md (do not delete)
4. Add a `pruned: YYYY-MM-DD reason: <reason>` line above the commented entry
5. Update README counts
6. Open Mall PR titled `prune: <entry name> (<reason>)`
7. After merge, document in `decisions/` if this prune sets a class precedent
8. Record in `decisions/curation-log.md` with `M` or `S` classification

## Pruning Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Hard-deleting the entry | Comment out instead — preserves history and reversibility |
| Skipping the coherence check | Pruning a referenced entry breaks the Edition for fleet heirs |
| Pruning without updating README counts | The Mall claims N stores; the count must match reality |
| Pruning multiple entries in one PR without separate rationales | Each prune is a decision; bundle wastes the audit trail |

## Re-Add Procedure

If a pruned store revives (un-archived, link restored, license clarified):

1. Run full [store-evaluation](../store-evaluation/SKILL.md) — past acceptance does not transfer
2. If it passes, uncomment in STORES.md and CATALOG.md
3. Update the prune line to `re-added: YYYY-MM-DD`
4. Increment counts

## Output Template (prune verdict)

```markdown
# Prune Verdict — <store name>

**Entry**: <STORES.md line or CATALOG.md ID>
**Date**: YYYY-MM-DD
**Reason**: <which staleness signal fired>

## Coherence Check

- Edition references: <count>
- References fixed first: yes/no
- Files affected: <list>

## Counts After Prune

- STORES.md: <before> → <after>
- CATALOG.md: <before> → <after>
- README badge: <before> → <after>

## ADR?

Yes | No — <if yes, link to decisions/ADR-NNN>

## ACT Pass Trail

<markers>
```

## Related

- [mall-curation](../mall-curation/SKILL.md)
- [store-evaluation](../store-evaluation/SKILL.md)
- [mall-maintenance-rules](../../instructions/mall-maintenance-rules.instructions.md)
- `/prune-store` prompt
