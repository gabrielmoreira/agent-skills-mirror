# Build Presentation Design System

## Reference and scope

Visual reference: the published eight-slide **Agentic Platform** deck at
<https://ozgurkarahan.com/agentic-platform/>.

Use its diagram-led composition. Its white slides and blue/amber accents form
the packaged brand-neutral fallback, not an identity to impose on every deck.
The website homepage uses a different palette and is not the style reference.
No local source checkout is required; this document and the bundled specimen
provide the reusable design rules.

The reference supplies composition, not factual authority. Its product names,
status badges, metrics and dates must not be copied as current claims.

## Palette

Resolve the identity brief before selecting this palette. When a target brand
is known, use its authoritative semantic colors instead. When the brand,
client, dominant color or authoritative source is unknown or ambiguous, ask
the user rather than sampling a logo, searching for likely colors or carrying
forward another client's identity. Use this table only when the user requests
a neutral deck, or when no authoritative identity exists and the user delegates
the choice or approves it as fallback.

| Token | Hex | Role |
|---|---|---|
| `paper` | `#FFFFFF` | Slide surface |
| `bg` | `#EDF1F7` | Outer surround |
| `ink` | `#16202F` | Main text |
| `muted` | `#53617A` | Accessible secondary text on white and tinted surfaces |
| `line` | `#E2E8F2` | Decorative separators, not meaningful boundaries alone |
| `azure` | `#0F6CBD` | Main emphasis, diagram icons, current step |
| `azure-soft` | `#EAF3FC` | Selected/response card fill |
| `azure-line` | `#BBD7F0` | Blue card borders |
| `amber` | `#A64B00` | Contrast, selected emphasis, governance label |
| `amber-soft` | `#FFF4E4` | Highlight/governance fill |
| `amber-line` | `#F0C078` | Highlight frame |
| `success` | `#1F7A55` | Confirmed or realized status text |
| `success-soft` | `#EFFAF5` | Confirmed or realized status fill |
| `success-line` | `#A8D7C3` | Confirmed or realized status frame |
| `sand` | `#9FB4D0` | Original dashed boundary color |
| `node` | `#F7F9FC` | Neutral cards |
| `shadow-soft` | `#16202F1A` | Slide elevation shadow |
| `shadow-float` | `#16202F2E` | Floating control or notes shadow |

Blue is the main accent, not the background. Amber should explain a distinction,
not decorate every card. For meaningful dashed boundaries, use a darker stroke
such as `muted` and an explicit label; pale source borders alone do not
meet non-text contrast needs. Never rely on color alone for status.

The viewer may be dark (`#0B1020`), as in the published deck; the **slides stay
white**. The neutral specimen uses the light surround for simpler print parity.

## Typography and density

| Role | Preferred family | Reference behavior | Reusable target at 1280 px width |
|---|---|---|---|
| Headline | Bricolage Grotesque, 800 | Tight, expressive, `-.02em` tracking | 40-48 px |
| Card/stage title | Bricolage Grotesque, 600 | Compact strong hierarchy | 24-28 px |
| Body | Instrument Sans, 400/500/600 | Left-aligned, line height 1.35-1.5 | 22-24 px |
| Eyebrow/step | IBM Plex Mono, 400/500 | Uppercase, `.1em`-`.22em` tracking | 16-18 px |
| Source/footer | IBM Plex Mono | Small consistent metadata | 14-16 px, no essential argument here |

Fallbacks: `Trebuchet MS`/`Segoe UI` for headings, `Segoe UI`/Arial for body,
Consolas for mono. Fallbacks make the specimen usable offline; they do not
establish exact-font fidelity. Final delivery should package appropriately
licensed fonts or clearly identify an approved substitution.

Do not repeat the source deck's very small `.58cqw`-`.9cqw` labels for essential
content. Shorten copy, split the slide or move details into notes. Avoid more
than four response cards on a projected slide. A card usually contains a title
and one short sentence. A main headline should wrap at most twice.

## Canvas and geometry

- 16:9; author/test at **1280 x 720 CSS px**.
- Source `.slide-inner` uses top/right/bottom/left padding
  `3cqw 4cqw 2cqw 4cqw`: 38.4 / 51.2 / 25.6 / 51.2 px at the reference width.
- Use 1.1-1.6cqw gaps (about 14-20 px); expand when copy or projection needs it.
- Cards have 10-12 px radii; shared governance frames about 14 px.
- Thin 1-1.6 px decorative borders; no large drop shadows inside every card.
- Viewer chrome and page shadow belong outside the exported slide.
- Size the stage against **both** viewport width and height. `100vw` alone
  clips slides in short windows.
- Scope `cqw` to each slide (`container-type: inline-size`). Position descendants
  inside it; do not accidentally resolve typography against the browser width.

## Diagram grammar

Use small inline outline SVGs: nominal 24 x 24 viewBox, stroke width 1.6-1.8,
round caps and joins. Make purely decorative icons `aria-hidden`; give a real
diagram its own text description. Prefer native shapes for large geometry.

