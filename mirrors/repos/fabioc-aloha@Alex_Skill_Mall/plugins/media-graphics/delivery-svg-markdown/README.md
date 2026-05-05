# delivery-svg-markdown

SVG dashboard composition for Markdown and GitHub, powered by D3.js patterns.

**Status**: Published (v1.0.0)

## Technology

**D3.js v7** (ISC license, 113k stars) for coordinate math, scales, axes, and
path generation. The agent uses D3's primitives (scales, shapes, layouts) to
produce raw SVG markup. The rendered output is pure static SVG with no runtime
JavaScript dependency, ensuring GitHub Markdown compatibility.

D3 modules used:

- `d3-scale` -- linear, band, ordinal, time scales
- `d3-shape` -- arc, line, area, pie, stack generators
- `d3-axis` -- axis tick generation and formatting
- `d3-format` / `d3-time-format` -- number and date formatting
- `d3-color` -- palette interpolation and contrast checks
- `d3-hierarchy` -- treemap, sunburst layouts (if needed)

## Scope

- Panel primitives (card, KPI, chart container) with shared coordinate system
- viewBox math: auto-sizing panels to content via D3 scale ranges
- Dark-slate and light-theme palettes (D3 color schemes)
- Chart primitives: bar, line, area, pie/donut, KPI strip, sparkline
- Text rendering: title, subtitle, axis labels, data labels
- Responsive grid: 1-column, 2-column, 3-column layouts
- GitHub-compatible: no external CSS, no JS, inline styles only
- Export: single `.svg` file or embedded in `.md`

Will absorb and extend `svg-dashboard-composition` from the Mall.

## Pipeline Position

Final step. Fires after `visual-vocabulary` selects chart types.
