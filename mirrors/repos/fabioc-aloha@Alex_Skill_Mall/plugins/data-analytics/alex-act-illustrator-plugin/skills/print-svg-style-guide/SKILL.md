---
name: print-svg-style-guide
description: "Author print-quality SVG figures for books, reports, and exec-facing documents. Ships the canvas + typography grammar (viewBoxes, print-legibility floor with math, type hierarchy, font stack, data-print-role markers, text-fits ladder), a Tailwind-grounded semantic palette (Blue = correct, Red = critique, Green = approval, Amber triple-duty, Grays scaffolding), and four structural composition idioms (BEFORE/AFTER paired panels with badges, numbered critique callouts, family-band abstracts, 5-Visual Rule dashboards). Use when authoring SVG figures for print, when reviewing a figure for print legibility, or when picking colors for a figure whose colors will carry meaning across a book or report."
lastReviewed: 2026-07-29
---

# Print-quality SVG style guide

Rules for print-quality SVG figures in books, reports, and exec-facing HTML. Distilled from a shipped book — Fabio Correa's *The Defensible Decision*, 53 figures across 14 chapters at print size 7×10in, figure width 4.39in — via Alex_DDA's `dd-book-illustrator` skill. Portable to any figure that will land on paper or a PDF.

Complements the big-idea family: `big-idea` and `chart-big-idea` decide what the figure ARGUES; this skill decides how it LOOKS. `flint-chart`'s publication config preset pins the Vega-Lite config that emits charts obeying these rules. `figure-generator` provides the engineering discipline that emits SVGs conforming to this guide.

## When to invoke

- Authoring a new SVG figure for a book, report, or exec-facing document
- Reviewing an existing figure for print-legibility, palette consistency, or composition
- Picking canvas dimensions when the target is print + on-screen
- Deciding a color role for a new figure that will co-exist with other figures in the same artifact
- Composing a BEFORE/AFTER paired panel, a numbered critique callout, a family-band abstract, or a dashboard subject to the 5-Visual Rule

## Canvas + font stack

Every figure obeys three defaults unless a specific composition need overrides:

| Property           | Value                                | When to override                                             |
| ------------------ | ------------------------------------ | ------------------------------------------------------------ |
| Font stack         | `Inter, system-ui, sans-serif`       | Never in figures. Book body prose can differ (Palatino, etc.) |
| Default viewBox    | `0 0 640 480` (4:3)                  | Standard chapter figure                                      |
| Widescreen viewBox | `0 0 640 380` (~17:10)               | Book-map, flow, wide-comparison figures                      |
| Dashboard viewBox  | `0 0 640 415` (varies)               | Dashboard-shaped figures                                     |

Reasons to pin at 640 viewBox width: (a) the print-legibility floor math (below) is calibrated to a 640-unit reference; (b) side-by-side figures across chapters read as one voice when they share horizontal dimensions.

## Print-legibility floor (gate-enforced)

Figures rendered at 7×10in with figure width 4.39in convert SVG px to print points via:

```text
printPoints = fontSizePx × 4.39 × 72 ÷ viewBoxWidth
```

At the standard 640-unit viewBox that reduces to `px × 0.4939`. Floors:

| Class                                                             | Floor       | Marker                                                                                                                 |
| ----------------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| Instructional (anything the reader must read)                     | **5.8pt**   | none                                                                                                                   |
| Note (annotation the reader is meant to read, below body copy)    | **2.9pt**   | `data-print-role="note"` required. Auto-promoted from `micro` when the text is ≥40 characters                          |
| Micro (source notes, attribution, hash stamps, provenance)        | **2.9pt**   | `data-print-role="micro"` required                                                                                     |

| px       | pt at 640 viewBox | Verdict                        |
| -------- | ----------------- | ------------------------------ |
| 9px      | 4.44pt            | micro only                     |
| 10px     | 4.94pt            | **fails** as instructional     |
| 11px     | 5.43pt            | **fails** as instructional     |
| **12px** | **5.93pt**        | **lowest safe instructional**  |

