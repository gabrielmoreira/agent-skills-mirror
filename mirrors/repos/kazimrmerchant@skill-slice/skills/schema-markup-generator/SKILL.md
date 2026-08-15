---
name: schema-markup-generator
description: "Generates JSON-LD Schema.org markup (WebSite, SoftwareApplication, BlogPosting, FAQPage, HowTo, BreadcrumbList, Organization) for Next.js. Use when adding or validating structured data for rich results. Not for Open Graph or Twitter cards alone. Never merge multiple schema types into one JSON-LD object."
category: seo
risk: safe
source: self
source_type: self
date_added: "2026-05-31"
tags: [seo, schema, json-ld, structured-data, rich-results, nextjs, technical-seo]
tools: [claude, cursor, gemini, claude-code]
version: 1.0.1
---

# Schema Markup Generator Skill

Add JSON-LD structured data to pages to unlock rich results, improve CTR, and signal context to Google and AI systems. Supports WebSite, SoftwareApplication, BlogPosting, FAQPage, HowTo, BreadcrumbList, and Organization schemas with Next.js App Router integration.

---

## When to Use

- Use when adding or auditing JSON-LD schema for websites, SaaS apps, tools, articles, FAQs, breadcrumbs, or organization pages.
- Use when schema must be implemented in Next.js App Router or validated against Google Rich Results and Schema.org tooling.
- Use when a page has strong content but lacks structured data for search engines and rich-result eligibility.
- Trigger keywords: `schema markup`, `json-ld`, `structured data`, `rich results`, `rich snippets`, `schema.org`, `breadcrumb schema`, `faq schema`, `howto schema`, `software application schema`.

---

## Prerequisites

- A web project (Next.js App Router recommended, but patterns apply to any React or HTML project).
- Access to the site's real content, legal entity details, pricing, logos, and image URLs — generated examples must be adapted to actual data.
- Browser access to Google Rich Results Test and Schema.org Validator for post-deployment validation.
- Windows host is primary. Use PowerShell for local checks. All path examples assume Windows conventions where relevant.

---

## Procedure

### 1. Create a Reusable `JsonLd` Component

The cleanest approach in Next.js App Router is a reusable component that safely escapes JSON content.

```jsx
// components/JsonLd.jsx
export function JsonLd({ data }) {
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: json }}
    />
  );
}
```

The `replace(/</g, '\\u003c')` call prevents `</script>` injection from breaking the HTML parser.

### 2. Use the Component on Any Page

```jsx
import { JsonLd } from '@/components/JsonLd';

export default function MyPage() {
  return (
    <>
      <JsonLd data={mySchemaObject} />
      {/* rest of page */}
    </>
  );
}
```

### 3. Select the Correct Schema Type by Page Type

Choose the schema that matches the page's primary purpose:

| Page Type | Schema Type |
|---|---|
| Homepage | `WebSite` (+ optional `Organization`) |
| Tool / SaaS app page | `SoftwareApplication` |
| Blog post | `BlogPosting` or `Article` |
| FAQ section / help page | `FAQPage` |
| Step-by-step guide | `HowTo` |
| Any non-homepage page | `BreadcrumbList` (additive) |
| About / contact page | `Organization` |

### 4. Generate the Schema Object

Below are production-ready templates. Replace all URLs, names, dates, and content with the site's real data.

#### WebSite + Sitelinks Searchbox (homepage only)

