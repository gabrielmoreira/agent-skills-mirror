// Faceless scenes: an audio-only video carried by die-cut photo stickers of the creator's head on moving paper
// (first used by short-faceless-1). Same contract as scenes.js, times already mapped to SHORT time.
//   paperFlow  full-frame textured paper that drifts all video long, with a few paper cut-outs floating over it.
//              {from: 0, to, grain 1.35, shapes: true}. Put it first in `scenes` with layout [[0, 1920]].
//   talkHead   the speaker as a sticker head that moves while he talks (no lip-sync): it nods on each word, floats,
//              and gets livelier while words are being said. `face` is the default sticker, `emo` swaps it on beats.
//              {dir: 'assets/stickers/', face, emo: [{from, to, img}], posKeys [[t, [x, top, w]]],
//               body: {at, armsAt, danceAt, shirt, pants, bpm 118}, crew: [{img, at, x, top, w, shirt, pants, phase}]}
//              body grows a paper-cut torso, legs and arms under the head (die-cut white outline like the stickers);
//              danceAt starts a disco-point dance on the beat. crew = friends' sticker heads that pop in and dance too.
//              Stickers: transparent PNGs cut by faceless-stickers/files/cutout.py (same width, head top = bbox top).
//   bgPattern  {from, to, keys: [[at, 'squares' | 'diamonds' | 'stripes' | 'none']], x 540, y 1500, a 1}: the paper
//              background changes pattern on the beat, each new one wipes in as a circle growing from (x, y).
//   disco      {at (drop), to, x 540, y 250, r 130, spotsAt}: a mirror ball lowers on its string from the top and
//              spins; light spots sweep the paper.
//   dancefloor {at, to, y0 1360, rows 5, cols 7, bpm 118}: perspective tile floor that unfolds back to front and
//              lights tiles on the beat.
import { C, W, H, clamp, lerp, S, leave, hash, noise1, makePaper, relief, drop } from './kit.js';

const TAU = Math.PI * 2;
const SKIN = '#E2B08C';
const col = c => (c && C[c]) || c || C.ink;
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
const envA = (s, t) => (s.from <= 0 ? 1 : S(t - s.from, 12)) * (1 - leave(t - (s.to ?? 1e9)));

