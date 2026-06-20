---
name: oxylabs-web-scraper
description: Production-grade web scraping with automatic anti-bot bypass, structured JSON parsing for 40+ targets, and geo-targeting. Use when the user needs to scrape web pages, extract product data, get search results, or collect structured data from supported e-commerce and search platforms without worrying about getting blocked and when geo targeting is required.
---

# Oxylabs Web Scraper API

## Authentication

Requires HTTP Basic Auth with credentials from environment variables:

```bash
curl -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" ...
```

## Endpoint

```
POST https://realtime.oxylabs.io/v1/queries
Content-Type: application/json
```

## Core Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `source` | Yes | Target scraper (e.g., `universal`, `amazon_product`, `google_search`) |
| `url` | Conditional | URL to scrape (for `universal` and `*_url` sources) |
| `query` | Conditional | Search query or product ID (for `*_search` and `*_product` sources) |
| `parse` | No | Enable structured data parsing (recommended for supported sources) |
| `render` | No | JavaScript rendering: `html` or `png` |
| `geo_location` | No | Geographic targeting (country, state, or ZIP code) |

## Quick Start

**Scrape any URL:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{"source": "universal", "url": "https://example.com"}'
```

**Google search with parsing:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{"source": "google_search", "query": "best laptops", "parse": true}'
```

**Amazon product by ASIN:**
```bash
curl -X POST 'https://realtime.oxylabs.io/v1/queries' \
  -u "$OXY_WSA_USERNAME:$OXY_WSA_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{"source": "amazon_product", "query": "B07FZ8S74R", "parse": true}'
```

## Choosing the Right Source

1. **Use specific sources when available** (`amazon_product`, `google_search`) - better parsing and reliability
2. **Use `universal` for unsupported sites** - works with any URL
3. **Enable `parse: true`** for structured JSON output on supported sources

## Response Structure

```json
{
  "results": [{
    "content": "...",
    "status_code": 200,
    "url": "https://..."
  }]
}
```

With `parse: true`, `content` contains structured data (title, price, reviews, etc.) instead of raw HTML.

## Available Sources

For the complete list of 40+ supported sources organized by category, see [sources.md](sources.md).

## More Examples

For detailed request/response examples including geo-location, JavaScript rendering, and custom headers, see [examples.md](examples.md).

## Error Handling

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Invalid parameters |
| 401 | Authentication failed |
| 403 | Access denied |
| 429 | Rate limit exceeded |

## Key Guidelines

- Always set `parse: true` for supported sources to get structured data
- Use ZIP codes for US e-commerce geo-location (e.g., `"90210"`)
- Use country/state format for search engines (e.g., `"California,United States"`)
- Add `render: "html"` for JavaScript-heavy pages
