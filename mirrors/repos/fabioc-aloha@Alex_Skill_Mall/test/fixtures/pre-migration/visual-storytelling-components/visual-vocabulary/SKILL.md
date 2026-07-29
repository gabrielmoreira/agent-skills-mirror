---
type: skill
lifecycle: stable
inheritance: inheritable
name: visual-vocabulary
description: Chart catalog organized by communication goal, CSAR evaluation loop for AI-generated charts, 5-visual rule, override decision framework, and living gallery references
tier: standard
applyTo: '**/*chart*,**/*visual*,**/*viz*,**/*dashboard*,**/*report*'
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Visual Vocabulary

Pick the right chart for the story you want to tell, evaluate whether an AI-generated chart choice is correct, and know when to override.

This skill is the **selection and evaluation** layer. It delegates chart design (color, annotation, decluttering) to `data-visualization` and narrative arc (three-act structure, audience framing) to `data-storytelling`. Use this skill first to decide WHAT to show; use those skills to decide HOW to show it.

## When to Use

- Choosing chart types for a dashboard, report, or data story
- Evaluating an AI-generated visualization (Copilot, ChatGPT, or any tool that auto-selects chart types)
- Building an SVG dashboard and deciding what each panel should contain
- Reviewing someone else's chart choices for story-intent alignment

## Module 1: Chart Catalog by Communication Goal

### Comparison

Show differences between items or groups.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Horizontal bar** | Ranking items; long category labels | More than 15 items (paginate or filter) |
| **Grouped bar** | Comparing 2-3 series across categories | More than 3 series (use small multiples) |
| **Dot plot** | Precise value comparison; tight ranges | Audience expects bars |
| **Slope chart** | Before/after comparison of ranked items | More than 10 items (too many crossing lines) |
| **Radar** | Multi-dimensional profile comparison | More than 7 axes; general audiences |
| **Bullet chart** | Actual vs. target with qualitative ranges | No clear target or benchmark |

### Change Over Time

Show trends, seasonality, or evolution.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Line** | Continuous data; up to 5 series | Categorical time (use bar) |
| **Area** | Emphasizing volume or magnitude of change | Multiple overlapping series (use stacked) |
| **Stacked area** | Part-to-whole composition changing over time | Need to compare individual series precisely |
| **Sparkline** | Inline trend context (KPI cards, tables) | Trend shape matters less than precise values |
| **Step line** | Discrete changes (pricing, policy, thresholds) | Continuous gradual change |
| **Small multiples** | Comparing trends across 6-20 categories | Fewer than 4 categories (use single line chart) |

### Proportion

Show part-to-whole relationships.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Donut** | 2-5 segments; one hero segment to highlight | More than 6 segments; comparing across groups |
| **Stacked bar** | Comparing composition across categories | More than 5 segments per bar |
| **Waffle** | Communicating percentages to general audiences | Precision matters (use table) |
| **Treemap** | Hierarchical part-to-whole with many items | Need to show change over time |
| **Sunburst** | Multi-level hierarchy exploration | Print or static context (needs interaction) |
| **Waterfall** | Showing additive/subtractive contributions | Non-sequential contributions |

### Distribution

Show spread, shape, or outliers.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Histogram** | Single variable distribution shape | Comparing distributions (use violin or ridgeline) |
| **Box plot** | Comparing distributions across groups | General audiences (unfamiliar format) |
| **Violin** | Distribution shape comparison across groups | Fewer than 3 groups (use histogram) |
| **Ridgeline** | Many distributions stacked for pattern scanning | Precision on individual values |
| **Scatter** | Two-variable distribution and outlier detection | Categorical data |
| **Beeswarm** | Small dataset; every point matters | More than 500 points (use density) |

### Relationship

Show correlation, causation, or connection.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Scatter** | Two continuous variables; outlier identification | Categorical variables |
| **Bubble** | Three variables (x, y, size) | More than 50 bubbles (overplotting) |
| **Heatmap** | Dense matrix relationships (correlation, time x category) | Fewer than 4x4 cells |
| **Parallel coordinates** | Multi-dimensional comparison (5+ variables) | General audiences |
| **Network graph** | Entity relationships, social connections | Hierarchical data (use tree) |
| **Chord diagram** | Bidirectional flows between categories | More than 10 categories |

### Flow and Process

Show movement, conversion, or paths.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Sankey** | Multi-stage flow with branching paths | Fewer than 3 stages (use stacked bar) |
| **Funnel** | Sequential drop-off (conversion, pipeline) | No sequential order |
| **Gantt** | Timeline with parallel activities | More than 30 tasks (filter or paginate) |
| **Swimlane** | Process flow with role/team assignments | Simple linear process |

### Deviation

Show variance from a reference point.

| Chart | Best When | Avoid When |
| --- | --- | --- |
| **Diverging bar** | Above/below target or median | No clear reference point |
| **Lollipop** | Deviation from baseline; cleaner than bars | Audience expects standard bars |
| **Line + reference** | Trend deviation from target over time | Multiple baselines |
| **Gauge** | Single KPI vs. target (dashboards, KPI cards) | More than 3 gauges on a page |

## Module 2: The CSAR Evaluation Loop

When an AI tool generates a chart, evaluate before accepting. Adapted from the Copilot Design Automation framework:

| Step | Question | Action |
| --- | --- | --- |
| **Clarify** | "What question am I answering?" | Write the question as a sentence before looking at the chart |
| **Summarize** | "The AI chose a [chart type]. Does it answer the question?" | Name the chart type and check it against Module 1 |
| **Act** | Accept, modify, or override | Accept if story-intent matches. Override if wrong goal group. Modify if right type but wrong emphasis |
| **Reflect** | "Why did I accept/override? What principle guided me?" | Document the rationale; builds judgment over time |

