# Kernel

![Kernel](../screenshots/kernel.webp)

**Scroll Experience** · Developer Portfolio

Paste the whole block below into Claude Code, Cursor, v0 — anything that writes
code. Both videos are already hosted, so the URLs work as-is; nothing to
download.

---

```
Build a developer portfolio site using React, Tailwind CSS and TypeScript. It has a cinematic scroll-scrubbed intro and then an ordinary, readable vertical résumé. One page, one scroll value, no cuts anywhere.

THE IDEA:

The camera pushes past a person's shoulder into their laptop until the glowing screen fills the frame. That white screen IS the page background, so there is no transition to hide. A wireframe tunnel then draws itself and the visitor travels down it toward their name, which starts as a speck at the vanishing point and grows as it is approached. The tunnel ends there. Everything after it is a plain vertical résumé on solid ground with no video behind it.

TWO VIDEOS:

Intro — anime night interior, seen from behind someone typing at a laptop, camera pushing steadily in until the blank glowing screen fills the frame:
https://zxdefgavgwfxastwmmjm.supabase.co/storage/v1/object/public/assets/kernel-intro.mp4

Tunnel — a fine dark wireframe lattice drawing itself out of empty white, camera pushing through it, resolving back to empty white:
https://zxdefgavgwfxastwmmjm.supabase.co/storage/v1/object/public/assets/kernel-wire.mp4

THE COLOUR THAT MAKES IT SEAMLESS — DO NOT CHANGE IT:

The page background is #e9f5f8. That is not a design choice, it is sampled from the laptop screen in the last frame of the intro clip. The intro ends on it, the tunnel clip opens and closes on it, and the résumé is painted with it. Because every boundary is the same flat colour, there is no detail at any join for the eye to catch, so the cuts are invisible without any cross-fade. Change this hex and you will see a flash at every seam.

DO NOT USE <video> — SCRUB FRAME STRIPS:

Extract both clips to webp frame strips and scrub them on a <canvas>. A <video> element cannot be seeked smoothly enough for scroll-scrubbing; it stutters on every seek.

  ffmpeg -i intro.mp4 -vf "fps=14,scale=1512:-2" -c:v libwebp -quality 76 frames/frame-%04d.webp
  ffmpeg -i tunnel.mp4 -vf "fps=14,scale=1512:-2" -c:v libwebp -quality 82 wire/wire-%04d.webp

That gives 113 intro frames and 112 tunnel frames.

Write a Scrubber class that takes a canvas, a frame count and a URL builder. It should load every 6th frame first so coarse scrubbing works immediately, then fill the gaps in batches of 12, and always draw the nearest already-loaded frame. Store decoded frames as ImageBitmap. Ease the drawn index toward the target (current += (target - current) * 0.14) so fast scrolling does not strobe. Draw with a cover fit and set canvas size from devicePixelRatio capped at 2.

SMOOTH SCROLL — LERP 0.08:

Keep the real scrollbar: put the true page height on document.body and position the content wrapper fixed at top left, full width. Each frame, ease a value toward window.scrollY (current += (target - current) * 0.085) and apply transform: translate3d(0, -current, 0) to the wrapper. Snap current to the target when within 0.06px or sub-pixel drift keeps the compositor awake forever. Observe the wrapper with a ResizeObserver and rewrite body height when it changes.

Under prefers-reduced-motion: reduce, skip all of this — leave the wrapper in normal flow and let the browser scroll it. Do not merely shorten the animation; the correct behaviour is scroll tracking the input 1:1.

EVERY MOVING THING READS THE SAME SCROLL VALUE:

Drive the scrub, the reveals and the progress bar from that one eased number inside a single requestAnimationFrame loop. Do not use IntersectionObserver for the reveals — it fires once at a threshold and hands off to a CSS transition running on its own clock, so a fast flick leaves a trail of half-finished animations. Instead read each element's getBoundingClientRect every frame and compute a 0→1 amount from its real position, then apply opacity and translate3d directly. This is what makes the whole page move as one object.

THE INTRO TIMELINE:

The intro occupies 400vh of scroll. Let p be progress 0→1 across it.
  - p 0.00 → 0.40 : intro clip scrubs; the screen fills the frame and goes white
  - p 0.14 → 0.30 : the hero name and SCROLL hint lift away and fade out
  - p 0.36 → 0.46 : a fixed sheet of #e9f5f8 rises and falls, bridging clip one's last frame to clip two's first. Both are that colour so the sheet is invisible; it exists only so nothing flickers between the two canvases.
  - p 0.44 → 0.97 : tunnel clip scrubs
  - p 0.48 → 0.93 : the name is approached (below)
After p = 1 the intro is done and the résumé scrolls normally.

THE NAME AT THE VANISHING POINT — THE SCALE MUST BE EXPONENTIAL:

Fixed, centred, above the canvases. It holds the résumé header: name at 64px, then role · location at 22px, then the email at 13px in mono with 0.28em tracking.

Scale it with 0.09 * Math.pow(17, t) where t is 0→1 across p 0.48 → 0.93. It must be exponential, not linear — apparent size goes as 1/distance, so a linear ramp reads as a zoom effect while this reads as travel. It starts at roughly 0.09 (a speck at the vanishing point) and ends at about 1.6 (filling the frame). Fade it in over the first tenth and leave it up once it lands; the résumé scrolls over it.

Do not put a card or a panel behind it. It begins tiny in the brightest, emptiest part of the frame, and by the time it is large it covers the lattice itself.

THE SCROLL-DRAWN SPINE:

Down the centre of the résumé, a 1px vertical hairline in the border colour with an accent-coloured fill that draws downward as you read. Implement as an absolutely positioned track at left-1/2 inside a relative résumé container, with an inner div at transform-origin top and scaleY driven each frame.

Measure it off the résumé container's own getBoundingClientRect, not off whole-page scroll — the video intro eats a third of the page, so page progress would leave the spine already part-drawn when the reading starts. Fill to a point 72% up the viewport, which is where the eye actually rests, so the line stays just ahead of the reader rather than lagging behind. Hide it below the md breakpoint; a centre rail has nowhere to go in a narrow column.

COLOURS:

  page / screen  #e9f5f8      hover row     #dcebf0
  hairlines      #c3d7de      primary type  #0d1519
  secondary      #4d5f68      metadata      #5f757f
  accent         #0b7d62      (status dot, links, metric figures only)

Never name a Tailwind colour `base`, `sm`, `lg` or `xl`. Those shadow the built-in font-size utilities, so a class like `md:text-base` silently resolves to the colour instead of the size — it will paint text the background colour with no error and no warning.

TYPOGRAPHY:

Inter for everything, JetBrains Mono for metadata, labels and figures. Both from Google Fonts with the two preconnect tags. Headings use tracking-[-0.02em]. Metadata is 11px mono at 0.18em tracking, uppercase.

THE RÉSUMÉ:

Solid #e9f5f8, max-width 1000px, generous hairline rules, no cards and no shadows. In order: a masthead with name and city; a status line with a small accent dot; one honest sentence; email and two links; then SELECTED WORK — four projects, each with an index number, name, one accent-coloured metric that matters (14k writes/sec sustained, 38ms p99 purge), two sentences of what it does, stack chips, and year plus role right-aligned; then EVERYTHING ELSE — eight more as a compact table of name, one-line description, stack, year; then HOW I WORK — four blocks of stack and practice, then three of writing, speaking and open source; then a contact line and a footer.

Write real specifics. Engineers read numbers, not adjectives — say what the thing did and how fast, not that it was performant.

TEXT DIET:

No hero paragraph, no skills bars, no percentage ratings, no testimonials, no logos-of-companies strip. The intro is the flourish; everything after it stays out of the way and shows the work.
```

---

From the free tier of [uiprompts.app](https://uiprompts.app) · [all prompts](../README.md)
