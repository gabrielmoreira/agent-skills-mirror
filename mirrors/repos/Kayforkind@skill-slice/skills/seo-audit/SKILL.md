---
name: seo-audit
description: "Runs a prioritized technical and on-page SEO audit covering crawl/index, ranking drops, Core Web Vitals, meta tags, and internal links. Use when the user wants an SEO health check or asks why traffic or rankings fell. Not for Next.js-specific Search Console coverage fixes (nextjs-seo-indexing), schema-markup chairs, or programmatic SEO page factories."
version: 2.0.1
---

# SEO Audit

You are an expert in search engine optimization. Your goal is to identify SEO issues and provide actionable recommendations to improve organic search performance.

## When to Use

Use this skill whenever the user asks to audit, review, or diagnose SEO issues on their site. Trigger keywords include:

- "SEO audit," "technical SEO," "SEO health check"
- "Why am I not ranking," "lost rankings," "my traffic dropped"
- "On-page SEO," "meta tags review," "SEO issues"
- "Not showing up in Google," "site isn't ranking," "Google update hit me"
- "Page speed," "core web vitals," "crawl errors," "indexing issues"
- Vague phrases like "my SEO is bad" or "help with SEO" — start with an audit

**Do NOT use this skill for:**
- Building pages at scale to target keywords → use **programmatic-seo**
- Adding structured data / schema markup → use **schema**
- AI search optimization (AEO, GEO, LLMO, AI Overviews) → use **ai-seo**

## Prerequisites

1. **Check for product marketing context first.** If `.agents/product-marketing.md` exists (or `.claude/product-marketing.md`, or the legacy `product-marketing-context.md` filename in older setups), read it before asking questions. Use that context and only ask for information not already covered or specific to this task.

2. **Gather site context before auditing:**
   - What type of site? (SaaS, e-commerce, blog, local business, multilingual, etc.)
   - What's the primary business goal for SEO?
   - What keywords/topics are priorities?
   - Any known issues or concerns?
   - Current organic traffic level?
   - Recent changes or migrations?
   - Full site audit or specific pages?
   - Technical + on-page, or one focus area?
   - Access to Search Console / analytics?

3. **Load reference files when relevant:**
   - `references/international-seo.md` — load when the site serves multiple languages or regions. Contains evidence and source URLs for hreflang, canonical + i18n, sitemaps, URL structure, and content quality across locales.
   - `references/ai-writing-detection.md` — load when reviewing content quality for common AI writing patterns to avoid (em dashes, overused phrases, filler words).

## Procedure

### Step 1 — Audit in Priority Order

Always audit in this order. Issues higher on the list block the impact of issues lower on the list.

1. **Crawlability & Indexation** — can Google find and index it?
2. **Technical Foundations** — is the site fast and functional?
3. **On-Page Optimization** — is content optimized?
4. **Content Quality** — does it deserve to rank?
5. **Authority & Links** — does it have credibility?

### Step 2 — Technical SEO Audit

#### 2a. Crawlability

**Robots.txt**
- Check for unintentional blocks
- Verify important pages are allowed
- Check sitemap reference

**XML Sitemap**
- Exists and is accessible
- Submitted to Search Console
- Contains only canonical, indexable URLs
- Updated regularly
- Proper formatting

**Site Architecture**
- Important pages within 3 clicks of homepage
- Logical hierarchy
- Internal linking structure
- No orphan pages

**Crawl Budget Issues** (for large sites)
- Parameterized URLs under control
- Faceted navigation handled properly
- Infinite scroll with pagination fallback
- Session IDs not in URLs

#### 2b. Indexation

**Index Status**
- Run `site:domain.com` check in Google
- Check Search Console coverage report
- Compare indexed vs. expected

**Indexation Issues**
- Noindex tags on important pages
- Canonicals pointing wrong direction
- Redirect chains/loops
- Soft 404s
- Duplicate content without canonicals

**Canonicalization**
- All pages have canonical tags
- Self-referencing canonicals on unique pages
- HTTP → HTTPS canonicals
- www vs. non-www consistency
- Trailing slash consistency

#### 2c. Site Speed & Core Web Vitals

**Core Web Vitals thresholds:**
- LCP (Largest Contentful Paint): < 2.5s
- INP (Interaction to Next Paint): < 200ms
- CLS (Cumulative Layout Shift): < 0.1

**Speed factors to check:**
- Server response time (TTFB)
- Image optimization
- JavaScript execution
- CSS delivery
- Caching headers
- CDN usage
- Font loading

**Tools:** PageSpeed Insights, WebPageTest, Chrome DevTools, Search Console Core Web Vitals report.

#### 2d. Mobile-Friendliness

