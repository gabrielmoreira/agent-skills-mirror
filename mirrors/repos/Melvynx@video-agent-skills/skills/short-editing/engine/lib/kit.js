// Drawing kit: tokens, springs, paper, sheets, text, cursor. Every function is a pure function of its inputs,
// so any frame renders identically in any order (stills, drafts and final share the same code).

// W x H follows spec.format: 1080x1920 (9:16 short), 1080x1080 ('square', X feed) or 1920x1080 ('wide', 16:9).
// The CLI passes them as ?w=&h= to the page.
const QS = typeof location !== 'undefined' ? new URLSearchParams(location.search) : null;
export const W = +QS?.get('w') || 1080, H = +QS?.get('h') || 1920;
const WD = W, HD = H;

// Strict palette: paper, ink, one blue (codelynx.dev/aibuilder --primary #258eff). Grays are ink tints.
export const C = {
  paper: '#F1EEE6', sheet: '#FCFBF8', ink: '#14161B', ink2: '#5C5F68', ink3: '#A19F98',
  line: '#E3DED3', blue: '#258EFF', blue2: '#1D6FD6', tint: '#E6F0FD', dim: '#D8D3C7', white: '#FFFFFF',
  onBlue: '#FFFFFF', pop: '#14161B',   // text on an accent fill, second label fill (style.colors onAccent / pop)
};
// Text families. F.sans is the creator's font (style.font.family), the default for every text call.
export const F = { sans: 'Inter', mono: 'JetBrains Mono' };
let GRAIN = 1;   // paper texture amount (style.paper.grain): 1 = fibers + grain, 0 = flat color
let TOOTH = 0;   // embossed paper relief (style.paper.tooth): 0 = none (default), 1 = cold-press paper you can feel
// finer paper control (each defaults to the knob above, so older styles render the same):
//   toothCell: tooth bump size in px (2.5 default; 1 to 1.5 = a crisp fine tooth instead of a soft stucco)
//   waves: the 90 px soft cockle of a real sheet (defaults to tooth; 0 = off, it reads as blur on 16:9)
//   mottle: the large soft light/dark blotches (defaults to grain; 0 = off, keeps fibers and grain crisp)
let TCELL = 2.5, WAVES = null, MOTTLE = null;
let LOGOS = 'lift';   // logo finish (style.paper.logos): 'lift' = raised soft shadow, 'flat' = no shadow, crisp hairline edge
let DEPTH = 1;   // shadow strength (style.paper.depth): 0 = flat, 1 = default, 2 = deep (ambient shadow, sheets lit from above, light falloff)
let DOTS = null;   // style.paper.dots {pitch (40), r (2), alpha (.07), color (white)}: a faint dot grid on the background (lemondedumarketing's dark split panel)
let BG = 'paper';   // background (style.paper.bg): 'paper' = textured sheet with a warm vignette, 'clean' = flat light gradient + a soft accent glow,
// 'flat' = the paper color alone (no grain, relief or vignette: a solid poster color like the nico-slowdown orange)
// shadow tints 'r,g,b' (style.paper.shadow recolors all three, e.g. a cool '16,40,64' for the clean look): sheet shadows, drop shadows, hairlines
let SH = '40,28,10', DROP = '20,16,8', EDGE = '60,45,20';
// Creator style (lib/style.js themeOf). Mutates C and F in place, so call it before initSheet / makeBackground.
export function setTheme(t = {}) {
  if (t.colors) Object.assign(C, t.colors);
  if (t.font) F.sans = famCss(t.font);
  if (t.grain != null) GRAIN = clamp(+t.grain, 0, 1.5);
  if (t.tooth != null) TOOTH = clamp(+t.tooth, 0, 1.5);
  if (t.toothCell != null) TCELL = clamp(+t.toothCell, .8, 8);
  if (t.waves != null) WAVES = clamp(+t.waves, 0, 1.5);
  if (t.mottle != null) MOTTLE = clamp(+t.mottle, 0, 1.5);
  if (t.depth != null) DEPTH = clamp(+t.depth, 0, 2);
  if (t.logos) LOGOS = t.logos;
  if (t.bg) BG = t.bg;
  if (t.dots) DOTS = t.dots === true ? {} : t.dots;
  if (t.shadow) SH = DROP = EDGE = String(t.shadow);
}
// CSS font shorthand needs quotes around a family with digits or dashes
export const famCss = f => /^[A-Za-z ,-]+$/.test(f) ? f : `"${String(f).replace(/"/g, '')}"`;
// Big-text look (style.display): the counters, stat values and big board texts in their own family, flat or embossed.
//   font: family of counters, stat values, depth texts and board texts of 100 px and more; weight: its weight (400 for a
//   single-weight face like Archivo Black); text: family of the other board texts; title: color of the board texts of
//   64 px and less that set none ('ink2'); flat: true drops the emboss of depth texts. Unset = Inter 800, embossed.
export const D = { font: null, weight: 800, text: null, title: null, flat: false };
export function setDisplay(d) {
  if (!d) return;
  if (d.font) D.font = famCss(d.font);
  if (d.weight) D.weight = d.weight;
  if (d.text) D.text = famCss(d.text);
  if (d.title) D.title = d.title;
  if (d.flat != null) D.flat = !!d.flat;
}
export const bgMode = () => BG;
export const shadowRGB = () => DROP;
export const edgeRGB = () => EDGE;
export const logoFinish = () => LOGOS;
export const depth = () => DEPTH;

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const E = {
  out: x => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),          // site easing cubic-bezier(.19,1,.22,1)
  io: x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2,
  cubic: x => 1 - Math.pow(1 - clamp(x), 3),
};

