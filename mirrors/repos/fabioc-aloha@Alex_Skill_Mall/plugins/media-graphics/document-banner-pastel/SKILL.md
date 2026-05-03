---
type: skill
lifecycle: stable
inheritance: inheritable
name: document-banner-pastel
description: Hand-authored pastel SVG banners for documentation — 1200×240 with content-specific iconography, complementary to algorithmic banner muscles
tier: extended
applyTo: '**/*document*,**/*banner*,**/*pastel*'
currency: 2026-04-29
lastReviewed: 2026-04-30
---

# Document Banner — Pastel Pattern


> Hand-authored pastel banners that match each document's content. Complement to [`alex-banner-generation`](../../../../Alex_ACT_Edition/.github/skills/alex-banner-generation/SKILL.md) (which is algorithmic, dark-slate, 1200×300, fixed watermarks).

## When to Use

| Use this pattern | Use the algorithmic muscle instead |
|---|---|
| Document needs unique content-specific iconography | Banner is purely structural (PLAN/CHANGELOG/RELEASE) |
| Pastel light theme matches the deliverable's audience (branding, education, healthcare, design) | Identity-stamping technical artifact in the Alex/ACT brand |
| Diagram on the right reinforces the document's mental model | One of the six fixed watermarks fits cleanly |
| You want the banner to age with the doc | Banner should never drift from the muscle's brand constants |

The two patterns coexist; pick by document role, not by aesthetic preference.

## Visual Skeleton

| Region | Spec |
|---|---|
| Canvas | 1200 × 240 viewBox |
| Background | 2- or 3-stop diagonal `<linearGradient>` x1=0 y1=0 x2=1 y2=1 |
| Bottom stripe | `<rect>` at `x=0 y=232 w=1200 h=8`, gradient or solid |
| Kicker (line 1) | `font-size=22 font-weight=500 letter-spacing=6` uppercased label, accent color |
| Headline (line 2) | `font-size=56 font-weight=700`, slate-800 `#1f2937` |
| Subhead (line 3) | `font-size=22 font-weight=400`, gray-600 `#4b5563` |
| Iconography | `<g transform="translate(870..950, 55)" opacity="0.95">` — content-specific |

Text font: `system-ui, -apple-system, Segoe UI, sans-serif`. Add `role="img"` and `aria-label="..."` to the root `<svg>` for accessibility.

## Pastel Palette (matches Mermaid palette convention)

Pick one of three accent tracks to match document tone. Each track ships a kicker color, a stripe color, and a 2- or 3-stop background gradient. All track text remains slate-800 `#1f2937`.

| Track | Tone | Kicker | Stripe | Background gradient |
|---|---|---|---|---|
| Purple | Strategic / identity / brand | `#6d28d9` | `#c4b5fd` | `#ede9fe` → `#fce7f3` (or 3-stop with `#dbeafe` at 100%) |
| Blue | Planning / synthesis / analytical | `#1d4ed8` | `#a78bfa` or `#93c5fd` | `#dbeafe` → `#ede9fe` (or 3-stop with `#d1fae5` at 100%) |
| Pink | Generative / questions / discovery | `#be185d` | `#f9a8d4` | `#fce7f3` → `#f3f4f6` |

A single 3-stop "rainbow" variant (`#fce7f3 → #ede9fe → #dbeafe`) is reserved for top-level READMEs that need to telegraph all three tracks at once.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 240" role="img" aria-label="DOCUMENT_NAME banner">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ede9fe"/>
      <stop offset="100%" stop-color="#fce7f3"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="240" fill="url(#bg)"/>
  <rect x="0" y="232" width="1200" height="8" fill="#c4b5fd"/>
  <g font-family="system-ui, -apple-system, Segoe UI, sans-serif" fill="#1f2937">
    <text x="60" y="80"  font-size="22" font-weight="500" letter-spacing="6" fill="#6d28d9">KICKER LABEL</text>
    <text x="60" y="148" font-size="56" font-weight="700">Document Headline</text>
    <text x="60" y="195" font-size="22" font-weight="400" fill="#4b5563">One-line subtitle that captures intent</text>
  </g>
  <!-- Iconography group: translate to (870..950, 55), opacity 0.95 -->
  <g transform="translate(940,55)" opacity="0.95">
    <!-- Pick an iconography variant from the table below -->
  </g>
