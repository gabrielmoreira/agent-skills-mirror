---
type: skill
lifecycle: stable
inheritance: inheritable
name: competitive-teardown
description: Analyzes competitor products and companies by synthesizing data from pricing pages, app store reviews, job postings, SEO signals, and social media into structured competitive intelligence. Produces...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Competitive Teardown

**Tier:** POWERFUL  
**Category:** Product Team  
**Domain:** Competitive Intelligence, Product Strategy, Market Analysis

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-1
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Teardown Workflow

Follow these steps in sequence to produce a complete teardown:

1. **Define competitors** — List 2–4 competitors to analyze. Confirm which is the primary focus.
2. **Collect data** — Use `references/data-collection-guide.md` to gather raw signals from at least 3 sources per competitor (website, reviews, job postings, SEO, social).  
   _Validation checkpoint: Before proceeding, confirm you have pricing data, at least 20 reviews, and job posting counts for each competitor._
3. **Score using rubric** — Apply the 12-dimension rubric below to produce a numeric scorecard for each competitor and your own product.  
   _Validation checkpoint: Every dimension should have a score and at least one supporting evidence note._
4. **Generate outputs** — Populate the templates in `references/analysis-templates.md` (Feature Matrix, Pricing Analysis, SWOT, Positioning Map, UX Audit).
5. **Build action plan** — Translate findings into the Action Items template (quick wins / medium-term / strategic).
6. **Package for stakeholders** — Assemble the Stakeholder Presentation using outputs from steps 3–5.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-2
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Scoring Rubric (12 Dimensions, 1-5)

| # | Dimension | 1 (Weak) | 3 (Average) | 5 (Best-in-class) |
|---|-----------|----------|-------------|-------------------|
| 1 | **Features** | Core only, many gaps | Solid coverage | Comprehensive + unique |
| 2 | **Pricing** | Confusing / overpriced | Market-rate, clear | Transparent, flexible, fair |
| 3 | **UX** | Confusing, high friction | Functional | Delightful, minimal friction |
| 4 | **Performance** | Slow, unreliable | Acceptable | Fast, high uptime |
| 5 | **Docs** | Sparse, outdated | Decent coverage | Comprehensive, searchable |
| 6 | **Support** | Email only, slow | Chat + email | 24/7, great response |
| 7 | **Integrations** | 0-5 integrations | 6-25 | 26+ or deep ecosystem |
| 8 | **Security** | No mentions | SOC2 claimed | SOC2 Type II, ISO 27001 |
| 9 | **Scalability** | No enterprise tier | Mid-market ready | Enterprise-grade |
| 10 | **Brand** | Generic, unmemorable | Decent positioning | Strong, differentiated |
| 11 | **Community** | None | Forum / Slack | Active, vibrant community |
| 12 | **Innovation** | No recent releases | Quarterly | Frequent, meaningful |

**Example completed row** (Competitor: Acme Corp, Dimension 3 – UX):

| Dimension | Acme Corp Score | Evidence |
|-----------|----------------|---------|
| UX | 2 | App Store reviews cite "confusing navigation" (38 mentions); onboarding requires 7 steps before TTFV; no onboarding wizard; CC required at signup. |

Apply this pattern to all 12 dimensions for each competitor.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-3
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: experiment-designer
description: Use when planning product experiments, writing testable hypotheses, estimating sample size, prioritizing tests, or interpreting A/B outcomes with practical statistical rigor.
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Experiment Designer

Design, prioritize, and evaluate product experiments with clear hypotheses and defensible decisions.

## When To Use

Use this skill for:
- A/B and multivariate experiment planning
- Hypothesis writing and success criteria definition
- Sample size and minimum detectable effect planning
- Experiment prioritization with ICE scoring
- Reading statistical output for product decisions

## Core Workflow

1. Write hypothesis in If/Then/Because format
- If we change `[intervention]`
- Then `[metric]` will change by `[expected direction/magnitude]`
- Because `[behavioral mechanism]`

2. Define metrics before running test
- Primary metric: single decision metric
- Guardrail metrics: quality/risk protection
- Secondary metrics: diagnostics only

3. Estimate sample size
- Baseline conversion or baseline mean
- Minimum detectable effect (MDE)
- Significance level (alpha) and power

Use:
```bash
python3 scripts/sample_size_calculator.py --baseline-rate 0.12 --mde 0.02 --mde-type absolute
```

4. Prioritize experiments with ICE
- Impact: potential upside
- Confidence: evidence quality
- Ease: cost/speed/complexity

ICE Score = (Impact * Confidence * Ease) / 10

5. Launch with stopping rules
- Decide fixed sample size or fixed duration in advance
- Avoid repeated peeking without proper method
- Monitor guardrails continuously

6. Interpret results
- Statistical significance is not business significance
- Compare point estimate + confidence interval to decision threshold
- Investigate novelty effects and segment heterogeneity

## Hypothesis Quality Checklist

- [ ] Contains explicit intervention and audience
- [ ] Specifies measurable metric change
- [ ] States plausible causal reason
- [ ] Includes expected minimum effect
- [ ] Defines failure condition

## Common Experiment Pitfalls

- Underpowered tests leading to false negatives
- Running too many simultaneous changes without isolation
- Changing targeting or implementation mid-test
- Stopping early on random spikes
- Ignoring sample ratio mismatch and instrumentation drift
- Declaring success from p-value without effect-size context

## Statistical Interpretation Guardrails

- p-value < alpha indicates evidence against null, not guaranteed truth.
- Confidence interval crossing zero/no-effect means uncertain directional claim.
- Wide intervals imply low precision even when significant.
- Use practical significance thresholds tied to business impact.

See:
- `references/experiment-playbook.md`
- `references/statistics-reference.md`

## Tooling

### `scripts/sample_size_calculator.py`

Computes required sample size (per variant and total) from:
- baseline rate
- MDE (absolute or relative)
- significance level (alpha)
- statistical power

Example:
```bash
python3 scripts/sample_size_calculator.py \
  --baseline-rate 0.10 \
  --mde 0.015 \
  --mde-type absolute \
  --alpha 0.05 \
  --power 0.8
```


---
type: skill
lifecycle: stable
inheritance: inheritable
name: landing-page-generator
description: Generates high-converting landing pages as complete Next.js/React (TSX) components with Tailwind CSS. Creates hero sections, feature grids, pricing tables, FAQ accordions, testimonial blocks, and C...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Landing Page Generator

Generate high-converting landing pages from a product description. Output complete Next.js/React components with multiple section variants, proven copy frameworks, SEO optimization, and performance-first patterns. Not lorem ipsum — actual copy that converts.

**Target:** LCP < 1s · CLS < 0.1 · FID < 100ms  
**Output:** TSX components + Tailwind styles + SEO meta + copy variants

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-6
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Generation Workflow

Follow these steps in order for every landing page request:

1. **Gather inputs** — collect product name, tagline, audience, pain point, key benefit, pricing tiers, design style, and copy framework using the trigger format below. Ask only for missing fields.
2. **Analyze brand voice** (recommended) — if the user has existing brand content (website copy, blog posts, marketing materials), run it through `marketing-skill/content-production/scripts/brand_voice_analyzer.py` to get a voice profile (formality, tone, perspective). Use the profile to inform design style and copy framework selection:
   - formal + professional → **enterprise** style, **AIDA** framework
   - casual + friendly → **bold-startup** style, **BAB** framework
   - professional + authoritative → **dark-saas** style, **PAS** framework
   - casual + conversational → **clean-minimal** style, **BAB** framework
