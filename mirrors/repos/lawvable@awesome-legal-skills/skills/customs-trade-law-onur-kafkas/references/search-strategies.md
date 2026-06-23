# Search Strategies — Query Patterns for All Data Sources

This file contains validated, curated search patterns for retrieving trade and customs data. Use these patterns in `web_search` and `web_fetch` calls throughout all workflows.

---

## 1. HTS Classification Lookup

### Current HTS Bulk JSON Discovery (Required for revision-aware work)

Follow `references/hts-data-sources.md` before relying on bulk JSON, GRI 6 hierarchy, rate fields, or Chapter 99 footnotes. Discover the latest JSON through Data.gov catalog metadata first; do not hard-code a revision-specific USITC URL as the primary source.

Current Data.gov catalog API pattern:

```text
web_fetch("https://catalog.data.gov/search?q=Harmonized+Tariff+Schedule+of+the+United+States+{current_year}&per_page=10")
```

Record:
- Data.gov catalog URL
- catalog checked / harvest date if available
- selected `HTS Revision N (JSON)` title
- JSON download URL
- analysis date
- HTS revision used

If Data.gov is unavailable, use:

```text
web_fetch("https://www.usitc.gov/tata/hts/archive/index.htm")
web_fetch("https://www.usitc.gov/harmonized_tariff_information")
```

Helper:

```text
python3 scripts/resolve-latest-hts-json.py --year {current_year}
```

### USITC REST API (for live keyword/rate lookup)
```
web_fetch("https://hts.usitc.gov/reststop/search?keyword={TERM}")
```
- Returns: Up to 100 tariff articles as JSON
- Fields: htsno, description, indent, general, special, other, footnotes, units
- **Does NOT include** chapter/section notes — only heading/subheading data
- URL-encode the keyword term
- Try multiple keyword variations for best coverage

REST results are useful for candidate discovery, but they do not replace a recorded current HTS revision for hierarchy-sensitive GRI 6 analysis.

### Bulk JSON (for hierarchy navigation)

- Use the selected JSON URL from Data.gov or fallback sources.
- Returns: complete flat array of HTS line items.
- Use `scripts/hts-hierarchy-builder.py` to convert to a navigable tree.
- If the user uploads a JSON file, record the filename and ask how it was sourced if revision/date is unclear.

### Chapter PDFs (for chapter/section notes)
```
web_fetch("https://hts.usitc.gov/reststop/file?release=currentRelease&filename=Chapter+{N}")
```
- Returns: Binary PDF — recommend user download
- **Only source** for chapter notes, section notes, and General Notes
- Critical for GRI 1 analysis

### Web Search Fallback
```
web_search("{product name} HTS classification HTSUS")
web_search("{product function} tariff heading chapter {XX}")
web_search("HTSUS {heading number} {product description}")
web_search("HTS chapter {N} notes {relevant note topic}")
```

---

## 2. CROSS Ruling Research

### Primary Method — Direct CROSS Search URL
```
web_fetch("https://rulings.cbp.gov/search?term={product+keywords}&collection=ALL&commodityGrouping=ALL&sortBy=DATE_DESC&pageSize=30&page=1")
```
- Returns: Current rulings sorted by date (newest first)
- URL-encode search terms (spaces as `+`)
- Adjust `collection`: `ALL` (default), `HQ` (Headquarters only), `NY` (New York only)
- Adjust `pageSize` (max 30) and `page` for pagination

### Individual Ruling Fetch
```
web_fetch("https://rulings.cbp.gov/ruling/{RULING_ID}")
```
- Returns: Full ruling text including product description, classification, reasoning, and status
- Use for achieving **Verified** evidence quality

### Boolean Search Patterns (supported in the `term` parameter)
- AND: `keyboard AND bluetooth AND 8471`
- OR: `smartwatch OR "smart watch" OR "wrist computer"`
- AND NOT: `keyboard AND NOT piano`
- NEAR: `essential NEAR character` (finds terms in proximity)
- Wildcard: `comput*` (matches computer, computing, computation)
- Exact phrase: `"essential character"`

### Ruling Research Strategy
1. Start broad: `web_fetch` with product keywords, `collection=ALL`, `sortBy=DATE_DESC`
2. Narrow by heading: add the 4-digit heading to the search terms
3. Focus on HQ rulings: set `collection=HQ` for authoritative Headquarters rulings
4. Fetch individual rulings: `web_fetch("https://rulings.cbp.gov/ruling/{ID}")` for full text
5. Check for revocations: look for revocation/modification notices in the ruling text

---

## 3. CIT/CAFC Court Decisions

Sources are **not** co-equal. Follow this strict priority order:

### Step 1: CIT Slip Opinions Index — identify decisions
```
web_fetch("https://www.cit.uscourts.gov/content/slip-opinions-{YYYY}")
```
- Returns: Structured table with opinion #, caption, date, docket, judge, jurisdiction code
- Filter for jurisdiction code `1581(a)` = classification cases

### Step 2: PDF Text Extraction — PRIMARY SOURCE for opinion text
```
bash: python3 scripts/cit-opinion-fetcher.py {slip-op-number}
```
- Example: `python3 scripts/cit-opinion-fetcher.py 26-11`
- Downloads the PDF from `cit.uscourts.gov` and extracts full text using pymupdf
- Also accepts a full URL or local file path
- This is the primary source for opinion text. Always use this before fallbacks.

### Step 3: Fallback Sources — only if PDF reader is unavailable
```
web_search("site:law.justia.com Court International Trade {product} classification")
web_search("site:law.justia.com CIT {HTS heading} {year}")
```
- Justia indexes full case text in readable format
- Use only as a fallback when direct PDF fetch fails

```
web_search("Court of International Trade {HTS heading} classification")
web_search("CIT {product type} classification {heading} GRI")
web_search("site:cit.uscourts.gov {product} classification")
```

### CAFC Appeals
```
web_search("CAFC {product type} HTS classification appeal")
web_search("Federal Circuit {heading} tariff classification")
web_search("Court of Appeals Federal Circuit customs classification {product}")
```

### CIT Decision Filtering
- Jurisdiction 1581(a): Classification disputes (primary interest)
- Jurisdiction 1581(c): AD/CVD cases
- Jurisdiction 1581(i): Residual jurisdiction
- Always check for CAFC appeal status of any CIT decision cited

---

## 4. Chapter 99 / Trade Remedy Surcharges

### Section 301 (China Tariffs)
```
web_search("Section 301 tariff {HTS heading} China {current_year}")
web_search("USTR Section 301 list {product type} {current_year}")
web_search("9903.88 {HTS heading} Section 301")
web_search("Section 301 exclusion {product} {HTS heading} {current_year}")
```

### Section 232 (Steel/Aluminum)
```
web_search("Section 232 tariff {product} {current_year}")
web_search("Section 232 steel aluminum tariff rate {current_year}")
web_search("Section 232 exclusion {product} {current_year}")
```

### Section 201 (Safeguard)
```
web_search("Section 201 safeguard tariff {product} {current_year}")
```

---

## 5. AD/CVD Orders

```
web_search("site:trade.gov antidumping duty order {product} {country}")
web_search("site:trade.gov countervailing duty order {product} {country}")
web_search("site:federalregister.gov AD/CVD order {product} {country}")
web_search("Commerce scope ruling {product} {country} AD/CVD")
web_search("ACCESS Commerce {product} {country} antidumping countervailing")
```

---

## 6. Country of Origin

### Marking Rules
```
web_search("CBP country of origin marking {product type}")
web_search("19 CFR 134 substantial transformation {product}")
web_fetch("https://rulings.cbp.gov/search?term=country+of+origin+{product}&collection=ALL&commodityGrouping=ALL&sortBy=DATE_DESC&pageSize=30&page=1")
```

### FTA Rules of Origin
```
web_search("USMCA rules of origin {HTS heading} tariff shift")
web_search("{FTA name} rules of origin {product type}")
web_search("CAFTA-DR origin {HTS chapter} rule")
```

### Trade Agreements Act (TAA)
```
web_search("TAA substantial transformation {product} {country}")
web_search("Trade Agreements Act designated country list {current_year}")
```

---

## 7. Supplemental Sources

### Informed Compliance Publications
```
web_search("CBP informed compliance {product type}")
web_search("site:cbp.gov informed compliance classification {chapter}")
```

### Explanatory Notes (World Customs Organization)
```
web_search("WCO Explanatory Notes heading {XXXX}")
web_search("Harmonized System Explanatory Notes {heading} {product}")
```

### Federal Register Notices
```
web_search("Federal Register {topic} tariff {current_year}")
web_search("site:federalregister.gov customs {product} {current_year}")
```

---

## Search Strategy Tips

1. **Always search with the current year** to get the most recent information
2. **Use multiple keyword variations** — trade terminology may differ from common language
3. **Prioritize direct source access** (Data.gov/USITC for HTS, CROSS for rulings, official CIT/CAFC opinion text for courts) over general web search
4. **Cross-reference** results from multiple searches — no single search captures everything
5. **Check footnotes** in HTS API results for Chapter 99 cross-references (e.g., "See 9903.88.15")
6. **Use Data.gov bulk JSON discovery** for revision-aware HTS hierarchy; use REST search for live keyword and rate confirmation
