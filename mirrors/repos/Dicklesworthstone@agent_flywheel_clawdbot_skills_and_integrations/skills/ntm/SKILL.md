---
name: ntm
description: >-
  Orchestrates NTM tmux agent swarms and robot APIs. Use when spawning/sending
  panes, robot state, triaging work, locks/mail, safety, pipelines, serve,
  code-first/batch-verify waves, or NTM errors.
---

# NTM

<!-- TOC: Non-Negotiable Rule | Start Here | Action Loop | Action Card | Intent Router | Throughput Doctrine | Pane Targeting | Project Resolution | Automation Rules | Verification Matrix | Failure Handling | Completion | Quick Search | Reference Index | Related Skills -->

NTM is a tmux control plane for multi-agent work. This entrypoint is the
operating kernel. Load one linked reference only when the current action needs
it.

## Non-Negotiable Rule

Discover the live contract, choose the smallest non-interactive surface, act,
then verify on the read surface that owns the resulting state.

Never infer success from command acceptance alone.

## Start Here

1. Read the target repository's `AGENTS.md` and `README.md`.
2. Confirm project/session resolution.
3. Discover only the catalog slice you need:
   ```bash
   ntm --robot-capabilities --capability-compact
   ntm --robot-capabilities --capability-command=send --capability-compact
   ntm --robot-capabilities --capability-search=interrupt --capability-compact
   ```
4. Bootstrap state:
   ```bash
   ntm --robot-snapshot
   ```
5. Name the authoritative postcondition before mutating anything.

For older NTM builds without capability filters, use
`ntm --robot-capabilities` and narrow locally.

## Mandatory Action Loop

```text
DISCOVER -> SNAPSHOT -> SELECT -> SCOPE -> EXECUTE -> VERIFY -> CLEAN UP
```

- **Discover:** Live capability, schema, repo policy, and tool availability.
- **Snapshot:** Session, panes, source health, work, mail, and locks.
- **Select:** Least interactive command with a structured result.
- **Scope:** Exact session, pane references, files, ownership, and blast radius.
- **Execute:** Prefer robot mode for automation.
- **Verify:** Owning state surface plus an independent artifact where useful.
- **Clean up:** Release or hand off locks, claims, pipelines, and sessions.

Re-snapshot after a cursor expiry, degraded-source recovery, or material state
transition.

## Action Card

Before a state change, answer:

```markdown
- Target: <project/session and canonical pane refs>
- Contract: <capability/schema checked>
- Evidence before: <cursor, source health, state>
- Ownership: <bead assignee and file reservations>
- Safety: <user pane inclusion, approvals, blast radius>
- Postcondition: <owning read surface>
- Recovery: <retry, interrupt, smart restart, restore, handoff>
```

If any field is unknown, stay read-only.

## Intent Router

| Intent | First surface | Load |
|---|---|---|
| Install, configure, environment | `ntm deps`, config | [CONFIG](references/CONFIG.md), [ENV-VARS](references/ENV-VARS.md) |
| Spawn/add/adopt agents | `ntm spawn`, `ntm add` | [SPAWN](references/SPAWN.md) |
| Send or batch prompts | `--robot-send` | [SEND](references/SEND.md) |
| Inspect state/output | snapshot, tail, inspect | [ROBOT-MODE](references/ROBOT-MODE.md) |
| Pick and assign work | work triage, assign | [WORK-AND-ASSIGN](references/WORK-AND-ASSIGN.md) |
| Coordinate files/agents | locks, mail, coordinator | [INTEGRATIONS](references/INTEGRATIONS.md) |
| Recover or resume | diagnose, checkpoint, handoff | [TROUBLESHOOTING](references/TROUBLESHOOTING.md), [DURABILITY](references/DURABILITY.md) |
| Run repeatable phases | pipeline | [PIPELINES](references/PIPELINES.md) |
| Run reasoning ensembles | ensemble | [ENSEMBLE](references/ENSEMBLE.md) |
| Operate HTTP/WebSocket API | serve | [SERVE](references/SERVE.md) |
| Review policy/approvals | safety, policy, approve | [SAFETY](references/SAFETY.md) |
| Use human dashboard | dashboard/palette | [DASHBOARD](references/DASHBOARD.md) |
| Find exact CLI syntax | live capabilities first | [COMMANDS](references/COMMANDS.md) |
| Run high-throughput coding waves | beads policy + orchestrator | [CODE-FIRST-BATCH-VERIFY](references/CODE-FIRST-BATCH-VERIFY.md) |