3. **Select design style** — map the user's choice (or infer from brand voice analysis) to one of the four Tailwind class sets in the Design Style Reference.
4. **Apply copy framework** — write all headline and body copy using the chosen framework (PAS / AIDA / BAB) before generating components. Match the voice profile's formality and tone throughout.
5. **Generate sections in order** — Hero → Features → Pricing → FAQ → Testimonials → CTA → Footer. Skip sections not relevant to the product.
6. **Validate against SEO checklist** — run through every item in the SEO Checklist before outputting final code. Fix any gaps inline.
7. **Output final components** — deliver complete, copy-paste-ready TSX files with all Tailwind classes, SEO meta, and structured data included.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-7
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Design Style Reference

| Style | Background | Accent | Cards | CTA Button |
|---|---|---|---|---|
| **Dark SaaS** | `bg-gray-950 text-white` | `violet-500/400` | `bg-gray-900 border border-gray-800` | `bg-violet-600 hover:bg-violet-500` |
| **Clean Minimal** | `bg-white text-gray-900` | `blue-600` | `bg-gray-50 border border-gray-200 rounded-2xl` | `bg-blue-600 hover:bg-blue-700` |
| **Bold Startup** | `bg-white text-gray-900` | `orange-500` | `shadow-xl rounded-3xl` | `bg-orange-500 hover:bg-orange-600 text-white` |
| **Enterprise** | `bg-slate-50 text-slate-900` | `slate-700` | `bg-white border border-slate-200 shadow-sm` | `bg-slate-900 hover:bg-slate-800 text-white` |

> **Bold Startup** headings: add `font-black tracking-tight` to all `<h1>`/`<h2>` elements.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-8
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Representative Component: Hero (Centered Gradient — Dark SaaS)

Use this as the structural template for all hero variants. Swap layout classes, gradient direction, and image placement for split, video-bg, and minimal variants.

```tsx
export function HeroCentered() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gray-950 px-4 text-center">
      <div className="absolute inset-0 bg-gradient-to-b from-violet-900/20 to-transparent" />
      <div className="pointer-events-none absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-violet-600/20 blur-3xl" />
      <div className="relative z-10 max-w-4xl">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm text-violet-300">
          <span className="h-1.5 w-1.5 rounded-full bg-violet-400" />
          Now in public beta
        </div>
        <h1 className="mb-6 text-5xl font-bold tracking-tight text-white md:text-7xl">
          Ship faster.<br />
          <span className="bg-gradient-to-r from-violet-400 to-pink-400 bg-clip-text text-transparent">
            Break less.
          </span>
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-xl text-gray-400">
          The deployment platform that catches errors before your users do.
          Zero config. Instant rollbacks. Real-time monitoring.
        </p>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button size="lg" className="bg-violet-600 text-white hover:bg-violet-500 px-8">
            Start free trial
          </Button>
          <Button size="lg" variant="outline" className="border-gray-700 text-gray-300">
            See how it works →
          </Button>
        </div>
        <p className="mt-4 text-sm text-gray-500">No credit card required · 14-day free trial</p>
      </div>
    </section>
  )
}
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-9
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## SEO Checklist

- [ ] `<title>` tag: primary keyword + brand (50–60 chars)
- [ ] Meta description: benefit + CTA (150–160 chars)
- [ ] OG image: 1200×630px with product name and tagline
- [ ] H1: one per page, includes primary keyword
- [ ] Structured data: FAQPage, Product, or Organization schema
- [ ] Canonical URL set
- [ ] Image alt text on all `<Image>` components
- [ ] robots.txt and sitemap.xml configured
- [ ] Core Web Vitals: LCP < 1s, CLS < 0.1
- [ ] Mobile viewport meta tag present
- [ ] Internal linking to pricing and docs

> **Validation step:** Before outputting final code, verify every checklist item above is satisfied. Fix any gaps inline — do not skip items.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-10
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Common Pitfalls

- Hero image not preloaded — add `priority` prop to first `<Image>`
- Missing mobile breakpoints — always design mobile-first with `sm:` prefixes
- CTA copy too vague — "Get started" beats "Learn more"; "Start free trial" beats "Sign up"
- Pricing page missing trust signals — add money-back guarantee and testimonials near CTA
- No above-the-fold CTA on mobile — ensure button is visible without scrolling on 375px viewport

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-11
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-analytics
description: Use when defining product KPIs, building metric dashboards, running cohort or retention analysis, or interpreting feature adoption trends across product stages.
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Product Analytics

Define, track, and interpret product metrics across discovery, growth, and mature product stages.

## When To Use

Use this skill for:
- Metric framework selection (AARRR, North Star, HEART)
- KPI definition by product stage (pre-PMF, growth, mature)
- Dashboard design and metric hierarchy
- Cohort and retention analysis
- Feature adoption and funnel interpretation

## Workflow

1. Select metric framework
- AARRR for growth loops and funnel visibility
- North Star for cross-functional strategic alignment
- HEART for UX quality and user experience measurement

2. Define stage-appropriate KPIs
- Pre-PMF: activation, early retention, qualitative success
- Growth: acquisition efficiency, expansion, conversion velocity
- Mature: retention depth, revenue quality, operational efficiency

3. Design dashboard layers
- Executive layer: 5-7 directional metrics
- Product health layer: acquisition, activation, retention, engagement
- Feature layer: adoption, depth, repeat usage, outcome correlation

4. Run cohort + retention analysis
- Segment by signup cohort or feature exposure cohort
- Compare retention curves, not single-point snapshots
- Identify inflection points around onboarding and first value moment

5. Interpret and act
- Connect metric movement to product changes and release timeline
- Distinguish signal from noise using period-over-period context
- Propose one clear product action per major metric risk/opportunity

## KPI Guidance By Stage

### Pre-PMF
- Activation rate
- Week-1 retention
- Time-to-first-value
- Problem-solution fit interview score

### Growth
- Funnel conversion by stage
- Monthly retained users
- Feature adoption among new cohorts
- Expansion / upsell proxy metrics

### Mature
- Net revenue retention aligned product metrics
- Power-user share and depth of use
- Churn risk indicators by segment
- Reliability and support-deflection product metrics

## Dashboard Design Principles

- Show trends, not isolated point estimates.
- Keep one owner per KPI.
- Pair each KPI with target, threshold, and decision rule.
- Use cohort and segment filters by default.
- Prefer comparable time windows (weekly vs weekly, monthly vs monthly).

See:
- `references/metrics-frameworks.md`
- `references/dashboard-templates.md`

## Cohort Analysis Method

1. Define cohort anchor event (signup, activation, first purchase).
2. Define retained behavior (active day, key action, repeat session).
3. Build retention matrix by cohort week/month and age period.
4. Compare curve shape across cohorts.
5. Flag early drop points and investigate journey friction.

## Retention Curve Interpretation

- Sharp early drop, low plateau: onboarding mismatch or weak initial value.
- Moderate drop, stable plateau: healthy core audience with predictable churn.
- Flattening at low level: product used occasionally, revisit value metric.
- Improving newer cohorts: onboarding or positioning improvements are working.

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| **Vanity metrics** — tracking pageviews or total signups without activation context | Always pair acquisition metrics with activation rate and retention |
| **Single-point retention** — reporting "30-day retention is 20%" | Compare retention curves across cohorts, not isolated snapshots |
| **Dashboard overload** — 30+ metrics on one screen | Executive layer: 5-7 metrics. Feature layer: per-feature only |
| **No decision rule** — tracking a KPI with no threshold or action plan | Every KPI needs: target, threshold, owner, and "if below X, then Y" |
| **Averaging across segments** — reporting blended metrics that hide segment differences | Always segment by cohort, plan tier, channel, or geography |
| **Ignoring seasonality** — comparing this week to last week without adjusting | Use period-over-period with same-period-last-year context |

## Tooling

### `scripts/metrics_calculator.py`

CLI utility for retention, cohort, and funnel analysis from CSV data. Supports text and JSON output.

```bash
# Retention analysis
python3 scripts/metrics_calculator.py retention events.csv
python3 scripts/metrics_calculator.py retention events.csv --format json

