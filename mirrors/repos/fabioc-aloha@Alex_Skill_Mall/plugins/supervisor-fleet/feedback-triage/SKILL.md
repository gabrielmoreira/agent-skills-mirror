---
type: skill
lifecycle: stable
inheritance: master-only
name: feedback-triage
description: Categorize, deduplicate, and route fleet feedback to Edition fix, Mall change, or AlexMaster escalation
tier: standard
applyTo: '"**/feedback/inbox/**"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Feedback Triage

Process incoming feedback from ACT-Edition heirs. Triage classifies each item, deduplicates against open issues, and routes to the right destination.

## When to Use

- A new file lands in `feedback/inbox/`
- A scheduled triage sweep runs (recommended weekly)
- A pattern emerges across recent feedback that warrants escalation

## The Three Routes

Every feedback item goes to exactly one of three destinations:

| Route | When | Destination |
|---|---|---|
| **Edition fix** | The brain template needs a change (skill bug, instruction gap, prompt error) | `Alex_ACT_Edition` PR |
| **Mall change** | A skill/store is broken, stale, or missing from the marketplace | `Alex_Skill_Mall` PR |
| **AlexMaster escalation** | Touches ACT framework, non-ACT heirs, or fleet-wide governance | `AlexMaster/AI-Memory/feedback/` |

## Triage Steps

### Step 1 — Categorize

Read the item and tag it with one of:

| Category | Definition |
|---|---|
| `bug` | An artifact in Edition or Mall produces incorrect output |
| `friction` | The artifact works but is awkward, slow, or confusing |
| `feature-request` | A new artifact or capability is being requested |
| `success` | A win worth recording (informs future patterns) |
| `framework` | Touches ACT manifesto, tenets, or claims — escalate |

### Step 2 — Deduplicate

Search `feedback/inbox/` and `decisions/` for similar items in the last 90 days:

```text
grep -ri "<keyword>" feedback/ decisions/
```

If a match exists:

- **Identical**: link the new item to the existing thread, close the new file
- **Related (same root cause)**: merge into the existing thread, note the new symptom
- **Distinct**: keep separate

### Step 3 — Severity

| Level | Definition | Action window |
|---|---|---|
| `critical` | Blocks fleet adoption or causes data loss | Same day |
| `high` | Blocks a heir or breaks a documented workflow | Within 1 week |
| `medium` | Friction but workaround exists | Next release |
| `low` | Cosmetic or nice-to-have | Backlog |

### Step 4 — Route

Apply the route table above. Move the file:

- Edition fix → open PR against `../Alex_ACT_Edition` with the verdict attached
- Mall change → open PR against `../Alex_Skill_Mall`
- Escalation → write a stub to `../AlexMaster/AI-Memory/feedback/` (if AlexMaster is local) or open an issue (if remote)

### Step 5 — Record

Append a row to `decisions/curation-log.md` (format below). This feeds the 60-day mechanical-vs-semantic re-evaluation per [ADR-001](../../../decisions/ADR-001-lane-0-audit.md).

## Curation Log Format

```markdown
| Date | Item | Category | Severity | Route | M/S | Notes |
|---|---|---|---|---|---|---|
| 2026-04-28 | mall-link-rot-01 | bug | medium | Mall change | M | 3 dead links in STORES.md |
```

Where `M/S` is **Mechanical** (script could detect) or **Semantic** (judgment required).

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Routing every item to "Edition fix" by default | Many items belong in the Mall or AlexMaster — read carefully |
| Skipping deduplication on busy weeks | Dedup is what prevents the inbox from becoming append-only noise |
| Auto-escalating ambiguous items | Escalation is a last resort, not a default. Ask first |
| Forgetting to record M/S classification | The 60-day re-eval depends on this signal |

## Related

- [brain-curation-rules](../../instructions/brain-curation-rules.instructions.md)
- [skill-review](../skill-review/SKILL.md) — for items routed to Edition
- `/triage-feedback` prompt
