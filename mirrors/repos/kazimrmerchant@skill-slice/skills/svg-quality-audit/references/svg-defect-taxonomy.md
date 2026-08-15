# SVG Defect Taxonomy (from the consolidated vault audit, 2026-07-15)

Scope: 17,348 unique SVGs in `assets/consolidated/all/` (by-source/ is a mirrored copy).
All counts below are from a 100% structural scan (verified, reproducible).

## Headline numbers
- Valid XML: 16,731 (96.4%) · Invalid: 617 (3.6%)
- Escape-bug files: 747 (4.3%) — recoverable: 735 · stay-invalid: 12
- JSON-LD `<script>` (benign): 11,306 (65.2%) · Executable JS `<script>`: 0
- No viewBox: 26 · Fixed root width/height: 17,132 (98.8%)
- Drawable shapes: median 47, p75 199, p95 2,642, max 22,895

## Defect classes (by exact ElementTree error)
| Bucket | Count | Severity | Recovery |
|---|---|---|---|
| "invalid token" line 1 col 38 | 533 | LOW* | un-escape `\n`→newline etc. |
| "junk after document element" | 94 | MED | trim trailing LLM text after `</svg>` |
| "mismatched tag" | 12 | MED | fix structure (assisted) |
| "duplicate attribute" | 6 of 23 parse-fails | MED | dedupe attrs (keep first) |
| "undefined entity" | 2 | MED | declare entity or use numeric |

* LOW because Chrome renders these fine once escaped; strict parser only chokes on the backslash.

## 1. Escape-bug (dominant)
Symptom: file contains literal backslash sequences `\\n` `\\t` `\\\"` where newlines / quotes belong.
Column 38 = right after `<?xml ...?>\n`. Cause: a JSON/`repr()` serialization step that escaped
the whole SVG string.
Recovery (safe, no-op on clean files — verified 186 clean files stayed valid):
```python
raw = open(p, encoding="utf-8", errors="replace").read()
fixed = raw.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
# then ET.fromstring(fixed) — 735/747 become valid
```
Note: the duplicate-attribute count is 23 total; 6 of those also fail ET parse, 17 are
browser-tolerated (Chrome drops the 2nd value → visual drift).

## 2. JSON-LD `<script>` is BENIGN (false-alarm guard)
`grep "<script"` hits 11k files. Break it down — 11,306 are
`<script type="application/ld+json">` (schema.org ImageObject metadata). Only flag REAL executable
JS: `type="text/javascript"` / `application/javascript` / `application/ecmascript` → 0 here.
Security verdict: clean. Also count `<image href="data:|https:">` separately (6 external here).

## 3. LLM-junk-after-`</svg>` (94)
Regex: find `</svg>\s*` then check if `raw[m.end():].strip()` is non-empty. Examples of leaked
text: "We need to output only the SVG XML. Must follow strict rules." Trim it for a clean library.
These RENDER fine (coverage ~84%) but pollute the asset.

## 4. Duplicate attributes (23)
`<path ... opacity="0.4" ... opacity="0.3" />` etc. Invalid XML. Chrome silently drops the 2nd.
Detect: for each tag, collect attr names via `re.findall(r'([\w:-]+)\s*=', attrs)`; if
`len(names) != len(set(names))` -> broken.

## 5. Undefined entity (2)
`&foo;` where `foo` is not `amp|lt|gt|quot|apos|#\d+;|#x..;` and no `<!ENTITY>` declared.
Detect: strip legal entities, then search `&[A-Za-z][A-Za-z0-9]*;`.

## Per-source quality signal (vision, stratified sample)
- Jules / domain / business dashboards -> mostly 5-9 (gallery-grade, recognizable).
- agy/* artistic -> clusters 1-6 (sludge, oversaturated, off-canvas, or parser-broken).
- "Valid XML" does NOT imply "looks good" -- e.g. `jules-w0059-sales-timeline` valid but scored 3 ("empty").
