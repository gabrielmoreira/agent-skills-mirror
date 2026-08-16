---
name: manage-skills
description: Manage the user's shared agent-skill library via skills-manager-cli — install, update, remove, deploy or undeploy skills per agent, manage presets, organize tags, search, and adopt existing skills. Use this whenever the user wants Claude Code, Codex, Cursor, or another agent to gain or lose a skill, wants to organize the central library, or asks what is installed or deployed. Prefer this over direct agent-folder installs because Skills Manager preserves source metadata, preset membership, updates, and cross-agent deployment state.
---

## Before doing anything

1. Confirm the CLI is available: `command -v skills-manager-cli`. If it's not on PATH, this skill doesn't apply — fall back to find-skills (or tell the user to install skills-manager).
2. **Always pass `--json` when you parse output yourself.** Pretty-printed output is for the user; JSON is for you. Errors include `ok=false`, a stable `code`, and `message` on stderr with a non-zero exit code.

```bash
skills-manager-cli --json skills list
```

## Mental model

There's **one central library** at `~/.skills-manager/skills/` that all agents share. Each skill has source metadata, preset membership, tags, and zero or more real deployments in agent directories. A **preset** is a reusable group; several presets may be deployed at the same time.

Keep these three states separate:
- **Library**: install/remove controls whether Skills Manager owns the skill.
- **Preset membership**: `presets add-skill/remove-skill` organizes the library only.
- **Deployment**: `skills deploy/undeploy` and `presets deploy/undeploy` control what an agent can actually see.

Internally, presets are still stored as scenarios for backward-compatible Git Backup. The CLI and UI call them presets.

## Install

```bash
# From skills.sh marketplace
skills-manager-cli skills install vercel-labs/agent-skills@react-best-practices

# Any git URL (use /tree/branch/subpath form when the skill lives in a sub-directory)
skills-manager-cli skills install https://github.com/anthropics/skills.git
skills-manager-cli skills install https://github.com/foo/bar/tree/main/skills/baz

# Local folder
skills-manager-cli skills install ./my-skill

# Force a source type when the ref is ambiguous
skills-manager-cli skills install foo/bar --skillssh
skills-manager-cli skills install ./looks-like/owner-repo --local
```

**Default is library-only** — the skill enters the DB but doesn't appear in any agent yet. Prefer an explicit follow-up deployment so scope is unambiguous:

```bash
skills-manager-cli skills deploy <skill> --agent claude_code --agent codex
```

`--sync` and `--sync-preset` remain legacy shortcuts for the exclusive active-preset workflow.

**Ref resolution** is deterministic, no path-existence guessing:
1. Starts with `./`, `../`, `/`, or `~/` → local path
2. Contains `://`, ends in `.git`, or starts with `git@` → git URL
3. Matches `owner/repo`, `owner/repo/skill`, or `owner/repo@skill` → skillssh
4. Otherwise → error; pass `--local` / `--git` / `--skillssh` to disambiguate

**Always verify after install** with `skills list` or `skills show <name>` so you can confirm the skill landed and report the preset / sync state back to the user.

## Search

```bash
skills-manager-cli --json skills search "react performance" --limit 5
```

Each result has `install_ref` (paste straight into `skills install`), `installs` (popularity proxy), and `skills_sh_url`. Show the top 1–3 with install counts before installing — anything with 10K+ installs is battle-tested; anything under 100 needs a careful look at the source repo.

## Update / Check

```bash
# Re-fetch one skill (git/skillssh re-clones, local/import re-imports source dir)
skills-manager-cli skills update <skill-name-or-id>

# Re-fetch all eligible skills
skills-manager-cli skills update --all

# Just probe remote revisions, don't touch files
skills-manager-cli skills check --all
```

`check` is the dry-run partner of `update`. Local-only skills (no git source) are reported as `skipped: true`.

**An update replaces the skill's directory wholesale**, so anything written inside it that the new version does not have would be destroyed. When the CLI detects that, it applies nothing and reports the paths instead:

```jsonc
{ "name": "ppt-master", "refreshed": false,
  "held_back_removals": ["library: templates/mine.pptx"] }
```

