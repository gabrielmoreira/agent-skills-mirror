// Story scenes: hand-drawn illustration scenes for narrative shorts (first used by short-chapeau-alu).
// Same contract as scenes.js: {type, from, to, layer, ...} with times already mapped to SHORT time.
//   foilHat (over)  a crinkled tinfoil hat with a little antenna that drops onto the speaker's head (face-tracked)
//   stampOver (over) a rubber stamp over the camera
//   sea             Eiffel tower line drawing, rising water, year counter, stamp, sea gauge, "simulation" wireframe
//   giec            flip-book of yearly reports that always say "dans 5 ans"
//   bike            recycling bins struck out, then a 100 km commute with a moving bike, km counter and a passing sun
//   equation        CQFD: IA = climat x10, then a callback stamp
//   crowd           GPT -> Mistral: a crowd of dots flows between two logo tiles, then regroups into a pyramid (elite on top)
//   cheque          a company cheque: handwritten payee, amount counts up, rolls back to 0, then a stamp lands
//                   {rect: [x, y, w], logo, payer, city, no, date, payee, words, memo, amount, currency '$', writeAt,
//                    countFrom, countTo, zeroAt (count rolls to 0, words struck), stampAt, stamp} (560 px tall)
import { C, W, H, clamp, lerp, seg, E, S, leave, track, sheet, shadow, text, measure, midBase, chip, hash } from './kit.js';

const TAU = Math.PI * 2;
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const mix = (a, b, p) => { const x = hex(a), y = hex(b); return `rgb(${x.map((v, i) => Math.round(lerp(v, y[i], clamp(p)))).join(',')})`; };
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }
function rise(ctx, p, dist, fn, dx = 0) { alpha(ctx, Math.min(1, p * 1.35), () => { ctx.translate(dx * (1 - p), dist * (1 - p)); fn(); }); }
function env(ctx, s, t, fn) {
  const out = s.to != null ? leave(t - s.to) : 0;
  alpha(ctx, 1 - out, () => { ctx.translate(0, -36 * out); fn(S(t - s.from + (s.pre || 0), 12)); });
}
const P = (t, at, w = 13) => at == null ? 0 : S(t - at, w);

// rubber stamp: lands from 1.35x to 1 (critically damped, no overshoot), slight angle
function stamp(ctx, x, y, str, p, o = {}) {
  if (p <= .002) return;
  const size = o.size || 64, w = measure(ctx, str, size, 800, -1) + 76, h = size + 54;
  ctx.save(); ctx.globalAlpha *= Math.min(1, p * 1.6); ctx.translate(x, y); ctx.rotate(o.rot ?? -.07); const k = 1 + .35 * (1 - p); ctx.scale(k, k);
  if (o.solid) shadow(ctx, -w / 2, -h / 2, w, h, 22, 22, .2, 8);
  ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, 22); ctx.fillStyle = o.solid ? C.sheet : 'rgba(37,142,255,.08)'; ctx.fill();
  ctx.lineWidth = 8; ctx.strokeStyle = C.blue; ctx.stroke();
  ctx.beginPath(); ctx.roundRect(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 14); ctx.lineWidth = 2.5; ctx.stroke();
  text(ctx, str, 0, midBase(0, size), { size, weight: 800, ls: -1, align: 'center', color: C.blue });
  ctx.restore();
}

// ---------------------------------------------------------------- face track (assets/faces.json from engine/faces.swift)
let FACES = null;
function faces() {
  if (FACES) return FACES;
  try { const x = new XMLHttpRequest(); x.open('GET', '/p/assets/faces.json', false); x.send(); FACES = x.status === 200 ? JSON.parse(x.responseText) : []; }
  catch { FACES = []; }
  return FACES;
}

