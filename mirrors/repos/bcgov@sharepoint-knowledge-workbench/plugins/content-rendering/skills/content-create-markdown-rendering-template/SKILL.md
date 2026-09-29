---
name: content-create-markdown-rendering-template
plugin: structured-content-rendering
description: Instantiates a new Markdown rendering (page-structure) template file from this plugin's canonical generic or standard-manual starter -- headings, body, and media placeholders, backed by real Phase 1-2 Standard Manual rendered-output evidence. Not an agent/native-skill instruction template (that is Task 0.7/0.8's separate template system).
allowed-tools: Bash, Read
examples:
  - "python -c \"import templates; templates.create_rendering_template('generic', 'markdown', 'out/page.template.md')\""
---

# Create Markdown Rendering Template

## Trigger and Purpose

Use this skill to instantiate a new Markdown *rendering* template file
(page/document layout -- headings, body, metadata placement, media
placement) for a given profile. Two profiles are currently defined:

- `generic` — the plugin's default page shape.
- `standard-manual` — the standard-manual variant, structurally confirmed against
  real rendered evidence at `runs/standard-manual-manual-v2/render/rendered-output/
  pages/` (a level-2 heading directly followed by body content, no front
  matter).

This is a *rendering* template — document/page structure, headings,
body, media placement, human-facing layout. It is distinct from Task
0.7/0.8's *agent/native-skill* template system (agent instructions,
answer formatting) — the two are never merged.

## Public Interface

```python
from templates import create_rendering_template

template = create_rendering_template(
    profile="generic",  # or "standard-manual"
    fmt="markdown",
    output_path="path/to/new-template.md",
)
# RenderingTemplate(schema_version, profile, format, content, path)
```

Writes `output_path` (the template text, containing `{{title}}`/
`{{body}}`/`{{media_dir}}` placeholders) and a `<output_path>.meta.json`
sidecar recording `schema_version`/`profile`/`format`, so a later
`validate-rendering-template` or `load_rendering_template` call can
recover them without re-parsing the template body.

Raises `UnknownTemplateProfileError`/`UnknownTemplateFormatError` for an
unrecognized `profile`/`fmt`.

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

## Dependencies

None beyond the Python standard library.