**Rule**: minimum instructional px = `viewBoxWidth ÷ 54.5`. At 640 that is 11.74px, so 12px is the floor. A wider viewBox raises the floor — recompute rather than assuming 12px.

**The micro marker is not an escape hatch**. It exists for text the reader never needs to read at size (attribution, hash stamps). Marking instructional content `micro` to clear the gate is gaming it — the reader still cannot read it. The `note` role's auto-promote (≥40 chars) catches the class where this happens by accident.

### When text won't fit at 12px, the answer is never to shrink it

Shrink-vs-overflow is a false choice; both lose. In priority order:

1. **Cut the text.** A figure carrying sentence-length explanation is restating adjacent prose, which fails the earn-a-figure test outright (see `chart-big-idea` Step 0.5). Move the sentences to the chapter body and leave labels in the figure.
2. **Reflow.** Split one dense panel into two, or switch to the widescreen viewBox.
3. **Abbreviate.** Fewer axis ticks, shortened value labels, a legend instead of per-point labels.
4. **Grow the canvas.** Last resort — it changes the figure's page footprint.

### Anti-pattern figures obey the floor too

A figure whose subject IS bad typography (collapsed hierarchy, unreadable clutter) must still clear 5.8pt. The gate cannot distinguish "deliberately bad" from "accidentally illegible," and neither can the reader.

**Demonstrate the failure through RELATIVE properties, never absolute smallness.** Typographic hierarchy is about differentiation: L1 through L4 have to differ from each other. Setting title, axis, and data labels all to 12px demonstrates collapsed hierarchy perfectly (everything is the same size) while every word stays legible in print. Setting them all to 10px demonstrates the same collapse and makes the figure unreadable, defeating its own teaching purpose.

| Failure being taught            | Wrong way                     | Right way                                                  |
| ------------------------------- | ----------------------------- | ---------------------------------------------------------- |
| Collapsed typographic hierarchy | Everything at 10px            | Everything at 12px — identical, therefore undifferentiated |
| Chart clutter                   | Shrink labels to cram more in | Keep 12px, let density itself read as clutter              |
| Illegible data labels           | Actually illegible            | 12px labels overlapping or colliding                       |

## Type hierarchy

| Role                  | Style                                        | Notes                                                                                                                            |
| --------------------- | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Figure title          | 18px / 700 / `#1f2937` / centered / y≈22-28   | 16px for very tall figures                                                                                                       |
| Subtitle              | 12px italic / `#6b7280` / centered / y≈40-48  | One-line takeaway                                                                                                                |
| Source note           | 9px / `#6b7280` / centered / y≈64             | Only when synthetic dataset needs attribution. Requires `data-print-role="micro"`                                                |
| Panel title           | 13px / 700 / `#1f2937` / left / x+12 / y+22  |                                                                                                                                  |
| Panel subtitle        | 12px italic / `#6b7280` / left               |                                                                                                                                  |
| Body / data           | 12px / `#1f2937` (data) or `#6b7280` (axis)  | 12px is the instructional minimum                                                                                                |
| Axis tick labels      | 12px / `#6b7280`                             | If ticks crowd at 12px, reduce tick COUNT or abbreviate values. Never shrink below 12px                                          |
| KPI number            | 14px / 700 / `#1e40af` inside white card     |                                                                                                                                  |
| Category label        | 12px / 700 / colored to match family accent | e.g., `COMPARISON` in `#1d4ed8`                                                                                                  |

## `data-print-role` markers (how to mark below-floor text safely)

Two roles below the 5.8pt instructional floor:

- **`data-print-role="micro"`** — attribution, provenance, hash stamps, source notes. Reader never needs to read at size.
- **`data-print-role="note"`** — annotation text the reader IS meant to read, but below body copy. Auto-promoted from `micro` when the text is ≥40 characters.

