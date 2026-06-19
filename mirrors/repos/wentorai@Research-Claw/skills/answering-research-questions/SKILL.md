---
name: answering-research-questions
description: Main orchestration workflow for systematic literature research - search, evaluate, traverse, synthesize via the rp_* tools pipeline (Scopus + OpenAlex)
when_to_use: When user asks a research question. When user wants to find specific data in literature. When starting comprehensive literature review. When user says "find papers about" or "what is known about".
version: 2.0.0
---

# Answering Research Questions

> **RC native tools** — this skill's pipeline ships as four built-in RC tools. Call them directly; do **not** shell out to any `rp.py` script or write curl:
> - `rp_search({ query, limit?, min_year? })` — Scopus relevance search enriched with OpenAlex abstracts + OA PDF links. The Elsevier key is built in.
> - `rp_abstracts({ dois })` — batch abstracts + OA links for a DOI list (OpenAlex, no key).
> - `rp_cite({ doi, direction?, limit? })` — citation traversal (`direction`: `both` / `backward` / `forward`).
> - `rp_fulltext({ doi, out? })` — OA full text (Elsevier ScienceDirect OA → OpenAlex OA fallback); pass `out` to also save the text to a file.
>
> Results return inline as JSON (there is no `--json <file>` flag). To persist a result set, save the returned JSON with the workspace file tools.


## Overview

Orchestrate the complete research workflow from query to findings.

**Core principle:** Systematic, trackable, comprehensive. Search → Evaluate → Traverse → Synthesize.

**Announce at start:** "I'm using the Answering Research Questions skill to find [specific data] about [topic]."

## The Process

### Phase 1: Parse Query

Extract from user's request:

**Keywords:**
- Main concepts (e.g., "BTK inhibitor", "selectivity")
- Synonyms and alternatives (e.g., "Bruton tyrosine kinase")
- Related terms (e.g., "off-target", "kinase panel")

**Data types needed:**
- Specific measurements (IC50, KD, EC50, etc.)
- Methods or protocols
- Structures or sequences
- Results or conclusions

**Constraints:**
- Date ranges
- Specific compounds/targets
- Organisms or systems
- Publication types

**Ask clarifying questions if needed:**
- "Are you looking for in vitro or in vivo data?"
- "Any specific time frame?" (maps to `PUBYEAR > Y` in the Scopus query)
- "Which kinases are you most interested in?"

### Phase 2: Initialize Research Session

**Propose folder name:**
```
research-sessions/YYYY-MM-DD-brief-description/
```

Example: `research-sessions/2025-10-11-btk-inhibitor-selectivity/`

**Show proposal to user:**
```
📁 Creating research folder: research-sessions/2025-10-11-btk-inhibitor-selectivity/
   Proceed? (y/n)
```

**Create folder structure:**
```bash
mkdir -p "research-sessions/YYYY-MM-DD-description"/{papers,citations}
```

**Initialize files:**

**Core files (always create these):**

**papers-reviewed.json:**
```json
{}
```

**citations/citation-graph.json:**
```json
{}
```

**SUMMARY.md:**
```markdown
# Research Query: [User's question]

**Started:** YYYY-MM-DD HH:MM
**Keywords:** keyword1, keyword2, keyword3
**Data types sought:** IC50 values, selectivity data, synthesis methods

---

## Highly Relevant Papers (Score ≥ 8)

Papers scored using `evaluating-paper-relevance` skill:
- Score 0-10 based on: Keywords (0-3) + Data type (0-4) + Specificity (0-3)
- Score ≥ 8: Highly relevant with significant data
- Score 7: Relevant with useful data
- Score 5-6: Possibly relevant
- Score < 5: Not relevant

(Papers will be added here as found)

Example format:
### [Paper Title](https://doi.org/10.1234/example)
**DOI:** [10.1234/example](https://doi.org/10.1234/example) | **Cited by:** 42 | **OA:** openalex-oa

---

## Relevant Papers (Score 7)

(Papers will be added here as found)

---

## Possibly Relevant Papers (Score 5-6)

(Noted for potential follow-up)

---

## Search Progress

- Initial Scopus search: X results
- Papers reviewed: Y
- Papers with relevant data: Z
- Citations followed: N

---

## Key Findings

(Synthesized findings will be added as research progresses)
```

