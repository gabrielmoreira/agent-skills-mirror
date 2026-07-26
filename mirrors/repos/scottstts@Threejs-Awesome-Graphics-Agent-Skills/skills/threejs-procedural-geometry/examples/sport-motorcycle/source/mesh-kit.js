import * as THREE from "three/webgpu";

import { SEED } from "./design-contract.js";

/* ============================================================================
   2. GEOMETRY KERNEL
   ----------------------------------------------------------------------------
   A small set of emitters shared by every part: a semantic mesh writer, a
   sampled-grid compiler with explicit seams and winding, revolves, swept
   profiles with either parallel-transport or world-up frames, thick panel
   shells with real rim thickness, and bevelled extrusions.
   Triangle emission is the last step; each part is planned as samples first.
   ========================================================================== */

const TAU = Math.PI * 2;
const V2 = (x = 0, y = 0) => new THREE.Vector2(x, y);
const V3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const lerp = THREE.MathUtils.lerp;
const clampf = THREE.MathUtils.clamp;
const smooth01 = (t) => t * t * (3 - 2 * t);
const ease = (t, p) => Math.pow(clampf(t, 0, 1), p);

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rnd = mulberry32(SEED);

/* --- curve resampling ---------------------------------------------------- */
function catmull2(pts, count, closed = false) {
  const c = new THREE.CatmullRomCurve3(pts.map((p) => V3(p[0] ?? p.x, p[1] ?? p.y, 0)), closed);
  c.curveType = "centripetal";
  return c.getSpacedPoints(closed ? count - 1 : count).map((p) => V2(p.x, p.y));
}
function catmull3(pts, count, closed = false) {
  const c = new THREE.CatmullRomCurve3(
    pts.map((p) => (p.isVector3 ? p.clone() : V3(p[0], p[1], p[2]))), closed);
  c.curveType = "centripetal";
  return c.getSpacedPoints(closed ? count - 1 : count);
}

