// Crash scene: a car rams a real 3D brick wall, drawn in perspective (no pose image). Same contract as scenes.js,
// times already mapped to SHORT time.
//   crashWall  a road in perspective, a brick wall that builds up course by course (every brick a shaded 3D box with
//              ink edges and a ground shadow), the car sticker that arrives, revs, rams it at hitAt and sinks into the
//              hole; the bricks around the impact burst out with real tumbling (rigid 3D boxes, gravity, bounces,
//              they settle flat on the road), the ones above the hole collapse, dust, blue burst, camera shake + punch.
//              {from, to, car (image path, front facing right), carH 470, enterAt, buildAt, ramAt, hitAt,
//               lane .8 (car lane across the wall, in bricks from its centre), rows 8, cols 6, brick ([len, h, thick] 120 56 62), color '#C8603E', yaw .62, pitch .3,
//               cx 600, cy 1215 (screen point of the impact face bottom centre), outDx}
import { C, clamp, lerp, E, S, leave, hash } from './kit.js';

const TAU = Math.PI * 2;
const hex = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const shade = (rgb, k) => `rgb(${rgb.map(v => Math.round(k < 1 ? v * k : v + (255 - v) * (k - 1))).join(',')})`;
const live = (s, t) => t >= s.from - 1 && t <= (s.to ?? 1e9) + 1;
function alpha(ctx, a, fn) { if (a <= .002) return; ctx.save(); ctx.globalAlpha *= a; fn(); ctx.restore(); }

// rotation matrix from Euler angles (x then y then z), applied to a local vector
function rot(v, [rx, ry, rz]) {
  let [x, y, z] = v, c = Math.cos(rx), s = Math.sin(rx);
  [y, z] = [y * c - z * s, y * s + z * c];
  c = Math.cos(ry); s = Math.sin(ry); [x, z] = [x * c + z * s, -x * s + z * c];
  c = Math.cos(rz); s = Math.sin(rz); [x, y] = [x * c - y * s, x * s + y * c];
  return [x, y, z];
}
const CORNERS = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]];
const FACES = [[0, 3, 2, 1, [0, 0, -1]], [4, 5, 6, 7, [0, 0, 1]], [0, 4, 7, 3, [-1, 0, 0]], [1, 2, 6, 5, [1, 0, 0]], [3, 7, 6, 2, [0, 1, 0]], [0, 1, 5, 4, [0, -1, 0]]];
const LIGHT = (() => { const l = [-.45, .8, -.42], n = Math.hypot(...l); return l.map(v => v / n); })();

// the wall: courses of bricks in running bond, impact face at X = 0, the wall spans Z (across the road)
function layout(s) {
  const [L, h, T] = s.brick || [120, 56, 62], rows = s.rows || 8, cols = s.cols || 6, gap = 5, W = cols * L, out = [];
  for (let r = 0; r < rows; r++) {
    const off = r % 2 ? L / 2 : 0, cuts = [];
    for (let z = -W / 2 - off; z < W / 2 - .1; z += L) cuts.push([Math.max(z, -W / 2), Math.min(z + L, W / 2)]);
    for (const [a, b] of cuts) {
      if (b - a < 10) continue;
      out.push({ r, c: [T / 2, h * r + h / 2, (a + b) / 2], half: [T / 2 - gap / 2, h / 2 - gap / 2, (b - a) / 2 - gap / 2] });
    }
  }
  return { bricks: out, L, h, T, W, rows };
}

