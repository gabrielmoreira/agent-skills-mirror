---
name: heatmap-analyze
description: >
  Ptengine Heatmap end-to-end analysis skill. Fetches real heatmap data via ptengine-cli and runs
  AI-powered CRO behavior analysis using a 4-stage psychology model. Before analysis, runs a
  short brand & intent discovery step (optionally with lightweight website/brand research via
  http / browser) to ground conclusions in business context. Self-contained — includes all
  analysis methodology, data transformation rules, and output schemas.
  Use this skill when the user wants to: analyze a webpage's heatmap data, understand user behavior
  on a page, compare audience segments, validate A/B test results, evaluate ad channel performance,
  analyze audience characteristics, find conversion barriers or opportunities, or optimize a landing page.
  Trigger whenever: "analyze heatmap", "heatmap analysis", "page behavior", "analyze this URL/page",
  "how are users behaving", "compare segments", "A/B test results", "ad performance", "audience analysis",
  "ptengine", "block-level analysis", "conversion optimization", "exit rate", "dwell time", "user drop-off",
  "landing page analysis", or any request involving page analytics combined with behavioral insights.
allowed-tools: bash file_read think http browser screenshot browser_navigate browser_snapshot browser_take_screenshot web_fetch web_search web_subpage_fetch
---

# Ptengine Heatmap Analysis

You are an expert CRO (Conversion Rate Optimization) analyst using Ptengine heatmap data. This skill
is fully self-contained: it includes the data fetching tool (ptengine-cli), analysis methodology
(4-stage psychology model), quality constraints, and output schemas.

## Skill Contents

```
heatmap-analyze/
├── SKILL.md                           # This file — workflow orchestration
├── install.sh                         # ptengine-cli installer
└── references/
    ├── ptengine-cli.md                # CLI command reference and output format
    ├── discovery.md                   # Phase 0b/0c: brand & intent discovery, research heuristic
    ├── data-transform.md              # Field mapping, tag/ranking computation
    ├── page-classification.md         # 7 page type definitions and classification
    ├── block-analysis.md              # Block content + stage classification (4-phase model)
    ├── quality-constraints.md         # Metric dictionary, evidence policy, terminology
    ├── page-types.md                  # Per-page-type interpretation guide
    ├── single-page-task.md            # Single page analysis task + schema
    ├── compare-task.md                # Segment comparison task + schema
    ├── ab-test-task.md                # A/B test validation task + schema
    ├── ad-performance.md              # Ad source quadrant analysis + schema
    └── audience-analysis.md           # Audience segment analysis + schema
```

## Data Source Boundary

This skill has a **two-track data source rule**. Read carefully — the rule is different for
heatmap data vs. brand context.

| Data type | Authoritative source | Not allowed |
|---|---|---|
| Heatmap metrics and block structure (`page_metrics`, `block_metrics`, `page_insight`, block names, dwell, exit, impression, etc.) for the analyzed URL | **`ptengine-cli` only** | Using `http` / `browser_*` / `screenshot` / Playwright MCP to scrape the analyzed URL and fill / replace block content or metrics |
| Brand / company / product / audience / competitive context | `http`, `browser_*`, `screenshot`, or local `file_read` of a user-provided brand doc | — |

**Why the split matters (not just a preference):** `ptengine-cli` returns aggregated behavior
over the selected date range. The live page may have been edited — blocks added, removed, or
reordered — since those users visited. Mixing a live scrape with historical aggregate data
produces misleading analysis (e.g. attributing a low dwell time to copy that did not exist when
the data was collected). **Brand context is immune to this problem** — a company's mission,
product line, and target audience are not time-window-specific.

**Concretely:**
- Phase 0c.1 MAY fetch the site root, `/about`, `/pricing`, etc. via `http` / `browser_*` to
  inform `brand_context` (see `references/discovery.md`).
- Phase 1–6 MUST populate every metric and block-level field from `ptengine-cli` responses.
- If block content is missing from ptengine-cli's response, ASK the user — do not scrape the
  analyzed URL to fill it in.

## Analysis Types

| Type | Description | When to use |
|------|-------------|-------------|
| `single_page` | Deep single-page behavior analysis | Default. "How are users behaving on this page?" |
| `compare` | Cross-segment comparison | "Compare new vs returning visitors" |
| `ab_test` | A/B test hypothesis validation | "Which version won and why?" |
| `ad_performance` | Ad source quadrant analysis | "Which ad channels are performing?" |
| `audience_analysis` | Audience segment characteristics | "Who is visiting and how do they differ?" |

## Pipeline

Listed in **execution order** (not alphabetical). Letter labels are structural anchors for
cross-references; the flow runs top-to-bottom:

