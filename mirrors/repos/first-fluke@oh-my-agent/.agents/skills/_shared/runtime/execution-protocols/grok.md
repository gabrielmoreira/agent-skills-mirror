# Execution Protocol (Grok)

When running as a Grok subagent or custom agent, follow this protocol for shared state coordination with oh-my-agent.

## State Management

Use file-based I/O for coordination. Write results to `.agents/results/`.

Grok has good native support for project files and can use terminal commands for coordination.

### Path Resolution (CRITICAL)

All result, progress, and state files MUST be written to the **project root** `.agents/` directory.

- **Project root** = the git repository root (where `.git` exists)
- **Session-scoped naming**: when running under an orchestration session, append session ID as suffix:
  - `result-{agent-id}-{sessionId}.md`
- **Manual runs**: `result-{agent-id}.md`

## On Start

1. Read the assigned task context (from orchestration or user prompt).
2. Create progress tracking if needed under `.agents/results/`.

## During Execution

- Use clear, structured output.
- Prefer editing existing files over creating new documentation unless requested.
- When done, write a clear summary to the designated result file.

## Grok-Specific Notes

- Leverage Grok's strong code understanding and search capabilities.
- Use `run_terminal_cmd` for shell operations.
- Subagent spawning via the `task` tool when appropriate.
- Follow any `agents_md` or project instructions loaded in the agent definition.