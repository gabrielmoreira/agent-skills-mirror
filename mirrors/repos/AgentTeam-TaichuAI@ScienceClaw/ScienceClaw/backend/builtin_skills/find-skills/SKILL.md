---
name: find-skills
description: "MANDATORY: When a user asks to install, find, search, or add ANY skill (e.g. 'install hello-world skill', 'find a skill for X', 'add a skill'), you MUST first run `skills find <query>` to search the skills ecosystem. NEVER create a skill from scratch without searching first. Even if the name sounds simple, always search — it may already exist as a published skill."
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## CRITICAL RULES

1. **ALWAYS search first**: When a user asks to install/find/add ANY skill, your FIRST action must be running `skills find <query>` in the sandbox.
2. **NEVER create from scratch without searching**: Even for simple-sounding skills like "hello-world", search first.
3. **Use the CLI directly**: The `skills` CLI is pre-installed globally in the sandbox. Use `skills` directly (NOT `npx skills` — npx causes unnecessary download prompts).
4. **Install to session workspace**: Use `HOME=<workspace_dir> skills add ... -g -y --agent '*'` so skills land in the current session's workspace (visible in the task file viewer).
5. **Call propose_skill_save**: After installing and testing a skill, ALWAYS call the `propose_skill_save` tool with the skill name so the user can choose to save it permanently.

## When to Use This Skill

Use this skill when the user:

- Asks to **install** a skill (e.g., "install hello-world skill", "安装一个 skill")
- Asks to **find** or **search** for a skill (e.g., "find a skill for X", "找一个 skill")
- Mentions a skill **by name** (e.g., "hello-world skill", "react testing skill")
- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows

## What is the Skills CLI?

The Skills CLI (`skills`) is pre-installed globally in the sandbox. It is the package manager for the open agent skills ecosystem.

**IMPORTANT: Always use `skills` directly, NEVER use `npx skills` (npx will try to re-download and prompt for confirmation).**

**Key commands:**

- `skills find [query]` - Search for skills by keyword (use this FIRST)
- `HOME=<workspace_dir> skills add <package> -g -y --agent '*'` - Install a skill to session workspace
- `skills list -g` - List installed skills
- `skills check` - Check for skill updates

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Check Locally Installed Skills FIRST

Before searching the online ecosystem, check if a matching skill is **already installed locally**. Locally installed skills are listed in your system prompt under "Available Skills" and live at `/skills/<name>/SKILL.md`.

- If the user mentions a skill by name (e.g., "hello-world") and it appears in your available skills list → **use it directly**. Read its SKILL.md for instructions. No need to search online.
- If the user wants to **modify** an existing local skill → skip find-skills entirely and go to **skill-creator** (phase 2 in the Skill Policy).
- Only proceed to Step 2 if no local skill matches.

### Step 2: Understand What They Need

When no local skill matches, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 3: Search the Online Ecosystem

Run the find command with a relevant query:

```bash
skills find [query]
```

For example:

- User asks "how do I make my React app faster?" → `skills find react performance`
- User asks "can you help me with PR reviews?" → `skills find pr review`
- User asks "I need to create a changelog" → `skills find changelog`

The command will return results like:

```
Install with skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 4: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install command they can run
3. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "vercel-react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.

To install it:
skills add vercel-labs/agent-skills@vercel-react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 5: Install to Session Workspace

If the user wants to proceed, install the skill into the **session workspace** so it appears in the task file viewer. Use `HOME=<workspace_dir>` to redirect the global install path:

```bash
HOME=<workspace_dir> skills add <owner/repo@skill> -g -y --agent '*'
```

Replace `<workspace_dir>` with your actual workspace directory (from the system prompt).

- `HOME=<workspace_dir>` — redirects `-g` install to `<workspace_dir>/.agents/skills/`
- `-g` installs globally (user-level, relative to HOME)
- `-y` skips confirmation prompts
- `--agent '*'` skips the interactive agent selection (REQUIRED in sandbox)

**IMPORTANT:** Never omit any of these flags. Without `--agent '*'` the command will hang waiting for interactive input.

### Step 6: Test the Installed Skill

After installation, test the skill by reading its SKILL.md/TEMPLATE.md and following its instructions.

- **If it works** → call `propose_skill_save(skill_name="<skill-name>")` to let the user save it permanently. Done!
- **If it does NOT fit the user's needs** → **do NOT keep trying to fix or adapt it**. Uninstall it and go back to Step 4 to try the **next candidate** from the search results.

### Step 7: Bail-Out — When to Stop Searching

Stop searching and escalate to **skill-creator** (create from scratch) when ANY of these is true:

1. **No results**: `skills find` returned zero matches.
2. **Exhausted candidates**: You have tried 2–3 different skills and none fit.
3. **Poor relevance**: All search results are clearly unrelated to what the user needs.

When bailing out:
1. Briefly tell the user: "I couldn't find a suitable existing skill. I'll create one from scratch."
2. Read `/builtin-skills/skill-creator/SKILL.md` and follow it to create the skill.
3. **NEVER** loop endlessly on an unsuitable skill. Move on.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist after searching:

1. Acknowledge that no existing skill was found.
2. **Immediately escalate to skill-creator**: read `/builtin-skills/skill-creator/SKILL.md` and follow it to create the skill from scratch.
3. Do NOT ask the user whether to proceed — just start creating. The user already expressed intent by asking for the skill.