// Critically damped step response. 0 before x=0, ~95% at 4.74/w s. Never overshoots: no bounce, no pulse.
export const S = (x, w = 14) => x <= 0 ? 0 : 1 - (1 + w * x) * Math.exp(-w * x);
export const vis = (t, a, b = Infinity, wi = 14, wo = 18) => S(t - a, wi) * (1 - S(t - b, wo));
// Exit curve: 0 -> 1 over d s (smoothstep), then exactly 1. Exits are shorter than entrances and end clean: a spring
// exit (S(x, 16)) leaves a 5-17% ghost for .2-.4 s that crossfades over the next beat. Every scene and item exit uses it.
export const LEAVE = .26;
export const leave = (x, d = LEAVE) => x <= 0 ? 0 : x >= d ? 1 : (x /= d, x * x * (3 - 2 * x));
// Smooth one-shot press (0 -> 1 -> 0) for button clicks.
export const press = (t, at, d = .18) => { const x = (t - at) / d; return x <= 0 || x >= 1 ? 0 : Math.sin(Math.PI * x); };

// Keyframed value with spring retargeting. keys: [[time, number|array, w?]] sorted by time.
export function track(t, keys, w = 12) {
  let v = keys[0][1]; if (Array.isArray(v)) v = v.slice();
  for (let i = 1; i < keys.length; i++) {
    const p = S(t - keys[i][0], keys[i][2] ?? w); if (p <= 0) break;
    const a = keys[i - 1][1], b = keys[i][1];
    if (Array.isArray(v)) for (let j = 0; j < v.length; j++) v[j] += (b[j] - a[j]) * p; else v += (b - a) * p;
  }
  return v;
}

