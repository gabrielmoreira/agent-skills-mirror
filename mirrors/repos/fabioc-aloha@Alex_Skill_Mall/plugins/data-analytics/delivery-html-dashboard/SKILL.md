---
type: skill
lifecycle: stable
inheritance: inheritable
name: delivery-html-dashboard
description: Render data dashboards as self-contained HTML files using Apache ECharts v6. Single file, zero build step, interactive charts with tooltips and data zoom. Declarative JSON option config optimized for AI generation.
tier: standard
applyTo: '**/*html*dashboard*,**/*echarts*,**/*interactive*chart*'
currency: 2026-05-04
lastReviewed: 2026-05-04
---

# Delivery: HTML Dashboard (ECharts)

Render dashboards as self-contained HTML files with interactive charts. One file, one CDN script tag, zero build step. Open in any browser.

The agent writes ECharts option objects (declarative JSON), not imperative drawing code. This makes the format ideal for AI generation: the model reasons about data mapping and visual encoding, ECharts handles rendering, animation, and interaction.

## When to Use

- Interactive dashboards (tooltips, zoom, legend toggle)
- Presentations or reports opened in a browser
- Stakeholders who expect "real" charts (not ASCII, not static images)
- Data with 20+ chart types available (treemap, sankey, gauge, radar)
- When the audience needs to explore data (filter, zoom, hover for detail)

## When NOT to Use

- GitHub README (no JS execution; use `delivery-svg-markdown`)
- Terminal-only consumers (use `delivery-ascii-dashboard`)
- Corporate BI tools required (use `delivery-powerbi-fabric`)
- The file must be < 50KB (ECharts CDN adds ~1MB on first load; use SVG)
- Offline with no cached CDN (bundle ECharts or use SVG fallback)

## Module 1: HTML Structure

### Template

Every dashboard is a single `.html` file with this structure:

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Dashboard Title}</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@6/dist/echarts.min.js"></script>
  <style>
    /* CSS custom properties, grid layout, KPI cards, print styles */
  </style>
</head>
<body>
  <header>
    <h1>{Title}</h1>
    <p class="subtitle">{Big Idea sentence}</p>
    <button id="theme-toggle" aria-label="Toggle theme">Toggle Theme</button>
  </header>

  <section class="kpi-strip">
    <!-- KPI cards -->
  </section>

  <section class="chart-grid">
    <!-- Chart containers -->
    <div class="chart-panel" id="chart1"></div>
    <div class="chart-panel" id="chart2"></div>
  </section>

  <footer>
    <p>{Action / recommendation sentence}</p>
  </footer>

  <script>
    // ECharts initialization and options
  </script>
</body>
</html>
```

### CDN Strategy

Primary CDN with fallback:

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@6/dist/echarts.min.js"></script>
<script>
  if (typeof echarts === 'undefined') {
    document.write('<script src="https://unpkg.com/echarts@6/dist/echarts.min.js"><\/script>');
  }
</script>
```

For offline use, the user can download `echarts.min.js` and reference it locally.

## Module 2: CSS Architecture

### Custom Properties (Theme System)

```css
:root, [data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-card: #ffffff;
  --text-primary: #212529;
  --text-secondary: #6c757d;
  --border: #dee2e6;
  --accent-1: #2563eb;
  --accent-2: #16a34a;
  --accent-3: #d97706;
  --accent-4: #dc2626;
  --accent-5: #7c3aed;
  --positive: #16a34a;
  --negative: #dc2626;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --radius: 8px;
}

[data-theme="dark"] {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --bg-card: #1e2a4a;
  --text-primary: #e0e0e0;
  --text-secondary: #999999;
  --border: #2a3a5e;
  --accent-1: #4a90d9;
  --accent-2: #50c878;
  --accent-3: #ffb347;
  --accent-4: #ff6b6b;
  --accent-5: #bb86fc;
  --positive: #50c878;
  --negative: #ff6b6b;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
  --radius: 8px;
}
```

### Grid Layout

