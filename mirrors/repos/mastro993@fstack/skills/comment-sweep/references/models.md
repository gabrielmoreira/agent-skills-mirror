# Scout models

Scouts only read files and list what they find, so they run on the cheapest fast model your harness offers. Tell which harness you are in from your own subagent tool, then use its row.

Last checked 2026-11-14. Model names go stale quickly: to update the map, edit that harness's row, or add a row for a new harness.

| Harness | Subagent tool | How to spawn a scout | Cheap model |
|---|---|---|---|
| Claude Code | `Agent` | `subagent_type: "general-purpose"`, `model: "haiku"` | `haiku` |
| Codex | `spawn_agent` | `model: "gpt-6-luna"`, `reasoning_effort: "low"`, when the tool takes them | `gpt-6-luna` |
| Copilot CLI | `task` | the built-in `task` agent, which already runs on a cheap model | built-in |
| VS Code Copilot | `runSubagent` | pass `model`; VS Code refuses a model that costs more than yours | `claude-haiku-5.5` or `gpt-6-luna` |
| oh-my-pi | `task` | the `scout` agent, or `model: "@smol"` when per-call models are on | `@smol` |
| OpenCode | `task` or `subagent` | `model: "<provider>/<cheap model>"` on builds that take it | the provider's smallest model |
| Cursor | `Task` | name the model in the call | Claude Haiku 5.5 or `composer-2.5` |
| Gemini CLI | `invoke_agent` | `agent_name: "codebase_investigator"`, which runs on Flash | built-in |
| Pi | none built in | the subagent extension's `scout` agent, if installed | the agent file's `model` |

When the row doesn't fit:

- **The tool won't take a model.** Use a built-in agent that already runs on a cheap model. If there isn't one, use the default subagent: it costs more, and still keeps the files out of your context.
- **The model in the row isn't offered.** Pick the smallest fast model the harness does list: a Haiku, a mini or nano model, a Flash, or a Luna.
- **Your harness isn't in the table.** Use the same rules, then add its row.
- **No subagents at all.** Take the inventory yourself, batch by batch.

Whatever you pick costs at most what your own model does.