For an already-running multi-pane swarm, use `/vibing-with-ntm` for the tending
loop and return here for exact command contracts.

## Swarm Throughput and Credit Doctrine

When many panes share one repo and one expensive build path, run the
two-phase pump: parallel code-first waves (real code + real tests, syntax
gate max, commit immediately) followed by one central batch-verify pass that
alone closes work with revision-bound evidence.

```text
PHASE 1 (all panes, parallel): claim -> code+tests -> syntax gate -> commit -> batch_pending -> next
        |  trigger: ready-pool dry | debt ceiling | articulation point | scope frontier | time/risk | rate dip
        v
PHASE 2 (orchestrator, once): commit-flush -> ONE verify over git-derived scope
        -> compile errors first -> cluster failures by file -> rework (same assignee)
        -> re-run green -> gate + close with evidence -> dependents unblock -> next wave
```

Full mechanics, tracker policy shape, triggers, and enforcement:
[CODE-FIRST-BATCH-VERIFY](references/CODE-FIRST-BATCH-VERIFY.md).

The pump is only safe on top of honest credit: process artifacts gate named
features or don't exist; refusal-only work never closes a positive-capability
item; closures cite evidence; metrics predeclare denominators. That incentive
layer — including how to encode it into the beads themselves so every swarm
agent sees it at claim time — is the vibing-with-ntm skill's HONEST-CREDIT
reference; its DOCTRINE-BOOTSTRAP reference is the step-by-step setup
(AGENTS.md law, tracker policy, root doctrine bead, AC templates,
enforcement canary). Encode both doctrines in the target repo's `AGENTS.md`
before the first wave.

## Pane Targeting

Use canonical selectors returned by live robot state:

- `%N`: stable tmux pane ID.
- `W.P`: explicit window and pane.
- Bare `N`: pane index in one-window sessions; window index in multi-window
  sessions.

Do not assume the user pane is index 0. Both dispatch surfaces exclude
user-typed panes by default, but their `--all` flags differ: robot `--all`
opts the user pane in, while shell `ntm send --all` broadens to all agent
panes and reaches the user pane only with `--include-user`. Prefer `%N` or
`W.P` for any state-changing single-pane action.

A malformed, missing, or ambiguous selector is a command error, not an empty
successful target set.

## Project Resolution

A session is a project name or `project--label`. The project directory must
resolve to the repository NTM, Beads, and Agent Mail should share. Check
`projects_base`, session labels, and the resolved absolute path before
claiming work or reserving files.

Do not repair resolution by guessing symlinks or moving repositories. Inspect
configuration and follow repo policy.

## Automation Rules

- Avoid `ntm view`, dashboard, palette, and other TUIs in automation.
- Prefer `--robot-*` output; use `--robot-format=toon` and
  `--robot-verbosity=terse` when supported and context is tight.
- Treat `success` as authoritative, then inspect `error_code` and `hint`.
- Exit `0` means success, `1` means command error, and `2` means
  unavailable/`NOT_IMPLEMENTED`.
- Critical arrays must be present as `[]`, never inferred from omission.
- A degraded source is evidence with limits, not permission to invent state.
- Cursors are local to one attention store; checkpoint/handoff artifacts are
  the portable continuity mechanism.

## Spawn and Detached-Session Guardrails

Treat the live capability catalog as the robot-surface count; do not copy a
number into automation guidance:

```bash
ntm --robot-capabilities | jq '.commands | length'
```

`ntm respawn <session>` and `ntm kill <session>` ask for confirmation. An
orchestrator must use `--force` only after its target and blast radius are
explicitly verified; otherwise the command will wait at a prompt and silently
stall automation.

For model-qualified launches, use `N:model:effort` where the agent supports an
effort hint, for example `--cod=2:gpt-5.6-terra:high`. Before using either
qualifier in a custom `[agents]` command, ensure the Go template contains
`{{.Model}}` (or `{{.ModelAlias}}`) and, for effort, `{{.ReasoningEffort}}`.
NTM rejects a requested qualifier that its template would ignore; fix the
template rather than assuming the launch received the setting.

A detached tmux session may begin at 80x24; a wide swarm can leave each pane
too small for agent dialogs and even make dialog detection miss wrapped
options. Before spawning or tending a large detached swarm, size the window:

