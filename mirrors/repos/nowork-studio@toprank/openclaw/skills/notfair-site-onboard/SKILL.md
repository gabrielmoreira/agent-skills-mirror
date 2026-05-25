---
name: notfair-site-onboard
description: Register a website in NotFair's OpenClaw adaptive layer and initialize its per-site work folder.
metadata: { "openclaw": { "emoji": "🧭", "homepage": "https://github.com/nowork-studio/notfair", "requires": { "bins": ["python3"] } } }
---

# NotFair Site Onboard

1. Read `{baseDir}/../../shared/adapter-rules.md`.
2. Read `{baseDir}/../../shared/artifact-contract.md`.
3. Read `{baseDir}/../../shared/policy.md`.
4. Gather the site URL, display name, brand terms, business weight, cadence, and one initial SEO goal.
5. Run:
   - `python3 {baseDir}/../../bin/bootstrap_workspace.py`
   - `python3 {baseDir}/../../bin/onboard_site.py <url> --display-name "..." --brand-terms "A,B" --business-weight 1.0 --cadence weekly --goal-type grow_non_brand_clicks --primary-metric non_brand_clicks_28d`
6. Read and follow the canonical NotFair skill at `{baseDir}/../../../seo/seo-analysis/SKILL.md` only if you need deeper site understanding during onboarding.
7. Confirm that `site-profile.json`, `goals.json`, and `portfolio.json` were updated.

## Wrapper job

Use this when the operator is adding a new website.

Your job:
- create or update the portfolio registry,
- initialize the site work folder,
- capture brand terms, business weight, cadence, and one initial SEO goal,
- write `site-profile.json` and `goals.json`.

If the user already has multiple sites, keep this site's state isolated under its own folder.
