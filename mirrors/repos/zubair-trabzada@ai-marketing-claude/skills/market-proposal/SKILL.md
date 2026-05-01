# Client Proposal Generator for Marketing Services

## Skill Purpose
Generate a professional, client-ready marketing services proposal. This skill produces a complete proposal document that positions the agency/consultant as the clear choice, frames pricing with anchoring and tiered options, and includes ROI projections to justify the investment.

## When to Use
- User wants to create a proposal for a prospective marketing client
- User has completed a discovery call and needs to formalize the engagement
- User wants a template for their marketing agency's proposals
- Triggered by `/market proposal` or `/market proposal <client name>`

## How to Execute

### Step 1: Gather Proposal Inputs
Collect these details from the user (ask if not provided):

**About the Client:**
1. Client name and company
2. Industry and business model
3. Current marketing situation (what they're doing now)
4. Primary pain points or challenges
5. Goals (revenue, growth, leads, brand awareness)
6. Budget range (if known)
7. Decision timeline
8. Key stakeholders and decision-makers

**About the Services:**
1. What services are you proposing? (SEO, paid ads, content, social, email, full-stack)
2. Engagement model (retainer, project, performance-based)
3. Proposed timeline
4. Your relevant case studies or results

**If audit data exists:** Check for any previous `/market audit` results. If found, automatically incorporate the findings into the Situation Analysis section for a data-backed proposal.

### Step 2: Discovery Call Question Framework
If the user hasn't had the discovery call yet, provide these 10 essential questions:

**Business Understanding:**
1. "Walk me through your business model. How do you make money?"
2. "Who is your ideal customer? Describe them in detail."
3. "What does your sales process look like from first touch to closed deal?"

**Current Marketing:**
4. "What marketing are you doing today, and what's working or not working?"
5. "What's your current monthly marketing spend, and what's the ROI?"
6. "What tools and platforms are you using?"

**Goals and Expectations:**
7. "If we're wildly successful, what does that look like in 6 months? 12 months?"
8. "What specific numbers are you trying to hit? (Revenue, leads, traffic)"
9. "What's the lifetime value of a customer for you?"

**Decision and Process:**
10. "Who else is involved in this decision, and what's your timeline for choosing a partner?"

**Bonus Questions:**
- "What's your biggest frustration with marketing right now?"
- "Have you worked with agencies or consultants before? What went well or poorly?"
- "Is there anything that would make you say 'no' to working together?"

### Step 3: Build the Proposal Document

#### Section 1: Cover Page
```
[Your Company Logo]

Marketing Strategy Proposal
Prepared for: [Client Name]
Prepared by: [Your Name / Agency]
Date: [Date]
Valid until: [Date + 30 days]

CONFIDENTIAL
```

#### Section 2: Executive Summary (1 page max)
Write a concise summary that:
- Acknowledges the client's situation and goals
- States the core problem you will solve
- Previews your recommended approach
- Hints at the expected outcome
- Creates urgency to act

**Template:**
```
[Client Name] is at an inflection point. With [current situation -- e.g., strong product-market fit but inconsistent lead generation], there's a significant opportunity to [desired outcome -- e.g., scale customer acquisition to support your growth targets].

Based on our analysis of [what you reviewed -- their website, ads, competitors, etc.], we've identified [X] key areas where strategic improvements could drive [specific result -- e.g., a 40-60% increase in qualified leads within 6 months].

This proposal outlines a [timeframe] engagement focused on [primary service areas], designed to [primary outcome]. Our approach is built on [your differentiator -- e.g., data-driven methodology, industry expertise, proven frameworks].

We recommend beginning with [first phase] to establish baselines and quick wins, then scaling efforts based on performance data.
```

#### Section 3: Situation Analysis (2-3 pages)
Present your analysis of the client's current marketing. This is where audit data from `/market audit` is invaluable.

**Structure:**
1. **Current State Overview** -- What they're doing now and how it's performing
2. **Opportunities Identified** -- Specific areas where improvement is possible
3. **Competitive Landscape** -- How they compare to competitors (from `/market competitors` if available)
4. **Key Challenges** -- Obstacles that need to be addressed
5. **Market Context** -- Industry trends and benchmarks

**Important:** Frame everything as opportunities, not failures. The client should feel understood, not criticized.

Good: "Your website converts at approximately 1.8%, which is below the industry benchmark of 3.2%. We see a clear path to close this gap through targeted CRO initiatives."

Bad: "Your website has a terrible conversion rate and needs a complete overhaul."

#### Section 4: Strategy and Approach (2-3 pages)
Present your recommended strategy. Be specific enough to demonstrate expertise but not so detailed that they could execute it without you.

**Structure:**
1. **Strategic Framework** -- Your overall approach and methodology
2. **Phase 1: Foundation** (Month 1-2) -- Setup, audits, baselines, quick wins
3. **Phase 2: Growth** (Month 3-4) -- Core campaign execution, optimization
4. **Phase 3: Scale** (Month 5-6) -- Expand what works, cut what doesn't, increase investment in winners
5. **Ongoing: Optimize** -- Continuous improvement, reporting, strategy refinement

For each phase, include:
- Specific activities and deliverables
- Expected outcomes
- How success will be measured

#### Section 5: Scope of Work (1-2 pages)
Detail exactly what is included (and what is not).

**Include:**
- Specific deliverables with quantities (e.g., "8 blog posts per month, 1,500-2,000 words each")
- Meeting cadence (e.g., "Bi-weekly strategy calls, monthly reporting")
- Response time commitments (e.g., "24-hour response on business days")
- Tools and platforms included
- Reporting format and frequency

**Explicitly Exclude:**
- Items outside scope to prevent scope creep
- Additional costs (ad spend, software, stock photos)
- Assumptions about client responsibilities

**Client Responsibilities Section:**
List what you need from the client to be successful:
- Timely feedback and approvals (specify SLA)
- Access to accounts, tools, and data
- Designated point of contact
- Content approvals within X business days
- Ad budget (separate from management fees)

#### Section 6: Timeline (1 page)
Visual timeline showing phases, milestones, and deliverables.

```
Month 1    | Month 2    | Month 3    | Month 4    | Month 5    | Month 6
-----------|------------|------------|------------|------------|----------
FOUNDATION | FOUNDATION | GROWTH     | GROWTH     | SCALE      | SCALE
Audit &    | Quick wins | Campaign   | Optimize   | Expand     | Full
Setup      | & baselines| Launch     | & iterate  | winners    | throttle

Key Milestones:
- Week 2: Complete audit and strategy document
- Week 4: First campaigns live
- Month 2: First performance report
- Month 3: Optimization recommendations
- Month 6: Comprehensive review and strategy refresh
```

#### Section 7: Investment (1-2 pages)
Present pricing using the Good-Better-Best tier structure.

**Three-Tier Pricing Model:**

| Component | Growth | Accelerate | Dominate |
|---|---|---|---|
| Strategy & Planning | Quarterly review | Monthly strategy | Weekly strategy |
| Content Creation | 4 pieces/month | 8 pieces/month | 16 pieces/month |
| Social Media | 3 platforms | 5 platforms | All platforms |
| Paid Ads Management | Up to $5K spend | Up to $15K spend | Up to $50K spend |
| SEO | Basic on-page | Full SEO program | Full SEO + link building |
| Email Marketing | -- | Monthly newsletter | Full automation |
| Reporting | Monthly report | Bi-weekly report | Weekly dashboard |
| Meetings | Monthly call | Bi-weekly call | Weekly call |
| **Monthly Investment** | **$X,XXX** | **$X,XXX** | **$X,XXX** |

**Pricing Psychology Tips:**
- Present three options; most clients choose the middle tier
- Name the tiers with aspirational labels (not Bronze/Silver/Gold)
- Anchor the highest tier first to make the middle tier feel reasonable
- Include a "Most Popular" or "Recommended" badge on the middle tier
- Show the math: "At [your LTV], you only need [X] new customers per month to see positive ROI"

**Pricing Models Reference:**

| Model | When to Use | Typical Range |
|---|---|---|
| Monthly Retainer | Ongoing services, relationship-based | $2,000-$25,000/month |
| Project-Based | Defined scope, one-time deliverable | $5,000-$100,000 per project |
| Performance-Based | Client wants risk-sharing, you're confident | Base + % of revenue/leads |
| Hybrid | Complex engagements | Base retainer + performance bonus |
| Hourly | Consulting, advisory, ad-hoc | $150-$500/hour |

#### Section 8: ROI Projection
Show the client the expected return on their investment.

**ROI Calculation Framework:**
```
Current State:
- Monthly website traffic: [X]
- Current conversion rate: [X%]
- Current leads/month: [X]
- Close rate: [X%]
- Average deal value: $[X]
- Current monthly revenue from marketing: $[X]

Projected State (6 months):
- Projected traffic increase: [X%] -> [new traffic]
- Projected conversion rate: [X%] -> [new leads/month]
- Projected leads increase: [X%]
- Projected revenue increase: $[X]/month
- 6-month projected ROI: [X]x

Investment: $[total 6-month cost]
Projected Return: $[projected revenue increase]
ROI: [X]x return
```

**Important:** Be conservative with projections. Under-promise and over-deliver. Use ranges rather than specific numbers. Add disclaimers that results depend on multiple factors.

#### Section 9: Team (0.5-1 page)
Introduce the team members who will work on this account.

For each team member:
- Name and title
- Relevant experience and expertise
- Role on this engagement
- Brief bio (2-3 sentences max)

#### Section 10: Case Studies (1-2 pages)
Include 2-3 relevant case studies that demonstrate results similar to what you're promising.

**Case Study Format:**
```
Client: [Industry and company type -- anonymize if needed]
Challenge: [1-2 sentences about their situation]
Solution: [1-2 sentences about what you did]
Results:
- [Specific metric 1: e.g., "Increased organic traffic 287% in 6 months"]
- [Specific metric 2: e.g., "Reduced cost per lead from $45 to $12"]
- [Specific metric 3: e.g., "Generated $180K in new revenue"]
```

#### Section 11: Next Steps (0.5 page)
Make it crystal clear what happens next. Reduce friction.

```
Ready to move forward? Here's what happens next:

1. Sign this proposal (e-signature link included)
2. We'll schedule a kickoff call within 48 hours
3. You'll receive our onboarding questionnaire and access request form
4. We begin the Foundation phase immediately

Questions? Contact [Name] at [email] or [phone].

This proposal is valid until [date -- 30 days from now].
```

### Step 4: Proposal Design and Formatting

**Best Practices:**
- Keep total proposal under 15 pages (excluding appendix)
- Use consistent headers, fonts, and colors throughout
- Include the client's logo alongside yours on the cover page
- Use charts and visuals instead of dense text wherever possible
- Bold key numbers and outcomes
- Use whitespace generously -- don't cram content
- Include page numbers and a table of contents for longer proposals
- Save as PDF for professional presentation

**Formatting in Markdown:**
- Use H1 for the proposal title
- Use H2 for major sections
- Use H3 for subsections
- Use tables for pricing, timelines, and comparisons
- Use bold for emphasis on key points
- Use blockquotes for client testimonials

### Step 5: Follow-Up Sequence After Sending

**Day 0 (Send Day):**
Send proposal via email with a brief cover note. Subject: "Your Marketing Growth Plan -- [Client Name]"

**Day 2:**
Follow-up email: "I wanted to make sure you received the proposal. Happy to hop on a quick call to walk through it if that would be helpful."

**Day 5:**
Value-add follow-up: Share a relevant article, case study, or insight related to their industry. Softly reference the proposal.

**Day 7:**
Direct follow-up: "I'd love to hear your thoughts on the proposal. Do you have any questions I can address? I'm available [specific times] this week for a call."

**Day 14:**
Final follow-up: "I wanted to check in one more time about the proposal. I understand timing may not be right -- if that's the case, I'm happy to reconnect when it makes sense. Otherwise, I'd love to discuss next steps."

**Day 21:**
Breakup email: "I haven't heard back, so I'll assume the timing isn't right. I'll close out this proposal on [expiration date]. If things change, my door is always open. Wishing you and [Company] the best."

### Step 6: Objection Handling

Prepare responses for common client pushbacks:

| Objection | Response Framework |
|---|---|
| "Too expensive" | Reframe as investment, show ROI math, offer smaller starting scope, compare to cost of inaction |
| "We can do this in-house" | Highlight opportunity cost, specialized expertise, speed to results, and the real fully-loaded cost of in-house |
| "We tried this before and it didn't work" | Ask what specifically didn't work, differentiate your approach, offer a pilot project with clear success criteria |
| "We need to think about it" | Set a specific follow-up date, offer to address specific concerns, provide additional references |
| "Can you guarantee results?" | Explain why guarantees are unrealistic in marketing but share historical results, offer performance-based component |
| "We're talking to other agencies" | Welcome it, differentiate on methodology not price, offer a trial period, emphasize culture fit |
| "The timeline is too long" | Explain why shortcuts fail, offer a quick-wins phase, show the phased approach with early value |
| "We don't have the budget right now" | Offer a smaller starting engagement, defer some payment, show the cost of waiting |

### Step 7: Terms and Conditions Essentials

Include these in the proposal appendix or as a separate document:

1. **Payment Terms:** Net 15 or Net 30, payment methods, late payment penalties
2. **Contract Duration:** Minimum commitment period, auto-renewal terms
3. **Cancellation Policy:** Required notice period (typically 30 days), exit process
4. **Scope Changes:** Process for handling scope changes and additional costs
5. **Intellectual Property:** Who owns the work product, license terms
6. **Confidentiality:** NDA terms, how client data is handled
7. **Liability Limitations:** Caps on liability, force majeure
8. **Reporting and Communication:** Agreed cadence and format
9. **Third-Party Costs:** Client responsibility for ad spend, software, stock images
10. **Results Disclaimer:** Marketing results are not guaranteed, past performance context

## Output Format

Generate a file called `CLIENT-PROPOSAL.md` with:

```markdown
# Marketing Services Proposal

## Prepared for: [Client Name]
## Prepared by: [Agency Name]
## Date: [Date]

---

## Table of Contents
1. Executive Summary
2. Situation Analysis
3. Strategy & Approach
4. Scope of Work
5. Timeline
6. Investment
7. ROI Projection
8. Our Team
9. Case Studies
10. Next Steps

---

[Full proposal content with all sections populated based on client details]

---

## Appendix
- Terms & Conditions
- Detailed Deliverable Descriptions
- Tool Stack
```

## Key Principles
- The proposal is a sales document, not a statement of work. It should SELL, not just describe.
- Lead with the client's problems and goals, not your services. Make them feel understood before presenting solutions.
- Every price should be anchored to the ROI it will generate. Never present cost without context.
- Use the client's own language from the discovery call. Mirror their words back to them.
- If audit data is available from previous skills, use it extensively -- data-backed proposals close at 2-3x the rate of generic proposals.
- Keep it concise. Executives skim. Use bold, headers, and tables to make key information scannable.
- Always include a specific, time-bound next step. Ambiguity kills deals.
