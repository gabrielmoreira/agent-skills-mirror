---
type: skill
lifecycle: stable
inheritance: inheritable
name: data-visualization
description: Story-intent chart selection, color theory, annotation patterns, decluttering rules, and the "title = insight" principle for data-driven visuals
tier: standard
applyTo: '**/*data*,**/*visualization*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Skill: Data Visualization


> Choose the right chart for the story, not just the data shape. Every chart should make an argument.

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

## Metadata

| Field              | Value                                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| **Skill ID**       | data-visualization                                                                                                             |
| **Version**        | 1.0.0                                                                                                                          |
| **Category**       | Data Analytics                                                                                                                 |
| **Difficulty**     | Intermediate                                                                                                                   |
| **Prerequisites**  | None                                                                                                                           |
| **Related Skills** | data-analysis, dashboard-design, data-storytelling, chart-interpretation, executive-storytelling, slide-design, graphic-design |

## Overview

Data visualization is not chart generation -- it is **visual argumentation**. The chart type, color palette, annotation, and title are all rhetorical choices that either strengthen or weaken the story.

### Core Principles

| Principle                 | Rule                                                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Title = Insight**       | Chart titles state the takeaway, not the data label. "California leads with 39M" not "Population by State" |
| **Story-Intent First**    | Ask "what story?" before "what chart?"                                                                     |
| **Data-Ink Ratio**        | Every pixel of ink should represent data. Remove everything else (Tufte)                                   |
| **3-Second Test**         | If a viewer can't grasp the point in 3 seconds, redesign                                                   |
| **Annotation = Argument** | Callouts carry the story; the chart is evidence, the annotation is the argument                            |

## Module 1: Story-Intent Chart Selection

The primary axis for chart selection is **what story the user wants to tell**. Data shape is a secondary constraint.

### Step 1 -- Identify Story Intent

| Story Intent         | Question Being Answered                          | Primary Charts                           | Advanced Charts                       |
| -------------------- | ------------------------------------------------ | ---------------------------------------- | ------------------------------------- |
| **Compare**          | "How do these items rank or differ?"             | Bar, Horizontal Bar, Grouped Bar, Radar  | Beeswarm, Parallel Coordinates        |
| **Change Over Time** | "How has this evolved?"                          | Line, Area, Stacked Area                 | Streamgraph, Ridgeline                |
| **Part-to-Whole**    | "What share does each segment hold?"             | Donut, Stacked Bar, Pie                  | Waffle, Sunburst                      |
| **Distribution**     | "How is this spread? What's normal vs. outlier?" | Histogram, Scatter                       | Violin, Beeswarm, Ridgeline           |
| **Relationship**     | "How are these variables connected?"             | Scatter, Bubble                          | Chord, Network Graph, Parallel Coords |
| **Flow / Process**   | "Where does it go? What are the paths?"          | Horizontal Bar (stages)                  | Sankey, Chord                         |
| **Hierarchy**        | "How is this organized in levels?"               | Treemap                                  | Sunburst                              |
| **Spatial Pattern**  | "Where are the concentrations?"                  | Heatmap                                  | Network Graph                         |
| **Deviation**        | "What deviates from the baseline?"               | Bar (diverging), Line (+ reference line) | Beeswarm                              |

### Step 2 -- Narrow by Data Shape

| Data Shape                  | Compatible Intents                   | Ruled Out                       |
| --------------------------- | ------------------------------------ | ------------------------------- |
| Categorical + numeric       | Compare, Part-to-Whole, Distribution | Flow (unless sequential)        |
| Two numeric variables       | Relationship, Distribution           | Part-to-Whole                   |
| Time series                 | Change Over Time, Deviation          | Hierarchy                       |
| Network / adjacency         | Relationship, Flow                   | Part-to-Whole, Change Over Time |
| Hierarchical (parent-child) | Hierarchy, Part-to-Whole             | Change Over Time, Distribution  |
| Flow matrix (source-target) | Flow, Relationship                   | Compare (use grouped bar)       |

