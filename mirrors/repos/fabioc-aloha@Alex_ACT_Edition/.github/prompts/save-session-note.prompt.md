---
description: "Append a quick session note to AI-Memory/notes.md for cross-session continuity"
mode: agent
lastReviewed: 2026-04-30
---

# Save Session Note

Capture a short observation, reminder, or open thread to `AI-Memory/notes.md` (user scope) so it survives across sessions and projects.

## Steps

1. **Get the note from the user** — one or two sentences. If they didn't include one in the request, ask: "What should I capture?"
2. **Resolve the AI-Memory root** using the standard algorithm: check `cognitive-config.json` for `ai_memory_root`, then auto-discover cloud drives, skip `ai_memory_exclude`, pick the first with `AI-Memory/`. CLI: `node .github/scripts/_registry.cjs --resolve .`
3. **Append to `notes.md`** at that root, creating the file if needed. Format:

   ```markdown
   ## YYYY-MM-DD HH:MM (heir: <heir_id>)
   <user's note>
   ```

   Use today's local date and time. Read `heir_id` from `.github/.act-heir.json` if available; otherwise omit the parenthetical.

4. **Strip per `cross-project-isolation.instructions.md`** — no file paths, client names, PII. If the note as written contains those, ask the user to rephrase before writing.
5. **Confirm** by quoting back the line that was appended.

## Notes

- This is a **user-scope** note, not a heir/project note. It lives in shared `AI-Memory/` and is visible across all of the user's heirs and AI surfaces.
- Keep notes terse — `notes.md` is meant to be skimmable.
- For project-specific notes, use the heir's local instructions or session memory instead.
