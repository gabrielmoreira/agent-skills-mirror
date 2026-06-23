---
name: specification-generator
description: Skill workflow for creating and synchronizing AI agent specifications (rules, agents, commands, or skills) in the specifications/ directory.
---

# Skill: AI Agent Specification Generator

This skill guides the AI assistant in creating, modifying, and compiling new developer specification files (rules, agents, commands, or skills) within the unified directory structure.

## Scaffolding Tool Usage

When asked by the user to add or bootstrap a specification, run the custom scaffolding script from the workspace root rather than writing directories manually. This ensures that proper YAML frontmatter and file structures are established.

```bash
npm --prefix specification-scripts run spec:create -- --type <type> --domain <domain> --name <name> --description "<description>"
```

### Parameters
- `--type`: One of `rule`, `agent`, `command`, `skill`
- `--domain`: One of `common`, `typescript`, `frontend`, `backend`, `database`, `testing`, `deployment`
- `--name`: kebab-case identifier (e.g. `query-caching` or `a11y-contrast`)
- `--description`: A short description summarizing the purpose of the specification

## Directory Mapping

The tool generates file targets under `specifications/` according to the following category/type scheme:

| Specification Type | Folder Path under `specifications/<domain>/` | Compiled Copilot Target | Compiled Claude Target |
|---|---|---|---|
| **rule** | `rules/<name>.md` | `.github/instructions/<name>.instructions.md` | `.claude/rules/<name>.md` |
| **agent** | `agents/<name>.md` | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` |
| **command** | `commands/<name>.md` | `.github/prompts/<name>.prompt.md` | `.claude/commands/<name>.md` |
| **skill** | `skills/<name>/SKILL.md` | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |

## Code Synchronization

The scaffolding tool automatically calls the synchronization engine on success. If you make manual updates to a file inside the `specifications/` directory, you **must** immediately trigger compilation to propagate the updates to the platform-specific folders:

```bash
npm --prefix specification-scripts run spec:sync
```

> [!WARNING]
> Never write or edit files directly inside the `.github/` or `.claude/` directories. Any direct edits will be overwritten the next time a sync command is executed.
