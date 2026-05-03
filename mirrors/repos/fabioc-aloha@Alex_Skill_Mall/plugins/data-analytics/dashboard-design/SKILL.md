---
type: skill
lifecycle: stable
inheritance: inheritable
name: dashboard-design
description: Dashboard layout patterns, KPI card design, filter architecture, narrative flow through panels, and self-contained HTML generation
tier: standard
applyTo: '**/*dashboard*,**/*design*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Dashboard Design


| Property     | Value                                                                  |
| ------------ | ---------------------------------------------------------------------- |
| **Domain**   | Data Analytics                                                         |
| **Category** | Dashboard Architecture & Layout                                        |
| **Components** | SKILL.md + dashboard-design.instructions.md + dashboard.prompt.md      |
| **Depends**  | data-visualization (chart content), data-analysis (KPIs and segments)  |

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

## Overview

Design dashboards that tell stories through layout. A dashboard is not a collection of charts -- it's a guided reading experience where position, size, and interaction design control what the viewer understands and in what order.

The cardinal rule: **reading order = story order**. KPIs answer "what?", charts answer "why?", tables answer "how much?", and drill-downs answer "show me more."

## Module 1: Layout Patterns

| Pattern           | Best For                  | Reading Flow                               | Use When                                       |
| ----------------- | ------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Inverted Pyramid  | Executive dashboards      | KPIs → hero chart → supporting → detail    | Audience scans from top, drills as needed       |
| Z-Pattern         | Marketing / consumer      | Top-left → top-right → bottom-left → end   | Two primary metrics side-by-side               |
| F-Pattern         | Data-heavy analytics      | Left column scanned top-down, right detail | Dense detail dashboards for analysts           |
| Hub-and-Spoke     | Exploration dashboards    | Central question, surrounding perspectives | When multiple equally important views exist    |
| Narrative Scroll  | Data stories / reports    | Top-to-bottom linear reading               | Self-contained HTML stories with guided arc    |

### Reference Pattern: Inverted Pyramid (from population.html)

```
┌────────────────────────────────────────────────────┐
│ HEADER: Title + subtitle + badge                   │
├────────────────────────────────────────────────────┤
│ KPI ROW: 3-6 cards (auto-fit grid)                 │
├────────────────────────────────────────────────────┤
│ CONTROLS: Search + filter buttons                  │
├────────────────────────────────────────────────────┤
│ HERO CHART: Full-width, clickable                  │
├───────────────────────┬────────────────────────────┤
│ SUPPORTING CHART 1    │ SUPPORTING CHART 2         │
├───────────────────────┴────────────────────────────┤
│ DATA TABLE: Sortable, ranked, inline indicators    │
├────────────────────────────────────────────────────┤
│ FOOTER: Data source + attribution + last updated   │
└────────────────────────────────────────────────────┘

         ┌── DRILL-DOWN MODAL ──┐
         │ Detail stats grid     │
         │ Horizontal bar        │
         │ Detail table          │
         └───────────────────────┘
```

## Module 2: KPI Card Design

Each KPI card follows the **metric + delta + context** pattern:

| Element      | Purpose                           | Example                    |
| ------------ | --------------------------------- | -------------------------- |
| Primary value| The headline number               | "334M"                     |
| Label        | What it measures                  | "Total Population"         |
| Delta        | Change indicator (arrow + %)      | "↑ 2.1% YoY"              |
| Sparkline    | Trend miniature (optional)        | Tiny 30-day line           |
| Subtitle     | Time range or source              | "2024 Census estimate"     |
| Icon/Emoji   | Visual anchor                     | "👥"                       |
| Accent color | Category signal                   | Brand purple               |

### KPI Selection Rules

| Rule                         | Why                                                    |
| ---------------------------- | ------------------------------------------------------ |
| 3-6 KPIs maximum             | More overwhelms; fewer under-informs                   |
| Each answers a different "what?"| Redundant KPIs waste prime real estate                |
| Include at least one delta   | Static numbers lack context                            |
| Lead with the most important | Top-left KPI gets the most attention                   |
| Color thresholds if applicable | Green/amber/red for status-driven metrics             |

## Module 3: Filter Architecture

| Filter Type     | Placement       | Behavior                           | Example                        |
| --------------- | --------------- | ---------------------------------- | ------------------------------ |
| Global filter   | Top, below KPIs | Affects all charts and table       | Region buttons, date range     |
| Chart filter    | Inline on chart | Affects only parent chart          | Sort toggle, limit slider      |
| Cross-filter    | Click on chart  | Highlights related data elsewhere  | Click bar → table highlights   |
| Drill-through   | Click on item   | Opens detail modal or new view     | Click state → city breakdown   |
| Search          | Top controls    | Text filter across primary column  | Search box for state names     |

### Filter Design Rules

1. Global filters visible at all times (sticky if page scrolls)
2. Active filter state clearly indicated (colored buttons, badges)
3. "All" or "Reset" always available as first option
4. Filter changes animate smoothly (transition: 300ms)
5. Filter state reflected in chart titles or subtitles

