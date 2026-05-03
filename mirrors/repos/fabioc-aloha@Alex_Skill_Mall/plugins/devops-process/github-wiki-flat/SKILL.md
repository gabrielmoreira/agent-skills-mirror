---
type: skill
lifecycle: stable
inheritance: inheritable
name: github-wiki-flat
description: GitHub Wiki has a flat namespace — no real folders, sidebar ordering tricks, link gotchas
tier: standard
applyTo: '**/*github*,**/*wiki*,**/*flat*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# GitHub Wiki Is Flat

**Category**: GitHub
**Time Saved**: 1-2 hours debugging broken links
**Battle-tested**: Yes — wiki publishing automation

---

## The Problem

You organize your wiki source files in a nice folder structure:

```
wiki/
  getting-started/
    installation.md
    configuration.md
  api/
    endpoints.md
    authentication.md
```

You push to GitHub Wiki. All your internal links break. Pages appear at root level with mangled names.

## Why It Happens

GitHub Wiki has **no folder hierarchy**. Every page renders at the wiki root. Folders in your source become part of the page name (with dashes).

```
wiki/getting-started/installation.md
  → renders at: /wiki/getting-started-installation

wiki/api/endpoints.md  
  → renders at: /wiki/api-endpoints
```

## The Rules

### 1. All Pages Render at Root

```
Source: docs/guide/setup.md
URL:    github.com/user/repo/wiki/guide-setup

NOT:    github.com/user/repo/wiki/guide/setup  ❌
```

### 2. Links Must Use Flat Names

```markdown
<!-- In wiki/getting-started/installation.md -->

<!-- ❌ WRONG — relative path -->
See [configuration](./configuration.md)

<!-- ✅ CORRECT — flat wiki name -->
See [configuration](getting-started-configuration)

<!-- ❌ WRONG — assumes hierarchy -->
See [endpoints](../api/endpoints.md)

<!-- ✅ CORRECT — flat wiki name -->
See [endpoints](api-endpoints)
```

### 3. _Sidebar.md Is Ground Truth

The sidebar defines your navigation. All links in `_Sidebar.md` must use flat names:

```markdown
<!-- _Sidebar.md -->

**Getting Started**
- [Installation](getting-started-installation)
- [Configuration](getting-started-configuration)

**API Reference**  
- [Endpoints](api-endpoints)
- [Authentication](api-authentication)
```

## Link Rewriting Automation

If you maintain wiki source in a folder structure, automate link rewriting on publish:

```javascript
function rewriteWikiLinks(content, sourceDir) {
  // Convert relative paths to flat wiki names
  return content.replace(
    /\[([^\]]+)\]\(\.?\/?([^)]+)\.md\)/g,
    (match, text, path) => {
      // ./sibling.md → folder-sibling
      // ../other/page.md → other-page
      const flatName = path
        .replace(/^\.\.?\/?/, '')
        .replace(/\//g, '-');
      return `[${text}](${flatName})`;
    }
  );
}
```

## Source Code Links

Links to source code from wiki need full repo URLs:

```markdown
<!-- ❌ WRONG — wiki-relative path -->
See [source](../src/index.ts)

<!-- ✅ CORRECT — full GitHub URL -->
See [source](https://github.com/user/repo/blob/main/src/index.ts)
```

## Three Link Types to Handle

| Link Type | Source | Wiki Target |
|-----------|--------|-------------|
| Same folder | `./sibling.md` | `folder-sibling` |
| Cross folder | `../api/page.md` | `api-page` |
| Source code | `../../src/file.ts` | Full GitHub blob URL |

## Verification Checklist

- [ ] All internal links use flat wiki names
- [ ] _Sidebar.md uses flat names
- [ ] Source code links use full GitHub URLs
- [ ] Test links after wiki push
- [ ] Automate link rewriting if maintaining folder structure

## Common Symptoms

- "Wiki links work locally but break on GitHub"
- "404 errors on wiki pages"
- "Pages show folder names in titles"

## Related Skills

- `github-readme-override` — File hierarchy gotchas
