---
name: content-validate-rendering-template
plugin: content-rendering
description: Validates a RenderingTemplate (from the Markdown or ASPX template-creation skills) for schema, placeholder, required-section and format-profile correctness. Use before relying on a template. Checks the template definition itself, not rendered output, which content-validate-rendered-output handles.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import templates, template_validation as tv; t = templates.load_rendering_template('page.template.md'); print(tv.validate_rendering_template(t).status)\""
---

# Validate Rendering Template

Validate a `RenderingTemplate` definition before it is relied on.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Validate the template definition only. Rendered-output checks (broken links, missing pages, stale source
  hash) belong to `content-validate-rendered-output`.
- Status is always `PASS` or `FAIL`, never `WARN`; every issue is an error.
- ASPX templates must be bare fragments: a full-page `<html>`/`<head>`/`<body>` wrapper fails validation.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from templates import load_rendering_template
from template_validation import validate_rendering_template
report = validate_rendering_template(load_rendering_template("path/to/page.template.md"))
# TemplateValidationReport(status="PASS"|"FAIL", issues=[...])
```

## Workflow

1. Load the template with `load_rendering_template` (it reads the `.meta.json` sidecar).
2. Call `validate_rendering_template`.
3. Report the status and each issue.

## Verification

Status must be `PASS`. A `FAIL` lists the cause: unknown profile or format, a missing required placeholder,
an unknown placeholder, `{{title}}` outside a heading construct, or an ASPX wrapper tag.

## References

- [Template profiles](references/rendering-template-profiles.md): read for the full rule list, allowed
  placeholders and profile definitions.
