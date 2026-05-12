---
name: ask
description: Send a request to a CCB agent with `ask`.
metadata:
  short-description: Ask agent
---

Use this only for `/ask <target> <message...>`.

- `TARGET` = first token after `/ask`.
- `MESSAGE` = exact raw remainder; forward verbatim.
- `TARGET=all` broadcasts.

```bash
command ask "$TARGET" <<'EOF'
$MESSAGE
EOF
```

After submit, return the command output and stop.