Both share the 2.9pt floor. The taxonomy exists because a coverage scanner otherwise cannot distinguish "this is a hash stamp" from "this is a caption the reader is expected to read."

## Tailwind-grounded semantic palette

Color carries meaning — pick from this palette rather than introducing new hues. Consistency across chapters is the reader's cross-reference tool.

> **Relationship to the constellation brand palette.** These are the **print variants** of the Alex ACT semantic role coding — darker Tailwind values (gray-800, blue-800, amber-700) tuned for high-contrast on white paper. The **screen variants** (`ddf4ff` pastels for mermaid classDefs, banner emerald `#10b981`) live in [`.github/config/brand-palette.json`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/.github/config/brand-palette.json) in `Alex_ACT_Steward`. Same semantic roles across both variants (Input / Output / Processing / Decision / Error / Neutral); different lightness for the target surface.

### Grays (neutral scaffolding)

| Hex       | Tailwind  | Use                                                |
| --------- | --------- | -------------------------------------------------- |
| `#1f2937` | gray-800  | Headlines, panel titles, primary text              |
| `#374151` | gray-700  | Table headers, secondary text                      |
| `#6b7280` | gray-500  | Subtitles, axis labels, muted data, source notes   |
| `#9ca3af` | gray-400  | Axis lines, thin separators                        |
| `#d1d5db` | gray-300  | Panel borders, dividers                            |
| `#f3f4f6` | gray-100  | BEFORE panel background (slightly deeper)          |
| `#f9fafb` | gray-50   | Default panel background                           |
| `#ffffff` | white     | Card backgrounds inside panels                     |
| `#cbd5e1` | slate-300 | De-emphasised bars (compare-with-selected pattern) |

### Discipline blues (correct / principled / primary data)

| Hex                                                       | Tailwind       | Use                                                             |
| --------------------------------------------------------- | -------------- | --------------------------------------------------------------- |
| `#1e40af`                                                 | blue-800       | Primary data, headline KPI, emphasised element                  |
| `#1d4ed8`                                                 | blue-700       | Category label + emphasis (family names, section headers)       |
| `#2563eb` / `#3b82f6` / `#60a5fa` / `#93c5fd` / `#dbeafe` | blue-600 → 100 | Sequential gradient (5-tone) for ordered categories             |
| `#eff6ff`                                                 | blue-50        | Category background (Comparison / principled sections)          |

### Semantic accents (used sparingly, one per role)

| Hex                               | Tailwind                    | Role(s)                                                                                                   |
| --------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------- |
| `#b91c1c`                         | red-700                     | Critique callouts (numbered circles), REJECTED badge, target / reference lines                            |
| `#fee2e2`                         | red-100                     | Rejection-callout background box                                                                          |
| `#15803d`                         | green-700                   | APPROVED badge (paired with red rejection)                                                                |
| `#7c2d12`                         | orange-900 ("burgundy")     | Additional dark accent for a second critique tone                                                         |
| `#b45309`                         | amber-700                   | (a) Composition chart family label; (b) footer-takeaway strip color at bottom of many figures            |
| `#d97706` / `#f59e0b` / `#fbbf24` | amber-600 → 400             | Composition-family data gradient                                                                          |
| `#fef3c7`                         | amber-50 ("warning yellow") | (a) Composition-family background; (b) warning / caution callout box background                           |

### Semantic discipline

Color carries meaning; role depends on figure context.

- **Blue family** = correct / principled / primary emphasis
- **Red** = rejection / critique / must-fix / target-line (never decorative)
- **Green** = approval / correction shipped
- **Amber** = triple-duty. Composition chart family in an abstract Chart-family figure; warning callout in any chapter; footer-takeaway strip at the bottom of many figures. Surrounding context disambiguates.
- **Burgundy** = additional dark accent when a second critique tone is needed
- **Grays** = defaults, muted, neutral scaffolding

