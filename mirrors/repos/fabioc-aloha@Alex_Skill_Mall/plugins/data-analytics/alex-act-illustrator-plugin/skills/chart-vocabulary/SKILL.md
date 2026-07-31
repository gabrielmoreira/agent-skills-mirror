---
name: chart-vocabulary
description: "Reference catalog of chart types organized by seven communication goals (comparison, change-over-time, proportion, distribution, relationship, flow, deviation), plus a CSAR evaluation loop for AI-generated chart choices, override decision table, 5-visual rule for dashboard density, living gallery pointers (FT Visual Vocabulary, Data-to-Viz, Data Viz Catalog, Vega-Lite examples, Storytelling with Data), and a 6-step selection algorithm. Use when picking a chart type, evaluating an AI-suggested chart, reviewing chart choices for story-intent alignment, sanity-checking a dashboard's density, or explaining chart taxonomy to a heir."
lastReviewed: 2026-07-30
---

# chart-vocabulary

Pick the right chart for the story you want to tell, evaluate whether an AI-suggested chart is correct, and know when to override.

This skill is the **selection and evaluation reference**. It sits upstream of the plugin's other chart skills:

| Step in the flow | Skill |
| --- | --- |
| Frame the Big Idea before authoring | [`chart-big-idea`](../chart-big-idea/SKILL.md) |
| **Pick the chart family + type** | **this skill** |
| Author the Flint spec + render | [`flint-chart`](../flint-chart/SKILL.md) |
| Structural / hand-authored SVG | [`figure-generator`](../figure-generator/SKILL.md) + [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) |
| AI-generated illustration / hero image | [`replicate-imagery`](../replicate-imagery/SKILL.md) |
| Verify after render | [`render-verify`](../render-verify/SKILL.md) |
| Deliver / browse the gallery | [`docs-shell`](../docs-shell/SKILL.md) |

`flint-chart` §0.2 (Question → family → chart) is a compact router pointing into this catalog; when a decision needs more than the router's ~7 rows, read this file. When picking a chart to hand-author rather than render via Flint, this catalog is still the reference — the delivery skill differs, the taxonomy does not.

## When to Use

- Choosing chart types for a dashboard, report, book figure, or data story
- Evaluating an AI-generated visualization (Copilot / ChatGPT / any tool that auto-selects chart types)
- Reviewing another agent's or teammate's chart choices for story-intent alignment
- Sanity-checking a dashboard's density (5-visual rule)
- Teaching a heir the chart taxonomy without them reading FT's catalog end to end

## Module 1: Chart Catalog by Communication Goal

Seven communication goals. Pick the goal first, then the chart. Never pick the chart first.

### Comparison

Show differences between items or groups.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Horizontal bar** | Ranking items; long category labels | More than 15 items (paginate or filter) |
| **Grouped bar** | Comparing 2-3 series across categories | More than 3 series (use small multiples) |
| **Dot plot** | Precise value comparison; tight ranges | Audience expects bars |
| **Slope chart** | Before/after comparison of ranked items | More than 10 items (too many crossing lines) |
| **Radar** | Multi-dimensional profile comparison | More than 7 axes; general audiences |
| **Bullet chart** | Actual vs. target with qualitative ranges | No clear target or benchmark |

### Change Over Time

Show trends, seasonality, or evolution.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Line** | Continuous data; up to 5 series | Categorical time (use bar) |
| **Area** | Emphasizing volume or magnitude of change | Multiple overlapping series (use stacked) |
| **Stacked area** | Part-to-whole composition changing over time | Need to compare individual series precisely |
| **Sparkline** | Inline trend context (KPI cards, tables) | Trend shape matters less than precise values |
| **Step line** | Discrete changes (pricing, policy, thresholds) | Continuous gradual change |
| **Small multiples** | Comparing trends across 6-20 categories | Fewer than 4 categories (use single line chart) |

### Proportion

Show part-to-whole relationships.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Donut** | 2-5 segments; one hero segment to highlight | More than 6 segments; comparing across groups |
| **Stacked bar** | Comparing composition across categories | More than 5 segments per bar |
| **Waffle** | Communicating percentages to general audiences | Precision matters (use table) |
| **Treemap** | Hierarchical part-to-whole with many items | Need to show change over time |
| **Sunburst** | Multi-level hierarchy exploration | Print or static context (needs interaction) |
| **Waterfall** | Showing additive/subtractive contributions | Non-sequential contributions |

