---
name: ccb-clear
description: Clear CCB managed agent conversation context with `ccb clear`. Use for `/ccb-clear`, `$ccb-clear`, `$ccb_clear`, or requests to reset one or more CCB agent contexts without deleting project state.
---

# CCB Clear

Run exactly one matching command:

```bash
command ccb clear
```

```bash
command ccb clear "$AGENT"
```

```bash
command ccb clear agent1 agent2
```

The bare command targets all configured agents. Named commands target only the
requested agents. Report the command output and stop. Do not substitute
`ccb kill`, restart agents, delete files, or poll.