// ---------------------------------------------------------------- foilHat (over)
// {layer: 'over', from, to, dropAt, lift: .72 (base above face centre, in face heights), size: 1}
function foilCone(ctx, fw, seed) {
  const bw = fw * .8, hh = fw * 1.18, ax = fw * .06;   // base half-width, height, apex lean
  // faceted cone: rows x cols of jittered vertices, lit from the upper left
  const rows = 6, cols = 9, V = [];
  for (let r = 0; r <= rows; r++) {
    const v = r / rows, row = [];
    for (let c = 0; c <= cols; c++) {
      const u = c / cols, edge = c === 0 || c === cols || r === rows, jx = edge ? 0 : (hash(seed + r * 31 + c * 7) - .5) * fw * .07, jy = r === 0 || r === rows ? 0 : (hash(seed + r * 13 + c * 17) - .5) * fw * .06;
      const half = bw * (1 - v), x = lerp(-half, half, u) + ax * v + jx, y = -hh * v + Math.sin(u * Math.PI) * fw * .1 * (1 - v) + jy;
      row.push([x, y, u]);
    }
    V.push(row);
  }
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const a = V[r][c], b = V[r][c + 1], d = V[r + 1][c], e = V[r + 1][c + 1];
    for (const [tri, k] of [[[a, b, e], 0], [[a, e, d], 1]]) {
      const u = (tri[0][2] + tri[1][2] + tri[2][2]) / 3, light = .55 + .45 * Math.cos((u - .32) * Math.PI * 1.1) - .12 * (r / rows);
      const n = hash(seed + r * 97 + c * 41 + k * 5) * .5 - .25, L = clamp(light + n, .05, 1);
      const g = Math.round(lerp(92, 250, L));
      ctx.beginPath(); ctx.moveTo(tri[0][0], tri[0][1]); ctx.lineTo(tri[1][0], tri[1][1]); ctx.lineTo(tri[2][0], tri[2][1]); ctx.closePath();
      ctx.fillStyle = `rgb(${g},${g + 2},${g + 6})`; ctx.fill();
      ctx.strokeStyle = `rgba(255,255,255,${.18 + .3 * hash(seed + r * 11 + c)})`; ctx.lineWidth = 1.2; ctx.stroke();
    }
  }
  // folded rim: a crinkled band around the base
  ctx.beginPath();
  for (let i = 0; i <= 40; i++) { const u = i / 40, x = lerp(-bw * 1.04, bw * 1.04, u), y = Math.sin(u * Math.PI) * fw * .12 + (hash(seed + i * 3) - .5) * fw * .025; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  for (let i = 40; i >= 0; i--) { const u = i / 40, x = lerp(-bw * 1.04, bw * 1.04, u), y = Math.sin(u * Math.PI) * fw * .12 - fw * .1 + (hash(seed + i * 5) - .5) * fw * .03; ctx.lineTo(x, y); }
  ctx.closePath();
  const rg = ctx.createLinearGradient(-bw, 0, bw, 0);
  rg.addColorStop(0, '#9A9EA6'); rg.addColorStop(.3, '#F4F5F7'); rg.addColorStop(.55, '#B9BDC4'); rg.addColorStop(.8, '#E8E9EC'); rg.addColorStop(1, '#8C9098');
  ctx.fillStyle = rg; ctx.fill(); ctx.strokeStyle = 'rgba(60,64,72,.35)'; ctx.lineWidth = 1.5; ctx.stroke();
  // outline
  ctx.beginPath(); ctx.moveTo(-bw, 0); ctx.lineTo(ax, -hh); ctx.lineTo(bw, 0); ctx.strokeStyle = 'rgba(40,44,52,.35)'; ctx.lineWidth = 2; ctx.stroke();
  // specular streak
  ctx.save(); ctx.globalAlpha = .55; ctx.beginPath(); ctx.moveTo(-bw * .55, -fw * .02); ctx.lineTo(ax - fw * .05, -hh * .92); ctx.lineTo(ax - fw * .02, -hh * .9); ctx.lineTo(-bw * .42, -fw * .02); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore();
  // antenna + blue ball (the martian touch)
  const tx = ax, ty = -hh;
  ctx.beginPath(); ctx.moveTo(tx, ty + 2); ctx.quadraticCurveTo(tx + fw * .05, ty - fw * .22, tx + fw * .02, ty - fw * .4); ctx.strokeStyle = '#6E737C'; ctx.lineWidth = Math.max(3, fw * .025); ctx.lineCap = 'round'; ctx.stroke();
  const br = fw * .075, bx = tx + fw * .02, by = ty - fw * .4 - br * .6;
  const bg = ctx.createRadialGradient(bx - br * .35, by - br * .35, br * .1, bx, by, br);
  bg.addColorStop(0, '#9CCBFF'); bg.addColorStop(.45, C.blue); bg.addColorStop(1, C.blue2);
  ctx.beginPath(); ctx.arc(bx, by, br, 0, TAU); ctx.fillStyle = bg; ctx.fill();
}
const foilHat = {
  draw(R, s, t) {
    const { ctx } = R, F = faces(); if (!F.length || R.seam >= H - 2) return;
    const fps = R.tl.fps || 30, f = F[clamp(Math.round(t * fps), 0, F.length - 1)]; if (!f || !f[2]) return;
    const drop = S(t - (s.dropAt ?? s.from), 9), out = s.to != null ? S(t - s.to, 10) : 0;
    const a = Math.min(1, drop * 3) * (1 - out); if (a <= .002) return;
    const T = R.camT(t, R.seam), fw = f[2] * T.s * (s.size || .82), fh = f[3] * T.s;
    const cx = T.x0 + f[0] * T.s, cy = T.y0 + f[1] * T.s - fh * (s.lift ?? .66);
    const dy = -(1 - drop) * 1100 - out * 700;
    ctx.save(); ctx.beginPath(); ctx.rect(0, R.seam, W, H - R.seam); ctx.clip();
    ctx.globalAlpha = a; ctx.translate(cx, cy + dy); ctx.rotate((f[4] || 0) * .9 + (1 - drop) * -.25);
    shadow(ctx, -fw * .8, -fw * .1, fw * 1.6, fw * .3, fw * .15, 18, .22, 12);
    foilCone(ctx, fw, 17);
    ctx.restore();
  },
};

// ---------------------------------------------------------------- stampOver (over): {layer: 'over', from, to, text, y, size, rot}
const stampOver = {
  draw(R, s, t) {
    const out = s.to != null ? S(t - s.to, 14) : 0, p = S(t - s.from, 11) * (1 - out);
    stamp(R.ctx, s.x ?? W / 2, s.y ?? 420, s.text, p, { size: s.size || 76, rot: s.rot ?? -.06, solid: true });
  },
};

// ---------------------------------------------------------------- Eiffel tower (line art). base at (cx, by), height h
function eiffel(ctx, cx, by, h, col, lw) {
  const hw = h * .36;   // half base
  const leg = (sgn, inner) => {   // curved leg edge from base to the top neck
    const x0 = cx + sgn * (inner ? hw * .55 : hw), x1 = cx + sgn * h * (inner ? .022 : .04), y1 = by - h * .86;
    ctx.beginPath(); ctx.moveTo(x0, by); ctx.bezierCurveTo(cx + sgn * hw * (inner ? .42 : .7), by - h * .25, cx + sgn * h * .08, by - h * .6, x1, y1); ctx.stroke();
  };
  const xAt = (y, sgn, inner) => {   // approximate edge x at height y (for platforms and bracing)
    const v = clamp((by - y) / (h * .86)); const w0 = inner ? hw * .55 : hw, w1 = h * (inner ? .022 : .04);
    return cx + sgn * lerp(w0, w1, 1 - Math.pow(1 - v, 2.1));
  };
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  leg(-1, false); leg(1, false); leg(-1, true); leg(1, true);
  // base arch
  ctx.beginPath(); ctx.moveTo(xAt(by - h * .16, -1, true), by - h * .16); ctx.quadraticCurveTo(cx, by - h * .36, xAt(by - h * .16, 1, true), by - h * .16); ctx.stroke();
  // platforms
  for (const [v, ext] of [[.25, .07], [.52, .045]]) {
    const y = by - h * v, xl = xAt(y, -1) - h * ext, xr = xAt(y, 1) + h * ext;
    ctx.beginPath(); ctx.moveTo(xl, y); ctx.lineTo(xr, y); ctx.moveTo(xl + h * .01, y + h * .03); ctx.lineTo(xr - h * .01, y + h * .03); ctx.stroke();
  }
  // cross bracing in the legs
  ctx.save(); ctx.lineWidth = lw * .45;
  for (const sgn of [-1, 1]) for (let k = 0; k < 7; k++) {
    const y0 = by - h * (.28 + k * .08), y1 = by - h * (.28 + (k + 1) * .08);
    if (y1 < by - h * .84) break;
    ctx.beginPath(); ctx.moveTo(xAt(y0, sgn), y0); ctx.lineTo(xAt(y1, sgn, true), y1); ctx.moveTo(xAt(y0, sgn, true), y0); ctx.lineTo(xAt(y1, sgn), y1); ctx.stroke();
  }
  for (const sgn of [-1, 1]) for (let k = 0; k < 3; k++) {
    const y0 = by - h * (k * .08), y1 = by - h * ((k + 1) * .08);
    ctx.beginPath(); ctx.moveTo(xAt(y0, sgn), y0); ctx.lineTo(xAt(y1, sgn, true), y1); ctx.moveTo(xAt(y0, sgn, true), y0); ctx.lineTo(xAt(y1, sgn), y1); ctx.stroke();
  }
  ctx.restore();
  // top: neck, lantern, spire
  const ny = by - h * .86;
  ctx.beginPath(); ctx.rect(cx - h * .03, ny - h * .04, h * .06, h * .04); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(cx, ny - h * .04); ctx.lineTo(cx, by - h); ctx.stroke();
  ctx.restore();
}
// wavy water surface path, filled down to `bottom`
function water(ctx, y, bottom, t, amp = 10, x0 = 0, x1 = W) {
  ctx.beginPath(); ctx.moveTo(x0, bottom);
  for (let x = x0; x <= x1; x += 12) ctx.lineTo(x, y + Math.sin(x * .012 + t * 1.6) * amp + Math.sin(x * .031 - t * 1.1) * amp * .45);
  ctx.lineTo(x1, bottom); ctx.closePath();
}