// ---------------------------------------------------------------- paperFlow
let PF = null;
const PW = 1320, PH = 2200;
function paperCanvas(grain) {
  if (PF) return PF;
  PF = makePaper(PW, PH, C.paper, 41, grain);
  relief(PF, 2.5, .18, 43); relief(PF, 70, .07, 47);   // tooth + soft cockle you can see moving
  return PF;
}
const SHAPES = [   // [kind, x, y, size, fill] around the edges, the centre stays free for the head
  ['circle', 120, 260, 120, 'sheet'], ['rect', 960, 210, 150, 'tint'], ['blob', 70, 1180, 170, 'sheet'],
  ['rect', 1010, 1020, 110, 'sheet'], ['circle', 980, 1640, 90, 'tint'], ['dot', 170, 1760, 34, 'blue'],
  ['blob', 880, 1500, 120, 'sheet'], ['dot', 930, 640, 22, 'blue'],
];
function shapePath(ctx, kind, s, seed) {
  ctx.beginPath();
  if (kind === 'circle' || kind === 'dot') ctx.arc(0, 0, s / 2, 0, TAU);
  else if (kind === 'rect') ctx.roundRect(-s / 2, -s / 2, s, s, s * .22);
  else { const n = 9; for (let i = 0; i <= n; i++) { const a = i / n * TAU, r = s / 2 * (.78 + .3 * hash(seed + i % n)); ctx[i ? 'lineTo' : 'moveTo'](Math.cos(a) * r, Math.sin(a) * r); } ctx.closePath(); }
}
const paperFlow = {
  draw(R, s, t) {
    const { ctx } = R, P = paperCanvas(s.grain ?? 1.35);
    const mx = (PW - W) / 2, my = (PH - H) / 2;
    const ox = -mx + (noise1(t * .11 + 2) - .5) * 2 * mx * .9, oy = -my + (noise1(t * .09 + 7) - .5) * 2 * my * .9;
    const k = 1 + .025 * Math.sin(t * .23);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(k, k); ctx.rotate(Math.sin(t * .17) * .012); ctx.translate(-W / 2, -H / 2);
    ctx.drawImage(P, ox, oy); ctx.restore();
    // a slow light falloff sweeping across, so the sheet feels lit
    const lx = W * (.3 + .4 * noise1(t * .07)), g = ctx.createRadialGradient(lx, -200, 0, lx, -200, H * 1.1);
    g.addColorStop(0, 'rgba(255,255,255,.22)'); g.addColorStop(.6, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(70,52,25,.035)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    if (s.shapes === false) return;
    SHAPES.forEach(([kind, x, y, sz, fill], i) => {
      const dx = (noise1(t * .16 + i * 13) - .5) * 70, dy = (noise1(t * .13 + i * 7 + 50) - .5) * 90, rot = (noise1(t * .1 + i * 3) - .5) * .9;
      const a = s.shapesA ?? 1;
      alpha(ctx, a, () => {
        ctx.translate(x + dx, y + dy); ctx.rotate(rot);
        drop(ctx, kind === 'dot' ? .16 : .2, kind === 'dot' ? 8 : 26, kind === 'dot' ? 3 : 10);
        shapePath(ctx, kind, sz, i * 11); ctx.fillStyle = fill === 'sheet' ? C.sheet : col(fill); ctx.fill();
        ctx.shadowColor = 'transparent';
        if (kind !== 'dot') { const gl = ctx.createLinearGradient(0, -sz / 2, 0, sz / 2); gl.addColorStop(0, 'rgba(255,255,255,.55)'); gl.addColorStop(.4, 'rgba(255,255,255,0)'); gl.addColorStop(1, 'rgba(60,44,20,.06)'); ctx.fillStyle = gl; ctx.fill(); }
      });
    });
  },
};

// ---------------------------------------------------------------- bgPattern
// light paper-on-paper patterns: blue tint cells + faint ink seams, drifting slowly so the frame stays alive
function patternFill(ctx, kind, t) {
  const tint = 'rgba(37,142,255,.085)', seam = 'rgba(20,22,27,.06)';
  ctx.save();
  if (kind === 'squares' || kind === 'diamonds') {
    const g = kind === 'squares' ? 135 : 150, d = (t * 16) % (2 * g);
    ctx.translate(W / 2, H / 2); if (kind === 'diamonds') ctx.rotate(Math.PI / 4); ctx.translate(d - 2 * g, d * .5 - 2 * g);
    const R0 = Math.ceil(1250 / g) + 2;
    ctx.fillStyle = tint;
    for (let i = -R0; i <= R0; i++) for (let j = -R0; j <= R0; j++) if ((i + j) & 1) ctx.fillRect(i * g, j * g, g, g);
    ctx.strokeStyle = seam; ctx.lineWidth = 2; ctx.beginPath();
    for (let i = -R0; i <= R0 + 1; i++) { ctx.moveTo(i * g, -R0 * g); ctx.lineTo(i * g, (R0 + 1) * g); ctx.moveTo(-R0 * g, i * g); ctx.lineTo((R0 + 1) * g, i * g); }
    ctx.stroke();
  } else if (kind === 'stripes') {
    const g = 96, d = (t * 22) % (2 * g);
    ctx.fillStyle = tint;
    for (let x = d - 2 * g; x < W + g; x += 2 * g) ctx.fillRect(x, 0, g, H);
    ctx.strokeStyle = seam; ctx.lineWidth = 2; ctx.beginPath();
    for (let x = d - 2 * g; x < W + g; x += g) { ctx.moveTo(x, 0); ctx.lineTo(x, H); }
    ctx.stroke();
  }
  ctx.restore();
}
const bgPattern = {
  draw(R, s, t) {
    const { ctx } = R, a = envA(s, t) * (s.a ?? 1); if (a <= .002) return;
    const K = (s.keys || []).filter(k => k[0] <= t); if (!K.length) return;
    const cur = K.at(-1), prev = K.at(-2), p = S(t - cur[0], 5), x = s.x ?? 540, y = s.y ?? 1500;
    alpha(ctx, a, () => {
      const r = 2300 * p;
      if (prev && p < .999) {   // the old pattern stays outside the growing circle
        ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.arc(x, y, r, 0, TAU); ctx.clip('evenodd'); patternFill(ctx, prev[1], t); ctx.restore();
      }
      ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.clip(); patternFill(ctx, cur[1], t); ctx.restore();
      if (p > .01 && p < .98) { ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.strokeStyle = `rgba(37,142,255,${.5 * (1 - p)})`; ctx.lineWidth = 10; ctx.stroke(); }
    });
  },
};

// ---------------------------------------------------------------- talkHead
const url = (s, n) => '/p/' + (s.dir || 'assets/stickers/') + n + '.png';
// one face at a time (no lip-sync): `face` by default, `emo` overrides it on emotional beats
function faceAt(s, t) {
  for (const e of s.emo || []) if (t >= e.from && t < e.to) return { img: e.img, key: 'e' + e.from };
  return { img: s.face, key: 'face' };
}
// speaking energy: 1 while a word is being said, eases back to 0 in the gaps
function talkingAt(t, words) {
  let v = 0;
  for (const w of words) { if (w.start > t + .1) break; if (t - w.end > .5) continue; v = Math.max(v, S(t - w.start + .05, 18) * (1 - S(t - w.end - .08, 9))); }
  return v;
}
// smooth nod: rises in ~.09 s, decays over ~.3 s, peak 1. No overshoot.
const nodK = x => x <= 0 ? 0 : (x / .09) * Math.exp(1 - x / .09);
function nodAt(t, words) {
  let v = 0, dir = 0;
  for (let i = 0; i < words.length; i++) {
    const w = words[i]; if (w.start > t) break; if (t - w.start > .8) continue;
    const k = nodK(t - w.start) * (.55 + .45 * hash(i + .5)); v += k; dir += k * (hash(i * 1.7) > .5 ? 1 : -1);
  }
  return { v: Math.min(1.3, v), dir: clamp(dir, -1, 1) };
}

// One dancer: paper-cut body under a sticker head. Local origin = neck point; u = head width.
function limb(ctx, pts, lw, color, bw) {
  ctx.beginPath(); pts.forEach(([x, y], i) => ctx[i ? 'lineTo' : 'moveTo'](x, y));
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (bw) { ctx.strokeStyle = C.white; ctx.lineWidth = lw + 2 * bw; } else { ctx.strokeStyle = color; ctx.lineWidth = lw; }
  ctx.stroke();
}
const arm = (sx, sy, a, bend, L1, L2, side) => {
  const ex = sx + Math.sin(a) * L1 * side, ey = sy + Math.cos(a) * L1, b = a + bend;
  return [[sx, sy], [ex, ey], [ex + Math.sin(b) * L2 * side, ey + Math.cos(b) * L2]];
};
function bodyParts(ctx, o, t, pass) {
  const u = o.u, bp = o.bodyP, ap = o.armsP, dp = o.danceP, b = t * (o.bpm || 118) / 60 + (o.phase || 0);
  const sway = Math.sin(Math.PI * b) * .1 * u * dp, bw = pass === 'outline' ? .045 * u : 0;
  const shirt = col(o.shirt || 'blue'), pants = col(o.pants || 'ink');
  // legs (from the hips), knees pump on the beat
  const hipY = .98 * u * bp, kb = (1 - Math.cos(TAU * b)) / 2 * dp;
  if (bp > .05) for (const sd of [-1, 1]) {
    const hx = sd * .2 * u + sway * .4, L = .46 * u * bp;
    const kx = hx + sd * .05 * u + Math.sin(Math.PI * b + (sd > 0 ? 0 : Math.PI)) * .07 * u * dp, ky = hipY + L - .08 * u * kb;
    const fx = hx + sd * .06 * u, fy = ky + L;
    limb(ctx, [[hx, hipY - .1 * u], [kx, ky], [fx, fy]], .27 * u * Math.max(.3, bp), pants, bw);
    if (pass !== 'outline') { ctx.beginPath(); ctx.ellipse(fx + sd * .07 * u, fy + .05 * u, .17 * u * bp, .08 * u * bp, 0, 0, TAU); ctx.fillStyle = C.ink; ctx.fill(); }
    else { ctx.beginPath(); ctx.ellipse(fx + sd * .07 * u, fy + .05 * u, .17 * u * bp + bw, .08 * u * bp + bw, 0, 0, TAU); ctx.fillStyle = C.white; ctx.fill(); }
  }
  // torso: shoulders wide, slightly narrower waist, rotates with the hips
  const tw = .98 * u, th = 1.02 * u * bp, wx = .74 * u;
  ctx.save(); ctx.rotate(Math.sin(Math.PI * b) * .05 * dp);
  ctx.beginPath();
  ctx.moveTo(-tw / 2 + .12 * u, -.04 * u); ctx.lineTo(tw / 2 - .12 * u, -.04 * u);
  ctx.quadraticCurveTo(tw / 2, -.02 * u, tw / 2, .16 * u);
  ctx.lineTo(wx / 2 + sway * .3, th); ctx.quadraticCurveTo(wx / 2 + sway * .3, th + .08 * u, wx / 2 - .1 * u + sway * .3, th + .08 * u);
  ctx.lineTo(-wx / 2 + .1 * u + sway * .3, th + .08 * u); ctx.quadraticCurveTo(-wx / 2 + sway * .3, th + .08 * u, -wx / 2 + sway * .3, th);
  ctx.lineTo(-tw / 2, .16 * u); ctx.quadraticCurveTo(-tw / 2, -.02 * u, -tw / 2 + .12 * u, -.04 * u); ctx.closePath();
  if (pass === 'outline') { ctx.lineJoin = 'round'; ctx.strokeStyle = C.white; ctx.lineWidth = 2 * bw; ctx.stroke(); ctx.fillStyle = C.white; ctx.fill(); }
  else {
    ctx.fillStyle = shirt; ctx.fill();
    const g = ctx.createLinearGradient(-tw / 2, 0, tw / 2, 0); g.addColorStop(0, 'rgba(255,255,255,.16)'); g.addColorStop(.5, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,.14)');
    ctx.fillStyle = g; ctx.fill();
    ctx.beginPath(); ctx.ellipse(0, -.03 * u, .2 * u, .09 * u, 0, 0, Math.PI); ctx.fillStyle = SKIN; ctx.fill();   // neck opening
  }
  // arms: disco point, swapping sides every 2 beats, forearms pump on the beat
  if (ap > .02) for (const sd of [-1, 1]) {
    const q = (Math.sin(Math.PI * b / 2 + (sd > 0 ? 0 : Math.PI)) + 1) / 2;   // 1 = up
    const rest = .32, a = lerp(rest, lerp(.5, 2.45, q), dp), bend = lerp(.25, lerp(.9, .15, q) * (.6 + .4 * (1 - Math.cos(TAU * b)) / 2), dp);
    const pts = arm(sd * .4 * u, .1 * u, a, bend, .4 * u * ap, .38 * u * ap, sd);
    if (pass === 'outline') { limb(ctx, pts, .19 * u, null, bw); ctx.beginPath(); ctx.arc(pts[2][0], pts[2][1], .1 * u * ap + bw, 0, TAU); ctx.fillStyle = C.white; ctx.fill(); }
    else {
      limb(ctx, pts.slice(1), .16 * u, SKIN); limb(ctx, pts.slice(0, 2), .2 * u, shirt);
      ctx.beginPath(); ctx.arc(pts[2][0], pts[2][1], .1 * u * ap, 0, TAU); ctx.fillStyle = SKIN; ctx.fill();
      if (sd > 0 && q > .5 && dp > .5) { ctx.beginPath(); ctx.arc(pts[2][0], pts[2][1], .1 * u * ap, 0, TAU); ctx.strokeStyle = 'rgba(0,0,0,.08)'; ctx.lineWidth = 2; ctx.stroke(); }
    }
  }
  ctx.restore();
}
// draw a head (+ body) with its top-left logic: x = centre, top = top of the head, w = head width
function figure(ctx, img, o, t) {
  const u = o.w, b = t * (o.bpm || 118) / 60 + (o.phase || 0), dp = o.danceP || 0;
  const bob = (1 - Math.cos(TAU * b)) / 2 * .07 * u * dp, sway = Math.sin(Math.PI * b) * .1 * u * dp;
  const REF = img ? img.height / img.width - .12 : 1.25;   // neck point: just above the bottom of the cut (the chin)
  const nx = o.x + sway * .6, ny = o.top + REF * u + bob;
  if ((o.bodyP || 0) > .002) {
    ctx.save(); ctx.translate(nx, ny);
    ctx.save(); drop(ctx, .26, 34, 14); bodyParts(ctx, { ...o, u }, t, 'outline'); ctx.restore();
    bodyParts(ctx, { ...o, u }, t, 'fill'); ctx.restore();
  }
  if (!img) return;
  const h = u * img.height / img.width, rot = (o.rot || 0) + Math.sin(TAU * b) * .06 * dp, sc = o.sc || 1;
  ctx.save(); ctx.translate(nx, ny - REF * u * .5); ctx.rotate(rot); ctx.scale(sc, sc);
  drop(ctx, .3, 42, 16);
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(img, -u / 2, -REF * u * .5, u, h);
  ctx.restore();
}

const talkHead = {
  needs(s, t) {
    if (t < s.from - .5 || t > (s.to ?? 1e9) + .5) return [];
    const names = new Set([s.face, ...(s.emo || []).map(e => e.img), ...(s.crew || []).map(c => c.img)]);
    return [...names].map(n => url(s, n));
  },
  draw(R, s, t) {
    const { ctx } = R, words = R.tl.words, a = envA(s, t); if (a <= .002) return;
    const [x, top, w] = s.posKeys ? track3(t, s.posKeys) : [W / 2, 560, 600];
    const f = faceAt(s, t), nod = nodAt(t, words), talk = talkingAt(t, words), B = s.body || {};
    const bodyP = B.at != null ? S(t - B.at, 7) : 0, armsP = B.armsAt != null ? S(t - B.armsAt, 8) : 0, danceP = B.danceAt != null ? S(t - B.danceAt, 5) : 0;
    const fl = 1 - danceP * .6;   // the idle float calms down once he dances
    const en = fl * (.55 + .45 * talk);   // more alive while he speaks
    const fx = (noise1(t * .4) - .5) * 30 * en, fy = (noise1(t * .33 + 9) - .5) * 24 * en, frot = (noise1(t * .27 + 3) - .5) * .09 * en
      + Math.sin(t * 7.3) * .02 * talk * fl;   // small talking wobble
    // a face change lands with a soft settle (1.04 -> 1), never a bounce
    const ch = s._ch || (s._ch = { key: null, at: -9 });
    if (f.key !== ch.key && f.key.startsWith('e')) { const e = (s.emo || []).find(e => 'e' + e.from === f.key); ch.at = e ? e.from : t; }
    ch.key = f.key;
    const pop = f.key.startsWith('e') ? .05 * (1 - S(t - ch.at, 14)) : 0;
    const k = w / 600;
    alpha(ctx, a, () => {
      // crew first (behind him)
      for (const c of s.crew || []) {
        const p = S(t - c.at, 10); if (p <= .002) continue;
        alpha(ctx, Math.min(1, p * 1.5), () => figure(ctx, R.img(url(s, c.img)), {
          x: c.x, top: c.top + (1 - p) * 260, w: c.w, bodyP: 1, armsP: 1, danceP: S(t - c.at - .2, 5), shirt: c.shirt, pants: c.pants,
          phase: c.phase || 0, bpm: B.bpm, sc: 1 + .06 * (1 - p), rot: (noise1(t * .3 + c.x) - .5) * .06,
        }, t));
      }
      figure(ctx, R.img(url(s, f.img)), {
        x: x + fx + nod.dir * nod.v * 8 * k, top: top + fy - nod.v * 24 * k, w, bodyP, armsP, danceP, shirt: B.shirt, pants: B.pants, bpm: B.bpm,
        rot: frot + nod.dir * .055 * nod.v, sc: 1 + .03 * nod.v + pop,
      }, t);
    });
  },
};
// snap: keys that move wider than 80 px jump there at once (teleport) instead of springing across
function track3(t, keys, snap) {
  let v = keys[0][1].slice();
  for (let i = 1; i < keys.length; i++) {
    const x = t - keys[i][0], far = snap && Math.abs(keys[i][1][0] - keys[i - 1][1][0]) >= 80;
    const p = far ? (x >= 0 ? 1 : 0) : S(x, keys[i][2] ?? 7); if (p <= 0) break;
    for (let j = 0; j < 3; j++) v[j] += (keys[i][1][j] - keys[i - 1][1][j]) * p;
  }
  return v;
}

// ---------------------------------------------------------------- disco
const disco = {
  draw(R, s, t) {
    const { ctx } = R, p = S(t - s.at, 6), out = 1 - S(t - (s.to ?? 1e9), 14); if (p <= .002 || out <= .002) return;
    const r = s.r || 130, x = s.x ?? W / 2, y = lerp(-r - 60, s.y ?? 250, p), th = t * 1.1;
    const lights = S(t - (s.spotsAt ?? s.at + .6), 6) * out;
    // light spots sweeping the paper (drawn first, under everything)
    if (lights > .01) {
      ctx.save(); ctx.globalCompositeOperation = 'multiply';
      for (let i = 0; i < 26; i++) {
        const a = th * .6 + i * 2.39996, d = 220 + 900 * hash(i * 1.3), sx = x + Math.cos(a) * d, sy = y + 300 + Math.sin(a) * d * .9;
        if (sy < -60 || sy > H + 60) continue;
        const rr = 30 + 34 * hash(i * 2.1), blue = i % 2 === 0;
        const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rr);
        g.addColorStop(0, blue ? `rgba(37,142,255,${.75 * lights})` : `rgba(150,140,120,${.3 * lights})`); g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g; ctx.fillRect(sx - rr, sy - rr, rr * 2, rr * 2);
      }
      ctx.restore();
      ctx.save(); ctx.globalCompositeOperation = 'screen';
      for (let i = 0; i < 18; i++) {
        const a = -th * .5 + i * 1.7, d = 160 + 820 * hash(i * 4.1 + 9), sx = x + Math.cos(a) * d, sy = y + 360 + Math.sin(a) * d;
        const rr = 18 + 22 * hash(i * 3.3), g = ctx.createRadialGradient(sx, sy, 0, sx, sy, rr);
        g.addColorStop(0, `rgba(255,255,255,${.85 * lights})`); g.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = g; ctx.fillRect(sx - rr, sy - rr, rr * 2, rr * 2);
      }
      ctx.restore();
    }
    alpha(ctx, out, () => {
      // string
      ctx.strokeStyle = C.ink2; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x, -10); ctx.lineTo(x, y - r - 14); ctx.stroke();
      ctx.fillStyle = C.ink2; ctx.beginPath(); ctx.roundRect(x - 16, y - r - 22, 32, 26, 6); ctx.fill();
      // ball: white die-cut ring + shadow, then the mirror tiles
      ctx.save(); drop(ctx, .3, 40, 18); ctx.beginPath(); ctx.arc(x, y, r + 10, 0, TAU); ctx.fillStyle = C.white; ctx.fill(); ctx.restore();
      ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.clip(); ctx.fillStyle = '#5E626B'; ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
      const NL = 12, NO = 24;
      for (let j = 0; j < NL; j++) {
        const la0 = -Math.PI / 2 + j * Math.PI / NL, la1 = la0 + Math.PI / NL;
        for (let k = 0; k < NO; k++) {
          const lo0 = k * TAU / NO + th, lo1 = lo0 + TAU / NO, lm = (lo0 + lo1) / 2;
          if (Math.cos(lm) <= -.05) continue;   // back side
          const P = (la, lo) => [x + r * Math.cos(la) * Math.sin(lo), y + r * Math.sin(la)];
          const q = [P(la0, lo0), P(la0, lo1), P(la1, lo1), P(la1, lo0)];
          const nz = Math.cos((la0 + la1) / 2) * Math.cos(lm), ny = Math.sin((la0 + la1) / 2), nx = Math.cos((la0 + la1) / 2) * Math.sin(lm);
          let l = clamp(.35 + .5 * (nz * .7 - ny * .5 - nx * .3));
          const tw = hash(j * 31 + k * 7 + Math.floor(t * 6) * 0.13);
          let fill = `rgb(${Math.round(lerp(120, 236, l))},${Math.round(lerp(124, 238, l))},${Math.round(lerp(132, 242, l))})`;
          if (tw > .93) fill = C.white; else if (tw < .05) fill = C.blue;
          ctx.beginPath(); q.forEach((pt, i) => ctx[i ? 'lineTo' : 'moveTo'](...pt)); ctx.closePath();
          ctx.fillStyle = fill; ctx.fill(); ctx.strokeStyle = 'rgba(40,40,48,.55)'; ctx.lineWidth = 1.6; ctx.stroke();
        }
      }
      const g = ctx.createRadialGradient(x - r * .35, y - r * .4, 0, x, y, r); g.addColorStop(0, 'rgba(255,255,255,.45)'); g.addColorStop(.5, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,.28)');
      ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
      // glints
      for (let i = 0; i < 3; i++) {
        const gp = (t * .9 + i * .37) % 1, gs = Math.sin(Math.PI * gp) * 26 * lights; if (gs < 2) continue;
        const gx = x + (hash(i + Math.floor(t * .9 + i * .37)) - .5) * r * 1.2, gy = y + (hash(i * 3 + Math.floor(t * .9 + i * .37)) - .6) * r * 1.1;
        ctx.fillStyle = C.white; ctx.beginPath();
        for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4, rr = k % 2 ? gs * .22 : gs; ctx.lineTo(gx + Math.cos(a) * rr, gy + Math.sin(a) * rr); }
        ctx.closePath(); ctx.fill();
      }
    });
  },
};

