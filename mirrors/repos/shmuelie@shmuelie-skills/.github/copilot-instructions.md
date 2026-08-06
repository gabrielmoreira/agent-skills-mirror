# Copilot Instructions for shmuelie-skills

## Project Overview

This is a Copilot CLI multi-plugin marketplace. Skills live only under
`.github/plugin/<plugin>/skills/<skill>/SKILL.md`. The root plugin aggregates all
focused plugin skill directories for `copilot plugin install shmuelie/shmuelie-skills`.

## Scanning for New Learnings

When asked to scan for new learnings or update skills, follow this process:

### Step 1: Query Copilot CLI session stores

Use the `sql` tool with `database: "session_store"` to search for sessions since the last sweep:
- `search_index` for technical patterns, conventions, and bug fixes
- `checkpoints` for detailed technical knowledge
- `sessions` and `turns` for conversation content

Also check WSL session stores — copy `$HOME/.copilot/session-store.db` from each WSL distro to a temp file via `wsl`, then query with Python/sqlite3.

### Step 2: Scan VS Code chat sessions (JSONL and JSON)

Check `%APPDATA%/Code/User/workspaceStorage/*/chatSessions/` for `.jsonl` and `.json` files larger than 200 bytes.

**JSONL format** (incremental updates):
- **Line kind=0**: Initial session state (contains `v.requests`, `v.customTitle`)
- **Line kind=1**: Incremental updates keyed by JSON array paths (`k` field):
  - `["customTitle"]` → session title (string `v`)
  - `["inputState", "inputText"]` → user message (string `v`)
- **Line kind=2**: Array splice/insert — response parts pushed to `["requests", N, "response"]`:
  - Items with `"kind": "thinking"` contain reasoning text
  - Items with `"kind": "textEditGroup"` are file edits
  - Items without a `kind` but with a string `value` are markdown response text

**JSON format** (older sessions): Parse as a single `json.load()`. Often have empty requests.

### Step 3: Scan VS Code state.vscdb for CLI sessions run through VS Code

Check `%APPDATA%/Code/User/workspaceStorage/*/state.vscdb` — SQLite database with `ItemTable`.

Query `chat.ChatSessionStore.index` for `{"entries": {sessionId: {title, ...}}}`.
This reveals Copilot CLI sessions that ran inside VS Code's integrated terminal.

When `copilotcli.session.metadata.json` (in `%APPDATA%/Code/User/globalStorage/github.copilot-chat/copilotCli/`)
shows `"writtenToDisc": true` and a `workspaceFolder` path, the session content is on the **remote machine**.

### Step 4: Check remote SSH hosts for session data

For each SSH host in `~/.ssh/config`, check for session data:

```bash
ssh <host> 'for d in ~/.copilot/session-state/*/; do
  if [ -f "$d/workspace.yaml" ]; then
    cat "$d/workspace.yaml"
    if [ -f "$d/plan.md" ]; then echo "--- PLAN ---"; cat "$d/plan.md"; fi
    echo "================================================================"
  fi
done'
```

Key files per session:
- `workspace.yaml` — session metadata (cwd, repo, branch, summary)
- `plan.md` — implementation plan (often contains the richest technical learnings)
- `events.jsonl` — full conversation event stream

Check any SSH hosts configured in `~/.ssh/config` that you use for remote
Copilot or development sessions.

### Step 5: Compare against existing skills

Review `.github/plugin/*/skills/` to identify:
- New patterns not yet covered by any skill
- Updates or corrections to existing skill content
- Entirely new topic areas that warrant a new skill

### Step 6: Update or create SKILL.md files

Choose the focused plugin that owns the topic. Create a new focused plugin when
no existing plugin is a coherent fit; do not put skills in a root `skills/`
directory.

Each SKILL.md has:
```markdown
---
name: skill-name
description: Brief description
---

Context instructions.

# Domain Knowledge
...
```

### Step 7: Do not bump versions for content changes

Plugin versions (`plugin.json` and their `marketplace.json` entries) and the
catalog `metadata.version` change **only when a release is cut**, not for skill
edits. Between releases, leave every version unchanged and record the change
under `[Unreleased]` (Step 8). Cutting a release is a separate, deliberate step:
bump the released plugins' versions, move the `[Unreleased]` notes into a dated
section, update the comparison links, and tag it.

### Step 8: Update changelogs

Following Keep a Changelog format:
- Add an entry to the changed **skill's own** `CHANGELOG.md`
  (`.github/plugin/<plugin>/skills/<name>/CHANGELOG.md`).
- Add a catalog-level entry to the **repository** `CHANGELOG.md` under
  `[Unreleased]` (not a new version section — that happens only at release time).

### Step 9: Update README.md if needed

Update if:
- A new skill or plugin was added (update the Skills table, focused plugin table,
  owning plugin README, and Project Structure)
- Source repos changed

### Step 10: Commit and push

With a descriptive message.

## Conventions

- Skills are markdown files at `.github/plugin/<plugin>/skills/<name>/SKILL.md`
- Every skill directory also has its own `CHANGELOG.md`
- Every skill has exactly one focused owning plugin
- The root aggregate plugin references focused skill directories; it owns no skills directly
- Each plugin manifest version must match its marketplace entry; focused plugin versions are independent
- Versions change only when a release is cut, never for a content change; between releases, changes go under `[Unreleased]`
- Follow Semantic Versioning for release version bumps
- Follow Keep a Changelog for every CHANGELOG.md (per-skill and repository)
- Skill descriptions should be specific and actionable, not vague
- Include code examples, gotchas, and bug patterns — not just general advice