### Step 3 -- Audience & Context Filter

| Choose Standard When                  | Choose Advanced When                          |
| ------------------------------------- | --------------------------------------------- |
| Audience expects familiar shapes      | Complex relationships (flows, networks)       |
| Tooltip interactivity is critical     | Distribution shape matters more than values   |
| Chart.js handles the data shape       | Hierarchical structure needs multi-level view |
| Dashboard has 3+ charts (consistency) | Single hero viz to anchor a story             |
| Executive audience (30s scan)         | Analyst audience (exploration expected)       |

### Story-Intent Detection Heuristics

When the user doesn't state intent explicitly, infer from language:

| User Language                                          | Inferred Intent  |
| ------------------------------------------------------ | ---------------- |
| "rank", "compare", "versus", "top", "best/worst"       | Compare          |
| "over time", "trend", "growth", "decline", "monthly"   | Change Over Time |
| "share", "proportion", "breakdown", "percent of"       | Part-to-Whole    |
| "spread", "range", "outlier", "normal", "distribution" | Distribution     |
| "correlation", "relationship", "predict", "affects"    | Relationship     |
| "flow", "path", "from X to Y", "conversion", "funnel"  | Flow / Process   |
| "hierarchy", "drill down", "parent/child", "levels"    | Hierarchy        |
| "where", "hotspot", "concentration", "geographic"      | Spatial Pattern  |
| "deviation", "variance", "above/below target", "gap"   | Deviation        |

## Module 2: Narrative Chart Pairing

A single chart tells one point. Paired charts reinforce the insight from a second angle.

| Primary Chart          | Good Pair                               | Why                                     |
| ---------------------- | --------------------------------------- | --------------------------------------- |
| Bar (compare)          | Donut (proportion)                      | Shows both absolute and relative size   |
| Line (trend)           | Bar (change amount)                     | Shows direction and magnitude           |
| Scatter (relationship) | Histogram (distribution)                | Shows correlation and individual spread |
| Treemap (hierarchy)    | Table (detail)                          | Shows structure and precise values      |
| Sankey (flow)          | Stacked bar (proportions at each stage) | Shows paths and stage composition       |

### The Inverted Pyramid Pattern

From `population.html` reference -- arrange visuals in absorption order:

| Layer | Component         | Time to Absorb | Purpose                        |
| ----- | ----------------- | -------------- | ------------------------------ |
| 1     | KPI cards         | 2 seconds      | "What's the big picture?"      |
| 2     | Hero chart        | 10 seconds     | Full distribution, interactive |
| 3     | Supporting charts | 15 seconds     | Same data, different lens      |
| 4     | Table             | As needed      | Precise values for analysts    |
| 5     | Drill-down        | On click       | Detail without clutter         |

## Module 3: Color Theory

### Mandatory: Colorblind-Safe Palette

All chart output MUST use a colorblind-safe palette. The canonical palette for all the AI assistant charting skills is **Tableau 10**, verified against deuteranopia, protanopia, and tritanopia:

```
#4e79a7  Blue-Steel   (primary)
#f28e2b  Orange
#e15759  Coral
#76b7b2  Teal
#59a14f  Sage
#edc948  Gold
#b07aa1  Mauve
#ff9da7  Rose
#9c755f  Brown
#bab0ac  Warm Gray
```

| Palette                   | Colors                                                    | Use Case                   |
| ------------------------- | --------------------------------------------------------- | -------------------------- |
| **Categorical (default)** | First N colors from the canonical 10 above                | Unordered categories       |
| **Sequential Blue**       | `#deebf7 → #08519c`                                       | Low-to-high numeric        |
| **Diverging RdBu**        | `#b2182b → #f7f7f7 → #2166ac`                             | Above/below midpoint       |
| **Semantic Region**       | Consistent color per category across all charts on a page | Region, department, status |