**CRITICAL: Always use clickable markdown links for DOIs** (`https://doi.org/...`)

**Auxiliary files (for large searches >100 papers):**

See `evaluating-paper-relevance` skill for guidance on when to create:
- **README.md** - Project overview, methodology, file inventory
- **TOP_PRIORITY_PAPERS.md** - Curated priority list organized by tier
- **evaluated-papers.json** - Rich structured data for programmatic access

For small searches (<50 papers), stick to core files only. For large searches (>100 papers), auxiliary files add significant organizational value.

### Phase 3: Search Literature

**Use searching-literature skill (`rp_search`):**

1. Construct a **Scopus** query from keywords (`TITLE-ABS-KEY(...)`, `AND/OR`, `W/n`,
   `PUBYEAR > Y`, `DOCTYPE(ar)`).
2. Run it; this also enriches every hit with OpenAlex abstracts + OA links in one pass:
   ```bash
   rp_search "TITLE-ABS-KEY(<terms>)" \
       --limit 100 --min-year 2015
   ```
3. Records land in `initial-search-results.json` with abstracts already attached (so
   Phase 4 scores from disk — no re-fetch).
4. Report: "🔎 Scopus: N papers · M with abstracts (OpenAlex)".

### Phase 4: Evaluate Papers

**Use evaluating-paper-relevance skill:**

For each paper:
1. Check papers-reviewed.json (skip if already processed)
2. Stage 1: Score the abstract already in the record (0-10)
3. If score ≥ 7: Stage 2 deep dive — `rp_fulltext <doi> --out papers/<slug>.xml`
4. Extract findings to SUMMARY.md
5. Save OA full text / pdf link returned by `rp_fulltext` (if `available`)
6. **Update papers-reviewed.json (for ALL papers, even low-scoring ones)**
7. If score ≥ 7: proceed to Phase 5 for this paper

**CRITICAL: Add every paper to papers-reviewed.json regardless of score. This prevents re-review and tracks complete search history.**

**Report progress for EVERY paper:**
```
📄 [15/100] Screening: "Paper Title"
   Abstract score: 8 → Fetching full text...
   ✓ Found IC50 data for 8 compounds
   → Added to SUMMARY.md

📄 [16/100] Screening: "Another Paper"
   Abstract score: 3 → Skipping (not relevant)

📄 [17/100] Screening: "Third Paper"
   Abstract score: 7 → Relevant, adding to queue...
```

**Every 10 papers, give summary update**

### Phase 5: Traverse Citations

**Use traversing-citations skill (`rp_cite`, OpenAlex):**

For papers scoring ≥ 7:
1. `rp_cite <doi> --direction both --limit 50`
   (backward = references, forward = citing papers, abstracts attached)
2. Filter for relevance (score ≥ 5)
3. Add to processing queue
4. Evaluate queued papers (return to Phase 4)

**Report progress:**
```
🔗 Following citations from highly relevant paper
   → Found 12 relevant references
   → Found 8 relevant citing papers
   → Adding 20 papers to queue
```

### Phase 6: Checkpoint

**Check after:**
- Every 50 papers reviewed
- Every 5 minutes of processing
- Queue exhausted

**Ask user:**
```
⏸️  Checkpoint: Reviewed 50 papers, found 12 relevant
    Papers with data: 7
    Continue searching? (y/n/summary)
```

**Options:**
- `y` - Continue processing
- `n` - Stop and finalize
- `summary` - Show current findings, then decide

### Phase 7: Synthesize Findings

**When stopping (user says no or queue empty):**

**Option A: Manual synthesis (small research sessions)**
1. **Review SUMMARY.md** - Organize by relevance and topic
2. **Extract key findings** - Group by data type
3. **Add synthesis section:**

```markdown
## Key Findings Summary

### IC50 Values for BTK Inhibitors
- Compound A: 12 nM (Smith et al., 2023)
- Compound B: 45 nM (Doe et al., 2024)
- [More compounds...]

### Selectivity Data
- Compound A shows >80-fold selectivity vs other kinases
- Tested against panel of 50 kinases (Jones et al., 2023)

### Synthesis Methods
- Lead compounds synthesized via [method]
- Yields: 30-45%
- Full protocols in [papers]

### Gaps Identified
- No data on selectivity vs [specific kinase]
- Limited in vivo data
- Few papers on resistance mechanisms
```

