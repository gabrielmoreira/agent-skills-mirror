import * as THREE from "three/webgpu";

const P = 6;                                   // points per strand
const S = 64 * Math.round(420000 / 64);        // strand count
const FLOOR = -0.87;

const HS = 0.36;                               // hand scale (world units per hand unit)

// ─────────────────────────────────────────────────────────────
// CPU helpers: creature shape + grooming
// ─────────────────────────────────────────────────────────────
const sstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const nrm3 = (x, y, z) => { const l = Math.hypot(x, y, z) || 1; return [x / l, y / l, z / l]; };
const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross3 = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dist3 = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const gauss = (d, s) => Math.exp(-(d * d) / (2 * s * s));

function ihash(i, j, k) {
  let h = (Math.imul(i, 374761393) + Math.imul(j, 668265263) + Math.imul(k, 1274126177)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}
function vnoise(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  let xf = x - xi, yf = y - yi, zf = z - zi;
  xf = xf * xf * (3 - 2 * xf); yf = yf * yf * (3 - 2 * yf); zf = zf * zf * (3 - 2 * zf);
  const c000 = ihash(xi, yi, zi), c100 = ihash(xi + 1, yi, zi), c010 = ihash(xi, yi + 1, zi), c110 = ihash(xi + 1, yi + 1, zi);
  const c001 = ihash(xi, yi, zi + 1), c101 = ihash(xi + 1, yi, zi + 1), c011 = ihash(xi, yi + 1, zi + 1), c111 = ihash(xi + 1, yi + 1, zi + 1);
  return lerp(lerp(lerp(c000, c100, xf), lerp(c010, c110, xf), yf), lerp(lerp(c001, c101, xf), lerp(c011, c111, xf), yf), zf);
}
const fbm = (x, y, z) => 0.5 * vnoise(x, y, z) + 0.3 * vnoise(x * 2.1 + 5.2, y * 2.1 + 1.3, z * 2.1 + 7.7) + 0.2 * vnoise(x * 4.3 + 1.7, y * 4.3 + 9.2, z * 4.3 + 3.1);

// ears
const EARS = [nrm3(-0.5, 0.83, 0.0), nrm3(0.5, 0.83, 0.0)].map(e => {
  const f = [0, 0, 1], d = dot3(f, e);
  const w = nrm3(f[0] - e[0] * d, f[1] - e[1] * d, f[2] - e[2] * d);
  return { e, w, u: cross3(e, w) };
});
const EAR_R = 0.4, EAR_H = 0.62;
let earK = 0, earDW = 0, earIdx = 0;
function evalEar(x, y, z) {
  earK = 0; earDW = 0;
  for (let i = 0; i < 2; i++) {
    const E = EARS[i];
    if (x * E.e[0] + y * E.e[1] + z * E.e[2] < 0.5) continue;
    const du = x * E.u[0] + y * E.u[1] + z * E.u[2];
    const dw = x * E.w[0] + y * E.w[1] + z * E.w[2];
    const k = 1 - Math.sqrt(du * du + dw * dw * 3.2) / EAR_R;
    if (k > earK) { earK = k; earDW = dw; earIdx = i; }
  }
}

const CHEEKS = [nrm3(-0.7, -0.25, 0.65), nrm3(0.7, -0.25, 0.65)];
const BOT = -0.62;
// unit direction -> surface point
function shape(x, y, z, o) {
  evalEar(x, y, z);
  let r = 1 + (earK > 0 ? EAR_H * Math.pow(earK, 1.6) : 0);
  for (const C of CHEEKS) r += 0.07 * Math.exp(-(1 - (x * C[0] + y * C[1] + z * C[2])) / 0.08);
  r *= 1 - 0.07 * y;
  const px = x * r * 1.06, pz = z * r;
  let py = y * r * 0.95;
  const s = py - BOT;
  if (s < 0) py = BOT + 0.45 * s - 0.55 * 0.15 * (1 - Math.exp(s / 0.15));
  o[0] = px; o[1] = py; o[2] = pz;
}

const _a = [0, 0, 0], _b = [0, 0, 0], _c = [0, 0, 0], _d = [0, 0, 0];
// position, outward normal and area stretch at a unit direction
function surfWith(fn, x, y, z) {
  const d = [x, y, z];
  const t1 = Math.abs(y) < 0.9 ? nrm3(...cross3(d, [0, 1, 0])) : nrm3(...cross3(d, [1, 0, 0]));
  const t2 = cross3(d, t1);
  const e = 1e-3;
  let q;
  q = nrm3(x + t1[0] * e, y + t1[1] * e, z + t1[2] * e); fn(q[0], q[1], q[2], _a);
  q = nrm3(x - t1[0] * e, y - t1[1] * e, z - t1[2] * e); fn(q[0], q[1], q[2], _b);
  q = nrm3(x + t2[0] * e, y + t2[1] * e, z + t2[2] * e); fn(q[0], q[1], q[2], _c);
  q = nrm3(x - t2[0] * e, y - t2[1] * e, z - t2[2] * e); fn(q[0], q[1], q[2], _d);
  const da = [_a[0] - _b[0], _a[1] - _b[1], _a[2] - _b[2]];
  const db = [_c[0] - _d[0], _c[1] - _d[1], _c[2] - _d[2]];
  const n = cross3(da, db);
  const nl = Math.hypot(n[0], n[1], n[2]) || 1e-9;
  const p = [0, 0, 0]; fn(x, y, z, p);
  return { p, n: [n[0] / nl, n[1] / nl, n[2] / nl], J: nl / (4 * e * e) };
}
const surf = (x, y, z) => surfWith(shape, x, y, z);

// face landmarks (as unit directions)
const EYES = [nrm3(-0.34, 0.13, 0.93), nrm3(0.34, 0.13, 0.93)];
const NOSE = nrm3(0, -0.06, 1), MUZ = nrm3(0, -0.17, 1);
const BLUSH = [nrm3(-0.56, -0.1, 0.82), nrm3(0.56, -0.1, 0.82)];
const FLUFF = [nrm3(-0.8, -0.3, 0.52), nrm3(0.8, -0.3, 0.52)];
const BELLY = nrm3(0, -0.55, 0.84);

// colour masks: [cream, stripe, earTip, blush]
function pattern(d, out) {
  evalEar(d[0], d[1], d[2]);
  const n1 = fbm(d[0] * 3.1 + 11, d[1] * 3.1, d[2] * 3.1);
  const earW = sstep(0.0, 0.15, earK);
  const inner = earK > 0 ? sstep(0.12, 0.35, earK) * sstep(0.0, 0.05, earDW) * (1 - sstep(0.78, 0.92, earK)) : 0;
  let cream = sstep(0.32, 0.7, dot3(d, BELLY) + (n1 - 0.5) * 0.3);
  cream = Math.max(cream, 1 - sstep(0.1, 0.27, dist3(d, MUZ)));
  cream *= 1 - earW;
  const phi = Math.atan2(d[0], -d[2]);
  const band = Math.sin(phi * 7 + n1 * 5 + d[1] * 1.5);
  const back = sstep(-0.15, 0.4, -d[2] * 0.8 + d[1] * 0.55);
  let stripe = sstep(0.25, 0.8, band) * back;
  const fh = sstep(0.32, 0.55, d[1]) * sstep(0.1, 0.4, d[2]) * (1 - sstep(0.3, 0.4, Math.abs(d[0])));
  stripe = Math.max(stripe, sstep(0.55, 0.92, Math.cos(d[0] * 26)) * fh);
  stripe *= (1 - cream) * (1 - earW * 0.7);
  const tip = earK > 0 ? sstep(0.62, 0.88, earK) * (1 - inner) : 0;
  let blush = Math.max(gauss(dist3(d, BLUSH[0]), 0.075), gauss(dist3(d, BLUSH[1]), 0.075)) * 0.8;
  blush = Math.max(blush, inner * 0.85);
  out[0] = cream; out[1] = stripe; out[2] = tip; out[3] = blush;
  return { earW, inner };
}

// length, flow direction and bend for a strand
function groom(d, n, r1, r2, r3, pat) {
  const { earW, inner } = pattern(d, pat);
  const clump = fbm(d[0] * 9 + 3, d[1] * 9, d[2] * 9);
  let len = 0.12 * (0.82 + 0.36 * r1) * (0.8 + 0.4 * clump);
  const fl = Math.max(gauss(dist3(d, FLUFF[0]), 0.22), gauss(dist3(d, FLUFF[1]), 0.22));
  len *= 1 + 0.55 * fl;
  len *= 1 + 0.15 * sstep(0.4, 0.8, dot3(d, BELLY));
  len *= lerp(1, 0.72, sstep(0.75, 0.95, d[2]));
  let bend = 0.95 * (0.85 + 0.3 * r2) * (1 - 0.2 * fl);
  let tuft = 0;
  if (earK > 0) {
    len = lerp(len, 0.065 * (0.8 + 0.4 * r1), earW);
    len = lerp(len, 0.03, inner);
    tuft = sstep(0.82, 0.97, earK);
    len = lerp(len, 0.16 * (0.8 + 0.4 * r1), tuft);
    bend = lerp(bend, 0.55, earW);
    bend = lerp(bend, 0.25, tuft);
  }
  // keep eyes, nose and mouth clear
  const eDist = Math.min(...EYES.map(E => Math.hypot(d[0] - E[0], (d[1] - E[1]) * 0.85, d[2] - E[2])));
  len *= lerp(0.05, 1, sstep(0.135, 0.22, eDist));
  len *= lerp(0.25, 1, sstep(0.08, 0.24, dist3(d, MUZ)));

  // flow: down/back on the body, outward from the nose on the face, toward the tip on ears
  let g = [0, -0.65, -1];
  const fw = sstep(0.3, 0.8, d[2]) * (1 - earW);
  const rad = nrm3(d[0] - NOSE[0], d[1] - NOSE[1] + 1e-4, d[2] - NOSE[2]);
  g = [lerp(g[0], rad[0] * 1.5, fw), lerp(g[1], rad[1] * 1.5, fw), lerp(g[2], rad[2] * 1.5, fw)];
  if (earK > 0) {
    const E = EARS[earIdx].e;
    const tipDir = [E[0] * 1.5 + (E[0] - d[0]) * 3, E[1] * 1.5 + (E[1] - d[1]) * 3, E[2] * 1.5 + (E[2] - d[2]) * 3];
    g = [lerp(g[0], tipDir[0], earW), lerp(g[1], tipDir[1], earW), lerp(g[2], tipDir[2], earW)];
  }
  const gn = dot3(g, n);
  let F = [g[0] - n[0] * gn, g[1] - n[1] * gn, g[2] - n[2] * gn];
  if (Math.hypot(...F) < 1e-4) F = cross3(n, Math.abs(n[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0]);
  F = nrm3(...F);
  const a = (r3 - 0.5) * 0.6, B = cross3(n, F);
  F = nrm3(F[0] * Math.cos(a) + B[0] * Math.sin(a), F[1] * Math.cos(a) + B[1] * Math.sin(a), F[2] * Math.cos(a) + B[2] * Math.sin(a));
  return { len, F, bend };
}

function randDir() {
  const z = Math.random() * 2 - 1, ph = Math.random() * Math.PI * 2, r = Math.sqrt(1 - z * z);
  return [r * Math.cos(ph), r * Math.sin(ph), z];
}

// ─────────────────────────────────────────────────────────────
// The rest of the cat: sitting loaf body, front paws, curled tail (all in "body space")
// The head lives in its own space: world = HEAD_C + local * SH (before the head turns)
// ─────────────────────────────────────────────────────────────
const HEAD_C = [0, 1.0, 0.25], SH = 0.82;
const NECK = [0, 0.45, 0.1];
const BODY_C = [0, -0.1, -0.38];
const softFloor = (py, B, k, keep) => { const s = py - B; return s < 0 ? B + keep * s - (1 - keep) * k * (1 - Math.exp(s / k)) : py; };

function bodyShape(x, y, z, o) {
  const rx = 0.9 * (1 - 0.13 * y), ry = 0.8, rz = 1.0 * (1 - 0.06 * y);
  let px = x * rx, py = y * ry, pz = z * rz;
  const c = Math.max(0, z * 0.9 + y * 0.3); pz += 0.08 * c * c;                       // chest
  const hip = Math.exp(-((y + 0.35) ** 2) / 0.12) * Math.max(0, -z); px *= 1 + 0.08 * hip; // haunches
  o[0] = px + BODY_C[0]; o[1] = softFloor(py + BODY_C[1], FLOOR + 0.1, 0.08, 0.35); o[2] = pz + BODY_C[2];
}
const PAWS = [[-0.34, FLOOR + 0.12, 0.6], [0.34, FLOOR + 0.12, 0.6]];
const pawShape = c => (x, y, z, o) => {
  const toes = z > 0 ? 1 + 0.05 * z * Math.abs(Math.sin(Math.atan2(x, z) * 4.5)) : 1;
  o[0] = c[0] + x * 0.19 * toes; o[2] = c[2] + z * 0.27 * toes;
  o[1] = softFloor(c[1] + y * 0.13, FLOOR + 0.035, 0.03, 0.3);
};

const tailCurve = new THREE.CatmullRomCurve3([
  [0.3, FLOOR + 0.32, -1.12], [0.7, FLOOR + 0.15, -1.0], [0.92, FLOOR + 0.13, -0.45],
  [0.9, FLOOR + 0.13, 0.1], [0.72, FLOOR + 0.13, 0.5], [0.6, FLOOR + 0.15, 0.8],
].map(v => new THREE.Vector3(...v)), false, 'centripetal');
const TAIL_N = 400;
const tailPts = tailCurve.getSpacedPoints(TAIL_N);
const tailFr = tailCurve.computeFrenetFrames(TAIL_N, false);
const tailR = u => 0.125 * lerp(1, 0.75, u) * (u > 0.88 ? Math.sqrt(Math.max(0, 1 - ((u - 0.88) / 0.12) ** 2)) : 1);
function tailAt(u, th, o) {
  const f = Math.min(TAIL_N - 1e-6, Math.max(0, u * TAIL_N)), i = Math.floor(f), t = f - i;
  const C = tailPts[i].clone().lerp(tailPts[i + 1], t);
  const Nn = tailFr.normals[i].clone().lerp(tailFr.normals[i + 1], t).normalize();
  const Bn = tailFr.binormals[i].clone().lerp(tailFr.binormals[i + 1], t).normalize();
  const r = tailR(u);
  o[0] = C.x + r * (Nn.x * Math.cos(th) + Bn.x * Math.sin(th));
  o[1] = C.y + r * (Nn.y * Math.cos(th) + Bn.y * Math.sin(th));
  o[2] = C.z + r * (Nn.z * Math.cos(th) + Bn.z * Math.sin(th));
  return C;
}
function tailSurf(u, th) {
  const e = 1e-3; u = Math.min(1 - e, Math.max(e, u));
  tailAt(u + e, th, _a); tailAt(u - e, th, _b); tailAt(u, th + e, _c); tailAt(u, th - e, _d);
  const pu = [(_a[0] - _b[0]) / (2 * e), (_a[1] - _b[1]) / (2 * e), (_a[2] - _b[2]) / (2 * e)];
  const pt = [(_c[0] - _d[0]) / (2 * e), (_c[1] - _d[1]) / (2 * e), (_c[2] - _d[2]) / (2 * e)];
  let n = cross3(pu, pt);
  const J = Math.hypot(...n);
  const p = [0, 0, 0]; const C = tailAt(u, th, p);
  if ((p[0] - C.x) * n[0] + (p[1] - C.y) * n[1] + (p[2] - C.z) * n[2] < 0) n = n.map(v => -v);
  return { p, n: nrm3(...n), J, T: nrm3(...pu) };
}

// inside tests (body space), used to cull hairs buried inside another part
const _s = [0, 0, 0];
function insideStar(fn, c, p) {
  const q = [p[0] - c[0], p[1] - c[1], p[2] - c[2]], l = Math.hypot(...q) || 1e-9;
  fn(q[0] / l, q[1] / l, q[2] / l, _s);
  return l < Math.hypot(_s[0] - c[0], _s[1] - c[1], _s[2] - c[2]) * 0.97;
}
function insideHead(p) {
  const q = [(p[0] - HEAD_C[0]) / SH, (p[1] - HEAD_C[1]) / SH, (p[2] - HEAD_C[2]) / SH], l = Math.hypot(...q) || 1e-9;
  shape(q[0] / l, q[1] / l, q[2] / l, _s);
  return l < Math.hypot(..._s) * 0.97;
}
const insideBody = p => insideStar(bodyShape, BODY_C, p);
const insidePaws = p => PAWS.some(c => insideStar(pawShape(c), c, p));
function insideTail(p) {
  if (p[1] > FLOOR + 0.45 || p[0] < 0.1) return false;
  for (let i = 0; i <= TAIL_N; i += 4) {
    const C = tailPts[i];
    if (Math.hypot(p[0] - C.x, p[1] - C.y, p[2] - C.z) < tailR(i / TAIL_N) * 0.95) return true;
  }
  return false;
}

// grooming for the non-head parts → { len, F, bend } and pattern [cream, stripe, tip, blush]
function finishFlow(g, n, r3) {
  const gn = dot3(g, n);
  let F = [g[0] - n[0] * gn, g[1] - n[1] * gn, g[2] - n[2] * gn];
  if (Math.hypot(...F) < 1e-4) F = cross3(n, Math.abs(n[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0]);
  F = nrm3(...F);
  const a = (r3 - 0.5) * 0.6, B = cross3(n, F);
  return nrm3(F[0] * Math.cos(a) + B[0] * Math.sin(a), F[1] * Math.cos(a) + B[1] * Math.sin(a), F[2] * Math.cos(a) + B[2] * Math.sin(a));
}
function bodyPattern(d, p, out) {
  const n1 = fbm(p[0] * 2.6 + 4, p[1] * 2.6, p[2] * 2.6);
  const chest = sstep(0.4, 0.78, dot3(d, nrm3(0, 0.1, 1)) + (n1 - 0.5) * 0.3);
  const band = Math.sin(p[2] * 8.5 + n1 * 4.5 + Math.abs(p[0]) * 1.5);
  const region = sstep(-0.45, 0.15, d[1] + (n1 - 0.5) * 0.3);
  let stripe = sstep(0.3, 0.8, band) * region;
  stripe = Math.max(stripe, Math.exp(-(d[0] * d[0]) / 0.012) * sstep(0.1, 0.5, d[1]) * 0.9);   // dorsal line
  stripe *= 1 - chest;
  out[0] = chest; out[1] = stripe; out[2] = 0; out[3] = 0;
  return chest;
}
function groomBody(d, p, n, r1, r2, r3, pat) {
  const chest = bodyPattern(d, p, pat);
  const clump = fbm(p[0] * 8 + 1, p[1] * 8, p[2] * 8);
  let len = 0.13 * (0.82 + 0.36 * r1) * (0.8 + 0.4 * clump);
  len *= 1 + 0.45 * chest * sstep(-0.3, 0.3, d[1]);                                         // chest ruff
  const g = [0, lerp(-0.55, -1, chest), lerp(-1, 0.15, chest)];
  return { len, F: finishFlow(g, n, r3), bend: 0.95 * (0.85 + 0.3 * r2) };
}
function groomPaw(d, p, n, r1, r2, r3, pat) {
  pat[0] = 1; pat[1] = 0; pat[2] = 0; pat[3] = 0;
  return { len: 0.05 * (0.8 + 0.4 * r1), F: finishFlow([0, -0.4, 1], n, r3), bend: 1.1 * (0.85 + 0.3 * r2) };
}
function tailPattern(u, out) {
  const ring = sstep(0.25, 0.75, Math.sin(u * 32)) * sstep(0.08, 0.2, u);
  out[0] = 0; out[1] = Math.max(ring, sstep(0.84, 0.9, u)); out[2] = 0; out[3] = 0;
}
function groomTail(u, T, p, n, r1, r2, r3, pat) {
  tailPattern(u, pat);
  return { len: 0.13 * (0.82 + 0.36 * r1), F: finishFlow(T, n, r3), bend: 1.05 * (0.85 + 0.3 * r2) };
}

// part descriptors: sample → { p (part space), pb (body space, for culling), n, J, groom }
const PARTS = [
  {
    head: true, measure: 4 * Math.PI,
    sample() {
      const d = randDir(), s = surf(...d);
      return { ...s, J: s.J * SH * SH, pb: [HEAD_C[0] + s.p[0] * SH, HEAD_C[1] + s.p[1] * SH, HEAD_C[2] + s.p[2] * SH],
        groom: (r1, r2, r3, pat) => groom(d, s.n, r1, r2, r3, pat) };
    },
    cull: pb => insideBody(pb),
  },
  {
    measure: 4 * Math.PI,
    sample() {
      const d = randDir(), s = surfWith(bodyShape, ...d);
      return { ...s, pb: s.p, groom: (r1, r2, r3, pat) => groomBody(d, s.p, s.n, r1, r2, r3, pat) };
    },
    cull: pb => insideHead(pb) || insidePaws(pb) || insideTail(pb),
  },
  ...PAWS.map(c => ({
    measure: 4 * Math.PI,
    sample() {
      const d = randDir(), s = surfWith(pawShape(c), ...d);
      return { ...s, pb: s.p, groom: (r1, r2, r3, pat) => groomPaw(d, s.p, s.n, r1, r2, r3, pat) };
    },
    cull: pb => insideBody(pb),
  })),
  {
    measure: 2 * Math.PI,
    sample() {
      const u = Math.random(), th = Math.random() * Math.PI * 2, s = tailSurf(u, th);
      return { ...s, pb: s.p, groom: (r1, r2, r3, pat) => groomTail(u, s.T, s.p, s.n, r1, r2, r3, pat) };
    },
    cull: pb => insideBody(pb),
  },
];
for (const part of PARTS) {
  let sum = 0, mx = 0;
  for (let i = 0; i < 12000; i++) { const J = part.sample().J; sum += J; mx = Math.max(mx, J); }
  part.area = (sum / 12000) * part.measure;
  part.maxJ = mx * 1.15;
}
const AREA = PARTS.reduce((a, p) => a + p.area, 0);

// skin meshes
function starGeo(fn, ws, hs, patFn) {
  const geo = new THREE.SphereGeometry(1, ws, hs);
  const pos = geo.attributes.position, nor = geo.attributes.normal;
  const pat = patFn ? new Float32Array(pos.count * 4) : null;
  const tmp = [0, 0, 0, 0];
  for (let i = 0; i < pos.count; i++) {
    const d = nrm3(pos.getX(i), pos.getY(i), pos.getZ(i));
    const s = surfWith(fn, d[0], d[1], d[2]);
    pos.setXYZ(i, s.p[0], s.p[1], s.p[2]);
    nor.setXYZ(i, s.n[0], s.n[1], s.n[2]);
    if (pat) { patFn(d, s.p, tmp); pat.set(tmp, i * 4); }
  }
  if (pat) geo.setAttribute('aPattern', new THREE.BufferAttribute(pat, 4));
  geo.computeBoundingSphere();
  return geo;
}
function tailGeo(nu, nt, withPat) {
  const pos = [], nor = [], pat = [], idx = [], tmp = [0, 0, 0, 0];
  for (let j = 0; j <= nu; j++) for (let i = 0; i <= nt; i++) {
    const u = j / nu, s = tailSurf(u, (i / nt) * Math.PI * 2);
    pos.push(...s.p); nor.push(...s.n);
    if (withPat) { tailPattern(u, tmp); pat.push(...tmp); }
  }
  for (let j = 0; j < nu; j++) for (let i = 0; i < nt; i++) {
    const a = j * (nt + 1) + i, b = a + nt + 1;
    idx.push(a, a + 1, b, a + 1, b + 1, b);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  if (withPat) g.setAttribute('aPattern', new THREE.Float32BufferAttribute(pat, 4));
  g.setIndex(idx);
  g.computeBoundingSphere();
  return g;
}


export {
  AREA,
  BODY_C,
  EYES,
  FLOOR,
  HEAD_C,
  HS,
  NECK,
  NOSE,
  PAWS,
  PARTS,
  P,
  S,
  SH,
  bodyPattern,
  bodyShape,
  groomBody,
  nrm3,
  pattern,
  pawShape,
  shape,
  sstep,
  starGeo,
  surf,
  tailGeo,
};
