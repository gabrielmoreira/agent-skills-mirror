# The animation: one HTML page, captured to MP4

The page draws the whole collage at time `t` with `window.setT(t)`, a pure function of `t`: the same `t` always gives the same frame. Opened in a browser it plays on its own; `capture.mjs` (below) calls `setT` frame by frame and pipes the screenshots to ffmpeg.

## What makes it look like a Vox documentary

- **Stop-motion clock**: every move runs on `q12(t)`, time held on 12 fps steps, while the capture runs at 30 fps. Paper moves in small jumps, never smooth video motion.
- **Springs without overshoot**: `S(x, w) = 1 - (1 + w x) e^(-w x)`, layers land and stop, no bounce.
- **The camera always pushes in**: a slow zoom (about 6 % over the shot) plus a small drift, and each depth moves less the further back it is (parallax: plate 0.4, middle 0.7, front 1).
- **Paper, never digital**: every cut-out has the white scissor rim and a soft warm shadow (stacked `drop-shadow`), the title sits on a torn paper strip (CSS `clip-path` polygon) in a serif (Instrument Serif), two grain canvases swap at 12 fps in `overlay` blend (opacity about .16), a warm vignette.
- **The real photo as halftone**: drawn by code from their photo, dots on a 45 degree grid sized by darkness, only inside the cut-out, on a cream paper base. Never redrawn by an AI.
- **Something always lives**: clouds drifting slowly, a bird flapping (swap two cut-outs every 2 to 3 steps of `q12`), notes falling and turning, a torn-paper wipe to change scene.
- **One entrance at a time**, every 0.5 to 1.5 s, and the last one lands at least 1.5 s before the end so the shot breathes.
- **Colors from the plates only**: dusty blue, cream, sepia, ink black, one warm yellow. No neon, no gradients, no glow.

## The page (tested, 1080x1920)

Layers in `layers/`: `plate-sky.png` (plate), `note.png` (a cut-out), `hero.png` (their cut-out photo). Change the layers, sizes, places and the timeline in `setT`; keep the rest.

