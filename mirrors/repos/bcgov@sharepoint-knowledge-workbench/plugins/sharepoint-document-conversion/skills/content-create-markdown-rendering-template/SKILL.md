---
name: content-create-markdown-rendering-template
plugin: sharepoint-document-conversion
description: Instantiates a new local Markdown rendering (page-structure) template file on disk from the plugin's canonical generic or standard-manual starter, with heading, body and media placeholders. Use when you need a new page layout template for Markdown output. Not an agent or native-skill instruction template.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import templates; templates.create_rendering_template('generic', 'markdown', 'out/page.template.md')\""
---

# Create Markdown Rendering Template

Write a new Markdown rendering template for the `generic` or `standard-manual` profile.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- This is a rendering (page layout) template. Never mix it with the agent or native-skill template system.
- Only the `generic` and `standard-manual` profiles exist; an unknown `profile` or `fmt` raises
  `UnknownTemplateProfileError` or `UnknownTemplateFormatError`.
- Placeholders are limited to `{{title}}`, `{{body}}` and `{{media_dir}}`.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from templates import create_rendering_template
t = create_rendering_template(profile="generic", fmt="markdown", output_path="out/page.template.md")
```

## Workflow

1. Choose the profile (`generic` or `standard-manual`) and the output path.
2. Call `create_rendering_template(profile, "markdown", output_path)`. It writes the template and a
   `<output_path>.meta.json` sidecar.
3. Validate the result with `content-validate-rendering-template`.

## Verification

Confirm both the template file and its `.meta.json` sidecar exist, then validate the template.

## References

- [Template profiles](references/rendering-template-profiles.md): read for profile definitions, placeholders,
  the sidecar file and validation rules.
