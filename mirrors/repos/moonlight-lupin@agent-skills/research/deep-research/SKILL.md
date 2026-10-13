---
name: deep-research
description: "Use when the user asks for \"deep research\", a \"research report on\", a \"comprehensive analysis of\", to \"look into X in depth\", to \"write a report on X\", or any question needing multi-source synthesis beyond a single search — an autonomous multi-step deep research engine implementing an iterative Think → Search → Extract → Synthesize → Stop loop. The LLM drives every decision: what to search, what's relevant, what's missing, and when to stop. Produces a cited, magazine-quality report with inline citations, category-specific formatting, and research stats. For entity vetting/dossiers use entity-research; for news digests use news-monitoring; for source-grounded Q&A use notebooklm-mode."
license: MIT
metadata:
  version: 1.9.2
  author: moonlight-lupin
  platforms: [linux, macos, windows]
  hermes:
    tags: [research, deep-research, report, synthesis, iterative, citations, evidence-basis, provenance]
    related_skills: [news-monitoring, entity-research, notebooklm-mode, youtube-topic-research, fact-checker, source-tracker]
---

# Deep Research — Iterative Research Engine

An autonomous, multi-step research engine that performs exhaustive information
gathering and synthesis. Unlike a single `web_search`, this skill implements an
iterative loop where the agent plans, searches, extracts, synthesizes, and
decides when to stop — producing a cited report with structured evidence,
source quality tiers, and explicit gaps/contradictions sections.

See `references/structured-evidence-format.md` for the evidence.json layer and
`references/docsgpt-concepts.md` for adaptive-depth concept mapping.

## When to use

- User asks for "deep research", "research report", "comprehensive analysis"
- User wants a written report on a topic (not just a quick answer)
- Question requires multi-source synthesis with citations
- User says "look into X in depth" or "write a report on X"

## When NOT to use

- **Entity vetting/dossiers** → use `entity-research` (has sanctions screening, structured lenses)
- **Recurring news digests** → use `news-monitoring` (has cron, dedup, multi-language)
- **Source-grounded Q&A from collected sources** → use `notebooklm-mode` (has vault + RAG)
- **Quick factual question** → just use `web_search` directly
- **Single-source extraction** → use `web_search` + `web_extract`

## Architecture

```
User question
  → Step 0: Clarification (optional — assess if question is too vague)
  → Step 1: Plan (sub-questions, key topics, success criteria, category, language, complexity)
  → Step 2: Date grounding + language anchor
  → Step 3: Iterative loop (max rounds = complexity cap: simple=2, moderate=3, complex=5)
      ├─ 3a: Generate gap-driven queries (incl. refute queries from round 2+, empty-search refinement)
      ├─ 3b: Search (web_search) + fetch (web_extract)
      ├─ 3c: Quality filter + extraction + source quality classification + numbered citations
      ├─ 3d: Synthesize into cumulative research state (with token budget check)
      ├─ 3e: Structured evidence (optional: evidence.json for 5+ sources)
      └─ 3f: Stopping check (LLM evaluates coverage + token budget)
  → Step 4: Final report (overview-first structure, see template)
  → Step 5: Stats summary
```

**Report output order (overview-first):** Executive Summary → comparison/overview table → detailed analysis per sub-question → contradictions → gaps → conclusion → source table. Readers get the answer and the at-a-glance comparison before the detailed reasoning.

## Step 0 — Clarification (optional)

Before planning, assess whether the question is specific enough to research productively. This step prevents wasting rounds on a question that's too vague.

**When to clarify:**
- The question is 1-5 words with no scope ("research AI", "tell me about quantum computing")
- The question could mean very different things depending on intent ("is X good?" — good for what? for whom?)
- The question lacks a clear angle ("look into climate change" — scientific? policy? economic?)

