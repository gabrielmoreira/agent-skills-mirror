---
type: skill
lifecycle: stable
inheritance: inheritable
name: vitepress-iframe-embed
description: VitePress iframe embedding gotchas — CSP headers, sandboxing, responsive sizing
tier: extended
applyTo: '**/*vitepress*,**/*iframe*,**/*embed*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# VitePress Iframe Embed

**Category**: VitePress
**Time Saved**: 1 hour debugging SPA routing
**Battle-tested**: Yes — embedding standalone HTML in VitePress sites

---

## The Problem

You have a standalone HTML application (a dashboard, interactive tool, or legacy page) that you want to include in your VitePress documentation site. You add a link in the nav, but clicking it either shows a blank page or VitePress intercepts the navigation.

## Why It Happens

VitePress is a Single Page Application (SPA). It intercepts all navigation clicks to provide smooth page transitions. When you link to a non-VitePress HTML file, the SPA router doesn't know what to do with it.

## The Rule

**Use the iframe embed pattern: Create a `.md` page with a Vue component that embeds your HTML via iframe.**

## The Pattern

### Step 1: Create Wrapper Markdown Page

```markdown
<!-- docs/tools/dashboard.md -->
---
title: Dashboard
---

<DashboardEmbed />
```

### Step 2: Create Vue Component

```vue
<!-- docs/.vitepress/components/DashboardEmbed.vue -->
<template>
  <div class="embed-container">
    <iframe 
      :src="iframeSrc" 
      frameborder="0"
      class="embed-frame"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const iframeSrc = computed(() => {
  // Add ?embed query param for the HTML to detect
  return '/tools/dashboard.html?embed'
})
</script>

<style scoped>
.embed-container {
  width: 100%;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.embed-frame {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
```

### Step 3: Register Component

```javascript
// docs/.vitepress/theme/index.js
import DefaultTheme from 'vitepress/theme'
import DashboardEmbed from '../components/DashboardEmbed.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('DashboardEmbed', DashboardEmbed)
  }
}
```

### Step 4: Modify HTML to Detect Embed Mode

```html
<!-- public/tools/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Hide chrome when embedded */
    .embed-mode header,
    .embed-mode footer,
    .embed-mode .nav { display: none; }
    
    .embed-mode main { padding: 0; margin: 0; }
  </style>
</head>
<body>
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
  
  <script>
    // Detect embed mode from URL
    if (window.location.search.includes('embed')) {
      document.body.classList.add('embed-mode');
    }
  </script>
</body>
</html>
```

## Alternative: Force Full Navigation

If you don't need seamless integration, use `target="_self"`:

```javascript
// docs/.vitepress/config.js
export default {
  themeConfig: {
    nav: [
      { text: 'Dashboard', link: '/tools/dashboard.html', target: '_self' }
    ]
  }
}
```

This forces a full page navigation, bypassing the SPA router.

## CSS Isolation Note

Iframes cannot access parent CSS custom properties. If your embedded HTML uses VitePress CSS variables, provide fallbacks:

```css
/* In embedded HTML */
:root {
  --vp-c-brand: #646cff;  /* Fallback, not inherited */
}
```

## Nav Configuration

```javascript
// docs/.vitepress/config.js
export default {
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Docs', link: '/guide/' },
      { text: 'Dashboard', link: '/tools/dashboard' }  // Points to .md wrapper
    ]
  }
}
```

## File Structure

```
docs/
  .vitepress/
    components/
      DashboardEmbed.vue
    theme/
      index.js
    config.js
  tools/
    dashboard.md          # Wrapper page
  public/
    tools/
      dashboard.html      # Actual HTML app
```

## Verification Checklist

- [ ] Wrapper `.md` page created
- [ ] Vue component renders iframe
- [ ] HTML detects `?embed` and hides chrome
- [ ] Nav links to wrapper page, not HTML directly
- [ ] CSS fallbacks for iframe isolation
- [ ] Test navigation from VitePress pages

## Common Symptoms

- Blank page when clicking nav link
- URL changes but content doesn't load
- VitePress layout appears but content area empty
- "Page not found" for HTML files

## Related Skills

- `github-wiki-flat` — Similar link rewriting issues
