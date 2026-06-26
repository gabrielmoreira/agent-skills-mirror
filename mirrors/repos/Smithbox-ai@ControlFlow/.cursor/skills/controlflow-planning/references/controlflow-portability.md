# ControlFlow Portability Notes

Keep these pieces from ControlFlow:

- phased planning
- semantic risk review
- complexity tiers
- artifact-first thinking
- explicit validation and rollback notes

Adapt these pieces for Codex instead of copying them literally:

- fixed agent rosters
- VS Code-specific tool names such as `vscode/askQuestions`
- P.A.R.T section contracts
- schema-driven chat outputs
- assumptions about always-available subagent dispatch

Codex-friendly replacements:

- use repo files and Markdown artifacts instead of schema-shaped chat payloads
- use `update_plan` for live state tracking
- use local shell inspection before asking questions
- use `spawn_agent` only when delegation is both available and desired by the user
- use concise progress updates instead of orchestration event logs