export const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export const noise1 = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u); };
export function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ---------- paper ----------
export function makePaper(w, h, base = C.paper, seed = 3, amount = 1, res = 1, mottle = amount) {
  const c = new OffscreenCanvas(w, h), x = c.getContext('2d'), r = rng(seed);
  x.fillStyle = base; x.fillRect(0, 0, w, h);
  for (let i = 0; i < Math.max(4, w * h / 80000 / (res * res)); i++) {   // soft mottling
    const px = r() * w, py = r() * h, rad = Math.min(w, h) * (.2 + r() * .5), light = r() > .45;
    const g = x.createRadialGradient(px, py, 0, px, py, rad);
    g.addColorStop(0, light ? `rgba(255,255,255,${.10 * mottle})` : `rgba(130,105,70,${.04 * mottle})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(px - rad, py - rad, rad * 2, rad * 2);
  }
  x.lineCap = 'round';                                               // fibers
  const fs = Math.sqrt(res);                                         // fibers: finer and denser at high res, never stretched
  for (let i = 0; i < w * h / 650 * amount / fs; i++) {
    const px = r() * w, py = r() * h, len = (4 + r() * 18) * fs, a = r() * Math.PI * 2, bend = (r() - .5) * .9;
    x.strokeStyle = r() > .35 ? `rgba(105,85,55,${.02 + r() * .045})` : `rgba(255,255,255,${.1 + r() * .16})`;
    x.lineWidth = (.5 + r() * .9) * fs; x.beginPath(); x.moveTo(px, py);
    x.quadraticCurveTo(px + Math.cos(a + bend) * len * .5, py + Math.sin(a + bend) * len * .5, px + Math.cos(a) * len, py + Math.sin(a) * len); x.stroke();
  }
  const id = x.getImageData(0, 0, w, h), d = id.data;                // grain
  for (let i = 0; i < d.length; i += 4) { const n = (r() - .5) * 9 * amount; d[i] += n; d[i + 1] += n; d[i + 2] += n * .9; }
  x.putImageData(id, 0, 0);
  return c;
}

// Embossed relief: a smooth random height field lit from the top left, laid over the paper in overlay mode.
// cell = feature size in px (3 = paper tooth, 40+ = the soft cockle of a real sheet). Wraps around, so tiles stay seamless.
export function relief(c, cell, k, seed) {
  if (k <= 0) return;
  const w = Math.max(4, Math.round(c.width / cell)), h = Math.max(4, Math.round(c.height / cell)), r = rng(seed);
  let hm = new Float32Array(w * h).map(() => r());
  const at = (X, Y) => hm[((Y % h + h) % h) * w + (X % w + w) % w];
  for (let pass = 0; pass < 2; pass++) {
    const o = new Float32Array(w * h);
    for (let Y = 0; Y < h; Y++) for (let X = 0; X < w; X++) { let s = 0; for (let j = -1; j <= 1; j++) for (let i = -1; i <= 1; i++) s += at(X + i, Y + j); o[Y * w + X] = s / 9; }
    hm = o;
  }
  const s = new OffscreenCanvas(w, h), sx = s.getContext('2d'), id = sx.createImageData(w, h), d = id.data;
  for (let Y = 0; Y < h; Y++) for (let X = 0; X < w; X++) {
    const v = clamp(128 + (at(X - 1, Y - 1) - at(X + 1, Y + 1)) * 700 * k, 0, 255), i = (Y * w + X) * 4;
    d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
  }
  sx.putImageData(id, 0, 0);
  const x = c.getContext('2d'); x.save(); x.globalCompositeOperation = 'overlay'; x.imageSmoothingQuality = 'high';
  x.drawImage(s, 0, 0, c.width, c.height); x.restore();
}

function dotGrid(x, W, H) {   // paper.dots: centered grid, so the dots sit symmetric around the frame's middle
  if (!DOTS) return;
  const p = DOTS.pitch || 40, r = DOTS.r ?? 2, x0 = (W / 2) % p, y0 = (H / 2) % p;
  x.save(); x.globalAlpha = DOTS.alpha ?? .07; x.fillStyle = DOTS.color || '#FFFFFF'; x.beginPath();
  for (let y = y0; y < H; y += p) for (let i = x0; i < W; i += p) { x.moveTo(i + r, y); x.arc(i, y, r, 0, 2 * Math.PI); }
  x.fill(); x.restore();
}
// res = device pixels per layout px: format 'youtube' renders --scale 2 (4K) and needs the page painted at native size,
// a 1920x1080 page stretched 2x reads as blurry, dirty paper (review 2026-10-06).
export function makeBackground(W = WD, H = HD, res = 1) {   // any size (format 'youtube' paints a 1920x1080 page behind its 1080 stage)
  if (BG === 'clean') return cleanBackground(W, H);
  if (BG === 'flat') { const c = new OffscreenCanvas(W, H), x = c.getContext('2d'); x.fillStyle = C.paper; x.fillRect(0, 0, W, H); dotGrid(x, W, H); return c; }
  const c = makePaper(W, H, C.paper, 7, GRAIN, res, MOTTLE ?? GRAIN), x = c.getContext('2d'), deep = clamp(DEPTH - 1);
  relief(c, TCELL * Math.sqrt(res), .16 * TOOTH, 21); relief(c, 90 * res, .1 * (WAVES ?? TOOTH), 23);   // tooth + the soft waves of a real sheet
  if (deep > 0) {   // key light from the top left, falling off toward the bottom right
    const l = x.createRadialGradient(W * .22, -H * .08, 0, W * .22, -H * .08, H * 1.05);
    l.addColorStop(0, `rgba(255,255,255,${.22 * deep})`); l.addColorStop(.55, 'rgba(255,255,255,0)'); l.addColorStop(1, `rgba(60,44,20,${.07 * deep})`);
    x.fillStyle = l; x.fillRect(0, 0, W, H);
  }
  const g = x.createRadialGradient(W / 2, H * .42, H * .2, W / 2, H * .5, H * .85);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(70,52,25,${(.10 + .06 * deep).toFixed(3)})`);
  x.fillStyle = g; x.fillRect(0, 0, W, H);
  return c;
}

// clean: white at the top and bottom, the paper tint in the middle, a wide soft glow of the accent behind the camera card
function cleanBackground(W, H) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d'), [r, g, b] = hexRGB(C.blue);
  const v = x.createLinearGradient(0, 0, 0, H); v.addColorStop(0, C.sheet); v.addColorStop(.45, C.paper); v.addColorStop(1, C.sheet);
  x.fillStyle = v; x.fillRect(0, 0, W, H);
  for (const [cx, cy, rad, a] of [[W / 2, H * .53, W * .78, .12], [W / 2, H * .3, W * .6, .05]]) {
    const h = x.createRadialGradient(cx, cy, 0, cx, cy, rad);
    h.addColorStop(0, `rgba(${r},${g},${b},${a})`); h.addColorStop(.5, `rgba(${r},${g},${b},${a * .45})`); h.addColorStop(1, `rgba(${r},${g},${b},0)`);
    x.fillStyle = h; x.fillRect(0, 0, W, H);
  }
  return c;
}
export const hexRGB = h => { h = String(h).replace('#', ''); if (h.length === 3) h = h.replace(/./g, '$&$&'); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };

