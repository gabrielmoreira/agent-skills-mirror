---
name: sketch
description: "Generates 2-3 disposable, stance-different HTML mockup variants for side-by-side UI exploration before production. Use when the user wants to sketch a screen, compare layouts, or see takes before building. Not for polished one-off artifacts (claude-design), diagrams (excalidraw), or locked designs that should just be implemented."
version: 1.0.1
author: Hermes Agent (adapted from gsd-build/get-shit-done)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [sketch, mockup, design, ui, prototype, html, variants, exploration, wireframe, comparison]
    related_skills: [spike, claude-design, popular-web-designs, excalidraw]
---

# Sketch

Throwaway HTML mockups: 2-3 design variants to compare side-by-side before committing to production code. The point is exploration through comparison, not shippable artifacts.

## When to Use

- User wants to **see a design direction before committing** to one
- User says things like "sketch this screen", "show me what X could look like", "compare layout A vs B", "give me 2-3 takes on this UI", "let me see some variants", "mockup this before I build"
- User is exploring a UI/UX idea and needs visual comparison of different design stances

### When NOT to use

- User wants a production component — use `claude-design` or build it properly
- User wants a polished one-off HTML artifact (landing page, deck) — use `claude-design`
- User wants a diagram — use `excalidraw` or `architecture-diagram`
- The design is already locked — just build it

### If the user has the full GSD system installed

If `gsd-sketch` shows up as a sibling skill (installed via `npx get-shit-done-cc --hermes`), prefer **`gsd-sketch`** for the full workflow: persistent `.planning/sketches/` with MANIFEST, frontier mode analysis, consistency audits across past sketches, and integration with the rest of GSD. This skill is the lightweight standalone version — one-off sketching without the state machinery.

## Prerequisites

- A browser available on the host for visual verification
- Python 3 or Node.js/npx available if serving HTML via HTTP (recommended over `file://`)
- On Windows (primary host), PowerShell is the default shell — use `Start-Process` to open files in browser

## Procedure

The core method is:

```
intake  →  variants  →  head-to-head  →  pick winner (or iterate)
```

### Step 1 — Intake (skip if the user already gave you enough)

Before generating variants, get three things — **one question at a time**, not all at once:

1. **Feel.** "What should this feel like? Adjectives, emotions, a vibe." — *"calm, editorial, like Linear"* tells you more than *"minimal"*.
2. **References.** "What apps, sites, or products capture the feel you're imagining?" — actual references beat abstract descriptions.
3. **Core action.** "What's the single most important thing a user does on this screen?" — the variants should all serve this well; if they don't, they're just decoration.

Reflect each answer briefly before the next question. If the user already gave you all three upfront, skip straight to variants.

### Step 2 — Generate 2-3 variants (never 1, rarely 4+)

Produce **2-3 variants** in one go. Each variant is a complete, standalone HTML file. Don't describe variants — build them. The point is comparison.

Each variant should take a **different design stance**, not different pixel values. Good variant axes:

- **Density:** compact / airy / ultra-dense (pick two contrasting poles)
- **Emphasis:** content-first / action-first / tool-first
- **Aesthetic:** editorial / utilitarian / playful
- **Layout:** single-column / sidebar / split-pane
- **Grounding:** card-based / bare-content / document-style

Pick one axis and pull apart from it. Two variants that differ only in accent color are wasted effort — the user can't distinguish them.

**Variant naming:** describe the stance, not the number.

```
sketches/
├── 001-calm-editorial/
│   ├── index.html
│   └── README.md
├── 001-utilitarian-dense/
│   ├── index.html
│   └── README.md
└── 001-playful-split/
    ├── index.html
    └── README.md
```

### Step 3 — Build real, self-contained HTML

Each variant is a **single self-contained HTML file**:

- Inline `<style>` — no build step, no external CSS
- System fonts or one Google Font via `<link>`
- Tailwind via CDN (`<script src="https://cdn.tailwindcss.com"></script>`) is fine
- Realistic fake content — actual sentences, actual names, not "Lorem ipsum"
- **Interactive**: links clickable, hovers real, at least one state transition (open/close, filter, toggle). A frozen static image is a worse spike than a sloppy animated one.

