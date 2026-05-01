# ADR-NNN: Quarterly Brain Retraining Pass — Q[N] [YYYY]

**Status**: Proposed | Accepted | Implemented
**Date**: YYYY-MM-DD
**Decision-maker**: Fabio Correa
**Quarter**: Q[N] [YYYY] (anchor: Edition v[X.Y.Z] shipped YYYY-MM-DD)
**Cadence reference**: [.github/copilot-instructions.md § Brain Retraining Cadence](../../.github/copilot-instructions.md)

---

## Why this pass exists

Cardinal Rule 3 in the Supervisor brain says critical thinking must be applied *and* evolved. The Brain Retraining Cadence schedules a full retraining pass every quarter against two evidence streams:

1. **Mall reality.** New skills, retired stores, updated patterns in `Alex_Skill_Mall`.
2. **Heir feedback from AI-Memory.** Real friction in real projects, written to `AI-Memory/feedback/alex-act/`.

Skipping a quarter is a Cardinal Rule 3 violation, not a deferral. This ADR is the artifact that proves the cycle ran.

---

## Evidence streams reviewed

### A. Mall changes since last quarterly pass

| Date range | Source | Findings |
|---|---|---|
| YYYY-MM-DD to YYYY-MM-DD | `Alex_Skill_Mall` git log | New skills added: N. Skills retired: N. Stores added/pruned: N. |

| Skill / store | Change | Edition impact |
|---|---|---|
| (e.g. `converters/md-to-pdf`) | Added in Mall, not in Edition | Promotion candidate |
| (e.g. `converters/md-to-word`) | Updated in Mall | Edition copy is stale |

### B. Heir feedback from AI-Memory

| Date range | Inbox path | Items processed |
|---|---|---|
| YYYY-MM-DD to YYYY-MM-DD | `AI-Memory/feedback/alex-act/` | N items, N hotfixed, N deferred, N rejected |

| Feedback item | Severity | Pattern | Action |
|---|---|---|---|
| (summary) | critical/high/medium/low | Bug / friction / feature / success | Edition fix / Mall change / escalate |

### C. Edition skills aged > 90 days without review

Walk the `brain-qa` semantic-review queue (`node scripts/brain-qa.cjs --json`) oldest-first. Skills with `lastReviewed` older than 90 days as of this pass:

| Skill / instruction | Last reviewed | Mall counterpart? | Decision |
|---|---|---|---|
| (e.g. `md-to-word`) | YYYY-MM-DD | Yes | Diff against Mall; upgrade or refresh `lastReviewed` |

---

## Decisions

### CT trifecta evolution (Cardinal Rule 3 falsifiability requirement)

> Cardinal Rule 3 requires ≥1 CT-trifecta refinement per quarter driven by real evidence. Document the refinement here, or document why none was needed with evidence.

| Trifecta file | Change | Evidence |
|---|---|---|
| `critical-thinking.instructions.md` | (e.g. added disconfirmer for X failure mode) | Heir feedback item Y |
| (or) None this quarter | (no failure modes surfaced; brain-qa clean across all releases; feedback shows no CT regressions) | Quarterly evidence summary |

Tag in `decisions/curation-log.md`: `[CT-EVOLUTION]`

### Edition skill upgrades

| Skill | Source pattern | Change |
|---|---|---|
| (e.g. `md-to-word`) | `Alex_Skill_Mall/skills/converters/md-to-word/` | Ported table-handling improvements, added converter-qa hooks |

### Edition skill retirements

| Skill | Reason | Replacement |
|---|---|---|
| (if any) | (not earning its tokens; see usage evidence) | (Mall skill loaded on demand, or none) |

### Mall promotion candidates

| Mall skill | Why promote to Edition | Risk |
|---|---|---|
| (e.g. `converters/md-to-pdf`) | Heir feedback shows N requests in window | Low — single SKILL.md, no deps |

### Releases shipped this quarter

| Edition version | Date | Bump type | Summary |
|---|---|---|---|
| v[X.Y.Z] | YYYY-MM-DD | major / minor / patch | (one line) |

---

## Falsifiability for this pass

This pass is wrong if any of these turn out to be true within the next quarter:

- A heir reports a regression traceable to a skill upgrade shipped in this pass
- Brain-qa fails on a CT instruction modified in this pass
- A retired skill is requested by a heir and the Mall counterpart does not satisfy the use case
- A promoted Mall skill is reverted within 30 days of promotion

If any of those fire, log a **post-mortem entry in `decisions/curation-log.md`** referencing this ADR.

---

## Pass-skipping clause

A quarter may go by without an ADR **only if** the curation log shows:

- Zero hotfixes shipped (no `critical` feedback items in the quarter)
- Zero CT-trifecta refinements (no failure modes surfaced)
- Brain-qa clean across all release commits in the window
- Mall snapshot has no promotion candidates above the trust bar

If those conditions hold, write a one-paragraph "no-action quarter" entry in `decisions/curation-log.md` instead of a full ADR. **Two consecutive no-action quarters is itself a flag** — likely means the cadence is not being run, not that nothing changed.

---

## Approval

- [ ] CT trifecta change documented (or absence justified with evidence)
- [ ] Mall promotion candidates evaluated against trust bar
- [ ] Skills aged > 90 days without `lastReviewed` update have a decision recorded
- [ ] Heir feedback inbox is empty or has documented deferral
- [ ] Brain-qa clean on Edition main
- [ ] Approved by: Fabio Correa
- [ ] Date: YYYY-MM-DD
