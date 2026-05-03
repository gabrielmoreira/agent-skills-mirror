# visual-vocabulary

Chart catalog organized by communication goal, with an evaluation framework for AI-generated chart choices.

## What It Does

- **Chart catalog** organized by 7 communication goals (comparison, change over time, proportion, distribution, relationship, flow, deviation) with specific chart recommendations and avoid-when guidance
- **CSAR evaluation loop** for reviewing AI-generated chart choices: Clarify the question, Summarize the AI's choice, Act (accept/modify/override), Reflect on the rationale
- **Override decision table** mapping common AI mis-selections to better alternatives
- **5-visual rule** for executive dashboards with composition guidance by audience type
- **SVG dashboard composition patterns** from production experience (panel primitives, pie sizing, bar spacing, dark-slate palette)
- **Living gallery references** to external chart catalogs that stay current

## When to Use

Pick this plugin when you need to decide WHAT chart to use. It delegates HOW to design the chart (color, annotation, decluttering) to `data-visualization` and HOW to frame the narrative to `data-storytelling`.

## Install

```bash
# Copy to your heir's local skills
cp -r plugins/data-analytics/visual-vocabulary/ .github/skills/local/visual-vocabulary/
```

## Complements

| Plugin | Relationship |
| --- | --- |
| `data-storytelling` | Use before this: defines the story arc and Big Idea |
| `data-visualization` | Use after this: designs the selected chart (color, labels, decluttering) |
| `dashboard-design` | Use after this: arranges the selected charts into a layout |
| `svg-dashboard-composition` | Use when output is SVG: composition mechanics and coordinate systems |
| `chart-interpretation` | The inverse: reading existing charts rather than creating new ones |

## Key Sources

- Kirk, *Fundamentals of Data Visualization* (chart type framework, Ch. 6)
- Knaflic, *Storytelling with Data* (Big Idea worksheet, decluttering principles)
- [FT Visual Vocabulary](https://ft-interactive.github.io/visual-vocabulary/)
- [From Data to Viz](https://www.data-to-viz.com/)
- VT_AIPOWERBI CSAR loop and Copilot Design Automation framework
