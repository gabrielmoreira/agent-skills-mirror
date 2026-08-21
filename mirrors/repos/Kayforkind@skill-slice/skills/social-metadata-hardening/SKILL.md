---
name: social-metadata-hardening
description: "Hardens Open Graph and Twitter Card tags so public URLs unfurl as rich cards on Facebook, LinkedIn, X, WhatsApp, Telegram, Slack, and Discord. Use when shared links show missing, stale, cropped, or broken previews, or when auditing og and twitter metadata before launch. Not for paid social ad creatives or sitemap-only SEO; never rely on client-side JS to inject tags crawlers must see."
version: 1.0.1
category: seo
risk: safe
source: self
source_type: self
date_added: "2026-05-31"
tags: [seo, open-graph, twitter-card, social-sharing, og-image, nextjs, metadata]
tools: [claude, cursor, gemini, claude-code]
---

# Social Metadata Hardening

Fix social sharing so every important URL unfurls as a rich card across all platforms. This skill covers OG tags, Twitter cards, absolute image URLs, `metadataBase` configuration, and cross-platform debugging.

## When to Use

- Shared links show **missing, stale, cropped, or incorrect** previews on social or chat platforms.
- Auditing **Open Graph, Twitter/X card, image URL, alt text, or `metadataBase`** coverage in a web app.
- **Pre-launch hardening** when every public page needs predictable rich previews across LinkedIn, X, Facebook, WhatsApp, Slack, Discord, and Telegram.
- Tags were added **client-side via JavaScript** and crawlers cannot see them.

## Prerequisites

- A deployed, publicly reachable URL (platform debuggers require live URLs).
- Node.js project using **Next.js App Router** (examples below); patterns adapt to other frameworks with static HTML head injection.
- PowerShell on Windows as primary shell. `curl.exe` (Windows 10+ built-in) or `Invoke-WebRequest` for verification.
- OG image asset hosted on HTTPS with no authentication required.

## Procedure

### Step 1 — Diagnose the current state

Check whether OG and Twitter tags exist in raw HTML (not JS-rendered):

```powershell
# Windows PowerShell — fetch raw HTML and filter for social tags
(Invoke-WebRequest -Uri 'https://www.yourdomain.com/blog/my-post' -UseBasicParsing).Content `
  -split "`n" | Select-String -Pattern 'og:|twitter:'

