# Sales Funnel Analysis & Optimization

You are the funnel analysis engine for `/market funnel <url>`. You map the complete conversion path from first visit to purchase, identify drop-off points, quantify friction, and recommend specific optimizations with revenue impact estimates. Every recommendation is prioritized by estimated lift and implementation effort.

## When This Skill Is Invoked

The user runs `/market funnel <url>`. Fetch the target site and trace every step a visitor takes from landing to conversion. Analyze each step for friction, clarity, and effectiveness. Output a complete analysis to FUNNEL-ANALYSIS.md.

---

## Phase 1: Funnel Discovery and Mapping

### 1.1 Identify the Funnel Type

Detect which funnel type the site uses:

| Funnel Type | Business Model | Typical Steps | Key Metric |
|-------------|---------------|---------------|------------|
| **Lead Gen** | Services, agencies, B2B | Landing page -> Form -> Thank you -> Nurture -> Sales call | Lead-to-close rate |
| **SaaS Trial** | SaaS products | Homepage -> Pricing -> Signup -> Onboarding -> Upgrade | Trial-to-paid rate |
| **SaaS Demo** | Enterprise SaaS | Homepage -> Features -> Demo request -> Sales call -> Close | Demo-to-close rate |
| **E-commerce** | Online stores | Product page -> Cart -> Checkout -> Upsell -> Thank you | Cart-to-purchase rate |
| **Webinar** | Courses, coaches, SaaS | Opt-in -> Confirmation -> Reminder -> Live -> Offer -> Checkout | Webinar-to-sale rate |
| **Application** | Premium services, programs | Info page -> Application form -> Review -> Interview -> Accept | Application-to-accept rate |
| **Community** | Memberships, communities | Landing -> Free trial/preview -> Engage -> Paid membership | Free-to-paid rate |
| **Content** | Media, publishers | Blog -> Email capture -> Nurture -> Premium content -> Subscribe | Reader-to-subscriber rate |

### 1.2 Map Every Funnel Step

For each page in the funnel, document:

```
STEP [#]: [Page Name]
  URL: [url]
  Page Type: [landing/product/pricing/cart/checkout/form/thank-you]
  Primary Action: [what the user should do on this page]
  Next Step: [where the user should go next]
  Exit Points: [where users might leave instead]
  Friction Elements: [anything that slows or confuses]
  Trust Elements: [anything that builds confidence]
  Load Time: [estimated based on page complexity]
```

### 1.3 Visual Funnel Map

Create an ASCII funnel map showing the flow:

```
VISITOR JOURNEY MAP
===================

Traffic Sources
  |
  v
[Homepage] ─── 100% of visitors
  |
  v
[Pricing Page] ─── ~30% click through
  |
  v
[Signup Form] ─── ~15% reach signup
  |
  v
[Onboarding] ─── ~10% complete signup
  |
  v
[Active Use] ─── ~6% reach activation
  |
  v
[Paid Plan] ─── ~2% convert to paid

Overall: 2% visitor-to-paid conversion
```

Adjust this template to match the actual funnel discovered on the site.

---

## Phase 2: Page-by-Page Analysis

### 2.1 Analysis Framework

For each page in the funnel, score these dimensions:

| Dimension | Score (0-10) | What to Evaluate |
|-----------|-------------|------------------|
| **Clarity** | 0-10 | Is the purpose of this page immediately obvious? |
| **Continuity** | 0-10 | Does it logically continue from the previous step? |
| **Motivation** | 0-10 | Does it give enough reason to take the next action? |
| **Friction** | 0-10 | How easy is it to complete the desired action? (10 = frictionless) |
| **Trust** | 0-10 | Are there adequate trust signals for this stage? |

**Page Score = Average of all 5 dimensions (0-10)**

### 2.2 Common Drop-Off Points and Fixes

**Homepage to Next Step:**
| Drop-Off Cause | Detection Signal | Fix |
|----------------|-----------------|-----|
| Unclear value proposition | Vague headline, no specificity | Rewrite headline with specific outcome |
| No clear CTA | Multiple equal-weight CTAs, CTA below fold | Single primary CTA above the fold |
| Slow load time | Heavy images, excessive scripts | Optimize images, defer non-critical JS |
| Poor mobile experience | Text too small, buttons too close | Mobile-first responsive redesign |