### Override Decision Table

| AI Chose | But Your Goal Is | Override To | Rationale |
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

| Slot | Role | Typical Chart |
| --- | --- | --- |
| 1-3 | **KPI cards** | Card, gauge, or sparkline |
| 4 | **Hero chart** | The main visual that carries the story |
| 5 | **Supporting chart** | A second angle on the same story |

A sixth visual is a table for drill-down, placed below the fold or on demand.

### Composition by Audience

| Audience | Visuals | Time Budget | Design Priority |
| --- | --- | --- | --- |
| Executive | 3-5 | 30 seconds | KPIs first, hero chart, one action item |
| Manager | 5-8 | 2 minutes | Filters, comparison charts, trend lines |
| Analyst | 8-15 | Unlimited | Detail tables, drill-through, cross-filters |
| General | 3-4 | 1 minute | Annotated hero chart, simple narrative |

## Module 4: SVG Dashboard Composition Patterns

Lessons from building production SVG dashboards:

### Panel Primitive

Every card in an SVG dashboard uses one function:

```
panel({ x, y, w, h, title, subtitle, color })
```

Constants: radius 16, fill #0f172a (dark slate), stroke #334155, title at y+32. One primitive, every card looks the same. Visual uniformity builds trust.

### Pie Chart Sizing

- Radius must fit within card boundaries with 40px margin on all sides
- Donut hole (inner radius) = 33% of outer radius for center labels
- Never more than 6 slices; group the rest as "Other"
- Center label for total count or primary metric

### Bar Chart Spacing

- Row height: 32px per bar (readable text + bar + gap)
- Label width: 40% of card width; bar width: 50%; value: 10%
- Longest bar fills the available width; others scale proportionally
- Sort by value descending (unless time-ordered)

### Color Palette (Dark Slate Theme)

| Use | Hex | Name |
| --- | --- | --- |
| Card background | #0f172a | Slate 950 |
| Card stroke | #334155 | Slate 700 |
| Primary text | #ffffff | White |
| Secondary text | #cbd5e1 | Slate 300 |
| Muted text | #94a3b8 | Slate 400 |
| Tertiary text | #64748b | Slate 500 |
| Positive/complete | #22c55e | Green 500 |
| Warning/pending | #f59e0b | Amber 500 |
| Error/critical | #ef4444 | Red 500 |
| Info/accent | #3b82f6 | Blue 500 |
| Purple accent | #8b5cf6 | Violet 500 |

### Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Pie arcs computed at wrong center coordinates | Calculate center from card y + card height, not absolute y |
| Incremental y-shifts corrupting multi-row layouts | Define each row's y from scratch (row N y = header + sum of previous row heights + gaps) |
| Labels bleeding outside card boundaries | Max y of any element = card y + card height - margin |
| Different font sizes per card | One title size (20px), one body size (13px), one muted size (11px) across all cards |
| Inline coordinate math | Define constants at the top: ROW_Y[], CARD_W, CARD_H, GAP |

## Module 5: Living Gallery References

Use these galleries to browse real examples when Module 1's table isn't enough. The galleries are the living source of truth; this skill is the decision framework.

| Gallery | URL | Organized By | Best For |
| --- | --- | --- | --- |
| **FT Visual Vocabulary** | https://ft-interactive.github.io/visual-vocabulary/ | Communication goal | Choosing chart type by what you want to say |
| **From Data to Viz** | https://www.data-to-viz.com/ | Data type and relationship | Choosing chart type by what your data looks like |
| **Data Viz Catalogue** | https://datavizcatalogue.com/ | Chart function | Understanding individual chart strengths/weaknesses |
| **Vega-Lite Examples** | https://vega.github.io/vega-lite/examples/ | Chart type | Declarative spec examples for programmatic generation |
| **Storytelling with Data** | https://community.storytellingwithdata.com/exercises | Story challenge | Real-world "makeover" exercises with before/after |

### When to Consult a Gallery

- Module 1 suggests 2+ chart types and you cannot decide
- The story intent doesn't fit any standard goal group
- You need to see a real example of a chart type before committing
- Client or stakeholder needs visual evidence that the chart type works for their data

## Module 6: Chart Selection Decision Tree

Run this algorithm when choosing charts for a dashboard or report:

```
1. Write the Big Idea sentence
   (audience + action + evidence)
   If you can't write it, the analysis isn't done.

2. List the 3-5 questions the dashboard must answer
   Each question becomes one visual.

3. For each question:
   a. Identify the communication goal (Module 1 header)
   b. Check the chart catalog table
   c. Filter by data shape and audience
   d. If AI generated a chart, run CSAR (Module 2)
   e. If still unsure, consult a gallery (Module 5)

4. Apply the 5-Visual Rule (Module 3)
   Cut the weakest visual if over budget.

5. Arrange by narrative flow:
   KPIs -> Hero chart -> Supporting -> Detail
   (delegate to dashboard-design for layout patterns)

6. Design each chart:
   (delegate to data-visualization for color,
    annotation, decluttering)
```

## Cross-References

- `data-visualization` -- color theory, annotation patterns, decluttering rules. Use after this skill selects chart types.
- `data-storytelling` -- three-act narrative structure, audience-first framing, Big Idea worksheet. Use before this skill to define the story.
- `dashboard-design` -- layout patterns, KPI card design, filter architecture. Use after this skill to arrange the visuals.
- `svg-dashboard-composition` -- SVG composition mechanics, panel primitives, coordinate systems. Use when the output format is SVG.
- `chart-interpretation` -- reading and evaluating existing charts. The inverse of this skill.
