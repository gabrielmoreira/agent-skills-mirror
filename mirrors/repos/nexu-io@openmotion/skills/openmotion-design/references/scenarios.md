# Design Studio Scenarios

Call `openmotion_design_catalog` with `action="list_scenarios"` to read the full scenario task profile for any scenario below, and `action="list_templates"` / `action="list_skills"` filtered by `scenario` to inspect starter templates and skills.

## Prototype

Deliver an interactive, responsive HTML web or app prototype rooted at `index.html`.
- Keep layout usable at Desktop (fluid), Tablet (`820×1180`) and Mobile (`390×844`).
- Render charts as real SVG/Canvas graphics, design real interactive states (hover, active, empty, loading, form feedback), and keep dynamic data separate from markup.

## Mobile app

Deliver a mobile-first interactive HTML prototype rooted at `index.html` designed for a `390×844` phone viewport with touch-friendly hit targets, bottom tab/navigation bars, safe-area spacing and realistic interactive screen flows.

## Slide deck

Deliver a single-file 1920×1080 (`16:9`) HTML presentation that speaks the Open Design / Design Studio deck host protocol:
- Mark each slide with `.slide` (with `.slide.active` on the visible slide) and optional `data-screen-label`.
- Listen for `window.addEventListener('message', ...)` receiving `{ type: 'od:slide', action: 'next' | 'prev' | 'first' | 'last' | 'go', index? }`.
- Post `{ type: 'od:deck-ready', capabilities: ['absolute-navigation', 'state-events'] }` on load and `{ type: 'od:slide-state', active, count, protocolVersion: 1 }` whenever the slide changes.
- Support keyboard navigation (Arrow keys, PageUp/PageDown, Home/End) and `@media print` with one 1920×1080 page per slide.
- Store speaker notes in `<script type="application/json" id="speaker-notes">["...", ...]</script>` or `<aside class="notes">...</aside>` inside each slide.

## Document

Deliver print-ready semantic HTML (`<article>`, clear heading levels, 65–80ch reading measure, horizontally scrollable tables on mobile, and `@media print` pagination with repeating `thead`). Export to PDF via `openmotion_design_project` (`action="export"`, `format="pdf"`).

## Website clone

Inspect user-supplied URLs, screenshots or files first—never fabricate an unseen page from memory. Rebuild layout, typography, colors and responsive breakpoints as editable portable HTML; clearly mark non-functional mock forms/actions and never wrap the target site in an iframe.

## Live artifact

Store structured JSON in `data.json` alongside `index.html` (and optional `provenance.json`). Fetch `./data.json` at load time using escaped DOM updates (`textContent`, never raw `innerHTML`). Keep credentials and raw provider headers out of project files.

## WebGL

Use `canvas.getContext('webgl2')` with a readable fallback message if unavailable, cap `devicePixelRatio` at `2`, handle resize cleanly, and pause `requestAnimationFrame` when `document.hidden` is true.
