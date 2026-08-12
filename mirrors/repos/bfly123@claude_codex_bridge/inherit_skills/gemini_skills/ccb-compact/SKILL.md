---
name: ccb-compact
description: Compact CCB managed agent conversation context with `ccb compact`. Use when the user writes `$ccb-compact`, `$ccb_compact`, or asks to summarize one or more mounted agent contexts without restarting agents or deleting project state.
metadata:
  short-description: Compact CCB agent context
---

# CCB Compact

Use this skill to request provider-native context compaction for mounted CCB agents.

Commands:

```bash
command ccb compact
```

```bash
command ccb compact "$AGENT"
```

```bash
command ccb compact agent1 agent2
```

Rules:

- A bare command targets all configured mounted agents; named commands target only those agents.
- Busy or queued agents are blocked before any pane input is sent.
- The command sends each provider's native compaction command and reports `unsupported` when no verified command exists.
- It does not delete `.ccb` state, workspaces, auth, sessions, logs, or memory files.
- Run once, report the command output, and stop. Do not poll or substitute `ccb clear`, restart, or kill.
