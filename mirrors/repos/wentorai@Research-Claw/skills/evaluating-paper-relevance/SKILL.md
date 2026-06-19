---
name: evaluating-paper-relevance
description: Two-stage paper screening - score OpenAlex abstracts, then deep dive into OA full text for specific data extraction
when_to_use: After literature search returns results. When need to determine if paper contains specific data. When screening papers for relevance. When extracting methods, results, data from papers.
version: 2.0.0
---

# Evaluating Paper Relevance

> **RC native tools** — this skill's pipeline ships as four built-in RC tools. Call them directly; do **not** shell out to any `rp.py` script or write curl:
> - `rp_search({ query, limit?, min_year? })` — Scopus relevance search enriched with OpenAlex abstracts + OA PDF links. The Elsevier key is built in.
> - `rp_abstracts({ dois })` — batch abstracts + OA links for a DOI list (OpenAlex, no key).
> - `rp_cite({ doi, direction?, limit? })` — citation traversal (`direction`: `both` / `backward` / `forward`).
> - `rp_fulltext({ doi, out? })` — OA full text (Elsevier ScienceDirect OA → OpenAlex OA fallback); pass `out` to also save the text to a file.
>
> Results return inline as JSON (there is no `--json <file>` flag). To persist a result set, save the returned JSON with the workspace file tools.


## Overview

Two-stage screening process: quick abstract scoring followed by deep dive into promising papers.

**Core principle:** Precision over breadth. Find papers that actually contain the specific data/methods user needs, not just topically related papers.

## When to Use

Use this skill when:
- Have list of papers from search
- Need to determine which papers have relevant data
- User asks for specific information (measurements, protocols, datasets, etc.)
- Screening papers one-by-one
- Any research domain (medicinal chemistry, genomics, ecology, computational methods, etc.)

## Choosing Your Approach

**Small searches (<50 papers):**
- Manual screening with progress reporting
- Use papers-reviewed.json + SUMMARY.md only
- No helper scripts needed
- Report progress to user for every paper

**Large searches (50-150 papers):**
- Consider helper scripts (screen_papers.py + deep_dive_papers.py)
- Use Progressive Enhancement Pattern (see Helper Scripts section)
- Create README.md with methodology
- May want TOP_PRIORITY_PAPERS.md for quick reference
- Use richer JSON structure (evaluated-papers.json categorized by relevance)
- Consider using subagent-driven-review skill for parallel screening

**Very large searches (>150 papers):**
- Definitely use helper scripts with Progressive Enhancement Pattern
- Create full auxiliary documentation suite (README.md, TOP_PRIORITY_PAPERS.md)
- Consider citation network analysis
- Plan for multi-week timeline
- Strongly consider subagent-driven-review skill for parallelization
- May need multiple consolidation checkpoints

## Two-Stage Process

### Stage 1: Abstract Screening (Fast)

**Goal:** Quickly identify promising papers

**Abstracts are already in the records.** `searching-literature` (`rp_search`) attaches
the OpenAlex abstract to each candidate, so screen from the record you already have — do
not re-fetch. If a record has `"abstract": ""` (OpenAlex coverage gap, ~20-50% of closed
papers), score from **title + journal + citation count** and flag `⚠️ No abstract`; never
silently drop it. To pull abstracts for a loose DOI list (e.g. citation traversal output),
use `rp_abstracts <doi> ...`.

**Score 0-10 based on:**
- **Keywords match (0-3 points)**: Does abstract mention key terms relevant to the query?
- **Data type match (0-4 points)**: Does it mention the specific information user needs?
  - Examples: measurements (IC50, expression levels, population sizes), protocols, datasets, structures, sequences, code
- **Specificity (0-3 points)**: Is it specific to user's question or just general background/review?

**Decision rules:**
- Score < 5: Skip (not relevant)
- Score 5-6: Note in summary as "possibly relevant" but skip for now
- Score ≥ 7: Proceed to Stage 2 (deep dive)

**IMPORTANT: Report to user for EVERY paper:**
```
📄 [N/Total] Screening: "Paper Title"
   Abstract score: 8 → Fetching full text...
```

