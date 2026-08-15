# Selectors Cookbook — Common Page Shapes

Selector recipes for the page shapes that cover ~90% of scraping work. Each recipe gives
the shape's signals, robust selector candidates (ordered best-first), and the fragility
traps. CSS shown first; XPath where CSS can't express the pattern (lxml or Playwright
`page.locator("xpath=…")`).

---

## 0. Selector strategy (read before writing any selector)

**Anchor hierarchy — always prefer the highest available:**

1. **Structured data**: JSON-LD / microdata / OpenGraph (see reference.md §3) — not a DOM
   selector at all; survives redesigns entirely.
2. **Semantic HTML**: `article`, `main`, `nav`, `time[datetime]`, `table`, `h1`–`h3`.
3. **Stable attributes**: `data-testid`, `data-id`, `data-product-id`, `id` (when not
   auto-generated), `itemprop`, ARIA (`[role=…]`, `[aria-label=…]`).
4. **Human-named classes**: `.post-title`, `.price`, `.pagination` — decent, watch for renames.
5. **Text anchors** (XPath): match on visible label text — good for label/value layouts.
6. **Structural position** (`:nth-child`) — last resort; breaks on any insertion.

**Never anchor to:** hashed/generated classes (`css-1x2y3z`, `sc-bdVaJa`, `_3xk2p`),
utility-class soup (`.flex.items-center.gap-2`), inline styles, or absolute indices into
`div` pyramids.

**Null discipline:** every `css_first`/`querySelector` result gets a None-check; a missing
node yields `null` in the record, never a crash and never a guessed value.

---

## 1. Article / post lists

Signals: repeated `<article>` or `.post`/`.entry` blocks, each with heading + link + date.

```css
/* container candidates, best-first */
main article
[data-testid="post-card"]
ul.post-list > li
div.entry, div.post-summary

/* within each item */
h2 a, h3 a                      /* title + href in one node */
time[datetime]                  /* machine-readable date — prefer the attribute */
a[rel="bookmark"]               /* WordPress-style canonical post link */
.excerpt, .summary, p:first-of-type
```

```python
for card in tree.css("main article"):
    a = card.css_first("h2 a, h3 a, header a")
    t = card.css_first("time[datetime]")
    row = {
        "title": a.text(strip=True) if a else None,
        "url": urljoin(page_url, a.attributes.get("href")) if a else None,
        "published_at": t.attributes.get("datetime") if t else None,
    }
```

Traps: pinned/featured posts duplicated at the top of page 1 (dedupe on URL handles it);
"related posts" widgets matching the same card selector — scope to `main`/`#content` to
exclude sidebars.

---

## 2. Tables

Signals: `<table>` with `thead`/`tbody`, or header row of `<th>`.

**Rule 1: map columns by header TEXT, not position** (see examples.md Example 3).

```css
table#results, table.data-table, main table   /* container */
thead th                                       /* headers */
tbody tr                                       /* data rows */
```

```python
headers = [th.text(strip=True).lower() for th in table.css("thead th")]
col = {h: i for i, h in enumerate(headers)}
for tr in table.css("tbody tr"):
    cells = tr.css("td")
    if len(cells) != len(headers):
        continue          # summary/spanning/group rows — skip, don't misalign
    price = cells[col["price"]].text(strip=True)
```

Traps and handling:
- **`rowspan`/`colspan`**: the naive `cells[i]` mapping silently shifts columns. Detect with
  `tr.css("td[rowspan], td[colspan]")` — if present, expand the grid properly or treat as drift.
- **No `thead`**: first `tr` holds `th` or styled `td` headers → `table.css("tr")[0]`.
- **Layout tables** (old sites): a `table` with no headers at all — fall back to position
  with a fixture-verified mapping.
- **Numbers**: strip currency symbols/thousands separators explicitly; a failed
  `float()` is drift, not a `null`.

XPath for header-relative cells without index math:

```
//table//tr[td][position()>0]/td[count(//table//th[normalize-space()="Price"]/preceding-sibling::th)+1]
```

---

## 3. Cards / product grids

Signals: repeated equal-size tiles in a grid; image + title + price/metadata per tile.

```css
[data-testid="product-card"], [data-product-id]      /* best: stable attributes */
li.product, div.card, .grid > div                    /* class-named fallbacks */

/* within a card */
a[href]                              /* usually wraps the whole card — first a wins */
img[src], img[data-src]              /* data-src = lazy-loaded real image */
[itemprop="price"], .price, [data-price]
h3, .card-title, [itemprop="name"]
```

```python
img = card.css_first("img")
image = (img.attributes.get("src") or img.attributes.get("data-src")
         or img.attributes.get("data-lazy-src")) if img else None
if image and image.startswith("data:"):
    srcset = img.attributes.get("data-srcset") or img.attributes.get("srcset") or ""
    image = srcset.split(",")[0].split()[0] if srcset else None   # placeholder → srcset
```

Traps: lazy-load placeholders (`data:` URIs, 1×1 gifs) in `src` with the real URL in
`data-src`/`srcset`; sale layouts with two prices (`.price--old` struck through vs
`.price--current`) — select the current explicitly, never "first `.price`"; sponsored
tiles interleaved in the grid (`[data-sponsored]`, `.ad-slot`) — exclude explicitly.

---

## 4. Navigation, breadcrumbs, site structure