/* --- semantic mesh writer ------------------------------------------------ */
class Writer {
  constructor() { this.p = []; this.n = []; this.t = []; this.i = []; }
  get count() { return this.p.length / 3; }
  vert(p, n, u, v) {
    this.p.push(p.x, p.y, p.z);
    this.n.push(n.x, n.y, n.z);
    this.t.push(u, v);
    return this.p.length / 3 - 1;
  }
  tri(a, b, c) { this.i.push(a, b, c); }
  quad(a, b, c, d) { this.i.push(a, b, c, b, d, c); }
  /* sampled surface: rows[row][col] of Vector3.  closeU stitches an explicit
     seam column so the UV wrap is not shared with the geometric seam.       */
  grid(rows, { closeU = false, flip = false, vRow = null, uRange = [0, 1], vRange = [0, 1], uvFn = null } = {}) {
    const R = rows.length, C = rows[0].length;
    const EC = closeU ? C + 1 : C;
    const wrap = (c) => ((c % C) + C) % C;
    const at = (r, c) => rows[clampf(r, 0, R - 1)][closeU ? wrap(c) : clampf(c, 0, C - 1)];
    const base = this.count;
    const dU = V3(), dV = V3(), nn = V3();
    for (let r = 0; r < R; r++) {
      for (let c = 0; c < EC; c++) {
        const P = at(r, c);
        dU.subVectors(at(r, c + 1), at(r, c - 1));
        dV.subVectors(at(r + 1, c), at(r - 1, c));
        nn.crossVectors(dU, dV);
        if (nn.lengthSq() < 1e-16) {
          const a = V3(), b = V3();
          for (const q of rows[clampf(r - 1, 0, R - 1)]) a.add(q);
          for (const q of rows[clampf(r + 1, 0, R - 1)]) b.add(q);
          nn.subVectors(a.divideScalar(C), b.divideScalar(C));
          if (nn.lengthSq() < 1e-16) nn.set(0, 1, 0);
        }
        nn.normalize(); if (flip) nn.negate();
        let u, v;
        if (uvFn) { const o = uvFn(r, c, R, EC); u = o[0]; v = o[1]; }
        else {
          u = lerp(uRange[0], uRange[1], c / (EC - 1));
          v = lerp(vRange[0], vRange[1], vRow ? vRow[r] : r / (R - 1));
        }
        this.vert(P, nn, u, v);
      }
    }
    for (let r = 0; r < R - 1; r++) {
      for (let c = 0; c < EC - 1; c++) {
        const a = base + r * EC + c, b = a + 1, cc = a + EC, d = cc + 1;
        if (flip) this.i.push(a, cc, b, b, cc, d);
        else this.i.push(a, b, cc, b, d, cc);
      }
    }
    return this;
  }
  /* hard-edged flat cap from a closed ring; normal from Newell's method */
  fan(ring, flip = false, uvScale = 1) {
    const n = V3(); const ctr = V3();
    for (let i = 0; i < ring.length; i++) {
      const a = ring[i], b = ring[(i + 1) % ring.length];
      n.x += (a.y - b.y) * (a.z + b.z);
      n.y += (a.z - b.z) * (a.x + b.x);
      n.z += (a.x - b.x) * (a.y + b.y);
      ctr.add(a);
    }
    ctr.divideScalar(ring.length); n.normalize(); if (flip) n.negate();
    const base = this.count;
    this.vert(ctr, n, 0.5, 0.5);
    for (let i = 0; i < ring.length; i++) {
      const a = ring[i];
      this.vert(a, n, 0.5 + (a.x - ctr.x) * uvScale, 0.5 + (a.y - ctr.y) * uvScale);
    }
    for (let i = 0; i < ring.length; i++) {
      const a = base + 1 + i, b = base + 1 + ((i + 1) % ring.length);
      if (flip) this.tri(base, b, a); else this.tri(base, a, b);
    }
    return this;
  }
  /* quad strip between two equal-length rings (annulus cap, rim band) */
  band(ringA, ringB, { closed = true, flip = false, v0 = 0, v1 = 1, hard = true } = {}) {
    const N = ringA.length;
    const rows = [ringA, ringB];
    if (!hard) return this.grid(rows, { closeU: closed, flip, vRange: [v0, v1] });
    const base = this.count;
    const lim = closed ? N : N - 1;
    for (let i = 0; i < lim; i++) {
      const j = (i + 1) % N;
      const a = ringA[i], b = ringA[j], c = ringB[i], d = ringB[j];
      const n = V3().crossVectors(V3().subVectors(b, a), V3().subVectors(c, a)).normalize();
      if (flip) n.negate();
      const u0 = i / N, u1 = (i + 1) / N;
      const i0 = this.vert(a, n, u0, v0), i1 = this.vert(b, n, u1, v0);
      const i2 = this.vert(c, n, u0, v1), i3 = this.vert(d, n, u1, v1);
      if (flip) this.i.push(i0, i2, i1, i1, i2, i3);
      else this.i.push(i0, i1, i2, i1, i3, i2);
    }
    return this;
  }
  geometry() {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(this.p, 3));
    g.setAttribute("normal", new THREE.Float32BufferAttribute(this.n, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(this.t, 2));
    g.setIndex(this.i);
    g.computeBoundingSphere();
    return g;
  }
}
const write = (fn) => { const w = new Writer(); fn(w); return w.geometry(); };

