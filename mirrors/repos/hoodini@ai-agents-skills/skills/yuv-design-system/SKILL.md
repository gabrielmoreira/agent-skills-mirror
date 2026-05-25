---
name: yuv-design-system
description: Yuval Avidani's brand and design system. Use for ANY visual output by Yuval — websites, landing pages, dashboards, React/HTML/CSS, slide decks, keynotes, infographics, charts, data viz, social images, profile pages, video banners, presentations, posters. Triggers: website, landing page, React, HTML, CSS, frontend, design system, typography, dashboard, slides, deck, keynote, infographic, chart, profile, banner, logo, brand. Hebrew: אתר, דף נחיתה, עיצוב, דאשבורד, מצגת, אינפוגרפיקה, גרף, לוגו. Apply automatically. Encodes two palette modes (Fly High purple/yellow/grey default; Warm Editorial pink/yellow/bone for Hope/bigcats/practical.yuv.ai), typography (Anton + Inter for English, Rubik + Assistant for Hebrew, letter-spacing 0 default), brand assets, canonical social links and credentials. Components PurpleBar, YellowUnderline, FlightHUD, CompassDial, CounterUp, HeroBg at references/components/. Project brand wins when specified.
---

# yuv-design-system

The canonical personal design system for **Yuval Avidani** (yuv.ai). Apply automatically whenever Yuval asks for any visual output and a brand isn't otherwise specified.

**Source of truth:** This is the canonical specification — rules, brand assets, links — for Yuval's visual system across web, presentations, infographics, and social. Public location: <https://github.com/hoodini/ai-agents-skills/tree/master/skills/yuv-design-system>. A private companion repo at <https://github.com/hoodini/yuv-design-system> holds runnable React components, Tailwind preset, and an install script — this skill bundles the LLM-readable spec + the four core brand images so it works standalone.

## How to use this skill

1. **Pick the palette mode** (Fly High vs Warm Editorial — see §1). Default to Fly High.
2. **Apply mandatory typography** (Anton/Inter + Rubik/Assistant — see §2).
3. **Use the bundled brand assets** when a logo, profile, or watermark is appropriate (see §3).
4. **Include the canonical link set** in footers, profile blocks, credits, and "find me elsewhere" sections (see §4).
5. **For deep dives** — load the reference file that matches the medium:

   | Medium | Read this file |
   |---|---|
   | Web / landing / React | `references/web-and-react.md` |
   | Slide decks / keynotes | `references/presentations.md` |
   | Infographics / charts / data viz | `references/visuals-and-charts.md` |
   | Social images / posters | `references/social-images.md` |
   | Hebrew / bilingual / RTL | `references/typography.md` § Hebrew |
   | Hardened patterns (bilingual toggle, mobile nav, cert flow, etc.) | `references/lessons-learned.md` |

   Load only what's relevant — keeps the working context small.

---

## §1. Palette modes — pick one

Two named modes. **Default Fly High** unless the project belongs to the Warm Editorial family (Hope the cheetah, Marcus the lion, bigcats.ai, the practical.yuv.ai course landing).

| Mode | Default? | Use for | Vibe |
|---|---|---|---|
| **Fly High** | yes | Keynotes, hackathon decks, dashboards, dev-facing UIs, product pages, marketing for technical audiences | Purple / yellow / light-grey · bold, optimistic, electric, slightly playful |
| **Warm Editorial** | only for the brand family above | Hope, bigcats.ai, course landing, anywhere a "warm, confrontational, paper-feel" mood fits | Pink / yellow / bone · warm, confident, premium, editorial |

When unsure, ask once: *"Fly High (purple/yellow/grey) or Warm Editorial (pink/yellow/bone)?"* then commit.

### Fly High tokens (default)

```css
:root {
  --yuv-purple:      #5E17EB;   /* primary brand, act-slide backgrounds, vertical accent bars */
  --yuv-purple-dark: #3D0DA8;   /* decorative depth, diagonal accents */
  --yuv-yellow:      #FFEC00;   /* loud accent only — never a background */
  --yuv-grey:        #F1F2F2;   /* page / content-slide background */
  --yuv-white:       #FFFFFF;   /* cards on grey, headers on purple */
  --yuv-black:       #000000;   /* headers on grey, body */
  --yuv-grey-dark:   #D4D6D6;   /* dividers on grey */
}
```

