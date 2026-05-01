---
description: "Run the greeting check-in on demand — Edition version + AI-Memory announcements"
mode: agent
lastReviewed: 2026-04-30
---

# Check-in

Run the full check protocol from [greeting-checkin/SKILL.md](../skills/greeting-checkin/SKILL.md), regardless of whether a greeting fired today.

## Steps

1. **Confirm heir** — read `.github/.act-heir.json`. If absent, refuse and suggest `/initialize` or `/finalize-migration`.
2. **Check Edition version** — `node .github/scripts/upgrade-self.cjs` (dry-run); compare to current `edition_version`.
3. **Scan AI-Memory** — check the announcements folder (resolution order in the skill); list anything newer than `last_sync_at`.
4. **Report** — one short paragraph or a tight bullet list. Don't lecture.
5. **Rewrite the marker** — overwrite `/memories/session/greeting-checkin.md` with today's findings so the greeting trigger stays quiet for the rest of the session.

If the user wants to act on findings, point them at `/upgrade` for version bumps and at the AI-Memory folder for announcements.
