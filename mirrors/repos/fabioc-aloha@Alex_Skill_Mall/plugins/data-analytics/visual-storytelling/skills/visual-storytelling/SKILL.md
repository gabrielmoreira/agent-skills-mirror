---
type: skill
lifecycle: stable
inheritance: inheritable
name: visual-storytelling
description: "Bundle plugin: installs the complete Visual Storytelling pipeline (brief, ingest, clean, select, deliver). See component SKILLs for detailed specs."
tier: standard
applyTo: "**/*dashboard*,**/*visual*,**/*chart*,**/*storytelling*"
currency: 2026-08-06
lastReviewed: 2026-08-06
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

In this collection, **CSAR always means Clarify, Summarize, Act, Reflect**.
Use it consistently across requirements, chart selection, orchestration, and
delivery. Accuracy is a mandatory acceptance criterion within Act; changing the
acronym to fit a local checklist makes cross-module evidence ambiguous.

## Executable Example Contract

Examples are release evidence only when they are coupled to their source data.
For every maintained example:

1. Derive expected metrics independently from the raw source.
2. Validate every user-facing surface: brief, embedded data, visible labels,
   aria descriptions, tooltips, captions, and action or evidence-boundary text.
3. Regenerate deterministic outputs and compare them with committed snapshots.
   If a format is hand-authored, say so and keep its regeneration gap open.
4. Validate formulas, units, grain, rounding, baseline, sort order, and every
   decision-bearing number. Presence-only string checks are insufficient.
5. Render visual outputs at their target viewports and inspect each chart, not
   only the first visible panel.
6. Apply at least one mutation to a decision-bearing value and require the
   contract to fail. Restore the artifact bit-identically afterward.

### Audit Closure Semantics

- **Open**: no validated remediation exists; leave the checkbox unchecked.
- **Mitigated**: part of the risk is reduced, but the completion test has not
  passed; leave it unchecked and name the remaining boundary.
- **Resolved**: the named executable or rendered completion test passes; only
  then check the item.

Do not convert a mitigated item to resolved merely because one delivery format
or one fixture passes. Integration claims require integration evidence.

## Component Skills

Each component has its own detailed SKILL.md. This bundle skill is a routing
layer; the real specs live in the components:

| Component                   | SKILL Path                                                |
| --------------------------- | --------------------------------------------------------- |
| `storytelling-requirements` | `skills/storytelling-requirements/SKILL.md` |
| `datasource-connectors`     | `skills/datasource-connectors/SKILL.md`     |
| `data-preparation`          | `skills/data-preparation/SKILL.md`          |
| `visual-vocabulary`         | `skills/visual-vocabulary/SKILL.md`         |
| `delivery-ascii-dashboard`  | `skills/delivery-ascii-dashboard/SKILL.md`  |
| `delivery-svg-markdown`     | `skills/delivery-svg-markdown/SKILL.md`     |
| `delivery-html-dashboard`   | `skills/delivery-html-dashboard/SKILL.md`   |

## When to Use Which Delivery

| Need                    | Format       | Why                                    |
| ----------------------- | ------------ | -------------------------------------- |
| GitHub README           | SVG          | No JS execution on GitHub              |
| Terminal output         | ASCII        | Universal, no rendering needed         |
| Interactive exploration | HTML         | Tooltips, zoom, legend toggle          |
| Static docs / reports   | SVG          | Crisp at any scale, inline in Markdown |
| Presentations           | HTML         | Open in browser, full-screen           |
| Offline / no CDN        | SVG or ASCII | No external dependencies               |
