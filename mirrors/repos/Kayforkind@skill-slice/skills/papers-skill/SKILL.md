---
name: papers-skill
description: "Searches Semantic Scholar and arXiv via the bundled papers.py CLI: metadata, citation/reference graphs, arXiv PDF download, and PyMuPDF text extract. Use when finding papers, analyzing citations, building reading lists, or summarizing arXiv preprints. Not for paywalled publisher PDFs, OCR of scanned pages, citation-alert watches, or general web due diligence (end-to-end-research)."
version: 1.0.1
category: research
risk: safe
source: community
source_repo: xwmxcz/papers-skill
source_type: community
date_added: "2026-06-11"
tags: [research, academic, papers, citations, arxiv, semantic-scholar, pdf]
tools: [claude-code, antigravity, cursor, gemini-cli, codex-cli, opencode]
license: "MIT"
license_source: "https://github.com/xwmxcz/papers-skill/blob/main/LICENSE"
---

# Papers Skill

## Overview

Papers Skill turns a coding agent into a literature-research assistant. It orchestrates a bundled Python CLI (`scripts/papers.py`) that hits the free Semantic Scholar and arXiv APIs, downloads arXiv PDFs, and extracts text with PyMuPDF. The agent decides which subcommand to invoke and how to combine results into a literature scan, a deep read of one paper, an impact analysis, or a reading list.

