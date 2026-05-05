---
type: skill
lifecycle: stable
inheritance: inheritable
name: delivery-svg-markdown
description: Render data dashboards as static SVG panels embeddable in Markdown. Uses D3.js v7 mental model for scales, shapes, and axes. No runtime JS; output is pure SVG with inline styles for GitHub compatibility.
tier: standard
applyTo: '**/*svg*,**/*markdown*dashboard*,**/*visual*,**/*chart*render*'
currency: 2026-05-04
lastReviewed: 2026-05-04
---

# Delivery: SVG in Markdown

Render dashboards as static SVG panels that embed directly in Markdown files. The output works in GitHub READMEs, VS Code preview, and any browser. No JavaScript runtime, no external CSS, no build step.

This is the mid-tier delivery format: richer than ASCII (color, curves, precise positioning), simpler than HTML (no interactivity, no CDN). The agent uses D3.js concepts (scales, shape generators, axes) as a mental model for producing SVG markup, but the output is raw SVG text, not a running D3 program.

## When to Use

- Dashboards that live in GitHub repos (README, wiki, docs)
- Reports rendered in VS Code Markdown preview
- Static visual artifacts that need color, precise layout, or curves
- Anywhere SVG is supported but JavaScript is not (email clients with SVG support, static sites)

## When NOT to Use

- Interactive filtering, drill-through, or tooltips needed (use `delivery-html-dashboard`)
- Terminal-only consumers with no graphical display (use `delivery-ascii-dashboard`)
- PowerPoint or PDF required (use `delivery-slides` or `delivery-pdf-report`)
- The audience is non-technical and expects branded corporate visuals (use HTML or Power BI)

## Module 1: SVG Foundations

### Coordinate System

SVG uses a top-left origin with y increasing downward. All positioning uses the `viewBox` attribute for responsive scaling.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"
     width="800" height="600" font-family="system-ui, -apple-system, sans-serif">
```

| Constant | Default | Rationale |
| --- | --- | --- |
| Dashboard width | 800px | Fits GitHub's max content width (~888px) with margin |
| Panel height | 200-300px | Comfortable for a single chart |
| Margin (top) | 40px | Room for title |
| Margin (right) | 20px | Breathing room |
| Margin (bottom) | 50px | Room for x-axis labels |
| Margin (left) | 60px | Room for y-axis labels |
| Font size (title) | 16px | Readable, not dominant |
| Font size (labels) | 12px | Legible at default zoom |
| Font size (data) | 11px | Compact, scannable |

### GitHub Compatibility Rules

GitHub's SVG sanitizer strips many features. These constraints are non-negotiable:

| Feature | Allowed? | Alternative |
| --- | --- | --- |
| Inline `style` attributes | Yes | Use these exclusively |
| `<style>` blocks | No (stripped) | Inline styles instead |
| External CSS | No | Inline styles |
| JavaScript | No (stripped) | Not applicable (static) |
| `<foreignObject>` | No (stripped) | Use `<text>` elements |
| `xlink:href` for images | Partial | Avoid; use inline paths |
| Gradients (`<linearGradient>`) | Yes | Keep `<defs>` simple |
| Filters (`<filter>`) | Limited | Avoid complex filters |
| `clip-path` | Yes | Works for chart area clipping |
| Web fonts | No | Use system font stack |

### Inline Style Pattern

Every visual element carries its own style as attributes:

```xml
<rect x="60" y="100" width="120" height="30"
      fill="#4A90D9" stroke="none" rx="2"/>
<text x="120" y="150" text-anchor="middle"
      fill="#E0E0E0" font-size="12" font-weight="500">Label</text>
