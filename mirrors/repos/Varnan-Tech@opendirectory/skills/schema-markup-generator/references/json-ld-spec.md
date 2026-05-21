# JSON-LD Schema Markup Spec

This document defines the required and recommended fields for each schema type this skill generates. The agent reads this before generating any markup.

---

## Section 1: What JSON-LD Is and Why It Matters

JSON-LD (JavaScript Object Notation for Linked Data) is Google's preferred format for structured data. You embed it as a `<script type="application/ld+json">` tag in the page `<head>`.

Why it works better than alternatives (Microdata, RDFa):
- Separate from HTML markup: you change the data without touching the visual layout
- Google parses it reliably, including on JavaScript-rendered pages
- AI crawlers (Google AI Overviews, ChatGPT, Perplexity) read JSON-LD consistently

What it does for your pages:
- Enables rich results in Google search (star ratings, FAQ dropdowns, product prices, how-to steps)
- Helps Google understand what a page is about, not just what it says
- Signals to AI systems that your content is authoritative and structured

---

## Section 2: Core JSON-LD Rules

Every JSON-LD block must follow these rules:

- The script tag: `<script type="application/ld+json">` placed inside `<head>`
- Every block needs `"@context": "https://schema.org"` as the first property
- Every block needs `"@type"` specifying the schema type
- All URLs must be absolute (start with `https://`)
- All dates must use ISO 8601 format: `"2026-04-10"` or `"2026-04-10T09:00:00+00:00"`
- All durations must use ISO 8601: `"PT15M"` (15 minutes), `"PT1H30M"` (1 hour 30 minutes)
- Multiple schema types on one page: one `<script>` block per type, not combined into one

---

## Section 3: Schema Types Reference

### FAQPage

Use when: The page has 2 or more question/answer pairs visible to the user. FAQ sections, support pages, product FAQ tabs.

Google rich result: FAQ dropdowns appear directly under the search result.

Required fields:
- `@type`: "FAQPage"
- `mainEntity`: array of Question objects, each with:
  - `@type`: "Question"
  - `name`: the question text (must match text visible on page)
  - `acceptedAnswer.@type`: "Answer"
  - `acceptedAnswer.text`: the answer text (must match text visible on page)

Rules:
- Questions and answers must be visible on the page — do not include hidden content
- Minimum 2 questions, no maximum
- Answer text can include basic HTML tags: `<p>`, `<ul>`, `<ol>`, `<li>`, `<a>`, `<br>`, `<strong>`, `<em>`
- Do not mark up content that requires clicking "expand" to see unless that content is in the DOM

---

### Article and BlogPosting

Use when: The page is a blog post, news article, opinion piece, or editorial content.

Use `Article` for general editorial content. Use `BlogPosting` specifically for informal blog posts. Use `NewsArticle` for news publications.

Google rich result: Article can appear in Google Discover and News with image, title, and date.

Required fields:
- `@type`: "Article", "BlogPosting", or "NewsArticle"
- `headline`: the article title (max 110 characters for Google News)
- `image`: array of image URLs. At least one image. Recommended: provide three aspect ratios (16x9, 4x3, 1x1). Minimum 50,000 pixels total (e.g. 696x392px).
- `datePublished`: ISO 8601 publish date
- `author`: object or array with `@type` ("Person" or "Organization") and `name`

Recommended fields:
- `dateModified`: ISO 8601 last-updated date
- `publisher`: Organization object with `name`, `url`, `logo`
- `description`: article summary (from meta description or first paragraph)
- `url`: canonical URL of the article

---

### Organization

Use when: The page represents a company, nonprofit, or institution. Common on About, Company, or homepage pages.

Google use: Establishes entity understanding for Knowledge Panel. Helps Google connect your site to your brand.

Required fields:
- `@type`: "Organization"
- `name`: company name
- `url`: company website

Recommended fields:
- `logo`: ImageObject with `url`, `width`, `height`
- `sameAs`: array of social profile URLs (LinkedIn, Twitter/X, YouTube, GitHub, etc.)
- `description`: company description
- `contactPoint`: ContactPoint object with `contactType` and `email` or `telephone`
- `@id`: use `"https://yourdomain.com/#organization"` as a stable identifier

---

### Product

Use when: The page sells or describes a specific product with a price.

Google rich result: Product price, availability, and ratings appear in search results.

Required fields (at least one of these must be present to qualify for rich results):
- `review` (Review object)
- `aggregateRating` (AggregateRating object)
- `offers` (Offer object)

Core fields:
- `@type`: "Product"
- `name`: product name
- `image`: array of product image URLs
- `description`: product description

