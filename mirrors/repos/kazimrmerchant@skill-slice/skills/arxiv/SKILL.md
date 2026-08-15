---
name: arxiv
description: "Searches arXiv via the Atom REST API and enriches papers with Semantic Scholar citations, references, and BibTeX. Use when finding preprints by keyword, author, category, or ID, or generating citations. Not for Hugging Face paper pages (hugging-face-papers) or general web due-diligence (end-to-end-research)."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Arxiv, Papers, Academic, Science, API]
    related_skills: [ocr-and-documents]
---

# arXiv Research

Search and retrieve academic papers from arXiv via their free REST API, then enrich with citation data from Semantic Scholar. No API key required for either service at baseline rates.

## When to Use

- **Trigger keywords**: "arxiv", "paper", "academic search", "citation count", "BibTeX", "related papers", "research", "preprint", "Semantic Scholar"
- You need to find papers on a topic, by an author, or in a specific category
- You need citation counts, reference lists, or paper recommendations
- You need to generate a BibTeX entry from an arXiv ID
- You need to read a paper's abstract or full PDF content

## Prerequisites

- `curl` available on PATH (Windows: `curl.exe` ships with Windows 10+; in PowerShell use `curl.exe` to avoid the `Invoke-WebRequest` alias)
- `python3` (or `python`) for XML parsing and JSON formatting — no third-party dependencies, stdlib only
- `web_extract` tool available for reading abstract pages and PDFs
- No API keys required for arXiv or Semantic Scholar baseline rates

**Windows / PowerShell notes:**
- Use `curl.exe` instead of `curl` to bypass the PowerShell alias for `Invoke-WebRequest`
- For multi-line Python snippets in PowerShell, use a here-string (`@' … '@`) or write to a temp `.py` file and run `python file.py`
- Alternatively, use the helper script `scripts/search_arxiv.py` which avoids inline quoting issues entirely

## Procedure

### 1. Search arXiv by keyword

```bash
# Basic keyword search (Linux/macOS)
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"

# PowerShell equivalent
curl.exe -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"
```

### 2. Get clean, parsed output

Use the helper script for the simplest path:

```bash
python scripts/search_arxiv.py "GRPO reinforcement learning"
python scripts/search_arxiv.py "transformer attention" --max 10 --sort date
python scripts/search_arxiv.py --author "Yann LeCun" --max 5
python scripts/search_arxiv.py --category cs.AI --sort date
python scripts/search_arxiv.py --id 2402.03300
python scripts/search_arxiv.py --id 2402.03300,2401.12345
```

No dependencies — uses only Python stdlib.

Alternatively, parse XML inline:

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5&sortBy=submittedDate&sortOrder=descending" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
    summary = entry.find('a:summary', ns).text.strip()[:200]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    print(f'{i+1}. [{arxiv_id}] {title}')
    print(f'   Authors: {authors}')
    print(f'   Published: {published} | Categories: {cats}')
    print(f'   Abstract: {summary}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

### 3. Use search query syntax

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.AI` |
| `co:` | Comment | `co:accepted+NeurIPS` |

Boolean operators:

```
# AND (default when using +)
search_query=all:transformer+attention

# OR
search_query=all:GPT+OR+all:BERT

# AND NOT
search_query=all:language+model+ANDNOT+all:vision

# Exact phrase
search_query=ti:"chain+of+thought"

# Combined
search_query=au:hinton+AND+cat:cs.LG
```

### 4. Sort and paginate

| Parameter | Options |
|-----------|---------|
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` |
| `sortOrder` | `ascending`, `descending` |
| `start` | Result offset (0-based) |
| `max_results` | Number of results (default 10, max 30000) |

```bash
# Latest 10 papers in cs.AI
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

### 5. Fetch specific papers by ID

```bash
# Single paper
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# Multiple papers
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300,2401.12345,2403.00001"
```

### 6. Generate BibTeX

```bash
curl -s "https://export.arxiv.org/api/query?id_list=1706.03762" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
root = ET.parse(sys.stdin).getroot()
entry = root.find('a:entry', ns)
if entry is None: sys.exit('Paper not found')
title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
authors = ' and '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
year = entry.find('a:published', ns).text[:4]
raw_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
cat = entry.find('arxiv:primary_category', ns)
primary = cat.get('term') if cat is not None else 'cs.LG'
last_name = entry.find('a:author', ns).find('a:name', ns).text.split()[-1]
print(f'@article{{{last_name}{year}_{raw_id.replace(\".\", \"\")},')
print(f'  title     = {{{title}}},')
print(f'  author    = {{{authors}}},')
print(f'  year      = {{{year}}},')
print(f'  eprint    = {{{raw_id}}},')
print(f'  archivePrefix = {{arXiv}},')
print(f'  primaryClass  = {{{primary}}},')
print(f'  url       = {{https://arxiv.org/abs/{raw_id}}}')
print('}')
"
```

### 7. Read paper content

```
# Abstract page (fast, metadata + abstract)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper (PDF → markdown via Firecrawl)
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

For local PDF processing, see the `ocr-and-documents` skill.

### 8. Enrich with Semantic Scholar (citations, references, recommendations)

Semantic Scholar returns JSON — pipe through `python3 -m json.tool` for readability.

**Get paper details + citation counts:**

```bash
# By arXiv ID
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,referenceCount,influentialCitationCount,year,abstract" | python3 -m json.tool

# By DOI
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1234/example?fields=title,citationCount"
```

**Get citations OF a paper (who cited it):**

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**Get references FROM a paper (what it cites):**

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**Search papers (returns JSON):**

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO+reinforcement+learning&limit=5&fields=title,authors,year,citationCount,externalIds" | python3 -m json.tool
```

**Get paper recommendations:**

```bash
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}' | python3 -m json.tool
```

**Author profile:**

```bash
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=Yann+LeCun&fields=name,hIndex,citationCount,paperCount" | python3 -m json.tool
```

**Useful Semantic Scholar fields:**

`title`, `authors`, `year`, `abstract`, `citationCount`, `referenceCount`, `influentialCitationCount`, `isOpenAccess`, `openAccessPdf`, `fieldsOfStudy`, `publicationVenue`, `externalIds` (contains arXiv ID, DOI, etc.)

### 9. Complete research workflow

1. **Discover**: `python scripts/search_arxiv.py "your topic" --sort date --max 10`
2. **Assess impact**: `curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=citationCount,influentialCitationCount"`
3. **Read abstract**: `web_extract(urls=["https://arxiv.org/abs/ID"])`
4. **Read full paper**: `web_extract(urls=["https://arxiv.org/pdf/ID"])`
5. **Find related work**: `curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,citationCount&limit=20"`
6. **Get recommendations**: POST to Semantic Scholar recommendations endpoint
7. **Track authors**: `curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=NAME"`