- Responsive design (not separate m. site)
- Tap target sizes
- Viewport configured
- No horizontal scroll
- Same content as desktop
- Mobile-first indexing readiness

#### 2e. Security & HTTPS

- HTTPS across entire site
- Valid SSL certificate
- No mixed content
- HTTP → HTTPS redirects
- HSTS header (bonus)

#### 2f. URL Structure

- Readable, descriptive URLs
- Keywords in URLs where natural
- Consistent structure
- No unnecessary parameters
- Lowercase and hyphen-separated

### Step 3 — International SEO & Localization

**Only check when the site serves multiple languages or regions.** Misconfigurations can suppress indexing of entire locale variants or drag down site-wide quality signals. Load `references/international-seo.md` for evidence and source URLs.

#### 3a. Hreflang

Three equivalent placement methods: HTML `<link>` in `<head>`, HTTP `Link` headers, XML sitemap `<xhtml:link>`. If using multiple, they must agree — conflicting signals cause Google to drop that pair. For 10+ locales, prefer sitemap-based (no page weight, no per-request cost).

**Check for:**
- Self-referencing entry on every page (page must include itself in the hreflang set)
- Reciprocal links (if A points to B, B must point back to A — or both are ignored)
- Valid codes: ISO 639-1 language + optional ISO 3166-1 Alpha 2 region (e.g., `en`, `en-GB` — never `en-UK`)
- `x-default` present, pointing to fallback page (language selector or default locale)
- All target URLs return 200, are indexable, and match their canonical URL
- No duplicate language-region codes pointing to different URLs

**Common errors:** Missing self-referencing entry (all hreflang ignored). No return tag / one-directional (pair dropped). Invalid codes like `en-UK` (use `en-GB`). Hreflang target is non-canonical, 404, or blocked (cluster discarded). HTML and sitemap annotations disagree (conflicting pair dropped).

**At scale:** `<xhtml:link>` children don't count toward the 50K URL sitemap limit, but the 50MB file size limit becomes the bottleneck (plan 2K–5K URLs per file with full hreflang). Focus hreflang on pages receiving wrong-language traffic — not required on every page. For Bing: supplement with `<html lang>` and `<meta http-equiv="content-language">` (Bing treats hreflang as a weak signal).

#### 3b. Canonicalization for Multilingual Sites

- Each locale page must self-canonical (e.g., `/ar/page` canonicals to `/ar/page`)
- Never cross-locale canonical (French to English) — suppresses the non-canonical locale entirely
- Canonical URL must appear in the hreflang set — if not, all hreflang is ignored
- Canonical overrides hreflang when they conflict
- Protocol/domain must be consistent across canonical, hreflang, and sitemap (`https` + same domain variant)
- Paginated locale pages: self-referencing canonical per page (never canonical page 2+ to page 1)

**Common mistakes:** all locales canonical to English (kills indexing), canonical URL not in hreflang set (silently ignored), protocol mismatch between canonical and hreflang, CMS setting deep page canonical to homepage.

#### 3c. International Sitemaps

**Check for:**
- `xmlns:xhtml` namespace on `<urlset>`, each `<url>` includes `<xhtml:link>` for all locales including itself
- `x-default` alternate included; all URLs absolute (full protocol + domain)
- Sitemap index in Search Console and robots.txt; split by content type, not by locale

**Next.js caveat:** `alternates.languages` does NOT auto-include a self-referencing `<xhtml:link>` for the `<loc>` URL — you must add the current locale explicitly.

#### 3d. Locale URL Structure

**Recommended:** Subdirectories (`/en/`, `/ar/`). **Acceptable:** Subdomains or ccTLDs. **Not recommended:** URL parameters (`?lang=en`).

**Check for:**
- Consistent locale prefix strategy; all locales prefixed (hiding locale from URLs prevents Google from distinguishing versions)
- Root URL handled as `x-default` with redirect, or serves default locale content
- No IP/Accept-Language content negotiation (Googlebot: US IPs, no Accept-Language header)
- Trailing slash + case consistency across locale paths, canonicals, hreflang, and sitemaps
- 301 redirects from non-canonical format to canonical

**Note:** Google's International Targeting report in Search Console is deprecated. Geotargeting relies on hreflang, content signals, and linking patterns.

#### 3e. Content Quality Across Locales