# Cohort matrix
python3 scripts/metrics_calculator.py cohort events.csv --cohort-grain month
python3 scripts/metrics_calculator.py cohort events.csv --cohort-grain week --format json

# Funnel conversion
python3 scripts/metrics_calculator.py funnel funnel.csv --stages visit,signup,activate,pay
python3 scripts/metrics_calculator.py funnel funnel.csv --stages visit,signup,activate,pay --format json
```

**CSV format for retention/cohort:**
```csv
user_id,cohort_date,activity_date
u001,2026-01-01,2026-01-01
u001,2026-01-01,2026-01-03
u002,2026-01-02,2026-01-02
```

**CSV format for funnel:**
```csv
user_id,stage
u001,visit
u001,signup
u001,activate
u002,visit
u002,signup
```

## Cross-References

- Related: `product-team/experiment-designer` — for A/B test planning after identifying metric opportunities
- Related: `product-team/product-manager-toolkit` — for RICE prioritization of metric-driven features
- Related: `product-team/product-discovery` — for assumption mapping when metrics reveal unknowns
- Related: `finance/saas-metrics-coach` — for SaaS-specific metrics (ARR, MRR, churn, LTV)


---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-discovery
description: Use when validating product opportunities, mapping assumptions, planning discovery sprints, or testing problem-solution fit before committing delivery resources.
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Product Discovery

Run structured discovery to identify high-value opportunities and de-risk product bets.

## When To Use

Use this skill for:
- Opportunity Solution Tree facilitation
- Assumption mapping and test planning
- Problem validation interviews and evidence synthesis
- Solution validation with prototypes/experiments
- Discovery sprint planning and outputs

## Core Discovery Workflow

1. Define desired outcome
- Set one measurable outcome to improve.
- Establish baseline and target horizon.

2. Build Opportunity Solution Tree (OST)
- Outcome -> opportunities -> solution ideas -> experiments
- Keep opportunities grounded in user evidence, not internal opinions.

3. Map assumptions
- Identify desirability, viability, feasibility, and usability assumptions.
- Score assumptions by risk and certainty.

Use:
```bash
python3 scripts/assumption_mapper.py assumptions.csv
```

4. Validate the problem
- Conduct interviews and behavior analysis.
- Confirm frequency, severity, and willingness to solve.
- Reject weak opportunities early.

5. Validate the solution
- Prototype before building.
- Run concept, usability, and value tests.
- Measure behavior, not only stated preference.

6. Plan discovery sprint
- 1-2 week cycle with explicit hypotheses
- Daily evidence reviews
- End with decision: proceed, pivot, or stop

## Opportunity Solution Tree (Teresa Torres)

Structure:
- Outcome: metric you want to move
- Opportunities: unmet customer needs/pains
- Solutions: candidate interventions
- Experiments: fastest learning actions

Quality checks:
- At least 3 distinct opportunities before converging.
- At least 2 experiments per top opportunity.
- Tie every branch to evidence source.

## Assumption Mapping

Assumption categories:
- Desirability: users want this
- Viability: business value exists
- Feasibility: team can build/operate it
- Usability: users can successfully use it

Prioritization rule:
- High risk + low certainty assumptions are tested first.

## Problem Validation Techniques

- Problem interviews focused on current behavior
- Journey friction mapping
- Support ticket and sales-call synthesis
- Behavioral analytics triangulation

Evidence threshold examples:
- Same pain repeated across multiple target users
- Observable workaround behavior
- Measurable cost of current pain

## Solution Validation Techniques

- Concept tests (value proposition comprehension)
- Prototype usability tests (task success/time-to-complete)
- Fake door or concierge tests (demand signal)
- Limited beta cohorts (retention/activation signals)

## Discovery Sprint Planning

Suggested 10-day structure:
- Day 1-2: Outcome + opportunity framing
- Day 3-4: Assumption mapping + test design
- Day 5-7: Problem and solution tests
- Day 8-9: Evidence synthesis + decision options
- Day 10: Stakeholder decision review

## Tooling

### `scripts/assumption_mapper.py`

CLI utility that:
- reads assumptions from CSV or inline input
- scores risk/certainty priority
- emits prioritized test plan with suggested test types

See `references/discovery-frameworks.md` for framework details.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-manager-toolkit
description: Comprehensive toolkit for product managers including RICE prioritization, customer interview analysis, PRD templates, discovery frameworks, and go-to-market strategies. Use for feature prioritizati...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Product Manager Toolkit

Essential tools and frameworks for modern product management, from discovery to delivery.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-15
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quick Start

### For Feature Prioritization
```bash
# Create sample data file
python scripts/rice_prioritizer.py sample

# Run prioritization with team capacity
python scripts/rice_prioritizer.py sample_features.csv --capacity 15
```

### For Interview Analysis
```bash
python scripts/customer_interview_analyzer.py interview_transcript.txt
```

### For PRD Creation
1. Choose template from `references/prd_templates.md`
2. Fill sections based on discovery work
3. Review with engineering for feasibility
4. Version control in project management tool

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-16
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Customer Discovery Process

```
Plan → Recruit → Interview → Analyze → Synthesize → Validate
```

#### Step 1: Plan Research
- Define research questions
- Identify target segments
- Create interview script (see `references/frameworks.md`)

#### Step 2: Recruit Participants
- 5-8 interviews per segment
- Mix of power users and churned users
- Incentivize appropriately

#### Step 3: Conduct Interviews
- Use semi-structured format
- Focus on problems, not solutions
- Record with permission
- Take minimal notes during interview

#### Step 4: Analyze Insights
```bash
python scripts/customer_interview_analyzer.py transcript.txt
```

Extracts:
- Pain points with severity
- Feature requests with priority
- Jobs to be done patterns
- Sentiment and key themes
- Notable quotes

#### Step 5: Synthesize Findings
- Group similar pain points across interviews
- Identify patterns (3+ mentions = pattern)
- Map to opportunity areas using Opportunity Solution Tree
- Prioritize opportunities by frequency and severity

#### Step 6: Validate Solutions
**Before building:**
- [ ] Create solution hypotheses (see `references/frameworks.md`)
- [ ] Test with low-fidelity prototypes
- [ ] Measure actual behavior vs stated preference
- [ ] Iterate based on feedback
- [ ] Document learnings for future research

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-17
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools Reference

### RICE Prioritizer

Advanced RICE framework implementation with portfolio analysis.

**Features:**
- RICE score calculation with configurable weights
- Portfolio balance analysis (quick wins vs big bets)
- Quarterly roadmap generation based on capacity
- Multiple output formats (text, JSON, CSV)

**CSV Input Format:**
```csv
name,reach,impact,confidence,effort,description
User Dashboard Redesign,5000,high,high,l,Complete redesign
Mobile Push Notifications,10000,massive,medium,m,Add push support
Dark Mode,8000,medium,high,s,Dark theme option
```

**Commands:**
```bash
# Create sample data
python scripts/rice_prioritizer.py sample