## Composition idioms

Four structural idioms that recur across chapters. Each has a fixed shape.

### 1. BEFORE/AFTER paired panels

Used to show a correction, a decluttering, or a rework. The AFTER panel earns the argument; the BEFORE panel sets the failure state.

- Side-by-side, BEFORE left, AFTER right
- Each panel: same width and height, `stroke="#d1d5db"` (gray-300) border, rounded `rx="4"`
- BEFORE panel background: `#f3f4f6` (gray-100)
- AFTER panel background: `#f9fafb` (gray-50) or `#eff6ff` (blue-50)
- Top-right of BEFORE: `<rect fill="#b91c1c" rx="3">` 80×20 with white "REJECTED" text 12pt/700
- Top-right of AFTER: `<rect fill="#15803d" rx="3">` same shape with white "APPROVED" text
- Panel title 13pt/700 + italic subtitle 12pt underneath

Skeleton:

```xml
<!-- BEFORE panel -->
<rect x="20" y="60" width="290" height="380" fill="#f3f4f6" stroke="#d1d5db" rx="4"/>
<rect x="230" y="68" width="80" height="20" fill="#b91c1c" rx="3"/>
<text x="270" y="83" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">REJECTED</text>
<text x="32" y="90" font-size="13" font-weight="700" fill="#1f2937">Before</text>
<text x="32" y="106" font-size="12" font-style="italic" fill="#6b7280">what the reader is asked to diagnose</text>
<!-- ... panel content ... -->

<!-- AFTER panel -->
<rect x="330" y="60" width="290" height="380" fill="#f9fafb" stroke="#d1d5db" rx="4"/>
<rect x="540" y="68" width="80" height="20" fill="#15803d" rx="3"/>
<text x="580" y="83" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">APPROVED</text>
<text x="342" y="90" font-size="13" font-weight="700" fill="#1f2937">After</text>
<text x="342" y="106" font-size="12" font-style="italic" fill="#6b7280">how the argument reads once the fixes land</text>
```

### 2. Numbered critique callouts

Used to walk the reader through a sequence of defects in a single flawed artifact. Each number matches a paragraph in the chapter body.

- Red-700 circle radius 10, top-right of each sub-panel or callout region
- White bold number 12pt/700 centered inside
- Sequential numbering 1, 2, 3, 4 matches the prose walkthrough
- Prose in the chapter body references the number, not the visual position

Skeleton:

```xml
<circle cx="580" cy="120" r="10" fill="#b91c1c"/>
<text x="580" y="124" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">1</text>
```

Place the circle at the top-right of the region being called out. If two numbers land close together, prefer diagonal spacing (1 at top-right, 2 at bottom-left of the same region) over overlapping.

### 3. Family-band abstract figures

Used to compare 5 related concepts (chart families, decision moves, verification steps) side-by-side. Each band gets its own accent color matched to the family it represents.

- 5 vertical panels side-by-side, each ~115px wide
- Panel border: 1.5px in family accent color (blue-700, amber-700, purple-700, green-700, red-700)
- Panel background: matching 50-tone (blue-50, amber-50, purple-50, green-50, red-50)
- Category label at top: 12pt/700 in family accent
- Italic question quote: 12pt italic in gray-500 ("Which is larger?", "What share?")
- Canonical example chart at 60-80px tall
- Four label blocks below: "Default failure:", "Cousins:", "Use for:" — each 12pt/700 label then 12pt gray-500 body

Compact skeleton for one band:

```xml
<rect x="20" y="80" width="115" height="360" fill="#eff6ff" stroke="#1d4ed8" stroke-width="1.5" rx="4"/>
<text x="30" y="102" font-size="12" font-weight="700" fill="#1d4ed8">COMPARISON</text>
<text x="30" y="120" font-size="12" font-style="italic" fill="#6b7280">"Which is larger?"</text>
<!-- ... 60-80px example chart ... -->
<text x="30" y="240" font-size="12" font-weight="700" fill="#1f2937">Default failure:</text>
<text x="30" y="256" font-size="12" fill="#6b7280">...</text>
```

