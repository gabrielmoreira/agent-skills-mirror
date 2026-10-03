---
name: workbench-initialize-document-workflow
plugin: workbench-setup
description: "Interactive intake wizard that records a source document's identity, processing stages, output formats (only implemented renderer profiles are executable choices), publication locations, agent-grounding representations and governance settings, then writes document-workflows/{DocumentId}.workflow.psd1 and publication-profiles/{DocumentId}.publication.psd1. Use when setting up a new document or revision for conversion or publication. Ask, propose defaults, validate, display, write, stop; never extracts, renders, or connects to SharePoint."
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import document_workflow as dw; dw.write_document_workflow('.', 'sample-manual', workflow, publication)\""
---

# Initialize Document Workflow

Run the interactive intake for one source document and write its two profile files.
Initialization only: configuration in, `.psd1` profiles out.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Execution boundary for this version:

```text
ask -> propose defaults -> validate -> display resolved configuration -> write profile files -> stop
```

Must **not**: extract documents; confirm topic boundaries; render content; connect to or
modify SharePoint; upload files; create pages; create agents; deploy native skills. Each
stays a separate, explicitly invoked domain-plugin capability.

Offer only implemented renderer profiles (`multipage-markdown`, `sharepoint-aspx`) as
executable choices. Record anything else in `UnsupportedRequests`.

Run from this skill's root: the helpers are `scripts/document_workflow.py` and
`scripts/psd1_writer.py`. Standard library only; no other plugin is required.

## Quick start

1. Ask the intake questions in [intake scope](references/document-workflow-intake-scope.md).
2. From the skill root, put `scripts/` on `sys.path`, build both profiles and write them with
   `write_document_workflow`; signatures are in
   [the API reference](references/document-workflow-api.md).

## Workflow

1. Ask for source-document identity, new conversion vs. revision, requested stages and
   output formats, publication and media locations, agent-grounding choices, and
   governance settings. List every unresolved decision explicitly.
2. Propose defaults for anything the user leaves open.
3. Call `build_workflow_profile` and `build_publication_profile`; they validate and raise
   `DocumentWorkflowError` on invalid input.
4. Display the resolved configuration and get confirmation.
5. Call `write_document_workflow`. It refuses to overwrite existing files unless
   `overwrite=True` is passed explicitly. Then stop.

## Verification

Confirm both files exist at `document-workflows/<id>.workflow.psd1` and
`publication-profiles/<id>.publication.psd1`, and that every requested renderer outside the
allowlist appears under `UnsupportedRequests`. Confirm no extraction, rendering or
SharePoint call was made.

## References

- [Intake scope](references/document-workflow-intake-scope.md): read before asking
  the user questions, or when a requested output format is not in the allowlist.
- [API reference](references/document-workflow-api.md): read before calling
  `build_*` or `write_document_workflow`, or when validation or overwrite errors occur.