**Translation quality:**
- AI-translated content is not inherently spam (Google's 2025 stance), but scaled low-value translations can trigger scaled content abuse policy
- Google uses visible content to determine language — translate ALL page content (title, description, headings, body), not just boilerplate
- Translating only template/nav while main content stays in original language creates duplicates

**Thin locale pages:**
- Helpful content system is site-wide — many thin locale pages can suppress rankings for strong pages too
- Don't noindex thin locales (wastes crawl budget) or cross-locale canonical (conflicts with hreflang)
- Best approach: don't create locale pages you cannot make genuinely helpful

**Check for:**
- All locale pages have fully translated main content (not just UI chrome)
- No near-identical content across locales ("Duplicate, Google chose different canonical" in GSC)
- Hreflang only for locales with genuine content and search demand
- Localized signals: currency, phone format, addresses where applicable
- Broken hreflang links (404s, redirects) waste crawl budget AND invalidate hreflang clusters

### Step 4 — On-Page SEO Audit

#### 4a. Title Tags

**Check for:**
- Unique titles for each page
- Primary keyword near beginning
- 50–60 characters (visible in SERP)
- Compelling and click-worthy
- Brand name placement (end, usually)

**Common issues:** Duplicate titles, too long (truncated), too short (wasted opportunity), keyword stuffing, missing entirely.

#### 4b. Meta Descriptions

**Check for:**
- Unique descriptions per page
- 150–160 characters
- Includes primary keyword
- Clear value proposition
- Call to action

**Common issues:** Duplicate descriptions, auto-generated garbage, too long/short, no compelling reason to click.

#### 4c. Heading Structure

**Check for:**
- One H1 per page
- H1 contains primary keyword
- Logical hierarchy (H1 → H2 → H3)
- Headings describe content
- Not just for styling

**Common issues:** Multiple H1s, skip levels (H1 → H3), headings used for styling only, no H1 on page.

#### 4d. Content Optimization

**Primary page content:**
- Keyword in first 100 words
- Related keywords naturally used
- Sufficient depth/length for topic
- Answers search intent
- Better than competitors

**Thin content issues:**
- Pages with little unique content
- Tag/category pages with no value
- Doorway pages
- Duplicate or near-duplicate content

#### 4e. Image Optimization

**Check for:**
- Descriptive file names
- Alt text on all images
- Alt text describes image
- Compressed file sizes
- Modern formats (WebP)
- Lazy loading implemented
- Responsive images

#### 4f. Internal Linking

**Check for:**
- Important pages well-linked
- Descriptive anchor text
- Logical link relationships
- No broken internal links
- Reasonable link count per page

**Common issues:** Orphan pages (no internal links), over-optimized anchor text, important pages buried, excessive footer/sidebar links.

#### 4g. Keyword Targeting

**Per page:**
- Clear primary keyword target
- Title, H1, URL aligned
- Content satisfies search intent
- Not competing with other pages (cannibalization)

**Site-wide:**
- Keyword mapping document
- No major gaps in coverage
- No keyword cannibalization
- Logical topical clusters

### Step 5 — Content Quality Assessment

#### 5a. E-E-A-T Signals

**Experience**
- First-hand experience demonstrated
- Original insights/data
- Real examples and case studies

**Expertise**
- Author credentials visible
- Accurate, detailed information
- Properly sourced claims

**Authoritativeness**
- Recognized in the space
- Cited by others
- Industry credentials

**Trustworthiness**
- Accurate information
- Transparent about business
- Contact information available
- Privacy policy, terms
- Secure site (HTTPS)

#### 5b. Content Depth

- Comprehensive coverage of topic
- Answers follow-up questions
- Better than top-ranking competitors
- Updated and current

#### 5c. User Engagement Signals

- Time on page
- Bounce rate in context
- Pages per session
- Return visits

### Step 6 — Check Common Issues by Site Type

#### SaaS / Product Sites
- Product pages lack content depth
- Blog not integrated with product pages
- Missing comparison/alternative pages
- Feature pages thin on content
- No glossary/educational content

#### E-commerce
- Thin category pages
- Duplicate product descriptions
- Missing product schema
- Faceted navigation creating duplicates
- Out-of-stock pages mishandled

#### Content / Blog Sites
- Outdated content not refreshed
- Keyword cannibalization
- No topical clustering
- Poor internal linking
- Missing author pages

#### Multilingual / Multi-Regional Sites
- Hreflang errors (missing return tags, invalid codes, no self-reference)
- Canonical conflicting with hreflang (cross-locale canonical suppresses indexing)
- Thin locale pages dragging down site-wide quality signal
- Only boilerplate translated, main content identical across locales
- No x-default fallback declared
- Sitemap missing hreflang alternates or missing reciprocal entries
- IP-based redirects hiding content from Googlebot
- Framework locale mode hiding locale from URLs

#### Local Business
- Inconsistent NAP
- Missing local schema
- No Google Business Profile optimization
- Missing location pages
- No local content

### Step 7 — Produce the Audit Report

Use this structure for the final output:

**Executive Summary**
- Overall health assessment
- Top 3–5 priority issues
- Quick wins identified

**Technical SEO Findings** — for each issue:
- **Issue**: What's wrong
- **Impact**: SEO impact (High/Medium/Low)
- **Evidence**: How you found it
- **Fix**: Specific recommendation
- **Priority**: 1–5 or High/Medium/Low

**On-Page SEO Findings** — same format as above

**Content Findings** — same format as above

**Prioritized Action Plan**
1. Critical fixes (blocking indexation/ranking)
2. High-impact improvements
3. Quick wins (easy, immediate benefit)
4. Long-term recommendations

## Pitfalls

### Schema Markup Detection Limitation — CRITICAL

**`web_fetch` and `curl` cannot reliably detect structured data / schema markup.**

Many CMS plugins (AIOSEO, Yoast, RankMath) inject JSON-LD via client-side JavaScript — it won't appear in static HTML or `web_fetch` output (which strips `<script>` tags during conversion).

**To accurately check for schema markup, use one of these methods:**
1. **Browser tool** — render the page and run: `document.querySelectorAll('script[type="application/ld+json"]')`
2. **Google Rich Results Test** — https://search.google.com/test/rich-results
3. **Screaming Frog export** — if the client provides one, use it (SF renders JavaScript)

Reporting "no schema found" based solely on `web_fetch` or `curl` leads to false audit findings — these tools can't see JS-injected schema. Always use a JavaScript-rendering method for schema detection.

### International SEO Pitfalls

- **Missing self-referencing hreflang entry** → all hreflang on that page is ignored
- **No return tag / one-directional hreflang** → pair is dropped
- **Invalid codes like `en-UK`** → use `en-GB` (ISO 3166-1 Alpha 2)
- **Hreflang target is non-canonical, 404, or blocked** → entire cluster discarded
- **HTML and sitemap hreflang annotations disagree** → conflicting pair dropped
- **All locales canonical to English** → kills indexing of non-English locales
- **Canonical URL not in hreflang set** → all hreflang silently ignored
- **Protocol mismatch between canonical and hreflang** → signals conflict
- **Next.js `alternates.languages`** → does NOT auto-include self-referencing `<xhtml:link>` for the `<loc>` URL; must add current locale explicitly
- **IP-based / Accept-Language redirects** → hide content from Googlebot (US IPs, no Accept-Language header)
- **Translating only boilerplate/nav** → creates duplicates, not localized pages
- **Noindex on thin locale pages** → wastes crawl budget; cross-locale canonical conflicts with hreflang
- **Google's International Targeting report in Search Console is deprecated** — geotargeting relies on hreflang, content signals, and linking patterns

### General Audit Pitfalls

- Auditing on-page issues before confirming crawlability/indexation — fixes won't matter if Google can't crawl the page
- Reporting schema as absent based on `web_fetch` or `curl` alone
- Ignoring site type — common issues differ significantly between SaaS, e-commerce, blog, multilingual, and local business sites
- Not checking for keyword cannibalization across pages
- Overlooking thin content's site-wide impact (helpful content system is site-wide)

## Verification

After completing the audit, verify key findings before reporting:

1. **Schema markup** — confirm via browser tool or Rich Results Test, NOT `web_fetch`/`curl`:
   - Browser: `document.querySelectorAll('script[type="application/ld+json"]')`
   - URL: https://search.google.com/test/rich-results

2. **Indexation** — run `site:domain.com` in Google and compare against expected page count

3. **Core Web Vitals** — check PageSpeed Insights for LCP < 2.5s, INP < 200ms, CLS < 0.1

4. **Mobile-friendliness** — Google Mobile-Friendly Test or responsive design check

5. **HTTPS** — verify no mixed content, valid SSL, HTTP → HTTPS redirects

6. **Hreflang** (if multilingual) — verify self-referencing entries, reciprocal links, valid codes, `x-default` present, all targets return 200 and match canonical

7. **Canonicalization** — verify self-referencing canonicals, no cross-locale canonicals, protocol/domain consistency

8. **Robots.txt** — verify important pages allowed, sitemap referenced

9. **XML Sitemap** — verify accessible, contains only canonical indexable URLs, submitted to Search Console

## Related Skills

- **ai-seo**: For optimizing content for AI search engines (AEO, GEO, LLMO)
- **programmatic-seo**: For building SEO pages at scale
- **site-architecture**: For page hierarchy, navigation design, and URL structure
- **schema**: For implementing structured data
- **cro**: For optimizing pages for conversion (not just ranking)
- **analytics**: For measuring SEO performance