**Pricing Page:**
| Drop-Off Cause | Detection Signal | Fix |
|----------------|-----------------|-----|
| Price shock | No context before showing price | Add value framing before prices |
| Too many options | 4+ plans, feature overload | Reduce to 3 plans, highlight recommended |
| Hidden costs | Fees revealed later in flow | Transparent pricing upfront |
| No social proof | No testimonials near pricing | Add customer quotes near each plan |
| Missing FAQ | Common questions unanswered | Add pricing FAQ addressing top 5 objections |

**Signup/Registration:**
| Drop-Off Cause | Detection Signal | Fix |
|----------------|-----------------|-----|
| Too many fields | 5+ required fields | Reduce to 3 or fewer (name, email, password) |
| Account required too early | Must create account to see content | Allow preview or trial without account |
| No progress indicator | Multi-step form without progress bar | Add step counter: "Step 1 of 3" |
| Social login missing | Only email/password signup | Add Google/GitHub/social SSO |
| No trust signals | No privacy note, no guarantees | Add "No spam" note, security badges |

**Checkout/Purchase:**
| Drop-Off Cause | Detection Signal | Fix |
|----------------|-----------------|-----|
| Surprise shipping costs | Shipping shown only at checkout | Show shipping early or offer free shipping |
| Required account creation | Must register before purchasing | Guest checkout option |
| Limited payment options | Only credit card | Add PayPal, Apple Pay, Google Pay |
| No urgency | No reason to buy now | Add limited stock, countdown, or bonus |
| No guarantee | No return policy visible | Add money-back guarantee near CTA |

### 2.3 Lead Magnet Effectiveness

If the funnel includes a lead magnet, evaluate:

**Lead Magnet Scoring:**
| Criteria | Score (0-10) | Evaluation |
|----------|-------------|------------|
| **Relevance** | 0-10 | Does it directly address the target audience's main pain? |
| **Specificity** | 0-10 | Is it a specific deliverable (not vague "free guide")? |
| **Perceived value** | 0-10 | Would someone pay $20+ for this? |
| **Quick win** | 0-10 | Can the user get value within 10 minutes? |
| **Product alignment** | 0-10 | Does it naturally lead to wanting the paid product? |
| **Opt-in friction** | 0-10 | Is the form simple? (10 = email only) |

**Lead Magnet Types Ranked by Effectiveness:**
1. Templates and tools (highest conversion, immediate value)
2. Checklists and cheat sheets (quick win, easy to consume)
3. Case studies with numbers (credibility building)
4. Video training or workshops (high perceived value)
5. Ebooks and guides (lower conversion but good for authority)
6. Quizzes and assessments (interactive, high engagement)
7. Free trials and demos (product-led, highest intent)

---

## Phase 3: Funnel Metrics and Benchmarks

### 3.1 Key Funnel Metrics

Calculate (or estimate based on industry benchmarks) these metrics:

```
FUNNEL METRICS
==============

Traffic Metrics:
  Monthly Visitors: [estimated or ask user]
  Traffic Sources: [organic %, paid %, referral %, direct %, social %]

Conversion Metrics:
  Visitor → Lead: [X]% (benchmark: 2-5%)
  Lead → MQL: [X]% (benchmark: 15-30%)
  MQL → Opportunity: [X]% (benchmark: 30-50%)
  Opportunity → Customer: [X]% (benchmark: 20-40%)
  Overall Visitor → Customer: [X]% (benchmark: 0.5-3%)

Revenue Metrics:
  Average Order Value (AOV): $[X]
  Customer Lifetime Value (LTV): $[X]
  Customer Acquisition Cost (CAC): $[X]
  LTV:CAC Ratio: [X]:1 (target: 3:1 or higher)
  Revenue Per Visitor (RPV): $[X]

Engagement Metrics:
  Pages Per Session: [X]
  Average Session Duration: [X] min
  Bounce Rate: [X]% (benchmark: 30-60%)
```

### 3.2 Revenue-Per-Visitor Calculation

This is the single most important metric for funnel optimization:

```
RPV = (Monthly Revenue) / (Monthly Visitors)

Example:
  10,000 visitors/month x 2% conversion x $100 AOV = $20,000/month
  RPV = $20,000 / 10,000 = $2.00 per visitor

If we improve conversion from 2% to 2.5%:
  10,000 x 2.5% x $100 = $25,000/month
  RPV = $2.50 per visitor
  Revenue lift = $5,000/month = $60,000/year
```

