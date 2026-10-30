# Build Presentation

Use **`build-presentation`** when the user asks for a presentation in HTML or
PowerPoint, says "use my Build presentation style", "same style as the Build
deck", "presentation style Build", "comme ma présentation Build", or invokes
`/build-presentation`.

This is a reusable **presentation style**, not a Microsoft Build news-retrieval
skill. Reuse the visual grammar for any topic. An explicit customer template,
brand requirement, or different style requested by the user takes precedence.
Do not use it for a website, social video, or a manager BR one-pager.

## 1. Load the actual design reference

The selected composition reference is the **published eight-slide Agentic
Platform deck**: `https://ozgurkarahan.com/agentic-platform/`. Use its layout
grammar. Use its white/blue/amber identity only for an approved neutral fallback,
not when an authoritative brand identity has been resolved.

Resolve bundled files from the directory containing `SKILL.md`. This package
does not require a private wiki or the reference website's source repository.
The bundled design system and starter are sufficient to begin offline.
If a required bundled file is missing, report the incomplete installation
rather than silently substituting a generic presentation style.

Read these files before authoring:

1. `references\design-system.md`:
   colors, fonts, spacing, diagram grammar, motion and HTML-to-PPTX mapping.
2. `assets\starter.html` for HTML:
   a neutral, reusable specimen, not approved presentation content.
3. The active project's existing deck and instructions, when present.
4. For PowerPoint output, invoke **`pptx`** when the client exposes it, or use
   an available native PowerPoint canvas or editable-PPTX library. Discover
   the tool's actual capabilities and read its authoring/validation guides.
   Resolve any tool-specific paths from that tool's installation, never a
   hardcoded home directory. The third-party `pptx` skill is not bundled.
   If no compatible tooling is available, report that prerequisite instead
   of silently returning HTML or installing software without approval.

The published deck is a **style reference only**. Its dates, product names,
availability labels, performance numbers and promises are not current evidence.
Do not carry over "GA", "live today", customer names or Build 2026 footers.

## 2. Establish the brief and evidence

Resolve topic, audience, language, time slot, output (`html`, `pptx`, or both),
whether a supplied template must be preserved, and the visual-identity brief.
The identity brief has four explicit decisions:

1. target brand/client, or an explicit brand-neutral mode;
2. authoritative source: brand kit, template, logo files or exact guidelines;
3. dominant color and its semantic role, plus any required supporting colors;
4. icon policy: generic outline family, official product icons, approved custom
  set, or a deliberate combination with clear boundaries.

Do not silently infer these decisions from a repository name, a lone logo,
unverified web results, previous clients or the packaged specimen. Inspect
materials already supplied by the user or present in the active project, but
treat conflicting or incomplete evidence as unresolved. If resolving identity
would require discovering which brand/client is intended, extracting colors
from artwork, or choosing a dominant color without an authoritative source,
ask one concise grouped question before authoring or restyling slides. Include
only the unresolved items, using the relevant prompts below:

```text
[Marque] Quelle marque ou quel client le deck représente-t-il, ou reste-t-il neutre ?
[Source] Quelle charte, quel modèle ou quels actifs font foi ?
[Dominante] Quelle couleur doit dominer, ou dois-je proposer des rôles à valider ?
[Icônes] Existe-t-il une bibliothèque officielle, ou puis-je utiliser une famille contour générique ?
```

Ask only for missing decisions that materially affect the result. If the user
delegates choices within a supplied authoritative identity, choose within that
identity. Use the packaged Build identity with one Lucide-style outline family
only for explicitly brand-neutral output or when no authoritative identity is
available and the user accepts the fallback. A quick start may default to HTML,
16:9 and the user's language, but it must not invent a client identity. An
explicit PowerPoint request must produce an editable `.pptx`, not just HTML.

For branded output, collect or locate only the approved assets needed now:

- primary logo plus light/dark or monochrome variants when available;
- primary, secondary, accent, surface and text colors as exact values;
- licensed heading/body typefaces and approved fallbacks;
- logo exclusion-zone, minimum-size and prohibited-use rules;
- an existing presentation template when it is the authoritative source.

Treat those inputs as constraints, not inspiration. Map brand colors to semantic
roles, verify text and non-text contrast, preserve logo geometry and use the
logo sparingly on title, closing or master/footer surfaces. Do not derive a full
palette from a logo when exact colors are available. Do not approximate a
missing logo or download an unofficial copy. When only part of the kit is
provided, identify the gaps and ask whether to use the packaged Build defaults
for the unspecified roles. Do not extract or approximate missing colors from
the logo unless the user explicitly authorizes that method and accepts the
proposed values.

