# Claude Blog - Blog Creation & Optimization Skill

## Project Overview

This repository contains **Claude Blog**, a Tier 4 Claude Code skill for blog content
creation, optimization, and management. It follows the Agent Skills open standard and the
3-layer architecture (directive, orchestration, execution). 28 sub-skills, 5 specialized
subagents, and 12 content templates are dual-optimized for Google rankings (December 2025
Core Update, E-E-A-T) and AI citations (GEO/AEO). Includes FLOW framework integration,
semantic topic-cluster planning + execution, and multilingual publishing (Pro Hub Challenge
v1.7.0 community release).

## Architecture

```
claude-blog/
  CLAUDE.md                          # Project instructions (this file)
  CONTRIBUTORS.md                    # Pro Hub Challenge attribution and integration decisions
  CHANGELOG.md                       # Keep a Changelog format
  .claude-plugin/plugin.json         # Plugin manifest (v1.7.0)
  .claude-plugin/marketplace.json    # Marketplace catalog for distribution
  .mcp.json                          # MCP server configuration (nanobanana-mcp)
  pyproject.toml                     # Python packaging (3.11+)
  scripts/sync_flow.py               # Pulls FLOW references (stdlib, sandboxed)
  skills/                            # 28 sub-skills (blog/ is the orchestrator)
    blog/SKILL.md                   # Main orchestrator, routing, scoring
      references/                   # 14 on-demand knowledge files
      templates/                    # 12 content templates
      scripts/                     # Python analysis scripts
    blog-write/SKILL.md            # Write new articles from scratch
    blog-rewrite/SKILL.md         # Optimize existing blog posts
    blog-analyze/SKILL.md         # 5-category 100-point scoring
    blog-brief/SKILL.md           # Detailed content briefs
    blog-outline/SKILL.md         # SERP-informed outlines
    blog-calendar/SKILL.md        # Editorial calendars
    blog-strategy/SKILL.md        # Blog positioning and planning
    blog-seo-check/SKILL.md      # Post-writing SEO validation
    blog-schema/SKILL.md          # JSON-LD schema generation
    blog-chart/SKILL.md           # Inline SVG data visualizations
    blog-repurpose/SKILL.md       # Multi-platform repurposing
    blog-geo/SKILL.md             # AI citation optimization
    blog-audit/SKILL.md           # Full-site blog health assessment
    blog-image/                    # AI image generation via Gemini
      SKILL.md                    # Image generation sub-skill
      references/                 # 3 reference docs (models, tools, prompts)
      scripts/                    # MCP setup and validation scripts
    blog-cannibalization/SKILL.md # Keyword overlap detection
    blog-factcheck/SKILL.md       # Statistics verification
    blog-persona/SKILL.md         # Writing persona management
    blog-taxonomy/SKILL.md        # CMS taxonomy management
    blog-notebooklm/               # NotebookLM source-grounded research
      SKILL.md                    # NotebookLM query sub-skill
      references/                 # 2 reference docs (commands, troubleshooting)
      scripts/                    # 10 Python scripts + requirements.txt
    blog-audio/                    # Audio narration via Gemini TTS
      SKILL.md                    # Audio generation sub-skill
      references/                 # 1 reference doc (30 voice catalog)
      scripts/                    # 5 Python scripts + requirements.txt
    blog-google/                   # Google API integration
      SKILL.md                    # Google API sub-skill (13 commands, 4 tiers)
      references/                 # 3 reference docs (auth, API, quotas)
      scripts/                    # 11 Google API scripts + venv wrapper
      assets/templates/           # 3 report templates
    blog-cluster/                  # Semantic topic-cluster planning + execution (v1.7.0)
      SKILL.md                    # Cluster planning + execute orchestrator
      references/                 # 3 ref docs (semantic clustering, architecture, execution)
    blog-flow/                     # FLOW framework prompts (v1.7.0)
      SKILL.md                    # FLOW orchestrator (find/optimize/win/prompts/sync)
      references/                 # Synced from github.com/AgriciDaniel/flow (CC BY 4.0)
    blog-multilingual/             # One-command international publishing (v1.7.0)
      SKILL.md                    # Multilingual orchestrator
    blog-translate/                # SEO-optimized translation (v1.7.0)
      SKILL.md
      references/                 # Translation rules + cultural adaptation profiles
    blog-localize/                 # Cultural deep-adaptation (v1.7.0)
      SKILL.md
    blog-locale-audit/             # Multilingual content QA (v1.7.0)
      SKILL.md
  agents/                            # 5 specialized subagents
    blog-researcher.md              # Statistics and source research
    blog-writer.md                  # Content generation
    blog-seo.md                     # SEO validation
    blog-reviewer.md                # Quality scoring (no Bash, post v1.7.0 hardening)
    blog-translator.md              # Multilingual translation (no Bash, v1.7.0)
  tests/                             # pytest suite incl. test_security_guardrails.py
```

