---
name: ask
description: Send a request to a CCB agent with `ask`.
metadata:
  short-description: Ask agent
---

Use this skill when the user writes `$ask <target> <message...>`.

- `TARGET` = first token; `MESSAGE` = raw remainder, forwarded verbatim.
- `TARGET=all` broadcasts.
- Plain `ask` injects concise-reply guidance while still delivering the full reply body.
- Use `--compact` when the caller wants an actively distilled answer, such as review findings, status, risks, blockers, or next actions.
- Use `--silence` when success does not need a body; failures, blockers, or required next actions should still surface.
- Do not manually append output-policy text; `ask` injects reply guidance.

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

After submit, return the command output and stop.
