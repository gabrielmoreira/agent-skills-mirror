# Loop Engineer

When the user asks to run an autonomous loop, orchestrate a multi-agent team,
or start a goal-driven task loop, the loop-engineer skill will activate automatically.

The skill is installed at ~/.gemini/skills/loop-engineer/SKILL.md.
Loop state files are stored in loop-stack/<loop-id>/.
Agent definitions are copied to .gemini/agents/ when a loop starts.

## Activation

Semantic matching (automatic): describe a multi-step goal — the skill activates.
Force activation via session command: `/skills enable loop-engineer`
Install (if not yet installed): `gemini skills install https://github.com/vibhasdutta/loop-engineer`

Activation examples:
- "I want to run an autonomous loop to add authentication to my API."
- "Help me orchestrate a multi-agent team to refactor this codebase."
- "Start a loop-engineer session for this project."
- "Run a loop to fix all failing tests."

## How agents work

Agents are defined in .gemini/agents/ with YAML frontmatter (name, description, kind, max_turns, temperature).
The main Gemini session invokes each agent by calling its named tool, waits for completion, then proceeds.
Agents run sequentially — Gemini does not run subagents concurrently.
Agents cannot call other agents; only the main session orchestrates them.

## State files

All loop state lives in loop-stack/<loop-id>/:
- PLAN.md — goal, tasks with [G1]/[G2] parallel group tags, stop condition
- STATUS.md — current state, attempts, last results from each agent
- MEMORY.md — accumulated learnings (grows smarter each iteration)
- TOOLS.md — discovered MCPs, skills, extensions, project tooling
- RESEARCH.md — researcher findings per task
- AGENTS.md — specialized agents created by agent-factory after planning

loop-stack/.global/ — shared across all loops in this project:
- MEMORY.md — cross-loop project learnings
- TOOLS.md — cached tool discovery (7-day TTL)

## Useful commands

- `/memory show` — display all loaded GEMINI.md context files
- `/memory reload` — rescan all GEMINI.md locations after changes
- `/skills list` — show discovered skills
- `/skills reload` — rescan skills after install
- `/agents` — manage subagent configuration
- `/restore` — list checkpoints (if checkpointing is enabled in settings)

## Resume

If a loop is in progress (loop-stack/*/STATUS.md exists, not ending in _DONE),
the skill offers to resume it before starting fresh.

## Import syntax

This GEMINI.md file supports `@file.md` to import content from other files:
@loop-stack/.global/MEMORY.md
