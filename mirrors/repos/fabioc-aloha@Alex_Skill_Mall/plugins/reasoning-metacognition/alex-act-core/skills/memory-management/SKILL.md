---
name: memory-management
description: "Memory-tier selection and writing mechanics — where content goes based on type (user preference → user memory, project convention → repo memory, cross-session state → repo-root HANDOFF.md not session memory, failure analysis → episodic, reusable domain knowledge → skill). Use when writing to persistent storage, deciding between memory tiers, preparing a cross-session handoff, choosing where a lesson learned should live, or looking up why HANDOFF.md is the right target rather than /memories/session/."
lastReviewed: 2026-08-01
---

# Memory Management

Companion to `memory-triggers.instructions.md`. The always-on trigger-detection rules live in that file; this skill carries the tier-selection detail and cross-session-continuity mechanics that the triggers hand off to.

## Memory Tier Selection

Once a trigger has fired and the decision to persist has been made, this table decides where the content lands:

| Content Type | Tier | Location |
|--------------|------|----------|
| User preference | User | `/memories/` |
| Communication style | User | `/memories/` |
| Project convention | Repo | `/memories/repo/` |
| Build/test commands | Repo | `/memories/repo/` |
| **Cross-session handoff (next session needs to know)** | **Repo file** | **`HANDOFF.md` at repo root** — NOT `/memories/session/` (that tier is cleared at conversation end) |
| In-conversation scratch (current session only) | Session | `/memories/session/` |
| Failure analysis | Episodic | `.github/episodic/postmortem-*.md` |
| Session chronicle | Episodic | `.github/episodic/meditation-*.md` |
| Reusable domain knowledge | Skill | `.github/skills/*/SKILL.md` |
| Shared project-agnostic collaboration artifact | Shared Memory bus | `Alex_ACT_Memory/{announcements,feedback,knowledge,insights}/` through [`ai-memory-setup`](../ai-memory-setup/SKILL.md) |

## Cross-Session Continuity — repo files, not session memory

The natural phrase "session handoff" reads like exactly what `/memories/session/` is for. It is not.

| Want | Use | Why |
|------|-----|-----|
| Notes I need *during* this conversation | `/memories/session/<topic>.md` | Scoped, ephemeral, cleared at end — by design |
| Notes the *next* session needs to pick up where this one left off | **Repo file** (`HANDOFF.md` at repo root) | Survives `/clear`, ships with the repo, discoverable from README, real audit trail |
| Cross-session lessons that are project-agnostic | `/memories/<topic>.md` | Auto-loaded on every session |

**Rule**: when the user asks for a "session handoff," "wrap up cleanly," or "prepare for next session," reach for the repo file first. Use session memory only for in-conversation scratch.

Keep `HANDOFF.md` current with the last session's state, replace or delete if too much has changed, never let it lie — stale handoffs are worse than no handoffs.

## Shared Memory Bus

Use `Alex_ACT_Memory` only when content must be project-agnostic and shared
across repositories, machines, or authorized users. Route the operation through
[`ai-memory-setup`](../ai-memory-setup/SKILL.md), which owns filesystem
discovery, channel rules, atomic writes, the `npm run check` gate, and separate
Git consent. Do not use the shared bus for ordinary project handoffs, personal
workflow preferences, or in-conversation scratch.

## Handoff template

When writing a fresh `HANDOFF.md` at session end:

```markdown
# Session Handoff

Last updated: YYYY-MM-DD HH:MM

## Just shipped
- [SHAs / files / outcomes]

## In progress
- [Specific next step + file paths]

## Pending queue
- [ ] [Ordered todos]

## Resume point
- [Where to pick up]
```

## Chronicle template

When a session arc is substantial enough to warrant a chronicle, write to `.github/episodic/meditation-YYYY-MM-DD-<topic>.md`:

```markdown
# Meditation: <Topic>

**Date**: YYYY-MM-DD
**Focus**: What we worked on

## Accomplished
- [Key outcomes]

## Patterns Extracted
- [What became skills / instructions / memory]

## Lessons
- [Insights worth remembering]

## Open Questions
- [What remains unresolved]
```

Skip the chronicle for short sessions or when nothing new emerged.

## Post-mortem template

For failure analysis, write to `.github/episodic/postmortem-YYYY-MM-DD-<topic>.md`:

```markdown
# Post-mortem: <Topic>

**Date**: YYYY-MM-DD
**Trigger**: What went wrong

## Timeline
- [Chronological events]

## Root cause
- [Not the symptom — the actual cause]

## What we did about it
- [Fixes shipped]

## What we learned
- [Pattern that should not recur]

## Related
- [Links to affected commits / files]
```

## Integration with Other Protocols

- **[Meditation](../meditation/SKILL.md)** — triggers skill extraction and chronicle writing
- **[Anti-hallucination](../anti-hallucination/SKILL.md)** — triggers verification-scope logging
- **Post-mortem** — triggers failure analysis
- **`Handoff routing`** — the always-on rule that fires this skill

## Related

- `memory-triggers.instructions.md` — the always-on trigger-detection rules that hand off to this skill
- `pii-memory-filter.instructions.md` — the write-boundary filter that applies to every tier above
- [meditation skill](../meditation/SKILL.md) — the discipline that populates episodic memory

## Would Revise If

Revise if the tier-selection table produces ambiguous routing decisions (a single content type could plausibly go in two tiers) ≥3 times in a quarter, if the `HANDOFF.md` template is bypassed for structured session-handoff writes ≥2 times, or if a new memory tier surfaces (e.g., a platform-provided shared-cross-repo tier) that the table cannot express.