/* --- ring / revolve ------------------------------------------------------ */
function ringPoints(center, axisU, axisV, radius, segments, phase = 0) {
  const out = [];
  for (let i = 0; i < segments; i++) {
    const a = phase + (i / segments) * TAU;
    out.push(V3().copy(center)
      .addScaledVector(axisU, Math.cos(a) * radius)
      .addScaledVector(axisV, Math.sin(a) * radius));
  }
  return out;
}
const AXES = {
  x: [V3(0, 1, 0), V3(0, 0, 1), V3(1, 0, 0)],
  y: [V3(0, 0, 1), V3(1, 0, 0), V3(0, 1, 0)],
  z: [V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)],
};
/* profile: Vector2(radius, distanceAlongAxis) */
function revolveRows(profile, axis, segments, offset = V3()) {
  const [u, v, w] = AXES[axis];
  return profile.map((pt) => ringPoints(
    V3().copy(offset).addScaledVector(w, pt.y), u, v, Math.max(pt.x, 1e-4), segments));
}
function arcLengthV(profile) {
  const v = [0]; let s = 0;
  for (let i = 1; i < profile.length; i++) {
    s += Math.hypot(profile[i].x - profile[i - 1].x, profile[i].y - profile[i - 1].y);
    v.push(s);
  }
  return v.map((x) => x / (s || 1));
}
function revolve(profile, { axis = "z", segments = 48, flip = false, offset = V3(), w = null, capStart = false, capEnd = false, uRange = [0, 1], vRange = [0, 1] } = {}) {
  const rows = revolveRows(profile, axis, segments, offset);
  const target = w || new Writer();
  target.grid(rows, { closeU: true, flip, vRow: arcLengthV(profile), uRange, vRange });
  if (capStart) target.fan(rows[0], !flip);
  if (capEnd) target.fan(rows[rows.length - 1], flip);
  // A lathe is a solid when its profile closes on itself, when both ends are
  // capped, OR when both ends land on the axis — that last case is a dome or
  // a plug, and missing it left such parts inside-out and invisible from
  // outside, since their front faces were the ones being culled.
  const last = profile[profile.length - 1];
  const closedProfile = Math.hypot(profile[0].x - last.x, profile[0].y - last.y) < 1e-4;
  const onAxisEnds = Math.abs(profile[0].x) < 1e-4 && Math.abs(last.x) < 1e-4;
  return w ? target : ((capStart && capEnd) || closedProfile || onAxisEnds
    ? orient(target.geometry()) : target.geometry());
}

/* --- swept profiles ------------------------------------------------------ */
/* Parallel-transport frames: minimises twist along an arbitrary path.       */
function transportFrames(points, seedUp) {
  const N = points.length, T = [], Nn = [], B = [];
  for (let i = 0; i < N; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(N - 1, i + 1)];
    const t = V3().subVectors(b, a);
    if (t.lengthSq() < 1e-14) t.copy(T[i - 1] || V3(0, 0, 1));
    T.push(t.normalize());
  }
  let n = seedUp ? seedUp.clone() : (Math.abs(T[0].y) < 0.94 ? V3(0, 1, 0) : V3(1, 0, 0));
  n = V3().crossVectors(T[0], V3().crossVectors(n, T[0]));
  if (n.lengthSq() < 1e-12) n = V3().crossVectors(T[0], V3(1, 0, 0));
  n.normalize();
  for (let i = 0; i < N; i++) {
    if (i > 0) {
      const ax = V3().crossVectors(T[i - 1], T[i]);
      if (ax.lengthSq() > 1e-12) {
        ax.normalize();
        n.applyAxisAngle(ax, Math.acos(clampf(T[i - 1].dot(T[i]), -1, 1)));
      }
    }
    Nn.push(n.clone());
    B.push(V3().crossVectors(T[i], n).normalize());
  }
  return { T, N: Nn, B };
}
/* World-up frames: keeps a profile's "up" locked to world Y — used for
   chassis rails whose section must not roll along the path.                */
