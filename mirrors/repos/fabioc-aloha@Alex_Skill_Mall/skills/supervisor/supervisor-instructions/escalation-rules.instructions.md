---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Always-on rules for what stays in the Supervisor and what escalates to AlexMaster"
application: "Active during all triage, audit, and review work — fires before any commit that could touch framework concerns"
applyTo: "**/feedback/**,**/.github/**,**/PLAN.md,**/decisions/**"
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Escalation Rules

The Supervisor's Cardinal Rule: **Defer to AlexMaster on framework-level concerns; own everything ACT-specific.** This file makes that rule operational.

## The Cardinal Test (always run first)

Before any commit, change, or accepted feedback item, ask: **Does AlexMaster do this?**

If yes → escalate. If no → in-house.

When uncertain → escalate. Cost of asking is low; cost of overreach is high (creates fleet drift, undermines AlexMaster as the framework source of truth).

## Always Escalate

| Signal | Why |
|---|---|
| Proposal for a new ACT tenet | Tenets are framework |
| Change to frontmatter spec, inheritance tiers, or copilot-instructions structure | Brain spec is framework |
| Change to how ACT pass works (steps, markers, trigger calibration) | ACT discipline is framework |
| New artifact type (beyond skill / instruction / prompt / agent / muscle) | Type system is framework |
| Cross-fleet pattern in 3+ heirs | Framework signal, not curation |
| Anything that would require modifying inherited artifacts in Edition | Inherited = AlexMaster-owned |

## Always In-House

| Signal | Skill |
|---|---|
| New domain skill submission to Edition | [skill-review](../skills/skill-review/SKILL.md) |
| New Mall store | [store-evaluation](../skills/store-evaluation/SKILL.md) |
| Mall prune or refresh | [staleness-discipline](../skills/staleness-discipline/SKILL.md), [mall-curation](../skills/mall-curation/SKILL.md) |
| Edition skill bug fix | [feedback-triage](../skills/feedback-triage/SKILL.md) |
| Cross-repo coherence violation | [coherence-audit](../skills/coherence-audit/SKILL.md) |
| Edition release | [release-ritual](../skills/release-ritual/SKILL.md) |

## Hard Rules

1. **Never modify inherited artifacts** — those that came from AlexMaster sync. Modifications must round-trip through AlexMaster's curation, not heir edits.
2. **No pre-emptive changes while an escalation is pending** — wait for AlexMaster's answer; the outcome may differ from your proposal.
3. **One concern per escalation** — bundling defeats the audit trail.
4. **Strip project context** before writing to `AI-Memory/feedback/` per [pii-memory-filter](./pii-memory-filter.instructions.md). Structured schema only.
5. **Every escalation is logged** in `decisions/curation-log.md` with route = `AlexMaster`.
6. **When uncertain, escalate** — see Cardinal Test.

## Multi-Observation Rule

A single heir's complaint is not framework signal — it's domain signal. Framework signal requires:

- ≥3 independent observations across unrelated heirs, **or**
- a single observation that affects the brain spec or ACT pass directly, **or**
- a structural class of concern (artifact-type, inheritance, frontmatter)

Below this bar, handle in-house.

## Routing Table

| Trigger | Route |
|---|---|
| `feedback/inbox/*` arrives | [feedback-triage](../skills/feedback-triage/SKILL.md) → may route to [escalation-routing](../skills/escalation-routing/SKILL.md) |
| Cardinal Test fails on planned change | [escalation-routing](../skills/escalation-routing/SKILL.md) → `/escalate-to-master` |
| Pattern recurs in 3+ heirs | [escalation-routing](../skills/escalation-routing/SKILL.md) → `/escalate-to-master` |
| Heir asks for a brain-spec change | [escalation-routing](../skills/escalation-routing/SKILL.md) → `/escalate-to-master` |

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Treating "I know what AlexMaster would say" as authority | Speculation is not delegation. Ask. |
| Modifying inherited Edition artifacts to fix a heir bug | Fix at AlexMaster, sync down. Heir-side patches drift. |
| Escalating every minor question | Multi-observation rule + matrix decide; not every doubt is framework |
| Skipping the curation log entry | Audit trail breaks at silent decisions |

## Related

- [escalation-routing](../skills/escalation-routing/SKILL.md) — the body of this rule
- [brain-curation-rules](./brain-curation-rules.instructions.md) — sibling rules for Edition curation
- [mall-maintenance-rules](./mall-maintenance-rules.instructions.md) — sibling rules for Mall maintenance
- `/escalate-to-master` prompt