</svg>
```

## Iconography Variants

Each variant fits inside a ~280×180 box anchored by the right-side `<g transform>`. Pick the one whose mental model matches the document.

### A — Tracks (timeline of options)

Use when the document presents N parallel paths or phases, optionally with a milestone.

```xml
<circle cx="60"  cy="60" r="34" fill="#bfdbfe" stroke="#93c5fd" stroke-width="2"/>
<text   x="60"  y="66" font-size="14" font-weight="700" text-anchor="middle">T1</text>
<text   x="60"  y="115" font-size="11" text-anchor="middle" fill="#4b5563">Path A</text>
<circle cx="160" cy="60" r="34" fill="#ddd6fe" stroke="#a78bfa" stroke-width="2"/>
<text   x="160" y="66" font-size="14" font-weight="700" text-anchor="middle">T2</text>
<circle cx="260" cy="60" r="34" fill="#a7f3d0" stroke="#34d399" stroke-width="2"/>
<text   x="260" y="66" font-size="14" font-weight="700" text-anchor="middle">T3</text>
<line x1="94"  y1="60" x2="126" y2="60" stroke="#9ca3af" stroke-width="2"/>
<line x1="194" y1="60" x2="226" y2="60" stroke="#9ca3af" stroke-width="2"/>
<!-- optional milestone marker -->
<circle cx="160" cy="155" r="6" fill="#fcd34d" stroke="#a16207" stroke-width="2"/>
<line x1="160" y1="94" x2="160" y2="149" stroke="#9ca3af" stroke-width="2" stroke-dasharray="3,3"/>
<text x="160" y="178" font-size="10" font-weight="600" text-anchor="middle" fill="#4b5563">Milestone · Date</text>
```

### B — Hub-and-spokes (one core, N audiences)

Use when the doc is about a central thing radiating to several stakeholders.

```xml
<circle cx="80"  cy="80"  r="40" fill="#ddd6fe" stroke="#a78bfa" stroke-width="2"/>
<text   x="80"  y="68"  font-size="11" font-weight="700" text-anchor="middle" fill="#6d28d9">CORE</text>
<text   x="80"  y="86"  font-size="13" font-weight="700" text-anchor="middle">LABEL</text>
<circle cx="180" cy="40"  r="22" fill="#bfdbfe" stroke="#93c5fd" stroke-width="2"/>
<text   x="180" y="44"  font-size="10" font-weight="700" text-anchor="middle">A</text>
<circle cx="220" cy="100" r="22" fill="#fbcfe8" stroke="#f9a8d4" stroke-width="2"/>
<text   x="220" y="104" font-size="10" font-weight="700" text-anchor="middle">B</text>
<circle cx="180" cy="160" r="22" fill="#a7f3d0" stroke="#6ee7b7" stroke-width="2"/>
<text   x="180" y="164" font-size="10" font-weight="700" text-anchor="middle">C</text>
<line x1="115" y1="65"  x2="160" y2="48"  stroke="#9ca3af" stroke-width="2"/>
<line x1="118" y1="92"  x2="200" y2="100" stroke="#9ca3af" stroke-width="2"/>
<line x1="115" y1="100" x2="162" y2="148" stroke="#9ca3af" stroke-width="2"/>
```

### C — Document mockup (form-like content)

Use when the doc is itself a structured artifact: branding plan, RFP, checklist, template.

```xml
<rect x="20" y="30"  width="240" height="40" rx="6" fill="#ffffff" stroke="#a78bfa" stroke-width="2"/>
<line x1="35" y1="50" x2="245" y2="50" stroke="#c4b5fd" stroke-width="2"/>
<text x="35" y="46" font-size="11" font-weight="700" fill="#6d28d9">SECTION A</text>
<rect x="20" y="80"  width="240" height="40" rx="6" fill="#ffffff" stroke="#a78bfa" stroke-width="2"/>
<line x1="35" y1="100" x2="220" y2="100" stroke="#c4b5fd" stroke-width="2"/>
<line x1="35" y1="110" x2="200" y2="110" stroke="#c4b5fd" stroke-width="2"/>
<text x="35" y="96" font-size="11" font-weight="700" fill="#6d28d9">SECTION B</text>
<rect x="20" y="130" width="240" height="40" rx="6" fill="#ffffff" stroke="#a78bfa" stroke-width="2"/>
<circle cx="40" cy="150" r="6" fill="#c4b5fd"/>
<circle cx="58" cy="150" r="6" fill="#c4b5fd"/>
<circle cx="76" cy="150" r="6" fill="#c4b5fd"/>
<text x="100" y="154" font-size="11" font-weight="700" fill="#6d28d9">SECTION C</text>
```

### D — Concept badge (single dominant idea)

Use when the doc resolves to one positioning claim or thesis.

```xml
<circle cx="100" cy="100" r="60" fill="#ddd6fe" stroke="#a78bfa" stroke-width="3"/>
<text x="100" y="92"  font-size="14" font-weight="700" text-anchor="middle">CLAIM</text>
<text x="100" y="110" font-size="14" font-weight="700" text-anchor="middle">LINE 2</text>
<text x="100" y="128" font-size="10" font-weight="500" text-anchor="middle" fill="#4b5563">tag · tag · tag</text>
```

### E — Symbol focus (open-ended prompt)

Use when the doc is a question set, brainstorm, or research kickoff.

```xml
<text x="100" y="120" font-size="120" font-weight="700" text-anchor="middle" fill="#f9a8d4">?</text>
<circle cx="40"  cy="50"  r="6" fill="#fbcfe8" stroke="#f9a8d4" stroke-width="2"/>
<circle cx="180" cy="50"  r="6" fill="#fbcfe8" stroke="#f9a8d4" stroke-width="2"/>
<circle cx="60"  cy="170" r="6" fill="#fbcfe8" stroke="#f9a8d4" stroke-width="2"/>
<circle cx="170" cy="170" r="6" fill="#fbcfe8" stroke="#f9a8d4" stroke-width="2"/>
```

## Embedding in Markdown

```markdown
# Document Title

