---
name: seo-geo-optimize
description: Audits and automatically implements SEO, local SEO (Geo/Schema.org), and Social Graph structured data across web projects according to modern best practices.
license: MIT
compatibility: opencode
metadata:
  category: enhancement
  phase: execution
---

# Skill: SEO & Geo Optimize

## What This Skill Does

Analyzes the project (especially frontend like SvelteKit, Next.js, or static static web apps) and ensures complete compliance with modern Search Engine Optimization (SEO) and Geotargeting (Local SEO) standards. Instead of just producing an audit report, this skill proactively implements missing meta tags, schema.org structured data, open graph entries, and semantic structures directly into the project's source code.

## When to Use

- When launching a new frontend project (after the MVP is generally complete).
- Before shipping a website to production.
- When the user asks to "optimize for search engines", "add meta tags", or "implement local SEO".
- For localized apps and landing pages that need schema.org injection.

## Execution Model

- **Always**: the primary agent or an `engineer` subagent runs this skill directly.
- **Rationale**: Implementing SEO often requires altering global layouts (e.g. `+layout.svelte`, `_app.tsx`), manipulating metadata routing handlers, and injecting JSON-LD scripts—all core engineering tasks.

## Workflow

### Step 1: Analyze Current State & Routing
Use `find` and `grep` to analyze the project's routing structure and identify existing SEO components:
- Does the project have a global `<Head>`, `<svelte:head>`, or a `<Seo>` component?
- Are there `robots.txt` and `sitemap.xml` (or generator endpoints) present?
- Is there an existing configuration for `hreflang` (for multi-language apps)?

### Step 2: On-Page SEO Implementation
For each major route or the global layout, ensure the following are implemented:
1. **Dynamic Meta Tags:** `title`, `description`, `canonical` URLs.
2. **Semantic HTML Elements:** Ensure proper `<h1>` wrapping for main content and absence of multiple `<h1>` tags on a single page.
3. If no centralized SEO component exists, **scaffold one** (e.g., `src/components/Seo.svelte` or `src/components/Seo.tsx`) and integrate it into the layouts.

### Step 3: Social & Open Graph Metadata
Inject essential social sharing tags into the centralized SEO component or layout:
- `og:title`, `og:description`, `og:type`, `og:url`, `og:image`
- `twitter:card` (typically `summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`

### Step 4: Local & Geo SEO (Structured Data via JSON-LD)
Audit for local business context and create JSON-LD schema objects (`<script type="application/ld+json">`). Ask the user for specific business data if not evident.
1. Implement `LocalBusiness` / `Organization` schemas globally or on contact pages.
2. Implement `BreadcrumbList` on subpages.
3. Ensure `hreflang` header mapping in multi-lingual apps so geo-targeting works correctly for different regions.

### Step 5: Web Crawlability Hooks
1. Create or verify `robots.txt`.
2. Ensure there's a dynamic or static `sitemap.xml` available (e.g. `src/routes/sitemap.xml/+server.ts` in SvelteKit).

### Step 6: Verify and Run Tests
- Use `npm run build` or the project's equivalent type checker/linter to ensure injecting metadata hasn't broken page compilation.
- Ensure all injected JSON-LD strings are properly escaped to prevent XSS issues in the template.

## Rules

1. **Be constructive:** Do not just output an audit report; actively add the `robots.txt`, SEO components, and tags to the code.
2. **Use centralized components:** Always prefer creating a single reusable `<Seo>` component over hardcoding tags into 20 different routes.
3. **Escaping JSON:** When injecting JSON-LD, ensure variables and content are cleanly stringified to avoid breaking HTML.
4. **No built-in explore agent:** do NOT use the built-in `explore` subagent type. Wait for user input if business details (address, social links) are needed for the JSON-LD schema.