### Distribution

Show spread, shape, or outliers.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Histogram** | Single variable distribution shape | Comparing distributions (use violin or ridgeline) |
| **Box plot** | Comparing distributions across groups | General audiences (unfamiliar format) |
| **Violin** | Distribution shape comparison across groups | Fewer than 3 groups (use histogram) |
| **Ridgeline** | Many distributions stacked for pattern scanning | Precision on individual values |
| **Scatter** | Two-variable distribution and outlier detection | Categorical data |
| **Beeswarm** | Small dataset; every point matters | More than 500 points (use density) |

### Relationship

Show correlation, causation, or connection.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Scatter** | Two continuous variables; outlier identification | Categorical variables |
| **Bubble** | Three variables (x, y, size) | More than 50 bubbles (overplotting) |
| **Heatmap** | Dense matrix relationships (correlation, time × category) | Fewer than 4×4 cells |
| **Parallel coordinates** | Multi-dimensional comparison (5+ variables) | General audiences |
| **Network graph** | Entity relationships, social connections | Hierarchical data (use tree) |
| **Chord diagram** | Bidirectional flows between categories | More than 10 categories |

### Flow and Process

Show movement, conversion, or paths.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Sankey** | Multi-stage flow with branching paths | Fewer than 3 stages (use stacked bar) |
| **Funnel** | Sequential drop-off (conversion, pipeline) | No sequential order |
| **Gantt** | Timeline with parallel activities | More than 30 tasks (filter or paginate) |
| **Swimlane** | Process flow with role/team assignments | Simple linear process |

### Deviation

Show variance from a reference point.

| Chart | Best when | Avoid when |
| --- | --- | --- |
| **Diverging bar** | Above/below target or median | No clear reference point |
| **Lollipop** | Deviation from baseline; cleaner than bars | Audience expects standard bars |
| **Line + reference** | Trend deviation from target over time | Multiple baselines |
| **Gauge** | Single KPI vs. target (dashboards, KPI cards) | More than 3 gauges on a page |

## Module 2: The CSAR Evaluation Loop

When an AI tool generates a chart, evaluate before accepting. Compose with [`render-verify`](../render-verify/SKILL.md)'s Prose-coupling check for a two-layer safety net: CSAR asks *did it pick the right chart family*; render-verify asks *did it render the right message*.

| Step | Question | Action |
| --- | --- | --- |
| **Clarify** | "What question am I answering?" | Write the question as a sentence before looking at the chart |
| **Summarize** | "The AI chose a [chart type]. Does it answer the question?" | Name the chart type and check it against Module 1 |
| **Act** | Accept, modify, or override | Accept if story-intent matches. Override if wrong goal group. Modify if right type but wrong emphasis |
| **Reflect** | "Why did I accept / override? What principle guided me?" | Document the rationale; builds judgment over time |

### Override Decision Table

| AI chose | But your goal is | Override to | Rationale |
| --- | --- | --- | --- |
| Pie (8 slices) | Compare items | Horizontal bar, sorted | Pie with 8+ slices is unreadable |
| Clustered bar | Show trend | Line chart | Time series needs continuity |
| 3D column | Anything | 2D bar or line | 3D adds no information, distorts perception |
| Stacked bar | Compare individual series | Grouped bar or small multiples | Stacking hides individual values |
| Donut | Show precise values | Table with conditional formatting | Donut communicates rough proportion only |
| Line (20 series) | Compare trends | Small multiples or highlight 3 key series | Too many lines become spaghetti |
| Map | Compare values | Bar chart sorted by value | Maps encode position; bars encode length (more precise) |

## Module 3: The 5-Visual Rule

Executive dashboards that work follow this constraint:

> **No more than 5 visuals per page.** Each visual answers a different question. If you need more, you need a second page, not a denser layout.

| Slot | Role | Typical chart |
| --- | --- | --- |
| 1-3 | **KPI cards** | Card, gauge, or sparkline |
| 4 | **Hero chart** | The main visual that carries the story |
| 5 | **Supporting chart** | A second angle on the same story |

A sixth visual is a table for drill-down, placed below the fold or on demand.

### Composition by Audience

