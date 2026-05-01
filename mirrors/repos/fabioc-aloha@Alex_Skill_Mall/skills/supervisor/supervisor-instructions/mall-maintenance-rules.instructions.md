---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Always-on routing for Mall maintenance — connects audit invocations, store proposals, and staleness signals to the right skill"
application: "Active whenever the Supervisor touches Alex_Skill_Mall files"
applyTo: "**/Alex_Skill_Mall/**,**/STORES.md,**/CATALOG.md,**/feedback/inbox/*store*"
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Mall Maintenance Rules

Routing rules for any work touching `Alex_Skill_Mall`.

## Routing Table

| Trigger | Skill | Prompt |
|---|---|---|
| `feedback/inbox/*store-proposal*.md` lands | [store-evaluation](../skills/store-evaluation/SKILL.md) | `/add-store` |
| Periodic audit (monthly or on-demand) | [mall-curation](../skills/mall-curation/SKILL.md) | `/audit-mall` |
| Staleness signal (broken link, archived upstream, low velocity) | [staleness-discipline](../skills/staleness-discipline/SKILL.md) | `/prune-store` |
| Heir reports broken Mall entry | [staleness-discipline](../skills/staleness-discipline/SKILL.md) → maybe escalate | `/prune-store` |
| Edition references a non-existent Mall entry | Coherence-fix first, then audit | `/audit-mall` |

## Hard Rules

1. **Never edit `Alex_Skill_Mall/` directly without invoking the Supervisor flow** — every change must be auditable through one of the three trifecta skills.
2. **Counts are sacred** — STORES.md count, CATALOG.md count, and README badge must agree after every change. Mechanical scripts (`mall-link-check.cjs`, `stores-staleness.cjs`) verify on a future PR gate.
3. **Pruning is reversible by re-add, never by delete** — comment out, don't remove.
4. **Two-source rule for adds** — every store needs at least two independent quality signals (see [store-evaluation](../skills/store-evaluation/SKILL.md) §1–2).
5. **ACT pass for every prune** — pruning is a quality decision; it must show alternatives, disconfirmers, and severity.
6. **Coherence before pruning** — if any Edition skill or instruction references the entry, fix Edition *first*.

## Cardinal Test

Before any commit to the Mall, ask: *Could a heir's brain-qa script reproduce this decision from the audit trail?* If no, the trail is incomplete.

## When to Escalate

| Situation | Escalate to |
|---|---|
| License of an existing entry changes ambiguously | AlexMaster (framework-level legal call) |
| > 30% of Mall entries flagged stale in one audit | AlexMaster (signal of process failure, not just maintenance work) |
| Coherence-fix would touch 5+ Edition files | Open coordinated PR pair (Edition + Mall) and pause until both reviewed |
| Proposal is for a new *category* of store, not a single entry | Defer to next Lane 4 (cross-repo coherence) review |

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Skip ACT pass on "obvious" prunes | Obviousness is exactly when alternatives are skipped — run the pass |
| Update STORES.md but forget README count | Counts are part of the contract; mechanical script will catch but trail is cleaner if the human catches first |
| Prune without checking Edition references | The fleet breaks silently |
| Treat the Mall as personal preference list | The Mall serves heirs; preferences are out of scope |

## Related

- [mall-curation](../skills/mall-curation/SKILL.md)
- [store-evaluation](../skills/store-evaluation/SKILL.md)
- [staleness-discipline](../skills/staleness-discipline/SKILL.md)
- [brain-curation-rules](./brain-curation-rules.instructions.md) — sibling rules for Edition curation
