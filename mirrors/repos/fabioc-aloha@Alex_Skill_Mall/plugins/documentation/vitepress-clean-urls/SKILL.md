---
type: skill
lifecycle: stable
inheritance: inheritable
name: vitepress-clean-urls
description: With `cleanUrls: true`, nav links must NOT have `.html` extensions:
tier: extended
applyTo: '**/*vitepress*,**/*clean*,**/*urls*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# VitePress Clean URLs

## The Problem

With `cleanUrls: true`, nav links must NOT have `.html` extensions:

```javascript
// vitepress.config.js
export default {
  cleanUrls: true  // URLs become /guide/intro instead of /guide/intro.html
}
```

```javascript
// Bad: will 404
nav: [
  { text: 'Guide', link: '/guide/intro.html' }  // Wrong!
]

// Also bad in markdown
[Read more](/guide/intro.html)  // Wrong!
```

## The Solution

When `cleanUrls: true`, use extensionless paths everywhere.

```javascript
// Good
nav: [
  { text: 'Guide', link: '/guide/intro' }
]

sidebar: [
  { text: 'Introduction', link: '/guide/intro' }
]
```

```markdown
<!-- In markdown files -->
[Read more](/guide/intro)
[See API](/api/methods)
```

## Common Gotchas

| Pattern | cleanUrls: false | cleanUrls: true |
|---------|------------------|-----------------|
| Nav links | `/guide.html` | `/guide` |
| Sidebar links | `/api/foo.html` | `/api/foo` |
| Markdown links | `[text](./page.html)` | `[text](./page)` |
| External links | Unchanged | Unchanged |

## Migration Script

```javascript
// scripts/remove-html-extensions.cjs
const glob = require('glob');
const fs = require('fs');

glob.sync('docs/**/*.md').forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  // Replace .html) with ) and .html] with ]
  content = content.replace(/\.html\)/g, ')');
  content = content.replace(/\.html\]/g, ']');
  fs.writeFileSync(file, content);
});
```

## Verification

```bash
# Find remaining .html links
grep -rn '\.html[)\]]' docs/

# Should return nothing
```

## When to Apply

- Enabling `cleanUrls: true` in existing project
- Migrating from other static site generators
- Any VitePress project setup

## Tags

`vitepress` `urls` `configuration` `links`
