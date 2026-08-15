---
name: statusline
description: "Configures the Cursor CLI status line (statusLine.command in cli-config.json): stdin JSON for model, context %, git/worktree, ANSI stdout above the prompt. Use when the user mentions statusline, statusLine, CLI status bar, prompt footer, or a session context bar. Not for Starship, oh-my-posh, VS Code status bar, or tmux. Never block longer than timeoutMs; the line is local and does not spend API tokens."
version: 1.0.1
---

## Overview

The CLI supports a user-configurable status line rendered above the prompt. On each conversation update, a command is spawned, receives a JSON payload on stdin describing the session, and its stdout is displayed as the status line. The spec is aligned with Claude Code's status line. The status line runs locally and does not consume API tokens.

## When to Use

- User wants to customize the status line / status bar above the CLI prompt.
- User wants to show model name, context usage, git branch, worktree, vim mode, or session info in the prompt footer.
- User mentions `statusLine`, `statusline`, `status line`, `CLI status bar`, or `prompt footer`.
- User wants a multi-line status area with ANSI colors.

## Prerequisites

- The CLI is installed and `~/.cursor/cli-config.json` exists (or can be created).
- `jq` is available on PATH for JSON parsing in shell scripts (recommended).
- On Windows, `.cmd`/`.bat` scripts are spawned with `shell: true`; ensure the script is executable via the configured command path.

## Procedure

### 1. Add the `statusLine` entry to config