```

## Module 2: D3.js Mental Model

The agent does not run D3. It uses D3's conceptual framework to compute SVG coordinates mathematically.

### Scales (D3-scale concepts)

A scale maps a data domain to a visual range.

**Linear scale** (continuous values):
```
domain: [0, maxValue]
range: [marginLeft, width - marginRight]
map(value) = range[0] + (value - domain[0]) / (domain[1] - domain[0]) * (range[1] - range[0])
```

**Band scale** (categorical values):
```
domain: [categories...]
range: [marginLeft, width - marginRight]
bandwidth = (range[1] - range[0]) / domain.length * (1 - padding)
step = (range[1] - range[0]) / domain.length
map(category) = range[0] + index * step + (step - bandwidth) / 2
```

**Ordinal scale** (category to color):
```
domain: [categories...]
range: [color1, color2, ...]
map(category) = range[index % range.length]
```

### Shape Generators (D3-shape concepts)

**Arc generator** (pie/donut):
```
arc(startAngle, endAngle, innerRadius, outerRadius):
  x1 = cx + outerRadius * sin(startAngle)
  y1 = cy - outerRadius * cos(startAngle)
  ...
  path = "M x1,y1 A outerRadius,outerRadius 0 largeArc,1 x2,y2 ..."
```

**Line generator** (line charts):
```
points: [(x1,y1), (x2,y2), ...]
path = "M x1,y1 L x2,y2 L x3,y3 ..."
```

**Area generator** (area charts):
```
path = "M x1,y1_top L x2,y2_top ... L xN,yN_top L xN,yN_bottom ... L x1,y1_bottom Z"
```

### Axis Generation

Axes are groups of lines and text elements:

```xml
<!-- Y-axis -->
<g transform="translate(60, 0)">
  <line x1="0" y1="40" x2="0" y2="250" stroke="#666" stroke-width="1"/>
  <!-- Ticks -->
  <g transform="translate(0, 100)">
    <line x1="-5" x2="0" stroke="#666"/>
    <text x="-8" text-anchor="end" fill="#999" font-size="11">50K</text>
  </g>
</g>
```

Tick count heuristic: 4-7 ticks for most charts. Use round numbers (multiples of 1, 2, 5, 10, 25, 50, 100...).

## Module 3: Color Palettes

### Dark-Slate Theme (default)

For dark backgrounds (terminal themes, dark-mode READMEs):

| Role | Hex | Usage |
| --- | --- | --- |
| Background | `#1E1E2E` | Dashboard background |
| Panel background | `#2A2A3E` | Chart panel fill |
| Text primary | `#E0E0E0` | Titles, values |
| Text secondary | `#999999` | Axis labels, captions |
| Grid lines | `#3A3A4E` | Background grid |
| Border | `#3A3A4E` | Panel borders |
| Accent 1 | `#4A90D9` | Primary data series (blue) |
| Accent 2 | `#50C878` | Secondary series (green) |
| Accent 3 | `#FFB347` | Tertiary series (orange) |
| Accent 4 | `#FF6B6B` | Quaternary / alert (red) |
| Accent 5 | `#BB86FC` | Quinary series (purple) |
| Positive | `#50C878` | Up, growth, good |
| Negative | `#FF6B6B` | Down, decline, bad |
| Neutral | `#999999` | Unchanged, baseline |

### Light Theme

For light backgrounds (printed docs, light-mode preview):

| Role | Hex | Usage |
| --- | --- | --- |
| Background | `#FFFFFF` | Dashboard background |
| Panel background | `#F8F9FA` | Chart panel fill |
| Text primary | `#212529` | Titles, values |
| Text secondary | `#6C757D` | Axis labels, captions |
| Grid lines | `#E9ECEF` | Background grid |
| Border | `#DEE2E6` | Panel borders |
| Accent 1 | `#2563EB` | Primary data series (blue) |
| Accent 2 | `#16A34A` | Secondary series (green) |
| Accent 3 | `#D97706` | Tertiary series (orange) |
| Accent 4 | `#DC2626` | Quaternary / alert (red) |
| Accent 5 | `#7C3AED` | Quinary series (purple) |

### Color Assignment Rules

