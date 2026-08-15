---
name: competitor-tracking
description: "Tracks developer-tool rivals on features, pricing, GitHub traction, content, community sentiment, and six-section sales battlecards. Use for competitive intelligence, battlecards, pricing comparisons, or a response to a rival launch. Not a consumer-brand listening playbook; do not use for SEO keyword research or writing positioning copy as the main deliverable."
version: 1.0.1
risk: unknown
source: https://github.com/jonathimer/devmarketing-skills/tree/main/skills/competitor-tracking
source_repo: jonathimer/devmarketing-skills
source_type: community
date_added: 2026-07-01
license: MIT
license_source: https://github.com/jonathimer/devmarketing-skills/blob/main/LICENSE
---

# Competitor Tracking

## Overview

Competitor tracking for developer tools requires monitoring multiple dimensions: product features, pricing, developer sentiment, content strategy, community growth, and funding/trajectory. Unlike consumer products, developer tools compete on technical merit, documentation quality, and community trust.

Effective competitor tracking helps you:

- Understand your competitive positioning
- Anticipate competitor moves
- Arm sales and marketing with accurate battlecards
- Identify market gaps and opportunities
- Learn from competitor successes and failures

## When to Use

Use this skill when you need systematic competitor analysis for developer tools. Trigger phrases and scenarios:

- "competitor analysis" / "track competitors" / "competitive intelligence" / "competitor research"
- "what are our competitors doing?"
- "build a battlecard for [competitor]"
- "how does our pricing compare to [competitor]?"
- "what should we do about [competitor]'s new feature?"
- "who are our indirect competitors?"
- "find gaps in [competitor]'s product"

This skill covers the full lifecycle: competitor identification, ongoing monitoring, sentiment analysis, battlecard creation, and response playbooks.

## Prerequisites

- **GitHub CLI (`gh`)** installed and authenticated for repo monitoring commands
- **PowerShell** as the primary shell on Windows host
- Access to a social listening / monitoring tool (e.g., Mention, Brandwatch, or similar) for sentiment tracking
- Optional: `npm` or `pip` for package download trend monitoring
- Optional: Archive.org access for historical website/pricing snapshots

## Procedure

### 1. Identify Competitors

Classify competitors into four categories:

**Direct Competitors:**
- Same category, same target developer
- Solve the same core problem
- Would appear in the same "best X tools" lists
- Example: If you're a CI/CD tool, other CI/CD tools

**Indirect Competitors:**
- Adjacent categories that overlap with your use case
- Might be expanding into your space
- Developers might use instead of your category
- Example: GitHub Actions competing with standalone CI tools

**DIY Alternatives:**
- Open source tools developers self-host
- Custom scripts and internal tooling
- "Just use bash scripts" or "build it yourself"
- Often your biggest competitor by volume

**Platform Alternatives:**
- Cloud provider native services (AWS, GCP, Azure equivalents)
- All-in-one platforms that include your functionality
- Enterprise suite solutions

### 2. Map the Competitive Landscape

Create a competitive landscape document with:

1. **Competitor profiles** — Company, product, target market, positioning
2. **Feature matrix** — Core features compared across competitors
3. **Pricing comparison** — Tiers, pricing model, enterprise pricing signals
4. **Strengths/weaknesses** — Honest assessment of each competitor
5. **Trajectory** — Funding, growth signals, strategic direction

### 3. Track Product and Features (Weekly/Monthly)

Monitor these signals on a recurring cadence:

- Changelog and release notes
- New feature announcements
- Pricing changes
- Integration announcements
- API changes
- SDK/library updates

**How to track:**

- Subscribe to competitor newsletters
- Follow their GitHub releases
- Monitor their Twitter/blog
- Set up monitoring alerts for `"[competitor] launch"` and `"[competitor] announces"`

**GitHub monitoring commands (PowerShell):**

