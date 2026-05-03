---
type: skill
lifecycle: stable
inheritance: inheritable
name: "md-scaffold"
description: Scaffold properly structured Markdown files from templates for clean first-pass conversion
tier: standard
applyTo: '**/*scaffold*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Markdown Scaffolder


> Start right, convert clean — templates that work with every converter

Generate properly structured Markdown files from battle-tested templates. Each template includes correct frontmatter, extended syntax examples, converter directives, and navigation sentinels so documents convert cleanly on first pass.

---

## When to Use

- Starting a new document that will be converted to Word, PDF, or email
- Need a consistent structure for reports, tutorials, or reference guides
- Want converter-ready Markdown with correct frontmatter from the start
- Creating Gamma-ready slide decks from Markdown
- Ensuring consistent document structure across a team
- Setting up documentation for a new project

---

## Available Templates

| Template | Purpose | Includes |
|----------|---------|----------|
| `report` | Formal report with TOC | Executive summary, sections, appendix, tables |
| `tutorial` | Step-by-step guide | Prerequisites, learning objectives, exercises |
| `reference` | CLI/API reference | Commands, parameters, examples |
| `slides` | Gamma-ready presentation | H2 slide breaks, speaker notes format |
| `email` | Newsletter/governance email | YAML frontmatter for RFC 5322 headers |

---

## Usage

```bash
# Create a report
node .github/muscles/md-scaffold.cjs report "Quarterly Review"

# Create a tutorial with custom output path
node .github/muscles/md-scaffold.cjs --output docs/guide.md tutorial "Getting Started"

# List available templates
node .github/muscles/md-scaffold.cjs --list

# Create slides for a presentation
node .github/muscles/md-scaffold.cjs slides "Sprint Demo"

# Create email template
node .github/muscles/md-scaffold.cjs email "Weekly Update"
```

---

## Options Reference

| Option | Description |
|--------|-------------|
| `--output PATH` | Custom output path (default: title-slugified.md) |
| `--list` | List all available templates |
| `--author NAME` | Set author in frontmatter |
| `--force` | Overwrite existing file |

---

## Template Design Principles

1. **Converter-ready**: Every template produces Markdown that passes `markdown-lint.cjs` on first run
2. **Navigation sentinels**: `<!-- nav:start -->` / `<!-- nav:end -->` markers for `nav-inject.cjs`
3. **Frontmatter included**: Correct YAML frontmatter for the target converter
4. **Extended syntax**: Callouts, kbd shortcuts, highlights, and other extended Markdown features
5. **Minimal editing**: Fill in content, delete unused sections — ready to convert

---

## Template Details

### Report Template

```yaml
---
title: "{{title}}"
author: "{{author}}"
date: "{{date}}"
style: professional
toc: true
---
```

Includes:

- Executive Summary
- Background
- Analysis with tables
- Recommendations
- Appendix
- Nav sentinels

### Tutorial Template

```yaml
---
title: "{{title}}"
author: "{{author}}"
date: "{{date}}"
difficulty: intermediate
time: "30 minutes"
---
```

Includes:

- Learning Objectives
- Prerequisites
- Step-by-step sections
- Exercises
- Summary
- Next Steps

### Reference Template

```yaml
---
title: "{{title}}"
version: "1.0.0"
date: "{{date}}"
---
```

Includes:

- Synopsis
- Commands table
- Options table
- Examples
- Exit codes
- See Also

### Slides Template

```yaml
---
title: "{{title}}"
author: "{{author}}"
date: "{{date}}"
format: gamma
---
```

Includes:

- H2 slide breaks
- Speaker notes format `<!-- notes: -->`
- Image placeholders
- Bullet point structure

### Email Template

```yaml
---
to: recipient@example.com
from: sender@example.com
subject: "{{title}}"
cc: 
reply-to: 
---
```

Includes:

- Greeting
- Body sections
- Call to action
- Signature

---

## Workflow Integration

### New Project Documentation

```bash
# Scaffold initial docs
node .github/muscles/md-scaffold.cjs report "Project Charter"
node .github/muscles/md-scaffold.cjs reference "CLI Reference"
node .github/muscles/md-scaffold.cjs tutorial "Getting Started"
```

### Convert to Distribution Format

```bash
# Scaffold → Edit → Convert
node .github/muscles/md-scaffold.cjs report "Q4 Review"
# ... edit quarterly-review.md ...
node .github/muscles/md-to-word.cjs quarterly-review.md --style professional
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| File already exists | Default won't overwrite | Use `--force` or `--output` |
| Template not found | Typo in template name | Use `--list` to see options |
| Frontmatter invalid | Manual editing broke YAML | Re-scaffold or fix YAML syntax |

---

## Requirements

- Node.js 18+

---

## Muscle Script

`.github/muscles/md-scaffold.cjs` (v1.0.0)

---

## Related Skills

- **md-to-word** — Convert scaffolded docs to Word
- **md-to-html** — Convert scaffolded docs to HTML
- **md-to-eml** — Convert email templates to .eml
- **lint-clean-markdown** — Validate scaffolded output
- **nav-inject** — Inject navigation using sentinels
- **gamma-presentation** — Alternative for Gamma slides

---

*Skill version: 2.0.0 | Last updated: 2026-04-14 | Category: document-conversion*
