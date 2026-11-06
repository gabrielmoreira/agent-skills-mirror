// Clean scenes: the "AI OS explainer" look (layout.card + paper.bg 'clean', first used by short-claude-5x-value-clean).
// One slide = one idea held 6 to 14 s: an accent eyebrow, a heavy 2-line headline that stays put, and white glass cards
// in the zone under it (y 500 to 880) that build up on the narrator's words. Times are SHORT time (mapped by mapSpec).
//   slide (stage) {from, to, pre, eyebrow, title: [l1, l2] | 'one line', hl: ['word'], size: 90, y: 350, items: [...]}
// Items use absolute 1080 px coords. Each takes {at, outAt, dimAt, ringAt}; at defaults to from - pre + .25 + i * .12.
//   card  {x, y, w, h, r}                       empty glass card
//   row   {x, y, w, h, logo, round, title, sub, pill, pillBlue, pillAlt, strikeAt}
//   stat  {x, y, w, h, logo, name, plan, value, dec, prefix, suffix, countAt, until, sub, badge, badgeAt, badgeTop, win, ghost, ghostAt}
//         ghost: a pale '?' card from ghostAt (default: slide start) that fills in at `at`
//   bars  {x, y, w, h, gap, max, rows: [{logo, label, sub, value, dec, suffix, at, countAt, until, win}]}
//   tweet {x, y, w, img, name, handle, text}     compact one-line tweet: avatar, name, handle, quote on the right
//   logo  {x, y, s, logo, tile, label}           (x, y = center)
//   img   {x, y, w, h, img}                      contain, (x, y = center)
//   pill  {x, y, text, blue, size, logo}         (x, y = center)
//   text  {x, y, text, size, weight, color: 'blue' | 'ink2' | 'ink3', align}
//   arrow {x, y, w, blue}                        horizontal, draws in from x
import { C, clamp, lerp, S, E, text, measure, midBase } from './kit.js';
import * as K from './kit.js';

const TAU = Math.PI * 2;
const rgba = (hex, a) => `rgba(${K.hexRGB(hex).join(',')},${a})`;
const hair = a => `rgba(${K.edgeRGB()},${a})`;
const fmt = (v, dec = 0) => { const [i, d] = Math.abs(v).toFixed(dec).split('.'); return (v < 0 ? '-' : '') + i.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + (d ? ',' + d : ''); };
const count = (it, t, at) => { const a = it.countAt ?? at, b = it.until ?? a + 1.2; return E.cubic(clamp((t - a) / Math.max(.05, b - a))); };
const addFilter = (ctx, f) => { ctx.filter = ctx.filter && ctx.filter !== 'none' ? ctx.filter + ' ' + f : f; };

// a white glass card: wide soft cool shadow, tight contact shadow, 1.5 px hairline
function glass(ctx, x, y, w, h, r = 28, o = {}) {
  K.shadow(ctx, x, y, w, h, r, 34, o.sh ?? .085, 12); K.shadow(ctx, x, y, w, h, r, 4, .05, 1.5);
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = o.fill || C.white; ctx.fill();
  ctx.strokeStyle = hair(.08); ctx.lineWidth = 1.5; ctx.stroke();
}
function ring(ctx, x, y, w, h, r, p) {
  if (p <= .002) return;
  ctx.save(); ctx.globalAlpha *= p; ctx.strokeStyle = C.blue; ctx.lineWidth = 3; ctx.shadowColor = rgba(C.blue, .35); ctx.shadowBlur = 18;
  ctx.beginPath(); ctx.roundRect(x - 6, y - 6, w + 12, h + 12, r + 6); ctx.stroke(); ctx.restore();
}
// a real logo (x, y = top left): contain in a rounded square (or a circle for avatars), hairline so white logos keep an edge
function logo(R, ctx, src, x, y, size, o = {}) {
  const im = R.img('/p/' + src); if (!im) return;
  const r = o.round ? size / 2 : o.r ?? size * .24;
  ctx.save(); if (o.gray) addFilter(ctx, `grayscale(${o.gray.toFixed(3)})`);
  if (o.round) K.cover(ctx, im, x, y, size, size, r);
  else {
    const k = Math.min(size / im.width, size / im.height), w = im.width * k, h = im.height * k;
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, size, size, r); ctx.clip(); ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(im, x + (size - w) / 2, y + (size - h) / 2, w, h); ctx.restore();
  }
  ctx.restore();
  ctx.beginPath(); ctx.roundRect(x + .5, y + .5, size - 1, size - 1, r); ctx.strokeStyle = hair(.10); ctx.lineWidth = 1; ctx.stroke();
}
// pale rounded label, (x, y) = center unless o.align 'left' | 'right'. Returns its width.
function pill(R, ctx, x, y, label, o = {}) {
  const size = o.size || 22, h = o.h || Math.round(size * 2), wt = o.weight || 600, padX = Math.round(size * .8), lg = o.logo ? size * 1.3 : 0;
  const w = measure(ctx, label, size, wt, -.2) + padX * 2 + (lg ? lg + size * .45 : 0);
  const X = o.align === 'left' ? x : o.align === 'right' ? x - w : x - w / 2;
  ctx.beginPath(); ctx.roundRect(X, y - h / 2, w, h, h / 2);
  ctx.fillStyle = o.solid ? C.blue : o.blue ? rgba(C.blue, .11) : '#EEF2F6'; ctx.fill();
  if (o.logo) logo(R, ctx, o.logo, X + padX * .8, y - lg / 2, lg, { r: lg * .28 });
  text(ctx, label, X + padX + (lg ? lg + size * .2 : 0), midBase(y, size), { size, weight: wt, ls: -.2, color: o.solid ? '#fff' : o.blue ? C.blue : C.ink2 });
  return w;
}

