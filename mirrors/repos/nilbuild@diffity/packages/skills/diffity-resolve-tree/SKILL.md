---
name: diffity-resolve-tree
description: Read open comments from the tree browser and resolve them by making code fixes
user-invocable: true
---

# Diffity Resolve Tree Skill

You are reading open comments left on repository files via the `diffity tree` browser and resolving them by making the requested code changes.

## Arguments

- `thread-id` (optional): Resolve a specific thread by ID instead of all open threads. Example: `/diffity-resolve-tree abc123`

## CLI Reference

```
{{binary}} agent list [--status open|resolved|dismissed] [--json]
{{binary}} agent comment --file <path> --line <n> [--end-line <n>] --body "<text>"
{{binary}} agent resolve <id> [--summary "<text>"]
{{binary}} agent dismiss <id> [--reason "<text>"]
{{binary}} agent reply <id> --body "<text>"
```

- `--file`, `--line`, `--body` are required for `comment`
- `--end-line` defaults to `--line` (single-line comment)
- `<id>` accepts full UUID or 8-char prefix

## Prerequisites

1. Check that `{{binary}}` is available: run `which {{binary}}`. If not found, {{install_hint}}.
2. Check that a tree session exists: run `{{binary}} agent list`. If this fails with "No active review session", tell the user to start diffity tree first (e.g. `{{binary}} tree`).

## Instructions

1. List open comment threads with full details:
   ```
   {{binary}} agent list --status open --json
   ```
   If a `thread-id` argument was provided, filter to just that thread. The JSON output includes the full comment body, file path, line numbers, and side for each thread.
2. If there are no open threads, tell the user there's nothing to resolve.
3. For each open thread:
   a. **Skip** general comments (filePath `__general__`) — these are summaries, not actionable code changes.
   b. **Skip** threads where the last comment is an agent reply that asks the user a question and the user hasn't responded yet — the agent is waiting for user input.
   c. **`[question]` comments** (from the user) — read the question, examine the relevant code, and reply with an answer:
      ```
      {{binary}} agent reply <thread-id> --body "Your answer here"
      ```
      Then resolve the thread with a summary of your answer.
   d. Comments phrased as questions without an explicit `[question]` tag (e.g. "should we add X?" or "can we rename this?") are suggestions — treat them as actionable requests and make the change.
   e. Read the comment body from the JSON output and understand what change is requested. The comment is anchored to a specific file and line range — read the full file to understand context:
      - If the comment suggests a code change, refactor, or improvement, make the change.
      - If the comment suggests adding documentation, add or update the relevant docs.
      - If the comment is genuinely unclear, reply asking for clarification:
        ```
        {{binary}} agent reply <thread-id> --body "Could you clarify what change you'd like here?"
        ```
   f. After making the change, resolve the thread with a summary:
      ```
      {{binary}} agent resolve <thread-id> --summary "Fixed: <brief description of what was changed>"
      ```
4. After resolving all applicable threads, run `{{binary}} agent list` to confirm status.
5. Tell the user to check the browser — resolved status will appear within 2 seconds via polling.
