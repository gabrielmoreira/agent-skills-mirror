---
type: skill
lifecycle: stable
inheritance: inheritable
name: alex-banner-generation
description: Generate branded SVG banners for documents (READMEs, plans, changelogs, release artifacts) using a configurable Node.js muscle. Covers watermark selection, subtitle craft, and embedding. Requires the generate-banner.cjs muscle from Alex_ACT_Edition.
tier: extended
applyTo: '**/*alex*,**/*banner*,**/*generation*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Alex Banner Generation

Generate visually consistent SVG banners for any document using the Alex — ACT Edition brand template.

## When to Use

- User asks for a banner, header image, or document decoration
- Creating a significant new document (README, PLAN, ROADMAP, CHANGELOG)
- User mentions adding a "header" or "branded image" to a doc

> **Looking for a lighter, hand-authored variant?** See `document-banner-pastel` — pastel 1200×240 banners with content-specific iconography. Use that for branding, education, or audience-facing docs; use this muscle for technical artifacts that need brand-stamped consistency.

## Prerequisites

This skill requires the `generate-banner.cjs` muscle from Alex_ACT_Edition at `.github/muscles/generate-banner.cjs`. The muscle handles SVG rendering; this skill handles the judgment calls (watermark selection, subtitle quality, placement).

## Brand Constants

| Element | Value |
| ------- | ----- |
| Dimensions | 1200 × 300 px |
| Background | `#0f172a` (Slate 900) |
| Accent bar | 4px wide, `#6366f1` (Indigo 500) |
| Series label | `ALEX · ACT EDITION` |
| Title | 56px / weight 700 / `#f1f5f9` |
| Subtitle | 18px / weight 600 / `#94a3b8` |
| Watermark | ~100px / weight 800 / `#f1f5f9` / 10% opacity |

## Watermark Categories

Pick the one that matches the document's role:

| Watermark | Use For |
| --------- | ------- |
| `ACT` | Critical-thinking content, ACT framework artifacts, manifestos |
| `EDITION` | Top-level repo identity (root README, ABOUT) |
| `DOCS` | User guides, tutorials, reference material |
| `RELEASE` | CHANGELOGs, release notes, version stamps |
| `PLAN` | Planning docs, roadmaps, milestone trackers |
| `NOTE` | Session notes, ad-hoc memos |

If no category fits, ask the user before inventing one — the muscle rejects unknown watermarks.

## Procedure

### Step 1 — Gather Inputs

Ask the user only for what's missing. Defaults:

- **Title** — the document's name. Keep ≤ 32 chars (the muscle enforces this).
- **Subtitle** — a single-line purpose statement, ≤ 80 chars. Lift it from the doc's first paragraph or its north-star sentence; don't invent.
- **Watermark** — pick from the table above based on doc role.
- **Filename** — defaults to `assets/banner-<title-slug>.svg`.

### Step 2 — Generate

```bash
node .github/muscles/generate-banner.cjs \
  --title "Document Title" \
  --subtitle "One-line purpose statement." \
  --watermark PLAN
```

| Flag | Purpose |
| ---- | ------- |
| `--force` | Overwrite an existing file |
| `--out path/to/banner.svg` | Non-default location |

Exit codes: 0 = success, 1 = validation error (length/watermark), 2 = filesystem error.

### Step 3 — Embed in the Document

Add this line just under the document's H1:

```markdown
![Banner](assets/banner-<slug>.svg)
```

The muscle prints the exact embed line; copy it verbatim.

## Subtitle Craft

The muscle takes whatever subtitle you pass — quality is your job. Good subtitles:

- State the document's **purpose**, not its contents ("Critical thinking made operational." not "This document explains ACT.")
- Are one clause, not a sentence list
- End with a period
- Avoid hype ("revolutionary", "ultimate") and meta language ("this document")
- Match the document's actual first paragraph — don't promise things the doc doesn't deliver

If uncertain, show two options to the user before generating.

## Validation Checklist

- [ ] File written under `assets/`
- [ ] Watermark matches the document's role
- [ ] Title ≤ 32 chars, subtitle ≤ 80 chars
- [ ] Embed line added under the document's H1
- [ ] Renders in VS Code preview without errors

## PNG Conversion (Optional)

GitHub renders SVG natively. If a downstream tool needs PNG:

```bash
npx svgexport assets/banner-foo.svg assets/banner-foo.png 1200:300
```

Don't ship PNGs unless required — they double asset weight and can drift from the SVG source.

## Boundaries

- The muscle never picks the watermark or writes the subtitle — that's skill judgment
- The muscle never edits source markdown — embedding is a separate step
- Custom colors/fonts/dimensions not supported — for non-template designs, generate raw SVG manually