// ---------------------------------------------------------------- items
const ITEMS = {
  card(R, ctx, it, e) { glass(ctx, it.x, it.y, it.w, it.h, it.r ?? 30); ring(ctx, it.x, it.y, it.w, it.h, it.r ?? 30, e.ring); },

  row(R, ctx, it, e, t) {
    const { x, y, w } = it, h = it.h ?? 124, r = it.r ?? 28, ic = it.icon ?? 72, ix = x + 26, mid = y + h / 2;
    glass(ctx, x, y, w, h, r);
    if (it.logo) logo(R, ctx, it.logo, ix, mid - ic / 2, ic, { round: it.round, gray: e.dim });
    const tx = it.logo ? ix + ic + 24 : x + 30, ty = it.sub ? mid - 6 : midBase(mid, 30);
    text(ctx, it.title || '', tx, ty, { size: 30, weight: 700, ls: -.6, color: e.dim > .5 ? C.ink3 : C.ink });
    if (it.sub) text(ctx, it.sub, tx, mid + 30, { size: 22, weight: 500, ls: -.2, color: C.ink2 });
    const st = it.strikeAt != null ? S(t - it.strikeAt, 11) : 0;
    if (st > .002) {
      const tw = measure(ctx, it.title || '', 30, 700, -.6), sy = ty - 30 * .34;
      ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(tx - 4, sy); ctx.lineTo(tx - 4 + (tw + 8) * st, sy); ctx.stroke(); ctx.restore();
    }
    if (it.pill) {
      const sw = it.pillAlt ? st : 0;
      if (sw < 1) { ctx.save(); ctx.globalAlpha *= 1 - sw; pill(R, ctx, x + w - 26, mid, it.pill, { align: 'right', blue: it.pillBlue }); ctx.restore(); }
      if (sw > 0) { ctx.save(); ctx.globalAlpha *= sw; pill(R, ctx, x + w - 26, mid, it.pillAlt, { align: 'right', solid: true }); ctx.restore(); }
    }
    ring(ctx, x, y, w, h, r, e.ring);
  },

  stat(R, ctx, it, e, t) {
    const { x, y, w } = it, h = it.h ?? 250, r = it.r ?? 30;
    const fill = it.ghost ? S(t - it.at, 12) : 1, gray = Math.max(e.dim, 1 - fill);
    glass(ctx, x, y, w, h, r, { fill: fill < 1 ? `rgba(255,255,255,${lerp(.55, 1, fill)})` : null });
    if (it.logo) logo(R, ctx, it.logo, x + 24, y + 24, 56, { gray });
    text(ctx, it.name || '', x + 96, y + 50, { size: 26, weight: 700, ls: -.5, color: gray > .5 ? C.ink3 : C.ink });
    if (it.plan) text(ctx, it.plan, x + 96, y + 77, { size: 20, weight: 500, ls: -.2, color: C.ink2 });
    const cp = count(it, t, it.at), va = it.countAt != null ? S(t - it.countAt, 16) : fill, sz = it.size ?? 70;
    if (it.ghost && va < 1) text(ctx, '?', x + 26, y + 172, { size: sz, weight: 800, ls: -2, color: C.dim, alpha: 1 - va });
    if (va > .002) text(ctx, (it.prefix || '') + fmt((it.value || 0) * cp, it.dec) + (it.suffix ?? ' $'), x + 26, y + 172, { size: sz, weight: 800, ls: -2.6, color: it.win ? C.blue : C.ink, alpha: va });
    if (it.sub) text(ctx, it.sub, x + 26, y + 212, { size: 21, weight: 500, ls: -.2, color: C.ink2, alpha: Math.max(.35, va) });
    if (it.badge) { const b = it.badgeAt != null ? S(t - it.badgeAt, 13) : 1;
      if (b > .002) { ctx.save(); ctx.globalAlpha *= Math.min(1, b * 1.3); ctx.translate(0, (1 - b) * 10); pill(R, ctx, x + w - 22, it.badgeTop ? y + 52 : y + h - 46, it.badge, { align: 'right', size: 28, weight: 800, solid: it.win, blue: !it.win }); ctx.restore(); } }
    ring(ctx, x, y, w, h, r, e.ring);
  },

  bars(R, ctx, it, e, t, s, i0) {
    const { x, w } = it, h = it.h ?? 118, gap = it.gap ?? 16, max = it.max || Math.max(...it.rows.map(r => r.value));
    it.rows.forEach((rw, j) => {
      const at = rw.at ?? e.at + j * .12, p = S(t - at, 13); if (p <= .002) return;
      const y = it.y + j * (h + gap) + (1 - p) * 20, mid = y + 50;
      ctx.save(); ctx.globalAlpha *= Math.min(1, p * 1.3);
      glass(ctx, x, y, w, h, 28);
      if (rw.logo) logo(R, ctx, rw.logo, x + 24, y + (h - 64) / 2, 64);
      const tx = x + 108;
      text(ctx, rw.label, tx, mid, { size: 28, weight: 700, ls: -.5 });
      if (rw.sub) text(ctx, rw.sub, tx + measure(ctx, rw.label, 28, 700, -.5) + 14, mid, { size: 21, weight: 500, ls: -.2, color: C.ink2 });
      const cp = count(rw, t, at + .2), va = S(t - (rw.countAt ?? at + .2), 16);
      const tw = w - 108 - 28, ty = y + h - 38;
      ctx.beginPath(); ctx.roundRect(tx, ty, tw, 16, 8); ctx.fillStyle = '#EDF1F5'; ctx.fill();
      const fw = tw * clamp(rw.value / max) * cp;
      if (fw > 1) { ctx.beginPath(); ctx.roundRect(tx, ty, Math.max(16, fw), 16, 8); ctx.fillStyle = rw.win ? C.blue : '#A9B2BD'; ctx.fill(); }
      if (va > .002) text(ctx, (rw.prefix || '') + fmt(rw.value * cp, rw.dec) + (rw.suffix ?? ' $'), x + w - 28, mid + 2, { size: 38, weight: 800, ls: -1.4, align: 'right', color: rw.win ? C.blue : C.ink, alpha: va });
      ring(ctx, x, y, w, h, 28, rw.ringAt != null ? S(t - rw.ringAt, 12) : 0);
      ctx.restore();
    });
  },

  tweet(R, ctx, it, e) {
    const { x, y, w } = it, h = it.h ?? 96, mid = y + h / 2;
    glass(ctx, x, y, w, h, 26);
    if (it.img) logo(R, ctx, it.img, x + 20, mid - 28, 56, { round: true });
    text(ctx, it.name || '', x + 92, mid - 4, { size: 24, weight: 700, ls: -.4 });
    if (it.handle) text(ctx, it.handle, x + 92, mid + 24, { size: 20, weight: 500, color: C.ink2 });
    if (it.text) text(ctx, '« ' + it.text + ' »', x + w - 28, midBase(mid, 28), { size: 28, weight: 600, ls: -.4, align: 'right', color: C.ink });
  },

  logo(R, ctx, it, e) {
    const s = it.s ?? 120, x = it.x - s / 2, y = it.y - s / 2;
    if (it.tile) {
      const T = s * 1.34, X = it.x - T / 2, Y = it.y - T / 2;
      glass(ctx, X, Y, T, T, T * .26); logo(R, ctx, it.logo, x, y, s, { gray: e.dim }); ring(ctx, X, Y, T, T, T * .26, e.ring);
    } else { ctx.save(); K.drop(ctx, .10, 24, 8); logo(R, ctx, it.logo, x, y, s, { gray: e.dim }); ctx.restore(); ring(ctx, x, y, s, s, s * .24, e.ring); }
    if (it.label) text(ctx, it.label, it.x, it.y + (it.tile ? s * .67 : s / 2) + 46, { size: it.labelSize ?? 30, weight: 700, ls: -.6, align: 'center', color: e.dim > .5 ? C.ink3 : C.ink });
  },

  img(R, ctx, it, e) {
    const im = R.img('/p/' + it.img); if (!im) return;
    const k = Math.min(it.w / im.width, it.h / im.height), w = im.width * k, h = im.height * k;
    ctx.save(); if (e.dim) addFilter(ctx, `grayscale(${e.dim.toFixed(3)})`); ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(im, it.x - w / 2, it.y - h / 2, w, h); ctx.restore();
  },

  pill(R, ctx, it) {
    const sz = it.size ?? 30;
    ctx.save(); if (it.lift !== false) { const w = measure(ctx, it.text, sz, 700, -.2) + sz * 1.6 + (it.logo ? sz * 1.75 : 0), h = Math.round(sz * 2); K.shadow(ctx, it.x - w / 2, it.y - h / 2, w, h, h / 2, 22, .07, 8); }
    pill(R, ctx, it.x, it.y, it.text, { size: sz, weight: 700, solid: it.blue, logo: it.logo }); ctx.restore();
  },

  text(R, ctx, it) {
    const color = it.color === 'blue' ? C.blue : it.color === 'ink2' ? C.ink2 : it.color === 'ink3' ? C.ink3 : C.ink;
    text(ctx, it.text, it.x, it.y, { size: it.size ?? 34, weight: it.weight ?? 700, ls: it.ls ?? -.6, align: it.align || 'center', color });
  },

  arrow(R, ctx, it, e) {
    const p = e.p, x2 = it.x + it.w * p, y = it.y; if (p <= .01) return;
    ctx.save(); ctx.strokeStyle = it.blue ? C.blue : C.ink3; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(it.x, y); ctx.lineTo(x2, y); ctx.moveTo(x2 - 18, y - 18); ctx.lineTo(x2, y); ctx.lineTo(x2 - 18, y + 18); ctx.stroke(); ctx.restore();
  },
};

