# AgentSkills Project Onboarding Checklist

## Repo Inspection

- Language/framework/package files
- Build, lint, test, and typecheck commands
- CI and release workflow
- Deployment or hosting files
- Existing docs and onboarding material
- Existing agent instruction files
- Existing skills or `.agents/skills` directory
- MCP or browser-testing needs
- Sensitive areas: auth, billing, customer data, production, secrets

## Profile Selection

- Main repo workflow: frontend, backend, game, docs, support, product, data,
  devops, business analysis, revenue, creator, or mixed
- Best matching skillset
- Atomic skills that are useful without a full bundle
- Skills or bundles to avoid because they are too broad
- Project-scope versus user-scope rationale
- MCP presets needed, if any

## Common Profile Map

| Repo signals | Focused recommendation |
|---|---|
| React, Next.js, Vite, Tailwind, browser UI, design QA | `frontend-product`; add `quality-testing` only when broader release coverage is needed |
| Express, FastAPI, Rails, Django, API contracts, auth, database schemas | `backend-api`; add `engineering-delivery` for issue planning and PR/release review |
| CI, containers, deployment files, environment config, release runbooks | `devops-cloud-release`; add `quality-testing` for release test planning |
| Library, SDK, docs site, README/API docs, migration notes | `technical-documentation`; add `engineering-delivery` if code changes are in scope |
| Product feedback, PRDs, roadmap discovery, user research | `product-research`; add `business-analysis` when stakeholder requirements or BRDs are central |
| Stakeholder process notes, BRDs, business rules, implementation handoff | `business-analysis`; add `acceptance-criteria-mapper` if only testability is missing |
| Support queue, KB, escalation, account health | `support-success`; avoid revenue bundles unless sales/account expansion is explicitly in scope |
| GTM site, outbound, campaign, pipeline, pricing, lifecycle | `revenue-growth`; use `sales-marketing` only for broader mixed marketing work |
| Metrics, dashboards, funnels, cohorts, retention, SQL analysis | `data-analytics-bi`; add `analytics-finance` for KPI narratives or finance close work |
| Game source, Phaser, Three.js, assets, playtesting, itch.io | `game-dev`; use `html5-game-publishing` when browser packaging/publishing is the main job |
| Unknown or mixed repo | Recommend 3-8 atomic skills first, then promote to a skillset after real tasks recur |

Avoid installing multiple overlapping skillsets on the first pass unless the
repo clearly has multiple durable work modes.

## Project Instructions

- Preserve existing instructions and add a focused AgentSkills section.
- Name installed skillsets or skills explicitly.
- Include only routing that should apply in this repo.
- Include local validation commands discovered from repo files.
- Include review gates for risky work.
- Link to longer docs instead of copying them into `AGENTS.md`.

## Verification

- Run installer dry run when available.
- Confirm selected skills are present in the intended scope.
- Use a small trigger prompt that should activate one selected skill.
- Confirm the agent reads project instructions from the repo root.
- Record rollback steps for files and installed skills.
