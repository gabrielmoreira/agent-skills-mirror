---
name: ask
description: Send a request to a CCB agent with `ask`.
metadata:
  short-description: Ask agent
---

Use this skill when the user writes `$ask <target> <message...>`.

- `TARGET` = first token; `MESSAGE` = raw remainder, forwarded verbatim.
- `TARGET=all` broadcasts.

```bash
command ask "$TARGET" <<'EOF'
$MESSAGE
EOF
```

After submit, return the command output and stop.
