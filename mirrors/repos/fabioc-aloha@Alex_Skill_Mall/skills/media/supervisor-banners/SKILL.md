---
type: skill
lifecycle: stable
inheritance: inheritable
name: supervisor-banners
description: Dark-slate SVG banner family — 1200×320 hero + 1200×60 section dividers — for governance, curation, and audit-style documentation
tier: extended
applyTo: '**/assets/banner*,**/*supervisor*,**/*governance*,**/*decisions*,**/*adr*,**/*changelog*'
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# Supervisor Banners

> Two-piece dark-slate SVG banner family for documentation that needs a sense of governance, audit trail, or curation discipline. One 1200×320 hero banner per repo, plus 1200×60 section dividers that label and visually segment a multi-document folder (decisions/, audits/, ledgers/, ADRs/).

## When to Use

| Use this pattern | Use a different pattern |
| --- | --- |
| Documentation has clear sections (ADRs, ledgers, assessments, proposals) that benefit from visual labeling | Single-document deliverable that needs only a hero banner ([`document-banner-pastel`](../document-banner-pastel/SKILL.md)) |
| Tone is governance, curation, audit, oversight, fleet management | Tone is creative, marketing, branding, generative ([`document-banner-pastel`](../document-banner-pastel/SKILL.md)) |
| You want a cohesive dark-slate identity across a folder of docs | You want algorithmic generation with fixed brand watermarks ([`alex-banner-generation`](../alex-banner-generation/SKILL.md)) |
| Reference set lives in a single `assets/` folder for copy-paste reuse | Banner is generated dynamically from data |

The pattern is purpose-built for repos that act as **source-of-truth ledgers** — a Supervisor, a registry, an audit catalog, an ADR collection.

## The Family

A supervisor-banner set is **one hero + N section dividers**, all sharing the same background and corner-accent treatment.

| Asset | Size | Role |
| --- | --- | --- |
| `banner-readme.svg` | 1200 × 320 | Hero banner for the main README; carries the repo identity, mission tagline, stat badges, and value-prop cards |
| `banner-<section>.svg` | 1200 × 60 | Section divider; carries an icon, an uppercase label, a one-line subtitle, and a 3-dot accent |

The hero anchors the brand. The dividers carry the same DNA into each subsection so a reader scrolling through a `decisions/` folder feels the same hand throughout.

## Hero Banner — 1200 × 320

### Visual skeleton

| Region | Spec |
| --- | --- |
| Canvas | 1200 × 320 viewBox, rounded corners `rx="16"` |
| Background | Diagonal `<linearGradient id="bg">` from `#0f172a` (slate 900) → `#1e293b` (slate 800) → `#0f172a` |
| Subtle grid | Horizontal lines every 40px, vertical every 100px, `opacity="0.04"`, stroke = accent color |
| Corner accents | 4 corner brackets using accent gradient at `opacity="0.6"` (top) and `0.3` (bottom) |
| Icon group | `<g transform="translate(120, 160)">` — 90×90 icon centered at this anchor with optional `filter="url(#glow)"` |
| Title | x=230 y=105, font-size=48 weight=700 fill=`#f8fafc` (slate 50) |
| Tagline | x=230 y=143, font-size=20 weight=400 fill=`#94a3b8` (slate 400) |
| Accent stripe | 140×3 rect at x=230 y=158, fill=accent gradient, `opacity="0.8"` |
| Stat badges | 3 pill rects at y=180, each `36px` tall, `rx="18"`, dark fill `#1e293b` with `#334155` stroke |
| Bottom tagline | x=230 y=258, font-size=13 fill=`#64748b` (slate 500) |
| Value-prop cards | 5 staggered cards at translate(790, 35), each 38px tall with gradient-tinted backgrounds |
| Version pill | bottom-right, 100×24 rounded pill with monospace version stamp |

### Required `<defs>`

```xml
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%"   style="stop-color:#0f172a"/>
    <stop offset="50%"  style="stop-color:#1e293b"/>
    <stop offset="100%" style="stop-color:#0f172a"/>
  </linearGradient>
  <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   style="stop-color:#10b981"/>
    <stop offset="50%"  style="stop-color:#14b8a6"/>
    <stop offset="100%" style="stop-color:#06b6d4"/>
  </linearGradient>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
```

The `accent` gradient is the **single knob** that gives a repo its identity. Pick a 3-stop palette from the table below and the rest of the family inherits it.

## Section Divider — 1200 × 60

### Visual skeleton

