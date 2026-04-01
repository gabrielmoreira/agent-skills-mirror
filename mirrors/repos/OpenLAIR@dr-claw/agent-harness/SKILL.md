---
name: drclaw
description: Dr. Claw workspace skill for project lookup, session inspection, TaskMaster progress, and OpenClaw reporting
---

# Dr. Claw Research Skill

Use this skill when the user asks about Dr. Claw projects, wants to inspect Claude/Cursor/Codex/Gemini sessions, or needs task progress pushed to OpenClaw/mobile.

## Setup check

Before using Dr. Claw, verify the server is reachable:

```bash
drclaw server status
```

If needed, start it:

```bash
drclaw server on
```

## Project discovery

```bash
drclaw --json projects list
```

Project references accepted by the CLI:

- `name`
- `displayName`
- filesystem `path` / `fullPath`

If a path exists locally but is not registered yet:

```bash
drclaw projects add /absolute/path/to/project --name "Display Name"
```

## Session workflows

List sessions:

```bash
drclaw --json sessions list <project-ref>
drclaw --json sessions list <project-ref> --provider cursor
```

Fetch messages:

```bash
drclaw --json sessions messages <project-ref> <session-id> --provider claude --limit 100
```

Send Claude a message:

```bash
drclaw --json chat send --project <project-ref> --message "<user message>"
```

List active sessions across projects:

```bash
drclaw --json chat sessions
```

## TaskMaster workflows

Check whether TaskMaster is present:

```bash
drclaw --json taskmaster detect <project-ref>
```

Get progress and next action:

```bash
drclaw --json taskmaster summary <project-ref>
drclaw --json taskmaster next-guidance <project-ref>
```

Initialize `.pipeline` for a project if needed:

```bash
drclaw taskmaster init <project-ref>
```

## OpenClaw / mobile reporting

Configure the default push channel once:

```bash
drclaw openclaw configure --push-channel feishu:<chat_id>
```

Preview a mobile report:

```bash
drclaw --json openclaw report --project <project-ref> --dry-run
```

Send it:

```bash
drclaw openclaw report --project <project-ref>
```

## Recommended operating flow

1. If the user did not specify a project, run `projects list` and resolve the project first.
2. For freeform project questions, use `chat send`.
3. For status/progress questions, prefer `taskmaster summary` and `taskmaster next-guidance`.
4. For proactive mobile updates, use `openclaw report`.
