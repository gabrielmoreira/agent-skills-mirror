---
name: kiro-cli
description: Spawn Kiro CLI via background process for code-related tasks. Use when user mentions "kiro", "kiro-cli", or needs to work with code — writing, modifying, reading, analyzing, reviewing, debugging, explaining, or understanding codebases. This includes building features, fixing bugs, refactoring, writing tests, code review, and exploring unfamiliar code.
metadata:
  {
    "openclaw": {
      "emoji": "🦉",
      "requires": { "bins": ["kiro-cli"] },
      "homepage": "https://kiro.dev"
    }
  }
---

# Kiro CLI

AWS AI coding assistant for building, testing, and deploying applications with automated workflows.

**Model:** `claude-sonnet-4.6` is the default (set via `kiro-cli settings chat.defaultModel`)

## ⚠️ PTY Required

Kiro is an interactive terminal app. Always use `pty:true` in exec tool:

```
bash pty:true command:"kiro-cli"
```

Without PTY, output breaks or agent hangs.

### Bash Tool Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | string | The shell command to run |
| `pty` | boolean | **Use for kiro!** Allocates pseudo-terminal for interactive CLIs |
| `workdir` | string | Working directory — ⚠️ may fallback to cwd if unavailable, use `mkdir -p && cd` instead |
| `background` | boolean | Run in background, returns sessionId for monitoring |
| `timeout` | number | Timeout in seconds (kills process on expiry) |
| `elevated` | boolean | Run on host instead of sandbox (if allowed) — use when kiro needs full file system access |

### Process Tool Actions (for background sessions)

| Action | Description |
|--------|-------------|
| `list` | List all running/recent sessions |
| `poll` | Check if session is still running |
| `log` | Get session output (with optional offset/limit) |
| `write` | Send raw data to stdin |
| `submit` | Send data + newline (like typing and pressing Enter) |
| `send-keys` | Send key tokens or hex bytes |
| `paste` | Paste text (with optional bracketed mode) |
| `kill` | Terminate the session |

## Quick Reference

| Mode | Command |
|------|---------|
| Interactive | `kiro-cli` |
| One-shot | `kiro-cli chat --no-interactive "prompt"` |
| Auto-approve all | add `--trust-all-tools` |
| Auto-approve specific | add `--trust-tools "fs_read,fs_write"` |
| Resume session | add `--resume` or `--resume-picker` |
| Custom agent | add `--agent <name>` |

## Non-Interactive Mode

Use for automation and one-shot queries:

```
# Single response, then exit (mkdir -p ensures directory exists)
bash pty:true command:"mkdir -p ~/project && cd ~/project && kiro-cli chat --no-interactive 'List TODO comments'"

# Auto-approve all tools
bash pty:true command:"mkdir -p ~/project && cd ~/project && kiro-cli chat --no-interactive --trust-all-tools 'Create hello.py'"

# Trust specific tools only
bash pty:true command:"mkdir -p ~/project && cd ~/project && kiro-cli chat --no-interactive --trust-tools 'fs_read,fs_write' 'Summarize package.json'"
```

**⚠️ Always use `mkdir -p <dir> && cd <dir> &&` instead of `workdir:` parameter** — if workdir is unavailable, exec may fallback to ~/.openclaw/workspace which contains sensitive files.

## Interactive Mode (Background)

Use for multi-turn conversations or longer tasks:

```
# Start background session
bash pty:true background:true command:"mkdir -p ~/project && cd ~/project && kiro-cli"
# Returns sessionId for tracking

# Monitor output
process action:log sessionId:<id>

# Check if still running
process action:poll sessionId:<id>

# Send input (if kiro asks a question)
process action:write sessionId:<id> data:"y"

# Submit with Enter (like typing and pressing Enter)
process action:submit sessionId:<id> data:"Build a REST API"

# Kill if needed
process action:kill sessionId:<id>
```

**Why directory matters:** Kiro wakes up in a focused directory, doesn't wander off reading unrelated files (like your SOUL.md 😅).

## Session Commands

```bash
kiro-cli chat --resume           # Resume last session in current directory
kiro-cli chat --resume-picker    # Pick from saved sessions
kiro-cli chat --list-sessions    # List all sessions
kiro-cli chat --delete-session <ID>  # Delete a session
```