**Default CSS reset + system font stack** for fast starts:

```html
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1a1a1a;
    background: #fafafa;
    line-height: 1.5;
  }
</style>
```

### Step 4 — Verify each variant visually

Open each variant in a browser. If it looks broken, fix it before showing the user.

**Use browser tools to verify rendering.** Don't just write HTML and hope it renders; load each variant and look at it:

```
browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
browser_vision(question="Does this layout look clean and readable? Any visible bugs (overlapping text, unstyled elements, broken images)?")
```

`browser_vision` returns an AI description of what's actually on the page plus a screenshot path — catches layout bugs that pure source inspection misses (e.g. a font import that silently failed, a flex container that collapsed). Fix and re-navigate until each variant looks right.

**On Windows (PowerShell)**, to open a variant manually:

```powershell
Start-Process "sketches\001-calm-editorial\index.html"
```

On macOS: `open sketches/001-calm-editorial/index.html`
On Linux: `xdg-open sketches/001-calm-editorial/index.html`

### Step 5 — Write a variant README

Each variant's `README.md` answers:

```markdown
## Variant: {stance name}

### Design stance
One sentence on the principle driving this variant.

### Key choices
- Layout: ...
- Typography: ...
- Color: ...
- Interaction: ...

### Trade-offs
- Strong at: ...
- Weak at: ...

### Best for
- The kind of user or use case this variant actually serves
```

### Step 6 — Present head-to-head comparison

After all variants are built, present them as a comparison. Don't just list — **opinionate**:

```markdown
## Three takes on the home screen

| Dimension | Calm editorial | Utilitarian dense | Playful split |
|-----------|----------------|-------------------|---------------|
| Density   | Low            | High              | Medium        |
| Primary action visibility | Low | High | Medium |
| Scan-ability | High | Medium | Low |
| Feel | Calm, trusted | Sharp, tool-like | Inviting, energetic |

**My take:** Utilitarian dense for power users, calm editorial for content-forward audiences. Playful split is weakest — tries to do both and commits to neither.
```

Let the user pick a winner, or combine two into a hybrid, or ask for another round.

### Step 7 — Output location

- Create `sketches/` (or `.planning/sketches/` if the user is using GSD conventions) in the repo root
- One subdir per variant: `NNN-stance-name/index.html` + `README.md`
- Keep variants disposable — a sketch that you felt the need to preserve should be promoted into real project code, not curated as an asset

**Typical tool sequence for one variant (Windows PowerShell):**

```powershell
New-Item -ItemType Directory -Force -Path "sketches\001-calm-editorial"
# write_file("sketches/001-calm-editorial/index.html", "<!doctype html>...")
# write_file("sketches/001-calm-editorial/README.md", "## Variant: Calm editorial\n...")
# browser_navigate(url="file:///$(pwd)/sketches/001-calm-editorial/index.html")
# browser_vision(question="How does this look? Any obvious layout issues?")
```

Repeat for each variant, then present the comparison table.

## Theming (when the project has a visual identity)

If the user has an existing theme (colors, fonts, tokens), put shared tokens in `sketches/themes/tokens.css` and `@import` them in each variant. Keep tokens minimal:

