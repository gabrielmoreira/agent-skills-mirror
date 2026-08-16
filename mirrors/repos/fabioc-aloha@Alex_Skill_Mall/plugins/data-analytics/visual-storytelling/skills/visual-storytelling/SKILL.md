---
name: visual-storytelling
description: "Orchestrates requirements, ingestion, preparation, narrative framing, and ASCII delivery for data stories. Use for a multi-step data story; install alex-act-illustrator-plugin for chart selection and graphical output."
lastReviewed: 2026-08-15
---

# Visual Storytelling (Bundle)

This is the entry point for the Visual Storytelling pipeline. It installs four
data and narrative components plus an orchestrator agent. Install
`alex-act-illustrator-plugin` when the target needs chart selection, SVG, HTML,
or another graphical artifact.

## Pipeline

```text
Brief -> Ingest -> Clean -> Select -> Deliver
```

1. **Brief** (`storytelling-requirements`): Structured intake producing audience,
   Big Idea, questions with communication goals, data sources, delivery target.
2. **Ingest** (`datasource-connectors`): Load from CSV, JSON, API, SQL, Excel,
   Parquet with error handling and encoding detection.
3. **Clean** (`data-preparation`): Profile, clean, aggregate, pivot, quality-check.
4. **Select** (`chart-vocabulary`, from Illustrator): Map each question's
   communication goal to the right chart type.
5. **Deliver**:
   - `delivery-ascii-dashboard` -- terminal/plain text (78-char aligned)
   - Illustrator -- Flint-backed SVG, HTML, and other graphical delivery after
     the user installs `alex-act-illustrator-plugin`

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

| Component | Owner |
| --- | --- |
| `storytelling-requirements` | Visual Storytelling |
| `datasource-connectors` | Visual Storytelling |
| `data-preparation` | Visual Storytelling |
| `delivery-ascii-dashboard` | Visual Storytelling |
| `chart-vocabulary` | Illustrator |
| Graphical delivery | Illustrator |

## When to Use Which Delivery

| Need | Route | Why |
| --- | --- | --- |
| Terminal output | ASCII | Universal, no rendering runtime needed |
| Graphical chart, report, or dashboard | Illustrator | One owner for selection, rendering, and visual verification |
| Offline / no graphical runtime | ASCII | No external dependency |