```css
body {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  margin: 0;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.kpi-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.chart-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px;
  min-height: 300px;
}

/* Full-width panel override */
.chart-panel.full-width {
  grid-column: 1 / -1;
}
```

### KPI Cards

```css
.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px;
  text-align: center;
}

.kpi-card .label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.kpi-card .value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.kpi-card .delta {
  font-size: 13px;
  margin-top: 4px;
}

.kpi-card .delta.positive { color: var(--positive); }
.kpi-card .delta.negative { color: var(--negative); }
```

### Print Styles

```css
@media print {
  body { background: white; color: black; padding: 0; }
  .chart-panel { break-inside: avoid; box-shadow: none; border: 1px solid #ccc; }
  #theme-toggle { display: none; }
  .kpi-card { box-shadow: none; border: 1px solid #ccc; }
}
```

### Responsive Breakpoints

```css
@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .chart-panel { min-height: 250px; }
}

@media (max-width: 480px) {
  .kpi-strip { grid-template-columns: 1fr; }
  body { padding: 12px; }
}
```

## Module 3: ECharts Option Patterns

### Initialization Pattern

```javascript
const charts = [];
function initChart(id, option) {
  const dom = document.getElementById(id);
  const chart = echarts.init(dom, null, { renderer: 'canvas' });
  chart.setOption(option);
  charts.push(chart);
  return chart;
}

// Responsive resize
window.addEventListener('resize', () => {
  charts.forEach(c => c.resize());
});
```

### Bar Chart Option

```javascript
{
  title: { text: 'Revenue by Region', left: 'center',
           textStyle: { color: 'var(--text-primary)', fontSize: 14 } },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['North', 'South'] },
  yAxis: { type: 'value', axisLabel: { formatter: '${value/1000}K' } },
  series: [{
    type: 'bar',
    data: [139100, 107300],
    itemStyle: { color: '#4a90d9', borderRadius: [4, 4, 0, 0] }
  }]
}
```

### Line Chart Option

```javascript
{
  title: { text: 'Revenue Trend', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
  yAxis: { type: 'value', min: 'dataMin', axisLabel: { formatter: v => `$${(v/1000).toFixed(1)}K` } },
  series: [{
    type: 'line',
    data: [36800, 39000, 42300, 40600, 44800, 42900],
    smooth: true,
    areaStyle: { opacity: 0.15 },
    lineStyle: { width: 2 },
    symbol: 'circle',
    symbolSize: 6
  }]
}
```

### Pie / Donut Option

```javascript
{
  title: { text: 'Revenue Split', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],  // donut; use ['0%', '70%'] for full pie
    data: [
      { value: 83300, name: 'N. Widget A' },
      { value: 65500, name: 'S. Widget A' },
      { value: 55800, name: 'N. Widget B' },
      { value: 41800, name: 'S. Widget B' }
    ],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
    label: { formatter: '{b}\n{d}%' }
  }]
}
```

### Horizontal Bar (Ranking)

```javascript
{
  title: { text: 'Segment Ranking', left: 'center' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  yAxis: { type: 'category', data: ['S. Widget B', 'N. Widget B', 'S. Widget A', 'N. Widget A'],
           inverse: true },
  xAxis: { type: 'value', axisLabel: { formatter: v => `$${(v/1000).toFixed(0)}K` } },
  series: [{
    type: 'bar',
    data: [41800, 55800, 65500, 83300],
    itemStyle: { borderRadius: [0, 4, 4, 0] },
    colorBy: 'data'
  }],
  color: ['#ff6b6b', '#ffb347', '#50c878', '#4a90d9']
}
```

### Gauge (Single KPI with target)

```javascript
{
  series: [{
    type: 'gauge',
    progress: { show: true, width: 12 },
    detail: { formatter: '{value}%', fontSize: 20 },
    data: [{ value: 72, name: 'Margin' }],
    axisLine: { lineStyle: { width: 12 } },
    max: 100
  }]
}
```

### Radar Chart