function uprightFrames(points, up = V3(0, 1, 0)) {
  const N = points.length, T = [], Nn = [], B = [];
  for (let i = 0; i < N; i++) {
    const a = points[Math.max(0, i - 1)], b = points[Math.min(N - 1, i + 1)];
    T.push(V3().subVectors(b, a).normalize());
  }
  for (let i = 0; i < N; i++) {
    let b = V3().crossVectors(T[i], up);
    if (b.lengthSq() < 1e-10) b = V3().crossVectors(T[i], V3(0, 0, 1));
    b.normalize();
    Nn.push(V3().crossVectors(b, T[i]).normalize());
    B.push(b);
  }
  return { T, N: Nn, B };
}
/* sectionFn(t, i) -> [Vector2] in (binormal, normal) frame coordinates */
function sweep(path, sectionFn, {
  closed = false, flip = false, upright = false, up = null, seedUp = null,
  capStart = true, capEnd = true, w = null, vScale = 1, uRange = [0, 1],
} = {}) {
  const F = upright ? uprightFrames(path, up || V3(0, 1, 0)) : transportFrames(path, seedUp);
  const rows = path.map((P, i) => {
    const t = i / (path.length - 1);
    const sec = sectionFn(t, i);
    return sec.map((s) => V3().copy(P).addScaledVector(F.B[i], s.x).addScaledVector(F.N[i], s.y));
  });
  const vRow = [0]; let acc = 0;
  for (let i = 1; i < path.length; i++) { acc += path[i].distanceTo(path[i - 1]); vRow.push(acc); }
  for (let i = 0; i < vRow.length; i++) vRow[i] = (vRow[i] / (acc || 1)) * vScale;
  const target = w || new Writer();
  target.grid(rows, { closeU: true, flip, vRow, uRange });
  if (capStart && !closed) target.fan(rows[0], !flip);
  if (capEnd && !closed) target.fan(rows[rows.length - 1], flip);
  return w ? target
    : (capStart && capEnd && !closed ? orient(target.geometry()) : target.geometry());
}
const tube = (path, radius, segments = 16, opts = {}) => {
  const rf = typeof radius === "number" ? () => radius : radius;
  return sweep(path, (t) => {
    const r = rf(t), out = [];
    for (let i = 0; i < segments; i++) {
      const a = (i / segments) * TAU;
      out.push(V2(Math.cos(a) * r, Math.sin(a) * r));
    }
    return out;
  }, opts);
};
function arcPath(center, axisU, axisV, radius, a0, a1, segments = 24) {
  const out = [];
  for (let i = 0; i <= segments; i++) {
    const a = lerp(a0, a1, i / segments);
    out.push(V3().copy(center).addScaledVector(axisU, Math.cos(a) * radius)
      .addScaledVector(axisV, Math.sin(a) * radius));
  }
  return out;
}

/* --- parametric sections -------------------------------------------------
   Four-quadrant superellipse.  Separate exponents and extents per quadrant
   give one control set that spans soft tank shoulders (n≈2.4) through the
   knife-edged creases of a fairing flank (n≈5.5).                          */
function superSection({
  halfW = 1, top = 1, bottom = 1, nTop = 2.6, nBot = 2.6,
  nTopIn = null, nBotIn = null, cx = 0, cy = 0, shoulder = 0, segments = 48,
  wTop = 1, wBot = 1,
} = {}) {
  const out = [];
  for (let i = 0; i < segments; i++) {
    const a = (i / segments) * TAU;
    const ca = Math.cos(a), sa = Math.sin(a);
    const upper = sa >= 0;
    const nx = upper ? (nTopIn ?? nTop) : (nBotIn ?? nBot);   // horizontal falloff
    const ny = upper ? nTop : nBot;                            // vertical falloff
    const h = upper ? top : bottom;
    const wk = upper ? wTop : wBot;                            // per-half width scale
    const x = Math.sign(ca) * Math.pow(Math.abs(ca), 2 / nx) * halfW * wk;
    // shoulder raises or drops the widest point without moving crown or keel
    const y = Math.sign(sa) * Math.pow(Math.abs(sa), 2 / ny) * h
      + shoulder * (1 - Math.abs(sa));
    out.push(V2(cx + x, cy + y));
  }
  return out;
}
/* rounded rectangle sampled by true perimeter arc length: four straights and
   four quarter-arcs, so corner radius stays exact at any segment count.    */
