---
name: omh-files
description: [omh] Policy overlay for local file tasks - add path scoping and destructive-action gates after preferring native file tools for ordinary list, search, organize, copy, move, and rename actions. Use when the user says: workspace-file-operator, workspace file operator, file operator, file operation, file operations, filesystem task, filesystem operation, file system task.
metadata:
  hermes:
    tags: [workflow, oh-my-hermes, filesystem]
    category: filesystem
    phase: file-task
    role: guide
    quality_tier: workflow-surface-gated
---

# Workspace File Operator

This is a Hermes-native `workspace-file-operator` workflow skill.

## Why This Exists

`workspace-file-operator` exists so Hermes users can ask for this workflow in chat and receive a structured, evidence-bounded OMH operating surface instead of ad hoc narration.

## Do Not Use When

- The request is already handled by a narrower explicit skill with stronger evidence.
- The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.

## Examples

Good example:

- Prompt: workspace-file-operator list files in the reports folder and move old PDFs into archive after confirmation.
- Expected behavior: Produce `prepare_workspace_file_operator_card` with required context, wrapper actions, and not-evidence boundaries.
- Why: The prompt names a real workflow surface that Hermes can orchestrate without hiding execution.

Bad example:

- Prompt: workspace-file-operator delete every matching file without path scope or confirmation.
- Expected behavior: Report the missing observed evidence or authority instead of claiming the external step happened.
- Why: Prepared OMH guidance is not platform, runtime, connector, file, memory, or delivery evidence.

## Completion Checklist

- The path root, allowed file operations, excluded paths, destructive-operation policy, and stop condition are explicit.
- Delete, overwrite, move, rename, permission change, archive mutation, upload, and download are gated or marked missing.
- Directory listings, file contents, hashes, diffs, and operation results are reported only from observed file evidence.

## Recovery Notes

- If the target path or folder is missing, ask for the smallest path scope needed before preparing the operation.
- If delete, overwrite, move, rename, chmod, or irreversible cleanup is requested, require an explicit confirmation gate.
- If the request is file conversion, deck/PDF export, or attachment delivery, route to materials-package or deliverable-package instead.

## Workflow Lane

- Current lane: **Automation and status** (`achievements`, `workspace-audit`, `production-audit`, `automation-blueprint`, `github-event-ops`, `agent-board`, `gateway-intent-card`, `voice-operator`, `+33 more`) - schedules, status, health, and ops review.
- If intent belongs to another lane, hand back to `oh-my-hermes` or name the adjacent workflow.
- Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.

## Use When

Use when Hermes should prepare or supervise local workspace/file-system operations such as listing, searching, organizing, copying, moving, renaming, archiving, or deleting files without claiming the operation ran.

    Strong routing signals: `workspace-file-operator`, `workspace file operator`, `file operator`, `file operation`, `file operations`, `filesystem task`, `filesystem operation`, `file system task`, `file system operation`, `list files`, `list folder`, `list directory`, `find local files`, `search files`, `organize files`, `organize folder`, `move file`, `move files`, `copy file`, `copy files`, `rename file`, `rename files`, `delete file`, `delete files`, `remove file`, `remove files`, `archive files`, `downloads folder`, `reports folder`, `folder cleanup`, `file cleanup`, `파일 작업`, `파일 조작`, `파일 정리`, `파일 검색`, `파일 찾아`, `파일 이동`, `파일 복사`, `파일 이름 변경`, `파일 삭제`, `폴더 정리`, `다운로드 폴더`, `디렉터리 목록`

## Catalog Metadata

Category: `filesystem`
Phase: `file-task`
Hermes role: `guide`
Quality tier: `workflow-surface-gated`
Reasoning demand: `standard`

Quality bar:

- Name the user-facing workflow objective, required context, next action, and stop condition.
- Separate prepared guidance from observed platform, runtime, connector, file, memory, or delivery evidence.
- Expose missing tools, credentials, targets, or observations as user-visible gaps.

Handoff policy:

Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

Required inputs:

- user request
- target context
- delivery or status expectation
- known missing evidence

Expected outputs:

- workspace_file_task_card/v1
- file_operation_scope/v1
- file_observation_manifest/v1 when observed
- file_confirmation_gate/v1 when destructive
- next action
- prepared-vs-observed boundary

Artifact expectations:

- workspace_file_task_card/v1 metadata-only wrapper card when prepared
- file_operation_scope/v1 with path root, allowed operations, excluded paths, and stop condition
- file_observation_manifest/v1 only when directory listings, file stats, hashes, diffs, or operation output are observed
- file_confirmation_gate/v1 for delete, overwrite, move, rename, chmod, archive mutation, or irreversible cleanup

Safety rules:

- A workspace file operator card is not file read, file write, copy, move, rename, delete, archive, upload, download, permission change, or destructive filesystem evidence unless observed file-operation output records it.
- Do not claim connector, gateway, runtime, file generation, memory mutation, or host automation evidence from prepared guidance.

## Runtime Evidence

Preferred harness for this skill: `workspace-file-operator`.

```sh
omh runtime record --skill workspace-file-operator --harness workspace-file-operator --status started
```

Record observed delegation results; otherwise return `not_available` or `not_observed`.
Prepared OMH routing is not execution, review, CI, merge-readiness, or merge evidence.
- Treat wrapper memory/context summaries as advisory local context, not proof of opaque Hermes memory reads or changes.
Preserve workflow intent and stop conditions; verify before claiming completion.

Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
