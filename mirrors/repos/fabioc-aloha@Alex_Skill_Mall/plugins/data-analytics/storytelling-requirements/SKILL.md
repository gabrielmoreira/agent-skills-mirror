---
type: skill
lifecycle: evolving
inheritance: inheritable
name: storytelling-requirements
description: Guided requirements template for data storytelling projects -- walks users through audience, Big Idea, questions, data sources, and delivery target before any chart is created
tier: standard
applyTo: '**/*story*,**/*requirements*,**/*brief*,**/*dashboard*,**/*report*'
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Storytelling Requirements

Every data storytelling project starts with a brief. This plugin provides the template and guides the user through it. No chart should be created before this document is filled out.

The brief is the contract between the analyst and the audience. It answers: who is reading this, what decision does it support, and what does the data need to show?

## When to Use

- Starting a new dashboard, report, or data story
- A stakeholder asks "can you build me a dashboard?" (the brief prevents building the wrong one)
- Before invoking `visual-vocabulary`, `data-visualization`, or any delivery plugin
- When a project has data but no clear question

## The Requirements Template

Copy this template to your project and fill it out with the user. Each section maps to a step in the storytelling pipeline.

### Section 1: Audience and Purpose

| Field | Answer |
| --- | --- |
| **Primary audience** | (e.g., "CFO and finance leadership team") |
| **Audience expertise** | Executive / Manager / Analyst / General |
| **Time budget** | 30 seconds / 2 minutes / Unlimited |
| **Decision this supports** | (e.g., "Whether to increase Q4 marketing spend") |
| **How they will consume it** | Screen / Print / Presentation / Email / Mobile |

### Section 2: The Big Idea

Write one sentence that captures the argument:

> **[Audience] should [action/decision] because [evidence from data].**

Example: "The exec team should double Q4 email marketing spend because every $1 generates $3.20 in pipeline."

If you cannot write this sentence, the analysis is not done yet. Go back to exploration.

### Section 3: Questions the Visuals Must Answer

List 3-5 questions, ranked by priority. Each question becomes one visual.

| # | Question | Communication Goal | Priority |
| --- | --- | --- | --- |
| 1 | (e.g., "How has revenue trended quarterly?") | Change Over Time | Must-have |
| 2 | (e.g., "Which regions contribute most?") | Comparison | Must-have |
| 3 | (e.g., "What share does each product line hold?") | Proportion | Should-have |
| 4 | | | |
| 5 | | | |

Communication goals map to chart types via `visual-vocabulary` Module 1.

### Section 4: Data Sources

| Source | Format | Location | Refresh Cadence | Notes |
| --- | --- | --- | --- | --- |
| (e.g., "Sales CRM export") | CSV | SharePoint folder | Monthly | Filter: last 8 quarters |
| | | | | |

### Section 5: Data Quality Concerns

| Concern | Impact | Mitigation |
| --- | --- | --- |
| (e.g., "Missing region codes for 12% of records") | Proportions will undercount | Map nulls to "Unknown" region |
| | | |

### Section 6: Delivery Target

| Field | Answer |
| --- | --- |
| **Output format** | SVG in Markdown / HTML dashboard / Power BI report / Slides / Email |
| **Branding** | Dark slate / Light / Custom palette |
| **Interactivity** | Static / Filters / Drill-through / Cross-filter |
| **Hosting** | GitHub README / SharePoint / Power BI Service / Local file |
| **Update frequency** | One-time / Weekly refresh / Real-time |

### Section 7: Constraints

| Constraint | Detail |
| --- | --- |
| **5-visual rule** | Executive audience: max 5 visuals per page (3 KPIs + hero + supporting) |
| **Accessibility** | WCAG 2.1 AA: 4.5:1 contrast, no color-only encoding |
| **Token budget** | (if rendering in AI context: max tokens for the output artifact) |
| **Deadline** | (when is this needed?) |

## How to Use This Template

### Guided Interview Mode

When a user says "build me a dashboard" or "make a report from this data", walk them through the template:

1. **Start with Section 2 (Big Idea).** If they can write the sentence, the rest flows. If they cannot, they need exploration first -- invoke `data-analysis` or `data-storytelling` Module 1 (Discover).

2. **Fill Section 1 (Audience).** This determines the 5-visual rule budget, chart complexity, and delivery format.

3. **Fill Section 3 (Questions).** Map each question to a communication goal using the heuristic table below. This is where `visual-vocabulary` fires.

4. **Fill Sections 4-5 (Data).** This determines which `datasource-connectors` and `data-preparation` steps are needed.

5. **Fill Sections 6-7 (Delivery).** This determines which `delivery-*` plugin to invoke.

### Communication Goal Heuristic

When users struggle to name the communication goal for a question, use these trigger words:

| Trigger Words in the Question | Communication Goal |
| --- | --- |
| "rank", "compare", "versus", "top", "best/worst" | Comparison |
| "over time", "trend", "growth", "decline", "monthly" | Change Over Time |
| "share", "proportion", "breakdown", "percent of" | Proportion |
| "spread", "range", "outlier", "distribution" | Distribution |
| "correlation", "relationship", "predict", "affects" | Relationship |
| "flow", "path", "conversion", "funnel", "from X to Y" | Flow |
| "deviation", "variance", "above/below target" | Deviation |

### The CSAR Check

After filling the brief and before building, run one CSAR pass:

- **Clarify**: Does the Big Idea sentence actually match the questions listed?
- **Summarize**: Do the communication goals match what the audience needs?
- **Act**: Remove any question that does not support the Big Idea. Add any missing angle.
- **Reflect**: Is this the right story to tell, or is the user anchored on their first framing?

## Pipeline Integration

```text
storytelling-requirements  (this plugin -- the brief)
         |
         v
datasource-connectors      (ingest data per Section 4)
         |
         v
data-preparation           (clean per Section 5 concerns)
         |
         v
visual-vocabulary          (select charts per Section 3 goals)
         |
         v
delivery-*                 (render per Section 6 target)
```

## Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Building charts before writing the Big Idea | The Big Idea is the filter. Without it, you build 20 charts and keep 5. |
| Skipping the audience section | Executive dashboards and analyst reports are different artifacts. The audience determines everything. |
| Listing 10+ questions for an executive dashboard | 5-visual rule. Cut to 3-5 questions or split into multiple pages. |
| No data quality section | Surprises in the data surface during the demo, not the build. Document concerns early. |
| Filling the template alone (without the stakeholder) | The brief is a conversation tool. Fill it together. |

## Cross-References

- `visual-vocabulary` -- chart selection by communication goal (fires after Section 3)
- `data-storytelling` -- narrative arc and orchestration (fires after the brief is complete)
- `data-visualization` -- chart design: color, annotation, decluttering (fires after chart selection)
- `data-preparation` -- cleaning and profiling (fires after Section 4-5)
- `datasource-connectors` -- data ingestion (fires after Section 4)
- `delivery-*` -- rendering to target format (fires after Section 6)