Offer fields (when pricing is on the page):
- `offers.@type`: "Offer"
- `offers.priceCurrency`: ISO 4217 code ("USD", "GBP", "EUR")
- `offers.price`: numeric price as string ("29.99")
- `offers.availability`: one of `https://schema.org/InStock`, `https://schema.org/OutOfStock`, `https://schema.org/PreOrder`
- `offers.url`: product page URL

AggregateRating fields (when ratings are on the page):
- `aggregateRating.ratingValue`: average rating (e.g. 4.5)
- `aggregateRating.reviewCount`: number of reviews
- `aggregateRating.bestRating`: maximum rating (usually 5)

---

### WebSite

Use when: Generating markup for the homepage or site-level schema.

Google use: Enables the Sitelinks Searchbox in search results when users search your brand name.

Required fields:
- `@type`: "WebSite"
- `name`: site name
- `url`: homepage URL

Recommended fields (for Sitelinks Searchbox):
- `potentialAction.@type`: "SearchAction"
- `potentialAction.target.urlTemplate`: search URL pattern (e.g. `"https://example.com/search?q={search_term_string}"`)
- `potentialAction.query-input`: `"required name=search_term_string"`

Only add `potentialAction` if the site has a working search feature. Do not add it for sites without search.

---

### HowTo

Use when: The page is a step-by-step guide or tutorial with numbered steps.

Google rich result: Steps appear directly in search results as an expandable list.

Required fields:
- `@type`: "HowTo"
- `name`: guide title
- `step`: array of HowToStep objects, each with:
  - `@type`: "HowToStep"
  - `name`: step title
  - `text`: step description

Recommended fields:
- `image`: feature image for the guide
- `estimatedDuration`: total time as ISO 8601 duration (e.g. `"PT30M"`)
- `supply`: array of HowToSupply objects if materials are needed
- `tool`: array of HowToTool objects if tools are needed

---

### BreadcrumbList

Use when: The page has a visible breadcrumb navigation trail.

Google use: Displays breadcrumb path in search results instead of the full URL.

Required fields:
- `@type`: "BreadcrumbList"
- `itemListElement`: array of ListItem objects, each with:
  - `@type`: "ListItem"
  - `position`: integer position starting at 1
  - `name`: display text for this breadcrumb
  - `item`: absolute URL (required for all items except the last)

Rules:
- Positions must be sequential integers starting at 1
- The last item does not need an `item` URL (it is the current page)

---

### SoftwareApplication

Use when: The page describes a software tool, app, or developer product.

Google rich result: Star ratings and price can appear in search results.

Required fields:
- `@type`: "SoftwareApplication"
- `name`: app name
- `operatingSystem`: one or more of "Windows", "macOS", "Linux", "Android", "iOS", "Web"
- `applicationCategory`: one of "GameApplication", "BusinessApplication", "EducationalApplication", "DeveloperApplication", "DesignApplication", "UtilitiesApplication", "SecurityApplication", "SocialNetworkingApplication"

Recommended fields:
- `offers`: pricing (use `"price": "0"` for free apps, or actual price)
- `aggregateRating`: if ratings are on the page
- `description`: app description
- `url`: app or product page URL
- `downloadUrl`: direct download link if available

---

### LocalBusiness

Use when: The page represents a physical business location with an address.

Google rich result: Business details, hours, and ratings appear in local search results and maps.

Required fields:
- `@type`: "LocalBusiness" (or a more specific subtype: "Restaurant", "Store", "MedicalBusiness", etc.)
- `name`: business name
- `address`: PostalAddress object with `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, `addressCountry`

Recommended fields:
- `telephone`: phone number in international format
- `url`: website URL
- `openingHoursSpecification`: array of OpeningHoursSpecification objects with `dayOfWeek`, `opens`, `closes`
- `aggregateRating`: if reviews are on the page
- `image`: business photos
- `priceRange`: "$", "$$", "$$$", or "$$$$"

---

## Section 4: Common Validation Errors

These errors cause Google to reject or ignore schema markup:

| Error | What causes it | How to fix |
|-------|----------------|------------|
| Missing @context | Forgot the first line | Add `"@context": "https://schema.org"` |
| Relative URLs | Using `/path` instead of `https://domain.com/path` | Use absolute URLs everywhere |
| Wrong date format | Using "April 10, 2026" instead of ISO 8601 | Use `"2026-04-10"` format |
| Content mismatch | Schema says X, visible page says Y | Schema must reflect page content |
| Hidden content | Marking up content not visible to users | Only markup visible, on-page content |
| Invented data | Filling fields with guessed or generic values | Every value must come from the page |
| Invalid JSON | Trailing comma, unmatched bracket | Validate JSON syntax before outputting |
| Wrong @type for content | Using "Article" for a product page | Match @type to actual page purpose |

---

## Section 5: Validation Tools

After generating markup, the user should validate it at:

- Google Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org

These tools show which rich result types the markup qualifies for and flag any errors.