# Run with default capacity (10 person-months)
python scripts/rice_prioritizer.py features.csv

# Custom capacity
python scripts/rice_prioritizer.py features.csv --capacity 20

# JSON output for integration
python scripts/rice_prioritizer.py features.csv --output json

# CSV output for spreadsheets
python scripts/rice_prioritizer.py features.csv --output csv
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-18
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Input/Output Examples
→ See references/input-output-examples.md for details

## Integration Points

Compatible tools and platforms:

| Category | Platforms |
|----------|-----------|
| **Analytics** | Amplitude, Mixpanel, Google Analytics |
| **Roadmapping** | ProductBoard, Aha!, Roadmunk, Productplan |
| **Design** | Figma, Sketch, Miro |
| **Development** | Jira, Linear, GitHub, Asana |
| **Research** | Dovetail, UserVoice, Pendo, Maze |
| **Communication** | Slack, Notion, Confluence |

**JSON export enables integration with most tools:**
```bash
# Export for Jira import
python scripts/rice_prioritizer.py features.csv --output json > priorities.json

# Export for dashboard
python scripts/customer_interview_analyzer.py interview.txt json > insights.json
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-19
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Best Practices

**Writing Great PRDs:**
- Start with the problem, not the solution
- Include clear success metrics upfront
- Explicitly state what's out of scope
- Use visuals (wireframes, flows, diagrams)
- Keep technical details in appendix
- Version control all changes

**Effective Prioritization:**
- Mix quick wins with strategic bets
- Consider opportunity cost of delays
- Account for dependencies between features
- Buffer 20% for unexpected work
- Revisit priorities quarterly
- Communicate decisions with context

**Customer Discovery:**
- Ask "why" five times to find root cause
- Focus on past behavior, not future intentions
- Avoid leading questions ("Wouldn't you love...")
- Interview in the user's natural environment
- Watch for emotional reactions (pain = opportunity)
- Validate qualitative with quantitative data

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-20
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference Documents

- `references/prd_templates.md` - PRD templates for different contexts
- `references/frameworks.md` - Detailed framework documentation (RICE, MoSCoW, Kano, JTBD, etc.)


---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-skills
description: 10 product agent skills and plugins for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. PM toolkit (RICE), agile PO, product strategist (OKR), UX researcher, UI design system, competitive teardow...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Product Team Skills

8 production-ready product skills covering product management, UX/UI design, and SaaS development.

## Quick Start

### Claude Code
```
/read product-team/product-manager-toolkit/SKILL.md
```

### Codex CLI
```bash
npx agent-skills-cli add alirezarezvani/claude-skills/product-team
```

## Skills Overview

| Skill | Folder | Focus |
|-------|--------|-------|
| Product Manager Toolkit | `product-manager-toolkit/` | RICE prioritization, customer discovery, PRDs |
| Agile Product Owner | `agile-product-owner/` | User stories, sprint planning, backlog |
| Product Strategist | `product-strategist/` | OKR cascades, market analysis, vision |
| UX Researcher Designer | `ux-researcher-designer/` | Personas, journey maps, usability testing |
| UI Design System | `ui-design-system/` | Design tokens, component docs, responsive |
| Competitive Teardown | `competitive-teardown/` | Systematic competitor analysis |
| Landing Page Generator | `landing-page-generator/` | Conversion-optimized pages |
| SaaS Scaffolder | `saas-scaffolder/` | Production SaaS boilerplate |

## Python Tools

9 scripts, all stdlib-only:

```bash
python3 product-manager-toolkit/scripts/rice_prioritizer.py --help
python3 product-strategist/scripts/okr_cascade_generator.py --help
```

## Rules

- Load only the specific skill SKILL.md you need
- Use Python tools for scoring and analysis, not manual judgment


---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-strategist
description: Strategic product leadership toolkit for Head of Product covering OKR cascade generation, quarterly planning, competitive landscape analysis, product vision documents, and team scaling proposals. U...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Product Strategist

Strategic toolkit for Head of Product to drive vision, alignment, and organizational excellence.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-23
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quick Start

```bash
# Growth strategy with default teams
python scripts/okr_cascade_generator.py growth

# Retention strategy with custom teams
python scripts/okr_cascade_generator.py retention --teams "Engineering,Design,Data"

# Revenue strategy with 40% product contribution
python scripts/okr_cascade_generator.py revenue --contribution 0.4

# Export as JSON for integration
python scripts/okr_cascade_generator.py growth --json > okrs.json
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-24
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## OKR Cascade Generator

### Usage

```bash
python scripts/okr_cascade_generator.py [strategy] [options]
```

**Strategies:** `growth` | `retention` | `revenue` | `innovation` | `operational`

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--teams`, `-t` | Comma-separated team names | Growth,Platform,Mobile,Data |
| `--contribution`, `-c` | Product contribution to company OKRs (0-1) | 0.3 (30%) |
| `--json`, `-j` | Output as JSON instead of dashboard | False |
| `--metrics`, `-m` | Metrics as JSON string | Sample metrics |

### Output Examples

#### Dashboard Output (`growth` strategy)

```
============================================================
OKR CASCADE DASHBOARD
Quarter: Q1 2025  |  Strategy: GROWTH
Teams: Growth, Platform, Mobile, Data  |  Product Contribution: 30%
============================================================

🏢 COMPANY OKRS
📌 CO-1: Accelerate user acquisition and market expansion
   └─ CO-1-KR1: Increase MAU from 100,000 to 150,000
   └─ CO-1-KR2: Achieve 50% MoM growth rate
   └─ CO-1-KR3: Expand to 3 new markets

📌 CO-2: Achieve product-market fit in new segments
📌 CO-3: Build sustainable growth engine

🚀 PRODUCT OKRS
📌 PO-1: Build viral product features and market expansion
   ↳ Supports: CO-1
   └─ PO-1-KR1: Increase product MAU to 45,000
   └─ PO-1-KR2: Achieve 45% feature adoption rate

👥 TEAM OKRS
Growth Team:
  📌 GRO-1: Build viral product features through acquisition and activation
     └─ GRO-1-KR1: Increase product MAU to 11,250
     └─ GRO-1-KR2: Achieve 11.25% feature adoption rate

