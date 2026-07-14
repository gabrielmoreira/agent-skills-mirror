---
name: ccb-clear
description: Clear conversation context for one or more mounted CCB agents using ccb clear. Use when the user invokes /ccb-clear, $ccb-clear, or $ccb_clear, or asks Grok to clear or reset CCB agent context without restarting agents or deleting project state.
---

# CCB Clear

Use this skill to clear provider conversation context for mounted CCB agents.

In the CCB source checkout, installed `ccb` is only for the active work
environment. Source validation uses `/home/bfly/yunwei/ccb_source/ccb_test`
from `/home/bfly/yunwei/test_ccb2` unless another external root is explicitly
allowed.

For a bare skill invocation or an explicit all-agents request:

```bash
command ccb clear
```

For named agents, pass only the requested names as separate quoted arguments:

```bash
command ccb clear "$AGENT"
```

```bash
command ccb clear agent1 agent2
```

Rules:

- Bare `/ccb-clear`, `$ccb-clear`, and `$ccb_clear` target all configured agents.
- Named requests target only the named agents.
- For ambiguous natural-language scope, ask which agents to clear instead of clearing all.
- This sends provider-native clear input to mounted target panes.
- It does not delete `.ccb`, auth, sessions, logs, workspaces, or memory files.
- Never substitute `ccb kill`, `ccb -n`, restart, direct tmux input, or file deletion.
- Run once, report the command output, then stop. Do not poll.
- If terminal permission is denied or cancelled, report that no clear was performed.
  Do not change Grok permission settings.
