# Skill Forge

An extension Skill built on top of the BrowserAct CLI. **Let AI write your scrapers — explore once, reuse forever.**

## What It Solves

Every time you ask an agent to scrape a new site, it starts from scratch:
- Different execution path each time
- Different failure modes
- Unreliable at scale
- Token cost grows linearly with each call

**Skill Forge separates "exploring a site" from "using a site":**

> Explore once to generate a deploy-ready Skill package. 500 or 5,000 records all run through the same stable path.

Scraping teams move from "build a scraper per request" to "run a platform that lets agents self-serve Skill generation."

## Install

Skill Forge is an extension separate from the BrowserAct entry Skill. Install it on its own.

### Agent Integration (Recommended)

Tell your AI agent:

> Install browser-act-skill-forge. Skill source: https://github.com/browser-act/skills/tree/main/browser-act-skill-forge . Verify it works after installation.

The agent handles Skill configuration and validates it.

### Prerequisites

- BrowserAct CLI installed (see [Installation](installation.md))
- BrowserAct entry Skill installed

## How It Works: A Four-Step Pipeline

```
Describe → Explore → Generate → Self-Test
```

| Step | What it does |
|------|--------------|
| **01 · Describe** | Tell the agent what you want |
| **02 · Explore** | API-first, DOM as fallback |
| **03 · Generate** | Parameterized Skill package |
| **04 · Self-test** | End-to-end validation + self-repair |

### Step 01 · Describe

Tell the agent in natural language what data you need and how you'll use it:

> "Pull title, company, salary, and URL from LinkedIn job postings. I'll run 300 keywords later."

### Step 02 · Explore: API-First, DOM Fallback

The agent automatically discovers the implementation path:

| Priority | Method | Stability |
|----------|--------|-----------|
| 1 | **API-first** — endpoint discovery via network capture | 10× more stable |
| 2 | **DOM fallback** — element extraction | Affected by site redesigns |

API paths keep working as long as the backend contract holds. DOM paths require re-exploration after a redesign.

### Step 03 · Generate: Parameterized Skill Package

Business variables become CLI arguments (not hard-coded):

```bash
# The generated Skill takes parameterized inputs
forged-skill linkedin-jobs --keyword "AI Engineer" --location "Remote"
forged-skill linkedin-jobs --keyword "Backend" --location "SF"
```

Output:
- `SKILL.md` — Skill file
- Executable script
- Deploy-ready

### Step 04 · Self-Test: End-to-End Validation + Self-Repair

A sub-agent runs tests automatically and self-repairs on failure until it passes — no manual intervention needed.

## Business Value

### For Individual Developers

- Pay the exploration cost once, reuse cheaply forever
- When a site redesigns, just tell the agent to re-explore
- Token cost shifts from "pay per call" to "pay once at exploration"

### For Scraping Teams

Traditional model:

```
Request → engineer codes scraper → test → deploy → maintain
            ↑                                    ↑
            takes requests                       breaks on redesign
```

Skill Forge model:

```
Request → agent explores and generates Skill → self-tests → deploy
                                                              ↑
                                                          re-explore on redesign
```

Engineers move from "writing every scraper" to "running the platform agents use to self-serve Skill generation."

## Use Cases

| Scenario | Description |
|----------|-------------|
| **Batch data collection** | Same pattern across N keywords / regions / categories |
| **Cross-site comparison** | Explore each site once, generate a Skill set with a unified interface |
| **Recurring monitoring** | Price changes, inventory changes, new arrivals |
| **Data mining** | Recruiting, e-commerce, social — structured data extraction |
| **Internal enterprise flows** | Encapsulate a fixed operation in an internal system as a reusable Skill |

## Relationship to the BrowserAct Entry Skill

| | BrowserAct entry Skill | Skill Forge |
|---|---|---|
| Role | Foundation, exposes local browser CLI capabilities | Extension Skill, built on top of the CLI |
| Required | ✓ | Optional |
| Use pattern | Agent explores and operates the browser live | Agent explores once, generates a reusable Skill |
| Token cost | Pay per call | Pay once at exploration |

BrowserAct provides the "ability to do things." Skill Forge provides the "ability to bake doing into a Skill."

## Next Steps

- [Installation](installation.md) — Install the base CLI and entry Skill
- [Anti-Blocking](anti-blocking.md) — Anti-scraping capabilities Skill Forge relies on during exploration
- [Agent Design](agent-design.md) — Network capture for API endpoint discovery