```bash
tmux resize-window -t <session> -x 420 -y 110
```

Re-check the actual pane geometry after layout changes; this is an operator
environment constraint, not an agent failure.

## Verification Matrix

| Mutation | Required read-back |
|---|---|
| Spawn/add/restart | session status plus pane PID/current command |
| Send/interrupt | target receipt plus fresh pane capture |
| Bead claim/assign/close | native `br show`/ready plus assignment state |
| File reservation | Agent Mail reservation result/conflict list |
| Pipeline run/resume/cancel | pipeline state/run ID |
| Lock acquire/release | lock owner/lease state |
| Checkpoint/handoff | artifact metadata and restore target |
| Safety approval | policy/token state |
| Event-producing action | events/digest/attention cursor movement |

Use git, Beads, process state, or emitted artifacts as independent evidence when
the action is meant to change them.

## Failure Handling

1. Preserve the structured error payload and exit code.
2. Re-read the relevant capability/schema when `INVALID_FLAG` appears; its
   `hint` field now carries a did-you-mean suggestion for near-miss flags.
3. Re-resolve session and pane references for not-found errors.
4. For dependency/source degradation, use the documented fallback once and
   report reduced confidence.
5. For a live agent that appears stuck, diagnose before interrupting or
   restarting.
6. Never loop indefinitely on mail, CASS, Beads, or provider failures.
7. Never use destructive recovery without the repository's explicit approval
   protocol.

## Completion

An NTM action is complete only when:

- the authoritative read surface proves the intended transition;
- target panes, user-pane policy, and ownership are unambiguous;
- downstream git/Beads/mail/pipeline state agrees where applicable;
- any opened lease, reservation, pipeline, or temporary session is released,
  completed, or handed off;
- no required command session is still running.

## Quick Search

Grep the references instead of loading them whole:

```bash
REFS=.claude/skills/ntm/references

# Find the exact flag/command contract
grep -niE "<flag-or-subcommand>" "$REFS"/COMMANDS.md "$REFS"/ROBOT-MODE.md

# Find pump mechanics by keyword
grep -niE "trigger|commit-flush|rework|gate|build-kill|revision" \
  "$REFS"/CODE-FIRST-BATCH-VERIFY.md

# Find closure/claim discipline
grep -niE "actor|close|ready|claim|dep add|cycles" "$REFS"/WORK-AND-ASSIGN.md

# Find recovery for an error string
grep -niE "<error-text>" "$REFS"/TROUBLESHOOTING.md "$REFS"/DURABILITY.md
```

## Reference Index

- [CODE-FIRST-BATCH-VERIFY](references/CODE-FIRST-BATCH-VERIFY.md): two-phase swarm pump
- [COMMANDS](references/COMMANDS.md): command catalog and syntax
- [CONFIG](references/CONFIG.md): configuration and project resolution
- [DASHBOARD](references/DASHBOARD.md): human dashboard behavior
- [DURABILITY](references/DURABILITY.md): checkpoint, restore, handoff
- [ENSEMBLE](references/ENSEMBLE.md): reasoning ensembles
- [ENV-VARS](references/ENV-VARS.md): environment controls
- [INTEGRATIONS](references/INTEGRATIONS.md): Beads, BV, mail, locks, CASS
- [PIPELINES](references/PIPELINES.md): pipeline lifecycle
- [ROBOT-MODE](references/ROBOT-MODE.md): robot envelopes and surfaces
- [SAFETY](references/SAFETY.md): approvals and policy
- [SELF-TEST](references/SELF-TEST.md): validation checks
- [SEND](references/SEND.md): targeting and dispatch
- [SERVE](references/SERVE.md): HTTP/WebSocket API
- [SPAWN](references/SPAWN.md): session and agent creation
- [TROUBLESHOOTING](references/TROUBLESHOOTING.md): diagnosis/recovery
- [WORK-AND-ASSIGN](references/WORK-AND-ASSIGN.md): triage and assignment

## Related Skills

- `/vibing-with-ntm`: tend active swarms
- `/beads-br`, `/beads-bv`: tracker mechanics and graph triage
- `/agent-mail`: coordination primitives
- `/brennerbot-with-ntm`: hypothesis research sessions
- `/open-beads-weighted-tmux-agent-sessions`: backlog-weighted spawning