```
Phase 0a: Prerequisites            # ptengine-cli install/config check
Phase 0c: Auto Research (optional) # runs before 0b when the first message lacks context
  0c.1: Website / brand research (web_fetch / http / browser, site root + about + pricing)
  0c.2: Lightweight block_metrics preview (ptengine-cli, only when it helps classification)
Phase 0b: Brand & Intent Discovery # informed clarifying questions, fewer after 0c.1 ran
Phase 0d: Parameter Collection     # URL, date range, analysis type, device, language, conversion
Phase 1: Data Fetch (ptengine-cli)
Phase 2: Page Classification
Phase 3: Data Enrichment (block content + phase assignment)
Phase 4: Input Assembly (transform to analysis format)
Phase 5: Analysis (apply methodology from references/)
Phase 6: Results Presentation
```

If the user already supplied enough context in the first message, Phase 0c and Phase 0b are
skipped entirely. See `references/discovery.md § Decision table` for precise skip rules.

---

## Phase 0a: Prerequisites

### Check ptengine-cli

Run `sh install.sh --check-only` (or check `command -v ptengine-cli`):
- **READY**: Proceed to Phase 0b / 0c / 0d
- **NEEDS_CONFIG**: Ask the user for API Key and Profile ID. If the user
  does not have an API Key, walk them through the 6-step product-UI flow
  in `references/ptengine-cli.md` § "Obtaining an API Key". Then run:
  `ptengine-cli config set --api-key <KEY> --profile-id <ID>`
- **NOT_INSTALLED**: Run `sh install.sh`, then configure

---

## Phase 0b: Brand & Intent Discovery

Read `references/discovery.md` before running this phase. In short:

- Do NOT jump to parameter collection if the user's first message lacks business context
  (brand / product / audience / primary goal). A generic dataset produces generic conclusions.
- Use `think` to pick **at most 5** (usually 1–3) targeted questions from the bank in
  `discovery.md § Question bank`. Never re-ask anything the user already stated.
- Skip this phase entirely when (a) the user supplied ≥ 2 business signals upfront, or
  (b) the user says "just analyze" / "skip questions" / "直接分析".
- The phase produces a `brand_context` object (schema in `discovery.md`) that Phases 2 / 3 / 5 / 6
  consume. The card **never overrides metric evidence** — it only shapes phrasing and finding
  priority.

---

## Phase 0c: Auto Research (optional)

Two sub-probes, both optional.

### 0c.1 — Website / brand research

Run when the user gave a URL but little business context. Fetch at most 3 URLs (site root,
`/about`, `/pricing` or similar) via `http` or, if JS-rendered, `browser_navigate`. Each page
contributes ≤ ~1500 characters into `think`; total budget < 20 seconds.

Do NOT fetch the analyzed URL to replace ptengine-cli's block-level data. See
`references/discovery.md § Phase 0c.1` for the full boundary statement.

Record every fetched URL in `brand_context.research_refs[]`. On timeout or error, fall back to
pure Phase 0b Q&A.

### 0c.2 — Heatmap preview (ptengine-cli)

Default posture: SKIP. Only run the 7-day `block_metrics` probe when page-type classification
is still ambiguous after 0c.1 AND a block-names sample would materially disambiguate it. The
probe informs `preview_signals` only; Phase 1 always performs the full-range fetch with the
user's requested date range. See `references/discovery.md § Phase 0c.2` for the full gate.

---

## Phase 0d: Parameter Collection

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| URL | Yes | — | Page URL to analyze |
| Date range | Yes | Last 30 days | YYYY-MM-DD |
| Analysis type | Yes | single_page | 5 types above |
| Device type | For block data | MOBILE | PC or MOBILE (block_metrics cannot use ALL) |
| Language | No | ENGLISH | CHINESE / ENGLISH / JAPANESE |
| Conversion name | No | — | Fuzzy match for conversion metrics |

For **compare**: which segments to compare (e.g. new vs returning visitors)
For **ab_test**: campaign name, type (inline/popup/redirect), version info

If `brand_context.primary_goal` is known, prefer it as the conversion framing even when
`Conversion name` is left blank.

---

## Phase 1: Data Fetch

Read `references/ptengine-cli.md` for full command reference.

### Core commands

```bash
# Page-level metrics
ptengine-cli heatmap query --query-type page_metrics \
  --url "<URL>" --start-date <START> --end-date <END> --output json

# Block-level metrics (MUST specify device type)
ptengine-cli heatmap query --query-type block_metrics \
  --url "<URL>" --start-date <START> --end-date <END> \
  --device-type <PC|MOBILE> --output json

# Dimension-grouped insights (for ad/audience analysis)
ptengine-cli heatmap query --query-type page_insight \
  --url "<URL>" --fun-name <sourceType|visitType|terminalType> \
  --start-date <START> --end-date <END> --output json

# Filtered data (for compare)
ptengine-cli heatmap query --query-type block_metrics \
  --url "<URL>" --start-date <START> --end-date <END> \
  --device-type MOBILE --filter "visitType include newVisitor" --output json
```

### Error handling
- `"success": false` → show error message and hint
- Rate limited → check `rateLimit.remainingMinute`, wait if needed
- No data → suggest checking URL and date range

### Data preprocessing (important)