// deterministic rigid-body pass for one brick from its release to time t
function simulate(b, i, t, hit, wall, lane) {
  const imp = [0, wall.h * 2.2, lane], R = s => hash(i * 7.31 + s);
  const d = Math.hypot(b.c[0] - imp[0], (b.c[1] - imp[1]) * 1.15, b.c[2] - imp[2]);
  const blast = d < wall.h * 5.4, above = !blast && Math.abs(b.c[2] - lane) < wall.L * 1.7 && b.c[1] > imp[1];
  if (!blast && !above) return { p: b.c, a: [0, 0, 0] };
  const rel = hit + (blast ? 0 : .07 + (b.c[1] - imp[1]) / 2600 + R(1) * .05);
  if (t <= rel) return { p: b.c, a: [0, 0, 0] };
  let p = [...b.c], a = [0, 0, 0], v, w;
  if (blast) {
    const k = 1 - d / (wall.h * 5.4), dir = [b.c[0] - imp[0] + 60, b.c[1] - imp[1] + 70, b.c[2] - imp[2]], n = Math.hypot(...dir);
    const sp = 450 + 1050 * Math.sqrt(k) + 400 * R(2);
    v = [dir[0] / n * sp + 330 + 380 * R(3), dir[1] / n * sp * .7 + 300 + 380 * R(4), dir[2] / n * sp * 1.1 + (R(5) - .5) * 420];
    w = [(R(6) - .5) * 22, (R(7) - .5) * 9, (R(8) - .5) * 22];
  } else { v = [120 + 260 * R(3), 0, (R(5) - .5) * 160]; w = [(R(6) - .5) * 5, 0, -2 - 4 * R(8)]; }
  const dt = 1 / 120, g = 2700, steps = Math.min(600, Math.floor((t - rel) / dt));
  let rest = 0;
  for (let n = 0; n < steps; n++) {
    v[1] -= g * dt;
    for (let k = 0; k < 3; k++) { p[k] += v[k] * dt; a[k] += w[k] * dt; }
    const low = Math.min(...CORNERS.map(q => rot([q[0] * b.half[0], q[1] * b.half[1], q[2] * b.half[2]], a)[1]));
    if (p[1] + low < 0) {
      p[1] = -low;
      if (v[1] < 0) v[1] = -v[1] * .28;
      v[0] *= .72; v[2] *= .72; w = w.map(x => x * .55);
    }
    if (p[1] + low < 2) {   // resting on the road: tip over onto the nearest face
      rest++; v[0] *= .96; v[2] *= .96;
      if (rest > 10) { w = w.map(x => x * .8); a[0] += (Math.round(a[0] / (Math.PI / 2)) * Math.PI / 2 - a[0]) * .12; a[2] += (Math.round(a[2] / (Math.PI / 2)) * Math.PI / 2 - a[2]) * .12; }
    }
  }
  return { p, a };
}