**When NOT to clarify:**
- The question already has sub-questions or specific parameters
- The user explicitly says "just research it" or "don't ask, just go"
- The question is specific enough to generate productive search queries immediately
- The question is a simple factual lookup ("what is the latest version of X?", "when did Y happen?") — even if short, if the intent is clear, proceed
- The user is responding to a prior clarification (don't loop)

**How:** Present 1-3 short questions to the user that would narrow the scope. Keep it brief — this is a scope check, not an interview:

> "Before I start researching, I'd like to clarify:
> 1. [narrowing question 1]
> 2. [narrowing question 2]
>
> Please provide these details and I'll begin."

If the question is already specific, skip this step entirely and proceed to Step 1.

## Step 1 — Research Plan

Before searching, break the question into a research plan. Output:

```
## Research Plan
Question: [user's question]
Date: [current date]
Language: [BCP 47 tag — e.g. en, zh-Hans, ja. Detect from query; user's explicit language preference overrides. Use consistently throughout the report.]

Sub-questions:
1. [specific sub-question 1]
2. [specific sub-question 2]
3. [specific sub-question 3]
4. [up to 6 total]

Key topics:
- [topic 1]
- [topic 2]

Success criteria:
- [what would comprehensive coverage look like?]
- [minimum: each sub-question has ≥1 source]

Report category: [factual | comparison | product | how-to | fact-check | explainer]

Complexity: [simple | moderate | complex]
```

**Complexity assessment and adaptive depth:**
Classify the question's complexity to determine the maximum number of research rounds. This prevents over-searching simple questions and under-searching complex ones.

| Complexity | Max rounds | Per-round breadth | When to use |
|---|---|---|---|
| **simple** | 2 | 2 | Single-factual question, narrow scope, 1-2 sub-questions. Example: "What is the latest version of Python?" |
| **moderate** | 3 | 3 | Multi-faceted question, 3-4 sub-questions, comparison or how-to. Example: "Compare Qdrant vs pgvector for RAG" |
| **complex** | 5 | 4 | Broad scope, 5-6 sub-questions, requires deep synthesis across domains. Example: "Comprehensive analysis of the self-hosting vs managed API tradeoff for AI infrastructure" |

The complexity cap is a **maximum**, not a target. The stopping check (Step 3f) still governs early termination. A simple question that finds comprehensive answers in 1 round should stop at 1 — the cap of 2 means it *can* go to 2 if needed, not that it *must*.

**Search budget** (adapted from upstream `research-input.ts` presets + `estimateMaxSearches`): announce the budget in the plan — "Search budget: ≤N queries", N = per-round breadth × max rounds (script: `estimate-budget --breadth B --rounds R`). When round 2+ runs deep-dive chains (§3a), the upper bound is tree-mode: `estimate-budget --breadth B --rounds R --halving`, upstream's breadth-halving recursion. The budget is a ceiling the loop must not exceed; prefer the cheapest round that answers well, per the §3f stopping check.

**Language anchoring:** Detect the output language from the query and normalize to a BCP 47 tag (e.g. `en`, `zh-Hans`, `zh-Hant`, `ja`). Use it consistently throughout — executive summary, analysis, contradictions, gaps, conclusion. Source titles, URLs, proper nouns, and code may stay in their original language; search queries may use any language that helps evidence gathering. If the user explicitly switches language mid-research, update the anchor and use the new language for all subsequent output.

**Report category detection:**
- "vs", "compare", "better than" → **comparison**
- "best", "top", "recommend", "buy" → **product**
- "how to", "guide", "steps" → **how-to**
- "is it true", "verify", "fact check" → **fact-check**
- "what is", "explain", "overview" → **explainer**
- default → **factual**

## Step 2 — Date Grounding

Inject the current date before any search. This is **mandatory** — LLMs default to training-cutoff years, producing stale queries.

> Today's date is {current date as "DD Month YYYY"}. When a search query needs a year or refers to "latest"/"current"/"this year", use {current year} or relative wording — never a year inferred from training data.

## Step 3 — Iterative Loop

### Round structure

Each round follows: **Query → Search → Extract → Synthesize → Check Stop**

Run **max N rounds** where N = complexity cap from Step 1 (simple=2, moderate=3, complex=5). Most topics converge in 2-3 rounds. The cap is a ceiling, not a target.

### 3a — Query Generation (gap-driven)

**Per-round breadth** comes from the complexity preset (Step 1): simple=2, moderate=3, complex=4 queries per round. **Round 1** targets the sub-questions from the plan. **Round 2+** targets gaps identified in the previous synthesis **and** per-query follow-up directions recorded during extraction (below).

Before generating queries, review:
- Original question and research plan
- Current research state (what's already found)
- Round number
- What's still missing

Generate queries that target the **gaps**, not repeat what's already found.

**Mini search plan per query** (adapted from upstream `search-plan.ts`): plan a search task, not a bag of keywords. Each generated query carries:
- **one angle** — a concise domain-keyword query, an exact identifier, or a natural-language question. Preserve error messages, standards, paper titles, model numbers, and technical terminology verbatim in the query text; never force them into a conversational sentence or truncate by word count. Avoid unrelated keyword piles ("official blog OR paper").
- **intent** — the donsetch `web_search` `intent` vertical: `web` (default), `news`, `paper`, `entity`, `code`. Broad AI news gets complementary discovery queries across models, products, and industry — never silently narrowed to LLM papers.
- **time window + domain scope** — recorded in the research state and expressed in the query text (the donsetch tier has no structural SERP filters). Never invent a domain or publisher whitelist; scope domains only when the user requested it or the domain is already verified in earlier sources. **Publication metadata is a hint, not proof** — a search result's date never becomes the claim's date; verify event dates in source text (§3c).
- **source preference** — `any` or `primary`; `primary` steers §3c toward official docs, filings, papers. It is an extraction preference, never a keyword or a fabricated tier.

**Frozen constraints on rewrite:** the time window and domain scope stay fixed across rounds and rewrites — a weak result is not permission to broaden them. On empty or thin results, only the query text changes:
- 1st empty → broader query or synonyms. 2nd consecutive → fundamentally different angle/domain/language. 3rd → move on; document as a gap rather than burning rounds on dead-end queries.
- **Identical-rewrite stop** — if the refined query equals the previous one modulo whitespace, stop refining that angle: move to the gap list, don't re-run the same search.

**Round-outcome classification** (adapted from upstream `search-assessment.ts`): after each round's extraction settles, classify the round outcome and let the reason pick the next move — the taxonomy replaces ad-hoc retry judgement with a bounded, reason-specific response. Classify exactly one of:

| Outcome | Meaning | Next move |
|---|---|---|
| `verified` | ≥1 stored claim anchored per §3c | No retry; proceed to synthesis / stop check |
| `no_results` | Search returned nothing | Refinement ladder above |
| `irrelevant` | Results exist, none survive §3c triage | One fundamentally-different-angle rewrite; treat as the 2nd-empty rung |
| `no_findings` | Relevant pages found but nothing goal-relevant extracted in them | One targeted re-read (a §3b fetch budget event, `focus`/`section`); then move on |
| `unmatched_sources` | A stored claim cites a source absent from the registered set | Re-anchor the claim to its correct registered source; never cite an unmatched source |
| `unmatched_quotes` | Stored excerpts fail §3c verbatim anchoring | `check-quote` repair-once (§3c) |

Relevance itself stays agent-judged — the taxonomy assigns each reason a single bounded response and forbids retry without a new move. Record the classification with your working state so the next round's query generation starts from the named gap.

**Follow-up threading (deep-dive chains, upstream's breadth-halving recursion, bounded):** while extracting (§3c), each query thread records ≤2 follow-up directions when a material gap remains — empty when covered, never padded. Round 2+ queries draw from these per-thread directions plus global gaps, and every thread carries the **original user goal** so deep queries stay aligned with it (drift guard). At most one active deep-dive chain per sub-question, width = ceil(preset breadth / 2) at each level below its first, all inside the plan's search budget.

**Coverage balancing (round 2+):** before following the loudest gap, put a query at any planned sub-question still at **zero coverage**. A gap list ordered by noise lets one loud thread starve a silent one; balancing is mandatory before generating optional deep-dive queries.

**Refute polarity requirement:** Round 2+ must include at least one query targeting counter-evidence, opposing viewpoints, or criticisms of the leading hypothesis. If no counter-evidence is found after searching, note it explicitly in the synthesis — refute count = 0 usually means you didn't search well, not that no counter-evidence exists. This prevents confirmation-biased research.

### 3b — Search and Fetch

**Provider preference (optional, user-set):** On request, use the donsetch MCP search/fetch tools, falling back to `web_search`/`web_extract` if unavailable. Never abort over a provider preference. Record the provider used in the run manifest and stats block.
```
web_search(query="...", limit=10)
```

Run one `web_search` per query (plus `query_variants` when two distinct angles serve one requirement). Then apply **snippet-first triage** — adapted from upstream `read-source.ts`'s on-demand reading, search results and their snippets are first-class evidence:

- **Triage before fetching.** Run §3c's quality filter on snippets and titles; a fetched page is a budgeted event, not a default. Fetch full page text only when a **concrete missing question** exists that the snippet cannot answer (missing date, statistic, named entity, or evidence for a targeted sub-question), or when the source is a primary-tier candidate for a key claim. Do not reject a promising candidate solely because its snippet lacks a date — that is exactly the fetch signal.
- **Budget the fetches.** ≤2 full-page fetches per round; run-wide ≤4 for moderate, ≤6 for complex reports (simple reports rarely need any). Track URLs already fetched — never re-fetch across rounds. Count page fetches in the stats block.
- **Keep evidence source types separate.** A snippet supports what it *states* — at most `[SOURCED]`, never independently corroborated. The fetched page text is the verbatim-quote substrate for §3c anchoring: a claim whose snippet was thin must be re-anchored to the page text before its snippet goes in the store.
- **Reading tools.** donsetch `web_fetch` modes are the primary reading path (`scan`/`read`/`deep` budgets, `focus`/`section` for targeted reading, `toc` for structure); built-in `web_extract` (head+tail with an on-disk full-text path) is the fallback.

```
web_extract(urls=["url1", "url2"])
```

### 3b.1 — Evidence Persistence (mandatory for 5+ source reports)

Persist evidence to disk from the first round so it survives context compaction: `init-run`, `register-source`, `add-claim`, `add-evidence`, `check-quote` subcommands of `scripts/research_validation.py`. Add claims and evidence **during** the loop (§3d), not at the end — the append-only `claims.jsonl` is the fabrication-detection backbone for the gates. On context compaction, re-read `claims.jsonl` instead of trusting compressed memory. **Also save each fetched page's text** to `<run_dir>/pages/<source_id>.txt` (write_file right after registering the source; for pages `web_extract` stored to disk, its reported path can be passed to `check-quote --file` directly). That page-text file is the substrate for verbatim quote anchoring (§3c). Full contract: `references/validation-gates.md`.

### 3c — Quality Filter and Extraction

Before extracting content, **discard low-quality results**:

- **Thin content**: landing pages, aggregator stubs, <100 words of substantive text
- **Irrelevant**: keyword overlap without topical relevance. Use word-boundary matching for topic terms — "port" should not match "transport" or "support"
- **Duplicate URLs**: already fetched in a previous round
- **Non-text**: video-only pages, image boards, login walls with no preview

For each quality source, extract **goal-relevant facts**:
- What facts in this source address a sub-question from the research plan?
- Ignore noise, navigation, ads, boilerplate
- Prefer specific data, statistics, named sources, dates over vague claims
- Record the source URL and title with each extracted fact. Assign each unique source a **numbered citation** `[1]`, `[2]`, etc. on first encounter — reuse the same number for subsequent facts from the same source. This produces cleaner inline citations than full URLs (especially on mobile/messaging platforms) and matches academic/magazine citation style. Deduplicate by URL: the same URL seen twice gets the same number.
- **Classify source quality** for each source: `primary` (official docs, model cards, SEC filings, original papers), `secondary` (tech journalism, analyst reports, reviews), `tertiary` (Wikipedia, aggregators, forum posts). This tier appears in the final source table and signals evidence strength to the reader.
- **Grade each fact's evidence basis** as you extract (see below) — you can't tag a report you didn't grade while reading

### Verbatim snippet anchoring (mandatory for claims you store)

Every factual claim recorded in the store (`add-claim` / `add-evidence`) carries a **verbatim contiguous excerpt** from that source's page text: copied exactly — original language, no paraphrase, no splicing across paragraphs, no added ellipses — 8–1500 characters (a tighter supporting run, not a whole paragraph). Anchor it **at extraction time, not at gate time**: before storing, run the deterministic check

```
python3 <skill_dir>/scripts/research_validation.py check-quote \
  --dir <run_dir> --source-id <sid> --snippet "<copied excerpt>" [--snippet "..."]
```

(a `--file <path>` variant anchors against any saved page text; repeated `--snippet`s check in one call). The check is exact substring matching modulo Unicode whitespace runs — no tokenizer, so CJK and any script anchor reliably where the tokenized support scorer struggles. **Keep the claim text itself quote-shaped**: the support scorer supports a claim only when one stored snippet covers every figure/year/entity the claim carries — split multi-fact claims or byte-align the claim to its snippet (see Pitfalls; prose paraphrase stays in the report body).

- **On a mismatch (`ok: false`): repair once** — re-copy the excerpt exactly from the page text (the `hint` field tells you when only quote/dash style differs). Never massage the snippet toward the claim, never splice.
- **No contiguous supporting excerpt exists?** The claim is not evidence-backed. Store it honestly — as `[REASONED]`/interpretive without a stored quote, or accept that `verify-claims` will flag `unsupported`. A truthful red is the correct outcome; never fix it by editing the quote.
- **Self-verification from memory does not count** — recall-level eyeballing is exactly how paraphrases slip through. Run the script; it reads the page text from disk.

### Evidence basis — the four-label discipline

Tag every **material fact** with the basis on which you're asserting it. A material fact is any substantive claim a reader would act on or challenge: a statistic, date, named entity or relationship, causal claim, or direct quote. This is deep-research's adaptation of pere-toolkit's canonical evidence discipline — the **same four labels**, applied to *facts* rather than financial figures.

| Label | A fact is `[LABEL]` when it is… |
|---|---|
| `[VERIFIED]` | corroborated across ≥2 independent, cited, dated sources |
| `[SOURCED]` | stated by one named / cited source, not independently corroborated |
| `[REASONED]` | your own analytical judgement or inference — not stated by any source |
| `[ESTIMATED]` | a calculation or stated assumption (e.g. a figure you derived from source data) |

Rules:
- **Lead on `[VERIFIED]` / `[SOURCED]`.** Present `[REASONED]` / `[ESTIMATED]` claims as *indicative* ("likely", "suggests", "on these figures") — never as hard fact.
- **Use these four exact labels** — never an improvised synonym (`[Official]`, `[Expert]`, `[Consensus]` → these are `[SOURCED]`, or `[VERIFIED]` only if independently corroborated).
- **Don't restate precision you don't have** — a source's "about half" is `~50% [SOURCED]`, not `50.0%`.
- **Never fabricate to fill a gap** — an unanswerable sub-question is a documented gap, not a `[REASONED]` guess dressed as fact.

**Relationship to source-quality tiers:** the `primary`/`secondary`/`tertiary` tier (above) classifies the *source*; the `[VERIFIED]`/`[SOURCED]`/`[REASONED]`/`[ESTIMATED]` label classifies the *fact*. They are orthogonal: a fact from a single primary source is `[SOURCED]` (strong source, but uncorroborated); the same fact from two independent primary sources becomes `[VERIFIED]`. Use both: tier in the source table, label inline on each claim.

### 3d — Synthesis

After extracting from all sources in the round, integrate findings into the **cumulative research state**:

**Token budget awareness:** Track approximate context consumption across rounds. If the cumulative research state + extracted content is approaching the model's context window or a self-imposed budget (suggested: ~50K tokens for moderate, ~100K for complex), prioritize synthesis and stopping over gathering more sources. When the budget is tight, summarize earlier rounds' findings more aggressively rather than carrying full extracts forward.

**Passage selection over summarization** (adapted from upstream `source-context.ts`): when a must-keep source is huge, do not summarize its evidence away — select the **original passages** scoring highest on query-term overlap, keep them verbatim (they stay anchor-eligible for §3c), and mark elided spans. A generated paraphrase cannot later pass `check-quote`; a verbatim passage can. donsetch `web_fetch focus`/`section` does this natively; with built-in `web_extract`, re-read the on-disk full-text path around term-matching sections instead of trusting the truncated head+tail window.

**Rough estimation heuristic:** You can't count tokens precisely, but you can estimate: each `web_extract` returning ~5K characters contributes ~1.5K tokens; the research state after N rounds with 3-5 sources per round is roughly N × 8-12K tokens. If you're on round 3+ of a complex topic and the last `web_extract` returned >10K characters, you're likely past 50K — summarize aggressively and head toward synthesis. When in doubt, treat any round-3+ complex research as budget-tight.

```
## Research State (after Round N)
[evolving synthesis of all findings so far]

### Sub-question 1: [question]
Status: [answered / partially answered / unanswered]
Findings: [synthesized facts, each with a numbered inline citation [N] matching the source table, and an evidence-basis tag, e.g. "adoption grew 40% in 2025 [1] [VERIFIED]"]

### Sub-question 2: [question]
Status: [...]
Findings: [...]

### Gaps identified:
- [what's still missing for round N+1 to target]
```

Synthesis rules:
- **Deduplicate** — if multiple sources say the same thing, cite the best one (or cite both for corroboration)
- **Resolve contradictions** — if sources disagree, present both with attribution. Do not arbitrate silently.
- **Inline citations** — every factual claim references its source using the numbered citation `[N]` assigned in §3c, matching the source table
- **Evidence basis** — tag each material fact `[VERIFIED]` / `[SOURCED]` / `[REASONED]` / `[ESTIMATED]` (see §3c). A fact becomes `[VERIFIED]` only once ≥2 *independent* sources corroborate it; a single source is `[SOURCED]`. Corroboration during dedup is what promotes `[SOURCED]` → `[VERIFIED]`.
- **Update gap list** — what sub-questions are still unanswered or thin?

### 3e — Structured Evidence (recommended for reports with 5+ sources)

Before writing the final report, structure the extracted evidence into a lightweight `evidence.json` intermediate. This separates evidence gathering from report writing and makes fabrication detectable. See `references/structured-evidence-format.md` for the schema, source quality ranking/weighting rules, and worked example.

**When to use:** reports with 5+ sources, comparison/fact-check categories, or when the user may want to verify claims. Skip for quick 2-3 source reports.

**Benefits validated in side-by-side testing** (July 2026):
- Forced claim precision (every assertion gets a kind + polarity + snippet)
- Refute polarity requirement surfaced counter-evidence the iterative loop missed
- Source quality tiers revealed evidence-strength gaps (too many tertiary sources)
- Explicit gaps + contradictions sections in the final report
- Full traceability: claim ID → snippet → source URL

**Source quality ranking and weighting** (see `references/structured-evidence-format.md` for full rules):
- **primary** (3× weight): official docs, model cards, SEC filings, API pricing pages, original papers
- **secondary** (2× weight): tech journalism, analyst reports, benchmark aggregators
- **tertiary** (1× weight): Reddit, forums, Wikipedia, blog aggregators — useful for refute polarity and real-world anecdotes, but **never the sole support for a factual claim if a primary/secondary source exists**

**Quality distribution check before writing the report** (`verify-claims` computes it from the store as `source_quality`):
- **Healthy**: ≥30% primary, ≤30% tertiary → proceed
- **Acceptable**: ≥1 primary for key claims, <50% tertiary → note thin primary coverage as a gap
- **Weak**: 0 primary, >50% tertiary → **flag in Gaps section** and attempt to fetch primary sources (official docs, model cards, pricing pages) before finalizing. If primary sources are unavailable, qualify tertiary-sourced claims explicitly ("community reports suggest..." not "X is true")

**Conflict resolution by quality:** When sources disagree, primary > secondary > tertiary. 2 independent secondary sources ≈ 1 primary. Tertiary cannot override secondary/primary — it becomes refute counter-evidence or writing_context instead.

### 3f — Stopping Check

After synthesis (and optional evidence structuring), evaluate whether the report is comprehensive enough:

> Given the research plan's success criteria:
> - Are all key sub-questions addressed with at least one source?
> - Are there significant gaps or unanswered aspects?
> - Is the evidence sufficient and corroborated?
> - Am I approaching the token budget? (tight context = prioritize synthesis)
>
> Reply YES (stop) or NO (continue) + one-sentence reason.

**Stop if:**
- All sub-questions have ≥1 source → YES
- **Saturation ≤5% for 2 consecutive rounds** — new material findings this round ≤5% of all accumulated findings, two rounds running → YES (quantified convergence measure, adapted from Anjos2/recursive-research; the threshold is unvalidated upstream — treat as a strong signal, never a substitute for the qualitative checks below)
- Most of the complexity cap used (e.g. round 2 of 2 for simple, round 3 of 3 for moderate) and remaining gaps are minor → YES
- Complexity cap reached (simple=2, moderate=3, complex=5) → YES
- Token budget approaching limit → YES (synthesize with what you have)
- Web search returning diminishing returns (same URLs, no new info) → YES

**Continue if:**
- Major sub-questions unanswered → NO
- Contradictions unresolved → NO
- Only 1-2 rounds done and topic is broad → NO

## Step 4 — Final Report

Produce the final report. Minimum 800 words (scale with topic complexity).

**Output order is overview-first**: the reader gets the answer and the at-a-glance comparison *before* the detailed reasoning. Do not bury the comparison table after the per-topic analysis.

Carry each material fact's **evidence-basis tag** inline (§3c), lead on `[VERIFIED]` / `[SOURCED]`, keep `[REASONED]` / `[ESTIMATED]` claims framed as indicative, and paste the **Evidence key** legend below the Sources table so the tags decode.

**Synthesis prompt structure:** When writing the final report, explicitly consult: (1) the original question, (2) the research plan (sub-questions, success criteria), (3) the cumulative research state from all rounds, (4) the evidence.json if produced, and (5) the numbered source list. Do not rely on the cumulative state alone if it has been compressed across many rounds — go back to the per-round findings to verify key claims. This prevents detail loss when the research state was aggressively summarized due to token budget pressure.

### Structure

```markdown
# [Report Title]

> **Research date:** [date] · **Rounds:** [N] · **Sources:** [N] · **Category:** [type]

## Executive Summary
[2-3 paragraph overview of key findings — the answer up front. If using structured evidence, note claim count and refute count here so the reader knows the evidence base.]

## [Comparison Table | Overview | Key Findings at a Glance]
[For comparison reports: a markdown table comparing options/entities across criteria. For factual/explainer reports: a numbered list of key findings with claim references. This section gives the reader the complete picture in one screen — the detailed analysis below is the supporting reasoning, not the main event. If using structured evidence, cite claim IDs like [c1], [c3] in table cells or list items.]

## [## Section per sub-question]
[Detailed analysis with inline citations — this is the supporting reasoning for the overview above. Each section traces back to the overview claims.]

### [### Subsections as needed]
[...]

## Contradictions
[If sources disagree, present both sides with attribution. Do not silently arbitrate. If no contradictions found, state "No direct contradictions between sources." This section is REQUIRED — its absence is a quality signal that counter-evidence wasn't searched.]

## Gaps
[What couldn't be determined from available sources. Each gap should note: what's unknown, why it matters, and whether it could be resolved with more research. If using structured evidence, reference the writing_context items. If no gaps, state "No significant gaps identified." **Source-set bias check (mandatory):** the first gap line must state the bias your whole source set shares — one dominant language, era, school, jurisdiction, or industry — adapted from Munger inversion. A homogeneous source set is itself a gap, even when every individual source is primary-tier.]

## Conclusion
[Synthesis of findings, implications, remaining uncertainties — ties back to the executive summary and overview. The conclusion confirms or qualifies the overview, it doesn't introduce new analysis.]

---
## Sources

**Quality distribution:** [N] primary · [N] secondary · [N] tertiary — [healthy/acceptable/weak]

| # | Title | URL | Quality | Accessed |
|---|-------|-----|---------|----------|
| 1 | [title] | [url] | primary/secondary/tertiary | [date] |

**Citation format:** Inline citations use `[N]` matching the source table above. On first mention of a source, include `[N]` — subsequent mentions may use `[N]` alone. For claims from the same source, cite the number once per paragraph unless the source is paginated.

**Evidence key** — `[VERIFIED]` corroborated across ≥2 independent, cited, dated sources · `[SOURCED]` from one named source, not independently corroborated · `[REASONED]` analytical judgement / inference · `[ESTIMATED]` calculation or stated assumption.
```

### Category-specific overview sections

| Category | Overview section format |
|---|---|
| **comparison** | Markdown table comparing options across criteria, with a verdict row or column. The detailed sections below provide the reasoning per option. |
| **product** | Ranked list with pros/cons, price range, and a "top pick" callout. Detailed sections cover each product. |
| **how-to** | Numbered overview of the steps. Detailed sections cover prerequisites, execution, and troubleshooting per step. |
| **fact-check** | Evidence for/against the claim in a two-column table, with a preliminary verdict. Detailed sections assess source credibility and reasoning. |
| **explainer** | Numbered key findings or a "progressive depth" overview (simple → deep). Detailed sections go deeper per concept. Glossary if technical. |
| **factual** | Numbered key findings with claim references. Detailed sections provide the supporting evidence per finding. |

### Fallback report

If LLM synthesis fails (timeout, error, garbled output), compile raw findings into a basic report:
- List all findings grouped by sub-question
- Include source URLs and keep each finding's evidence-basis tag
- Add note: "This is a raw findings compilation; synthesis was not completed."
- Never output "No information could be gathered" if any sources were fetched — always compile what exists.

## Step 5 — Research Stats

After the report, output a compact stats block:

```
---
📊 Research stats: [duration] · [N] rounds · [N] queries · [N] page fetches · [N] sources cited · provider: [donsetch/built-in]
```

## Step 5.5 — Validation Gates (mandatory before delivery)

**Deterministic gates** — `scripts/research_validation.py`, stdlib-only, checks structure not judgment. Every report with 5+ sources passes three gates before delivery: `validate-report` (structure), `verify-citations` (inline `[N]` ↔ Sources rows), and `verify-claims --strict` (stored evidence must support each factual claim; a claim stored with `basis: verified` needs sources on ≥2 different sites; at least one `polarity: refute` claim, or `--refute-none "<what you searched>"`). **Loop:** validate → fix → re-run all three, max 3 cycles; still failing → stop and report the remaining problems to the user honestly. Never skip the gates, never deliver with a red gate. Quick 2-3 source reports (no store): `verify-claims` warns instead of failing — record it in the stats block. Full contract, flags, and the failure loop: `references/validation-gates.md`.

**Optional Jev pre-screen.** On instances with TypeSafe Jev configured, add `--jev-prescreen` to `verify-claims` for an advisory semantic pre-check that flags gate false-reds/false-greens before the deterministic run. It degrades to a clean SKIPPED line when Jev is not set up — never blocks, never changes the gate's exit code. See the contract in `references/validation-gates.md`.

**Snippet anchoring prerequisite.** `verify-claims` scores the *stored* snippets — it cannot tell a well-copied quote from a well-paraphrased one. That is what `check-quote` (§3c) is for: a red gate whose snippets never passed `check-quote` means anchoring was skipped, which is itself a defect. Anchor first, store second, gate third.

## Step 6 — Follow-up Report Revision (optional)

For "verify X in the earlier report" / "update the pricing section" requests on a delivered report. Adapted from upstream's evidence panel + `report-revision.ts`: a follow-up researches narrowly and patches **only the passages citing the finding** — the rest of the report stays byte-identical.

1. **Map.** `python3 <skill_dir>/scripts/research_validation.py map-citations --report <report.md> [--citation N]` returns the top-level blocks citing each `[N]` (code fences excluded; exit 1 = no block cites N). This defines exactly what a follow-up may touch — nothing else.
2. **Bounded follow-up research.** One round, ≤2 query directions derived from the target finding and the user's instruction. Same snippet-first triage and quality filter (§3b/§3c); new page text joins the existing run dir; register new sources before citing them.
3. **Patch cited blocks only.** Revise the blocks from step 1 (tables and lists are updated as whole blocks). Leave unrelated paragraphs untouched. If the evidence contradicts the existing claim, state the correction; if it is insufficient, say so instead of inventing a fix.
4. **Sources.** Append new entries to the Sources table with the next free numbers; never renumber existing citations — old inline `[N]`s must keep resolving.
5. **History.** Save the revision as `<name>-rev.md` next to the original (`-rev2`, `-rev3`, … for further rounds). The original file stays untouched; on failure or cancellation, nothing is saved.
6. **Re-run all three gates** (Step 5.5) on the revised report before delivery. A red gate after revision means the revision did not land cleanly — fix, don't ship.

## Follow-on Investment Analysis (optional)

When the report covers an investment question and the user provides deal parameters, build a quantitative pro-forma using `execute_code`. Always model the as-is use as a baseline. See `references/real-estate-investment-analysis.md` for the template.

See `references/structured-evidence-format.md` for the evidence.json schema and writing-context vs claims distinction.

## Vault Integration (optional)

For larger research tasks (10+ sources) or when the user may want to follow up with grounded Q&A:

1. Create a vault per `notebooklm-mode` at `<project_folder>/research-<topic>/`
2. Save each source as a numbered file in `sources/` with verbatim extracts
3. Use `ingest_source.py` to write + index atomically
4. After the report, tell the user: "Sources saved to vault at [path]. You can ask follow-up questions grounded in these sources — say 'notebooklm mode' to query the vault."

This is optional — the skill works fully without a vault for one-off reports.

## Subagent Mode (optional)

For genuinely parallel research across distinct sub-topics (e.g. researching 3 unrelated companies):

```
delegate_task(
  goal="Research [sub-topic] as part of a deep-research project. Run web searches, extract content, and return findings with source URLs and titles.",
  context="You are a research subagent. Topic: [sub-topic]. Sub-questions: [list]. Use web_search and web_extract. Return structured findings with citations.",
  toolsets=["web"]
)
```

**Rules:**
- Only use subagents when sub-topics are genuinely independent
- Collect results from all subagents, then synthesize yourself
- Never delegate the synthesis step — the orchestrator must see all findings
- Subagent summaries are self-reports — verify source URLs exist before citing

## Concurrency and Rate Limits

- Full-page fetches are on-demand and budgeted (§3b): ≤2/round, run-wide cap by complexity — snippets carry the triage
- If `web_extract` fails on a URL, note it and move on — don't retry endlessly
- If `web_search` returns no results, apply the §3a refinement protocol including the identical-rewrite stop

## Pitfalls

- **Overclaiming basis** — when torn between two labels, pick the weaker one. A source's "about half" stays `~50% [SOURCED]`.
- **Conflating claims with context** — subject facts are claims; scope, methodology, and availability limits are writing_context.
- **Subagent self-reports** — verify source URLs exist before citing. The orchestrator synthesizes.
- **Clarification: one round** — if the reply is still vague, proceed with the best interpretation of intent.
- **Complexity misclassification** — complexity is breadth of synthesis, not how impressive the topic sounds. A narrow factual topic with six sub-questions is moderate.
- **Token budget fills before the cap** — on long extractions, summarize aggressively when context is tight rather than waiting for the round ceiling.
- **Word-boundary matching** — "port" matching "transport" or "support" is a false hit; filter on topical relevance, not substring overlap.
- **Store claims are quote-shaped** — the deterministic scorer supports a claim only when ONE stored snippet covers every figure, year AND entity the claim text carries; anything else caps at `partial`−0.01 (strict red for factual). The law, validated live three times in one session: multi-fact claims split per snippet, claim text byte-aligns to its quote, and prose paraphrase stays in the report body. Instances of the same law: **CJK claims** extract no tokens, so even an identical snippet scores ~0.33 — byte-identical claim text (entity axis 1.0) or anchor via `check-quote` (tokenization-free) instead; **glommed capitalized runs** ("Scrape URL FIRECRAWL" → one entity `scrape url`) never set-match a claim that says "Firecrawl" alone; **alphanumeric brand prefixes** ("x402" → figure `402`) cap unless the snippet carries the brand text. Diagnose with the script's `_figures`/`_entities`/`_tokens` helpers before rewriting.
- **Anchored to the wrong substrate** — `check-quote --source-id` reads `pages/<source_id>.txt`; verify the id resolves to the URL the sentence actually came from before treating a mismatch as fabrication — the same sentence on another page's file gives a false red.
- **Unanchored snippets** — storing a snippet (or evidence) that never passed `check-quote` is how a smooth paraphrase becomes "evidence": the scorer sees familiar tokens and rates it supported. Verbatim excerpt, checked against the saved page text (`<run_dir>/pages/<source_id>.txt`), repair-once on mismatch — never massage the snippet toward the claim, never splice across paragraphs. No contiguous excerpt exists? The claim is not evidence-backed; store it honestly and let the gate flag it.
- **Store CLI ordering and field pairs** — the subcommand must precede `--dir` (`research_validation.py add-claim --dir <d> ...`, never `--dir <d> add-claim`). `add-claim` takes claim+kind+polarity+basis+snippet+source_id; `add-evidence` takes evidence_snippet+source_id — swapping the pairs stores the snippet in source_id and surfaces later as unregistered-source_id warnings. `basis` takes ONLY the four labels — a source TIER name (`primary`/`secondary`) is rejected (rc 2), and `kind` takes no `refute` value: refute is a **polarity**. When looping store calls in a script, check every response's JSON — a rejected call exits 2 silently while the loop's "stored" message lies.
- **Citation density in the body** — every Sources row must be cited at least once (`verify-citations` fails on uncited rows); required sections (`## Executive Summary`, `## Contradictions`, `## Gaps`, `## Conclusion`) must be `##`-level, not `#`.
- **Fallback if synthesis fails** — compile raw findings with citations and tags; empty output is the failure mode.
- **Evidence key** — paste the four-label legend under the Sources table so `[VERIFIED]` / `[SOURCED]` / `[REASONED]` / `[ESTIMATED]` decode.

## Related Work

[Odysseus](https://github.com/pewdiepie-archdaemon/odysseus) — PewDiePie's self-hosted AI workspace — includes a "Deep Research" feature with multi-step web research and source reading, conceptually similar to this skill's Think → Search → Extract → Synthesize → Stop loop. This skill is a pure-prompt workflow (no UI, no server) designed to run inside any agent's tool loop.

[AnotiaWang/deep-research-web-ui](https://github.com/AnotiaWang/deep-research-web-ui) (MIT) — Nuxt UI wrapping dzhng/deep-research with a hardened engine, and the main vendor source for this skill. **Vendored:** verbatim-quote evidence anchoring, v1.8.2 (`shared/utils/search-learning.ts` → `check-quote`, §3c); structured search mini-plans with frozen constraints, planning discipline and provider guidance, v1.9.0 (`shared/utils/search-plan.ts` → §3a); search-budget presets + breadth-halving estimate, v1.9.0 (`shared/utils/research-input.ts` → Step 1 + `estimate-budget`); bounded deep-dive threading on follow-up directions, v1.9.0 (`lib/core/deep-research.ts` → §3a); six-way round-outcome taxonomy with per-reason bounded retry, v1.9.1 (`shared/utils/search-assessment.ts` → §3a); snippet-first on-demand reading with fetch budgets, v1.9.0 (`lib/core/read-source.ts` → §3b); term-scored verbatim passage selection, v1.9.0 (`lib/core/source-context.ts` → §3d); surgical report revision with citation→block mapping, v1.9.0 (`shared/utils/report-revision.ts` → Step 6 + `map-citations`). **Evaluated, not vendored:** full tree recursion, streaming-JSON structured-output repair, UI/deployment layers, and dzhng's "the source is irrelevant" prompt (contradicts this skill's provenance discipline). Full two-sided map: `references/anotiawang-deep-research-concepts.md`.

[Anjos2/recursive-research](https://github.com/Anjos2/recursive-research) (MIT) — Claude Code prompt skill for long-cycle recursive research. **Vendored (v1.9.2, guidance-level):** saturation-based stop signal (§3f), coverage balancing across plan sub-questions (§3a), mandatory source-set bias check in the Gaps section (Step 4). **Not vendored:** cycle machinery, WDM weighted-source scoring, per-domain seed source lists, preventive context-pause thresholds, local-corpus mode. The ≤5% threshold is unvalidated upstream (repo last pushed 2026-04-22, no field hardening); it ships as a signal, not a rule. Map: `references/recursive-research-concepts.md`.

[DocsGPT](https://github.com/arc53/DocsGPT) (arc53, MIT) — ResearchAgent Plan → Research → Synthesize with adaptive depth, clarification, token-budget tracking, and empty-search refinement. Mapping: `references/docsgpt-concepts.md`.

`references/skills-monetization.md` — condensed AI-skills monetization knowledge bank (marketplaces, what sells, pricing) from the 2026-07-01 research dossier.

## Evals

`evals/routing-fixtures.json` holds lightweight contract fixtures — sample request →
expected routing, required output fields, and forbidden output patterns. They are
specs, not run against a live model; the repo-root `tests/test_routing_fixtures.py`
validates they stay well-formed and route to real skills.