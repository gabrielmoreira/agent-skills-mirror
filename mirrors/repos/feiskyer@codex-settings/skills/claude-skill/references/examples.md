# Example Usage Scenarios

Use these as patterns, not rigid templates. Keep commands aligned with the installed `claude --help` output on the target machine.

## Read-Only Repository Analysis

**User**: "Use Claude Code to explain this codebase structure without changing anything."

```bash
claude -p "explain the codebase structure, major entry points, and risks for future refactors" \
  --tools "Read,Grep,Glob"
```

Why this works:

- No `--model`, so Claude Code uses the configured default model.
- `--tools` keeps the session read-only and predictable.

## Safe Bug Fix

**User**: "Use Claude Code headless mode to fix the authentication bug and run the relevant tests."

```bash
claude -p "fix the authentication bug in the login flow and run the relevant tests" \
  --permission-mode acceptEdits \
  --tools "Bash,Read,Edit,Write" \
  --allowedTools "Read" "Edit" "Write" "Bash(npm test *)"
```

Why this works:

- `acceptEdits` is a good default for coding tasks.
- `--tools` restricts built-in tool availability.
- `--allowedTools` pre-approves the specific test command pattern instead of every Bash command.

## Batch Refactor

**User**: "Update imports from `old-lib` to `new-lib` across the repo."

```bash
claude -p "update imports from old-lib to new-lib across the repository and report the affected files" \
  --permission-mode acceptEdits \
  --tools "Bash,Read,Edit,Write" \
  --allowedTools "Read" "Edit" "Write" "Bash(npm run test *)"
```

## JSON Security Report

**User**: "Review the current repository for security issues and return JSON."

```bash
claude -p "review the repository for security vulnerabilities and provide a concise report" \
  --output-format json \
  --append-system-prompt "Focus on concrete findings, exploitability, and mitigations."
```

Why this works:

- `json` output is easier to consume in scripts.
- `--append-system-prompt` keeps Claude Code defaults intact.

## Resume a Session

**User**: "Continue the session and add tests for the refactor."

```bash
claude -r "$session_id" -p "continue by adding tests for the refactor and summarizing the result"
```

## Continue the Most Recent Session

**User**: "Pick up where Claude Code left off."

```bash
claude -c -p "continue with the next step"
```

## MCP-Assisted Investigation

**User**: "Use Claude Code plus my monitoring MCP servers to investigate payment API latency."

```bash
claude -p "investigate the payment API latency spike and summarize likely causes" \
  --permission-mode acceptEdits \
  --mcp-config monitoring-tools.json \
  --allowedTools "Read" "mcp__datadog__*" "mcp__prometheus__*"
```

## Fully Unattended Run in a Sandbox

**User**: "Run Claude Code without permission prompts inside my CI container."

```bash
claude -p "apply the requested changes and run the validation steps" \
  --permission-mode bypassPermissions \
  --tools "Bash,Read,Edit,Write"
```

Use this only when the environment is already isolated. If the environment is not isolated, prefer `dontAsk` plus preconfigured permission rules or `acceptEdits` plus targeted `--allowedTools`.

## Read-Only Line Count

**User**: "Give me a read-only Claude Code command that counts lines of code by language."

```bash
claude -p "Count lines of code in this repository by language. Stay read-only and use only the find and wc shell families plus file reads." \
  --permission-mode default \
  --tools "Read,Bash" \
  --allowedTools "Read" "Bash(find:*)" "Bash(wc:*)"
```

Why this works:

- `--tools` defines the hard read-only boundary.
- `--allowedTools` pre-approves only the argument-aware `find` and `wc` command families.
- The command still uses the configured model because there is no `--model` flag.
