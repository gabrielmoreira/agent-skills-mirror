---
type: skill
lifecycle: stable
inheritance: master-only
name: store-adoption
description: Fetch plugin store updates, inventory contents, match against fleet profile, and generate adoption candidates report
tier: standard
applyTo: '**/*store*,**/*adopt*,**/*plugin*,**/*candidate*'
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# Store Adoption

Fetch updates from all 4 plugin stores, inventory their contents, and generate a ranked list of adoption candidates matched against the fleet's needs.

## When to Use

- Monthly cadence: run as part of the Brain Retraining Cadence
- When a new heir is added to the fleet (new needs to match)
- When a store gets a significant update (new category of plugins)
- On demand via `/scan-stores`

## Inputs

- **Fleet profile** (`fleet/fleet-profile.json`) — each heir's domain, stack, and needs
- **Portfolio intelligence** (refreshed daily by AlexFleetPortfolio):
  - `AlexFleetPortfolio/repos/repo-analysis.json` — descriptions, languages, topics for all 69 repos
  - `AlexFleetPortfolio/repos/repo-classification.json` — AI-classified categories (9 categories, tiers)
  - `AlexFleetPortfolio/repos/traffic-latest.json` — view/clone activity (signals active repos)
- **4 plugin stores** (local clones at `C:\Development\`):
  - `.github-private` (production, 37 plugins)
  - `copilot-plugins` (official GitHub)
  - `awesome-copilot` (community)
  - `playground` (staging, 800+)

## Process

### Step 1 — Fetch and inventory (mechanical)

```bash
node scripts/store-sync.cjs
```

This does three things:
1. **Pulls AlexFleetPortfolio** — gets the latest daily-refreshed repo data (descriptions, topics, languages, classifications, traffic)
2. **Pulls all 4 plugin stores** — gets latest plugin additions
3. **Writes outputs**:
   - `fleet/store-inventory.json` + `fleet/STORE-INVENTORY.md` — plugin tables
   - `fleet/portfolio-snapshot.json` — repo-analysis + repo-classification snapshot from AlexFleetPortfolio

Use `--skip-fetch` to inventory without pulling (offline mode).

### Step 2 — Semantic matching (AI)

Read `fleet/STORE-INVENTORY.md` and `fleet/fleet-profile.json`. For each store (production first, then official, community, playground):

1. Scan the plugin descriptions in the inventory table
2. For each plugin, assess: **does this plugin's purpose match any heir's domain, mission, or stated needs?**
3. Weight by relevance: a healthcare plugin is relevant to the `health` heir, not to `job`
4. Filter out Microsoft-internal tools that require internal infrastructure (ICM, ADX clusters, CloudMine, etc.)
5. Flag plugins that serve multiple heirs (cross-cutting capabilities)

Present the top candidates as:

```markdown
| Plugin | Store | Why | Heirs served | Components |
| --- | --- | --- | --- | --- |
| deep-review | production | Adversarial code review — all heirs benefit | all | 1 skill, 3 agents |
```

### Step 3 — Triage candidates

Apply the same judgment as Mall store-evaluation:

| Signal | Action |
| --- | --- |
| Production store + matches 3+ heirs | Strong candidate — evaluate for Mall promotion |
| Official store + matches domain need | Good candidate — install to specific heirs |
| Community + high star count | Worth reviewing — quality varies |
| Playground + niche domain | Only if specific heir needs it urgently |

### Step 4 — Route approved candidates

| Destination | When |
| --- | --- |
| **Mall** (`Alex_Skill_Mall`) | Skill is domain-general, would serve multiple heirs |
| **Heir local/** | Plugin serves one specific heir's niche |
| **Edition baseline** | Plugin is universally useful (rare — must pass skill-review gates) |
| **Defer** | Not needed now, log in `decisions/curation-log.md` |

### Step 5 — Update fleet profile

After installing candidates, update `fleet-profile.json`:
- Remove satisfied needs from heir entries
- Add newly discovered needs surfaced during review

## Outputs

| File | Content |
| --- | --- |
| `fleet/store-inventory.json` | Structured plugin inventory (names, counts, README excerpts) |
| `fleet/STORE-INVENTORY.md` | Markdown tables for AI semantic search |
| `fleet/fleet-profile.json` | Updated after triage (manual step) |

## Keeping the Profile Current

The fleet profile is the matching input. Keep it accurate:

- When a new heir is registered, add its entry with domain, stack, needs
- When an heir installs Mall skills, remove those needs
- When the fleet's mission shifts (new project domain), update domain_summary
- Run `node scripts/store-sync.cjs` monthly to refresh candidates

## Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| Installing every candidate | Apply the selection filter — most candidates are noise |
| Skipping production store | Production has the highest quality bar — check it first |
| Updating profile after install but not after retirement | Dead heirs inflate the needs signal |
| Running without fetching | Stale stores produce stale candidates — always fetch first |