The field is omitted entirely when nothing is held back, so test for its presence rather than for an empty array. `refreshed: false` *with* `held_back_removals` is **not a failure and not something to retry** — the skill is untouched and still on its old version. Show the user the listed paths and ask. There is no CLI flag to override this; only the desktop app can confirm and proceed, because only a person can say those files are expendable. The paths are prefixed with where they live (`library`, or an agent key for a deployed copy).

Note what this does *not* cover: a file the user edited that the new version also ships is reported as surviving, because its path survives — the update overwrites their edits silently. Warn anyone keeping local modifications inside a skill folder.

## Remove

```bash
# Always preview first when removing more than one
skills-manager-cli skills remove <skill> --dry-run

# --yes is required for the actual delete; --json mode does NOT auto-confirm
skills-manager-cli skills remove <skill> --yes
```

Remove deletes the central-library copy, all synced targets across agents, and the DB row. It's not reversible without re-installing.

## Deploy / Undeploy

```bash
skills-manager-cli skills deploy <skill> --agent claude_code
skills-manager-cli skills undeploy <skill> --agent codex
skills-manager-cli skills deploy <skill-a> <skill-b> --agent codex --dry-run
skills-manager-cli skills deploy <skill> --agent claude_code --agent codex
skills-manager-cli --json skills status <skill>
```

These commands change real managed deployments without deleting the central-library copy or changing preset membership. `skills enable/disable` are deprecated compatibility commands and do not change deployment; never use them.

`skills deploy` and `skills undeploy` always require at least one explicit `--agent`, whether the command names one skill or several. `skills status` also reports target rows left by a custom agent that is no longer registered, so stale deployments stay visible and can be cleaned with an explicit undeploy while the row exists.

## Legacy exclusive sync

```bash
# Sync current active preset to all enabled agents
skills-manager-cli skills sync

# Preview the target list — safe, no writes
skills-manager-cli skills sync --dry-run

# Switch the one legacy active preset, then sync
skills-manager-cli skills sync --preset "Web Dev"

# Only sync to a single agent (useful when one agent's directory got out of sync)
skills-manager-cli skills sync --tool claude_code
```

## Adopt skills installed elsewhere

When skills already live in an agent's directory (e.g. installed via `npx skills add` or manual `git clone`) but aren't in the central library, pull them in:

```bash
# Dry-run scan first — lists candidates without writing
skills-manager-cli skills adopt ~/.claude/skills --dry-run

# Adopt everything found — each becomes source_type=local (can't auto-update from git)
skills-manager-cli skills adopt ~/.claude/skills

# Adopt a single skill and pin it to a git source so `update` works later
skills-manager-cli skills adopt ~/.claude/skills/react-best-practices \
  --git-url https://github.com/vercel-labs/agent-skills/tree/main/react-best-practices

# Or pass --git-subpath explicitly when the URL is just the repo root
skills-manager-cli skills adopt ~/.claude/skills/react-best-practices \
  --git-url https://github.com/vercel-labs/agent-skills \
  --git-subpath react-best-practices

# Skill lives at the repo root? Pass an empty subpath
skills-manager-cli skills adopt ~/.claude/skills/my-skill \
  --git-url https://github.com/me/my-skill --git-subpath ""
```

`adopt` auto-excludes anything already in the DB or already a sync target, so it's safe to re-run. `--git-url` requires either a URL with a subpath (`/tree/branch/path`) or an explicit `--git-subpath` — without that, future `update` would re-clone the wrong directory, so the CLI refuses to guess.

## Tag

```bash
skills-manager-cli skills tag add <skill> web frontend
skills-manager-cli skills tag remove <skill> frontend
skills-manager-cli skills tag set <skill> web frontend
skills-manager-cli skills tag rename frontend web
skills-manager-cli skills tag delete obsolete --dry-run
skills-manager-cli skills tag delete obsolete --yes
skills-manager-cli skills tag list <skill>   # tags on one skill
skills-manager-cli skills tag list           # all distinct tags
```

Useful organization queries:

```bash
skills-manager-cli --json skills list --untagged
skills-manager-cli --json skills list --no-preset
skills-manager-cli --json skills list --tag frontend
skills-manager-cli --json skills list --preset "Web Dev"
skills-manager-cli --json skills list --deployed-to codex
```

## Presets

