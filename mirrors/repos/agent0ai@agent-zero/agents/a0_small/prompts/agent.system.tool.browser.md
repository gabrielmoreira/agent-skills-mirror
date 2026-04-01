### browser_agent
subordinate browser worker for web tasks
args: `message`, `reset`
- give clear task-oriented instructions credentials and a stop condition
- `reset=true` starts a new browser session; `false` continues the current one
- when continuing, refer to open pages instead of restarting
downloads go to `/a0/tmp/downloads`
