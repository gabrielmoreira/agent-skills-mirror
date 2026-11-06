// Meta scenes: "the AI edits the video you are watching" beats.
// Same contract as scenes.js: {type, from, to, layer, ...} with times already mapped to SHORT time.
//   capStyles (over) the live caption cycles through N caption styles, with a "Style 07 / 20" counter and a dot rail
//   camTile (over)   the camera as a framed tile on full paper that moves on spoken words (top, bottom, left, right)
//   camSplit (over)  split screen flipped: the camera rises from its bottom slot to the TOP of the frame, paper below
import { C, F, W, H, E, clamp, lerp, seg, S, leave, track, sheet, text, measure, midBase, chip, cover } from './kit.js';
import * as K from './kit.js';

const TAU = Math.PI * 2;
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
const envA = (s, t) => S(t - s.from + (s.pre || 0), 12) * (1 - leave(t - (s.to ?? 1e9)));

// ---------------------------------------------------------------- capStyles (over)
// {layer: 'over', from, to, cycleFrom, cycleTo, n: 20, y: 1180, counterY: 300}
// Before cycleFrom it shows style 0 (the house sticker). Hide the normal captions over [from, to].
const MONO = 'JetBrains Mono', SERIF = 'Georgia';
const words = c => c.words.map(w => w.text);
function lineW(ctx, ws, size, wt, ls, fam = F.sans) { const sp = measure(ctx, ' ', size, wt, ls, fam || F.sans); return ws.reduce((a, w, i) => a + measure(ctx, w, size, wt, ls, fam) + (i ? sp : 0), 0); }
// lay words out centred on (cx, base); fn(word, x, w, i) draws each one
function lay(ctx, ws, cx, size, wt, ls, fam, fn) { fam = fam || F.sans;
  const sp = measure(ctx, ' ', size, wt, ls, fam || F.sans); let x = cx - lineW(ctx, ws, size, wt, ls, fam) / 2;
  ws.forEach((w, i) => { const ww = measure(ctx, w, size, wt, ls, fam); fn(w, x, ww, i); x += ww + sp; });
}
function sticker(ctx, s, x, y, o) {
  ctx.save(); ctx.font = `${o.weight || 800} ${o.size}px ${o.fam || F.sans}`; ctx.letterSpacing = (o.ls ?? -1.5) + 'px'; ctx.textAlign = o.align || 'left';
  ctx.lineJoin = 'round';
  if (o.stroke) { ctx.lineWidth = o.lw || o.size * .22; ctx.strokeStyle = o.stroke; if (o.shadow !== false) { ctx.shadowColor = 'rgba(20,16,8,.28)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 6; } ctx.strokeText(s, x, y); ctx.shadowColor = 'transparent'; }
  if (o.fill !== null) { ctx.fillStyle = o.fill || C.ink; ctx.fillText(s, x, y); }
  ctx.restore();
}
// 'clean' (21st, not in the capStyles cycle): a white pill with sentence-case ink text, the clean look's caption.
// Designed at 42 px (base), so captions.size is the real text size. Emphasised words take the accent.
function cleanPill(ctx, c, y) {
  const ws = words(c), sz = 42, wt = 500, ls = -.4, w = lineW(ctx, ws, sz, wt, ls), h = 76, padX = 30;
  ctx.save(); K.drop(ctx, .10, 26, 7);
  ctx.beginPath(); ctx.roundRect(W / 2 - w / 2 - padX, y - h / 2, w + padX * 2, h, 22); ctx.fillStyle = C.white; ctx.fill();
  ctx.shadowColor = 'transparent'; ctx.strokeStyle = `rgba(${K.edgeRGB()},.09)`; ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
  lay(ctx, ws, W / 2, sz, wt, ls, null, (s, x, ww, i) => text(ctx, s, x, midBase(y, sz), { size: sz, weight: c.words[i].emph ? 600 : wt, ls, color: c.words[i].emph ? C.blue : C.ink }));
}
cleanPill.base = 42;
// 20 styles, all inside the palette (ink, paper, one blue). Each draws chunk c centred at y; t for per-word timing.
const STYLES = [
  (ctx, c, y, t) => lay(ctx, words(c), W / 2, 84, 800, -1.5, null, (w, x, ww, i) => sticker(ctx, w, x, midBase(y, 84), { size: 84, stroke: C.sheet, fill: c.words[i].emph ? C.blue : C.ink })),
  (ctx, c, y) => { const s = words(c).join(' '), sz = 76, w = measure(ctx, s, sz, 800, -1.2); sheet(ctx, W / 2 - w / 2 - 40, y - 62, w + 80, 124, 62, { fill: C.blue, elev: .8, border: false }); text(ctx, s, W / 2, midBase(y, sz), { size: sz, weight: 800, ls: -1.2, align: 'center', color: C.white }); },
  (ctx, c, y) => { const s = words(c).join(' '), sz = 76, w = measure(ctx, s, sz, 800, -1.2); sheet(ctx, W / 2 - w / 2 - 36, y - 60, w + 72, 120, 18, { fill: C.ink, elev: .8, border: false }); text(ctx, s, W / 2, midBase(y, sz), { size: sz, weight: 800, ls: -1.2, align: 'center', color: C.white }); },
  (ctx, c, y) => sticker(ctx, words(c).join(' ').toUpperCase(), W / 2, midBase(y, 80), { size: 80, weight: 900, ls: 4, align: 'center', stroke: C.sheet }),
  (ctx, c, y, t) => lay(ctx, words(c), W / 2, 84, 800, -1.5, null, (w, x, ww, i) => sticker(ctx, w, x, midBase(y, 84), { size: 84, stroke: C.sheet, fill: t >= c.words[i].start ? C.blue : C.ink3 })),
  (ctx, c, y, t) => lay(ctx, words(c), W / 2, 84, 800, -1.5, null, (w, x, ww, i) => {
    const p = S(t - c.words[i].start, 18); sticker(ctx, w, x, midBase(y, 84), { size: 84, stroke: C.sheet });
    if (p > .01) { ctx.fillStyle = C.blue; ctx.beginPath(); ctx.roundRect(x, y + 50, ww * p, 14, 7); ctx.fill(); }
  }),
  (ctx, c, y) => sticker(ctx, words(c).join(' '), W / 2, midBase(y, 92), { size: 92, weight: 700, ls: -1, fam: SERIF, align: 'center', stroke: C.sheet, fill: C.ink }),
  (ctx, c, y) => { const s = words(c).join(' ').toLowerCase(); chip(ctx, W / 2, y, s, { size: 58, weight: 700, ls: 0, h: 120, padX: 44 }); },
  (ctx, c, y) => lay(ctx, words(c), W / 2, 80, 800, -1.2, null, (w, x, ww) => { ctx.fillStyle = C.tint; ctx.beginPath(); ctx.roundRect(x - 10, y - 52, ww + 20, 104, 14); ctx.fill(); text(ctx, w, x, midBase(y, 80), { size: 80, weight: 800, ls: -1.2, color: C.blue2 }); }),
  (ctx, c, y) => sticker(ctx, words(c).join(' '), W / 2, midBase(y, 92), { size: 92, weight: 900, align: 'center', stroke: C.ink, lw: 5, shadow: false, fill: C.sheet }),
  (ctx, c, y) => sticker(ctx, words(c).at(-1), W / 2, midBase(y, 150), { size: 150, weight: 900, ls: -5, align: 'center', stroke: C.sheet, fill: C.blue }),
  (ctx, c, y) => sticker(ctx, words(c).join(' ').toLowerCase(), W / 2, midBase(y, 84), { size: 84, weight: 500, ls: -1, align: 'center', stroke: C.sheet, fill: C.ink }),
  (ctx, c, y) => lay(ctx, words(c), W / 2, 84, 800, -1.5, null, (w, x, ww, i) => sticker(ctx, w, x, midBase(y, 84), { size: 84, stroke: C.sheet, fill: i ? C.blue : C.ink })),
  (ctx, c, y) => lay(ctx, words(c), W / 2, 66, 800, -1, null, (w, x, ww) => { sheet(ctx, x - 16, y - 50, ww + 32, 100, 20, { elev: .6 }); text(ctx, w, x, midBase(y, 66), { size: 66, weight: 800, ls: -1 }); }),
  (ctx, c, y) => { ctx.save(); ctx.translate(W / 2, y); ctx.rotate(-.06); const s = words(c).join(' '), w = measure(ctx, s, 78, 900, -1.5); sheet(ctx, -w / 2 - 34, -60, w + 68, 120, 14, { elev: 1 }); text(ctx, s, 0, midBase(0, 78), { size: 78, weight: 900, ls: -1.5, align: 'center' }); ctx.restore(); },
  (ctx, c, y, t) => { const s = words(c).join(' '), n = Math.round(s.length * seg(t, c.start, c.start + .35)), sz = 72, w = measure(ctx, s, sz, 600, 0, MONO), x = W / 2 - w / 2;
    sheet(ctx, x - 34, y - 58, w + 68, 116, 18, { elev: .8 }); text(ctx, s.slice(0, n), x, midBase(y, sz), { size: sz, weight: 600, fam: MONO });
    if (n < s.length || (t * 2 | 0) % 2) { ctx.fillStyle = C.blue; ctx.fillRect(x + measure(ctx, s.slice(0, n), sz, 600, 0, MONO) + 4, y - 34, 6, 68); } },
  (ctx, c, y) => sticker(ctx, words(c).join(' '), W / 2, midBase(y, 88), { size: 88, weight: 900, align: 'center', stroke: C.sheet, fill: C.blue }),
  (ctx, c, y) => { const ws = words(c), lh = 86, y0 = y - (ws.length - 1) * lh / 2; ws.forEach((w, i) => sticker(ctx, w, W / 2, midBase(y0 + i * lh, 80), { size: 80, weight: 900, ls: -2, align: 'center', stroke: C.sheet, fill: i === ws.length - 1 ? C.blue : C.ink })); },
  (ctx, c, y) => sticker(ctx, '[ ' + words(c).join(' ') + ' ]', W / 2, midBase(y, 66), { size: 66, weight: 700, ls: 0, fam: MONO, align: 'center', stroke: C.sheet, fill: C.blue }),
  (ctx, c, y) => { const s = words(c).join(' '), sz = 72, w = measure(ctx, s, sz, 800, -1.2), x = W / 2 - w / 2 - 50;
    sheet(ctx, x, y - 64, w + 100, 128, 22, { elev: 1 }); ctx.fillStyle = C.blue; ctx.beginPath(); ctx.roundRect(x, y - 64, 14, 128, [22, 0, 0, 22]); ctx.fill();
    text(ctx, s, x + 60, midBase(y, sz), { size: sz, weight: 800, ls: -1.2 }); },
  cleanPill,
];

const capStyles = {
  draw(R, s, t) {
    const { ctx } = R, a = envA(s, t); if (a <= .002 || !R.allChunks) return;
    const n = Math.min(s.n || 20, STYLES.length), y = s.y ?? 1180;
    let c = null; for (const ch of R.allChunks) if (ch.start - .02 <= t) c = ch; else break;
    const k = t < s.cycleFrom ? 0 : Math.min(n - 1, Math.floor(seg(t, s.cycleFrom, s.cycleTo) * n * .9999));
    const showCap = c && t >= s.from - .1 && (t <= c.end + .4 || t < s.cycleTo);
    alpha(ctx, a, () => {
      // fade per chunk only: style switches cut hard (each lasts ~.25 s)
      if (showCap) { const p = S(t - c.start + .12, 30); alpha(ctx, Math.min(1, p * 1.4), () => { ctx.translate(0, (1 - p) * 18); STYLES[k](ctx, c, y, t); }); }
      // counter + dot rail, only once the cycling starts
      const q = S(t - s.cycleFrom + .15, 14); if (q <= .002) return;
      alpha(ctx, q, () => {
        const cy = s.counterY ?? 300; ctx.translate(0, (1 - q) * 30);
        chip(ctx, W / 2, cy, `Style ${String(k + 1).padStart(2, '0')} / ${n}`, { size: 44, h: 92, weight: 800, ls: -.5 });
        const gap = 34, x0 = W / 2 - (n - 1) * gap / 2;
        for (let i = 0; i < n; i++) { ctx.beginPath(); ctx.arc(x0 + i * gap, cy + 84, i === k ? 10 : 7, 0, TAU); ctx.fillStyle = i <= k ? C.blue : 'rgba(252,251,248,.85)'; ctx.fill(); }
      });
    });
  },
};

// ---------------------------------------------------------------- camTile (over)
// {layer: 'over', from, to, w: 460, h: 580, keys: [[t, [cx, cy]]], labelKeys: [[t, 'En haut']], r: 24, zoom: 1}
// The camera in a paper frame; it glides to each key. The label chip sits mirrored across the screen centre.
// r = corner radius (w / 2 on a square tile = a round bubble), zoom > 1 frames the face tighter.
// sizeKeys: [[t, [w, h], spring?]] animates the tile size (e.g. full frame shrinking into a picture-in-picture);
// frame: 'line' drops the paper sheet for a bare rounded window with a 1px border (lineColor), no shadow, no rise.
// cut: true enters at full opacity on `from` (a hard cut, e.g. a full-frame camera that then shrinks to reveal what is under it).
const camTile = {
  draw(R, s, t) {
    const { ctx } = R, a = s.cut ? (t < s.from ? 0 : 1 - leave(t - (s.to ?? 1e9))) : envA(s, t); if (a <= .002) return;
    const [w, h] = s.sizeKeys ? track(t, s.sizeKeys, 9) : [s.w || 460, s.h || 580];
    const x = track(t, s.keys.map(([k, v]) => [k, v[0]]), 9), y = track(t, s.keys.map(([k, v]) => [k, v[1]]), 9);
    const rise = s.frame === 'line' ? 0 : 1 - S(t - s.from + (s.pre || 0), 12), [, , CW, CH] = R.spec.cam?.crop || [0, 0, 1200, 1080], eyes = R.spec.cam?.eyes || [600, 400];
    alpha(ctx, Math.min(1, a * 1.3), () => {
      ctx.translate(0, rise * 80);
      const r = s.r ?? 24;
      if (s.frame !== 'line') sheet(ctx, x - w / 2 - 14, y - h / 2 - 14, w + 28, h + 28, r + 12, { elev: 1.4 });
      cover(ctx, R.cam, x - w / 2, y - h / 2, w, h, r, [eyes[0] / CW, clamp(eyes[1] / CH + .08)], s.zoom ?? 1);
      if (s.frame === 'line') { ctx.beginPath(); ctx.roundRect(x - w / 2 + .5, y - h / 2 + .5, w - 1, h - 1, r); ctx.lineWidth = 1; ctx.strokeStyle = s.lineColor || 'rgba(255,255,255,.22)'; ctx.stroke(); }
      // label: newest key wins, cross-fade
      let cur = null, at = -1e9; for (const [k, v] of s.labelKeys || []) if (t >= k) { cur = v; at = k; }
      if (cur) {
        const p = S(t - at, 16), lx = lerp(W / 2, W - x, .9), ly = lerp(H / 2, H - y, .75);
        chip(ctx, clamp(lx, 260, W - 260), ly + (1 - p) * 24, cur, { size: 48, h: 104, weight: 800, dot: C.blue, alpha: Math.min(1, p * 1.4) });
      }
    });
  },
};

// ---------------------------------------------------------------- camSplit (over)
// {layer: 'over', from, to, h: 820, enterFrom: 1240, dur: .7}
// The camera panel slides from its split slot (top = enterFrom, the seam before) up to the top of the frame, h tall,
// with the same torn paper edge and a soft shadow; the paper below is free for an 'over' board drawn after it.
// Pair it with a layout key [from, 1920, 400] (the bottom camera leaves at once, this panel replaces it pixel for
// pixel) and captions.yKeys [[from, h + 60]] so the captions sit on the split line.
const camSplit = {
  draw(R, s, t) {
    const { ctx } = R; if (t < s.from || !R.cam || !R.camFit) return;
    const a = 1 - leave(t - (s.to ?? 1e9)); if (a <= .002) return;
    const h = s.h || 820, e0 = s.enterFrom ?? 1240, p = E.io(seg(t, s.from, s.from + (s.dur ?? .7)));
    const top = lerp(e0, 0, p), bot = lerp(H, h, p);
    const A = R.camFit(e0), B = R.camFit(H - h); B.y0 -= H - h;
    const T = { s: lerp(A.s, B.s, p), x0: lerp(A.x0, B.x0, p), y0: lerp(A.y0, B.y0, p) };
    alpha(ctx, a, () => {
      if (bot < H - 2) {   // shadow the panel casts on the paper under its torn edge
        const g = ctx.createLinearGradient(0, bot - 6, 0, bot + 46); g.addColorStop(0, 'rgba(40,28,10,.22)'); g.addColorStop(1, 'rgba(40,28,10,0)');
        ctx.fillStyle = g; ctx.fillRect(0, bot - 6, W, 52);
      }
      ctx.save(); ctx.beginPath(); ctx.rect(0, top, W, H - top); ctx.clip(); if (bot < H - 2) ctx.clip(R.camEdge(bot, false));
      ctx.drawImage(R.cam, T.x0, T.y0, R.CW * T.s, R.CHh * T.s); ctx.restore();
    });
  },
};

export const META = { capStyles, camTile, camSplit };
// the same 20 looks as live captions (spec.captions.style, names in lib/style.js CAPTION_STYLES)
export const CAPTION_DRAW = STYLES;
