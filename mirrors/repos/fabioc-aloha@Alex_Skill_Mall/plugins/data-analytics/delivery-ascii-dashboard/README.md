# delivery-ascii-dashboard

Pure ASCII art dashboards. The cheapest, most portable delivery method.

## Why ASCII

- **Zero dependencies.** No SVG renderer, no browser, no Chart.js CDN.
- **LLM-native.** An LLM can produce and validate the output in the same context window.
- **Predictable geometry.** No emojis (variable width). Every character is exactly one cell.
- **Universal rendering.** Terminals, code fences, log files, plain-text email, CI output.
- **Cheapest token cost.** No coordinate math, no color hex codes, no viewBox calculations.

## What It Supports

- KPI strips (3-6 metric cards in a row)
- Horizontal bar charts (sorted, with labels and values)
- Sparkline rows (trend at a glance)
- Two-column layouts (side-by-side panels)
- Full dashboards (header + KPIs + charts + footer CTA)
- Status indicators (`[x]`, `[-]`, `[ ]`, `[OK]`, `[!!]`)

## Install

```bash
cp -r plugins/delivery-ascii-dashboard/ .github/skills/local/delivery-ascii-dashboard/
```

## Pipeline Position

Final delivery step. Alternative to SVG/HTML/Power BI when simplicity and portability matter most.

## Upgrade Path

When ASCII isn't enough: `delivery-svg-markdown` (color, branding) or `delivery-html-dashboard` (interactivity).
