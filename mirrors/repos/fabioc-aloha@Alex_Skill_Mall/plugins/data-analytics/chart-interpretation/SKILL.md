---
type: skill
lifecycle: stable
inheritance: inheritable
name: chart-interpretation
description: Read any chart (image, HTML, screenshot) and extract insights, patterns, anomalies, bias, and narrative -- the reverse of visualization
tier: standard
applyTo: '**/*chart*,**/*interpretation*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Chart Interpretation


| Property     | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| **Domain**   | Data Analytics                                                        |
| **Category** | Visual Analysis & Insight Extraction                                  |
| **Components** | SKILL.md + chart-interpretation.instructions.md + interpret.prompt.md |
| **Depends**  | data-visualization (chart type knowledge), data-analysis (validation) |

## Overview

The reverse of data visualization. Instead of data → chart, this skill reads chart → insights → narrative. It extracts meaning from existing charts (screenshots, images, HTML, Power BI reports) and produces structured analysis adapted to the target audience.

The cardinal rule: **read what the chart says, then read what it doesn't say**. The visible data points tell one story; the missing context, truncated axes, and suppressed categories tell another.

## Module 1: Chart Type Recognition

Identify the chart type to determine the correct reading strategy.

| Chart Type       | Key Visual Features                    | Reading Strategy                          |
| ---------------- | -------------------------------------- | ----------------------------------------- |
| Bar / Column     | Rectangular bars, one axis categorical | Compare bar lengths, check sort order     |
| Horizontal Bar   | Bars extend left-to-right              | Rank comparison, read labels first        |
| Line             | Connected points over axis             | Follow trend direction, find inflections  |
| Area             | Filled region under line               | Volume over time, stacking if multiple    |
| Pie / Donut      | Circular segments                      | Part-to-whole, count segments, check %    |
| Scatter           | Points in x-y space                   | Look for clusters, outliers, trend line   |
| Bubble           | Scatter with size encoding             | Three dimensions: x, y, size             |
| Histogram        | Bars touching, x is continuous         | Distribution shape, skew, outliers       |
| Heatmap          | Color grid                             | Pattern density, row-column relationships |
| Treemap          | Nested rectangles                      | Hierarchical proportions                  |
| Sankey           | Flow ribbons between stages            | Volume flow, biggest paths               |
| Box Plot         | Box + whiskers                         | Median, IQR, outlier dots                |
| Network          | Nodes + edges                          | Clusters, hubs, isolates                 |
| Violin           | Mirrored density curves                | Distribution shape + density             |

## Module 2: Visual Decoding

Extract data from visual encodings:

| Encoding         | What to Read                          | Precision Level     |
| ---------------- | ------------------------------------- | ------------------- |
| Position (axis)  | Exact values from gridlines/labels    | High (if labeled)   |
| Length (bar)      | Relative magnitude between items     | High                |
| Color hue        | Category membership                   | Categorical only    |
| Color intensity  | Value magnitude in sequential scheme  | Medium              |
| Size (area)      | Third variable (bubble, treemap)      | Low (area perception is poor) |
| Angle (pie)      | Proportion (poor human accuracy)      | Low                 |
| Slope (line)     | Rate of change                        | Medium              |

## Module 3: Pattern Detection

| Pattern          | What to Look For                        | Significance                           |
| ---------------- | --------------------------------------- | -------------------------------------- |
| **Trend**        | Consistent upward/downward direction    | Growth, decline, momentum              |
| **Inflection**   | Direction change point                  | Market shift, intervention effect      |
| **Plateau**      | Flat region after growth/decline        | Saturation, stabilization              |
| **Cluster**      | Groups of points in scatter/network     | Natural segments, sub-populations      |
| **Outlier**      | Points far from the main group          | Anomaly, error, or special case        |
| **Periodicity**  | Repeating pattern at intervals          | Seasonality, weekly cycle              |
| **Gap**          | Missing data or discontinuity           | Data quality issue or deliberate omission |
| **Skew**         | Asymmetric distribution shape           | Non-normal population, concentration   |
| **Dominance**    | One item >> all others                  | Power law, market leader, outlier      |

## Module 4: Misleading Visual Detection

Check every chart for these deceptive patterns:

| Deception                  | How to Detect                                              | Actual Impact                          |
| -------------------------- | ---------------------------------------------------------- | -------------------------------------- |
| **Non-zero baseline**      | Y-axis starts above 0                                      | Exaggerates differences (sometimes 2-5x)|
| **Truncated axis**         | Axis range excludes data or starts mid-range               | Hides context, magnifies small changes |
| **Dual axes**              | Two Y-axes with different scales                           | Implies correlation where none may exist|
| **3D effects**             | Perspective distortion on bars/pies                        | Area comparison becomes inaccurate     |
| **Cherry-picked range**    | Time window starts/ends at convenient point                | Hides contrary trend outside window     |
| **Suppressed categories**  | "Other" aggregates significant items                       | Hides important segments               |
| **Area distortion**        | Variable-width bars, non-proportional icons                | Size doesn't match value               |
| **Missing denominator**    | Percentages without base size                              | 50% of 10 ≠ 50% of 10,000            |
| **Reversed axis**          | Values increase downward or rightward                      | Readers misread direction              |

## Module 5: Structural Element Reading

Always read these elements before interpreting the data:

| Element          | What to Extract                        | If Missing                              |
| ---------------- | -------------------------------------- | --------------------------------------- |
| **Title**        | Author's intended takeaway             | Chart lacks stated purpose              |
| **Subtitle**     | Time range, filter condition, context  | Context must be inferred                |
| **Axes labels**  | What variables are plotted             | Interpretation becomes guesswork        |
| **Legend**        | Category-to-color mapping             | Color meaning unclear                   |
| **Annotations**  | Author-highlighted insights            | No guided reading                       |
| **Data source**  | Where the data came from              | Credibility unknown                     |
| **Date/time**    | When data was collected/reported       | Freshness unknown                       |

## Module 6: Narrative Extraction

Convert visual observations into prose at three audience levels:

### Executive Summary (30 seconds)

```
3 bullets maximum:
• [Primary insight — the main takeaway]  
• [Supporting evidence — the strongest proof point]  
• [Recommendation or implication — what to do about it]
```

### Detailed Analysis (2-3 minutes)

```
The chart shows [chart type] plotting [X variable] against [Y variable]
for [time range / scope].

Primary finding: [Main pattern or insight with specific numbers]

Supporting observations:
- [Pattern 1 with evidence]
- [Pattern 2 with evidence]
- [Anomaly or exception worth noting]

Context and caveats:
- [What the chart doesn't show]
- [Potential biases or limitations]
- [Comparison to benchmarks if available]
```

### Talking Points (presenter-ready)

```
"What you're seeing here is [explain the main pattern in plain language]."
"The key number to focus on is [highlight], which tells us [implication]."
"What's interesting is [surprise or anomaly] — this suggests [hypothesis]."
"The action item here is [recommendation]."
```

## Module 7: Confidence Rating

Rate interpretation confidence honestly:

| Level    | When                                            | Signal to User                           |
| -------- | ----------------------------------------------- | ---------------------------------------- |
| **High** | Clear labels, clean data, familiar chart type   | "The chart clearly shows..."             |
| **Medium** | Some inference needed (unlabeled, partial data) | "Based on visual estimation..."        |
| **Low**  | Ambiguous visual, missing context, blurry image | "This appears to show, but verify..."   |

## Module 8: Follow-Up Recommendations

After interpreting, suggest what would strengthen the analysis:

| Suggestion Type         | Example                                                    |
| ----------------------- | ---------------------------------------------------------- |
| Missing variable        | "Add cost data to see if revenue growth is profitable"     |
| Time extension          | "Extend to 24 months to confirm the seasonal pattern"      |
| Segmentation            | "Break this down by region to check for Simpson's Paradox" |
| Alternative chart       | "A scatter plot would better show the correlation"          |
| Baseline addition       | "Add a target line to show performance vs. plan"           |

## Module 9: CSAR Loop Integration

Use the Dialog Engineering CSAR Loop for structured chart reading:

| Phase        | Action                                                |
| ------------ | ----------------------------------------------------- |
| **Clarify**  | What chart type? What variables? What time range?     |
| **Summarize**| State the main finding in one sentence                |
| **Act**      | Extract specific data points, patterns, anomalies     |
| **Reflect**  | What's missing? What would I want to see next?        |

## Anti-Patterns

| Anti-Pattern              | Problem                                    | Fix                                      |
| ------------------------- | ------------------------------------------ | ---------------------------------------- |
| Describing, not interpreting | "This is a bar chart" (no insight)       | Say what the bars MEAN, not what they ARE|
| Ignoring the title         | Missing the author's intended message     | Read title first -- it's the thesis      |
| Over-precision from visual | "Revenue is exactly $4,237,892"           | Estimate from visual: "roughly $4.2M"    |
| Missing bias check         | Accepting the chart at face value         | Always scan for misleading elements      |
| Single-lens reading        | Only one interpretation offered           | Provide primary + alternative reading    |