🎯 ALIGNMENT SCORES
✓ Vertical Alignment: 100.0%
! Horizontal Alignment: 75.0%
✓ Coverage: 100.0%  |  ✓ Balance: 97.5%  |  ✓ Overall: 94.0%
✅ Overall alignment is GOOD (≥80%)
```

#### JSON Output (`retention --json`, truncated)

```json
{
  "quarter": "Q1 2025",
  "strategy": "retention",
  "company": {
    "objectives": [
      {
        "id": "CO-1",
        "title": "Create lasting customer value and loyalty",
        "key_results": [
          { "id": "CO-1-KR1", "title": "Improve retention from 70% to 85%", "current": 70, "target": 85 }
        ]
      }
    ]
  },
  "product": { "contribution": 0.3, "objectives": ["..."] },
  "teams": ["..."],
  "alignment_scores": {
    "vertical_alignment": 100.0, "horizontal_alignment": 75.0,
    "coverage": 100.0, "balance": 97.5, "overall": 94.0
  }
}
```

See `references/examples/sample_growth_okrs.json` for a complete example.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-25
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Best Practices

### OKR Cascade

- Limit to 3-5 objectives per level, each with 3-5 key results
- Key results must be measurable with current and target values
- Validate parent-child relationships before finalizing

### Alignment Scoring

- Target >80% overall alignment; investigate any score below 60%
- Balance scores ensure no team is overloaded
- Horizontal alignment prevents conflicting goals across teams

### Team Configuration

- Configure teams to match your actual org structure
- Adjust contribution percentages based on team size
- Platform/Infrastructure teams often support all objectives
- Specialized teams (ML, Data) may only support relevant objectives

## Related Skills

- **Senior PM** (`project-management/senior-pm/`) — Portfolio management and risk analysis inform strategic planning
- **Competitive Teardown** (`product-team/competitive-teardown/`) — Competitive intelligence feeds product strategy


---
type: skill
lifecycle: stable
inheritance: inheritable
name: roadmap-communicator
description: Use when preparing roadmap narratives, release notes, changelogs, or stakeholder updates tailored for executives, engineering teams, and customers.
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Roadmap Communicator

Create clear roadmap communication artifacts for internal and external stakeholders.

## When To Use

Use this skill for:
- Building roadmap presentations in different formats
- Writing stakeholder updates (board, engineering, customers)
- Producing release notes (user-facing and internal)
- Generating changelogs from git history
- Structuring feature announcements

## Roadmap Formats

1. Now / Next / Later
- Best for uncertainty and strategic flexibility.
- Communicate direction without false precision.

2. Timeline roadmap
- Best for fixed-date commitments and launch coordination.
- Requires active risk and dependency management.

3. Theme-based roadmap
- Best for outcome-led planning and cross-team alignment.
- Groups initiatives by problem space or strategic objective.

See `references/roadmap-templates.md` for templates.

## Stakeholder Update Patterns

### Board / Executive
- Outcome and risk oriented
- Focus on progress against strategic goals
- Highlight trade-offs and required decisions

### Engineering
- Scope, dependencies, and sequencing clarity
- Status, blockers, and resourcing implications

### Customers
- Value narrative and timing window
- What is available now vs upcoming
- Clear expectation setting

See `references/communication-templates.md` for reusable templates.

## Release Notes Guidance

### User-Facing Release Notes
- Lead with user value, not internal implementation details.
- Group by workflows or user jobs.
- Include migration/behavior changes explicitly.

### Internal Release Notes
- Include technical details, operational impact, and known issues.
- Capture rollout plan, rollback criteria, and monitoring notes.

## Changelog Generation

Use:
```bash
python3 scripts/changelog_generator.py --from v1.0.0 --to HEAD
```

Features:
- Reads git log range
- Parses conventional commit prefixes
- Groups entries by type (`feat`, `fix`, `chore`, etc.)
- Outputs markdown or plain text

## Feature Announcement Framework

1. Problem context
2. What changed
3. Why it matters
4. Who benefits most
5. How to get started
6. Call to action and feedback channel

## Communication Quality Checklist

- [ ] Audience-specific framing is explicit.
- [ ] Outcomes and trade-offs are clear.
- [ ] Terminology is consistent across artifacts.
- [ ] Risks and dependencies are not hidden.
- [ ] Next actions and owners are specified.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: saas-scaffolder
description: Generates complete, production-ready SaaS project boilerplate including authentication, database schemas, billing integration, API routes, and a working dashboard using Next.js 14+ App Router, Type...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# SaaS Scaffolder

**Tier:** POWERFUL  
**Category:** Product Team  
**Domain:** Full-Stack Development / Project Bootstrapping

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-28
description: [1-3 sentences]
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## File Tree Output

```
my-saas/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx
│   │   ├── settings/page.tsx
│   │   ├── billing/page.tsx
│   │   └── layout.tsx
│   ├── (marketing)/
│   │   ├── page.tsx
│   │   ├── pricing/page.tsx
│   │   └── layout.tsx
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── webhooks/stripe/route.ts
│   │   ├── billing/checkout/route.ts
│   │   └── billing/portal/route.ts
│   └── layout.tsx
├── components/
│   ├── ui/
│   ├── auth/
│   │   ├── login-form.tsx
│   │   └── register-form.tsx
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── stats-card.tsx
│   ├── marketing/
│   │   ├── hero.tsx
│   │   ├── features.tsx
│   │   ├── pricing.tsx
│   │   └── footer.tsx
│   └── billing/
│       ├── plan-card.tsx
│       └── usage-meter.tsx
├── lib/
│   ├── auth.ts
│   ├── db.ts
│   ├── stripe.ts
│   ├── validations.ts
│   └── utils.ts
├── db/
│   ├── schema.ts
│   └── migrations/
├── hooks/
│   ├── use-subscription.ts
│   └── use-user.ts
├── types/index.ts
├── middleware.ts
├── .env.example
├── drizzle.config.ts
└── next.config.ts
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-29
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Scaffold Checklist

The following phases must be completed in order. **Validate at the end of each phase before proceeding.**

### Phase 1 — Foundation
- [ ] 1. Next.js initialized with TypeScript and App Router
- [ ] 2. Tailwind CSS configured with custom theme tokens
- [ ] 3. shadcn/ui installed and configured
- [ ] 4. ESLint + Prettier configured
- [ ] 5. `.env.example` created with all required variables

✅ **Validate:** Run `npm run build` — no TypeScript or lint errors should appear.  
🔧 **If build fails:** Check `tsconfig.json` paths and that all shadcn/ui peer dependencies are installed.

### Phase 2 — Database
- [ ] 6. Drizzle ORM installed and configured
- [ ] 7. Schema written (users, accounts, sessions, verification_tokens)
- [ ] 8. Initial migration generated and applied
- [ ] 9. DB client singleton exported from `lib/db.ts`
- [ ] 10. DB connection tested in local environment

✅ **Validate:** Run a simple `db.select().from(users)` in a test script — it should return an empty array without throwing.  
🔧 **If DB connection fails:** Verify `DATABASE_URL` format includes `?sslmode=require` for NeonDB/Supabase. Check that the migration has been applied with `drizzle-kit push` (dev) or `drizzle-kit migrate` (prod).

### Phase 3 — Authentication
- [ ] 11. Auth provider installed (NextAuth / Clerk / Supabase)
- [ ] 12. OAuth provider configured (Google / GitHub)
- [ ] 13. Auth API route created
- [ ] 14. Session callback adds user ID and subscription status
- [ ] 15. Middleware protects dashboard routes
- [ ] 16. Login and register pages built with error states

✅ **Validate:** Sign in via OAuth, confirm session user has `id` and `subscriptionStatus`. Attempt to access `/dashboard` without a session — you should be redirected to `/login`.  
🔧 **If sign-out loops occur in production:** Ensure `NEXTAUTH_SECRET` is set and consistent across deployments. Add `declare module "next-auth"` to extend session types if TypeScript errors appear.

### Phase 4 — Payments
- [ ] 17. Stripe client initialized with TypeScript types
- [ ] 18. Checkout session route created
- [ ] 19. Customer portal route created
- [ ] 20. Stripe webhook handler with signature verification
- [ ] 21. Webhook updates user subscription status in DB idempotently

✅ **Validate:** Complete a Stripe test checkout using a `4242 4242 4242 4242` card. Confirm `stripeSubscriptionId` is written to the DB. Replay the `checkout.session.completed` webhook event and confirm idempotency (no duplicate DB writes).  
🔧 **If webhook signature fails:** Use `stripe listen --forward-to localhost:3000/api/webhooks/stripe` locally — never hardcode the raw webhook secret. Verify `STRIPE_WEBHOOK_SECRET` matches the listener output.

