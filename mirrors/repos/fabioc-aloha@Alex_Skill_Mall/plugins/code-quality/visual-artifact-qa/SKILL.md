---
type: skill
lifecycle: stable
inheritance: inheritable
name: visual-artifact-qa
description: Visual output that passes static checks can still fail to render:
tier: standard
applyTo: '**/*visual*,**/*artifact*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Visual Artifact QA

## The Problem

Visual output that passes static checks can still fail to render:

- SVG validates but doesn't display correctly
- CSS passes linting but looks wrong
- HTML is valid but layout breaks
- No CI check catches visual regressions

## The Solution

Render → View → Diff loop.

```
┌─────────────┐
│   Render    │ Generate the visual artifact
└──────┬──────┘
       ▼
┌─────────────┐
│    View     │ Actually look at it (image tool, browser)
└──────┬──────┘
       ▼
┌─────────────┐
│    Diff     │ Compare against intent/previous version
└──────┬──────┘
       ▼
┌─────────────┐
│    Fix      │ Correct issues found
└──────┬──────┘
       │
       └──────► Repeat until correct
```

## For SVG Banners

```javascript
// 1. Render
const svg = generateBanner(config);
fs.writeFileSync('banner.svg', svg);

// 2. View (convert to PNG for preview)
const sharp = require('sharp');
await sharp('banner.svg').png().toFile('banner-preview.png');

// 3. Diff against expected
// - Text readable?
// - Colors correct?
// - Layout as designed?

// 4. Fix and re-render
```

## For CSS Changes

```javascript
// 1. Apply change
// 2. View in browser (all breakpoints)
// 3. Screenshot comparison
await page.screenshot({ path: 'after.png' });
// 4. Diff with before.png
```

## Automation Limits

| Check Type | Automated? | Notes |
|------------|------------|-------|
| Valid syntax | Yes | Lint, validate |
| Renders without error | Partial | Can detect crashes |
| Looks correct | No | Human judgment required |
| Matches design | No | Needs visual comparison |

## Verification

1. Artifact renders in target environment
2. Visual output matches intent
3. Changes are intentional (diff reviewed)

## When to Apply

- SVG generation
- PDF generation
- Email templates
- Any visual output that humans see

## Tags

`quality` `visual` `testing` `qa`