// ---------------------------------------------------------------- slide
function headline(ctx, s, t, t0) {
  const lines = Array.isArray(s.title) ? s.title : s.title ? [s.title] : [], hl = new Set((s.hl || []).map(w => w.toLowerCase()));
  const base = s.size ?? 90, maxW = s.maxW ?? 960, wt = 800;
  let size = base; const widest = Math.max(0, ...lines.map(l => measure(ctx, l, base, wt, -3.5)));
  if (widest > maxW) size = base * maxW / widest;
  const ls = -3.5 * size / 90, y0 = s.y ?? (lines.length > 1 ? 350 : 395);
  lines.forEach((line, i) => {
    const p = S(t - (t0 + .06 + i * .08), 12); if (p <= .002) return;
    const ws = line.split(' '), sp = measure(ctx, ' ', size, wt, ls), ww = ws.map(w => measure(ctx, w, size, wt, ls));
    let x = 540 - (ww.reduce((a, b) => a + b, 0) + sp * (ws.length - 1)) / 2;
    const y = y0 + i * size * 1.0 + (1 - p) * 22, b = (1 - p) * 8;
    ctx.save(); ctx.globalAlpha *= Math.min(1, p * 1.3); if (b > .4) addFilter(ctx, `blur(${b.toFixed(1)}px)`);
    ws.forEach((w, j) => { text(ctx, w, x, y, { size, weight: wt, ls, color: hl.has(w.toLowerCase().replace(/[.,:;!?]+$/, '')) ? C.blue : C.ink }); x += ww[j] + sp; });
    ctx.restore();
  });
}

