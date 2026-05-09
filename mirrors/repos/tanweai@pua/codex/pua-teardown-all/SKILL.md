---
name: pua-teardown-all
description: "PUA teardown alias for Codex. Codex subcommand mapping for Claude Code /pua:teardown-all style usage; invoke with $pua-teardown-all."
license: MIT
---

# pua-teardown-all

This is a Codex CLI alias for the Claude Code `/pua:teardown-all` command.

Release all active PUA agent state and loop state according to the teardown protocol. Explain destructive cleanup before deleting files.

When this alias changes `~/.pua/config.json`, preserve unknown fields and create `~/.pua/` if missing. Do not claim completion without command/output evidence.
