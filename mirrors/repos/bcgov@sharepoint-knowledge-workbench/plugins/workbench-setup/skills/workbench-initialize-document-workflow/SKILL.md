---
name: workbench-initialize-document-workflow
plugin: workbench-setup
description: "Interactive intake wizard covering source-document identity, requested processing stages, requested output formats (only implemented renderer profiles offered as executable choices), publication locations, agent-grounding representations, and governance/evidence settings. Produces document-workflows/<DocumentId>.workflow.psd1 and publication-profiles/<DocumentId>.publication.psd1. Execution boundary: ask -> propose defaults -> validate -> display resolved configuration -> write profile files -> stop. Never extracts documents, renders content, or connects to/modifies SharePoint."
allowed-tools: Bash, Read
examples:
  - "python -c \"import document_workflow as dw; dw.write_document_workflow('.', 'sample-manual', workflow, publication)\""
---

# Initialize Document Workflow

## Trigger and Purpose

Use this skill to run the broader interactive intake wizard for a
source document, per `docs/superpowers/specs/2026-08-02-multi-
document-destination-configuration-design.md` Sections 1 (Layer 1b,
Layer 2) and 8. Ask the user (across all domains, without performing
any of their work): source-document identity, new conversion vs.
revision, content type/ownership, requested processing stages,
requested output formats, human-facing publication locations, media
locations, ASPX publication, agent-grounding representations, existing-
vs-new agent decisions, native-skill requirements, governance/evidence
settings, and an explicit list of unresolved decisions.

**Only implemented renderer profiles may be offered as executable
choices** — currently `multipage-markdown` and `sharepoint-aspx`
(`document_workflow.IMPLEMENTED_RENDERER_PROFILES`, kept in sync with
`structured-content-rendering`'s actual registered renderers).
Anything else requested is recorded in `UnsupportedRequests`, never
silently treated as executable.

**Execution boundary — initialization only, this version:**
```text
ask -> propose defaults -> validate -> display resolved configuration -> write profile files -> stop
```
Must **not**: extract documents; confirm topic boundaries; render
content; connect to or modify SharePoint; upload files; create pages;
create agents; deploy native skills. Every one of those stays a
separate, explicitly invoked domain-plugin capability.

`initialize-publication-profile` (a narrower, earlier-conceived skill
named in the design doc) is **superseded/absorbed** into this wizard's
broader flow — not a separate, fourth skill.

## Public Interface

```python
from document_workflow import (
    classify_renderer_requests, build_workflow_profile,
    build_publication_profile, write_document_workflow,
)

workflow = build_workflow_profile(document_id=..., source_path=..., source_format=...,
                                   is_revision=..., requested_stages=[...],
                                   requested_renderer_profiles=[...],
                                   human_confirmation_gates={...},
                                   publication_profile_path=...,
                                   agent_actions_requested=[...], outstanding_decisions=[...])

publication = build_publication_profile(document_id=..., title=..., content_type=...,
                                         content_owner=..., source_package_path=...,
                                         package_identity=..., human_publication={...})

workflow_path, publication_path = write_document_workflow(repo_root, document_id, workflow, publication)
```

Both `build_*` functions validate before returning (raise
`DocumentWorkflowError` on invalid input, e.g. an empty `document_id`
or an unimplemented renderer profile placed in `HumanPublication.
PublicationProfile`). `write_document_workflow` refuses to silently
overwrite existing profile files unless `overwrite=True` is passed
explicitly.

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library.

