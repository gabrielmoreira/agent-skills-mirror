# Aurum

![Aurum](../screenshots/aurum.webp)

**Hero Section** · Precious Metals

Paste the whole block below into Claude Code, Cursor, v0 — anything that writes
code. The video is already hosted, so the URL works as-is; nothing to download.

---

```
Build a full-viewport cinematic hero section using React, Tailwind CSS and TypeScript. The entire page is one full-height hero — no scrolling sections below it.

BACKGROUND VIDEO:

The background is molten gold pouring and folding over itself in slow motion against pure black.

Video URL: https://zxdefgavgwfxastwmmjm.supabase.co/storage/v1/object/public/assets/aurum.mp4

The video is fixed behind everything at z-index 0, full-bleed at 100vw by 100svh, object-cover.

THE LOOP MUST NOT HARD-CUT — THIS IS THE MOST IMPORTANT PART:

Do NOT use a plain <video loop>. This clip's first and last frames are very different, so looping back to frame 1 produces a visible jolt every 8 seconds, and that single detail is what makes a cinematic hero look cheap.

Instead build a crossfade player: two <video> elements stacked in the same container, same src, both muted and playsInline. Player A autoplays. Listen to timeupdate on both. When the visible player reaches (duration - 1 second) and the other is still paused:
  - set the other player's currentTime to 0 and play it
  - fade the visible one's opacity to 0 and the other's to 1, over 900ms (CSS transition-opacity duration-[900ms] ease-linear)
  - after the 900ms dissolve has FINISHED, swap which one is "front" and pause the old one

Swap roles after the dissolve completes, not on the "ended" event — the outgoing player keeps playing underneath during the fade, and swapping early makes it pop.

SCRIM:

Over the video, a pointer-events-none overlay at z-index 1: a left-to-right scrim: rgba(8,6,10,0.94) at 0%, 0.6 at 40%, transparent by 70%. This is not decoration — it is what keeps the headline legible as the footage moves underneath it.

TYPOGRAPHY:

Display face is Instrument Serif, body is Inter, both from Google Fonts (with the two preconnect tags). Headline: text-5xl on mobile, sm:text-6xl, md:text-7xl, leading-[0.95], tracking-[-0.02em], max-w-[13ch].

COLOURS:

Page background #08060a, text #ffffff.

NAV:

relative z-10, flex justify-between, max-w-7xl mx-auto, px-8 py-7. Wordmark "Aurum" in the display serif at text-[26px], tracking-tight. Links: "Vaults", "Pricing", "Custody" at text-[13px], muted, brightening on hover. A CTA pill on the right reading "Open an account".

The CTA pill uses a liquid-glass treatment:
  background: rgba(255,255,255,0.01); background-blend-mode: luminosity;
  backdrop-filter: blur(4px); border: none;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
  position: relative; overflow: hidden;
and a ::before pseudo-element with inset 0, border-radius inherit, padding 1.4px, a vertical white gradient (0.45 → 0.15 → 0 → 0 → 0.15 → 0.45), masked with
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
That class needs position:relative, so do not also put a Tailwind "fixed" on it — the cascade drops it.

HERO CONTENT:

Bottom-aligned inside a max-w-7xl container, px-8, pb-20, min-height calc(100svh - 104px), justify-end.
  - eyebrow: "Allocated metal" at text-[11px], uppercase, tracking-[0.42em], muted
  - h1: "Weight you can" then "ask for back." wrapped in <em className="not-italic"> at a muted colour so the second half recedes
  - a row with a solid pill "Open an account" and a quiet text link "Read the terms →"

FOOTER RAIL:

Pinned to the bottom inside the same container: a thin top border and three small uppercase items at text-[10px], tracking-[0.3em], very low opacity — "Est. 2016", "Zurich · Perth" (hidden on mobile), "Fully allocated".

ENTRANCE:

A fade-rise keyframe (opacity 0 → 1, translateY 24px → 0) over 0.8s ease-out. Eyebrow plays immediately, headline at 0.2s, CTA row at 0.4s.

REDUCED MOTION:

Under prefers-reduced-motion: reduce, disable the entrance animations and hide the video entirely so the page settles to a static, readable state.

TEXT DIET:

Do not add feature grids, testimonials, spec tables or paragraphs. The hero is the whole page: wordmark, three nav links, one line, one CTA. Cut words, keep motion.
```

---

From the free tier of [uiprompts.app](https://uiprompts.app) · [all prompts](../README.md)
