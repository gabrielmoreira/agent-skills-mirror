---
name: "svg-banner"
description: "Generate 1200x320 SVG banners for READMEs, plans, notes, and release artifacts. Ships with a pluggable brand config: default is the Alex ACT brand (slate-900 background, emerald-teal-cyan accent, x-loop mark, ACT/EDITION/DOCS/RELEASE/PLAN/NOTE watermarks). Heirs override the config for their own brand. Use when a document needs a hero banner, a section header, or brand-stamped consistency at the top of a markdown file."
lastReviewed: 2026-07-29
---

# SVG Banner

Author 1200×320 SVG banners for the top of a markdown document. Generic template with a pluggable brand config; the default brand is Alex ACT.

Renamed on 2026-07-29 from `alex-banner-generation` — same design, same script, brand now lives in `.github/config/banner-brand.json` instead of hardcoded in the script.

## When to Use

- Adding a hero banner to a README, PLAN, ROADMAP, CHANGELOG, or release artifact
- A branded section header for a documentation site
- A visual identity stamp for a doc shared externally

> **Looking for a lighter, hand-authored variant?** The Mall ships [`document-banner-pastel`](https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/plugins/media-graphics/document-banner-pastel/SKILL.md) — pastel 1200×240 banners with content-specific iconography (tracks / hub-and-spokes / mockup / badge / symbol). Use that pattern for branding, education, or audience-facing docs; use this skill for technical artifacts that need brand-stamped consistency.

## The design (fixed across brands)

Every banner obeys this layout. Only the brand config (colors, mark, labels, watermarks) varies.

| Element     | Value                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| Dimensions  | 1200 × 320 px                                                                                                             |
| Layout      | Left brand label (row 1), accent bar, title (row 2), subtitle (row 3); ghost watermark bottom-right; mark image top-right |
| Font stack  | `Segoe UI, Helvetica, Arial, sans-serif` (system-first for banners so they render without web-font load)                  |
| Title       | 56 px / weight 700, upper-left column                                                                                     |
| Subtitle    | 18 px / weight 600, under title                                                                                           |
| Brand label | 15 px / weight 700 accent + 13 px / weight 600 muted sub-label                                                            |
| Watermark   | ~100 px / weight 800, 10% opacity, bottom-right                                                                           |
| Mark        | PNG (base64-embedded), ~170×170, top-right                                                                                |
| Accent bar  | 3 px gradient stroke under the brand label                                                                                |
| Left ribbon | 6 px vertical gradient stripe (`x=0`) matching accent                                                                     |

Title cap: **32 chars**. Subtitle cap: **80 chars**. Longer inputs are rejected by the script — reflow or abbreviate.

Related design grammar: the illustrator plugin's [`print-svg-style-guide`](https://github.com/fabioc-aloha/Alex_ACT_Illustrator_Plugin/blob/main/.github/skills/print-svg-style-guide/SKILL.md) covers print-quality figure typography, semantic palette, and composition idioms for book / report figures. Banners are screen-first and share the palette-semantic-role discipline but not the print-legibility gates.

## Brand configuration

Brand values live in `.github/config/banner-brand.json`. The script reads it on every run. If the file is absent, the script falls back to the built-in Alex ACT default (documented below).

Schema:

```json
{
  "brand": {
    "label": "ALEX",
    "subLabel": "ARTIFICIAL CRITICAL THINKING"
  },
  "colors": {
    "background": "#0f172a",
    "accent1": "#10b981",
    "accent2": "#14b8a6",
    "accent3": "#06b6d4",
    "title": "#f1f5f9",
    "subtitle": "#94a3b8",
    "brandLabel": "#10b981",
    "brandSubLabel": "#94a3b8",
    "watermark": "#f1f5f9"
  },
  "mark": {
    "path": ".github/skills/svg-banner/assets/mark-mono-emerald-256.png",
    "width": 170,
    "height": 170,
    "x": 970,
    "y": 42
  },
  "watermarks": ["ACT", "EDITION", "DOCS", "RELEASE", "PLAN", "NOTE"],
  "watermarkDescriptions": {
    "ACT": "Critical-thinking content, ACT framework artifacts, manifestos",
    "EDITION": "Top-level repo identity (root README, ABOUT)",
    "DOCS": "User guides, tutorials, reference material",
    "RELEASE": "CHANGELOGs, release notes, version stamps",
    "PLAN": "Planning docs, roadmaps, milestone trackers",
    "NOTE": "Session notes, ad-hoc memos"
  }
}
```

### Default: Alex ACT brand

Steward ships `.github/config/banner-brand.json` with the Alex ACT brand as the default. Heirs that inherit from Steward baseline without editing the config get Alex-branded banners out of the box, matching the historical behavior of the pre-2026-07-29 `alex-banner-generation` skill.

### Overriding for your own brand

Two paths:

**A — commit a project-specific config.** Edit `.github/config/banner-brand.json` in your workspace. The script reads it every run. Ship the file with the repo so every collaborator produces on-brand banners.

**B — one-off via `--brand-config`.** Pass `--brand-config path/to/other.json` on the command line. Useful for testing a redesign before committing it, or for a heir that runs multiple brands from the same tree.

Brand config rules:

- **Palette semantics carry**: `accent1/accent2/accent3` form a left-to-right gradient. Pick three colors from your brand's accent family in a natural progression (deep → medium → light, or cool → warm). Avoid a red/green pairing without a redundant cue (deuteranopia — see the plugin's `print-svg-style-guide` § Redundant encoding).
- **Watermark whitelist is the discipline signal**: pick 4-8 watermark categories that map to your project's document classes. Small vocabulary keeps banners readable across the repo; large vocabulary devolves into decoration.
- **Font stack**: leave `Segoe UI, Helvetica, Arial, sans-serif` unless your brand requires otherwise (currently not overridable — fork the script if you need a different family). System-first fonts render without a web-font fetch (fast, offline-safe).
- **Mark path**: relative to the repository root. PNG or JPG; SVG not currently supported (base64-embed of raster is simpler and self-contained in the output).

## Procedure

### Step 1 — Gather inputs

Ask the user only for what's missing. Defaults:

- **Title** — the document's name. Keep ≤ 32 chars (the script enforces this).
- **Subtitle** — a single-line purpose statement, ≤ 80 chars. Lift it from the doc's first paragraph or its north-star sentence; don't invent.
- **Watermark** — pick from the config's `watermarks[]` array based on the doc's role. The script rejects unknown watermarks.
- **Filename** — defaults to `assets/banner-<title-slug>.svg`. Override with `--out` if the user wants a specific path.

### Step 2 — Generate

```sh
node .github/skills/svg-banner/scripts/generate-banner.cjs \
  --title "Document Title" \
  --subtitle "One-line purpose statement." \
  --watermark PLAN
```

Add `--force` to overwrite an existing file. Add `--out path/to/banner.svg` for a non-default location. Add `--brand-config path/to/config.json` to use a non-default brand.

The script exits 0 on success, 1 on validation errors (length, watermark whitelist), 2 on filesystem errors (file exists without `--force`).

### Step 3 — Embed in the document

Add this line just under the document's H1:

```markdown
![Banner](assets/banner-<slug>.svg)
```

The script prints the exact embed line; copy it verbatim.

## Subtitle Craft (the LLM-judgment part)

The script takes whatever subtitle you pass — quality is your job. Good subtitles:

- State the document's **purpose**, not its contents (`"Critical thinking made operational."` not `"This document explains ACT."`)
- Are one clause, not a sentence list
- End with a period
- Avoid hype ("revolutionary", "ultimate") and meta language ("this document")
- Match the document's actual first paragraph — don't promise things the doc doesn't deliver

If you're not sure the subtitle is right, show two options to the user before generating.

The `big-idea` skill's Big Idea distillation is a strong upstream for subtitle authoring: the Big Idea of the doc IS the subtitle of its banner.

## Validation Checklist

Before declaring done:

- [ ] File written under `assets/`
- [ ] Watermark matches the document's role (not just convenient) and is in the brand config's whitelist
- [ ] Title ≤ 32 chars, subtitle ≤ 80 chars (else the script rejects)
- [ ] Embed line added under the document's H1
- [ ] Mark image renders in the top-right corner (correct path in brand config)
- [ ] Renders in VS Code preview without errors

## PNG Conversion (optional)

GitHub renders SVG banners natively in `README.md` and most surfaces, so SVG is preferred. If a downstream tool needs PNG:

```sh
# Via svgexport (npm i -g svgexport, or use npx):
npx svgexport assets/banner-foo.svg assets/banner-foo.png 1200:320
```

Do not ship PNGs unless required — they double the asset weight and can drift from the SVG source.

## Boundaries

- The script does not pick the watermark, write the subtitle, or design the brand — those are LLM / skill / brand-owner judgment calls.
- The script does not edit the source markdown — embedding the banner in the doc is a separate step.
- Layout, dimensions, and typography scale are fixed. If your project needs a different banner shape (taller, wider, split-column), fork the script rather than parametrizing the layout — the current shape is calibrated for readability at 1200×320.
- Brand config lives in `.github/config/banner-brand.json`. Any other location requires the `--brand-config` flag on every invocation.

## Falsifiability

Revisit this skill by **2026-10-29** (90 days) or sooner if any of the following fires:

- Banners shipped via this skill are aesthetically rejected by the user ≥3 times in a quarter
- The SVG pipeline renders incorrectly in >10% of target environments (GitHub, VS Code preview, browsers) over any 30-day window
- A heir configures a brand override and reports the config schema is too tight or too loose (missing fields they need, or fields they never use) ≥2 times in a quarter
- Users request customization the skill forbids (custom dimensions, layout, or typography) ≥3 times in a quarter — signal the "fork rather than parametrize" boundary is wrong
- The default Alex brand config drifts from the built-in fallback in the script (two sources of truth in disagreement) — one of them wins on the next audit

## Falsifiability

Revisit this skill by **2026-08-26** (90 days) or sooner if any of the following fires:

- Banners shipped via this skill are aesthetically rejected by the user ≥3 times in a quarter
- The SVG pipeline renders incorrectly in >10% of target environments (GitHub, VS Code preview, browsers) over any 30-day window
- The muscle adds new template categories without a corresponding entry being added to this skill within the same change
- Users request customization the skill forbids (custom colors/fonts/dimensions) ≥3 times in a quarter — signal the brand constants are too tight