| Region | Spec |
| --- | --- |
| Canvas | 1200 × 60 viewBox, rounded corners `rx="8"` |
| Background | Horizontal `<linearGradient>` from `#0f172a` → `#1e293b` |
| Bottom stripe | 1200×4 rect at y=56, fill=accent gradient, `opacity="0.6"` |
| Icon | 16×20 SVG icon at `transform="translate(30, 30)"`, fill=accent palette |
| Label | x=58 y=28, font-size=13 weight=700 fill=primary accent, `letter-spacing="2"`, uppercase |
| Subtitle | x=58 y=44, font-size=11 fill=`#64748b` (slate 500) |
| Accent dots | Right side at x=1170/1155/1143 y=30, radii 4/3/2, opacity 0.4/0.3/0.2 |

### Required `<defs>`

```xml
<defs>
  <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   style="stop-color:#0f172a"/>
    <stop offset="100%" style="stop-color:#1e293b"/>
  </linearGradient>
  <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%"   style="stop-color:#TRACK1"/>
    <stop offset="50%"  style="stop-color:#TRACK2"/>
    <stop offset="100%" style="stop-color:#TRACK3"/>
  </linearGradient>
</defs>
```

Each section gets its own `accent` gradient so a reader can tell at a glance which kind of document they're looking at.

## Accent Tracks (pick one per section)

All tracks share the same dark-slate background. The accent gradient is the only thing that changes.

| Track | Tone | Stop 1 | Stop 2 | Stop 3 | Suggested use |
| --- | --- | --- | --- | --- | --- |
| Emerald-teal | Governance, oversight, audit | `#10b981` | `#14b8a6` | `#06b6d4` | Hero banner; ADR sections |
| Indigo-purple | Audit trails, append-only ledgers | `#818cf8` | `#a78bfa` | `#c084fc` | Changelogs, curation logs |
| Amber-orange | Snapshots, point-in-time assessments | `#f59e0b` | `#f97316` | `#ef4444` | Inventories, compliance assessments, wish lists |
| Sky-blue | Proposals awaiting decision | `#38bdf8` | `#0ea5e9` | `#0284c7` | Proposals, RFCs, drafts |
| Forest-cyan | Architecture, design rationale | `#10b981` | `#14b8a6` | `#06b6d4` | Founding plans, design docs (overlaps emerald-teal by design) |
| Warm-red | Edition / heir template identity | `#f59e0b` | `#f97316` | `#ef4444` | When the family is for the Edition repo, not Supervisor |
| Cool-violet | Marketplace / catalog identity | `#38bdf8` | `#818cf8` | `#c084fc` | When the family is for the Mall repo |

Three accent tracks (warm-red, cool-violet, emerald-teal) form the **cross-repo identity convention**: a heir running Supervisor + Edition + Mall sees three distinct hero colors that map directly to the three repos. Tracks 1-5 in the same column are then used **inside** Supervisor's `decisions/` folder to label sub-sections.

## Icon Glyphs (for section dividers)

Each divider gets a 16×20 monogram. The glyphs below are illustrative; substitute any 16×20 SVG path that matches your section name.

| Section | Glyph hint | SVG primitive |
| --- | --- | --- |
| ADR / Decisions | Gavel | `<rect x="-8" y="-12" width="16" height="10" rx="3"/>` + `<rect x="-2" y="-2" width="4" height="16" rx="1"/>` |
| Ledger / Changelog | Lined list | `<rect x="-10" y="-12" width="20" height="24" rx="2" fill="none" stroke="..."/>` + 3 `<line>` rows |
| Assessment | Clipboard with check | `<rect x="-9" y="-10" width="18" height="22" rx="2"/>` + `<rect x="-4" y="-14" width="8" height="6" rx="1"/>` + checkmark `<path>` |
| Proposal | Folded document | `<path d="M-8,-12 L4,-12 L10,-6 L10,12 L-8,12 Z"/>` |
| Architecture | Blueprint cross | `<rect x="-10" y="-10" width="20" height="20" rx="2" fill="none"/>` + 2 crosshair lines + 2 corner dots + dashed diagonal |

Keep glyphs **monochromatic** in the accent palette — no fills bleeding in from outside the track.