// sea: {from, to, base: 1150, h: 700, year: {fromYear, toYear, countFrom, countTo, y}, waterKeys: [[t, level 0..1]],
//   stamp: {text, at}, gauge: {at}, sim: {at}}
const sea = {
  draw(R, s, t) {
    const { ctx } = R, by = s.base ?? 1150, th = s.h ?? 700, cx = W / 2;
    env(ctx, s, t, pin => {
      const sim = s.sim ? E.io(seg(t, s.sim.at, s.sim.at + .9)) : 0, scanY = lerp(150, 1260, sim);
      // simulation grid (only where the scan line has passed)
      if (sim > 0) {
        ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, scanY); ctx.clip();
        ctx.fillStyle = 'rgba(37,142,255,.05)'; ctx.fillRect(0, 0, W, scanY);
        ctx.strokeStyle = 'rgba(37,142,255,.22)'; ctx.lineWidth = 1.5;
        for (let x = 0; x <= W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1300); ctx.stroke(); }
        for (let y = 0; y <= 1300; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
        ctx.restore();
        if (sim < 1) { ctx.fillStyle = C.blue; ctx.fillRect(0, scanY - 2, W, 4); alpha(ctx, .25, () => { const g = ctx.createLinearGradient(0, scanY - 90, 0, scanY); g.addColorStop(0, 'rgba(37,142,255,0)'); g.addColorStop(1, 'rgba(37,142,255,.5)'); ctx.fillStyle = g; ctx.fillRect(0, scanY - 90, W, 90); }); }
      }
      // tower: draws on from the ground up
      const draw = E.out(seg(t, s.from - (s.pre || 0), s.from - (s.pre || 0) + .9));
      ctx.save(); ctx.beginPath(); ctx.rect(0, lerp(by + 10, by - th - 20, draw), W, th + 60); ctx.clip();
      eiffel(ctx, cx, by, th, C.ink, 6);
      if (sim > 0) { ctx.beginPath(); ctx.rect(0, 0, W, scanY); ctx.clip(); eiffel(ctx, cx, by, th, C.blue, 6); }
      ctx.restore();
      // ground line
      rise(ctx, pin, 0, () => { ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(110, by); ctx.lineTo(W - 110, by); ctx.stroke(); });
      // water
      if (s.waterKeys) {
        const lv = track(t, s.waterKeys, 5), wy = by + 14 - th * lv;
        if (lv > .003) {
          ctx.save(); ctx.globalCompositeOperation = 'multiply';
          water(ctx, wy + 14, 1320, t + 1.3, 8); ctx.fillStyle = 'rgba(37,142,255,.13)'; ctx.fill();
          water(ctx, wy, 1320, t, 11); ctx.fillStyle = 'rgba(37,142,255,.2)'; ctx.fill();
          ctx.restore();
          ctx.save(); water(ctx, wy, 1320, t, 11); ctx.strokeStyle = C.blue; ctx.lineWidth = 5; ctx.stroke(); ctx.restore();
        }
      }
      // year counter
      if (s.year) {
        const y = s.year, k = E.io(seg(t, y.countFrom, y.countTo)), yr = Math.round(lerp(y.fromYear, y.toYear, k));
        rise(ctx, P(t, s.from - (s.pre || 0), 12) * (1 - (s.sim ? P(t, s.sim.at, 12) : 0)), 40, () => {
          text(ctx, String(yr), cx, y.y ?? 330, { size: 120, weight: 800, ls: -4, align: 'center', color: k >= 1 ? C.blue : C.ink });
        });
      }
      // sea gauge (right side): needle stuck at 0
      if (s.gauge) {
        const g = P(t, s.gauge.at, 12), gx = 900, top = by - 420;
        rise(ctx, g, 40, () => {
          sheet(ctx, gx - 60, top - 40, 120, 460, 28, { elev: .8 });
          ctx.strokeStyle = C.ink3; ctx.lineWidth = 3;
          for (let i = 0; i <= 10; i++) { const y = top + i * 38, big = i % 5 === 0; ctx.beginPath(); ctx.moveTo(gx - (big ? 34 : 22), y); ctx.lineTo(gx + (big ? 34 : 22), y); ctx.stroke(); }
          const ny = top + 380;
          ctx.fillStyle = C.blue; ctx.beginPath(); ctx.roundRect(gx - 44, ny - 7, 88, 14, 7); ctx.fill();
          chip(ctx, gx - 80, ny, '0 cm', { align: 'right', size: 40, h: 80, fill: C.blue, color: C.white, border: false });
        });
      }
      if (s.stamp) stamp(ctx, s.stamp.x ?? cx, s.stamp.y ?? 760, s.stamp.text, P(t, s.stamp.at, 11), { size: 84, rot: -.08, solid: true });
      if (s.sim) {
        const q = P(t, s.sim.at + .5, 13), str = '> simulation.exe', n = Math.round(str.length * E.out(seg(t, s.sim.at + .5, s.sim.at + 1.2)));
        alpha(ctx, q, () => { sheet(ctx, W / 2 - 280, 250, 560, 96, 22, { elev: .6, fill: C.ink }); text(ctx, str.slice(0, n), W / 2 - 246, midBase(298, 40), { size: 40, weight: 600, fam: 'JetBrains Mono', color: C.white }); });
      }
    });
  },
};