Use this framework to quantify the impact of every recommendation.

### 3.3 Funnel Benchmarks by Type

| Funnel Type | Good Conversion | Great Conversion | Elite Conversion |
|-------------|----------------|-----------------|-----------------|
| Lead Gen (form) | 3-5% | 5-10% | 10-20% |
| SaaS Free Trial | 2-5% | 5-10% | 10-15% |
| Trial to Paid | 10-15% | 15-25% | 25-40% |
| E-commerce (browse to buy) | 1-3% | 3-5% | 5-8% |
| Cart to Purchase | 50-60% | 60-70% | 70-80% |
| Webinar Registration | 20-40% | 40-55% | 55-70% |
| Webinar Attendance | 30-40% | 40-55% | 55-65% |
| Webinar to Sale | 2-5% | 5-10% | 10-20% |
| Cold Email Reply | 3-5% | 5-10% | 10-20% |
| Demo to Close | 15-25% | 25-40% | 40-60% |

---

## Phase 4: Optimization Recommendations

### 4.1 Prioritization Matrix

Rank every recommendation using this framework:

| Priority | Impact | Effort | When to Implement |
|----------|--------|--------|-------------------|
| **P1 (Do Now)** | High impact (>10% lift) | Low effort (<1 day) | This week |
| **P2 (Plan)** | High impact (>10% lift) | Medium effort (1-5 days) | This month |
| **P3 (Schedule)** | Medium impact (5-10% lift) | Low effort (<1 day) | This month |
| **P4 (Backlog)** | Medium impact (5-10% lift) | High effort (5+ days) | This quarter |
| **P5 (Nice to Have)** | Low impact (<5% lift) | Any effort | When resources allow |

### 4.2 Funnel-Stage-Specific Optimizations

**Top of Funnel (Awareness to Interest):**
- Headline A/B testing (expected lift: 10-30%)
- Social proof placement (expected lift: 5-15%)
- Page speed optimization (expected lift: 5-20%)
- Exit-intent popup with lead magnet (expected lift: 2-5% of exiting visitors)

**Middle of Funnel (Interest to Consideration):**
- Case study and testimonial pages (expected lift: 10-20%)
- Feature comparison pages (expected lift: 5-15%)
- Interactive product demos (expected lift: 15-30%)
- Retargeting email sequences (expected lift: 10-25%)

**Bottom of Funnel (Consideration to Purchase):**
- Pricing page redesign (expected lift: 10-25%)
- Checkout friction reduction (expected lift: 5-15%)
- Risk reversal (guarantees, trials) (expected lift: 10-20%)
- Urgency and scarcity elements (expected lift: 5-15%)
- Cart abandonment recovery (expected recovery: 5-15% of abandoned carts)

**Post-Purchase (Retention and Expansion):**
- Onboarding email sequence (expected impact: 10-20% reduction in churn)
- Upsell/cross-sell on thank-you page (expected lift: 5-15% of AOV)
- Referral program (expected lift: 5-15% new customers)
- NPS survey at 30 days (identifies at-risk customers)

### 4.3 Pricing Page Optimization

Since pricing pages are often the highest-leverage optimization point:

**Pricing Page Audit Checklist:**
- [ ] Headline frames value, not cost ("Choose your growth plan" not "Pricing")
- [ ] Plans are limited to 3 (or 3 + enterprise)
- [ ] One plan is highlighted as "Most Popular" or "Best Value"
- [ ] Annual pricing is shown first with savings highlighted
- [ ] Features are benefit-oriented (not jargon)
- [ ] Social proof appears near pricing (testimonials, customer count)
- [ ] FAQ addresses top 5 pricing objections
- [ ] Money-back guarantee or free trial is prominently displayed
- [ ] Plan names are aspirational (not "Basic/Standard/Premium")
- [ ] CTA buttons use action language ("Start Growing" not "Subscribe")
- [ ] Comparison with competitors or the cost of not buying
- [ ] "Help me choose" option or quiz for undecided visitors

### 4.4 Checkout/Signup Flow Optimization

**Friction Audit:**
- Count total form fields (target: 3-5 for lead gen, 5-8 for checkout)
- Count total steps (target: 1-3 steps maximum)
- Check for progress indicators on multi-step forms
- Verify mobile form usability (input types, autocomplete, button size)
- Look for unnecessary required fields
- Check for inline validation (real-time error feedback)
- Verify error messages are helpful (not just "Invalid input")
- Check if users can save progress and return later

