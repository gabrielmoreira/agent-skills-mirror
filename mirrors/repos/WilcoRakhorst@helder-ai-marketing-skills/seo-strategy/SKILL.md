---
name: seo-strategy
description: "Search engine optimization strategy and implementation: technical SEO, on-page optimization, content structure, internal linking, and SEO in the AI era. Use when the user wants to set up an SEO strategy, optimize a website for search engines, fix technical SEO issues, or when terms like 'SEO', 'search engine optimization', 'Google rankings', 'rank higher', 'improve rankings', 'technical SEO', 'on-page SEO', 'meta tags', 'internal links', 'content structure', 'indexation', 'crawlability', 'page speed', 'Core Web Vitals', 'SEO audit', 'SEO strategy', or 'organic traffic' are mentioned. For keyword research, see seo-keyword-research. For AI visibility (GEO), see geo-optimization."
---

# SEO Strategy

SEO = optimizing a website for organic search results. Core principle: content for people, not for systems.

**Related skills:** geo-optimization (E-E-A-T, GEO, writing guidelines) | seo-keyword-research (keywords) | content-creator (writing & publishing)

## SEO in the AI era

| Still works                          | No longer works                        |
|:-------------------------------------|:---------------------------------------|
| In-depth, substantive content        | Thin keyword-only pages                |
| Clear structure (H1-H3)             | Short, generic blog posts              |
| Authority through content clusters   | Keyword stuffing and over-optimization |
| Internal links between topics        | Writing only "for Google"              |
| Technical foundation (indexation, speed) | Focusing purely on individual keywords |

SEO is the foundation that GEO builds on. See the geo-optimization skill for AI visibility and anti-patterns.

## Technical SEO

**Crawlability:** XML sitemap up-to-date | robots.txt correct | no unintended noindex | canonical tags for duplicates | clean URLs | 301 redirects (no 404s) | HTTPS required

**Mobile-first indexing:** Fully rolled out by Google since July 2024 — Google indexes exclusively the mobile version of pages. Ensure content, structured data, and internal links are identical on desktop and mobile. No mobile version = not indexed.

**IndexNow:** Protocol to notify search engines (Bing, Yandex, Naver) directly when pages are created or updated. Free, faster indexation than waiting for a crawl. Implementation: generate a key via Bing Webmaster Tools and add a simple API call to your publishing workflow. WordPress: use the IndexNow plugin. *(Note: Google has its own crawl prioritization and does not use IndexNow.)*

**Core Web Vitals:** LCP < 2.5s | INP < 200ms | CLS < 0.1 (source: web.dev/articles/vitals). For details: use a web performance optimization tool or skill.

**Schema Markup:** LocalBusiness (business details) | Article (blog posts) | BreadcrumbList | Service | Person (author, E-E-A-T) | VideoObject (videos)

**Schema status (Feb 2026) — only use active types:**

| Type | Status | Notes |
|:-----|:-------|:------|
| FAQPage | Restricted Aug 2023 | ONLY for government and healthcare; not for commercial sites |
| HowTo | Removed Sep 2023 | No rich results — do not use |
| SpecialAnnouncement | Expired Jul 2025 | Remove from existing markup |
| ClaimReview | Expired Jun 2025 | Remove from existing markup |
| Dataset | Expired end 2025 | No rich results anymore |

**JSON-LD rendering:** Ensure JSON-LD is in the initial server-rendered HTML. JavaScript-injected structured data can be processed with a delay by Google — critical for Product and Offer markup. *(Source: Google JS SEO guidelines Dec 2025)*

**JavaScript SEO — 4 critical rules (Dec 2025):**
1. **Canonical conflict:** If the raw HTML has a different canonical than JavaScript injects, Google may use *both*. Ensure they are identical.
2. **noindex via JavaScript:** If raw HTML contains `noindex` but JavaScript removes it, Google may still honor the raw HTML signal. Always send noindex in the initial server response.
3. **Non-200 status codes:** Google does not render JavaScript on pages returning non-HTTP 200. Meta tags and structured data via JS are then invisible to Googlebot.
4. **Structured data in JS:** Product and Offer markup via JS may be processed with a delay. Always embed time-sensitive structured data in server-rendered HTML.

## On-page SEO

- **Title:** unique, primary keyword near the front, max 60 characters
- **Meta description:** unique, 120-155 characters, primary keyword + CTA
- **Headings:** one H1 per page, H2 for main sections, H3 for subsections, logical hierarchy
- **Content:** lead with the answer, short paragraphs (3-4 sentences), bullet points
- **Semantic SEO:** use synonyms and related terms (entities). Google expects context: for "baking" also "oven", "temperature", "ingredients". Without these, Google understands the topic less well.
- **URL:** short, descriptive, includes primary keyword, hyphens
- **Images:** descriptive filenames (`seo-checklist-smb.jpg`), alt text, WebP/AVIF, properly sized
- **Video:** YouTube embeds increase engagement, VideoObject schema, transcription for indexation

