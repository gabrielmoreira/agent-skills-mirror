---
name: nextjs-seo-indexing
description: "Fixes Next.js App Router indexing issues: canonical and generateMetadata, noindex leaks, sitemap/robots routes, static rendering, internal linking, and Search Console coverage. Use when a Next.js site wastes crawl budget or shows discovered-not-indexed URLs. Not for site-wide SEO audits of non-Next stacks (seo-audit), schema-markup chairs, or programmatic keyword-page factories."
version: 1.0.1
category: seo
risk: safe
source: self
source_type: self
date_added: "2026-05-31"
tags: [seo, indexing, nextjs, search-console, crawl-budget, canonical, sitemap, robots, noindex, redirects]
tools: [claude, cursor, gemini, claude-code]
---

# Next.js SEO Indexing & Crawl Budget Skill

Fix Google Search Console coverage issues, canonical problems, sitemap errors, and crawl budget waste in Next.js apps. This skill walks through a full seven-step audit covering canonical tags, noindex leaks, sitemap health, static rendering, internal linking, redirects, and robots.txt.

---

## When to Use

- A Next.js site shows Google Search Console coverage issues: duplicate canonicals, accidental `noindex`, crawl waste, or "discovered – not indexed" URLs.
- You are auditing sitemap, robots.txt, redirect chains, internal-linking, or static-rendering problems before an SEO release.
- You need framework-specific examples for Next.js App Router `metadata`, `generateMetadata`, `robots.js`, and `sitemap` routes.
- A client or stakeholder reports dropped indexed page counts or coverage report regressions.

---

## Prerequisites

- **Runtime:** Node.js 18+ and Next.js 13+ (App Router) project locally.
- **Access:** Codebase read/write access, deployed URL, and ideally Google Search Console property access.
- **Windows host (primary):** Commands below are PowerShell-first. Where a Unix equivalent is useful (e.g., `curl` on WSL), it is noted. PowerShell aliases: `curl` maps to `Invoke-WebRequest` unless `curl.exe` is explicitly called.
- **Tools:** `ripgrep` (`rg`) recommended for fast code search. Install via `winget install BurntSushi.ripgrep.MSVC` or use `Select-String` as fallback.
- **No live secrets:** All URLs and keys in examples use `yourdomain.com` / `YOUR_KEY` placeholders.

---

## Procedure

### Understanding Search Console Coverage States

Before fixing anything, map the Search Console report to the correct state:

| Status | Meaning | Fix |
|--------|---------|-----|
| Crawled – not indexed | Google crawled but chose not to index | Improve content quality + canonical + internal links |
| Duplicate without canonical | Multiple URLs serve same content, no canonical | Add explicit canonical to the preferred URL |
| Excluded by noindex | `noindex` tag present | Remove `noindex` if page should be indexed |
| Duplicate, Google chose different canonical | Google prefers a different URL than you specified | Align canonical with the URL Google naturally picks |
| Alternative page with proper canonical | Correct — non-preferred duplicate pointing to canonical | Expected behavior, not a problem |
| Not found 404 | Page deleted or URL changed | Add redirect or restore page |
| Discovered – not indexed | Google knows it exists but hasn't crawled it | Improve internal linking + crawl budget |
| Page with redirect | Redirect chain or redirect to wrong target | Shorten redirect chain, verify destination |

---

### Step 1 — Canonical Audit

Every indexable page must have an absolute canonical URL with a consistent scheme, subdomain, and trailing-slash policy.

**1.1 — Search for canonical definitions in the codebase:**

```powershell
# PowerShell — find all canonical references
rg -n --glob '*.{js,ts,jsx,tsx}' 'canonical|alternates' app pages

# Fallback without ripgrep
Get-ChildItem -Recurse -Include *.js,*.ts,*.jsx,*.tsx app pages | Select-String -Pattern 'canonical|alternates'
```

**1.2 — App Router static metadata export:**

```js
// app/blog/my-post/page.js
export const metadata = {
  title: 'My Post Title',
  alternates: {
    canonical: 'https://www.yourdomain.com/blog/my-post',
  },
};
```

**1.3 — App Router dynamic metadata (generateMetadata):**

```js
export async function generateMetadata({ params }) {
  return {
    alternates: {
      canonical: `https://www.yourdomain.com/blog/${params.slug}`,
    },
  };
}
```

**1.4 — Fix common canonical mistakes:**

```js
// ❌ WRONG — relative URL
canonical: '/blog/my-post'

// ❌ WRONG — missing trailing slash inconsistency
// (pick one and stick with it sitewide)

// ✓ CORRECT — absolute URL, consistent scheme + subdomain
canonical: 'https://www.yourdomain.com/blog/my-post'
```

**1.5 — Verify deployed canonical tags render in HTML:**

```powershell
# PowerShell — fetch the page and extract canonical link
curl.exe -s https://www.yourdomain.com/blog/my-post | Select-String 'rel="canonical"'

