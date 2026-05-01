# SEO Content Audit

## Skill Purpose
Perform a comprehensive SEO audit of a webpage or website, covering on-page SEO, content quality (E-E-A-T), keyword analysis, technical SEO, and content strategy. This skill combines automated analysis via `scripts/analyze_page.py` with expert-level manual review to produce an actionable SEO audit document.

## When to Use
- User provides a URL and asks for SEO analysis, audit, or recommendations
- User wants to improve organic search rankings and traffic
- User asks about on-page SEO, meta tags, content quality, or technical SEO
- User wants a content gap analysis or content strategy recommendations
- Triggered by `/market seo <url>` or `/market seo`

## How to Execute

### Step 1: Run Automated Analysis
Use the Python analysis script to gather baseline data:

```bash
python3 scripts/analyze_page.py <url>
```

This script extracts:
- Title tag and meta description
- Open Graph tags
- Heading hierarchy (H1-H6)
- Links (internal and external)
- Images and alt text status
- Forms and CTAs
- Schema/structured data
- Social links
- Tracking scripts
- Viewport meta tag (mobile-friendliness indicator)
- Canonical tag
- Robots meta directives

Capture the JSON output and use it as the foundation for the manual analysis.

### Step 2: On-Page SEO Checklist
Evaluate each element and score it as Pass, Needs Work, or Fail.

#### Title Tag
| Criteria | Best Practice | Check |
|---|---|---|
| Exists | Every page must have a unique title tag | Pass/Fail |
| Length | 50-60 characters (displays fully in SERPs) | Pass/Needs Work/Fail |
| Primary keyword | Contains the primary target keyword | Pass/Needs Work/Fail |
| Keyword position | Primary keyword appears near the beginning | Pass/Needs Work/Fail |
| Brand name | Includes brand name (typically at the end, separated by pipe or dash) | Pass/Needs Work/Fail |
| Uniqueness | Different from other pages on the site | Pass/Fail |
| Compelling | Would a searcher want to click this? | Pass/Needs Work/Fail |

**Common title tag mistakes:**
- Too long (truncated in search results)
- Missing primary keyword
- Keyword stuffing ("Best SEO Tool | Top SEO Tool | SEO Software | SEO Platform")
- Using the same title across multiple pages
- Generic titles ("Home", "Welcome", "Page 1")
- Missing brand name

#### Meta Description
| Criteria | Best Practice | Check |
|---|---|---|
| Exists | Every page should have a meta description | Pass/Fail |
| Length | 150-160 characters | Pass/Needs Work/Fail |
| Primary keyword | Naturally includes the target keyword | Pass/Needs Work/Fail |
| Call to action | Includes a reason to click | Pass/Needs Work/Fail |
| Unique | Different from other pages | Pass/Fail |
| Compelling | Acts as ad copy for the search result | Pass/Needs Work/Fail |

#### Heading Hierarchy (H1-H6)
| Criteria | Best Practice | Check |
|---|---|---|
| H1 exists | Exactly one H1 per page | Pass/Fail |
| H1 contains keyword | Primary keyword in the H1 | Pass/Needs Work/Fail |
| H1 differs from title | H1 and title tag are different (but related) | Pass/Needs Work/Fail |
| Logical hierarchy | H2 under H1, H3 under H2 (no skipping levels) | Pass/Needs Work/Fail |
| Descriptive subheadings | H2s and H3s describe content sections clearly | Pass/Needs Work/Fail |
| Keywords in subheadings | Secondary keywords appear naturally in H2s/H3s | Pass/Needs Work/Fail |
| Not overused | Headers used for structure, not styling | Pass/Needs Work/Fail |

#### Image Optimization
| Criteria | Best Practice | Check |
|---|---|---|
| Alt text | Every image has descriptive alt text | Pass/Needs Work/Fail |
| Alt text quality | Alt text describes the image and includes keywords naturally | Pass/Needs Work/Fail |
| File names | Descriptive filenames (not IMG_001.jpg) | Pass/Needs Work/Fail |
| File size | Images optimized for web (WebP preferred, compressed) | Pass/Needs Work/Fail |
| Lazy loading | Below-fold images use lazy loading | Pass/Needs Work/Fail |
| Responsive images | Uses srcset or picture element for different sizes | Pass/Needs Work/Fail |
| Decorative images | Decorative images have empty alt="" (not missing alt) | Pass/Needs Work/Fail |