```html
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap" rel="stylesheet">
<style>
  html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #e9e1cf; }
  #stage { position: absolute; inset: 0; overflow: hidden; background: #8fa9c4; }
  .layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 540px 900px; }
  .plate { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  .cut { position: absolute; left: 0; top: 0; transform-origin: 50% 100%; }
  .cut img, .cut canvas { display: block; width: 100%; height: auto; }
  /* the white scissor rim + the soft paper shadow under every cut-out */
  .rim { filter: drop-shadow(5px 0 0 #fbf7ee) drop-shadow(-5px 0 0 #fbf7ee) drop-shadow(0 5px 0 #fbf7ee) drop-shadow(0 -5px 0 #fbf7ee)
                 drop-shadow(0 14px 18px rgba(40, 26, 10, .32)); }
  .strip { position: absolute; left: 190px; top: 300px; width: 700px; height: 150px; background: #f4eddc;
    clip-path: polygon(0 8%, 6% 0, 14% 6%, 23% 1%, 33% 7%, 44% 2%, 55% 8%, 66% 1%, 77% 6%, 88% 0, 100% 7%, 98% 50%, 100% 93%, 89% 100%, 78% 94%, 66% 99%, 54% 93%, 42% 100%, 31% 94%, 19% 99%, 8% 93%, 0 100%, 2% 50%);
    display: flex; align-items: center; justify-content: center; font: 104px 'Instrument Serif', serif; color: #1b1b1b; }
  canvas.grain { position: absolute; inset: 0; width: 1080px; height: 1920px; mix-blend-mode: overlay; pointer-events: none; }
  #vignette { position: absolute; inset: 0; background: radial-gradient(ellipse 75% 60% at 50% 45%, transparent 55%, rgba(40, 26, 10, .28) 100%); }
</style>
</head>
<body>
<div id="stage">
  <div class="layer" id="back"><img class="plate" src="layers/plate-sky.png"></div>
  <div class="layer" id="mid"><div class="cut rim" id="note" style="width: 520px"><img src="layers/note.png"></div></div>
  <div class="layer" id="front"><div class="cut rim" id="hero" style="width: 760px"><canvas id="heroHt"></canvas></div></div>
  <div class="strip" id="title">Paris, 1885</div>
  <canvas class="grain" id="grainA" width="540" height="960"></canvas>
  <canvas class="grain" id="grainB" width="540" height="960"></canvas>
  <div id="vignette"></div>
</div>
<script>
const DUR = 6;                                                   // seconds, the capture reads it
const $ = id => document.getElementById(id);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const q12 = t => Math.floor(t * 12 + 1e-6) / 12;                 // stop-motion clock: every move held on 12 fps steps
const S = (x, w = 14) => x <= 0 ? 0 : 1 - (1 + w * x) * Math.exp(-w * x);   // spring, never overshoots
function rng(seed) { return () => (seed = (seed * 16807) % 2147483647) / 2147483647; }

// halftone by code: the real photo stays the real photo (never redrawn), only printed as dots
function halftone(src, canvas, cell = 7) {
  const w = src.naturalWidth, h = src.naturalHeight, k = 760 / w;
  const W = Math.round(w * k), H = Math.round(h * k);
  const off = new OffscreenCanvas(W, H), o = off.getContext('2d');
  o.drawImage(src, 0, 0, W, H);
  const px = o.getImageData(0, 0, W, H).data;
  canvas.width = W; canvas.height = H;
  const c = canvas.getContext('2d');
  c.fillStyle = '#f1ead8';                                       // paper under the dots, only where the photo is
  for (let y = 0; y < H; y += 2) for (let x = 0; x < W; x += 2) if (px[(y * W + x) * 4 + 3] > 128) c.fillRect(x, y, 2, 2);
  c.fillStyle = '#161412';
  const a = Math.PI / 4, ca = Math.cos(a), sa = Math.sin(a), R = Math.hypot(W, H);
  for (let v = -R; v < R; v += cell) for (let u = -R; u < R; u += cell) {
    const x = u * ca - v * sa + W / 2, y = u * sa + v * ca + H / 2;
    if (x < 0 || y < 0 || x >= W || y >= H) continue;
    const i = ((y | 0) * W + (x | 0)) * 4;
    if (px[i + 3] < 128) continue;
    const lum = (0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2]) / 255;
    const ink = Math.pow(1 - lum, 0.85) * 1.12;                  // a little contrast, deep blacks
    if (ink < 0.04) continue;
    c.beginPath(); c.arc(x, y, Math.min(cell * 0.62, cell * 0.5 * Math.sqrt(ink) * 1.25), 0, 7); c.fill();
  }
}

// grain: two seeded canvases that swap, the paper flicker
for (const [id, seed] of [['grainA', 11], ['grainB', 97]]) {
  const c = $(id).getContext('2d'), d = c.createImageData(540, 960), r = rng(seed);
  for (let i = 0; i < d.data.length; i += 4) { const g = 128 + (r() - 0.5) * 120; d.data[i] = d.data[i + 1] = d.data[i + 2] = g; d.data[i + 3] = 255; }
  c.putImageData(d, 0, 0);
}

window.setT = function (t) {
  const tq = q12(t);
  // camera: slow push-in + drift, deeper layers move less (parallax)
  const push = 1 + 0.06 * tq / DUR, drift = -18 * tq / DUR;
  $('back').style.transform = `scale(${1 + (push - 1) * 0.4}) translateY(${drift * 0.4}px)`;
  $('mid').style.transform = `scale(${1 + (push - 1) * 0.7}) translateY(${drift * 0.7}px)`;
  $('front').style.transform = `scale(${push}) translateY(${drift}px)`;
  // the note slides in, then the hero rises from below, each on the 12 fps steps
  const n = S(tq - 0.3, 9);
  $('note').style.transform = `translate(${80 + 420 * (1 - n)}px, ${560}px) rotate(${-6 + 10 * (1 - n)}deg)`;
  const h = S(tq - 0.9, 8);
  $('hero').style.transform = `translate(160px, ${820 + 900 * (1 - h)}px) rotate(${-1.5 * (1 - h)}deg)`;
  // the title strip lands, slightly tilted
  const s = S(tq - 1.8, 12);
  $('title').style.transform = `translateY(${-260 * (1 - s)}px) rotate(${-2 + 3 * (1 - s)}deg)`;
  $('title').style.opacity = clamp((tq - 1.8) * 8);
  const g = Math.floor(t * 12) % 2;
  $('grainA').style.opacity = 0.16 * g; $('grainB').style.opacity = 0.16 * (1 - g);
};

// load every image, build the halftone, then either play (preview) or wait for the capture
const imgs = [...document.images].map(i => i.decode().catch(() => {}));
const photo = new Image(); photo.src = 'layers/hero.png';
window.ready = Promise.all([...imgs, photo.decode(), document.fonts.ready]).then(() => halftone(photo, $('heroHt')));
window.ready.then(() => {
  window.setT(0);
  if (!location.search.includes('capture')) { const t0 = performance.now(); (function play() { window.setT(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(play); })(); }
});
</script>
</body>
</html>
```

