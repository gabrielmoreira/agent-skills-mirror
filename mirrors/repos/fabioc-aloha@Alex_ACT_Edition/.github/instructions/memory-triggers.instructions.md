---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Automatic memory formation triggers — when to persist without being asked"
application: "Always active — unconscious monitoring for memory-worthy events"
applyTo: "**"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Memory Triggers

Automatic prompts to form memories. Don't wait to be asked — recognize trigger conditions and persist.

## Trigger Conditions

| Trigger | Memory Type | Action |
|---------|-------------|--------|
| **User corrects me** | User or Repo | Write what I got wrong + correct approach |
| **Same pattern 3×** | Skill candidate | Propose: "This seems worth capturing as a skill" |
| **Error → fix cycle** | Post-mortem | Write failure analysis to episodic |
| **User states preference** | User memory | Capture preference immediately |
| **Session > 30 min** | Handoff | Prompt: "Should we write a session handoff?" |
| **Significant decision** | Chronicle | Record in episodic with rationale |
| **New project convention** | Repo memory | Write to `/memories/repo/` |

## Trigger Detection

### User Correction

Phrases that indicate correction:

- "No, I meant..."
- "That's not right"
- "Actually..."
- "Not what I asked for"
- "Try again"

**Response**: Acknowledge, understand the gap, write to memory if pattern.

### Pattern Recognition

Track mentally:

- Have I done this before this session?
- Did I do this in a previous session (check episodic)?
- Is this generalizable beyond this specific case?

**At 3× threshold**: "I've applied this pattern multiple times. Worth capturing as a skill?"

### Preference Detection

User statements that encode preferences:

- "I prefer..."
- "Always do X"
- "Don't do Y"
- "I like when you..."
- Consistent behavior corrections

**Response**: Acknowledge and persist immediately to user memory.

### Time Awareness

After extended work (estimate by conversation depth, not literal time):

- Many tool calls
- Multiple files touched
- Complex reasoning chains

**Prompt**: "We've covered a lot. Want me to write a session handoff before we wrap up?"

## Memory Tier Selection

| Content Type | Tier | Location |
|--------------|------|----------|
| User preference | User | `/memories/` |
| Communication style | User | `/memories/` |
| Project convention | Repo | `/memories/repo/` |
| Build/test commands | Repo | `/memories/repo/` |
| Session context | Session | `/memories/session/` |
| Failure analysis | Episodic | `.github/episodic/postmortem-*.md` |
| Session chronicle | Episodic | `.github/episodic/meditation-*.md` |
| Reusable domain knowledge | Skill | `.github/skills/*/SKILL.md` |

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Write every observation | Filter for patterns and preferences |
| Duplicate across tiers | Choose most appropriate tier |
| Write without structure | Use templates (handoff, post-mortem, skill) |
| Forget to update index | Add to INDEX.md when writing |
| Overwrite without reason | Append or version if content evolving |

## Integration with Other Protocols

- **Meditation**: Triggers skill extraction and chronicle writing
- **Calibration**: Triggers prediction logging
- **Post-mortem**: Triggers failure analysis
- **Handoff**: Triggers session continuity

This instruction makes memory formation **proactive, not reactive**.