function roundRect(halfW, halfH, r, segments = 40) {
  r = Math.min(r, Math.min(halfW, halfH) * 0.999);
  const sw = 2 * (halfW - r), sh = 2 * (halfH - r), arc = (Math.PI / 2) * r;
  const total = 2 * sw + 2 * sh + 4 * arc;
  const corner = [[halfW - r, halfH - r, 0], [-(halfW - r), halfH - r, Math.PI / 2],
    [-(halfW - r), -(halfH - r), Math.PI], [halfW - r, -(halfH - r), Math.PI * 1.5]];
  const out = [];
  for (let i = 0; i < segments; i++) {
    let s = (i / segments) * total;
    // start mid-way along the right edge so the seam sits on a straight run
    s = (s + sh / 2) % total;
    if (s < sh) { out.push(V2(halfW, -(halfH - r) + s)); continue; } s -= sh;
    if (s < arc) { const a = corner[0][2] + s / r; out.push(V2(corner[0][0] + Math.cos(a) * r, corner[0][1] + Math.sin(a) * r)); continue; } s -= arc;
    if (s < sw) { out.push(V2(halfW - r - s, halfH)); continue; } s -= sw;
    if (s < arc) { const a = corner[1][2] + s / r; out.push(V2(corner[1][0] + Math.cos(a) * r, corner[1][1] + Math.sin(a) * r)); continue; } s -= arc;
    if (s < sh) { out.push(V2(-halfW, halfH - r - s)); continue; } s -= sh;
    if (s < arc) { const a = corner[2][2] + s / r; out.push(V2(corner[2][0] + Math.cos(a) * r, corner[2][1] + Math.sin(a) * r)); continue; } s -= arc;
    if (s < sw) { out.push(V2(-(halfW - r) + s, -halfH)); continue; } s -= sw;
    const a = corner[3][2] + s / r;
    out.push(V2(corner[3][0] + Math.cos(a) * r, corner[3][1] + Math.sin(a) * r));
  }
  return out;
}
/* uniform scale/offset helpers for 2D sections */
const secScale = (pts, sx, sy = sx) => pts.map((p) => V2(p.x * sx, p.y * sy));
const secMove = (pts, dx, dy) => pts.map((p) => V2(p.x + dx, p.y + dy));
/* explicit closed polyline through 2D controls (the sculpted-profile route) */
const section = (controls, n) => catmull2(controls, n, true);

/* --- panel shells --------------------------------------------------------
   Bodywork is not a zero-thickness sheet: every cowl carries a visible edge
   where it meets the next panel.  Offset the sampled outer surface along its
   own normals and stitch the four boundaries.                              */
function gridNormals(rows) {
  const R = rows.length, C = rows[0].length;
  const at = (r, c) => rows[clampf(r, 0, R - 1)][clampf(c, 0, C - 1)];
  const out = [];
  for (let r = 0; r < R; r++) {
    const line = [];
    for (let c = 0; c < C; c++) {
      const dU = V3().subVectors(at(r, c + 1), at(r, c - 1));
      const dV = V3().subVectors(at(r + 1, c), at(r - 1, c));
      const n = V3().crossVectors(dU, dV);
      if (n.lengthSq() < 1e-16) n.set(0, 1, 0);
      line.push(n.normalize());
    }
    out.push(line);
  }
  return out;
}
function panelShell(rows, thickness, { flip = false, rim = [1, 1, 1, 1], w = null, taper = null, uRange = [0, 1], vRange = [0, 1] } = {}) {
  const N = gridNormals(rows);
  const R = rows.length, C = rows[0].length;
  const sgn = flip ? 1 : -1;
  const inner = rows.map((row, r) => row.map((P, c) => {
    const k = taper ? taper(r / (R - 1), c / (C - 1)) : 1;
    return V3().copy(P).addScaledVector(N[r][c], sgn * thickness * k);
  }));
  const target = w || new Writer();
  target.grid(rows, { flip, uRange, vRange });
  target.grid(inner, { flip: !flip, uRange, vRange });
  const edge = (getOuter, getInner, count, doFlip) => {
    const A = [], B = [];
    for (let i = 0; i < count; i++) { A.push(getOuter(i)); B.push(getInner(i)); }
    target.band(A, B, { closed: false, flip: doFlip });
  };
  if (rim[0]) edge((i) => rows[0][i], (i) => inner[0][i], C, flip);
  if (rim[1]) edge((i) => rows[R - 1][i], (i) => inner[R - 1][i], C, !flip);
  if (rim[2]) edge((i) => rows[i][0], (i) => inner[i][0], R, !flip);
  if (rim[3]) edge((i) => rows[i][C - 1], (i) => inner[i][C - 1], R, flip);
  const all = rim[0] && rim[1] && rim[2] && rim[3];
  return w ? target : (all ? orient(target.geometry()) : target.geometry());
}

