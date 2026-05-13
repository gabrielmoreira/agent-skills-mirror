---
name: ask
description: Send a request to a CCB agent with `ask`.
metadata:
  short-description: Ask agent
---

Use this only for `/ask <target> <message...>`.

- `TARGET` = first token; `MESSAGE` = raw remainder, forwarded verbatim.
- `TARGET=all` broadcasts.

Always send `MESSAGE` through the `<<'EOF' ... EOF` heredoc below. No other form is allowed.

```bash
command ask "$TARGET" <<'EOF'
$MESSAGE
EOF
```

After the command returns, immediately end the turn. Do not wait for a reply, do not run `pend` / `ping` / `watch`, do not poll, do not add commentary.
