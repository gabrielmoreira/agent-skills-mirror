---
name: Wentor API
description: Access Wentor platform academic services — paper Q&A search, structured paper search, and AI figure generation. Requires a Wentor API token.
metadata: { "openclaw": { "always": true } }
---

# Wentor Academic API

Three services for academic research, accessible via the Wentor platform API.

**Base URL:** `https://wentor.ai/api/v1/academic`
**Auth:** Bearer token from your Wentor dashboard → API Token section.

All endpoints require:
1. A valid Wentor API token (`Authorization: Bearer <token>`)
2. The corresponding service enabled in your dashboard

---

## 1. wentor_qa — Paper Q&A Search

Natural-language paper search. Ask a question, get relevant papers.

- **Quota:** 20 requests/day
- **Rate limit:** 5 requests/minute

### Request

```
POST /api/v1/academic/qa
Content-Type: application/json
Authorization: Bearer <token>
```

```json
{ "query": "attention mechanism transformer", "size": 10, "year": [2024, 2025] }
```

| Field      | Type       | Required | Default     | Description                                |
|------------|------------|----------|-------------|-------------------------------------------|
| `query`    | string     | yes      | —           | Natural language question (2–500 chars)     |
| `size`     | int        | no       | 10          | Results per page (1–50)                     |
| `offset`   | int        | no       | 0           | Pagination offset                          |
| `sort`     | string     | no       | `relevance` | `relevance`, `citations`, or `year`        |
| `year`     | int[]      | no       | null        | Filter by publication year(s)              |
| `sci_only` | bool       | no       | false       | Only return SCI-indexed papers             |

Response: `{ items: [{ id, title, title_zh, doi, ... }], total }`.

---

## 2. wentor_search — Structured Paper Search

Search papers by specific fields: title, keyword, author, organization, venue.

- **Quota:** 100 requests/day
- **Rate limit:** 10 requests/minute

### Request

```
GET /api/v1/academic/search
Authorization: Bearer <token>
```

| Param     | Type   | Required         | Default     | Description                          |
|-----------|--------|------------------|-------------|--------------------------------------|
| `title`   | string | at least one     | —           | Paper title (partial match)          |
| `keyword` | string | at least one     | —           | Topic keyword                        |
| `author`  | string | at least one     | —           | Author name                          |
| `org`     | string | at least one     | —           | Institution/organization             |
| `venue`   | string | at least one     | —           | Journal or conference name           |
| `page`    | int    | no               | 0           | Page number (0-indexed)              |
| `size`    | int    | no               | 10          | Results per page (1–50)              |
| `sort`    | string | no               | `relevance` | `relevance`, `citations`, or `year`  |

At least one of `title`, `keyword`, `author`, `org`, or `venue` is required.

Response: `{ items: [{ id, title, title_zh, doi, ... }], total, page, size }`.

---

## 3. wentor_plot — Academic Figure Generation

Generate academic figures from text descriptions. Text-to-image only (no image editing).

- **Quota:** 10 requests/day
- **Rate limit:** 2 requests/minute

### Request

```
POST /api/v1/academic/plot
Content-Type: application/json
Authorization: Bearer <token>
```

```json
{ "prompt": "A bar chart comparing BLEU scores of 5 MT models on WMT-2023" }
```

| Field    | Type   | Required | Description                                          |
|----------|--------|----------|------------------------------------------------------|
| `prompt` | string | yes      | Figure description in natural language (2–2000 chars) |

Response: `{ image: "data:image/png;base64,..."|null, text: string|null, prompt: string }`.
`image` is a base64-encoded PNG data URI. `null` if generation failed.

---

## Error Codes

| HTTP | Code                      | Meaning                                        |
|------|---------------------------|------------------------------------------------|
| 401  | `UNAUTHORIZED`            | Missing or invalid API token                   |
| 400  | `MISSING_SEARCH_CRITERIA` | No search field provided (wentor_search only)  |
| 400  | `INVALID_PARAMS`          | Invalid search parameters (upstream)           |
| 403  | `SERVICE_NOT_ENABLED`     | Enable the service in your dashboard first     |
| 422  | validation error          | Invalid field value (e.g., query too short)    |
| 429  | `QUOTA_EXCEEDED`          | Daily quota exhausted, resets at midnight UTC  |
| 429  | `RATE_LIMITED`            | Too many requests per minute, slow down        |
| 429  | `UPSTREAM_RATE_LIMITED`   | Upstream service rate limited, retry later     |
| 502  | `UPSTREAM_ERROR`          | Upstream service error                         |
| 503  | `UPSTREAM_UNAVAILABLE`    | Upstream service temporarily unavailable       |

## Usage Tips

- Use **wentor_qa** when you have a natural-language research question and want to discover relevant papers.
- Use **wentor_search** when you know specific metadata (author name, conference, institution) and want precise results.
- Use **wentor_plot** to generate publication-ready figures. Be specific in your prompts — include chart type, data description, axis labels, and visual style preferences.
- Combine **wentor_qa** + **wentor_plot**: search for papers first, then visualize findings as figures.
- Check your remaining quota on the Wentor dashboard under the Services section.