let SHEET = null;
export function initSheet(ctx) { const p = makePaper(420, 420, C.sheet, 11, .55 * GRAIN, 1, .55 * (MOTTLE ?? GRAIN)); relief(p, TCELL, .1 * TOOTH, 31); SHEET = ctx.createPattern(p, 'repeat'); }
export const sheetFill = () => SHEET || C.sheet;

// ---------- shadows (pre-blurred 9-slice sprites: no per-frame blur cost) ----------
const SHC = new Map();
function shSprite(r, blur, a) {
  const k = r + '|' + blur + '|' + a + '|' + SH; let o = SHC.get(k); if (o) return o;
  const pad = Math.ceil(blur * 2.5) + 2, core = 2 * r + 8, S_ = core + pad * 2;
  const c = new OffscreenCanvas(S_, S_), x = c.getContext('2d');
  x.filter = `blur(${blur}px)`; x.fillStyle = `rgba(${SH},${a})`; x.beginPath(); x.roundRect(pad, pad, core, core, r); x.fill();
  o = { c, pad, S: S_, cs: pad + r + 2 }; SHC.set(k, o); return o;
}
// shadow() follows the style depth (alpha x depth, longer and softer when deeper); shadowRaw() draws exactly what it is given.
export function shadow(ctx, x, y, w, h, r, blur, a, dy = 0) {
  if (DEPTH <= 0) return;
  shadowRaw(ctx, x, y, w, h, r, blur * (.6 + .4 * DEPTH), Math.min(1, +(a * DEPTH).toFixed(3)), dy * (.5 + .5 * DEPTH));
}
// canvas drop shadow (text, cutouts, photos) with the same depth scaling; reset with ctx.shadowColor = 'transparent'
export function drop(ctx, a, blur, dy, rgb = DROP) {
  ctx.shadowColor = `rgba(${rgb},${Math.min(1, a * DEPTH).toFixed(3)})`; ctx.shadowBlur = blur * (.6 + .4 * DEPTH); ctx.shadowOffsetY = dy * (.5 + .5 * DEPTH);
}

