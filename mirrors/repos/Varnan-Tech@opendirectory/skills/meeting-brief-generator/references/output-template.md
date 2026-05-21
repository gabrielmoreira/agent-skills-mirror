# Output Template

One template. The brief format is fixed. Replace every [BRACKETED SLOT] with content from Tavily results. Never leave bracket text in the output. Skip a slot with "Limited public information found" if no data exists for it.

---

## Template

```markdown
# Meeting Brief: [COMPANY NAME] — [MEETING DATE]

Meeting type: [MEETING TYPE or "Not specified"]
Contact: [CONTACT NAME, TITLE or "Not specified"]

---

## Company Snapshot

[One sentence: what the company does, founded year, HQ, size, funding stage. Source URL in parentheses.]

---

## Recent News

[Bullet 1: Event + why it matters for the call. Source URL.]
[Bullet 2: Event + why it matters. Source URL.]
[Bullet 3: Event + why it matters. Source URL.]

(If no news found in the last 30 days, write: "No news found in the last 30 days.")

---

## Decision Maker

[NAME]: [Title], [tenure at company]. [One background fact: prior company, area of focus, or notable work]. ([Source URL])

(If no contact provided, write: "Not specified.")

---

## Tech Stack Signals

- [Tool or platform] — spotted in [source: job posting / engineering blog / GitHub / BuiltWith] ([URL])
- [Tool or platform] — spotted in [source] ([URL])

(If nothing found, write: "No public tech stack data found.")

---

## Competitive Context

- vs. [Competitor 1]: [One observable difference or weakness] ([URL])
- vs. [Competitor 2]: [One observable difference] ([URL])

---

## Talking Points

- Because [specific finding from research], mention [your point] to [goal for the conversation].
- Because [specific finding], mention [point] to [goal].
- Because [specific finding], mention [point] to [goal].

---

## Open Questions

- [Question specific to this company]? (based on [finding and source])
- [Question specific to this company]? (based on [finding and source])
- [Question specific to this company]? (based on [finding and source])
```

---

## Worked Example

Company: Acme Corp (acmecorp.io)
Contact: Jordan Lee, VP Engineering
Meeting date: 2026-04-15
Meeting type: Discovery

```markdown
# Meeting Brief: Acme Corp — 2026-04-15

Meeting type: Discovery
Contact: Jordan Lee, VP Engineering

---

## Company Snapshot

Acme Corp builds Kubernetes observability tooling for platform engineering teams, founded 2019, headquartered in San Francisco, 120 employees, Series B ($28M led by Bessemer Venture Partners, January 2026). ([TechCrunch](https://techcrunch.com/acme-series-b))

---

## Recent News

- Raised $28M Series B in January 2026 to expand enterprise sales and double engineering headcount. ([TechCrunch](https://techcrunch.com/acme-series-b))
- Posted 12 backend engineering roles focused on Go and distributed systems in March 2026. ([Acme Careers](https://acmecorp.io/careers))
- Published an engineering blog post on migrating their internal monolith to microservices. ([Acme Blog](https://acmecorp.io/blog/microservices))

---

## Decision Maker

Jordan Lee: VP Engineering, joined Acme Corp in 2023. Previously Staff Engineer at Datadog for 4 years, focused on metrics ingestion pipelines. Active on LinkedIn writing about platform engineering and internal developer platforms. ([LinkedIn](https://linkedin.com/in/jordan-lee))

---

## Tech Stack Signals

- Kubernetes — core product is built on top of it; mentioned in all job postings ([Acme Careers](https://acmecorp.io/careers))
- Go — primary backend language, referenced in 12 open engineering roles ([Acme Careers](https://acmecorp.io/careers))
- Prometheus — mentioned in engineering blog as current metrics stack ([Acme Blog](https://acmecorp.io/blog/microservices))
- AWS — referenced in infrastructure job descriptions ([Acme Careers](https://acmecorp.io/careers))

---

## Competitive Context

- vs. Datadog: Acme focuses specifically on Kubernetes-native observability vs Datadog's broader APM suite; Acme markets on lower cost and fewer agents to deploy. ([G2 Comparison](https://g2.com/compare/acme-vs-datadog))
- vs. Grafana: Grafana requires more manual setup; Acme's value prop is opinionated defaults for platform teams. ([Acme Blog](https://acmecorp.io/blog/vs-grafana))

---

## Talking Points

- Because Acme raised a Series B in January and posted 12 backend engineering roles, mention your enterprise onboarding package to understand their scaling timeline and whether they are building infrastructure ahead of the hire or after.
- Because their engineering blog describes a recent monolith-to-microservices migration, mention your service mesh observability features to open a conversation about how they are currently tracking latency across services.
- Because Jordan Lee previously worked at Datadog, mention your pricing model comparison to acknowledge they have deep familiarity with enterprise observability tooling and will ask sharp questions about cost.

---

## Open Questions

- With 12 open backend roles and a Series B closed in January, what does the engineering headcount look like 12 months from now? (based on Acme Careers page and TechCrunch funding report)
- The engineering blog mentions the microservices migration is ongoing. How are service-to-service latency and error rates currently tracked? (based on Acme Blog post on microservices)
- Jordan came from Datadog. What gaps in the current observability setup prompted the search for a new tool? (based on LinkedIn profile and Acme's founding story)
```

---

## Fill-In Rules

1. Replace every [BRACKETED SLOT] with content from Tavily results
2. Never leave bracket text in the output
3. Source every claim with a URL in parentheses
4. Skip sections with no data using "Limited public information found" or "Not specified"
5. Talking points must follow the "Because/mention/to" formula exactly
6. Open questions must reference a specific finding in parentheses
7. Word count must stay under 400 words