#### Internal Linking
| Criteria | Best Practice | Check |
|---|---|---|
| Internal links present | Page links to other relevant pages on the site | Pass/Needs Work/Fail |
| Anchor text | Internal link anchor text is descriptive (not "click here") | Pass/Needs Work/Fail |
| Deep linking | Links go to specific pages, not just homepage | Pass/Needs Work/Fail |
| Relevant context | Links are contextually relevant to surrounding content | Pass/Needs Work/Fail |
| Reasonable count | 3-10 internal links per 1,000 words of content | Pass/Needs Work/Fail |
| Broken links | No broken internal links (404s) | Pass/Fail |

#### URL Structure
| Criteria | Best Practice | Check |
|---|---|---|
| Readable | URL is human-readable and descriptive | Pass/Needs Work/Fail |
| Keywords | URL contains relevant keywords | Pass/Needs Work/Fail |
| Length | Under 75 characters (ideally under 60) | Pass/Needs Work/Fail |
| Hyphens | Words separated by hyphens (not underscores) | Pass/Fail |
| Lowercase | All lowercase characters | Pass/Fail |
| No parameters | Clean URLs without unnecessary query parameters | Pass/Needs Work/Fail |
| Trailing slashes | Consistent use (either always or never) | Pass/Needs Work/Fail |

### Step 3: Content Quality Assessment (E-E-A-T)

Evaluate the content against Google's E-E-A-T framework:

#### Experience
Does the content demonstrate first-hand experience with the topic?

**Check for:**
- Personal anecdotes, case studies, or real-world examples
- Screenshots, photos, or evidence of hands-on experience
- Specific details that only someone with experience would know
- "I did X and here's what happened" type content

**Score:** Strong / Present / Weak / Missing

#### Expertise
Does the author have demonstrated knowledge in this subject?

**Check for:**
- Author bio with relevant credentials
- Depth of content (not superficial)
- Accurate information and data
- Proper use of industry terminology
- Links to authoritative sources

**Score:** Strong / Present / Weak / Missing

#### Authoritativeness
Is the website and author recognized as an authority on this topic?

**Check for:**
- Author bylines with real names and bios
- About page with company background
- Industry awards or certifications
- Backlinks from authoritative sites
- Media mentions or press coverage
- Guest posts on industry publications

**Score:** Strong / Present / Weak / Missing

#### Trustworthiness
Can users trust this content and this website?

**Check for:**
- HTTPS (SSL certificate)
- Privacy policy and terms of service
- Physical address and contact information
- Customer reviews and testimonials
- Security badges and certifications
- Transparent business practices
- Accurate, up-to-date information
- Properly sourced claims and statistics

**Score:** Strong / Present / Weak / Missing

### Step 4: Keyword Analysis

#### Primary Keyword Assessment
| Element | Evaluation |
|---|---|
| Primary keyword identified | What keyword is this page targeting? |
| Search intent alignment | Does the content match what searchers expect? (informational, commercial, transactional, navigational) |
| Keyword in title | Present, position, natural usage |
| Keyword in H1 | Present, natural usage |
| Keyword in first 100 words | Appears early in the content |
| Keyword in subheadings | Appears in at least one H2 or H3 |
| Keyword in meta description | Present and natural |
| Keyword in URL | Present |
| Keyword density | 1-2% is ideal. Over 3% is keyword stuffing. |

#### Secondary Keywords
Identify 5-10 related keywords that should be naturally included in the content:
- Synonyms and variations of the primary keyword
- Long-tail variations
- Related questions (People Also Ask)
- LSI (Latent Semantic Indexing) keywords

#### Search Intent Analysis
Determine the search intent behind the target keyword and evaluate if the content matches:

| Intent Type | User Goal | Content Should Be |
|---|---|---|
| Informational | Learn something | Blog post, guide, tutorial, FAQ |
| Commercial | Compare options | Comparison page, review, list |
| Transactional | Buy something | Product page, pricing page, checkout |
| Navigational | Find a specific page | Homepage, login page, specific tool |

**Misalignment is a ranking killer.** If the user searches "how to do X" (informational) and lands on a sales page (transactional), they bounce -- and Google notices.

### Step 5: Technical SEO Quick Check

#### Robots.txt
```
Check: Does /robots.txt exist and is it properly configured?
```
- [ ] robots.txt is accessible
- [ ] Not blocking important pages or resources
- [ ] Points to sitemap.xml
- [ ] Not blocking CSS/JS (needed for rendering)

#### XML Sitemap
```
Check: Does /sitemap.xml exist?
```
- [ ] Sitemap exists and is accessible
- [ ] Contains all important pages
- [ ] No broken URLs in sitemap
- [ ] Submitted to Google Search Console
- [ ] Last modified dates are accurate