```css
/* sketches/themes/tokens.css */
:root {
  --color-bg: #fafafa;
  --color-fg: #1a1a1a;
  --color-accent: #0066ff;
  --color-muted: #666;
  --radius: 8px;
  --font-display: "Inter", sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

Don't over-tokenize a throwaway sketch — three colors and one font is usually enough.

## Interactivity bar

A sketch is interactive enough when the user can:

1. **Click a primary action** and something visible happens (state change, modal, toast, navigation feint)
2. **See one meaningful state transition** (filter a list, toggle a mode, open/close a panel)
3. **Hover recognizable affordances** (buttons, rows, tabs)

More than that is over-engineering a throwaway. Less than that is a screenshot.

## Frontier mode (picking what to sketch next)

If sketches already exist and the user says "what should I sketch next?":

- **Consistency gaps** — two winning variants from different sketches made independent choices that haven't been composed together yet
- **Unsketched screens** — referenced but never explored
- **State coverage** — happy path sketched, but not empty / loading / error / 1000-items
- **Responsive gaps** — validated at one viewport; does it hold at mobile / ultrawide?
- **Interaction patterns** — static layouts exist; transitions, drag, scroll behavior don't

Propose 2-4 named candidates. Let the user pick.

## Pitfalls

### Dark industrial is NOT the default for creative/3D projects

If the project involves 3D graphics, art generation, animation, or any visually-driven domain — do NOT default to dark technical palettes (deep navy, monospace, grid lines, glowing teal). Instead lean warm and alive: soft gradients, organic shapes, generous white space, vibrant accent colors, bouncy spring transitions. If the user says "this should look like art" or "pixar style", abandon any industrial template immediately.

### `nth-child(even/odd)` is fragile for alternating section backgrounds

Sections inside a shared `<main>` sibling often have different classes interspersed — `:nth-child(2)` may not be "the services section." Use **explicit class selectors** (`.services`, `.materials`, `.gallery`) instead.

### Serve HTML mockups via HTTP, not `file://`

External CSS/JS references from `<link>` and `<script>` are blocked by browser CORS on `file://` URIs — the page appears broken even though the source is correct. Launch a quick server:

**Windows (PowerShell):**
```powershell
cd sketches\001-variant
python -m http.server 8080
# or
npx serve .
```

**macOS/Linux:**
```bash
cd sketches/001-variant && python -m http.server 8080
# or
npx serve .
```

Then navigate to `http://localhost:8080` instead of the `file://` path.

### CSS techniques for "alive, Pixar-like" feel

**Morphing organic blobs** — animated `border-radius` shapes float in the hero:

```css
.hero::before {
  content: ''; position: absolute;
  width: 200px; height: 200px;
  background: linear-gradient(135deg, rgba(249,115,22,0.25), rgba(236,72,153,0.2));
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  animation: morph-blob 8s ease-in-out infinite;
}
@keyframes morph-blob {
  0%, 100% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; transform: rotate(0deg) scale(1); }
  50% { border-radius: 50% 50% 33% 67% / 55% 27% 73% 45%; transform: rotate(180deg) scale(1.1); }
}
```

**Spring-bounce transitions** — feel alive, not mechanical:

```css
--transition-smooth: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
--transition-bounce: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

**Glass-morphism navigation pill** — floating rounded navbar:

```css
.nav {
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 9999px;
  border: 1px solid rgba(255,255,255,0.5);
}
```

## Verification

After generating all variants, verify the following:

1. **Each variant renders correctly** — use `browser_navigate` + `browser_vision` on each file:
   ```
   browser_navigate(url="file:///absolute/path/to/sketches/001-calm-editorial/index.html")
   browser_vision(question="Does this layout look clean and readable? Any visible bugs?")
   ```
   Expected: no overlapping text, no unstyled elements, no broken images.

2. **Interactivity works** — click at least one primary action in each variant and confirm a visible state change occurs.

3. **Directory structure is correct** — verify all files exist:
   ```powershell
   Get-ChildItem -Recurse sketches | Select-Object FullName
   ```
   Expected: each variant subdir contains `index.html` and `README.md`.

4. **HTTP serving works (if using external resources)** — start a local server and confirm the page loads:
   ```powershell
   cd sketches\001-variant
   python -m http.server 8080
   ```
   Navigate to `http://localhost:8080` — page should render identically to the `file://` version (or better, if external resources were blocked by CORS).

5. **Comparison table is presented** — the head-to-head table with an opinionated recommendation has been shown to the user.

## Related skills

- **spike** — for technical feasibility exploration (code-level, not visual)
- **claude-design** — for production-quality HTML artifacts and components
- **popular-web-designs** — for design pattern references
- **excalidraw** — for diagrams and architecture sketches

## Attribution

Adapted from the GSD (Get Shit Done) project's `/gsd-sketch` workflow — MIT © 2025 Lex Christopherson ([gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)). The full GSD system ships persistent sketch state, theme/variant pattern references, and consistency-audit workflows; install with `npx get-shit-done-cc --hermes --global`.
