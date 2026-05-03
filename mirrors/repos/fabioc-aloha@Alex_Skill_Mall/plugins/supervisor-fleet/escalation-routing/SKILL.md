---
type: skill
lifecycle: stable
inheritance: master-only
name: escalation-routing
description: Decide whether a feedback item is in-scope for the Supervisor or must be escalated to AlexMaster (framework-level)
tier: standard
applyTo: '"**/feedback/inbox/**,**/feedback/triaged/**"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Escalation Routing

The Supervisor owns ACT-fleet curation. AlexMaster owns the framework. This skill draws the line.

## When to Use

- Triaging an inbox item via [feedback-triage](../feedback-triage/SKILL.md) and the route is unclear
- A pattern recurs across heirs and feels like it belongs in the framework, not the curation
- A heir requests something the Supervisor cannot grant alone

## The Cardinal Test

Before any change, ask: **Does AlexMaster do this?**

| If AlexMaster… | Then the change is… |
|---|---|
| Owns the artifact type (instruction, skill, prompt schema, ACT tenet) | Framework — escalate |
| Owns the policy (how releases work, what counts as a skill, the ACT pass) | Framework — escalate |
| Owns the brain spec (copilot-instructions.md, three-tier inheritance) | Framework — escalate |
| Just has a sibling artifact (a different skill, a different store) | Curation — handle in-house |
| Is downstream consumer (would adopt the change later) | Curation — handle in-house |

## In-Scope vs Escalation Matrix

| Signal | Route |
|---|---|
| Proposal for a new ACT tenet | **Escalate** |
| Proposal for a new artifact type (e.g., "we need a `pattern.md` alongside skills") | **Escalate** |
| Proposal that changes the brain spec (frontmatter fields, inheritance tiers) | **Escalate** |
| Proposal that changes how the ACT pass works | **Escalate** |
| Cross-fleet pattern observed in 3+ unrelated heirs | **Escalate** (it's framework signal) |
| Domain skill (a new specialized capability) | **In-house** |
| New mall store | **In-house** ([store-evaluation](../store-evaluation/SKILL.md)) |
| Edition skill bug fix | **In-house** ([feedback-triage](../feedback-triage/SKILL.md) → Edition PR) |
| Mall entry refresh | **In-house** ([mall-curation](../mall-curation/SKILL.md)) |
| Coherence violation | **In-house** ([coherence-audit](../coherence-audit/SKILL.md)) |
| Heir request for a curated pattern bundle | **In-house** |
| Disagreement about whether to handle in-house | **Escalate** (when in doubt, escalate — the cost of asking is low; the cost of overreach is high) |

## Escalation Procedure

1. Confirm the item meets at least one **Escalate** signal — and document which one
2. Run a full ACT pass (high stakes — this is a framework-level claim about scope)
3. Write the escalation as a feedback file at `AI-Memory/feedback/<YYYY-MM-DD>-<short-slug>.md` in the AlexMaster workspace (per [pii-memory-filter](../../instructions/pii-memory-filter.instructions.md): structured schema only, no domain data)
4. Required fields:
   - **From**: Alex_ACT_Supervisor
   - **Date**: YYYY-MM-DD
   - **Category**: tenet-proposal / spec-change / artifact-type / cross-fleet-pattern / scope-question
   - **Severity**: low / medium / high / critical
   - **Signal count**: how many independent observations support this (the multi-observation rule)
   - **Description**: structured, abstract — what / why / proposed action
5. Record the escalation in `decisions/curation-log.md` with route `AlexMaster` and M/S = S
6. Wait for AlexMaster to act — **do not modify Edition or Mall in anticipation** of the escalation outcome. Pre-emptive changes are scope creep.

## Hard Rules

1. **When in doubt, escalate** — overreach is more expensive than asking
2. **Never modify framework artifacts in Edition or Mall** — they are inherited from AlexMaster; modifying them creates fleet drift
3. **One escalation per concern** — bundling unrelated items defeats the audit trail
4. **Strip project context per [cross-project-isolation](../../instructions/pii-memory-filter.instructions.md)** before writing to AlexMaster's `AI-Memory/feedback/`
5. **No silent escalations** — every escalation is logged in `curation-log.md`

## What "In-House" Means

If the item is in-house, it routes to one of the existing skills:

| Item type | In-house skill |
|---|---|
| Skill submission or fix | [skill-review](../skill-review/SKILL.md) |
| Generic feedback or bug | [feedback-triage](../feedback-triage/SKILL.md) |
| New mall store | [store-evaluation](../store-evaluation/SKILL.md) |
| Mall prune/refresh | [staleness-discipline](../staleness-discipline/SKILL.md) or [mall-curation](../mall-curation/SKILL.md) |
| Coherence violation | [coherence-audit](../coherence-audit/SKILL.md) |
| Release coordination | [release-ritual](../release-ritual/SKILL.md) |

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Modifying inherited artifacts "just this once" | Modifications must come through AlexMaster sync, never in heirs |
| Escalating every trivial question | Use the matrix; trivial items waste AlexMaster's bandwidth |
| Pre-emptive change while waiting for escalation outcome | Wait for the answer; the change you preempt may not be what AlexMaster decides |
| Bundling unrelated escalations | One concern, one escalation file |
| Forgetting to log the escalation | Curation log is the audit trail; missing entries break the 60-day re-evaluation |

## Output Template (escalation file)

```markdown
# Escalation — <short title>

**From**: Alex_ACT_Supervisor
**Date**: YYYY-MM-DD
**Category**: tenet-proposal | spec-change | artifact-type | cross-fleet-pattern | scope-question
**Severity**: low | medium | high | critical
**Signal count**: N independent observations

## What

<2-3 sentence abstract>

## Why this is framework-level (not curation)

<cite which Escalate signal fired>

## Evidence

- <observation 1, abstracted per cross-project-isolation>
- <observation 2>
- ...

## Proposed Action (for AlexMaster)

<2-3 sentence proposal>

## Impact if Not Adopted

<what continues to drift, what cost accrues>

## ACT Pass Trail

<markers>
```

## Related

- [feedback-triage](../feedback-triage/SKILL.md) — primary entry point that may route here
- [escalation-rules](../../instructions/escalation-rules.instructions.md) — always-on routing
- [pii-memory-filter](../../instructions/pii-memory-filter.instructions.md) and [cross-project-isolation guidance](../../instructions/pii-memory-filter.instructions.md) — content rules
- `/escalate-to-master` prompt