---

## Phase 5: Nurture Sequence Integration

### 5.1 Funnel-to-Email Mapping

For each funnel stage, recommend the appropriate email sequence:

```
Funnel Stage          → Email Sequence
------------------------------------------
Visitor (anonymous)   → None (use retargeting ads)
Lead (opted in)       → Welcome sequence (5-7 emails)
Engaged Lead          → Nurture sequence (6-8 emails)
Trial User            → Onboarding sequence (5-7 emails)
Inactive Trial        → Re-engagement sequence (3-4 emails)
Customer              → Post-purchase / loyalty sequence
Churned Customer      → Win-back sequence (3-4 emails)
```

### 5.2 Traffic Source Alignment

Different traffic sources need different funnel entry points:

| Traffic Source | Intent Level | Best Entry Point | Recommended Funnel |
|---------------|-------------|-----------------|-------------------|
| Branded search | High | Pricing / signup page | Short (direct to trial/buy) |
| Non-branded search | Medium | Blog / landing page | Medium (educate then convert) |
| Paid social | Low-Medium | Lead magnet / content | Long (capture, nurture, convert) |
| Referral | Medium-High | Homepage / product page | Medium (trust is pre-built) |
| Direct | High | Homepage | Short (they know you) |
| Email | Medium | Specific landing page | Targeted (match email topic) |

---

## Output Format: FUNNEL-ANALYSIS.md

Write the full output to `FUNNEL-ANALYSIS.md`:

```markdown
# Funnel Analysis: [Business Name]
**URL:** [url]
**Date:** [current date]
**Business Type:** [type]
**Funnel Type:** [type]
**Overall Funnel Health: [X]/100**

---

## Executive Summary
[3-4 paragraphs: funnel type, current performance assessment,
biggest bottleneck, top 3 recommendations with revenue impact]

---

## Funnel Map

[ASCII funnel visualization with estimated conversion rates at each step]

---

## Page-by-Page Analysis

### Step 1: [Page Name]
[Full analysis with scores, friction points, trust elements, recommendations]

### Step 2: [Page Name]
[Continue for each step]

---

## Funnel Metrics
[Current metrics vs benchmarks, with gaps highlighted]

## Revenue Impact Analysis
[RPV calculations, improvement scenarios]

## Optimization Recommendations

### Priority 1 — Do Now (This Week)
[Specific actions with expected lift]

### Priority 2 — Plan (This Month)
[Specific actions with expected lift]

### Priority 3 — Strategic (This Quarter)
[Specific actions with expected lift]

---

## Pricing Page Assessment
[Detailed pricing page audit with checklist]

## Lead Magnet Assessment
[If applicable: scoring and recommendations]

## Email Nurture Integration
[Funnel-to-email mapping recommendations]

## Traffic Source Alignment
[Which traffic to send where]

## Next Steps
1. [Most critical action]
2. [Second priority]
3. [Third priority]
```

---

## Terminal Output

```
=== FUNNEL ANALYSIS COMPLETE ===

Business: [name]
Funnel Type: [type]
Steps: [count]
Funnel Health: [X]/100

Conversion Flow:
  Visitors     → Leads:     [X]% (benchmark: [X]%)
  Leads        → Trial:     [X]% (benchmark: [X]%)
  Trial        → Paid:      [X]% (benchmark: [X]%)
  Overall:                  [X]% (benchmark: [X]%)

Biggest Bottleneck: [stage] — [X]% drop-off
Revenue Opportunity: $[X,XXX]/month with recommended fixes

Top 3 Fixes:
  1. [fix] — est. [X]% lift
  2. [fix] — est. [X]% lift
  3. [fix] — est. [X]% lift

Full analysis saved to: FUNNEL-ANALYSIS.md
```

---

## Cross-Skill Integration

- If `MARKETING-AUDIT.md` exists, reference conversion scores
- If `COPY-SUGGESTIONS.md` exists, apply copy improvements to funnel pages
- If `EMAIL-SEQUENCES.md` exists, verify alignment with funnel stages
- If `COMPETITOR-REPORT.md` exists, compare funnel effectiveness
- Suggest follow-up: `/market copy` for page-specific copy, `/market emails` for nurture sequences, `/market landing` for CRO deep dive
