---
type: skill
lifecycle: stable
inheritance: inheritable
name: config-content-separation
description: Mixing structure and content makes both hard to maintain:
tier: standard
applyTo: '**/*config*,**/*content*,**/*separation*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Config + Content Separation

## The Problem

Mixing structure and content makes both hard to maintain:

```javascript
// Bad: structure and content interleaved
const menu = [
  { label: 'Home', icon: 'house', content: 'Welcome to our site...' },
  { label: 'About', icon: 'info', content: 'We are a company that...' }
];
```

Content updates require touching code. Structure changes require editing content.

## The Solution

JSON defines structure. Separate files hold content.

```json
// config/menu.json
{
  "items": [
    { "id": "home", "label": "Home", "icon": "house", "contentFile": "home.md" },
    { "id": "about", "label": "About", "icon": "info", "contentFile": "about.md" }
  ]
}
```

```markdown
<!-- content/home.md -->
# Welcome

Welcome to our site. We're glad you're here.
```

```javascript
// Loader resolves file references at runtime
function loadMenu(configPath, contentDir) {
  const config = require(configPath);
  
  return config.items.map(item => ({
    ...item,
    content: fs.readFileSync(path.join(contentDir, item.contentFile), 'utf8')
  }));
}
```

## Caching Pattern

```javascript
let cache = null;
let cacheTime = 0;
const CACHE_TTL = 60000; // 1 minute

function getMenu(refresh = false) {
  if (!refresh && cache && Date.now() - cacheTime < CACHE_TTL) {
    return cache;
  }
  
  cache = loadMenu('./config/menu.json', './content');
  cacheTime = Date.now();
  return cache;
}

// Force refresh on explicit request
app.post('/admin/refresh-content', (req, res) => {
  getMenu(true);
  res.json({ status: 'refreshed' });
});
```

## Benefits

- Content authors edit markdown, not JSON
- Developers edit structure without touching content
- Version control diffs are meaningful (content vs structure)
- Can hot-reload content without rebuilding

## Verification

1. Change content file → reflected without code change
2. Change structure → content unchanged
3. Missing content file → clear error message

## When to Apply

- CMS-like systems
- Documentation sites
- Configuration panels
- Any mix of structure + prose

## Tags

`build` `architecture` `content-management` `configuration`