const crashWall = {
  needs(s, t) { return live(s, t) && s.car ? ['/p/' + s.car] : []; },
  draw(R, s, t) {
    const { ctx } = R;
    const out = s.to != null ? leave(t - s.to) : 0, pin = S(t - s.from, 12);
    if (pin <= .002 || out >= 1) return;
    const wall = layout(s), rgb = hex(s.color || '#C8603E'), hit = s.hitAt ?? s.from + 2.6;
    const ya = s.yaw ?? .62, pa = s.pitch ?? .3, f = s.zoom ? 2400 * s.zoom : 2750, D = 2400, cx = s.cx ?? 560, cy = s.cy ?? 1250;
    const cyw = Math.cos(ya), syw = Math.sin(ya), cp = Math.cos(pa), sp = Math.sin(pa);
    const view = ([X, Y, Z]) => { const x1 = X * cyw - Z * syw, z1 = X * syw + Z * cyw; return [x1, Y * cp + z1 * sp, z1 * cp - Y * sp]; };
    const proj = P => { const [x, y, z] = view(P), k = f / (D + z); return [cx + x * k, cy - y * k, z, k]; };
    const poly = (pts, fill, stroke, lw) => {
      ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath();
      if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
    };
    const th = t - hit, after = th > 0, lane = (s.lane ?? .8) * wall.L;

    alpha(ctx, (1 - out) * Math.min(1, pin * 1.4), () => {
      ctx.translate((s.outDx ?? -820) * out * out, 60 * (1 - pin));
      // camera shake + zoom punch on impact
      if (after) {
        const e = Math.exp(-th * 6.5), A = 30 * e, [ix, iy] = proj([0, wall.h * 2.2, lane]), z = 1 + .085 * Math.exp(-th * 5) * Math.min(1, th * 30);
        ctx.translate(A * Math.sin(th * 91), A * .8 * Math.cos(th * 77));
        ctx.translate(ix, iy); ctx.scale(z, z); ctx.translate(-ix, -iy);
      }
      // ---- road in perspective
      const rp = E.out(clamp((t - s.from) / .45));
      const roadW = 430, x0 = -2600, x1 = lerp(x0, 1900, rp);
      poly([proj([x0, 0, -roadW]), proj([x1, 0, -roadW]), proj([x1, 0, roadW]), proj([x0, 0, roadW])].map(q => q.slice(0, 2)), '#E9E3D6');
      ctx.lineCap = 'round';
      for (const z of [-roadW, roadW]) { const a = proj([x0, 0, z]), b = proj([x1, 0, z]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.strokeStyle = C.ink; ctx.lineWidth = 7; ctx.stroke(); }
      for (let x = x0 + 80; x < x1 - 160; x += 300) { const a = proj([x, 0, -roadW * .55]), b = proj([x + 150, 0, -roadW * .55]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.strokeStyle = C.ink3; ctx.lineWidth = 6; ctx.stroke(); }

      // ---- car position (front bumper X), revs, rams, sinks into the hole
      const enter = s.enterAt ?? s.from, ram = s.ramAt ?? hit - .44, idleX = -640;
      let carX;
      if (t < ram) carX = lerp(-2300, idleX, E.out(clamp((t - enter) / .62))) - 70 * E.io(clamp((t - enter - .9) / (ram - enter - .9)));
      else if (!after) carX = lerp(idleX - 70, 0, Math.pow(clamp((t - ram) / (hit - ram)), 2.2));
      else carX = 190 * E.out(clamp(th / .2)) - 25 * E.io(clamp((th - .2) / .5));
      const rev = t > enter + .6 && t < ram ? Math.sin(t * 95) * 3.5 : 0;
      const tilt = after ? -.13 * Math.exp(-th * 5) * Math.sin(clamp(th / .06) * Math.PI / 2) : t > ram ? .03 * clamp((t - ram) / .2) : 0;

      // ---- bricks: build up, then the blast
      const build = s.buildAt ?? s.from + .2;
      const items = wall.bricks.map((b, i) => {
        const bp = S(t - build - b.r * .07 - hash(i * 3.3) * .05, 13); if (bp <= .002) return null;
        const st = after ? simulate(b, i, t, hit, wall, lane) : { p: b.c, a: [0, 0, 0] };
        const p = [st.p[0], st.p[1] + 260 * (1 - bp), st.p[2]];
        const pts = CORNERS.map(q => { const r = rot([q[0] * b.half[0], q[1] * b.half[1], q[2] * b.half[2]], st.a); return [p[0] + r[0], p[1] + r[1], p[2] + r[2]]; });
        return { kind: 'brick', i, p, a: st.a, pts, depth: view(p)[2], fade: Math.min(1, bp * 1.6) };
      }).filter(Boolean);

      // ground shadows first
      for (const it of items) {
        const k = .2 * clamp(1 - it.p[1] / 700) * it.fade;
        if (k <= .01) continue;
        const ys = it.pts.map(q => q[1]), lo = Math.min(...ys);
        const foot = it.pts.filter(q => q[1] < lo + 30).map(q => proj([q[0] + 14, 0, q[2] - 10]));
        if (foot.length < 3) continue;
        const c = foot.reduce((a, q) => [a[0] + q[0] / foot.length, a[1] + q[1] / foot.length], [0, 0]);
        foot.sort((u, w) => Math.atan2(u[1] - c[1], u[0] - c[0]) - Math.atan2(w[1] - c[1], w[0] - c[0]));
        poly(foot, `rgba(40,28,18,${k})`);
      }
      const im = s.car && R.img('/p/' + s.car), ch = s.carH || 470;
      const carP = proj([carX - 190, 0, lane]), carDepth = view(after ? [0, 120, lane - wall.L * .9] : [carX - 140, 120, lane])[2];
      if (im) {   // car shadow on the road
        const a = proj([carX - 420, 0, lane - 90]), b = proj([carX - 10, 0, lane + 90]);
        ctx.save(); ctx.fillStyle = 'rgba(40,28,18,.16)'; ctx.beginPath();
        ctx.ellipse((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 4, Math.abs(b[0] - a[0]) / 2 + 30, 26 * carP[3], 0, 0, TAU); ctx.fill(); ctx.restore();
      }
      const drawCar = () => {
        if (!im) return;
        const k = carP[3], hgt = ch * k, wid = hgt * im.width / im.height;
        // the bumper sits at (0.95, 0.9) of the sticker: anchor it on the car's front bottom
        const fx = proj([carX, 0, lane])[0], fy = carP[1] + rev * .3;
        // speed lines while it rams
        if (t > ram && t < hit + .05) {
          const q = clamp((t - ram) / .15);
          ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.lineCap = 'round';
          for (let j = 0; j < 3; j++) { const y = fy - hgt * (.22 + j * .14), x = fx - wid * 1.02; ctx.beginPath(); ctx.moveTo(x - 60 - 220 * q, y); ctx.lineTo(x - 60, y); ctx.stroke(); }
          ctx.restore();
        }
        ctx.save(); ctx.translate(fx, fy); ctx.rotate(tilt);
        const sq = after ? 1 - .07 * Math.exp(-th * 7) * Math.min(1, th * 25) : 1;
        ctx.scale(sq, 2 - sq); ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(im, -wid * .95, -hgt * .9, wid, hgt); ctx.restore();
      };

      // painter: everything sorted far to near, the car in the list as one item
      const list = [...items, { kind: 'car', depth: carDepth }].sort((u, w) => w.depth - u.depth);
      for (const it of list) {
        if (it.kind === 'car') { drawCar(); continue; }
        const P = it.pts.map(proj);
        alpha(ctx, it.fade, () => {
          ctx.lineJoin = 'round';
          for (const [a, b, c, d, n] of FACES) {
            const q = [P[a], P[b], P[c], P[d]];
            const cr = (q[1][0] - q[0][0]) * (q[2][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[2][0] - q[0][0]);
            if (cr >= 0) continue;
            const wn = rot(n, it.a), l = Math.max(0, wn[0] * LIGHT[0] + wn[1] * LIGHT[1] + wn[2] * LIGHT[2]);
            poly(q, shade(rgb, .74 + .5 * l), C.ink, 2.6);
            if (l > .5 && Math.abs(wn[0]) > .6) {   // a few pits on the lit big face: baked-clay texture
              ctx.fillStyle = shade(rgb, .82);
              for (let j = 0; j < 3; j++) {
                const u = .2 + .6 * hash(it.i * 9 + j), v = .25 + .5 * hash(it.i * 5 + j * 2);
                const x = lerp(lerp(q[0][0], q[1][0], u), lerp(q[3][0], q[2][0], u), v), y = lerp(lerp(q[0][1], q[1][1], u), lerp(q[3][1], q[2][1], u), v);
                ctx.beginPath(); ctx.arc(x, y, 2.6, 0, TAU); ctx.fill();
              }
            }
          }
        });
      }

      // ---- impact: cracks a beat before, blue ring + burst lines, dust clouds
      const [ix, iy] = proj([0, wall.h * 2.2, lane]);
      if (after && th < .5) {
        const q = E.out(clamp(th / .22)), fade = 1 - clamp((th - .16) / .2);
        alpha(ctx, fade, () => {
          ctx.strokeStyle = C.blue; ctx.lineCap = 'round';
          ctx.lineWidth = 9; ctx.beginPath(); ctx.arc(ix, iy, 40 + 220 * q, 0, TAU); ctx.stroke();
          for (let j = 0; j < 10; j++) {
            const an = j / 10 * TAU + .3, r0 = 90 + 170 * q, r1 = r0 + 110 * q * (.7 + .3 * hash(j));
            ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(ix + Math.cos(an) * r0, iy + Math.sin(an) * r0); ctx.lineTo(ix + Math.cos(an) * r1, iy + Math.sin(an) * r1); ctx.stroke();
          }
        });
      }
      if (after) {
        for (let j = 0; j < 6; j++) {
          const st = .04 + j * .05, x = th - st; if (x <= 0 || x > 1.2) continue;
          const g = E.out(clamp(x / .8)), fade = 1 - clamp((x - .55) / .65);
          const wp = proj([70 + hash(j * 2.1) * 220 * g, 20 + 120 * g * hash(j * 4.7), lane + (j % 2 ? 1 : -1) * (180 + 260 * hash(j * 3.9)) * g]);
          const r = (34 + 46 * hash(j * 1.7)) * (.4 + .6 * g) * wp[3];
          alpha(ctx, fade, () => {
            const puffs = [0, 1, 2].map(m => [wp[0] + (m - 1) * r * .7, wp[1] - (m === 1 ? r * .35 : 0), r * (m === 1 ? 1 : .75)]);
            ctx.strokeStyle = C.ink; ctx.lineWidth = 8;   // one clean outline around the union: stroke wide, then fill over it
            for (const [x, y, rr] of puffs) { ctx.beginPath(); ctx.arc(x, y, rr, 0, TAU); ctx.stroke(); }
            ctx.fillStyle = '#ECE7DD';
            for (const [x, y, rr] of puffs) { ctx.beginPath(); ctx.arc(x, y, rr, 0, TAU); ctx.fill(); }
          });
        }
      }
    });
  },
};

export const CRASH = { crashWall };