| Audience | Visuals | Time budget | Design priority |
| --- | --- | --- | --- |
| Executive | 3-5 | 30 seconds | KPIs first, hero chart, one action item |
| Manager | 5-8 | 2 minutes | Filters, comparison charts, trend lines |
| Analyst | 8-15 | Unlimited | Detail tables, drill-through, cross-filters |
| General | 3-4 | 1 minute | Annotated hero chart, simple narrative |

## Module 4: Living Gallery References

Use these galleries to browse real examples when Module 1's tables aren't enough. The galleries are the living source of truth; this skill is the decision framework.

| Gallery | URL | Organized by | Best for |
| --- | --- | --- | --- |
| **FT Visual Vocabulary** | [ft-interactive.github.io/visual-vocabulary](https://ft-interactive.github.io/visual-vocabulary/) | Communication goal | Choosing chart type by what you want to say |
| **From Data to Viz** | [data-to-viz.com](https://www.data-to-viz.com/) | Data type and relationship | Choosing chart type by what your data looks like |
| **Data Viz Catalog** | [datavizcatalogue.com](https://datavizcatalogue.com/) | Chart function | Understanding individual chart strengths/weaknesses |
| **Vega-Lite Examples** | [vega.github.io/vega-lite/examples](https://vega.github.io/vega-lite/examples/) | Chart type | Declarative spec examples for programmatic generation |
| **Storytelling with Data** | [community.storytellingwithdata.com/exercises](https://community.storytellingwithdata.com/exercises) | Story challenge | Real-world "makeover" exercises with before / after |

### When to consult a gallery

- Module 1 suggests 2+ chart types and you cannot decide
- The story intent doesn't fit any standard goal group
- You need to see a real example of a chart type before committing
- Stakeholder needs visual evidence that the chart type works for their data

## Module 5: Chart Selection Decision Tree

Run this algorithm when choosing charts for a dashboard, report, or book figure:

```text
1. Write the Big Idea sentence (audience + action + evidence)
   → delegate to chart-big-idea; if you can't write it, the analysis isn't done

2. List the 3-5 questions the artifact must answer
   Each question becomes one visual

3. For each question:
   a. Identify the communication goal (Module 1 header)
   b. Check the chart catalog table
   c. Filter by data shape and audience
   d. If AI generated a chart, run CSAR (Module 2)
   e. If still unsure, consult a gallery (Module 4)

4. Apply the 5-Visual Rule (Module 3)
   Cut the weakest visual if over budget

5. Arrange by narrative flow:
   KPIs → Hero chart → Supporting → Detail

6. Author + render:
   → statistical charts: flint-chart (Vega-Lite / ECharts / Chart.js via Flint MCP)
   → structural / hand-authored SVG: figure-generator + print-svg-style-guide
   → AI-generated illustration: replicate-imagery

7. Verify: render-verify (Prose-coupling + failure catalog)
```

## Attribution

The chart catalog (Module 1), CSAR loop (Module 2), 5-visual rule (Module 3), gallery references (Module 4), and selection tree (Module 5) are adapted from the `visual-vocabulary` skill in [`fabioc-aloha/Alex_ACT_Visual_Storytelling`](https://github.com/fabioc-aloha/Alex_ACT_Visual_Storytelling) (v1.2.0, absorbed 2026-07-30). The upstream skill also carries Module 4 SVG composition patterns (panel primitive, pie sizing, dark-slate palette); those are covered in the plugin's [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md) and [`figure-generator`](../figure-generator/SKILL.md) with print-legibility math + brand-palette semantic colors, so they are not duplicated here.

FT Visual Vocabulary, Data-to-Viz, Data Viz Catalog, Vega-Lite examples, and Storytelling with Data are cited under their published URLs; this skill is a decision framework built on top of those galleries, not a replacement for them.

## Would Revise If

Revisit by 2026-10-30 (90 days) or sooner if:

- ≥3 chart types in Module 1 are reported as miscategorised or missing a "best when / avoid when" pair
- The CSAR override decision table produces the wrong verdict for a real chart choice ≥2 times in observation
- The 5-visual rule is contradicted by a working dashboard that ships more visuals without density complaints (rule too strict)
- One of the five galleries in Module 4 retires or moves; the URL check fails
- A heir installs `chart-vocabulary` and `visual-vocabulary` from the Mall on the same brain and reports confusion about which is canonical (the absorption story isn't landing)
- The selection tree in Module 5 sends a heir to the wrong plugin skill ≥2 times (routing miscalibrated)
- Zero heirs invoke this skill in the 90-day window (decoration, not load-bearing)
