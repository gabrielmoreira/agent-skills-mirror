---
name: pua-flavor
description: "PUA flavor alias for Codex. Codex subcommand mapping for Claude Code /pua:flavor style usage; invoke with $pua-flavor."
license: MIT
---

# pua-flavor

This is a Codex CLI alias for the Claude Code `/pua:flavor` command.

Read the flavor reference and help the user choose/set a flavor in ~/.pua/config.json without overwriting unrelated fields.

When this alias changes `~/.pua/config.json`, preserve unknown fields and create `~/.pua/` if missing. Do not claim completion without command/output evidence.
