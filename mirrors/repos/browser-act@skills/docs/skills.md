# Skills

## Installing the Entry Skill

Tell your agent:

> Install the browser-act Skill from https://github.com/browser-act/skills/tree/main/browser-act

The agent automatically downloads the SKILL file into its Skills directory. Once installed, the agent becomes aware of BrowserAct and invokes it when appropriate.

## Two-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Entry Skill (the installed file)       │
│  Lightweight, stable, rarely changes    │
│  Teaches the agent: "browser-act exists"│
├─────────────────────────────────────────┤
│  Runtime content (get-skills CLI)       │
│  Environment-aware, version-matched     │
│  Teaches the agent: "use it like this"  │
└─────────────────────────────────────────┘
```

### Layer 1: Entry Skill

The file installed into the agent's Skills directory. It's intentionally minimal:
- Triggers agent awareness of BrowserAct
- Contains trigger words that activate it
- Points the agent to `get-skills` for actual instructions

The entry Skill rarely changes — it's the stable entry point.

### Layer 2: Runtime Content via `get-skills`

The agent's first command must always be:

```bash
browser-act get-skills core --skill-version <version>
```

It returns everything the agent needs for the current session:
- **Environment state** — CLI version, API Key status
- **Browser list** — All available browsers with their IDs, types, and descriptions
- **Active sessions** — Currently running sessions
- **Core commands** — Interaction reference
- **Directives** — Dynamic rules based on the current state

## Topics

| Command | Content | When to use |
|---------|---------|-------------|
| `get-skills core --skill-version <v>` | Core workflow, commands, environment state | Always first |
| `get-skills advanced` | Proxy, Profile, privacy mode, advanced patterns | When core isn't enough |
| `get-skills main` | Latest SKILL.md content for self-update | When a version mismatch is detected |

## Progressive Loading

- **Most tasks only need `get-skills core`** — covers 80% of use cases
- **Load `get-skills advanced` only when needed** — proxy config, Profile import, etc.
- Avoid pulling unrelated information all at once

## Version Compatibility

The `--skill-version` parameter lets the CLI detect incompatibilities:

```bash
# The Skill claims version 2.0.2
browser-act get-skills core --skill-version 2.0.2
```

If the CLI version is incompatible with the Skill version, the output includes upgrade guidance:
- CLI too old → `uv tool upgrade browser-act-cli`
- Skill too old → `browser-act get-skills main` for the latest Skill content

Version compatibility is automatic: the Skill file declares its version, the CLI checks compatibility. When incompatible, the upgrade guidance lands directly in the output and the agent runs it automatically.

## Dynamic Directives

`get-skills` output includes "Directives" — context-aware rules generated based on the current state:

| Directive | Trigger |
|-----------|---------|
| **Multi-browser directive** | When multiple browsers exist, provides selection guidance based on `desc` matching |
| **Session directive** | When existing sessions are detected, reminds the agent of ownership rules |
| **Authentication directive** | When the API Key is missing, steers away from stealth operations |

Directives are BrowserAct's mechanism for adapting guidance to the agent's current situation without hard-coding every scenario in the Skill.

## Workflow from the Agent's Perspective

```
1. User says "check the price on example.com"
2. The agent's entry Skill activates (trigger word match)
3. Agent runs: browser-act get-skills core --skill-version 2.0.2
4. Agent receives: environment state + browser list + commands + dynamic directives
5. Agent picks an appropriate browser (desc match)
6. Agent confirms with the user (confirmation gate)
7. Agent executes browser operations
8. Agent closes the session, updates the browser's desc
```

## Agent Compatibility

Works with any agent that can:
1. Read SKILL files from a Skills directory
2. Execute shell commands
3. Parse text output

Compatibility list:
- **Claude Code** — SKILL.md in `.claude/skills/`
- **GitHub Copilot** — Discovered via the Skills directory
- **Cursor** — Rules / Skills directory
- **Windsurf** — Agent Skills system
- **Google Gemini CLI** — AGENTS.md integration
- **OpenCode** — Skills system
- **Codex** — Skills integration

## Next Steps

- [Quick Start](quick-start.md) — Run your first automation
- [Commands](commands.md) — Complete command reference
- [Skill Forge](skill-forge.md) — Bake operations into reusable Skills