/* --- bevelled extrusion (rotors, sprockets, brackets, caliper bodies) ---- */
function offsetPoly(pts, d) {
  const N = pts.length, out = [];
  for (let i = 0; i < N; i++) {
    const p = pts[i], a = pts[(i - 1 + N) % N], b = pts[(i + 1) % N];
    const e0 = V2().subVectors(p, a).normalize(), e1 = V2().subVectors(b, p).normalize();
    const n0 = V2(e0.y, -e0.x), n1 = V2(e1.y, -e1.x);
    const n = V2().addVectors(n0, n1).normalize();
    const cosHalf = Math.max(0.35, n.dot(n1));
    out.push(V2(p.x + n.x * d / cosHalf, p.y + n.y * d / cosHalf));
  }
  return out;
}
const toRing = (pts2, z, axis = "z") => pts2.map((p) =>
  axis === "z" ? V3(p.x, p.y, z) : axis === "x" ? V3(z, p.y, p.x) : V3(p.x, z, p.y));
/* solid plate with chamfered rim */
function extrudePlate(poly, depth, { bevel = 0.0012, axis = "z", z = 0, w = null, flip = false } = {}) {
  const h = depth / 2, inn = offsetPoly(poly, -bevel);
  const z0 = z - h, z1 = z + h, b = Math.min(bevel, depth * 0.35);
  const rows = [
    toRing(inn, z0, axis), toRing(poly, z0 + b, axis),
    toRing(poly, z1 - b, axis), toRing(inn, z1, axis),
  ];
  const target = w || new Writer();
  target.grid(rows, { closeU: true, flip: axis === "x" ? !flip : flip });
  target.fan(rows[0], axis === "x" ? flip : !flip);
  target.fan(rows[3], axis === "x" ? !flip : flip);
  return w ? target : orient(target.geometry());
}
/* resample a closed 2D polyline to n points by arc length — lets an annulus
   pair a 258-point toothed profile with a plain circular bore              */