// Smooth push-in. A slow zoom done with the canvas transform re-snaps glyphs and edge antialiasing every frame, each
// element on a different frame, so text wobbles inside its card (up to 1 px jumps). zoomLayer() draws the scene into a
// layer at a fixed transform (zoomAt() only records the zoom there) and composites that layer scaled as one image:
// continuous subpixel motion, card and text locked together. 1x on purpose: a 2x+ layer goes through Chrome's mipmapped
// downscale, which snaps again (measured: 1x sd .01 px per frame, direct .25 px, 2x .2 px).
const LAYERS = [];
let layerDepth = 0;
function layerCtx(w, h) {
  let x = LAYERS[layerDepth];
  if (x && x.canvas.width === w && x.canvas.height === h) return x;
  const c = typeof document !== 'undefined' ? Object.assign(document.createElement('canvas'), { width: w, height: h }) : new OffscreenCanvas(w, h);
  x = c.getContext('2d'); x._zoomLayer = true;
  return (LAYERS[layerDepth] = x);
}
export function zoomLayer(R, draw) {
  const ctx = R.ctx, cv = ctx.canvas, x = layerCtx(cv.width, cv.height);
  x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, cv.width, cv.height); x.setTransform(ctx.getTransform());
  for (const k of ['font', 'fillStyle', 'strokeStyle', 'lineWidth', 'lineCap', 'lineJoin', 'textAlign', 'textBaseline', 'letterSpacing']) x[k] = ctx[k];
  x.save(); x._zoom = null; layerDepth++;
  try { draw({ ...R, ctx: x }); } finally { layerDepth--; x.restore(); }
  const z = x._zoom;
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  if (z) { ctx.translate(z[1], z[2]); ctx.scale(z[0], z[0]); ctx.translate(-z[1], -z[2]); }
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(x.canvas, 0, 0); ctx.restore();
}
// scale by k around (px, py): recorded for the composite inside a zoomLayer, a plain transform anywhere else
export function zoomAt(ctx, k, px, py) {
  if (!ctx._zoomLayer) { ctx.translate(px, py); ctx.scale(k, k); ctx.translate(-px, -py); return; }
  const q = ctx.getTransform().transformPoint(new DOMPoint(px, py)); ctx._zoom = [k, q.x, q.y];
}
function shadowRaw(ctx, x, y, w, h, r, blur, a, dy = 0) {
  r = Math.max(0, Math.min(Math.round(r), Math.floor(Math.min(w, h) / 2)));
  const { c, pad, S: s, cs } = shSprite(r, Math.round(blur), a);
  const X = x - pad, Y = y - pad + dy, Wd = w + pad * 2, Hd = h + pad * 2, m = s - 2 * cs, dm = Wd - 2 * cs, dn = Hd - 2 * cs;
  if (dm < 0 || dn < 0) { ctx.drawImage(c, X, Y, Wd, Hd); return; }
  const sx = [0, cs, s - cs], sw = [cs, m, cs], dx = [X, X + cs, X + Wd - cs], dw = [cs, dm, cs], dyy = [Y, Y + cs, Y + Hd - cs], dh = [cs, dn, cs];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) ctx.drawImage(c, sx[i], sx[j], sw[i], sw[j], dx[i], dyy[j], dw[i], dh[j]);
}