```css
nav[aria-label="breadcrumb" i] li, ol.breadcrumb li     /* breadcrumbs */
nav a[href], header nav a[href]                          /* primary nav */
aside nav a[href], .sidebar a[href], nav.toc a[href]     /* docs sidebar/TOC */
```

BreadcrumbList JSON-LD beats DOM scraping when present (`@type: "BreadcrumbList"`,
`itemListElement[].item.name/@id`). For crawl seeding, prefer the sitemap over walking nav
links — nav shows what's promoted, the sitemap shows what exists.

Trap: mega-menus contain hundreds of links including cross-site promos — filter to
same-host + path-prefix before adding to a frontier.

---

## 5. Page metadata (title, canonical, dates, author)

Precedence: **JSON-LD → meta tags → visible DOM** (see reference.md §3 for extractors).

```css
link[rel="canonical"]                        /* THE canonical URL — dedupe key */
meta[property="og:title"], title
meta[property="article:published_time"]      /* ISO-8601, publisher-set */
meta[name="author"], [rel="author"], [itemprop="author"]
time[datetime]                               /* attribute, not the human text */
html[lang]                                   /* language tag */
```

Date extraction order: `article:published_time` meta → JSON-LD `datePublished` →
`time[datetime]` attribute → visible text (last resort; needs `dateutil` parsing and a
recorded format assumption). Store all dates ISO-8601 UTC.

Trap: relative dates in visible text ("3 days ago") are relative to *fetch* time — resolve
against `_prov.fetched_at` and mark the field as approximate, or prefer a machine-readable
source.

---

## 6. Pagination controls

```css
link[rel="next"]                              /* head link — most reliable when present */
a[rel="next"]                                 /* body version */
nav.pagination a, ul.pager a
a[aria-label*="next" i]                       /* accessible labels */
.pagination li:last-child a                   /* positional — last resort */
```

XPath text-anchor when nothing structural exists:

```
//a[normalize-space()="Next" or normalize-space()="›" or normalize-space()="»"]
```

Total-count discovery (for the coverage gate): `.pagination li:nth-last-child(2)` (last
numbered page), or text like "Showing 1–20 of 483" →
`re.search(r"of\s+([\d,]+)", text)`.

Traps: "Next" present but disabled on the last page (`a.disabled`, `aria-disabled="true"`,
or an `<span>` replacing the `<a>`) — check before following; sites whose last page links
back to page 1 — the `seen` set in the pagination loop (reference.md §4.2) is mandatory.

---

## 7. JSON-LD script blocks

```css
script[type="application/ld+json"]
```

Parsing rules (full extractor in reference.md §3):
- A page can carry **multiple** blocks; a block can be an object, an **array**, or an
  object with an **`@graph`** array — flatten all three.
- Malformed JSON in one block must not kill extraction — skip and continue.
- `@type` can be a string or a **list** (`["Product", "Vehicle"]`) — check with set overlap.
- Values that "should" be objects are sometimes bare strings (`"author": "Jane"` vs
  `{"@type": "Person", "name": "Jane"}`) — handle both.

High-value types → fields:

| @type | Fields worth extracting |
|---|---|
| `Product` | name, sku, brand.name, offers.price, offers.priceCurrency, offers.availability, aggregateRating.ratingValue |
| `Article` / `NewsArticle` / `BlogPosting` | headline, datePublished, dateModified, author.name, mainEntityOfPage |
| `Event` | name, startDate, endDate, location.name, location.address, offers.price |
| `BreadcrumbList` | itemListElement[].item.name / @id (category path) |
| `Recipe`, `JobPosting`, `FAQPage` | domain-specific but consistently structured |

---

## 8. Label/value layouts (spec sheets, definition lists)

Signals: `<dl>`, or two-column label/value tables, or `.spec-row` pairs.

```css
dl dt, dl dd          /* zip dt/dd pairs in order */
.spec-name, .spec-value
```

```python
dts = [n.text(strip=True) for n in tree.css("dl.specs dt")]
dds = [n.text(strip=True) for n in tree.css("dl.specs dd")]
specs = dict(zip(dts, dds))          # verify equal lengths first; mismatch = drift
```

XPath text-anchor — the pattern CSS cannot do, ideal for "find the value next to this label":

```
//dt[normalize-space()="Weight"]/following-sibling::dd[1]
//th[contains(normalize-space(), "ISBN")]/following-sibling::td[1]
//*[normalize-space()="SKU"]/following-sibling::*[1]
```

Text anchors survive class renames and layout swaps; they break on label wording changes —
match the shortest distinctive token (`contains()`), normalize whitespace, and mind case.

---

## 9. Fragility checklist (run against every new selector set)

- [ ] Zero selectors reference hashed/utility classes.
- [ ] Every field has a fallback chain or an explicit "null when absent" decision.
- [ ] Scoped to a content root (`main`, `article`, `#content`) so sidebars/footers/ads
      can't leak into results.
- [ ] Tested against the saved fixture AND one page of a *different* item (second fixture)
      — a selector that only works on one page is a coincidence.
- [ ] Pagination end-condition tested (last page fixture or simulated empty page).
- [ ] Table column mapping is header-text based; rowspan/colspan presence checked.
- [ ] Lazy-image and placeholder handling verified for any image field.
- [ ] Selector set recorded in `recon.md` with the fixture hash it was validated against.
