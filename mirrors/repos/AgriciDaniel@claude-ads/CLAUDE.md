# Claude Ads: Paid Advertising Audit & Optimization Skill

## Project Overview

This repository contains **Claude Ads**, a Tier 4 Claude Code skill for comprehensive
paid advertising analysis across all major platforms. It follows the Agent Skills open
standard and the 3-layer architecture (directive, orchestration, execution). 22 sub-skills,
10 agents (6 audit + 4 creative), and 12 industry templates cover Google, Meta, YouTube, LinkedIn,
TikTok, Microsoft, Apple, and Amazon Ads with 250+ weighted audit checks, plus cross-platform
attribution and server-side tracking deep dives.

## Architecture

```
claude-ads/
  CLAUDE.md                          # Project instructions (this file)
  ads/                               # Main orchestrator skill
    SKILL.md                         # Entry point, routing table, core rules
    references/                      # On-demand knowledge files (25 files)
  scripts/                           # Python execution scripts (repo root; installed under <SKILL_BASE>/ads/scripts/)
  skills/                            # 22 specialized sub-skills (Wave 2)
    ads-audit/SKILL.md              # Full multi-platform audit
    ads-google/SKILL.md             # Google Ads deep analysis (incl. AI Max)
    ads-meta/SKILL.md               # Meta/Facebook Ads (Andromeda + GEM + Lattice + Entity-ID predictor)
    ads-youtube/SKILL.md            # YouTube Ads (Demand Gen, Shorts, CTV)
    ads-linkedin/SKILL.md           # LinkedIn Ads analysis
    ads-tiktok/SKILL.md             # TikTok Ads (post-USDS)
    ads-microsoft/SKILL.md          # Microsoft/Bing Ads analysis
    ads-apple/SKILL.md              # Apple Ads (AdAttributionKit, dual attribution)
    ads-amazon/SKILL.md             # Amazon Ads (Sponsored Products/Brands/Display, ACOS/TACOS)
    ads-attribution/SKILL.md        # Cross-platform attribution audit
    ads-server-side-tracking/SKILL.md # sGTM, CAPI Gateway, dedup, hashing
    ads-creative/SKILL.md           # Creative quality + Entity-ID retrieval scoring
    ads-landing/SKILL.md            # Landing page analysis
    ads-budget/SKILL.md             # Budget allocation optimization
    ads-plan/SKILL.md               # Strategic ad planning by industry
    ads-competitor/SKILL.md         # Competitor ad research
    ads-math/SKILL.md               # PPC financial calculator
    ads-test/SKILL.md               # A/B test design
    ads-dna/SKILL.md                # Brand DNA extraction
    ads-create/SKILL.md             # Campaign concepts and copy briefs
    ads-generate/SKILL.md           # AI ad image generation
    ads-photoshoot/SKILL.md         # Product photography in 5 styles
  agents/                            # 10 agents (6 audit + 4 creative)
    audit-google.md                # Google Ads audit agent
    audit-meta.md                  # Meta Ads audit agent
    audit-creative.md              # Creative quality agent
    audit-tracking.md              # Conversion tracking agent
    audit-budget.md                # Budget analysis agent
    audit-compliance.md            # Compliance verification agent
    creative-strategist.md         # Campaign concept strategist
    visual-designer.md             # AI image generation orchestrator
    copy-writer.md                 # Headlines, CTAs, primary text
    format-adapter.md              # Asset dimension validation
  tests/                             # 41-test pytest eval harness (Wave 2)
    conftest.py                    # Shared fixtures
    fixtures/check-catalog.yaml    # 209-check canonical catalog
    routing/                       # Trigger → skill snapshot tests
    audit/                         # Catalog coverage + scoring math tests
    scripts/                       # SSRF + sanitize_error regression tests
  install.sh / install.ps1          # Cross-platform installers
  uninstall.sh / uninstall.ps1      # Cross-platform uninstallers
```

## Commands

| Command | Purpose |
|---------|---------|
| `/ads audit` | Full multi-platform audit with 6 parallel agents (Wave 2 sub-skills run standalone; see notes) |
| `/ads google` | Google Ads deep analysis (incl. AI Max) |
| `/ads meta` | Meta/Facebook Ads analysis (Andromeda + GEM + Lattice) |
| `/ads youtube` | YouTube Ads analysis |
| `/ads linkedin` | LinkedIn Ads analysis |
| `/ads tiktok` | TikTok Ads analysis |
| `/ads microsoft` | Microsoft/Bing Ads analysis |
| `/ads apple` | Apple Ads (AdAttributionKit, dual attribution) |
| `/ads amazon` | Amazon Ads (Sponsored Products/Brands/Display, ACOS/TACOS) — *Wave 2* |
| `/ads attribution` | Cross-platform attribution audit (AAK, GA4, Consent Mode V2, MMP) — *Wave 2* |
| `/ads tracking` | Server-side tracking pipeline audit (sGTM, CAPI Gateway, dedup, hashing) — *Wave 2* |
| `/ads creative` | Creative quality and fatigue assessment |
| `/ads landing` | Landing page conversion analysis |
| `/ads budget` | Budget allocation optimization |
| `/ads plan <type>` | Strategic ad planning by industry |
| `/ads competitor` | Competitor ad research |
| `/ads math` | PPC financial calculator (CPA, ROAS, break-even, LTV:CAC) |
| `/ads test` | A/B test design (hypothesis, significance, sample size) |
| `/ads report` | PDF audit report generation for client deliverables |
| `/ads dna <url>` | Extract brand DNA from website → `brand-profile.json` |
| `/ads create` | Generate campaign concepts + copy briefs → `campaign-brief.md` |
| `/ads generate` | Generate AI ad images from brief → `ad-assets/` |
| `/ads photoshoot` | Product photography in 5 styles |

## Development Rules

- Keep SKILL.md files under 500 lines / 5000 tokens
- Reference files should be focused; aim for under 350 lines. Split when a
  single reference exceeds that and starts mixing concerns
- Scripts must have docstrings, CLI interface, and JSON output
- Follow kebab-case naming for all skill directories
- Agents invoked via Task tool with `context: fork`, never via Bash
- No hardcoded credentials; use MCP servers for external API access

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://agricidaniel.com/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.