// A sheet of paper: layered soft shadow, grain fill, hairline edge. elev 0..2 lifts it.
export function sheet(ctx, x, y, w, h, r, o = {}) {
  const a = o.alpha ?? 1, e = o.elev ?? 1; if (a <= .002 || w <= 0 || h <= 0) return;
  ctx.save(); ctx.globalAlpha *= a;
  const deep = clamp(DEPTH - 1);
  if (o.shadow !== false) {
    if (deep > 0) shadowRaw(ctx, x, y, w, h, r, 46 * e + 26, +(.07 * deep).toFixed(3), 26 * e + 12);   // ambient: the wide soft pool under a lifted sheet
    shadow(ctx, x, y, w, h, r, 18 * e + 8, .11, 9 * e + 4); shadow(ctx, x, y, w, h, r, 3, .07, 1.5);
    if (deep > 0) shadowRaw(ctx, x, y, w, h, r, 1, +(.09 * deep).toFixed(3), .8);   // contact: the dark hairline where it meets the paper
  }
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = o.fill || sheetFill(); ctx.fill();
  if (deep > 0) {   // lit from above: brighter top, a touch of shade at the bottom, a bright top edge
    const g = ctx.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, `rgba(255,255,255,${.30 * deep})`); g.addColorStop(Math.min(.5, 90 / h), 'rgba(255,255,255,0)');
    g.addColorStop(Math.max(.5, 1 - 120 / h), 'rgba(60,44,20,0)'); g.addColorStop(1, `rgba(60,44,20,${.05 * deep})`);
    ctx.fillStyle = g; ctx.fill();
    ctx.save(); ctx.clip(); const t = ctx.createLinearGradient(0, y, 0, y + Math.min(36, h / 2));
    t.addColorStop(0, `rgba(255,255,255,${.9 * deep})`); t.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.strokeStyle = t; ctx.lineWidth = 3; ctx.beginPath(); ctx.roundRect(x + .5, y + 1, w - 1, h - 1, r); ctx.stroke(); ctx.restore();
  }
  if (o.border !== false) { ctx.strokeStyle = o.stroke || `rgba(${EDGE},.07)`; ctx.lineWidth = o.lw || 1.5; ctx.stroke(); }
  ctx.restore();
}

// Depth helpers (only above depth 1, so the default look is unchanged). lift: the shadows of a raised rounded shape
// without its fill. gloss: a lit top edge on a filled rounded shape. groove: an inset track (shadow inside the top edge).
export const deepness = () => clamp(DEPTH - 1);
export function lift(ctx, x, y, w, h, r, e = 1) {
  const d = clamp(DEPTH - 1); if (d <= 0 || w <= 0 || h <= 0) return;
  shadowRaw(ctx, x, y, w, h, r, 34 * e + 14, +(.15 * d).toFixed(3), 18 * e + 6); shadowRaw(ctx, x, y, w, h, r, 4, +(.16 * d).toFixed(3), 2);
}
export function gloss(ctx, x, y, w, h, r, k = 1) {
  const d = clamp(DEPTH - 1) * k; if (d <= 0) return;
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.clip();
  const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, `rgba(255,255,255,${.28 * d})`); g.addColorStop(.5, 'rgba(255,255,255,0)'); g.addColorStop(1, `rgba(0,0,0,${.10 * d})`);
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h); ctx.restore();
}
export function groove(ctx, x, y, w, h, r) {
  const d = clamp(DEPTH - 1); if (d <= 0) return;
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.clip();
  ctx.shadowColor = `rgba(${SH},${(.22 * d).toFixed(3)})`; ctx.shadowBlur = 10; ctx.shadowOffsetY = 4;
  ctx.beginPath(); ctx.rect(x - 40, y - 40, w + 80, h + 80); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = '#000'; ctx.fill('evenodd');
  ctx.restore();
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.strokeStyle = `rgba(255,255,255,${(.7 * d).toFixed(3)})`; ctx.lineWidth = 2;
  ctx.translate(0, 1.5); ctx.stroke(); ctx.restore();
}

