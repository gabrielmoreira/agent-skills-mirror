# Autonomous Safety Guardrails

**Status**: Scaffold, opt-in
**Authority**: This file is **read at every heartbeat** by [`orchestrator.md`](orchestrator.md). Drift here = halt.

> The autonomous layer adds **zero** new permissions. It composes the **strictest** of:
> - this file,
> - [`autonomy-config.yaml`](autonomy-config.yaml) `safety:` block,
> - [`.ai/agent-config.yaml`](../agent-config.yaml) safety contract,
> - the resolved `scope_authority_file` (depth-priority winner).
>
> When two rules conflict, **the stricter rule wins**. The orchestrator never picks the looser interpretation.

---

## Contents

| Section | Purpose |
|---|---|
| [Inherited Contracts](#inherited-contracts) | What we already enforce, do not restate |
| [Stop Conditions](#stop-conditions) | Every condition that halts a run |
| [Forbidden Actions](#forbidden-actions) | Hard nos, regardless of approval |
| [Approval Gates](#approval-gates) | When humans must say yes |
| [Sanitisation Rules](#sanitisation-rules) | What is stripped from prompts and logs |
| [Heartbeat Behaviour](#heartbeat-behaviour) | Re-alignment protocol mid-run |
| [Recovery & Resume](#recovery--resume) | What's safe to resume, what isn't |

---

## Inherited Contracts

These rules already apply to every agent in the project. The orchestrator **inherits** them — it does not weaken them.

- **Archive-first / never-delete** — see [`.ai/maintenance.md`](../maintenance.md). Every "delete" is an archive move.
- **Never reset DB** — see [`.ai/maintenance.md`](../maintenance.md). Destructive DB operations are forbidden.
- **Credential isolation** — see [`.ai/credentials.md`](../credentials.md). Secrets only via env vars; `.env` is never authored or committed.
- **Host vs container isolation** — see [`.ai/environment.md`](../environment.md). No silent host mutations.
- **Naming consult** — see [Naming agent](../../.github/agents/pds-man-naming.agent.md). Mandatory before any new identifier.
- **Depth-priority instruction system** — see [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md). The deepest `.ai/instruct.md` wins.

The autonomous layer cannot relax any of these. Attempting to do so is itself a halt condition (see below).

---

## Stop Conditions

The orchestrator MUST halt at the earliest opportunity (next loop iteration, before the next agent invocation) when ANY of these is true:

### Sentinel-driven

1. **PAUSE file exists** — `.ai/PAUSE` present at any heartbeat or pre-iteration check.
2. **Configuration disabled mid-run** — `autonomy-config.yaml.enabled` flipped to `false`.

### Budget-driven

3. **Steps** — `step_index >= limits.max_steps`.
4. **Wall clock** — elapsed > `limits.max_wall_clock_minutes`.
5. **Files modified** — `len(files_modified) > limits.max_files_modified`.
6. **Tokens** — observer estimate exceeds `limits.max_tokens_per_run`.

### Outcome-driven

7. **Failure streak** — three consecutive agent results with `outcome ∈ {BLOCK, error}`.
8. **Validator/Reviewer BLOCK** — a single BLOCK at the gate stage of the pipeline.
9. **Logging failure** — a step log write fails or violates the required-fields schema.
10. **Scope drift** — heartbeat detects `scope_authority_file` content changed since pre-flight.

### Human-driven

11. **Approval denied** — user rejects an approval gate.
12. **Approval timeout** — no answer within `human_approval.approval_timeout_minutes`.
13. **Manual halt** — user invokes `/ai-autonomous-stop <goal_id>` (future command; today: create `.ai/PAUSE`).

### Safety-driven (terminal, no resume)

14. **Forbidden action attempted** — see [Forbidden Actions](#forbidden-actions). Logged as `safety_violation`.
15. **Allowed-agent violation** — orchestrator about to invoke an agent not in `autonomy-config.yaml.allowed_agents`.
16. **Sanitiser hit** — secret pattern detected in goal, summary, or log payload.

Categories 1–13 produce a **resumable** halt. Category 14–16 produce a **terminal** halt; the user must restart with a new `goal_id`.

---

## Forbidden Actions

Regardless of approval, regardless of scope, the orchestrator MUST NOT cause an agent to:

| Forbidden | Why |
|---|---|
| Write or modify `.env`, `.env.*`, `secrets/`, `*.pem`, `*.key` | Credential isolation ([`credentials.md`](../credentials.md)) |
| Edit any file under `.ai/governance/` | Governance is human-curated |
| Edit any `.ai/instruct.md` | Instruction edits go through `/ai-reflect` → `pds-man-curator` |
| Edit `.ai/index.md` directly | Rebuild via `/ai-update-index` only |
| Run `git push --force`, `git reset --hard <published>`, `git rebase` of shared history | Version control safety ([versioncontrol agent](../../.github/agents/pds-man-versioncontrol.agent.md)) |
| Run `DROP`, `TRUNCATE`, `DELETE FROM` without `WHERE`, schema reset | Never-reset-db ([`maintenance.md`](../maintenance.md)) |
| Install host-level packages, modify PATH, write to user dotfiles | Host isolation ([`environment.md`](../environment.md)) |
| Use `--no-verify`, `--force`, or any flag that bypasses a safety hook | Safety primitives are non-negotiable |
| Invoke `pds-man-curator` or `pds-meta-learner` | These edit governance; humans drive them |

A planned agent invocation that would cause any of the above is **rejected at the orchestrator level** before the agent is even called. The rejection is logged with `outcome: "safety_violation"` and the run terminates.

---

## Approval Gates

`autonomy-config.yaml.human_approval.mode` controls breadth. Inside that breadth, every gate must include:

- **Agent** to be invoked
- **Planned input summary** (≤200 chars, sanitised)
- **Affected paths** (workspace-relative)
- **Safety level** of the action (`low | medium | high`)
- **Expected outcome** in one line

The user answers `yes`, `no`, or `details`. `details` does not advance the loop — it only echoes the queue row and step log; the gate remains open.

A `yes` is scoped to **this single hand-off**. There is no "yes to all" until a future revision.

---

## Sanitisation Rules

Applied to: `goal`, `last_step_summary`, `approval_pending.planned_input`, every step log `input_summary` / `output_summary`.

Drop or mask any match for:

```
password\s*[:=]\s*\S+
api[_-]?key\s*[:=]\s*\S+
secret\s*[:=]\s*\S+
token\s*[:=]\s*\S+
Bearer\s+[A-Za-z0-9._\-]+
-----BEGIN [A-Z ]+-----
ssh-(rsa|ed25519|dss)\s+\S+
postgres(?:ql)?://[^:\s]+:[^@\s]+@
mysql://[^:\s]+:[^@\s]+@
mongodb(\+srv)?://[^:\s]+:[^@\s]+@
```

A match in the **goal itself** is a terminal halt with `safety_violation`. A match in a generated summary is replaced with `[REDACTED]` and logged with `outcome: "sanitised"` (non-terminal).

---

## Heartbeat Behaviour

Heartbeat interval is inherited from [`.ai/agent-config.yaml`](../agent-config.yaml) → `core.heartbeat_interval`. At each heartbeat:

1. Re-read `scope_authority_file`. Hash-compare against the value captured at pre-flight. Mismatch → halt with `scope_drift`.
2. Re-read this file. Hash-compare. Mismatch → halt with `guardrails_drift`. The user must re-run after acknowledging the change.
3. Re-check `.ai/PAUSE`. Present → halt.
4. Re-check `autonomy-config.yaml.enabled`. False → halt.
5. Emit a heartbeat log entry with `outcome: "heartbeat_ok"` and the current `step_index`.

The heartbeat is a **read-only** check. It never repairs drift; it only stops.

---

## Recovery & Resume

`/ai-autonomous-resume <goal_id>` is allowed when the queue row's `status` is `paused`, `paused_timeout`, or `awaiting_approval`. The resume path:

1. Re-runs the full **pre-flight contract** from [`orchestrator.md`](orchestrator.md). The world may have changed since the pause — files committed, sentinel created, config disabled.
2. If pre-flight fails, the row stays in its current status; the orchestrator does not silently re-pause.
3. On success, the loop re-enters at `step_index` from the queue row. The next agent is re-selected from scratch (no replay of stale plans).

**Never resumable**: `completed`, `aborted`, `denied`, and any row with `stop_reason ∈ {safety_violation, allowed_agent_violation, sanitiser_hit, guardrails_drift}`.

---

## See Also

- [`orchestrator.md`](orchestrator.md) — the loop that obeys this file
- [`autonomy-config.yaml`](autonomy-config.yaml) — knobs (limits, approval mode, safety level)
- [`task-queue.md`](task-queue.md) — where halts are recorded
- [`.ai/maintenance.md`](../maintenance.md) | [`.ai/credentials.md`](../credentials.md) | [`.ai/environment.md`](../environment.md) — inherited contracts
