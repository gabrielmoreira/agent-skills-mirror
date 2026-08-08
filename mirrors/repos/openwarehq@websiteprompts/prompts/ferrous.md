# Ferrous

![Ferrous](../screenshots/ferrous.webp)

**Hero Section** · Applied Physics

Paste the whole block below into Claude Code, Cursor, v0 — anything that writes
code. The video is already hosted, so the URL works as-is; nothing to download.

---

```
Build a full-viewport cinematic hero section using React, Tailwind CSS and TypeScript. The entire page is one full-height hero — no scrolling sections below it.

BACKGROUND VIDEO:

Extreme macro of black ferrofluid rising into a field of sharp symmetrical spikes as a magnetic field builds beneath it, the liquid surface glossy and reflecting a single cold highlight along each spike, the pattern reorganising slowly and continuously, pure black background with nothing else in frame, black chrome and cold white only, one continuous shot, no cuts, no on-screen text, no watermarks

Video URL: https://zxdefgavgwfxastwmmjm.supabase.co/storage/v1/object/public/assets/ferrous.mp4

The video sits behind everything at z-index 0, full-bleed at 100vw by 100svh, object-cover.

THE LOOP MUST NOT HARD-CUT — THIS IS THE MOST IMPORTANT PART:

Do NOT use a plain <video loop>. This clip's first and last frames are very different, so looping back to frame 1 produces a visible jolt every 8 seconds, and that single detail is what makes a cinematic hero look cheap.

Instead build a crossfade player: two <video> elements stacked in the same container, same src, both muted and playsInline. Player A autoplays. Listen to timeupdate on both. When the visible player reaches (duration - 1 second) and the other is still paused:
  - set the other player's currentTime to 0 and play it
  - fade the visible one's opacity to 0 and the other's to 1, over 900ms (CSS transition-opacity duration-[900ms] ease-linear)
  - after the 900ms dissolve has FINISHED, swap which one is "front" and pause the old one

Swap roles after the dissolve completes, not on the "ended" event — the outgoing player keeps playing underneath during the fade, and swapping early makes it pop.

SCRIM:

Over the video, a pointer-events-none overlay at z-index 1, rising from the bottom in the page background colour:
  linear-gradient(to top, rgba(7,7,8,0.94) 0%, rgba(7,7,8,0.45) 36%, transparent 64%)
This is not decoration — the headline sits at the bottom of the frame, and this is what keeps it legible as the footage moves underneath it.

COLOURS:

Page background #070708, text white. This is a dark page — every muted value below is quoted against that.

TYPOGRAPHY:

Display face is Instrument Serif, body is Inter, both from Google Fonts (with the two preconnect tags). Set them in tailwind.config as font-display and font-sans.

NAV:

relative z-10, flex justify-between, max-w-7xl mx-auto, px-8 py-7. Wordmark "Ferrous" in the display serif at text-[26px], leading-none, tracking-tight. Links: "Research", "Applications", "Team" at text-[13px], text-white/55, going to full opacity on hover. A CTA pill on the right reading "Work with us".

The CTA pill uses a liquid-glass treatment:
  background: rgba(255,255,255,0.01); background-blend-mode: luminosity;
  backdrop-filter: blur(4px); border: none;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
  position: relative; overflow: hidden;
and a ::before pseudo-element with inset 0, border-radius inherit, padding 1.4px, a vertical white gradient (0.45 → 0.15 at 20% → 0 at 40% → 0 at 60% → 0.15 at 80% → 0.45), masked with
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
That class needs position:relative, so do not also put a Tailwind "fixed" on it — the cascade drops it.

HERO CONTENT:

Bottom-aligned inside a max-w-7xl container, relative z-10, px-8, pb-20, min-height calc(100svh - 104px), flex-col justify-end.
  - eyebrow: "Applied magnetics" at text-[11px], uppercase, tracking-[0.42em], text-white/45
  - h1: "It organises" then "itself." wrapped in <em className="not-italic text-white/45"> so the second half recedes. mt-6, max-w-[13ch], font-display, text-5xl / sm:text-6xl / md:text-7xl, leading-[0.95], tracking-[-0.02em]
  - mt-10, a row with gap-5: a solid pill "Work with us" (rounded-full, bg-white text-black, px-7 py-3.5, text-[13px], font-medium, hover:opacity-90) and a quiet text link "Read the papers →" at text-[13px], text-white/55

FOOTER:

Pinned to the bottom, pointer-events-none, inset-x-0, z-10, max-w-7xl, px-8, pb-8. A row with a border-white/10 top border, pt-5, text-[10px], uppercase, tracking-[0.3em], text-white/30, space-between:
  "Est. 2016" · "Delft" (hidden on mobile, sm:block) · "Nine papers"

ENTRANCE:

A fade-rise keyframe (opacity 0 → 1, translateY 24px → 0) over 0.8s ease-out, both fill mode. Eyebrow plays immediately, headline at 0.2s, CTA row at 0.4s.

REDUCED MOTION:

Under prefers-reduced-motion: reduce, disable the entrance animations (animation: none, opacity 1, transform none) and hide the video entirely so the page settles to a static, readable state.

TEXT DIET:

Do not add feature grids, testimonials, spec tables or paragraphs. The hero is the whole page: wordmark, three nav links, one line, one CTA. Cut words, keep motion.
```

---

From the free tier of [uiprompts.app](https://uiprompts.app) · [all prompts](../README.md)