### Phase 5 — UI
- [ ] 22. Landing page with hero, features, pricing sections
- [ ] 23. Dashboard layout with sidebar and responsive header
- [ ] 24. Billing page showing current plan and upgrade options
- [ ] 25. Settings page with profile update form and success states

✅ **Validate:** Run `npm run build` for a final production build check. Navigate all routes manually and confirm no broken layouts, missing session data, or hydration errors.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-30
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: spec-to-repo
description: Use when the user says 'build me an app', 'create a project from this spec', 'scaffold a new repo', 'generate a starter', 'turn this idea into code', 'bootstrap a project', 'I have requirements and...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Spec to Repo

Turn a natural-language project specification into a complete, runnable starter repository. Not a template filler — a spec interpreter that generates real, working code for any stack.

## When to Use

- User provides a text description of an app and wants code
- User has a PRD, requirements doc, or feature list and needs a codebase
- User says "build me an app that...", "scaffold this", "bootstrap a project"
- User wants a working starter repo, not just a file tree

**Not this skill** when the user wants a SaaS app with Stripe + Auth specifically — use `product-team/saas-scaffolder` instead.

## Core Workflow

### Phase 1 — Parse & Interpret

Read the spec. Extract these fields silently:

| Field | Source | Required |
|-------|--------|----------|
| App name | Explicit or infer from description | yes |
| Description | First sentence of spec | yes |
| Features | Bullet points or sentences describing behavior | yes |
| Tech stack | Explicit ("use FastAPI") or infer from context | yes |
| Auth | "login", "users", "accounts", "roles" | if mentioned |
| Database | "store", "save", "persist", "records", "schema" | if mentioned |
| API surface | "endpoint", "API", "REST", "GraphQL" | if mentioned |
| Deploy target | "Vercel", "Docker", "AWS", "Railway" | if mentioned |

