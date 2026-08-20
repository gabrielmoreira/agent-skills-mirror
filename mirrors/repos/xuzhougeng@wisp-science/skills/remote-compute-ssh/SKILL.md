---
name: remote-compute-ssh
description: Submit recoverable SSH-direct research Runs with live progress cards and model-free monitoring.
license: Apache-2.0
---

# Remote compute over SSH

Use this skill after choosing an `ssh:<alias>` execution context. Wisp owns the
job lifecycle locally: `run_in_context` creates the Run record, stages explicit
inputs with persisted byte progress, and starts a detached supervisor on the server.
The Runs panel and SQLite record remain authoritative if the conversation ends
or Wisp restarts.

## Dispatch workflow

1. Use short `run_in_context` calls for read-only discovery such as
   `nvidia-smi -L`, `which python3`, or `module avail`. Free-form shell SSH is
   disabled. Use the interpreter path reported by the context probe; do not
   assume a `python` alias exists when the probe found `python3`.
2. Put the real command in one `run_in_context` call. Include environment
   activation in the command so the Run is reproducible.
3. To watch the Run or wait for later work, call `monitor_run` with the
   returned Run id. Wisp inserts a live card in the conversation, suspends
   the tool without additional model calls, and resumes the same agent turn
   with the terminal result. If the result has `wait_interrupted: true`, the
   remote process is still running: answer the user from the snapshot, then
   call `monitor_run` again with the same id. Do not resubmit. Use `cancel_run`
   only when the user asked to stop. For fire-and-forget work, report the Run id
   and end the turn instead.
4. Use `get_run` only for one explicit status snapshot; never call it repeatedly
   to wait. Use `cancel_run` when the user asks to stop.

Never monitor a Run with `Start-Sleep`, `sleep`, `ssh ... ps`, `kill -0`, a
shell polling loop, `nohup`, background `&`, or hand-written PID files. Those
duplicate the control plane and can strand the agent turn. A transient SSH
error is stored as `last_poll_error`; do not resubmit, because Wisp retries the
same idempotent remote handle.

```json
{
  "context_id": "ssh:gpu-box",
  "title": "Motif enrichment across 2,000 backgrounds",
  "command": "source ~/miniforge3/etc/profile.d/conda.sh && conda activate genomics && python motif_enrichment_analysis.py",
  "timeout_secs": 14400,
  "input_paths": ["scripts/motif_enrichment_analysis.py"]
}
```

Then, when live monitoring is needed:

```json
{ "run_id": "<id returned by run_in_context>" }
```

Pass that object to `monitor_run`. The call may remain suspended for hours;
it does not consume model tokens while the Run Manager watches the job.
If `wait_interrupted` is true, respond from the snapshot and call `monitor_run`
again with the same id; do not resubmit.

`input_paths` are project-relative local files. Wisp validates them, copies
them into an isolated `inputs/` directory, and flattens them to their basenames.
The command starts in that directory, so the example above can use the staged
script by basename. Upload progress, throughput, and ETA appear in the Run card. For a large dataset already on
the server, reference its absolute remote path in `command`; do not copy it
back to the laptop just to send it out again.

A remote command or application exiting non-zero is normal exploration after a
successful login. Read stderr, correct the command from the probed
capabilities, and continue. Stop only when SSH rejects authentication or host
trust; do not repeat a rejected login with guessed credentials or SSH options.

The control directory is `~/.wisp-science/runs/<run-id>` and the command starts
in its `inputs/` subdirectory. stdout and stderr are
tailed into the Run record. The SSH supervisor requires `setsid`, GNU-compatible
`timeout`, `bash`, and `/proc`; a missing prerequisite fails the Run instead of
running without a wall-time limit. Wisp maps the supervisor timeout marker to
`timed_out`.

## Results

Declare `output_specs` with workdir-relative globs for the final products.
After the Run succeeds, Wisp collects the matches on the server, checksums
them, pulls them back through a persisted transfer Run, places them under the
project's configured results directory, and registers each as an
ArtifactVersion. The Run records `harvested_at` once registration completes;
`harvest_run({"run_id":"..."})` retries a failed or interrupted harvest.

Selection is the database boundary: only spec-matched outputs are transferred
and recorded. Point globs at final products (for example `Trinity.fasta`),
never at intermediate trees. A non-bundle glob may match at most 500 files.
For a many-file output that must be kept, set `bundle: true` so the matches
(or a whole directory) arrive as one tar.gz archive registered as a single
artifact:

```json
{
  "output_specs": [
    { "glob": "results/*.tsv", "kind": "table", "residency": "auto" },
    { "glob": "assembly_out", "kind": "archive", "residency": "local", "bundle": true }
  ]
}
```