### Color Rules (Non-Negotiable)

| Rule                            | Explanation                                                                               |
| ------------------------------- | ----------------------------------------------------------------------------------------- |
| **Always colorblind-safe**      | Never use a palette that has not been tested for deuteranopia, protanopia, and tritanopia |
| **Semantic consistency**        | Same color = same meaning across all charts on a page                                     |
| **Highlight, don't decorate**   | Use saturated color for the key data point; mute everything else                          |
| **Sequential for ordered data** | Light-to-dark for low-to-high                                                             |
| **Diverging for deviation**     | Two hues diverging from neutral midpoint                                                  |
| **Never rely on color alone**   | Add patterns, labels, or shapes for accessibility                                         |
| **Test with Sim Daltonism**     | Verify with protanopia and deuteranopia simulation                                        |

### WCAG Contrast Requirements

| Context             | Minimum Ratio              |
| ------------------- | -------------------------- |
| Text on background  | 4.5:1 (AA), 7:1 (AAA)      |
| Chart labels        | 4.5:1 minimum              |
| Data vs. background | 3:1 for graphical elements |

## Module 4: Decluttering (Tufte's Data-Ink Ratio)

Every element must earn its place. Remove anything that doesn't carry data.

| Remove                    | Replace With                         |
| ------------------------- | ------------------------------------ |
| Gridlines                 | Light reference lines only if needed |
| Borders around chart area | White space separation               |
| Legends (when possible)   | Direct labels on data                |
| Background fills          | Transparent / minimal                |
| 3D effects                | Never. Always flat.                  |
| Redundant axis labels     | Context in title or subtitle         |

### Before/After Anti-Patterns

| Anti-Pattern       | Problem                 | Fix                              |
| ------------------ | ----------------------- | -------------------------------- |
| Rainbow palette    | No semantic meaning     | Use 2-3 purposeful colors        |
| Every bar labeled  | Visual noise            | Label key values only            |
| Dual Y axes        | Misleading correlation  | Two separate charts              |
| Pie with 8+ slices | Unreadable              | Horizontal bar, sorted           |
| Missing axis zero  | Exaggerated differences | Start at zero or note truncation |

## Module 5: Annotation Hierarchy

| Element      | Content                                                 | Rule               |
| ------------ | ------------------------------------------------------- | ------------------ |
| **Title**    | The insight ("Sales peaked at $4.2M in Q3")             | Never a data label |
| **Subtitle** | Context ("Quarterly revenue, FY 2024-2025")             | Who, what, when    |
| **Callout**  | The exception ("Q1 2025: +31% jump -- pricing change?") | Arrow or highlight |
| **Footnote** | Caveats ("Excludes returns. Source: SAP ERP.")          | Small, bottom      |
| **Source**   | Data provenance                                         | Always present     |

## Module 6: Small Multiples

Use faceted views when a single chart would be overloaded.

| Use Small Multiples When              | Use Overlay When          |
| ------------------------------------- | ------------------------- |
| 5+ series on one chart                | 2-3 series that interact  |
| Each series has its own pattern       | Comparison is the point   |
| Reader needs to see individual shapes | Relative position matters |

### Implementation

```
Grid: 2x3 or 3x4 panels
Each panel: Same axes, same scale (critical!)
Difference: One variable changes per panel (category, time period, cohort)
```

## Module 7: Accessibility

| Requirement       | Implementation                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------ |
| **Alt text**      | Describe the chart's insight, not its structure ("Revenue grew 34% in 2024" not "Bar chart showing revenue") |
| **Patterns**      | Add hatching or shapes alongside color                                                                       |
| **Keyboard**      | Tab-navigable data points in interactive charts                                                              |
| **Screen reader** | `aria-label` on chart container, data table fallback                                                         |
| **High contrast** | Test in Windows High Contrast mode                                                                           |

## Module 8: Tool Targets