// ---------------------------------------------------------------- dancefloor
const dancefloor = {
  draw(R, s, t) {
    const { ctx } = R, out = 1 - S(t - (s.to ?? 1e9), 14); if (t < s.at - .05 || out <= .002) return;
    const y0 = s.y0 ?? 1360, y1 = H + 40, rows = s.rows || 5, cols = s.cols || 7, b = Math.floor(t * (s.bpm || 118) / 60);
    const xAt = (c, y) => { const f = (y - y0) / (y1 - y0), half = lerp(430, 900, f); return W / 2 + (c / cols - .5) * 2 * half; };
    const yAt = r => y0 + (y1 - y0) * Math.pow(r / rows, 1.25);
    alpha(ctx, out, () => {
      // floor slab shadow on the paper
      ctx.save(); drop(ctx, .28, 40, -6);
      ctx.beginPath(); ctx.moveTo(xAt(0, y0), y0); ctx.lineTo(xAt(cols, y0), y0); ctx.lineTo(xAt(cols, y1), y1); ctx.lineTo(xAt(0, y1), y1); ctx.closePath();
      ctx.fillStyle = C.ink; ctx.globalAlpha *= S(t - s.at, 8); ctx.fill(); ctx.restore();
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        const p = S(t - s.at - (rows - 1 - r) * .06 - Math.abs(c - cols / 2) * .03, 10); if (p <= .002) continue;
        const ya = yAt(r), yb = yAt(r + 1), g = 5;
        const lit = hash(r * 17 + c * 5 + b * 3.1), on = lit > .62, blue = lit > .8;
        const fill = blue ? C.blue : on ? C.sheet : r % 2 === c % 2 ? '#2A2D35' : '#1E2027';
        ctx.save(); ctx.globalAlpha *= p;
        ctx.beginPath(); ctx.moveTo(xAt(c, ya) + g, ya + g); ctx.lineTo(xAt(c + 1, ya) - g, ya + g); ctx.lineTo(xAt(c + 1, yb) - g, yb - g); ctx.lineTo(xAt(c, yb) + g, yb - g); ctx.closePath();
        ctx.fillStyle = fill; ctx.fill();
        if (on) { ctx.save(); ctx.clip(); const gl = ctx.createLinearGradient(0, ya, 0, yb); gl.addColorStop(0, 'rgba(255,255,255,.35)'); gl.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = gl; ctx.fill(); ctx.restore(); }
        ctx.restore();
      }
    });
  },
};