function resampleRing(pts, n) {
  if (pts.length === n) return pts;
  const N = pts.length, cum = [0];
  for (let i = 1; i <= N; i++) cum.push(cum[i - 1] + pts[i % N].distanceTo(pts[i - 1]));
  const total = cum[N];
  const out = [];
  let j = 1;
  for (let i = 0; i < n; i++) {
    const s = (i / n) * total;
    while (j < N && cum[j] < s) j++;
    const t = (s - cum[j - 1]) / Math.max(1e-9, cum[j] - cum[j - 1]);
    out.push(V2().lerpVectors(pts[j - 1], pts[j % N], t));
  }
  return out;
}
/* annular plate (disc with hub bore, sprocket) */
function extrudeRing(outer, inner, depth, { bevel = 0.0010, axis = "z", z = 0, w = null } = {}) {
  inner = resampleRing(inner, outer.length);
  const h = depth / 2, b = Math.min(bevel, depth * 0.35);
  const oi = offsetPoly(outer, -bevel), ii = offsetPoly(inner, bevel);
  const z0 = z - h, z1 = z + h;
  const O = [toRing(oi, z0, axis), toRing(outer, z0 + b, axis), toRing(outer, z1 - b, axis), toRing(oi, z1, axis)];
  const I = [toRing(ii, z0, axis), toRing(inner, z0 + b, axis), toRing(inner, z1 - b, axis), toRing(ii, z1, axis)];
  const target = w || new Writer();
  const fx = axis === "x";
  target.grid(O, { closeU: true, flip: fx });
  target.grid(I, { closeU: true, flip: !fx });
  target.band(O[0], I[0], { closed: true, flip: !fx });
  target.band(O[3], I[3], { closed: true, flip: fx });
  return w ? target : orient(target.geometry());
}
const circlePoly = (r, n, phase = 0, cx = 0, cy = 0) => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const a = phase + (i / n) * TAU;
    out.push(V2(cx + Math.cos(a) * r, cy + Math.sin(a) * r));
  }
  return out;
};

/* --- filleted box (cast covers, calipers, master cylinders) --------------
   Loft superellipse sections whose extent follows a rounded end profile, so
   corners carry a true 3D fillet instead of a flat chamfer.                */
function filletBox(w_, h_, d_, r, {
  segments = 32, rings = 11, taperTop = 1, taperBot = 1, shear = 0, w = null, axisCap = true,
} = {}) {
  const hw = w_ / 2, hh = h_ / 2, hd = d_ / 2;
  r = Math.min(r, Math.min(hw, hh, hd) * 0.98);
  const rows = [];
  for (let i = 0; i < rings; i++) {
    const t = i / (rings - 1);
    const z = lerp(-hd, hd, t);
    // spherical fillet: how far the section pulls in near each end cap
    const over = Math.abs(z) - (hd - r);
    const inset = over > 0 ? r - Math.sqrt(Math.max(0, r * r - over * over)) : 0;
    const rr = Math.max(1e-4, r - inset);
    const base = roundRect(Math.max(1e-4, hw - inset), Math.max(1e-4, hh - inset), rr, segments);
    rows.push(base.map((p) => {
      const vy = clampf(p.y / hh, -1, 1);
      const k = vy > 0 ? lerp(1, taperTop, vy) : lerp(1, taperBot, -vy);
      return V3(p.x * k + shear * z, p.y, z);
    }));
  }
  const target = w || new Writer();
  target.grid(rows, { closeU: true });
  if (axisCap) { target.fan(rows[0], true); target.fan(rows[rows.length - 1], false); }
  return w ? target : (axisCap ? orient(target.geometry()) : target.geometry());
}

/* --- orientation guard ---------------------------------------------------
   A loft's winding depends on whether its station table runs +Z or -Z, and on
   which way its section is wound.  Rather than police that by hand in forty
   tables, every closed body is checked: if the enclosed signed volume comes
   out negative the surface is inside-out, so flip winding and normals.
   Silent inversion is the single most common failure in generated hard
   surfaces — it survives a wireframe check and only shows up as wrong light. */
function signedVolume(geometry) {
  const p = geometry.attributes.position.array;
  const idx = geometry.index.array;
  let v = 0;
  for (let i = 0; i < idx.length; i += 3) {
    const a = idx[i] * 3, b = idx[i + 1] * 3, c = idx[i + 2] * 3;
    const ax = p[a], ay = p[a + 1], az = p[a + 2];
    const bx = p[b], by = p[b + 1], bz = p[b + 2];
    const cx = p[c], cy = p[c + 1], cz = p[c + 2];
    v += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx);
  }
  return v / 6;
}
function flipGeometry(geometry) {
  const n = geometry.attributes.normal.array;
  for (let i = 0; i < n.length; i++) n[i] = -n[i];
  const idx = geometry.index.array;
  for (let i = 0; i < idx.length; i += 3) {
    const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t;
  }
  geometry.attributes.normal.needsUpdate = true;
  geometry.index.needsUpdate = true;
  return geometry;
}
let INVERTED = 0;
function orient(geometry) {
  if (!geometry.index) return geometry;
  if (signedVolume(geometry) < 0) { INVERTED++; flipGeometry(geometry); }
  return geometry;
}

