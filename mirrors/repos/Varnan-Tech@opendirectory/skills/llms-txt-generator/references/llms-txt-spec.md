# llms.txt Specification

Proposed by Jeremy Howard (fast.ai / answer.ai). See: https://llmstxt.org

## Purpose

`/llms.txt` is a markdown file at the root of a website that helps LLMs understand what the site is about and where to find authoritative content. It is the AI equivalent of `robots.txt` — but instead of telling crawlers what to avoid, it tells AI agents what to read.

## Why It Matters

When an AI agent is asked about a company or product, it may visit the site. Without `llms.txt`, the agent has to infer structure from HTML, JavaScript-heavy pages, and noise. With `llms.txt`, the agent gets a clean, structured, LLM-optimized summary in seconds.

Missing `llms.txt` = invisible to AI agents and generative search (GEO failure).

---

## File Format

The file MUST be valid Markdown. MUST be served at exactly: `https://yourdomain.com/llms.txt`

### Required Elements

**1. H1 Header — Site/Product Name**
```markdown
# Product Name
```

**2. Optional Summary Block (blockquote or plain paragraph)**
```markdown
> One-paragraph plain-English description of what this site is about. 
> Written for an LLM, not for marketing. Factual, concise, no fluff.
```

**3. H2 Sections with Link Lists**
Each section is an H2 heading followed by a list of links with descriptions:
```markdown
## Section Name

- [Page Title](https://domain.com/page): One-sentence description of what this page contains.
- [Another Page](https://domain.com/other): What an LLM will find here.
```

### Recommended Sections (use only what exists on the site)

| Section | What to include |
|---------|----------------|
| `## Docs` | API reference, getting started, installation guides |
| `## API` | API endpoints, SDKs, developer reference |
| `## Blog` | Top 5-10 most relevant/recent blog posts |
| `## Examples` | Code examples, tutorials, demos |
| `## About` | Company, team, mission pages |
| `## Pricing` | Pricing page if public |
| `## Changelog` | Release notes, changelog |

### Link Description Format

Keep descriptions factual and information-dense. Write what an LLM would find there:

**Good:**
```markdown
- [API Authentication](https://api.example.com/docs/auth): How to obtain and use API keys, OAuth 2.0 flow, token refresh, and rate limit headers.
```

**Bad:**
```markdown
- [API Authentication](https://api.example.com/docs/auth): Learn about our amazing auth system!
```

---

## llms-full.txt (Optional)

A second file at `/llms-full.txt` that contains the FULL prose content of key pages — suitable for LLMs that want to ingest everything at once rather than follow links.

Format: same as `llms.txt` but with full page content pasted inline under each link, separated by `---`.

---

## Validation Checklist

Before saving the output, check:
- [ ] File starts with an H1 (site/product name)
- [ ] Has at least one H2 section with links
- [ ] Every link description is factual (no marketing fluff)
- [ ] All URLs are absolute (https://...), not relative
- [ ] No broken links (verify URLs resolve during crawl)
- [ ] File is clean Markdown with no HTML tags
- [ ] Under 5,000 words (LLMs have context limits)