```javascript
{
  radar: {
    indicator: [
      { name: 'Revenue', max: 100000 },
      { name: 'Growth', max: 20 },
      { name: 'Margin', max: 50 },
      { name: 'Volume', max: 2000 }
    ]
  },
  series: [{
    type: 'radar',
    data: [
      { value: [83300, 16.8, 30, 1666], name: 'North Widget A' },
      { value: [41800, 11.5, 30, 836], name: 'South Widget B' }
    ]
  }]
}
```

### Dataset Transform (filter/sort in ECharts)

```javascript
{
  dataset: [
    { source: [
      ['segment', 'revenue', 'margin'],
      ['N. Widget A', 83300, 24990],
      ['S. Widget A', 65500, 19650],
      ['N. Widget B', 55800, 16740],
      ['S. Widget B', 41800, 12540]
    ]},
    { transform: { type: 'sort', config: { dimension: 'revenue', order: 'desc' } } }
  ],
  xAxis: { type: 'category' },
  yAxis: {},
  series: [{ type: 'bar', datasetIndex: 1, encode: { x: 'segment', y: 'revenue' } }]
}
```

## Module 4: Interactivity Patterns

### Tooltip Configuration

```javascript
tooltip: {
  trigger: 'axis',           // 'axis' for line/bar, 'item' for pie/scatter
  backgroundColor: 'rgba(30,30,46,0.95)',
  borderColor: '#3a3a4e',
  textStyle: { color: '#e0e0e0' },
  formatter: params => {
    // Custom HTML tooltip
    let html = `<strong>${params[0].axisValue}</strong><br/>`;
    params.forEach(p => {
      html += `${p.marker} ${p.seriesName}: $${(p.value/1000).toFixed(1)}K<br/>`;
    });
    return html;
  }
}
```

### Data Zoom (scrollable axis)

Use when data has > 12 time periods or > 20 categories:

```javascript
dataZoom: [
  { type: 'inside', start: 0, end: 100 },      // scroll/pinch
  { type: 'slider', start: 0, end: 100, height: 20 }  // visible slider
]
```

### Legend Toggle

ECharts legends are interactive by default. Clicking a legend item hides/shows the series.

```javascript
legend: {
  type: 'scroll',   // scrollable if many items
  top: 'bottom',
  textStyle: { color: 'var(--text-secondary)' }
}
```

### Chart Connection (cross-filtering)

Connect multiple charts so tooltip/highlight syncs:

```javascript
echarts.connect([chart1, chart2, chart3]);
```

This creates linked tooltips across charts sharing the same axis categories.

## Module 5: Theme Integration

### Dark/Light Toggle

```javascript
document.getElementById('theme-toggle').addEventListener('click', () => {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);

  // Update ECharts theme colors
  const textColor = next === 'dark' ? '#e0e0e0' : '#212529';
  const axisColor = next === 'dark' ? '#666' : '#ccc';
  charts.forEach(chart => {
    chart.setOption({
      title: { textStyle: { color: textColor } },
      xAxis: { axisLine: { lineStyle: { color: axisColor } },
               axisLabel: { color: textColor } },
      yAxis: { axisLine: { lineStyle: { color: axisColor } },
               axisLabel: { color: textColor } }
    });
  });
});
```

### ECharts Color Palette

Set globally for consistent series colors:

```javascript
const PALETTE = {
  dark: ['#4a90d9', '#50c878', '#ffb347', '#ff6b6b', '#bb86fc'],
  light: ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed']
};

// Apply in each chart option:
color: PALETTE[document.documentElement.getAttribute('data-theme') || 'dark']
```

## Module 6: Accessibility

### ECharts Aria Module

Enable automatic chart descriptions for screen readers:

```javascript
{
  aria: {
    enabled: true,
    decal: { show: true },  // Pattern fills for color-blind users
    label: {
      description: 'Bar chart showing revenue by region. North leads with $139.1K.'
    }
  }
}
```

### Additional a11y Requirements

| Requirement | Implementation |
| --- | --- |
| Color not sole differentiator | Enable `decal` patterns; add data labels |
| Keyboard navigation | ECharts supports Tab/Arrow by default |
| Focus indicators | ECharts highlight on focus built-in |
| Alt text for KPI cards | Use `aria-label` on `.kpi-card` elements |
| Semantic structure | Use `<header>`, `<section>`, `<footer>` |
| Sufficient contrast | All text passes WCAG AA (4.5:1 ratio) |

