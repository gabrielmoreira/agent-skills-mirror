import * as THREE from 'three/webgpu';
import {
  Fn, uniform, uniformArray, attribute, varyingProperty, vec2, vec3, vec4, float, int, ivec2,
  textureLoad, positionLocal, positionWorld, positionView, positionGeometry, normalGeometry, cameraPosition,
  modelWorldMatrix, mix, smoothstep, clamp, abs, max, min, pow, exp, sin, cos, sqrt, normalize, cross, dot,
  length, floor, fract, atan, mod, luminance, texture, hash, instanceIndex, uv, pass, mrt, output, time, renderOutput,
  Loop, If, screenUV, select, convertToTexture, tan, cameraViewMatrix, reflect, sign
} from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
import { gaussianBlur } from 'three/addons/tsl/display/GaussianBlurNode.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

/** Animated tissue, appendage mechanics and depth-ordered underwater optics.
 * Scene units: one unit is approximately 15 cm. Caller owns camera motion.
 */
export async function createLuminescentJellyfish({
  renderer, camera, seed = 7, msaa = 4, fullRect = false, blur = true,
}) {
const SEED = seed;

const OPTICS = {                                     // water + lens
  // beam attenuation c = a + b per unit (1 unit ≈ 15 cm): pure-water absorption (red ≫ green > blue) plus particle scattering
  absorption: new THREE.Vector3(0.075, 0.034, 0.024), // per unit (1 unit ≈ hero bell radius ≈ 15 cm)
  fov: 40, focus: 7.2, cocAtInfinity: 12, exposure: 1.0,
};
const SWIM = { thrust: 0.36, drag: 1.0 };
const WARMUP = 8;                                    // seconds simulated before the first frame (t = 0 is the hero composition)

// ───────────────────────────── deterministic rng ─────────────────────────────
function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const rng = mulberry32(SEED * 9973 + 17);
const rr = (a, b) => a + (b - a) * rng();
const PHI_MAX = 1.66, HB = 0.82, LAP_D = 0.075, N_LAPPET = 16;     // 32 lappets / 32 notches
const LOBE_A = 0.035;                                                // exumbrella lobes: grooves run from the crown into each notch
const COSM = Math.cos(PHI_MAX);
const HT = HB * (1 - COSM);                                          // apex height above rim
const thick = s => 0.20 * Math.pow(1 - s, 1.4) + 0.012;
const lappet = th => Math.sqrt(Math.abs(Math.sin(N_LAPPET * th)));
const phiEdge = th => PHI_MAX - LAP_D * (1 - lappet(th));
function outerP(phi) { return [Math.sin(phi), HB * (Math.cos(phi) - COSM)]; }
function outerN(phi) { const nx = HB * Math.sin(phi), ny = Math.cos(phi), l = Math.hypot(nx, ny); return [nx / l, ny / l]; }
function innerP(phi, s) { const o = outerP(phi), n = outerN(phi), t = thick(s); return [o[0] - n[0] * t, o[1] - n[1] * t]; }

// radius of inner / outer surface at height y (rest pose, lookup)
const PROFILE = (() => {
  const N = 400, out = [], inn = [];
  for (let i = 0; i <= N; i++) { const s = i / N, phi = s * PHI_MAX; out.push(outerP(phi)); inn.push(innerP(phi, s)); }
  const at = (arr, y) => { // outermost crossing, scanning in from the margin (inner surface dips at the apex lens)
    const n = arr.length - 1;
    if (y <= arr[n][1]) return arr[n][0];
    for (let i = n; i > 0; i--) { const a = arr[i], b = arr[i - 1]; if ((a[1] - y) * (b[1] - y) <= 0) { const t = (y - a[1]) / ((b[1] - a[1]) || 1e-9); return a[0] + (b[0] - a[0]) * t; } }
    return 0;
  };
  const innerTop = inn[0][1];
  return { outerR: y => at(out, y), innerR: y => at(inn, y), innerTop, innerY(r) { // height of inner surface at radius r
    for (let i = 1; i < inn.length; i++) if (inn[i][0] >= r) { const a = inn[i - 1], b = inn[i], t = (r - a[0]) / (b[0] - a[0]); return a[1] + (b[1] - a[1]) * t; }
    return inn[inn.length - 1][1]; } };
})();

// Contraction field shared by bell, core, tentacle roots and arm roots (bijective → no new intersections)
// c = apex contraction, cm = margin contraction (the wave reaches the margin later)
function deformJS(x, y, z, c, cm, t, seed) {
  const u = Math.min(1, Math.max(0, 1 - y / HT)), w = u * u, ce = c + (cm - c) * w;
  const th = Math.atan2(z, x);
  const wob = Math.sin(th * 2 + t * 0.9 + seed) * 0.012 * w;
  const sr = 1 - ce * 0.17 * w + wob;
  const ny = y + ce * (y * 0.07 - w * w * 0.03);
  return [x * sr, ny, z * sr];
}
const deformTSL = (p, c0, cm, seed) => {
  const u = float(1).sub(p.y.div(HT)).clamp(0, 1);
  const w = u.mul(u);
  const c = c0.add(cm.sub(c0).mul(w));
  const th = atan(p.z, p.x);
  const wob = sin(th.mul(2).add(time.mul(0.9)).add(seed)).mul(0.012).mul(w);
  const sr = float(1).sub(c.mul(0.17).mul(w)).add(wob);
  const ny = p.y.add(c.mul(p.y.mul(0.07).sub(w.mul(w).mul(0.03))));
  // inverse-transpose Jacobian for normals (radial scale sr(y), vertical map g(y))
  const inside = smoothstep(0.0, 0.001, p.y).mul(float(1).sub(smoothstep(HT - 0.001, HT, p.y)));
  const srd = c.mul(0.34).mul(u).div(HT).mul(inside);
  const gd = float(1).add(c.mul(float(0.07).add(u.mul(u).mul(u).mul(0.12).div(HT).mul(inside))));
  return { p: vec3(p.x.mul(sr), ny, p.z.mul(sr)), sr, srd, gd };
};
const deformNormal = (p, n, d) => normalize(vec3(
  n.x.div(d.sr),
  n.y.div(d.gd).sub(p.x.mul(n.x).add(p.z.mul(n.z)).mul(d.srd).div(d.sr.mul(d.gd))),
  n.z.div(d.sr)));

// ───────────────────────────── tissue micro-texture (generated once, tileable) ─────────────────────────────
// R: distance to nearest cell nucleus (F1), G: cell-wall distance (F2−F1), B: smooth value-noise fbm
function makeCellTexture(N = 256, cells = 16, seed = SEED) {
  const r = mulberry32(seed * 31 + 5), pts = new Float32Array(cells * cells * 2);
  for (let i = 0; i < cells * cells; i++) { pts[i * 2] = r(); pts[i * 2 + 1] = r(); }
  const G = 8, grid = new Float32Array(G * G * 4); const r2 = mulberry32(seed * 7 + 3); for (let i = 0; i < grid.length; i++) grid[i] = r2();
  const vnoise = (x, y, g, o) => { x *= g; y *= g; const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi, sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    const at = (a, b) => grid[(((a % g) + g) % g + (((b % g) + g) % g) * g) * 4 + o];
    return (at(xi, yi) * (1 - sx) + at(xi + 1, yi) * sx) * (1 - sy) + (at(xi, yi + 1) * (1 - sx) + at(xi + 1, yi + 1) * sx) * sy; };
  const data = new Uint8Array(N * N * 4);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const u = (x + 0.5) / N * cells, v = (y + 0.5) / N * cells, cx = Math.floor(u), cy = Math.floor(v);
    let f1 = 9, f2 = 9;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const gx = cx + dx, gy = cy + dy, k = (((gx % cells) + cells) % cells) + (((gy % cells) + cells) % cells) * cells;
      const px = gx + pts[k * 2], py = gy + pts[k * 2 + 1], d = Math.hypot(px - u, py - v);
      if (d < f1) { f2 = f1; f1 = d; } else if (d < f2) f2 = d;
    }
    const fb = vnoise(x / N, y / N, 4, 0) * 0.55 + vnoise(x / N, y / N, 8, 1) * 0.3 + vnoise(x / N, y / N, 8, 2) * 0.15;
    const o = (y * N + x) * 4;
    data[o] = Math.min(255, f1 * 1.4 * 255); data[o + 1] = Math.min(255, (f2 - f1) * 2 * 255); data[o + 2] = fb * 255; data[o + 3] = 255;
  }
  const t = new THREE.DataTexture(data, N, N, THREE.RGBAFormat, THREE.UnsignedByteType);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter;
  t.generateMipmaps = true; t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true;
  return t;
}
const cellTex = makeCellTexture();
const cells = uvn => texture(cellTex, uvn);

// ───────────────────────────── shared shading helpers ─────────────────────────────
const uSigma = uniform(OPTICS.absorption);
const uExposure = uniform(OPTICS.exposure);
const absorb = dist => exp(uSigma.mul(dist).negate());
const sq = x => x.mul(x);                            // (pow(x, 2) is NaN for x < 0 in WGSL)
// individual pigment/emission hue: h ∈ [-1, 1] runs from bluer to pinker animals
const hueTint = h => vec3(float(1).add(h.mul(0.28)), float(1).sub(h.mul(0.06)), float(1).sub(h.mul(0.10)));
const jellyParams = uniformArray(Array.from({ length: 16 }, () => new THREE.Vector4(1, 0, 0, 0)), 'vec4');   // (glow, hue, -, -)
const viewDirW = () => normalize(cameraPosition.sub(positionWorld));