4. **Update search progress stats**
5. **List all files downloaded**

**Option B: Script-based synthesis (large research sessions >50 papers)**

For large research sessions, consider creating a synthesis script:

**create `generate_summary.py`:**
- Read `evaluated-papers.json` from helper scripts
- Aggregate findings by priority and scaffold type
- Generate comprehensive SUMMARY.md with:
  - Executive summary with statistics
  - Papers grouped by relevance score
  - Priority recommendations for next steps
  - Methodology documentation
- Include timestamps and reproducibility info

**Benefits:**
- Consistent formatting across sessions
- Easy to regenerate as more papers added
- Can customize grouping/filtering logic
- Documents complete methodology

**Final report:**
```
✅ Research complete!

📊 Summary:
   - Papers reviewed: 127
   - Relevant papers: 18
   - Highly relevant: 7
   - Data extracted: IC50 values for 45 compounds, selectivity data, synthesis methods

📁 All findings in: research-sessions/2025-10-11-btk-inhibitor-selectivity/
   - SUMMARY.md (organized findings)
   - papers/ (14 PDFs + supplementary data)
   - papers-reviewed.json (complete tracking)
```

### Phase 8: Final Consolidation

**CRITICAL: Always consolidate findings at the end**

#### 1. Create relevant-papers.json

**Filter papers-reviewed.json to extract only relevant papers (score ≥ 7):**

```python
# Read papers-reviewed.json
with open('papers-reviewed.json') as f:
    all_papers = json.load(f)

# Filter for relevant papers (score >= 7)
relevant_papers = {
    doi: data for doi, data in all_papers.items()
    if data.get('score', 0) >= 7
}

# Save to relevant-papers.json
with open('relevant-papers.json', 'w') as f:
    json.dump(relevant_papers, f, indent=2)
```

**Format:**
```json
{
  "10.1234/example1.2023": {
    "title": "Paper title",
    "status": "highly_relevant",
    "score": 9,
    "source": "scopus_search",
    "timestamp": "2025-10-11T16:00:00Z",
    "found_data": ["IC50 values", "synthesis methods"],
    "full_text_source": "openalex-oa"
  },
  "10.1234/example2.2023": {
    "title": "Another paper",
    "status": "relevant",
    "score": 7,
    "source": "forward_citation",
    "timestamp": "2025-10-11T16:15:00Z",
    "found_data": ["MIC data"]
  }
}
```

#### 2. Enhance SUMMARY.md with Methodology Section

**Add these sections to the TOP of existing SUMMARY.md (before paper listings):**

