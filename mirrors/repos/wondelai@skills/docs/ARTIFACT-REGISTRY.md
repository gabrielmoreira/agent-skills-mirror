# Metaskill Artifact Registry

Canonical skeletons for the `docs/` artifacts that the 12 metaskills (create/improve/grow × business/website/app, improve-code-quality, remove-technical-debt, design-code-architecture) create and extend in a **user's project**. This file is maintainer-facing: it prevents drift between the 12 skills. Each metaskill ships the skeletons it *creates* in its own `references/artifact-templates.md`; for artifacts it only *extends*, the section headings below are the contract.

Rules every metaskill follows:

- Artifacts are UPPERCASE, content-named, and live flat in the user's project `docs/` folder.
- Ownership is soft: the listed creator defines the skeleton, but any metaskill creates the file if missing and extends it otherwise — add or update your own sections, preserve everyone else's.
- Section headings are the cross-metaskill contract. Extend under these exact headings; add new `###` subsections rather than renaming `##` sections.
- Every recommendation lands as a checkbox or a table row with owner/priority — implementable, never essayistic.
- Each journey also maintains a private tracker `docs/<SKILL-NAME>-PLAN.md` (skeleton at the end). Trackers are never shared between journeys.

## docs/CUSTOMER.md

Who we serve and the evidence. Creates: create-business, create-app. Extends: grow-business, grow-app, improve-business, improve-app, create-website.

```markdown
# Customer

## Job Statement
When [situation], I want to [motivation], so I can [outcome].

## Job Dimensions
| Dimension | Description |
|---|---|
| Functional | |
| Emotional | |
| Social | |

## Competing Alternatives
| Alternative (incl. non-consumption) | Why hired today | Weakness |
|---|---|---|

## Interview Evidence
| Date | Who | Concrete facts (past behavior) | Commitment given |
|---|---|---|---|

## Validation Verdict
Decision (proceed / revise / stop) and reasoning.

## Segments & Best-Fit Customer
```

## docs/POSITIONING.md

How the market should understand us — positioning canvas and messaging in one file. Creates: create-business, create-website. Extends: grow-website, grow-business, improve-website, improve-app.

```markdown
# Positioning & Messaging

## Competitive Alternatives

## Unique Attributes → Value Themes
| Attribute | Value ("so what") | Proof |
|---|---|---|

## Best-Fit Customer

## Market Category
Choice (existing / subcategory / new) and rationale.

## One-Liner

## Brand Script (StoryBrand)
Character · Problem (external/internal/philosophical) · Guide · Plan · Call to action · Failure · Success.

## Key Messages
| Surface | Message | Status |
|---|---|---|
```

## docs/STRATEGY.md

How we win. Creates: create-business, improve-business. Extends: grow-business, create-app.

```markdown
# Strategy

## Diagnosis
The single critical challenge.

## Guiding Policy

## Coherent Actions
| Action | Owner | Due | Status |
|---|---|---|---|

## No-List
What we explicitly will not do.

## Strategy Canvas & ERRC Grid
| Factor | Eliminate | Reduce | Raise | Create |
|---|---|---|---|---|

## Beachhead
Target segment, scoring rationale.

## Whole-Product Checklist
- [ ] gap (owner, priority)
```

## docs/OFFER.md

What we sell and at what price. Creates: create-business. Extends: grow-business, grow-website, improve-business.

```markdown
# Offer & Pricing

## Offer Stack
| Element | Description | Honest value | Objection it kills |
|---|---|---|---|
Core offer · Bonuses · Guarantee · Scarcity/urgency (real only) · Name.

## Willingness-to-Pay Evidence
| Segment | Acceptable | Expensive | Prohibitive | Source |
|---|---|---|---|---|

## Leader / Filler / Killer Features
| Feature | Class | Tier placement |
|---|---|---|

## Tiers (Good / Better / Best)

## Price Metric
What we charge per, and why.
```

## docs/EXPERIMENTS.md

Every test we run, with pre-committed criteria. Creates: create-business, create-app. Extends: improve-website, grow-website, grow-app, create-website, improve-app.

```markdown
# Experiments

## Experiment Cards
### EXP-001 — [name]
- Hypothesis: We believe [outcome] if [who] [does what] because [reason]
- Type: sprint / smoke test / concierge / painted door / A-B
- Primary metric & threshold (pre-committed):
- Guardrail metric:
- Decision rule (pivot / persevere / iterate):
- Result & verdict:

## Experiment Backlog
| Idea | ICE (impact/confidence/ease) | Status |
|---|---|---|
```

## docs/MARKETING.md

Acquisition plan and channel playbooks. Creates: grow-business, create-website. Extends: grow-website.

```markdown
# Marketing

## Target Market & Avatar
PVP niche choice · one-paragraph avatar.

## Before / During / After Grid
| Phase | Square | Current state | Plan |
|---|---|---|---|

## Channels
| Channel | Approach | Owner | Status |
|---|---|---|---|

## Word-of-Mouth (STEPPS)
| Lever | Idea | Status |
|---|---|---|

## Outbound Process
Roles, sequences, qualification, handoff.

## Referral & Invite Mechanics

## Nurture Sequences
```

## docs/METRICS.md

What we measure and current baselines. Creates: improve-business, grow-app. Extends: grow-business, grow-website, improve-website.

```markdown
# Metrics

## Stage & One Metric That Matters
OMTM · counter-metric · why now.

## KPI Definitions
| Metric | Definition | Actionable ratio? | Owner |
|---|---|---|---|

## Baselines & Targets
| Metric | Baseline (date) | Target | Line in the sand (miss response) |
|---|---|---|---|

## Funnel
| Stage | Conversion | Benchmark | Bottleneck? |
|---|---|---|---|

## Cohort Notes
```

