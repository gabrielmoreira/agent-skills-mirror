---
type: skill
lifecycle: stable
inheritance: inheritable
name: svg-graphics
description: Scalable, accessible, theme-aware visuals
tier: extended
applyTo: '**/*svg*,**/*graphics*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# SVG Graphics Skill


> Scalable, accessible, theme-aware visuals.

## Why SVG

- Scales infinitely (retina, print)
- Text is searchable/accessible
- CSS-styleable (dark mode)
- Small file size
- Version control friendly

## Banner Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300">
  <rect width="100%" height="100%" fill="#1a1a2e"/>
  <text x="50" y="100" font-size="48" fill="#fff" font-family="system-ui">
    Project Name
  </text>
  <text x="50" y="150" font-size="24" fill="#888">One-line description</text>
</svg>
```

## Key Techniques

| Technique | Use Case |
|-----------|----------|
| `viewBox` | Responsive scaling |
| `<defs>` + `<use>` | Reusable components |
| `<linearGradient>` | Modern backgrounds |
| `<clipPath>` | Shaped containers |
| CSS variables | Theme switching |

## Dark/Light Mode

```xml
<style>
  @media (prefers-color-scheme: dark) {
    .bg { fill: #1a1a2e; }
    .text { fill: #ffffff; }
  }
  @media (prefers-color-scheme: light) {
    .bg { fill: #ffffff; }
    .text { fill: #1a1a2e; }
  }
</style>
```

## Icon Guidelines

| Size | Use |
|------|-----|
| 16x16 | Favicon, small UI |
| 32x32 | Tab icon, lists |
| 128x128 | App icon |
| 512x512 | Store listing |

## SMIL Animation

### Fade-In Pattern

```xml
<g opacity="0">
  <text x="50" y="100" font-size="48" fill="#fff">Title</text>
  <animate attributeName="opacity" from="0" to="1" dur="0.8s" begin="0.5s" fill="freeze"/>
</g>
```

| Attribute | Purpose |
|-----------|---------|
| `begin` | Delay before start |
| `dur` | Animation duration |
| `fill` | `"freeze"` (keep state) or `"remove"` (revert) |

### Staggered Entrance

Increment `begin` by 0.3s per element for smooth staggering.

**Note**: GitHub README renders SVG statically — animations won't play.

## CSS Transforms

### Nested Group Pattern

Separate position and animation transforms:

```xml
<!-- Outer: position -->
<g transform="translate(600, 150)">
  <!-- Inner: animation -->
  <g>
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>
    <circle r="20" fill="#4a90d9"/>
  </g>
</g>
```

**Rule**: Never mix static positioning and animated transforms on the same element.

## ClipPath Layers

3-layer pattern for shaped containers:

```xml
<defs>
  <clipPath id="card">
    <rect x="50" y="50" width="400" height="200" rx="16"/>
  </clipPath>
</defs>

<!-- Layer 1: Background -->
<rect x="50" y="50" width="400" height="200" rx="16" fill="#f6f8fa"/>

<!-- Layer 2: Clipped content -->
<g clip-path="url(#card)">
  <image href="photo.jpg" x="50" y="50" width="400" height="200"/>
</g>

<!-- Layer 3: Border (on top) -->
<rect x="50" y="50" width="400" height="200" rx="16" fill="none" stroke="#d1d9e0" stroke-width="2"/>
```

## Optimization

### SVGO Config

```json
{
  "plugins": [
    "preset-default",
    { "name": "removeViewBox", "active": false },
    { "name": "removeDimensions", "active": true }
  ]
}
```

**Critical**: Never remove `viewBox` (breaks scaling) or `<title>` (breaks accessibility).

### Size Budget

| Type | Target | Max |
|------|--------|-----|
| Icon | < 1 KB | 2 KB |
| Badge | < 2 KB | 5 KB |
| Banner | < 10 KB | 25 KB |
| Diagram | < 25 KB | 50 KB |

## Accessibility

- `role="img"` on decorative SVGs
- `<title>` for screen readers
- Sufficient contrast (4.5:1 min)
- `aria-hidden="true"` if purely decorative

## SVG vs Mermaid

| Scenario | SVG | Mermaid |
|----------|-----|---------|
| README branding | ✅ | ❌ |
| Dev docs flow | ❌ | ✅ |
| Dark/light theme | ✅ | ⚠️ |
| High-DPI output | ✅ | ⚠️ |

## Illustration: Organic Shapes

### The Snowman Problem

AI defaults to stacking circles — producing geometric snowmen. Real subjects need `<path>` with Bezier curves.

**Mandatory Rules**:

1. Start with silhouette — outline must be identifiable alone
2. Use `<path>` with curves for ALL organic shapes
3. Get proportions right before details
4. Count limbs correctly (quadrupeds have 4 legs)

### Feature Table

| Animal | Key Features | Common Mistake |
|--------|--------------|----------------|
| Dog | Snout, floppy ears on SIDE, 4 legs | Flat face, ears on top |
| Cat | Pointed ears on TOP, whiskers, slender | No whiskers, stocky |
| Bird | Beak, wings, 2 legs, NO arms | 4 legs, arms not wings |

### Path-First Approach

```xml
<!-- Dog body outline - single path defining silhouette -->
<path d="M 120,180 C 120,140 140,110 180,105 C 210,100 250,100 280,110..." 
      fill="#c89050" stroke="#6b4226" stroke-width="2"/>
```

**Why**: Silhouette reads as "dog" even without color. ALL shapes use `<path>` — no perfect circles.

## Tools

| Tool | Purpose |
|------|---------|
| SVGO | Optimize/minify |
| Inkscape | Visual editing |
| svg-to-png | Rasterization |