```markdown
# Research Query: [User's question]

**Date:** 2025-10-11
**Duration:** 2h 15m
**Status:** Complete

---

## Search Strategy

**Keywords:** BTK, Bruton tyrosine kinase, inhibitor, selectivity, off-target, kinase panel, IC50
**Data types sought:** IC50 values, selectivity data, kinase panel screening
**Constraints:** None (open date range)

**Scopus Query:**
```
TITLE-ABS-KEY(("BTK" OR "Bruton tyrosine kinase") AND (inhibitor OR "kinase inhibitor") AND (selectivity OR "off-target"))
```

---

## Screening Methodology

**Rubric:** Abstract scoring (0-10) — Keywords (0-3) + Data type (0-4) + Specificity (0-3).
- Threshold: ≥7 = relevant.

**Sources:**
- Discovery + ranking + citation counts: **Scopus** (`rp_search`)
- Abstracts + OA full-text links: **OpenAlex** (`rp_search`/`abstracts`/`fulltext`)
- Forward/backward citations: **OpenAlex** (`rp_cite`)

---

## Results Statistics

**Papers Screened:**
- Total reviewed: 127 papers
- Highly relevant (≥8): 12 papers
- Relevant (7): 18 papers
- Possibly relevant (5-6): 23 papers
- Not relevant (<5): 74 papers

**Data Extracted:**
- IC50 values: 45 compounds across 12 papers
- Selectivity data: 8 papers with kinase panel screening
- Full text obtained: 18/30 relevant papers (60%)

**Citation Traversal:**
- Papers with citations followed: 7
- References screened: 45 papers
- Citing papers screened: 38 papers
- Relevant papers found via citations: 8 papers

---

## Key Findings Summary

### IC50 Values for BTK Inhibitors
- Ibrutinib: 0.5 nM (Smith et al., 2023)
- Acalabrutinib: 3 nM (Doe et al., 2024)
- [Additional findings synthesized from papers below]

### Selectivity Patterns
- Most inhibitors show >50-fold selectivity vs other kinases
- Common off-targets: TEC, BMX (other TEC family kinases)

### Gaps Identified
- Limited data on selectivity vs JAK/SYK
- Few papers on resistance mechanisms
- No in vivo selectivity data found

---

## File Inventory

- `SUMMARY.md` - This file (methodology + findings)
- `relevant-papers.json` - 30 relevant papers (score ≥7)
- `papers-reviewed.json` - All 127 papers screened
- `papers/` - 18 PDFs + 5 supplementary files
- `citations/citation-graph.json` - Citation relationships

---

## Reproducibility

**To reproduce:**
1. Run the Scopus query above via `rp_search`
2. Apply screening rubric (threshold ≥7)
3. Follow citations from highly relevant papers (≥8) via `rp_cite`
4. Retrieve OA full text via `rp_fulltext`

**Software:** Research Superpowers skills (Scopus + OpenAlex pipeline)

---

[Existing paper listings follow below...]

## Highly Relevant Papers (Score ≥ 8)

### [Paper Title]...
```

**Report to user:**
```
✅ Research session complete!

📄 Consolidation complete:
   1. SUMMARY.md - Enhanced with methodology, statistics, and findings
   2. relevant-papers.json - 30 relevant papers (score ≥7) in JSON format

📁 All files in: research-sessions/2025-10-11-btk-inhibitor-selectivity/
   - SUMMARY.md (complete: methodology + paper-by-paper findings)
   - relevant-papers.json (30 relevant papers for programmatic access)
   - papers-reviewed.json (127 total papers screened)
   - papers/ (18 PDFs)

🔍 Quick access:
   - Open SUMMARY.md for complete findings and methodology
   - Use relevant-papers.json for programmatic access

💡 Optional: Clean up intermediate files?
   → Use cleaning-up-research-sessions skill to safely remove temporary files
```

## Workflow Checklist

**Use TodoWrite to track these steps:**

- [ ] Parse user query (keywords, data types, constraints)
- [ ] Propose and create research folder
- [ ] Initialize tracking files (SUMMARY.md, papers-reviewed.json, citation-graph.json)
- [ ] Search Scopus via `rp_search` (searching-literature skill)
- [ ] For each paper: evaluate using evaluating-paper-relevance skill
- [ ] For relevant papers (≥7): traverse citations using traversing-citations skill
- [ ] Report progress regularly
- [ ] Checkpoint every 50 papers or 5 minutes
- [ ] When done: synthesize findings and enhance SUMMARY.md with methodology
- [ ] Create relevant-papers.json (filtered JSON for programmatic access)
- [ ] Final report with stats and file locations

## Integration Points

**Skills used:**
1. `searching-literature` - Scopus search + OpenAlex enrichment (`rp_search`)
2. `evaluating-paper-relevance` - Score abstracts, extract from OA full text (`rp_fulltext`)
3. `traversing-citations` - Follow citation networks via OpenAlex (`rp_cite`)

**All skills coordinate through:**
- Shared `papers-reviewed.json` (deduplication)
- Shared `SUMMARY.md` (findings accumulation)
- Shared `citation-graph.json` (relationship tracking)

**File organization:**
- **Small searches (<50 papers):** Core files only (papers-reviewed.json, SUMMARY.md, citation-graph.json)
- **All searches:** Create relevant-papers.json at end; enhance SUMMARY.md with methodology
- **Large searches (>100 papers):** May add auxiliary files (README.md, TOP_PRIORITY_PAPERS.md, evaluated-papers.json) for better organization