## Module 4: Narrative Flow

The dashboard tells a story through panel arrangement:

| Layer | Component          | Answers              | Time to Absorb |
| ----- | ------------------ | -------------------- | -------------- |
| 1     | KPI cards          | "What's the story?"  | 2 seconds      |
| 2     | Hero chart         | "Show me the shape"  | 10 seconds     |
| 3     | Supporting charts  | "What else?"         | 15 seconds     |
| 4     | Data table         | "Give me the details"| As needed      |
| 5     | Drill-down modal   | "Tell me more about X"| On demand     |

### Progressive Disclosure

- **Above the fold**: KPIs + hero chart (must convey the main story without scrolling)
- **Below the fold**: Supporting views + table (deeper evidence)
- **On demand**: Drill-down modals, tooltips, expandable rows

## Module 5: Self-Contained HTML Pattern

Every dashboard outputs as a single HTML file:

| Requirement                | Implementation                                              |
| -------------------------- | ----------------------------------------------------------- |
| Zero build step            | Open in browser, no npm/webpack/build                       |
| Embedded data              | JavaScript arrays/objects, not external API calls           |
| Single CDN dependency      | Chart.js 4.x via jsdelivr                                  |
| Responsive                 | CSS grid with `auto-fit`, `minmax`, media queries           |
| Themeable                  | CSS custom properties for colors, spacing, fonts            |
| Accessible                 | Semantic HTML, ARIA labels, alt text on charts              |
| Print-friendly             | `@media print` styles for clean output                      |

### CSS Custom Properties Template

```css
:root {
  --bg-primary: #0f0f23;
  --bg-card: #1a1a2e;
  --text-primary: #e8e8f0;
  --text-secondary: #888;
  --accent-1: #6366f1;
  --accent-2: #3b82f6;
  --accent-3: #10b981;
  --accent-4: #f59e0b;
  --accent-5: #ec4899;
  --border-radius: 12px;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
  --transition: 0.3s ease;
}
```

## Module 6: Platform Targets

| Platform            | Output Format     | Key Differences                            |
| ------------------- | ----------------- | ------------------------------------------ |
| **HTML** (primary)  | Self-contained    | Chart.js + Canvas, embedded data           |
| **Power BI**        | Report spec       | DAX measures, M queries, visual config     |
| **Streamlit**       | Python app        | Plotly charts, st.columns, st.metric       |
| **React**           | Component tree    | Recharts/Nivo, state management, props     |

Default to HTML unless the user specifies otherwise.

## Module 7: Chart Grid Pattern (from visuals.html)

For dashboards that showcase multiple chart types or let users explore:

| Component          | Purpose                             | Implementation                    |
| ------------------ | ----------------------------------- | --------------------------------- |
| Category filter    | Show charts by category             | Button row with colored states    |
| Card grid          | Visual index of available charts    | CSS grid, auto-fit, minmax(280px) |
| Mini preview       | Quick visual (130px height canvas)  | Chart.js render at small scale    |
| Metadata badges    | "Best for", "Data type"             | Tags below chart preview          |
| Modal detail       | Full chart + metadata + examples    | Fixed overlay, arrow key nav      |

## Module 8: Interaction Patterns

| Pattern               | Trigger          | Effect                              |
| --------------------- | ---------------- | ----------------------------------- |
| Hover tooltip         | Mouse over bar   | Show exact value + label            |
| Click drill-down      | Click chart item | Open modal with detail view         |
| Filter select         | Click button     | Filter all charts to selection      |
| Sort toggle           | Click column head| Re-sort table ascending/descending  |
| Search highlight      | Type in search   | Fade non-matching, highlight match  |
| Responsive collapse   | Screen < 768px   | Stack columns, hide secondary charts|

## Module 9: 5-Visual Rule (VT BIT 5424)

Executive dashboards follow the 5-Visual Rule:

1. **1 KPI row** (3-6 metric cards)
2. **1 hero chart** (the main story)
3. **2 supporting charts** (different lenses on same data)
4. **1 data table** (detail on demand)

Maximum 5 visual elements above the fold. More than 5 creates cognitive overload for executive audiences. Analysts get more through drill-down, not more panels.

## Anti-Patterns

| Anti-Pattern           | Problem                                      | Fix                                    |
| ---------------------- | -------------------------------------------- | -------------------------------------- |
| Chart soup             | Too many charts with no narrative connection | Apply 5-Visual Rule, add story arc     |
| Dashboard as database  | Every field shown "just in case"             | Show only what answers the KPI questions|
| Inconsistent colors    | Same category = different color across charts | Use semantic color map (region → color) |
| No drill-down escape   | Modal/detail has no clear close/back          | Always show close button + ESC handler |
| Tiny charts            | Cramming 10 charts into one screen           | Fewer, larger charts with drill paths  |
| Static title           | "Revenue Dashboard"                          | "Revenue grew 34% -- but growth is slowing" |