### Adding a layer

1. An element in the right depth div: `<div class="cut rim" id="eiffel" style="width: 420px"><img src="layers/eiffel.png"></div>` (`#back` = moves least, `#front` = moves most; add more depth divs if needed, each with its own parallax factor in `setT`).
2. Its move in `setT`, from `tq` (never from `t`), for example a rise from below starting at 1.2 s: `const e = S(tq - 1.2, 8); $('eiffel').style.transform = \`translate(330px, ${600 + 1300 * (1 - e)}px)\`;`.
3. Something that loops (a cloud drifting): `translateX(${-40 * tq}px)`. A bird flapping: two `<img>`, show one or the other with `Math.floor(tq * 12 / 3) % 2`.

### A torn-paper wipe (change of scene)

A full-frame div of cream paper with a torn bottom edge (`clip-path` polygon like `.strip`), above everything but the grain, that drops from `translateY(-1920px)` to `0` with `S(tq - a, 10)`, then the next scene's layers are shown under it and it leaves downward the same way.

### The photo as a print

When the cut-out is not clean, keep the whole photo as a print: same `halftone()` (a JPG has no transparency, so the whole rectangle is printed), in a cream frame:

```html
<div class="cut" id="hero" style="width: 640px; padding: 18px; background: #fbf7ee; box-shadow: 0 14px 22px rgba(40,26,10,.32)"><canvas id="heroHt"></canvas></div>
```

`photo.src = 'photo.jpg'` instead of `layers/hero.png`, and tilt it a little (`rotate(-2deg)`) when it lands.

### Formats

- 16:9: `width: 1920px; height: 1080px` on `html, body` and `.layer`, `transform-origin: 960px 540px`, the plates in 16:9, and `setViewport({ width: 1920, height: 1080 })` in `capture.mjs`.
- 1:1: 1080x1080 the same way.

## capture.mjs

```js
// node capture.mjs <animation.html> <out.mp4>: every frame of window.setT(t) at 30 fps, piped to ffmpeg
import puppeteer from 'puppeteer';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [html, out] = process.argv.slice(2);
const FPS = 30;
const browser = await puppeteer.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920 });
await page.goto(pathToFileURL(path.resolve(html)).href + '?capture', { waitUntil: 'networkidle0' });
await page.evaluate(() => window.ready);
const dur = await page.evaluate(() => DUR);
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
  '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const frames = Math.round(dur * FPS);
for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.setT(t), i / FPS);
  const shot = await page.screenshot({ type: 'jpeg', quality: 95 });
  if (!ff.stdin.write(shot)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % FPS === 0) process.stdout.write(`\r${Math.round(100 * i / frames)} %`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`\r${out}, ${dur} s`);
```

`node capture.mjs animation.html <slug>.mp4` (`DUR` in the page sets the length). The page waits on `window.ready` (images decoded, fonts loaded, halftone drawn) before the first frame. A frame that looks different from the browser preview: an image that did not load (check the paths, relative to the page).

A sound bed: `ffmpeg -v error -y -i <slug>.mp4 -i music.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "afade=t=out:st=<DUR-1>:d=1" -shortest <slug>-music.mp4`. Calm and slow under paper animations: no whooshes, no clicks on every entrance.
