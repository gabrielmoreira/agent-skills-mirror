---
type: skill
lifecycle: stable
inheritance: inheritable
name: supervisor
description: Complete ACT Supervisor package — fleet governance, Mall curation, release ritual, feedback triage, and cross-repo coherence for users running their own ACT Edition fleet
tier: extended
applyTo: '**/*supervisor*,**/*fleet*,**/*curation*'
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# ACT Supervisor

A complete package for running your own Supervisor instance — the curator that keeps an ACT Edition fleet healthy, the Skill Mall fresh, and cross-repo coherence intact.

## What the Supervisor Does

The Supervisor is a focused AI assistant that manages two sibling repos:

| Repo | Role | Supervisor's job |
|------|------|-----------------|
| **Alex_ACT_Edition** | Brain template — heirs deploy from here | Review skills, cut releases, triage feedback, run brain-qa |
| **Alex_Skill_Mall** | Skill marketplace consumed by heirs | Curate stores, evaluate submissions, prune stale entries |

It is **not** a fleet manager (that's the user or a Master instance), **not** a framework author (ACT tenets belong upstream), and **not** a general-purpose brain. It does two jobs and does them well.

## Architecture

```
                  ┌─────────────────────┐
                  │   You (or Master)   │
                  │  Framework author   │
                  └──────────┬──────────┘
                             │ delegates curation
                             ▼
                  ┌─────────────────────┐
                  │     Supervisor      │
                  │   (this package)    │
                  └──────┬───────┬──────┘
                         │       │
                  curates│       │maintains
                         ▼       ▼
            ┌────────────────┐  ┌────────────────┐
            │ ACT Edition    │  │  Skill Mall    │
            │ (brain repo)   │  │ (marketplace)  │
            └────────────────┘  └────────────────┘
                         │
                    deployed to
                         ▼
            ┌────────────────────────┐
            │  Heir projects (fleet) │
            └────────────────────────┘
```

## What's in This Package

### Skills (13) — the Supervisor's cognitive toolkit

| Skill | What it does |
|-------|-------------|
| `coherence-audit` | Cross-repo consistency: Edition references match Mall reality |
| `escalation-routing` | Cardinal Test: what stays in Supervisor vs escalates upstream |
| `feedback-triage` | Categorize, deduplicate, and route heir feedback |
| `fleet-announcement` | Author fleet-wide announcements via AI-Memory |
| `fleet-management` | Heir synchronization, drift detection, version stamps |
| `mall-curation` | Add, keep, refresh, or prune Mall entries |
| `release-process` | Full release automation (VS Code Marketplace pattern) |
| `release-ritual` | Preflight, brain-qa, changelog, tag, push for Edition |
| `skill-review` | Four-gate review: spec, quality, scope, safety |
| `staleness-discipline` | Detect and prune stale Mall entries |
| `store-adoption` | Evaluate external stores and adopt artifacts |
| `store-evaluation` | Five-dimension scorecard for new store proposals |
| `version-management` | Semver discipline: bump rules, breaking-change classification |

### Instructions (9) — always-on behavioral rules

Located in `supervisor-instructions/`. These fire automatically based on context:

| Instruction | When it fires |
|-------------|--------------|
| `act-self-critique` | Applying ACT to ACT itself |
| `brain-curation-rules` | Any work touching Edition |
| `escalation-rules` | Before any commit to Edition or Mall |
| `feedback-triage` | Processing heir feedback from AI-Memory |
| `mall-maintenance-rules` | Any work touching Mall |
| `release-discipline` | Cutting any Edition release |
| `release-management` | Version bumps and changelogs |
| `risk-analysis` | Curation decisions with consequences |
| `version-management` | PR classification and release tagging |

### Prompts (21) — slash commands

Located in `supervisor-prompts/`. Key commands:

| Command | Purpose |
|---------|---------|
| `/cut-release` | Cut a versioned release of Edition |
| `/triage-feedback` | Process heir feedback inbox |
| `/review-skill` | Four-gate skill review |
| `/audit-mall` | Monthly Mall health audit |
| `/audit-coherence` | Cross-repo reference check |
| `/audit-currency` | Brain file freshness review |
| `/scan-stores` | Discover skills from external stores |
| `/add-store` | Evaluate and add a new Mall entry |
| `/prune-store` | Remove stale Mall entries |
| `/fleet` | Fleet dashboard and status |
| `/review-fleet` | Fleet health review |
| `/escalate-to-master` | Route framework concerns upstream |
| `/preflight-release` | Pre-release validation |
| `/status` | Current project status |

### Scripts (9) — mechanical automation

Located in `supervisor-scripts/`. All Node.js (`.cjs`), cross-platform:

| Script | Purpose |
|--------|---------|
| `brain-qa.cjs` | Deterministic brain health checks (frontmatter, dates, schema) |
| `coherence-check.cjs` | Cross-repo reference validation |
| `fleet-dashboard.cjs` | Generate fleet status dashboard |
| `fleet-inventory.cjs` | Discover heir projects on disk |
| `mall-link-check.cjs` | HTTP HEAD every URL in Mall |
| `store-sync.cjs` | Clone/pull external plugin stores + generate inventory |
| `stores-staleness.cjs` | Flag stale stores (no commits, archived, broken) |
| `sync-from-master.cjs` | Pull shared-core instruction updates from upstream |
| `repos.config.json` | Sibling repo paths configuration |

### Identity template

Located in `supervisor-identity/`:
- `copilot-instructions.md` — Supervisor identity, mission, cardinal rules, routing
- `quarterly-retraining-ADR-template.md` — Template for quarterly brain review

## Setup Guide

### Prerequisites

- **VS Code** with GitHub Copilot Chat
- **Node.js** 18+ (for scripts)
- **Git** and **gh** CLI (for GitHub API access)
- An **ACT Edition** repo (the brain template your fleet deploys from)
- A **Skill Mall** repo (the marketplace your heirs shop from)

### Step 1: Create the Supervisor repo

```bash
mkdir Alex_ACT_Supervisor
cd Alex_ACT_Supervisor
git init
mkdir -p .github/{skills,instructions,prompts} scripts decisions fleet
```

### Step 2: Install the Supervisor brain

Copy from this Mall package into your Supervisor repo:

```bash
# Skills (core Supervisor capabilities)
cp -r <mall>/skills/supervisor/coherence-audit .github/skills/
cp -r <mall>/skills/supervisor/escalation-routing .github/skills/
cp -r <mall>/skills/supervisor/feedback-triage .github/skills/
cp -r <mall>/skills/supervisor/fleet-announcement .github/skills/
cp -r <mall>/skills/supervisor/fleet-management .github/skills/
cp -r <mall>/skills/supervisor/mall-curation .github/skills/
cp -r <mall>/skills/supervisor/release-process .github/skills/
cp -r <mall>/skills/supervisor/release-ritual .github/skills/
cp -r <mall>/skills/supervisor/skill-review .github/skills/
cp -r <mall>/skills/supervisor/staleness-discipline .github/skills/
cp -r <mall>/skills/supervisor/store-adoption .github/skills/
cp -r <mall>/skills/supervisor/store-evaluation .github/skills/
cp -r <mall>/skills/supervisor/version-management .github/skills/

# Instructions
cp <mall>/skills/supervisor/supervisor-instructions/*.md .github/instructions/

# Prompts
cp <mall>/skills/supervisor/supervisor-prompts/*.md .github/prompts/

# Scripts
cp <mall>/skills/supervisor/supervisor-scripts/*.cjs scripts/
cp <mall>/skills/supervisor/supervisor-scripts/repos.config.json scripts/

# Identity
cp <mall>/skills/supervisor/supervisor-identity/copilot-instructions.md .github/copilot-instructions.md
mkdir -p decisions/templates
cp <mall>/skills/supervisor/supervisor-identity/quarterly-retraining-ADR-template.md decisions/templates/
```

### Step 3: Configure sibling repos

Edit `scripts/repos.config.json` to point at your Edition and Mall:

```json
{
    "siblings": {
        "edition": {
            "name": "My_ACT_Edition",
            "path": "../My_ACT_Edition",
            "remote": "https://github.com/you/My_ACT_Edition.git"
        },
        "mall": {
            "name": "My_Skill_Mall",
            "path": "../My_Skill_Mall",
            "remote": "https://github.com/you/My_Skill_Mall.git"
        }
    }
}
```

### Step 4: Customize the identity

Edit `.github/copilot-instructions.md`:
- Replace repo names with yours
- Set your mission statement
- Adjust cardinal rules if your fleet has different governance
- Update the routing section for your upstream (Master or none)

### Step 5: Set up AI-Memory (optional but recommended)

AI-Memory is a shared folder (OneDrive, iCloud, Dropbox) that connects heirs to the Supervisor:

```
AI-Memory/
├── announcements/
│   └── alex-act/          # Supervisor writes, heirs read
│       └── README.md
├── feedback/
│   └── alex-act/          # Heirs write, Supervisor reads
│       └── README.md
├── notes.md               # Cross-session notes
└── user-profile.json      # Optional personal preferences
```

**Setup**:
1. Create the folder structure in your cloud storage
2. Heirs write feedback via `/feedback` prompt
3. Supervisor reads feedback via `/triage-feedback`
4. Supervisor writes announcements (upgrade notices, breaking changes)
5. Heirs read announcements on session start (greeting check-in)

The channel is **user-scoped**: each user has their own AI-Memory. There is no global fleet bus.

### Step 6: Set up external store monitoring (optional)

Clone external plugin stores for skill discovery:

```bash
mkdir -p ~/Development/MALL
cd ~/Development/MALL

# Official Microsoft skills
gh repo clone microsoft/skills microsoft-skills

# Community stores (pick what's relevant)
gh repo clone anthropics/courses anthropics-courses
gh repo clone AdrianBerger/awesome-copilot-instructions awesome-copilot
```

Then run store-sync to generate inventory:

```bash
node scripts/store-sync.cjs
```

## Key Facilities

### Brain-QA

Mechanical health checks for the Edition brain:

```bash
node scripts/brain-qa.cjs
```

Checks frontmatter schema, date freshness, missing fields, cross-references. Exit 0 = clean. Non-zero = fix before release.

### Mall Link Check

Validate every URL in the Mall:

```bash
node scripts/mall-link-check.cjs
```

### Coherence Check

Verify Edition references match Mall reality:

```bash
node scripts/coherence-check.cjs
```

### Fleet Dashboard

Generate a status dashboard of all heir projects:

```bash
node scripts/fleet-dashboard.cjs
```

### Release Ritual

Cut a release of Edition (high-stakes, full ACT pass):

1. `/preflight-release` — run all gates
2. `/cut-release` — changelog, version bump, tag, push

### Quarterly Retraining

Every quarter, review the brain against evidence:

1. Copy `decisions/templates/quarterly-retraining-ADR.md`
2. Walk the brain-qa review queue
3. Review Mall changes and heir feedback
4. Evolve the critical-thinking trifecta
5. Record decisions in the ADR

## Cadence

| Frequency | Action |
|-----------|--------|
| Weekly | `/triage-feedback` on AI-Memory inbox |
| Monthly | `/audit-mall` for staleness + `/audit-coherence` |
| Per release | `/preflight-release` then `/cut-release` |
| Quarterly | Full retraining pass (ADR template) |

## What the Supervisor Does NOT Do

- Author the ACT framework (manifesto, tenets, claims) — that's upstream
- Manage non-ACT heirs — that's the user or a Master instance
- Make direct commits to Edition — every change goes through PR review
- Store PII in AI-Memory — filtered per `pii-memory-filter`
- Override heir customizations — heirs own their `local/` paths

## Token Budget

Target: 25K tokens. If the Supervisor brain grows past that, it has scope-crept. The Edition brain is 60K+; the Supervisor must stay lean.

## Related

- [Alex_ACT_Edition](https://github.com/fabioc-aloha/Alex_ACT_Edition) — the brain template
- [Alex_Skill_Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) — the marketplace
- [ACT Manifesto](https://github.com/fabioc-aloha/Alex_ACT_Supervisor/tree/main/ACT) — the critical thinking framework
