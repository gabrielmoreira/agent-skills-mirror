---
name: duckduckgo-search
description: Runs keyless DuckDuckGo search (text, news, images, videos) via the ddgs CLI or a verified Python DDGS import. Use when built-in web_search is unavailable, FIRECRAWL_API_KEY is unset, or DDG results are requested. Not for full-page extraction, arXiv lookup (arxiv), or Hugging Face paper pages (hugging-face-papers).
version: 1.3.1
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [search, duckduckgo, web-search, free, fallback]
    related_skills: [arxiv]
    fallback_for_toolsets: [web]
---

# DuckDuckGo Search

Free web search using DuckDuckGo. **No API key required.** Prefer the `ddgs` CLI when installed; use the Python `DDGS` library only after verifying that `ddgs` is importable in the target Python runtime.

## When to Use

- `web_search` is unavailable or unsuitable.
- `FIRECRAWL_API_KEY` is not set and a free search fallback is needed.
- DuckDuckGo results are specifically desired (different index than Google/Bing).
- You need text, news, image, or video results without an API key.

**Trigger keywords:** duckduckgo, ddgs, free search, web search fallback, search without api key, ddg search.

## Prerequisites

- Python 3.8+ available on the host.
- `pip` available in the environment where `ddgs` will run.
- Network access to DuckDuckGo endpoints (some cloud IPs may be blocked).

**Windows (PowerShell) is the primary host.** Bash equivalents are noted where relevant.

## Procedure

### Step 1 — Detect what is available

Check whether the `ddgs` CLI is installed before choosing an approach.

**PowerShell:**
```powershell
if (Get-Command ddgs -ErrorAction SilentlyContinue) { "DDGS_CLI=installed" } else { "DDGS_CLI=missing" }
```

**Bash (Linux/macOS):**
```bash
command -v ddgs >/dev/null && echo "DDGS_CLI=installed" || echo "DDGS_CLI=missing"
```

Decision tree:
1. If `ddgs` CLI is installed → use **Method 1 (CLI)** via terminal.
2. If `ddgs` CLI is missing → do not assume `execute_code` can import `ddgs`.
3. If the user wants DuckDuckGo specifically → install `ddgs` in the relevant environment first.
4. Otherwise → fall back to built-in web/browser tools.

> **Runtime separation:** Terminal and `execute_code` are separate runtimes. A successful shell install does not guarantee `execute_code` can import `ddgs`. Never assume third-party Python packages are preinstalled inside `execute_code`.

### Step 2 — Install `ddgs` (only when needed)

Install `ddgs` only when DuckDuckGo search is specifically needed and the runtime does not already provide it.

```powershell
pip install ddgs
ddgs --help
```

If a workflow depends on Python imports, verify that the same runtime can import `ddgs` before using `from ddgs import DDGS`.

> **Package name:** The package is `ddgs` (previously `duckduckgo-search`). Install with `pip install ddgs`.

### Step 3 — Choose a method

#### Method 1: CLI Search (Preferred)

Use the `ddgs` command via terminal when it exists. This avoids assuming the `execute_code` sandbox has the `ddgs` Python package installed.

```powershell
# Text search
ddgs text -q "python async programming" -m 5

# News search
ddgs news -q "artificial intelligence" -m 5

# Image search
ddgs images -q "landscape photography" -m 10

# Video search
ddgs videos -q "python tutorial" -m 5

# With region filter
ddgs text -q "best restaurants" -m 5 -r us-en

# Recent results only (d=day, w=week, m=month, y=year)
ddgs text -q "latest AI news" -m 5 -t w

# JSON output for parsing
ddgs text -q "fastapi tutorial" -m 5 -o json
```

**CLI flags:**

| Flag | Description | Example |
|------|-------------|---------|
| `-q` | Query — **required** | `-q "search terms"` |
| `-m` | Max results | `-m 5` |
| `-r` | Region | `-r us-en` |
| `-t` | Time limit | `-t w` (week) |
| `-s` | Safe search | `-s off` |
| `-o` | Output format | `-o json` |

> Do not confuse `-q` (query) and `-m` (max results count).

#### Method 2: Python API (Only After Verification)

Use the `DDGS` class in `execute_code` or another Python runtime **only after verifying** that `ddgs` is installed there.

**Safe wording:**
- "Use `execute_code` with `ddgs` after installing or verifying the package if needed."

**Avoid saying:**
- "`execute_code` includes `ddgs`."
- "DuckDuckGo search works by default in `execute_code`."

> **HARD RULE:** `max_results` must always be passed as a **keyword argument**. Positional usage raises an error on all methods: `ddgs.text("query", 5)` → error. Use `ddgs.text("query", max_results=5)`.

**Text search** — general research, companies, documentation:

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.text("python async programming", max_results=5):
        print(r["title"])
        print(r["href"])
        print(r.get("body", "")[:200])
        print()
