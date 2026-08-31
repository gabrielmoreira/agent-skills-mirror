# NTM Skill Self-Test

Trigger phrases and scenarios the NTM skill should activate on, paired with the
first thing the agent should do. Use this to sanity-check that skill
description, triggers, and reference files still cover the real request surface.

## Contents

- [Swarm lifecycle](#swarm-lifecycle)
- [Dispatch / send](#dispatch--send)
- [Coordination and recovery](#coordination-and-recovery)
- [Safety and approvals](#safety-and-approvals)
- [Work intelligence](#work-intelligence)
- [Robot-mode automation](#robot-mode-automation)
- [Durability](#durability)
- [Pipelines and serve](#pipelines-and-serve)
- [Error strings operators actually paste](#error-strings-operators-actually-paste)
- [Non-triggers](#non-triggers) — what should NOT fire this skill

---

## Swarm lifecycle

| Trigger phrase | First action |
|----------------|--------------|
| "Spawn a swarm on `myproject` with 3 Claude and 2 Codex" | `ntm spawn myproject --cc=3 --cod=2` — see SPAWN.md |
| "Launch a mixed agent swarm" | `ntm spawn <session> --cc=N --cod=N --agy=N` |
| "Add another Claude pane to the running swarm" | `ntm add <session> --cc=1` or `ntm scale` |
| "Adopt this existing tmux session into ntm" | `ntm adopt <session>` |
| "Kill the swarm" | `ntm kill <session>` |
| "Remove just pane 3, keep the session" | `ntm kill <session> --pane=3` |
| "Revive the dead panes in place" | `ntm respawn <session>` (`--force` in scripts; `--panes` takes bare indices or `%ID` only) |

## Dispatch / send

| Trigger phrase | First action |
|----------------|--------------|
| "Send marching orders to all Claude panes" | `ntm send <session> --cc "..."` — SEND.md |
| "Broadcast to every pane" | `ntm send <session> --all "..."` (agent panes only; `--include-user` opts the user pane in) |
| "Pair two exact multi-window panes on the broken build" | `ntm send <session> --panes=0.2,%7 "..."` |
| "Send this file's contents as the prompt" | `ntm send <session> --file prompts/X.md` |
| "Distribute ready beads across idle agents" | `ntm send <session> --distribute --dist-strategy=dependency` |

## Coordination and recovery

| Trigger phrase | First action |
|----------------|--------------|
| "Check the agent mail inbox" | `ntm mail inbox <session> --json` |
| "See who holds which file locks" | `ntm locks list <session> --all-agents` |
| "Force-release a stale reservation" | `ntm locks force-release <session> <id> --note "..."` — approval-gated by default: first run files an approval, a second operator runs `ntm approve <id>`, then rerun (SAFETY.md) |
| "Get coordinator digest" | `ntm coordinator digest <session>` |

## Safety and approvals

| Trigger phrase | First action |
|----------------|--------------|
| "Is that command going to be blocked?" | `ntm safety check --json "<cmd>"` — SAFETY.md |
| "Show me what got blocked last 24h" | `ntm safety blocked --hours 24` |
| "Install the safety wrappers and Claude hook" | `ntm safety install` (then `ntm safety status` — `installation_state` must be `effective`, not just `installed_not_effective`) |
| "Show me the policy rules" | `ntm policy show --all` |
| "Approve this pending token" | `ntm approve <token>` (NOT bead id) |
| "Deny approval with reason" | `ntm approve deny <token> --reason "..."` |

## Work intelligence

| Trigger phrase | First action |
|----------------|--------------|
| "What should I work on next" | `ntm work triage` or `ntm work next` — WORK-AND-ASSIGN.md |
| "Triage by label" | `ntm work triage --by-label` |
| "Find beads touching this file" | `ntm work impact <path>` |
| "Assign ready work automatically" | `ntm assign <session> --auto --strategy=dependency` |
| "Pin these beads to codex" | `ntm assign <session> --beads=br-1,br-2 --agent=codex` |
| "The queue is dry / no ready work exists" | `ntm work queue-dry --format=json`, then preview `--ideate` only if dry |
| "Before assigning ten panes, check pressure" | `ntm --robot-agent-health=<session>` + `ntm --robot-rch-status` + `ntm --robot-quota-status` |

## Robot-mode automation

| Trigger phrase | First action |
|----------------|--------------|
| "Bootstrap automation state" | `ntm --robot-snapshot` — ROBOT-MODE.md |
| "Wait until something needs attention" | `ntm --robot-wait=<session> --wait-until=attention` |
| "Wait for the rate limit to clear" | `ntm --robot-wait=<session> --wait-until=rate_limit_lifted --panes=...` |
| "Is pane 2 actively working" | `ntm --robot-is-working=<session> --panes=2` |
| "Smart-restart pane 2 (not brute kill)" | `ntm --robot-smart-restart=<session> --panes=2` |
| "Show me context-window usage per pane" | `ntm --robot-context=<session>` |
| "Tail 50 lines from pane 3 without retiling" | `ntm --robot-tail=<session> --panes=3 --lines=50` |
| "Rotate a rate-limited Claude pane" | inspect quota + `ntm rotate status --json`; only in a proven one-window session preview `ntm rotate <session> --pane=N --dry-run`, then require operator review |
| "Does this robot flag still exist" | `ntm --robot-capabilities | jq '.commands[] | select(.flag=="--robot-...")'` |

## Durability

| Trigger phrase | First action |
|----------------|--------------|
| "Snapshot the whole session before this refactor" | `ntm checkpoint save <session> -m "..."` — DURABILITY.md |
| "Roll everything back" | `ntm checkpoint restore <session> last` or `ntm rollback` |
| "Write a handoff for another operator" | `ntm handoff create <session>` |
| "Move this session to another machine" | `ntm checkpoint export` + `checkpoint import` |
| "Resume after a crash" | `ntm resume <session>` |
| "What happened during this session" | `ntm timeline show <session-id>` |

## Pipelines and serve

| Trigger phrase | First action |
|----------------|--------------|
| "Run the review pipeline" | `ntm pipeline run .ntm/pipelines/<file>.yaml --session <s>` — PIPELINES.md |
| "Status of that pipeline run" | `ntm pipeline status <run-id>` |
| "Start the local NTM API server" | `ntm serve --port 7337` — SERVE.md |
| "Headless pipeline from a script" | `ntm --robot-pipeline-run=<file> --session=<s>` (`--pipeline-session` is a deprecated alias) |
| "Run the red-green workflow against live panes" | `ntm workflow run red-green` (v1.25+ executes the coordination loop; `ntm spawn -t` only sizes a session) |

## Error strings operators actually paste

These should all route to TROUBLESHOOTING.md via the index table:

- `project not found`
- `CASS detected identical message`
- `Continue anyway? [y/N]`
- `zsh: command not found` (after `send --all`)
- `reservation_conflict`
- `CURSOR_EXPIRED`
- `unknown flag: --mail-project=`
- `ntm: unknown command: timeline` (old binaries)
- `rate_limited` / "resets 3pm"
- `PANE_AGENT_DEAD`
- `Aborted.` with exit 0 from a scripted `ntm respawn`
- `project name %q contains '--'`

## Non-triggers

These look NTM-ish but belong to companion skills:

- **"How do I tend a stuck swarm / unstick ladder / orchestrator loop"** → `vibing-with-ntm`
- **"Bead creation / dep graph / dependency resolution"** → `br` + `beads-workflow`
- **"Agent-mail reservation handshake"** → `agent-mail`
- **"Rotate which Claude account is active globally"** → `caam` (ntm's `--robot-switch-account` wraps it for sessions)
- **"Block this destructive command system-wide"** → `dcg`
- **"Two-person launch button"** → `slb`
