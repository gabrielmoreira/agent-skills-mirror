# visual-storytelling

Turn raw data into visual stories. One plugin, full pipeline.

**Status**: Complete (v2.0.1)

## What You Get

Install this bundle to get the complete Visual Storytelling pipeline:

| Step | Component | Tokens |
| --- | --- | --- |
| 1. Brief | `storytelling-requirements` | 2,700 |
| 2. Ingest | `datasource-connectors` | 2,800 |
| 3. Clean | `data-preparation` | 2,300 |
| 4. Select | Illustrator `chart-vocabulary` | External |
| 5. Render | `delivery-ascii-dashboard` | 3,300 |

Plus an orchestrator agent that runs the full pipeline end-to-end.

**Total**: 11,100 tokens across four bundled components. Install
`alex-act-illustrator-plugin` for SVG, HTML, and other graphical output.

## Usage

```text
@visual-storytelling Show me sales trends from data.csv as an ASCII dashboard
```

The orchestrator reads a brief, selects chart types, and delivers the dashboard
in your chosen format. Install only what you need: a project doing SVG
dashboards can skip the HTML plugin.

## Delivery Formats

| Format | Use When |
| --- | --- |
| ASCII | Terminal, plain text, Markdown code blocks |
| Graphical | Illustrator with Flint-backed chart selection and delivery |