```

Returns: `title`, `href`, `body`.

**News search** — current events, breaking news:

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.news("AI regulation 2026", max_results=5):
        print(r["date"], "-", r["title"])
        print(r.get("source", ""), "|", r["url"])
        print(r.get("body", "")[:200])
        print()
```

Returns: `date`, `title`, `body`, `url`, `image`, `source`.

**Image search** — visual references, diagrams:

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.images("semiconductor chip", max_results=5):
        print(r["title"])
        print(r["image"])
        print(r.get("thumbnail", ""))
        print(r.get("source", ""))
        print()
```

Returns: `title`, `image`, `thumbnail`, `url`, `height`, `width`, `source`.

**Video search** — tutorials, demos, explainers:

```python
from ddgs import DDGS

with DDGS() as ddgs:
    for r in ddgs.videos("FastAPI tutorial", max_results=5):
        print(r["title"])
        print(r.get("content", ""))
        print(r.get("duration", ""))
        print(r.get("provider", ""))
        print(r.get("published", ""))
        print()
```

Returns: `title`, `content`, `description`, `duration`, `provider`, `published`, `statistics`, `uploader`.

**Quick reference:**

| Method | Use When | Key Fields |
|--------|----------|------------|
| `text()` | General research, companies | title, href, body |
| `news()` | Current events, updates | date, title, source, body, url |
| `images()` | Visuals, diagrams | title, image, thumbnail, url |
| `videos()` | Tutorials, demos | title, content, duration, provider |

### Step 4 — Search then extract (full content)

DuckDuckGo returns titles, URLs, and snippets — **not full page content**. To get full page content, search first, then extract the most relevant URL with `web_extract`, browser tools, or `curl`.

CLI:
```powershell
ddgs text -q "fastapi deployment guide" -m 3 -o json
```

Python (only after verifying `ddgs` is installed in that runtime):
```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("fastapi deployment guide", max_results=3))
    for r in results:
        print(r["title"], "->", r["href"])
```

Then extract the best URL with `web_extract` or another content-retrieval tool.

## Pitfalls

- **`max_results` is keyword-only:** `ddgs.text("query", 5)` raises an error. Always use `ddgs.text("query", max_results=5)`.
- **Do not assume the CLI exists:** Check `Get-Command ddgs` (PowerShell) or `command -v ddgs` (bash) before using it.
- **Do not assume `execute_code` can import `ddgs`:** `from ddgs import DDGS` may fail with `ModuleNotFoundError` unless that runtime was prepared separately.
- **Package name confusion:** The package is `ddgs` (previously `duckduckgo-search`). Install with `pip install ddgs`.
- **CLI flag confusion:** `-q` is the query; `-m` is max results count. Do not swap them.
- **Empty results:** If `ddgs` returns nothing, it may be rate-limited. Wait a few seconds and retry.
- **Rate limiting:** DuckDuckGo may throttle after many rapid requests. Add a short delay between searches if needed.
- **No content extraction:** `ddgs` returns snippets, not full page content. Use `web_extract`, browser tools, or `curl` for the full article/page.
- **Cloud IP blocking:** DuckDuckGo may block requests from some cloud IPs. If searches return empty, try different keywords or wait a few seconds.
- **Field variability:** Return fields may vary between results or `ddgs` versions. Use `.get()` for optional fields to avoid `KeyError`.
- **Separate runtimes:** A successful `ddgs` install in terminal does not automatically mean `execute_code` can import it.

## Verification

### Verify CLI is installed

**PowerShell:**
```powershell
Get-Command ddgs
ddgs --help
```

**Bash:**
```bash
command -v ddgs && ddgs --help
```

Expected: help text listing `text`, `news`, `images`, `videos` subcommands.

### Verify a text search returns results

```powershell
ddgs text -q "python async programming" -m 3 -o json
```

Expected: JSON array with objects containing `title`, `href`, and `body` fields.

### Verify Python import (only if using Method 2)

```python
from ddgs import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text("test query", max_results=1))
    print(results[0]["title"])
```

Expected: at least one result printed. If `ModuleNotFoundError` occurs, the Python runtime does not have `ddgs` installed — do not use Method 2 there.

### Troubleshooting

| Problem | Likely Cause | What To Do |
|---------|--------------|------------|
| `ddgs: command not found` | CLI not installed in the shell environment | Install `ddgs`, or use built-in web/browser tools instead |
| `ModuleNotFoundError: No module named 'ddgs'` | Python runtime does not have the package installed | Do not use Python DDGS there until that runtime is prepared |
| Search returns nothing | Temporary rate limiting or poor query | Wait a few seconds, retry, or adjust the query |
| CLI works but `execute_code` import fails | Terminal and `execute_code` are different runtimes | Keep using CLI, or separately prepare the Python runtime |

## Related Skills

- `arxiv` — academic paper search (complementary for research workflows).
- Firecrawl-based search skills — more configurable but require `FIRECRAWL_API_KEY`.

---

Validated against `ddgs==9.11.2` semantics. CLI availability and Python import availability are treated as separate concerns so the documented workflow matches actual runtime behavior.
