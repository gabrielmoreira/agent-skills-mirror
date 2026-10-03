---
name: content-create-aspx-rendering-template
plugin: content-rendering
description: Instantiates a new ASPX/modern-page rendering (page-structure) template file from the plugin's canonical generic or standard-manual starter, backed by the confirmed Add-PnPPage and Add-PnPPageTextPart fragment shape. Use when you need a new page layout template for SharePoint modern pages. Not an agent or native-skill instruction template, and never a raw wrapped .aspx page (confirmed Access denied).
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import templates; templates.create_rendering_template('generic', 'aspx', 'out/page.template.html')\""
---

# Create ASPX Rendering Template

Write a new ASPX/modern-page rendering template fragment for the `generic` or `standard-manual` profile.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Produce a bare fragment: a heading followed by body, with no `<html>`, `<head>` or `<body>` wrapper.
  That is the shape `Add-PnPPageTextPart` consumes. Raw wrapped `.aspx` upload to Site Pages is a confirmed
  `Access denied` platform boundary and this skill never produces it.
- This is a rendering (page layout) template. Never mix it with the agent or native-skill template system.
- An unknown `profile` or `fmt` raises `UnknownTemplateProfileError` or `UnknownTemplateFormatError`.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from templates import create_rendering_template
t = create_rendering_template(profile="generic", fmt="aspx", output_path="out/page.template.html")
```

## Workflow

1. Choose the profile (`generic` or `standard-manual`) and the output path.
2. Call `create_rendering_template(profile, "aspx", output_path)`. It writes the fragment (with `{{title}}`,
   `{{body}}`, `{{media_dir}}` placeholders) and a `<output_path>.meta.json` sidecar.
3. Validate the result with `content-validate-rendering-template`.

## Verification

Confirm the fragment and its `.meta.json` sidecar exist and that the fragment has no full-page wrapper tags.

## References

- [Template profiles](references/rendering-template-profiles.md): read for profile definitions, placeholders,
  the sidecar file and validation rules.
