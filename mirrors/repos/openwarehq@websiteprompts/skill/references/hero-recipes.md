# Hero recipes — copy-paste code for each mechanic

One worked example per mechanic. Adapt the fonts, colours and copy per the site's
world; keep the structure.

---

## RECIPE 1 · LOOP HERO

Fullscreen seamless-looping video, glass nav, cinematic serif type. The default
choice, and what most "cinematic site" requests actually mean.

**Structure.** A fixed `<video>` at `inset-0 w-full h-full object-cover z-0`, the
scrim at `z-10 pointer-events-none`, nav and hero content at `z-20`. No decorative
blobs or gradient meshes — the footage supplies all the depth the page needs.

```tsx
<div className="relative min-h-[100svh] w-screen overflow-hidden">
  <video
    className="absolute inset-0 h-full w-full object-cover"
    src="/hero.mp4" poster="/hero.webp"
    autoPlay muted playsInline preload="auto"
  />
  <div className="pointer-events-none absolute inset-0 z-10" style={{
    background:
      'linear-gradient(to top, rgba(10,10,11,.96) 0%, rgba(10,10,11,.55) 26%, transparent 50%)',
  }} />
  <nav className="relative z-20 mx-auto flex max-w-7xl justify-between px-8 py-7">…</nav>
  <header className="relative z-20 mx-auto flex max-w-7xl flex-col justify-end px-8 pb-20
                     min-h-[calc(100svh-104px)]">…</header>
</div>
```

**Reframing the subject.** Generated footage almost always centres its subject —
which is exactly where a left-aligned headline runs. Push the video, not the
container: `scale-[1.35] translate-x-[11%]`. The scale must overhang further than
the shift (`(scale − 1) / 2 ≥ translate`) or the container shows through the edge.

**Typography.** Display serif + modern sans is the house look (Instrument Serif +
Inter; Playfair for luxury; Space Mono / Orbitron for tech). Load via `<link>` in
`index.html` with both `preconnect` tags. Headline
`text-5xl sm:text-6xl md:text-7xl leading-[0.95] tracking-[-0.02em] max-w-[13ch]`.
Put the second half of the headline in `<em className="not-italic">` at a muted
colour so it recedes — one line, two weights of attention.

**Liquid glass** (nav pill and CTA):

```css
.liquid-glass {
  background: rgba(255,255,255,0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
  border: none; box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
  position: relative; overflow: hidden;
}
.liquid-glass::before {
  content:''; position:absolute; inset:0; border-radius:inherit; padding:1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,.45) 0%, rgba(255,255,255,.15) 20%, rgba(255,255,255,0) 40%,
    rgba(255,255,255,0) 60%, rgba(255,255,255,.15) 80%, rgba(255,255,255,.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude; pointer-events:none;
}
```

Gotcha: `.liquid-glass` needs `position: relative`, so a Tailwind `fixed` on the
same element loses to the cascade and the border ring vanishes. Force it inline if
the element must be fixed.

**Fade-rise entrance** (staggered):

```css
@keyframes fade-rise { from { opacity:0; translate:0 24px } to { opacity:1; translate:0 0 } }
.animate-fade-rise         { animation: fade-rise .8s ease-out both; }
.animate-fade-rise-delay   { animation: fade-rise .8s ease-out .2s both; }
.animate-fade-rise-delay-2 { animation: fade-rise .8s ease-out .4s both; }
```

Animate the standalone `translate` property, not `transform` — `transform`
overwrites Tailwind's `-translate-x-1/2` centring. Eyebrow immediately, headline at
0.2s, CTA row at 0.4s. One `animation` shorthand per element.

---

## RECIPE 2 · CROSSFADE LOOP PLAYER (the anti-hard-cut)

**The single most important recipe here.** A plain `<video loop>` cuts from the
last frame straight back to the first; in real footage those frames differ, and it
lands as a visible jolt every few seconds. It is invisible in a screenshot, which
is why it ships.

Two stacked players, same source. B starts ~1s before A ends, they dissolve across
each other, and roles swap **after** the dissolve finishes — swapping on `ended`
pops, because the outgoing player is still visible mid-fade.

```tsx
function CrossfadeVideo({ src, poster }: { src: string; poster?: string }) {
  const a = useRef<HTMLVideoElement>(null);
  const b = useRef<HTMLVideoElement>(null);
  const [front, setFront] = useState<'a' | 'b'>('a');

  useEffect(() => {
    const FADE = 900;                    // ms, must match the CSS duration
    const cur = front === 'a' ? a.current : b.current;
    const nxt = front === 'a' ? b.current : a.current;
    if (!cur || !nxt) return;

    const onTime = () => {
      if (!cur.duration || cur.currentTime < cur.duration - 1) return;
      if (!nxt.paused) return;
      nxt.currentTime = 0;
      void nxt.play();
      cur.style.opacity = '0';
      nxt.style.opacity = '1';
      window.setTimeout(() => { cur.pause(); setFront(front === 'a' ? 'b' : 'a'); }, FADE);
    };
    cur.addEventListener('timeupdate', onTime);
    return () => cur.removeEventListener('timeupdate', onTime);
  }, [front]);

  return (
    <>
      <video ref={a} src={src} poster={poster} autoPlay muted playsInline
        className="absolute inset-0 h-full w-full object-cover transition-opacity duration-[900ms] ease-linear" />
      <video ref={b} src={src} muted playsInline
        className="absolute inset-0 h-full w-full object-cover opacity-0 transition-opacity duration-[900ms] ease-linear" />
    </>
  );
}
```

