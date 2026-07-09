# Loop Engineer

When the user asks to run an autonomous loop, orchestrate a multi-agent team,
or start a goal-driven task loop, the loop-engineer skill will activate.

The skill is installed at ~/.config/opencode/skills/loop-engineer/SKILL.md
(also auto-discovered from ~/.claude/skills/loop-engineer/ if Claude is installed).
Loop state files are stored in loop-stack/<loop-id>/.
Agent definitions are copied to .opencode/agents/ when a loop starts.

## Activation

Type `/loop-engineer` to start (custom command installed to ~/.config/opencode/commands/).
Or describe a multi-step goal — the skill tool will activate via semantic matching.
Manual skill load: use the `skill` tool with name "loop-engineer".

## How agents work

Agents are defined in .opencode/agents/ as markdown files with YAML frontmatter
(name, description, mode: subagent, steps, temperature, permission).
The main OpenCode session invokes each agent via the `task` tool, waits for completion,
then proceeds. Agents run sequentially — one at a time.
Agents cannot invoke other agents (OpenCode subagent constraint).

## State files

All loop state lives in loop-stack/<loop-id>/:
- PLAN.md — goal, tasks with [G1]/[G2] parallel group tags, stop condition
- STATUS.md — current state, attempts, last results from each agent
- MEMORY.md — accumulated learnings (grows smarter each iteration)
- TOOLS.md — discovered MCPs, skills, project tooling
- RESEARCH.md — researcher findings per task
- AGENTS.md — specialized agents created by agent-factory after planning

loop-stack/.global/ — shared across all loops in this project:
- MEMORY.md — cross-loop project learnings
- TOOLS.md — cached tool discovery (7-day TTL)

## Configuration

MCP servers: configure in opencode.json under "mcp" key.
Agents: .opencode/agents/*.md
Commands: .opencode/commands/*.md
Global skills: ~/.config/opencode/skills/
Claude-compat skills: ~/.claude/skills/ (also loaded by OpenCode)

## Resume

If a loop is in progress (loop-stack/*/STATUS.md exists, not ending in _DONE),
the skill offers to resume it before starting fresh.