This skill is the Skill-mode port of the [papers-mcp](https://github.com/xwmxcz/papers-mcp) MCP server by the same author. Both projects share the same feature set; this one ships as a plugin so it can be installed with a single command and needs no long-running MCP process.

## When to Use

- Use when the user asks to **search academic papers** by topic, author, or venue.
- Use when the user names a **specific paper** (by DOI, arXiv ID, or title) and wants metadata, the abstract, the TL;DR, or its reference list.
- Use when the user wants to find work that **cites** a known paper (impact analysis, follow-up tracking).
- Use when the user wants to **download an arXiv PDF** and have it summarized.
- Use when the user asks to **build a reading list** around a topic.

**Do NOT use this skill when:**

- The user wants paywalled non-arXiv full text. This skill cannot bypass publisher paywalls; it can only fetch arXiv PDFs and metadata everywhere.
- The user wants OCR over scanned PDFs. PyMuPDF extracts embedded text only; scanned image-PDFs return the fallback message and need a separate OCR step.
- The user wants real-time citation alerts or RSS-style watching. This skill is request-driven.

## Prerequisites

Three Python packages are required: `httpx`, `arxiv`, and `PyMuPDF`. Check once per session using the **same interpreter** for both the import-check and the install so targets stay in sync.

**Windows (PowerShell, primary):**

```powershell
python -c "import httpx, arxiv, fitz" 2>&1
if ($LASTEXITCODE -ne 0) { python -m pip install httpx arxiv PyMuPDF }
```

If `python` is not on PATH, fall back to `py` (Windows launcher) or the absolute interpreter path — and invoke pip via the same interpreter:

```powershell
py -c "import httpx, arxiv, fitz" 2>&1
if ($LASTEXITCODE -ne 0) { py -m pip install httpx arxiv PyMuPDF }
```

**macOS / Linux (bash):**

```bash
python -c "import httpx, arxiv, fitz" 2>&1 || python -m pip install httpx arxiv PyMuPDF
```

No API keys or credentials are needed. The CLI performs outbound HTTPS only to `api.semanticscholar.org` and `arxiv.org`. No authentication tokens are sent.

## Procedure

### Step 1 — Locate the bundled CLI

The script lives at `${CLAUDE_PLUGIN_ROOT}/skills/papers-skill/scripts/papers.py` and is bundled with this skill (no separate install needed). Always quote the path so it survives spaces.

**Windows (PowerShell):**

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" <subcommand> [args]
```

**macOS / Linux (bash):**

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/papers-skill/scripts/papers.py" <subcommand> [args]
```

### Step 2 — Pick the right subcommand

| Subcommand | Purpose | Max results | Example |
|---|---|---|---|
| `search <query> [--limit N]` | Semantic Scholar keyword search | 20 | `search "diffusion models" --limit 5` |
| `detail <paper_id>` | Full metadata, TL;DR, top references | — | `detail 10.48550/arXiv.2310.06825` |
| `citations <paper_id> [--limit N]` | Papers citing this one | 20 | `citations <id> --limit 15` |
| `arxiv <query> [--max-results N]` | arXiv preprint search | 10 | `arxiv "RLHF" --max-results 5` |
| `download <arxiv_id> [--save-dir D]` | Save PDF locally | — | `download 2310.06825 --save-dir ./pdfs` |
| `read <pdf_path> [--max-pages N]` | Extract PDF text via PyMuPDF | — | `read ./pdfs/foo.pdf --max-pages 20` |

**ID auto-detection rules** (for `detail` and `citations`):

- DOIs starting with `10.` → used as-is (e.g. `10.48550/arXiv.2310.06825`)
- Bare numeric IDs of 10+ digits → treated as arXiv IDs
- Long hex strings → treated as Semantic Scholar `paperId`s

### Step 3 — Execute the workflow

#### Workflow A: Literature scan on a topic

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" search "retrieval augmented generation" --limit 10
```

Present results as a ranked table: **# | Title | Year | Citations | ID**, then ask the user which papers to dig into.

#### Workflow B: Deep-read one paper

```powershell
# 1. Confirm match — ALWAYS call detail before download
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" detail 2005.11401

# 2. Download the PDF
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" download 2005.11401 --save-dir ./pdfs

# 3. Extract abstract + intro + conclusion
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" read ./pdfs/2005.11401v4.RAG.pdf --max-pages 10
```

Summarize as: **problem · method · key result · limitations**.

#### Workflow C: Impact analysis on an anchor paper

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" detail 10.48550/arXiv.2005.11401
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" citations 10.48550/arXiv.2005.11401 --limit 20
```

Cluster the citing papers by year/theme and highlight the most-cited follow-ups.

### Step 4 — Format output

- Always include the paper ID alongside every title so the user can re-query precisely.
- Cite as `[FirstAuthor et al., Year] *Title* (cites: N)`.
- For PDFs you download, always report the absolute save path.
- Confirm the save path with the user before downloading to an unexpected location.

### Hard rules

- ✅ **Always call `detail` before `download`** to confirm the paper matches user intent. Skipping this leads to wrong PDFs being fetched.
- ❌ **Don't crawl.** The script auto-retries 429s with exponential backoff (3×); don't pile on parallel queries.
- ❌ **Don't raise `--max-pages` to 100+** without warning the user — it can consume a large amount of context.
- `read` opens a local PDF file with PyMuPDF — make sure the path the user supplies is one they trust.
- `download` writes a PDF to the directory the user specifies (default: current working directory).

## Examples

### Example: Build a reading list on "RLHF"

```powershell
# 1. Search Semantic Scholar for breadth
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" search "reinforcement learning from human feedback" --limit 10

# 2. Cross-check arXiv for recent preprints
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" arxiv "RLHF" --max-results 5

# 3. For each top hit, pull detail + citations
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" detail 2204.05862
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" citations 2204.05862 --limit 10
```

Present a curated list grouped by sub-topic with citation counts and one-line summaries.

## Pitfalls

1. **Missing optional dependency message.** The script returns `需要安装 arxiv: pip install arxiv` or `需要安装 PyMuPDF: pip install PyMuPDF` instead of crashing when an optional dependency is missing. Offer to run the install command: `python -m pip install arxiv PyMuPDF`.

2. **Semantic Scholar rate limiting.** `搜索失败: rate limit, retries exhausted` from `search`, `detail`, or `citations`. Semantic Scholar's anonymous tier rate-limits aggressively; the script retries 3× with exponential backoff. **Fix:** Wait ~10 seconds and retry once. For repeated runs, fall back to the `arxiv` subcommand for arXiv-indexed work.

3. **Download fails with `找不到 arXiv ID: …`.** The user gave a non-arXiv ID (likely a DOI for a non-arXiv paper). Use `detail` to inspect; only papers with an `externalIds.ArXiv` field can be downloaded.

4. **Scanned PDF returns fallback text.** `PDF无法提取文本（可能是扫描件）` — PyMuPDF extracts embedded text only. Offer the user an alternative version or note that OCR is required (separate tool).

5. **Garbled Chinese output on Windows.** The script already forces UTF-8 stdout. If the host terminal is still misconfigured, set the environment variable before running:

   ```powershell
   $env:PYTHONIOENCODING = "utf-8"
   ```

6. **Paywalled full text.** The skill cannot fetch full text from paywalled publishers (Elsevier, Springer, Wiley, etc.). It can only read open arXiv PDFs. Metadata and abstracts are available everywhere via Semantic Scholar.

## Verification

After running any subcommand, verify the output is valid:

**Check 1 — Search returns results:**

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" search "attention is all you need" --limit 3
```

Expected: JSON or formatted output with at least 1 result containing `title`, `year`, `citationCount`, and `paperId` fields.

**Check 2 — Detail resolves a known paper:**

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" detail 10.48550/arXiv.1706.03762
```

Expected: Metadata including title "Attention Is All You Need", authors, abstract, TL;DR, and a references list.

**Check 3 — Download + read round-trip:**

```powershell
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" download 1706.03762 --save-dir ./pdfs
python "$env:CLAUDE_PLUGIN_ROOT/skills/papers-skill/scripts/papers.py" read ./pdfs/1706.03762v7.pdf --max-pages 5
```

Expected: PDF file written to `./pdfs/`, then extracted text from the first 5 pages printed to stdout.

**Check 4 — Dependencies present:**

```powershell
python -c "import httpx, arxiv, fitz; print('OK')"
```

Expected: `OK` with no error output.

## Related Skills

- **arxiv-skill** — if the user only needs arXiv preprint search without Semantic Scholar citation graphs.
- **pdf-extract-skill** — for general-purpose PDF text extraction beyond arXiv downloads.

## Additional Resources

- Skill home (this plugin): https://github.com/xwmxcz/papers-skill
- Upstream MCP server: https://github.com/xwmxcz/papers-mcp
- Semantic Scholar API docs: https://api.semanticscholar.org/
- arXiv API docs: https://info.arxiv.org/help/api/
- PyMuPDF docs: https://pymupdf.readthedocs.io/
