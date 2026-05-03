---
type: skill
lifecycle: stable
inheritance: inheritable
name: vitepress-spa-routing
description: VitePress intercepts all navigation clicks for SPA routing:
tier: extended
applyTo: '**/*vitepress*,**/*spa*,**/*routing*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# VitePress SPA Routing

## The Problem

VitePress intercepts all navigation clicks for SPA routing:

```html
<!-- This link will be handled by VitePress router -->
<a href="/external-app/">External App</a>

<!-- VitePress fetches /external-app/index.md instead of navigating -->
```

This breaks:

- Links to non-VitePress pages in the same domain
- Links to static HTML files
- Links to other apps hosted at subpaths

## The Solution

### Option 1: target="_self" (Force Full Navigation)

```javascript
// In .vitepress/config.js
nav: [
  { 
    text: 'External App', 
    link: '/app/',
    target: '_self'  // Forces full page navigation
  }
]
```

### Option 2: External Link

```javascript
nav: [
  { 
    text: 'External App', 
    link: 'https://same-domain.com/app/' // Full URL bypasses router
  }
]
```

### Option 3: Iframe Embed (See vitepress-iframe-embed skill)

For standalone HTML that should appear within VitePress layout.

## When Each Applies

| Scenario | Solution |
|----------|----------|
| Link to different app on same domain | `target: "_self"` |
| Link to truly external site | Full URL |
| Embed external content in VitePress layout | Iframe pattern |
| Link to static HTML file | `target: "_self"` |

## In Markdown

```markdown
<!-- Bad: VitePress intercepts -->
[Go to app](/app/)

<!-- Good: Force navigation -->
<a href="/app/" target="_self">Go to app</a>

<!-- Also good: Full URL -->
[Go to app](https://example.com/app/)
```

## Verification

1. Click the link
2. Browser should do full page load (network tab shows document request)
3. URL bar shows target URL (not VitePress route)

## When to Apply

- Multi-app deployments on same domain
- Static HTML files alongside VitePress
- Links to server-rendered pages

## Tags

`vitepress` `spa` `routing` `navigation`
