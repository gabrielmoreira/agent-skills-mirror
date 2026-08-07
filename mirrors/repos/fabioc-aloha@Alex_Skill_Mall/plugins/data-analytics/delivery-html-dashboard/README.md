# delivery-html-dashboard

Single-file HTML dashboard shell powered by an integrity-pinned Apache ECharts
CDN resource.

**Status**: Published (v1.0.1)

## Technology

**Apache ECharts v6** (Apache 2.0 license, 66k stars) for interactive charting.
Declarative JSON option configuration makes it ideal for AI-generated output:
the agent writes an ECharts option object, not imperative drawing code.

Key advantages over Chart.js:

- 20+ chart types out of the box (bar, line, pie, scatter, radar, treemap,
  heatmap, gauge, funnel, sankey, sunburst, boxplot, candlestick...)
- Built-in dataset transforms (filter, sort, aggregate)
- Dual rendering engine: Canvas (performance) or SVG (quality)
- Progressive rendering for 10M+ data points
- Built-in dark/light themes + custom theme builder
- Accessibility: auto-generated chart descriptions, decal patterns
- Rich tooltips, legend interactions, data zoom, brush selection

Loaded via one exact CDN `<script>` tag (no build step):

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
    integrity="sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD"
    crossorigin="anonymous"></script>
```

## Scope

- Single HTML file, zero build step, open in any browser
- ECharts 6.1.0 via an integrity-pinned CDN resource for interactive charts
- KPI card components with metric + delta + sparkline
- CSS Grid responsive layout with auto-fit breakpoints
- Filter architecture (global, chart-level, cross-filter via ECharts connect)
- Embedded data: JSON in `<script>` tag, no external fetch
- CSS custom properties + ECharts theme for light/dark mode toggle
- Print-friendly `@media print` stylesheet
- WCAG 2.1 AA accessibility (ECharts aria module)
- Interactivity: tooltips, legend toggle, data zoom (no drill-through)

## Pipeline Position

Final step. Alternative to `delivery-svg-markdown` when interactivity is needed.
