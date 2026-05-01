---
type: instruction
lifecycle: stable
description: "Triage heir feedback from AI-Memory and ship fixes upstream — communication runs through OneDrive, not this repo"
applyTo: "**"
inheritance: master-only
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# Heir Feedback Triage

Heirs of `Alex_ACT_Edition` submit feedback to `AI-Memory/feedback/alex-act/` on the user's shared OneDrive — **not** to a folder in this repo. Supervisor (when running on the user's behalf) reads, groups, ships, deletes.

The channel is **user-scoped**: only heirs deployed by the same user can write to this Supervisor's inbox, and only this Supervisor reads from it. Other users running their own ACT fleet have their own AI-Memory and their own (optional) supervisor.

## Channel locations

| Direction | Absolute path (Windows) | Format |
|---|---|---|
| Heir → Supervisor | `%USERPROFILE%\OneDrive - Correa Family\AI-Memory\feedback\alex-act\` | One markdown file per submission |
| Supervisor → Heirs | `%USERPROFILE%\OneDrive - Correa Family\AI-Memory\announcements\alex-act\` | One markdown file per announcement |

Cross-platform path resolution: heirs and Supervisor both check candidate roots in priority order (`OneDrive - Correa Family`, `OneDrive`, `iCloudDrive`, `iCloud Drive`, `iCloud~com~apple~CloudDocs`, `Dropbox`). First existing path wins.

The file schema is documented in the AI-Memory folder READMEs. Do not duplicate the schema here.

## Triage workflow

1. **Read all entries** in `AI-Memory/feedback/alex-act/` (skip the README)
2. **Validate frontmatter** — drop or flag malformed entries
3. **Verify stripping rules** per `cross-project-isolation.instructions.md` — refuse entries with file paths, client names, PII, or domain data; respond by writing an announcement asking the heir to resubmit cleanly
4. **Group by paradigm/lane** — bugs, friction, features, success notes
5. **Decide**:
   - Ship fix → bump `Alex_ACT_Edition` and write release announcement
   - Defer → log in `decisions/curation-log.md` with rationale
   - Reject → respond via `announcements/alex-act/` with reasoning
6. **Delete processed files** from `feedback/alex-act/` once shipped or rejected. The folder is an inbox, not an archive.

## Anti-patterns

| Anti-pattern | Why it breaks |
|---|---|
| Adding a `feedback/` folder back to this repo | Forces heirs to PR — high friction, requires repo access. AI-Memory is async, no auth required. |
| Reading feedback without applying stripping rules | Sycophancy risk — implementing a fix based on data that shouldn't have been shared. |
| Leaving processed files in `feedback/alex-act/` | Inbox bloat. The folder size is the work-pending signal. |
| Writing to a heir repo to "respond" | Violates pull-only architecture. Use `announcements/alex-act/` instead. |

## Severity routing

| Severity | Response time | Action |
|---|---|---|
| `critical` | Same day | Hotfix patch release of Edition |
| `high` | Within current minor cycle | Include in next minor |
| `medium` | Next minor or two | Group with related items |
| `low` | Bundle with major | Backlog in `decisions/curation-log.md` |

## Falsifiability

This channel design is wrong if, after 90 days, fewer than 50% of submitted feedback entries have a triage decision logged. That would mean the Supervisor is not running the triage loop and AI-Memory is silently growing. Mitigation: schedule weekly `/triage-feedback` via session memory or calendar reminder.