# WSL / Unix
curl -s https://www.yourdomain.com/blog/my-post | grep -i 'rel="canonical"'
```

---

### Step 2 — Noindex Audit

A single `noindex` in the root layout will deindex the entire site. Audit systematically.

**2.1 — Search for noindex in metadata:**

```powershell
# PowerShell with ripgrep
rg -n --glob '*.{js,ts,jsx,tsx}' 'noindex|robots.*noindex' app pages

# Fallback
Get-ChildItem -Recurse -Include *.js,*.ts,*.jsx,*.tsx app pages |
  Select-String -Pattern 'noindex|robots'
```

**2.2 — Check root layout for sitewide robots directives:**

```powershell
Select-String -Path app\layout.js -Pattern 'robots'
```

In Next.js App Router, `robots` in the root layout applies globally. Only set it there if you want the whole site affected.

```js
// app/layout.js — only set robots if you need sitewide control
export const metadata = {
  // ✓ Allow indexing
  robots: { index: true, follow: true },
  // ❌ This would noindex the entire site:
  // robots: { index: false }
};
```

**2.3 — Check deployed pages for noindex headers and meta tags:**

```powershell
# Check HTTP headers
curl.exe -sI https://www.yourdomain.com/blog/my-post | Select-String 'x-robots|noindex'

# Check meta tags in HTML
curl.exe -s https://www.yourdomain.com/blog/my-post | Select-String 'noindex'
```

---

### Step 3 — Sitemap Health

**3.1 — Verify sitemap routes return 200 + valid XML:**

```powershell
# PowerShell — check headers
curl.exe -sI https://www.yourdomain.com/sitemap.xml

# Check first 20 lines of XML
curl.exe -s https://www.yourdomain.com/sitemap.xml | Select-Object -First 20

# WSL / Unix
curl -sI https://www.yourdomain.com/sitemap.xml | grep -i "content-type\|status"
curl -s https://www.yourdomain.com/sitemap.xml | head -20
```

**3.2 — Next.js App Router sitemap (recommended pattern):**

```js
// app/sitemap.js
export default async function sitemap() {
  const baseUrl = 'https://www.yourdomain.com';

  // Static pages
  const staticPages = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'daily', priority: 1.0 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
  ];

  // Dynamic pages (fetch from DB or CMS)
  const posts = await getPosts(); // your data fetch
  const dynamicPages = posts.map(post => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly',
    priority: 0.7,
  }));

  return [...staticPages, ...dynamicPages];
}
```

**3.3 — Multiple sitemaps (sitemap index):**

```js
// app/sitemap-tools/sitemap.js
// app/sitemap-blog/sitemap.js
// Each returns an array of URL entries
```

**3.4 — Submit sitemap to Google Search Console:**

1. Open Google Search Console → your property.
2. Go to **Sitemaps**.
3. Enter `sitemap.xml` (or the full path for sub-sitemaps).
4. Click **Submit**.
5. Return after 24–48h to check status is "Success".

---

### Step 4 — Static Rendering Verification

Pages must be statically generated (or SSR with metadata in HTML) for Google to see SEO tags at crawl time.

**4.1 — Check build output:**

```powershell
npm run build 2>&1 | Select-String '○|●|λ|/blog|/tools'
```

```text
○  /about             (static)
●  /blog/[slug]       (SSG)  ← good
λ  /api/data          (serverless) ← expected for APIs
```

**4.2 — If important pages are `λ` (fully dynamic), add generateStaticParams:**

```js
// app/blog/[slug]/page.js
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map(post => ({ slug: post.slug }));
}
```

**4.3 — Rebuild and confirm the route is now `●` or `○`:**

```powershell
npm run build 2>&1 | Select-String '/blog'
```

---

### Step 5 — Internal Linking Audit

Pages with zero internal links are rarely indexed. Every important page should be reachable from:

1. Homepage or navigation
2. A sitemap
3. At least one other content page

**5.1 — Find orphaned pages (manual grep approach):**

```powershell
# PowerShell — search for references to a slug across all files
Get-ChildItem -Recurse -Include *.js,*.ts,*.jsx,*.tsx,*.md |
  Select-String -Pattern '/blog/my-orphan-post' |
  Where-Object { $_.Path -notmatch 'sitemap|my-orphan-post' }

# WSL / Unix
grep -r "/blog/my-orphan-post" --include="*.{js,ts,jsx,tsx,md}" . | grep -v "sitemap\|the-page-itself"
```

**5.2 — Fix orphans by adding contextual links:**

- Add the page to a category listing page.
- Link to it from a related blog post.
- Add it to the main navigation or footer if it is a key page.

---

### Step 6 — Redirect Audit

**6.1 — Find all redirects in Next.js config:**

```powershell
Select-String -Path next.config.js -Pattern 'redirects' -Context 0,10
```

**6.2 — Test for redirect chains (A → B → C should be A → C):**

```powershell
# PowerShell — follow redirects and show each hop
curl.exe -sIL https://www.yourdomain.com/old-url

