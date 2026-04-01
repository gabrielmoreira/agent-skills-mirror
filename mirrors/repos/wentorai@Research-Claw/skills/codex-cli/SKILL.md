---
name: codex-cli
description: >
  Reference for using OpenAI Codex CLI to handle complex coding tasks.
  Use when Research-Claw needs to delegate multi-file projects, iterative
  debugging, or complex code generation to a specialized AI coding tool.
  Trigger words: codex, coding CLI, delegate coding, complex project.
---

# Codex CLI (OpenAI)

Terminal-based AI coding agent by OpenAI. Reads, edits, and runs code locally in a sandboxed environment. Built in Rust.

## Detect Installation

```bash
which codex  # should return a path
codex --version
```

## Install

```bash
npm i -g @openai/codex
```

Requires an OpenAI API key or ChatGPT account (prompted on first run).

## Non-Interactive Usage (exec)

For programmatic invocation from Research-Claw, use `codex exec`:

```bash
# Basic non-interactive execution
codex exec "Refactor the auth module to use JWT tokens"

# Pipe from stdin
echo "Fix the failing test in src/utils.test.ts" | codex exec -

# Full-auto mode (workspace writes + minimal approvals)
codex exec --full-auto "Add error handling to all API routes"

# Skip all approvals (dangerous — use only in sandboxed environments)
codex exec -a never -s workspace-write "Update dependencies and fix breaking changes"

# Save final response to file
codex exec -o result.md "Explain the architecture of this project"
```

## Key Flags

| Flag | Description |
|------|-------------|
| `-m, --model <model>` | Override model (e.g. `gpt-5-codex`) |
| `-a, --ask-for-approval <mode>` | `untrusted` / `on-request` / `never` |
| `-s, --sandbox <policy>` | `read-only` / `workspace-write` / `danger-full-access` |
| `--full-auto` | Shortcut: `workspace-write` sandbox + `on-request` approvals |
| `--add-dir <path>` | Grant write access to additional directories |
| `-C, --cd <path>` | Set working directory for the agent |
| `-i, --image <path>` | Attach image files (comma-separated) |
| `-o, --output-last-message <path>` | Write final response to file |
| `--json` | Print newline-delimited JSON events |
| `--ephemeral` | Don't persist session to disk |
| `--skip-git-repo-check` | Allow running outside a git repository |
| `--oss` | Use local OSS model via Ollama |

## Research-Claw exec Patterns

```bash
# Delegate a complex coding task
exec("codex exec --full-auto -C /path/to/project 'Implement the feature described in TODO.md'")

# Read-only analysis
exec("codex exec -s read-only -o /tmp/analysis.md -C /path/to/project 'Analyze code quality and list issues'")

# With model selection
exec("codex exec -m gpt-5-codex --full-auto 'Fix all TypeScript type errors'")
```

## Docs

- CLI reference: https://developers.openai.com/codex/cli/reference
- SDK (programmatic): https://developers.openai.com/codex/sdk