## Internal links and content clusters

- Link from within content, use descriptive anchor texts (not "click here")
- Pillar links to at least 3 supporting articles; supporting articles link back

```
Pillar (core topic)
  |-- Supporting A  |-- Supporting B  |-- Supporting C  |-- Checklist D
```

## Search intent

| Type               | Example                     | Page type               | CTA                          |
|:-------------------|:----------------------------|:------------------------|:-----------------------------|
| **Informational**  | "What is SEO?"              | Blog, FAQ               | Newsletter, related article  |
| **Navigational**   | "Login [Brand]"             | Login, contact          | --                           |
| **Commercial**     | "Best SEO agency 2026"      | Comparison, pillar      | Quote request                |
| **Transactional**  | "Request SEO audit"         | Services, contact       | Direct contact, order form   |

**SEO vs GEO per intent:** SEO-first for navigational and transactional queries (blue link dominant). GEO-first for long-tail informational/commercial questions where AI Overviews take the most space. See the geo-optimization skill.

## SEO content length guidelines

| Type                     | Length                |
|:-------------------------|:----------------------|
| **Pillar page**          | 1,500-2,500 words     |
| **Supporting article**   | 1,200-1,800 words     |
| **FAQ page**             | 800-1,200 words       |
| **Checklist/how-to**     | 600-1,200 words       |
| **Service page**         | 800-1,500 words       |

**Workflow:** keyword research > determine search intent > set up structure > write with expertise > internal links > meta tags > CTA + social proof > publish > monitor

**Helpful Content test:** Does this article add something that doesn't already exist? (original data, unique case study, practical experience). Avoid interstitial pop-ups. If not: rewrite or remove.

> **Myth-busting:** Word count is *not* a direct ranking factor (confirmed by Google). A 500-word article that fully answers the search query outranks a 2,000-word article that doesn't. Use length guidelines as minimums for topical coverage, not as a goal in themselves. The Flesch readability score is also *not* a ranking factor — Yoast deprioritized it in v19.3. Use readability as a quality indicator, not as an SEO metric.

Writing guidelines (E-E-A-T, language, authorship): see the geo-optimization skill.

## Conversion (CRO)

Findability is step 1, action is step 2. Every SEO page needs a logical next step (button, form, lead magnet). Social proof (reviews, logos) on landing pages reduces bounce rate.

## Voice Search

**90%+ of voice answers** come directly from Featured Snippets. Voice queries have a local intent in 46% of cases.

| Check | Requirement |
|:------|:------------|
| TTFB | < 2 seconds (strongest selection signal) |
| HTTPS | Required |
| Featured Snippet | Direct answer within the first 40-55 words after an H-tag |
| FAQ headings | Min. 3 H2/H3 headings as a question sentence |
| `speakable` schema | Marks top answers for Google Assistant |
| LocalBusiness schema | For local intent (address, phone, opening hours) |

**Platform → index source:** Google Assistant → Google | Siri → **Bing** | Alexa → **Bing** | Cortana → Bing. Submit Siri- and Alexa-visible content also via **Bing Webmaster Tools**.

**`speakable` schema (WordPress: add via JSON-LD in functions.php or SEO plugin):**
```json
{
  "@type": "Article",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".article-summary", "h2 + p"]
  }
}
```

*Source: Bhanunamikaze/Agentic-SEO-Skill*

## Google AI Mode

In May 2025, Google launched **AI Mode** as a separate tab in Google Search (available in 180+ countries). Unlike AI Overviews (above organic results), AI Mode offers a fully conversational search experience **without organic blue links**. AI citation is the only visibility mechanism within AI Mode.

**Implication:** Treat AI citation as an independent KPI alongside traditional rankings and traffic. Monitor visibility in Google AI Mode, AI Overviews, ChatGPT, Perplexity, and Bing Copilot separately — not only via Search Console.

*Source: Google I/O May 2025*

## Authority and external signals

- **Backlinks:** relevance over quantity; one authoritative link > 100 vague links
- **Digital PR:** mentions on niche websites or local news sites
- **Brand mentions:** brand name on social media and forums builds trust, even without a link. See the geo-optimization skill for the GEO scorecard (external validation, niche association, sentiment) and the Reddit factor.

## Content maintenance

