---
name: workbench-resolve-workbench-paths
plugin: workbench-setup
description: Resolves a DocumentId plus already-parsed connection/document-workflow/publication-profile dicts into the concrete export paths and arguments the four Phase 9 SharePoint analysis plugins (sharepoint-discovery, sharepoint-schema, sharepoint-link-remediation, sharepoint-page-modernization) would need, checks each referenced path against the real filesystem, and prints the resolved invocations. Never executes a downstream plugin -- print, don't execute.
allowed-tools: Bash, Read
examples:
  - "python -c \"from path_resolution import resolve_workbench_paths, format_invocations; print(format_invocations(resolve_workbench_paths(document_id='sample-manual', connection=connection, workflow_profile=workflow, publication_profile=publication, workbench_root='.')))\""
---

# Resolve Workbench Paths

## Trigger and Purpose

Use this skill to close Seam 2 described in
`docs/architecture/sharepoint-engineering-plugin-set.md` and designed
in `docs/superpowers/specs/2026-08-07-sharepoint-collection-and-
orchestration-design.md` (Part B): the four Phase 9 SharePoint analysis
plugins take explicit paths as parameters and read none of
`workbench-setup`'s config — deliberately, so each stays independently
installable (`plugin-architecture-policy.md` §1.3, verified by
`isolated_install_check.py`). Nothing before this skill resolved
`workbench-setup`'s config into the concrete paths those plugins need.

This skill is that resolution layer, and only that: it reads a
`DocumentId` plus already-parsed connection/workflow-profile/
publication-profile dicts, resolves them into the export paths each
downstream plugin skill's `SKILL.md` documents as its inputs, checks
each one against the real filesystem, and **prints** the resolved
invocations. It never launches a subprocess, never imports a downstream
plugin module, and never executes anything on the user's behalf.

## Why print, not execute

Per the design spec: "Print-don't-execute keeps the layer inspectable,
keeps `workbench-setup` free of any dependency on the four plugins
(preserving *its* standalone installability), and makes the resolution
logic testable without running anything." Adding real execution here
would either (a) require `workbench-setup` to import or shell out to
four plugins it has no dependency on today, breaking §1.3, or (b) turn
this skill into an orchestration/workflow engine making conditional
execution decisions — both are explicitly out of scope for this design
(see the spec's "What this deliberately does NOT do"). A human or agent
reads the printed invocations and runs the ones they choose themselves,
using each downstream plugin's own documented interface.

## Why plugins are not made to read config themselves

Resolution flows **downward only**: this layer reads config and emits
explicit paths/arguments down to plugin invocations — it never makes a
downstream plugin reach up into `workbench-setup`'s config itself. That
would create a shared-config coupling across all five plugins and
defeat the whole point of each one installing and running standalone.

## Export path convention

Nothing before this skill defined where collected SharePoint exports
live on disk — Part A (`sharepoint-collection`, the plugin that would
produce them) is design-only, not authorized to build. Until a human
produces exports by hand or Part A exists, this skill resolves against
the minimal convention implied by the design spec:

```text
<workbench_root>/sharepoint-exports/<DocumentId>/<skill-export-subdir>/<filename>
```

`<skill-export-subdir>`/`<filename>` per entry are fixed data in
`path_resolution.DOWNSTREAM_INVOCATIONS`, taken directly from each
downstream skill's own `SKILL.md` "Usage" section — not invented
per-call. An absent file is reported `UNAVAILABLE`, never fabricated as
if present.

## Public Interface

```python
from path_resolution import resolve_workbench_paths, format_invocations

result = resolve_workbench_paths(
    document_id="sample-manual",
    connection=connection,               # Layer 1 connection-config dict
    workflow_profile=workflow_profile,   # Layer 1b document-workflow dict
    publication_profile=publication_profile,  # Layer 2 publication-profile dict
    workbench_root=".",
)
print(format_invocations(result))
```

`result.overall_status` is `"PASS"` (every downstream invocation has
all its required paths present), `"EMPTY"` (none of them do), or
`"PARTIAL"` (a mix — the individual `ResolvedInvocation.status` values
name which). Each `ResolvedInvocation` carries `plugin`, `skill`,
`status` (`"AVAILABLE"` | `"PARTIAL"` | `"UNAVAILABLE"`), `args`
(resolved `Path`s for the files that exist), and `missing` (filenames
that do not). `document_id` is cross-checked against
`workflow_profile`/`publication_profile`'s own `Document.DocumentId`
when present; a mismatch raises `ValueError` rather than silently
resolving against the wrong document.

## What this does NOT do

- Does not execute, subprocess, or import any of the four downstream
  plugins.
- Does not make any plugin depend on `workbench-setup`, or read shared
  config itself.
- Does not branch on profile contents beyond the `DocumentId` identity
  check — no conditional orchestration, no execution ordering, no state
  machine. If a future need requires that, this design has been
  outgrown; see the design spec's own note to that effect.
- Does not implement Part A (`sharepoint-collection`) — that remains
  `DESIGN_ONLY`, `REQUIRES_HUMAN_DECISION`, out of scope here.

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library.