or

```
📄 [N/Total] Screening: "Paper Title"
   Abstract score: 4 → Skipping (insufficient relevance)
```

**Never screen silently** - user needs to see progress happening

### Stage 2: Deep Dive (Thorough)

**Goal:** Extract specific data/methods from promising papers

#### 1. Fetch Full Text (one command)

`rp_fulltext` is the single entry point. It tries, in order, and returns the first that works:

1. **Elsevier ScienceDirect** — for Elsevier-prefix DOIs (`10.1016`, `10.1006`, ...) that
   are open access on the personal key; returns the article XML text inline.
2. **OpenAlex `best_oa_location`** — for everything else; returns an `oa_pdf_url` to the
   free version (repository, preprint, publisher OA), if one exists.

```bash
# Get a verdict + (for Elsevier OA) the text saved to disk
rp_fulltext "10.1016/j.cell.2023.01.001" --out papers/cell2023.xml
```

Returns one of:
```json
{"available": true,  "source": "elsevier-oa",  "saved_to": "papers/cell2023.xml", "chars": 84210}
{"available": true,  "source": "openalex-oa",  "pdf_url": "https://.../paper.pdf"}
{"available": false, "source": "elsevier"}        // Elsevier DOI but paywalled
{"available": false, "source": "not-elsevier"}    // non-Elsevier + no OA copy found
```

