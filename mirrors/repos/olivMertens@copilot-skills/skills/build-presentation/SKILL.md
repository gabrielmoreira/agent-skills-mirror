---
name: build-presentation
description: >-
  Create or restyle brand-aware HTML and editable PowerPoint presentations
  with coherent palettes, icon systems, rounded diagrams, clear typography,
  and staged reveals. Use for "create a presentation", "HTML presentation",
  "PowerPoint deck", "HTML to PowerPoint", "crée une présentation",
  "présentation HTML puis PowerPoint", or /build-presentation.
  Reuse the style for any topic. An explicit template or different style
  takes precedence. Not for websites or social video.
---

# Build Presentation

Create a diagram-led HTML deck, an editable PowerPoint deck, or both.
This package is self-contained for its instructions, design reference and
HTML starter. PowerPoint generation requires separate compatible tooling.

## Procedure

Resolve all paths from **the directory containing this SKILL.md**, not the
current working directory or a particular user's home.

1. Read [the workflow](references/workflow.md).
2. Read [the design system](references/design-system.md).
3. For HTML, adapt [the standalone starter](assets/starter.html).
4. For HTML-to-PowerPoint work, read
   [the conversion guide](references/html-to-pptx.md). Use an installed `pptx`
   skill, a native PowerPoint canvas, or another available editable-PPTX tool.
   Discover capabilities before relying on them; do not assume a machine path.
   **Always save the `.pptx` in the same folder as the source `.html`, reusing
   the HTML base name** (`deck.html` → `deck.pptx`). Never emit the deck to a
   separate build, dist, temp or working directory.

If the user asks for HTML then PowerPoint, review the HTML with them before
rebuilding the approved version as native PowerPoint objects.

- Resolve the identity before authoring: target brand or brand-neutral mode,
  authoritative brand source, dominant color role, and icon policy. Derive
  these only from user-approved assets, an authoritative template, or explicit
  values. If any decision is missing, ambiguous, conflicting, or would require
  guessing colors from a logo or discovering an intended client, ask one
  concise grouped question before choosing a palette or visual assets.
- Once identity is resolved, choose individual icons from the approved policy
  according to their semantic meaning; do not ask the user to select every
  glyph. Keep each icon category coherent while allowing approved brand marks,
  official product icons and generic concept icons to coexist deliberately.
- If the user explicitly requests a brand-neutral result, or delegates the
  visual choice and no authoritative identity is available, use the packaged
  white/blue/amber Build identity and generic Lucide-style outline icons.
  Treat this as an explicit fallback, not as an inferred client identity.
- When an approved brand kit is supplied, preserve the deck's layout grammar
  while applying the brand logo, semantic color roles and licensed typefaces.
  Never invent, redraw, recolor or distort a logo. If the kit is incomplete,
  ask for the missing identity decisions; use Build defaults for unspecified
  elements only after the user accepts that fallback.
- Reuse design, not old product claims or client content.
- Preserve the requested language exactly. In French, keep every accent,
  cedilla and ligature in source and rendered output; never transliterate
  words such as « accès », « capacité », « décision » or « cœur » to ASCII.
- Use one coherent icon family. Prefer Lucide-style outline icons for generic
  concepts, official product icons for named Microsoft/Azure services, and
  user-approved assets for brands. Never use emoji as presentation icons.

## Icon systems

The skill supports three icon categories, each with clear sourcing and sourcing rules:

**Lucide icons (generic concepts)** — ISC license, free, 5000+ outline glyphs
- Source: <https://lucide.dev>
- Quick reference: [lucide-icons-reference.md](references/lucide-icons-reference.md) — 30+ common icons with copy-ready SVG paths
- Use for: Database, Server, Workflow, Bot, MessageSquare, ShieldCheck, KeyRound, FileSearch, History, UserCheck, etc.
- How to add: Visit lucide.dev, copy the SVG path, embed inline with `class="icon"` and `aria-hidden="true"` (if decorative)
- Offline-first: No CDN needed; embed SVG paths directly in HTML
- See [design-system.md](references/design-system.md) and [workflow.md](references/workflow.md) for detailed examples and list

**Official vendor icons** — Microsoft, Azure, Google Cloud, AWS, Apple, etc.
- Verify current provenance and permitted use before adding
- Microsoft/Azure: <https://learn.microsoft.com/en-us/azure/architecture/icons/>
- Google Cloud: <https://cloud.google.com/architecture/icons>
- AWS: <https://aws.amazon.com/architecture/icons/>
- Apple: Official app store or design resources
- Do NOT confuse with generic glyphs; use official icons for named products only

**Brand marks** — Logos and approved company/product assets
- Use only supplied or explicitly approved by user
- Preserve aspect ratio, exclusion zone, and original colors
- Never recolor, redraw, or add a generic symbol variant
- Keep essential content readable without motion and in print.
- Use generic examples unless the user provides approved source material.
- If PowerPoint tooling is unavailable, report the missing prerequisite.
  Do not pass off HTML, PDF or whole-slide images as editable PowerPoint.
- Do not install software, upload, publish or send files without the applicable
  user approval. Creating a local artifact does not authorize publication.

See [README.md](README.md) for installation and example prompts.
