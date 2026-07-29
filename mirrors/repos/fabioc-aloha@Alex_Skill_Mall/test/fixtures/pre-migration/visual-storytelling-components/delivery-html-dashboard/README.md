# delivery-html-dashboard

Self-contained HTML dashboard powered by Apache ECharts.

**Status**: Published (v1.0.0)

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

Loaded via single CDN `<script>` tag (no build step):

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@6/dist/echarts.min.js"></script>
```

## Scope

- Single HTML file, zero build step, open in any browser
- ECharts 6.x via CDN for interactive charts
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