// ---------------------------------------------------------------- mascot
// Full-body cartoon mascot, one drawn pose per beat (no lip-sync). Pose PNGs share one canvas (cutout.py --canvas):
// feet at FOOT of the height, body centred. Pivot = feet, so squash/stretch and hops read like a cartoon.
const FOOT = .95;
const murl = (s, n) => '/p/' + (s.dir || 'assets/mascot/') + n + '.png';
function phrasesOf(s, words) {
  if (s._ph && s._ph.n === words.length) return s._ph.list;
  const list = []; let cur = null;
  for (const w of words) { if (cur && w.start - cur.end < (s.gap ?? .42)) cur.end = w.end; else list.push(cur = { start: w.start, end: w.end }); }
  s._ph = { n: words.length, list }; return list;
}
// which drawing is on screen at t, and since when (drives the squash on every swap)
function poseAt(s, t, words) {
  const D = s.dance;
  if (D && t >= D.at && t < (D.to ?? 1e9)) {
    const beat = (D.beats || 2) * 60 / (D.bpm || 104), k = Math.floor((t - D.at) / beat);
    return { img: D.imgs[k % D.imgs.length], since: D.at + k * beat };
  }
  const P = s.poses || []; let lastEnd = -1e9;
  for (let i = 0; i < P.length; i++) {
    const end = P[i].to ?? Math.min(P[i].at + (s.hold ?? 1.8), P[i + 1]?.at ?? 1e9);
    if (t >= P[i].at && t < end) return { img: P[i].img, since: P[i].at, flip: P[i].flip };
    if (end <= t) lastEnd = Math.max(lastEnd, end);
  }
  const ph = phrasesOf(s, words); let prevEnd = -1e9;
  for (let i = 0; i < ph.length; i++) {
    const a = ph[i].start - .06, b = ph[i].end + .22;
    if (t >= a && t < b) { const talk = s.talk || []; return { img: talk[i % talk.length] || s.idle, since: Math.max(a, lastEnd) }; }
    if (b <= t) prevEnd = b;
  }
  return { img: s.idle, since: Math.max(prevEnd, lastEnd) };
}
// cartoon swap: lands squashed, overshoots tall, settles (~.35 s)
const swapK = x => x < 0 || x > .6 ? 0 : Math.exp(-x * 9) * Math.cos(x * 24);
function drawMascot(ctx, img, o) {
  if (!img) return;
  const h = o.h, w = h * img.width / img.height;
  ctx.save(); ctx.translate(o.x, o.y);
  // contact shadow on the ground, shrinks while airborne
  if (o.ground !== false) {
    const air = clamp(-(o.lift || 0) / (h * .3));
    ctx.save(); ctx.scale((1 - air * .45) * (1 - (o.gone || 0)), 1);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, h * .2); g.addColorStop(0, `rgba(30,22,10,${.22 * (1 - air * .6)})`); g.addColorStop(1, 'rgba(30,22,10,0)');
    ctx.fillStyle = g; ctx.scale(1, .16); ctx.beginPath(); ctx.arc(0, 0, h * .2, 0, TAU); ctx.fill(); ctx.restore();
  }
  ctx.translate(0, o.lift || 0); ctx.rotate(o.rot || 0); ctx.scale(o.sx || 1, o.sy || 1);
  if (o.flip) ctx.scale(-1, 1);
  ctx.save();
  if (o.clipY != null) { ctx.beginPath(); ctx.rect(-W, -h * 2, W * 2, h * 2 + o.clipY); ctx.clip(); }
  if (o.filter) ctx.filter = o.filter;
  drop(ctx, .3, 38, 16);
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(img, -w / 2, -FOOT * h, w, h);
  ctx.restore();
  // the cut gets a die-cut white edge so the floating head still reads as a sticker
  if (o.clipY != null && o.cutA > .01) alpha(ctx, o.cutA, () => {
    drop(ctx, .25, 16, 6); ctx.beginPath(); ctx.roundRect(-h * .13, o.clipY - h * .012, h * .26, h * .028, h * .014); ctx.fillStyle = C.white; ctx.fill();
  });
  ctx.restore();
}
function hopAt(t, jumps, d = .5) {   // 0..1 height, plus squash before take-off and on landing
  let lift = 0, sq = 0;
  for (const j of jumps || []) {
    const x = t - (j.at ?? j);
    if (x > -.12 && x < 0) sq = Math.max(sq, Math.sin(Math.PI * (x + .12) / .12) * .5);
    else if (x >= 0 && x < d) lift = Math.max(lift, Math.sin(Math.PI * x / d));
    else if (x >= d && x < d + .22) sq = Math.max(sq, Math.sin(Math.PI * (x - d) / .22));
  }
  return { lift, sq };
}
// travel between two posKeys far apart = one cartoon leap: arc in the air, lean into the move, squash on landing.
// p = spring progress of the newest key still moving, dx = its horizontal distance.
function travelAt(t, keys, sp = 7) {
  let best = null;
  for (let i = 1; i < (keys || []).length; i++) {
    const x = t - keys[i][0]; if (x < -.14) break;
    const dx = keys[i][1][0] - keys[i - 1][1][0]; if (Math.abs(dx) < 80) continue;
    const p = S(x, keys[i][2] ?? sp); if (p < .985) best = { x, p, dx, dir: Math.sign(dx), amt: Math.min(1, Math.abs(dx) / 520) };
  }
  return best;
}
// teleport (s.teleport): every posKeys move wider than 80 px. He zips thin and vanishes in TP_OUT s before the key,
// then pops back at the new spot (spring, no overshoot). k = time since the key, from = where he left.
const TP_OUT = .1, TP_IN = .45;
function teleportAt(t, keys) {
  for (let i = (keys || []).length - 1; i >= 1; i--) {
    const k = t - keys[i][0]; if (k < -TP_OUT || k > TP_IN) continue;
    if (Math.abs(keys[i][1][0] - keys[i - 1][1][0]) < 80) continue;
    const v = k < 0 ? (u => u * u * (3 - 2 * u))(-k / TP_OUT) : S(k, 15);
    return { k, v, from: track3(keys[i][0] - .001, keys, true) };
  }
  return null;
}
// cartoon poof: a compact paper cloud (outline only on the outside) that swells then shrinks, plus a few marker ticks
function poof(ctx, x, cy, r, k) {
  if (k <= 0 || k >= 1) return;
  const e = 1 - Math.pow(1 - k, 3), a = k < .7 ? 1 : 1 - (k - .7) / .3, sh = 1 - k * k, P = [];
  for (let i = 0; i < 8; i++) {
    const ang = i / 8 * TAU + hash(i * 3.3) * .6, d = r * (.12 + .45 * e) * (.8 + .4 * hash(i * 1.9));
    P.push([x + Math.cos(ang) * d, cy + Math.sin(ang) * d * .75, r * (.22 + .08 * hash(i * 5.7)) * sh]);
  }
  P.push([x, cy, r * .3 * sh * (1 - e)]);
  alpha(ctx, a, () => {
    ctx.strokeStyle = 'rgba(20,22,27,.6)'; ctx.lineWidth = 7;
    for (const [px, py, pr] of P) if (pr > 1) { ctx.beginPath(); ctx.arc(px, py, pr, 0, TAU); ctx.stroke(); }
    ctx.fillStyle = C.white;
    for (const [px, py, pr] of P) if (pr > 1) { ctx.beginPath(); ctx.arc(px, py, pr, 0, TAU); ctx.fill(); }
    ctx.strokeStyle = C.ink; ctx.lineCap = 'round'; ctx.lineWidth = 6; ctx.globalAlpha *= .7 * (1 - k);
    for (let i = 0; i < 6; i++) {
      const ang = i / 6 * TAU + .3, r0 = r * (.6 + .45 * e), r1 = r0 + r * .2;
      ctx.beginPath(); ctx.moveTo(x + Math.cos(ang) * r0, cy + Math.sin(ang) * r0 * .8); ctx.lineTo(x + Math.cos(ang) * r1, cy + Math.sin(ang) * r1 * .8); ctx.stroke();
    }
  });
}
// little paper dust puffs at the feet when he lands
function dust(ctx, x, y, h, k) {
  if (k <= 0 || k >= 1) return;
  const e = 1 - Math.pow(1 - k, 3), a = 1 - k;
  for (let i = 0; i < 6; i++) {
    const side = i % 2 ? 1 : -1, d = (h * .1 + h * .22 * e) * (.7 + .5 * hash(i * 2.3)), r = h * (.03 + .035 * e) * (.7 + .6 * hash(i * 5.1));
    alpha(ctx, a, () => {
      ctx.beginPath(); ctx.arc(x + side * d, y - h * (.01 + .05 * e * hash(i * 1.7)), r, 0, TAU);
      ctx.fillStyle = C.white; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(20,22,27,.55)'; ctx.stroke();
    });
  }
}
// marker speed strokes trailing behind him while he flies across
function speedLines(ctx, x, y, h, dir, a) {
  if (a <= .02) return;
  ctx.save(); ctx.lineCap = 'round'; ctx.strokeStyle = C.ink;
  for (let i = 0; i < 4; i++) {
    const yy = y - h * (.25 + .17 * i), len = h * (.22 + .14 * hash(i * 3.1)) * a, x0 = x - dir * h * (.3 + .06 * hash(i * 7.7));
    ctx.globalAlpha = .55 * a; ctx.lineWidth = 7 - i; ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x0 - dir * len, yy); ctx.stroke();
  }
  ctx.restore();
}
const mascot = {
  needs(s, t) {
    if (t < s.from - .5 || t > (s.to ?? 1e9) + .5) return [];
    const n = new Set([s.idle, s.travelPose, s.airPose, ...(s.talk || []), ...(s.poses || []).map(p => p.img), ...(s.dance?.imgs || []), ...(s.crew || []).flatMap(c => c.imgs)]);
    return [...n].filter(Boolean).map(x => murl(s, x));
  },
  draw(R, s, t) {
    const { ctx } = R, words = R.tl.words, a = envA(s, t); if (a <= .002) return;
    const [x, footY, h] = s.posKeys ? track3(t, s.posKeys, s.teleport) : [W / 2, 1560, 1100];
    const D = s.dance, bpm = D?.bpm || 104, dp = D ? S(t - D.at, 6) * (1 - S(t - (D.to ?? 1e9), 8)) : 0, beat = t * bpm / 60;
    const nod = nodAt(t, words), talk = talkingAt(t, words), pose = poseAt(s, t, words);
    alpha(ctx, a, () => {
      // friends behind him, they pop up from under the floor and dance on the beat
      for (const c of s.crew || []) {
        const p = S(t - c.at, 9) * (1 - S(t - (c.to ?? 1e9), 9)); if (p <= .002) continue;
        const cb = beat + (c.phase || 0), k = Math.floor((t - c.at) / (2 * 60 / bpm));
        const bounce = Math.abs(Math.sin(Math.PI * cb)), x0 = t - c.at;
        const pop = swapK(x0 - .02) * .8 + swapK(((t - c.at) % (2 * 60 / bpm))), ci = c.imgs[Math.max(0, k) % c.imgs.length];
        drawMascot(ctx, R.img(murl(s, ci)), {
          x: c.x, y: c.footY + (1 - p) * (H - c.footY + c.h * 1.1), h: c.h * (s.sizes?.[ci] ?? 1), lift: -bounce * c.h * .035,   // sinks fully below the frame
          sx: 1 + .05 * pop, sy: 1 - .07 * pop + .03 * bounce, rot: Math.sin(Math.PI * cb) * .05, flip: c.flip,
        });
      }
      // squash and stretch layers
      const tp = s.teleport ? teleportAt(t, s.posKeys) : null, tr = s.teleport ? null : travelAt(t, s.posKeys), hop = hopAt(t, s.jumps);
      let img = pose.img, flip = pose.flip ?? s.flip, since = pose.since;
      // leap: anticipation crouch, arc, landing squash; the travel pose (running, facing right) flips with the direction
      let arc = 0, lean = 0, land = 0, crouch = 0;
      if (tr) {
        if (tr.x < 0) crouch = Math.sin(Math.PI * (tr.x + .14) / .14) * .6 * tr.amt;
        else { arc = Math.sin(Math.PI * Math.min(1, tr.p / .92)) * tr.amt; lean = tr.dir * Math.sin(Math.PI * Math.min(1, tr.p / .8)) * .2 * tr.amt; }
        if (tr.p > .86) land = Math.sin(Math.PI * (tr.p - .86) / .125) * tr.amt;
        if (s.travelPose && tr.x >= 0 && tr.p < .82) { img = s.travelPose; flip = tr.dir < 0; since = t - tr.x; }
      }
      if (s.airPose && !tr && hop.lift > .25) { img = s.airPose; flip = s.flip; }
      const sw = swapK(t - since);
      const bounce = Math.abs(Math.sin(Math.PI * beat)) * dp, idle = 1 - dp;
      const sq = Math.max(hop.sq, crouch, land), up = Math.max(hop.lift, arc * .8);
      let sx = 1 + .09 * sw + .03 * nod.v * idle + .07 * sq - .04 * up, sy = 1 - .11 * sw - .045 * nod.v * idle - .11 * sq + .08 * up;
      if (tp) { sx *= tp.v; sy *= 1 + .22 * (1 - tp.v); }   // zips thin and tall, then springs back
      sy += .012 * Math.sin(t * 2.6) * idle + .04 * (bounce - .5) * dp; sx -= .025 * (bounce - .5) * dp;
      const rot = lean + ((noise1(t * .45 + 3) - .5) * .07 + nod.dir * .035 * nod.v + Math.sin(t * 8.1) * .016 * talk) * idle + Math.sin(Math.PI * beat) * .06 * dp;
      const lift = -(hop.lift * h * .16 + arc * h * .38 + bounce * h * .04);
      const fx = (noise1(t * .3) - .5) * 26 * idle;
      // head-only gag: the body is cut off at the chin, then unrolls back down
      let clipY = null, cutA = 0;
      for (const [f0, f1] of s.headOnlySpans || []) {
        const cp = S(t - f0, 12) * (1 - S(t - f1, 9)); if (cp <= .002) continue;
        clipY = lerp(h * .2, -FOOT * h + (s.chin ?? .6) * h, cp); cutA = clamp((cp - .7) / .3);
      }
      let filter = null;
      for (const [f0, f1] of s.hueSpans || []) if (t >= f0 && t < f1 + .3) { const e = 1 - S(t - f1, 14); filter = `hue-rotate(${Math.round((t - f0) * 900 * e)}deg) saturate(${1 + .5 * e})`; }
      if (tr && tr.x > 0) speedLines(ctx, x + fx, footY + lift, h, tr.dir, Math.sin(Math.PI * Math.min(1, tr.p / .85)) * tr.amt);
      if (tp && s.dust !== false) {   // puffs behind him: where he vanished, then where he lands
        const pf = tp.from; poof(ctx, pf[0] + fx, pf[1] - pf[2] * .45, pf[2] * .42, (tp.k + TP_OUT * .5) / .4);
        if (tp.k >= 0) poof(ctx, x + fx, footY - h * .45, h * .42, tp.k / .4);
      }
      if (!tp || tp.v > .01) drawMascot(ctx, R.img(murl(s, img)), { x: x + fx, y: footY, h: h * (s.sizes?.[img] ?? 1), lift, sx, sy, rot, clipY, cutA, filter, flip, gone: tp ? 1 - tp.v : 0 });
      // dust when he lands: after a leap, and after each jump of s.jumps
      if (s.dust !== false) {
        if (tr && tr.p > .8) dust(ctx, x + fx, footY, h, (tr.p - .8) / .2);
        for (const j of s.jumps || []) { const k = (t - (j.at ?? j) - .48) / .45; if (k > 0 && k < 1) dust(ctx, x + fx, footY, h * .8, k); }
      }
    });
  },
};
// ---------------------------------------------------------------- bills
// {from, at, to, n 22}: paper dollar bills flutter down over everything (money leaving the wallet).
const bills = {
  draw(R, s, t) {
    const { ctx } = R, out = 1 - S(t - (s.to ?? 1e9), 10); if (t < s.at || out <= .002) return;
    const n = s.n || 22, x0 = t - s.at;
    for (let i = 0; i < n; i++) {
      const d = hash(i * 3.7) * (s.spread ?? 2.2), x = x0 - d; if (x <= 0) continue;
      const vy = 330 + 260 * hash(i * 1.9), y = -140 + x * vy, bx = 80 + hash(i * 5.3) * (W - 160) + Math.sin(x * 2.6 + i) * 90;
      if (y > H + 140) continue;
      const rot = Math.sin(x * 2.1 + i * 2) * .7 + (hash(i) - .5), flipX = Math.cos(x * 4.2 + i * 1.3), sc = .8 + .45 * hash(i * 7.1);
      alpha(ctx, out, () => {
        ctx.translate(bx, y); ctx.rotate(rot); ctx.scale(sc * (.25 + .75 * Math.abs(flipX)), sc);
        const bw = 190, bh = 92;
        drop(ctx, .22, 18, 8); ctx.beginPath(); ctx.roundRect(-bw / 2 - 7, -bh / 2 - 7, bw + 14, bh + 14, 12); ctx.fillStyle = C.white; ctx.fill(); ctx.shadowColor = 'transparent';
        ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, 7); ctx.fillStyle = '#CFE3C4'; ctx.fill();
        ctx.lineWidth = 3; ctx.strokeStyle = '#4F7A47'; ctx.beginPath(); ctx.roundRect(-bw / 2 + 9, -bh / 2 + 9, bw - 18, bh - 18, 5); ctx.stroke();
        ctx.beginPath(); ctx.arc(0, 0, 27, 0, TAU); ctx.fillStyle = '#F4F8EF'; ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#3F6A38'; ctx.font = '800 38px Inter'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('$', 0, 2);
        if (flipX < 0) { ctx.fillStyle = 'rgba(40,60,30,.12)'; ctx.fillRect(-bw / 2, -bh / 2, bw, bh); }
      });
    }
  },
};

