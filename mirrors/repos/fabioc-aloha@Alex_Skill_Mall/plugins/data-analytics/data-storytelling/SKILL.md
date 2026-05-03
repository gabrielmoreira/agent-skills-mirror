---
type: skill
lifecycle: stable
inheritance: inheritable
name: data-storytelling
description: End-to-end data narrative construction -- three-act structure, Knaflic/Duarte methodology, audience-first framing, and orchestration across analysis, visualization, and dashboard skills
tier: standard
applyTo: '**/*data*,**/*storytelling*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Data Storytelling


| Property     | Value                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| **Domain**   | Data Analytics                                                              |
| **Category** | Narrative & Orchestration                                                   |
| **Components** | SKILL.md + data-storytelling.instructions.md + datastory.prompt.md          |
| **Depends**  | data-analysis (findings), data-visualization (charts), dashboard-design (layout) |

## Overview

This is the orchestrator skill. It transforms raw data into a complete, coherent narrative by activating analysis, visualization, and dashboard skills in sequence. The output is a self-contained artifact -- typically an HTML dashboard or scrollable report -- where every chart, annotation, and KPI serves the story.

The cardinal rule: **data stories have arguments, not just observations**. A collection of charts with captions is a report. A data story says "here's what happened, here's why it matters, and here's what we should do."

## Module 1: Three-Act Data Structure

Every data story follows this arc:

| Act          | Purpose                               | Content                                          |
| ------------ | ------------------------------------- | ------------------------------------------------ |
| **Setup**    | Establish context and baseline        | Who, what, when, where + "here's how things were"|
| **Conflict** | Reveal the surprise, problem, or gap  | "But then this happened" / "X is not what we expected" |
| **Resolution**| Deliver insight and recommendation   | "This means X, and we should do Y"               |

### Act Mapping to Dashboard Components

| Act        | Dashboard Element                 |
| ---------- | --------------------------------- |
| Setup      | KPI cards showing baseline stats  |
| Conflict   | Hero chart revealing the anomaly  |
| Resolution | Supporting charts + annotated insight |

## Module 2: Audience-First Framing

Before choosing a single chart, identify who will read this and what decision it supports.

| Audience    | Time Budget | What They Need                     | Artifact Style            |
| ----------- | ----------- | ---------------------------------- | ------------------------- |
| **Executive** | 30 seconds | Headline + action recommendation  | KPI dashboard, 5-Visual   |
| **Manager**   | 2 minutes  | Context + options + trade-offs    | Dashboard with filters    |
| **Analyst**   | Unlimited  | Full data + methodology + caveats | Detailed report with drill|
| **General**   | 1 minute   | Simple story, familiar visuals    | Scroll narrative, annotated|

## Module 3: Knaflic Method ("Storytelling with Data")

The 5-step framework from Cole Nussbaumer Knaflic:

| Step                     | Action                                               |
| ------------------------ | ---------------------------------------------------- |
| 1. Understand context    | Who is the audience? What do they need to do?        |
| 2. Choose an effective visual | Story intent → chart type (SKILL cross-ref)     |
| 3. Eliminate clutter     | Remove everything that isn't data or supporting story|
| 4. Focus attention       | Use color, size, position to direct the eye          |
| 5. Tell a story          | Connect visuals with narrative text                  |

## Module 4: Duarte Contrast ("What Is" vs. "What Could Be")

Nancy Duarte's tension pattern drives engagement:

```
What Is:      "Today, we process 500 support tickets per day"
What Could Be: "With the new model, we could process 2000 with the same team"
What Is:      "Current SLA breach rate is 12%"
What Could Be: "Top performers achieve 3% -- the gap is process, not people"
```

Use this pattern when the story needs to motivate action, not just inform.

## Module 5: Big Idea Worksheet

Force the story into one sentence before building anything:

```
[Subject/audience] should [action/decision]
because [evidence from data].
```

Examples:

- "The exec team should double Q4 marketing spend because every $1 of email marketing generates $3.20 in pipeline"
- "Engineering should prioritize Region B support because resolution time is 2.5x the company average"

If you can't write the Big Idea sentence, the analysis isn't done yet.

## Module 6: Explanatory vs. Exploratory

| Mode           | You Know the Story? | Goal                          | Output                     |
| -------------- | -------------------- | ----------------------------- | -------------------------- |
| **Explanatory** | Yes                 | Guide viewer to a conclusion  | Annotated dashboard/report |
| **Exploratory** | No (yet)            | Let viewer discover patterns  | Interactive dashboard      |

Default to **explanatory** for executives and general audiences. Use **exploratory** for analysts.

## Module 7: Annotation as Narration

Annotations carry the argument. The chart is evidence; the annotation is the lawyer.

| Annotation Type | Purpose                              | Example                                    |
| --------------- | ------------------------------------ | ------------------------------------------ |
| **Title**       | State the insight (not the metric)   | "Revenue grew 34% but growth is slowing"   |
| **Subtitle**    | Provide context                      | "Quarterly actuals, FY2024-FY2025"         |
| **Callout**     | Highlight the key data point         | Arrow + "Q3 peak: $4.2M"                   |
| **Caption**     | Add nuance below the chart           | "Note: Q1 2025 includes one-time adjustment"|
| **Footnote**    | Source, methodology, caveats         | "Source: Internal CRM, excludes returns"   |

## Module 8: Orchestration Protocol

When `/datastory` is invoked, execute these phases in order:

### Phase 0: Ingest

- Activate `data-ingest.cjs` (or inline parse)
- Output: clean columnar data + metadata

### Phase 1: Discover

- Activate `data-analysis` skill
- Output: 3-5 insight statements with story intents

### Phase 2: Visualize

- Activate `data-visualization` skill for each insight
- Match story intent → chart type
- Output: chart specs with titles-as-insights

### Phase 3: Arrange

- Activate `dashboard-design` skill
- Choose layout by audience
- Place KPIs, hero, supporting, table, drill-down
- Output: dashboard scaffold

### Phase 4: Narrate

- Apply three-act structure
- Write Big Idea sentence
- Add annotations as narration
- Validate: top-to-bottom read tells the story
- Output: self-contained HTML with narrative

## Module 9: Quality Checks

Before delivering the final output:

| Check                         | Pass Criteria                                       |
| ----------------------------- | --------------------------------------------------- |
| Big Idea exists               | One sentence captures the entire story              |
| Three-act present             | Setup → Conflict → Resolution identifiable          |
| Titles are insights           | No chart titled "Revenue by Quarter" (must be a sentence) |
| Color consistency             | Same category = same color across all visuals       |
| Source attribution             | Every chart cites its data source                   |
| Audience match                | Executive gets 5 visuals, analyst gets drill-down   |
| 3-second test                 | Each chart conveys its point in 3 seconds           |
| Annotation coverage           | Hero chart has at least 1 callout annotation        |
| Data freshness                | Date range stated; "as of" timestamp included       |

## Anti-Patterns

| Anti-Pattern              | Problem                                    | Fix                                     |
| ------------------------- | ------------------------------------------ | --------------------------------------- |
| Chart collection          | Charts exist but don't connect             | Apply three-act structure               |
| Data dump                 | Every metric shown "just in case"          | Write Big Idea first, cut everything else|
| Insight-free annotations  | "This is a bar chart showing revenue"      | State what the data means, not what it is|
| Wrong audience depth      | Analyst-level detail for C-suite           | Match artifact to audience time budget  |
| No recommendation         | Story ends at "here's what happened"       | Always include "so here's what we should do" |
| Over-designed              | Fancy visuals, weak argument              | Substance over aesthetics               |