![](banners/document-name.svg)

Body content...
```

Use empty alt text `![]` (not `![Banner]`) so pandoc's `markdown→docx` reader doesn't emit the alt text as a figure caption when the doc gets exported. The aria-label on the SVG itself preserves accessibility.

## Procedure

1. **Choose the variant** — match the document's mental model to A/B/C/D/E above
2. **Choose the track** — purple/blue/pink based on tone
3. **Copy the template** + iconography variant into `banners/<doc-slug>.svg` next to the doc
4. **Fill the kicker** (uppercase, ≤ 20 chars), **headline** (≤ 32 chars to fit at 56px), **subhead** (≤ 80 chars)
5. **Customize the iconography** — replace placeholder labels with content-specific text
6. **Embed** with `![](banners/<slug>.svg)` under the doc's H1

## Anti-patterns

| Anti-pattern | Why it breaks |
|---|---|
| Embedding with `![Banner](...)` alt text | pandoc exports the alt as a figure caption in the docx |
| Mixing pastel banners with `alex-banner-generation` dark-slate banners in the same doc | Two visual systems compete; pick one per doc |
| Inventing new accent colors per banner | Loses the three-track recognition cue across the docset |
| Banner > 240px tall | Crowds the document's first paragraph; 240 is the cap |
| Saturated brand colors (`#0078d4`, `#d97706`, `#166534`) | Breaks the pastel system; if you want a brand color, use `alex-banner-generation` instead |

## Falsifiability

This pattern fails if, after 30 days of use, < 50% of new branded docs reuse one of variants A–E. That would mean each banner is reinvented from scratch and the variant table is decorative. Mitigation: track variant adoption in a heir's session memory; if reuse < 50%, the variant set is wrong (not specific enough, or doesn't match real document types).

## Related

- [`alex-banner-generation`](../../../../Alex_ACT_Edition/.github/skills/alex-banner-generation/SKILL.md) — algorithmic dark-slate variant for technical artifacts
- [`svg-graphics`](../svg-graphics/SKILL.md) — generic SVG cookbook (animation, clipPath, dark/light mode)
- [`graphic-design`](../graphic-design/SKILL.md) — broader design system patterns