| Step            | Frequency     | Action                                                    |
|:----------------|:--------------|:----------------------------------------------------------|
| **Audit**       | 6-12 months   | Which pages are gaining/losing?                           |
| **Prune**       | After audit   | Remove or merge low-value content                         |
| **Refresh**     | Ongoing       | Update data, dates, internal links                        |
| **Quick wins**  | Monthly       | Optimize position 4-10 towards top 3                      |
| **Cannibalization** | After audit | Multiple URLs ranking for the same keyword? Merge to strongest URL + 301 redirect, or clarify intent differentiation |

## Local SEO

- Google Business Profile: claim, verify, complete fully, respond to reviews
- NAP (Name, Address, Phone) consistent across website + external profiles
- Local keywords in title tags and content
- Schema LocalBusiness with address

## Monitoring

| Tool                    | Purpose                                       | Cost           |
|:------------------------|:----------------------------------------------|:---------------|
| **Search Console**      | Indexation, CTR, search performance            | Free           |
| **GA4**                 | Engagement, conversions, behavior              | Free           |
| **Screaming Frog**      | Deep-crawl technical errors                    | Free (500 URLs)|
| **Ahrefs / Semrush**    | Competition, backlinks, keyword tracking       | Paid           |
| **PageSpeed Insights**  | Core Web Vitals per page                       | Free           |

**SMB minimum:** Search Console + GA4 + Yoast SEO (free).

**CTR optimization (quick win):** Find pages in Search Console with high impressions but low CTR. Optimize title and meta description with action words ("Step-by-step", "2026 update", "Free check") to get more clicks from the same position.

## WordPress REST API automation

SEO metadata can be automated via the WordPress REST API, reducing manual work significantly.

**Fields that work via REST API** (`wp-json/wp/v2/posts/{id}`, method POST, meta object):

| Field                        | Works via API | Notes                                  |
|:-----------------------------|:--------------|:---------------------------------------|
| `_yoast_wpseo_title`        | Yes           | Use `%%sep%%` and `%%sitename%%`       |
| `_yoast_wpseo_metadesc`     | Yes           | Max 156 chars, include keyphrase       |

**Fields that may NOT work via API** (depends on installation):

| Field                        | Reason                                         |
|:-----------------------------|:-----------------------------------------------|
| `_yoast_wpseo_focuskw`      | Not always registered in REST API schema       |

**Recommended workflow for automated publishing:**

1. Script creates draft post — `_yoast_wpseo_title` and `_yoast_wpseo_metadesc` set via API
2. Manually in wp-admin: Yoast SEO > SEO tab > Set Focus keyphrase > Save
3. Then check the Yoast analysis

**Yoast thresholds to target:**

| Check                     | Requirement                                                      |
|:--------------------------|:-----------------------------------------------------------------|
| Meta description          | 120-156 characters, keyphrase included                           |
| Keyphrase density         | Min. 4x in text for an average article (700-1,200 words)        |
| Keyphrase in subheading   | Min. 1 H2 or H3 containing the keyphrase or synonym             |
| Keyphrase in introduction | First paragraph must contain the keyphrase                       |
| Outbound links            | Min. 1-2 external links to authoritative sources                 |
| Featured image alt text   | Include keyphrase or synonym                                     |

## SEO checklist for SMBs

**Technical:** HTTPS | sitemap in Search Console | robots.txt | no 404s | responsive | Core Web Vitals | schema markup

**On-page:** unique titles (60 chars) + descriptions (120-155 chars) | one H1 | logical H2-H3 | alt text | descriptive filenames | internal links

**Content:** pillar + supporting articles | answers real questions | author + date visible | min. 1,200 words | search intent determined | CTA per page

**Local:** Business Profile complete | NAP consistent | local keywords

## Scope

| This skill                         | Refer to                                    |
|:-----------------------------------|:--------------------------------------------|
| SEO strategy, technical, on-page   | seo-keyword-research: keywords              |
| Content clusters, internal links   | geo-optimization: AI visibility, GEO        |
| Local SEO, CRO basics             | content-creator: writing & publishing       |

## Data integrity

- Only verified facts; no rankings or statistics without a source

## References

- Google: [Web Vitals](https://web.dev/articles/vitals) (LCP, INP, CLS thresholds)
- Google Search Central: [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- Google Search Central: [How Search Works](https://developers.google.com/search/docs/fundamentals/how-search-works)
- Yoast: [SEO REST API](https://developer.yoast.com/customization/apis/rest-api/) (read-only; meta via WP REST API meta object)
- WordPress: [REST API — Posts](https://developer.wordpress.org/rest-api/reference/posts/)
