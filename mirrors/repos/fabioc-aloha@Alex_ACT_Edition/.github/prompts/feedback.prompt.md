---
description: "File feedback to the user (and their Supervisor, if any) via AI-Memory — guided through stripping rules and file naming"
mode: agent
lastReviewed: 2026-04-30
---

# Feedback

Capture friction, bugs, feature ideas, or success notes from this session and write them to `AI-Memory/feedback/alex-act/` so they propagate to the user (and their Supervisor, if they run one).

## Steps

1. **Ask the user what to surface** — bug, friction, feature request, or success. Capture the gist in their own words.
2. **Classify**:
   - `category`: `bug` | `friction` | `feature-request` | `success`
   - `severity`: `low` | `medium` | `high` | `critical`
   - `skill`: name of the skill if specific to one, otherwise empty
3. **Resolve the AI-Memory root** using the standard algorithm: check `cognitive-config.json` for `ai_memory_root` override, then auto-discover cloud drives (OneDrive, iCloud, Dropbox, Google Drive, Box, etc.), skip `ai_memory_exclude` entries, pick the first with `AI-Memory/`. Run `node .github/scripts/_registry.cjs --resolve .` if unsure. If none found, offer to create one: `node .github/scripts/_registry.cjs --discover` then `--init <name>`.
4. **Strip per `cross-project-isolation.instructions.md`** before writing:
   - No file paths from the heir project
   - No client names, domain entities, or business specifics
   - No code snippets longer than 5 lines
   - No configuration values, connection strings, endpoints
   - No PII (contact info, names + identifiers, health/financial data)
5. **Write the file** at `<ai-memory-root>/feedback/alex-act/YYYY-MM-DD-<heir-id>-<short-slug>.md` with frontmatter:

   ```yaml
   ---
   heir_id: <from .github/.act-heir.json>
   edition_version: <from marker>
   date: <today ISO date>
   category: <classification>
   severity: <classification>
   skill: <skill-name-or-empty>
   ---
   ```

   Body sections (only these two):

   ```markdown
   ## What happened
   <abstract description, no project specifics>

   ## Expected behavior
   <what should have happened>
   ```

6. **Confirm** the file path back to the user. Note that if they have no Supervisor, this serves as a personal log they can review later.

## Refuse if

- The feedback requires project-specific context to make sense after stripping (ask the user to abstract the pattern)
- The marker (`.github/.act-heir.json`) is missing — bootstrap is incomplete