| Target                | Library                | Output                    | When                              |
| --------------------- | ---------------------- | ------------------------- | --------------------------------- |
| HTML (self-contained) | Chart.js 4.x via CDN   | `.html` file              | Default -- zero-config dashboards |
| HTML (advanced)       | Raw Canvas 2D API      | `.html` file              | Sankey, Chord, Sunburst, etc.     |
| Python                | Plotly                 | Interactive HTML/notebook | Data science workflows            |
| Python (static)       | Matplotlib + Seaborn   | PNG/SVG                   | Publications, reports             |
| Markdown              | Mermaid                | Inline in docs            | Documentation, PRs                |
| Power BI              | DAX measures + visuals | .pbix                     | Enterprise BI                     |

### Chart.js Configuration Defaults

```javascript
// Standard Chart.js defaults for all data-viz skills
Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.plugins.legend.display = false; // prefer direct labels
Chart.defaults.scales.x.grid.display = false; // declutter
Chart.defaults.scales.y.grid.color = "rgba(255,255,255,0.06)"; // subtle
Chart.defaults.plugins.tooltip.backgroundColor = "rgba(0,0,0,0.85)";
```

## Module 9: Advanced Canvas Charts

10 chart types rendered with raw Canvas 2D API -- no extra dependencies beyond the browser.

| Chart                    | Story Intent           | Data Shape              | Key Technique                       |
| ------------------------ | ---------------------- | ----------------------- | ----------------------------------- |
| **Sankey**               | Flow                   | Source-target-value     | Bezier curves between stacked bars  |
| **Chord**                | Relationship           | Adjacency matrix        | Circular arcs with ribbons          |
| **Streamgraph**          | Change Over Time       | Multi-series time       | Stacked area with centered baseline |
| **Sunburst**             | Hierarchy              | Parent-child            | Concentric arcs, angular proportion |
| **Parallel Coordinates** | Compare (multi-dim)    | Many numeric columns    | Vertical axes, polylines            |
| **Beeswarm**             | Distribution           | Categorical + numeric   | Force-separated dots on axis        |
| **Ridgeline**            | Distribution (compare) | Series of distributions | Overlapping density curves          |
| **Waffle**               | Part-to-Whole          | Percentages             | Grid of colored squares             |
| **Network Graph**        | Relationship           | Nodes + edges           | Force-directed layout               |
| **Violin**               | Distribution           | Grouped distributions   | Mirrored density curves             |

### Canvas Rendering Pattern

```javascript
// Standard pattern for all advanced charts
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const dpr = window.devicePixelRatio || 1;
canvas.width = canvas.clientWidth * dpr;
canvas.height = canvas.clientHeight * dpr;
ctx.scale(dpr, dpr);
// ... render logic
```

## Reference Implementations

| File               | Charts             | Pattern                                        |
| ------------------ | ------------------ | ---------------------------------------------- |
| `visuals.html`     | 14 standard types  | Card grid, mini/full pairs, per-chart metadata |
| `adv_visuals.html` | 10 advanced types  | Canvas-only rendering, zero dependencies       |
| `population.html`  | 4 dashboard charts | Inverted pyramid, narrative flow, drill-down   |

## Anti-Patterns

| Anti-Pattern                    | Why It Fails                                | Fix                                         |
| ------------------------------- | ------------------------------------------- | ------------------------------------------- |
| "Chart type first, data second" | Picks visual before understanding the story | Start with story intent                     |
| Title just labels axes          | No argument, no insight                     | Write a sentence the viewer should conclude |
| Rainbow palette on categories   | No semantic meaning, accessibility failure  | Max 2-3 purposeful hues                     |
| Dual Y axes                     | Implies false correlation                   | Two separate charts                         |
| Pie chart with 8+ slices        | Unreadable, angle perception is poor        | Sorted horizontal bar                       |
| 3D anything                     | Distorts perception, adds zero information  | Always flat                                 |
| Default gridlines               | Clutter that competes with data             | Remove or make very subtle                  |
