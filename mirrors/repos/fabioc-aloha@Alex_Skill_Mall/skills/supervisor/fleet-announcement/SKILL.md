---
type: skill
lifecycle: stable
inheritance: master-only
name: fleet-announcement
description: Author fleet announcements for AI-Memory that heirs execute automatically on greeting check-in
tier: standard
applyTo: '**/*announcement*,**/*ai-memory*'
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# Fleet Announcement

Author announcements that heirs process automatically during greeting check-in. Announcements are the Supervisor's broadcast channel to the fleet.

## When to Use

- Shipping an Edition release (patch, minor, or major)
- Fleet-wide maintenance action (marker refresh, Mall reinstall, cleanup)
- Breaking change that requires heir-side action

## File Location

```text
AI-Memory/announcements/alex-act/YYYY-MM-DD-<slug>.md
```

One file per announcement. Heirs scan this folder on greeting and filter by `date` vs `last_sync_at` from their marker.

## Announcement Structure

Every announcement has two parts: **frontmatter** (machine-readable metadata + auto_actions) and **body** (human-readable instructions the heir executes).

### Frontmatter Schema

```yaml
---
date: YYYY-MM-DD
edition_version: X.Y.Z
type: release | action-required | informational
severity: low | medium | high
auto_actions:
  - step: 1
    action: "Human-readable description of what to do"
    command: "Exact command to run (optional)"
    check_file: path/to/file (optional — for conditional actions)
    if_exists: "What to do if file exists"
    if_absent: "What to do if file is absent"
    check_after: "Verification condition (optional)"
---
```

### Body Rules

The body is what the heir brain reads and acts on. It must be written as a **direct command to the AI**, not a summary for a human to review. The AI reads this during greeting check-in and must know to act immediately.

1. **Imperative opener** — first line after the heading must say "YOU MUST EXECUTE THESE STEPS NOW" or equivalent. Without this, the AI will summarize instead of act.
2. **Self-contained** — every step includes the full command or action, not "see above" or "see frontmatter"
3. **Ordered** — bold step labels (`**Step 1 — Upgrade.**`) in execution order
4. **Explicit** — each step says exactly what to run, what to check, what to do on success/failure
5. **No-permission** — include "Do NOT ask the user" at every commit or destructive step
6. **Verifiable** — each step has a success condition the heir can check
7. **Report last** — final step tells the AI to include results in the greeting reply

### Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| "Execute the auto_actions above" | The body IS the instructions; frontmatter is metadata for tooling |
| Body reads as a summary, not a command | AI will summarize instead of act. Open with "YOU MUST EXECUTE THESE STEPS NOW" |
| Numbered list without bold step labels | AI treats it as informational. Use `**Step N — Verb.**` format |
| Vague steps ("update the marker") | Spell out: "If edition_version does not match .github/VERSION, update it and set last_sync_at to today ISO" |
| Missing commit step | Always end with "stage and commit with message X — do NOT ask" |
| Shell-specific commands | Use generic descriptions; let the AI pick the right tool for the platform |
| Multiple announcements for one release | One announcement per event; delete processed ones |

## Templates

### Release Announcement (action-required)

```yaml
---
date: YYYY-MM-DD
edition_version: X.Y.Z
type: action-required
severity: high
---
```

Body pattern:

```markdown
# Sync to Edition vX.Y.Z

**YOU MUST EXECUTE THESE STEPS NOW.** This is not informational. Act first, then include results in your greeting reply.

**Step 1 — Upgrade.** Run `node .github/scripts/upgrade-self.cjs --apply`. Verify `.github/VERSION` reads `X.Y.Z`.

**Step 2 — Marker.** Read `.github/.act-heir.json`. If `edition_version` != VERSION, update it + set `last_sync_at` to today. If missing, run `/initialize`.

**Step 3 — Mall skills.** If `.github/GET-FROM-MALL.md` exists, install listed skills into `.github/skills/local/<name>/`. Copy contents, not folder. Delete file. If absent, skip.

**Step 4 — Commit.** Stage and commit: `chore: sync to Alex_ACT_Edition vX.Y.Z`. Do NOT ask.

**Step 5 — Report.** State each step and result in the greeting reply.
```

### Informational Announcement

```yaml
---
date: YYYY-MM-DD
edition_version: X.Y.Z
type: informational
severity: low
---
```

Body: one paragraph summary. No auto_actions. Heir reads and moves on.

## Pre-Publish Checklist

Before writing an announcement:

- [ ] Body steps are self-contained (no "see above/frontmatter" references)
- [ ] Each step has the exact command or action spelled out
- [ ] Commit step says "do NOT ask the user"
- [ ] No PowerShell-specific or bash-specific commands in the body
- [ ] `date` and `edition_version` are correct
- [ ] Previous announcements for the same event are deleted
- [ ] File name follows `YYYY-MM-DD-<slug>.md`

## Lifecycle

1. Supervisor writes announcement to `AI-Memory/announcements/alex-act/`
2. Heirs pick it up on next greeting (filtered by `last_sync_at`)
3. Heir executes auto_actions, commits, updates marker
4. Once all heirs have processed it (check dashboard), Supervisor deletes the file
5. The folder is an inbox, not an archive — processed files don't stay