#### Canonical Tags
- [ ] Canonical tag present on the page
- [ ] Points to the correct URL (self-referencing or to the canonical version)
- [ ] Consistent with robots.txt and sitemap

#### Page Speed
Reference benchmarks:

| Metric | Good | Needs Work | Poor |
|---|---|---|---|
| Largest Contentful Paint (LCP) | Under 2.5s | 2.5-4.0s | Over 4.0s |
| First Input Delay (FID) | Under 100ms | 100-300ms | Over 300ms |
| Cumulative Layout Shift (CLS) | Under 0.1 | 0.1-0.25 | Over 0.25 |
| Time to First Byte (TTFB) | Under 200ms | 200-500ms | Over 500ms |
| First Contentful Paint (FCP) | Under 1.8s | 1.8-3.0s | Over 3.0s |

**Common speed issues to flag:**
- Unoptimized images (recommend WebP format, compression)
- Render-blocking JavaScript or CSS
- No browser caching headers
- No CDN detected
- Excessive third-party scripts (tracking, widgets, fonts)
- Unminified CSS and JavaScript
- Missing compression (gzip or brotli)

#### Mobile-Friendliness
- [ ] Viewport meta tag present (`<meta name="viewport" content="width=device-width, initial-scale=1">`)
- [ ] Text readable without zooming (minimum 16px body text)
- [ ] Tap targets adequately sized and spaced (minimum 48x48px)
- [ ] No horizontal scrolling required
- [ ] Responsive images
- [ ] Forms usable on mobile

### Step 6: Content Gap Analysis

Methodology for identifying content gaps:

1. **Identify the topic cluster:** What is the main topic this page/site covers?
2. **Map existing content:** What subtopics are already covered?
3. **Identify missing subtopics:** What related topics are competitors covering that this site is not?
4. **Analyze People Also Ask:** What questions do searchers have about this topic?
5. **Check related searches:** What does Google suggest at the bottom of the SERP?

**Content Gap Template:**
| Missing Topic | Search Volume Potential | Competition | Content Type Needed | Priority |
|---|---|---|---|---|
| [Topic] | High/Med/Low | High/Med/Low | Blog/Guide/Tool/Page | 1-5 |

### Step 7: Featured Snippet Optimization

Identify opportunities to capture featured snippets:

**Types of featured snippets:**
1. **Paragraph snippet** -- Answer in 40-60 words. Use a clear question as H2/H3 followed by a concise answer.
2. **List snippet** -- Use ordered or unordered lists with H2 containing the target query.
3. **Table snippet** -- Use HTML tables with clear headers.
4. **Video snippet** -- Include video with descriptive title and timestamps.

**Optimization checklist:**
- [ ] Target question-based queries ("how to", "what is", "why does")
- [ ] Place answer immediately after the question heading
- [ ] Keep paragraph answers between 40-60 words
- [ ] Use structured lists and tables where appropriate
- [ ] Include the target query in an H2 or H3

### Step 8: Schema Markup Audit

Check for structured data implementation:

| Schema Type | Applicable To | Status |
|---|---|---|
| Organization | Homepage, About page | Present/Missing |
| LocalBusiness | Local businesses | Present/Missing/N/A |
| Product | Product pages | Present/Missing/N/A |
| Article | Blog posts, news | Present/Missing/N/A |
| FAQ | FAQ sections | Present/Missing |
| HowTo | Tutorial content | Present/Missing/N/A |
| Review/AggregateRating | Reviews, testimonials | Present/Missing/N/A |
| BreadcrumbList | All pages with breadcrumbs | Present/Missing |
| WebSite/SearchAction | Homepage (sitelinks search box) | Present/Missing |
| Event | Event pages | Present/Missing/N/A |