### 4. 5-Visual Rule dashboards

Used for dashboard-shaped figures. From dashboard-design literature (Wexler / Shaffer / Cotgreave *Big Book of Dashboards*): 5 or fewer visuals per dashboard, with an obvious visual hierarchy.

- ≤5 visuals per dashboard
- One dominant KPI (largest single visual, top-left, blue-800 emphasis)
- Position → size → color hierarchy (readers scan top-left to bottom-right; big elements before small; bright before muted)
- **Blurred-thumbnail test**: shrink the figure to thumbnail size and apply Gaussian blur. The dominant KPI should still be identifiable. If the blur destroys the hierarchy, position or size is wrong.
- **Mobile-preserved hierarchy**: mentally re-flow the dashboard as a single column. The reading order should still make sense.

## Anti-patterns

| Don't                                                          | Why                                                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Introduce new hues outside the palette above                   | Consistency across chapters is the reader's cross-reference tool                       |
| Use red for anything except critique / rejection / target-line | Red carries the "must-fix" signal; decorative red would degrade the signal             |
| Use amber outside Composition-family / warning / takeaway      | Amber signals family membership or warning throughout; other uses confuse              |
| Add drop-shadows, gradients, or decorative flourishes          | Publication-appropriate = restraint; the argument does the work, not the graphics      |
| Ship a figure without the italic subtitle                      | The subtitle carries the one-line takeaway that binds the figure to the argument       |
| Substitute the font stack                                      | Inter is intentional (open-source, wide numerals, ships on companion sites' CSS)       |
| Shrink text below 12px to fit more in                          | The instructional floor exists for the reader; going below it fails them silently      |
| Use `data-print-role="micro"` on instructional content         | The taxonomy is not an escape hatch; instructional means the reader has to read it     |
| Ship an anti-pattern figure below the floor                    | The gate cannot distinguish deliberate from accidental illegibility                    |
| Skip the deuteranopia check on red/green pairings              | Roughly 8% of male readers see them the same; color + shape or color + label survive |

## Related skills

- [`chart-big-idea`](../chart-big-idea/SKILL.md) — Step 0.5 earn-a-figure gate + Step 4.5 focus discipline. The framing side of the same discipline.
- [`flint-chart`](../flint-chart/SKILL.md) § Publication config preset — pins the Vega-Lite `config` block that emits statistical charts obeying this style guide.
- [`render-verify`](../render-verify/SKILL.md) § Prose-coupling check — verifies the surrounding prose after the figure ships.
- [`figure-generator`](../figure-generator/SKILL.md) — the engineering discipline that emits SVGs conforming to this guide (`.mjs` generators, `data-sha256` audit hash, contract tests).
- `markdown-mermaid` — sibling for Mermaid-authored diagrams (different rendering model, shares palette discipline where colors carry meaning).

## Would revise if

The floor formula, palette, or composition idioms have failed if any of the following occur within 90 days:

- A figure shipped through this skill's discipline fails a print-legibility audit that this skill was supposed to prevent
- Adopters report the semantic-palette rules are ambiguous ≥3 times in a quarter (color role unclear)
- The `data-print-role="note"` auto-promote rule (≥40 chars) misses a class of content it should catch
- The 5-Visual Rule dashboard blurred-thumbnail test is skipped ≥3 times because the tooling is too heavy

Track outcomes at [`operations/ledgers/curation-log.md`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/operations/ledgers/curation-log.md) in Alex_ACT_Steward.

Adapted from *The Defensible Decision* (Fabio Correa) via the `dd-book-illustrator` skill in Alex_DDA. The floor math, palette semantics, and composition idioms are book-tested across 53 shipped figures and 368 pages.
