# Export to PDF & speaker notes

## Speaker notes

Every deck gets a `<deck-name>-notes.md` file (both scaffolds create one). It is **not
projected** — it holds the narrative, outline, and per-slide talking points. Keep it next
to the deck so notes and slides stay in sync. Never put notes on the slides themselves;
slides are for the audience, notes are for the presenter.

## Exporting slides to PDF

A PDF is useful for sharing the deck after the talk or printing handouts. The export is
**image-based** (one picture per slide, no selectable text) — the goal is a faithful,
content-complete capture of what the audience sees, not a text document.

Because the deck is interactive, a correct export must do two things, and the bundled
script handles both:

1. **Wait for content to render** before capturing each slide (network settle + a pause
   so entrance animations finish) — never screenshot a half-drawn slide.
2. **Reveal click-hidden content.** Anything gated behind a click or an entrance
   animation (step reveals, Framer Motion fade-ins) is forced visible before the shot, so
   it appears in the PDF without anyone clicking through it.

### Option A — bundled script (recommended; works for both tracks)

```bash
pip install playwright pillow && playwright install chromium

# React deck: start the dev server first, then point at its URL
python scripts/export-deck-pdf.py http://localhost:5173 -o my-deck-slides.pdf

# HTML deck: point at the file
python scripts/export-deck-pdf.py path/to/index.html -o my-deck-slides.pdf
```

It walks every slide via the deck's dot strip (each dot has an aria-label `Slide N` on the
scaffolds, or a `title` like `Đến Slide N` on older decks), injects CSS to neutralize
animation timing and un-hide opacity/visibility-hidden content, waits `--wait` seconds
(default 1.5, enough for Framer Motion stagger) per slide, and screenshots the fixed
`#stage` (HTML) or the viewport (React) at 1920×1080.

**What it covers automatically:** reveals done with opacity/visibility/entrance animations
— the common case when you build step reveals as recommended in the design system. Add a
`data-reveal` attribute to anything custom and it gets forced visible too.

**What it does NOT cover:** reveals that only a real click can trigger because they swap
state — flip cards, "run simulation" buttons, growing counters, checklist ticking. There
is no generic way to know those; you have to drive them per slide. For that, adapt the
proven per-slide pattern (see below) rather than fighting the generic script.

### Bespoke per-slide capture (for click-driven reveals)

When slides hide content behind real interactions, write a short capture script that, for
each slide: navigates (click the dot), performs the slide's interactions
(`page.click(...)`, wait), and screenshots — taking two shots (before/after) where it
helps. This is exactly how the author's existing exporters work; use them as templates:

- `AI14/day1-presentation/capture_slides.py` — Playwright + Pillow + reportlab. Clicks
  dots, flips `.perspective-1000` cards, clicks "Chạy"/"Thêm", ticks checklist rows, and
  captures before/after per interactive slide with generous waits (1.5–10s).
- `presentations/bmad-presentation/export-pdf.js` — Playwright + pdf-lib. Reads the slide
  count from the `1/X` counter, hides the nav, and uses `page.pdf({width:'1920px',
  height:'1080px'})` per slide (this variant keeps **vector text**, not just an image),
  advancing with ArrowRight and waiting 1.5s for animations.

The bundled `export-deck-pdf.py` is the zero-config default for standard decks; reach for
the per-slide pattern only when a deck has click-gated state.

### Option B — Browser print (works for both tracks, zero deps)

1. Open the deck in Chrome (the running dev server for React, or the file for HTML).
2. Add a temporary print stylesheet that shows every slide stacked, one per page, at the
   1920×1080 aspect, and disables the nav bar. For the plain-HTML template, override
   `.slide { display:flex !important; position:relative; page-break-after:always; }` and
   hide `#nav`. For React, render all slides instead of just the current one behind a
   `?print` flag.
3. File → Print → Save as PDF, paper size **Landscape**, margins **None**, background
   graphics **on**.

Quick and dependency-free, but fiddly because each track needs a print mode.

### Option B — decktape (good for self-contained HTML decks)

```bash
npx decktape generic --key=ArrowRight <url-or-file> <deck-name>-slides.pdf
```

`decktape` drives the deck in a headless browser, pressing the next key and capturing each
slide. The `generic` profile fits these custom decks. Point it at the dev-server URL
(React) or a `file://` path / local server (HTML).

### Option C — Playwright screenshot loop (most control)

If you have Playwright (this environment has a Playwright MCP), script it: load the deck,
then for each slide press `ArrowRight`, wait for the transition, and screenshot the stage
at 1920×1080. Combine the PNGs into a PDF (e.g. `img2pdf` or a short script). Use this
when print/decktape mishandle animations or custom scaling.

## Naming

Save exports as `<deck-name>-slides.pdf` alongside the deck (matching the existing
convention of exported PDFs living near their source deck).
