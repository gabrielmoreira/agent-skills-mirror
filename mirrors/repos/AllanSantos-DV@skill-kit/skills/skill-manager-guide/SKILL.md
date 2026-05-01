---
name: skill-manager-guide
description: "**GUIDE SKILL** — Guide to the Skill Manager for Copilot extension. USE FOR: adding/removing skill repos, syncing skills, pushing feedback, configuring sync intervals, troubleshooting sync issues, understanding skill format. DO NOT USE FOR: creating new skills (use skill-creator), creating agents (use agent-creator)."
argument-hint: Describe what you need help with in the Skill Manager extension
license: MIT
---

# Skill Manager for Copilot — User Guide

You are helping a developer who uses the **Skill Manager for Copilot** VS Code extension. This skill teaches you how the extension works so you can guide them effectively.

## What is a Skill?

A **skill** is a Markdown file (`SKILL.md`) that gives you (the AI agent) domain-specific knowledge. Skills are organized in Git repositories and synced to the developer's local workspace via this extension.

## Extension Commands

| Command | What it does |
|---------|-------------|
| `Skills: Add Repository` | Adds a Git repo URL as a skill source |
| `Skills: Add Official Repository` | Adds the curated official skill repo |
| `Skills: Remove Repository` | Removes a previously added repo |
| `Skills: Pull All` | Syncs all skills from all configured repos |
| `Skills: Pull Repo` | Syncs skills from a specific repo |
| `Skills: Push Feedback` | Sends local feedback to the repo via branch + PR |
| `Skills: Status` | Shows sync status of all skills |
| `Skills: Enable Skill` | Re-enables a disabled skill (including workspace-disabled) |
| `Skills: Disable Skill` | Disables a skill without deleting it |
| `Skills: Enable Agent` | Re-enables a disabled agent (including workspace-disabled) |
| `Skills: Disable Agent` | Disables an agent without deleting it |
| `Skills: Move Agent to Workspace` | Moves an agent from global to the current workspace |
| `Skills: Move Agent to Global` | Moves an agent from workspace back to global |
| `Skills: Browse Catalog` | Opens the skill catalog in the browser |

## How Sync Works

1. The extension clones configured repos to a local cache.
2. On `Pull`, it copies skills from `<repo>/skills/<name>/` to the workspace's `.github/skills/` directory.
3. Each synced skill gets a `.manifest.json` tracking its origin and hash.
4. If the local copy hasn't been edited, it auto-updates on next pull.
5. If the local copy was edited, the conflict strategy kicks in (configurable).

## Configuration

Users configure the extension in VS Code settings (`skillManager.*`):

```jsonc
{
  // List of skill repositories
  "skillManager.repos": [
    { "name": "Official", "url": "https://github.com/AllanSantos-DV/skill-kit.git", "priority": 1 },
    { "name": "Team", "url": "https://github.com/my-org/team-skills.git", "priority": 2 }
  ],

  // Auto-sync interval in minutes (0 = disabled)
  "skillManager.syncIntervalMinutes": 30,

  // What to do when same skill exists in multiple repos
  // "highest-priority" | "ask" | "keep-local"
  "skillManager.conflictStrategy": "highest-priority",

  // What to do when local skill was edited and repo has update
  // "keep-local" | "overwrite" | "ask"
  "skillManager.localEditStrategy": "ask"
}
```

## Skill Structure

Every skill lives in a folder under `skills/` in the repo:

```
skills/
  my-skill/
    SKILL.md            ← Required: the skill content (you read this)
    FEEDBACK.md         ← Optional: feedback protocol for this skill
    references/         ← Optional: extra docs loaded on-demand
      api-reference.md
      examples.md
```

### SKILL.md Frontmatter

```yaml
---
name: my-skill
description: What this skill teaches
---
```

Supported attributes: `name`, `description`, `argument-hint`, `compatibility`, `disable-model-invocation`, `license`, `metadata`, `user-invocable`.

### Version Convention

- **Patch** (1.0.0 → 1.0.1): typos, clarifications
- **Minor** (1.0.1 → 1.1.0): new scenarios, improvements
- **Major** (1.1.0 → 2.0.0): fundamental rewrites

## Feedback Flow

If a skill has `FEEDBACK.md`, users can submit improvements:

1. Developer writes feedback in the local skill directory
2. `Skills: Push Feedback` creates a branch and pushes
3. A PR is created on the skill repo for the maintainer to review

## Sidebar & Status

- The **Skill Manager** sidebar shows all skills grouped by repo
- Icons indicate state: ✓ synced, ↑ local-only, ⊘ disabled
- The status bar shows overall sync state: synced, divergent, error, or syncing
- Skills with benchmark reports show a 📊 icon; reports are centralized in `~/.copilot/skill-benchmarks/`

## Scoped Disable & Remove (Skills and Agents)

When disabling or removing a **global** skill or agent, the extension prompts "Global or this workspace?":

- **Global** — disables/removes for all workspaces. Persisted in `placements.json` (survives `.excluded.json` cleanup).
- **This workspace** — disables only in the current workspace. The item remains visible in other workspaces.

Re-enabling a workspace-disabled item (via `Enable Skill` or `Enable Agent`) reactivates it by removing the workspace entry from `placements.json`.

## Moving Agents Between Scopes

Just like skills, agents can be moved between global and workspace scope:

- **Move to Workspace** — copies the agent file to `.github/agents/` in the current workspace and removes from global. Tracked in `placements.json`.
- **Move to Global** — copies the agent file back to `~/.copilot/agents/` and removes from workspace. Tracked in `placements.json`.

On next `Pull`, the sync respects these decisions — an agent moved to a workspace is not reinstalled globally.

## Benchmark Reports

Benchmark reports are centralized in `~/.copilot/skill-benchmarks/`. When pulling from a repo that contains benchmarks (under `skill-benchmarks/`), results are:

1. Copied to the global benchmarks directory
2. Registered in `placements.json` for quick lookup
3. Accessible from the sidebar via the 📊 icon or the benchmark command

## When the User Asks for Help

- **"How do I add a skill repo?"** → `Ctrl+Shift+P` → `Skills: Add Repository` → paste the Git URL
- **"My skills aren't updating"** → Run `Skills: Pull All`, check status bar for errors
- **"How do I disable a skill?"** → Right-click the skill in sidebar → `Disable Skill`
- **"How do I create my own skill?"** → Create a folder under `skills/` with a `SKILL.md` containing frontmatter + content
- **"How do I submit improvements?"** → Edit the local skill, then `Skills: Push Feedback`
