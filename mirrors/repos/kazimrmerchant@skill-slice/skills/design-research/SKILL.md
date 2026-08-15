---
name: design-research
description: "Synthesizes JTBD jobs, App Store review patterns, interview evidence, quote-backed personas, and scored opportunities before any mockups. Trigger on product discovery, UX research, heuristic or CRO audits, or demographic-only persona decks. Not a visual-interface skill; do not use during an implementation sprint whose deliverable is pixels or code."
version: 1.0.1
---

# Design Research: Mobile UX Research and Opportunity Analysis

> Research informs design. Design informs development. Always in this order.
> This skill produces insights and product opportunities, not interfaces.

## Skill Boundary

| Question | Skill to Use |
| -------------------------------------------- | ------------------------------------------------------ |
| **Who are our users and what do they need?** | **This skill** design-research |
| **What are the highest-leverage moves?** | **This skill** opportunity analysis section |
| **How should the app look and feel?** | mobile-ui-ux |
| **How should we build this feature?** | mobile-architecture / flutter-implementation-planner |
| **How do we reach users?** | mobile-gtm-strategy |

## Core Methodology: Jobs-to-be-Done (JTBD)

Every research activity focuses on understanding what "job" users are hiring the app to do. Research uncovers:
- **Functional jobs** — the practical tasks users need to accomplish
- **Emotional jobs** — how users want to feel or avoid feeling
- **Social jobs** — how users want to be perceived by others
- **Context** — the situation that triggers each job

## When to Use

Use this skill when:
- Starting a new product or major feature before any wireframes are produced
- User research or App Store review data exists but has not been synthesised
- Existing personas feel stale or were never grounded in actual users
- Design decisions are being made from intuition
- Planning user interviews or usability studies
- Conducting UX audits, heuristic reviews, CRO, journey mapping, or product discovery
- General research tasks involving learning, investigation, synthesis, source gathering, or decision support

**Do not use this skill when:**
- Personas and design principles already exist and are recent (under 6 months)
- During an active development sprint
- The team needs visual mockups (use mobile-ui-ux for that)

## Prerequisites

Before starting, inventory available resources:
- Existing analytics (Firebase, Mixpanel, Amplitude)
- App Store reviews (AppFollow, Sensor Tower)
- Support tickets or user emails
- Previous user interviews or surveys
- Competitor apps with visible review patterns

**Reference sources to verify before relying on platform-specific guidance:**
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

**Research methodology references:**
- PRISMA 2020 statement: https://www.prisma-statement.org/prisma-2020-statement
- PRISMA 2020 checklist: https://www.prisma-statement.org/prisma-2020-checklist
- Nielsen Norman Group UX research methods: https://www.nngroup.com/articles/which-ux-research-methods/
- Pew Research Center methods: https://www.pewresearch.org/our-methods/

## Procedure

### Phase 1: Research Process

#### Step 1: Scoping and Planning

1. Inventory all available data sources (analytics, reviews, tickets, prior interviews, competitor apps).
2. Define research questions using this template:

```markdown
## Research Questions

Primary:
- What job are users hiring [app] to do?
- When and where does this job typically arise?
- What are current pain points and workarounds?

Secondary:
- Who gets the most value from the app today?
- Who uses the app but shouldn't (wrong fit)?
- What would make a user recommend this app?
```

#### Step 2: App Store Review Analysis

Mine reviews systematically before conducting any primary research. Reviews are free, abundant, and represent users who cared enough to write.

1. Collect reviews and categorize by star rating (1-star through 5-star).
2. Look for patterns in 1–3 star reviews (what is consistently broken).
3. Look for patterns in 4–5 star reviews (what is genuinely valued).
4. Identify feature requests that appear three or more times (what users are desperate for).
5. Track competitor mentions (where users are coming from and going to).

```markdown
## App Store Review Analysis [App Name]

**Reviews analysed:** X (1-star: X, 2-star: X, 3-star: X, 4-star: X, 5-star: X)
**Date range:** YYYY-MM to YYYY-MM

### Top Pain Points (1–3 star reviews)
1. [Issue] mentioned X times — Example quote: "..."
2. [Issue] mentioned X times — Example quote: "..."

### Top Delighters (4–5 star reviews)
1. [Feature/Experience] mentioned X times — Example quote: "..."
2. [Feature/Experience] mentioned X times — Example quote: "..."

### Feature Requests (any rating)
1. [Request] mentioned X times

### Competitive Mentions
- Coming from: [competitor] (X mentions)
- Switching to: [competitor] (X mentions)
```

#### Step 3: Quantitative Data Analysis

When analytics data is available, examine:
- Onboarding completion rate and which step has the largest drop-off
- Feature adoption for features with under 20% usage
- Session length and frequency distribution
- D1/D7/D30 retention broken down by cohort and acquisition channel

