---
name: claude-code
description: >
  Reference for using Claude Code CLI to handle complex coding tasks.
  Use when Research-Claw needs to delegate multi-file projects, code review,
  refactoring, or agentic coding workflows to Anthropic's Claude Code.
  Trigger words: claude code, claude cli, delegate coding, code agent.
---

# Claude Code CLI (Anthropic)

Agentic coding tool by Anthropic. Reads, edits, and runs code with full project context. Supports non-interactive print mode for programmatic use.

## Detect Installation

```bash
which claude  # should return a path
claude --version
```

## Install

```bash
npm install -g @anthropic-ai/claude-code
```

Requires authentication: run `claude auth login` (Anthropic account or `--console` for API billing).

## Non-Interactive Usage (print mode)

For programmatic invocation from Research-Claw, use `-p` (print mode):

```bash
# Basic non-interactive execution
claude -p "Refactor the auth module to use async/await"

# Pipe content for analysis
cat src/utils.ts | claude -p "Find bugs in this file"

# JSON output for parsing
claude -p --output-format json "List all TODO comments in the project"

# Skip permission prompts (for fully automated pipelines)
claude -p --dangerously-skip-permissions "Fix all lint errors"

# Budget and turn limits
claude -p --max-turns 5 --max-budget-usd 2.00 "Add unit tests for the auth module"

# Model selection
claude -p --model sonnet "Explain this codebase architecture"
```

## Key Flags

| Flag | Description |
|------|-------------|
| `-p, --print` | Non-interactive mode: run task, print result, exit |
| `--model <model>` | Set model (`sonnet`, `opus`, or full model ID) |
| `--output-format <fmt>` | `text` / `json` / `stream-json` |
| `--max-turns <n>` | Limit agentic turns (print mode) |
| `--max-budget-usd <n>` | Spending cap in USD (print mode) |
| `--dangerously-skip-permissions` | Skip all permission prompts |
| `--allowedTools <tools>` | Auto-approve specific tools, e.g. `"Bash(git *)" "Read"` |
| `--tools <tools>` | Restrict available tools, e.g. `"Bash,Read,Edit"` |
| `--add-dir <path>` | Grant access to additional directories |
| `--append-system-prompt <text>` | Append to default system prompt |
| `-c, --continue` | Continue most recent conversation |
| `-r, --resume <id>` | Resume session by ID or name |
| `--effort <level>` | `low` / `medium` / `high` / `max` |

## Research-Claw exec Patterns

```bash
# Delegate a complex coding task
exec("claude -p --dangerously-skip-permissions --max-turns 10 'Implement the feature described in TODO.md'")

# Read-only analysis with budget cap
exec("claude -p --tools 'Read' --max-budget-usd 1.00 'Review code quality and list issues'")

# JSON output for structured results
exec("claude -p --output-format json 'List all exported functions in src/'")
```

## Docs

- CLI reference: https://code.claude.com/docs/en/cli-reference
- Common workflows: https://code.claude.com/docs/en/common-workflows