Full token file (CSS + JSON + Tailwind preset) lives in `references/tokens/`. Copy `palette.css` straight into any project.

### The two-background rule (Fly High, non-negotiable)

Every slide or page section lives in one of two states. **Never invent a third.** Yellow is an accent, never a background.

| Type | Background | Headline color | Use for |
|---|---|---|---|
| **Act** | Purple `#5E17EB` | White `#FFFFFF` | Title, section divider, closer, hero |
| **Content** | Light grey `#F1F2F2` | Black `#000000` | Everything else — info, evidence, lists, dashboards |

### Warm Editorial tokens

```css
:root {
  --pink:       #FF1464;   /* primary brand, CTAs, thread color */
  --yellow:     #E5FF00;   /* accent — when it shows up, it dominates */
  --black:      #0A0A0A;   /* warm near-black, never blue-black */
  --off-white:  #FAFAF7;   /* paper-feel, replaces #FFFFFF entirely */
  --bone:       #F5EEE4;   /* transitional sections, cream */
  --charcoal:   #1A1A1A;   /* primary text on light */
}
```

Full Warm Editorial rules (paper grain, warm shadows, gradient bans, etc.) → `references/palettes-warm-editorial.md`.

### Rules that apply to BOTH modes

- **No pure `#FFFFFF` as the root** of a page or slide. Cards on grey in Fly High *can* be pure white; the canvas itself never is.
- **No blue, slate, indigo, emerald, cyan, zinc.** No default Tailwind palette. Stay in the chosen mode or in the project's brand.
- **Border radius: `0` or `999px` only.** The 8–12px middle ground is the single most "AI template" tell.
- **Asymmetric over grid-perfect.** Offset columns. One element breaking the grid is the move.
- **Whitespace is generous.** Premium comes from restraint.
- **Max content width 1440px.** Section padding 120–160px desktop, 64–80px mobile.

---

## §2. Typography — mandatory

### English

