---
name: drive
description: Terminal automation CLI for AI agents. Use drive to create tmux sessions, execute commands, send keystrokes, read output, poll for patterns, run commands in parallel across sessions, and manage processes. Always use --json for structured output.
---

# Drive — Terminal Automation via tmux

Run from: `cd apps/drive && uv run python main.py <command>`

Drive gives you full programmatic control over tmux sessions — creating terminals, running commands, reading output, and orchestrating parallel workloads.

## Commands

### session — Manage tmux sessions

```bash
drive session create agent-1 --json                     # Opens a Terminal window (headed — default)
drive session create agent-1 --window build --json      # Named window, headed
drive session create agent-1 --detach --json            # Headless (no Terminal window)
drive session list --json                                # List all sessions
drive session kill agent-1 --json                        # Kill a session
```

**Default is headed** — a new Terminal.app window opens attached to the session so you can watch live. Only use `--detach` when you explicitly need a headless session.

### run — Execute command and wait for completion

Uses sentinel protocol (`__DONE_<token>:<exit_code>`) for reliable completion detection.

```bash
drive run agent-1 "npm test" --json                     # Run and wait
drive run agent-1 "make build" --timeout 120 --json     # Custom timeout
drive run agent-1 "ls" --pane 1 --json                  # Target specific pane
```

Returns: exit code, captured output between sentinels.

### send — Raw keystrokes (no completion waiting)

For interactive tools (vim, ipython, etc.) where sentinel detection would interfere.

```bash
drive send agent-1 "vim file.txt" --json                # Send command
drive send agent-1 ":wq" --json                         # Send vim command
drive send agent-1 "y" --no-enter --json                # Send without Enter
```

### logs — Capture pane output

```bash
drive logs agent-1 --json                               # Current pane content
drive logs agent-1 --lines 500 --json                   # Last 500 lines of scrollback
drive logs agent-1 --pane 1 --json                      # Specific pane
```

### poll — Wait for pattern in output

```bash
drive poll agent-1 --until "BUILD SUCCESS" --json                   # Wait for pattern
drive poll agent-1 --until "ready" --timeout 60 --json              # With timeout
drive poll agent-1 --until "error|success" --interval 2.0 --json   # Custom interval
```

Pattern is a regex. Returns matched text and full pane content.

### fanout — Parallel execution

```bash
drive fanout "npm test" --targets agent-1,agent-2,agent-3 --json         # Same command, multiple sessions
drive fanout "git pull" --targets a1,a2,a3 --timeout 30 --json           # With timeout
```

Runs command in all target sessions concurrently using ThreadPoolExecutor. Returns ordered results.

## Key Patterns

- **Create sessions first** — `drive session create` before running commands (headed by default — opens a Terminal window)
- **Use `run` for commands that complete** — It waits and gives you exit code + output
- **Use `send` for interactive tools** — vim, ipython, anything that doesn't "finish"
- **Use `poll` to wait for async events** — Watch for build completion, server startup, etc.
- **Use `logs` to inspect** — Check what happened in a pane
- **Use `fanout` for parallel work** — Run same command across multiple sessions
- **Use `proc` for process management** — List, kill, and inspect processes instead of raw ps/kill
- **Use `--json` always** — Structured output for reliable parsing
- **Write all files to /tmp** — Any JSON, logs, or other files you generate must go to `/tmp/`. Never write output files into the project directory.

### proc — Process management

List, kill, inspect, and monitor processes. The agent's replacement for Activity Monitor.

```bash
drive proc list --json                                    # All user processes
drive proc list --name claude --json                      # Filter by name
drive proc list --session job-abc123 --json               # Processes in a tmux session
drive proc list --parent 12345 --json                     # Children of a PID
drive proc list --cwd /path/to/project --json             # Processes running from a directory
drive proc kill 12345 --json                              # Kill by PID (SIGTERM → wait → SIGKILL)
drive proc kill --name "claude" --json                    # Kill all matching name
drive proc kill 12345 --tree --json                       # Kill PID and all children
drive proc kill 12345 --force --json                       # Force kill (SIGKILL, no grace period)
drive proc kill 12345 --signal 9 --json                   # Same as --force
drive proc tree 12345 --json                              # Show process tree from PID
drive proc top --session job-abc123 --json                # Resource snapshot for session
drive proc top --pid 12345,12346 --json                   # Resource snapshot for specific PIDs
```

Each process includes `cwd` (working directory) in its JSON output — use this to identify processes spawned from a specific project or directory.

**Kill uses a two-step pattern**: sends the signal (default SIGTERM), waits up to 5 seconds for graceful exit, then SIGKILL if still alive. Use `--tree` to kill a process and all its children (critical for Claude Code which spawns node subprocesses).

#### Process cleanup pattern

During cleanup, `cd` back to your original working directory and use `proc list` to find processes you started that you don't need running anymore. If the task specified they should keep running, leave them alone.

```
1. drive proc list --session job-abc123 --json   → see what's running
2. drive proc kill <pid> --tree --json           → kill it and children
3. drive proc list --name <name> --json          → verify nothing survived
```

## Sentinel Protocol

Drive wraps commands with markers: `echo "__START_<token>" ; <cmd> ; echo "__DONE_<token>:$?"`

This gives:
- Reliable completion detection (no guessing)
- Accurate exit code capture
- Clean output extraction (only content between markers)