// ---------- text ----------
export const font = (size, weight = 700, fam = F.sans) => `${weight} ${size}px ${fam}`;
const MC = new Map();
export function measure(ctx, s, size, weight = 700, ls = 0, fam = F.sans) {
  const k = s + '|' + size + '|' + weight + '|' + ls + '|' + fam; let v = MC.get(k);
  if (v == null) { ctx.save(); ctx.font = font(size, weight, fam); ctx.letterSpacing = ls + 'px'; v = ctx.measureText(s).width - ls; ctx.restore(); MC.set(k, v); }
  return v;
}
export function text(ctx, s, x, y, o = {}) {
  ctx.font = font(o.size || 40, o.weight || 700, o.fam); ctx.letterSpacing = (o.ls ?? 0) + 'px';
  ctx.textAlign = o.align || 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = o.color || C.ink;
  if (o.depth) { embossed(ctx, s, x, y, o); return; }
  if (o.halo) { ctx.save(); ctx.lineWidth = o.halo; ctx.lineJoin = 'round'; ctx.strokeStyle = C.sheet; if (o.alpha != null) ctx.globalAlpha *= o.alpha; ctx.strokeText(s, x, y); ctx.restore(); }   // paper-coloured outline so text stays legible over dots and lines
  if (o.alpha != null) { ctx.save(); ctx.globalAlpha *= o.alpha; ctx.fillText(s, x, y); ctx.restore(); } else ctx.fillText(s, x, y);
}
// Embossed text (o.depth, 1 = default strength): the face stays flat in its own color, raised off the paper by a lit
// white top edge, a tight contact shadow and a soft wide one. No extrusion.
function embossed(ctx, s, x, y, o) {
  const sz = o.size || 40, face = o.color || C.ink, k = Math.max(1, DEPTH) * o.depth, off = 1e4;
  ctx.save(); if (o.alpha != null) ctx.globalAlpha *= o.alpha;
  for (const [a, blur, dy] of [[.3, .04, .03], [.12, .2, .1]]) {   // shadow only: the glyphs are drawn far off-canvas, their shadow lands under the text
    ctx.save(); ctx.shadowColor = `rgba(${DROP},${Math.min(1, a * k).toFixed(3)})`; ctx.shadowBlur = blur * sz; ctx.shadowOffsetX = off; ctx.shadowOffsetY = dy * sz;
    ctx.translate(-off, 0); ctx.fillText(s, x, y); ctx.restore();
  }
  ctx.fillStyle = '#fff'; ctx.fillText(s, x, y - sz * .022);
  ctx.fillStyle = face; ctx.fillText(s, x, y);
  ctx.restore(); ctx.fillStyle = face;
}
// '#rrggbb' mixed toward black by k (0..1)
export function darken(hex, k) {
  const n = parseInt(String(hex).replace('#', '').slice(0, 6), 16); if (Number.isNaN(n)) return hex;
  const f = v => Math.round(v * (1 - k)).toString(16).padStart(2, '0');
  return '#' + f(n >> 16 & 255) + f(n >> 8 & 255) + f(n & 255);
}
// Inter cap height is ~.727em: baseline that visually centers caps on y.
export const midBase = (y, size) => y + size * .36;
export function wrap(ctx, s, maxW, size, weight = 500, ls = 0, fam = F.sans) {
  const out = []; let line = '';
  for (const w of s.split(' ')) { const t = line ? line + ' ' + w : w; if (line && measure(ctx, t, size, weight, ls, fam) > maxW) { out.push(line); line = w; } else line = t; }
  if (line) out.push(line); return out;
}

