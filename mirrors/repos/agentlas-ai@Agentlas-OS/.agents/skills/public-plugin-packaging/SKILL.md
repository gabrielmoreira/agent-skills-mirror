---
name: public-plugin-packaging
description: "Use when packaging an Agentlas agent repo for public GitHub release, Codex plugin submission, Claude adapter distribution, or one-line terminal installation."
---

# Public Plugin Packaging

## Procedure

1. Separate public operating-system files from private hosted service code.
2. Include `README.md`, `LICENSE`, `SECURITY.md`, `AGENTS.md`, `agents/`,
   `skills/`, `.agentlas/global-commands.json`, schemas, templates, install
   scripts, runtime command files, and verification.
3. Keep private research, credentials, raw logs, and local paths out of the
   package.
4. Run `scripts/public_safety_check.sh`.
5. Run runtime-specific plugin validation when available.

## Output

Return release surface, install command, global_commands, validation commands,
and blockers.
