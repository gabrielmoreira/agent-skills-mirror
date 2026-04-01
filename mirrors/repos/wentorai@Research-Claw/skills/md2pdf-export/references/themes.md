# CSS Themes Reference

## Built-in Themes

The converter ships with three built-in themes:

### `github` (default)
- Light theme mimicking GitHub's Markdown rendering
- Sans-serif font stack: system UI → Helvetica → Arial
- Max width 980px, centered
- Subtle borders on h1/h2, striped tables
- Best for: documentation, READMEs, technical reports

### `github-dark`
- Dark variant of the GitHub theme
- Background: `#0d1117`, text: `#c9d1d9`
- Appropriate for dark-mode documents or presentations
- Best for: slides, developer documentation for dark-mode readers

### `minimal`
- Serif body font (Georgia), clean and readable
- Narrower width (700px) for better readability
- Lighter borders, more whitespace
- Best for: essays, papers, articles, long-form content

## Creating a Custom Theme

A theme is just a CSS string. To add a custom theme:

### Option 1: Extend md2pdf.js

```javascript
const { THEMES, convertMarkdown } = require('./md2pdf.js');

// Add custom theme
THEMES['academic'] = `
  body {
    font-family: "Computer Modern", "Latin Modern Roman", serif;
    font-size: 12pt;
    line-height: 1.5;
    max-width: 6.5in;
    margin: 0 auto;
    padding: 1in;
  }
  h1 { font-size: 1.5em; text-align: center; margin-bottom: 2em; }
  h2 { font-size: 1.2em; margin-top: 1.5em; }
  /* ... */
`;

convertMarkdown({ inputPath: 'paper.md', theme: 'academic' });
```

### Option 2: Use front-matter CSS injection

```yaml
---
puppeteer:
  format: A4
---

<style>
  body { font-family: "Noto Serif CJK SC", serif; }
  h1 { color: #c41e3a; }
</style>

# My Document
```

The `<style>` tag in Markdown body is rendered as-is into the HTML,
so it overrides the base theme.

### Option 3: Print-specific CSS

Use `@media print` to apply styles only in PDF output:

```yaml
---
puppeteer:
  format: A4
---

<style>
@media print {
  body { font-size: 10pt; }
  .no-print { display: none; }
  h1 { page-break-before: always; }
  h1:first-of-type { page-break-before: avoid; }
}
</style>
```

## Page Break Control

Insert page breaks in your Markdown:

```markdown
Some content on page 1.

<!-- pagebreak -->

This starts on a new page.
```

CSS-based page breaks also work:

```css
h1 { page-break-before: always; }
table { page-break-inside: avoid; }
```