```powershell
# Track competitor repo activity
gh api repos/[competitor]/[repo] --jq '.stargazers_count, .open_issues_count'

# Search for competitor mentions in issues
gh search issues "[competitor]" --limit 50
```

### 4. Track Pricing and Packaging

**Key signals:**
- Pricing page changes (use archive.org to track history)
- New tier introductions
- Enterprise/custom pricing signals
- Free tier changes
- Usage-based vs seat-based shifts

**Competitive pricing intelligence questions:**
- What's included in free tier?
- Where are the upgrade triggers?
- How do they handle overages?
- What's the enterprise motion?

### 5. Track Positioning and Messaging

**Track changes in:**
- Homepage headline and hero
- "Who it's for" positioning
- Primary use cases emphasized
- Comparison pages (how they position against others)
- Case studies and social proof

**Analyze:**
- What problem do they lead with?
- What audience are they targeting?
- What's their unique angle?
- How are they different from 6 months ago?

### 6. Track Content Strategy

**Monitor:**
- Blog post frequency and topics
- Documentation quality and coverage
- Video/tutorial content
- Conference talks and sponsorships
- Developer education initiatives

**Look for:**
- SEO plays (what keywords are they targeting?)
- Content gaps you can exploit
- Successful content formats to learn from

### 7. Track Community and Traction

**GitHub signals:**
- Stars/forks growth rate
- Issue volume and response time
- Contributor growth
- Release frequency

**Community signals:**
- Discord/Slack member counts
- Forum activity
- Stack Overflow tag activity
- Reddit mention frequency

**npm/PyPI monitoring:**
- Track download trends for competitor packages
- Monitor version release frequency
- Watch for new packages in their ecosystem

### 8. Monitor Developer Sentiment

Set up alerts in your social listening tool for:

- Competitor brand mentions
- Negative sentiment toward competitors (opportunity signals)
- Comparison queries (`"[competitor] vs"`)

**Churn signals to watch for:**
- "Migrating away from [competitor]"
- "Looking for [competitor] alternative"
- "Frustrated with [competitor]"
- "Canceling [competitor]"

**Praise signals (learn from them):**
- "Love [competitor]'s [feature]"
- "[Competitor] just works"
- "Best part of [competitor] is..."

**Feature gap signals:**
- "Wish [competitor] had..."
- "[Competitor] doesn't support..."
- "Waiting for [competitor] to add..."

**Sentiment trend analysis (90-day window):**
- Mention volume for competitors over 90 days
- Sentiment distribution: positive vs negative
- Co-mentions where competitor and your brand appear together

### 9. Build Competitive Battlecards

Create battlecards for sales and marketing teams using this structure:

**1. Competitor Overview**
- Company background
- Target market
- Key value proposition
- Recent news/trajectory

**2. When We Win**
- Scenarios where you have advantage
- Customer types that prefer you
- Use cases you excel at
- Proof points and case studies

**3. When We Lose**
- Scenarios where competitor has advantage
- What to watch out for
- How to mitigate their strengths

**4. Common Objections**
- "But [competitor] has [feature]"
- "[Competitor] is cheaper"
- "[Competitor] is more established"
- Response frameworks for each

**5. Competitive Differentiation**
- Key technical differences
- Pricing comparison
- Support/service differences
- Community/ecosystem differences

**6. Landmines to Set**
- Questions to ask that favor you
- Requirements that highlight your strengths
- Evaluation criteria that matter

### 10. Keep Battlecards Fresh

**Update triggers:**
- Competitor launches major feature
- Competitor changes pricing
- You ship something that changes the comparison
- Sales team reports new objections
- Win/loss analysis reveals new patterns

**Review cadence:**
- Major competitors: monthly review
- Minor competitors: quarterly review
- Emerging competitors: as needed

### 11. Respond to Competitor Moves

**Always respond when:**
- Competitor makes false claims about you
- Competitor targets your specific customers
- Major market shift that affects positioning

**Consider responding when:**
- Competitor launches feature you have
- Competitor enters your core market
- Competitor's crisis creates opportunity