/* --- geometry utilities -------------------------------------------------- */
function mirrorX(geometry) {
  const g = geometry.clone();
  const p = g.attributes.position, n = g.attributes.normal;
  for (let i = 0; i < p.count; i++) { p.setX(i, -p.getX(i)); n.setX(i, -n.getX(i)); }
  const idx = g.index.array;
  for (let i = 0; i < idx.length; i += 3) { const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t; }
  g.index.needsUpdate = true; p.needsUpdate = true; n.needsUpdate = true;
  g.computeBoundingSphere();
  return g;
}
function xform(geometry, m) {
  const g = geometry.clone(); g.applyMatrix4(m); return g;
}
const M = {
  t: (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z),
  rx: (a) => new THREE.Matrix4().makeRotationX(a),
  ry: (a) => new THREE.Matrix4().makeRotationY(a),
  rz: (a) => new THREE.Matrix4().makeRotationZ(a),
  s: (x, y, z) => new THREE.Matrix4().makeScale(x, y, z),
  c: (...ms) => ms.reduce((acc, m) => acc.multiply(m), new THREE.Matrix4()),
};

/* --- part registry & diagnostics ---------------------------------------- */
const PARTS = [];
const SLOT_COLORS = {};
function add(parent, geometry, material, name, { cast = true, receive = true, slot = null } = {}) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = cast; mesh.receiveShadow = receive;
  mesh.name = name;
  mesh.userData.slot = slot || (material.userData && material.userData.slot) || "misc";
  parent.add(mesh);
  const tris = geometry.index ? geometry.index.count / 3 : geometry.attributes.position.count / 3;
  PARTS.push({ name, tris, slot: mesh.userData.slot });
  return mesh;
}
/* pair(): author once on +X, mirror to -X — the symmetry contract */
function pair(parent, geometry, material, name, opts = {}) {
  const a = add(parent, geometry, material, name + ".R", opts);
  const b = add(parent, mirrorX(geometry), material, name + ".L", opts);
  return [a, b];
}
function instance(parent, geometry, material, matrices, name, opts = {}) {
  const im = new THREE.InstancedMesh(geometry, material, matrices.length);
  im.castShadow = opts.cast !== false; im.receiveShadow = opts.receive !== false;
  im.name = name;
  im.userData.slot = opts.slot || (material.userData && material.userData.slot) || "misc";
  matrices.forEach((m, i) => im.setMatrixAt(i, m));
  im.instanceMatrix.needsUpdate = true;
  parent.add(im);
  const tris = (geometry.index ? geometry.index.count / 3 : geometry.attributes.position.count / 3);
  PARTS.push({ name, tris: tris * matrices.length, slot: im.userData.slot, instanced: matrices.length });
  return im;
}

export {
  AXES, INVERTED, M, PARTS, SLOT_COLORS, TAU, V2, V3, Writer, add, arcLengthV, arcPath, catmull2, catmull3, circlePoly, clampf, ease, extrudePlate, extrudeRing, filletBox, flipGeometry, gridNormals, instance, lerp, mirrorX, mulberry32, offsetPoly, orient, pair, panelShell, resampleRing, revolve, revolveRows, ringPoints, rnd, roundRect, secMove, secScale, section, signedVolume, smooth01, superSection, sweep, toRing, transportFrames, tube, uprightFrames, write, xform,
};

/** Closed bodies whose winding was corrected by the orientation guard. */
export function invertedCount() { return INVERTED; }
export function resetInvertedCount() { INVERTED = 0; }
