# yuv-design

> **Yuval Avidani's signature web-design defaults — automatic.**

A Claude-Code-discoverable skill that encodes the full YUV.AI design system as defaults: **Anton + Rubik** for display, **Inter + Assistant** for body, **pink + yellow + bone** palette, paper grain, warm shadows, asymmetric layouts, GSAP-first motion, RTL/LTR bilingual support.

Drop this skill into `~/.claude/skills/`, restart your agent, and every web request — landing page, dashboard, React component, single artifact — comes back with the YUV.AI fingerprint without any per-request copy-paste of fonts, colors, or rules.

---

## Why this exists

Yuval ships a lot of web work. Without a skill like this, every request either:

1. Comes back with generic AI-template aesthetic — soft shadows, 12px radii, slate gray, Inter on everything, lorem ipsum, default Tailwind palette. Indistinguishable from every other AI-generated site.
2. Requires a paragraph of brand instructions every single time.

This skill solves both. The agent reads it once at session start, and every subsequent web output uses Anton uppercase, the warm pink/yellow palette, real grain, and asymmetric layouts — automatically.

It's the **frontend / web counterpart** to [`yuv-viral-video`](../yuv-viral-video/), which carries the same brand into rendered MP4s.

---

## What you get, automatically

### Typography
- **Anton** UPPERCASE for English headlines · letter-spacing `-0.04em` · the only display weight (it's already heavy)
- **Rubik Black** weight 900 for Hebrew headlines (RTL-aware)
- **Inter** for English body · weights 400 / 500 / 600 / 700
- **Assistant** for Hebrew body · weight 400+
- Mixed-language single declaration — browser auto-routes per glyph

### Color palette
- Pink `#FF1464` — the brand thread, every CTA
- Yellow `#E5FF00` — accent, dominates when used (no timid swatches)
- Off-white `#FAFAF7` — replaces pure white everywhere
- Bone `#F5EEE4` — transitional sections
- Charcoal `#1A1A1A` — primary text
- Warm gray `#8B8680` — secondary text

### Banned by default
- Pure `#FFFFFF`
- Default Tailwind palette (`slate-*`, `zinc-*`, `indigo-*`, etc.)
- Blue / navy / cool tones
- 8px / 12px corporate-rounded radii
- Soft drop-shadow rounded-corner template cards
- Multicolor icon sets
- Stock photography / generic business imagery
- Lorem ipsum / placeholder text
- system-ui / serif default stacks

### Layout & motion
- Asymmetric > grid-perfect
- 0px or 999px or 40–56px (glass) border radius only
- Warm-toned shadows (pink/orange undertone)
- 1–2% paper grain overlay on light backgrounds
- 120–160px desktop section padding
- 1440px max content width
- GSAP for anything non-trivial · `back.out(1.7)`, `power3.out`, `expo.out`, `sine.inOut`
- Phosphor / Lucide icons single-stroke only

### Bilingual built-in
- `dir="rtl"` on Hebrew pages
- Logical CSS properties (`*-inline-*`) over physical (`*-left`)
- Mixed Hebrew + English in one container — automatic per-glyph routing

### Hyperframes-compatible
- Semantic HTML5 (no div soup)
- `HYPERFRAMES_VIDEO_SLOT` markers for capturable regions
- GSAP timelines (seekable) over CSS keyframes
- No wall-clock dependencies — deterministic for frame capture

---

## Install

```bash
mkdir -p ~/.claude/skills
cd /tmp && git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/hoodini/ai-agents-skills.git yuv-clone
cd yuv-clone && git sparse-checkout set skills/yuv-design
cp -R skills/yuv-design ~/.claude/skills/
cd && rm -rf /tmp/yuv-clone
```

Restart your Claude Code / Codex / Cursor / Gemini-CLI session. The skill will auto-discover.

---

## How to use it

You don't need to invoke it. Once installed, any web/frontend request from Yuval triggers it automatically. The skill description front-loads keywords like *website, landing page, web UI, React, component, HTML, CSS, frontend, dashboard, marketing page, design system* (and Hebrew equivalents — *אתר, דף נחיתה, עיצוב אתר, פיתוח אתר, רכיב, דאשבורד*) so the matcher routes Yuval's requests through it without anything explicit.

When commissioning work:

> *"build me a landing page for [project]"*
> *"make a dashboard for tracking [thing]"*
> *"create a hero section about [topic]"*

The skill applies. Output uses Anton uppercase, pink/yellow palette, paper grain, warm shadows, asymmetric layout. No mention of fonts or colors needed.

---

## Override

If a project has its own brand system (a client's palette, a specific design system you're matching), **the project wins**. This skill is the default for the empty state, not a hard override.

Just specify the override in the request:

> *"build a landing page for Acme Corp — use their brand: navy + orange, Roboto + Roboto Slab"*

The skill will respect that and skip the YUV.AI defaults.

---

## What's in the skill

- **`SKILL.md`** — the full design system encoded as agent-readable rules. Typography matrix, palette table, banned list, layout defaults, animation library preferences, RTL setup, Hyperframes patterns, two starter snippets (English hero + Hebrew RTL hero), one-line self-check before shipping. Plus 12 **battle-tested rules** distilled from production iterations.

- **`patterns.md`** — copy-paste code templates for production-tested components, extracted from real sites built with this skill (most recently [effects.yuv.ai](https://effects.yuv.ai)). Includes:
  1. Bilingual toggle (EN/HE with flag emojis)
  2. Mobile hamburger nav (≤ 880px collapse)
  3. Effect-ID copy chip
  4. Hyperframes hero reel (real `data-*` attributes)
  5. IntersectionObserver demo pause
  6. Course CTA template (practical.yuv.ai, verified content)
  7. Liquid glass card with 3D tilt-pop
  8. Connect / social grid (with verified handles + URLs)
  Plus a pre-ship checklist of 12 must-pass items.

- **`lessons-learned.md`** — 15 specific anti-patterns from real sessions, each paired with the corrective pattern. Read this **before** starting any frontend output to skip the iteration cost. Covers: side-by-side bilingual, missing mobile nav, stacked headlines, untranslated `document.title`, generic install commands, WebFetch on SPAs, invented CTA content, and more.

- **`README.md`** — this file. Public-facing intro and install instructions.

No scripts, no build dependencies — pure documentation that the agent reads once and applies. Together, the four files encode the full muscle memory of building a YUV.AI-grade frontend on the first pass.

---

## Companion skills

| Skill | Purpose | Output |
|---|---|---|
| [`yuv-design`](.) (this skill) | Web / frontend defaults | HTML, CSS, React, Next.js |
| [`yuv-viral-video`](../yuv-viral-video/) | Video editorial defaults | Rendered MP4s via Hyperframes |

Both encode the same YUV.AI brand system, tuned for their delivery medium.

---

## Credits

Built by Yuval Avidani · [yuv.ai](https://yuv.ai) · [@hoodini](https://github.com/hoodini)

License: MIT.