1. Use sequential assignment (Accent 1, 2, 3...) for unrelated categories
2. Use semantic colors (Positive/Negative) when data has inherent direction
3. Never exceed 5 distinct data colors in a single chart (split into panels)
4. Maintain 3:1 minimum contrast ratio between data elements and background
5. For single-series charts, use Accent 1 only

## Module 4: Chart Primitives

### KPI Strip

A row of metric cards, each showing label + value + optional delta.

```xml
<g transform="translate(0, 0)">
  <!-- Card 1 -->
  <rect x="0" y="0" width="250" height="80" rx="4" fill="#2A2A3E"/>
  <text x="20" y="25" fill="#999" font-size="11">REVENUE</text>
  <text x="20" y="55" fill="#E0E0E0" font-size="24" font-weight="700">$246.4K</text>
  <text x="20" y="72" fill="#50C878" font-size="11">+12.3% YoY</text>
</g>
```

Layout: cards evenly spaced across dashboard width. Gap = 16px between cards.
Formula: `cardWidth = (dashWidth - (n-1) * gap) / n`

### Horizontal Bar Chart

```xml
<g transform="translate(60, 80)">
  <!-- Bar -->
  <rect x="0" y="0" width="320" height="24" rx="2" fill="#4A90D9"/>
  <!-- Label (left of axis) -->
  <text x="-8" y="16" text-anchor="end" fill="#E0E0E0" font-size="12">North</text>
  <!-- Value (right of bar) -->
  <text x="328" y="16" fill="#999" font-size="11">$139.1K</text>
</g>
```

Bar spacing: bandwidth = step * 0.7 (30% gap between bars).

### Vertical Bar Chart

Same as horizontal, rotated. Y-axis for values, x-axis for categories. Use band scale for x, linear scale for y.

### Line Chart

```xml
<polyline points="60,200 160,180 260,150 360,160 460,130 560,140"
          fill="none" stroke="#4A90D9" stroke-width="2" stroke-linejoin="round"/>
<!-- Data points -->
<circle cx="60" cy="200" r="3" fill="#4A90D9"/>
```

For multiple series: one `<polyline>` per series, different stroke colors.

### Area Chart

```xml
<path d="M 60,200 L 160,180 L 260,150 ... L 560,250 L 60,250 Z"
      fill="#4A90D9" fill-opacity="0.3" stroke="#4A90D9" stroke-width="2"/>
```

### Pie / Donut Chart

Each slice is a `<path>` using arc commands:

```xml
<path d="M cx,cy-r A r,r 0 largeArc,1 x2,y2 L cx,cy Z" fill="#4A90D9"/>
```

For donut: add inner radius, close path along inner arc.
Maximum slices: 6. Group remaining into "Other."

### Sparkline

Minimal line chart without axes, embedded in KPI cards:

```xml
<polyline points="0,10 5,8 10,12 15,6 20,9 25,4 30,7"
          fill="none" stroke="#4A90D9" stroke-width="1.5"
          transform="translate(180, 30)"/>
```

## Module 5: Layout System

### Grid Layouts

| Layout | Columns | Panel width | Use when |
| --- | --- | --- | --- |
| Single | 1 | 800px | One hero chart, or detailed view |
| Two-column | 2 | 384px (16px gap) | Comparison, two related charts |
| Three-column | 3 | 252px (22px gap) | KPI strip, multiple small charts |

### Dashboard Structure

```
+--[ Title Bar ]------------------------------------------+
|                                                          |
+--[ KPI Strip ]------------------------------------------+
|  [Card 1]  [Card 2]  [Card 3]  [Card 4]               |
+--[ Row 1 ]----------------------------------------------+
|  [Chart: full width]                                     |
+--[ Row 2 ]----------------------------------------------+
|  [Chart: left]          [Chart: right]                  |
+--[ Footer ]---------------------------------------------+
|  Action / Insight sentence                              |
+---------------------------------------------------------+
```