Files over the size caps (or `residency: "remote"`) are moved out of the run
workdir into the project's persistent remote data area, registered as
`ssh://` references with checksum and size, and ledgered so they stay visible
in `list_remote_files`. Workspace cleanup never orphans them. Delete a
ledgered persist file with `remove_remote_files` only after the user confirms
they no longer need it — that marks the artifact's source discarded. Explicit
`ssh://…` URIs in `output_specs` still register a remote reference without
any download.

## Cleanup: servers are disposable

Tasks and artifacts belong to the project; the server only computes. After the
results are harvested (or knowingly abandoned), reclaim the workspace:

- `cleanup_run_workspace({"run_id":"..."})` deletes the Run's
  `~/.wisp-science/runs/<run-id>` directory (inputs, logs, intermediates). A
  succeeded Run with declared `output_specs` must be harvested first; the tool
  refuses otherwise so results are never lost. Registered artifacts stay in the
  project. Before deletion Wisp pulls a trailing slice of stdout/stderr
  (at most 4 MiB per stream) into `runs/<id>/` — not the complete remote logs.
- `list_remote_files({"context_id":"ssh:<alias>"})` shows every file this
  project placed on the server (staged inputs, uploads, and harvest-persisted
  outputs) classified as active, replaced, or orphan; `remove_remote_files`
  deletes retracted ones. Current successful uploads stay active — they are
  the user's dataset, not sweep fodder. Replaced rows are closed in the ledger
  only (they share a path with the current file). Harvest-persisted outputs
  stay active while a live External artifact still points at them. Uploads are
  ledgered when the transfer attempt starts, so a failed or cancelled partial
  is visible and can be removed.
- Removing the SSH host from Settings audits remaining references and
  ledgered files, then marks those External artifacts as source-discarded.
  Later download, preview, or transfer of those URIs is refused even if the
  same alias is re-registered.
- Project settings can enable retention windows that automatically clean
  succeeded+harvested and failed run workspaces after N days.

Intermediate files (for example Trinity's hundreds of thousands of read
partitions) should never be enumerated, downloaded, or registered — leave them
in the workdir and let cleanup reclaim them in one deletion.

## Transfers between local and SSH contexts

Use `transfer_between_contexts` for one exact remote file or directory. The
destination may be another selected SSH context or `local`. Never compose
nested `ssh`, `scp`, or `rsync -e ssh` inside `run_in_context`.

Users can also upload from the Files panel: select the SSH context, open the
destination folder, then use **Upload** or drop local files. That UI path
submits the same `file_transfer` Run and does not require this tool.

For a local upload via the agent, set `source_context_id` to `local`, provide
the exact existing absolute local file or directory, and select an SSH
destination.
Omit `destination_path` to place the file under the project's configured
remote data directory for that server. Wisp rejects globs, symlinks, special
files, and existing remote destinations, and ledgers every successful upload
so retracted files can be found and removed later. Call `monitor_run`
with the returned Run id; call it again after `wait_interrupted`.

For a local download, set `destination_context_id` to `local` and provide the
exact new absolute local path. Ask the user when that path is unspecified.
Wisp stages the item beside the destination, never overwrites an existing
path, and removes partial staging data after failure or cancellation. Call
`monitor_run` with the returned Run id; call it again after `wait_interrupted`.

When the user approves persistent A→B trust, call `configure_ssh_trust` first.
It creates a dedicated key on A, carries only the public key through Wisp,
installs it on B, and verifies the directed edge. The transfer then prefers
rsync when both servers provide it and falls back to scp. If the user does not
want server SSH configuration changed, select the relay route; Wisp downloads
to a private local temporary directory and uploads with B's separately stored
credentials.

## Cancellation and recovery

`cancel_run({"run_id":"..."})` changes an SSH Run to `cancelling`. Wisp
verifies the persisted token, PGID, and Linux process start time before sending
TERM to the remote process group; it records `cancelled` only after remote
confirmation. If the server is temporarily unreachable, the Run stays
`cancelling` and retry continues after reconnection or app restart.

Active statuses are `submitted`, `running`, and `cancelling`. Terminal statuses
are `succeeded`, `failed`, `timed_out`, `cancelled`, and `lost`. `lost` means
the remote token/control directory/process identity was definitively missing,
not merely that one SSH poll failed.

## Current boundary

This implementation is SSH-direct and assumes a Linux-like server with `sh`,
`bash`, `nohup`, `setsid`, and `/proc`. Do not daemonize or create a new session
inside the job, because that escapes process-group cancellation.

Scheduler lifecycle is not implemented yet. Do not submit `sbatch`, `qsub`, or
`bsub` through this direct runner: the Run would only track the short submit
command, not the scheduler job. On a shared login node, ask the user for a
dedicated compute host or explain that scheduler-aware submit/poll/cancel is a
separate capability still needed.
