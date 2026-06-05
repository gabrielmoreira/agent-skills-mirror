---
name: ask
description: Send a request to a CCB agent with `ask`.
metadata:
  short-description: Ask agent
---

Use this when the user asks you to delegate with CCB, or when project memory
says to use CCB `ask` for collaboration.

## Choose The Mode First

- Normal user turn, direct chat request, release handoff, review handoff, or any
  context that is not a CCB-delivered active parent job: use plain `ask`.
- Do not probe `--callback`. If you are unsure whether there is an active parent
  job, there is not one; use plain `ask`.
- Use `--callback` only when this exact turn is an active CCB task and the child
  result is required before you can finish that parent task. After callback
  submit, stop; CCB will deliver the child result as a continuation.
- If CCB says `ask --callback requires an active parent job`, the mode choice was
  wrong. For a user-requested delegation, submit once with plain `ask` and stop.
- Use `--silence` only for independent work where success does not need a reply
  body. Failures, blockers, or required next actions should still surface.
- Use `--compact` when the caller wants distilled findings, status, risks,
  blockers, or next actions.
- Use `--artifact-request` when the task body is large or must be passed by file.
  CCB stores the request in a text artifact and sends the target only a file
  reference.
- Use `--artifact-reply` when the caller or callback continuation should receive
  the target result as a text artifact path, even if the target replies inline.
- Use `--artifact-io` when both the request and reply should be artifact-backed.
- `--artifact-*` modes are CCB/daemon managed; they do not require the target
  agent to manually write a reply file.

## Command Rules

- `TARGET` = first token; `MESSAGE` = raw remainder sent as the task body.
- `TARGET=all` broadcasts.
- Plain `ask` injects concise-reply guidance while still delivering the full
  reply body.
- `ask` may append reply guidance unless the message already contains explicit
  output requirements.
- Plain nested `ask` from an active CCB task is rejected; choose `--callback` for
  needed dependency results or `--silence` for independent no-result-needed work.
- Do not manually append output-policy text; `ask` injects reply guidance.
- `ask get`, `pend`, `watch`, and `ping` are diagnostics-only commands for explicit debugging requests, not normal ask workflow tools.
- For callback work with a large child result, combine `--callback` with
  `--artifact-reply`.

Always send `MESSAGE` through the `<<'EOF' ... EOF` heredoc below. No other form is allowed.

```bash
command ask "$TARGET" <<'EOF'
$MESSAGE
EOF
```

```bash
command ask --compact "$TARGET" <<'EOF'
$MESSAGE
EOF
```

```bash
command ask --silence "$TARGET" <<'EOF'
$MESSAGE
EOF
```

```bash
command ask --callback "$TARGET" <<'EOF'
$MESSAGE
EOF
```

```bash
command ask --artifact-io "$TARGET" <<'EOF'
$MESSAGE
EOF
```

```bash
command ask --callback --artifact-reply "$TARGET" <<'EOF'
$MESSAGE
EOF
```

After the command returns, immediately end the turn. Do not wait for a reply, do not run `ask get` / `pend` / `ping` / `watch`, do not poll, do not add
commentary. For `--callback`, report only that delegation was submitted; the final result belongs in the later continuation task.