```markdown
## Analytics Insights

Drop-off point: [Step X] of onboarding — [Y]% complete past this point
Implication: [What this suggests about user confusion or friction]

Feature blindspot: [Feature Y] only [Z]% of users have used it once
Implication: [Discoverability issue or wrong ICP assumption]
```

#### Step 4: User Interviews

1. Recruit a minimum of 5 interviews to identify patterns; 8–12 for confidence.
2. Include active users (usability research), churned users (retention research), and target non-users (acquisition research).
3. Use the discussion guide template below.

```markdown
# User Interview Discussion Guide [Research Goal]

## Introduction (5 min)
- Thank participant
- Explain purpose: "We're trying to understand how you use [app], not to evaluate you"
- Get consent to record

## Context Questions (10 min)
Walk me through the last time you [core app action].
- What were you trying to accomplish?
- What triggered you to open the app then?
- What alternatives did you consider?

## Problem Exploration (20 min)
- What's the most frustrating part of [job-to-be-done] today?
- How did you handle this before [app] existed?
- If [app] disappeared tomorrow, what would you use instead?
- What would have to be true for you to recommend this app?

## Feature Probing (if needed) (10 min)
- [Specific hypothesis to test]
- "Have you ever tried [feature X]?" If no: why not / didn't know

## Closing (5 min)
- Is there anything important we haven't covered?
- Who else do you know who uses apps like this?
- Can we follow up with you?
```

#### Step 5: Synthesis

After data collection, identify patterns using the JTBD framework.

```markdown
## Synthesis Summary

### Core Jobs Identified
1. [Job statement: "When I [situation], I want to [motivation], so I can [outcome]"]
   Evidence: [quote + data point]

### Underserved Jobs (opportunity)
1. [Job that current solution addresses poorly]
   Evidence: [pattern from reviews or interviews]

### Overserved Jobs (simplification opportunity)
1. [Job that is more complex than it needs to be]
   Evidence: [complexity complaints in reviews]
```

### Phase 2: Opportunity Analysis

The goal is not to generate ideas — it is to identify the moves that would make this product 10× more valuable to the users the research has described. Not 10% better. The kind of feature that makes users say "how did I live without this?"

#### Step 6: Understand Current Value Before Proposing Additions

Answer these questions using research data:
- What problem does this app solve today?
- Who uses it and why, and what is the primary job-to-be-done?
- What is the core action users take every session?
- Where do users spend most time, and where do they drop off?
- What do users complain about most, and what do they request most?
- What does the current D1/D7/D30 retention signal about product-market fit?

#### Step 7: Evaluate Across Three Scales

For each finding, generate opportunities at three levels of ambition. Do not self-censor at this stage — capture the idea, evaluate it afterward.

**Massive (high effort, potentially transformative):**
Features that fundamentally expand what the product can do. New markets, new use cases, new platform capabilities.
- Ask: What adjacent problem could be solved that would make the app indispensable? What would make this a platform rather than a tool? What would make competitors nervous?
- Mobile-specific massive bets: offline-first when competitors require connectivity, Home Screen widget layer, Siri/Shortcuts integration, Watch app for a genuinely new use case, platform-native collaboration via SharePlay.

**Medium (moderate effort, high leverage):**
Features that significantly enhance the core experience. Force multipliers on what already works.
- Ask: What would make the core action 10× faster or easier? What data exists that could personalise the experience? What workflow is painful and could be automated?
- Mobile-specific medium bets: personalised push notifications that predict when a user wants to act, adaptive onboarding based on first action, Dynamic Island integration for real-time glanceable data, Spotlight Search integration.

**Small (low effort, disproportionate value):**
Changes that punch above their weight. Often overlooked because they appear too simple.
- Ask: What single button or shortcut would save users a minute every session? What information are users hunting for that could be surfaced immediately on open? What do users do manually every day that could be remembered or automated?
- Mobile-specific small bets: review prompt at the exact right moment (after a successful action, never mid-task), keyboard shortcuts for iPad/Mac Catalyst power users, drag-and-drop support for content-heavy apps, contextual empty states, smart defaults based on user history.

#### Step 8: Evaluate Each Opportunity

For every candidate opportunity, assess these dimensions:
- **Impact** — How much more valuable would this make the product for mobile users?
- **Reach** — What percentage of users would this affect, and does the iOS/Android split matter?
- **Frequency** — How often would users encounter this value per session or per week?
- **Differentiation** — Does this set the app apart from competitors, or merely match them?
- **Defensibility** — Is this easy to copy, or does it compound over time?
- **Feasibility** — Can this be built within Flutter and native interop constraints?
- **Platform fit** — Is this a natural pattern for iOS and Android users?

