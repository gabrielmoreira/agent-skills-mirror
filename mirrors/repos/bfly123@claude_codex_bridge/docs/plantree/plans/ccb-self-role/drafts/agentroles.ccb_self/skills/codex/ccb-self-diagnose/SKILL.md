---
name: ccb-self-diagnose
description: Diagnose CCB runtime, mounted daemon graph, tmux namespace and panes, provider context, queue/inbox/trace, replies/artifacts, config drift, and storage boundaries. Use when the user asks what is broken, which agent is stuck, whether CCB is mounted, why a reply did not arrive, or what to check first.
---

# CCB Self Diagnose

Use this skill for read-only triage. Prefer CCB control-plane diagnostics and
read-only tmux evidence. Do not mutate runtime state from this skill.

## Evidence Model

Keep these categories separate in every diagnosis:

- Authority: current mounted daemon service graph, lifecycle, lease, current
  configured-agent runtime records, and loaded config.
- Evidence: `ccb ping`, `ccb doctor`, `ccb ps`, `ccb queue`, `ccb pend`,
  `ccb trace`, `ccb fault list`, `ccb doctor logs <agent>`, reply/artifact
  records, tmux pane metadata/text capture, provider session files, pid files,
  and config validation or reload dry-run output.
- Residue: disk-only `.ccb/agents/*` directories for unknown agents, stale
  panes, stale sockets, old session artifacts, dead helpers, and orphaned
  provider state.

Configured-agent and restart target authority comes from the mounted daemon
graph, not disk config, tmux panes, or `.ccb/agents/*` residue.

## Core Workflow

1. Confirm the project anchor and current mounted daemon generation.
2. Gather the control-plane snapshot:
   - `ccb ping ccbd`
   - `ccb doctor`
   - `ccb ps`
   - `ccb queue --detail all`
   - `ccb fault list`
   - `ccb pend --inbox --detail <agent>` when one agent is suspected
   - `ccb trace <job_id|message_id|attempt_id|reply_id>` for lineage issues
   - `ccb doctor logs <agent>` when provider/API evidence is needed
3. Gather read-only tmux evidence when pane or provider state matters:
   - current CCB tmux namespace/session/socket
   - pane ids, active/dead flags, titles, current commands, and captured text
   - activity sampling when supported
   - provider session and pid-file paths plus modification times when useful,
     without reading secret or private provider-state contents
4. For config drift, run `ccb config validate` first, then
   `ccb reload --dry-run`. Do not treat disk config as live graph until reload
   has succeeded and the daemon graph has been rechecked.
5. For artifact-backed replies or requests, read the full artifact file before
   acting. If the full file is absent or expired, report a blocker and do not
   infer from preview text alone.
6. Classify the failure domain and hand off:
   - daemon lifecycle, namespace, pane, provider context, config drift, or
     storage boundary -> `ccb-self-recover`
   - job/message/reply/artifact/callback lineage -> `ccb-self-chain`
   - config design/edit/reload readiness -> built-in `ccb-config`

## Failure Domains

Use the smallest domain that explains the evidence:

- Daemon lifecycle: no mounted daemon, unhealthy heartbeat, bad lease, stale
  generation, socket issue.
- Tmux namespace/pane: missing CCB namespace, dead pane, stale pane id, pane
  text not changing, layout/sidebar mismatch.
- Provider context/API: auth, quota/rate limit, model mismatch, endpoint/base
  URL, network, provider outage, or corrupted conversation context. Do not read
  secrets.
- Message chain: queued ask, missing reply, incomplete reply, pending callback,
  artifact-backed reply not read, or retry/resubmit/ack decision.
- Config drift: disk config differs from loaded daemon graph, dry-run reload
  blocked, role binding missing, or changed startup inputs need post-reload
  runtime refresh.
- Storage boundary: provider state or runtime files live in the wrong root, or
  project/runtime relocation rules are violated.

## Reporting

Return a concise diagnosis:

```text
Status: ok|warn|error
Suspected domain: ...
Authority: ...
Evidence: ...
Residue: ...
Confidence: high|medium|low
Next action: ...
Blocked by: ...
```

## Red Lines

- Do not run `ccb reload`, `ccb clear`, `ccb repair`, `ccb restart`, `ccb kill`,
  or raw tmux mutation from this skill.
- Do not read provider auth, credentials, API keys, or unrelated private
  provider state.
- Do not use screenshots unless pane text/metadata is insufficient and the
  target is CCB-owned.
- Do not present tmux evidence as configured-agent authority.
