---
description: "Short alias for /save-session-note — append a quick observation to AI-Memory/notes.md"
mode: agent
lastReviewed: 2026-04-30
---

# Note

Alias for `/save-session-note`. Follow the same protocol — capture a short note to user-scope `AI-Memory/notes.md` so it survives across sessions and projects.

See `.github/prompts/save-session-note.prompt.md` for the full steps.

## Quick Form

If the user's request already includes the note text, skip the "what should I capture?" question and write it directly. Resolve AI-Memory root, append timestamped line, strip per `cross-project-isolation.instructions.md`, confirm.