// ---------------------------------------------------------------- confetti
// {at, to, x 540, y 900, n 140, power 1}: paper confetti burst (blue, ink, tint, white) with gravity and flutter.
const CONF = ['blue', 'ink', 'tint', 'white', 'blue', 'sheet'];
const confetti = {
  draw(R, s, t) {
    const { ctx } = R, x0 = t - s.at, out = 1 - S(t - (s.to ?? s.at + 3.5), 8); if (x0 <= 0 || out <= .002) return;
    const n = s.n || 140, pw = s.power || 1;
    for (let i = 0; i < n; i++) {
      const ang = -Math.PI / 2 + (hash(i * 1.3) - .5) * (s.cone ?? 2.4), v = (900 + 1500 * hash(i * 2.7)) * pw;
      const drag = 2.2, e = (1 - Math.exp(-drag * x0)) / drag;
      const px = (s.x ?? W / 2) + Math.cos(ang) * v * e + Math.sin(x0 * 5 + i) * 26 * x0;
      const py = (s.y ?? 900) + Math.sin(ang) * v * e + 520 * x0 * x0;
      if (py > H + 40) continue;
      const fl = Math.cos(x0 * (7 + 6 * hash(i * 4.4)) + i), sz = 16 + 16 * hash(i * 6.1);
      alpha(ctx, out, () => {
        ctx.translate(px, py); ctx.rotate(x0 * (3 + 5 * hash(i)) + i); ctx.scale(1, .2 + .8 * Math.abs(fl));
        const c = CONF[i % CONF.length]; ctx.fillStyle = c === 'sheet' ? C.sheet : col(c);
        if (i % 3) ctx.fillRect(-sz / 2, -sz * .3, sz, sz * .6); else { ctx.beginPath(); ctx.arc(0, 0, sz * .38, 0, TAU); ctx.fill(); }
      });
    }
  },
};

export const FACE = { paperFlow, bgPattern, talkHead, disco, dancefloor, mascot, bills, confetti };
