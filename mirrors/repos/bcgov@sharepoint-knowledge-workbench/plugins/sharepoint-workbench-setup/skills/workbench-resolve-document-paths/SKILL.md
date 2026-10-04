---
name: workbench-resolve-document-paths
plugin: sharepoint-workbench-setup
description: Resolves a DocumentId plus already-parsed connection, document-workflow and publication-profile dicts into the concrete export paths and arguments the two SharePoint analysis plugins (sharepoint-site-assessment, sharepoint-site-migration) need, checks each path against the real filesystem, and prints the resolved invocations. Use when preparing to run those plugins for a document. Never executes a downstream plugin; print, don't execute.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from path_resolution import resolve_workbench_paths, format_invocations; print(format_invocations(resolve_workbench_paths(document_id='sample-manual', connection=connection, workflow_profile=workflow, publication_profile=publication, workbench_root='.')))\""
---

# Resolve Workbench Paths

Turn a `DocumentId` and parsed config dicts into the explicit paths the downstream
SharePoint analysis plugins take as parameters, and print them for a human or agent to run.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Print, don't execute. Never launch a subprocess, import a downstream plugin module, or run
  anything on the user's behalf.
- Resolution flows downward only. Never make a downstream plugin read `sharepoint-workbench-setup` config.
- No conditional orchestration: no branching on profile contents beyond the `DocumentId`
  identity check, no execution ordering.
- Never fabricate a path. An absent file is reported `UNAVAILABLE`.
- Run from this skill's root with `scripts/` on `sys.path`; helper is
  `scripts/path_resolution.py`. Standard library only.

## Quick start

Call `resolve_workbench_paths(...)` then `format_invocations(result)` and show the output;
signatures are in [the API reference](references/path-resolution-api.md).

## Workflow

1. Collect `document_id` and the three parsed dicts (connection, workflow profile,
   publication profile) plus `workbench_root`.
2. Resolve against the convention
   `<workbench_root>/sharepoint-exports/<DocumentId>/<skill-export-subdir>/<filename>`.
3. Print the invocations. The user decides which to run, using each downstream plugin's own
   documented interface.

## Verification

Check `result.overall_status` (`PASS`, `PARTIAL` or `EMPTY`) and each invocation's
`status` and `missing` list. A `DocumentId` mismatch against the profiles raises
`ValueError`; do not work around it.

## References

- [API reference](references/path-resolution-api.md): read before calling
  `resolve_workbench_paths`, or when interpreting result statuses.
- [Design rationale](references/path-resolution-design.md): read when asked why this prints
  instead of executes, about the export path convention, or whether to add execution.