ptengine-cli returns all metric values as **formatted strings** (e.g. `"6,777"`, `"55.08%"`,
`"3m 13s"`), not raw numbers. Before proceeding to analysis, parse these strings into numeric
values following the rules in `references/data-transform.md` § "Value format parsing". Getting
this step wrong will produce incorrect analysis — pay special attention to percentage values
(already percentages, do NOT multiply by 100 again) and duration formats (page-level uses
"Xm Ys", block-level uses "Xs").

---

## Phase 2: Page Classification

Read `references/page-classification.md` for full criteria.

If `brand_context` is populated, its `business_model` and (when present) `preview_signals.proposed_page_type`
act as **weak priors**. Full-data signals (actual block names from Phase 1, full page_insight
sourceType distribution) still override the prior when they disagree. Never skip the full
classification check just because the prior looks confident.

Classify the URL into one of 7 types and map to internal key:

| Result | Key | Notes |
|---|---|---|
| Sales Landing Page | `sales_lp` or `ad_lp` | ad_lp if ad traffic >50% |
| Article LP | `article_lp` | |
| Product Detail Page | `pdp` | |
| Homepage | `homepage` | |
| Campaign / Promotion | `sales_lp` | |
| Other Content | `other_content` | |
| Other Function | `other_function` | |

If uncertain, ask the user.

---

## Phase 3: Data Enrichment

Read `references/block-analysis.md` for the 4-phase psychology model and module categories.

### 3a. Block Content Analysis
For each block, determine `module_category`, `content_summary`, `marketing_intent` using the
module categories for the detected page type. If `brand_context.product_or_service` or
`brand_voice` is set, use it to choose between equally-grounded paraphrasings — do NOT invent
block copy that ptengine-cli did not return.

### 3b. Block Stage Classification
Assign each block to phase 1-4 using the criteria in block-analysis.md. Load the correct
phase names for the page_type and language from the phase name tables.

Use block_name and block position as primary signals when screenshots are not included
in ptengine-cli's response. Do not fetch screenshots of the analyzed URL to substitute for
ptengine-cli's block-level data (see Data Source Boundary — the first row of the table).

---

## Phase 4: Input Assembly

Read `references/data-transform.md` for detailed field mapping, tag computation, and ranking algorithms.

Key steps:
1. Assemble `base_metric` from page_metrics response
2. Assemble `block_data[]` from block_metrics + Phase 3 enrichment
3. Compute tags (High/Medium/Low) and rankings if not provided by API
4. For ad/audience analysis: compute quadrant assignments

---

## Phase 5: Execute Analysis

Based on analysis type, read the corresponding reference and follow its methodology:

| Type | Reference file | Key output fields |
|------|---------------|-------------------|
| single_page | `references/single-page-task.md` | core_insight, narrative_structure, barriers, opportunities |
| compare | `references/compare-task.md` | macro_performance, narrative_comparison, barriers/opportunities per segment |
| ab_test | `references/ab-test-task.md` | core_conclusion, hypothesis_validation with win_version_index |
| ad_performance | `references/ad-performance.md` | core_insights.summary, ad_performance_overview.description |
| audience_analysis | `references/audience-analysis.md` | core_insights.summary, user_profile.description |

Before writing analysis, also read:
- `references/page-types.md` — interpretation guide for the detected page type
- `references/quality-constraints.md` — metric dictionary, evidence policy, terminology enforcement

If `brand_context` is populated, apply its framing per `references/discovery.md § Handoff`:
`primary_goal` shapes which barriers/opportunities surface first; `known_problems` becomes a
hypothesis the narrative can confirm or complicate (always hedged, always backed by metric
evidence).

### Critical quality gates (always apply)

1. **Full block coverage**: ALL blocks must appear in narrative structure (no omissions)
2. **Directional consistency**: Verify metric direction language matches the direction table
3. **Evidence grounding**: Always cite dwell + exit, use hedging for causal claims
4. **No technical leaks**: No block_ids, camelCase keys, or raw tags in output text
5. **Language purity**: No mixed-language output; apply terminology enforcement
6. **Source separation**: fvDropOffRate from base_metric only; exitRate from block_data only
7. **Low sample warning**: If total visits < 100 or a block's impressionRate is very low (< 10%),
   note the limited data confidence in the analysis. Metrics from very few sessions can be misleading.

---

## Phase 6: Present Results

Output a **human-readable Markdown report** in the target language — not JSON. The report is for
marketing practitioners, CRO specialists, and site operators who need actionable insights.

Each analysis type has its own report template defined in the corresponding reference file.
The general structure is:

1. **Core finding** — the single most important insight, prominently displayed
2. **Detailed analysis** — phase-by-phase narrative (behavior tasks) or structured comparison
3. **Barriers and opportunities** — clearly separated with supporting data
4. **Improvement suggestions** — 1-3 concrete, actionable recommendations
5. **Next steps** — offer to run a different analysis type, compare segments, or save results

When `brand_context.source != "none"`, open the report with a one-sentence framing line that
ties the analysis to `brand_context.primary_goal`. If `brand_context.research_refs` is non-empty,
a small "Sources consulted" footnote listing those URLs may be appended at the end of the report.
Do NOT echo `brand_context` itself as raw YAML in the report.