**Handling each case:**
- `elsevier-oa` → the XML text is on disk; grep/scan it (next step).
- `openalex-oa` → fetch the `pdf_url` (it's a free copy) and read it.
- `available: false` → **no free full text exists.** Note in SUMMARY.md
  `⚠️ Full text paywalled - no OA version`, then score from **abstract only**. Do not
  hand-write curl to publisher pages or Unpaywall — `the rp_* tools` already consulted OpenAlex's
  OA index, which subsumes Unpaywall coverage.

Report to user:
```
⚠️  No open-access full text - continuing with abstract only
```
or
```
✓ Open-access full text retrieved (openalex-oa)
```

#### 2. Scan for Relevant Content

**Focus on sections:**
- **Methods**: Experimental procedures, protocols
- **Results**: Data tables, figures, measurements
- **Tables/Figures**: Often contain the specific data user needs
- **Supplementary Information**: Additional data, extended methods

**What to look for (adapt to research domain):**
- Specific data user requested
  - **Medicinal chemistry**: IC50 values, compound structures, SAR data
  - **Genomics**: Gene expression levels, sequences, variant data
  - **Ecology**: Population measurements, species counts, environmental parameters
  - **Computational**: Algorithms, code availability, performance benchmarks
  - **Clinical**: Patient outcomes, treatment protocols, sample sizes
- Methods/protocols described in detail
- Statistical analysis and significance
- Data availability statements
- Code/data repositories mentioned

**Use grep/text search (adapt search terms):**
```bash
# Examples for different domains
grep -i "IC50\|Ki\|MIC" paper.xml                    # Medicinal chemistry
grep -i "expression\|FPKM\|RNA-seq" paper.xml        # Genomics
grep -i "abundance\|population\|sampling" paper.xml  # Ecology
grep -i "algorithm\|github\|code" paper.xml          # Computational
```

#### 3. Extract Findings

**Create structured extraction (adapt to research domain):**

**Example 1: Medicinal chemistry**
```json
{
  "doi": "10.1234/medchem.2023",
  "title": "Novel kinase inhibitors...",
  "relevance_score": 9,
  "findings": {
    "data_found": [
      "IC50 values for compounds 1-12 (Table 2)",
      "Selectivity data (Figure 3)",
      "Synthesis route (Scheme 1)"
    ],
    "key_results": [
      "Compound 7: IC50 = 12 nM",
      "10-step synthesis, 34% yield"
    ]
  }
}
```

**Example 2: Genomics**
```json
{
  "doi": "10.1234/genomics.2023",
  "title": "Gene expression in disease...",
  "relevance_score": 8,
  "findings": {
    "data_found": [
      "RNA-seq data for 50 samples (GEO: GSE12345)",
      "Differential expression results (Table 1)",
      "Gene set enrichment analysis (Figure 4)"
    ],
    "key_results": [
      "123 genes upregulated (FDR < 0.05)",
      "Pathway enrichment: immune response"
    ]
  }
}
```

**Example 3: Computational methods**
```json
{
  "doi": "10.1234/compbio.2023",
  "title": "Novel alignment algorithm...",
  "relevance_score": 9,
  "findings": {
    "data_found": [
      "Algorithm pseudocode (Methods)",
      "Code repository (github.com/user/tool)",
      "Benchmark results (Table 2)"
    ],
    "key_results": [
      "10x faster than BLAST",
      "98% accuracy on test dataset"
    ]
  }
}
```

#### 4. Download Materials

**PDFs:**
```bash
# If PDF available
curl -L -o "papers/$(echo $doi | tr '/' '_').pdf" "https://doi.org/$doi"
```

**Supplementary data:**
```bash
# Download SI files if URLs found
curl -o "papers/${doi}_supp.zip" "https://publisher.com/supp/file.zip"
```

#### 5. Update Tracking Files

**CRITICAL: Use ONLY papers-reviewed.json and SUMMARY.md. Do NOT create custom tracking files.**

**CRITICAL: Add EVERY paper to papers-reviewed.json, regardless of score. This prevents re-reviewing papers and tracks complete search history.**

**Add to papers-reviewed.json:**

**For relevant papers (score ≥7):**
```json
{
  "10.1234/example.2023": {
    "status": "relevant",
    "score": 9,
    "source": "scopus_search",
    "timestamp": "2025-10-11T10:30:00Z",
    "found_data": ["IC50 values", "synthesis methods"],
    "has_full_text": true,
    "full_text_source": "openalex-oa"
  }
}
```

**For not-relevant papers (score <7):**
```json
{
  "10.1234/another.2023": {
    "status": "not_relevant",
    "score": 4,
    "source": "scopus_search",
    "timestamp": "2025-10-11T10:31:00Z",
    "reason": "no activity data, review paper"
  }
}
```

**Always add papers even if skipped** - this prevents re-processing and documents what was already checked.

**Add to SUMMARY.md (examples for different domains):**

**Medicinal chemistry example:**
```markdown
### [Novel kinase inhibitors with improved selectivity](https://doi.org/10.1234/medchem.2023) (Score: 9)

**DOI:** [10.1234/medchem.2023](https://doi.org/10.1234/medchem.2023)
**Journal:** J. Med. Chem. · **Cited by:** 42 · **OA:** openalex-oa

**Key Findings:**
- IC50 values for 12 inhibitors (Table 2)
- Compound 7: IC50 = 12 nM, >80-fold selectivity
- Synthesis route (Scheme 1, page 4)

**Files:** PDF, supplementary data
```

**Genomics example:**
```markdown
### [Transcriptomic analysis of disease progression](https://doi.org/10.1234/genomics.2023) (Score: 8)

**DOI:** [10.1234/genomics.2023](https://doi.org/10.1234/genomics.2023)
**Data:** [GEO: GSE12345](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE12345)

**Key Findings:**
- RNA-seq data: 50 samples, 3 conditions
- 123 differentially expressed genes (FDR < 0.05)
- Immune pathway enrichment (Figure 3)

**Files:** PDF, supplementary tables with gene lists
```

**Computational methods example:**
```markdown
### [Fast sequence alignment with novel algorithm](https://doi.org/10.1234/compbio.2023) (Score: 9)

**DOI:** [10.1234/compbio.2023](https://doi.org/10.1234/compbio.2023)
**Code:** [github.com/user/tool](https://github.com/user/tool)

**Key Findings:**
- New alignment algorithm (pseudocode in Methods)
- 10x faster than BLAST, 98% accuracy
- Benchmark datasets available

**Files:** PDF, code repository linked
```

**IMPORTANT: Always make DOIs clickable links:**
- DOI format: `[10.1234/example.2023](https://doi.org/10.1234/example.2023)`
- Makes papers easy to access directly from SUMMARY.md

## Progress Reporting

**CRITICAL: Report to user as you work - never work silently!**

**For every paper, report:**
1. **Start screening:** `📄 [N/Total] Screening: "Title..."`
2. **Abstract score:** `Abstract score: X/10`
3. **Decision:** What you're doing next (fetching full text / skipping / etc)

**For relevant papers, report findings immediately (adapt to domain):**

**Medicinal chemistry example:**
```
📄 [15/127] Screening: "Selective BTK inhibitors..."
   Abstract score: 8 → Fetching full text...
   ✓ Found IC50 data for 8 compounds (Table 2)
   ✓ Selectivity data vs 50 kinases (Figure 3)
   → Added to SUMMARY.md
```

**Genomics example:**
```
📄 [23/89] Screening: "Gene expression in liver disease..."
   Abstract score: 9 → Fetching full text...
   ✓ RNA-seq data available (GEO: GSE12345)
   ✓ 123 DEGs identified (Table 1, FDR < 0.05)
   → Added to SUMMARY.md
```

**Computational methods example:**
```
📄 [7/45] Screening: "Novel phylogenetic algorithm..."
   Abstract score: 8 → Fetching full text...
   ✓ Code available (github.com/user/tool)
   ✓ Benchmark results (10x faster, Table 2)
   → Added to SUMMARY.md
```

**Update user every 5-10 papers with summary:**
```
📊 Progress: Reviewed 30/127 papers
   - Highly relevant: 3
   - Relevant: 5
   - Currently screening paper 31...
```

**Why this matters:** User needs to see work happening and provide feedback/corrections early

## Integration with Other Skills

**Full text:**
- Always go through `rp_fulltext` (Elsevier-OA → OpenAlex-OA). It already
  consults OpenAlex's OA index, so there is no separate Unpaywall/PMC step to run.

**After finding relevant paper:**
1. **Extract findings** to SUMMARY.md
2. **Download files** to papers/ folder
3. **Call traversing-citations skill** to find related papers
4. **Update papers-reviewed.json** to avoid re-processing

## Scoring Rubric

| Score | Meaning | Action |
|-------|---------|--------|
| 0-4 | Not relevant | Skip, brief note in summary |
| 5-6 | Possibly relevant | Note for later, skip deep dive for now |
| 7-8 | Relevant | Deep dive, extract data, add to summary |
| 9-10 | Highly relevant | Deep dive, extract data, follow citations, highlight in summary |

## Helper Scripts (Optional)

**When screening many papers (>20), consider creating a helper script:**

**Benefits:**
- Batch processing with rate limiting
- Consistent scoring logic
- Save intermediate results
- Resume after interruption

**Create in research session folder:**
```python
# research-sessions/YYYY-MM-DD-query/screen_papers.py
```

**Key components:**
1. **Fetch abstracts** - reuse `rp_abstracts` / `rp_lib.openalex_by_dois` (it already rate-limits + caches)
2. **Score abstracts** - Implement scoring rubric (0-10)
3. **Save results** - JSON with scored papers categorized by relevance
4. **Progress reporting** - Print status as it runs

Do not write your own HTTP/rate-limit code — import `rp_lib` so caching and per-host
limits stay consistent with the rest of the pipeline.

### Progressive Enhancement Pattern (Recommended for 50+ papers)

**For large-scale screening, use two-script pattern:**

**Script 1: Abstract Screening** (`screen_papers.py`)
- Batch fetch abstracts
- Score using rubric (0-10)
- Categorize by relevance
- Output: `evaluated-papers.json` with basic metadata

**Script 2: Deep Dive** (`deep_dive_papers.py`)
- Read Script 1 output
- Fetch full text for highly relevant papers (score ≥8)
- Extract domain-specific data (measurements, protocols, datasets, etc.)
- Update same JSON file with enhanced metadata

**Benefits:**
- **Can run steps independently** - Score abstracts once, re-run deep dive multiple times
- **Resume if interrupted** - No need to re-fetch abstracts if deep dive fails
- **Re-run deep dive without re-scoring abstracts** - Adjust extraction logic, keep scores
- **Consistent and reproducible** - Same scoring logic applied to all papers
- **Save API calls** - Abstract screening happens once, deep dive only on relevant papers

**Script design:**
- Parameterize keywords and data types for specific query
- Progressive enhancement - add detail to same JSON file
- Rate limiting and caching come free from `rp_lib` — import it, don't reimplement
- Keep scripts with research session for reproducibility

**When NOT to create helper script:**
- Few papers (<20)
- One-off quick searches
- Manual screening is faster

## Common Mistakes

**Not tracking all papers:** Only adding relevant papers to papers-reviewed.json → Add EVERY paper regardless of score to prevent re-review
**Hand-fetching full text:** curl-ing publisher pages / Unpaywall / PMC → use `rp_fulltext`; it already covers OpenAlex's OA index. If it returns `available:false`, no free copy exists.
**Creating unnecessary files for small searches:** For <50 papers, use ONLY papers-reviewed.json and SUMMARY.md. For large searches (>100 papers), structured evaluated-papers.json and auxiliary files (README.md, TOP_PRIORITY_PAPERS.md) add significant value and should be used.
**Too strict:** Skipping papers that mention data indirectly → Re-read abstract carefully
**Too lenient:** Deep diving into tangentially related papers → Focus on specific data user needs
**Missing supplementary data:** Many papers hide key data in SI → Always check for supplementary files
**Silent screening:** User can't see progress → Report EVERY paper as you screen it
**No periodic summaries:** User loses big picture → Update every 5-10 papers
**Non-clickable DOIs/PMIDs:** Plain text identifiers → Always use markdown links
**Re-reviewing papers:** Wastes time → Always check papers-reviewed.json first
**Not using helper scripts:** Manually screening 100+ papers → Consider batch script

## Quick Reference

| Task | Action |
|------|--------|
| Check if reviewed | Look up DOI in papers-reviewed.json |
| Score abstract | Keywords (0-3) + Data type (0-4) + Specificity (0-3) |
| Pull missing abstracts | `rp_abstracts <doi> ...` |
| Get full text | `rp_fulltext <doi> --out papers/FILE.xml` |
| Find data | Grep for terms, focus on Methods/Results/Tables |
| Update tracking | Add to papers-reviewed.json + SUMMARY.md |

## Next Steps

After evaluating paper:
- If score ≥ 7: Call `skills/research/traversing-citations`
- Continue to next paper in search results
- Check if reached 50 papers or 5 minutes → ask user to continue or stop

## Auxiliary Files (for large searches >100 papers)

### README.md Template

**Use this structure for research projects with 100+ papers:**

1. **Project Overview**
   - Query description
   - Target molecules/topics
   - Date completed

2. **Quick Start Guide**
   - Where to start reading
   - Priority lists

3. **File Inventory**
   - Description of each file
   - What each is used for

4. **Key Findings Summary**
   - Statistics
   - Top findings
   - Coverage by category

5. **Methodology**
   - Scoring rubric
   - Decision rules
   - Data sources

6. **Next Steps**
   - Recommended actions
   - Priority order

### TOP_PRIORITY_PAPERS.md Template

**For datasets with >50 relevant papers, create curated priority list:**

- Organized by tier (Tier 1: Must-read, Tier 2: High-value, etc.)
- Include score, DOI, key findings summary
- Note full text availability
- Suggest reading order

**Example structure:**
```markdown
# Top Priority Papers

## Tier 1: Must-Read (Score 10)

### [Paper Title](https://doi.org/10.xxxx/yyyy) (Score: 10)

**DOI:** [10.xxxx/yyyy](https://doi.org/10.xxxx/yyyy)
**Full text:** ✓ OA (openalex-oa)

**Key Findings:**
- Finding 1
- Finding 2

---

## Tier 2: High-Value (Score 8-9)

[Additional papers organized by priority...]
```
