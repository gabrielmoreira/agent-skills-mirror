---
type: skill
lifecycle: stable
name: "meditation"
description: "Consolidate session learning into permanent architecture — extract patterns into skills, instructions, prompts, or memory"
tier: core
applyTo: '**/*meditat*,**/*consolidat*'
inheritance: inheritable
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Meditation

Transform session insights into durable knowledge. Most sessions don't need it; some have a pattern worth keeping.

## When to Fire

- User says "let's meditate", "consolidate", or invokes `/meditate`
- End of a significant work session
- After solving a hard problem with a reusable insight
- Before a long break from a project

**Skip when**: the session was routine execution of patterns already encoded. Meditation on every session produces noise; the discipline is to write only what's new and portable.

## The Five Steps

### 1. Review

Scan the session honestly:

- What problems did we solve?
- What mistakes did we make?
- What patterns emerged that weren't already encoded?
- What would help future sessions?

### 2. Extract

Separate signal from noise. For each candidate pattern, ask: *"Is this already covered by an existing skill, instruction, or memory?"* If yes, skip. If no, route by type:

| If pattern is... | Create / update |
|---|---|
| Reusable domain knowledge | Skill (`.github/skills/<name>/SKILL.md`) |
| Always-on behavior or rule | Instruction (`.github/instructions/<name>.instructions.md`) |
| Repeatable workflow / slash command | Prompt (`.github/prompts/<name>.prompt.md`) |
| Automatable mechanical task | Muscle (`.github/muscles/<name>.cjs`) |
| User preference (cross-project) | User memory (`/memories/<name>.md`) |
| Project / repo convention | Repo memory (`/memories/repo/<name>.md`) |
| Session continuity for next chat | Session memory (`/memories/session/<name>.md`) |

### 3. Write

Each artifact gets correct frontmatter, concrete examples (not abstractions), and tables with real data. Avoid the "capabilities list" anti-pattern — describe behavior, not features.

For skills and instructions: include a **Trigger** or **When to fire** section so future sessions know when the pattern applies.

### 4. Chronicle (optional)

If the session arc was substantial, write to `.github/episodic/meditation-YYYY-MM-DD-<topic>.md`:

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

### 5. Handoff (when ending a session)

If the user is closing the thread, write to `/memories/session/<topic>-handoff.md`:

```markdown
# Session Handoff — <Topic>

## Just shipped
- [SHAs / files / outcomes]

## In progress
- [Specific next step + file paths]

## Pending queue
- [Ordered todos]

## Resume point
- [Where to pick up]
```

## Quality Bar

A meditation is complete when:

- New patterns are persisted, not just acknowledged
- Nothing important lives only in the context window
- Existing artifacts were checked for duplication before writing new ones
- The session can be closed without losing the thread

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Writing a meditation note for every session | Most sessions are routine execution; only write when something new emerged |
| Duplicating an existing skill / memory under a new name | Always grep first: is this already covered? |
| Aspirational notes ("we should do X someday") | Memory is for what was learned, not what was wished |
| Long prose chronicles when a one-line memory suffices | Match artifact size to insight size |
| Skipping the duplication check to "just capture it" | Adds noise that the next session has to filter |

## Related

- [meditation.instructions.md](../../instructions/meditation.instructions.md) — when this skill fires
- [/meditate prompt](../../prompts/meditate.prompt.md) — slash-command entry
- [memory-triggers.instructions.md](../../instructions/memory-triggers.instructions.md) — automatic triggers between meditations
