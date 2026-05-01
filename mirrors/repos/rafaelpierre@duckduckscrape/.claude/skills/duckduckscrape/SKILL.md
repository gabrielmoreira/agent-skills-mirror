---
name: duckduckscrape
description: >
  Lightweight web search via DuckDuckGo with BM25 relevance ranking.
  Use when asked to search the web, look something up, find recent information,
  research a topic, or browse the internet.
  Trigger phrases: search the web, look up, find information about, google,
  browse the web, web search, find recent, what is the latest on.
argument-hint: "<search query>"
---

# DuckDuckScrape

Lightweight DuckDuckGo web search tool with BM25 relevance ranking.
Results are fetched concurrently over HTTP/2 and re-ranked by content relevance.

## Usage

```bash
# Basic search — returns top 5 results ranked by BM25
duckduckscrape search "your query"

# Preferred for agent use: clean JSON on stdout, progress on stderr
duckduckscrape search "your query" --output json

# Control number of results
duckduckscrape search "your query" -k 3

# Fast mode: skip full-page fetching (uses only DDG snippets, no BM25 re-ranking)
duckduckscrape search "your query" --no-fetch

# Filter by recency (d=past day, w=past week, m=past month, y=past year)
duckduckscrape search "breaking news" --time-filter d

# Filter by region
duckduckscrape search "local elections" --region us-en

# Tune concurrency and per-request timeout
duckduckscrape search "your query" --concurrency 8 --timeout 15
```

## JSON output schema

Each element in the returned array contains:

| Field         | Type           | Description                                           |
|---------------|----------------|-------------------------------------------------------|
| `title`       | string         | Page title                                            |
| `url`         | string         | Full URL                                              |
| `display_url` | string         | Shortened display URL                                 |
| `snippet`     | string         | DuckDuckGo result snippet                             |
| `content`     | string or null | Extracted main-body text (null when --no-fetch)       |
| `bm25_score`  | number         | BM25 relevance score (present when ranking is active) |

## Notes

- Progress logs go to **stderr**; clean JSON goes to **stdout**.
  Pipe stdout for programmatic use; stderr can be discarded or logged separately.
- PDFs are automatically skipped during content fetching.
- BM25 filtering removes results with zero relevance to the query.
- Use `--no-fetch` for a fast, low-cost keyword search without content extraction.