// ---------- small components ----------
export function checkIcon(ctx, cx, cy, s, color, p = 1, lw) {
  if (p <= 0) return; ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = lw || s * .16; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const pts = [[-.42, .02], [-.12, .32], [.44, -.3]].map(([a, b]) => [cx + a * s, cy + b * s]);
  const l1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]), l2 = Math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]), L = (l1 + l2) * p;
  ctx.beginPath(); ctx.moveTo(...pts[0]);
  if (L <= l1) ctx.lineTo(lerp(pts[0][0], pts[1][0], L / l1), lerp(pts[0][1], pts[1][1], L / l1));
  else { ctx.lineTo(...pts[1]); ctx.lineTo(lerp(pts[1][0], pts[2][0], (L - l1) / l2), lerp(pts[1][1], pts[2][1], (L - l1) / l2)); }
  ctx.stroke(); ctx.restore();
}

// Paper label. (x, y) is the center unless o.align = 'left' | 'right'. Returns the width.
export function chip(ctx, x, y, label, o = {}) {
  const size = o.size || 34, h = o.h || Math.round(size * 1.9), padX = o.padX ?? Math.round(size * .72), wt = o.weight || 700, ls = o.ls ?? -.3;
  const lead = o.dot ? size * .78 : o.check ? size * .95 : 0;
  const w = measure(ctx, label, size, wt, ls) + padX * 2 + lead;
  const a = o.alpha ?? 1; if (a <= .002) return w;
  const X = o.align === 'left' ? x : o.align === 'right' ? x - w : x - w / 2, Y = y - h / 2;
  ctx.save(); ctx.globalAlpha *= a;
  if (o.scale && o.scale !== 1) { ctx.translate(X + w / 2, y); ctx.scale(o.scale, o.scale); ctx.translate(-(X + w / 2), -y); }
  sheet(ctx, X, Y, w, h, h / 2, { fill: o.fill, elev: o.elev ?? .45, border: o.border ?? !o.fill });
  if (o.dot) { ctx.beginPath(); ctx.arc(X + padX + size * .2, y, size * .2, 0, Math.PI * 2); ctx.fillStyle = o.dot; ctx.fill(); }
  if (o.check) checkIcon(ctx, X + padX + size * .32, y, size * .62, o.color || C.ink, o.checkP ?? 1);
  text(ctx, label, X + padX + lead, midBase(y, size), { size, weight: wt, ls, color: o.color || C.ink });
  ctx.restore(); return w;
}

// macOS-style pointer, tip at (x, y).
const ARROW = typeof Path2D !== 'undefined' ? new Path2D('M0 0 L0 21.5 L5.3 16.6 L8.9 24.8 L12.4 23.3 L8.9 15.3 L15.9 15.3 Z') : null;
export function cursor(ctx, x, y, o = {}) {
  const a = o.alpha ?? 1; if (a <= .002) return;
  const s = (o.scale || 2.1) * (1 - .14 * (o.press || 0));
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s);
  shadow(ctx, -1, 1, 17, 25, 6, 3, .18, 1.5);
  ctx.lineJoin = 'round'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.6; ctx.stroke(ARROW);
  ctx.fillStyle = '#111'; ctx.fill(ARROW); ctx.restore();
}

// Rounded image draw with cover crop.
export function cover(ctx, img, x, y, w, h, r = 0, focus = [.5, .5], zoom = 1) {
  if (!img) { ctx.fillStyle = '#ddd'; ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fill(); return; }
  const iw = img.width, ih = img.height, s = Math.max(w / iw, h / ih) * zoom, cw = w / s, ch = h / s;
  const sx = clamp(iw * focus[0] - cw / 2, 0, iw - cw), sy = clamp(ih * focus[1] - ch / 2, 0, ih - ch);
  ctx.save(); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; if (r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.clip(); }
  ctx.drawImage(img, sx, sy, cw, ch, x, y, w, h); ctx.restore();
}
