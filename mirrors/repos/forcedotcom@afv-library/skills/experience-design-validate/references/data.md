# Data & Analytics

> **Skip this reference if the design has no charts, dashboards, metrics, filters, search, tables, or lists — nothing that turns numbers into something you can feel.**

Data is where craft is most often abandoned and most rewarded when it isn't. A chart that's titled with the question it answers, colored with one accent and a chorus of grays, sorted purposefully, and stripped of non-data ink — that chart respects the reader. A dashboard that opens with the most important metric in the top-left and surfaces anomalies first feels like it was designed by someone who had to use it. The craft is in restraint: fewer colors, fewer gridlines, no rainbow scales, no truncated axes, no decorative donut centers.

## Why this matters

A well-crafted data view tells you something in five seconds. A poorly crafted one shows you a screenful of numbers and trusts you to figure out what matters. The difference is rarely about the data itself — it's about composition, hierarchy, color discipline, number formatting, and the dozens of small decisions that determine whether a chart feels like an artifact of clear thinking or a default chart-library output. When data is presented with craft, the product feels analytical and trustworthy. When it isn't, even accurate numbers feel suspect, and the reader has to do the work the designer should have done.

---

## Charts

- **Each chart answers one question.** The title tells the reader what they're about to learn. A chart with a generic label like "Sales" has wasted its opening line.
- **The chart type fits the data.** Bars compare categories, lines show trends over time, pies show parts of a whole — and only when there are few enough slices to read at a glance. A bar chart for time-series, a pie chart with a dozen slices, or a scatter plot used for ranking all read as defaults. Tables outperform charts when the user needs exact values.
- **Restraint carries the visual weight.** Gridlines fade to the lightest element. 3D effects are gone. Bars are sorted with intent. The Y-axis on bar charts starts at zero — truncated axes read as misleading.
- **Annotations highlight the takeaway.** A callout, a highlighted point, a trend indicator — the chart doesn't make the reader hunt for the message. Projected and historical data look different.

## Color in Charts

- **Color discipline carries the message.** Sequential data uses a single hue light to dark; diverging data meets at a meaningful midpoint. Categorical palettes stay small. Beyond a handful of distinct hues, the eye gives up.
- **The accent color marks what matters.** The most important series wears the brand color; everything else recedes to gray. Emphasis comes from muting context, not brightening every line.
- **Semantic color is consistent across the product.** Green always means good. Red always means bad. Reversing that mapping in one chart undoes instinct everywhere.

## Metrics

- **Every metric carries context.** A number alone says less than a number with a comparison, a target, or a trend. A metric without context is decoration.
- **Number formatting is uniform.** Same separators, same decimal precision, same units across the same view. Two formats for the same metric type undoes the calm of a dashboard. Zero is not null — "—" or "No data" tells the user nothing was measured.

## Dashboards

- **The dashboard answers articulable questions.** If the team can't say what questions it's for, it's a data gallery. Hierarchy walks the eye top-left to bottom-right; anomalies surface first; widgets sit on a grid.
- **The time range is global and visible.** A single control governs the dashboard. Comparison mode pairs current and prior data clearly. Drill-down is invited from each summary.

## Filters and Search

- **Filters apply immediately for cheap operations; expensive ones get an Apply button.** Active filters are unmistakably visible — chips above the content, clear individually and in total. Empty results explain themselves and offer a way to broaden.
- **Search scope is communicated.** Matching text is highlighted in results. Clearing search preserves filters; clearing filters preserves search.

## Tables and Lists

- **Format reflects how users use the data.** Compare, scan, act, or distribute — each pattern wants a different shape. The most important column reads first. Default sort matches the user's most common need.
- **Bulk actions float, never push.** Calculations live in a footer when they matter. View switching preserves filters and selection. Auto-refresh doesn't shove the user around.
- **Raw database fields and ISO timestamps never reach the user.** A field labeled `created_at_utc` or a timestamp like `2024-03-14T17:32:01.000Z` reads as a leaked implementation detail.

---

## Scoring Guide

**Contributes to dimensions: Useful, Coherent**

| Score | Criteria |
|-------|----------|
| 9-10 | Data presentations form a coherent system. Charts answer specific questions. Metrics carry context. Dashboards lead with anomalies. Filters and search are predictable. |
| 7-8 | Most data has context and consistent formatting. Minor gaps in chart-color discipline or filter behavior. |
| 5-6 | Mixed number formats, metrics without comparison, charts with truncated axes, filter state lost on navigation. |
| 3-4 | Misleading visualizations. Inconsistent semantic color. Numbers without units. Tables show raw fields. |
| 1-2 | No coherent data presentation. Charts mislead. Metrics carry no meaning. |
