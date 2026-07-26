---
name: reconnect
description: Enable or disable tmux-bound disconnect recovery for the current Codex thread. Use only for the explicit invocations `$reconnect on` or `$reconnect off` inside a CCB-managed or ordinary tmux Codex CLI.
---

# Reconnect

Execute exactly one command for the matching invocation:

- `$reconnect on` → run `command codex-reconnect on`.
- `$reconnect off` → run `command codex-reconnect off`.

Relay the command result concisely. If it fails, report the error and do not claim recovery is enabled.
For any other argument, reply with the exact usage: `$reconnect on` or `$reconnect off`.

Do not change files, start a goal, run other tools, or claim coverage for quota, billing,
authentication, policy, context-window, approval, or ordinary task-completion failures.