```bash
skills-manager-cli presets list
skills-manager-cli presets current
skills-manager-cli presets show "Web Dev"
skills-manager-cli presets create "Web Dev" --description "Frontend work"
skills-manager-cli presets update "Web Dev" --name "Frontend"
skills-manager-cli presets delete "Old" --dry-run
skills-manager-cli presets delete "Old" --yes

skills-manager-cli presets add-skill <preset> <skill>...
skills-manager-cli presets remove-skill <preset> <skill>...

skills-manager-cli presets deploy <preset>                  # all enabled coding agents
skills-manager-cli presets deploy <preset> --agent codex
skills-manager-cli presets undeploy <preset> --agent claude_code
skills-manager-cli presets undeploy <preset>                # every agent with target rows for this preset
skills-manager-cli --json presets status <preset>
```

`deploy/undeploy` are additive and match the app's Preset pills. Explicit `presets apply/deactivate` commands remain for the legacy exclusive active-preset model; do not use them for normal "turn this preset on/off" requests.

The no-`--agent` defaults intentionally differ: deploy targets all installed, enabled coding agents; undeploy discovers the preset's actual target rows and removes them even when an agent is now disabled, uninstalled, or no longer registered. Use the no-agent undeploy for "turn this preset off everywhere."

Preset create/update/delete and add-skill/remove-skill are organization-only CLI operations. They never deploy or undeploy agent files implicitly.

## Health check

When sync misbehaves or a command errors in a confusing way:

```bash
skills-manager-cli --json repo status   # base dir, skill / preset counts, active preset
skills-manager-cli --json agents list  # detected agents and their target paths
skills-manager-cli agents enable codex
skills-manager-cli agents disable claude_code
```

`repo status` and `agents list` are read-only and are the first checks for "why isn't this skill showing up in Cursor" questions. `agents disable` is a real mutation: it removes every managed deployment for that agent. `agents enable` makes the agent globally available again and re-syncs the legacy active preset, if one exists; use explicit skill or preset deployment afterward when the requested state is additive.

Use `agents disable <agent>` when the user wants the whole Agent integration turned off or wants every managed skill removed from it. If they only want one skill or preset removed while keeping the Agent available for future deployments, use `skills undeploy` or `presets undeploy` instead.

## Typical workflows

### "Find me a skill for X" / "Install a skill that does X"

1. `skills search "X" --limit 5` — show the top 1–3 hits with install counts and source.
2. If a clear winner: `skills install <install_ref>`.
3. If ambiguous: ask the user to pick.
4. Deploy it to the agent(s) the user requested with `skills deploy`.
5. `skills status <name>` to confirm the library and deployment state.

### "What skills do I have?"

```bash
skills-manager-cli --json skills list
```

The `preset_ids`, `presets`, `deployed_to`, `tags`, and `source_type` fields are usually the most informative. The legacy `enabled` field is not deployment state.

### "Pull in the skills already installed in my agent directories"

1. `skills adopt ~/.claude/skills --dry-run` (and any other agent dirs the user mentions) — show the candidate list.
2. After user confirms: `skills adopt ~/.claude/skills`.
3. For any adopted skill where the user knows the original repo, follow up with `skills adopt ... --git-url ... --git-subpath ...` to restore the update link.

### "Update everything"

```bash
skills-manager-cli skills check --all     # see what has upstream changes
skills-manager-cli skills update --all    # apply
```

Report which skills actually refreshed (`refreshed: true` in the JSON) vs which were already up-to-date.

## Pitfalls

- **Install succeeded but skill doesn't appear in the agent** → install defaults to library-only. Use `skills deploy <skill> --agent <key>`.
- **Preset membership changed but agent files did not** → membership is organization only. Follow with `presets deploy` or `skills deploy` when the user also asked to make it visible.
- **No active preset** only affects legacy `skills sync` / `presets apply`; additive deploy commands do not require one.
- **Adopted skills can't be `update`d from git** → `npx skills add` and manual `git clone` don't leave source metadata, so adopt has to treat them as `local`. Fix per-skill with `adopt ... --git-url ... --git-subpath ...`, or just `skills remove` + `skills install <git-ref>` to start clean with a real source.
- Use `--dry-run` before bulk remove, tag delete, preset delete, deploy, or undeploy operations. Use `check` before `update`.
