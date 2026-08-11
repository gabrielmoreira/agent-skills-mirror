---
name: deep-research
description: |
  Read this skill when the user asks for a research report, deep research, industry report, analysis report, whitepaper, or any substantive document deliverable; or when the topic requires multi-source retrieval and cross-validation (competitive analysis, market analysis, industry research, deep dive, landscape survey); or when the user is unsatisfied with the depth of an existing answer. Keyword signals: research, deep research, deep dive, analysis, investigate, report, survey, industry analysis, competitive analysis, market analysis. Trigger when: (1) the user wants to produce a formal report or research document as the deliverable; (2) the topic requires current, verifiable data from multiple sources — news, market analysis, competitive landscape, industry research; (3) the user is unsatisfied with the depth of an existing answer. Skip when a single search or model recall suffices and no document output is needed.

---

# Deep Research Skill

Turn vague questions into verifiable, actionable, evidence-backed research outcomes, with polished HTML report as default deliverable.

---

## References (Read On Demand)

Each file maps to an independent condition — combine as needed:
- New research or deepening existing content -> [reference/research-workflow.md](reference/research-workflow.md) (full workflow, including gap diagnosis for deepening)
- Delivering an HTML report -> [reference/report-template.html](reference/report-template.html) (whether new or restructured)

---

## Non-Negotiable Rules

1. Plan and confirm before heavy execution: after loading, output plan draft + kickoff Q&A, wait for confirmation. No heavy retrieval before user confirms.
2. Minimize user typing: provide selectable options with defaults; allow start or `B A A A C` (one letter per question).
3. Every major claim needs evidence: traceable to sources; include counter-evidence or uncertainty notes.
4. Default deliverable is HTML report: follow template rules for structure, citations, and visual quality.

---

## Immediate Actions After Trigger

### Step 1: Quick pre-search
Run one web_search call with 2-3 queries in parallel from different angles (e.g. "what is X" + "X current debates" + "X use cases"). No deep reading — just enough to understand the topic's shape and key concerns so the plan and questions are sharper.

### Step 2: Output the research plan draft
Include at least: objective and boundary, key question breakdown (3-7), source strategy, deliverable outline, expected depth mode.

### Step 3: Send kickoff Q&A card
The card has two tiers:

**Confirm questions (≤3)**: scope-defining questions that genuinely affect this research — customized from the pre-search, not a fixed template. Reference dimensions (pick what applies): depth / time range / geography / source preference / angle of focus.

**Optional add-ons (exactly 3)**: cross-domain or adjacent angles surfaced by the pre-search — things outside the natural research scope that the user likely didn't think to ask for but would find valuable. Do not put things that obviously belong in the core research here.

Adapt the confirmation word to the user's language (e.g., "start" in English, the equivalent in the user's language).

> Heads up: deep research takes longer than a quick answer — expect multiple search rounds and cross-checking.

### Step 4: Wait for user confirmation
Support: start (all defaults), letter-combo options, free-text constraints followed by start.

### Low-Input Interaction Rules
1. If user replies start: begin immediately with default settings.
2. If user replies option combo: parse and begin.
3. If user declines questions: begin with defaults, state assumptions explicitly.
4. If input is still ambiguous: ask only the single most critical follow-up.

---

## When User Says "Too Shallow" / "Lacks Evidence" (Scenario B: Deepen Existing Content)

This is deepening mode, not a new report. Enter deepening mode instead of superficial rewriting.

First, assess the type of existing content:
- If the existing content is an HTML report (regardless of origin), proactively ask: "Would you like to restructure this into a full deep-research report using our template?"
  - User agrees -> read deepen-guide.md + report-template.html, restructure to template
  - User declines -> read deepen-guide.md only, deepen within the existing format
- If the existing content is not an HTML report (plain text, Markdown, etc.) -> read deepen-guide.md only, output format follows existing content

Got it, I'll dig deeper.

Just reply `ok` to go with default settings, or tell me what bothered you most:

**1) Biggest gap?**
- A. Not enough evidence
- B. Conclusions too vague
- C. No counterpoints
- D. Recommendations can't be acted on

**2) Where to focus?**
- A. Data and facts
- B. Reasoning and methodology
- C. Industry cases and comparisons

---

## Minimal Execution Pseudoflow

```text
read this skill first
read research-workflow.md
if output is HTML report: read report-template.html

if task is new research:
    draft plan + send kickoff Q&A -> wait for confirmation
    execute full workflow -> deliver

if task is deepening existing content:
    diagnose gaps (Phase 6 of research-workflow.md) -> re-run retrieval on weak areas
    rewrite affected sections only -> deliver
```

---

## Output Style

- Planning and kickoff: concise, friendly, decision-ready
- Report phase: conclusion-first, evidence-transparent, method-reproducible
- Interaction: prioritize low-typing start, ask more only when needed
