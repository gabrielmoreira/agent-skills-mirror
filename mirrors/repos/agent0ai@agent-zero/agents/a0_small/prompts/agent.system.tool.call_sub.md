### call_subordinate
delegate research or complex subtasks to a specialized agent.
args: `message`, optional `profile`, `reset`
- `profile`: use `researcher` for all research or web gathering; `developer` for coding; `hacker` for exploration.
- `reset`: `true` for first message or when changing profile; `false` to continue.
- `message`: define role, goal and specific task.
{{if agent_profiles}}
profiles:
{{agent_profiles}}
{{endif}}
example: `{"tool_name": "call_subordinate", "tool_args": {"profile": "researcher", "message": "Research Italy AI trends...", "reset": true}}`
