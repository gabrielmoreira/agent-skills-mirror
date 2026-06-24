---
name: find-paper-references
description: Automatically find references for academic paper Markdown files. Reads full paper text, identifies each knowledge point requiring citation (epidemiological data, mechanism descriptions, existing research conclusions, etc.), searches PubMed for 3-5 most relevant articles per kn...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# find-paper-references — Academic Paper PubMed Reference Finder

## Tools

Scripts are located in the `scripts/` subdirectory of this skill:

- `batch_search.py` — **Main entry point**: accepts all queries at once, parallel search, batch esummary fetch, typical runtime 10-20s
- `remap_refs.py` — Converts `[PMID:XXXXXXXX]` markers to `[1][2]` numbering and generates formal references (**not called by this skill — handled by subsequent endnote/zotero skill**)
- `convert_to_docx.py` — Converts `.md` to `.docx` (**not called by this skill**)

### Skill Boundary

```
┌─────────────────────────────────────────────────────┐
│  find-paper-references                              │
│  ─────────────────────────────────────────────────  │
│  Step 0-3: Identify knowledge points → Build PubMed search JSON │
│  Step 4:   batch_search.py batch search                         │
│  Step 5:   Select articles → Insert [PMID:xxxxxxxx] markers     │
│  Step 6:   Write to .md file                                    │
│  Step 7:   Generate _candidates.md candidate reference list     │
│  Step 8:   Prompt user to choose EndNote / Zotero to continue   │
│  ──────────────── Workflow ends ──────────────────────────────── │
│                                                     │
│  Formatting → format-references-endnote (EndNote)              │
│            → format-references-zotero (Zotero)                 │
└─────────────────────────────────────────────────────┘
```

---

## Workflow (Execute in Order)

### Step 0: Ask for NCBI API Key

Before starting any search, check and ask:

```
Do you have an NCBI API key? If so, search speed increases from 3 req/s to 10 req/s.
No worries if not — just skip and we'll proceed.
```

- **User provides key**: Before all script calls in this session, execute:
  ```bash
  # Windows
  $env:NCBI_API_KEY = "user_provided_key"
  # Mac/Linux
  export NCBI_API_KEY="user_provided_key"
  ```
  Then continue the workflow normally. Key is valid only for this session, not written to any file.

- **User doesn't have one / skips**: Proceed to Step 1. The script automatically uses the conservative 3 req/s rate.

### Step 1: Determine Target File + Article Type

Read the full file content, then determine article type — can be auto-detected or confirmed with the user:

**Auto-detection rules:**
- Contains `## Materials and Methods` / `## Methods` section → **Research Article**
- No such section, body consists mainly of review-style paragraphs → **Review**
- When uncertain, ask the user directly

---

## Article Type Citation Rules

Based on the detected type, this workflow must follow the corresponding rules:

### Research Article Rules
```
Citation zones:  Introduction and Discussion only
            Materials/Methods and Results → skip entirely, insert no citations
Per knowledge point: max 2 articles (top 2 by relevance, no padding)
Total target: at least 30 unique PMIDs in the text
```

### Review Rules
```
Citation zones:  All paragraphs except Conclusion
            Conclusion paragraphs → skip
Per knowledge point: max 5 articles
Total target: approximately 1 citation per 100 words, +/- 20%
            Target range = [word_count*0.8/100, word_count*1.2/100] (rounded)
            Example: 5000 words → target 40-60 articles; 8000 words → target 64-96 articles
```

---

### Step 2: Identify Sentences Requiring Citations

Read through the paper, **strictly following the citation zone rules for the current article type**, skip sections that don't need citations.

Within allowed citation zones, identify all **knowledge points requiring literature support**:

**Needs citation (applicable to allowed sections):**
- Epidemiological data ("Lung cancer is one of the most common malignancies worldwide")
- Known biological functions of proteins/genes ("GPX4 reduces lipid peroxides to non-toxic alcohols")
- Signaling pathway descriptions ("xCT mediates cellular cystine uptake")
- Published research conclusions ("TRIM3 is downregulated in breast cancer")
- Known mechanisms of treatments/drugs ("Erastin induces ferroptosis by inhibiting xCT")