## Common Categories

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `cs.CR` | Cryptography and Security |
| `stat.ML` | Machine Learning (Statistics) |
| `math.OC` | Optimization and Control |
| `physics.comp-ph` | Computational Physics |

Full list: https://arxiv.org/category_taxonomy

## Rate Limits

| API | Rate | Auth |
|-----|------|------|
| arXiv | ~1 req / 3 seconds | None needed |
| Semantic Scholar | 1 req / second | None (100/sec with API key) |

## Pitfalls

- **arXiv returns Atom XML, not JSON.** You must parse XML — use the helper script `scripts/search_arxiv.py` or the inline Python snippet. Do not attempt `json.tool` on arXiv responses.
- **PowerShell `curl` alias.** In PowerShell, `curl` is aliased to `Invoke-WebRequest` by default. Use `curl.exe` explicitly, or remove the alias with `Remove-Item Alias:curl` in your session.
- **Inline Python in PowerShell.** Multi-line `python3 -c "..."` strings break in PowerShell due to quoting differences. Prefer writing to a temp `.py` file or using `scripts/search_arxiv.py`.
- **Rate limiting.** arXiv allows ~1 request per 3 seconds; Semantic Scholar allows 1 request per second without an API key. Exceeding these rates results in HTTP 429 or 503 errors. Add `sleep 3` between arXiv calls in loops.
- **arXiv ID formats.** Old-format IDs like `hep-th/0601001` use a slash; new-format IDs like `2402.03300` do not. Always URL-encode the slash as `%2F` if passing old IDs in query parameters.
- **ID versioning.** `arxiv.org/abs/1706.03762` always resolves to the **latest** version. `arxiv.org/abs/1706.03762v1` points to a **specific** immutable version. When generating citations, preserve the version suffix you actually read to prevent citation drift — a later version may substantially change content. The API `<id>` field returns the versioned URL (e.g., `http://arxiv.org/abs/1706.03762v7`).
- **Withdrawn papers.** Papers can be withdrawn after submission. The `<summary>` field will contain a withdrawal notice (look for "withdrawn" or "retracted"). Metadata fields may be incomplete. Always check the summary before treating a result as a valid paper.
- **Semantic Scholar coverage gaps.** Not all arXiv papers are indexed in Semantic Scholar. If you get a 404, the paper may not yet be indexed — fall back to arXiv metadata only.
- **`max_results` cap.** The arXiv API supports up to 30000 results per query, but large result sets are slow and may time out. Use `start` for pagination instead of requesting everything at once.

## Verification

1. **Verify arXiv API is reachable:**

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:test&max_results=1" | head -5
```

Expected: XML output beginning with `<?xml` and containing `<feed` and at least one `<entry>`.

2. **Verify helper script works:**

```bash
python scripts/search_arxiv.py "attention is all you need" --max 1
```

Expected: One result line with arXiv ID `1706.03762` (the "Attention Is All You Need" paper).

3. **Verify Semantic Scholar is reachable:**

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:1706.03762?fields=title,citationCount" | python3 -m json.tool
```

Expected: JSON with `"title": "Attention Is All You Need"` and a numeric `citationCount`.

4. **Verify web_extract can read an abstract page:**

```
web_extract(urls=["https://arxiv.org/abs/1706.03762"])
```

Expected: Markdown content containing the paper title, authors, and abstract text.

## Related skills

- **ocr-and-documents** — for local PDF processing, OCR, and document extraction when `web_extract` on arXiv PDFs is insufficient or you need offline analysis.