## docs/PRODUCT.md

What we build and why. Creates: create-app, create-business. Extends: grow-app, improve-app.

```markdown
# Product

## Vision
One paragraph.

## MVP Definition
Type, scope, what it deliberately excludes.

## Outcome Roadmap
| Outcome / problem | Job served | Priority | Status |
|---|---|---|---|

## Opportunity Solution Tree Notes

## Hook Model
Trigger → Action → Variable reward → Investment; weakest phase.

## Activation & Retention Plan
| Friction / moment | Fix | Owner | Status |
|---|---|---|---|

## Discovery Cadence
Weekly touchpoint plan.
```

## docs/OPERATIONS.md

How the company runs. Creates: improve-business. Extends: grow-business.

```markdown
# Operations

## Vision/Traction Summary
Core values · focus · 10-year/3-year/1-year picture.

## Rocks (this quarter)
| Rock | Owner | Binary done-condition | Status |
|---|---|---|---|

## Team Structure
Accountability chart / team topology; cognitive-load notes.

## Meeting Cadence
| Meeting | Rhythm | Agenda |
|---|---|---|

## Management Leverage
1:1 cadence, delegation decisions.

## Motivation (Autonomy / Mastery / Purpose)
| Lever | Finding | Fix |
|---|---|---|
```

## docs/WEBSITE.md

Site structure and page briefs. Creates: create-website. Extends: improve-website, grow-website.

```markdown
# Website

## Sitemap

## Page Briefs
### / (home)
- Purpose & primary conversion action:
- Message (from POSITIONING.md):
- CTA (direct + transitional):
- Copy blocks:

## Conversion Elements
| Objection (Big 5) | Counter | Placement | Status |
|---|---|---|---|

## Audit Findings
| Issue | Severity (0-4) | Fix | Status |
|---|---|---|---|

## Lead Capture
Scorecard/quiz funnel design.
```

## docs/DESIGN.md

Visual and interaction system. Creates: create-website, create-app. Extends: improve-website, improve-app, grow-app.

```markdown
# Design System

## Design Direction
Signature moment, personality, references.

## Typography
Typefaces, scale, measure, line height, loading strategy.

## Tokens
Spacing scale · color palette (shades, tinted grays) · shadows.

## Components
| Component | Decision | Status |
|---|---|---|

## UX Audit Findings
| Issue | Heuristic | Severity (0-4) | Fix | Status |
|---|---|---|---|---|

## Microinteraction Inventory
| Interaction | Trigger/Rules/Feedback/Loops | Fix | Status |
|---|---|---|---|
```

## docs/ARCHITECTURE.md

System structure and decisions — includes domain model and data decisions (no separate DATA.md or DOMAIN.md). Creates: design-code-architecture, create-app. Extends: remove-technical-debt, improve-code-quality.

```markdown
# Architecture

## System Context
What the system does, key integrations, load reality (back-of-envelope numbers).

## Layer Map & Dependency Rule
Layers, what depends on what, current violations.
| Violation | Location | Fix | Status |
|---|---|---|---|

## Bounded Contexts & Context Map
Contexts, relationships, anti-corruption layers.

## Domain Glossary (Ubiquitous Language)
| Term | Meaning | Code name |
|---|---|---|

## Data & Storage Decisions
Data models, storage engines, isolation levels, replication, system-of-record vs derived data.

## Decision Log
| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
```

## docs/TECH-DEBT.md

The debt ledger — single queue for all code journeys. Creates: remove-technical-debt, improve-code-quality. Extends: create-app, design-code-architecture (debt deliberately taken).

```markdown
# Technical Debt

## Debt Ledger
| Item | Location | Type | Risk | Effort | Priority | Status |
|---|---|---|---|---|---|---|

## Smell Inventory
| Smell | Location | Refactoring | Status |
|---|---|---|---|

## Sprout / Wrap Register
Code added beside legacy (to fold back in later).

## Debt Budget & Broken-Windows Policy
Time per iteration; what gets fixed now vs boarded up with a ticket.

## Adopted Conventions
```

## docs/TESTING.md

The safety net — what behavior is pinned, where the gaps are. Creates: remove-technical-debt, improve-code-quality, create-app. Extends: design-code-architecture.

```markdown
# Testing

## Test Strategy
Pyramid, tooling, what "green" gates.

## Safety Net Map
| Module | Pinned behaviors | Test files | Gaps |
|---|---|---|---|

## Characterization Backlog
- [ ] module (risk, priority)

## CI Gates
```

## docs/RELIABILITY.md

Production hardening status. Creates: improve-code-quality, design-code-architecture. Extends: remove-technical-debt.

```markdown
# Reliability

## Integration-Point Audit
| Dependency | Timeout | Circuit breaker | Bulkhead | Retry policy | Status |
|---|---|---|---|---|---|

## Query & Resource Findings
Unbounded result sets, missing LIMITs/pagination, blocked threads.

## Health Checks & Metrics
Deep health checks · RED metrics · symptom-based alerts.

## Deploy vs Release
Feature flags, expand-contract migrations, rollback plan.
```

## Tracker: docs/<SKILL-NAME>-PLAN.md

One per journey (e.g. `docs/CREATE-BUSINESS-PLAN.md`). Never shared.

```markdown
# <Journey> Plan

## Context
Intake answers, date started, project specifics.

## Phase Status
| Phase | Skill | Status | Artifact | Date |
|---|---|---|---|---|
Statuses: pending · in-progress · awaiting-evidence · done · deferred: <reason> · skipped: <reason>

## Key Decisions
| Date | Phase | Decision | Rationale |
|---|---|---|---|

## Next Actions
- [ ] action (owner, due)
```
