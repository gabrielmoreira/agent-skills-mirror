# Loop Engineer

This workspace uses loop-engineer for autonomous multi-agent task execution.

## How to run a loop

1. Open GitHub Copilot Chat
2. Switch to **Agent mode** (select "Agent" in the mode dropdown — required for file and terminal access)
3. Attach `.github/prompts/loop-engineer.prompt.md` by typing `#loop-engineer.prompt` or using the paperclip button
4. Describe your goal — the wizard asks 3 quick questions (mode, goal, git) then runs fully autonomously. No resume support — every run is a fresh loop, even if `loop-stack/` contains a prior `*_DONE/` directory.

## Key files

- `.github/prompts/loop-engineer.prompt.md` — the skill (attach this in Copilot Chat to activate)
- `.github/agents/loop-engineer-*.agent.md` — the 8 agent roles (researcher, executor, verifier, auditor, memory-keeper, planner, agent-factory, resource-scout), prefixed to avoid colliding with any other custom agents you have
- `.github/loop-engineer-knowledge/` — research reference material (not agents — kept out of `.github/agents/` since VS Code treats any `.md` file there as a custom agent)
- `loop-stack/` — loop state (PLAN.md, STATUS.md, MEMORY.md, etc.)
- `.vscode/mcp.json` — MCP server config (resource-scout checks this for available tools)

## Parallel execution

This loop dispatches subagents in true parallel (confirmed: code.visualstudio.com/docs/agents/subagents) — batches of researchers, executors, verifiers, and auditors all run concurrently, not one at a time.
