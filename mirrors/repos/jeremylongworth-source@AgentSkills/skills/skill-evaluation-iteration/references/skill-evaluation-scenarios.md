# Skill Evaluation Scenarios

Use these scenarios to test whether the skillset routes correctly and produces useful outputs. Do not use all scenarios every time; choose the smallest set that covers the suspected gap.

## Game Development

### Browser Game Build

Prompt: "Build a small browser game I can publish on itch.io. I want a 2D arcade loop with a polished HUD and pay-what-you-want support."

Expected routing:

- `product-brainstorming-planning` if the concept is vague
- `game-skill-orchestration`
- `game-phaser-development`
- `game-content-design`
- `game-ui-design`
- `game-sound-design`
- `itch-html5-game-publishing`

Quality bar:

- Defines player-facing loop, controls, scoring, failure/retry, HUD, browser QA, and itch.io package/page requirements.
- Avoids jumping straight to code when the core loop is undefined.

### 3D Performance And Assets

Prompt: "My Three.js prototype runs slowly on mobile after I added animated GLB enemies and postprocessing. Audit it."

Expected routing:

- `game-threejs-development`
- `react-next-performance-optimization` only if a React/Next shell is involved
- `game-3d-asset-design`
- `game-3d-model-design`
- `visual-ui-ux-audit` if browser screenshots/interactions matter

Quality bar:

- Requests or gathers performance evidence before changes.
- Checks renderer settings, asset weight, draw calls, texture memory, animation mixers, postprocessing, device pixel ratio, and mobile viewport behavior.

### Playtest Readiness

Prompt: "I think my tutorial level is confusing. Help me plan a playtest and decide what to change."

Expected routing:

- `game-playtesting-usability`
- `game-content-design`
- `game-ui-design`
- `customer-research-validation` if player motivation or audience fit is unknown

Quality bar:

- Defines research question, participant criteria, tasks, observation plan, evidence capture, severity, synthesis, and retest criteria.

## Sales And Marketing

### GTM Strategy

Prompt: "We are launching a B2B SaaS tool for small agencies. Build a 90-day sales and marketing plan."

Expected routing:

- `growth-strategy-orchestration`
- `marketing-positioning-strategy`
- `customer-research-validation`
- `competitive-market-research`
- `content-seo-strategy`
- `sales-prospecting-outreach`
- `marketing-analytics-attribution`

Quality bar:

- Defines ICP, buying context, positioning, funnel, channels, metrics, experiments, and 30/60/90-day plan.
- Flags evidence gaps before recommending high-cost channels.

### Paid Campaign Experiment

Prompt: "Should I test LinkedIn ads or Google Search first for an enterprise ABM offer?"

Expected routing:

- `growth-strategy-orchestration`
- `account-based-marketing`
- `paid-media-growth`
- `experiment-design-validation`
- `marketing-analytics-attribution`
- `competitive-market-research` when current market/channel evidence is needed

Quality bar:

- Compares intent, audience targeting, offer, buying committee, budget, conversion quality, measurement, and guardrails.
- Verifies current platform docs for tactical setup if specific settings are recommended.

## Frontend And Product

### UI Polish

Prompt: "This app works but feels amateur. Audit the UI and give me specific fixes."

Expected routing:

- `visual-ui-ux-audit`
- `tailwind-design-system` if Tailwind is used
- `concise-technical-writing` for final findings

Quality bar:

- Uses visual evidence when possible.
- Prioritizes findings by impact and gives concrete, scoped fixes.

### Ambiguous Feature

Prompt: "I want an AI assistant that helps users improve prompts. Help me plan it."

Expected routing:

- `product-brainstorming-planning`
- `customer-research-validation` if user need is uncertain
- `experiment-design-validation` for validation tests

Quality bar:

- Clarifies user, problem, workflow, options, MVP, acceptance criteria, and validation before implementation planning.

## Skill Quality

### Skillset Improvement

Prompt: "Improve our skills for sales demos and proposal writing."

Expected routing:

- `skill-evaluation-iteration`
- `sales-conversion-enablement`
- `concise-technical-writing`

Quality bar:

- Tests current skill behavior against realistic sales-demo/proposal scenarios.
- Patches only concrete trigger, workflow, output, routing, validation, or freshness gaps.