## Module 7: Data Embedding

### Inline Dataset

Data lives in a `<script>` block inside the HTML. No external fetch, no CORS issues:

```javascript
const DATA = {
  monthly: [
    { month: 'Jan', revenue: 36800, units: 536, cost: 25760 },
    { month: 'Feb', revenue: 39000, units: 568, cost: 27300 },
    // ...
  ],
  segments: [
    { name: 'N. Widget A', revenue: 83300, margin: 24990 },
    // ...
  ],
  kpis: {
    totalRevenue: 246400,
    totalMargin: 73920,
    marginPct: 30.0,
    totalUnits: 5448
  }
};
```

### Large Dataset Handling

For datasets > 10,000 rows, use ECharts dataset with `large: true`:

```javascript
series: [{
  type: 'scatter',
  large: true,
  largeThreshold: 5000,
  data: bigArray
}]
```

## Module 8: Construction Process

### Step 1: Plan Layout from Brief

From the dashboard plan (structured data from orchestrator):

1. Determine KPI count (2-5 cards)
2. Determine chart count and types
3. Assign grid positions: full-width vs. two-column
4. Estimate total page height

### Step 2: Generate HTML Shell

Write the `<!DOCTYPE html>` through `<body>` with:
- CSS custom properties for chosen theme
- Grid layout matching the panel plan
- Empty `<div>` containers with IDs for each chart

### Step 3: Generate ECharts Options

For each chart:
1. Build the option object from the data
2. Map data values to the appropriate ECharts series type
3. Configure tooltip, legend, and color
4. Add aria labels

### Step 4: Wire Up Initialization

```javascript
document.addEventListener('DOMContentLoaded', () => {
  initChart('chart1', option1);
  initChart('chart2', option2);
  // ...
  echarts.connect(charts);
});
```

### Step 5: Validate

| Check | Criteria |
| --- | --- |
| Opens in browser | No console errors, charts render |
| Single file | No external resources besides ECharts CDN |
| Responsive | Resize browser; charts adapt, grid reflows |
| Theme toggle | Button switches dark/light correctly |
| Print | Ctrl+P shows clean layout, no cutoff charts |
| Accessible | Tab through charts; aria labels present |
| Data correct | Tooltip values match source data |

## Module 9: Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Multiple CDN scripts | Use only ECharts; it has all chart types built-in |
| Imperative canvas drawing | Use declarative option objects; let ECharts render |
| External data fetch (CORS issues) | Embed data inline in `<script>` |
| Fixed pixel heights on charts | Use `min-height` + resize handler |
| Missing `resize()` listener | Charts won't adapt to window changes |
| Inline styles on chart containers | Use CSS classes; inline only for theme vars |
| Over-animating (slow load) | Set `animation: false` for > 10 series |
| No tooltip | Tooltips are the primary exploration tool; always enable |
| Forgetting `init` after DOM ready | Wrap in `DOMContentLoaded` event |
| Using ECharts themes API | Stick to CSS vars + inline color; simpler to generate |

## Module 10: File Size Guidelines

| Component | Approximate Size |
| --- | --- |
| HTML shell + CSS | 3-5 KB |
| ECharts CDN (cached) | ~1 MB (first load only) |
| ECharts options (4 charts) | 2-4 KB |
| Inline data (small dataset) | 1-3 KB |
| Total HTML file size | 8-15 KB (excluding CDN) |

Target: keep the `.html` file under 50KB. If data exceeds 30KB, consider pagination or server-side rendering.

## Cross-References

- `visual-vocabulary` -- select chart types before rendering
- `storytelling-requirements` -- the brief determines delivery target
- `delivery-svg-markdown` -- downgrade path when no JS allowed
- `delivery-ascii-dashboard` -- downgrade path for terminal-only
- `delivery-powerbi-fabric` -- enterprise path when PBI ecosystem required