- **Display / headlines:** [Anton](https://fonts.google.com/specimen/Anton). Always UPPERCASE. **Letter-spacing default `0` (normal).** Anton is already condensed — negative tracking makes letters touch, which is what the system used to do wrong. Only at very large hero sizes (≥ 180px) can you go negative, and never tighter than `-0.015em`. Line-height `1.0`–`1.05`. Never lowercase, never title case.
- **Body / UI:** [Inter](https://fonts.google.com/specimen/Inter), 400 / 500 / 600 / 700 / 900. Line-height `1.5` for body.
- **Mono (readouts, citations, eyebrows):** [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono).

### Hebrew

- **Display:** [Rubik](https://fonts.google.com/specimen/Rubik) (weights up to 900).
- **Body:** [Assistant](https://fonts.google.com/specimen/Assistant).
- Hebrew pages: `<html lang="he" dir="rtl">` + logical CSS properties (`margin-inline-start`, not `margin-left`).

### Bilingual rule (battle-tested)

**Never stack EN + HE side-by-side or in adjacent positions.** Anton + Rubik at display sizes overlap visually (descenders invade the next ascender row). Use a language toggle instead — one language visible at a time. Full hardened pattern in `references/lessons-learned.md` § Bilingual toggle.

### One Google Fonts link — always safe to load all four

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;900&family=JetBrains+Mono:wght@400;500&family=Rubik:wght@400;500;600;700;800;900&family=Assistant:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Stack the families in one variable so the browser picks per glyph:

```css
:root {
  --yuv-font-display: 'Anton', 'Rubik', system-ui, sans-serif;
  --yuv-font-body:    'Inter', 'Assistant', system-ui, sans-serif;
  --yuv-font-mono:    '"JetBrains Mono"', '"SF Mono"', ui-monospace, Menlo, monospace;
}
h1, h2, h3, .display {
  font-family: var(--yuv-font-display);
  text-transform: uppercase;        /* Latin only — Hebrew unaffected */
  letter-spacing: 0;                /* Anton is condensed — DO NOT add negative tracking */
  line-height: 1.0;
}
/* Only at hero size (≥ 180px) and only when the headline visually demands it: */
.display-hero { letter-spacing: -0.01em; }   /* max — never tighter */
```

**Banned defaults:** serif fonts, script fonts, `system-ui`, the default Tailwind font stack.

---

## §3. Brand assets — bundled in `assets/`

Four canonical files are bundled with this skill. Reach for them when an output deserves a real brand mark instead of a placeholder.

### Asset retrieval — fallback chain (works on any machine)

When you need a brand image, follow this chain in order:

1. **Look inside the skill bundle.** On a properly-installed machine, the assets are always present at one of: `~/.claude/skills/yuv-design-system/assets/`, `~/.copilot/skills/yuv-design-system/assets/`, or `~/.agents/skills/yuv-design-system/assets/`. Use whichever path your runtime exposes.

2. **If the skill location isn't known** (headless, fresh container), scan common spots for a local clone of the repo: `~/Documents/ai-decks/yuv-design-system/`, `~/yuv-design-system/`, `~/Code/yuv-design-system/`, `~/dev/yuv-design-system/`. If found, use its `assets/`.

3. **If nothing is local, clone the canonical repo.** Private, but the user's GitHub auth on the machine will let `git clone` work without prompts:

   ```bash
   git clone https://github.com/hoodini/yuv-design-system.git ~/Documents/ai-decks/yuv-design-system
   ~/Documents/ai-decks/yuv-design-system/scripts/install-skill.sh
   ```

   That populates `~/.claude/skills/yuv-design-system/assets/` plus the Copilot/agent symlinks.

4. **Last-resort fallback for sandboxed sessions where step 3 isn't possible** (e.g. CI with no git auth): embed via base64 `data:image/png;base64,…` inline. Acceptable only as a last resort — file references stay small and edit-friendly.

The repo is `https://github.com/hoodini/yuv-design-system` and is **private**. Don't attempt `raw.githubusercontent.com` URLs — they will 404 without a personal access token. Use `git clone` instead.

### The four files

| File | When to use | Notes |
|---|---|---|
| `assets/logo-square-transparent.png` | Logos on light or dark backgrounds — anywhere you need a clean cutout (favicon, header, app icon, social card on a custom bg) | Phoenix mark, transparent background, square |
| `assets/logo-square-color.png` | Hero badges, social profile images, OG images, anywhere the logo needs its own colored backplate | Phoenix mark on the brand backplate, square |
| `assets/logo-rectangle-wordmark.png` | Watermarks (bottom-right corner of slides, videos, screenshots), email signatures, lower-third overlays, certificates | "LET'S FLY HIGH · YUV.AI" wordmark |
| `assets/profile-yuval-studio.png` | About sections, course pages, podcast art, "meet your instructor" blocks, speaker bio cards | Yuval in the studio under the YUV.AI neon |

### Quick path — call `ensure-assets.sh`

If you're running in a shell-capable session and just want a guaranteed-good assets path, run:

```bash
ASSETS_DIR=$(/path/to/yuv-design-system/scripts/ensure-assets.sh)
echo "$ASSETS_DIR"
```

The script walks the fallback chain (skill bundle → local clones → git clone) and prints the absolute path to a working `assets/` directory. If GitHub auth isn't set up and the clone fails, it exits non-zero with a clear message.

### Embedding rules

- **Watermark placement:** bottom-right corner of any slide / video / shareable image, ~3% of the canvas width margin, ~120–180px wide at 1920×1080. Use `logo-rectangle-wordmark.png` for watermarks. Never stretch.
- **Hero logos on dark backgrounds:** prefer `logo-square-transparent.png` so the phoenix sits on whatever background you have.
- **Hero logos on light/grey/bone backgrounds:** also prefer the transparent square — the mark has enough internal color to stand on its own.
- **Social profile / OG cards:** `logo-square-color.png` (has its own backplate so it stands out in feeds).
- **Profile photo for bios / about / contact:** `profile-yuval-studio.png`. Crop to square or 4:5 portrait depending on the surface.

For web embedding, copy the asset into the project's `public/` and reference it; or for HTML artifacts where you can't add files, inline as a `data:image/png;base64,…` URI (only acceptable as a last resort — file references are preferred). On slides, embed natively.

---

## §4. Canonical bio + link set — auto-include

Whenever an output has a footer, contact section, "find me elsewhere" block, profile card, speaker bio, credits panel, or video end-screen, **include this set automatically**. Don't ask Yuval to provide it.

### Credentials (use in bios, about sections, speaker intros, course pages)

- **2× GitHub Star** (recognised twice by GitHub for community impact)
- **AWS Gen AI Superstar**
- **AI commentator on Channel 12 News (Israel)** — מגיש פינת AI בחדשות 12 / "AI segment host on Channel 12 News" / "Resident AI commentator on Channel 12 News"
- **AI Builder & Speaker**
- **Technical Content Creator**
- Founder of **YUV.AI** — leading Hebrew-speaking AI educator and technical innovator
- Active communities across X, Instagram, TikTok, YouTube, LinkedIn, Facebook, GitHub

### Suggested one-liners (drop into bios)

- *Yuval Avidani — 2× GitHub Star, AWS Gen AI Superstar, AI commentator on Channel 12 News (Israel). Founder of YUV.AI. Builds, teaches, and ships AI that actually works.*
- *AI Builder & Speaker. Technical Content Creator. 2× GitHub Star. AWS Gen AI Superstar. The AI guy on Channel 12 News.*
- Hebrew: *יובל אבידני — מגיש פינת AI בחדשות 12, GitHub Star כפול, AWS Gen AI Superstar, מייסד YUV.AI. בונה, מלמד, ומשגר AI שעובד.*

### Link set

```
website:  https://yuv.ai
linktree: https://linktr.ee/yuvai
x:        https://x.com/yuvalav              · @yuvalav
instagram:https://instagram.com/yuval_770     · @yuval_770
tiktok:   https://www.tiktok.com/@yuval.ai    · @yuval.ai
youtube:  https://youtube.com/@yuv-ai         · @yuv-ai
github:   https://github.com/hoodini           · @hoodini
facebook: https://facebook.com/yuval.avidani  · @yuval.avidani
linkedin: https://www.linkedin.com/in/yuval-avidani-87081474/
```

### Inclusion rules

- **Footers:** all eight platforms + linktree, each as an icon-only button (Phosphor or Lucide brand glyphs, single-color stroke matching the active palette).
- **Speaker bios / about cards:** website + linkedin + linktree + one signature social (X or Instagram).
- **Video end-screens:** website + 3 socials (typically X, Instagram, YouTube).
- **Email signatures / certificate footers:** website + linkedin + linktree.
- **Linktree-as-shortcut:** for any "follow me everywhere" CTA, link directly to https://linktr.ee/yuvai instead of listing all eight — punchier and one tap.

### Drop-in HTML snippet (Fly High mode)

```html
<footer class="yuv-socials" style="display:flex;gap:16px;align-items:center;justify-content:center;padding:48px 0;background:var(--yuv-grey)">
  <a href="https://yuv.ai" aria-label="Website" style="color:var(--yuv-purple)"><i class="ph ph-globe"></i></a>
  <a href="https://x.com/yuvalav" aria-label="X" style="color:var(--yuv-purple)"><i class="ph ph-x-logo"></i></a>
  <a href="https://instagram.com/yuval_770" aria-label="Instagram" style="color:var(--yuv-purple)"><i class="ph ph-instagram-logo"></i></a>
  <a href="https://www.tiktok.com/@yuval.ai" aria-label="TikTok" style="color:var(--yuv-purple)"><i class="ph ph-tiktok-logo"></i></a>
  <a href="https://youtube.com/@yuv-ai" aria-label="YouTube" style="color:var(--yuv-purple)"><i class="ph ph-youtube-logo"></i></a>
  <a href="https://github.com/hoodini" aria-label="GitHub" style="color:var(--yuv-purple)"><i class="ph ph-github-logo"></i></a>
  <a href="https://facebook.com/yuval.avidani" aria-label="Facebook" style="color:var(--yuv-purple)"><i class="ph ph-facebook-logo"></i></a>
  <a href="https://www.linkedin.com/in/yuval-avidani-87081474/" aria-label="LinkedIn" style="color:var(--yuv-purple)"><i class="ph ph-linkedin-logo"></i></a>
  <a href="https://linktr.ee/yuvai" aria-label="Linktree" style="color:var(--yuv-purple)"><i class="ph ph-tree-structure"></i></a>
</footer>
```

Full machine-readable link list (JSON, with handles + URLs for programmatic use): `references/social-and-links.md`.

---

## §5. Visuals, infographics & charts — the "thinking in pictures" default

Yuval prefers visual explanation over prose wherever possible. Charts, infographics, dynamic diagrams, isometric scenes, animated counters, before-and-after splits. **When something could be explained as a number, a chart, or a diagram, default to the visual.**

### Encoding rules in brand

- **Fly High primary series colour:** `#5E17EB` purple. Highlight or "hero" data point: `#FFEC00` yellow. Secondary series: charcoal / `#3D0DA8` / `#D4D6D6` greys. Never blue.
- **Warm Editorial primary series:** `#FF1464` pink. Highlight: `#E5FF00` yellow. Secondary: charcoal / warm grey.
- **Always label the hero number.** If there's a big stat, render it with `<CounterUp>` (component in `references/components/CounterUp.tsx`) — count from 0 with `requestAnimationFrame`, ease-out cubic, ~1400ms.
- **No 3D bar charts. No pie charts with > 4 slices. No rainbow palettes.** Pick categorical or sequential, never both.
- **Grids and axes:** 1px charcoal at 10–15% opacity. No coloured gridlines.
- **Type on charts:** Anton uppercase for axis labels and section titles, Inter for tick numbers, JetBrains Mono for raw readouts.

### Default libraries

| Surface | Library | Notes |
|---|---|---|
| React chart | recharts | Lightweight, easy palette override. |
| Vanilla HTML chart | Chart.js | Drop-in, easy to skin via `options.scales` + custom colors. |
| Bespoke / interactive infographic | D3 + GSAP | When the visual has personality — sankey, force layout, custom layout. |
| Hand-built SVG infographic | inline `<svg>` | For static / printable / Hyperframes-capturable visuals. |
| Slide-deck stat slide | `<CounterUp>` + Anton heading | Pattern in `references/components/CounterUp.tsx` |

Full chart-skinning guidance, sample Chart.js options object, recharts override pattern, and isometric SVG patterns → `references/visuals-and-charts.md`.

---

## §6. Signature components (Fly High)

These are the recognisable fingerprints. Full source in `references/components/`.

| Component | Role |
|---|---|
| `<PurpleBar height={96}>` | Vertical purple accent bar to the left of every major content-slide headline. The single most consistent brand mark in the system. **Use it.** |
| `<YellowUnderline width={210}>` | Hand-drawn SVG underline anchored under **one specific word** — never decoratively floating. For the punchline word in a subtitle. |
| `<FlightHUD n={12} cite="…" tone="content">` | Bottom HUD strip: progress bar + flight phase (CLIMB/CRUISE/DESCENT/LANDED) + instrument readouts (ALT / SPD / HDG / FUEL). Establishes the flight-simulator throughline across a deck. |
| `<CompassDial heading={287}>` / `<AltimeterDial alt={35000}>` | Circular SVG cockpit instruments. **Title and section-divider slides only** — overuse cheapens them. |
| `<CounterUp to={95}>` | Animated number counter pairs with a big Anton % sign for stat slides. |
| `<HeroBg src={image} overlay={…}>` | Ken-Burns full-bleed image background with mandatory overlay gradient for headline contrast. |

### The yellow highlight span (critical pattern)

```tsx
<h1 style={{ fontSize: 148, lineHeight: 1.05, letterSpacing: 0 /* see warnings */ }}>
  The team that<br />
  wins this weekend<br />
  won't have the<br />
  <span style={{
    display: 'inline-block',
    background: '#FFEC00',
    color: '#000',
    padding: '0.08em 0.4em',          /* em-based so it scales with font size */
    letterSpacing: '0.01em',          /* slight POSITIVE tracking inside the box */
    boxDecorationBreak: 'clone',
    WebkitBoxDecorationBreak: 'clone',
  }}>
    smartest model.
  </span>
</h1>
```

**Three rules baked into this pattern — all battle-tested gotchas:**

1. **`letterSpacing: 0`** on the headline (never negative). Anton is already condensed; negative tracking makes letters touch.
2. **`letterSpacing: '0.01em'` inside the yellow span** — slight positive tracking so letters breathe inside the yellow rectangle. Without this, the yellow box looks like a wall of crammed glyphs.
3. **`padding: '0.08em 0.4em'`** (em-based) instead of pixel padding — scales with the headline size. With pixel padding, the yellow box hugs letters too tight at large sizes.

Plus the always-rules: `line-height ≥ 1.0`, `display: inline-block`, `boxDecorationBreak: clone`. Without these the yellow box eats the previous line's descenders. Full pattern + anti-patterns: `references/lessons-learned.md`.

### One Anton element per slide / section

Stacking multiple Anton blocks in a row (a headline + four big Anton stat tiles, say) makes the surface read like a wall of thick type. **Rule: one Anton element per slide.** Supporting numbers, labels, and stat values go in **Inter 900** or **JetBrains Mono** at the size you'd otherwise put Anton. The slide stays calm, the hero remains the hero.

---

## §7. Animation defaults

Every animation needs a reason. Alive, not restless. Hovers are deliberate. Reveals are scroll-triggered. Numbers count up on viewport entry. Connecting lines draw themselves.

Library preference order:
1. **GSAP** — primary. Use SplitText for headline reveals, ScrollTrigger for scroll-driven sequences, MotionPath for SVG paths. Prefer GSAP over Framer Motion for non-trivial work — higher-end results, and timelines are seekable (matters for Hyperframes capture).
2. **Three.js + React Three Fiber** — for 3D when the project justifies it.
3. **MediaPipe** — gesture / pose interactions when the project has a signature wow moment.
4. **Lottie** — when the designer has shipped a `.json`.
5. **CSS-only** — hover states, focus rings, button press feedback. Don't reach for a library for these.

### Hyperframes compatibility (free insurance)

Yuval often captures sites and decks as MP4 for keynotes, reels, and marketing. Hyperframes (https://hyperframes.mintlify.app/llms.txt) renders HTML to deterministic, frame-by-frame video. Default to Hyperframes-friendly patterns even when capture isn't requested:

- Semantic HTML5 (`<section>`, `<article>`, `<header>`, `<nav>`, `<footer>`). Div soup is harder to target.
- Mark capture-destined regions: `<!-- HYPERFRAMES_VIDEO_SLOT: hero --> … <!-- /HYPERFRAMES_VIDEO_SLOT -->`.
- Prefer GSAP timelines (seekable) over CSS `@keyframes` for sequences that might be captured.
- **No wall-clock dependencies.** No `Date.now()`, no orphan `setInterval`. Use scroll position, GSAP timelines, or `requestAnimationFrame` tied to a deterministic clock.

### Signature video banner — mandatory on landing sites

Every landing page or marketing site Yuval ships opens with a cinematic product-demo video banner at the top, embedded as an `<iframe>` pointing at a self-looping Hyperframes-compatible HTML composition (`public/demo/index.html`). "Hero with static text and a stock image" is banned — the hero opens with motion. Full 6-scene narrative arc, device mockup spec, cursor choreography rules, and deterministic loop pattern → `references/presentations.md` § Signature video banner.

---

## §8. Bilingual & Hebrew — battle-tested rules

Hebrew work has hard-earned rules. **Read these before writing any HE/EN page:**

1. **Bilingual = toggle, never side-by-side.** Anton at `8vw` + Rubik 900 at `5–6vw` visually collide. Build a language toggle with `data-lang="en"` / `data-lang="he"` attributes and a universal show/hide rule. Default EN, button to switch.
2. **`document.title` is part of the toggle.** Swap the tab title too — otherwise it screams "half-built bilingual" to native readers.
3. **Mobile = duplicate the language toggle** into the always-visible mobile cluster, not just inside the hamburger.
4. **`<html lang="he" dir="rtl">`** when Hebrew is the default. Logical CSS (`margin-inline-start`, `padding-inline-end`) everywhere.
5. **One display headline per section.** Never two stacked display fonts.

Full hardened bilingual toggle (HTML + CSS + JS) and mobile-nav pattern → `references/lessons-learned.md`.

---

## §9. What NOT to ship — explicit anti-defaults

- **Stock photography.** No generic business people, abstract cityscapes, Unsplash textures. Prefer abstract geometric, AI-generated in palette, or Yuval's own imagery (Hope cheetah, Marcus lion, the studio shot).
- **Emoji in enterprise / client work.** Personal blogs and casual content are fine.
- **Soft drop-shadow rounded-corner template cards** — the dominant AI slop visual. Flat card, 12px radius, `0 4px 6px rgba(0,0,0,0.1)`. Never ship.
- **The default Tailwind palette** (`slate`, `zinc`, `gray`, `emerald`, `cyan`, `indigo`, `violet`, `rose`).
- **Multicolour icon sets.** Phosphor / Lucide with single-color stroke only.
- **Cookie banners, chat widgets, marketing popups in demo builds.** Production concerns. Leave demos clean.
- **AI-generated feel** — templated hero → features → pricing → footer, lorem ipsum, "Your tagline here." Write real copy.
- **Pure `#FFFFFF`** as a page/slide root.
- **Blue as a default accent** unless the project explicitly requires it.
- **Yellow as a slide / page background.** Accent only.
- **A third background colour** in Fly High. Two-background rule is non-negotiable.
- **Anton at large sizes with `line-height < 1.0`** inside a multi-line headline that has a `box-decoration-break: clone` span. Descenders get eaten.
- **`<YellowUnderline>` floating with no anchor.** Always under a specific word.
- **WebFetch on JS-rendered SPAs** (Teachable, Kajabi, practical.yuv.ai, etc.). Use Claude-in-Chrome.

---

## §10. Pre-flight checklist (run before delivering anything)

1. Palette mode picked explicitly (Fly High default, Warm Editorial only for the brand family).
2. Page/slide root is **not pure `#FFFFFF`**. Cards in Fly High *can* be `#FFFFFF`.
3. No default Tailwind color classes (`slate-*`, `zinc-*`, `indigo-*`, `emerald-*`, …).
4. Two-background rule respected in Fly High — every section is purple-act or grey-content, no third.
5. Anton is **uppercase**, `letter-spacing: 0` by default (NEVER negative — Anton is already condensed), `-0.01em` only at hero size (≥ 180px). Line-height ≥ 1.0 whenever a yellow `box-decoration-break: clone` span sits inside a multi-line headline. Yellow span uses em-based padding (`0.08em 0.4em`) + slight POSITIVE tracking (`0.01em`).
6. Hebrew pages have `dir="rtl"` + logical CSS. Bilingual pages use a **toggle**, not side-by-side.
7. Border radius is `0` or `999px`. Nothing in between.
8. Shadows match the mode — plain low-opacity black for Fly High, warm pink/orange undertone for Warm Editorial. No blue-black.
9. **Social link footer included** wherever a footer / credits / about section exists, with the canonical link set.
10. **Brand mark used** where a logo is appropriate — square transparent on hero, rectangle wordmark in corners, profile photo in about/bio.
11. `<PurpleBar>` next to content-slide headlines (Fly High).
12. `<YellowUnderline>` anchored to a specific word — never decorative.
13. For any catalog with > 8 GSAP demos: IntersectionObserver pauses offscreen demos.
14. For any frontend output: resize the preview to 375×812 (iPhone size) and verify before declaring done. Mobile-first is a baseline check, not polish.

If any fails — fix before shipping.

---

## Where the canonical files live

| File | Purpose |
|---|---|
| `assets/logo-square-transparent.png` | Square phoenix mark, transparent background |
| `assets/logo-square-color.png` | Square phoenix mark on brand backplate |
| `assets/logo-rectangle-wordmark.png` | "LET'S FLY HIGH · YUV.AI" rectangle wordmark (watermarks) |
| `assets/profile-yuval-studio.png` | Yuval in the studio (bios, about, course pages) |
| `references/tokens/palette.css` | Drop-in CSS variables |
| `references/tokens/palette.json` | Design tokens in JSON |
| `references/tokens/tailwind.config.js` | Tailwind preset |
| `references/components/*.tsx` | Signature React components |
| `references/components/keyframes.css` | Shared `yuv-*` keyframes |
| `references/web-and-react.md` | Web/React deep-dive |
| `references/presentations.md` | Slide deck rules + signature video banner |
| `references/visuals-and-charts.md` | Infographics, charts, data-viz patterns |
| `references/social-images.md` | Social cards, OG images, posters |
| `references/typography.md` | Full type system including Hebrew/RTL |
| `references/social-and-links.md` | Machine-readable link set + footer patterns |
| `references/lessons-learned.md` | Hardened patterns + anti-patterns from production |
| `references/palettes-warm-editorial.md` | Warm Editorial mode deep dive |

### Where this skill lives

- **Public spec + assets (canonical for LLM use):** <https://github.com/hoodini/ai-agents-skills/tree/master/skills/yuv-design-system>
- **Private companion repo (runnable React components + install script):** <https://github.com/hoodini/yuv-design-system> — clone via `git clone https://github.com/hoodini/yuv-design-system.git` from any of Yuval's machines for the React components and Tailwind preset.

---

Maintained by [@hoodini](https://github.com/hoodini) · [yuv.ai](https://yuv.ai) · [@yuvalav](https://x.com/yuvalav)