## Hero Banner Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="1200" height="320"
     role="img" aria-label="REPO_NAME — TAGLINE">
  <title>REPO_NAME</title>
  <desc>TAGLINE</desc>
  <defs>
    <!-- bg, accent, glow filters here (see Required defs) -->
  </defs>

  <rect width="1200" height="320" rx="16" fill="url(#bg)"/>

  <!-- subtle grid (omitted for brevity) -->
  <!-- corner accents -->
  <!-- icon group at translate(120, 160) -->

  <text x="230" y="105" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="48" font-weight="700" fill="#f8fafc" letter-spacing="-1">REPO_NAME</text>

  <text x="230" y="143" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="20" fill="#94a3b8">REPO_TAGLINE</text>

  <rect x="230" y="158" width="140" height="3" rx="1.5" fill="url(#accent)" opacity="0.8"/>

  <g transform="translate(230, 180)">
    <!-- 3 stat badges, each 36px tall pill -->
  </g>

  <text x="230" y="258" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="13" fill="#64748b">SECONDARY_TAGLINE</text>

  <g transform="translate(790, 35)">
    <!-- 5 staggered value-prop cards -->
  </g>

  <rect x="1070" y="280" width="100" height="24" rx="12" fill="#1e293b" stroke="#334155"/>
  <text x="1120" y="296" font-family="Consolas, monospace" font-size="11"
        fill="#94a3b8" text-anchor="middle">vX.Y.Z</text>
</svg>
```

## Section Divider Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 60" width="1200" height="60"
     role="img" aria-label="SECTION_NAME">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   style="stop-color:#0f172a"/>
      <stop offset="100%" style="stop-color:#1e293b"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   style="stop-color:#TRACK1"/>
      <stop offset="50%"  style="stop-color:#TRACK2"/>
      <stop offset="100%" style="stop-color:#TRACK3"/>
    </linearGradient>
  </defs>

  <rect width="1200" height="60" rx="8" fill="url(#bg)"/>
  <rect x="0" y="56" width="1200" height="4" rx="2" fill="url(#accent)" opacity="0.6"/>

  <g transform="translate(30, 30)">
    <!-- 16x20 monogram glyph in accent palette -->
  </g>

  <text x="58" y="28" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="13" font-weight="700" fill="#TRACK1" letter-spacing="2">LABEL</text>
  <text x="58" y="44" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="11" fill="#64748b">One-line subtitle</text>

  <circle cx="1170" cy="30" r="4" fill="#TRACK1" opacity="0.4"/>
  <circle cx="1155" cy="30" r="3" fill="#TRACK2" opacity="0.3"/>
  <circle cx="1143" cy="30" r="2" fill="#TRACK3" opacity="0.2"/>
</svg>
```

## Reference Implementation

The pattern is exercised in `Alex_ACT_Supervisor/assets/`:

| File | Track | Used in |
| --- | --- | --- |
| `banner-readme.svg` | emerald-teal hero | `README.md` |
| `banner-architecture.svg` | emerald-teal divider | `decisions/PLAN.md` |
| `banner-adr.svg` | emerald-teal divider | `decisions/ADR-*.md` |
| `banner-ledgers.svg` | indigo-purple divider | `decisions/curation-log.md`, `edition-changelog.md`, `brain-qa-changelog.md` |
| `banner-assessments.svg` | amber-orange divider | `decisions/ACT-ASSESSMENT-*.md`, `supervisor-brain-inventory.md`, `wish-list.md` |
| `banner-proposals.svg` | sky-blue divider | `decisions/proposals/*.md` |

Copy the six files into your project's `assets/` folder and edit four things per banner: (1) the `accent` gradient stops, (2) the title text, (3) the stat badges or label, (4) the icon glyph.

## Anti-Patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Mixing pastel and dark-slate banners in the same folder | Visual whiplash — readers lose the brand thread |
| Using a different background color per section | The point of the family is one background and varying accents |
| Skipping the section dividers and using only the hero | Sections lose their visual labels; folder feels flat |
| Inlining the gradient stops instead of using `<defs>` | Breaks the single-knob principle; refactor cost grows linearly |
| Filling icon glyphs with non-accent colors | The accent gradient is the section's identity; outside colors leak |
| Adding 6+ section types | Readers stop distinguishing tracks; pick a 4-5 maximum |

## Falsifiability

This pattern is decorative if any of these turn out true within 60 days of adoption in a project:

- A reader can't identify which section a document belongs to from its banner alone (defeats the divider purpose)
- Banners need to be regenerated on every release (defeats the copy-and-edit reuse model — promote to algorithmic muscle instead)
- Two of the accent tracks become interchangeable in practice (collapse them or pick a sharper distinction)
- The hero banner is never opened standalone (drop the dimensions to 1200×120 and reclaim README real estate)

## Cross-References

- [`document-banner-pastel`](../document-banner-pastel/SKILL.md) — pastel hero banners for creative / brand contexts
- [`alex-banner-generation`](../alex-banner-generation/SKILL.md) — algorithmic banner muscle with fixed brand watermarks (Edition family)
- [`svg-graphics`](../svg-graphics/SKILL.md) — general-purpose SVG authoring guidance
- [`svg-dashboard-composition`](../svg-dashboard-composition/SKILL.md) — for composing multi-fragment SVG dashboards (different problem)