Two alternatives, when they fit better:

- **Ping-pong** a webp frame strip (0→N→0 forever) — seamless *by construction*,
  correct for rotating, oscillating or breathing subjects. Wrong for directional
  motion, where playing backwards reads as a mistake.
  ```ts
  let dir = 1, f = 0;
  function tick() {
    requestAnimationFrame(tick);
    f += dir;
    if (f >= N - 1) { f = N - 1; dir = -1; }
    if (f <= 0)     { f = 0;     dir =  1; }
    const i = Math.round(f);
    if (i !== lastDrawn) { drawFrame(i); lastDrawn = i; }
  }
  ```
- **Play-once-freeze** — no `loop`; the last frame holds on `ended`. For a
  below-the-fold moment that is supposed to *end*.

---

## RECIPE 3 · SCROLL-SCRUB (fly-through / reveal)

Scroll drives the frame index of a canvas-drawn webp strip. Bulletproof on any
host, and it allows per-frame surgical edits.

**Do not seek a `<video>`.** Browsers cannot seek smoothly enough for
scroll-scrubbing; it stutters on every frame. Extract a strip instead:

```bash
ffmpeg -i public/hero.mp4 -vf "fps=14,scale=1512:-2" -c:v libwebp -quality 78 \
  public/frames/frame-%04d.webp
```

Then use `lib/scrubber.ts` (drop-in, dependency-free):

```tsx
const canvas = useRef<HTMLCanvasElement>(null);
useEffect(() => {
  const s = new Scrubber(canvas.current!, FRAME_COUNT);
  s.resize();
  window.addEventListener('resize', () => s.resize());
  let raf = 0;
  const loop = () => {
    raf = requestAnimationFrame(loop);
    const max = document.documentElement.scrollHeight - window.innerHeight;
    s.tick(seg(window.scrollY / max, 0, 0.4));   // this clip owns 0 → 0.4 of the page
  };
  raf = requestAnimationFrame(loop);
  return () => cancelAnimationFrame(raf);
}, []);
```

Layout: a sticky 500–900vh runway; the canvas cover-draws the nearest loaded
frame; keep a static keyframe `<img>` underneath as the instant fallback so the
first paint is never empty.

**A there-and-back strip** (open, then close again on the way down) is just a
longer strip — reverse the clip with `ffmpeg -vf reverse` and extract both into one
folder. Watch the frame count: extraction usually drops the first frame of every
clip after the first, so trimming in ffmpeg *as well* drops two and creates a skip.

---

## RECIPE 4 · CURSOR SCRUB

The pointer seeks the film. Memorable — and completely inert on touch, so always
ship a fallback (autoplay the clip when `matchMedia('(pointer: coarse)')` matches).

```ts
const SENSITIVITY = 0.8;
let prevX = window.innerWidth / 2, target = 0, seeking = false;
const clamp = (t: number) => Math.max(0, Math.min(video.duration || 0, t));

window.addEventListener('mousemove', (e) => {
  const delta = e.clientX - prevX; prevX = e.clientX;
  target = clamp(target + (delta / window.innerWidth) * SENSITIVITY * (video.duration || 0));
  if (!seeking) { seeking = true; video.currentTime = target; }
});
// queue the NEXT seek from onSeeked — issuing seeks freely floods the decoder and freezes it
video.addEventListener('seeked', () => {
  if (Math.abs(video.currentTime - target) > 0.01) video.currentTime = target;
  else seeking = false;
});
```

The video is `fixed inset-0 z-0 object-cover`, `muted playsInline preload="auto"`,
and does **not** autoplay.

Pairs well with a typewriter headline:

```ts
function useTypewriter(text: string, speed = 38, startDelay = 600) {
  const [displayed, setD] = useState(''); const [done, setDone] = useState(false);
  useEffect(() => {
    let i = 0, id = 0;
    const t = window.setTimeout(() => {
      id = window.setInterval(() => {
        i++; setD(text.slice(0, i));
        if (i >= text.length) { clearInterval(id); setDone(true); }
      }, speed);
    }, startDelay);
    return () => { clearTimeout(t); clearInterval(id); };
  }, [text, speed, startDelay]);
  return { displayed, done };
}
```

Cursor while typing: `inline-block w-[2px] h-[1.1em] bg-current` with
`@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }` at `1s step-end infinite`.

---

## RECIPE 5 · MULTI-SCENE SCROLL

Several clips read as one journey. Two ways in, in order of reliability:

**Flat-colour seams (free and invisible).** If clip A ends on a flat field of
colour and clip B opens on the same one, the join is undetectable — there is no
detail to misalign, so no cross-fade is needed at all. Sample the hex from A's last
frame, paint the page background exactly that, and bridge the two canvases with a
fixed sheet of it that rises and falls across the handover. Change that hex and a
flash appears at every seam.

**Crossfade scenes.** N independent full-bleed clips, opacity-crossfaded on scroll
with one kinetic word per world (FALL / DEEPER / THROUGH / ARRIVE). No morphing
risk, and the clips can all be generated in parallel. Add a thin vertical progress
filament down one edge for depth.

A true generated chain — where the camera never stops moving between worlds — is a
different order of difficulty; see the "Multi-clip" section of SKILL.md for the
laws and the honest ceiling, and **github.com/oso95/scroll-world** (MIT) for a
full config-driven engine with dive-in clips, connectors and phone hardening.
