---
mode: agent
description: "Supervisor: Consolidate session learning — extract new patterns into skills, instructions, prompts, or memory"
lastReviewed: 2026-04-30
---

# /meditate

Run the meditation protocol on the current session.

## Steps

1. **Review** — problems solved, mistakes made, patterns that emerged
2. **Check for duplication** — grep existing user memory, repo memory, session memory, skills, and instructions before writing anything new
3. **Extract** only what's new and portable across future sessions
4. **Route** each surviving pattern:

   | If pattern is... | Write to |
   |---|---|
   | Cross-project preference or hazard | `/memories/<name>.md` (user memory) |
   | Supervisor curation rule or pattern | `.github/instructions/<name>.instructions.md` |
   | Reusable curation procedure | `.github/skills/<name>/SKILL.md` |
   | Repeatable workflow / slash command | `.github/prompts/<name>.prompt.md` |
   | Session continuity (closing thread) | `/memories/session/<topic>-handoff.md` |
   | Decision worth auditing | `decisions/curation-log.md` row |

5. **Write** with correct frontmatter and a trigger origin (date + concrete cause)
6. Report what was persisted, and explicitly name what was *not* persisted because it was already covered
7. **Compact** — run `/compact` to discard transcript noise. The persisted artifacts are now the canonical record of this session. This is irreversible by design; consolidation succeeded, raw data is redundant.

## Anti-pattern guard

If after step 1 nothing new emerged, say so, then still run `/compact` at step 7. Most sessions are routine execution of patterns already encoded — that's the system working, not a gap to fill, and the transcript still earns the same cleanup.
