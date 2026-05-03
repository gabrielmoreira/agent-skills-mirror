---
type: skill
lifecycle: stable
inheritance: master-only
name: mall-curation
description: Curate Alex_Skill_Mall — decide when to add, keep, refresh, or prune stores and catalog entries
tier: standard
applyTo: '"**/Alex_Skill_Mall/**,**/STORES.md,**/CATALOG.md"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Mall Curation

Maintain `Alex_Skill_Mall` as a high-signal marketplace. Curation is judgment-driven — every entry should earn its place.

## When to Use

- Periodic mall audit (recommended monthly, fired by `/audit-mall`)
- A proposal lands in `feedback/inbox/` to add a new store
- A heir reports a Mall entry is broken, stale, or wrong
- A regression in cross-repo coherence (Edition references a store the Mall has dropped)

## The Four Curation Verbs

Every Mall entry exists in one of four states. Curation moves entries between states.

| Verb | When | Action |
|---|---|---|
| **Add** | A proposed store passes [store-evaluation](../store-evaluation/SKILL.md) | Insert into STORES.md and CATALOG.md, update README counts |
| **Keep** | An entry passes the staleness sweep | No change; record audit timestamp |
| **Refresh** | An entry's metadata, link, or description has drifted but the store is still valuable | Update in place; note the change in commit message |
| **Prune** | An entry fails [staleness-discipline](../staleness-discipline/SKILL.md) and refresh won't save it | Remove from STORES.md and CATALOG.md, update counts, document in `decisions/` |

## Curation Decision Tree

```text
For each entry under audit:
├── Is the link reachable (HTTP 2xx)?
│   ├── No → Refresh (update URL) or Prune
│   └── Yes ↓
├── Has the upstream repo been updated in the last 6 months?
│   ├── No, and repo is archived → Prune
│   ├── No, but repo is alive → Keep with note ("low-velocity")
│   └── Yes ↓
├── Does the description still match upstream README?
│   ├── No → Refresh
│   └── Yes ↓
├── Is the entry still relevant to ACT-Edition heirs?
│   ├── No (orphan domain, replaced by better option) → Prune
│   └── Yes → Keep
```

## Hard Rules

1. **Pruning is reversible by re-add, not by undo** — never delete entries; comment them out and document in `decisions/`. This preserves history.
2. **Counts in README must match** — STORES.md count, CATALOG.md count, README badge must agree after any add/prune. Run `mall-link-check.cjs` (when shipped) or grep manually.
3. **Two-source rule for additions** — a new store needs ≥2 independent signals (e.g., heir feedback + upstream stars + active maintenance) before it's added.
4. **Pruning sets precedent** — every prune that defines a class ("we don't accept solo-author stores under N stars") becomes an ADR.

## Output Template (audit report)

```markdown
# Mall Audit — YYYY-MM-DD

## Summary

- Entries audited: <count>
- Add candidates: <count>
- Keep: <count>
- Refresh: <count>
- Prune candidates: <count>
- Coherence violations: <count>

## Add Candidates

| Proposal | Source | Score | Verdict |
|---|---|---|---|

## Refresh List

| Entry | Issue | Proposed change |
|---|---|---|

## Prune Candidates

| Entry | Reason | ADR? |
|---|---|---|

## ACT Pass Trail

<paste markers>
```

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Bulk prune without per-entry rationale | Each prune cites which gate failed |
| Adding stores because they're popular elsewhere | Two-source rule still applies |
| Refreshing in place without committing the diff | Audit trail matters — every refresh is a commit |
| Skipping coherence check after prune | Editions may reference the pruned store; cross-check before commit |

## Related

- [store-evaluation](../store-evaluation/SKILL.md) — gate for adds
- [staleness-discipline](../staleness-discipline/SKILL.md) — gate for prunes
- [mall-maintenance-rules](../../instructions/mall-maintenance-rules.instructions.md) — always-on routing
- `/audit-mall`, `/add-store`, `/prune-store` prompts
