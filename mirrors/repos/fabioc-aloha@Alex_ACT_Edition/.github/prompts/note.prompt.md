---
description: "Short alias for /save-session-note — write a quick pending-action note to repo-root HANDOFF.md"
mode: agent
lastReviewed: 2026-05-13
---

# Note

Alias for `/save-session-note`. Follow the same protocol — capture a short note to repo-root `HANDOFF.md` so pending actions remain visible on the project root.

See `.github/prompts/save-session-note.prompt.md` for the full steps.

## Quick Form

If the user's request already includes the note text, skip the "what should I capture?" question and write it directly. Resolve repo root, append checkbox item to `HANDOFF.md`, optionally mirror to AI-Memory with stripping, confirm.
