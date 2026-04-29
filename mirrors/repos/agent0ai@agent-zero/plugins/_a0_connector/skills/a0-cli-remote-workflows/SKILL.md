---
name: a0-cli-remote-workflows
description: Guide safe use of A0 CLI remote shell execution and remote file editing on the connected host machine. Load before using code_execution_remote or text_editor_remote for local project work through the CLI connector.
version: 1.0.0
author: Agent Zero Team
tags: ["agent-zero", "a0", "cli", "connector", "remote-execution", "remote-files"]
trigger_patterns:
  - "code_execution_remote"
  - "text_editor_remote"
  - "remote file editing"
  - "remote shell execution"
  - "edit my local files through a0 cli"
  - "run commands on the cli host"
allowed_tools:
  - code_execution_remote
  - text_editor_remote
---

# A0 CLI Remote Workflows

## Boundary

Use `code_execution_remote` and `text_editor_remote` only for work on the machine where A0 CLI is running. These paths, shells, runtimes, and files belong to the CLI host, not the Agent Zero server or Docker container.

If the task belongs inside Agent Zero's own runtime, use the normal server-side tools instead.

## Access Modes

- Read only: inspect files and poll/reset existing execution sessions. Do not attempt writes or mutating shell work until the user switches the CLI to Read&Write with F3.
- Read&Write: shell-backed execution, writes, and patches may modify the CLI host. Keep changes narrow and intentional.
- Execution may also be disabled locally in the CLI. If a remote tool returns a structured disabled/no-client error, explain the required CLI toggle instead of falling back to the server filesystem.

## Remote Execution

- Use `runtime=terminal` for shell commands, `runtime=python` for Python snippets, and `runtime=nodejs` for Node.js snippets.
- Reuse the same integer `session` while continuing a workflow; session state is local to the CLI frontend.
- Use `runtime=output` when a previous command is still running or returned before the shell reached a prompt.
- Use `runtime=reset` when a session is stuck or a clean shell is safer.
- Treat `runtime=input` as deprecated compatibility for sending one line to a running shell.
- Match the remote host shell syntax. A Windows CLI may need PowerShell syntax even when Agent Zero runs on Linux.

## Remote File Editing

- Start with `read` when inspecting a file or preparing line-based edits.
- Use `write` only when replacing or creating the whole file is truly the right operation.
- Prefer `patch` with `patch_text` for context-anchored edits, especially after inserts/deletes or when line numbers may have shifted.
- Use `patch` with `edits` only for small line-range edits based on the latest remote read.
- If freshness-aware line patching rejects an edit as stale, reread the file and retry with updated ranges.

## Patch Text Rules

- `patch_text` supports update hunks for one file.
- Use one `@@ existing line` anchor, then `+new line` entries for insertion.
- For replacement, use `@@ before target` followed by `-old` and `+new`, or use `@@ old target` followed by the same replacement pair.
- Do not repeat the same old line as both context and deletion in one hunk.
- Every non-header content line must begin with exactly one prefix: space for context, `+` for additions, or `-` for removals.
- Do not stack multiple `@@` anchors for one insert.

## Failure Handling

- If no CLI is connected or subscribed, ask the user to connect A0 CLI to this chat.
- If writes are blocked, tell the user to switch local access to Read&Write with F3.
- If execution is disabled, tell the user to enable remote execution in the CLI.
- If a request times out or the CLI disconnects, poll once if a session may still be running; otherwise summarize the failure and wait for reconnection.
