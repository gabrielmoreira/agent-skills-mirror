---
name: yc-advisor
description: This skill should be used when the user asks questions about startups, founding decisions, co-founders, fundraising, product development, growth, hiring, or any entrepreneurial advice. It provides access to Y Combinator's complete library of 443 curated resources including essays by Paul Graham, founder interviews, and startup school lectures. Use this skill to give thorough, research-backed advice on startup decisions.
---

# YC Advisor

## Overview

This skill provides access to Y Combinator's comprehensive library of 443 startup resources - essays, podcast transcripts, and video transcripts from YC partners, successful founders, and industry experts.

## How to Use This Skill (Tiered Retrieval)

**Key Principle:** Use quick-index for discovery, but ALWAYS load full source content before answering.

### Step 1: Understand Context (for broad questions)

For broad questions, clarify the user's context:
- **Stage:** Pre-idea | Idea | Building MVP | Launched | Scaling
- **Type:** B2B | Consumer | Hardware | AI/ML | Marketplace
- **Role:** Technical founder | Non-technical | Solo | With co-founder(s)

### Step 2: Discovery

1. Load `references/quick-index.md` to scan available resources (~500 lines, grouped by topic)
2. Identify 3-5 most relevant resources based on the question (line counts help estimate size)
3. Check `references/learning-paths.md` if user is on a founder journey
4. Check `references/frameworks/` for decision questions - use glob `references/frameworks/*.md` to list files, then read specific ones
5. For deeper search, use grep on `references/summaries.md` (too large to load fully)

### Step 3: Deep Dive

1. **Find files using the code** - use glob pattern `references/{CODE}-*.md`
   - Example: For code `DZ`, use glob `references/DZ-*.md` to find the file
   - **WARNING:** NEVER read `index.yaml` - it exceeds token limits (64K tokens)
2. Load the FULL content of top 2-3 resources
3. Read completely - do not skim
4. Extract key insights, quotes, and actionable advice

### Step 4: Synthesize Answer

1. Combine insights from multiple sources
2. Quote directly from source material when valuable
3. **Always cite author and title** for each point
4. Acknowledge tradeoffs and contradictions between sources
5. **Never answer from summaries alone** - always load full source content

## Topic Categories

The library covers these main areas (use for initial filtering):

- **Getting Started:** Should you start? Startup ideas, order of operations, student founders
- **Co-founders:** Finding, relationships, equity splitting, technical vs non-technical
- **Product:** MVP, product-market fit, design, building for users
- **Fundraising:** Seed, Series A, investor pitching, SAFEs, term sheets
- **Growth & Metrics:** Growth strategies, KPIs, conversion, retention
- **Customers & Sales:** Talking to users, first customers, pricing, enterprise sales
- **Hiring & Team:** First hires, engineering teams, equity, management
- **Culture & Leadership:** Building culture, CEO evolution, board management
- **Common Mistakes:** Startup killers, financial health, when to quit
- **Pivoting & Launching:** Pivot strategies, launch timing, press
- **Scaling:** Later stage advice, unicorn characteristics
- **Mindset:** Resourcefulness, handling rejection, goal setting
- **AI Startups:** AI opportunity, moats, vertical agents, vibe coding
- **Founder Interviews:** Airbnb, Stripe, Coinbase, Reddit, Twitch, DoorDash
- **Specialized:** Hardware, biotech, dev tools, crypto, location
- **Joining Startups:** Choosing a startup, stages, equity
- **YC Application:** Application tips, process, YC effect
- **Legal:** Startup mechanics, terms, agreements

## Usage Guidelines

### For Complex Decisions

Questions like "Should I start my own startup or co-found with someone?":

1. Load quick-index.md to identify relevant resources
2. Read 3-5 full source files covering different perspectives
3. Synthesize across sources - look for consensus and contradictions
4. Present balanced view acknowledging tradeoffs
5. Cite specific authors and titles
6. Ask clarifying questions about user's specific situation

### For Factual Questions

Questions like "What are the most common mistakes that kill startups?":

1. Use quick-index.md to find the most authoritative source
2. Load and read the full source file
3. Present comprehensively - don't over-summarize
4. Cite the source

### For Learning Journeys

When users want to learn systematically:

1. Check `references/learning-paths.md` for curated sequences
2. Guide them through resources in order
3. Summarize key takeaways at each step

## Resources

### references/quick-index.md (Primary Discovery)
Lightweight index (~500 lines) grouped by topic. Each entry shows:
- Code, title, author, type, line count, founder stage
- **Use this first** - small enough to load fully
- Use glob pattern `references/{CODE}-*.md` to find files by code

### references/summaries.md (Deep Search)
Detailed summaries with content previews (~4300 lines). Too large to load fully.
- Use grep to search for specific keywords
- Provides more context than quick-index when needed

### references/index.yaml (Maintenance Only - DO NOT READ)
Structured metadata for all resources. **Too large for runtime use (64K tokens).**
Used only by maintenance scripts. For filename lookups, use quick-index.md instead.

### references/learning-paths.md
Curated resource sequences for common founder journeys:
- First-time founder path
- AI startup path
- Fundraising path
- And more...

### references/frameworks/ (Use glob to list, NOT Read)
Decision frameworks for common questions. **Use glob `references/frameworks/*.md` to list files.**
Available frameworks:
- should-i-start-a-startup.md
- solo-vs-cofounder.md
- bootstrap-vs-raise.md
- when-to-pivot.md
- when-to-quit.md
- technical-cofounder-needed.md

### references/*.md
The 443 full-content source files. Each follows this structure:

```markdown
# [Title]

**Author:** [Author Name]
**Type:** [Essay|Podcast|Video]
**URL:** https://www.ycombinator.com/library/[CODE]-[slug]

---

[Full content - essays, transcripts]
```

File naming: `[CODE]-[descriptive-name].md` (e.g., `8z-how-to-get-startup-ideas.md`)