### Icon hierarchy

Resolve the icon policy with the identity brief, then let semantics determine
the individual glyphs. Keep one visual grammar within a deck:

1. **Generic concepts:** use Lucide or an equivalent Lucide-style outline set.
  Useful mappings include `Database`/`Server` for a system of record,
  `Workflow` for orchestration, `Bot` for an agent, `MessageSquare` for a
  channel, `PlugZap` for an adapter, `ShieldCheck` for governance, `KeyRound`
  for access, `FileSearch` for evidence, `History` for audit and `UserCheck`
  for human validation.
  
  **How to add Lucide icons to your HTML deck:**
  - Source: <https://lucide.dev> (ISC license, free for any use)
  - Quick reference: See [lucide-icons-reference.md](lucide-icons-reference.md) for 30+ common icons with SVG paths
  - Each icon has a 24×24 viewBox with stroke paths
  - Copy the SVG path data and embed as inline `<svg>` with `class="icon"`
  - Stroke width is controlled by CSS: `--icon { stroke-width: 1.7; }`
  - Example: `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 20 0"/></svg>`
  - Do NOT use a CDN; embed SVG paths inline for offline-first delivery
  
2. **Named vendor products:** use the current official vendor icon and verify
  its provenance and permitted use. For example, Azure Container Apps,
  Microsoft Foundry, Azure AI Search and Microsoft 365 use current official
  Microsoft architecture icons rather than generic glyphs.
  
  **Vendor icon sources** (verify current provenance):
  - Microsoft/Azure: <https://learn.microsoft.com/en-us/azure/architecture/icons/>
  - Google Cloud: <https://cloud.google.com/architecture/icons>
  - AWS: <https://aws.amazon.com/architecture/icons/>
  - Apple: Official App Store connect assets
  - Others: Vendor-supplied icon/logo kits (always verify usage rights)
  
3. **Brands:** use only supplied or approved logo assets and preserve their
  aspect ratio, exclusion zone and colors.
4. **Controls:** use familiar arrow, home, fullscreen, print and notes symbols;
  retain an accessible name and add text or a tooltip when needed.

Do not use emoji as icons. Keep generic concept icons in one family; approved
brand marks and official vendor icons are deliberate exceptions and should not
be redrawn to imitate that family. Avoid generic AI sparkles unless the concept
is literally generation; for agents, show the actor or workflow role instead.
Icons support scanning, but the adjacent label carries the meaning.

**Accessibility reminder:** All purely decorative icons must have `aria-hidden="true"`.
Meaningful diagrams should have an accessible name (e.g., `<svg ... title="Database server">`).

### Brand identity override

An approved brand kit overrides the default blue/amber palette and typefaces,
but not the deck's accessibility, spacing or diagram discipline. Define brand
colors as semantic tokens such as `brand-primary`, `brand-accent`, `surface`,
`text` and `text-muted`; do not scatter raw values through slide rules. Keep a
light and dark logo variant when the kit provides both, and choose the variant
from the actual background rather than adding an improvised badge behind it.

The logo identifies the presentation; it is not a decorative icon. Prefer one
consistent placement on the title, closing slide or master/footer. Preserve its
aspect ratio, clear space and minimum size, and never recolor, crop, stretch,
outline or reconstruct it. If the brand palette fails contrast requirements,
keep the brand color for large accents and use an accessible approved text tone.

Do not confuse visual research with authorization. A logo found in the project
may establish an available asset, but it does not by itself establish the
target client, dominant color, complete palette or permission to recolor the
deck. Ask when those decisions are not explicit. If the user authorizes palette
extraction from artwork, present the sampled values as a proposal and obtain
approval before applying them throughout the deck.

| Motif | Meaning |
|---|---|
| Rounded neutral card | Actor, stage or capability |
| Primary-tinted card | Current focus or concrete response |
| Accent frame with a label | Shared policy, constraint, governance or chosen contrast |
| Dashed labeled container | Execution or responsibility boundary |
| Short pill | Status, category or lifecycle step; always text-labeled |
| Connector/arrow | Actual direction, dependency or handoff |
| Outcome bar | One consequence or next step, not another paragraph |

Align connector endpoints with the intended cards. Do not run lines through
labels. Where a boundary matters, put its label and contents inside it.

## Layout recipes

### A. Shift + concept map

Top left: eyebrow and a two-part headline ("From ..." / "To ...").
Use a muted old state and a bold brand-primary new state; an accent
strike-through is optional, never the only indication of which state is old.

Under it, use an audience row, a clearly labeled shared boundary containing
two delivery lanes, then a shared-capabilities row. End with one takeaway.
Describe concepts before product names.

### B. Same map, real implementation

