---
name: content-search-summarization
description: Use this skill when asked to search public content platforms such as Bilibili or YouTube, pick the top relevant results for a topic, and summarize each item with links and brief overviews. Uses Runtime-aware routing — opencli first, fetch second, browser last.
license: Proprietary session artifact for local Copilot use
---

# Content search summarization skill

Use this skill when the user asks for tasks such as:

- "Find the top 5 videos about X on Bilibili and summarize them"
- "Search YouTube for a topic and give me the best results"
- "Look up public content on a supported site and summarize the top items"

## Execution routing (critical)

Before attempting any search, classify the platform and pick the best execution path:

```text
if opencli supports the platform:
    use opencli (deterministic, zero LLM cost, session-reuse)
elif public API exists:
    use fetch (structured JSON, no rendering needed)
elif site is SSR and publicly accessible:
    use web_fetch or Playwright (metadata extraction)
else:
    require login-state browser or declare blocked
```

This is the single most important decision in this skill.

### Platform registry

| Platform | opencli command | Public API | SSR fetch | Access tier |
|----------|----------------|-----------|-----------|-------------|
| Bilibili | `opencli bilibili search --keyword <kw>` | `api.bilibili.com` | partial | T1: opencli preferred |
| YouTube | `opencli youtube search --keyword <kw>` | YouTube Data API | partial | T1: opencli preferred |
| 小红书 | `opencli xiaohongshu search --keyword <kw>` | ❌ | ❌ SPA shell | T2: opencli required |
| 抖音 | `opencli tiktok search --keyword <kw>` | ❌ | ❌ JS obfuscated | T2: opencli required |
| 知乎 | `opencli zhihu search --keyword <kw>` | ❌ | ❌ login-gated | T2: opencli required |
| 微博 | `opencli weibo search --keyword <kw>` | ❌ | ❌ | T2: opencli required |
| 豆瓣 | `opencli douban search --keyword <kw>` | ❌ | partial | T2: opencli preferred |
| arXiv | ❌ | `export.arxiv.org` | ✅ SSR | T3: fetch / web_fetch |
| Wikipedia | `opencli wikipedia search --keyword <kw>` | `en.wikipedia.org/api` | ✅ SSR | T1: any path works |
| HackerNews | `opencli hackernews top` | `hn.algolia.com/api` | ✅ SSR | T1: any path works |
| Reddit | `opencli reddit search --keyword <kw>` | ❌ | partial | T1: opencli preferred |
| BBC | `opencli bbc news` | ❌ | ✅ SSR | T3: fetch / web_fetch |

### Access tier definitions

- **T1**: multiple working paths; opencli preferred for consistency
- **T2**: opencli required; no public fallback available; if opencli is unavailable, declare blocked with explanation
- **T3**: public fetch works reliably; opencli optional

### When opencli is unavailable

If `opencli` is not installed or Browser Bridge is not connected:

- for T1 platforms: fall back to fetch or web_fetch
- for T2 platforms: **stop immediately and tell the user** — do not attempt blind scraping
- for T3 platforms: use fetch / web_fetch directly
- always note which execution path was used in the output

## Primary strategy

1. Check the platform registry above and pick the correct execution path.
2. For opencli: run the command and parse structured output (JSON/YAML).
3. For fetch/web_fetch: construct the appropriate URL and extract metadata.
4. Rank results by practical relevance, not just raw view count:
   - exact keyword match in title
   - clarity of topic focus
   - likely tutorial / overview value
   - recency and popularity as secondary hints
5. Always include source links.

## Supported workflow

### 1. Search

For opencli-supported platforms:

```bash
opencli bilibili search --keyword "<keyword>" --limit 10 -f json
opencli youtube search --keyword "<keyword>" --limit 10 -f json
opencli xiaohongshu search --keyword "<keyword>" --limit 10 -f json
```

For public API platforms:

```text
https://api.bilibili.com/x/web-interface/search/type?keyword=<keyword>&search_type=video
https://hn.algolia.com/api/v1/search?query=<keyword>
```

For SSR platforms:

```text
Use web_fetch to load the search result page and extract metadata.
```

### 2. Filter and rank

Prefer results that:

- directly match the requested topic
- are clearly about the requested concept rather than loosely related content
- look like tutorials, explainers, or practical overviews

Avoid results that:

- are generic entertainment content that only happens to mention the keyword
- are clearly unrelated despite matching a broad term like `AI`

### 3. Fetch more detail

When possible, open each selected result page and collect:

- page title
- meta description
- page description
- tags / keywords
- lightweight stat text if available

Use those fields to produce a summary that is better than title-only guessing.

### 4. Summarize

For each selected item, provide:

- rank
- original title
- optional translated / normalized title if helpful
- platform / source
- capture time when available
- source link
- author / uploader if available
- a short summary of what the item is likely about
- confidence level: `high`, `medium`, or `low`
- a brief caveat when the summary is inferred from metadata rather than full content
- execution path used (opencli / fetch / web_fetch / browser)

Be clear when the summary is inferred from metadata and page description rather than a full transcript.

## Output format

Return a compact ranked list.

Recommended structure:

1. execution path used and why
2. query keyword and capture time
3. a ranked list of top items
4. a short summary paragraph for each item

Recommended per-item fields:

- `Rank`
- `Title`
- `Platform`
- `Link`
- `Author`
- `Captured at`
- `Summary`
- `Confidence`
- `Caveat`
- `Execution path`

## Proven example patterns

### Bilibili via opencli (recommended)

```bash
opencli bilibili search --keyword "AI agent" --limit 10 -f json
```

Then filter the top 5 most relevant, open detail pages for metadata enrichment.

### arXiv via web_fetch (public SSR)

```text
web_fetch https://arxiv.org/search/?query=AI+agent&searchtype=all
```

Extract paper titles, authors, abstracts from the SSR result page.

### Xiaohongshu (opencli required)

```bash
opencli xiaohongshu search --keyword "AI skill" --limit 10 -f json
```

If opencli is not available, declare: "小红书 is a T2 platform that requires opencli with Browser Bridge. Public scraping is not reliable."

## Key cautions

- Do not claim you watched the whole video unless you actually processed a transcript or full content.
- Phrase summaries as "主要在讲 / 偏向 / 看起来聚焦于" when based on metadata.
- Keep links and titles accurate.
- For broad keywords like `AI`, narrow to the user's likely intent if enough exact-match results exist.
- If publish time or exact timestamp is unavailable, explicitly say it was not visible in the captured result.
- Add one explicit evidence note per item (for example, title keyword match, description snippet, or metadata field used).
- **Never attempt blind scraping on T2 platforms without opencli.** Declare blocked instead.