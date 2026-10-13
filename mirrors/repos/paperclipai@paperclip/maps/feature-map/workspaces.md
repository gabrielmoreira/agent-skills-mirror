# Execution workspaces, services, and files

A project or task can use a managed workspace with inspectable files, Git state, services, and runtime controls. Operators can follow its lifecycle through provisioning, use, and closure.

Implementation: [workspace list](../../ui/src/pages/Workspaces.tsx), [execution workspace](../../ui/src/pages/ExecutionWorkspaceDetail.tsx), [project workspace](../../ui/src/pages/ProjectWorkspaceDetail.tsx).

Agent access: [companion](../agent-access-map/workspaces.md).

## Sub-features

- `binding`: identify the workspace actually bound to a task/run.
- `provisioning`: observe readiness and failures instead of inferring readiness from a created record.
- `services`: start/stop supported services and inspect logs and exposed endpoints.
- `files-git`: inspect workspace files and repository state used for the deliverable.
- `closure`: close/reopen or reconcile through permitted controls without losing work.

## How to get to it (user POV)

### `task-workspace`

Use the task’s workspace card or Files panel and follow its workspace link.

### `workspace-management`

Open `/workspaces`, a project workspace, or `/execution-workspaces/:workspaceId` and its Services/Configuration/Runtime logs views.

## Driving it with Playwright and the Paperclip CLI

Preconditions: follow the [baseline](./README.md#before-driving-a-journey). Enable isolated-workspace UI where needed. Use an owned disposable repository and environment; record workspace ID and branch.

### `task-workspace`

Automated: [workspace card](../../ui/src/components/IssueWorkspaceCard.test.tsx) and [task binding](../../server/src/__tests__/issue-runtime-workspace-binding.test.ts) cover host/binding contracts.

Manual: Run a task that writes a small file, follow the bound workspace, and inspect the file and revision. Reload and verify links still refer to the same workspace, not another checkout or a stale run.

For task workspace selection, use the authorized task workspace API to choose a
task directory, project source, or existing workspace. Verify that a change
made during a run stays pending until the next normal admission. Submit another
choice using the returned revision, then retry the superseded request; it must
fail without replacing the newer pending choice. A projectless
task must retain its files across resume and reassignment. Use the repository
preparation API to add an authorized repository beneath that workspace;
repeat the request and verify that it reuses the checkout and pinned revision.
See [task binding tests](../../server/src/__tests__/task-workspace-binding.test.ts)
and [repository access tests](../../server/src/__tests__/task-workspace-repositories-trust.test.ts).
An existing projectless folder alias of a sandbox-restricted project must be
rejected for a standard local task before its adapter executes. Repeat after
relocating the configured source; retained ownership must still enforce the
boundary. This is separate from ordinary authorized file preview/download.
For a registered worktree selected for a sandbox or SSH environment, configured
and built-in provision scripts must not run on the controller during fresh
creation, reuse, or rebuild, including host runtime provisioning. Repeat with
standard trust and a protected read-only source, then with source write grants;
permissions must not change execution placement. Verify isolated source copying
and selected-environment dispatch still work. Repeat an explicit local isolated
source choice: copying remains available but controller scripts must stay absent,
including after binding or metadata changes and closed-worktree reopening. An
implicit trusted local project default remains a positive provisioning control.
Repeat with a newer configured default overriding an older primary source, then
with a newer primary overriding an older nonprimary source. Both configured and
built-in hooks must run for the implicit local default. Task creation and controller
classification share configured-default, primary, creation-time and ID precedence.
Explicit choices and saved copy-only markers still suppress hooks; changing the
default must not rotate an existing binding or clear its marker.
SSH keeps its explicit remote provision-command path; these checks
do not claim a new sandbox provision transport.
Low-trust closed-worktree reopening, including a board-comment reopen of a projectless task, must also suppress both kinds of host provision script. Returned checkpoints must reject file, symlink or missing parents before host writes, even if a nested file is marked unchanged. The retained host file and recovery evidence must survive rejection. These are automated safety contracts, not new live runtime acceptance.

For a child created by an admitted agent with an explicit existing workspace, verify that a matching sandbox boundary permits creation before the child has an ID. A changed child policy, unrelated parent, or forged creator run must fail. See the [child workspace trust regression](../../server/src/__tests__/task-workspace-child-trust.test.ts). This automated contract does not add live acceptance evidence.

### `workspace-management`

Automated: [workspace detail](../../ui/src/pages/ExecutionWorkspaceDetail.test.tsx) and [runtime service](../../server/src/__tests__/workspace-runtime.test.ts) cover UI and runtime contracts separately.

Manual: Provision a disposable workspace, wait for readiness, start an available service, open its endpoint, and inspect a real response and logs. Stop it and verify it actually stops. Exercise close/reopen only after inspecting pending changes and active runs.

## Gotchas

- UI visibility, default isolation policy, the local environment row, a workspace
  record, and a running service are distinct prerequisites. A fresh instance
  still needs an owned cwd/repository and runtime commands; `/workspaces` lists
  existing work. Reopening depends on lifecycle, not a generic detail action.

- A link or running badge does not prove the service is reachable from the user’s browser.
- Workspace IDs, runtime leases, and repository paths are not interchangeable.
- Organizational project, source project, task files, personal `AGENT_HOME`, and
  provider home have separate meanings. Private source ownership remains attached
  to copied files after source configuration changes or workspace closure.
- Use [recovery](./recovery.md) for divergence/export repair and [CLI operations](./cli-operations.md) for local worktree tooling.