# WSL / Unix
curl -sI https://www.yourdomain.com/old-url | grep -i location
```

**6.3 — Keep redirects flat in next.config.js:**

```js
// next.config.js — keep redirects flat (no chains)
async redirects() {
  return [
    {
      source: '/old-url',
      destination: '/new-url', // Must NOT itself redirect
      permanent: true, // 308 for SEO
    },
  ];
}
```

---

### Step 7 — robots.txt Check

**7.1 — Fetch and inspect robots.txt:**

```powershell
curl.exe -s https://www.yourdomain.com/robots.txt
```

```text
# ✓ Good
User-agent: *
Allow: /
Sitemap: https://www.yourdomain.com/sitemap.xml

# ❌ Bad — disallows crawling of important content
Disallow: /blog/
Disallow: /tools/
```

**7.2 — Next.js App Router robots.js:**

```js
// app/robots.js (Next.js App Router)
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/' },
    sitemap: 'https://www.yourdomain.com/sitemap.xml',
  };
}
```

**7.3 — Verify deployed robots.txt matches your config:**

```powershell
curl.exe -s https://www.yourdomain.com/robots.txt
```

Confirm the output contains `Allow: /` and the `Sitemap:` line. If it shows `Disallow:` on important paths, fix `app/robots.js` and redeploy.

---

## Pitfalls

- **Root layout `noindex` nukes the entire site.** A single `robots: { index: false }` in `app/layout.js` deindexes every page. Always check the root layout first when indexing drops sitewide.
- **Relative canonical URLs.** Google may ignore `canonical: '/blog/my-post'`. Always use absolute URLs with consistent scheme and subdomain.
- **Trailing-slash inconsistency.** If some canonicals end with `/` and others don't, Google treats them as duplicates. Pick one policy and enforce it sitewide.
- **Dynamic pages without `generateStaticParams`.** Pages marked `λ` in build output may not render metadata in the initial HTML, causing Google to miss SEO tags.
- **Redirect chains.** A → B → C wastes crawl budget and dilutes link equity. Flatten to A → C. Verify the destination itself does not redirect.
- **`Disallow:` on important paths in robots.txt.** Even if pages have canonical tags, if robots.txt blocks crawling, Google cannot see the canonical. Never `Disallow` paths you want indexed.
- **Sitemap not submitted to Search Console.** A valid sitemap at `/sitemap.xml` does nothing if Google does not know about it. Submit it explicitly.
- **Orphan pages with zero internal links.** Sitemap inclusion alone is not enough. Google prioritizes pages with real internal links. Add contextual links from related content.
- **Changing URL structure without redirects.** If you change slug patterns or domain, add 308 redirects before deploying. Failing to do so causes mass "Not found 404" in Search Console.
- **Treating "Alternative page with proper canonical" as an error.** This is expected behavior — non-preferred duplicates correctly pointing to the canonical. Do not "fix" these.

---

## Verification

Run through this checklist after applying fixes:

- [ ] All important pages have absolute canonical URLs (`https://www.yourdomain.com/...`)
- [ ] No important pages accidentally `noindex`ed (checked root layout + individual pages)
- [ ] Sitemap routes return HTTP 200 with `Content-Type: application/xml`
- [ ] Sitemap submitted to Google Search Console and status is "Success"
- [ ] Important pages statically generated (`●` or `○`) in `npm run build` output
- [ ] No redirect chains (A→B→C flattened to A→C)
- [ ] `robots.txt` allows important content (`Allow: /`, no `Disallow` on indexable paths)
- [ ] Every important page has ≥1 internal inbound link
- [ ] `generateStaticParams` added for dynamic routes with known slugs

**Quick verification commands:**

```powershell
# 1. Canonical check on a live page
curl.exe -s https://www.yourdomain.com/blog/my-post | Select-String 'rel="canonical"'

# 2. Noindex check on a live page
curl.exe -s https://www.yourdomain.com/blog/my-post | Select-String 'noindex'

# 3. Sitemap returns 200
curl.exe -sI https://www.yourdomain.com/sitemap.xml | Select-String '200'

# 4. robots.txt is accessible
curl.exe -s https://www.yourdomain.com/robots.txt

# 5. Build output shows static pages
npm run build 2>&1 | Select-String '○|●|λ'

# 6. No redirect chains
curl.exe -sIL https://www.yourdomain.com/old-url
```

---

## Limitations

- Does not guarantee Google will index a page; final indexing decisions remain with the search engine.
- Requires access to the codebase, deployed URLs, and ideally Google Search Console data for confident diagnosis.
- Treat recommendations that change URL structure, redirects, or canonical policy as production-impacting and review them before deployment.
- Search Console data has a 2–3 day reporting delay. Wait at least 72h before re-checking coverage after fixes.