### Vertical Spacing

| Element | Height | Spacing after |
| --- | --- | --- |
| Title bar | 50px | 16px |
| KPI strip | 90px | 24px |
| Chart panel | 200-300px | 24px |
| Footer | 40px | 0 |

Total height = sum of all elements + spacing. Set `viewBox` height accordingly.

## Module 6: Construction Process

### Step 1: Compute Layout

From the dashboard plan (structured data from orchestrator):

1. Count panels and their layout positions (full, left, right)
2. Assign each panel a row
3. Compute total height: sum all row heights + spacing
4. Set `viewBox="0 0 800 {totalHeight}"`

### Step 2: Compute Scales

For each chart panel:

1. Determine domain from data (min/max for linear; categories for band)
2. Determine range from panel dimensions and margins
3. Use the scale math (Module 2) to get pixel positions

### Step 3: Generate SVG Elements

For each panel:

1. Render panel background (`<rect>` with fill and rx)
2. Render axes (lines + tick marks + labels)
3. Render data elements (bars, lines, arcs)
4. Render data labels (positioned relative to data elements)
5. Render title

### Step 4: Assemble Document

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {h}"
     width="800" height="{h}" font-family="system-ui, -apple-system, sans-serif">
  <!-- Background -->
  <rect width="800" height="{h}" fill="{theme.background}"/>

  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" fill="{theme.textPrimary}"
        font-size="16" font-weight="600">{title}</text>

  <!-- KPI Strip (if present) -->
  <g transform="translate(0, 50)">...</g>

  <!-- Chart panels -->
  <g transform="translate(0, {rowY})">...</g>

  <!-- Footer -->
  <text x="400" y="{h - 15}" text-anchor="middle" fill="{theme.textSecondary}"
        font-size="12">{footer}</text>
</svg>
```

### Step 5: Embed in Markdown

Two output modes:

**Inline SVG** (for GitHub README):
````markdown
## Dashboard

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" ...>
  ...
</svg>
````

**External file** (for linking):
```markdown
## Dashboard

![Sales Dashboard](./dashboard.svg)
```

## Module 7: Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Using `<style>` blocks | GitHub strips them. Use inline `style` or direct attributes |
| Using `<foreignObject>` for text | GitHub strips it. Use `<text>` with `<tspan>` for wrapping |
| Hardcoding pixel positions without scale math | Compute from data domain and range. Charts should rescale with data |
| More than 5 colors in one chart | Split into panels or use a highlight-vs-context pattern |
| Tiny text (< 10px) | Minimum 11px for labels, 12px for axis text |
| Missing `xmlns` attribute | Required for standalone SVG files |
| Using `em`/`rem` units | Use `px` only. SVG doesn't inherit document font size |
| Complex gradients or filters | GitHub may strip or misrender. Keep `<defs>` simple |
| Relying on hover/animation | No interactivity in static SVG. Design for static consumption |
| Setting width/height without viewBox | Always include viewBox for responsive scaling |

## Module 8: Validation Checklist

Before delivering SVG output, verify:

| Check | Criteria |
| --- | --- |
| GitHub-safe | No `<style>`, no `<script>`, no `<foreignObject>`, has `xmlns` |
| Readable | All text >= 11px, contrast ratio >= 3:1 against background |
| Correct data | Spot-check 2-3 values: bar height / position matches data |
| Responsive | `viewBox` present, width/height match, scales properly |
| Color accessible | Not relying on color alone (use labels or patterns) |
| File size | < 100KB for typical dashboards (pure SVG is compact) |
| Clean markup | No unnecessary whitespace, no commented-out elements |

## Cross-References

- `visual-vocabulary` -- select chart types before rendering
- `storytelling-requirements` -- the brief determines delivery target
- `delivery-ascii-dashboard` -- downgrade path for terminal-only environments
- `delivery-html-dashboard` -- upgrade path when interactivity is needed
