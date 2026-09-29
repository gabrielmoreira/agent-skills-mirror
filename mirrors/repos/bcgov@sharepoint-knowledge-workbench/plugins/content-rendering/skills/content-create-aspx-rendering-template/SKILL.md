---
name: content-create-aspx-rendering-template
plugin: structured-content-rendering
description: Instantiates a new ASPX/modern-page rendering (page-structure) template file from this plugin's canonical generic or standard-manual starter -- heading, body, and media placeholders, backed by the confirmed-working Add-PnPPage/Add-PnPPageTextPart fragment shape from the Phase 3.0 tenant experiment. Not an agent/native-skill instruction template (that is Task 0.7/0.8's separate template system), and never a raw wrapped .aspx page (confirmed Access denied).
allowed-tools: Bash, Read
examples:
  - "python -c \"import templates; templates.create_rendering_template('generic', 'aspx', 'out/page.template.html')\""
---

# Create ASPX Rendering Template

## Trigger and Purpose

Use this skill to instantiate a new ASPX/modern-page *rendering*
template file (page/document layout -- heading, body, metadata
placement, media placement) for a given profile. Two profiles are
currently defined:

- `generic` — the plugin's default page shape.
- `standard-manual` — the standard-manual variant, structurally confirmed against
  the Phase 3.0 Sec.15 tenant experiment
  (`tools/phase-3-sharepoint-discovery/aspx-experiment/
  initiate-a-file.html`): a heading followed directly by body content,
  with no `<html>`/`<head>`/`<body>` wrapper — the shape
  `Add-PnPPageTextPart` consumes. Raw wrapped `.aspx` file upload to
  Site Pages is a confirmed `Access denied` platform boundary; this
  template family never produces that shape.

This is a *rendering* template — document/page structure, headings,
body, media placement, human-facing layout. It is distinct from Task
0.7/0.8's *agent/native-skill* template system (agent instructions,
answer formatting) — the two are never merged.

## Public Interface

```python
from templates import create_rendering_template

template = create_rendering_template(
    profile="generic",  # or "standard-manual"
    fmt="aspx",
    output_path="path/to/new-template.html",
)
# RenderingTemplate(schema_version, profile, format, content, path)
```

Writes `output_path` (the fragment text, containing `{{title}}`/
`{{body}}`/`{{media_dir}}` placeholders) and a `<output_path>.meta.json`
sidecar recording `schema_version`/`profile`/`format`.

Raises `UnknownTemplateProfileError`/`UnknownTemplateFormatError` for an
unrecognized `profile`/`fmt`.

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

## Dependencies

None beyond the Python standard library.

