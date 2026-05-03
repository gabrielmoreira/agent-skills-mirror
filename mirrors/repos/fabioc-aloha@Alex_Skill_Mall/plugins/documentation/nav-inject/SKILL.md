---
type: skill
lifecycle: stable
inheritance: inheritable
name: "nav-inject"
description: Inject cross-document navigation tables into multi-file Markdown documentation suites
tier: standard
applyTo: '**/*nav*,**/*inject*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Navigation Injector


> One config, every file navigable -- keep multi-doc suites connected

Reads a `nav.json` config and stamps a navigation table into every `.md` file in a documentation suite. Eliminates manual navigation maintenance across multi-file document sets.

## When to Use

- Maintaining a multi-file documentation suite (governance, specs, guides)
- Need consistent cross-document navigation across all Markdown files
- Want to update navigation in one place and propagate everywhere
- Preparing document suites for Word/PDF conversion with navigation links

## How It Works

1. Define a `nav.json` with the list of documents, labels, and icons
2. Run `nav-inject.cjs` -- it finds `<!-- nav:start -->` / `<!-- nav:end -->` sentinels in each file
3. The navigation table is generated and injected between sentinels
4. Run again after adding/removing files -- only sentinel content is replaced

## Usage

```bash
# Initialize a starter nav.json
node .github/muscles/nav-inject.cjs --init

# Inject navigation into all files
node .github/muscles/nav-inject.cjs nav.json

# Preview changes without writing
node .github/muscles/nav-inject.cjs nav.json --dry-run
```

## nav.json Format

```json
{
  "title": "Project Documentation",
  "style": "table",
  "position": "top",
  "files": [
    { "path": "README.md", "label": "Overview", "icon": "📋" },
    { "path": "SETUP.md", "label": "Setup Guide", "icon": "🔧" },
    { "path": "API.md", "label": "API Reference", "icon": "📡" }
  ]
}
```

## Output Styles

| Style | Format | Best For |
|-------|--------|----------|
| `table` | Markdown table with icons and descriptions | Formal documentation suites |
| `list` | Bullet list with links | Lightweight nav headers |

## Sentinel Markers

Every target file must contain these markers (added automatically by `md-scaffold.cjs`):

```markdown
<!-- nav:start -->
<!-- nav:end -->
```

The injector replaces only the content between sentinels, preserving all other content.

## Output Example

Given a `nav.json` with three files, the injected navigation looks like:

```markdown
<!-- nav:start -->
| | Document | Description |
|---|----------|-------------|
| 📋 | [Overview](README.md) | Project introduction |
| 🔧 | [Setup Guide](SETUP.md) | Installation and configuration |
| 📡 | [API Reference](API.md) | Endpoint documentation |
<!-- nav:end -->
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| File missing sentinels | Skipped with warning — never injects without markers |
| Empty `files` array | Removes content between sentinels (cleans up) |
| File listed in nav.json but missing on disk | Included in nav table (link may 404) — warns |
| Nested directories | Paths are relative to nav.json location |
| Duplicate entries | Rendered as-is — no deduplication |

## Integration with md-to-word

When converting a doc suite to Word, run `nav-inject` first so the navigation table is included in the converted document. The table renders as a standard markdown table in Word output.