**Implementation guidance:**
- Use JSON-LD format (Google's preferred format)
- Validate with Google's Rich Results Test
- Don't mark up content that isn't visible on the page
- Keep schema data consistent with on-page content

### Step 9: Internal Linking Opportunities

Identify specific internal linking improvements:

1. **Orphan pages** -- Pages with no internal links pointing to them
2. **Hub pages** -- High-authority pages that should link to related content
3. **Topical clusters** -- Group related content and create linking structures
4. **CTA links** -- Blog content should link to relevant product/service pages
5. **Footer/sidebar links** -- Sitewide links to important pages

**Linking Architecture Assessment:**
```
Homepage
  |-- Category/Service Pages (Pillar Content)
       |-- Individual Blog Posts/Articles (Cluster Content)
            |-- Back-links to Pillar Content
  |-- Key Conversion Pages (Pricing, Signup, Contact)
       |-- Linked from relevant content
```

### Step 10: Core Web Vitals Impact Assessment

Evaluate the revenue impact of Core Web Vitals performance:

**Research-backed impacts:**
- Sites passing all Core Web Vitals see 24% fewer page abandonments
- A 100ms decrease in LCP correlates with a 1.1% increase in conversion rates
- Reducing CLS by 0.1 corresponds to a 15% decrease in bounce rate
- Pages loading within 2 seconds have an average bounce rate of 9%, while pages loading in 5 seconds have a 38% bounce rate

**Recommendations by metric:**
| Metric | If Failing | Typical Fixes |
|---|---|---|
| LCP | Over 2.5s | Optimize hero image, preload critical resources, use CDN, reduce server response time |
| FID/INP | Over 100ms | Reduce JavaScript execution, defer non-critical scripts, use web workers |
| CLS | Over 0.1 | Set image dimensions, reserve space for ads/embeds, avoid inserting content above existing content |

### Step 11: Blog and Content Strategy Recommendations

Based on the audit findings, recommend:

1. **Publishing cadence** -- How often to publish based on competition and resources
2. **Content types** -- Blog posts, guides, tools, videos, infographics
3. **Keyword targeting strategy** -- Balance between high-volume and long-tail
4. **Content length** -- Benchmark against top-ranking content for target keywords
5. **Content update strategy** -- How often to refresh existing content
6. **Distribution plan** -- How to promote content beyond organic search

**Content Prioritization Matrix:**
| Content Idea | Search Volume | Competition | Business Value | Priority Score |
|---|---|---|---|---|
| [Topic] | High/Med/Low | High/Med/Low | High/Med/Low | 1-10 |

Scoring: High volume + Low competition + High business value = Highest priority

## Output Format

Generate a file called `SEO-AUDIT.md` with:

```markdown
# SEO Content Audit
## [URL]
### Date: [Date]

---

## SEO Health Score: [X/100]

---

## On-Page SEO Checklist

### Title Tag
- Status: [Pass/Needs Work/Fail]
- Current: "[current title]"
- Recommended: "[improved title]"
- Issues: [list issues]

### Meta Description
- Status: [Pass/Needs Work/Fail]
- Current: "[current meta]"
- Recommended: "[improved meta]"

### Heading Hierarchy
[H1-H6 structure analysis]

### Image Optimization
[Alt text audit results]

### Internal Linking
[Link analysis]

### URL Structure
[URL assessment]

---

## Content Quality (E-E-A-T)
| Dimension | Score | Evidence |
|---|---|---|
| Experience | [Strong/Present/Weak/Missing] | [details] |
| Expertise | [Strong/Present/Weak/Missing] | [details] |
| Authoritativeness | [Strong/Present/Weak/Missing] | [details] |
| Trustworthiness | [Strong/Present/Weak/Missing] | [details] |

---

## Keyword Analysis
- Primary Keyword: [keyword]
- Search Intent: [type]
- Keyword Placement: [checklist results]
- Secondary Keywords: [list]

---

## Technical SEO
[Quick check results]

---

## Content Gap Analysis
[Missing topics table]

---

## Featured Snippet Opportunities
[Specific opportunities]

---

## Schema Markup
[Current vs recommended]

---

## Internal Linking Opportunities
[Specific recommendations]

---

## Core Web Vitals
[Performance assessment with revenue impact]

---

## Content Strategy Recommendations
[Publishing plan, content priorities]

---

## Prioritized Recommendations

### Critical (Fix Immediately)
1. [recommendation with expected impact]

### High Priority (This Month)
1. [recommendation]

### Medium Priority (This Quarter)
1. [recommendation]

### Low Priority (When Resources Allow)
1. [recommendation]
```

## Key Principles
- SEO audits should be educational, not just diagnostic. Explain WHY each element matters so the client understands the value.
- Always provide the "before" (current state) and "after" (recommended change) so the client can see exactly what needs to change.
- Tie SEO improvements to business outcomes. "Optimizing your title tag" means nothing to a business owner. "Optimizing your title tag could increase your click-through rate by 20-35%, bringing an estimated 500 more visitors per month to this page" is actionable.
- Use the automated script data as a starting point, but add expert analysis on top. The script finds the data; the skill interprets what it means.
- Prioritize recommendations by effort-to-impact ratio. A title tag change takes 5 minutes but can impact every search impression. A full content rewrite takes weeks.
- If the user has run `/market audit` or `/market landing` previously, cross-reference those findings with the SEO audit for a more complete picture.