// ───────────────────────────── bell geometry ─────────────────────────────
function buildBellGeometry(NS = 44, NT = 192) {
  const rows = [];   // each row: array of {p,n,s,layer}
  const ringPt = (s, j, layer) => {
    const th = j / NT * Math.PI * 2, phi = s * phiEdge(th);
    const groove = 1;                                               // lobe relief is applied in the shader (with its normals)
    let r, y, n;
    if (layer === 0) { [r, y] = outerP(phi); n = outerN(phi); }
    else { [r, y] = innerP(phi, s); n = outerN(phi); n = [-n[0], -n[1]]; }
    r *= groove;
    return { p: [r * Math.cos(th), y, r * Math.sin(th)], n: [n[0] * Math.cos(th), n[1], n[0] * Math.sin(th)], s, th, layer };
  };
  for (let i = 0; i <= NS; i++) rows.push(Array.from({ length: NT + 1 }, (_, j) => ringPt(i / NS, j, 0)));
  rows.push(Array.from({ length: NT + 1 }, (_, j) => {             // rounded lip at the margin
    const th = j / NT * Math.PI * 2, phi = phiEdge(th);
    const o = outerP(phi), inn = innerP(phi, 1), t = [Math.cos(phi), -HB * Math.sin(phi)], tl = Math.hypot(t[0], t[1]);
    const tk = thick(1) * 0.7, r = (o[0] + inn[0]) / 2 + t[0] / tl * tk, y = (o[1] + inn[1]) / 2 + t[1] / tl * tk;
    return { p: [r * Math.cos(th), y, r * Math.sin(th)], n: [t[0] / tl * Math.cos(th), t[1] / tl, t[0] / tl * Math.sin(th)], s: 1, th, layer: 0.5 };
  }));
  for (let i = NS; i >= 0; i--) rows.push(Array.from({ length: NT + 1 }, (_, j) => ringPt(i / NS, j, 1)));
  const W = NT + 1, pos = [], nrm = [], aS = [], aTh = [], aL = [], idx = [];
  rows.forEach(row => row.forEach(v => { pos.push(...v.p); nrm.push(...v.n); aS.push(v.s); aTh.push(v.th); aL.push(v.layer); }));
  for (let r = 0; r < rows.length - 1; r++) for (let j = 0; j < NT; j++) {
    const a = r * W + j, b = a + 1, c = a + W, d = c + 1; idx.push(a, c, b, b, c, d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
  g.setAttribute('aS', new THREE.Float32BufferAttribute(aS, 1));
  g.setAttribute('aTheta', new THREE.Float32BufferAttribute(aTh, 1));
  g.setAttribute('aLayer', new THREE.Float32BufferAttribute(aL, 1));
  g.setIndex(idx);
  return g;
}

// Gonads: four folded, frilled curtains hanging from the subumbrella, inside the cavity by construction
function buildCoreGeometry(NA = 72, NV = 10) {
  const pos = [], nrm = [], aA = [], aV = [], idx = []; let base = 0, worst = 1;
  for (let k = 0; k < 4; k++) {
    const alpha = k * Math.PI / 2;
    for (let i = 0; i <= NA; i++) {
      const a = i / NA, th = alpha + (a - 0.5) * 1.35, sa = Math.sin(Math.PI * a);
      const rho0 = 0.25 + 0.10 * sa;
      const yTop = PROFILE.innerY(rho0) - 0.012;
      const depth = 0.03 + 0.10 * Math.pow(sa, 0.6);
      for (let j = 0; j <= NV; j++) {
        const v = j / NV;
        const ruff = (0.034 * Math.sin(a * Math.PI * 13 + v * 2.2) + 0.012 * Math.sin(a * Math.PI * 29 + 1.3)) * Math.pow(v, 1.1);
        const rho = rho0 + ruff + 0.05 * v;            // folds splay outward along the subumbrella
        const y = yTop - v * depth;
        worst = Math.min(worst, PROFILE.innerR(y) - rho);
        pos.push(rho * Math.cos(th), y, rho * Math.sin(th));
        nrm.push(Math.cos(th), 0.2, Math.sin(th));
        aA.push(a); aV.push(v);
      }
    }
    for (let i = 0; i < NA; i++) for (let j = 0; j < NV; j++) {
      const a = base + i * (NV + 1) + j, b = a + 1, c = a + NV + 1, d = c + 1; idx.push(a, c, b, b, c, d);
    }
    base += (NA + 1) * (NV + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
  g.setAttribute('aA', new THREE.Float32BufferAttribute(aA, 1));
  g.setAttribute('aV', new THREE.Float32BufferAttribute(aV, 1));
  g.setIndex(idx);
  g.userData.clearance = worst;
  return g;
}

// ───────────────────────────── jellies ─────────────────────────────
// home = rim-centre position; R = bell radius; tilt = initial axis lean (x,z)
const JELLY_DEFS = [
  { home: [0.95, 1.05, -7.0], R: 1.0, tilt: [-0.30, 0.10], period: 3.9, glow: 1.0, hs: 1.02, hue: 0.05 },   // hero
  { home: [-2.45, 1.30, -9.8], R: 0.80, tilt: [0.10, 0.06], period: 3.4, glow: 0.95 },
  { home: [-2.05, -1.15, -12.6], R: 0.62, tilt: [-0.08, 0.10], period: 3.1, glow: 0.9 },
  { home: [1.45, -2.45, -17.2], R: 0.62, tilt: [0.10, -0.05], period: 3.3, glow: 0.85 },
  { home: [8.1, 2.95, -17.6], R: 0.74, tilt: [-0.12, 0.0], period: 3.6, glow: 0.9 },
  { home: [-8.5, 2.6, -18.4], R: 0.92, tilt: [0.15, 0.05], period: 4.2, glow: 0.8 },
  { home: [-4.9, -5.0, -19.0], R: 0.66, tilt: [0.05, 0.1], period: 3.2, glow: 0.8 },
  { home: [9.9, -1.5, -18.8], R: 0.78, tilt: [-0.1, 0.1], period: 3.7, glow: 0.85 },
  // the rest of the bloom, out of the hero frame — seen when orbiting
  { home: [20.0, 3.0, -24.0], R: 0.9, tilt: [0.0, 0.1], period: 3.8, glow: 0.8 },
  { home: [7.4, -1.0, -3.5], R: 0.85, tilt: [-0.1, -0.1], period: 3.5, glow: 0.9 },
  { home: [-7.8, 0.6, -2.0], R: 0.8, tilt: [0.12, 0.0], period: 3.3, glow: 0.9 },
  { home: [-2.5, 2.2, 6.5], R: 0.95, tilt: [0.0, -0.1], period: 4.0, glow: 0.9 },
];
const NJ = JELLY_DEFS.length;
const N_TENT = 32, N_ARM = 4, NODES = 32;
const UP = new THREE.Vector3(0, 1, 0);

class Jelly {
  constructor(def, i) {
    this.i = i; this.R = def.R; this.glow = def.glow; this.period = def.period * rr(0.95, 1.05);
    this.home = new THREE.Vector3(...def.home);
    this.pos = this.home.clone(); this.vel = new THREE.Vector3();
    this.tilt = new THREE.Vector3(def.tilt[0], 0, def.tilt[1]);
    this.axis = new THREE.Vector3(def.tilt[0], 1, def.tilt[1]).normalize();
    this.turn = rr(0.024, 0.034) * (rng() < 0.5 ? -1 : 1);   // lazy circling: lean direction precesses
    this.sink = SWIM.thrust / this.period;                        // neutral at full stroke strength
    this.spin = rr(0, Math.PI * 2); this.spinRate = rr(-0.03, 0.03);
    this.phase = rr(0, 1); this.c = 0; this.cm = 0; this.cPrev = 0; this.seed = rr(0, 100);
    // individuality: bell height, hue, appendage proportions
    this.hs = def.hs ?? rr(0.86, 1.22); this.hue = def.hue ?? rr(-1, 1); this.tentLen = rr(0.75, 1.25); this.armLen = rr(0.8, 1.2);
    this.wander = [rr(0, 100), rr(0, 100)];
    this.quat = new THREE.Quaternion(); this.updateQuat();
  }
  updateQuat() {
    const qa = new THREE.Quaternion().setFromUnitVectors(UP, this.axis);
    const qs = new THREE.Quaternion().setFromAxisAngle(UP, this.spin);
    this.quat.copy(qa).multiply(qs);
  }
  static contraction(x) { // quick power stroke, slow elastic recovery with a slight rebound flare
    const k = 0.30;
    if (x < k) { const s = Math.sin(Math.PI / 2 * x / k); return s * s; }
    const r = (x - k) / (1 - k);
    return 0.5 + 0.5 * Math.cos(Math.PI * Math.pow(r, 0.75)) - 0.07 * Math.sin(Math.PI * Math.min(1, r * 1.6)) * (r > 0.2 ? 1 : r / 0.2);
  }
  step(dt, t) {
    this.phase += dt / this.period;
    this.cPrev = this.c; this.c = Jelly.contraction(this.phase % 1); this.cm = Jelly.contraction((this.phase + 0.93) % 1);
    const dc = (this.c - this.cPrev) / dt;
    // steering: lean toward home (horizontal) with slow wander, stroke strength regulates depth
    const to = this.home.clone().sub(this.pos);
    const lean = this.tilt.clone().applyAxisAngle(UP, this.turn * t).multiplyScalar(0.8 + 0.2 * Math.cos(t * 0.031 + this.wander[0]));
    lean.x += THREE.MathUtils.clamp(to.x * 0.16, -0.25, 0.25); lean.z += THREE.MathUtils.clamp(to.z * 0.16, -0.25, 0.25);
    // avoid neighbours (bell + trailing appendage capsule)
    for (const o of jellies) if (o !== this) {
      const d = this.pos.clone().sub(o.pos); d.y *= 0.35; const l = d.length(), need = (this.R + o.R) * 2.6;
      if (l < need) lean.addScaledVector(d.normalize(), (need - l) / need * 0.4);
    }
    const desired = new THREE.Vector3(0, 1, 0).add(lean);
    if (desired.angleTo(UP) > 0.42) { desired.normalize(); const ax = new THREE.Vector3().crossVectors(UP, desired).normalize(); desired.copy(UP).applyAxisAngle(ax, 0.42); }
    desired.normalize();
    this.axis.lerp(desired, 1 - Math.exp(-dt * 0.3)).normalize();
    this.spin += this.spinRate * dt; this.updateQuat();
    const strength = THREE.MathUtils.clamp(1 + to.y * 0.9, 0.3, 1.7);
    const acc = this.axis.clone().multiplyScalar(Math.max(dc, 0) * SWIM.thrust * this.R * strength);
    acc.y -= this.sink * this.R;
    this.vel.addScaledVector(acc, dt);
    // the camera drifts with the water mass, so bodies only see a weak residual current they can stem;
    // appendages still feel the full current and eddies (see simulate), which streams them gently
    const flow = flowAt(this.pos, t).multiplyScalar(0.3);
    this.vel.lerp(flow, 1 - Math.exp(-SWIM.drag * dt));
    this.pos.addScaledVector(this.vel, dt);
  }
  toWorld(lx, ly, lz, out) { out.set(lx * this.R, ly * this.R * this.hs, lz * this.R).applyQuaternion(this.quat).add(this.pos); return out; }
  bellCenter(out = new THREE.Vector3()) { return this.toWorld(0, 0.45, 0, out); }
}

// slow divergence-free ambient current (ABC flow)
function abc(p, t, k, A, B, C, w, out) {
  return out.set(
    A * Math.sin(k * p.z + w) + C * Math.cos(k * p.y + 0.7 * w),
    B * Math.sin(k * p.x + 0.6 * w + 1.3) + A * Math.cos(k * p.z + w),
    C * Math.sin(k * p.y + 0.7 * w) + B * Math.cos(k * p.x + 0.6 * w + 1.3));
}
const _fine = new THREE.Vector3();
function flowAt(p, t, out = new THREE.Vector3(), fine = false) {
  abc(p, t, 0.22, 0.035, 0.028, 0.03, t * 0.05, out);
  if (fine) out.add(abc(p, t, 1.15, 0.040, 0.034, 0.037, t * 0.35 + 2.0, _fine));   // eddies at appendage scale
  return out;
}

const jellies = JELLY_DEFS.map((d, i) => new Jelly(d, i));

// ───────────────────────────── appendage simulation (CPU verlet, uploaded as a float texture) ─────────────────────────────
const chains = [];
jellies.forEach(j => {
  for (let k = 0; k < N_TENT; k++) {
    const th = (k + 0.5) * Math.PI / N_LAPPET + 0.0;               // a notch between lappets
    const thN = Math.round(th * N_LAPPET / Math.PI) * Math.PI / N_LAPPET; // exact notch angle
    const phi = phiEdge(thN), [r, y] = outerP(phi);
    chains.push({ j, type: 0, ang: thN, root: [(r * (1 - LOBE_A) - 0.012) * Math.cos(thN), y - 0.005, (r * (1 - LOBE_A) - 0.012) * Math.sin(thN)],
      len: j.R * j.tentLen * rr(4.6, 7.2) * (rng() < 0.1 ? rr(0.25, 0.55) : 1), bend: 0.04, width: rng() < 0.12 ? 0 : rr(0.7, 1.3) });
  }
  for (let k = 0; k < N_ARM; k++) {
    const a = Math.PI / 4 + k * Math.PI / 2 + rr(-0.1, 0.1);
    chains.push({ j, type: 1, ang: a, root: [0.04 * Math.cos(a), PROFILE.innerTop - 0.10, 0.04 * Math.sin(a)],
      root2: [0.09 * Math.cos(a), PROFILE.innerTop - 0.36, 0.09 * Math.sin(a)], len: j.R * j.armLen * rr(2.9, 3.8), bend: 0.3, width: 1, seed: rr(0, 50) });
  }
});
const NCH = chains.length;
jellies.forEach(j => { j.firstChain = chains.findIndex(ch => ch.j === j); });
const P = new Float32Array(NCH * NODES * 3), PP = new Float32Array(NCH * NODES * 3);
const simData = new Float32Array(NCH * NODES * 4), frameData = new Float32Array(NCH * NODES * 4);
const simTex = new THREE.DataTexture(simData, NODES, NCH, THREE.RGBAFormat, THREE.FloatType);
const frameTex = new THREE.DataTexture(frameData, NODES, NCH, THREE.RGBAFormat, THREE.FloatType);
[simTex, frameTex].forEach(t => { t.magFilter = t.minFilter = THREE.NearestFilter; t.needsUpdate = true; });

const armHalfWidth = u => 0.36 * 0.8 * smoothstepJS(0.03, 0.2, u) * (1 - 0.55 * u * u);   // matches shader W(u)
function smoothstepJS(a, b, x) { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

const _v = new THREE.Vector3(), _w = new THREE.Vector3(), _q = new THREE.Quaternion(), _f = new THREE.Vector3();
function pinned(ch, idx, out) {
  const j = ch.j, src = idx === 0 ? ch.root : (ch.type === 1 ? ch.root2 : [ch.root[0] * 1.02, ch.root[1] - 0.06, ch.root[2] * 1.02]);
  const d = deformJS(src[0], src[1], src[2], j.c, j.cm, simTime, j.seed);
  return j.toWorld(d[0], d[1], d[2], out);
}
function initChains() {
  chains.forEach((ch, c) => {
    const j = ch.j, seg = ch.len / (NODES - 1); ch.seg = seg;
    const p0 = pinned(ch, 0, new THREE.Vector3()), p1 = pinned(ch, 1, new THREE.Vector3());
    const dir = p1.clone().sub(p0).normalize();
    const down = j.axis.clone().negate();
    for (let i = 0; i < NODES; i++) {
      const p = i === 0 ? p0 : i === 1 ? p1 : p1.clone().addScaledVector(dir.clone().lerp(down, 0.85).normalize(), seg * (i - 1));
      const o = (c * NODES + i) * 3; P[o] = PP[o] = p.x; P[o + 1] = PP[o + 1] = p.y; P[o + 2] = PP[o + 2] = p.z;
    }
  });
}
let simTime = -WARMUP;
const G = -0.55;
const _qi = new THREE.Quaternion();
function simulate(dt) {
  simTime += dt;
  for (const j of jellies) j.step(dt, simTime);
  const damp = Math.exp(-2.4 * dt);
  for (let c = 0; c < NCH; c++) {
    const ch = chains[c], j = ch.j, base = c * NODES;
    pinned(ch, 0, _v); let o = base * 3; PP[o] = P[o]; PP[o + 1] = P[o + 1]; PP[o + 2] = P[o + 2]; P[o] = _v.x; P[o + 1] = _v.y; P[o + 2] = _v.z;
    pinned(ch, 1, _v); o += 3; PP[o] = P[o]; PP[o + 1] = P[o + 1]; PP[o + 2] = P[o + 2]; P[o] = _v.x; P[o + 1] = _v.y; P[o + 2] = _v.z;
    for (let i = 2; i < NODES; i++) {
      o = (base + i) * 3;
      _v.set(P[o], P[o + 1], P[o + 2]);
      flowAt(_v, simTime, _f, true);
      // velocity relaxes toward the local water velocity (drag), plus weak negative buoyancy
      let vx = (P[o] - PP[o]) / dt, vy = (P[o + 1] - PP[o + 1]) / dt, vz = (P[o + 2] - PP[o + 2]) / dt;
      vx = _f.x + (vx - _f.x) * damp; vy = _f.y + (vy - _f.y) * damp + G * j.R * dt * (ch.type ? 0.6 : 0.25);   // near-neutral buoyancy vz = _f.z + (vz - _f.z) * damp;
      PP[o] = P[o]; PP[o + 1] = P[o + 1]; PP[o + 2] = P[o + 2];
      P[o] += vx * dt; P[o + 1] += vy * dt; P[o + 2] += vz * dt;
    }
  }
  for (let it = 0; it < 6; it++) {
    for (let c = 0; c < NCH; c++) {
      const ch = chains[c], base = c * NODES, seg = ch.seg;
      for (let i = 1; i < NODES - 1; i++) constrain(base + i, base + i + 1, seg, i <= 1 ? 1 : 0.5, 1);
      for (let i = 0; i < NODES - 2; i++) constrain(base + i, base + i + 2, seg * 2 * 0.985, i <= 1 ? 1 : 0.5, ch.bend, ch.type === 0);
    }
  }
  collide();
  collideNeighbours();
}
// w = share of correction applied to node b (1 = a is pinned)
function constrain(a, b, rest, w, k, onlyCompress) {
  const oa = a * 3, ob = b * 3;
  const dx = P[ob] - P[oa], dy = P[ob + 1] - P[oa + 1], dz = P[ob + 2] - P[oa + 2];
  const l = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
  if (onlyCompress && l > rest) return;   // bending: resist folding only
  const corr = (l - rest) / l * k;
  const wb = w, wa = 1 - w;
  P[oa] += dx * corr * wa; P[oa + 1] += dy * corr * wa; P[oa + 2] += dz * corr * wa;
  P[ob] -= dx * corr * wb; P[ob + 1] -= dy * corr * wb; P[ob + 2] -= dz * corr * wb;
}
// bell, arm↔arm and tentacle↔arm clearance, solved in each jelly's local frame
const _loc = new THREE.Vector3();
function collide() {
  for (const j of jellies) {
    _qi.copy(j.quat).invert();
    const first = j.firstChain;
    const armStart = first + N_TENT;
    for (let c = first; c < first + N_TENT + N_ARM; c++) {
      const ch = chains[c];
      for (let i = 2; i < NODES; i++) {
        const o = (c * NODES + i) * 3;
        _loc.set(P[o], P[o + 1], P[o + 2]).sub(j.pos).applyQuaternion(_qi).divideScalar(j.R); _loc.y /= j.hs;
        const y = _loc.y, r = Math.sqrt(_loc.x * _loc.x + _loc.z * _loc.z);
        let changed = false;
        if (ch.type === 0) {            // tentacles stay outside the bell
          if (y > -0.02 && y < HT + 0.05) { const R0 = PROFILE.outerR(Math.max(y, 0)) * (1 - 0.17 * j.c) + 0.03; if (r < R0) { const s = R0 / Math.max(r, 1e-4); _loc.x *= s; _loc.z *= s; changed = true; } }
        } else {                        // arms stay inside the cavity
          if (y > -0.02) { const R0 = Math.max(0.02, PROFILE.innerR(Math.min(y, PROFILE.innerTop)) * (1 - 0.17 * j.c) - armHalfWidth(i / (NODES - 1)) - 0.03); if (r > R0) { const s = R0 / r; _loc.x *= s; _loc.z *= s; changed = true; } }
          if (y > PROFILE.innerTop - 0.06) { _loc.y = PROFILE.innerTop - 0.06; changed = true; }
        }
        if (changed) { _loc.y *= j.hs; _loc.multiplyScalar(j.R).applyQuaternion(j.quat).add(j.pos); P[o] = _loc.x; P[o + 1] = _loc.y; P[o + 2] = _loc.z; }
      }
    }
    // arm spine clearance against tentacles and other arms (AABB-culled: most tentacle nodes never come near)
    const reach = 0.36 * j.R;
    let x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
    for (let a = armStart; a < armStart + N_ARM; a++) for (let ia = 3; ia < NODES; ia++) {
      const o = (a * NODES + ia) * 3;
      if (P[o] < x0) x0 = P[o]; if (P[o] > x1) x1 = P[o]; if (P[o + 1] < y0) y0 = P[o + 1]; if (P[o + 1] > y1) y1 = P[o + 1]; if (P[o + 2] < z0) z0 = P[o + 2]; if (P[o + 2] > z1) z1 = P[o + 2];
    }
    x0 -= reach; y0 -= reach; z0 -= reach; x1 += reach; y1 += reach; z1 += reach;
    for (let c = first; c < armStart + N_ARM; c++) {
      const isArm = c >= armStart;
      for (let i = isArm ? 3 : 2; i < NODES; i++) {
        const ob = (c * NODES + i) * 3;
        if (P[ob] < x0 || P[ob] > x1 || P[ob + 1] < y0 || P[ob + 1] > y1 || P[ob + 2] < z0 || P[ob + 2] > z1) continue;
        const hb = armHalfWidth(i / (NODES - 1)) * j.R;
        for (let a = armStart; a < armStart + N_ARM; a++) {
          if (a === c || (isArm && a > c)) continue;
          for (let ia = 3; ia < NODES; ia++) {
            const oa = (a * NODES + ia) * 3;
            const dx = P[ob] - P[oa], dy = P[ob + 1] - P[oa + 1], dz = P[ob + 2] - P[oa + 2];
            const d2 = dx * dx + dy * dy + dz * dz;
            if (d2 > reach * reach * 4) continue;
            const ha = armHalfWidth(ia / (NODES - 1)) * j.R;
            if (isArm && (i < 8 || ia < 8)) continue;                // arms share the manubrium near the root
            const need = isArm ? 0.5 * (ha + hb) : ha + 0.06 * j.R;
            if (d2 < need * need && d2 > 1e-10) {
              const d = Math.sqrt(d2), push = (need - d) / d;
              if (isArm) { const h = push * 0.5; P[ob] += dx * h; P[ob + 1] += dy * h; P[ob + 2] += dz * h; P[oa] -= dx * h; P[oa + 1] -= dy * h; P[oa + 2] -= dz * h; }
              else { P[ob] += dx * push; P[ob + 1] += dy * push; P[ob + 2] += dz * push; }
            }
          }
        }
      }
    }
  }
}
// appendages of one animal drape around, never through, a neighbour's bell
const _bc = new THREE.Vector3();
function collideNeighbours() {
  for (const j of jellies) {
    const c0 = j.firstChain, c1 = c0 + N_TENT + N_ARM;
    let x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
    for (let o = c0 * NODES * 3; o < c1 * NODES * 3; o += 3) {
      if (P[o] < x0) x0 = P[o]; if (P[o] > x1) x1 = P[o]; if (P[o + 1] < y0) y0 = P[o + 1]; if (P[o + 1] > y1) y1 = P[o + 1]; if (P[o + 2] < z0) z0 = P[o + 2]; if (P[o + 2] > z1) z1 = P[o + 2];
    }
    for (const k of jellies) {
      if (k === j) continue;
      k.bellCenter(_bc); const rad = 1.15 * k.R * Math.max(1, k.hs);
      if (_bc.x + rad < x0 || _bc.x - rad > x1 || _bc.y + rad < y0 || _bc.y - rad > y1 || _bc.z + rad < z0 || _bc.z - rad > z1) continue;
      _qi.copy(k.quat).invert();
      for (let c = c0; c < c1; c++) for (let i = 2; i < NODES; i++) {
        const o = (c * NODES + i) * 3;
        const dx = P[o] - _bc.x, dy = P[o + 1] - _bc.y, dz = P[o + 2] - _bc.z;
        if (dx * dx + dy * dy + dz * dz > rad * rad) continue;
        _loc.set(P[o], P[o + 1], P[o + 2]).sub(k.pos).applyQuaternion(_qi).divideScalar(k.R); _loc.y /= k.hs;
        if (_loc.y < -0.02 || _loc.y > HT + 0.04) continue;
        const r = Math.sqrt(_loc.x * _loc.x + _loc.z * _loc.z), R0 = PROFILE.outerR(Math.max(_loc.y, 0)) + 0.04;
        if (r >= R0) continue;
        if (r < 1e-4) { _loc.x = R0; } else { _loc.x *= R0 / r; _loc.z *= R0 / r; }
        _loc.y *= k.hs; _loc.multiplyScalar(k.R).applyQuaternion(k.quat).add(k.pos);
        P[o] = _loc.x; P[o + 1] = _loc.y; P[o + 2] = _loc.z;
      }
    }
  }
}
function upload() {
  for (let c = 0; c < NCH; c++) {
    const ch = chains[c], base = c * NODES;
    for (let i = 0; i < NODES; i++) { const o = (base + i) * 3, q = (base + i) * 4; simData[q] = P[o]; simData[q + 1] = P[o + 1]; simData[q + 2] = P[o + 2]; simData[q + 3] = 1; }
    if (ch.type === 1) {  // parallel-transported frame for the frilled arms
      let n = new THREE.Vector3(Math.cos(ch.ang), 0, Math.sin(ch.ang)).applyQuaternion(ch.j.quat);
      for (let i = 0; i < NODES; i++) {
        const a = Math.max(0, i - 1), b = Math.min(NODES - 1, i + 1), oa = (base + a) * 3, ob = (base + b) * 3;
        _v.set(P[ob] - P[oa], P[ob + 1] - P[oa + 1], P[ob + 2] - P[oa + 2]).normalize();
        n.addScaledVector(_v, -n.dot(_v)).normalize();
        const q = (base + i) * 4; frameData[q] = n.x; frameData[q + 1] = n.y; frameData[q + 2] = n.z; frameData[q + 3] = 0;
      }
    }
  }
  simTex.needsUpdate = true; frameTex.needsUpdate = true;
}

// ───────────────────────────── chain sampling in TSL (Catmull-Rom over the sim texture) ─────────────────────────────
function chainSample(tex, row, t) {
  const x = t.clamp(0, 1).mul(NODES - 1);
  const i1 = floor(x).min(NODES - 2).toVar();
  const f = x.sub(i1).toVar();
  const ld = k => textureLoad(tex, ivec2(int(k), int(row))).xyz;
  const p0 = ld(i1.sub(1).max(0)), p1 = ld(i1), p2 = ld(i1.add(1)), p3 = ld(i1.add(2).min(NODES - 1));
  const a = p1.mul(2), b = p2.sub(p0), c2 = p0.mul(2).sub(p1.mul(5)).add(p2.mul(4)).sub(p3), d3 = p0.negate().add(p1.mul(3)).sub(p2.mul(3)).add(p3);
  const p = a.add(b.mul(f)).add(c2.mul(f.mul(f))).add(d3.mul(f.mul(f).mul(f))).mul(0.5);
  const d = b.add(c2.mul(f).mul(2)).add(d3.mul(f.mul(f)).mul(3)).mul(0.5);
  return { p, d, f, i1 };
}

// ───────────────────────────── light sources & transport ─────────────────────────────
// Nothing here is "painted". Every photon has a source — the jellies' photocytes (bioluminescence), the
// diver's two video lights, the residual blue downwelling from far above — and reaches the lens either
// directly or after scattering off tissue, particles or the water itself, losing red first on the way.
const LIGHT = {
  emission: [0.56, 0.42, 1.0],        // bioluminescent spectrum as recorded (blue-violet)
  coreI: 2.8,                        // gonad / manubrium photocyte cluster, radiant intensity per R²
  lampI: 5.5, lampCol: [1.0, 0.85, 0.70],                    // two 5600K video lights, dimmed for bioluminescence work
  lampOffset: [2.4, 0.9, 0.35], lampCone: [0.40, 0.72],      // on arms ±x, above, ahead; inner/outer half-angles (rad)
  ambient: [0.0010, 0.0040, 0.0072],  // downwelling irradiance at twilight depth (zenith-weighted, blue)
  gTissue: 0.55, gWater: 0.88, gParticle: 0.70,              // Henyey–Greenstein asymmetry (all forward-peaked)
  bWater: 0.030,                      // water scattering coefficient per unit (≈0.13 m⁻¹), sets halo strength
};
const TISSUE = {
  pigment: [0.95, 0.48, 1.0],         // mauve pigment: what survives its absorption (passes red + blue, eats green)
  absorb: [0.35, 1.10, 0.25],         // pigment absorption coefficient shape (per unit path, per unit density)
  ior: 1.15,                          // relative index of the mesoglea: a clear, glassy body
  sBell: 1.0, sCore: 7.0, sArm: 8.0, sTent: 42.0,            // scattering coefficients (per unit path): clear bulk, dense structures
  roughBell: 0.035, roughArm: 0.12,   // surface roughness (rad) of the wet exumbrella and the frills
  aBell: 0.12, aCore: 0.9, aArm: 0.5, aTent: 0.4,            // pigment density per tissue
  emitBell: 0.55, emitCore: 0.6, emitArm: 0.06, emitTent: 0.07,
};
// forward-peaked scattering removes little light from the direct beam: effective extinction ≈ (1 − g)·σs
const EXT = 1 - LIGHT.gTissue;
const jellyLights = uniformArray(Array.from({ length: 16 }, () => new THREE.Vector4()), 'vec4');           // xyz, intensity
const jellyTints = uniformArray(Array.from({ length: 16 }, () => new THREE.Vector4(1, 1, 1, 1)), 'vec4');   // emission rgb, R
const uLampA = uniform(new THREE.Vector3()), uLampB = uniform(new THREE.Vector3()), uLampDir = uniform(new THREE.Vector3(0, 0, -1));
const uLampI = uniform(LIGHT.lampI), uLampCol = uniform(new THREE.Vector3(...LIGHT.lampCol));
const uAmbient = uniform(new THREE.Vector3(...LIGHT.ambient));
const PIG = vec3(...TISSUE.pigment), ABS = vec3(...TISSUE.absorb);
const INV4PI = 1 / (4 * Math.PI);
const hg = (c, g) => float((1 - g * g) * INV4PI).div(float(1 + g * g).sub(c.mul(2 * g)).max(1e-4).pow(1.5));
// thin tissue single-scatters forward; dense tissue (arms, gonads, nematocyst bands) multiply scatters toward isotropic
const tissuePhase = c => hg(c, LIGHT.gTissue).mul(0.6).add(0.4 * INV4PI);
const particlePhase = c => hg(c, LIGHT.gParticle).mul(0.75).add(0.25 * INV4PI);
const lampSpot = dir => smoothstep(Math.cos(LIGHT.lampCone[1]), Math.cos(LIGHT.lampCone[0]), dot(dir, uLampDir));

// Radiance scattered toward the camera at x (V = unit x→camera), per unit scattering coefficient
function inscatter(x, V, phase) {
  const sum = vec3(0).toVar();
  Loop(NJ, ({ i }) => {
    const L = jellyLights.element(i), E = jellyTints.element(i);
    const r0 = E.w.mul(0.35);                                   // the photocyte cluster is extended, not a point
    const dv = x.sub(L.xyz), d2 = dot(dv, dv).add(r0.mul(r0)), d = sqrt(d2);
    sum.addAssign(E.xyz.mul(L.w.mul(phase(dot(dv, V).div(d))).div(d2)).mul(absorb(d)));
  });
  for (const lp of [uLampA, uLampB]) {
    const dv = x.sub(lp), d2 = dot(dv, dv).add(0.02), d = sqrt(d2), dir = dv.div(d);
    sum.addAssign(uLampCol.mul(uLampI.mul(lampSpot(dir)).mul(phase(dot(dir, V))).div(d2)).mul(absorb(d)));
  }
  sum.addAssign(uAmbient.mul(phase(V.y.negate())).mul(4 * Math.PI));     // downwelling travels along −y
  return sum;
}
// Light reflected by a smooth interface toward the camera along mirror direction Rd: the water's own
// radiance in that direction plus every source seen as a small sphere (photocyte cluster or lamp lens).
const waterSky = dir => vec3(0.0034, 0.0150, 0.0250).mul(exp(float(1).sub(dir.y).mul(-3.4)));
function mirrorEnv(x, Rd, N, rough = 0) {
  const r2 = rough * rough;
  const sum = waterSky(Rd).toVar();
  Loop(NJ, ({ i }) => {
    const L = jellyLights.element(i), E = jellyTints.element(i);
    const dv = L.xyz.sub(x), d = length(dv).max(1e-3), l = dv.div(d);
    const r0 = E.w.mul(0.35), ang = r0.div(d);
    const facing = smoothstep(-0.05, 0.1, dot(l, N));            // a source behind the interface is not reflected
    const a2 = ang.mul(ang).max(1e-5), w2 = a2.add(r2);                    // source disc widened by the surface roughness
    const glint = exp(float(1).sub(dot(Rd, l)).mul(-2).div(w2)).mul(a2.div(w2));
    sum.addAssign(E.xyz.mul(L.w.div(r0.mul(r0).mul(Math.PI))).mul(glint).mul(facing).mul(absorb(d)));
  });
  for (const lp of [uLampA, uLampB]) {
    const dv = lp.sub(x), d = length(dv).max(1e-3), l = dv.div(d), ang = float(0.06).div(d);
    const a2 = ang.mul(ang), w2 = a2.add(r2);
    const glint = exp(float(1).sub(dot(Rd, l)).mul(-2).div(w2)).mul(a2.div(w2));
    sum.addAssign(uLampCol.mul(uLampI.div(0.06 * 0.06 * Math.PI)).mul(glint).mul(lampSpot(l.negate())).mul(absorb(d)));
  }
  return sum;
}
const schlick = (cosT, n) => { const r0 = ((n - 1) / (n + 1)) ** 2; return float(1).sub(cosT).clamp(0, 1).pow(5).mul(1 - r0).add(r0); };

// ───────────────────────────── jelly materials ─────────────────────────────
// Each animal is rendered into its own layer (see the image pipeline) with three outputs:
//   output — radiance leaving the tissue toward the lens (premultiplied), alpha = 1 − mean transmittance
//   aux    — screen-space refraction offset (xy), forward-scatter "frost" (z), optical depth (w)
// and then composited over everything behind it: behind(uv + offset, frosted) · e^(−τ·absorption) + radiance.
function tissueMaterial(side = THREE.DoubleSide) {
  return new THREE.MeshBasicNodeMaterial({
    transparent: true, depthWrite: false, depthTest: false, side,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor,
  });
}
const uRefrK = uniform(new THREE.Vector2(1, 1));   // (ior − 1) · focal length in uv units — set on resize
// writes refraction/frost/optical depth for this fragment, returns opacity
function tissueOutputs(mat, { tau, frost, nWorld, pathW, dist, refr = 1, behind = 0 }) {
  const nV = normalize(cameraViewMatrix.mul(vec4(nWorld, 0)).xyz);
  const off = vec2(nV.x, nV.y.negate()).mul(uRefrK).mul(pathW.add(behind)).div(dist).mul(refr);
  mat.mrtNode = mrt({ aux: vec4(off, frost, tau) });
  mat.opacityNode = float(1).sub(exp(tau.negate()));
}

const jellyUniforms = () => ({
  uC: uniform(0).onObjectUpdate(({ object }) => object.userData.jelly.c),
  uCm: uniform(0).onObjectUpdate(({ object }) => object.userData.jelly.cm),
  uSeed: uniform(0).onObjectUpdate(({ object }) => object.userData.jelly.seed),
  uHs: uniform(1).onObjectUpdate(({ object }) => object.userData.jelly.hs),
  uHue: uniform(0).onObjectUpdate(({ object }) => object.userData.jelly.hue),
  uR: uniform(1).onObjectUpdate(({ object }) => object.userData.jelly.R),
  uIdx: uniform(0).onObjectUpdate(({ object }) => object.userData.jelly.i),
  uEmit: uniform(1).onObjectUpdate(({ object }) => object.userData.jelly.glow * (1 + 0.25 * object.userData.jelly.c)),
});

// Bell: a thin gelatinous shell, nearly index-matched to sea water. It is seen through
//  · light its tissue scatters — lit mostly from inside by the gonads, forward-peaked, filtered by pigment;
//  · its photocytes: exumbrella warts, marginal bulbs, rhopalia, ring and radial canals;
//  · what it does to the scene behind it: refraction by the lens-shaped mesoglea, Beer–Lambert pigment
//    absorption, forward-scatter frosting, and a faint Fresnel mirror at grazing angles.
// Drawn twice: back faces first, then front faces (with the mirror term), each in a fixed layer order.
function makeBellMaterial(side) {
  const m = tissueMaterial(side);
  const U = jellyUniforms();
  const vN = varyingProperty('vec3', 'vBellN');
  m.positionNode = Fn(() => {
    // exumbrella lobes: r ← r·(1 − A·(1 − L(θ))·s²), L = 1 mid-lobe, 0 in the notch; normals tilt by (1/r)·dr/dθ
    const sA = attribute('aS', 'float'), thA = attribute('aTheta', 'float');
    const L = float(0.5).sub(cos(thA.mul(2 * N_LAPPET)).mul(0.5));
    const k = float(1).sub(float(1).sub(L).mul(LOBE_A).mul(sA.mul(sA)));
    const p = vec3(positionGeometry.x.mul(k), positionGeometry.y, positionGeometry.z.mul(k));
    const slope = sin(thA.mul(2 * N_LAPPET)).mul(LOBE_A * N_LAPPET).mul(sA.mul(sA));
    const sgn = float(1).sub(smoothstep(0.6, 0.9, attribute('aLayer', 'float')).mul(2));
    const nG = normalize(normalGeometry.sub(vec3(sin(thA).negate(), 0, cos(thA)).mul(slope).mul(sgn)));
    const d = deformTSL(p, U.uC, U.uCm, U.uSeed);
    // non-uniform (height) scale: pre-divide by s² so the model matrix yields the inverse-transpose normal
    vN.assign(normalize(modelWorldMatrix.mul(vec4(deformNormal(p, nG, d).mul(vec3(1, float(1).div(U.uHs.mul(U.uHs)), 1)), 0)).xyz));
    return d.p;
  })();
  const s = attribute('aS', 'float'), th = attribute('aTheta', 'float'), layer = attribute('aLayer', 'float');
  const x = positionWorld, V = viewDirW(), dist = length(cameraPosition.sub(x));
  const N = normalize(vN), ndv = abs(dot(N, V)).max(0.06);
  // mesoglea thickness (bell radii); each face carries half of the shell's optical path
  const thickU = float(0.20).mul(float(1).sub(s).max(0).pow(1.4)).add(0.012);
  const pathW = thickU.mul(0.5).mul(U.uR).div(ndv).min(U.uR.mul(0.8));   // grazing paths are long: glassy bright rims
  // anatomy
  const inner = smoothstep(0.6, 0.9, layer);
  const lip = float(1).sub(abs(layer.sub(0.5)).mul(4).clamp(0, 1));
  const arc = sin(s.mul(PHI_MAX)).max(0.02);
  const cu = th.mul(16 / Math.PI);
  const dPrim = abs(fract(cu.mul(0.5).add(0.25)).sub(0.5)).mul(2 * Math.PI / 16).mul(arc);
  const dSec = abs(fract(cu.mul(0.5).add(0.75)).sub(0.5)).mul(2 * Math.PI / 16).mul(arc);
  const reach = smoothstep(0.08, 0.35, s);
  const canals = exp(sq(dPrim.div(0.010)).negate()).add(exp(sq(dSec.div(0.007)).negate()).mul(0.45)).mul(reach);
  const canalGlow = exp(dPrim.div(0.045).negate()).mul(reach);   // photocyte light diffusing into the mesoglea
  const ring = exp(sq(s.sub(0.94).div(0.013)).negate());
  const notch = float(1).sub(abs(sin(th.mul(N_LAPPET))).pow(0.5));
  const bulbs = smoothstep(0.55, 1.0, notch).mul(smoothstep(0.95, 1.0, s));
  const notchIdx = floor(th.mul(N_LAPPET / Math.PI).add(0.5));
  const rhop = float(1).sub(mod(notchIdx, 4).min(1)).mul(smoothstep(0.8, 1.0, notch)).mul(smoothstep(0.97, 1.0, s));
  const muscle = sin(s.mul(150.0)).mul(0.5).add(0.5).pow(3).mul(smoothstep(0.35, 0.6, s)).mul(smoothstep(0.97, 0.85, s));
  const rest = positionGeometry;
  const wTop = smoothstep(0.32, 0.12, s);
  const uvSide = vec2(th.mul(8 / (2 * Math.PI)), s.mul(2.4)), uvTop = rest.xz.mul(1.3);
  const tc = mix(cells(uvSide), cells(uvTop), wTop);
  const tf = mix(cells(uvSide.mul(3).add(0.37)), cells(uvTop.mul(3).add(0.37)), wTop);
  const warts = smoothstep(0.22, 0.0, tf.r).mul(tc.b.mul(1.4)).mul(smoothstep(0.1, 0.5, s)).mul(float(1).sub(inner));
  // scattering density: canals, muscle bands and cell walls are denser than the clear mesoglea
  const density = float(0.75).add(tc.b.mul(0.5)).add(smoothstep(0.0, 0.2, tc.g).oneMinus().mul(0.25))
    .add(canals.mul(0.9)).add(muscle.mul(inner).mul(0.6)).add(lip.mul(2.0)).add(ring.mul(0.8));
  const pigTint = hueTint(U.uHue);
  const E = jellyTints.element(int(U.uIdx)).xyz;
  m.colorNode = Fn(() => {
    const scattered = inscatter(x, V, tissuePhase).mul(PIG.mul(pigTint)).mul(density).mul(pathW).mul(TISSUE.sBell);
    const photocytes = warts.mul(0.9).add(bulbs.mul(0.7)).add(rhop.mul(2.2)).add(ring.mul(0.22)).add(lip.mul(0.25))
      .add(canals.mul(0.14)).add(canalGlow.mul(0.035));
    const emitted = E.mul(mix(vec3(1), PIG.mul(pigTint), 0.4)).mul(photocytes).mul(U.uEmit).mul(TISSUE.emitBell);
    let rad = scattered.add(emitted);
    // Fresnel gloss on every wall facing the lens: the outer surface mirrors the lamps and the water above;
    // the subumbrella, seen through the clear bell, mirrors the glowing gonads it encloses
    const Nf = N.mul(sign(dot(N, V)));
    const F = schlick(ndv, TISSUE.ior);
    rad = rad.add(mirrorEnv(x, reflect(V.negate(), Nf), Nf, TISSUE.roughBell).mul(F));
    return rad.mul(absorb(dist));
  })();
  const sigS = float(TISSUE.sBell).mul(density).mul(pathW);
  const tau = sigS.mul(EXT).add(float(TISSUE.aBell).mul(pathW).mul(density));
  // the near wall refracts the animal's own insides (≈0.35 R behind it) as well as the water beyond
  tissueOutputs(m, { tau, frost: sigS.mul(LIGHT.gTissue), nWorld: N, pathW, dist, behind: U.uR.mul(side === THREE.FrontSide ? 0.35 : 0.1) });
  return m;
}
const bellMatBack = makeBellMaterial(THREE.BackSide), bellMatFront = makeBellMaterial(THREE.FrontSide);

// Gonads: dense, pigmented, photocyte-rich folds — the animal's main light source (jellyLights) seen up close
const coreMat = tissueMaterial();
{
  const U = jellyUniforms();
  const vN = varyingProperty('vec3', 'vCoreN');
  coreMat.positionNode = Fn(() => {
    const p = positionGeometry, d = deformTSL(p, U.uC, U.uCm, U.uSeed);
    vN.assign(normalize(modelWorldMatrix.mul(vec4(deformNormal(p, normalGeometry, d).mul(vec3(1, float(1).div(U.uHs.mul(U.uHs)), 1)), 0)).xyz));
    return d.p;
  })();
  const a = attribute('aA', 'float'), v = attribute('aV', 'float');
  const x = positionWorld, V = viewDirW(), dist = length(cameraPosition.sub(x));
  const N = normalize(vN), ndv = abs(dot(N, V)).max(0.12);
  const pathW = U.uR.mul(0.025).div(ndv).min(U.uR.mul(0.1));
  const taper = smoothstep(1.0, 0.55, a.sub(0.5).abs().mul(2)).mul(smoothstep(0.0, 0.35, v).mul(0.6).add(0.4));
  coreMat.colorNode = Fn(() => {
    const E = jellyTints.element(int(U.uIdx)).xyz;
    const folds = sin(a.mul(Math.PI * 13).add(v.mul(2.2))).mul(0.5).add(0.5);
    const cellsC = smoothstep(0.3, 0.0, cells(vec2(a.mul(6.0), v.mul(1.2))).r);
    const pig = PIG.mul(hueTint(U.uHue));
    const scattered = inscatter(x, V, tissuePhase).mul(pig).mul(pathW).mul(TISSUE.sCore);
    const emitted = E.mul(mix(vec3(1), pig, 0.5)).mul(float(0.35).add(folds.mul(0.4)).add(cellsC.mul(0.5))).mul(U.uEmit).mul(TISSUE.emitCore);
    return scattered.add(emitted).mul(taper).mul(absorb(dist));
  })();
  const sigS = float(TISSUE.sCore).mul(pathW).mul(taper);
  tissueOutputs(coreMat, { tau: sigS.mul(EXT).add(float(TISSUE.aCore).mul(pathW).mul(taper)), frost: sigS.mul(0.3), nWorld: N, pathW, dist, refr: 0.5 });
}

// Pixel footprint, to keep thin structures at ≥1 px with energy-conserving coverage (no aliasing shimmer)
const uPxAngle = uniform(0.001);

// Marginal tentacles: thin cylinders of nematocyst-laden tissue, lit by their own bell (fading with distance
// from it, inverse-square), by neighbours and by the diver's lights. Lighting is smooth along a strand: per vertex.
const tentMat = tissueMaterial();
{
  const vCover = varyingProperty('float', 'vCover'), vWW = varyingProperty('float', 'vTentW'), vLit = varyingProperty('vec3', 'vTentLit');
  tentMat.positionNode = Fn(() => {
    const a = attribute('aA', 'vec4'), b = attribute('aB', 'vec4');
    const row = a.x, t = a.y, side = a.z, Rj = a.w, wv = b.x;
    const { p, d } = chainSample(simTex, row, t);
    const toCam = cameraPosition.sub(p);
    const S = normalize(cross(normalize(d), toCam));
    const wWorld = Rj.mul(mix(0.013, 0.0035, t.pow(0.7))).mul(wv);
    const w = max(wWorld, length(toCam).mul(uPxAngle).mul(1.15));
    vCover.assign(wWorld.div(w)); vWW.assign(wWorld);
    vLit.assign(inscatter(p, normalize(toCam), tissuePhase));
    return p.add(S.mul(side.mul(w).mul(0.5)));
  })();
  const a = attribute('aA', 'vec4'), b = attribute('aB', 'vec4');
  const t = a.y, side = a.z, len = b.y, jp = jellyParams.element(int(b.z));
  const tube = sqrt(float(1).sub(side.mul(side)).max(0));              // chord length through the cylinder
  const bands = sin(t.mul(len).mul(55.0)).mul(0.5).add(0.5).pow(3);     // nematocyst batteries: denser, scatter more
  const tip = float(1).sub(smoothstep(0.85, 1.0, t));
  const path = vWW.mul(tube);
  const dens = bands.mul(0.8).add(0.6);
  tentMat.colorNode = Fn(() => {
    const E = jellyTints.element(int(b.z)).xyz;
    const dist = length(cameraPosition.sub(positionWorld));
    const scattered = vLit.mul(PIG.mul(hueTint(jp.y))).mul(path).mul(dens).mul(TISSUE.sTent);
    const emitted = E.mul(bands).mul(tube).mul(jp.x).mul(TISSUE.emitTent).mul(float(1).sub(t.mul(0.7)));
    return scattered.add(emitted).mul(vCover).mul(tip).mul(absorb(dist));
  })();
  const tau = float(TISSUE.sTent * EXT).add(TISSUE.aTent).mul(path).mul(dens).mul(vCover).mul(tip);
  tentMat.mrtNode = mrt({ aux: vec4(0, 0, tau.mul(0.3), tau) });
  tentMat.opacityNode = float(1).sub(exp(tau.negate()));
}

// Oral arms: three twisting frilled curtains around each simulated spine
const ARM = { MU: 360, KV: 10, FINS: 3, twist: 0.8, lambda: 0.11, amp: 0.075, edgeGrowth: 1.8 };
const armMat = tissueMaterial();
{
  const vN = varyingProperty('vec3', 'vArmN'), vLit = varyingProperty('vec3', 'vArmLit');
  armMat.positionNode = Fn(() => {
    const a = attribute('aA', 'vec4'), b = attribute('aB', 'vec4');
    const row = a.x, u = a.y, v = a.z, fin = a.w, Rj = b.x, seed = b.y, Lr = b.z;
    const { p, d, f, i1 } = chainSample(simTex, row, u);
    const T = normalize(d);
    const n0 = textureLoad(frameTex, ivec2(int(i1), int(row))).xyz, n1 = textureLoad(frameTex, ivec2(int(i1.add(1)), int(row))).xyz;
    const nRaw = mix(n0, n1, f);
    const N = normalize(nRaw.sub(T.mul(dot(nRaw, T))));
    const B = cross(T, N);
    const sArc = u.mul(Lr);                                   // arc length in bell radii
    const tw = sArc.mul(ARM.twist / 3.3).add(sin(sArc.mul(0.9).add(seed)).mul(0.6)).add(fin.mul(2 * Math.PI / 3)).add(seed);
    const finDir = N.mul(cos(tw)).add(B.mul(sin(tw)));
    const finNrm = N.mul(sin(tw).negate()).add(B.mul(cos(tw)));
    const lobes = sq(sin(sArc.mul(3.1).add(seed.mul(1.7)))).mul(0.30).add(sq(sin(sArc.mul(7.3).add(seed))).mul(0.15)).add(0.55);
    const W = float(0.36).mul(smoothstep(0.03, 0.2, u)).mul(float(1).sub(u.mul(u).mul(0.55))).mul(lobes);
    // lettuce-edge frill: the margin grows longer than the core, so wavelength shortens toward the edge
    const k0 = float(2 * Math.PI / ARM.lambda);
    const kE = k0.mul(v.mul(ARM.edgeGrowth).add(1));
    const warp = sin(sArc.mul(2.1).add(seed)).mul(3.0).add(sin(sArc.mul(5.7).add(seed.mul(2.3))).mul(1.2));
    const ph = sArc.mul(kE).add(warp).add(fin.mul(1.9));
    const ph2 = ph.mul(2.3).add(1.7);
    const ampMod = sin(sArc.mul(1.7).add(seed)).mul(0.4).add(0.6);
    const gate = smoothstep(0.02, 0.15, u);
    const A = float(ARM.amp).mul(v.pow(2.2)).mul(ampMod).mul(gate);
    const ruf = A.mul(sin(ph)).add(A.mul(0.25).mul(sin(ph2)));
    const dRds = A.mul(cos(ph)).mul(kE).add(A.mul(0.25 * 2.3).mul(cos(ph2)).mul(kE));
    const dAdv = float(ARM.amp * 2.2).mul(v.max(0.001).pow(1.2)).mul(ampMod).mul(gate);
    const dphdv = sArc.mul(k0).mul(ARM.edgeGrowth);
    const dRdv = dAdv.mul(sin(ph)).add(A.mul(cos(ph)).mul(dphdv)).add(A.mul(0.25 * 2.3).mul(cos(ph2)).mul(dphdv));
    const dPds = T.add(finNrm.mul(dRds));                     // per bell radius of arc length
    const dPdv = finDir.mul(W.max(0.002)).add(finNrm.mul(dRdv));
    vN.assign(normalize(cross(dPds, dPdv)));
    const pos = p.add(finDir.mul(v.mul(W).mul(Rj))).add(finNrm.mul(ruf.mul(Rj)));
    vLit.assign(inscatter(pos, normalize(cameraPosition.sub(pos)), tissuePhase));
    return pos;
  })();
  const a = attribute('aA', 'vec4'), b = attribute('aB', 'vec4');
  const u = a.y, v = a.z, fin = a.w, Rj = b.x, Lr = b.z, jp = jellyParams.element(int(b.w));
  const dist = length(cameraPosition.sub(positionWorld));
  const N = normalize(vN), ndv = abs(dot(N, viewDirW())).max(0.06);
  const pathW = Rj.mul(mix(0.030, 0.010, v)).div(ndv).min(Rj.mul(0.5));      // the curtain thins toward its frilled margin
  const lace = smoothstep(0.22, 0.0, cells(vec2(u.mul(Lr).mul(1.1), v.mul(0.35).add(fin.mul(0.31)))).g);
  const fade = float(1).sub(smoothstep(0.80, 1.0, u)).mul(smoothstep(0.0, 0.05, u));
  const dens = lace.mul(0.9).add(0.7).mul(fade);
  armMat.colorNode = Fn(() => {
    const E = jellyTints.element(int(b.w)).xyz;
    const scattered = vLit.mul(PIG.mul(hueTint(jp.y))).mul(pathW).mul(dens).mul(TISSUE.sArm);
    const emitted = E.mul(lace.mul(smoothstep(0.5, 1.0, v))).mul(jp.x).mul(TISSUE.emitArm).mul(fade);   // luminous mucus on the margins
    // wet, glassy frills: Fresnel gloss of the lights on whichever side faces the lens
    const Nf = N.mul(sign(dot(N, viewDirW())));
    const gloss = mirrorEnv(positionWorld, reflect(viewDirW().negate(), Nf), Nf, TISSUE.roughArm).mul(schlick(ndv, TISSUE.ior)).mul(fade);
    return scattered.add(emitted).add(gloss).mul(absorb(dist));
  })();
  const sigS = float(TISSUE.sArm).mul(pathW).mul(dens);
  tissueOutputs(armMat, { tau: sigS.mul(EXT).add(float(TISSUE.aArm).mul(pathW).mul(dens)), frost: sigS.mul(0.25), nWorld: N, pathW, dist, refr: 0.6, behind: Rj.mul(0.05) });
}

// ───────────────────────────── meshes ─────────────────────────────
// One scene per animal, so each can be rendered into its own layer and composited in depth order.
const bellGeoBack = buildBellGeometry();
const bellGeoFront = bellGeoBack.clone();
{ // front pass draws the far (inner) wall before the near (outer) one: reverse triangle order
  const idx = bellGeoFront.index.array, tri = idx.length / 3, out = new Uint32Array(idx.length);
  for (let t = 0; t < tri; t++) out.set(idx.subarray((tri - 1 - t) * 3, (tri - t) * 3), t * 3);
  bellGeoFront.setIndex(new THREE.BufferAttribute(out, 1));
}
const coreGeo = buildCoreGeometry();
if (coreGeo.userData.clearance < 0) console.warn('gonad clearance negative', coreGeo.userData.clearance);

function buildTentacleGeometry(j, MT = 120) {
  const tChains = chains.map((c, i) => [c, i]).filter(([c]) => c.type === 0 && c.j === j);
  const nV = tChains.length * (MT + 1) * 2;
  // packed: aA = (row, t, side, R), aB = (width, length/R, jelly, 0)   (WebGPU allows 8 vertex buffers)
  const aA = new Float32Array(nV * 4), aB = new Float32Array(nV * 4);
  const idx = []; let v = 0;
  for (const [ch, row] of tChains) {
    const b = v;
    for (let i = 0; i <= MT; i++) for (const s of [-1, 1]) { aA.set([row, i / MT, s, ch.j.R], v * 4); aB.set([ch.width, ch.len / ch.j.R, ch.j.i, 0], v * 4); v++; }
    for (let i = 0; i < MT; i++) { const a = b + i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(nV * 3), 3));
  g.setAttribute('aA', new THREE.BufferAttribute(aA, 4)); g.setAttribute('aB', new THREE.BufferAttribute(aB, 4));
  g.setIndex(idx);
  return g;
}
function buildArmGeometry(j) {
  const aChains = chains.map((c, i) => [c, i]).filter(([c]) => c.type === 1 && c.j === j);
  const { MU, KV, FINS } = ARM, per = (MU + 1) * (KV + 1);
  const nV = aChains.length * FINS * per;
  // packed: aA = (row, u, v, fin), aB = (R, seed, length/R, jelly)
  const aA = new Float32Array(nV * 4), aB = new Float32Array(nV * 4);
  const idx = new Uint32Array(aChains.length * FINS * MU * KV * 6); let v = 0, k = 0;
  for (const [ch, row] of aChains) for (let f = 0; f < FINS; f++) {
    const b = v;
    for (let i = 0; i <= MU; i++) for (let jj = 0; jj <= KV; jj++) {
      aA.set([row, i / MU, jj / KV, f], v * 4); aB.set([ch.j.R, ch.seed, ch.len / ch.j.R, ch.j.i], v * 4); v++;
    }
    for (let i = 0; i < MU; i++) for (let jj = 0; jj < KV; jj++) {
      const a = b + i * (KV + 1) + jj, c = a + KV + 1; idx[k++] = a; idx[k++] = c; idx[k++] = a + 1; idx[k++] = a + 1; idx[k++] = c; idx[k++] = c + 1;
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(nV * 3), 3));
  g.setAttribute('aA', new THREE.BufferAttribute(aA, 4)); g.setAttribute('aB', new THREE.BufferAttribute(aB, 4));
  g.setIndex(new THREE.BufferAttribute(idx, 1));
  return g;
}
jellies.forEach(j => {
  const sc = new THREE.Scene();
  const g = new THREE.Group();
  // within the layer: appendages hang behind/below, then gonads, then the bell's far walls, then its near walls
  const tent = new THREE.Mesh(buildTentacleGeometry(j), tentMat); tent.renderOrder = 0;
  const arms = new THREE.Mesh(buildArmGeometry(j), armMat); arms.renderOrder = 1;
  const core = new THREE.Mesh(coreGeo, coreMat); core.renderOrder = 2;
  const back = new THREE.Mesh(bellGeoBack, bellMatBack); back.renderOrder = 3;
  const front = new THREE.Mesh(bellGeoFront, bellMatFront); front.renderOrder = 4;
  for (const m of [tent, arms, core, back, front]) { m.frustumCulled = false; m.userData.jelly = j; }
  // two layers: the animal's insides (and its far walls), then its near wall, which refracts them
  const g2 = new THREE.Group(), sc2 = new THREE.Scene();
  g.add(core, back); g2.add(front);
  sc.add(g, tent, arms); sc2.add(g2);
  j.group = g; j.group2 = g2; j.scenes = [sc, sc2];
});
function syncJellyMeshes() { for (const j of jellies) { for (const g of [j.group, j.group2]) { g.position.copy(j.pos); g.quaternion.copy(j.quat); g.scale.set(j.R, j.R * j.hs, j.R); } jellyParams.array[j.i].set(j.glow, j.hue, 0, 0); } }

// ───────────────────────────── the water column ─────────────────────────────
// Between objects the camera records the water's own path radiance:
//  (1) the asymptotic downwelling field at twilight depth — exponentially brighter toward the zenith, blue,
//      no sun shafts (those die out in the first tens of metres);
//  (2) light from every source scattered into the view ray by the water: the aureoles around the jellies and
//      the faint veil of the video-light beams. Integrated per pixel with equiangular sampling (the 1/r²
//      singularity is sampled exactly) and a Petzold-like forward-peaked phase function.
const WATER_SAMPLES = 6, WATER_RANGE = 60;
const waterPhase = c => hg(c, LIGHT.gWater).mul(0.85).add(0.15 * INV4PI);
function equiangular(C0, dir, Lpos, h0, weight) {
  const toL = Lpos.sub(C0), t0 = dot(toL, dir);
  const h = length(toL.sub(dir.mul(t0))).max(h0);
  const a0 = atan(t0.negate(), h), a1 = atan(float(WATER_RANGE).sub(t0), h);
  const acc = vec3(0).toVar();
  for (let k = 0; k < WATER_SAMPLES; k++) {
    const s = t0.add(h.mul(tan(mix(a0, a1, (k + 0.5) / WATER_SAMPLES))));
    const q = C0.add(dir.mul(s)).sub(Lpos), dl = length(q).max(1e-3), qd = q.div(dl);
    acc.addAssign(absorb(dl.add(s)).mul(waterPhase(dot(qd, dir.negate()))).mul(weight(qd)));
  }
  return acc.mul(a1.sub(a0).div(h).div(WATER_SAMPLES));
}
const bgScene = new THREE.Scene();
const bgMat = new THREE.MeshBasicNodeMaterial({ side: THREE.BackSide, depthWrite: false, depthTest: false });
bgMat.colorNode = Fn(() => {
  const dir = normalize(positionWorld.sub(cameraPosition)), C0 = cameraPosition;
  // radiance distribution at depth: L(θ) ∝ exp(−k(1 − cos θ)), upward/downward ratio ≈ e^6.8 ≈ 900
  const col = waterSky(dir).toVar();
  const scat = vec3(0).toVar();
  Loop(NJ, ({ i }) => {
    const L = jellyLights.element(i), E = jellyTints.element(i);
    scat.addAssign(E.xyz.mul(L.w).mul(equiangular(C0, dir, L.xyz, E.w.mul(0.3).max(0.02), () => float(1))));
  });
  for (const lp of [uLampA, uLampB]) scat.addAssign(uLampCol.mul(uLampI).mul(equiangular(C0, dir, lp, float(0.05), lampSpot)));
  col.addAssign(scat.mul(LIGHT.bWater));
  return col;
})();
const bg = new THREE.Mesh(new THREE.SphereGeometry(400, 48, 24), bgMat);
bg.frustumCulled = false; bgScene.add(bg);

// ───────────────────────────── suspended matter: marine snow and bubbles ─────────────────────────────
// Real objects in the water, not screen-space dots: each marine-snow aggregate is a small irregular translucent
// polyhedron with its own orientation, lit by whatever light reaches it (lit flank toward a jelly, forward glow
// when back-lit, invisible in the dark). Gas bubbles from a seep below rise in loose clusters; a bubble is an air
// sphere in water — a mirror wherever the incidence passes the critical angle (48.6°), clear in the middle.
// Depth of field is optical, not a sprite: a defocused particle's geometry is spread over its blur circle with
// its energy conserved. Particles are drawn in depth slices interleaved with the jelly layers.
const partScene = new THREE.Scene();
// indexed icosphere with smooth normals: shared vertices are shaded once
const indexedSphere = (r, detail) => { const g = new THREE.IcosahedronGeometry(r, detail); g.deleteAttribute('normal'); g.deleteAttribute('uv'); const m = mergeVertices(g); m.computeVertexNormals(); return m; };
const uRange = uniform(new THREE.Vector2(0, 1e9));
const uCamFwd = uniform(new THREE.Vector3(0, 0, -1));
const particleSets = [];
const premult = { transparent: true, depthWrite: false, depthTest: false, side: THREE.FrontSide, blending: THREE.CustomBlending,
  blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor };
// rotate v by the per-instance random rotation (axis–angle, Rodrigues)
const rotRand = (v, id) => {
  const ax = normalize(vec3(hash(id.add(13.1)), hash(id.add(17.3)), hash(id.add(19.7))).sub(0.5).add(1e-3));
  const ang = hash(id.add(23.9)).mul(6.2832).add(time.mul(hash(id.add(29.3)).sub(0.5).mul(0.3)));   // slow tumble
  const c = cos(ang), s = sin(ang);
  return v.mul(c).add(cross(ax, v).mul(s)).add(ax.mul(dot(ax, v)).mul(float(1).sub(c)));
};
// shared optics for a small object centred at C with physical radius r: slice culling, defocus spread
function particleOptics(C, r) {
  const toC = cameraPosition.sub(C), dist = length(toC), depth = dot(toC.negate(), uCamFwd).max(0.05);
  const pxW = dist.mul(uPxAngle);
  const blurR = cocOf(depth, uResScale.mul(48)).mul(pxW).mul(0.5);
  const R = max(r.add(blurR), pxW.mul(0.8));                            // radius actually covered on the sensor
  const inSlice = dist.greaterThanEqual(uRange.x).and(dist.lessThan(uRange.y)).and(dist.greaterThan(0.35));
  return { dist, R, spread: R.div(r), energy: sq(r.div(R)), inSlice, defocus: smoothstep(1.3, 3.0, R.div(r)) };
}

function makeSnow(N, box, ahead, seedOff) {
  const uCenter = uniform(new THREE.Vector3());
  const mat = new THREE.MeshBasicNodeMaterial(premult);
  const vLit = varyingProperty('vec3', 'vSnowLit'), vF = varyingProperty('vec4', 'vSnowF'), vRel = varyingProperty('vec3', 'vSnowRel');
  const id = float(instanceIndex).add(seedOff);
  const flake = hash(id.add(77.0)).lessThan(0.08);
  const r = mix(0.003, 0.014, hash(id.add(4242.0)).pow(6)).mul(select(flake, 1.8, 1.0));   // radius, steep power law
  const rawCenter = Fn(() => {
    const h = vec3(hash(id), hash(id.add(1731.0)), hash(id.add(3517.0)));
    const B = vec3(box.x, box.y, box.z);
    // slow sinking plus a gentle drift
    const drift = vec3(sin(time.mul(0.05).add(h.x.mul(40))).mul(0.25), time.mul(-0.012).mul(h.y.add(0.4)), cos(time.mul(0.04).add(h.z.mul(40))).mul(0.25));
    return mod(h.mul(B).add(drift).sub(uCenter), B).sub(B.mul(0.5)).add(uCenter);
  })();
  mat.positionNode = Fn(() => {
    const out = cameraPosition.sub(uCamFwd.mul(10)).toVar();               // culled: behind the lens
    const dRaw = length(cameraPosition.sub(rawCenter));
    // only this depth slice does any work (vertices of one instance branch together)
    If(dRaw.greaterThanEqual(uRange.x).and(dRaw.lessThan(uRange.y)).and(dRaw.greaterThan(0.35)), () => {
      const center = rawCenter.toVar();
      Loop(NJ, ({ i }) => {   // carried around bells, not through them
        const L = jellyLights.element(i), rb = jellyTints.element(i).w.mul(1.15);
        const dv = center.sub(L.xyz);
        If(dot(dv, dv).lessThan(rb.mul(rb)), () => { center.assign(L.xyz.add(normalize(dv).mul(rb))); });
      });
      const o = particleOptics(center, r);
      // irregular aggregate: anisotropic, lumpy (displacement keyed to vertex position keeps it watertight)
      const shape = vec3(1, select(flake, hash(id.add(31.0)).mul(0.4).add(0.25), hash(id.add(31.0)).mul(0.5).add(0.6)), hash(id.add(37.0)).mul(0.5).add(0.6));
      const lump = hash(dot(positionGeometry, vec3(12.9, 78.2, 37.7)).add(id)).mul(0.6).add(0.7);
      const local = rotRand(positionGeometry.mul(shape).mul(lump), id);
      const nW = rotRand(normalize(normalGeometry.div(shape)), id);
      const V = normalize(cameraPosition.sub(center));
      // light: lit flank (diffuse reflection) plus forward glow through the translucent aggregate
      const lit = vec3(0).toVar();
      Loop(NJ, ({ i }) => {
        const L = jellyLights.element(i), E = jellyTints.element(i);
        const dv = L.xyz.sub(center), d2 = dot(dv, dv).add(sq(E.w.mul(0.35))), d = sqrt(d2), l = dv.div(d);
        const refl = dot(nW, l).max(0).mul(INV4PI * 2.2), fwd = particlePhase(dot(l.negate(), V)).mul(0.8);
        lit.addAssign(E.xyz.mul(L.w.div(d2)).mul(refl.add(fwd)).mul(absorb(d)));
      });
      for (const lp of [uLampA, uLampB]) {
        const dv = lp.sub(center), d2 = dot(dv, dv).add(0.02), d = sqrt(d2), l = dv.div(d);
        const refl = dot(nW, l).max(0).mul(INV4PI * 2.2), fwd = particlePhase(dot(l.negate(), V)).mul(0.8);
        lit.addAssign(uLampCol.mul(uLampI.mul(lampSpot(l.negate())).div(d2)).mul(refl.add(fwd)).mul(absorb(d)));
      }
      lit.addAssign(uAmbient.mul(0.4));
      vLit.assign(lit.mul(4 * Math.PI * 0.55).mul(absorb(o.dist)));         // albedo 0.55
      vF.assign(vec4(o.energy, o.defocus, 1, 0));
      // defocused: the same geometry spread over its blur circle
      const off = local.mul(r.mul(2)).mul(o.spread);
      vRel.assign(off.sub(V.mul(dot(off, V))).div(o.R));               // offset across the line of sight, in blur radii
      out.assign(center.add(off));
    });
    return out;
  })();
  // in focus the aggregate's own shape; defocused, the lens spreads it into a smooth blur kernel
  // aggregates are loose and fluffy: optically thin at their silhouette, denser toward the middle
  const fluff = smoothstep(1.0, 0.25, length(vRel).mul(0.9));
  const kernel = mix(fluff, exp(dot(vRel, vRel).mul(-3.2)).mul(2.6), vF.y);
  mat.colorNode = vLit.mul(vF.x).mul(kernel);
  mat.opacityNode = vF.x.mul(0.35).mul(kernel).mul(float(1).sub(vF.y.mul(0.6))).clamp(0, 1);
  const mesh = new THREE.InstancedMesh(indexedSphere(0.5, 1), mat, N);
  mesh.frustumCulled = false; partScene.add(mesh);
  particleSets.push({ uCenter, ahead });
}

// Bubbles: loose clusters released by a seep somewhere below, rising at a few cm/s and wobbling
const BUB = { clusters: 22, per: 14 };
const uBubDebug = uniform(1);
function makeBubbles() {
  const mat = new THREE.MeshBasicNodeMaterial(premult);
  const vN = varyingProperty('vec3', 'vBubN'), vC = varyingProperty('vec4', 'vBubC');
  const id = float(instanceIndex), cl = floor(id.div(BUB.per));
  const r = mix(0.004, 0.024, hash(id.add(3.3)).pow(3)).mul(uBubDebug);        // 0.6–3.6 mm radius
  const center = Fn(() => {
    const base = vec3(hash(cl.add(1.1)).mul(14).sub(6), 0, hash(cl.add(2.2)).mul(-15).sub(3.5));
    const speed = r.mul(38).add(0.18);                                         // bigger bubbles rise faster
    const span = 18, y = mod(time.mul(speed).add(hash(cl.add(5.5)).mul(span)).add(hash(id).mul(1.5)), span).sub(span * 0.55);
    const spread = vec3(hash(id.add(7.7)), 0, hash(id.add(9.9))).sub(0.5).mul(0.6).mul(y.add(10).mul(0.06).add(0.3));
    const wob = vec3(sin(time.mul(6.0).add(id)), 0, cos(time.mul(5.3).add(id))).mul(r.mul(2.0));   // zig-zag of mm bubbles
    return base.add(vec3(0, y, 0)).add(spread).add(wob);
  })();
  mat.positionNode = Fn(() => {
    const o = particleOptics(center, r);
    vN.assign(normalGeometry.div(vec3(1, float(1).sub(smoothstep(0.009, 0.024, r).mul(0.32)), 1)));
    vC.assign(vec4(center, select(o.inSlice, o.energy, 0)));
    // bubbles above ~2 mm radius flatten into oblate, rocking ellipsoids
    const ob = smoothstep(0.009, 0.024, r).mul(0.32).mul(sin(time.mul(7.0).add(id)).mul(0.25).add(1));
    const shapeB = vec3(float(1).add(ob.mul(0.5)), float(1).sub(ob), float(1).add(ob.mul(0.5)));
    return select(o.inSlice, center.add(positionGeometry.mul(shapeB).mul(r.mul(2)).mul(o.spread)), cameraPosition.sub(uCamFwd.mul(10)));
  })();
  const C = vC.xyz, V = normalize(cameraPosition.sub(C)), N = normalize(vN);
  const cosi = dot(N, V).clamp(0, 1);
  // water → air: total internal reflection beyond the critical angle, Schlick (R0 ≈ 0.02) inside it
  const R = select(cosi.lessThan(Math.cos(Math.asin(1 / 1.333))), float(1), schlick(cosi, 1.333));
  mat.colorNode = Fn(() => mirrorEnv(C, reflect(V.negate(), N), N).mul(R).mul(vC.w).mul(absorb(length(cameraPosition.sub(C)))))();
  mat.opacityNode = R.mul(vC.w).mul(0.85);
  const mesh = new THREE.InstancedMesh(indexedSphere(0.5, 2), mat, BUB.clusters * BUB.per);
  mesh.frustumCulled = false; partScene.add(mesh);
}

// ───────────────────────────── image pipeline ─────────────────────────────
// A back-to-front optical compositor:
//   1. the water's path radiance fills the frame;
//   2. for each animal, far to near: the marine snow and bubbles in the depth slice behind it are drawn, then the
//      animal is rendered alone into a layer (radiance, opacity, refraction offset, frost, optical depth),
//      blurred by its own circle of confusion, and composited over the frame: the scene behind it is refracted,
//      frosted by forward scattering and attenuated by Beer–Lambert transmittance; its own light is added;
//   3. the particles in front of the nearest animal; then veiling glare, exposure, tone curve, sensor.
const uFocus = uniform(OPTICS.focus), uCocInf = uniform(OPTICS.cocAtInfinity), uResScale = uniform(1);
// circle of confusion in device pixels: thin lens, plus small-angle forward scattering by the water,
// which blurs a subject in proportion to the path length to it
const uWaterBlur = uniform(0.15);
const WATER_BLUR = 0.15;
const cocOf = (d, cap) => {
  const lens = abs(float(1).sub(uFocus.div(d))).mul(uCocInf), water = d.mul(uWaterBlur);
  return sqrt(lens.mul(lens).add(water.mul(water))).mul(uResScale).min(cap);
};
const cocJS = d => Math.min(60 * uResScale.value, Math.hypot(Math.abs(1 - uFocus.value / d) * uCocInf.value, d * uWaterBlur.value) * uResScale.value);

const MSAA = msaa;
const hdrRT = (count = 1, samples = 0) => {
  const rt = new THREE.RenderTarget(1, 1, { type: THREE.HalfFloatType, depthBuffer: false, count, samples });
  if (count > 1) { rt.textures[0].name = 'output'; rt.textures[1].name = 'aux'; }
  return rt;
};
// the frame ping-pongs between two buffers: each composite reads the frame as drawn so far and writes the next
const frameRTs = [hdrRT(), hdrRT()]; let cur = 0;
const mainRT = { get texture() { return frameRTs[cur].texture; }, get width() { return frameRTs[0].width; }, get height() { return frameRTs[0].height; } };
const layerRT = hdrRT(2, MSAA), blurA = hdrRT(2), blurB = hdrRT(2);
const waterRT = hdrRT();                              // path radiance is smooth: half resolution, bilinear up
const waterMat = new THREE.MeshBasicNodeMaterial(); waterMat.colorNode = texture(waterRT.texture).sample(screenUV).rgb;
const waterQuad = new THREE.QuadMesh(waterMat);
// aux accumulates refraction offsets and optical depths: a straight sum (ONE, ONE), never weighted by alpha —
// its fourth channel is τ, not a coverage
const SUM = new THREE.BlendMode(THREE.CustomBlending);
SUM.blendSrc = SUM.blendDst = SUM.blendSrcAlpha = SUM.blendDstAlpha = THREE.OneFactor;
const layerMRT = mrt({ output, aux: vec4(0) }).setBlendMode('aux', SUM);
// three clears secondary attachments to alpha = 1 by default — here alpha is optical depth, so an "empty" layer
// would transmit only e⁻¹ of everything behind it. Empty must mean τ = 0.
layerMRT.setClearColor('output', new THREE.Color(0x000000), 0);
layerMRT.setClearColor('aux', new THREE.Color(0x000000), 0);

// separable gaussian over both layer attachments (13 taps, σ = 3 taps; spacing scales the blur)
const blurIn0 = texture(blurA.textures[0]), blurIn1 = texture(blurA.textures[1]);
const uBlurStep = uniform(new THREE.Vector2());
const blurMat = new THREE.MeshBasicNodeMaterial();
{
  const W = [1, 0.946, 0.801, 0.607, 0.411, 0.249, 0.135].map(w => w);
  const norm = 1 / (W[0] + 2 * W.slice(1).reduce((a, b) => a + b, 0));
  const g = (tex) => {
    let acc = tex.sample(screenUV).mul(W[0] * norm);
    for (let k = 1; k < W.length; k++) acc = acc.add(tex.sample(screenUV.add(uBlurStep.mul(k))).add(tex.sample(screenUV.sub(uBlurStep.mul(k)))).mul(W[k] * norm));
    return acc;
  };
  const b0 = g(blurIn0), b1 = g(blurIn1);
  blurMat.colorNode = b0.rgb; blurMat.opacityNode = b0.a;
  blurMat.mrtNode = mrt({ output: b0, aux: b1 });
}
const blurQuad = new THREE.QuadMesh(blurMat);

// composite one layer over the frame
const compBehind = texture(frameRTs[0].texture), compL0 = texture(layerRT.textures[0]), compL1 = texture(layerRT.textures[1]);
const uTexel = uniform(new THREE.Vector2());
const compMat = new THREE.MeshBasicNodeMaterial();
compMat.colorNode = Fn(() => {
  const L = compL0.sample(screenUV), A = compL1.sample(screenUV);
  const uvR = screenUV.add(A.xy);
  // forward scattering in the tissue frosts what is seen through it
  const fr = A.z.mul(14).min(7).mul(uTexel);
  const behind = compBehind.sample(uvR).mul(0.4)
    .add(compBehind.sample(uvR.add(vec2(fr.x, fr.y.mul(0.5)))).mul(0.15)).add(compBehind.sample(uvR.add(vec2(fr.x.negate(), fr.y.mul(-0.5)))).mul(0.15))
    .add(compBehind.sample(uvR.add(vec2(fr.x.mul(-0.5), fr.y))).mul(0.15)).add(compBehind.sample(uvR.add(vec2(fr.x.mul(0.5), fr.y.negate()))).mul(0.15));
  // Beer–Lambert: the mauve pigment takes a little more green than red or blue
  const T = exp(A.w.negate().mul(vec3(0.9, 1.15, 0.85)));
  return behind.rgb.mul(T).add(L.rgb);
})();
const compQuad = new THREE.QuadMesh(compMat);

// screen rectangle covered by one animal (bell + every appendage node), padded by its blur
const _pp = new THREE.Vector3(), _cv = new THREE.Vector3();
function jellyRect(j, pad, W, H) {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, behind = false;
  const add = (x, y, z, rad) => {
    _pp.set(x, y, z).applyMatrix4(camera.matrixWorldInverse);
    if (_pp.z > -0.1) { behind = true; return; }
    const pr = rad / (-_pp.z * uPxAngle.value);
    _pp.applyMatrix4(camera.projectionMatrix);
    const px = (_pp.x * 0.5 + 0.5) * W, py = (0.5 - _pp.y * 0.5) * H;
    x0 = Math.min(x0, px - pr); x1 = Math.max(x1, px + pr); y0 = Math.min(y0, py - pr); y1 = Math.max(y1, py + pr);
  };
  j.bellCenter(_cv); add(_cv.x, _cv.y, _cv.z, j.R * 1.25 * Math.max(1, j.hs));
  for (let c = j.firstChain; c < j.firstChain + N_TENT + N_ARM; c++)
    for (let i = 2; i < NODES; i += 2) { const o = (c * NODES + i) * 3; add(P[o], P[o + 1], P[o + 2], chains[c].type ? j.R * 0.45 : j.R * 0.05); }
  if (behind || fullRect) return { x: 0, y: 0, w: W, h: H };
  x0 = Math.max(0, Math.floor(x0 - pad)); y0 = Math.max(0, Math.floor(y0 - pad));
  x1 = Math.min(W, Math.ceil(x1 + pad)); y1 = Math.min(H, Math.ceil(y1 + pad));
  if (x1 <= x0 || y1 <= y0) return null;
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}

function drawParticles(near, far) {
  uRange.value.set(near, far);
  renderer.setRenderTarget(frameRTs[cur]); renderer.render(partScene, camera);
}
function compositeJelly(j, rect, sigma) {
  for (const sc of j.scenes) compositeLayer(sc, rect, sigma);
}
function blurPass() {   // cleared with the layer's clear values, then the gaussian writes its outputs
  renderer.setMRT(layerMRT); renderer.autoClear = true; blurQuad.render(renderer); renderer.autoClear = false; renderer.setMRT(null);
}
function compositeLayer(sc, rect, sigma) {
  const W = mainRT.width, H = mainRT.height;
  const setRect = rt => { rt.scissor.set(rect.x, rect.y, rect.w, rect.h); };
  renderer.setScissorTest(true);
  // 1. this layer of the animal alone
  // (renderer.clear() ignores per-attachment clear colours; a render pass with the MRT bound honours them)
  setRect(layerRT); renderer.setRenderTarget(layerRT); renderer.setMRT(layerMRT);
  renderer.autoClear = true; renderer.render(sc, camera); renderer.autoClear = false;
  renderer.setMRT(null);
  let src = layerRT;
  // 2. its defocus (scene-referred, before compositing)
  if (sigma > 0.6 && blur) {
    const step = sigma / 3;
    blurIn0.value = layerRT.textures[0]; blurIn1.value = layerRT.textures[1]; uBlurStep.value.set(step / W, 0);
    setRect(blurA); renderer.setRenderTarget(blurA); blurPass();
    blurIn0.value = blurA.textures[0]; blurIn1.value = blurA.textures[1]; uBlurStep.value.set(0, step / H);
    setRect(blurB); renderer.setRenderTarget(blurB); blurPass();
    src = blurB;
  }
  // 3. composite over the frame as drawn so far (full frame: outside the animal it is an exact copy)
  renderer.setScissorTest(false);
  compBehind.value = frameRTs[cur].texture; compL0.value = src.textures[0]; compL1.value = src.textures[1];
  cur ^= 1;
  renderer.setRenderTarget(frameRTs[cur]); compQuad.render(renderer);
}
const _order = [];
function renderScene() {
  const W = mainRT.width, H = mainRT.height;
  renderer.setMRT(null); renderer.setScissorTest(false);
  renderer.setRenderTarget(waterRT); renderer.clear(); renderer.render(bgScene, camera);
  renderer.setRenderTarget(frameRTs[cur]); waterQuad.render(renderer);
  _order.length = 0;
  for (const j of jellies) { j.bellCenter(_cv); _order.push([j, _cv.distanceTo(camera.position)]); }
  // an animal that is off screen needs no layer, and no slice boundary either
  _order.sort((a, b) => b[1] - a[1]);
  let far = 1e6;
  for (const [j, d] of _order) {
    const sigma = cocJS(Math.max(0.1, d)) * 0.5;
    const rect = jellyRect(j, Math.ceil(3 * sigma + 18 * uResScale.value), W, H);
    if (!rect) continue;
    drawParticles(d, far); far = d; compositeJelly(j, rect, sigma);
  }
  drawParticles(0, far);
  mainTex.value = frameRTs[cur].texture;
  renderer.setRenderTarget(null);
}

// final: veiling glare, port optics, exposure, tone curve, sensor
const pipeline = new THREE.RenderPipeline(renderer);
pipeline.outputColorTransform = false;
const mainTex = texture(frameRTs[0].texture);
const bloomNear = bloom(mainTex, 0.45, 0.25, 0.12);       // lens veiling glare only
const bloomWide = bloom(mainTex, 0.22, 0.7, 0.3);
const finalNode = Fn(() => {
  // flat-port housing: refraction at the port gives mild pincushion and lateral colour that grow with field angle
  const q = screenUV.sub(0.5), r2 = dot(q, q);
  const uvD = q.mul(float(1).sub(r2.mul(0.07))).add(0.5);
  const ca = q.mul(r2).mul(0.014);
  const lensed = vec3(mainTex.sample(uvD.sub(ca)).r, mainTex.sample(uvD).g, mainTex.sample(uvD.add(ca)).b);
  const hdr = lensed.add(bloomNear.rgb).add(bloomWide.rgb).toVar();
  const vig = float(1).sub(r2.mul(1.25)).clamp(0, 1).pow(1.4);
  const sat = mix(vec3(luminance(hdr.rgb)), hdr.rgb, 1.6);      // AgX desaturates; restore the emitters' chroma
  const graded = sat.mul(vig).mul(uExposure).add(vec3(0.0002, 0.0007, 0.0012));
  const ldr = renderOutput(vec4(graded, 1)).toVar();
  // low-light sensor noise: shot noise dominates in the shadows, faint chroma component
  const seedN = screenUV.mul(vec2(1931.7, 1213.3)).add(fract(time.mul(13.7)).mul(97.0));
  const nL = hash(seedN.dot(vec2(1, 57))).add(hash(seedN.dot(vec2(1, 61)).add(3.1))).sub(1.0);
  const nC = vec3(hash(seedN.dot(vec2(1, 71)).add(7.7)), 0.5, hash(seedN.dot(vec2(1, 83)).add(1.9))).sub(0.5);
  const amp = float(0.030).mul(float(1).sub(luminance(ldr.rgb).mul(0.7)));
  return vec4(ldr.rgb.add(nL.mul(amp)).add(nC.mul(amp.mul(0.35))), 1);
})();
pipeline.outputNode = finalNode;

const _c = new THREE.Vector3(), _r = new THREE.Vector3(), _u = new THREE.Vector3(), _fw = new THREE.Vector3();

makeSnow(16000, new THREE.Vector3(36, 24, 44), 16, 0);          // the water volume in view
makeSnow(1500, new THREE.Vector3(8, 6, 8), 3.2, 50000);          // the near field
makeBubbles();
const hueTintJS = h => [1 + 0.28 * h, 1 - 0.06 * h, 1 - 0.10 * h];
function updateLights() {
  for (const j of jellies) {   // gonad/manubrium photocytes: the animal's main light, brightening with each stroke
    j.toWorld(0, 0.40, 0, _c);
    jellyLights.array[j.i].set(_c.x, _c.y, _c.z, LIGHT.coreI * j.glow * j.R * j.R * (1 + 0.3 * Math.max(0, j.c)));
    const t = hueTintJS(j.hue);
    jellyTints.array[j.i].set(LIGHT.emission[0] * t[0], LIGHT.emission[1] * t[1], LIGHT.emission[2] * t[2], j.R);
  }
  // video lights ride the camera housing on arms
  camera.matrixWorld.extractBasis(_r, _u, _fw); _fw.negate();
  const [ox, oy, oz] = LIGHT.lampOffset;
  uLampA.value.copy(camera.position).addScaledVector(_r, ox).addScaledVector(_u, oy).addScaledVector(_fw, oz);
  uLampB.value.copy(camera.position).addScaledVector(_r, -ox).addScaledVector(_u, oy).addScaledVector(_fw, oz);
  uLampDir.value.copy(_fw);
}

// ───────────────────────────── loop ─────────────────────────────
initChains();
for (let i = 0; i < 60 * WARMUP; i++) simulate(1 / 60);   // settle the appendages before the first frame
upload(); syncJellyMeshes(); updateLights();
let acc = 0, noDefocus = false;

return {
  update(dt, orbitTarget) {
  acc += dt; let n = 0;
  while (acc >= 1 / 60 && n < 3) { simulate(1 / 60); acc -= 1 / 60; n++; }
  if (n === 3) acc = 0;
  upload(); syncJellyMeshes();

    updateLights();
  // autofocus on the subject: the bell nearest the orbit pivot, eased like a focus puller
  const fwd = camera.getWorldDirection(new THREE.Vector3());
  let target = OPTICS.focus;
  {
    let best = 1e9;
    for (const j of jellies) { j.bellCenter(_c); const d = _c.distanceTo(orbitTarget) / j.R; if (d < best) { best = d; target = Math.max(0.5, _c.sub(camera.position).dot(fwd)); } }
  }
  const k = 1 - Math.exp(-dt * 3);
  uFocus.value += (target - uFocus.value) * k;
  uCocInf.value += ((noDefocus ? 0 : OPTICS.cocAtInfinity) - uCocInf.value) * k;
  for (const ps of particleSets) ps.uCenter.value.copy(camera.position).addScaledVector(fwd, ps.ahead);
  uCamFwd.value.copy(fwd);
  bg.position.copy(camera.position);

  },
  resize({ bufferWidth: w, bufferHeight: h }) {
    uPxAngle.value = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / h;
  for (const rt of [...frameRTs, layerRT, blurA, blurB]) rt.setSize(w, h);
  waterRT.setSize(Math.ceil(w / 2), Math.ceil(h / 2));
  uResScale.value = h / 1080;
  uTexel.value.set(1 / w, 1 / h);
  // screen-space refraction: (n − 1) × focal length in uv units (x in width units)
  const f = 1 / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2));
  const k = 1 - 1 / TISSUE.ior;
  uRefrK.value.set(k * f * h / w, k * f);

  },
  render() { renderScene(); pipeline.render(); },
  setDebugMode(mode) {
    pipeline.outputNode = mode === 'nopost' ? renderOutput(mainTex) : finalNode;
    uWaterBlur.value = mode === 'no-water-blur' ? 0 : WATER_BLUR;
    uCocInf.value = mode === 'no-defocus' ? 0 : OPTICS.cocAtInfinity;
    noDefocus = mode === 'no-defocus';
    pipeline.needsUpdate = true;
  },
  dispose() {
    pipeline.dispose();
    for (const rt of [...frameRTs, layerRT, blurA, blurB, waterRT]) rt.dispose();
    simTex.dispose(); frameTex.dispose(); cellTex.dispose();
    const geometries = new Set(), materials = new Set();
    for (const sc of [bgScene, partScene, ...jellies.flatMap(j => j.scenes)]) {
      sc.traverse(o => {
        if (o.geometry) geometries.add(o.geometry);
        if (o.material) for (const m of (Array.isArray(o.material) ? o.material : [o.material])) materials.add(m);
      });
      sc.clear();
    }
    for (const g of geometries) g.dispose();
    for (const m of materials) m.dispose();
    for (const q of [waterQuad, blurQuad, compQuad]) q.material.dispose();
  },
};
}