Edit `~/.cursor/cli-config.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.cursor/statusline.sh",
    "padding": 2
  }
}
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `type` | yes | — | Must be `"command"` |
| `command` | yes | — | Path to an executable or inline command. `~` is expanded. |
| `padding` | no | `0` | Horizontal inset (in characters) for the status line container. |
| `updateIntervalMs` | no | `300` | Minimum interval between invocations. Clamped to >= 300ms. |
| `timeoutMs` | no | `2000` | Maximum time the command may run before it is killed. |

The `command` field supports full paths, `~` expansion, and shell-style argument splitting. You can point it at a script file or use an inline command like `jq -r '...'`.

### 2. Create the status line script

Create `~/.cursor/statusline.sh` (or any path referenced in `command`). Make it executable:

```bash
chmod +x ~/.cursor/statusline.sh
```

### 3. Understand the stdin payload

The command receives a JSON object on stdin. Key fields:

| Field | Description |
|-------|-------------|
| `session_id` | Unique session identifier |
| `session_name` | Custom session name. Absent if no name has been set |
| `transcript_path` | Path to conversation transcript file |
| `render_width_chars` | Usable terminal columns minus built-in padding |
| `cwd`, `workspace.current_dir` | Current working directory (both contain the same value) |
| `autorun` | `true` when auto-run is enabled for the current session |
| `workspace.project_dir` | Directory where transcripts are stored |
| `workspace.added_dirs` | Additional directories (empty array for now) |
| `model.id`, `model.display_name` | Current model identifier and display name |
| `model.param_summary` | Formatted parameter summary (e.g. "(Thinking)", "High"). Absent when empty |
| `model.max_mode` | `true` when max mode is enabled. Absent otherwise |
| `version` | CLI version string |
| `output_style.name` | `"default"` or `"compact"` |
| `context_window.total_input_tokens` | Estimated input tokens (derived from used_percentage) |
| `context_window.total_output_tokens` | Cumulative output tokens (null when not tracked) |
| `context_window.context_window_size` | Maximum context window size in tokens |
| `context_window.used_percentage` | Percentage of context window used |
| `context_window.remaining_percentage` | Percentage of context window remaining |
| `context_window.current_usage` | Token counts from the last API call (null before first call) |
| `vim.mode` | `"NORMAL"` or `"INSERT"` when vim mode is enabled |
| `worktree.name` | Worktree name when running inside a worktree |
| `worktree.path` | Absolute path to the worktree directory |

**Fields that may be absent:** `session_name`, `model.param_summary`, `model.max_mode`, `vim`, `worktree`.

**Fields that may be null:** `context_window.current_usage` (null before first API call), `context_window.used_percentage` and `context_window.remaining_percentage` (may be null early in the session).

Full JSON schema example:

```json
{
  "session_id": "abc123",
  "session_name": "my session",
  "transcript_path": "/path/to/transcript.jsonl",
  "render_width_chars": 120,
  "cwd": "/Users/me/project",
  "autorun": false,
  "model": {
    "id": "claude-4-opus",
    "display_name": "Claude 4 Opus",
    "param_summary": "(Thinking)",
    "max_mode": true
  },
  "workspace": {
    "current_dir": "/Users/me/project",
    "project_dir": "/Users/me/project/.cursor/transcripts",
    "added_dirs": []
  },
  "version": "1.2.3",
  "output_style": {
    "name": "default"
  },
  "context_window": {
    "total_input_tokens": 15234,
    "total_output_tokens": null,
    "context_window_size": 200000,
    "used_percentage": 34.5,
    "remaining_percentage": 65.5,
    "current_usage": null
  },
  "vim": {
    "mode": "NORMAL"
  },
  "worktree": {
    "name": "my-feature",
    "path": "/Users/me/.cursor/worktrees/repo/my-feature"
  }
}
```

### 4. Write the script (choose an example)

#### Basic: model + context usage

```bash
#!/usr/bin/env bash
payload=$(cat)
model=$(echo "$payload" | jq -r '.model.display_name')
pct=$(echo "$payload" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
printf "\033[90m%s  ctx %s%%\033[0m" "$model" "$pct"
```

#### Context progress bar

```bash
#!/usr/bin/env bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

echo "[$MODEL] $BAR $PCT%"
```

#### Multi-line with git info

```bash
#!/usr/bin/env bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BRANCH=""
git rev-parse --git-dir > /dev/null 2>&1 && BRANCH=" | 🌿 $(git branch --show-current 2>/dev/null)"

echo -e "\033[36m[$MODEL]\033[0m 📁 ${DIR##*/}$BRANCH"
echo -e "ctx $PCT%"
```

#### Inline jq command (no script file)

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

### 5. Rendering rules

- **Multiple lines** are supported: each line of stdout renders as a separate row in the status area.
- **ANSI color codes** are supported (use chalk, tput, `\033[32m`, etc.).
- If the command exits non-zero with empty stdout, the status line is not updated (previous text is kept).
- If the command times out or a new update arrives while the script is running, the in-flight process is killed.
- The command is spawned with `child_process.spawn` (no shell on Unix, `shell: true` on Windows for `.cmd`/`.bat` compatibility). Updates are debounced at the configured interval. If a new update triggers while a script is running, the in-flight process is killed via `AbortController` and the new invocation starts immediately.

## Examples

See the scripts in step 4 above. For more advanced scripts, check `scripts/` in the skill directory for ready-to-use status line scripts, and `references/` for the full `StatusLinePayload` TypeScript interface definition. Load `references/` when you need the exact field types or want to verify which fields are nullable.

## Pitfalls

- **Null context percentages early in session:** `context_window.used_percentage` and `remaining_percentage` may be `null` before the first API call. Always use `// 0` in `jq` to default.
- **Absent optional fields:** `session_name`, `model.param_summary`, `model.max_mode`, `vim`, and `worktree` are absent entirely (not null) when not applicable. Use `// empty` or conditional checks rather than assuming they exist.
- **Script not executable:** On Unix, the script must have execute permission (`chmod +x`). A missing shebang line can also cause silent failures.
- **Timeout kills slow scripts:** Default `timeoutMs` is 2000ms. Git commands or network calls may exceed this. Increase `timeoutMs` if needed, but keep it reasonable to avoid UI lag.
- **Non-zero exit with empty stdout keeps old text:** If your script errors and prints nothing, the previous status line persists, which can be confusing during debugging. Always print something even on error paths.
- **Windows shell spawning:** On Windows, `.cmd`/`.bat` files are spawned with `shell: true`. Ensure the command path resolves correctly with `~` expansion or use a full path.
- **`updateIntervalMs` clamped to >= 300ms:** You cannot set a faster update interval than 300ms.
- **In-flight process killed on new update:** If updates arrive rapidly, your script may be killed mid-execution. Keep scripts fast and idempotent.

## Verification

1. **Test the script with mock input before wiring it up:**

```bash
echo '{"model":{"display_name":"Opus"},"context_window":{"used_percentage":25}}' | ./statusline.sh
```

Expected output (basic example):

```
Opus  ctx 25%
```

2. **Verify config is valid JSON:**

```bash
jq . ~/.cursor/cli-config.json
```

3. **Verify the script path resolves and is executable:**

```bash
ls -la ~/.cursor/statusline.sh
test -x ~/.cursor/statusline.sh && echo "executable" || echo "NOT executable"
```

4. **Test multi-line and color rendering** by piping a richer mock payload:

```bash
echo '{"model":{"display_name":"Claude 4 Opus","param_summary":"(Thinking)","max_mode":true},"context_window":{"used_percentage":42.5},"workspace":{"current_dir":"/Users/me/project"},"vim":{"mode":"NORMAL"}}' | ./statusline.sh
```

5. **Launch the CLI** and confirm the status line appears above the prompt with the expected model name, context percentage, and any additional fields. If nothing appears, check that the script exits 0 and produces stdout within `timeoutMs`.
