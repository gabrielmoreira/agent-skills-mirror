---
name: content-validate-rendering-template
plugin: structured-content-rendering
description: Validates a RenderingTemplate (from create-markdown-rendering-template or create-aspx-rendering-template) for schema/placeholder/required-section/format-profile-compatibility correctness -- known profile/format, required placeholders present, no unknown placeholder tokens, title placed inside an actual heading construct, and (ASPX only) no full-page wrapper tags. Validates the template definition itself, not rendered output (that is validate-rendered-output's job).
allowed-tools: Bash, Read
examples:
  - "python -c \"import templates, template_validation as tv; t = templates.load_rendering_template('page.template.md'); print(tv.validate_rendering_template(t).status)\""
---

# Validate Rendering Template

## Trigger and Purpose

Use this skill to validate a `RenderingTemplate` (produced by
`create-markdown-rendering-template` or `create-aspx-rendering-template`,
or loaded via `templates.load_rendering_template`) before it is relied
on. Detects:

- unknown `profile`/`format`;
- missing required placeholders (`{{title}}`, `{{body}}`);
- unknown placeholder tokens (anything outside `{{title}}`, `{{body}}`,
  `{{media_dir}}`);
- `{{title}}` not placed inside an actual heading construct (a markdown
  `#`-prefixed line, or an ASPX `<h1>`-`<h6>` tag) -- a template with a
  bare, unheaded title placeholder would render pages with no real
  heading element;
- (ASPX only) a full-page `<html>`/`<head>`/`<body>` wrapper -- ASPX
  rendering templates must be bare fragments for `Add-PnPPageTextPart`;
  raw wrapped `.aspx` upload is a confirmed `Access denied` platform
  boundary (Phase 3.0 Sec.15).

This validates the *template definition itself* — not rendered output.
Rendered-output validation (broken links, missing pages, stale source
hash) is `validate-rendered-output`'s separate job
(`renderers/validate_rendered.py`).

## Public Interface

```python
from templates import load_rendering_template
from template_validation import validate_rendering_template

template = load_rendering_template("path/to/page.template.md")
report = validate_rendering_template(template)
# TemplateValidationReport(status="PASS"|"FAIL", issues=[...])
```

Every issue is `severity="error"` — status is always `PASS` or `FAIL`,
never `WARN` (nothing about a malformed template is a reviewable
discrepancy the way a canonical-content heading-drift smell might be).

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

## Dependencies

None beyond the Python standard library.