Score each opportunity: **must do**, **strong**, **needs more thought**, **pass**.

#### Step 9: Prioritise

Stack-rank opportunities into a recommended sequence.

```markdown
## Recommended Priority

### Do Now (quick wins — low effort, disproportionate value)
1. [Feature] Why: [reason] Impact: [what changes] Effort: [rough estimate]

### Do Next (high leverage — moderate effort, clear return)
1. [Feature] Why: [reason] Unlocks: [what becomes possible]

### Explore (strategic bets — high effort, transformative upside)
1. [Feature] Why: [reason] Risk: [what could go wrong] Upside: [what is gained]

### Backlog (good but not now)
1. [Feature] Why later: [reason]
```

#### Step 10: Force Through Opportunity Categories

When generating opportunities, explicitly consider each category to avoid blind spots:

| Category | Question |
| ------------------ | ------------------------------------------------- |
| Speed | What interaction takes too many taps or too long? |
| Automation | What do users do manually every session? |
| Native Integration | What platform capability is unused? |
| Personalisation | How does each user's usage pattern differ? |
| Offline | What breaks without internet? |
| Notifications | What push would users actually look forward to? |
| Collaboration | How do users involve others? |
| Confidence | What creates user anxiety? |
| Delight | What could spark a genuine talking point? |
| Accessibility | Who cannot use this well today? |
| App Store | What would lift rating and conversion? |
| Retention | What makes users come back tomorrow? |

### Phase 3: Produce Deliverables

#### File Organisation

```
docs/design/{feature-name}-research-{MMDDYY}/
  {feature-name}-personas.md
  {feature-name}-customer-segments.md
  {feature-name}-design-principles.md
  {feature-name}-research-discussion-guide.md
  {feature-name}-opportunities.md
```

#### Personas

A good persona includes: a fictional name and one-sentence job title, the primary JTBD, pain points with real user quotes citing source and date, success criteria in the user's own words, device and usage context, and technical comfort level.

```markdown
## [Name] — [Job Title / User Type]

> "[Direct quote from a real user that captures this persona's mindset]"

**Primary Job:** [One sentence — what they hire the app to do]
**Context:** [When and where they use the app]

**Pain Points:**
- [Pain 1] User quote: "..." (source: App Store review, MM/YYYY)
- [Pain 2] User quote: "..."

**What success looks like:**
"[Outcome in their words]"

**Tech comfort:** High / Medium / Low
**Platform:** iOS / Android
**Usage frequency:** Daily / Weekly / Event-triggered
```

Avoid generic demographics without JTBD. "Sarah, 34, lives in Seattle, likes yoga" tells designers nothing actionable.

#### Customer Segments

Group users by behaviour, not demographics.

```markdown
## Customer Segments

| Segment | Size (est.) | Primary Job | Characteristics | Design Implications |
| ------- | ------------ | ----------- | --------------- | ---------------------------- |
| [Name] | ~X% of users | [JTBD] | [Behaviours] | [What this means for the UI] |
```

#### Design Principles

Good design principles are: specific to this product (not generic "be simple"), tied to a research insight, actionable so designers can use them to resolve disagreements, and limited to 3–7. Each principle should be traceable to a specific finding.

```markdown
## Design Principles — [Feature / Product]

### 1. [Principle Title]
_[Tagline — one sentence that makes this memorable]_
**Insight:** [What research finding does this come from?]
**In practice:** [One example of this principle applied]
**Not:** [What this principle rules out]
```

#### Opportunities Document

```markdown
## Opportunity Analysis — [Feature / Product]
Date: YYYY-MM-DD | Platform: iOS / Android / Both

### Current Value
What the app does today, for whom, and what the core loop is.
Current retention: D1 X%, D7 X%, D30 X%.

### The Question
What would make this 10× more valuable to the users we researched?

### Massive Opportunities
### Medium Opportunities
### Small Gems

### Recommended Priority
#### Do Now
#### Do Next
#### Explore

### Open Questions
- [Question requiring user input or further research]
```

### Phase 4: Handoff to Design

Produce a brief handoff document connecting every finding to a design or backlog decision.

```markdown
## Research → Design Handoff

**Key finding for designers:**
[1–3 things every designer touching this feature must know]

**Primary user:** [Persona name] doing [JTBD]

**Design principles to apply:**
1. [Principle 1]
2. [Principle 2]

**Top opportunities to explore:**
1. [Opportunity 1] Score: [score]
2. [Opportunity 2] Score: [score]

**Open questions for design to answer:**
- [Question that research revealed but did not resolve]

**Next skill:** mobile-ui-ux [specific component or flow to design first]
```