## Error Handling

**No results found:**
- Try broader keywords
- Remove constraints
- Check spelling
- Try different synonyms

**API rate limiting:**
- `rp_lib` already rate-limits per host and retries 429/5xx with backoff — usually no
  action needed.
- Scopus has a hard **20k results/week** quota on the personal key; if a sweep is huge,
  warn the user before burning it.

**Full text unavailable:**
- `rp_fulltext` returned `available:false` → no OA copy exists.
- Note in SUMMARY.md (`⚠️ paywalled - no OA`), continue with abstract-only evaluation.

**Too many results:**
- Narrow the Scopus query (`AND`, `PUBYEAR > Y`, `DOCTYPE(ar)`, tighter `TITLE-ABS-KEY`).
- Process first 100 by relevancy, ask before continuing.

## Quick Reference

| Phase | Skill | Output |
|-------|-------|--------|
| Parse | (built-in) | Keywords, data types, constraints |
| Initialize | (built-in) | Folder, SUMMARY.md, tracking files |
| Search | searching-literature (`rp_search`) | Scopus hits + OpenAlex abstracts/OA links |
| Evaluate | evaluating-paper-relevance | Scored papers, extracted findings |
| Traverse | traversing-citations | Additional papers from citations |
| Synthesize | (built-in) | Enhanced SUMMARY.md with methodology + findings |
| Consolidate | (built-in) | relevant-papers.json (filtered to score ≥7) |

## Common Mistakes

**Not tracking all papers:** Only adding relevant papers to papers-reviewed.json → Add EVERY paper to prevent re-review, track complete history
**Creating unnecessary auxiliary files for small searches:** For <50 papers, stick to core files (papers-reviewed.json, SUMMARY.md, citation-graph.json). For large searches (>100 papers), auxiliary files like README.md and TOP_PRIORITY_PAPERS.md add value.
**Silent work:** User can't see progress → Report EVERY paper, give updates every 10
**Non-clickable identifiers:** Plain text DOIs → Always use markdown links (https://doi.org/...)
**Jumping to evaluation without good search:** Too narrow results → Optimize search first
**Not tracking papers:** Re-reviewing same papers → Always use papers-reviewed.json
**Following all citations:** Exponential explosion → Filter before traversing
**No checkpoints:** User loses context → Report and ask every 50 papers
**Poor synthesis:** Just list papers → Group by data type, extract key findings
**Batch reporting:** Reporting 20 papers at once → Report each one as you go

## User Communication (CRITICAL)

**NEVER work silently! User needs continuous feedback.**

**Report frequency:**
- **Every paper:** Brief status as you screen (`📄 [N/Total] Title... Score: X`)
- **Every 5-10 papers:** Progress summary with counts
- **Every finding:** Immediately report what data you found
- **Every decision point:** Ask before changing direction

**Be specific in progress reports:**
- ✅ "Found IC50 = 12 nM for compound 7 (Table 2)"
- ❌ "Found data"
- ✅ "Screening paper 25/127: Not relevant (score 3)"
- ❌ Silently skip papers

**Ask for clarification when needed:**
- ✅ "Are you looking for in vitro or in vivo IC50 values?"
- ❌ Assume and potentially waste time

**Report blockers immediately:**
- ✅ "⚠️ Paper behind paywall - evaluating from abstract only"
- ❌ Silently skip without mentioning

**Periodic summaries (every 10-15 papers):**
```
📊 Progress update:
   - Reviewed: 30/127 papers
   - Highly relevant: 3 (scores 8-10)
   - Relevant: 5 (score 7)
   - Currently: Screening paper 31...
```

**Why:** User can course-correct early, knows work is happening, can stop if needed

## Success Criteria

Research session successful when:
- All relevant papers found and evaluated
- Specific data extracted and organized
- Citations followed systematically
- No duplicate processing
- Clear SUMMARY.md with actionable findings
- User questions answered with evidence

## Next Steps

After completing research:
- User reviews SUMMARY.md and relevant-papers.json
- **Optional**: Run cleaning-up-research-sessions skill to remove intermediate files
- May request deeper dive into specific papers
- May request follow-up searches with refined keywords
- May archive or share research session folder