**Usually don't respond when:**
- Minor feature parity announcements
- Competitor's internal issues (unless affects their customers)
- Petty competitive shots

**Feature launch response playbook:**
1. Assess: Do we have parity? Better? Gap?
2. Internal communication to sales/support
3. Update battlecards if needed
4. Consider content response (blog, comparison page update)
5. Monitor developer conversations for context

**Pricing change response playbook:**
1. Analyze impact on competitive positioning
2. Update pricing comparison materials
3. Brief sales team
4. Consider if pricing adjustment needed
5. Monitor churn/acquisition impact

**Crisis opportunity response playbook:**
1. Don't be sleazy or pile on
2. Be helpful to affected users if appropriate
3. Create migration content if there's genuine demand
4. Let your product speak for itself

## Examples

### Social Listening Alert Patterns

Set up these alert queries in your monitoring tool:

- Competitor sentiment overview (last 30 days, by sentiment)
- Churn signals: `"alternative OR migrating OR switching" + [competitor name]`
- Feature gaps: `"wish OR need OR missing" + [competitor name]`
- Comparison mentions: `"[competitor] vs"`

### GitHub Repo Snapshot (PowerShell)

```powershell
# Get star count and open issues for a competitor repo
gh api repos/competitor-org/competitor-repo --jq '.stargazers_count, .open_issues_count'

# Search for recent issues mentioning the competitor
gh search issues "competitor-name" --limit 50
```

### Archive.org for Pricing History

1. Navigate to `https://web.archive.org/web/*/https://competitor.com/pricing`
2. Compare snapshots from 6 months ago vs today
3. Document tier changes, price increases/decreases, and feature re-packaging

## Pitfalls

- **Tracking too many competitors** — Focus on 3–5 direct competitors plus 2–3 indirect. Diluting attention across 20 competitors means none are tracked well.
- **Ignoring DIY alternatives** — "Just build it yourself" is often the largest competitor by volume for developer tools. Don't skip this category.
- **Stale battlecards** — Battlecards that are 6 months old are worse than no battlecard because they create false confidence. Follow the review cadence.
- **Confirmation bias in sentiment analysis** — Don't only collect negative sentiment about competitors. Track praise signals too — they reveal what you should learn from.
- **Overreacting to minor feature parity** — Not every competitor feature launch warrants a response. Reserve responses for moves that materially affect positioning.
- **Sleazy crisis exploitation** — When a competitor has an outage or crisis, piling on damages your brand. Be helpful, not opportunistic.
- **Not verifying GitHub CLI auth** — `gh` commands will fail silently or with confusing errors if not authenticated. Run `gh auth status` first.
- **Forgetting platform alternatives** — Cloud-native services (AWS, GCP, Azure) are often the real competition for enterprise deals, not other startups.

## Verification

1. **GitHub CLI is authenticated:**

```powershell
gh auth status
```

Expected output: `Logged in to github.com as [username]`

2. **Competitor repo data is accessible:**

```powershell
gh api repos/[competitor]/[repo] --jq '.stargazers_count'
```

Expected: A numeric value (e.g., `15423`)

3. **Battlecard completeness check** — Verify each battlecard contains all 6 sections: Overview, When We Win, When We Lose, Common Objections, Competitive Differentiation, Landmines to Set.

4. **Monitoring alerts are active** — Confirm your social listening tool shows results for each competitor alert query within the last 7 days.

5. **Pricing snapshot exists** — Confirm you have at least one Archive.org snapshot of each major competitor's pricing page saved for historical comparison.

## Related Skills

- **developer-listening** — Broader monitoring beyond just competitors
- **alternatives-pages** — Turn competitive intelligence into content
- **positioning** — Differentiate based on competitive insights

## Limitations

- Use this skill only when the task clearly matches its upstream source and local project context.
- Verify commands, generated code, dependencies, credentials, and external service behavior before applying changes.
- Do not treat examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
