---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Convert Markdown to standalone HTML with embedded CSS, images, and Mermaid diagrams"
application: "When converting Markdown files to HTML for sharing, print, or offline viewing"
applyTo: "**/*.md"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Markdown to HTML Conversion

Auto-loaded for HTML conversion requests.

## Quick Reference

| Option | Usage |
|--------|-------|
| `--style professional` | Business docs (Segoe UI, blue headings) |
| `--style academic` | Papers/theses (Palatino, narrow width) |
| `--style minimal` | Clean modern (Inter font) |
| `--style dark` | Dark background |
| `--toc` | Add table of contents |
| `--mermaid-png` | High-quality diagram rendering |

## Command

```bash
node .github/muscles/md-to-html.cjs SOURCE.md [OUTPUT.html] [options]
```

## Automatic Handling

| Content | Behavior |
|---------|----------|
| Local images | Base64 embedded by default |
| YAML frontmatter | Extracted for title, stripped |
| Mermaid diagrams | Table fallback (or PNG with `--mermaid-png`) |
| Code blocks | Syntax highlighting |
| Tables | Striped rows, styled headers |

## Quality Checklist

### Before Conversion

- [ ] Source is valid Markdown (run lint-clean-markdown)
- [ ] Images exist at referenced paths
- [ ] Mermaid syntax is valid

### After Conversion

- [ ] Open HTML in browser to verify
- [ ] Check images render
- [ ] Print preview looks correct
- [ ] Diagrams display properly

## Common Patterns

| Use Case | Command |
|----------|---------|
| Business report | `--style professional --toc` |
| Academic paper | `--style academic --toc` |
| Quick share | `--style minimal` |
| Print-ready | `--style academic` (narrower width) |
| With diagrams | `--mermaid-png` |

## Do NOT

- Skip `--toc` for documents with many headings
- Use `--mermaid-png` without mermaid-cli installed
- Forget to verify output before sharing
