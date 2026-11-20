# Reckon SEO Autopilot Skills

These skills define reusable specialist behavior for Reckon SEO Autopilot. Agents compose
skills dynamically with typed contracts, least-privilege tools and evaluation requirements.

## Composition

An agent run must declare:

- Agent definition and purpose
- One or more skill files
- Authorized tools
- Model and budget policy
- Bounded steps and timeout
- Typed inputs and outputs
- Required evidence
- Evaluation, security and failure rules
- Tenant, user, website, task and policy attribution

## Categories

- `research/`: keyword, competitor, intent and SERP research
- `technical_seo/`: crawl, indexability, schema and performance
- `content/`: content audits, optimization, authority and briefs
- `on_page/`: page optimization, internal links and metadata
- `off_page/`: backlink and link-quality analysis
- `execution/`: WordPress/CMS, browser automation, verification and rollback
- `analytics/`: Search Console, performance and opportunities
- `governance/`: prompt defense, approval, tenancy, compliance and cost
- `reporting/`: reporting and recommendation prioritization
- `product/`: solution product, UX, SaaS and implementation knowledge

Skills are guidance for deterministic and agent-assisted work. They must not grant tools or
bypass the central policy engine.