# Alternative using curl.exe (ships with Windows 10+)
curl.exe -s https://www.yourdomain.com/blog/my-post | findstr /i "og: twitter:"
```

If tags do **not** appear in raw HTML, they are being injected by JavaScript and crawlers will not see them. Proceed to Step 2.

### Step 2 — Create the shared metadata helper

Create `lib/socialMetadata.js` in your project. This helper guarantees absolute URLs, correct MIME types, and full OG + Twitter coverage:

```js
// lib/socialMetadata.js
export function buildSocialMetadata({
  title,
  description,
  path,          // '/blog/my-post'
  image,         // '/images/og/my-post.jpg' or full URL
  imageAlt,
  imageWidth = 1200,
  imageHeight = 630,
}) {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://www.yourdomain.com';

  // Always produce an absolute URL
  const imageUrl = image?.startsWith('http') ? image : `${baseUrl}${image}`;
  const pageUrl  = `${baseUrl}${path}`;

  // Detect MIME type from extension
  const ext = imageUrl.split('.').pop().toLowerCase();
  const mimeMap = { jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp' };
  const imageType = mimeMap[ext] || 'image/jpeg';

  return {
    title,
    description,
    alternates: { canonical: pageUrl },
    openGraph: {
      title,
      description,
      url: pageUrl,
      type: 'website',  // use 'article' for blog posts
      images: [{
        url: imageUrl,
        secureUrl: imageUrl,   // explicit HTTPS version
        width: imageWidth,
        height: imageHeight,
        alt: imageAlt || title,
        type: imageType,
      }],
    },
    twitter: {
      card: 'summary_large_image',  // NOT 'summary' — that shows a tiny image
      title,
      description,
      images: [imageUrl],
    },
  };
}
```

### Step 3 — Set `metadataBase` in the root layout

This is **required** when using relative metadata URLs in Next.js App Router:

```js
// app/layout.js
import { buildSocialMetadata } from '@/lib/socialMetadata';

export const metadata = {
  metadataBase: new URL('https://www.yourdomain.com'), // REQUIRED for absolute URLs
  ...buildSocialMetadata({
    title: 'My Site — Tagline Here',
    description: 'Site-wide description.',
    path: '/',
    image: '/images/og/home.jpg',
    imageAlt: 'My Site homepage preview',
  }),
};
```

> **HARD RULE:** If your helper already outputs absolute canonical/OG URLs, previews can still work without `metadataBase`, but setting it prevents edge-case relative URL bugs.

### Step 4 — Apply the helper to every shareable page

**Static page:**

```js
// app/about/page.js
import { buildSocialMetadata } from '@/lib/socialMetadata';

export const metadata = buildSocialMetadata({
  title: 'About Us | My Site',
  description: 'Learn about our team and mission.',
  path: '/about',
  image: '/images/og/about.jpg',
  imageAlt: 'The My Site team',
});
```

**Dynamic page (blog post, tool page):**

```js
// app/blog/[slug]/page.js
import { buildSocialMetadata } from '@/lib/socialMetadata';

export async function generateMetadata({ params }) {
  const post = await getPost(params.slug);
  return buildSocialMetadata({
    title: `${post.title} | My Blog`,
    description: post.excerpt,
    path: `/blog/${params.slug}`,
    image: post.ogImage || '/images/og/default.jpg',
    imageAlt: post.title,
  });
}
```

### Step 5 — Verify OG image assets

OG images must meet these specifications:

| Requirement | Value |
|-------------|-------|
| Dimensions | **1200 × 630px** (2:1 ratio) |
| File size | **Under 8MB** (Facebook limit) |
| Protocol | **HTTPS** |
| Filename | **No spaces** (use hyphens) |
| Format | **JPEG or PNG** (WebP works on most but not all crawlers) |
| Access | **GET with no authentication** |

```powershell
# Verify OG image is reachable and check headers
curl.exe -sI https://www.yourdomain.com/images/og/home.jpg

# PowerShell native
Invoke-WebRequest -Uri 'https://www.yourdomain.com/images/og/home.jpg' -Method Head `
  | Select-Object StatusCode, Headers
```

### Step 6 — Deploy and force platform cache refresh

After deploying, paste the URL into each platform's debugger and trigger a fresh crawl:

| Platform | Debugger URL | Action |
|----------|-------------|--------|
| Facebook / Meta | https://developers.facebook.com/tools/debug/ | Click "Fetch new scrape information" |
| LinkedIn | https://www.linkedin.com/post-inspector/ | Click "Inspect" |
| X / Twitter | https://cards-dev.twitter.com/validator | Enter URL and submit |
| General preview | https://metatags.io | Paste URL |

### Step 7 — Platform-specific notes

**Facebook / Meta:**
- Caches aggressively — always use the Sharing Debugger to force recrawl.
- Minimum image: 200×200px (but use 1200×630 for quality).
- Required tags: `og:title`, `og:description`, `og:image`, `og:url`.

**X / Twitter:**
- Use `twitter:card = summary_large_image` for full-width images.
- `twitter:image` must be an absolute URL.
- Use the Card Validator to test.

**LinkedIn:**
- Caches hard — use Post Inspector to refresh.
- Respects `og:` tags; **ignores `twitter:` tags**.
- Image must be ≥1.91:1 aspect ratio.

**WhatsApp / Telegram:**
- Read OG tags on first share; cache can last hours.
- Re-share after a few hours for the cache to clear naturally.

**Slack / Discord:**
- Both use OG tags; both cache.
- Discord also supports `og:type = article` for richer embeds.

## Pitfalls

- **Relative image URLs break previews.** Every OG and Twitter image URL must be absolute (`https://...`). Relative paths like `/images/og/home.jpg` will not unfurl.
- **`twitter:card` set to `summary`** produces a tiny square image. Always use `summary_large_image` for rich cards.
- **Tags injected by client-side JavaScript** are invisible to crawlers. Move metadata to `export const metadata` or `generateMetadata` (server-side).
- **Stale previews after fix.** Platforms cache aggressively. You must manually trigger recrawl via each platform's debugger — deploying alone is not enough.
- **WebP images may not render** on all crawlers. Prefer JPEG or PNG for maximum compatibility.
- **Missing `metadataBase`** causes relative URL bugs in Next.js when the helper outputs relative paths. Always set it in the root layout.
- **Filenames with spaces** can break URL encoding on some platforms. Use hyphens only.
- **Images behind authentication** will not load for crawlers. OG images must be publicly accessible.
- **LinkedIn ignores `twitter:` tags entirely.** Do not rely on Twitter card tags for LinkedIn previews — ensure `og:` tags are complete.

## Verification

### 1. Confirm tags exist in raw HTML

```powershell
# PowerShell — check for OG and Twitter tags in server-rendered HTML
(Invoke-WebRequest -Uri 'https://www.yourdomain.com/blog/my-post' -UseBasicParsing).Content `
  -split "`n" | Select-String -Pattern 'og:title|og:description|og:image|twitter:card|twitter:image'
```

**Expected output:** Lines containing `og:title`, `og:description`, `og:image` (with absolute URL), `twitter:card` set to `summary_large_image`, and `twitter:image` (with absolute URL).

If no lines appear, tags are JS-rendered and must be moved server-side.

### 2. Confirm image is reachable and correct

```powershell
curl.exe -sI https://www.yourdomain.com/images/og/home.jpg
```

**Expected:** `HTTP/2 200` with `content-type: image/jpeg` or `image/png` and `content-length` under 8MB (8388608 bytes).

### 3. Validate with platform debuggers

Run each URL through:

| Platform | Tool |
|----------|------|
| Facebook | https://developers.facebook.com/tools/debug/ |
| LinkedIn | https://www.linkedin.com/post-inspector/ |
| Twitter/X | https://cards-dev.twitter.com/validator |
| General | https://metatags.io |

**Expected:** Each debugger shows a rich card preview with the correct title, description, and 1200×630 image.

### 4. Final checklist

- [ ] `metadataBase` set in root layout
- [ ] All shareable pages use shared `buildSocialMetadata` helper
- [ ] OG image URLs are absolute (start with `https://`)
- [ ] `secureUrl` set equal to `url` in OG image block
- [ ] Image is 1200×630px, under 8MB, HTTPS
- [ ] `twitter:card` is `summary_large_image` (not `summary`)
- [ ] Image alt text present
- [ ] Tags visible in raw HTML (not JavaScript-rendered)
- [ ] All platform debuggers show correct preview
- [ ] Cache refreshed on all platforms after deployment

## Limitations

- Cannot force immediate cache refresh on every social platform; some previews may remain stale after a correct fix.
- Requires publicly reachable deployed URLs for reliable validation with platform debuggers.
- Does not replace brand, accessibility, or legal review of image text, alt text, and preview copy.