### Phase 5: UX Audit and Conversion (Expert Workflow)

For wireframes, audits, heuristic reviews, CRO, journeys, and product discovery:

1. **Frame the decision:** What user behavior, product risk, or conversion problem must be understood?
2. **Gather evidence:** Analytics, recordings, support tickets, interviews, usability tests, competitor references, screenshots.
3. **Map user goal, entry point, decision points, objections, errors, and success criteria.**
4. **Recommend changes by impact, confidence, effort, and risk.**
5. **Define validation:** Usability test, A/B test, instrumentation, task success, time-on-task, conversion, retention, or qualitative confidence.

### Phase 6: General Research and Ideation (Expert Workflow)

For learning, investigation, synthesis, source gathering, insight extraction, or decision support:

1. **Clarify the research question, decision, scope, timeframe, audience, and confidence level needed.**
2. **Choose the evidence strategy:** Desk research, primary research, data analysis, expert review, competitive scan, literature review, or user research.
3. **Gather sources transparently and evaluate credibility, recency, independence, bias, and relevance.**
4. **Synthesize into findings, implications, recommendations, risks, and unanswered questions.**
5. **Provide provenance:** Source links, accessed dates, confidence notes, and verification steps.

## Pitfalls

- **Solution-first research.** Always start with "what problem?" before "what feature?". Research that begins with a predetermined answer produces confirmation, not insight.
- **Demographic-only personas.** Age, location, and occupation tell designers nothing without JTBD, context, and real quotes.
- **Only interviewing happy users.** Include churned users for retention research — they will tell you things active users won't.
- **Ignoring App Store reviews.** They are free, abundant, and represent the most motivated segment of your user base. Always start there.
- **Analysis paralysis.** Timebox research. Five interviews produce initial patterns. Validate later rather than perfecting the research before acting.
- **Generic design principles.** A principle that could apply to any app provides no decision-making value.
- **Research that never touches a decision.** Every finding must connect to a design decision, a backlog item, or an opportunity in the priority list. If it connects to nothing, either the research question was wrong or the synthesis is incomplete.
- **10× thinking without research grounding.** Generating "game-changing" ideas from intuition alone produces lists of plausible-sounding features with no evidence of user value. The opportunity analysis in Phase 2 is only valuable when it draws from the research in Phase 1.
- **Findings based on personal taste.** Recommendations must be evidence-based, not subjective preference.
- **Conversion work that degrades trust or accessibility.** Never sacrifice usability or accessibility for conversion optimization.
- **Wireframes covering only the happy path.** Always cover failure and edge states: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
- **Obscured uncertainty.** The answer must make uncertainty visible. Findings must be traceable to evidence.

## Verification

After completing research and opportunity analysis, verify the deliverables:

1. **Check persona grounding:** Every persona has at least one real user quote with source and date. No persona relies on demographics alone.
2. **Check design principle traceability:** Each principle maps to a specific research finding. No principle is generic enough to apply to any app.
3. **Check opportunity scoring:** Every opportunity has scores for all seven dimensions (Impact, Reach, Frequency, Differentiation, Defensibility, Feasibility, Platform fit).
4. **Check finding-to-decision linkage:** Every finding in the synthesis connects to at least one design decision, backlog item, or prioritized opportunity.
5. **Check deliverable file structure:**
   ```powershell
   Get-ChildItem -Path "docs/design" -Recurse -Filter "*.md" | Select-Object FullName
   ```
   Confirm all five deliverable files exist: personas, customer-segments, design-principles, research-discussion-guide, opportunities.
6. **Check handoff document completeness:** The handoff references a specific persona, lists design principles, names top opportunities with scores, and points to the next skill (mobile-ui-ux).
7. **Verify reference currency:** Before relying on any platform-specific guidance, confirm the referenced URLs are still current:
   - WCAG 2.2: https://www.w3.org/TR/WCAG22/
   - Apple HIG: https://developer.apple.com/design/human-interface-guidelines
   - Material: https://m3.material.io/
8. **Quality checklist for UX/UI deliverables:**
   - User can complete the core task quickly and repeatedly.
   - UI supports keyboard, screen readers, visible focus, and sufficient contrast.
   - Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
   - Controls use familiar affordances and expose state clearly.
   - Motion is purposeful and respects reduced-motion preferences.
   - Visual direction is intentional and consistent with the product domain.

## Related Skills

- **mobile-ui-ux** — Use after research is complete to design visual interfaces, component behavior, and interaction states.
- **mobile-architecture** — Use to determine how to build the features identified by opportunity analysis.
- **flutter-implementation-planner** — Use to plan Flutter-specific implementation of prioritized features.
- **mobile-gtm-strategy** — Use to plan go-to-market for features validated through research.