Treat language fidelity as part of correctness. Author HTML and PowerPoint text
in UTF-8/Unicode and preserve the orthography the audience expects. For French,
keep accents, cedillas, ligatures and accented capitals: `é`, `è`, `ê`, `à`,
`ù`, `ç`, `œ`, `É`, `À`, `Ç`. Use French quotation marks where appropriate
and non-breaking spacing before `:`, `;`, `?` and `!` when the output format
supports it. Never simplify visible French to ASCII (`acces`, `capacite`,
`coeur`) for implementation convenience. Before delivery, inspect titles,
labels, controls, notes and metadata for lost diacritics in every output format.

Use the user's supplied or explicitly authorized topic sources. For factual
claims, record the source and as-of date; check current first-party documentation
for availability, licensing, pricing or roadmap statements. Private content
and links do not belong in a public deck. Do not retrieve workplace material
when the task is only styling existing content.

Keep source notes separate from presentation copy. A presentation should not
accidentally disclose local paths, mailbox links, private account context or
credentials. Use synthetic examples where a demonstration is needed.

## 3. Design the storyline before filling boxes

Create a short slide plan with:

`slide | takeaway | layout | evidence | speaker note`

For a substantive new storyline, critically review the plan before
implementation and obtain the user's approval. If the host provides an
independent reviewer, use it when authorized; no named custom agent is required.
When HTML is requested before PowerPoint, obtain approval of the HTML version
before rebuilding it as native PowerPoint objects.

Use the reference's narrative progression where it fits:

1. **Shift:** a concise before/after statement that explains why the topic matters.
2. **Concept map:** explain the system in audience language before product names.
3. **Implementation map:** reuse the exact geometry and add the real components.
4. **Lifecycle:** show the flow and responsibility boundaries.
5. **Zoom:** problem -> concrete response -> observable outcome.
6. **Decision/resources:** leave one next step and a small set of usable links.

This is a menu, not a compulsory six-slide sequence. Do not force every topic
into an agent architecture. Keep one focal diagram and one takeaway per slide.
Put detail in speaker notes or an appendix rather than shrinking the type.

## 4. Preserve the resolved style across formats

- Keep the packaged white/blue/amber identity only for brand-neutral output or
  when the user explicitly accepts it as the fallback. Otherwise map the
  approved brand palette to the same semantic roles across every format.
- Use approved brand typefaces when supplied; otherwise use Bricolage Grotesque
  headings, Instrument Sans body and IBM Plex Mono labels as neutral fallbacks.
- Tracked uppercase eyebrows, assertive left-aligned headlines, generous margins.
- Rounded cards, thin line icons, pills, labeled dashed boundaries and
  lightly tinted frames that express relationships rather than decoration.
- Stable geometry between overview and zoom slides. Meaningful connectors,
  explicit labels and a small consistent footer.
- Staged reveals that follow the speaker's explanation, not continuous motion.

Use the numerical tokens and layout recipes in the design reference. Do not
replace the selected palette with generic gradients, dark-blue slides or the
default theme from another skill. Generic presentation-tool design suggestions
must not override this explicitly chosen style.

Choose icons by meaning and provenance:

- For generic actions and concepts, use a single Lucide-style outline family.
  Visit <https://lucide.dev> to browse all available glyphs (ISC license, free).
  **Quick reference:** See [lucide-icons-reference.md](lucide-icons-reference.md) for 30+ common icons with copy-ready SVG paths.
  Recommended mappings:
  - `Database` or `Server`: systems of record
  - `Workflow`: orchestration / process
  - `Bot`: agents or AI actors
  - `MessageSquare`: conversational channels
  - `ShieldCheck`: governance / security
  - `KeyRound`: access / authentication
  - `FileSearch`: search / discovery
  - `History`: audit / timeline
  - `UserCheck`: human review / validation
  - `Zap`: action / power
  - `TrendingUp`: growth / success
  - `AlertCircle`: warning / risk
  
  **To add a Lucide icon to your HTML slide:**
  1. Go to <https://lucide.dev> and find the icon name (e.g., "database")
  2. Click the icon to copy its SVG path data (or see [lucide-icons-reference.md](lucide-icons-reference.md))
  3. Embed as an inline `<svg>` element in your HTML with `class="icon"` and `aria-hidden="true"` (if decorative)
  4. Example:
     ```html
     <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
       <ellipse cx="12" cy="5" rx="9" ry="3"/>
       <path d="M3 5v14a9 3 0 0 0 18 0V5"/>
     </svg>
     ```
  5. The CSS class `.icon` already defines sizing, stroke width and color (`var(--azure)`)
  
