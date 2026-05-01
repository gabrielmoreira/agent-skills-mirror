---
name: toprank-portfolio-review
description: Review all registered websites in the Toprank OpenClaw portfolio and rank which site deserves attention next.
metadata: { "openclaw": { "emoji": "📊", "homepage": "https://github.com/nowork-studio/toprank", "requires": { "bins": ["python3"] } } }
---

# Toprank Portfolio Review

1. Read `{baseDir}/../../shared/adapter-rules.md`.
2. Read `{baseDir}/../../shared/artifact-contract.md`.
3. Read `{baseDir}/../../shared/policy.md`.
4. Load `portfolio.json` and each active site's `latest-state.json` from the OpenClaw runtime home.
5. Run `python3 {baseDir}/../../bin/portfolio_review.py` to get the current ranked site list and write a portfolio review artifact.
6. Read and follow the canonical Toprank skill at `{baseDir}/../../../seo/seo-analysis/SKILL.md` only for the top-ranked site(s) if you need deeper analysis.
7. If the top site needs deeper work, either launch `toprank-weekly-review` for that site or ask the operator which site to dive into.

## Wrapper job

Use this when the operator owns multiple websites and needs portfolio-level prioritization.

Your job:
- scan all active sites,
- rank them by urgency and upside,
- name the one or two sites that deserve attention now,
- create queue items or follow-up tasks for deeper site reviews.

Use business weight, visible regressions, and opportunity size when ranking the sites.
