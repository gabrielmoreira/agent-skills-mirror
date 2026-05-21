# Brief Format Guide

## Purpose

A meeting brief gives you the 3 minutes of research that makes a 30-minute call feel like you have been following this company for months. It is a reference document, not a report. Every section answers one question a prepared seller asks before a call.

---

## Structure (fixed, one template)

```
# Meeting Brief: {Company} — {Date}

## Company Snapshot
## Recent News
## Decision Maker
## Tech Stack Signals
## Competitive Context
## Talking Points
## Open Questions
```

---

## Section Rules

### Company Snapshot
One or two sentences maximum. Cover: what the company does, when it was founded, where it is based, approximate size (employees or revenue range), and funding stage if known. Cite the source URL inline.

Do not write a paragraph. One sentence per data point is enough.

Example:
- Acme Corp builds developer tooling for Kubernetes observability, founded 2019, 120 employees, Series B ($28M, Bessemer, 2024). [Source](https://example.com)

### Recent News
Last 30 days only. Three bullets maximum. Each bullet states the event and why it matters for the call.

Format: `[Event]. Source: [URL]`

Skip this section entirely if no news was found in the last 30 days. Write "No news found in the last 30 days."

Do not include news older than 30 days unless it is a major funding round within the last 90 days.

### Decision Maker
Name, title, tenure at the company, and one notable background fact (prior company, published work, area of focus). Cite sources.

If no contact was provided: write "Not specified."

Do not speculate about seniority or buying authority. Only state what research confirms.

### Tech Stack Signals
Bullet list of tools, platforms, or infrastructure visible from public sources (job postings, engineering blog, GitHub, BuiltWith-style data). Each bullet names the tool and where it was spotted.

Format: `{Tool} — spotted in {job posting / engineering blog / GitHub}`

If nothing was found: "No public tech stack data found."

### Competitive Context
Two to four bullets. Name the competitors and state one observable differentiator or weakness per competitor. Use research data, not assumptions.

Format: `vs. {Competitor}: {one observable difference}`

### Talking Points
Three to five bullets. Each follows this exact formula from the GTM playbook:

`Because [specific finding from research], mention [your point] to [goal for the conversation].`

Every talking point must trace to a specific Tavily result. Do not write a talking point without a "Because" clause grounded in research.

Examples:
- Because Acme raised a Series B in January and posted 12 backend engineering roles, mention your enterprise onboarding package to understand their scaling timeline.
- Because their engineering blog mentions a migration from monolith to microservices, mention your observability tooling to open a conversation about their infra complexity.

### Open Questions
Two to three questions specific to this company's situation. They should open discovery, not pitch. Generic questions ("What are your goals?") are not acceptable here.

Format: `{Question} (based on {finding})`

Examples:
- With the recent Series B, what is the 12-month engineering headcount plan? (based on 12 open backend roles)
- The engineering blog mentions moving to microservices last year. How is observability handled across services currently? (based on engineering blog post)

---

## Length and Format Rules

- Under 400 words total
- No paragraphs in the brief body (bullets and one-liners only)
- No em dashes anywhere
- No banned words: incredible, amazing, leveraging, game-changing, groundbreaking, pivotal, utilize, disruptive, transformative, unlock, seamless, robust
- Every claim has a source URL
- Sections with no data say "Limited public information found" or "Not specified" (never leave blank)

---

## Citation Rule

Every data point must be followed by a source URL in parentheses or as a markdown link. This is non-negotiable. If you cannot cite it, do not include it.

Acceptable: `120 employees ([LinkedIn](https://linkedin.com/company/acme))`
Not acceptable: `approximately 100-150 employees`

---

## Validation Checklist

- [ ] Under 400 words
- [ ] Every section present (or explicitly marked as "Not found")
- [ ] No em dashes
- [ ] No banned words
- [ ] Every claim has a source URL
- [ ] Talking points use "Because/mention/to" formula
- [ ] Open questions are company-specific, not generic
- [ ] Decision Maker section says "Not specified" if no contact provided
