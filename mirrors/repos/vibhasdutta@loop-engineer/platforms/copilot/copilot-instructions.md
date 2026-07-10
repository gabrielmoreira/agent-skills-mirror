# Loop Engineer

This workspace uses loop-engineer for autonomous multi-agent task execution.

## How to run a loop

1. Open GitHub Copilot Chat
2. Switch to **Agent mode** (select "Agent" in the mode dropdown — required for file and terminal access)
3. Attach `.github/prompts/loop-engineer.prompt.md` by typing `#loop-engineer.prompt` or using the paperclip button
4. Describe your goal — the wizard asks 2 quick questions then runs fully autonomously

## How to resume a loop

If `loop-stack/` contains an in-progress loop, attach the prompt file and say "continue" — the loop resumes from exactly where it stopped without re-running the startup sequence.

## After a completed loop

If `loop-stack/*_DONE/` exists and you want to follow up on those findings, attach the prompt file and say "continue doing the fixes from the audit" (or similar). The wizard reads the prior REPORT.md and starts a follow-on loop pre-loaded with those findings.

## Key files

- `.github/prompts/loop-engineer.prompt.md` — the skill (attach this in Copilot Chat to activate)
- `.github/agents/loop-engineer-*.agent.md` — the 8 agent roles (researcher, executor, verifier, auditor, memory-keeper, planner, agent-factory, resource-scout), prefixed to avoid colliding with any other custom agents you have
- `.github/loop-engineer-knowledge/` — research reference material (not agents — kept out of `.github/agents/` since VS Code treats any `.md` file there as a custom agent)
- `loop-stack/` — loop state (PLAN.md, STATUS.md, MEMORY.md, etc.)
- `.vscode/mcp.json` — MCP server config (resource-scout checks this for available tools)

## Parallel execution

This loop dispatches subagents in true parallel (confirmed: code.visualstudio.com/docs/agents/subagents) — batches of researchers, executors, verifiers, and auditors all run concurrently, not one at a time.