**Never needs citation:**
- This study's own experimental results
- Instrument/reagent descriptions in Methods (entire section skipped for Research Articles)
- Results section (entirely skipped for Research Articles)
- Conclusion section (skipped for Reviews)
- General technical operation descriptions

**After identification, estimate total knowledge points:**
- Research Article: target ≥ 30 unique citations → typically need to identify 20-35 knowledge points
- Review: **calculate total word count first**, estimate target citations at 1 per 100 words, typically need knowledge points close to target number (1-2 articles per point)

Organize identified knowledge points into a list, each containing:
- Section name (to confirm it's in an allowed citation zone)
- The sentence from the original text
- Core concept of the knowledge point (for generating search terms)

### Step 3: Organize All Queries into Temporary JSON

Organize all knowledge points into the following format, write to `%TEMP%\ref_queries.json` (or `/tmp/ref_queries.json`):

```json
[
  {"id": 1, "description": "global lung cancer incidence", "query": "global cancer statistics 2020 GLOBOCAN lung cancer Sung", "method": "pubmed"},
  {"id": 2, "description": "ferroptosis definition", "query": "Ferroptosis iron-dependent nonapoptotic cell death Dixon 2012", "method": "pubmed"},
  {"id": 3, "description": "TRIM3 structure and function", "query": "TRIM3 ubiquitin ligase RING domain substrate degradation", "method": "litsense"},
  ...
]
```

**Method options:**
- `"pubmed"` — Keyword-based precise search (recommended for most knowledge points)
- `"litsense"` — Semantic search (suitable for descriptive sentences, specific protein functions, etc.)
- `"auto"` — Try LitSense first; if results < 2 articles, automatically fall back to PubMed

**Query writing guidelines:**
- Use English, 3-8 keywords
- Prefer MeSH terms (ferroptosis, non-small cell lung cancer, ubiquitin ligase)
- For known classic papers, add author or year to query ("Dixon 2012", "Stockwell 2017")

### Step 4: Run batch_search.py Once to Get All Results

```bash
python "SKILL_DIR/scripts/batch_search.py" "%TEMP%\ref_queries.json" --max 5
```

Script searches all queries in parallel, batch-fetches esummary, **typical runtime 10-20 seconds** (vs. minutes for sequential searching).

Output JSON format:
```json
[
  {"id": 1, "description": "...", "results": [{pmid, title, authors, journal, year, doi}, ...]},
  ...
]
```

**If any result is empty**, create a new JSON file with adjusted keywords and re-run batch_search.py.

### Step 5: Select Most Relevant Articles and Insert PMID Markers

For each sentence requiring citation:

1. Sort candidates by relevance, select according to **article type limits**:
   - **Research Article**: max **2** per knowledge point, select only the most relevant
   - **Review**: max **5** per knowledge point, can cover different research angles
2. Insert `[PMID:XXXXXXXX]` at **end of original sentence**; for multiple: `[PMID:111][PMID:222]`
3. If same PMID already cited, reuse it — do not insert duplicates

**After insertion, count current unique PMIDs:**
- Research Article: if fewer than 30, return to Step 2 to identify more knowledge points
- Review: **calculate word count, compute target range [words*0.8/100, words*1.2/100] (rounded)**, if not within range, return to Step 2 to add or reduce

**Example (before/after):**
```
Before: Ferroptosis is a form of regulated cell death driven by iron-dependent lipid peroxidation.
After:  Ferroptosis is a form of regulated cell death driven by iron-dependent lipid peroxidation[PMID:25789077].
```

**Flexible formats supported by remap_refs.py (all handled correctly):**
- Case insensitive: `[PMID:123]` `[pmid:123]` `[Pmid:123]`
- Spaces around colon: `[PMID: 123]` `[ PMID : 123 ]`
- Multiple in one bracket: `[PMID:123, PMID:456]` → `[1][2]` (spaces and comma variants accepted)

### Step 6: Write PMID-Marked Full Text to New File

**Do not overwrite the original file.** Write the full text with `[PMID:XXXXXXXX]` markers to a **new file**:

- Original `paper.md` → New file `paper_refs.md` (generated in same directory)

Naming rule: remove `.md` suffix from original filename, add `_refs.md`. Examples:
- `TRIM3_ferroptosis.md` → `TRIM3_ferroptosis_refs.md`
- No extension case: `manuscript` → `manuscript_refs.md`

Keep the original file unchanged — no modifications.

### Step 7: Write Candidate References to Separate File

**Do not** append the reference candidate section to the original `.md` file — it will interfere with subsequent formatting.

Instead, generate a separate candidate file `originalfilename_candidates.md` in the same directory:

```markdown

## Reference Candidates

> Below are PubMed search results for each knowledge point. Those selected for the text are marked with checkmark.
> Next step: Use format-references-endnote or format-references-zotero skill for formatting.

### Knowledge Point 1: [brief description]
- ✓ **[PMID:25789077]** Dixon SJ et al. "Ferroptosis: an iron-dependent form of nonapoptotic cell death." *Cell* 2012;149(5):1060-72.
- [PMID:26593993] Stockwell BR et al. "Ferroptosis: a regulated cell death nexus linking metabolism, redox biology, and disease." *Cell* 2017;171(2):273-285.
- [PMID:31634899] ...

### Knowledge Point 2: [brief description]
...
```

**Step 7 completion ends this workflow.** Do not run remap_refs.py or convert_to_docx.py.

### Step 8: Proactively Remind User to Choose Formatting Tool

After Step 7, **must proactively ask the user** to choose next step:

```
All citation markers have been inserted (N unique references total). Ready to format and export to Word?

Do you use EndNote or Zotero for reference management?
```

- User chooses **EndNote** → immediately load `format-references-endnote` skill to continue
- User chooses **Zotero** → immediately load `format-references-zotero` skill to continue
- User says "not now" / "let me check first" → inform them "say 'format references' anytime to continue"

**Do not** end silently — this reminder is mandatory.

---

## Next Step: Reference Formatting (Separate Skill)

After the `[PMID:xxxxxxxx]`-marked .md file is generated, choose based on user's reference manager:

### EndNote Users

Use **format-references-endnote** skill. It will:
1. Convert `[PMID:xxxx]` markers to EndNote CWYW-recognized `{Author, Year, Title}` placeholders
2. Generate `.ris` file for automatic import to local EndNote library
3. Output `.docx` file — user clicks "Update Citations" once in Word to complete formatting


### Zotero Users

Use **format-references-zotero** skill. It will:
1. Convert `[PMID:xxxx]` markers to native Zotero field codes
2. Search/download any CSL citation style
3. Output `.docx` file — click "Refresh" once in Word to complete

---

## NCBI API Key (Optional, Free)

NCBI provides free API keys. With a key, rate limit increases from 3 req/s to 10 req/s, concurrent workers increase from 4 to 8, making searches faster and less likely to trigger rate limiting.

**How to get one:**
1. Register NCBI account: https://www.ncbi.nlm.nih.gov/account/
2. Go to Account Settings → API Key Management → Generate

**How to use:**
```bash
# Temporary (current session only)
set NCBI_API_KEY=your_key    # Windows
export NCBI_API_KEY=your_key  # Mac/Linux

# Permanent (recommended: add to system env vars or .env file)
```

**Works fine without a key** — script automatically uses conservative 3 req/s rate and auto-retries on 429 errors.

## Important Notes

- Search terms must be in English (PubMed indexes primarily English literature)
- For very recent research (2024 onwards), PubMed indexing may have delays
- On 429 rate limiting, script auto-retries with backoff (up to 4 times) — no manual intervention needed

## Input Validation

This skill accepts requests that match the documented purpose of `find-paper-references` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `find-paper-references` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