function slide(R, s, t) {
  const ctx = R.ctx, t0 = s.from - (s.pre || 0), out = s.to != null ? S(t - (s.to - .1), 22) : 0;
  if (out > .995) return;
  ctx.save(); ctx.globalAlpha *= 1 - out; if (out > .02) addFilter(ctx, `blur(${(out * 10).toFixed(1)}px)`);
  if (s.eyebrow) {
    const p = S(t - t0, 12);
    if (p > .002) text(ctx, s.eyebrow, 540, midBase(s.eyebrowY ?? 231, 30) + (1 - p) * 14, { size: 30, weight: 600, ls: -.3, align: 'center', color: C.blue, alpha: Math.min(1, p * 1.3) });
  }
  headline(ctx, s, t, t0);
  (s.items || []).forEach((it, i) => {
    const at = it.at ?? t0 + .25 + i * .12, p = S(t - at, 13); if (p <= .002 && !it.ghost) return;
    const o = it.outAt != null ? S(t - it.outAt, 18) : 0; if (o > .995) return;
    const pe = it.ghost ? Math.max(p, S(t - (it.ghostAt ?? t0 + .25 + i * .12), 13)) : p;
    const e = { at, p, dim: it.dimAt != null ? S(t - it.dimAt, 10) : 0, ring: it.ringAt != null ? S(t - it.ringAt, 12) : 0 };
    const blur = (1 - pe) * 7 + o * 5;
    ctx.save(); ctx.globalAlpha *= Math.min(1, pe * 1.3) * (1 - o) * (1 - .4 * e.dim); ctx.translate(0, (1 - pe) * 24 - o * 10);
    if (blur > .4) addFilter(ctx, `blur(${blur.toFixed(1)}px)`);
    if (it.k === 'bars') ITEMS.bars(R, ctx, it, e, t, s, i); else ITEMS[it.k]?.(R, ctx, it, e, t, s);
    ctx.restore();
  });
  ctx.restore();
}

export const CLEAN = { slide: { draw: slide } };
