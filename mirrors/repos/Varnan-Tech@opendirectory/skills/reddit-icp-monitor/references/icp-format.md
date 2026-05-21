# ICP Format

Rules for defining a good ICP for Reddit monitoring and the canonical docs/icp.md format.

---

## What Makes a Good Pain Point Phrase

Pain point phrases are the most important input. Weak phrases return noise. Strong phrases surface exactly the posts you want.

**Write in first-person buyer language, not product marketing language.**

Good phrases match what someone would actually type when frustrated:
- "onboarding takes forever"
- "can't figure out why users are churning"
- "new hire ramp time is killing us"
- "docs are always out of date"
- "deployment takes hours"
- "can't reproduce what's in production"

Bad phrases use category language your ICP would never use:
- "needs better developer productivity tooling"
- "seeks churn reduction solution"
- "looking for CI/CD pipeline optimization"
- "wants improved observability platform"

**3-6 phrases is the right range.** Too few and you miss signals. Too many and you flood the results with weak matches.

---

## What Makes a Good Subreddit Choice

Choose subreddits where your ICP goes to ask questions, not where they discuss your product category.

Good subreddits (where people describe problems):
- r/devops — engineers asking "how do you handle X" and venting about ops problems
- r/ExperiencedDevs — senior engineers sharing pain points
- r/startups — founders discussing GTM, ops, and scaling problems
- r/SaaS — SaaS founders and operators discussing growth problems
- r/entrepreneurship — early-stage founders venting and asking for advice
- r/sysadmin — ops teams discussing tooling and workflow pain

Bad subreddits (noise, not signal):
- r/programming — too broad, technical discussions not pain points
- r/technology — consumer focus, not B2B
- r/MachineLearning — research-focused, not operational pain
- Your product's own subreddit — not monitoring your own community

---

## Anti-Keywords

Anti-keywords reduce false positives. If a post contains an anti-keyword, Gemini scores it lower.

Common anti-keyword categories:
- Company size disqualifiers: "enterprise", "Fortune 500", "10,000 employees"
- Platform disqualifiers: "SAP", "Oracle", "Salesforce Enterprise"
- Competitor-specific: add your main competitor if their users are not your ICP
- Geographic disqualifiers: "government", "regulated industry", "HIPAA-only" (if you don't serve those)

---

## Canonical docs/icp.md Format

```yaml
---
product: "One sentence: what the product does and who it's for."
personas:
  - "Job title, company size, industry (e.g. VP Engineering, 50-200 person B2B SaaS)"
  - "Job title, company size, industry (add more if needed)"
---

pain_points:
  - "exact phrase your ICP uses when they have the problem"
  - "another phrase — keep it first-person and conversational"
  - "third phrase"
  - "fourth phrase (optional)"
  - "fifth phrase (optional)"

anti_keywords:
  - "enterprise"
  - "government"
  - "add more if needed"

subreddits:
  - devops
  - ExperiencedDevs
  - startups
```

**Rules:**
- `product` must be one sentence. The agent passes this to Gemini for scoring context.
- `pain_points` must be in quotes. Each is passed as a Reddit search query.
- `subreddits` are bare names without the `r/` prefix.
- The file is saved automatically after the first run if it does not exist.
- Edit it directly to refine keywords based on what you find.

---

## Worked Example

For a sales onboarding platform targeting VP Sales at B2B SaaS companies:

```yaml
---
product: "Ramp helps B2B SaaS sales teams cut new hire time-to-first-deal by replacing ad hoc onboarding with structured playbooks and live deal coaching."
personas:
  - "VP Sales, 50-200 person B2B SaaS company"
  - "Head of Revenue, Series B startup"
---

pain_points:
  - "new rep ramp time too long"
  - "sales onboarding is a mess"
  - "new hires aren't hitting quota"
  - "onboarding takes 90 days"
  - "reps forget what they learned in training"

anti_keywords:
  - "enterprise"
  - "government"
  - "channel sales"

subreddits:
  - sales
  - SaaS
  - startups
  - EntrepreneurRideAlong
```

Subreddits to avoid for this product: r/cscareerquestions (job seekers, not managers), r/sales (mostly individual contributors, not VPs).
