---
name: PDS Depth-Priority Hierarchical-Instruct pointer
alwaysApply: true
globs:
  - "**/*"
---

# Continue compatibility — rules pointer

> Continue reads rule files from `.continue/rules/*.md`. This project's authoritative rules live in [`.hi/`](../../.hi/) and per-directory `.hi/instruct.md` files. The files in this directory are pointers — they tell Continue where to look so its agent behaves the same way GitHub Copilot does in this repo.

## Project rules location

> ⛔ **STOP. This file holds no rules.** It is a thin pointer to the single master reference. Do not duplicate rules here.

**→ [`.hi/instruct.md`](../../.hi/instruct.md) is the single authoritative master.**

Before suggesting any change, read and obey its **[⛔ Mandatory Reading Contract](../../.hi/instruct.md#-stop--mandatory-reading-contract-non-negotiable)**. That contract is the *only* place that defines the mandatory reading order, the cross-cutting canonical map, the depth-priority rule (**the deepest `.hi/instruct.md` always wins**), and the governed import/merge guard.

Do not invent a new `.continue/rules/*.md` file with project rules in it — those rules belong in the appropriate `.hi/` file.

## MCP server

Continue does not auto-discover MCP servers from a workspace file. To enable the project's [`hia-instruct`](../../.hi/mcp/README.md) server, add this block to your `~/.continue/config.json` once:

```jsonc
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "hia_mcp"],
          "env": { "PDS_WORKSPACE": "<absolute path to this workspace>" }
        }
      }
    ]
  }
}
```

Install once per clone: `cd .hi/mcp/python && pip install -e .` (or use the Node twin).
