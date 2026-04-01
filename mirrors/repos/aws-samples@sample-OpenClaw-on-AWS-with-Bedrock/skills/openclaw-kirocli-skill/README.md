# OpenClaw Kiro CLI Skill 🦉

[中文文档](./README.zh-CN.md)

> A dedicated [OpenClaw](https://github.com/openclaw/openclaw) skill for [Kiro CLI](https://kiro.dev/) — AWS's AI coding assistant.

## What is This?

This repository provides a **Kiro-only skill** for OpenClaw. It teaches OpenClaw how to:

- Launch and manage Kiro CLI sessions (interactive or one-shot)
- Use Plan Mode for complex multi-step projects
- Save and resume development conversations
- Switch between custom agents
- Run coding tasks in the background with progress tracking

### How is this different from [openclaw-kirocli-coding-agent](https://github.com/terrificdm/openclaw-kirocli-coding-agent)?

| | This Repo (kiro-cli) | coding-agent |
|---|---|---|
| **Focus** | Kiro CLI only | Multi-agent (Kiro, Codex, Claude Code, OpenCode, Pi) |
| **Depth** | Deep Kiro integration with all features | General coding agent orchestration |
| **Use Case** | You only use Kiro CLI | You switch between multiple coding agents |
| **Features** | Plan Mode, Session Resume, Custom Agents, Context Management | Basic launch & monitor for all agents |

**Choose this skill if:** You're committed to Kiro CLI and want full feature coverage.

**Choose coding-agent if:** You use multiple coding agents and need flexibility.

## What is OpenClaw?

[OpenClaw](https://github.com/openclaw/openclaw) is an open-source AI assistant framework that connects to various messaging platforms (WhatsApp, Discord, Telegram, Signal, etc.). It can be extended with **skills** — modular instruction sets for specific tasks.

## What is Kiro CLI?

[Kiro CLI](https://kiro.dev/) is AWS's AI coding assistant with powerful features:

- **Plan Mode** — Structured planning for complex projects
- **Session Persistence** — Save and resume conversations
- **Custom Agents** — Pre-configured tool permissions and behaviors
- **MCP Integration** — Model Context Protocol support
- **Steering Files** — Project context awareness

## Installation

### 1. Install Prerequisites

**OpenClaw:** Follow the [installation guide](https://docs.openclaw.ai/)

**Kiro CLI:**
```bash
curl -fsSL https://kiro.dev/install.sh | bash
kiro-cli login
```

### 2. Add the Skill

**Option A: Clone to workspace (recommended)**
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/terrificdm/openclaw-kirocli-skill.git kiro-cli
```

**Option B: Copy files only**
```bash
mkdir -p ~/.openclaw/workspace/skills/kiro-cli
cp -r skills/kiro-cli/* ~/.openclaw/workspace/skills/kiro-cli/
```

## Usage

Once installed, OpenClaw will automatically use this skill when you mention **"kiro"** or need to work with code.

### One-Shot Tasks

```
"Use kiro to add error handling to my API routes"
"Ask kiro to list all TODO comments in src/"
```

OpenClaw runs:
```bash
kiro-cli chat --no-interactive --trust-all-tools "your task"
```

### Interactive Sessions

```
"Start a kiro session to help me build a REST API"
"Tell kiro I want to use FastAPI with SQLAlchemy"
```

OpenClaw manages background sessions:
```bash
# Start session
exec pty:true background:true command:"kiro-cli"

# Send messages & monitor progress
process action:submit sessionId:XXX data:"your message"
process action:log sessionId:XXX
```

### Plan Mode (Complex Projects)

```
"Use kiro's plan mode to design a user authentication system"
```

Plan Mode workflow:
1. **Requirements** — Kiro asks clarifying questions
2. **Research** — Analyzes your codebase
3. **Planning** — Creates detailed implementation plan
4. **Execution** — Implements after your approval

### Session Management

```
"Resume my last kiro conversation"
"Save this kiro session as 'auth-refactor'"
```

Commands: `/chat save <name>`, `/chat load <name>`, `--resume`

## Key Features

| Feature | Command/Flag | Description |
|---------|--------------|-------------|
| Plan Mode | `/plan` | Structured planning for complex tasks |
| Session Resume | `/chat save/load` | Persist conversations |
| Custom Agents | `/agent swap <name>` | Switch agent configurations |
| Tool Trust | `--trust-all-tools` | Auto-approve tool execution |
| Context | `@path` syntax | Include files in conversation |
| Model Switch | `/model` | Change AI model mid-session |

## File Structure

```
skills/kiro-cli/
├── SKILL.md              # Main skill instructions
└── references/
    └── advanced.md       # Detailed feature documentation
```

## Tested Scenarios

This skill has been validated with 10 test scenarios:

- ✅ Non-interactive mode (one-shot tasks)
- ✅ Background interactive mode (long-running sessions)
- ✅ Plan Mode (1,215-line shooter game project)
- ✅ Session save/resume
- ✅ Custom agent switching
- ✅ Model confirmation (claude-sonnet-4.6)
- ✅ Workspace protection rules

## Important Notes

1. **Always use `pty:true`** — Kiro CLI needs a pseudo-terminal
2. **Use directory isolation** — `mkdir -p ~/project && cd ~/project && kiro-cli`
3. **Never run in `~/.openclaw/workspace`** — Contains sensitive files

## Links

- [OpenClaw](https://github.com/openclaw/openclaw) | [Docs](https://docs.openclaw.ai/)
- [Kiro CLI](https://kiro.dev/) | [Docs](https://kiro.dev/docs)
- [coding-agent skill](https://github.com/terrificdm/openclaw-kirocli-coding-agent) (multi-agent version)
