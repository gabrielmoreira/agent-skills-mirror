import * as THREE from "three/webgpu";

/*
   GEOMETRY KERNEL
   Reusable emitters shared by every subassembly.  Nothing in the model constructs a
   BufferGeometry directly; each part supplies a *plan* (sampled sections, paths,
   outlines) and one of these compilers emits triangles, normals, UVs and winding.
*/

const TAU = Math.PI * 2;
const PI  = Math.PI;
const V2  = (x = 0, y = 0) => new THREE.Vector2(x, y);
const V3  = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const lerp = THREE.MathUtils.lerp;
const clamp = THREE.MathUtils.clamp;
const smooth01 = (t) => { t = clamp01(t); return t * t * (3 - 2 * t); };
const smoother01 = (t) => { t = clamp01(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const deg = (d) => d * PI / 180;

function mulberry32(seed){
  let a = seed >>> 0;
  return function(){
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* --- geometry accounting: every emitted part is recorded ---------------------------- */
const PART_LOG = [];
function logPart(name, geometry){
  const tris = geometry.index ? geometry.index.count / 3 : geometry.attributes.position.count / 3;
  PART_LOG.push({ part: name, tris: Math.round(tris), verts: geometry.attributes.position.count });
  return geometry;
}

/* --- 1D / 2D interpolation --------------------------------------------------------- */

/** Monotone-ish Catmull-Rom through 2D control points, resampled to `count` points. */
function spline2(points, count, { closed = false, tension = 0.5 } = {}){
  const pts = points.map(p => (p.isVector2 ? p.clone() : V2(p[0], p[1])));
  const n = pts.length;
  const at = (i) => closed ? pts[((i % n) + n) % n] : pts[clamp(i, 0, n - 1)];
  const out = [];
  const spans = closed ? n : n - 1;
  for (let s = 0; s < count; s++){
    const g = (s / (closed ? count : count - 1)) * spans;
    const i = Math.min(Math.floor(g), spans - 1);
    const t = g - i;
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    const t2 = t * t, t3 = t2 * t;
    const m1x = tension * (p2.x - p0.x), m1y = tension * (p2.y - p0.y);
    const m2x = tension * (p3.x - p1.x), m2y = tension * (p3.y - p1.y);
    out.push(V2(
      (2*t3 - 3*t2 + 1) * p1.x + (t3 - 2*t2 + t) * m1x + (-2*t3 + 3*t2) * p2.x + (t3 - t2) * m2x,
      (2*t3 - 3*t2 + 1) * p1.y + (t3 - 2*t2 + t) * m1y + (-2*t3 + 3*t2) * p2.y + (t3 - t2) * m2y,
    ));
  }
  return out;
}

/**
 * Shape-preserving monotone cubic (Fritsch-Carlson) through (x,y) knots.
 * This must be C1: an ease-per-segment curve has zero slope at every knot, which prints
 * a visible ripple onto a lofted body — the surface reads as a stack of terraces under
 * grazing studio light.  Monotone tangents keep it smooth AND overshoot-free, so a
 * knot never bulges the panel between it and its neighbour.
 */
function curve1(knots){
  const k = knots.slice().sort((a, b) => a[0] - b[0]);
  const n = k.length;
  if (n === 1) return () => k[0][1];
  const d = new Array(n - 1), m = new Array(n);
  for (let i = 0; i < n - 1; i++) d[i] = (k[i+1][1] - k[i][1]) / (k[i+1][0] - k[i][0]);
  m[0] = d[0]; m[n-1] = d[n-2];
  for (let i = 1; i < n - 1; i++) m[i] = (d[i-1] * d[i] <= 0) ? 0 : (d[i-1] + d[i]) * 0.5;
  for (let i = 0; i < n - 1; i++){
    if (d[i] === 0){ m[i] = 0; m[i+1] = 0; continue; }
    const a = m[i] / d[i], b = m[i+1] / d[i], s = a*a + b*b;
    if (s > 9){ const f = 3 / Math.sqrt(s); m[i] = f * a * d[i]; m[i+1] = f * b * d[i]; }
  }
  return function(x){
    if (x <= k[0][0]) return k[0][1];
    if (x >= k[n-1][0]) return k[n-1][1];
    let i = 0; while (i < n - 2 && x > k[i+1][0]) i++;
    const h = k[i+1][0] - k[i][0], t = (x - k[i][0]) / h;
    const t2 = t * t, t3 = t2 * t;
    return (2*t3 - 3*t2 + 1) * k[i][1] + (t3 - 2*t2 + t) * h * m[i]
         + (-2*t3 + 3*t2) * k[i+1][1] + (t3 - t2) * h * m[i+1];
  };
}

/* --- core compiler: sampled row grid ----------------------------------------------- */
/**
 * rows[r][c] -> Vector3.  Emits an explicit seam column when closeU.
 * Geometric normals from central differences; pole fallback from row centroids.
 * `flip` reverses BOTH normal direction and index winding.
 */
function gridGeometry(rows, { closeU = true, flip = false, vRow = null, uRow = null, uScale = 1, uOffset = 0 } = {}){
  const R = rows.length, C = rows[0].length;
  const EC = closeU ? C + 1 : C;
  const positions = new Float32Array(R * EC * 3);
  const normals   = new Float32Array(R * EC * 3);
  const uvs       = new Float32Array(R * EC * 2);
  const wrap = (c) => ((c % C) + C) % C;
  const P = (r, c) => rows[clamp(r, 0, R - 1)][closeU ? wrap(c) : clamp(c, 0, C - 1)];

  const dU = V3(), dV = V3(), nrm = V3();
  for (let r = 0; r < R; r++){
    for (let c = 0; c < EC; c++){
      const p = P(r, c), v = r * EC + c;
      positions[v*3] = p.x; positions[v*3+1] = p.y; positions[v*3+2] = p.z;
      dU.subVectors(P(r, c + 1), P(r, c - 1));
      dV.subVectors(P(Math.min(R - 1, r + 1), c), P(Math.max(0, r - 1), c));
      nrm.crossVectors(dU, dV);
      if (nrm.lengthSq() < 1e-14){
        const a = V3(), b = V3();
        const pr = Math.max(0, r - 1), nr = Math.min(R - 1, r + 1);
        for (const q of rows[pr]) a.add(q); a.divideScalar(C);
        for (const q of rows[nr]) b.add(q); b.divideScalar(C);
        nrm.subVectors(a, b);
        if (nrm.lengthSq() < 1e-14) nrm.set(0, 1, 0);
      }
      nrm.normalize(); if (flip) nrm.negate();
      normals[v*3] = nrm.x; normals[v*3+1] = nrm.y; normals[v*3+2] = nrm.z;
      uvs[v*2]   = uOffset + (uRow ? uRow[Math.min(c, uRow.length - 1)] : c / (EC - 1)) * uScale;
      uvs[v*2+1] = vRow ? vRow[r] : r / (R - 1);
    }
  }
  const idx = [];
  for (let r = 0; r < R - 1; r++){
    for (let c = 0; c < EC - 1; c++){
      const a = r * EC + c, b = a + 1, cc = a + EC, d = cc + 1;
      if (flip) idx.push(a, cc, b, b, cc, d);
      else      idx.push(a, b, cc, b, d, cc);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  g.setAttribute('normal',   new THREE.BufferAttribute(normals, 3));
  g.setAttribute('uv',       new THREE.BufferAttribute(uvs, 2));
  g.setIndex(idx);
  g.computeBoundingSphere();
  return g;
}

/** Longitudinal v from real accumulated centreline distance, so UV density is
 *  independent of output ring count. */
function distanceV(rows){
  const v = [0];
  const c0 = V3(), c1 = V3();
  const centroid = (row, out) => { out.set(0,0,0); for (const p of row) out.add(p); return out.divideScalar(row.length); };
  centroid(rows[0], c0);
  let acc = 0;
  for (let i = 1; i < rows.length; i++){
    centroid(rows[i], c1);
    acc += c0.distanceTo(c1);
    v.push(acc);
    c0.copy(c1);
  }
  const inv = 1 / (acc || 1);
  return v.map(x => x * inv);
}

/* --- closed-loop lofting ------------------------------------------------------------ */

/**
 * Loft a stack of closed 3D loops (all with equal point counts).
 * `capStart` / `capEnd` add contracted rounded terminals instead of hard flat caps.
 */
function loftLoops(loops, { flip = false, capStart = false, capEnd = false, capSegs = 4, capBulge = 0.5, useDistanceV = true } = {}){
  let rows = loops;
  const cap = (loop, dir, bulgeScale) => {
    const c = V3(); for (const p of loop) c.add(p); c.divideScalar(loop.length);
    const nrm = V3();
    { // loop plane normal via Newell
      for (let i = 0; i < loop.length; i++){
        const a = loop[i], b = loop[(i + 1) % loop.length];
        nrm.x += (a.y - b.y) * (a.z + b.z);
        nrm.y += (a.z - b.z) * (a.x + b.x);
        nrm.z += (a.x - b.x) * (a.y + b.y);
      }
      nrm.normalize().multiplyScalar(dir);
    }
    let radius = 0; for (const p of loop) radius = Math.max(radius, p.distanceTo(c));
    const out = [];
    for (let s = 1; s <= capSegs; s++){
      const a = (s / capSegs) * PI * 0.5;
      const shrink = Math.cos(a), push = Math.sin(a) * radius * bulgeScale;
      out.push(loop.map(p => V3().copy(c).addScaledVector(V3().subVectors(p, c), shrink).addScaledVector(nrm, push)));
    }
    return out;
  };
  if (capStart) rows = [...cap(loops[0], -1, capBulge).reverse(), ...rows];
  if (capEnd)   rows = [...rows, ...cap(loops[loops.length - 1], 1, capBulge)];
  return gridGeometry(rows, { closeU: true, flip, vRow: useDistanceV ? distanceV(rows) : null });
}

/* --- parallel-transport sweep of an arbitrary section ------------------------------- */
function transportFrames(points){
  const n = points.length, tangents = [], normals = [], binormals = [];
  for (let i = 0; i < n; i++){
    const a = points[Math.max(0, i - 1)], b = points[Math.min(n - 1, i + 1)];
    const t = V3().subVectors(b, a);
    if (t.lengthSq() < 1e-16) t.copy(tangents[i - 1] || V3(0,0,1));
    tangents.push(t.normalize());
  }
  let nrm = Math.abs(tangents[0].y) < 0.94 ? V3(0,1,0) : V3(1,0,0);
  nrm = V3().crossVectors(tangents[0], V3().crossVectors(nrm, tangents[0])).normalize();
  for (let i = 0; i < n; i++){
    if (i > 0){
      const axis = V3().crossVectors(tangents[i-1], tangents[i]);
      if (axis.length() > 1e-7){
        axis.normalize();
        nrm = nrm.clone().applyAxisAngle(axis, Math.acos(clamp(tangents[i-1].dot(tangents[i]), -1, 1)));
      }
    }
    normals.push(nrm.clone());
    binormals.push(V3().crossVectors(tangents[i], nrm).normalize());
  }
  return { tangents, normals, binormals };
}

/**
 * Sweep a 2D section (function of t -> array of Vector2 in the frame's normal/binormal
 * plane) along a 3D path with parallel-transport frames.
 */
function sweepSection(path, sectionAt, { flip = false, capStart = false, capEnd = false, capSegs = 4, roll = null } = {}){
  const F = transportFrames(path);
  const loops = path.map((p, i) => {
    const t = i / (path.length - 1);
    const sec = sectionAt(t, i);
    let N = F.normals[i], B = F.binormals[i];
    if (roll){
      const a = roll(t);
      const ca = Math.cos(a), sa = Math.sin(a);
      const n2 = V3().addScaledVector(N, ca).addScaledVector(B, sa);
      const b2 = V3().addScaledVector(N, -sa).addScaledVector(B, ca);
      N = n2; B = b2;
    }
    return sec.map(s => V3().copy(p).addScaledVector(N, s.x).addScaledVector(B, s.y));
  });
  return loftLoops(loops, { flip, capStart, capEnd, capSegs });
}

function sweepTube(path, radiusAt, segs = 16, opts = {}){
  const rf = typeof radiusAt === 'number' ? () => radiusAt : radiusAt;
  const circle = (r) => { const o = []; for (let i = 0; i < segs; i++){ const a = i / segs * TAU; o.push(V2(Math.cos(a) * r, Math.sin(a) * r)); } return o; };
  return sweepSection(path, (t) => circle(Math.max(rf(t), 1e-4)), opts);
}

/** Rounded-rect / squircle section helper (width, height, corner exponent). */
function squircle(halfW, halfH, exp = 3.2, segs = 28){
  const o = [];
  for (let i = 0; i < segs; i++){
    const a = i / segs * TAU;
    const ca = Math.cos(a), sa = Math.sin(a);
    o.push(V2(Math.sign(ca) * Math.pow(Math.abs(ca), 2 / exp) * halfW,
              Math.sign(sa) * Math.pow(Math.abs(sa), 2 / exp) * halfH));
  }
  return o;
}

/* --- airfoils ----------------------------------------------------------------------- */
/**
 * NACA-style section with independent thickness, camber, camber position, blunt trailing
 * edge and leading-edge droop.  Returns a CLOSED loop of Vector2 in (chord, thickness)
 * with the leading edge at (0,0) and trailing edge at (1,0).  Cosine spacing packs
 * resolution into the leading edge where curvature is highest.
 */
function airfoilLoop(n, { thick = 0.11, camber = 0.06, camberPos = 0.4, teThick = 0.004, leRadius = 1 } = {}){
  const half = Math.max(6, n >> 1);
  const xs = [];
  for (let i = 0; i <= half; i++) xs.push(0.5 - 0.5 * Math.cos(PI * i / half));
  const yt = (x) => 5 * thick * (0.2969 * Math.sqrt(x) * leRadius - 0.1260 * x - 0.3516 * x*x + 0.2843 * x*x*x - 0.1015 * x*x*x*x)
                    + teThick * 0.5 * x;
  const yc = (x) => {
    const m = camber, p = clamp(camberPos, 0.05, 0.95);
    return x < p ? m / (p*p) * (2*p*x - x*x) : m / ((1-p)*(1-p)) * ((1 - 2*p) + 2*p*x - x*x);
  };
  const dyc = (x) => {
    const m = camber, p = clamp(camberPos, 0.05, 0.95);
    return x < p ? 2*m / (p*p) * (p - x) : 2*m / ((1-p)*(1-p)) * (p - x);
  };
  const up = [], lo = [];
  for (const x of xs){
    const th = Math.atan(dyc(x)), t = yt(x), c = yc(x);
    up.push(V2(x - t * Math.sin(th), c + t * Math.cos(th)));
    lo.push(V2(x + t * Math.sin(th), c - t * Math.cos(th)));
  }
  // closed loop: upper LE->TE, blunt TE edge, lower TE->LE (LE pole shared once)
  return [...up, ...lo.slice(1).reverse()];
}

/**
 * Loft an airfoil across spanwise stations.  Every station owns chord, thickness,
 * camber, incidence, dihedral and a 3D leading-edge anchor — the real parameters an
 * aerodynamicist works in, not a scaled box.
 */
function wingLoft(stations, { sectionPoints = 64, roundTips = false, flip = false } = {}){
  const loops = stations.map(st => {
    const loop = airfoilLoop(sectionPoints, st.section || {});
    const inc  = st.incidence || 0;
    const ci = Math.cos(inc), si = Math.sin(inc);
    const dih = st.dihedral || 0;
    const cd = Math.cos(dih), sd = Math.sin(dih);
    const chordDir = st.chordDir || V3(0, 0, -1);   // trailing direction
    const upDir    = st.upDir    || V3(0, 1, 0);
    const spanDir  = st.spanDir  || V3(1, 0, 0);
    return loop.map(p => {
      // rotate section about the leading edge by the incidence angle
      const cx =  p.x * ci + p.y * si;
      const cy = -p.x * si + p.y * ci;
      const x  = cx * st.chord, y = cy * st.chord;
      // dihedral tips the section out of the chord plane about the chord axis
      const yy = y * cd, sx = y * sd;
      return V3().copy(st.le)
        .addScaledVector(chordDir, x)
        .addScaledVector(upDir, yy)
        .addScaledVector(spanDir, sx);
    });
  });
  // roundTips: true | false | [innerEnd, outerEnd].  An element that meets the car's
  // centreline must NOT be capped there, or the mirrored half shows a seam.
  const want = Array.isArray(roundTips) ? roundTips : [roundTips, roundTips];
  const tip = (loop, dir) => {
    const c = V3(); for (const p of loop) c.add(p); c.divideScalar(loop.length);
    const out = [];
    for (let s = 1; s <= 3; s++){
      const a = (s / 3) * PI * 0.5;
      out.push(loop.map(p => V3().copy(c).addScaledVector(V3().subVectors(p, c), Math.cos(a))
        .addScaledVector(dir, Math.sin(a) * 0.006)));
    }
    return out;
  };
  if (want[1]){
    const d1 = V3().subVectors(loops[loops.length-1][0], loops[loops.length-2][0]).normalize();
    loops.push(...tip(loops[loops.length-1], d1));
  }
  if (want[0]){
    const d0 = V3().subVectors(loops[0][0], loops[1][0]).normalize();
    loops.unshift(...tip(loops[0], d0).reverse());
  }
  return loftLoops(loops, { flip, useDistanceV: true });
}

/* --- authored 2D outlines extruded into plates -------------------------------------- */
/**
 * A plate is an authored outline (endplate, fence, strake, fin) extruded with a bevel,
 * then optionally deformed by a 3D warp.  Outline coordinates are real metres in the
 * plate's own (u,v) frame; `warp(u,v,w)` returns the final world-space position, which
 * is how curled endplates and twisted fences get their shape.
 */
function plate(outline, { thickness = 0.005, bevel = 0.0022, bevelSegs = 2, curveSegs = 1, warp = null, holes = [] } = {}){
  const shape = new THREE.Shape(outline.map(p => (p.isVector2 ? p : V2(p[0], p[1]))));
  for (const h of holes) shape.holes.push(new THREE.Path(h.map(p => (p.isVector2 ? p : V2(p[0], p[1])))));
  const g = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(thickness - bevel * 2, 1e-4),
    bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel, bevelOffset: 0,
    bevelSegments: bevelSegs, curveSegments: curveSegs, steps: 1,
  });
  g.translate(0, 0, -thickness * 0.5 + bevel);
  if (warp){
    const pos = g.attributes.position;
    const p = V3();
    for (let i = 0; i < pos.count; i++){
      p.fromBufferAttribute(pos, i);
      const q = warp(p.x, p.y, p.z);
      pos.setXYZ(i, q.x, q.y, q.z);
    }
    pos.needsUpdate = true;
  }
  g.computeVertexNormals();
  g.computeBoundingSphere();
  return g;
}

/* --- lathes & revolutions ----------------------------------------------------------- */
/** Revolve an (radius, axisPos) profile about +X (wheels, hubs, discs, nuts). */
function latheX(profile, segs = 64, { flip = false, phase = 0 } = {}){
  const rows = profile.map(p => {
    const loop = [];
    for (let i = 0; i < segs; i++){
      const a = phase + i / segs * TAU;
      loop.push(V3(p.y, Math.cos(a) * Math.max(p.x, 1e-5), Math.sin(a) * Math.max(p.x, 1e-5)));
    }
    return loop;
  });
  const vRow = [0]; let acc = 0;
  for (let i = 1; i < profile.length; i++){
    acc += Math.hypot(profile[i].x - profile[i-1].x, profile[i].y - profile[i-1].y);
    vRow.push(acc);
  }
  for (let i = 0; i < vRow.length; i++) vRow[i] /= acc || 1;
  return gridGeometry(rows, { closeU: true, flip, vRow });
}

/** Revolve an (radius, y) profile about +Y. */
function latheY(profile, segs = 48, { flip = false } = {}){
  const rows = profile.map(p => {
    const loop = [];
    for (let i = 0; i < segs; i++){
      const a = i / segs * TAU;
      loop.push(V3(Math.cos(a) * Math.max(p.x, 1e-5), p.y, Math.sin(a) * Math.max(p.x, 1e-5)));
    }
    return loop;
  });
  return gridGeometry(rows, { closeU: true, flip, vRow: null });
}

/* --- transforms & assembly ---------------------------------------------------------- */
function clone(g){ return g.clone(); }
function xform(g, fn){
  const pos = g.attributes.position, nor = g.attributes.normal;
  const p = V3(), n = V3();
  for (let i = 0; i < pos.count; i++){
    p.fromBufferAttribute(pos, i);
    const q = fn(p.x, p.y, p.z, i);
    pos.setXYZ(i, q.x, q.y, q.z);
  }
  pos.needsUpdate = true;
  g.computeVertexNormals();
  return g;
}
function mirrorX(g){
  const out = g.clone();
  out.scale(-1, 1, 1);
  const idx = out.index;
  if (idx){ for (let i = 0; i < idx.count; i += 3){ const t = idx.getX(i); idx.setX(i, idx.getX(i+2)); idx.setX(i+2, t); } idx.needsUpdate = true; }
  const n = out.attributes.normal;
  for (let i = 0; i < n.count; i++) n.setX(i, -n.getX(i));
  n.needsUpdate = true;
  out.computeBoundingSphere();
  return out;
}
function merge(list){
  const clean = list.filter(Boolean);
  if (clean.length === 1) return clean[0];
  const out = THREE.BufferGeometryUtils
    ? THREE.BufferGeometryUtils.mergeGeometries(clean)
    : mergeManual(clean);
  return out;
}
function mergeManual(geos){
  let vTotal = 0, iTotal = 0;
  for (const g of geos){ vTotal += g.attributes.position.count; iTotal += g.index ? g.index.count : g.attributes.position.count; }
  const pos = new Float32Array(vTotal * 3), nor = new Float32Array(vTotal * 3), uvs = new Float32Array(vTotal * 2);
  const idx = vTotal > 65535 ? new Uint32Array(iTotal) : new Uint16Array(iTotal);
  let vo = 0, io = 0;
  for (const g of geos){
    const p = g.attributes.position, n = g.attributes.normal, u = g.attributes.uv;
    pos.set(p.array.subarray(0, p.count * 3), vo * 3);
    if (n) nor.set(n.array.subarray(0, n.count * 3), vo * 3);
    if (u) uvs.set(u.array.subarray(0, u.count * 2), vo * 2);
    if (g.index){ for (let i = 0; i < g.index.count; i++) idx[io++] = g.index.getX(i) + vo; }
    else { for (let i = 0; i < p.count; i++) idx[io++] = i + vo; }
    vo += p.count;
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  out.setAttribute('normal',   new THREE.BufferAttribute(nor, 3));
  out.setAttribute('uv',       new THREE.BufferAttribute(uvs, 2));
  out.setIndex(new THREE.BufferAttribute(idx, 1));
  out.computeBoundingSphere();
  return out;
}
/** Rigid placement without an extra Object3D per detail. */
function place(g, { pos = [0,0,0], rot = [0,0,0], scale = [1,1,1] } = {}){
  const m = new THREE.Matrix4().compose(
    new THREE.Vector3(...pos),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(...rot, 'XYZ')),
    new THREE.Vector3(...scale));
  const out = g.clone();
  out.applyMatrix4(m);
  return out;
}

export {
  TAU, PI, V2, V3, clamp01, lerp, clamp, smooth01, smoother01, deg,
  mulberry32, PART_LOG, logPart, spline2, curve1, gridGeometry, distanceV,
  loftLoops, transportFrames, sweepSection, sweepTube, squircle, airfoilLoop,
  wingLoft, plate, latheX, latheY, clone, xform, mirrorX, merge, mergeManual, place,
};