// ---------------------------------------------------------------- giec: flip-book of yearly reports
// {from, to, rect: [x, y, w, h], yearKeys: [[at, 2021], ...], tally: {text, at}}
function report(ctx, x, y, w, h, year) {
  sheet(ctx, x, y, w, h, 30, { elev: 1.3 });
  text(ctx, 'RAPPORT DU GIEC', x + 60, y + 92, { size: 38, weight: 800, ls: 4, color: C.ink2 });
  text(ctx, String(year), x + 56, y + 250, { size: 170, weight: 800, ls: -7, color: C.ink });
  ctx.fillStyle = C.line; ctx.fillRect(x + 60, y + 300, w - 120, 3);
  for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.roundRect(x + 60, y + 340 + i * 42, (w - 120) * [1, .86, .62][i], 16, 8); ctx.fillStyle = C.dim; ctx.fill(); }
  text(ctx, 'Fin du monde :', x + 60, y + h - 70, { size: 46, weight: 800, color: C.ink });
  chip(ctx, x + w - 60, y + h - 86, 'dans 5 ans', { align: 'right', size: 46, h: 92, fill: C.blue, color: C.white, border: false });
}
const giec = {
  draw(R, s, t) {
    const { ctx } = R, [x, y, w, h] = s.rect || [120, 340, 840, 620];
    env(ctx, s, t, pin => {
      rise(ctx, pin, 60, () => {
        const ys = s.yearKeys; let i = 0; while (i + 1 < ys.length && t >= ys[i + 1][0]) i++;
        const nextAt = ys[i + 1]?.[0], curAt = ys[i][0];
        // outgoing report slides left, the new one arrives from the right
        if (i > 0) { const p = S(t - curAt, 13); if (p < .999) alpha(ctx, 1 - p, () => { ctx.save(); ctx.translate(-260 * p, 0); ctx.rotate(-.02 * p); report(ctx, x, y, w, h, ys[i - 1][1]); ctx.restore(); }); }
        const p = i > 0 ? S(t - curAt, 13) : 1;
        alpha(ctx, Math.min(1, p * 1.4), () => { ctx.save(); ctx.translate(320 * (1 - p), 0); report(ctx, x, y, w, h, ys[i][1]); ctx.restore(); });
        void nextAt;
        // tally row: one dot per report seen so far
        const n = ys.filter(([a]) => t >= a).length, dx = 44, x0 = W / 2 - (ys.length - 1) * dx / 2;
        for (let k = 0; k < ys.length; k++) { const q = P(t, ys[k][0], 14); ctx.beginPath(); ctx.arc(x0 + k * dx, y + h + 70, 11, 0, TAU); ctx.fillStyle = k < n ? mix(C.dim, C.ink, q) : C.dim; ctx.fill(); }
      });
      if (s.tally) { const q = P(t, s.tally.at, 13); if (q > .002) rise(ctx, q, 24, () => chip(ctx, W / 2, y + h + 160, s.tally.text, { size: 42, h: 88 })); }
    });
  },
};