**Stack inference rules** (when user doesn't specify):

| Signal | Inferred stack |
|--------|---------------|
| "web app", "dashboard", "SaaS" | Next.js + TypeScript |
| "API", "backend", "microservice" | FastAPI (Python) or Express (Node) |
| "mobile app" | Flutter or React Native |
| "CLI tool" | Go or Python |
| "data pipeline" | Python |
| "high performance", "systems" | Rust or Go |

After parsing, present a structured interpretation back to the user:

```
## Spec Interpretation

**App:** [name]
**Stack:** [framework + language]
**Features:**
1. [feature]
2. [feature]

**Database:** [yes/no — engine]
**Auth:** [yes/no — method]
**Deploy:** [target]

Does this match your intent? Any corrections before I generate?
```

Flag ambiguities. Ask **at most 3** clarifying questions. If the user says "just build it", proceed with best-guess defaults.

### Phase 2 — Architecture

Design the project before writing any files:

1. **Select template** — Match to a stack template from `references/stack-templates.md`
2. **Define file tree** — List every file that will be created
3. **Map features to files** — Each feature gets at minimum one file/component
4. **Design database schema** — If applicable, define tables/collections with fields and types
5. **Identify dependencies** — List every package with version constraints
6. **Plan API routes** — If applicable, list every endpoint with method, path, request/response shape

Present the file tree to the user before generating:

```
project-name/
├── README.md
├── .env.example
├── .gitignore
├── .github/workflows/ci.yml
├── package.json / requirements.txt / go.mod
├── src/
│   ├── ...
├── tests/
│   ├── ...
└── ...
```

### Phase 3 — Generate

Write every file. Rules:

- **Real code, not stubs.** Every function has a real implementation. No `// TODO: implement` or `pass` placeholders.
- **Syntactically valid.** Every file must parse without errors in its language.
- **Imports match dependencies.** Every import must correspond to a package in the manifest (package.json, requirements.txt, go.mod, etc.).
- **Types included.** TypeScript projects use types. Python projects use type hints. Go projects use typed structs.
- **Environment variables.** Generate `.env.example` with every required variable, commented with purpose.
- **README.md.** Include: project description, prerequisites, setup steps (clone, install, configure env, run), and available scripts/commands.
- **CI config.** Generate `.github/workflows/ci.yml` with: install, lint (if linter in deps), test, build.
- **.gitignore.** Stack-appropriate ignores (node_modules, __pycache__, .env, build artifacts).

**File generation order:**
1. Manifest (package.json / requirements.txt / go.mod)
2. Config files (.env.example, .gitignore, CI)
3. Database schema / migrations
4. Core business logic
5. API routes / endpoints
6. UI components (if applicable)
7. Tests
8. README.md

### Phase 4 — Validate

After generation, run through this checklist:

- [ ] Every imported package exists in the manifest
- [ ] Every file referenced by an import exists in the tree
- [ ] `.env.example` lists every env var used in code
- [ ] `.gitignore` covers build artifacts and secrets
- [ ] README has setup instructions that actually work
- [ ] No hardcoded secrets, API keys, or passwords
- [ ] At least one test file exists
- [ ] Build/start command is documented and would work

Run `scripts/validate_project.py` against the generated directory to catch common issues.

## Examples

### Example 1: Task Management API

**Input spec:**
> "Build me a task management API. Users can create, list, update, and delete tasks. Tasks have a title, description, status (todo/in-progress/done), and due date. Use FastAPI with SQLite. Add basic auth with API keys."

**Output file tree:**
```
task-api/
├── README.md
├── .env.example              # API_KEY, DATABASE_URL
├── .gitignore
├── .github/workflows/ci.yml
├── requirements.txt          # fastapi, uvicorn, sqlalchemy, pytest
├── main.py                   # FastAPI app, CORS, lifespan
├── models.py                 # SQLAlchemy Task model
├── schemas.py                # Pydantic request/response schemas
├── database.py               # SQLite engine + session
├── auth.py                   # API key middleware
├── routers/
│   └── tasks.py              # CRUD endpoints
└── tests/
    └── test_tasks.py         # Smoke tests for each endpoint
```

### Example 2: Recipe Sharing Web App

**Input spec:**
> "I want a recipe sharing website. Users sign up, post recipes with ingredients and steps, browse other recipes, and save favorites. Use Next.js with Tailwind. Store data in PostgreSQL."

**Output file tree:**
```
recipe-share/
├── README.md
├── .env.example              # DATABASE_URL, NEXTAUTH_SECRET, NEXTAUTH_URL
├── .gitignore
├── .github/workflows/ci.yml
├── package.json              # next, react, tailwindcss, prisma, next-auth
├── tailwind.config.ts
├── tsconfig.json
├── next.config.ts
├── prisma/
│   └── schema.prisma         # User, Recipe, Ingredient, Favorite models
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          # Homepage — recipe feed
│   │   ├── recipes/
│   │   │   ├── page.tsx      # Browse recipes
│   │   │   ├── [id]/page.tsx # Recipe detail
│   │   │   └── new/page.tsx  # Create recipe form
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts
│   │       └── recipes/route.ts
│   ├── components/
│   │   ├── RecipeCard.tsx
│   │   ├── RecipeForm.tsx
│   │   └── Navbar.tsx
│   └── lib/
│       ├── prisma.ts
│       └── auth.ts
└── tests/
    └── recipes.test.ts
```

### Example 3: CLI Expense Tracker

**Input spec:**
> "Python CLI tool for tracking expenses. Commands: add, list, summary, export-csv. Store in a local SQLite file. No external API."

**Output file tree:**
```
expense-tracker/
├── README.md
├── .gitignore
├── .github/workflows/ci.yml
├── pyproject.toml
├── src/
│   └── expense_tracker/
│       ├── __init__.py
│       ├── cli.py            # argparse commands
│       ├── database.py       # SQLite operations
│       ├── models.py         # Expense dataclass
│       └── formatters.py     # Table + CSV output
└── tests/
    └── test_cli.py
```

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| **Placeholder code** — `// TODO: implement`, `pass`, empty function bodies | Every function has a real implementation. If complex, implement a working simplified version. |
| **Stack override** — picking Next.js when the user said Flask | Always honor explicit tech preferences. Only infer when the user doesn't specify. |
| **Missing .gitignore** — committing node_modules or .env | Generate stack-appropriate .gitignore as one of the first files. |
| **Phantom imports** — importing packages not in the manifest | Cross-check every import against package.json / requirements.txt before finishing. |
| **Over-engineering MVP** — adding Redis caching, rate limiting, WebSockets to a v1 | Build the minimum that works. The user can iterate. |
| **Ignoring stated preferences** — user says "PostgreSQL" and you generate MongoDB | Parse the spec carefully. Explicit preferences are non-negotiable. |
| **Missing env vars** — code reads `process.env.X` but `.env.example` doesn't list it | Every env var used in code must appear in `.env.example` with a comment. |
| **No tests** — shipping a repo with zero test files | At minimum: one smoke test per API endpoint or one test per core function. |
| **Hallucinated APIs** — generating code that calls library methods that don't exist | Stick to well-documented, stable APIs. When unsure, use the simplest approach. |

## Validation Script

### `scripts/validate_project.py`

Checks a generated project directory for common issues:

```bash
# Validate a generated project
python3 scripts/validate_project.py /path/to/generated-project

# JSON output
python3 scripts/validate_project.py /path/to/generated-project --format json
```

Checks performed:
- README.md exists and is non-empty
- .gitignore exists
- .env.example exists (if code references env vars)
- Package manifest exists (package.json, requirements.txt, go.mod, Cargo.toml, pubspec.yaml)
- No .env file committed (secrets leak)
- At least one test file exists
- No TODO/FIXME placeholders in generated code

## Progressive Enhancement

For complex specs, generate in stages:

1. **MVP** — Core feature only, working end-to-end
2. **Auth** — Add authentication if requested
3. **Polish** — Error handling, validation, loading states
4. **Deploy** — Docker, CI, deploy config

Ask the user after MVP: "Core is working. Want me to add auth/polish/deploy next, or iterate on what's here?"

## Cross-References

- Related: `product-team/saas-scaffolder` — SaaS-specific scaffolding (Next.js + Stripe + Auth)
- Related: `engineering/spec-driven-workflow` — spec-first development methodology
- Related: `engineering/database-designer` — database schema design patterns
- Related: `engineering-team/senior-fullstack` — full-stack implementation patterns


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ui-design-system
description: UI design system toolkit for Senior UI Designer including design token generation, component documentation, responsive design calculations, and developer handoff tools. Use for creating design syst...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# UI Design System

Generate design tokens, create color palettes, calculate typography scales, build component systems, and prepare developer handoff documentation.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-33
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Trigger Terms

Use this skill when you need to:

- "generate design tokens"
- "create color palette"
- "build typography scale"
- "calculate spacing system"
- "create design system"
- "generate CSS variables"
- "export SCSS tokens"
- "set up component architecture"
- "document component library"
- "calculate responsive breakpoints"
- "prepare developer handoff"
- "convert brand color to palette"
- "check WCAG contrast"
- "build 8pt grid system"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-34
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Workflow 2: Create Component System

**Situation:** You need to structure a component library using design tokens.

**Steps:**

1. **Define component hierarchy**
   - Atoms: Button, Input, Icon, Label, Badge
   - Molecules: FormField, SearchBar, Card, ListItem
   - Organisms: Header, Footer, DataTable, Modal
   - Templates: DashboardLayout, AuthLayout

2. **Map tokens to components**

   | Component | Tokens Used |
   |-----------|-------------|
   | Button | colors, sizing, borders, shadows, typography |
   | Input | colors, sizing, borders, spacing |
   | Card | colors, borders, shadows, spacing |
   | Modal | colors, shadows, spacing, z-index, animation |

3. **Define variant patterns**

   Size variants:
   ```
   sm: height 32px, paddingX 12px, fontSize 14px
   md: height 40px, paddingX 16px, fontSize 16px
   lg: height 48px, paddingX 20px, fontSize 18px
   ```

   Color variants:
   ```
   primary: background primary-500, text white
   secondary: background neutral-100, text neutral-900
   ghost: background transparent, text neutral-700
   ```

4. **Document component API**
   - Props interface with types
   - Variant options
   - State handling (hover, active, focus, disabled)
   - Accessibility requirements

5. **Reference:** See `references/component-architecture.md`

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-35
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Workflow 4: Developer Handoff

**Situation:** You need to hand off design tokens to development team.

**Steps:**

1. **Export tokens in required formats**
   ```bash
   # For CSS projects
   python scripts/design_token_generator.py "#0066CC" modern css

   # For SCSS projects
   python scripts/design_token_generator.py "#0066CC" modern scss

   # For JavaScript/TypeScript
   python scripts/design_token_generator.py "#0066CC" modern json
   ```

2. **Prepare framework integration**

   **React + CSS Variables:**
   ```tsx
   import './design-tokens.css';

   <button className="btn btn-primary">Click</button>
   ```

   **Tailwind Config:**
   ```javascript
   const tokens = require('./design-tokens.json');

   module.exports = {
     theme: {
       colors: tokens.colors,
       fontFamily: tokens.typography.fontFamily
     }
   };
   ```

   **styled-components:**
   ```typescript
   import tokens from './design-tokens.json';

   const Button = styled.button`
     background: ${tokens.colors.primary['500']};
     padding: ${tokens.spacing['2']} ${tokens.spacing['4']};
   `;
   ```

3. **Sync with Figma**
   - Install Tokens Studio plugin
   - Import design-tokens.json
   - Tokens sync automatically with Figma styles

4. **Handoff checklist**
   - [ ] Token files added to project
   - [ ] Build pipeline configured
   - [ ] Theme/CSS variables imported
   - [ ] Component library aligned
   - [ ] Documentation generated

5. **Reference:** See `references/developer-handoff.md`

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-36
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quick Reference Tables

### Color Scale Generation

| Step | Brightness | Saturation | Use Case |
|------|------------|------------|----------|
| 50 | 95% fixed | 30% | Subtle backgrounds |
| 100 | 95% fixed | 38% | Light backgrounds |
| 200 | 95% fixed | 46% | Hover states |
| 300 | 95% fixed | 54% | Borders |
| 400 | 95% fixed | 62% | Disabled states |
| 500 | Original | 70% | Base/default color |
| 600 | Original × 0.8 | 78% | Hover (dark) |
| 700 | Original × 0.6 | 86% | Active states |
| 800 | Original × 0.4 | 94% | Text |
| 900 | Original × 0.2 | 100% | Headings |

### Typography Scale (1.25x Ratio)

| Size | Value | Calculation |
|------|-------|-------------|
| xs | 10px | 16 ÷ 1.25² |
| sm | 13px | 16 ÷ 1.25¹ |
| base | 16px | Base |
| lg | 20px | 16 × 1.25¹ |
| xl | 25px | 16 × 1.25² |
| 2xl | 31px | 16 × 1.25³ |
| 3xl | 39px | 16 × 1.25⁴ |
| 4xl | 49px | 16 × 1.25⁵ |
| 5xl | 61px | 16 × 1.25⁶ |

### WCAG Contrast Requirements

| Level | Normal Text | Large Text |
|-------|-------------|------------|
| AA | 4.5:1 | 3:1 |
| AAA | 7:1 | 4.5:1 |

Large text: ≥18pt regular or ≥14pt bold

### Style Presets

| Aspect | Modern | Classic | Playful |
|--------|--------|---------|---------|
| Font Sans | Inter | Helvetica | Poppins |
| Font Mono | Fira Code | Courier | Source Code Pro |
| Radius Default | 8px | 4px | 16px |
| Shadows | Layered, subtle | Single layer | Soft, pronounced |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-37
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Validation Checklist

### Token Generation
- [ ] Brand color provided in hex format
- [ ] Style matches project requirements
- [ ] All token categories generated
- [ ] Semantic colors include contrast values

### Component System
- [ ] All sizes implemented (sm, md, lg)
- [ ] All variants implemented (primary, secondary, ghost)
- [ ] All states working (hover, active, focus, disabled)
- [ ] Uses only design tokens (no hardcoded values)

### Accessibility
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] Touch targets ≥ 44×44px
- [ ] Semantic HTML elements used