In-chat commands:
- `/chat save <name>` — Save current conversation
- `/chat load <name>` — Load saved conversation
- `/chat resume` — Resume from saved sessions

## Tool Permissions

```bash
/tools                 # List all tools and permissions
/tools trust read      # Trust a tool for session
/tools untrust shell   # Require confirmation
/tools trust-all       # Trust all tools (use carefully!)
/tools reset           # Reset to defaults
```

Default: only `read` is trusted. Others require confirmation.

## Context Management

```bash
/context show              # View current context usage
/context add README.md     # Add file to session context
/context add docs/*.md     # Add with glob pattern
/context remove file.py    # Remove from context
/context clear             # Clear all session context
```

For persistent context, use agent `resources` field instead.

## File References

Use `@path` syntax to include files inline:

```
@src/index.ts              # Include file contents
@src/                      # Include directory tree
@"path with spaces.txt"    # Quoted paths
```

Tab completion works after `@`.

## Model Selection

```bash
/model                     # Show current model
/model <name>              # Switch model
/model set-current-as-default  # Save as default
```

Models: Auto (cost-effective), Claude Opus 4.6, Claude Sonnet 4.6/4.5/4.0, Claude Haiku 4.5

## Custom Agents

```bash
kiro-cli agent list              # List agents
kiro-cli agent create my-agent   # Create new agent
kiro-cli agent generate          # AI-assisted creation
kiro-cli --agent my-agent        # Use agent
```

Config: `.kiro/agents/` (local) or `~/.kiro/agents/` (global)

## Images

Drag and drop images into terminal, or use `/paste` for clipboard. Supported: JPEG, PNG, GIF, WebP (max 10MB, up to 10 images per request).

## Help Agent

Use `/help` to switch to built-in Help Agent for questions about Kiro CLI features, commands, and configuration.

## Plan Mode

Suggest `/plan` to user for complex multi-step tasks:

```
> /plan Build a user auth system
```

Workflow: Requirements → Research → Plan → Handoff

Plan agent is read-only (can explore code but not modify).

## Quick Examples

```
# Quick one-shot
bash pty:true command:"mkdir -p ~/project && cd ~/project && kiro-cli chat --no-interactive --trust-all-tools 'Add error handling'"

# Long task with wake notification
bash pty:true background:true command:"mkdir -p ~/project && cd ~/project && kiro-cli chat --no-interactive --trust-all-tools 'Refactor auth module. When done: openclaw gateway wake --text \"Done\" --mode now'"

# With custom agent
bash pty:true background:true command:"mkdir -p ~/project && cd ~/project && kiro-cli --agent aws-expert 'Set up Lambda'"
```

## Rules

1. Always use `pty:true` — Kiro needs a terminal
2. Respect user's tool choice — don't switch without asking
   - Orchestrator mode: do NOT hand-code patches yourself
   - If kiro fails/hangs, respawn it or ask user, but don't silently take over
3. Use `--no-interactive` for automation
4. Use `--trust-all-tools` for unattended execution
5. Suggest `/plan` for complex tasks — let user decide
6. **Use `mkdir -p <dir> && cd <dir> &&` not `workdir:`** — workdir fallback can leak into ~/.openclaw/workspace
7. **Be patient** — don't kill sessions because they're "slow"
8. **Monitor with process:log** — check progress without interfering
9. **NEVER spawn kiro in ~/.openclaw/workspace** — contains sensitive files (SOUL.md, MEMORY.md)
10. **Parallel is OK** — run multiple kiro sessions at once for batch work

## Progress Updates (Critical)

When you spawn kiro in the background, keep the user in the loop:

- Send 1 short message when you start (what's running + where)
- Then only update again when something changes:
  - a milestone completes (build finished, tests passed)
  - the agent asks a question / needs input
  - you hit an error or need user action
  - the agent finishes (include what changed + where)
- If you kill a session, immediately say you killed it and why

This prevents the user from seeing only "Agent failed before reply" and having no idea what happened.

## Advanced Features

See [references/advanced.md](references/advanced.md) for:
- Installation / Authentication (links to official docs)
- Steering (project context)
- Kiro Skills
- Knowledge Bases
- MCP Integration
- Custom Agent Configuration
- Subagents
- Hooks
- Prompts Management
- Settings
- In-Chat Commands
- Other Commands