```js
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "100 SEO Tools",
  "url": "https://www.100seotools.com",
  "description": "Free online SEO tools for keyword research, technical audits, and more.",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://www.100seotools.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

#### SoftwareApplication (tool / SaaS app pages)

```js
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Keyword Density Checker",
  "applicationCategory": "WebApplication",
  "operatingSystem": "Web",
  "url": "https://www.100seotools.com/tools/keyword-density-checker",
  "description": "Free keyword density checker tool. Analyze keyword frequency and optimize your content for SEO.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "featureList": [
    "Analyze keyword frequency",
    "Detect over-optimization",
    "Export results as CSV"
  ],
  "provider": {
    "@type": "Organization",
    "name": "100 SEO Tools",
    "url": "https://www.100seotools.com"
  }
}
```

#### Article / BlogPosting (blog posts)

```js
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How to Improve Your Core Web Vitals in 2025",
  "description": "A practical guide to improving LCP, FID, and CLS scores for better rankings.",
  "url": "https://www.100seotools.com/blog/improve-core-web-vitals",
  "datePublished": "2025-01-15",
  "dateModified": "2025-03-20",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://www.100seotools.com/author/jane-smith"
  },
  "publisher": {
    "@type": "Organization",
    "name": "100 SEO Tools",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.100seotools.com/logo.png"
    }
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://www.100seotools.com/images/blog/core-web-vitals.jpg",
    "width": 1200,
    "height": 630
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://www.100seotools.com/blog/improve-core-web-vitals"
  }
}
```

#### FAQPage (FAQ sections, tool help pages)

```js
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is keyword density?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Keyword density is the percentage of times a keyword appears in a piece of content relative to the total word count. A healthy keyword density is typically 1-3%."
      }
    },
    {
      "@type": "Question",
      "name": "Is this tool free to use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, our keyword density checker is completely free with no registration required."
      }
    }
  ]
}
```

#### HowTo (step-by-step tool guides)

```js
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Check Keyword Density",
  "description": "Step-by-step guide to analyzing keyword density using our free tool.",
  "totalTime": "PT2M",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Paste your content",
      "text": "Copy your article or webpage content and paste it into the text area.",
      "image": "https://www.100seotools.com/images/how-to/step1.jpg"
    },
    {
      "@type": "HowToStep",
      "position": 2,
      "name": "Enter your target keyword",
      "text": "Type the keyword you want to analyze in the keyword field."
    },
    {
      "@type": "HowToStep",
      "position": 3,
      "name": "Click Analyze",
      "text": "Press the Analyze button to get your keyword density report instantly."
    }
  ]
}
```

#### BreadcrumbList (all non-homepage pages)

```js
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://www.100seotools.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "SEO Tools",
      "item": "https://www.100seotools.com/tools"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Keyword Density Checker",
      "item": "https://www.100seotools.com/tools/keyword-density-checker"
    }
  ]
}
```

#### Organization (about, contact pages)

```js
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "100 SEO Tools",
  "url": "https://www.100seotools.com",
  "logo": "https://www.100seotools.com/logo.png",
  "sameAs": [
    "https://twitter.com/100seotools",
    "https://www.linkedin.com/company/100seotools"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "user@example.com"
  }
}
```

### 5. Combine Multiple Schemas on One Page

A tool page can have `BreadcrumbList` + `SoftwareApplication` + `FAQPage`:

```jsx
export default function ToolPage() {
  return (
    <>
      <JsonLd data={breadcrumbSchema} />
      <JsonLd data={softwareApplicationSchema} />
      <JsonLd data={faqSchema} />
      {/* page content */}
    </>
  );
}
```

**HARD RULE:** Each schema lives in its own `<script>` tag — do NOT merge them into one object. Google and other consumers expect separate JSON-LD blocks per type.

### 6. Validate Before Deploying

1. **Google Rich Results Test** — https://search.google.com/test/rich-results
2. **Schema.org Validator** — https://validator.schema.org/
3. **Google Search Console** → Enhancements → check for warnings after deployment

### 7. Quick Local Check (Windows PowerShell)

```powershell
# Check if schema appears in rendered HTML
(Invoke-WebRequest -Uri "https://www.yourdomain.com/tools/keyword-density" -UseBasicParsing).Content | Select-String -Pattern "application/ld\+json" -Context 0,5
```

---

## Pitfalls

- **Do NOT merge multiple schema types into a single JSON-LD object.** Each type gets its own `<script type="application/ld+json">` tag.
- **Do NOT use relative URLs in schema.** All URLs must be absolute HTTPS (e.g., `https://www.example.com/page`, not `/page`).
- **Do NOT deploy without validating the rendered HTML.** Frameworks and rendering modes (SSR, SSG, CSR) can change the final markup. Always validate the deployed page, not only the source code.
- **Do NOT use placeholder content in production.** Generated examples must be adapted to the site's real content, legal entity details, ratings, pricing, and availability.
- **Do NOT assume rich-result display.** Valid schema does not guarantee rich-result eligibility or display; Google and other consumers decide whether to use it.
- **Do NOT forget the `</script>` escape.** The `replace(/</g, '\\u003c')` in the `JsonLd` component prevents content containing `</script>` from breaking the HTML parser.
- **Do NOT put `WebSite` schema on non-homepage pages.** The `WebSite` type with `potentialAction` (SearchAction) is for the homepage only.
- **Do NOT omit `BreadcrumbList` on inner pages.** Every non-homepage page should include breadcrumb schema for navigation context.
- **Do NOT use `datePublished` and `dateModified` interchangeably.** `datePublished` is the original publish date; `dateModified` is the last significant update. Both should use ISO 8601 format (`YYYY-MM-DD`).

---

## Verification

### Checklist

- [ ] Homepage has `WebSite` schema
- [ ] Tool/app pages have `SoftwareApplication` schema
- [ ] Blog posts have `BlogPosting` / `Article` schema
- [ ] FAQ sections have `FAQPage` schema
- [ ] Step-by-step guides have `HowTo` schema
- [ ] All non-homepage pages have `BreadcrumbList`
- [ ] About/contact page has `Organization` schema
- [ ] All URLs in schema are absolute HTTPS
- [ ] Schema validated with Google Rich Results Test
- [ ] No schema errors in Google Search Console

### Commands

```powershell
# Verify schema script tags exist in rendered HTML
(Invoke-WebRequest -Uri "https://www.yourdomain.com/" -UseBasicParsing).Content | Select-String -Pattern "application/ld\+json" -AllMatches

# Count how many JSON-LD blocks are on a page
((Invoke-WebRequest -Uri "https://www.yourdomain.com/tools/example" -UseBasicParsing).Content | Select-String -Pattern "application/ld\+json" -AllMatches).Count
```

### External Validation

1. Open https://search.google.com/test/rich-results — paste the page URL or HTML source.
2. Confirm detected schema types match what was implemented.
3. Open https://validator.schema.org/ — paste the page URL for full Schema.org compliance check.
4. Check Google Search Console → Enhancements section for any warnings or errors after deployment.

---

## Limitations

- Does not guarantee rich-result eligibility or display; Google and other consumers decide whether to use valid schema.
- Generated examples must be adapted to the site's real content, legal entity details, ratings, pricing, and availability.
- Always validate deployed HTML, not only source code, because frameworks and rendering modes can change the final markup.
