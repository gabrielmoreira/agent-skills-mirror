# Kiro CLI Advanced Reference

## Installation

See official guide: [https://kiro.dev/docs/cli/installation](https://kiro.dev/docs/cli/installation)

---

## Authentication

See official guide: [https://kiro.dev/docs/cli/authentication](https://kiro.dev/docs/cli/authentication)

```bash
kiro-cli login      # Sign in
kiro-cli logout     # Sign out
kiro-cli whoami     # Check current user
kiro-cli doctor     # Diagnose issues
```

### Remote Login (SSH)

**Builder ID / IAM**: Uses device code — works automatically.

**Social login (GitHub/Google)**:
1. Run `kiro-cli login` on remote, note the port (e.g., 49153)
2. On local: `ssh -L 49153:localhost:49153 -N user@remote-host`
3. Press Enter on remote, complete auth in local browser

---

## Steering (Project Context)

Provide persistent knowledge via markdown in `.kiro/steering/`:

```
.kiro/steering/
├── product.md       # Product overview
├── tech.md          # Tech stack
├── structure.md     # Project structure
└── api-standards.md # API conventions
```

- **Workspace**: `.kiro/steering/` — current project only
- **Global**: `~/.kiro/steering/` — all projects
- **AGENTS.md**: Supported in project root or `~/.kiro/steering/`

---

## Kiro Skills

Skills are instruction packages that extend Kiro's capabilities. They activate automatically based on your request.

### Default Agent

Automatically loads skills from `.kiro/skills/` and `~/.kiro/skills/`. No configuration needed.

### Custom Agents

Must explicitly declare skills in `resources`:

```json
{
  "resources": [
    "skill://.kiro/skills/*/SKILL.md",
    "skill://~/.kiro/skills/*/SKILL.md"
  ]
}
```

If a custom agent isn't using expected skills, check that `skill://` paths are in its `resources` field.

---

## Knowledge Bases

For large codebases or documentation (millions of tokens). Searched on demand, doesn't consume context until needed.

### Enable Knowledge Base

```bash
kiro-cli settings chat.enableKnowledge true
```

### Add Content

```bash
> /knowledge add /path/to/codebase --include "**/*.py" --exclude "node_modules/**"
```

### In Agent Config

```json
{
  "resources": [
    {
      "type": "knowledgeBase",
      "source": "file://./docs",
      "name": "ProjectDocs",
      "description": "Project documentation",
      "indexType": "best",
      "autoUpdate": true
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `indexType` | `"best"` (quality) or `"fast"` (speed) |
| `autoUpdate` | Re-index when agent spawns |

---

## MCP Integration

```bash
kiro-cli mcp add --name my-server --command "node server.js" --scope workspace
kiro-cli mcp list [workspace|global]
kiro-cli mcp status --name my-server
kiro-cli mcp remove --name my-server --scope workspace
```

### In Agent Config

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  },
  "includeMcpJson": true
}
```

### MCP Loading Priority

Agent config > Workspace `.kiro/settings/mcp.json` > Global `~/.kiro/settings/mcp.json`

---

## Custom Agent Configuration

Location: `.kiro/agents/<name>.json` (local) or `~/.kiro/agents/<name>.json` (global)

### Key Fields

| Field | Description |
|-------|-------------|
| `name` | Agent identifier |
| `description` | What the agent does |
| `prompt` | System prompt (inline or `file://path`) |
| `tools` | Available tools (`["read", "write", "@git"]`, or `["*"]` for all) |
| `allowedTools` | Pre-approved tools (supports wildcards) |
| `toolsSettings` | Tool-specific config |
| `resources` | Context (`file://`, `skill://`, `knowledgeBase`) |
| `mcpServers` | MCP server configs |
| `hooks` | Lifecycle hooks |
| `model` | Model override |
| `keyboardShortcut` | Quick switch (e.g., `"ctrl+a"`) |
| `welcomeMessage` | Shown when switching to agent |

### Example

```json
{
  "name": "aws-expert",
  "description": "AWS infrastructure specialist",
  "prompt": "You are an AWS expert. Follow best practices.",
  "tools": ["read", "write", "shell", "aws"],
  "allowedTools": ["read", "aws"],
  "toolsSettings": {
    "aws": {
      "allowedServices": ["s3", "lambda", "cloudformation"]
    }
  },
  "resources": [
    "file://README.md",
    "file://.kiro/steering/**/*.md",
    "skill://.kiro/skills/**/SKILL.md"
  ],
  "model": "claude-sonnet-4",
  "keyboardShortcut": "ctrl+a"
}
```

### AllowedTools Wildcards

```json
{
  "allowedTools": [
    "read",                    // Exact match
    "@git/git_status",         // Specific MCP tool
    "@server/read_*",          // Prefix wildcard
    "@fetch"                   // All tools from server
  ]
}
```

---

## Subagents

Subagents run tasks autonomously in parallel.

### Capabilities

- Own context and tool access
- Live progress tracking
- Parallel execution
- Results returned to main agent

### Available Tools in Subagents

✓ `read`, `write`, `shell`, `code`, MCP tools
✗ `web_search`, `web_fetch`, `grep`, `glob`

### Config

```json
{
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["reviewer", "tester"],
      "trustedAgents": ["reviewer"]
    }
  }
}
```

---

## Hooks

Run commands at lifecycle trigger points.

### Hook Types

| Hook | Trigger |
|------|---------|
| `agentSpawn` | When agent is activated |
| `userPromptSubmit` | When user submits prompt |
| `preToolUse` | Before tool execution (can block) |
| `postToolUse` | After tool execution |
| `stop` | When assistant finishes |

### Example

```json
{
  "hooks": {
    "agentSpawn": [
      { "command": "git status" }
    ],
    "preToolUse": [
      {
        "matcher": "execute_bash",
        "command": "echo \"$(date) - Bash:\" >> /tmp/audit.log"
      }
    ],
    "postToolUse": [
      {
        "matcher": "fs_write",
        "command": "cargo fmt --all"
      }
    ]
  }
}
```

---

## Prompts Management

Create reusable prompt templates.

```bash
/prompts list                           # List all prompts
/prompts create --name code-review      # Create prompt
/prompts edit code-review               # Edit prompt
/prompts details code-review            # View details
```

### Using Prompts

```
@code-review                            # Use local prompt
@server-name/prompt-name arg1 arg2      # MCP prompt with args
```

### Storage

- Local: `.kiro/prompts/`
- Global: `~/.kiro/prompts/`

Priority: Local > Global > MCP

---

## Settings

```bash
kiro-cli settings list --all            # Show all settings
kiro-cli settings <key> <value>         # Set value
kiro-cli settings -d <key>              # Reset to default
```

### Common Settings

| Setting | Description |
|---------|-------------|
| `chat.defaultModel` | Default model |
| `chat.defaultAgent` | Default agent |
| `chat.enableKnowledge` | Enable knowledge bases |
| `chat.enableTangentMode` | Enable tangent mode |
| `chat.diffTool` | External diff tool |

---

## In-Chat Commands

Quick reference (detailed usage for `/tools`, `/context`, `/model` in main SKILL.md):

| Command | Description |
|---------|-------------|
| `/help` | Switch to Help Agent |
| `/plan` | Enter Plan Agent mode |
| `/agent swap` | Switch agent |
| `/model` | Change model |
| `/tools` | Manage tool permissions |
| `/context` | Manage context files |
| `/knowledge` | Manage knowledge bases |
| `/prompts` | Manage prompt templates |
| `/mcp` | View MCP servers |
| `/editor` | Multi-line input |
| `/reply` | Reply to specific parts |
| `/paste` | Paste image from clipboard |
| `/compact` | Compress context (summarize old messages) |
| `/chat save/load` | Save/load session |
| `Ctrl+J` | Insert newline |
| `Shift+Tab` | Toggle Plan mode |

---

## Other Commands

```bash
kiro-cli translate "find large files"   # Natural language → shell
kiro-cli update                         # Update Kiro CLI
kiro-cli doctor                         # Diagnose issues
kiro-cli uninstall                      # Uninstall (macOS)
```
