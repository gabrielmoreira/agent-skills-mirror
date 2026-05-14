---
description: "Save session state for handoff in repo-root SESSION-HANDOFF.md (and mirror to AI-Memory)"
mode: agent
lastReviewed: 2026-05-13
---

# Save Session Note

Capture a short observation, reminder, or open thread in repo-root `SESSION-HANDOFF.md` so pending actions stay visible to the user across sessions.

## Steps

1. **Get the note from the user** — one or two sentences. If they didn't include one in the request, ask: "What should I capture?"
2. **Resolve repo root**:
   - If in a git repo, use the top-level root.
   - If not in a git repo, use the current workspace root.
3. **Upsert `SESSION-HANDOFF.md`** at repo root. If missing, create this structure:

   ```markdown
   # Session Handoff

   Last updated: YYYY-MM-DD HH:MM

   ## Pending Actions
   - [ ] <user note>

   ## Resume Hint
   - Open this file first in the next session.
   ```

   If it exists, update `Last updated` and append the new item under `## Pending Actions` as `- [ ] <user note>`.
4. **Mirror to AI-Memory (optional but recommended)**: resolve AI-Memory root using the standard algorithm (check `cognitive-config.json` for `ai_memory_root`, then auto-discover cloud drives, skip `ai_memory_exclude`, pick the first with `AI-Memory/`). Append to `notes.md` at that root, creating the file if needed. Format:

   ```markdown
   ## YYYY-MM-DD HH:MM (heir: <heir_id>)
   <user's note>
   ```

   Use today's local date and time. Read `heir_id` from `.github/.act-heir.json` if available; otherwise omit the parenthetical.

5. **Strip per `cross-project-isolation.instructions.md` for AI-Memory mirror only** — no file paths, client names, PII. If the mirrored note contains those, ask the user to rephrase before writing to AI-Memory. (Project-local `SESSION-HANDOFF.md` can include project context.)
6. **Confirm** by quoting the line added to `SESSION-HANDOFF.md` and its file path.

## Notes

- Canonical handoff artifact is repo-root `SESSION-HANDOFF.md`.
- AI-Memory mirror is for cross-project continuity and searchability.
- Keep notes terse and action-oriented.
