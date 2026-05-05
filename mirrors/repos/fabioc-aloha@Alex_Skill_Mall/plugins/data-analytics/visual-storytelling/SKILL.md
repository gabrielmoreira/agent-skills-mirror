---
type: skill
lifecycle: stable
inheritance: inheritable
name: visual-storytelling
description: "Bundle plugin: installs the complete Visual Storytelling pipeline (brief, ingest, clean, select, deliver). See component SKILLs for detailed specs."
tier: standard
applyTo: '**/*dashboard*,**/*visual*,**/*chart*,**/*storytelling*'
currency: 2026-05-04
lastReviewed: 2026-05-04
---

# Visual Storytelling (Bundle)

This is the entry point for the Visual Storytelling pipeline. It installs 7
component plugins and an orchestrator agent.

## Pipeline

```text
Brief -> Ingest -> Clean -> Select -> Deliver
```

1. **Brief** (`storytelling-requirements`): Structured intake producing audience,
   Big Idea, questions with communication goals, data sources, delivery target.
2. **Ingest** (`datasource-connectors`): Load from CSV, JSON, API, SQL, Excel,
   Parquet with error handling and encoding detection.
3. **Clean** (`data-preparation`): Profile, clean, aggregate, pivot, quality-check.
4. **Select** (`visual-vocabulary`): Map each question's communication goal to
   the right chart type using the visual vocabulary catalog.
5. **Deliver**: Render to the chosen format:
   - `delivery-ascii-dashboard` -- terminal/plain text (78-char aligned)
   - `delivery-svg-markdown` -- GitHub-compatible static SVG (D3.js patterns)
   - `delivery-html-dashboard` -- interactive HTML (Apache ECharts v6)

## Orchestrator Agent

The `visual-storytelling` agent runs the full pipeline. Invoke it with a data
source, a rough request, and a delivery target. It produces a structured brief,
delegates to each pipeline step, and runs a CSAR QA loop on the output.

## Component Skills

Each component has its own detailed SKILL.md. This bundle skill is a routing
layer; the real specs live in the components:

| Component | SKILL Path |
| --- | --- |
| `storytelling-requirements` | `.github/skills/local/storytelling-requirements/SKILL.md` |
| `datasource-connectors` | `.github/skills/local/datasource-connectors/SKILL.md` |
| `data-preparation` | `.github/skills/local/data-preparation/SKILL.md` |
| `visual-vocabulary` | `.github/skills/local/visual-vocabulary/SKILL.md` |
| `delivery-ascii-dashboard` | `.github/skills/local/delivery-ascii-dashboard/SKILL.md` |
| `delivery-svg-markdown` | `.github/skills/local/delivery-svg-markdown/SKILL.md` |
| `delivery-html-dashboard` | `.github/skills/local/delivery-html-dashboard/SKILL.md` |

## When to Use Which Delivery

| Need | Format | Why |
| --- | --- | --- |
| GitHub README | SVG | No JS execution on GitHub |
| Terminal output | ASCII | Universal, no rendering needed |
| Interactive exploration | HTML | Tooltips, zoom, legend toggle |
| Static docs / reports | SVG | Crisp at any scale, inline in Markdown |
| Presentations | HTML | Open in browser, full-screen |
| Offline / no CDN | SVG or ASCII | No external dependencies |