// ---------------------------------------------------------------- bike: bins, then a 100 km commute
function bin(ctx, x, y, w, h, lbl) {
  sheet(ctx, x, y + 40, w, h - 40, 26, { elev: .9 });
  ctx.beginPath(); ctx.roundRect(x - 14, y, w + 28, 46, 16); ctx.fillStyle = C.ink; ctx.fill();
  ctx.beginPath(); ctx.roundRect(x + w / 2 - 34, y - 18, 68, 26, 10); ctx.strokeStyle = C.ink; ctx.lineWidth = 7; ctx.stroke();
  ctx.strokeStyle = C.dim; ctx.lineWidth = 8; ctx.lineCap = 'round';
  for (let i = 1; i < 4; i++) { const lx = x + w * i / 4; ctx.beginPath(); ctx.moveTo(lx, y + 90); ctx.lineTo(lx, y + h - 40); ctx.stroke(); }
  text(ctx, lbl, x + w / 2, y + h + 64, { size: 40, weight: 700, align: 'center', color: C.ink2 });
}
function bikeIcon(ctx, x, y, s, col, rot) {   // (x, y) = ground contact centre
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const r = 26;
  for (const wx of [-38, 38]) { ctx.beginPath(); ctx.arc(wx, -r, r, 0, TAU); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(-38, -r); ctx.lineTo(-8, -r); ctx.lineTo(18, -62); ctx.lineTo(-18, -62); ctx.lineTo(-8, -r); ctx.moveTo(-18, -62); ctx.lineTo(-38, -r); ctx.moveTo(18, -62); ctx.lineTo(38, -r); ctx.moveTo(18, -62); ctx.lineTo(14, -78); ctx.lineTo(26, -80); ctx.moveTo(-20, -68); ctx.lineTo(-10, -68); ctx.stroke();
  ctx.restore();
}
function house(ctx, x, y, col) { ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(x - 44, y); ctx.lineTo(x - 44, y - 56); ctx.lineTo(x, y - 94); ctx.lineTo(x + 44, y - 56); ctx.lineTo(x + 44, y); ctx.closePath(); ctx.stroke(); ctx.strokeRect(x - 12, y - 36, 24, 36); ctx.restore(); }
function office(ctx, x, y, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.strokeRect(x - 40, y - 130, 80, 130);
  ctx.fillStyle = col; for (let r = 0; r < 4; r++) for (let c = 0; c < 2; c++) ctx.fillRect(x - 24 + c * 30, y - 112 + r * 26, 16, 12); ctx.restore();
}
// {from, to, bins: {from, to, labels, strikeAt}, route: {from, countFrom, countTo, km, header}, sun: {from, to}}
const bike = {
  draw(R, s, t) {
    const { ctx } = R;
    env(ctx, s, t, () => {
      const b = s.bins;
      if (b) {
        const pin = S(t - b.from + (s.pre || 0), 12), out = b.to != null ? S(t - b.to, 14) : 0;
        alpha(ctx, 1 - out, () => {
          ctx.translate(0, -40 * out);
          const bw = 220, bh = 300, gap = 70, x0 = W / 2 - (bw * 3 + gap * 2) / 2, y = 470;
          (b.labels || ['Verre', 'Papier', 'Plastique']).forEach((l, i) => rise(ctx, S(t - b.from + (s.pre || 0) - i * .08, 12), 60, () => bin(ctx, x0 + i * (bw + gap), y, bw, bh, l)));
          void pin;
          const st = E.out(seg(t, b.strikeAt, b.strikeAt + .35));
          if (st > 0) {
            ctx.save(); ctx.strokeStyle = C.blue; ctx.lineWidth = 16; ctx.lineCap = 'round';
            const ax = x0 - 30, ay = y + bh + 40, bx = x0 + bw * 3 + gap * 2 + 30, by2 = y - 60;
            ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(lerp(ax, bx, st), lerp(ay, by2, st)); ctx.stroke(); ctx.restore();
          }
        });
      }
      const r = s.route;
      if (r && t > r.from - .6) {
        const pin = S(t - r.from, 12);
        const pts = [[150, 1000], [330, 1000], [420, 760], [620, 860], [760, 620], [880, 650]];
        const path = u => {   // catmull-rom through pts, u 0..1
          const n = pts.length - 1, f = clamp(u) * n, i = Math.min(n - 1, Math.floor(f)), k = f - i;
          const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(n, i + 2)];
          const cr = (a, b2, c, d) => .5 * ((2 * b2) + (-a + c) * k + (2 * a - 5 * b2 + 4 * c - d) * k * k + (-a + 3 * b2 - 3 * c + d) * k * k * k);
          return [cr(p0[0], p1[0], p2[0], p3[0]), cr(p0[1], p1[1], p2[1], p3[1])];
        };
        const prog = E.io(seg(t, r.countFrom, r.countTo));
        rise(ctx, pin, 50, () => {
          // sun crossing the sky (a day passes)
          if (s.sun) {
            const q = seg(t, s.sun.from, s.sun.to), a = Math.PI * (1 - q), sx = W / 2 + Math.cos(a) * 330, sy = 760 - Math.sin(a) * 290;
            alpha(ctx, P(t, s.sun.from - .3, 10) * (1 - S(t - s.sun.to, 10)), () => {
              ctx.strokeStyle = C.line; ctx.lineWidth = 3; ctx.setLineDash([4, 14]); ctx.beginPath(); ctx.ellipse(W / 2, 760, 330, 290, 0, Math.PI, TAU); ctx.stroke(); ctx.setLineDash([]);
              ctx.beginPath(); ctx.arc(sx, sy, 38, 0, TAU); ctx.fillStyle = C.sheet; ctx.fill(); ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.stroke();
              ctx.lineCap = 'round'; for (let i = 0; i < 8; i++) { const an = i * TAU / 8; ctx.beginPath(); ctx.moveTo(sx + Math.cos(an) * 54, sy + Math.sin(an) * 54); ctx.lineTo(sx + Math.cos(an) * 70, sy + Math.sin(an) * 70); ctx.stroke(); }
            });
          }
          // road
          ctx.lineCap = 'round'; ctx.lineJoin = 'round';
          ctx.beginPath(); for (let i = 0; i <= 80; i++) { const [x, y] = path(i / 80); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
          ctx.strokeStyle = C.dim; ctx.lineWidth = 22; ctx.stroke();
          ctx.setLineDash([2, 22]); ctx.strokeStyle = C.sheet; ctx.lineWidth = 6; ctx.stroke(); ctx.setLineDash([]);
          if (prog > 0) { ctx.beginPath(); for (let i = 0; i <= 80 * prog; i++) { const [x, y] = path(i / 80); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.strokeStyle = C.blue; ctx.lineWidth = 10; ctx.stroke(); }
          house(ctx, 110, 1000, C.ink); office(ctx, 975, 640, C.ink);
          const [bx, byy] = path(prog), [nx, ny] = path(Math.min(1, prog + .01));
          bikeIcon(ctx, bx, byy - 12, 1.1, C.ink, Math.atan2(ny - byy, nx - bx) * .6);
          // km counter
          const km = Math.round((r.km ?? 100) * prog);
          text(ctx, String(km), W / 2 + 40, 330, { size: 150, weight: 800, ls: -6, align: 'right', color: C.ink });
          text(ctx, 'km', W / 2 + 64, 330, { size: 150, weight: 800, ls: -6, color: C.blue });
        });
      }
    });
  },
};

// ---------------------------------------------------------------- equation: CQFD, IA = climat x10
function thermo(ctx, cx, cy, s, fill) {
  ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.lineWidth = 8; ctx.strokeStyle = C.ink; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(0, 60, 34, -Math.PI * .32, Math.PI * 1.32); ctx.lineTo(-18, -80); ctx.arc(0, -80, 18, Math.PI, 0); ctx.closePath(); ctx.stroke();
  ctx.beginPath(); ctx.arc(0, 60, 22, 0, TAU); ctx.fillStyle = C.blue; ctx.fill();
  const top = lerp(40, -84, fill); ctx.beginPath(); ctx.roundRect(-8, top, 16, 60 - top, 8); ctx.fill();
  for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(26, -70 + i * 26); ctx.lineTo(40, -70 + i * 26); ctx.lineWidth = 5; ctx.stroke(); }
  ctx.restore();
}
// {from, to, cqfd: {at}, ia: {at}, climate: {at, fillFrom, fillTo}, boost: {at, text}, end: {at, text}}
const equation = {
  draw(R, s, t) {
    const { ctx } = R, size = 290, y = 540, xl = 120, xr = W - 120 - size;
    env(ctx, s, t, () => {
      if (s.cqfd) stamp(ctx, W / 2, 320, 'CQFD', P(t, s.cqfd.at, 11), { size: 96, rot: -.05, solid: true });
      const pa = P(t, s.ia?.at, 12), pc = P(t, s.climate?.at, 12);
      if (pa > .002) rise(ctx, pa, 60, () => {
        sheet(ctx, xl, y, size, size, 62, { elev: 1.2 });
        text(ctx, 'IA', xl + size / 2, midBase(y + size / 2, 150), { size: 150, weight: 800, ls: -6, align: 'center', color: C.blue });
        text(ctx, "L'IA", xl + size / 2, y + size + 70, { size: 44, weight: 800, align: 'center', color: C.ink });
      });
      const eq = P(t, s.climate?.at != null ? s.climate.at - .1 : null, 13);
      if (eq > .002) rise(ctx, eq, 30, () => text(ctx, '=', W / 2, midBase(y + size / 2, 140), { size: 140, weight: 800, align: 'center', color: C.ink3 }));
      if (pc > .002) rise(ctx, pc, 60, () => {
        sheet(ctx, xr, y, size, size, 62, { elev: 1.2 });
        thermo(ctx, xr + size / 2 - 8, y + size / 2 + 6, 1.05, E.io(seg(t, s.climate.fillFrom ?? s.climate.at, s.climate.fillTo ?? s.climate.at + 1)));
        text(ctx, 'Le climat', xr + size / 2, y + size + 70, { size: 44, weight: 800, align: 'center', color: C.ink });
      });
      if (s.boost) { const q = P(t, s.boost.at, 12); if (q > .002) rise(ctx, q, 30, () => chip(ctx, xr + size + 16, y - 10, s.boost.text || '×10', { align: 'right', size: 58, h: 108, padX: 34, fill: C.blue, color: C.white, border: false, scale: .9 + .1 * q })); }
      if (s.end) stamp(ctx, W / 2, 1080, s.end.text, P(t, s.end.at, 11), { size: 70, rot: .05, solid: true });
    });
  },
};

// ---------------------------------------------------------------- crowd: GPT -> Mistral, then the pyramid
const OPENAI = typeof Path2D !== 'undefined' ? new Path2D('M252.794 108.802C289.191 99.0484 326.265 110.305 351.148 135.135C385.113 126.072 422.85 134.862 449.492 161.505C476.136 188.149 484.925 225.888 475.862 259.85V259.854C500.696 284.735 511.95 321.81 502.198 358.207C492.447 394.602 464.161 421.084 430.215 430.217C421.083 464.162 394.603 492.448 358.206 502.199C321.812 511.951 284.734 500.693 259.852 475.864C225.887 484.927 188.15 476.137 161.507 449.495C134.864 422.851 126.073 385.111 135.136 351.149C110.304 326.266 99.0496 289.192 108.801 252.795C118.552 216.4 146.84 189.918 180.784 180.785C189.917 146.841 216.396 118.553 252.794 108.802ZM374.292 407.145C374.292 411.271 372.092 415.086 368.517 417.148L283.723 466.102C302.487 480.585 327.555 486.459 352.217 479.852C386.997 470.532 410.068 439.312 410.555 405.006V317.717C410.555 315.08 409.125 312.621 406.843 311.303L374.292 292.509V407.145ZM251.868 415.897C248.296 417.959 243.893 417.959 240.317 415.897L155.526 366.942C152.366 390.436 159.811 415.08 177.866 433.136H177.863C203.325 458.594 241.896 462.962 271.85 446.232L347.449 402.586C349.735 401.268 351.148 398.8 351.148 396.163V358.579L251.868 415.897ZM368.602 220.628C366.319 219.309 363.474 219.318 361.191 220.637L328.641 239.431L427.921 296.749C431.496 298.811 433.697 302.627 433.697 306.752V404.661C455.622 395.654 473.244 376.881 479.851 352.218C489.169 317.442 473.668 281.85 444.201 264.274L368.602 220.628ZM177.303 206.34C155.377 215.348 137.756 234.122 131.148 258.783C121.832 293.561 137.331 329.153 166.799 346.727L242.398 390.373C244.68 391.692 247.525 391.684 249.807 390.366L282.357 371.572L183.078 314.253C179.504 312.189 177.303 308.375 177.303 304.251V206.34ZM259.849 279.145V331.858L305.5 358.213L351.15 331.858V279.145L305.5 252.789L259.849 279.145ZM327.276 144.9C308.512 130.418 283.445 124.543 258.782 131.15C224.002 140.471 200.931 171.691 200.445 205.995V293.286C200.445 295.923 201.875 298.381 204.158 299.7L236.707 318.493V203.856C236.707 199.731 238.909 195.916 242.483 193.853L327.276 144.9ZM433.137 177.867C407.675 152.407 369.103 148.038 339.149 164.769L263.55 208.415C261.265 209.734 259.852 212.202 259.852 214.838V252.423L359.132 195.105C362.703 193.041 367.108 193.041 370.682 195.105L455.473 244.06C458.635 220.567 451.189 195.922 433.135 177.867H433.137Z') : null;
function openaiLogo(ctx, cx, cy, size, col) { ctx.save(); const k = size / 420; ctx.translate(cx - 305.5 * k, cy - 305.5 * k); ctx.scale(k, k); ctx.fillStyle = col; ctx.fill(OPENAI, 'evenodd'); ctx.restore(); }
// Mistral "M" in pixel blocks (5 x 5 grid of 46.5 px cells on a 256 x 233 art board), front face ink, shadow ink3
const MISTRAL = [[0, 0], [4, 0], [0, 1], [1, 1], [3, 1], [4, 1], [0, 2], [2, 2], [4, 2], [0, 3], [4, 3], [0, 4], [4, 4]];
function mistralLogo(ctx, cx, cy, size, col, col2) {
  const c = size / 5.5, x0 = cx - size / 2, y0 = cy - c * 2.5;
  for (const [gx, gy] of MISTRAL) { ctx.fillStyle = col2; ctx.fillRect(x0 + gx * c, y0 + gy * c, c, c); ctx.fillStyle = col; ctx.fillRect(x0 + gx * c + c * .5, y0 + gy * c, c, c); }
}
function logoTile(ctx, x, y, size, kind, act, lbl) {
  sheet(ctx, x, y, size, size, 58, { elev: .5 + .7 * act });
  if (act > .01) alpha(ctx, act, () => { ctx.beginPath(); ctx.roundRect(x - 9, y - 9, size + 18, size + 18, 66); ctx.strokeStyle = C.blue; ctx.lineWidth = 6; ctx.stroke(); });
  const col = mix(C.ink3, C.ink, .35 + .65 * act);
  if (kind === 'openai') openaiLogo(ctx, x + size / 2, y + size / 2, size * .56, col);
  else mistralLogo(ctx, x + size / 2, y + size / 2, size * .5, col, mix(C.dim, C.ink3, act));
  text(ctx, lbl, x + size / 2, y + size + 66, { size: 46, weight: 800, ls: -.8, align: 'center', color: col });
}
// {from, to, header: {text, at}, tilesAt, leaveAt, flowAt, pyrAt, lowAt, eliteAt, samAt, bestAt, n: 40, elite: 4}
const crowd = {
  draw(R, s, t) {
    const { ctx } = R, n = s.n || 40, ne = s.elite || 4, size = 250, ty = 420, xl = 150, xr = W - 150 - size;
    env(ctx, s, t, pin => {
      const pyr = S(t - s.pyrAt, 7), tilesOut = S(t - s.pyrAt, 12);
      // phase A: tiles + header
      alpha(ctx, 1 - tilesOut, () => {
        ctx.translate(0, -60 * tilesOut);
        if (s.header) rise(ctx, P(t, s.header.at - (s.pre || 0), 12), 40, () => text(ctx, s.header.text, W / 2, 320, { size: 64, weight: 800, ls: -1.5, align: 'center' }));
        const flow = S(t - s.flowAt, 8), leave = P(t, s.leaveAt, 10);
        rise(ctx, P(t, s.tilesAt, 12), 50, () => {
          logoTile(ctx, xl, ty, size, 'openai', 1 - flow, 'GPT');
          logoTile(ctx, xr, ty, size, 'mistral', flow, 'Mistral');
          // arrow between the tiles
          const ax0 = xl + size + 40, ax1 = xr - 40, ay = ty + size / 2, g = E.out(seg(t, s.leaveAt, s.leaveAt + .5));
          if (g > 0) { ctx.strokeStyle = C.ink; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; const xe = lerp(ax0, ax1, g); ctx.beginPath(); ctx.moveTo(ax0, ay); ctx.lineTo(xe, ay); ctx.moveTo(xe - 22, ay - 22); ctx.lineTo(xe, ay); ctx.lineTo(xe - 22, ay + 22); ctx.stroke(); }
          void leave;
        });
      });
      // pyramid frame (phase B)
      const apex = [W / 2, 430], baseY = 1150, baseW = 880, cutY = 690;
      const fr = E.out(seg(t, s.pyrAt + .1, s.pyrAt + .9));
      if (fr > 0) {
        ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 5; ctx.lineJoin = 'round';
        ctx.beginPath(); ctx.moveTo(W / 2 - baseW / 2, baseY); ctx.lineTo(apex[0], apex[1]); ctx.lineTo(W / 2 + baseW / 2, baseY); ctx.closePath();
        ctx.setLineDash([2400 * fr, 2400]); ctx.stroke(); ctx.setLineDash([]);
        const half = (cutY - apex[1]) / (baseY - apex[1]) * baseW / 2;
        alpha(ctx, fr, () => { ctx.setLineDash([10, 12]); ctx.lineWidth = 3; ctx.strokeStyle = C.ink3; ctx.beginPath(); ctx.moveTo(W / 2 - half, cutY); ctx.lineTo(W / 2 + half, cutY); ctx.stroke(); ctx.setLineDash([]); });
        ctx.restore();
        const ql = P(t, s.lowAt, 12);
        if (ql > .002) rise(ctx, ql, 24, () => { mistralLogo(ctx, W / 2 - 150, 1070, 58, C.ink, C.ink3); text(ctx, '& co', W / 2 - 100, midBase(1070, 44), { size: 44, weight: 800, color: C.ink2 }); });
        const qb = P(t, s.bestAt, 12);
        if (qb > .002) rise(ctx, qb, 24, () => { sheet(ctx, W / 2 - 85, 215, 170, 170, 44, { elev: 1.1 }); openaiLogo(ctx, W / 2, 300, 108, C.ink); });
      }
      // the crowd
      const cols = 8, r = 17, gap = 44;
      for (let i = 0; i < n; i++) {
        const isE = i >= n - ne, j = isE ? i - (n - ne) : i;
        const gA = [xl + size / 2 + ((i % cols) - (cols - 1) / 2) * gap * .78, ty + size + 150 + Math.floor(i / cols) * gap * .9];
        const k = n - ne, colsB = 8, gB = [xr + size / 2 + ((j % colsB) - (colsB - 1) / 2) * gap * .78, ty + size + 150 + Math.floor(j / colsB) * gap * .9];
        // pyramid slots: the crowd fills the lower trapezoid, the elite sits near the apex
        let gC;
        if (isE) gC = [W / 2 + (j - (ne - 1) / 2) * 50, 610];
        else {
          const rowsC = [14, 12, 10], ri = j < rowsC[0] ? 0 : j < rowsC[0] + rowsC[1] ? 1 : 2, ci = j - rowsC.slice(0, ri).reduce((a, b) => a + b, 0), cnt = Math.min(rowsC[ri], k - rowsC.slice(0, ri).reduce((a, b) => a + b, 0));
          gC = [W / 2 + (ci - (cnt - 1) / 2) * 54, 1100 - ri * 58 - 70];
        }
        const f = isE ? 0 : S(t - s.flowAt - j * .025, 9), p = pyr > 0 ? S(t - s.pyrAt - .2 - (isE ? .3 : j * .012), 8) : 0;
        let x = lerp(gA[0], gB[0], f), y = lerp(gA[1], gB[1], f) - Math.sin(f * Math.PI) * 90;
        x = lerp(x, gC[0], p); y = lerp(y, gC[1], p);
        const appear = P(t, s.tilesAt + .15 + i * .012, 12); if (appear <= .002) continue;
        const el = isE ? P(t, s.eliteAt, 12) : 0;
        alpha(ctx, Math.min(1, appear * 1.4) * (1 - tilesOut * 0) , () => {
          ctx.beginPath(); ctx.arc(x, y + (1 - appear) * 30, r * (isE ? 1 + .25 * el : 1), 0, TAU); ctx.fillStyle = isE ? mix(C.ink2, C.blue, el) : mix(C.ink2, C.ink3, p * .4); ctx.fill();
        });
      }
      // elite ring + labels
      const qe = P(t, s.eliteAt, 12);
      if (qe > .002) alpha(ctx, qe, () => { ctx.beginPath(); ctx.roundRect(W / 2 - 120, 610 - 44, 240, 88, 44); ctx.strokeStyle = C.blue; ctx.lineWidth = 5; ctx.stroke(); });
      const qs = P(t, s.samAt, 12);
      if (qs > .002) rise(ctx, qs, 20, () => { ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(W / 2 + 124, 610); ctx.lineTo(W / 2 + 190, 610); ctx.stroke(); chip(ctx, W / 2 + 196, 610, 'Sam Altman', { align: 'left', size: 42, h: 86, fill: C.ink, color: C.white, border: false }); });
      void pin;
    });
  },
};

// ---------------------------------------------------------------- cheque
// {rect: [x, y, w], logo: 'assets/logos/x.png', payer, city, no, date, payee, words, memo, amount, currency: '$',
//  writeAt (payee + words + signature written), countFrom, countTo (amount 0 -> amount), zeroAt (rolls back to 0),
//  stampAt, stamp: 'SANS PROVISION'}. Height is fixed (560).
const HAND = '"Bradley Hand", "Snell Roundhand", cursive';
const money = (v, cur) => Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ' + cur;
function handwrite(ctx, str, x, y, size, p, color) {   // revealed left to right like a pen
  if (p <= .002) return; const w = measure(ctx, str, size, 700, 0, HAND) + 20;
  ctx.save(); ctx.beginPath(); ctx.rect(x - 10, y - size * 1.3, w * p, size * 1.9); ctx.clip();
  text(ctx, str, x, y, { size, weight: 700, fam: HAND, color }); ctx.restore();
}
function scribble(ctx, x, y, w, p, color) {   // abstract signature, drawn progressively
  if (p <= .002) return; const n = 70; ctx.save(); ctx.beginPath();
  for (let i = 0; i <= n * p; i++) { const u = i / n, xx = x + u * w + Math.sin(u * TAU * 4.3) * 20, yy = y - Math.sin(u * TAU * 2.1 + 1) * 22 * (1 - u * .5) - Math.cos(u * TAU * 6.4) * 9; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
  ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); ctx.restore();
}
const cheque = {
  draw(R, s, t) {
    const { ctx } = R, [x, y, w] = s.rect || [60, 300, W - 120], h = 560, pad = 48, cur = s.currency || '$';
    env(ctx, s, t, p => rise(ctx, p, 90, () => {
      sheet(ctx, x, y, w, h, 34, { elev: 1.4 });
      ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 34); ctx.clip();   // guilloche + blue edge band
      ctx.strokeStyle = 'rgba(37,142,255,.075)'; ctx.lineWidth = 2;
      for (let k = 0; k < 16; k++) { ctx.beginPath(); for (let i = 0; i <= 80; i++) { const u = i / 80, xx = x + u * w, yy = y + 20 + k * 34 + Math.sin(u * TAU * 2.5 + k * .55) * 16; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.stroke(); }
      ctx.fillStyle = C.blue; ctx.fillRect(x, y, 16, h); ctx.restore();
      const lx = x + pad + 8;
      // header: logo, payer, number, date
      const im = s.logo ? R.img('/p/' + s.logo) : null;
      if (im) { ctx.save(); ctx.beginPath(); ctx.roundRect(lx, y + 40, 84, 84, 20); ctx.clip(); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, lx, y + 40, 84, 84); ctx.restore(); }
      const nx = lx + (im ? 84 + 24 : 0);
      text(ctx, s.payer || '', nx, y + 82, { size: 42, weight: 800, ls: -.8 });
      if (s.city) text(ctx, s.city, nx, y + 122, { size: 34, weight: 500, color: C.ink3 });
      if (s.no) text(ctx, s.no, x + w - pad, y + 82, { size: 34, weight: 600, color: C.ink3, align: 'right' });
      if (s.date) text(ctx, s.date, x + w - pad, y + 122, { size: 34, weight: 600, color: C.ink2, align: 'right' });
      ctx.fillStyle = C.line; ctx.fillRect(lx, y + 164, w - pad * 2 - 8, 2);
      // payee
      const pw = E.io(seg(t, s.writeAt ?? 1e9, (s.writeAt ?? 1e9) + .8));
      text(ctx, "Payez à l'ordre de", lx, y + 226, { size: 34, weight: 500, color: C.ink3 });
      ctx.fillStyle = C.ink3; ctx.fillRect(lx, y + 312, w - pad * 2 - 8, 2);
      handwrite(ctx, s.payee || '', lx + 10, y + 298, 84, pw, C.ink);
      // amount in words (struck when the amount rolls back) + amount box
      const zw = s.zeroAt != null ? E.io(seg(t, s.zeroAt, s.zeroAt + .45)) : 0;
      text(ctx, 'La somme de', lx, y + 376, { size: 34, weight: 500, color: C.ink3 });
      ctx.fillStyle = C.ink3; ctx.fillRect(lx, y + 448, 470, 2);
      const ww = E.io(seg(t, (s.writeAt ?? 1e9) + .5, (s.writeAt ?? 1e9) + 1.3));
      handwrite(ctx, s.words || '', lx + 6, y + 436, 50, ww, mix(C.ink, C.ink3, zw));
      if (zw > .002 && s.words) { const sw = measure(ctx, s.words, 50, 700, 0, HAND); ctx.fillStyle = C.blue; ctx.fillRect(lx, y + 420, (sw + 16) * zw, 5); }
      const bw = 360, bx = x + w - pad - bw, by = y + 352, bh = 116;
      ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 22); ctx.fillStyle = C.tint; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = C.blue; ctx.stroke();
      const up = E.out(seg(t, s.countFrom ?? 1e9, s.countTo ?? 1e9)), v = (s.amount || 0) * up * (1 - zw);
      const vs = v >= 1e5 ? Math.round(v / 1e4) * 1e4 : Math.round(v / 10) * 10;
      text(ctx, money(vs, cur), bx + bw / 2, midBase(by + bh / 2, 58), { size: 58, weight: 800, ls: -1.6, align: 'center', color: mix(C.blue, C.ink3, zw) });
      // memo + signature
      if (s.memo) text(ctx, s.memo, lx, y + 516, { size: 34, weight: 500, color: C.ink2 });
      ctx.fillStyle = C.ink3; ctx.fillRect(x + w - pad - 260, y + 520, 260, 2);
      scribble(ctx, x + w - pad - 236, y + 498, 210, E.io(seg(t, (s.writeAt ?? 1e9) + .9, (s.writeAt ?? 1e9) + 1.7)), C.ink);
      if (s.stamp) stamp(ctx, x + w / 2, y + h / 2 + 10, s.stamp, P(t, s.stampAt, 11), { size: 74, rot: -.09, solid: true });
    }));
  },
};

export const STORY = { foilHat, stampOver, sea, giec, bike, equation, crowd, cheque };
