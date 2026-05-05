# visual-storytelling

Turn raw data into visual stories. One plugin, full pipeline.

**Status**: Complete (v1.0.0)

## What You Get

Install this bundle to get the complete Visual Storytelling pipeline:

| Step | Component | Tokens |
| --- | --- | --- |
| 1. Brief | `storytelling-requirements` | 1,900 |
| 2. Ingest | `datasource-connectors` | 2,000 |
| 3. Clean | `data-preparation` | 1,500 |
| 4. Select | `visual-vocabulary` | 3,300 |
| 5a. Render | `delivery-ascii-dashboard` | 2,700 |
| 5b. Render | `delivery-svg-markdown` | 4,200 |
| 5c. Render | `delivery-html-dashboard` | 4,800 |

Plus an orchestrator agent that runs the full pipeline end-to-end.

**Total**: 20,400 tokens (all 7 components loaded).

## Usage

```text
@visual-storytelling Show me sales trends from data.csv as an HTML dashboard
```

The orchestrator reads a brief, selects chart types, and delivers the dashboard
in your chosen format. Install only what you need: a project doing SVG
dashboards can skip the HTML plugin.

## Delivery Formats

| Format | Use When |
| --- | --- |
| ASCII | Terminal, plain text, Markdown code blocks |
| SVG | GitHub README, VS Code preview, static docs |
| HTML | Browser, interactive exploration, presentations |