Duplicate A's coordinates, reading order and grouping. Replace concept labels
with verified components. The audience should recognize the structure instantly.
Do not redraw the whole architecture simply because names appeared.
Reserve identical header, diagram and footer slots across the pair so a shorter
title cannot shift the map vertically. The specimen's paired headers reserve
9cqw; compare the corresponding card rectangles after changing text.

### C. Lifecycle with responsibility

Three main stages with compact numbered labels and connectors. Give a complex
middle stage more width if needed; do not flatten everything into equal boxes.
Put shared constraints in one encompassing labeled band. Add a clearly labeled
feedback path only where the system actually has one.

### D. Focused lifecycle overview

Show the whole lifecycle, emphasizing the one or two stages the talk is about.
Other stages remain legible but quieter. An optional brand-accent feedback step
must have text explaining the distinction. No "new", "GA" or "already solved"
status without evidence and an as-of date.

### E. Problem -> response -> outcome

Small problem card on the left, clear bridge, larger response area on the right.
Use a 2 x 2 response grid at most; keep any current lifecycle step in a compact
stepper. End with a wide outcome bar. This is the specimen's zoom slide.

### F. Capability boundary

One large dashed runtime/container with an explicit boundary label; small
capability cards inside. One brand-accent exception/identity card is enough.
Do not imply included services, security guarantees or pricing from placement.

### G. Resources and decision

Two or three resource groups with real, descriptive links and one final action.
No non-clickable `<a>` elements. Keep private prep sources out of public slides.

## Motion and static state

Use motion to explain reading order:

1. Eyebrow/headline.
2. Main diagram or problem.
3. Supporting cards in order.
4. Shared frame/outcome.

Typical entrance duration: 400-800 ms. Stagger neighboring cards by 150-300 ms.
Small upward motion (about 6-12 px) or restrained pop is sufficient. Prefer
finishing a simple slide's entrance within 2-3 seconds; the original 6-second
build is not mandatory.

Do not animate every word, auto-advance slides, or add continuous drift.
Unnecessary infinite pulse markers are omitted. Essential labels exist in the
static DOM and no-JavaScript output.

## Language fidelity

Presentation typography includes orthography. Keep source files and generated
artifacts in Unicode and preserve the requested language exactly. For French,
retain accents, cedillas, ligatures and accented capitals in headings, labels,
notes and controls: « accès », « capacité », « façade », « décision », « cœur »,
« ÉTAPE », « À VALIDER ». Never output `acces`, `capacite`, `facade`, `decision`
or `coeur` as a workaround for encoding or font problems.

Use French punctuation conventions when they fit the medium: quotation marks
« … » and non-breaking spaces before `:`, `;`, `?` and `!`. Confirm that the
chosen fonts contain the required glyphs in HTML and PowerPoint. A fallback
font is preferable to missing glyphs or stripped accents.

Provide a static mode. For `prefers-reduced-motion: reduce` and print,
remove animation/delays and set final opacity/transform explicitly. A
completed screenshot is not evidence that animated playback works.

## PowerPoint mapping

Use a native wide slide: **13.333333 x 7.5 inches**.

| Quantity | Conversion from reference HTML |
|---|---|
| Position/size in inches | CSS px / 96 |
| Position/size in EMU | CSS px * 9525 |
| Font size in points | CSS px * 0.75 |
| 1cqw at 1280 px | 12.8 px = 0.133333 in = 9.6 pt for text |
| Left/right inset | 51.2 px = 0.533333 in |
| Top inset | 38.4 px = 0.4 in |
| 44 px headline | 33 pt |
| 24 px body | 18 pt |
| 16 px metadata | 12 pt |

These conversions assume the slide is measured at its **unscaled reference
size**, not after a viewer transform. If the canvas reports other units, inspect
its schema and convert once; never apply both conversions.

Map CSS cards to native roundrects, pills to roundrects (not stretched ellipses),
text to real runs and connectors to native connectors. Set text margins
explicitly. Check line wrapping, family names, bold weights and theme shadows.
Use native tables/charts for data instead of screenshotting them.

Keep the same component positions and semantic grouping as HTML. A simple
native Fade/Appear is a valid equivalent to a CSS reveal; springs, animated
border draws and pseudo-elements need a deliberate approximation.
If timing is extracted from HTML, capture it before disabling animations.

Follow the installed PowerPoint tool's authoring/validation guidance and the
bundled `references\html-to-pptx.md`. Resolve these bundled paths from the
directory containing `SKILL.md`. Do not assume a universal HTML exporter.

## Specimen and review expectations

`assets\starter.html` contains neutral concept, implementation, lifecycle and
zoom examples. It is a reusable building block, not a source-backed final talk.
Replace its example labels, footers and references when authoring.

The specimen has no external assets, telemetry or application dependencies.
It uses local-font aliases and fallbacks. Opening it does not fetch any public
website or private wiki content.

A final deck should retain this grammar while being simpler than the source
where readability requires it. Inspect the rendered output rather than treating
a valid HTML or PPTX file as evidence of visual quality.