## Commands

| Command | Purpose |
|---------|---------|
| `/blog write` | Write new articles optimized for rankings + AI citations |
| `/blog rewrite` | Optimize existing posts with sourced statistics |
| `/blog analyze` | 5-category 100-point scoring with AI detection |
| `/blog brief` | Detailed content briefs with competitive analysis |
| `/blog outline` | SERP-informed outlines with heading hierarchy |
| `/blog calendar` | Editorial calendars with topic clusters |
| `/blog strategy` | Blog positioning and content planning |
| `/blog seo-check` | Post-writing SEO validation checklist |
| `/blog schema` | JSON-LD schema markup generation |
| `/blog chart` | Inline SVG data visualization charts |
| `/blog repurpose` | Multi-platform content repurposing |
| `/blog geo` | AI citation optimization audit |
| `/blog image` | AI image generation and editing via Gemini |
| `/blog audit` | Full-site blog health assessment |
| `/blog cannibalization` | Detect keyword overlap across posts |
| `/blog factcheck` | Verify statistics against cited sources |
| `/blog persona` | Manage writing personas and voice profiles |
| `/blog taxonomy` | Tag/category CMS management |
| `/blog notebooklm` | Query NotebookLM for source-grounded research |
| `/blog audio` | Generate audio narration via Gemini TTS |
| `/blog google` | Google API data: PSI, CrUX, GSC, GA4, NLP, YouTube, Keywords |
| `/blog cluster` | Semantic topic-cluster planning + execution (v1.7.0) |
| `/blog multilingual` | Write + translate + localize + emit hreflang in one command (v1.7.0) |
| `/blog translate` | SEO-optimized translation with format preservation (v1.7.0) |
| `/blog localize` | Cultural deep-adaptation per locale (v1.7.0) |
| `/blog locale-audit` | Multilingual content QA (v1.7.0) |
| `/blog flow` | FLOW framework prompts: find, optimize, win, prompts index, sync (v1.7.0) |

## Development Rules

- Keep SKILL.md files under 500 lines / 5000 tokens
- SKILL.md frontmatter: only valid fields (name, description, user-invokable, argument-hint, compatibility, license, metadata, disable-model-invocation). Do NOT use `allowed-tools` -- it is not a Claude Code spec field
- New reference files should be focused and under 200 lines. Existing comprehensive references (platform-guides, schema-stack, content-templates, distribution-playbook) are exempt from this guideline
- Scripts must have docstrings, CLI interface, and JSON output
- Follow kebab-case naming for all skill directories
- Agents invoked via Task tool, never via Bash
- Python 3.11+ required; dependencies in pyproject.toml
- Test with `python -m pytest tests/` after changes
- Run `claude plugin validate .` before pushing plugin changes
- Plugin skills auto-discovered from `skills/` directory (do not list in plugin.json)

## Distribution

### Anthropic Official Marketplace
Submit at: claude.ai/settings/plugins/submit or platform.claude.com/plugins/submit

### Self-Hosted Marketplace
```
/plugin marketplace add AgriciDaniel/claude-blog
/plugin install claude-blog@AgriciDaniel-claude-blog
```

### Standalone Install (no marketplace)
```bash
curl -sL https://raw.githubusercontent.com/AgriciDaniel/claude-blog/main/install.sh | bash
```

## Release Blog Post

After cutting a new release (git tag + `gh release create`), run:

```
/release-blog
```

This generates a blog post on https://claude-blog.md/blog/, handles cover image generation, SEO metadata, FAQ schema, internal linking, sitemap/llms.txt updates, Vercel deployment, and Google indexing.