- For any named product or cloud service, use its current official vendor icon
  rather than a generic cloud, database or AI glyph. Verify product identity,
  icon provenance and permitted use before adding it. Microsoft and Azure
  services use current official Microsoft architecture icons.
  - Microsoft/Azure: <https://learn.microsoft.com/en-us/azure/architecture/icons/>
  - Google Cloud: <https://cloud.google.com/architecture/icons>
  - AWS: <https://aws.amazon.com/architecture/icons/>
  - Apple: Official app store connect or design resources
  
- For a company, product or customer brand, use only an asset supplied or
  explicitly approved by the user. Do not imitate a logo with a generic symbol.
- Use familiar symbols for controls, such as arrows for previous/next and the
  standard fullscreen glyph. Add visible text or a tooltip when meaning may be
  ambiguous.
- Keep icons subordinate to the message. An icon never replaces an essential
  label, proves a claim, or carries status by color alone. Avoid emoji, mixed
  filled/outline families, decorative sparkles and repeated icons on every card.

Improve accessibility rather than copying reference defects: shorten long
entrances, remove unnecessary infinite pulses, use readable type and accessible
muted text, and keep all information available in static/reduced-motion output.
Color alone is never a status, boundary or availability label.

## 5. HTML output

Start from the bundled standalone specimen, or adapt the project's existing
viewer. Do not introduce React, a CDN or a build system merely to make slides.
Inline CSS/SVG and a small vanilla controller are sufficient. Keep any approved
images and fonts local; include font licenses when redistributing them.

The starter uses local-font lookups with named fallbacks and makes no network
requests. Exact-font fidelity still needs installed fonts or packaged licensed
font files. If fonts are substituted, disclose that before final approval.

Required behavior:

- Fit the 16:9 stage to both viewport dimensions without clipping.
- Provide real, labeled previous/next and slide-selection buttons.
- Support arrows, PageUp/PageDown, Home/End and hash links.
- Do not hijack typing, modified shortcuts or native button/link activation.
- Make focus visible and announce slide changes.
- Reveal on entry and provide a static/reduced-motion mode; never gate
  essential text on an animation finishing.
- With JavaScript disabled, show all slides. Print all slides in final state
  and omit viewer controls. Footnotes and actual links remain readable.
- If fullscreen is provided, request it only after a user action and surface
  unsupported/denied requests; it is not a prerequisite for presenting.

For sources, use compact references in the slide or speaker notes and a real
linked resources slide. Do not put a private preparation path in a public footer.

## 6. Native, editable PowerPoint output

The style skill owns the design; the installed `pptx` skill or native canvas
owns file manipulation. Do not modify the installed PowerPoint skill.

Use native text boxes, rounded rectangles, connectors and editable tables/charts
where applicable. A whole-slide screenshot is not an editable slide.
Small icons may be SVG or high-resolution images; group related components
logically and preserve reading order, accessible labels and speaker notes.

Use 16:9 geometry. The design reference maps a 1280 x 720 CSS-pixel slide to
13.333333 x 7.5 inches. Evaluate `cqw` at that fixed width before converting;
do not interpret responsive CSS units directly as points.

For HTML conversion, consult the bundled `references\html-to-pptx.md`:
capture entrance timing **before** freezing the DOM, extract final unscaled
geometry, rebuild native shapes, then validate. This is a reconstruction method, not a universal exporter.

Prefer simple native Appear/Fade builds. CSS spring effects, animated borders
and line draws do not necessarily have faithful native equivalents. If the
available tool cannot author or preserve a requested effect, deliver a readable
static equivalent and state the limitation. Never claim animation parity from
a static render. Only modify OOXML timing with schema validation afterwards.

Verify actual font family names and embedding rights. Avoid synthetic bold on
an already-bold installed face. Package/allow embedding only licensed fonts;
otherwise obtain approval for an explicit substitute. Do not promise
pixel-identical HTML and PowerPoint without comparing both rendered outputs.

## 7. Inspect, fix, and hand off

For HTML, inspect every slide at 1280 x 720 and 1920 x 1080, plus a smaller
viewport. Exercise keyboard/button navigation, hash bounds, static mode,
reduced motion, no-JavaScript and print output. Check overflow, reading order,
focus, contrast, links, assets, browser errors and language fidelity. For French,
explicitly scan visible copy and speaker notes for missing accents or cedillas.

For PowerPoint, render and inspect every slide, extract the text, check
editability and inspect the real presentation's layout. Follow the selected
PowerPoint tool's validation procedure and use an independent visual reviewer
when available and authorized. Validate after any package/XML
edits and check animation behavior in a capable viewer when animations matter.

Fix defects and re-inspect the affected output. Source-backed wording and
privacy are separate from visual quality: both must hold.

Deliver the actual artifact path and a short explanation of how to open it,
plus any genuine limitations (for example, font substitution or static builds).
Never commit, publish, deploy, email or upload a presentation just because it
renders. Follow the user's explicit delivery boundary.
