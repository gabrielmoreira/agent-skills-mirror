# Tool Sets Reference — Complete Guide

Detailed breakdown of every available tool set for custom agents, with role-based combinations.

---

## Built-In Tool Sets

### `search`

Tools for finding and understanding code across the workspace.

| Tool | What It Does |
|------|-------------|
| Codebase search | Semantic search across workspace files |
| File search | Find files by name/glob pattern |
| Text search (grep) | Exact text or regex search |
| List usages | Find references, definitions, implementations of a symbol |
| Search results | Access VS Code search view results |
| Changed files | Git diffs of current changes |

**Include when:** The agent needs to understand existing code, find files, or track changes.

### `read`

Tools for inspecting files and editor state.

| Tool | What It Does |
|------|-------------|
| Read file | Read contents of a file (with line ranges) |
| List directory | List folder contents |
| Problems/errors | Get compile/lint errors |
| Selection | Get current editor selection |
| Terminal last command | Get last command run in terminal |
| Terminal selection | Get selected text in terminal |

**Include when:** The agent needs to read file contents, check errors, or see terminal output.

### `edit`

Tools for modifying files in the workspace.

| Tool | What It Does |
|------|-------------|
| Replace in file | Edit existing file content (find and replace) |
| Create file | Create a new file with content |
| Rename symbol | Rename across workspace using language server |

**Include when:** The agent needs to modify, create, or rename files. **Omit for read-only agents.**

### `terminal`

Tools for running commands in the integrated terminal.

| Tool | What It Does |
|------|-------------|
| Run command | Execute a command in VS Code terminal |
| Background process | Start long-running processes (servers, watchers) |
| Get output | Retrieve output from background processes |
| Kill terminal | Stop a background process |

**Include when:** The agent needs to build, test, install, or run commands. **Omit for read-only agents.**

### `agent`

Tools for agent-to-agent communication.

| Tool | What It Does |
|------|-------------|
| Run sub-agent | Invoke another agent programmatically |

**Include when:** The agent orchestrates other agents (coordinators, orchestrators). **Requires `agents` field to list available sub-agents.**

### `todo`

Tools for tracking progress.

| Tool | What It Does |
|------|-------------|
| TODO list | Track items, mark as done |

**Include when:** The agent manages multi-step workflows. Lightweight, safe to include broadly.

### `web`

Tools for external research.

| Tool | What It Does |
|------|-------------|
| Fetch webpage | Get content from a URL |
| GitHub repo search | Search code in a GitHub repository |
| Open browser | Open URL in integrated browser |

**Include when:** The agent needs to research docs, verify APIs, or access external content.

---

## MCP Server Tools

MCP (Model Context Protocol) servers extend agent capabilities with custom tools.

### Syntax

```yaml
tools:
  - <server-name>/*        # All tools from a server
```

### Examples

```yaml
tools:
  - atlassian-mcp/*        # Jira + Confluence access
  - context7/*             # Library documentation lookup
  - my-custom-server/*     # Your custom MCP server
```

MCP tools follow the same inheritance rules as built-in tool sets: declare to restrict, omit `tools` entirely to inherit all (including MCP).

---

## Role-Based Combinations

### Read-Only Research Agent

```yaml
tools:
  - search        # find code
  - read          # read files
  - web           # external research
  - todo          # track progress
```

**Use case:** Researcher, analyst, documentation reviewer.
**Cannot:** Edit files, run commands, invoke sub-agents.

### Read-Only Validator

```yaml
tools:
  - search        # find code to verify
  - read          # read files to check
  - web           # verify external claims
  - todo          # track validation items
```

**Use case:** Code reviewer, assumption checker, quality gate.
**Cannot:** Edit files, run commands, invoke sub-agents.

### Orchestrator / Router

```yaml
# tools: omitted — inherits ALL
# Constrained by body instructions ("NEVER edit/run")
# Omitting ensures full-access sub-agents inherit ALL tools
```

**Use case:** Entry-point coordinator that classifies and delegates.
**Tool access:** ALL (inherited). Restriction is via body instructions ("NEVER edit files, run commands, or write code"), not via `tools` field.
**Why omit instead of declare?** If an orchestrator declares `tools: [search, read, agent, todo]`, sub-agents that omit `tools` (e.g. implementor) inherit only that restricted set — breaking their full-access design. Omitting `tools` on the orchestrator ensures the full tool set flows down to workers that need it.

### Full-Access Implementor

```yaml
# tools: omitted — inherits ALL
```

**Use case:** Agent that writes code, runs tests, creates files.
**Gets:** Everything — built-in tools, MCP tools, extension tools.

### Research + MCP Agent

```yaml
tools:
  - search
  - read
  - web
  - todo
  - atlassian-mcp/*       # Jira/Confluence context
  - context7/*            # Library docs
```

**Use case:** Researcher with access to project management and documentation tools.
**Cannot:** Edit files, run commands.

### Terminal-Only Ops Agent

```yaml
tools:
  - read           # check file state
  - terminal       # run commands
  - todo           # track tasks
```

**Use case:** DevOps agent for builds, deploys, infra tasks.
**Cannot:** Edit files directly, search code, invoke agents.

### Minimal Review Agent

```yaml
tools:
  - search
  - read
```

**Use case:** Focused code reviewer with minimal surface area.
**Cannot:** Anything beyond reading code.

---

## Decision Guide

Use this table to choose the right tool combination:

| The agent needs to... | Include |
|----------------------|---------|
| Find code/files | `search` |
| Read file contents | `read` |
| Edit/create files | `edit` |
| Run shell commands | `terminal` |
| Delegate to other agents | `agent` + set `agents` field |
| Track multi-step progress | `todo` |
| Research external docs/URLs | `web` |
| Use Jira/Confluence/custom tools | `<server-name>/*` |
| Do EVERYTHING | **Omit `tools` entirely** |

### The Inheritance Rule (Quick Reference)

```
tools: omitted     → Inherits ALL from parent (or system)
tools: [list]      → Gets ONLY what's listed (overrides inheritance)
tools: ['*']       → ❌ DOES NOT EXIST — this is NOT valid syntax
```