### Developer Handoff
- [ ] Tokens exported in required format
- [ ] Framework integration documented
- [ ] Design tool synced
- [ ] Component documentation complete


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ux-researcher-designer
description: UX research and design toolkit for Senior UX Designer/Researcher including data-driven persona generation, journey mapping, usability testing frameworks, and research synthesis. Use for user resear...
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# UX Researcher & Designer

Generate user personas from research data, create journey maps, plan usability tests, and synthesize research findings into actionable design recommendations.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-39
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Trigger Terms

Use this skill when you need to:

- "create user persona"
- "generate persona from data"
- "build customer journey map"
- "map user journey"
- "plan usability test"
- "design usability study"
- "analyze user research"
- "synthesize interview findings"
- "identify user pain points"
- "define user archetypes"
- "calculate research sample size"
- "create empathy map"
- "identify user needs"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-40
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Workflow 2: Create Journey Map

**Situation:** You need to visualize the end-to-end user experience for a specific goal.

**Steps:**

1. **Define scope**

   | Element | Description |
   |---------|-------------|
   | Persona | Which user type |
   | Goal | What they're trying to achieve |
   | Start | Trigger that begins journey |
   | End | Success criteria |
   | Timeframe | Hours/days/weeks |

2. **Gather journey data**

   Sources:
   - User interviews (ask "walk me through...")
   - Session recordings
   - Analytics (funnel, drop-offs)
   - Support tickets

3. **Map the stages**

   Typical B2B SaaS stages:
   ```
   Awareness → Evaluation → Onboarding → Adoption → Advocacy
   ```

4. **Fill in layers for each stage**

   ```
   Stage: [Name]
   ├── Actions: What does user do?
   ├── Touchpoints: Where do they interact?
   ├── Emotions: How do they feel? (1-5)
   ├── Pain Points: What frustrates them?
   └── Opportunities: Where can we improve?
   ```

5. **Identify opportunities**

   Priority Score = Frequency × Severity × Solvability

6. **Reference:** See `references/journey-mapping-guide.md` for templates

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-41
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Workflow 4: Synthesize Research

**Situation:** You have raw research data (interviews, surveys, observations) and need actionable insights.

**Steps:**

1. **Code the data**

   Tag each data point:
   - `[GOAL]` - What they want to achieve
   - `[PAIN]` - What frustrates them
   - `[BEHAVIOR]` - What they actually do
   - `[CONTEXT]` - When/where they use product
   - `[QUOTE]` - Direct user words

2. **Cluster similar patterns**

   ```
   User A: Uses daily, advanced features, shortcuts
   User B: Uses daily, complex workflows, automation
   User C: Uses weekly, basic needs, occasional

   Cluster 1: A, B (Power Users)
   Cluster 2: C (Casual User)
   ```

3. **Calculate segment sizes**

   | Cluster | Users | % | Viability |
   |---------|-------|---|-----------|
   | Power Users | 18 | 36% | Primary persona |
   | Business Users | 15 | 30% | Primary persona |
   | Casual Users | 12 | 24% | Secondary persona |

4. **Extract key findings**

   For each theme:
   - Finding statement
   - Supporting evidence (quotes, data)
   - Frequency (X/Y participants)
   - Business impact
   - Recommendation

5. **Prioritize opportunities**

   | Factor | Score 1-5 |
   |--------|-----------|
   | Frequency | How often does this occur? |
   | Severity | How much does it hurt? |
   | Breadth | How many users affected? |
   | Solvability | Can we fix this? |

6. **Reference:** See `references/persona-methodology.md` for analysis framework

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-42
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quick Reference Tables

### Research Method Selection

| Question Type | Best Method | Sample Size |
|---------------|-------------|-------------|
| "What do users do?" | Analytics, observation | 100+ events |
| "Why do they do it?" | Interviews | 8-15 users |
| "How well can they do it?" | Usability test | 5-8 users |
| "What do they prefer?" | Survey, A/B test | 50+ users |
| "What do they feel?" | Diary study, interviews | 10-15 users |

### Persona Confidence Levels

| Sample Size | Confidence | Use Case |
|-------------|------------|----------|
| 5-10 users | Low | Exploratory |
| 11-30 users | Medium | Directional |
| 31+ users | High | Production |

### Usability Issue Severity

| Severity | Definition | Action |
|----------|------------|--------|
| 4 - Critical | Prevents task completion | Fix immediately |
| 3 - Major | Significant difficulty | Fix before release |
| 2 - Minor | Causes hesitation | Fix when possible |
| 1 - Cosmetic | Noticed but not problematic | Low priority |

### Interview Question Types

| Type | Example | Use For |
|------|---------|---------|
| Context | "Walk me through your typical day" | Understanding environment |
| Behavior | "Show me how you do X" | Observing actual actions |
| Goals | "What are you trying to achieve?" | Uncovering motivations |
| Pain | "What's the hardest part?" | Identifying frustrations |
| Reflection | "What would you change?" | Generating ideas |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: product-team-skill-43
description: Skill from product-team plugin
tier: standard
applyTo: '**/*product*,**/*ux*,**/*roadmap*,**/*discovery*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Validation Checklist

### Persona Quality
- [ ] Based on 20+ users (minimum)
- [ ] At least 2 data sources (quant + qual)
- [ ] Specific, actionable goals
- [ ] Frustrations include frequency counts
- [ ] Design implications are specific
- [ ] Confidence level stated

### Journey Map Quality
- [ ] Scope clearly defined (persona, goal, timeframe)
- [ ] Based on real user data, not assumptions
- [ ] All layers filled (actions, touchpoints, emotions)
- [ ] Pain points identified per stage
- [ ] Opportunities prioritized

### Usability Test Quality
- [ ] Research questions are testable
- [ ] Tasks are realistic scenarios, not instructions
- [ ] 5+ participants per design
- [ ] Success metrics defined
- [ ] Findings include severity ratings

### Research Synthesis Quality
- [ ] Data coded consistently
- [ ] Patterns based on 3+ data points
- [ ] Findings include evidence
- [ ] Recommendations are actionable
- [ ] Priorities justified

## Related Skills

- **UI Design System** (`product-team/ui-design-system/`) — Research findings inform design system decisions
- **Product Manager Toolkit** (`product-team/product-manager-toolkit/`) — Customer interview analysis complements persona research
