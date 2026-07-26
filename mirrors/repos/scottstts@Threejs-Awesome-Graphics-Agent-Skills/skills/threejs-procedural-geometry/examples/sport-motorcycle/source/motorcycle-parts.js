import * as THREE from "three/webgpu";
import { texture, uv } from "three/tsl";

import { AX, D, DEG, forkPt, seg, steerPt } from "./design-contract.js";
import { M, PARTS, TAU, V2, V3, Writer, add, arcLengthV, catmull2, catmull3, circlePoly, clampf, ease, extrudePlate, extrudeRing, filletBox, gridNormals, instance, lerp, offsetPoly, orient, pair, panelShell, revolve, ringPoints, roundRect, secMove, section, smooth01, superSection, sweep, toRing, tube, write, xform } from "./mesh-kit.js";
import { MAT, canvas2d, canvasTexture, keep } from "./motorcycle-materials.js";

/* ============================================================================
   4. WHEELS · TYRES · BRAKES · FINAL DRIVE
   ----------------------------------------------------------------------------
   Wheel-local frame: +X is the axle, the wheel plane is Y/Z.  Everything here
   is generated from the tyre and rim dimensions in the contract, so changing
   180/55 to 190/50 moves the sprocket, chain line and hugger with it.
   ========================================================================== */

/* --- 4.1 rim shell -------------------------------------------------------
   Closed section: the tyre-side barrel out to the flange lips, back along the
   inner face.  Only the flange edge and the inner face are ever seen, but the
   section is closed so the lip silhouette is real geometry.                */
function rimSection(rimW, seatR) {
  const hw = rimW / 2;
  const lip = seatR + 0.0106, wellO = seatR - 0.0185, wellI = wellO - 0.0068;
  const p = [];
  const push = (u, r) => p.push(V2(r, u));         // (radius, axial) for revolve
  // tyre-side barrel, left flange -> right flange
  push(-hw - 0.0052, lip);
  push(-hw - 0.0022, lip - 0.0052);
  push(-hw + 0.0020, seatR + 0.0002);
  push(-hw + 0.0125, seatR - 0.0042);
  push(-hw + 0.0225, wellO + 0.0034);
  push(0, wellO);
  push(hw - 0.0225, wellO + 0.0034);
  push(hw - 0.0125, seatR - 0.0042);
  push(hw - 0.0020, seatR + 0.0002);
  push(hw + 0.0022, lip - 0.0052);
  push(hw + 0.0052, lip);
  // flange tip roll-over
  push(hw + 0.0072, lip - 0.0012);
  push(hw + 0.0076, lip - 0.0044);
  // inner face, right -> left
  push(hw + 0.0046, lip - 0.0098);
  push(hw - 0.0040, seatR - 0.0092);
  push(hw - 0.0170, wellI + 0.0040);
  push(hw - 0.0280, wellI);
  push(0, wellI - 0.0016);
  push(-hw + 0.0280, wellI);
  push(-hw + 0.0170, wellI + 0.0040);
  push(-hw + 0.0040, seatR - 0.0092);
  push(-hw - 0.0046, lip - 0.0098);
  push(-hw - 0.0076, lip - 0.0044);
  push(-hw - 0.0072, lip - 0.0012);
  return p;
}

/* --- 4.2 three-spoke split wheel ----------------------------------------
   Three roots leave the hub and fork into six rim arms — the split-spoke
   pattern this machine wears.  Each arm is a lofted rounded-rectangle section
   whose tangential width, axial depth and dish all vary along the radius.  */
function spokeArm({ r0, r1, a0, a1, w0, w1, d0, d1, dish0, dish1, rings, segs, bow = 0 }) {
  const path = [], secs = [];
  for (let i = 0; i < rings; i++) {
    const t = i / (rings - 1);
    const te = smooth01(t);
    const r = lerp(r0, r1, t);
    const a = lerp(a0, a1, te) + bow * Math.sin(Math.PI * t) * 0.4;
    const x = lerp(dish0, dish1, te);
    path.push(V3(x, Math.sin(a) * r, Math.cos(a) * r));
    // section is authored in (tangential, axial) and rotated into the wheel
    const halfW = lerp(w0, w1, ease(t, 0.85));
    const halfD = lerp(d0, d1, ease(t, 0.7));
    secs.push(roundRect(halfD, halfW, Math.min(halfD, halfW) * 0.55, segs));
  }
  // frames: profile x -> axle direction, profile y -> tangential
  const rows = path.map((P, i) => {
    const radial = V3(0, P.y, P.z).normalize();
    const tang = V3().crossVectors(V3(1, 0, 0), radial).normalize();
    return secs[i].map((s) => V3().copy(P).addScaledVector(V3(1, 0, 0), s.x).addScaledVector(tang, s.y));
  });
  return rows;
}

function makeWheel(spec) {
  const { rimW, seatR, hubHalf, hubR, boreR, dishOut = 0, armDepth = 1, name = "wheel" } = spec;
  const g = new THREE.Group();
  g.name = name;
  const S = seg(64);

  /* rim shell */
  add(g, revolve(rimSection(rimW, seatR), { axis: "x", segments: S }), MAT.wheelBlack, name + ".rim");

  /* Lime pinstripe: applied to the outward-facing flange wall, the only band
     of rim the tyre sidewall does not cover, which is the only place a rim
     stripe reads.  Landmarks come from the same section constants.        */
  const stripe = (side) => {
    const hw = rimW / 2, lip = seatR + 0.0106;
    const a = V2(lip - 0.0102, side * (hw + 0.0043));
    const b = V2(lip - 0.0158, side * (hw - 0.0012));
    const n = V2(b.y - a.y, -(b.x - a.x)).normalize().multiplyScalar(side * 0.0004);
    return revolve([
      V2(a.x + n.x, a.y + n.y), V2(b.x + n.x, b.y + n.y),
    ], { axis: "x", segments: S, flip: side < 0 });
  };
  add(g, stripe(1), MAT.lime, name + ".pinstripe.R", { cast: false });
  add(g, stripe(-1), MAT.lime, name + ".pinstripe.L", { cast: false });

  /* hub barrel + bearing faces */
  const hubProf = [
    V2(boreR, -hubHalf), V2(hubR * 0.72, -hubHalf), V2(hubR * 0.86, -hubHalf + 0.008),
    V2(hubR, -hubHalf + 0.020), V2(hubR * 1.02, -hubHalf * 0.35),
    V2(hubR * 1.02, hubHalf * 0.35), V2(hubR, hubHalf - 0.020),
    V2(hubR * 0.86, hubHalf - 0.008), V2(hubR * 0.72, hubHalf), V2(boreR, hubHalf),
    V2(boreR, hubHalf - 0.006), V2(hubR * 0.60, hubHalf - 0.012),
    V2(hubR * 0.60, -hubHalf + 0.012), V2(boreR, -hubHalf + 0.006),
  ];
  add(g, revolve(hubProf, { axis: "x", segments: seg(40) }), MAT.wheelBlack, name + ".hub");
  // bearing seals
  for (const s of [-1, 1]) {
    const y = s * (hubHalf - 0.004);
    add(g, revolve([V2(boreR + 0.0005, y), V2(hubR * 0.62, y), V2(hubR * 0.62, y + s * 0.004), V2(boreR + 0.0005, y + s * 0.004)],
      { axis: "x", segments: seg(28) }), MAT.rubber, name + ".seal" + s, { cast: false });
  }

  /* Spokes: three roots, six arms.  Sections are deeper across the axle than
     they are wide, so the wheel reads as a slim blade from the side and a
     stiff web from the front — the way a cast sport wheel actually looks. */
  const spokes = new Writer();
  const rimInner = seatR - 0.0253;
  for (let k = 0; k < 3; k++) {
    const base = (k / 3) * TAU + Math.PI * 0.5;
    // root: hub -> split point
    spokes.grid(spokeArm({
      r0: hubR * 0.92, r1: 0.109, a0: base, a1: base, w0: 0.0300, w1: 0.0212,
      d0: 0.0250 * armDepth, d1: 0.0225 * armDepth,
      dish0: dishOut * 0.15, dish1: dishOut * 0.60, rings: seg(9), segs: seg(22),
    }), { closeU: true });
    // two arms to the rim
    for (const s of [-1, 1]) {
      spokes.grid(spokeArm({
        r0: 0.1045, r1: rimInner + 0.005, a0: base + s * 0.050, a1: base + s * 0.330,
        w0: 0.0158, w1: 0.0124, d0: 0.0232 * armDepth, d1: 0.0176 * armDepth,
        dish0: dishOut * 0.62, dish1: dishOut * 0.40, rings: seg(11), segs: seg(20),
        bow: s * 0.05,
      }), { closeU: true });
    }
  }
  add(g, spokes.geometry(), MAT.wheelBlack, name + ".spokes");

  /* valve stem */
  const va = 0.9;
  const vp = V3(rimW * 0.18, Math.sin(va) * (seatR - 0.024), Math.cos(va) * (seatR - 0.024));
  const vdir = V3(0, Math.sin(va), Math.cos(va));
  add(g, tube([vp.clone().addScaledVector(vdir, -0.004), vp.clone().addScaledVector(vdir, 0.017),
    vp.clone().addScaledVector(vdir, 0.030)], (t) => lerp(0.0042, 0.0034, t), seg(12)),
    MAT.boltDark, name + ".valve");

  return g;
}

/* --- 4.3 tyre with generated tread --------------------------------------
   The tread grooves are geometry, not a normal map: the section radius is
   displaced by a sweeping groove field so the shoulder blocks break the
   silhouette and catch the rim light the way moulded rubber does.         */
function tyreProfile(sectionW, outerR, seatR, rimW) {
  const hw = sectionW / 2, hb = rimW / 2;
  const c = [
    // the bead starts level with the rim flange tip so the tyre wraps the lip
    // instead of leaving a bare ring of rim above the seat
    [hb + 0.0058, seatR + 0.0098],
    [hb + 0.0112, seatR + 0.0232],
    [hw * 0.93, seatR + 0.0400],
    [hw, (seatR + outerR) * 0.5 + 0.0065],
    [hw * 0.985, outerR - 0.0245],
    [hw * 0.905, outerR - 0.0105],
    [hw * 0.760, outerR - 0.0032],
    [hw * 0.520, outerR - 0.0004],
    [hw * 0.220, outerR + 0.0002],
    [0, outerR + 0.0003],
  ];
  const half = catmull2(c, 26);                   // bead -> crown
  // mirror into one monotonic run: -bead ... crown ... +bead.  Emitting the
  // crown first folds the loft back on itself and destroys the tread field.
  const full = [];
  for (let i = 0; i < half.length; i++) full.push(V2(half[i].y, -half[i].x));
  for (let i = half.length - 2; i >= 0; i--) full.push(V2(half[i].y, half[i].x));
  return full;                                    // (radius, axial)
}
function makeTyre({ sectionW, outerR, seatR, rimW, name }) {
  const prof = tyreProfile(sectionW, outerR, seatR, rimW);
  // the groove field is the reason for this segment count: an 8 mm slot needs
  // ~3 mm sampling around a 1.9 m circumference to survive as geometry
  const S = seg(420);
  const R = prof.length;
  const vRow = arcLengthV(prof);
  // lateral position across the crown, 0 at centre -> 1 at shoulder
  const crownAt = prof.map((p) => clampf(Math.abs(p.y) / (sectionW * 0.5), 0, 1));
  const onTread = prof.map((p) => clampf((p.x - (outerR - 0.030)) / 0.028, 0, 1));

  const rows = [];
  for (let r = 0; r < R; r++) {
    const row = [];
    const side = Math.sign(prof[r].y) || 1;
    const v = crownAt[r], tread = onTread[r];
    for (let c = 0; c < S; c++) {
      const a = (c / S) * TAU;
      const turn = a / TAU;
      let cut = 0;
      if (tread > 0.01) {
        // seven groove sets per side per revolution, swept back toward the
        // shoulder and phase-offset side to side
        const sweep = 0.055 + 0.44 * Math.pow(v, 1.25);
        const phase = turn * 7 + side * sweep + (side > 0 ? 0 : 0.5);
        const d = Math.abs(fractf(phase) - 0.5);
        const w = 0.038 + 0.020 * v;
        const inBand = smooth01(clampf((0.88 - v) / 0.10, 0, 1)) * smooth01(clampf((v - 0.030) / 0.07, 0, 1));
        cut = Math.pow(Math.max(0, 1 - d / w), 0.55) * inBand * tread;
        // central circumferential rain groove
        if (v < 0.050) cut = Math.max(cut, smooth01(clampf((0.050 - v) / 0.028, 0, 1)) * 0.95);
      }
      const depth = 0.0052 * smooth01(clampf(cut, 0, 1));
      const rr = prof[r].x - depth;
      row.push(V3(prof[r].y, Math.sin(a) * rr, Math.cos(a) * rr));
    }
    rows.push(row);
  }
  // rows run bead -> bead (+X) and columns run round the carcass, which winds
  // the surface inward; flip so the outward face is the one that survives
  // culling.  Left unflipped you see through to the far wall's interior.
  const geo = write((w) => w.grid(rows, {
    closeU: true, flip: true,
    uvFn: (r, c, R2, C2) => [c / (C2 - 1), vRow[r]],
  }));
  const m = new THREE.Mesh(geo, MAT.tyre);
  m.castShadow = true; m.receiveShadow = true; m.name = name;
  m.userData.slot = "tyre";
  PARTS.push({ name, tris: geo.index.count / 3, slot: "tyre" });
  return m;
}
const fractf = (x) => x - Math.floor(x);

/* --- 4.4 petal brake disc ------------------------------------------------ */
function petalPoly(R, lobes, depth, n) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU;
    const t = fractf(a * lobes / TAU);
    const notch = Math.pow(0.5 + 0.5 * Math.cos(t * TAU), 2.6);
    out.push(V2(Math.cos(a) * (R - depth * notch), Math.sin(a) * (R - depth * notch)));
  }
  return out;
}
function rotorAlphaFor(outerR, innerR, holeR, rows) {
  const W = 1024, H = 160;
  const [c, x] = canvas2d(W, H);
  x.fillStyle = "#fff"; x.fillRect(0, 0, W, H);
  x.fillStyle = "#000";
  const span = outerR - innerR;
  for (const row of rows) {
    const rAt = lerp(outerR, innerR, row.v);
    const rx = (holeR / (TAU * rAt)) * W;
    const ry = (holeR / span) * H;
    for (let i = 0; i < row.n; i++) {
      const u = ((i + (row.off || 0)) / row.n) * W;
      x.save(); x.translate(u, row.v * H); x.scale(rx, ry);
      x.beginPath(); x.arc(0, 0, 1, 0, TAU); x.fill(); x.restore();
      if (u < rx * 2) { x.save(); x.translate(u + W, row.v * H); x.scale(rx, ry); x.beginPath(); x.arc(0, 0, 1, 0, TAU); x.fill(); x.restore(); }
    }
  }
  // no mipmaps: a 4 mm hole is only a few texels wide and alphaTest would
  // dissolve the whole drilling pattern at the first minification level
  const t = canvasTexture(c, { aniso: 16 });
  t.generateMipmaps = false;
  t.minFilter = THREE.LinearFilter;
  t.needsUpdate = true;
  return t;
}
function makeRotor({ outerR, innerR, thick, hubR, boltR, name, side = 1, carrierArms = 5 }) {
  const g = new THREE.Group(); g.name = name;
  const n = seg(200);
  const outer = petalPoly(outerR, 12, outerR * 0.062, n);
  const inner = circlePoly(innerR, n);

  /* friction faces carry the drilled pattern (angle, radial) */
  const faces = new Writer();
  const oR = toRing(outer, thick / 2, "x"), oL = toRing(outer, -thick / 2, "x");
  const iR = toRing(inner, thick / 2, "x"), iL = toRing(inner, -thick / 2, "x");
  faces.band(oR, iR, { closed: true, flip: false });
  faces.band(oL, iL, { closed: true, flip: true });
  const alpha = rotorAlphaFor(outerR, innerR, 0.0022, [
    { v: 0.30, n: 36 }, { v: 0.62, n: 36, off: 0.5 },
  ]);
  const faceMat = MAT.rotorSteel.clone();
  faceMat.userData.slot = "rotorSteel";
  faceMat.opacityNode = texture(alpha, uv()).r;
  faceMat.alphaTest = 0.5;
  faceMat.side = THREE.DoubleSide;
  add(g, faces.geometry(), faceMat, name + ".face");

  /* petal edge + bore edge stay solid so the silhouette is real */
  const edges = new Writer();
  edges.band(oL, oR, { closed: true, flip: false });
  edges.band(iR, iL, { closed: true, flip: false });
  add(g, edges.geometry(), MAT.rotorSteel, name + ".edge");

  /* floating carrier: arms from the hub flange out to the bobbin ring */
  const carrier = new Writer();
  const cOuter = innerR + 0.004;
  revolve([V2(hubR, -thick * 0.9), V2(hubR, thick * 0.9), V2(hubR + 0.010, thick * 1.5),
    V2(hubR + 0.010, -thick * 1.5)], { axis: "x", segments: seg(44), w: carrier });
  for (let i = 0; i < carrierArms; i++) {
    const a = (i / carrierArms) * TAU + 0.3;
    const rows = spokeArm({
      r0: hubR + 0.004, r1: cOuter, a0: a, a1: a + 0.16, w0: 0.0155, w1: 0.0092,
      d0: thick * 1.45, d1: thick * 1.15, dish0: 0, dish1: 0, rings: seg(7), segs: seg(14),
    });
    carrier.grid(rows, { closeU: true });
  }
  // bobbin ring
  revolve([V2(cOuter - 0.006, -thick * 1.1), V2(cOuter + 0.003, -thick * 1.1),
    V2(cOuter + 0.003, thick * 1.1), V2(cOuter - 0.006, thick * 1.1)],
    { axis: "x", segments: seg(90), w: carrier });
  add(g, carrier.geometry(), MAT.rotorCarrier, name + ".carrier");

  /* floating buttons */
  const bob = revolve([V2(0, -thick * 1.5), V2(0.0042, -thick * 1.5), V2(0.0052, -thick * 0.9),
    V2(0.0052, thick * 0.9), V2(0.0042, thick * 1.5), V2(0, thick * 1.5)],
    { axis: "x", segments: seg(12) });
  const mats = [];
  for (let i = 0; i < 10; i++) {
    const a = (i / 10) * TAU + 0.15;
    mats.push(M.t(0, Math.sin(a) * (innerR + 0.0015), Math.cos(a) * (innerR + 0.0015)));
  }
  instance(g, bob, MAT.bolt, mats, name + ".buttons");

  /* mounting bolts into the wheel hub */
  const boltG = hexBolt(0.0052, 0.0042);
  const bm = [];
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * TAU + 0.6;
    bm.push(M.c(M.t(side * 0.004, Math.sin(a) * boltR, Math.cos(a) * boltR), M.rz(Math.PI / 2)));
  }
  instance(g, boltG, MAT.bolt, bm, name + ".bolts");
  return g;
}

/* --- 4.5 fasteners ------------------------------------------------------- */
/* Fasteners are emitted as solids and then orientation-checked.  The hex head
   was previously hand-flipped, which left every hex bolt on the machine
   inside-out — visible as partially culled slivers wherever one sat proud of
   its parent (sprocket carrier, clutch cover, rotor faces).             */
function hexBolt(r, h, flange = true) {
  const w = new Writer();
  const hex = circlePoly(r, 6, Math.PI / 6);
  const hexTop = offsetPoly(hex, -r * 0.14);
  const rows = [
    toRing(hexTop, h, "y"), toRing(hex, h - r * 0.16, "y"), toRing(hex, 0, "y"),
  ];
  w.grid(rows, { closeU: true });
  w.fan(rows[0], false);
  if (flange) {
    revolve([V2(0, 0), V2(r * 1.32, 0), V2(r * 1.30, -r * 0.28), V2(0, -r * 0.30)],
      { axis: "y", segments: 14, w });
  } else {
    w.fan(rows[2], true);
  }
  return orient(w.geometry());
}
function socketBolt(r, h) {
  const w = new Writer();
  revolve([V2(0, h), V2(r * 0.62, h), V2(r * 0.62, h - r * 0.5), V2(r, h - r * 0.55),
    V2(r, 0), V2(r * 0.7, -h * 0.6), V2(0, -h * 0.6)], { axis: "y", segments: 18, w });
  return orient(w.geometry());
}

/* --- 4.6 final drive ----------------------------------------------------- */
function sprocketPoly(teeth, pitchR, n) {
  const tipR = pitchR + 0.0072, rootR = pitchR - 0.0060;
  const out = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU;
    const t = fractf(a * teeth / TAU);
    // trapezoidal tooth with a rounded tip and generous root radius
    const s = Math.abs(t - 0.5) * 2;                    // 0 at tooth centre
    let r;
    if (s < 0.42) r = lerp(tipR, tipR - 0.0016, ease(s / 0.42, 2));
    else if (s < 0.80) r = lerp(tipR - 0.0016, rootR, smooth01((s - 0.42) / 0.38));
    else r = rootR - 0.0004 * Math.sin((s - 0.80) / 0.20 * Math.PI);
    out.push(V2(Math.cos(a) * r, Math.sin(a) * r));
  }
  return out;
}
function makeSprocket({ teeth, pitchR, thick, boreR, name, mat }) {
  const n = seg(teeth * 6);
  const w = new Writer();
  extrudeRing(sprocketPoly(teeth, pitchR, n), circlePoly(pitchR * 0.44, seg(72)), thick,
    { axis: "x", bevel: 0.0009, w });
  /* Lightened web.  This was a flat ring laid at +/-thick/2 with separate rib
     bars floating on it: the ring landed on exactly the plane extrudeRing puts
     its faces on, so the two z-fought across the whole hub, and the loose ribs
     shaded as detached slivers.  It is now one closed revolved profile that
     steps down into the recess and back out, sharing only an edge with the
     tooth face — no coincident area, no separate parts.                  */
  const inner = pitchR * 0.44, outer = pitchR - 0.017;
  const lip = thick * 0.46, floorZ = thick * 0.24;
  revolve([
    V2(inner - 0.001, -lip), V2(inner + 0.005, -floorZ),
    V2(outer - 0.005, -floorZ), V2(outer, -lip),
    V2(outer, lip), V2(outer - 0.005, floorZ),
    V2(inner + 0.005, floorZ), V2(inner - 0.001, lip),
    V2(inner - 0.001, -lip),
  ], { axis: "x", segments: seg(72), w });
  const g = w.geometry();
  const mesh = new THREE.Mesh(g, mat || MAT.alloyMachined);
  mesh.castShadow = true; mesh.receiveShadow = true; mesh.name = name;
  mesh.userData.slot = "alloyMachined";
  PARTS.push({ name, tris: g.index.count / 3, slot: "alloyMachined" });
  return mesh;
}

/* chain: tangent construction between the two pitch circles, sagged bottom run */
function chainPath(cA, rA, cB, rB, sag) {
  const d = Math.hypot(cB[0] - cA[0], cB[1] - cA[1]);
  const al = Math.atan2(cB[1] - cA[1], cB[0] - cA[0]);
  const be = Math.asin(clampf((rB - rA) / d, -1, 1));
  const t1 = al + Math.PI / 2 + be, t2 = al - Math.PI / 2 - be;
  const P = (c, r, a) => V2(c[0] + Math.cos(a) * r, c[1] + Math.sin(a) * r);
  const pts = [];
  const run = (p0, p1, n, bow) => {
    for (let i = 0; i <= n; i++) {
      const t = i / n;
      const p = V2().lerpVectors(p0, p1, t);
      p.y -= bow * Math.sin(Math.PI * t);
      pts.push(p);
    }
  };
  const arc = (c, r, a0, a1, n) => {
    for (let i = 1; i < n; i++) pts.push(P(c, r, lerp(a0, a1, i / n)));
  };
  run(P(cA, rA, t1), P(cB, rB, t1), 26, 0);                       // top run
  arc(cB, rB, t1, t2 - TAU, seg(46));                             // around rear
  run(P(cB, rB, t2), P(cA, rA, t2), 26, sag);                     // bottom run, slack
  arc(cA, rA, t2, t1 - TAU, seg(20));                             // around front
  return pts;
}
function makeChain({ cA, rA, cB, rB, x, pitch, name }) {
  const g = new THREE.Group(); g.name = name;
  const raw = chainPath(cA, rA, cB, rB, 0.013);
  // resample to exact pitch spacing so link plates butt end to end
  const cum = [0];
  for (let i = 1; i < raw.length; i++) cum.push(cum[i - 1] + raw[i].distanceTo(raw[i - 1]));
  const total = cum[cum.length - 1] + raw[0].distanceTo(raw[raw.length - 1]);
  const links = Math.round(total / pitch);
  const step = total / links;
  const sampleAt = (s) => {
    s = ((s % total) + total) % total;
    let i = 1;
    while (i < cum.length && cum[i] < s) i++;
    if (i >= cum.length) return raw[raw.length - 1].clone().lerp(raw[0], (s - cum[cum.length - 1]) / Math.max(1e-6, total - cum[cum.length - 1]));
    const t = (s - cum[i - 1]) / Math.max(1e-6, cum[i] - cum[i - 1]);
    return V2().lerpVectors(raw[i - 1], raw[i], t);
  };
  const hw = D.chainW / 2;
  const plate = (() => {
    const w = new Writer();
    const shape = catmull2([
      [-pitch / 2, 0.0062], [-pitch * 0.18, 0.0080], [pitch * 0.18, 0.0080], [pitch / 2, 0.0062],
      [pitch / 2 + 0.0018, 0], [pitch / 2, -0.0062], [pitch * 0.18, -0.0080],
      [-pitch * 0.18, -0.0080], [-pitch / 2, -0.0062], [-pitch / 2 - 0.0018, 0],
    ], 30, true);
    extrudePlate(shape, 0.0022, { axis: "x", bevel: 0.0005, w });
    return w.geometry();
  })();
  const roller = revolve([V2(0.0035, -0.0038), V2(0.0052, -0.0038), V2(0.0052, 0.0038), V2(0.0035, 0.0038)],
    { axis: "x", segments: seg(14) });
  const pin = revolve([V2(0, -hw - 0.0012), V2(0.0022, -hw - 0.0012), V2(0.0022, hw + 0.0012), V2(0, hw + 0.0012)],
    { axis: "x", segments: seg(10), capStart: true, capEnd: true });

  const outer = [], innerP = [], rollers = [], pins = [];
  for (let i = 0; i < links; i++) {
    const s = i * step;
    const a = sampleAt(s - step * 0.5), b = sampleAt(s + step * 0.5);
    const mid = V2().addVectors(a, b).multiplyScalar(0.5);
    const ang = Math.atan2(b.y - a.y, b.x - a.x);
    // path is in the Z(fore/aft) - Y(up) plane; +x of the section maps to +Z
    const base = M.c(M.t(x, mid.y, mid.x), M.rx(-ang));
    const outerPlate = i % 2 === 0;
    const off = outerPlate ? hw : hw - 0.0026;
    (outerPlate ? outer : innerP).push(M.c(base.clone(), M.t(off, 0, 0)));
    (outerPlate ? outer : innerP).push(M.c(base.clone(), M.t(-off, 0, 0)));
    if (!outerPlate) rollers.push(base.clone());
    pins.push(M.c(M.t(x, b.y, b.x), M.rx(-ang)));
  }
  instance(g, plate, MAT.chain, outer, name + ".plateOuter");
  instance(g, plate, MAT.chainGold, innerP, name + ".plateInner");
  instance(g, roller, MAT.chain, rollers, name + ".rollers");
  instance(g, pin, MAT.bolt, pins, name + ".pins");
  return g;
}

/* ============================================================================
   5. CHASSIS · FORKS · SWINGARM · CONTROLS
   ----------------------------------------------------------------------------
   Steering geometry is the spine of this file: every front-end part is placed
   by forkPt()/steerPt() at a stated distance along the fork axis, so rake and
   triple-clamp offset propagate to the yokes, bars, calipers and fender
   without a single hand-placed transform.
   ========================================================================== */

/* revolve a profile about the axis joining two 3D points */
function revolveAlongPts(w, origin, dir, length, radii, segments) {
  const u = Math.abs(dir.y) < 0.94 ? V3(0, 1, 0) : V3(1, 0, 0);
  const b = V3().crossVectors(dir, u).normalize();
  const n = V3().crossVectors(b, dir).normalize();
  const rows = radii.map(([t, r]) => ringPoints(
    V3().copy(origin).addScaledVector(dir, t * length), b, n, Math.max(r, 1e-4), segments));
  w.grid(rows, { closeU: true });
  w.fan(rows[0], true);
  w.fan(rows[rows.length - 1], false);
  return w;
}
function revolveAlong(w, pts, radii, segments) {
  const p0 = pts[0], p1 = pts[pts.length - 1];
  return revolveAlongPts(w, p0, V3().subVectors(p1, p0).normalize(), p0.distanceTo(p1), radii, segments);
}
/* helix path for coil springs; pitch flattens at both ends so the coil seats */
function helixPath(p0, p1, coils, radius, segsPerCoil = 16) {
  const axis = V3().subVectors(p1, p0);
  const len = axis.length();
  axis.normalize();
  const u = Math.abs(axis.y) < 0.94 ? V3(0, 1, 0) : V3(1, 0, 0);
  const b = V3().crossVectors(axis, u).normalize();
  const n = V3().crossVectors(b, axis).normalize();
  const total = Math.round(coils * segsPerCoil);
  const pts = [];
  for (let i = 0; i <= total; i++) {
    const t = i / total;
    const a = t * coils * TAU;
    const r = radius * (t < 0.05 ? 0.93 + t * 1.4 : t > 0.95 ? 0.93 + (1 - t) * 1.4 : 1);
    pts.push(V3().copy(p0).addScaledVector(axis, t * len)
      .addScaledVector(n, Math.cos(a) * r).addScaledVector(b, Math.sin(a) * r));
  }
  return pts;
}

/* --- 5.1 frame ----------------------------------------------------------
   Twin-spar perimeter rail.  The box section is shallow and narrow at the
   steering head, deepest over the engine where bending peaks, and closes into
   a thick plate at the pivot.                                            */
function frameSparSection(t, segs) {
  // Slim through the tank run and only deep where it turns down to the pivot.
  // A fat rail here becomes a dark diagonal across the flank that swamps the
  // tank hump and seat scoop — the spine stops reading at all.
  const lat = lerp(0.0150, 0.0205, smooth01(clampf(t * 1.6, 0, 1)))
    * (1 - 0.20 * smooth01(clampf((t - 0.64) / 0.36, 0, 1)));
  const vert = 0.0215 + 0.0130 * smooth01(clampf(t / 0.55, 0, 1))
    + 0.0235 * smooth01(clampf((t - 0.55) / 0.45, 0, 1));
  return secMove(roundRect(lat, vert, Math.min(lat, vert) * 0.46, segs), 0, -0.004 * Math.sin(Math.PI * t));
}
function buildFrame(root) {
  const g = new THREE.Group(); g.name = "frame"; root.add(g);
  const S = seg(26);

  /* steering head */
  const hA = steerPt(D.headTube.l0), hB = steerPt(D.headTube.l1);
  const hDir = V3().subVectors(hB, hA).normalize();
  add(g, tube([
    hA.clone().addScaledVector(hDir, -0.012), hA, hB, hB.clone().addScaledVector(hDir, 0.012),
  ], (t) => D.headTube.r * (t < 0.12 || t > 0.88 ? 1.16 : 1.0), seg(28)),
    MAT.alloyAnodized, "frame.headTube");

  /* main spars, authored right and mirrored */
  const path = catmull3(D.spar.path, seg(34));
  pair(g, sweep(path, (t) => frameSparSection(t, S), { upright: true }),
    MAT.alloyAnodized, "frame.spar");

  /* head gussets tying each spar into the head tube */
  const gus = catmull3([
    [0.026, 0.856, 0.444], [0.050, 0.844, 0.428], [0.068, 0.830, 0.402], [0.076, 0.818, 0.372],
  ], seg(12));
  pair(g, sweep(gus, (t) => roundRect(lerp(0.011, 0.016, t), lerp(0.022, 0.030, t), 0.008, seg(20)),
    { upright: true }), MAT.alloyAnodized, "frame.gusset");

  /* pivot plate: thick cast lug carrying the swingarm and the engine */
  const pivotPlate = write((w) => extrudePlate(catmull2([
    [-0.070, 0.098], [0.028, 0.088], [0.062, 0.030], [0.058, -0.052],
    [0.006, -0.088], [-0.062, -0.070], [-0.086, 0.010],
  ], seg(48), true), 0.026, { axis: "x", bevel: 0.0035, w }));
  pair(g, xform(pivotPlate, M.t(0.134, D.pivot[1], D.pivot[0])), MAT.alloyAnodized, "frame.pivotPlate");

  /* pivot boss + swingarm shaft */
  add(g, xform(revolve([
    V2(0.014, -0.152), V2(0.030, -0.152), V2(0.030, -0.120), V2(0.020, -0.108),
    V2(0.020, 0.108), V2(0.030, 0.120), V2(0.030, 0.152), V2(0.014, 0.152),
  ], { axis: "x", segments: seg(30) }), M.t(0, D.pivot[1], D.pivot[0])),
    MAT.alloyCast, "frame.pivotBoss");
  add(g, xform(revolve([V2(0, -0.164), V2(0.0135, -0.164), V2(0.0135, 0.164), V2(0, 0.164)],
    { axis: "x", segments: seg(20), capStart: true, capEnd: true }), M.t(0, D.pivot[1], D.pivot[0])),
    MAT.bolt, "frame.pivotShaft");

  /* front cross member and the upper shock mount */
  add(g, tube(catmull3([
    [-0.084, 0.845, 0.436], [0, 0.862, 0.440], [0.084, 0.845, 0.436],
  ], seg(14)), 0.017, seg(14)), MAT.alloyAnodized, "frame.crossFront");
  add(g, filletBox(0.128, 0.052, 0.070, 0.014, { segments: seg(26), rings: seg(9) })
    .translate(0, 0.618, -0.176), MAT.alloyAnodized, "frame.shockMount");

  /* subframe */
  pair(g, sweep(catmull3(D.subframe.upper, seg(26)),
    (t) => roundRect(lerp(0.0135, 0.0105, t), lerp(0.0205, 0.0150, t), 0.0075, seg(18)),
    { upright: true }), MAT.alloyAnodized, "frame.subUpper");
  pair(g, sweep(catmull3(D.subframe.lower, seg(20)),
    (t) => roundRect(lerp(0.0115, 0.0092, t), lerp(0.0150, 0.0118, t), 0.0065, seg(16)),
    { upright: true }), MAT.alloyAnodized, "frame.subLower");
  add(g, tube(catmull3([[-0.052, 0.884, -0.826], [0, 0.888, -0.838], [0.052, 0.884, -0.826]], seg(12)),
    0.0105, seg(12)), MAT.alloyAnodized, "frame.subCross");
  return g;
}

/* --- 5.2 front end ------------------------------------------------------- */
function buildFrontEnd(root) {
  const g = new THREE.Group(); g.name = "front"; root.add(g);
  const F = D.fork, S = seg(30), half = F.halfTrack;
  const up = AX.up, fwd = AX.fwd;
  const legAt = (L, s = half) => forkPt(L, s);

  /* outer tube — the fat upper leg of an inverted fork */
  const outerLeg = write((w) => revolveAlong(w,
    [legAt(F.topL + 0.004), legAt(F.sliderTopL)],
    [[0, F.sliderR * 1.10], [0.03, F.sliderR * 1.05], [0.92, F.sliderR], [1, F.sliderR * 1.06]], S));
  pair(g, outerLeg, MAT.paintFlat, "fork.outer");

  /* exposed inner tube — hard chrome, the brightest vertical on the machine */
  pair(g, write((w) => revolveAlong(w,
    [legAt(F.sliderTopL + 0.004), legAt(F.axleLugL + 0.036)],
    [[0, F.tubeR], [1, F.tubeR]], S)), MAT.chrome, "fork.stanchion");

  /* dust seal collar */
  pair(g, write((w) => revolveAlong(w, [legAt(F.sliderTopL - 0.006), legAt(F.sliderTopL + 0.014)],
    [[0, F.sliderR * 1.00], [0.5, F.sliderR * 1.07], [1, F.sliderR * 1.00]], seg(24))),
    MAT.rubber, "fork.seal");

  /* cap and preload adjuster */
  pair(g, write((w) => revolveAlong(w, [legAt(F.topL + 0.002), legAt(F.topL + 0.020)],
    [[0, F.sliderR * 1.13], [0.7, F.sliderR * 1.13], [1, F.sliderR * 1.03]], seg(24))),
    MAT.alloyMachined, "fork.cap");
  pair(g, write((w) => revolveAlong(w, [legAt(F.topL + 0.018), legAt(F.topL + 0.030)],
    [[0, 0.0125], [1, 0.0108]], 6)), MAT.bolt, "fork.adjuster");

  /* axle holder casting */
  const ax = legAt(0);
  pair(g, write((w) => {
    revolveAlong(w, [legAt(F.axleLugL + 0.062), legAt(-0.006)],
      [[0, 0.0248], [0.28, 0.0300], [0.70, 0.0332], [1, 0.0296]], seg(26));
    revolveAlongPts(w, V3(half - 0.030, ax.y, ax.z), V3(1, 0, 0), 0.062,
      [[0, 0.0140], [0.10, 0.0300], [0.34, 0.0336], [0.80, 0.0336], [0.92, 0.0300], [1, 0.0150]], seg(26));
  }), MAT.alloyCast, "fork.axleHolder");
  /* pinch-bolt ears behind the axle */
  pair(g, filletBox(0.030, 0.052, 0.024, 0.007, { segments: seg(20), rings: seg(7) })
    .translate(half + 0.014, ax.y + 0.030, ax.z - 0.028), MAT.alloyCast, "fork.pinchEar");
  const pinch = [];
  for (const dy of [0.012, 0.046]) {
    pinch.push(M.c(M.t(half + 0.030, ax.y + dy, ax.z - 0.028), M.rz(-Math.PI / 2)));
  }
  instance(g, socketBolt(0.0058, 0.010), MAT.boltDark, pinch, "fork.pinchBolt.R");
  instance(g, socketBolt(0.0058, 0.010), MAT.boltDark,
    pinch.map((m) => M.c(M.s(-1, 1, 1), m)), "fork.pinchBolt.L");

  /* -- triple clamps: web plate plus real bosses on the fork/stem axes -- */
  const yoke = (L, thick, webHalf, bossR, stemR) => write((w) => {
    const c = steerPt(L);
    const rows = [];
    const R = seg(9);
    for (let i = 0; i < R; i++) {
      const t = i / (R - 1);
      const y = lerp(-thick / 2, thick / 2, t);
      const k = 1 - 0.09 * Math.pow(Math.abs(t - 0.5) * 2, 2);
      const poly = catmull2([
        [-(half + bossR) * k, -webHalf * 0.52 * k], [-half * k, webHalf * 0.90 * k],
        [-0.028 * k, webHalf * k], [0.028 * k, webHalf * k], [half * k, webHalf * 0.90 * k],
        [(half + bossR) * k, -webHalf * 0.52 * k], [half * 0.60 * k, -webHalf * 0.84 * k],
        [-half * 0.60 * k, -webHalf * 0.84 * k],
      ], seg(56), true);
      rows.push(poly.map((p) => V3().copy(c)
        .addScaledVector(V3(1, 0, 0), p.x).addScaledVector(fwd, p.y).addScaledVector(up, y)));
    }
    w.grid(rows, { closeU: true });
    w.fan(rows[0], true); w.fan(rows[R - 1], false);
    for (const s of [-1, 1]) {
      const fc = forkPt(L, s * half);
      revolveAlong(w, [fc.clone().addScaledVector(up, -thick * 0.78), fc.clone().addScaledVector(up, thick * 0.78)],
        [[0, bossR * 0.97], [0.5, bossR], [1, bossR * 0.97]], seg(24));
    }
    revolveAlong(w, [c.clone().addScaledVector(up, -thick * 0.7), c.clone().addScaledVector(up, thick * 0.7)],
      [[0, stemR], [1, stemR]], seg(22));
  });
  add(g, yoke(F.lowerClampL, 0.026, 0.045, 0.0388, 0.026), MAT.alloyMachined, "fork.lowerYoke");
  add(g, yoke(F.upperClampL, 0.020, 0.040, 0.0368, 0.024), MAT.alloyMachined, "fork.upperYoke");
  add(g, tube([steerPt(F.lowerClampL - 0.034), steerPt(F.upperClampL + 0.024)], 0.0155, seg(18)),
    MAT.bolt, "fork.stem");
  add(g, write((w) => revolveAlong(w,
    [steerPt(F.upperClampL + 0.014), steerPt(F.upperClampL + 0.032)], [[0, 0.0228], [1, 0.0215]], 6)),
    MAT.bolt, "fork.stemNut");

  /* -- clip-on bars ----------------------------------------------------- */
  pair(g, write((w) => {
    const c = forkPt(F.upperClampL - 0.032, half);
    revolveAlong(w, [c.clone().addScaledVector(up, -0.015), c.clone().addScaledVector(up, 0.015)],
      [[0, F.sliderR * 1.32], [1, F.sliderR * 1.32]], seg(22));
  }), MAT.alloyMachined, "bar.clamp");

  const barPath = catmull3([
    [half, D.bar.y + 0.010, D.bar.z + 0.030],
    [half + 0.034, D.bar.y - 0.001, D.bar.z + 0.012],
    [D.bar.halfWidth, D.bar.y - 0.014, D.bar.z - 0.012],
    // the tube stops inside the grip: it used to end on the same point as the
    // grip and the bar-end, stacking three flat caps in one plane
    [D.bar.halfWidth + 0.014, D.bar.y - 0.018, D.bar.z - 0.026],
  ], seg(18));
  pair(g, tube(barPath, 0.0112, seg(16)), MAT.alloyMachined, "bar.tube");

  const gripPath = catmull3([
    [D.bar.halfWidth - 0.030, D.bar.y - 0.011, D.bar.z - 0.001],
    [D.bar.halfWidth, D.bar.y - 0.017, D.bar.z - 0.018],
    [D.bar.halfWidth + 0.030, D.bar.y - 0.023, D.bar.z - 0.034],
  ], seg(12));
  pair(g, sweep(gripPath, (t) => circlePoly(lerp(0.0158, 0.0176, Math.sin(t * 2.4)), seg(18)),
    { upright: true }), MAT.rubber, "bar.grip");
  const gEnd = gripPath[gripPath.length - 1];
  const gDir = V3().subVectors(gEnd, gripPath[gripPath.length - 2]).normalize();
  /* Bar end: a short barrel that starts 14 mm inside the rubber at a radius
     well under the grip's, so the joint is a collar rather than a ball
     perched on the end.  Its previous 42 mm sphere read as a separate part. */
  pair(g, write((w) => revolveAlongPts(w, gEnd.clone().addScaledVector(gDir, -0.014),
    gDir, 0.034, [[0, 0.0120], [0.30, 0.0150], [0.42, 0.0186], [0.80, 0.0184],
      [0.92, 0.0158], [1, 0.0088]], seg(24))),
    MAT.alloyMachined, "bar.end");

  /* lever, master cylinder, reservoir, switch block */
  const perch = V3(D.bar.halfWidth - 0.048, D.bar.y - 0.006, D.bar.z + 0.006);
  /* The blade should leave the handlebar at an acute angle rather than 90°.
     Set the root direction to ~35° relative to the bar, then keep only a
     very slight additional sweep near the tip. */
  const barDir = V3().subVectors(gripPath[gripPath.length - 1], gripPath[0]).normalize();
  const ahead = V3(-barDir.z, 0, barDir.x).normalize();
  const leverAngle = 35 * DEG;
  const leverDir = barDir.clone().multiplyScalar(Math.cos(leverAngle))
    .add(ahead.clone().multiplyScalar(Math.sin(leverAngle))).normalize();
  const pivot = perch.clone().addScaledVector(ahead, 0.010).add(V3(0, -0.004, 0));
  const leverPath = catmull3([
    pivot,
    pivot.clone().addScaledVector(leverDir, 0.032).addScaledVector(ahead, 0.001),
    pivot.clone().addScaledVector(leverDir, 0.066).addScaledVector(ahead, 0.003),
    pivot.clone().addScaledVector(leverDir, 0.098).addScaledVector(barDir, 0.010),
  ], seg(16));
  pair(g, sweep(leverPath, (t) => roundRect(lerp(0.0038, 0.0024, t),
    lerp(0.0095, 0.0058, t), 0.0020, seg(14)), { upright: true }),
    MAT.alloyMachined, "bar.lever");
  pair(g, filletBox(0.034, 0.042, 0.056, 0.010, { segments: seg(22), rings: seg(8) })
    .translate(perch.x - 0.004, perch.y + 0.012, perch.z - 0.008), MAT.alloyMachined, "bar.masterCyl");
  pair(g, filletBox(0.030, 0.032, 0.030, 0.008, { segments: seg(18), rings: seg(7) })
    .translate(perch.x - 0.002, perch.y + 0.040, perch.z - 0.016), MAT.plastic, "bar.reservoir");
  pair(g, filletBox(0.030, 0.038, 0.054, 0.010, { segments: seg(20), rings: seg(8) })
    .translate(D.bar.halfWidth - 0.086, D.bar.y - 0.012, D.bar.z + 0.012), MAT.plastic, "bar.switchBlock");

  /* brake line from the perch down the fork to the caliper */
  pair(g, tube(catmull3([
    [perch.x - 0.012, perch.y + 0.006, perch.z - 0.022],
    [half + 0.074, 0.822, 0.398], [half + 0.044, 0.690, 0.454],
    [half + 0.032, 0.548, 0.512], [half + 0.026, 0.424, 0.562],
    [half + 0.020, 0.348, 0.598],
  ], seg(26)), 0.0042, seg(10)), MAT.rubber, "brake.hoseFront");

  return g;
}

/* --- 5.3 brake calipers -------------------------------------------------
   Two bodies straddling the rotor with bridges over the top: the disc slot is
   real geometry, so the caliper reads correctly from every angle.        */
function makeCaliper({ axleY, axleZ, discX, phi, span, rIn, rOut, halfGap, thick, name, mount = "radial" }) {
  const g = new THREE.Group(); g.name = name;
  const rMid = (rIn + rOut) / 2;
  const bodyPath = [];
  const N = seg(14);
  for (let i = 0; i <= N; i++) {
    const a = lerp(phi - span, phi + span, i / N);
    bodyPath.push(V3(0, axleY + Math.sin(a) * rMid, axleZ + Math.cos(a) * rMid));
  }
  // transported frames map section.x to the radial direction and section.y to
  // the axle direction, so the caliper section is authored radial-first
  const sect = (t) => roundRect(
    ((rOut - rIn) / 2) * (1 - 0.16 * Math.pow(Math.abs(t - 0.5) * 2, 2.4)), thick / 2, thick * 0.32, seg(18));
  const outSign = discX >= 0 ? 1 : -1;

  for (const s of [1, -1]) {
    const off = discX + s * (halfGap + thick / 2);
    add(g, sweep(bodyPath.map((p) => V3(off, p.y, p.z)), sect, { seedUp: V3(1, 0, 0) }),
      MAT.alloyAnodized, name + ".body" + (s > 0 ? "O" : "I"));
    const bores = [];
    for (let i = 0; i < 2; i++) {
      const a = lerp(phi - span * 0.5, phi + span * 0.5, i);
      bores.push(M.t(off + s * thick * 0.44, axleY + Math.sin(a) * rMid, axleZ + Math.cos(a) * rMid));
    }
    instance(g, revolve([V2(0, 0), V2(0.0126, 0), V2(0.0126, s * 0.0035), V2(0.0098, s * 0.0048)],
      { axis: "x", segments: seg(18) }), MAT.alloyMachined, bores, name + ".bore" + (s > 0 ? "O" : "I"));
  }
  for (const f of [-0.62, 0, 0.62]) {
    const a = phi + span * f;
    add(g, filletBox(halfGap * 2 + thick * 2.05, 0.016, 0.020, 0.005, { segments: seg(16), rings: seg(6) })
      .translate(discX, axleY + Math.sin(a) * (rOut - 0.005), axleZ + Math.cos(a) * (rOut - 0.005)),
      MAT.alloyAnodized, name + ".bridge" + f);
  }
  for (const s of [1, -1]) {
    add(g, sweep(bodyPath.map((p) => V3(discX + s * (halfGap - 0.0024), p.y, p.z)),
      () => roundRect((rOut - rIn) * 0.30, 0.0024, 0.0012, seg(10)), { seedUp: V3(1, 0, 0) }),
      MAT.plastic, name + ".pad" + (s > 0 ? "O" : "I"));
  }
  if (mount === "radial") {
    const ears = [];
    for (const f of [-0.80, 0.80]) {
      const a = phi + span * f;
      const c = V3(discX + outSign * (halfGap + thick),
        axleY + Math.sin(a) * (rIn + 0.008), axleZ + Math.cos(a) * (rIn + 0.008));
      add(g, filletBox(0.026, 0.024, 0.026, 0.007, { segments: seg(16), rings: seg(6) })
        .translate(c.x, c.y, c.z), MAT.alloyAnodized, name + ".ear" + f);
      ears.push(M.c(M.t(c.x + outSign * 0.016, c.y, c.z), M.rz(-outSign * Math.PI / 2)));
    }
    instance(g, socketBolt(0.0065, 0.010), MAT.boltDark, ears, name + ".bolts");
  }
  const bn = phi + span * 0.92;
  add(g, tube([
    V3(discX + halfGap * outSign, axleY + Math.sin(bn) * rOut, axleZ + Math.cos(bn) * rOut),
    V3(discX + halfGap * outSign, axleY + Math.sin(bn) * (rOut + 0.017), axleZ + Math.cos(bn) * (rOut + 0.017)),
  ], (t) => lerp(0.0042, 0.0028, t), seg(10)), MAT.bolt, name + ".bleed");
  return g;
}

/* --- 5.4 swingarm, shock, linkage --------------------------------------- */
function buildSwingarm(root) {
  const g = new THREE.Group(); g.name = "swingarm"; root.add(g);

  const armPath = (s) => catmull3([
    [s * 0.118, D.pivot[1] + 0.004, D.pivot[0] + 0.012],
    [s * 0.128, D.pivot[1] + 0.020, D.pivot[0] - 0.090],
    [s * 0.132, D.pivot[1] + 0.026, D.pivot[0] - 0.230],
    [s * 0.126, D.pivot[1] - 0.006, D.pivot[0] - 0.380],
    [s * 0.113, D.rear.axle[1] + 0.006, D.rear.axle[0] + 0.052],
    [s * 0.108, D.rear.axle[1], D.rear.axle[0] + 0.008],
  ], seg(28));
  const armSect = (t) => {
    const vert = lerp(0.062, 0.030, ease(t, 0.85));
    const lat = lerp(0.030, 0.020, ease(t, 0.6));
    return secMove(roundRect(lat, vert, Math.min(lat, vert) * 0.42, seg(24)),
      0, -0.006 * Math.sin(Math.PI * clampf(t * 1.15, 0, 1)));
  };
  for (const s of [1, -1]) {
    add(g, sweep(armPath(s), armSect, { upright: true }), MAT.alloyAnodized,
      "swingarm.arm" + (s > 0 ? "R" : "L"));
  }
  add(g, xform(revolve([
    V2(0.024, -0.150), V2(0.044, -0.150), V2(0.048, -0.120),
    V2(0.048, 0.120), V2(0.044, 0.150), V2(0.024, 0.150),
  ], { axis: "x", segments: seg(30) }), M.t(0, D.pivot[1], D.pivot[0])),
    MAT.alloyAnodized, "swingarm.pivotTube");
  add(g, sweep(catmull3([
    [-0.128, D.pivot[1] + 0.030, D.pivot[0] - 0.116],
    [0, D.pivot[1] + 0.041, D.pivot[0] - 0.130],
    [0.128, D.pivot[1] + 0.030, D.pivot[0] - 0.116],
  ], seg(16)), () => roundRect(0.030, 0.016, 0.007, seg(18)), { upright: true }),
    MAT.alloyAnodized, "swingarm.brace");

  for (const s of [1, -1]) {
    const c = V3(s * 0.106, D.rear.axle[1], D.rear.axle[0]);
    add(g, filletBox(0.026, 0.062, 0.116, 0.012, { segments: seg(22), rings: seg(8) })
      .translate(c.x, c.y, c.z + 0.026), MAT.alloyAnodized, "swingarm.carrier" + (s > 0 ? "R" : "L"));
    add(g, xform(revolve([V2(0.014, -0.014), V2(0.030, -0.014), V2(0.030, 0.014), V2(0.014, 0.014)],
      { axis: "x", segments: seg(20) }), M.t(c.x, c.y, c.z)), MAT.bolt,
      "swingarm.axleNut" + (s > 0 ? "R" : "L"));
    add(g, filletBox(0.024, 0.026, 0.030, 0.006, { segments: seg(16), rings: seg(6) })
      .translate(c.x, c.y, c.z + 0.086), MAT.alloyMachined, "swingarm.adjuster" + (s > 0 ? "R" : "L"));
  }

  add(g, sweep(catmull3([
    [-0.132, D.pivot[1] + 0.056, D.pivot[0] - 0.020],
    [-0.136, D.pivot[1] + 0.062, D.pivot[0] - 0.130],
    [-0.132, D.pivot[1] + 0.036, D.pivot[0] - 0.250],
  ], seg(12)), () => roundRect(0.017, 0.010, 0.005, seg(14)), { upright: true }),
    MAT.plastic, "swingarm.chainSlider");
  add(g, tube(catmull3([
    [0.108, D.pivot[1] + 0.006, D.pivot[0] - 0.070],
    [0.104, D.rear.axle[1] + 0.030, D.rear.axle[0] + 0.120],
    [0.098, D.rear.axle[1] + 0.020, D.rear.axle[0] + 0.030],
  ], seg(12)), 0.0075, seg(12)), MAT.alloyMachined, "swingarm.torqueArm");

  /* monoshock */
  const sTop = V3(0, 0.598, -0.184), sBot = V3(0, 0.318, -0.256);
  const dir = V3().subVectors(sBot, sTop).normalize();
  add(g, tube([sTop.clone().addScaledVector(dir, 0.030), sTop.clone().addScaledVector(dir, 0.152)],
    0.0155, seg(16)), MAT.chrome, "shock.rod");
  add(g, tube([sTop.clone().addScaledVector(dir, 0.150), sBot], (t) => lerp(0.0245, 0.0225, t), seg(18)),
    MAT.alloyAnodized, "shock.body");
  add(g, tube(helixPath(sTop.clone().addScaledVector(dir, 0.028), sBot.clone().addScaledVector(dir, -0.030),
    6.2, 0.0375, seg(18)), 0.0060, seg(10)), MAT.paintFlat, "shock.spring");
  add(g, filletBox(0.038, 0.052, 0.030, 0.010, { segments: seg(18), rings: seg(7) })
    .translate(0.038, 0.470, -0.148), MAT.alloyAnodized, "shock.reservoir");
  add(g, filletBox(0.052, 0.046, 0.070, 0.010, { segments: seg(18), rings: seg(7) })
    .translate(0, 0.302, -0.262), MAT.alloyAnodized, "shock.rocker");
  pair(g, tube([V3(0.032, 0.294, -0.278), V3(0.030, 0.320, -0.174)], 0.0088, seg(12)),
    MAT.alloyMachined, "shock.tieRod");
  return g;
}

/* --- 5.5 rider controls -------------------------------------------------- */
function buildControls(root) {
  const g = new THREE.Group(); g.name = "controls"; root.add(g);
  const P = D.peg, pp = D.pillionPeg;

  for (const s of [1, -1]) {
    add(g, xform(write((w) => extrudePlate(catmull2([
      [-0.048, 0.052], [0.020, 0.046], [0.052, 0.004], [0.030, -0.048],
      [-0.026, -0.052], [-0.058, -0.006],
    ], seg(40), true), 0.012, { axis: "x", bevel: 0.0022, w })),
      M.t(s * (P.halfW - 0.012), P.y, P.z)), MAT.alloyMachined, "peg.hanger" + (s > 0 ? "R" : "L"));
    add(g, write((w) => revolveAlongPts(w, V3(s * P.halfW, P.y, P.z), V3(s, 0.06, 0).normalize(), 0.072,
      [[0, 0.0125], [0.12, 0.0152], [0.85, 0.0140], [0.93, 0.0182], [1, 0.0164]], seg(20))),
      MAT.knurled, "peg.rider" + (s > 0 ? "R" : "L"));
    // the root sits on the lower subframe rail under the tail, not in mid-air
    add(g, sweep(catmull3([
      [s * 0.076, 0.782, -0.472],
      [s * 0.108, 0.716, -0.480],
      [s * 0.134, 0.660, -0.484],
      [s * (pp.halfW - 0.012), pp.y, pp.z],
    ], seg(12)), (t) => roundRect(lerp(0.011, 0.013, t), lerp(0.026, 0.016, t), 0.006, seg(14)),
      { upright: true }), MAT.paintFlat, "peg.pillionHanger" + (s > 0 ? "R" : "L"));
    add(g, write((w) => revolveAlongPts(w, V3(s * pp.halfW, pp.y, pp.z), V3(s, 0.05, 0).normalize(),
      0.052, [[0, 0.0115], [0.15, 0.0140], [0.88, 0.0130], [1, 0.0150]], seg(18))),
      MAT.rubber, "peg.pillion" + (s > 0 ? "R" : "L"));
  }

  add(g, tube(catmull3([
    [-0.150, P.y - 0.010, P.z + 0.012], [-0.158, P.y - 0.028, P.z + 0.098],
    [-0.150, P.y - 0.030, P.z + 0.168],
  ], seg(12)), 0.0068, seg(12)), MAT.alloyMachined, "control.shiftLever");
  add(g, write((w) => revolveAlongPts(w, V3(-0.150, P.y - 0.030, P.z + 0.168),
    V3(-1, 0.02, 0.10).normalize(), 0.040, [[0, 0.0095], [1, 0.0085]], seg(14))),
    MAT.rubber, "control.shiftTip");
  add(g, tube(catmull3([
    [0.150, P.y - 0.008, P.z + 0.008], [0.166, P.y - 0.034, P.z + 0.090],
    [0.158, P.y - 0.040, P.z + 0.156],
  ], seg(12)), 0.0072, seg(12)), MAT.alloyMachined, "control.brakePedal");
  add(g, filletBox(0.010, 0.034, 0.026, 0.005, { segments: seg(14), rings: seg(6) })
    .translate(0.158, P.y - 0.044, P.z + 0.162), MAT.knurled, "control.pedalPad");
  add(g, filletBox(0.030, 0.078, 0.032, 0.011, { segments: seg(18), rings: seg(7) })
    .translate(0.166, P.y + 0.026, P.z - 0.026), MAT.alloyMachined, "control.rearMaster");
  add(g, tube(catmull3([
    [0.166, P.y + 0.062, P.z - 0.030], [0.146, P.y + 0.096, P.z - 0.072],
    [0.120, P.y + 0.108, P.z - 0.126],
  ], seg(10)), 0.0038, seg(10)), MAT.rubber, "control.rearHose");
  add(g, tube(catmull3([
    [0.166, P.y - 0.006, P.z - 0.020],
    [0.140, D.pivot[1] - 0.020, D.pivot[0] - 0.120],
    [0.120, D.rear.axle[1] + 0.052, D.rear.axle[0] + 0.180],
    [0.106, D.rear.axle[1] + 0.014, D.rear.axle[0] + 0.062],
  ], seg(20)), 0.0040, seg(10)), MAT.rubber, "control.rearBrakeLine");

  add(g, tube(catmull3([
    [-0.126, D.pivot[1] - 0.028, D.pivot[0] + 0.030],
    [-0.150, D.pivot[1] - 0.072, D.pivot[0] - 0.030],
    [-0.156, D.pivot[1] - 0.104, D.pivot[0] - 0.108],
  ], seg(10)), (t) => lerp(0.0105, 0.0080, t), seg(12)), MAT.paintFlat, "stand.side");
  add(g, filletBox(0.010, 0.020, 0.048, 0.005, { segments: seg(14), rings: seg(6) })
    .translate(-0.158, D.pivot[1] - 0.112, D.pivot[0] - 0.124), MAT.paintFlat, "stand.foot");
  return g;
}

/* ============================================================================
   6. ENGINE · EXHAUST · COOLING
   ----------------------------------------------------------------------------
   636 cc inline four.  The crankcase is a loft of stations along Z; the barrel
   and head are authored upright in a bore-local frame and then rotated by the
   contract's bank angle, so ports, cam cover and throttle bodies all move
   together if that angle changes.
   ========================================================================== */

/* loft a run of 2D sections placed along +Z, capped at both ends */
function loftZ(stations, { w = null, flip = false, capStart = true, capEnd = true } = {}) {
  const rows = stations.map((s) => s.sec.map((p) => V3(p.x, p.y, s.z)));
  const target = w || new Writer();
  target.grid(rows, { closeU: true, flip });
  if (capStart) target.fan(rows[0], !flip);
  if (capEnd) target.fan(rows[rows.length - 1], flip);
  return w ? target : orient(target.geometry());
}
/* loft along +Y — used inside the bore-local frame, section is (x, z) */
function loftY(stations, { w = null, flip = false, capStart = true, capEnd = true } = {}) {
  const rows = stations.map((s) => s.sec.map((p) => V3(p.x, s.y, p.y)));
  const target = w || new Writer();
  target.grid(rows, { closeU: true, flip });
  if (capStart) target.fan(rows[0], !flip);
  if (capEnd) target.fan(rows[rows.length - 1], flip);
  return w ? target : orient(target.geometry());
}

function buildEngine(root) {
  const g = new THREE.Group(); g.name = "engine"; root.add(g);
  const E = D.engine, S = seg(40);
  const box = (hw, lo, hi, r) => secMove(roundRect(hw, (hi - lo) / 2, r, S), 0, (hi + lo) / 2);

  /* -- 6.1 crankcase ---------------------------------------------------- */
  add(g, loftZ([
    { z: 0.168, sec: box(0.074, 0.258, 0.396, 0.026) },
    { z: 0.132, sec: box(0.104, 0.230, 0.424, 0.030) },
    { z: 0.076, sec: box(0.128, 0.202, 0.440, 0.034) },
    { z: 0.018, sec: box(0.139, 0.182, 0.446, 0.036) },
    { z: -0.040, sec: box(0.140, 0.176, 0.444, 0.036) },
    { z: -0.094, sec: box(0.131, 0.192, 0.434, 0.034) },
    { z: -0.140, sec: box(0.108, 0.228, 0.418, 0.030) },
    { z: -0.176, sec: box(0.070, 0.286, 0.400, 0.024) },
  ]), MAT.alloyCast, "engine.crankcase");

  add(g, loftZ([
    { z: 0.124, sec: box(0.086, 0.176, 0.232, 0.024) },
    { z: 0.060, sec: box(0.104, 0.160, 0.216, 0.026) },
    { z: -0.020, sec: box(0.107, 0.154, 0.212, 0.026) },
    { z: -0.092, sec: box(0.094, 0.166, 0.222, 0.024) },
    { z: -0.128, sec: box(0.070, 0.190, 0.240, 0.020) },
  ]), MAT.alloyCast, "engine.sump");
  add(g, write((w) => revolveAlongPts(w, V3(0.050, 0.156, 0.030), V3(0, -1, 0), 0.020,
    [[0, 0.0130], [0.5, 0.0130], [1, 0.0110]], 6)), MAT.bolt, "engine.drainPlug");

  /* -- 6.2 barrel, head and cam cover in the bore-local frame ---------- */
  const bore = new THREE.Group();
  bore.name = "engine.top";
  bore.position.set(0, E.crank[1], E.crank[0]);
  bore.rotation.x = E.bankAngle;
  g.add(bore);
  const bx = (hw, lo, hi, r) => secMove(roundRect(hw, (hi - lo) / 2, r, S), 0, (hi + lo) / 2);

  add(bore, loftY([
    { y: 0.120, sec: bx(0.138, -0.080, 0.072, 0.020) },
    { y: 0.146, sec: bx(0.132, -0.074, 0.066, 0.018) },
    { y: 0.172, sec: bx(0.126, -0.070, 0.062, 0.016) },
    { y: 0.238, sec: bx(0.124, -0.068, 0.060, 0.014) },
    { y: 0.252, sec: bx(0.130, -0.074, 0.070, 0.016) },
  ]), MAT.alloyCast, "engine.barrel");
  add(bore, loftY([
    { y: 0.250, sec: bx(0.132, -0.082, 0.080, 0.016) },
    { y: 0.270, sec: bx(0.136, -0.088, 0.088, 0.018) },
    { y: 0.288, sec: bx(0.134, -0.086, 0.084, 0.018) },
    { y: 0.298, sec: bx(0.128, -0.078, 0.074, 0.018) },
  ]), MAT.alloyCast, "engine.head");
  add(bore, loftY([
    { y: 0.296, sec: bx(0.126, -0.078, 0.072, 0.018) },
    { y: 0.314, sec: bx(0.128, -0.080, 0.074, 0.020) },
    { y: 0.338, sec: bx(0.120, -0.072, 0.066, 0.022) },
    { y: 0.348, sec: bx(0.104, -0.060, 0.054, 0.022) },
  ]), MAT.alloyCast, "engine.camCover");

  const ribs = [], plugs = [], stubs = [];
  for (let i = 0; i < 4; i++) {
    const x = lerp(-0.084, 0.084, i / 3);
    ribs.push(M.t(x, 0.350, 0.002));
    plugs.push(M.t(x, 0.352, -0.028));
    stubs.push(M.t(x, 0.298, -0.088));
  }
  instance(bore, filletBox(0.030, 0.014, 0.104, 0.006, { segments: seg(16), rings: seg(6) }),
    MAT.alloyCast, ribs, "engine.camRib");
  instance(bore, revolve([V2(0.0135, 0), V2(0.0135, 0.013), V2(0.0100, 0.015)],
    { axis: "y", segments: seg(14), capEnd: true }), MAT.boltDark, plugs, "engine.plugTube");
  instance(bore, revolve([V2(0.0225, 0), V2(0.0225, 0.030), V2(0.0250, 0.036), V2(0.0250, 0.054)],
    { axis: "y", segments: seg(16) }), MAT.plastic, stubs, "engine.intakeStub");
  add(bore, filletBox(0.212, 0.060, 0.088, 0.016, { segments: seg(22), rings: seg(8) })
    .translate(0, 0.356, -0.106), MAT.plastic, "engine.throttleBodies");

  /* -- 6.3 side covers -------------------------------------------------- */
  add(g, xform(revolve([
    V2(0.030, 0.140), V2(0.086, 0.140), V2(0.100, 0.134), V2(0.107, 0.120),
    V2(0.109, 0.094), V2(0.104, 0.058), V2(0.088, 0.020), V2(0.040, 0.006), V2(0, 0.004),
  ], { axis: "x", segments: seg(44), capEnd: true }), M.t(0, 0.340, -0.052)),
    MAT.alloyCast, "engine.clutchCover");
  const ccBolts = [];
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * TAU + 0.2;
    ccBolts.push(M.c(M.t(0.130, 0.340 + Math.sin(a) * 0.098, -0.052 + Math.cos(a) * 0.098),
      M.rz(-Math.PI / 2)));
  }
  instance(g, hexBolt(0.0050, 0.0038), MAT.bolt, ccBolts, "engine.clutchBolts");

  add(g, xform(revolve([
    V2(0.028, -0.142), V2(0.078, -0.142), V2(0.092, -0.136), V2(0.099, -0.120),
    V2(0.099, -0.086), V2(0.090, -0.036), V2(0.046, -0.008), V2(0, -0.004),
  ], { axis: "x", segments: seg(44), capEnd: true, flip: true }), M.t(0, 0.352, 0.014)),
    MAT.alloyCast, "engine.altCover");

  add(g, xform(revolve([
    V2(0.026, -0.152), V2(0.062, -0.152), V2(0.070, -0.144), V2(0.072, -0.120),
    V2(0.066, -0.104), V2(0.030, -0.096), V2(0, -0.094),
  ], { axis: "x", segments: seg(32), capEnd: true, flip: true }),
    M.t(0, D.countershaft[1], D.countershaft[0])), MAT.alloyCast, "engine.sprocketCover");
  const fs = makeSprocket({
    teeth: 15, pitchR: D.frontSprocketR, thick: 0.0072, boreR: 0.020,
    name: "sprocket.front", mat: MAT.chain,
  });
  fs.position.set(-0.0876, D.countershaft[1], D.countershaft[0]);
  g.add(fs);

  add(g, xform(revolve([V2(0.026, -0.106), V2(0.038, -0.106), V2(0.040, -0.070),
    V2(0.030, -0.056), V2(0, -0.054)], { axis: "x", segments: seg(22), capEnd: true, flip: true }),
    M.t(0, 0.424, -0.126)), MAT.alloyCast, "engine.starter");
  add(g, xform(revolve([V2(0.024, 0.104), V2(0.040, 0.104), V2(0.044, 0.078),
    V2(0.034, 0.062), V2(0, 0.060)], { axis: "x", segments: seg(22), capEnd: true }),
    M.t(0, 0.248, 0.086)), MAT.alloyCast, "engine.waterPump");

  /* -- 6.4 exhaust ------------------------------------------------------
     Four headers leave the head face, drop down the front of the engine,
     converge under the sump and feed the right-side silencer.           */
  const ex = new THREE.Group(); ex.name = "exhaust"; g.add(ex);
  const R = D.exhaust;
  for (let i = 0; i < 4; i++) {
    const p = V3(lerp(-0.086, 0.086, i / 3), 0.268, 0.086)
      .applyAxisAngle(V3(1, 0, 0), E.bankAngle)
      .add(V3(0, E.crank[1], E.crank[0]));
    const sx = Math.sign(p.x) || 1, ax = Math.abs(p.x);
    add(ex, tube(catmull3([
      [p.x, p.y, p.z],
      [p.x, p.y - 0.050, p.z + 0.048],
      [sx * ax * 0.95, p.y - 0.144, p.z + 0.070],
      [sx * ax * 0.87, 0.288, p.z + 0.026],
      [sx * ax * 0.75, 0.224, 0.156],
      [sx * ax * 0.58, 0.199, 0.040],
      [sx * ax * 0.42, 0.195, -0.080],
      [sx * ax * 0.22, 0.197, -0.166],
    ], seg(34)), (t) => R.headerR * (1 + 0.10 * t), seg(14)), MAT.header, "exhaust.header" + i);
  }
  add(ex, filletBox(0.112, 0.084, 0.098, 0.028, { segments: seg(22), rings: seg(8) })
    .translate(0.014, R.collectorY + 0.008, R.collectorZ), MAT.header, "exhaust.preChamber");
  add(ex, tube(catmull3([
    [0.040, R.collectorY + 0.010, R.collectorZ - 0.044],
    [0.078, R.collectorY + 0.026, R.collectorZ - 0.074],
    [0.108, R.collectorY + 0.048, R.collectorZ - 0.100],
  ], seg(14)), (t) => lerp(0.036, R.canR0 * 0.92, t), seg(18)), MAT.header, "exhaust.link");

  const canA = V3(...R.canA), canB = V3(...R.canB);
  const canDir = V3().subVectors(canB, canA).normalize();
  add(ex, write((w) => revolveAlongPts(w, canA, canDir, canA.distanceTo(canB), [
    [0, R.canR0 * 0.86], [0.06, R.canR0], [0.55, R.canR1 * 0.95],
    [0.90, R.canR1], [1, R.canR1 * 0.98],
  ], seg(32))), MAT.titanium, "exhaust.can");
  add(ex, write((w) => revolveAlongPts(w, canB.clone().addScaledVector(canDir, -0.016), canDir, 0.028, [
    [0, R.canR1 * 1.04], [0.62, R.canR1 * 1.04], [0.66, R.canR1 * 0.95], [1, R.canR1 * 0.90],
  ], seg(32))), MAT.alloyAnodized, "exhaust.canCap");
  add(ex, write((w) => revolveAlongPts(w, canB.clone().addScaledVector(canDir, 0.001), canDir, 0.018, [
    [0, R.canR1 * 0.78], [1, R.canR1 * 0.72],
  ], seg(28))), MAT.plastic, "exhaust.outlet");
  add(ex, sweep(catmull3([
    [0.128, 0.310, -0.520], [0.152, 0.344, -0.556], [0.136, 0.396, -0.598],
  ], seg(10)), () => roundRect(0.006, 0.016, 0.004, seg(12)), { upright: true }),
    MAT.alloyAnodized, "exhaust.strap");

  /* -- 6.5 cooling ------------------------------------------------------ */
  const C = D.radiator;
  const radRows = [];
  const RN = seg(26);
  for (let i = 0; i < 6; i++) {
    const t = i / 5;
    const y = lerp(C.y0, C.y1, t);
    const row = [];
    for (let c = 0; c <= RN; c++) {
      const x = lerp(-C.halfW, C.halfW, c / RN);
      // bowed forward at the centre, following the fairing's plan curve
      const bow = 0.026 * (1 - Math.pow(Math.abs(x) / C.halfW, 2));
      row.push(V3(x, y, C.z1 + bow - 0.012 * t));
    }
    radRows.push(row);
  }
  add(g, panelShell(radRows, 0.028), MAT.radiator, "cooling.radiator");
  for (const s of [1, -1]) {
    add(g, sweep(catmull3([
      [s * (C.halfW + 0.005), C.y0 - 0.008, C.z1 + 0.004],
      [s * (C.halfW + 0.007), (C.y0 + C.y1) / 2, C.z1 + 0.008],
      [s * (C.halfW + 0.005), C.y1 + 0.008, C.z1 + 0.004],
    ], seg(10)), () => roundRect(0.010, 0.020, 0.006, seg(14)), { upright: true }),
      MAT.alloyCast, "cooling.radTank" + (s > 0 ? "R" : "L"));
  }
  add(g, xform(revolve([V2(0.086, 0), V2(0.086, 0.026), V2(0.062, 0.030), V2(0, 0.030)],
    { axis: "z", segments: seg(28), capStart: true }), M.t(-0.020, 0.478, C.z0 - 0.056)),
    MAT.plastic, "cooling.fan");
  add(g, tube(catmull3([
    [0.108, C.y1 - 0.014, C.z1 - 0.004], [0.132, 0.578, 0.230], [0.110, 0.536, 0.152],
  ], seg(12)), 0.0135, seg(12)), MAT.rubber, "cooling.upperHose");
  add(g, tube(catmull3([
    [-0.100, C.y0 + 0.016, C.z1 - 0.004], [-0.120, 0.318, 0.224], [-0.072, 0.264, 0.118],
    [-0.024, 0.252, 0.092],
  ], seg(14)), 0.0135, seg(12)), MAT.rubber, "cooling.lowerHose");
  add(g, filletBox(0.172, 0.048, 0.030, 0.008, { segments: seg(20), rings: seg(7) })
    .translate(0, 0.328, C.z1 + 0.010), MAT.radiator, "cooling.oilCooler");
  return g;
}

/* ============================================================================
   7. BODYWORK
   ----------------------------------------------------------------------------
   Every panel is a sampled surface, not a primitive.  Closed volumes (tank,
   tail) use four-quadrant superellipse sections whose exponents carry the
   design language: soft ~2.6 crowns over knife-edged ~5 lower creases.  Open
   panels (cowl, flanks, belly, fenders) go through panelShell() so the cut
   edges have real thickness — which is what separates a fairing from a decal.
   ========================================================================== */

/* open arc of the four-quadrant superellipse, a0 -> a1 in section angle */
function arcSuper({ halfW, top, bottom, cx = 0, cy = 0, nTop = 2.6, nBot = 2.6,
  nTopIn = null, nBotIn = null, a0, a1, segments = 40 }) {
  const out = [];
  for (let i = 0; i <= segments; i++) {
    const a = lerp(a0, a1, i / segments);
    const ca = Math.cos(a), sa = Math.sin(a);
    const upper = sa >= 0;
    const nx = upper ? (nTopIn ?? nTop) : (nBotIn ?? nBot);
    const ny = upper ? nTop : nBot;
    const h = upper ? top : bottom;
    out.push(V2(
      cx + Math.sign(ca) * Math.pow(Math.abs(ca), 2 / nx) * halfW,
      cy + Math.sign(sa) * Math.pow(Math.abs(sa), 2 / ny) * h,
    ));
  }
  return out;
}
/* Resample a station table so a loft reads as a surface rather than a run of
   flats.  Ten stations across 700 mm of tank leaves 80 mm facets, which on a
   gloss black panel is exactly where the highlight breaks and gives away the
   polygon.  Z advances linearly; every shape column eases, so the stations
   become tangent rather than corners.                                    */
function resampleTable(table, n) {
  const m = table.length - 1;
  const out = [];
  for (let i = 0; i < n; i++) {
    const f = (i / (n - 1)) * m;
    const j = Math.min(m - 1, Math.floor(f));
    const raw = f - j, eased = smooth01(raw);
    out.push(table[0].map((_, k) => lerp(table[j][k], table[j + 1][k], k === 0 ? raw : eased)));
  }
  return out;
}
/* closed loft from a station table, capped at both ends */
function loftClosed(rows) {
  return orient(write((w) => {
    w.grid(rows, { closeU: true });
    w.fan(rows[0], true);
    w.fan(rows[rows.length - 1], false);
  }));
}
/* conformal decal: lift a rectangle of the parent surface along its own
   normals so graphics wrap the panel instead of floating over it          */
/* Returns the lifted patch plus whether the parent grid's own winding faces
   inward there.  A station table that runs -Z produces inward normals, which
   would bury the graphic inside the panel and show it mirrored.          */
function decalPatch(rows, r0, r1, c0, c1, lift = 0.0007) {
  const N = gridNormals(rows);
  const centre = V3();
  let n = 0;
  for (const row of rows) for (const p of row) { centre.add(p); n++; }
  centre.divideScalar(n);
  let facing = 0;
  for (let r = r0; r <= r1; r++) {
    for (let c = c0; c <= c1; c++) {
      facing += N[r][c].dot(V3().subVectors(rows[r][c], centre));
    }
  }
  const sign = facing < 0 ? -1 : 1;
  const out = [];
  for (let r = r0; r <= r1; r++) {
    const line = [];
    for (let c = c0; c <= c1; c++) {
      line.push(V3().copy(rows[r][c]).addScaledVector(N[r][c], lift * sign));
    }
    out.push(line);
  }
  out.inward = sign < 0;
  return out;
}
/* Rows run along the machine's length, so U follows Z and V follows the
   column direction across the panel.  Seen from +X the nose is to screen-left,
   from -X it is to screen-right, so mirrored panels reverse U.  V is reversed
   per call because a section's columns climb on one flank and fall on the
   other.  Winding is flipped when the parent grid faces inward there.    */
function addDecal(parent, rows, r0, r1, c0, c1, material, name,
  { flipU = false, flipV = false } = {}) {
  const patch = decalPatch(rows, r0, r1, c0, c1);
  const inward = patch.inward;
  const geo = write((w) => w.grid(patch, {
    flip: inward,
    uvFn: (r, c, R, C) => [
      flipU ? 1 - r / (R - 1) : r / (R - 1),
      flipV ? c / (C - 1) : 1 - c / (C - 1),
    ],
  }));
  return add(parent, geo, material, name, { cast: false, receive: false });
}

function buildBody(root) {
  const g = new THREE.Group(); g.name = "body"; root.add(g);
  const B = D.body;
  const SS = seg(52);

  /* ======================================================================
     7.1 FUEL TANK COVER — widest at the rider's knees, lower flank scooped
     so it tucks in over the frame spar.
     ==================================================================== */
  const tankTable = [
    // z,      halfW, top,   bottom, nTop, nBot, wBot
    [-0.300, 0.064, 0.868, 0.784, 2.9, 3.2, 0.92],
    [-0.230, 0.090, 0.888, 0.764, 2.9, 3.0, 0.90],
    [-0.150, 0.124, 0.896, 0.738, 2.8, 2.7, 0.86],
    [-0.060, 0.151, 0.898, 0.714, 2.7, 2.5, 0.82],
    [0.030, 0.161, 0.892, 0.702, 2.6, 2.4, 0.80],
    [0.120, 0.158, 0.880, 0.704, 2.5, 2.4, 0.82],
    [0.210, 0.140, 0.864, 0.718, 2.5, 2.5, 0.86],
    [0.300, 0.112, 0.848, 0.740, 2.6, 2.7, 0.90],
    [0.372, 0.082, 0.834, 0.766, 2.8, 3.0, 0.94],
    [0.418, 0.058, 0.824, 0.790, 3.0, 3.2, 0.96],
  ];
  const tankRows = resampleTable(tankTable, seg(30)).map(([z, hw, top, bot, nT, nB, wB]) => superSection({
    halfW: hw, top: (top - bot) / 2, bottom: (top - bot) / 2, cy: (top + bot) / 2,
    nTop: nT, nBot: nB, nTopIn: nT * 1.15, nBotIn: nB * 1.6, wBot: wB, segments: SS,
  }).map((p) => V3(p.x, p.y, z)));
  add(g, loftClosed(tankRows), MAT.paintGloss, "body.tank");

  /* Anything sitting on the tank has to be seated on the tank, not at a
     remembered height: the crown moved when the hump was raised, which left
     the filler half sunk at one edge and floating at the other.  Sample the
     generated surface and match its local slope.                         */
  const crownOf = (row) => {
    let y = -Infinity;
    for (const p of row) if (Math.abs(p.x) < 0.030 && p.y > y) y = p.y;
    return y;
  };
  const tankCrown = (z) => {
    let lo = null, hi = null;
    for (const row of tankRows) {
      const rz = row[0].z;
      if (rz <= z && (!lo || rz > lo[0].z)) lo = row;
      if (rz >= z && (!hi || rz < hi[0].z)) hi = row;
    }
    if (!lo) return crownOf(hi);
    if (!hi || lo === hi) return crownOf(lo);
    return lerp(crownOf(lo), crownOf(hi),
      (z - lo[0].z) / (hi[0].z - lo[0].z));
  };
  /* Seat a fitting on the chord through its OWN rim, not on the crown with a
     slope guessed from a wider baseline.  Sampling ±48 mm for a ±32 mm cap
     over-rotated it: the leading edge sank into the tank while the trailing
     edge lifted off — half buried, half proud.  Taking the chord across the
     part's actual radius puts every point of the rim the same height clear. */
  const seatOn = (z, reach, lift) => {
    const yF = tankCrown(z + reach), yB = tankCrown(z - reach);
    return M.c(M.t(0, (yF + yB) / 2 + lift, z),
      M.rx(Math.atan2(yB - yF, 2 * reach)));
  };

  /* domed cap with a rolled rim and a key barrel, sitting in a recessed
     collar — a plain disc at this scale disappears into the gloss */
  add(g, xform(revolve([
    V2(0, 0.0065), V2(0.013, 0.0062), V2(0.023, 0.0042), V2(0.029, 0.0005),
    V2(0.0315, -0.0035), V2(0.030, -0.0085), V2(0.024, -0.012), V2(0, -0.013),
  ], { axis: "y", segments: seg(36) }), seatOn(0.196, 0.032, 0.0030)),
    MAT.alloyMachined, "body.fillerCap");
  add(g, xform(revolve([
    V2(0, 0.0072), V2(0.0068, 0.0070), V2(0.0075, 0.0045), V2(0, 0.0042),
  ], { axis: "y", segments: seg(20) }), seatOn(0.196, 0.032, 0.0030)),
    MAT.boltDark, "body.fillerKey");
  // open annular collar: no closed volume to test, so its winding is stated
  add(g, xform(revolve([
    V2(0.0305, -0.0025), V2(0.0400, -0.0050), V2(0.0425, -0.0125),
  ], { axis: "y", segments: seg(36), flip: true }), seatOn(0.196, 0.032, 0.0030)),
    MAT.paintFlat, "body.fillerRing");
  add(g, xform(write((w) => extrudePlate(catmull2([
    [0, 0.074], [0.031, 0.040], [0.035, -0.048], [0, -0.072],
    [-0.035, -0.048], [-0.031, 0.040],
  ], seg(40), true), 0.004, { axis: "y", bevel: 0.0012, w })), seatOn(0.058, 0.073, 0.0018)),
    MAT.rubber, "body.tankPad");

  /* ======================================================================
     7.2 RIDER SEAT
     ==================================================================== */
  const seatTable = [
    [-0.470, 0.052, 0.856, 0.816], [-0.420, 0.080, 0.845, 0.806],
    [-0.372, 0.097, 0.836, 0.798], [-0.326, 0.100, 0.830, 0.794],
    [-0.286, 0.093, 0.830, 0.794], [-0.240, 0.076, 0.836, 0.798],
    [-0.196, 0.054, 0.846, 0.806],
  ];
  const seatRows = resampleTable(seatTable, seg(18)).map(([z, hw, top, bot]) => superSection({
    halfW: hw, top: (top - bot) / 2, bottom: (top - bot) / 2, cy: (top + bot) / 2,
    nTop: 3.4, nBot: 4.6, nTopIn: 4.0, nBotIn: 6.0, segments: SS,
  }).map((p) => V3(p.x, p.y, z)));
  add(g, loftClosed(seatRows), MAT.seat, "body.seatRider");

  /* ======================================================================
     7.3 TAIL UNIT — rises behind the rider then knifes to a point; high
     lower exponents keep the underside folded rather than inflated.
     ==================================================================== */
  // shorter and more upswept than a first pass suggests: a supersport tail
  // finishes barely past the rear axle and rides high above the hugger
  // The spine is the machine's signature line: hump over the tank, scoop at
  // the rider's seat, then a hard kick up through the tail before the tip
  // knifes down.  A flat run through here reads as a naked bike.
  const tailTable = [
    [-0.395, 0.090, 0.852, 0.788, 3.0, 3.4],
    [-0.462, 0.102, 0.878, 0.780, 3.0, 3.8],
    [-0.535, 0.106, 0.898, 0.774, 3.0, 4.2],
    [-0.610, 0.103, 0.914, 0.772, 3.1, 4.6],
    [-0.686, 0.096, 0.926, 0.776, 3.2, 5.0],
    [-0.755, 0.082, 0.934, 0.790, 3.4, 5.2],
    // the last three stations are the cut-off face, not a taper: the crown
    // holds its height while the underside climbs to meet it
    [-0.818, 0.062, 0.939, 0.822, 3.6, 5.0],
    [-0.858, 0.038, 0.941, 0.868, 3.8, 4.6],
    [-0.878, 0.014, 0.936, 0.916, 4.2, 4.4],
  ];
  const tailRows = resampleTable(tailTable, seg(26)).map(([z, hw, top, bot, nT, nB]) => superSection({
    halfW: hw, top: (top - bot) / 2, bottom: (top - bot) / 2, cy: (top + bot) / 2,
    nTop: nT, nBot: nB, nTopIn: nT * 1.2, nBotIn: nB * 1.1, segments: SS,
  }).map((p) => V3(p.x, p.y, z)));
  add(g, loftClosed(tailRows), MAT.paintFlat, "body.tail");
  const tR = tailRows.length, tC = tailRows[0].length;
  // superSection starts at +X and runs anticlockwise, so the -X flank sits
  // either side of the half-way column
  addDecal(g, tailRows, Math.round(tR * 0.10), Math.round(tR * 0.42),
    0, Math.round(tC * 0.085), MAT.decalKawasaki, "body.decalTail.R", { flipV: true });
  addDecal(g, tailRows, Math.round(tR * 0.10), Math.round(tR * 0.42),
    Math.round(tC * 0.415), Math.round(tC * 0.50), MAT.decalKawasaki,
    "body.decalTail.L", { flipU: true });

  // the pillion pad rides proud of the tail crown, as it does on the machine
  const pilTable = [
    [-0.442, 0.050, 0.884, 0.856], [-0.492, 0.070, 0.900, 0.872],
    [-0.545, 0.074, 0.912, 0.886], [-0.600, 0.066, 0.922, 0.898],
    [-0.648, 0.046, 0.928, 0.908],
  ];
  const pilRows = resampleTable(pilTable, seg(15)).map(([z, hw, top, bot]) => superSection({
    halfW: hw, top: (top - bot) / 2, bottom: (top - bot) / 2, cy: (top + bot) / 2,
    nTop: 3.6, nBot: 6, segments: SS,
  }).map((p) => V3(p.x, p.y, z)));
  add(g, loftClosed(pilRows), MAT.seat, "body.seatPillion");

  pair(g, sweep(catmull3([
    [0.086, 0.870, -0.470], [0.101, 0.888, -0.560], [0.094, 0.894, -0.646],
  ], seg(12)), () => roundRect(0.008, 0.011, 0.005, seg(12)), { upright: true }),
    MAT.alloyAnodized, "body.grabRail");

  /* tail lamp let into the tail end, LED bar behind the lens */
  const lampRows = [];
  for (let i = 0; i <= 6; i++) {
    const t = i / 6, z = lerp(-0.790, -0.862, t);
    const hw = lerp(0.066, 0.030, t), h = lerp(0.034, 0.016, t);
    lampRows.push(arcSuper({
      halfW: hw, top: h, bottom: h, cy: lerp(0.876, 0.904, t),
      nTop: 3.4, nBot: 4.6, a0: Math.PI * 0.82, a1: Math.PI * 0.18, segments: seg(26),
    }).map((p) => V3(p.x, p.y, z)));
  }
  add(g, panelShell(lampRows, 0.005, { flip: true }), MAT.lensRed, "body.tailLamp");
  add(g, filletBox(0.066, 0.009, 0.020, 0.003, { segments: seg(14), rings: seg(5) })
    .translate(0, 0.894, -0.800), MAT.led, "body.tailLED");

  /* ======================================================================
     7.4 UPPER COWL — one shell from the nose tip back to the screen base,
     wrapping down both flanks.  Its lower boundary rises at the front: that
     gap is the headlight aperture, and the lamp units fill it.
     ==================================================================== */
  const cowlTable = [
    // z,     halfW, crownY, lowY,  nTop, nBot, crownPinch
    [0.500, 0.152, 0.982, 0.780, 2.45, 3.2, 1.90],
    [0.560, 0.158, 0.990, 0.778, 2.45, 3.2, 1.86],
    [0.620, 0.159, 0.986, 0.780, 2.45, 3.3, 1.82],
    [0.680, 0.155, 0.972, 0.790, 2.50, 3.4, 1.78],
    [0.740, 0.148, 0.952, 0.806, 2.55, 3.5, 1.74],
    [0.790, 0.138, 0.932, 0.826, 2.65, 3.6, 1.70],
    [0.840, 0.122, 0.912, 0.848, 2.80, 3.8, 1.68],
    [0.878, 0.100, 0.896, 0.864, 3.00, 4.0, 1.72],
    [0.902, 0.070, 0.884, 0.872, 3.30, 4.2, 1.80],
    [0.918, 0.036, 0.876, 0.870, 3.70, 4.4, 1.95],
  ];
  /* Two creases are pressed into the shell either side of the crown and one
     along each cheek.  They are geometry, not shading: a black fairing has no
     albedo variation to read, so its whole form is carried by where the
     softbox highlight breaks.                                            */
  const CREASES = [[0.255, 0.030, 0.055], [0.745, 0.030, 0.055],
    [0.400, 0.020, 0.045], [0.600, 0.020, 0.045]];
  const cowlRows = [];
  const cowlSegs = seg(58);
  for (let i = cowlTable.length - 1; i >= 0; i--) {
    const [z, hw, crown, low, nT, nB, pinch] = cowlTable[i];
    const cy = (crown + low) / 2, h = (crown - low) / 2;
    const sec = arcSuper({
      halfW: hw, top: h, bottom: h, cy,
      // pinch < 2 narrows the crown into a central ridge instead of a dome
      nTop: nT, nBot: nB, nTopIn: pinch, nBotIn: nB * 1.25,
      a0: -Math.PI * 0.42, a1: Math.PI * 1.42, segments: cowlSegs,
    });
    const taper = smooth01(clampf((0.918 - z) / 0.20, 0, 1));   // fade out at the tip
    cowlRows.push(sec.map((p, c) => {
      const u = c / cowlSegs;
      let k = 1;
      for (const [uc, depth, wdt] of CREASES) {
        k -= depth * taper * Math.exp(-Math.pow((u - uc) / wdt, 2));
      }
      return V3(p.x * k, cy + (p.y - cy) * k, z);
    }));
  }
  add(g, panelShell(cowlRows, 0.0042), MAT.paintFlat, "body.cowlUpper");
  const cC = cowlRows[0].length;
  addDecal(g, cowlRows, 4, 7, Math.round(cC * 0.06), Math.round(cC * 0.20),
    MAT.decalNinja, "body.decalNinja.R", { flipV: true });
  addDecal(g, cowlRows, 4, 7, Math.round(cC * 0.80), Math.round(cC * 0.94),
    MAT.decalNinja, "body.decalNinja.L", { flipU: true });

  /* lower nose: bridges the headlight aperture down to the side cowls, and
     gives the front its folded chin under the lamps                      */
  const chinTable = [
    [0.620, 0.150, 0.788, 0.694],
    [0.686, 0.148, 0.792, 0.698],
    [0.752, 0.143, 0.794, 0.706],
    [0.812, 0.133, 0.797, 0.720],
    [0.862, 0.118, 0.801, 0.740],
    [0.898, 0.094, 0.812, 0.768],
    [0.918, 0.056, 0.838, 0.808],
  ];
  const chinRows = [];
  for (let i = chinTable.length - 1; i >= 0; i--) {
    const [z, hw, yTop, yBot] = chinTable[i];
    const row = [];
    const N = seg(30);
    for (let c = 0; c <= N; c++) {
      const u = (c / N) * 2 - 1;                         // +X edge -> -X edge
      const k = Math.pow(Math.max(0, 1 - Math.pow(Math.abs(u), 2.4)), 0.40);
      row.push(V3(-u * hw, lerp(yTop, yBot, k), z));
    }
    chinRows.push(row);
  }
  add(g, panelShell(chinRows, 0.0042, { flip: true }), MAT.paintFlat, "body.cowlChin");

  /* ram-air duct in the nose centre */
  const duct = [];
  for (let i = 0; i <= 5; i++) {
    const t = i / 5, z = lerp(0.924, 0.848, t);
    duct.push(roundRect(lerp(0.019, 0.028, t), lerp(0.014, 0.021, t), 0.006, seg(20))
      .map((p) => V3(p.x, p.y + lerp(0.838, 0.834, t), z)));
  }
  add(g, write((w) => w.grid(duct, { closeU: true, flip: true })), MAT.plastic, "body.ramDuct");
  add(g, write((w) => w.fan(duct[duct.length - 1], false)), MAT.screenMesh, "body.ramScreen",
    { cast: false });

  /* Twin LED headlights filling the aperture between cowl and chin.  The
     units are wedges that widen and drop as they run back into the nose,
     which is what gives the ZX-6R its hooded stare.                      */
  for (const s of [1, -1]) {
    const hl = [];
    const RN = seg(7);
    for (let i = 0; i <= RN; i++) {
      const t = i / RN, z = lerp(0.918, 0.822, t);
      const cx = s * lerp(0.036, 0.070, ease(t, 0.85));
      const hw = lerp(0.014, 0.034, ease(t, 0.8));
      const hh = lerp(0.011, 0.026, ease(t, 0.9));
      const cy = lerp(0.850, 0.830, t);
      hl.push(catmull2([
        [-hw, -hh * 0.45], [-hw * 0.62, hh * 0.92], [hw * 0.55, hh],
        [hw, hh * 0.10], [hw * 0.78, -hh * 0.72], [-hw * 0.20, -hh],
      ], seg(30), true).map((p) => V3(cx + p.x * s, cy + p.y, z)));
    }
    add(g, write((w) => { w.grid(hl, { closeU: true }); w.fan(hl[hl.length - 1], false); }),
      MAT.reflector, "body.headlampHousing" + (s > 0 ? "R" : "L"));
    add(g, write((w) => w.fan(hl[0].map((p) => V3(p.x, p.y, p.z + 0.004)), false)),
      MAT.glass, "body.headlampLens" + (s > 0 ? "R" : "L"), { cast: false });
    /* LED projector bar visible through the lens */
    add(g, write((w) => w.grid([
      hl[1].map((p) => V3(p.x * 0.86 + s * 0.006, p.y * 0.0 + hl[1][0].y * 0 + p.y, p.z - 0.006)),
      hl[2].map((p) => V3(p.x * 0.80 + s * 0.008, p.y, p.z - 0.004)),
    ], { closeU: true })), MAT.led, "body.headlampLED" + (s > 0 ? "R" : "L"), { cast: false });
    /* eyebrow position lamp along the top edge of the aperture */
    add(g, sweep(catmull3([
      [s * 0.030, 0.858, 0.908], [s * 0.052, 0.854, 0.878], [s * 0.072, 0.846, 0.846],
    ], seg(8)), () => roundRect(0.0035, 0.0050, 0.0018, seg(10)), { upright: true }),
      MAT.led, "body.positionLamp" + (s > 0 ? "R" : "L"), { cast: false });
  }

  /* Windscreen.  Its lower edge has to sit ON the cowl crown, which is a domed
     section, not a straight line — so sample the same station table the cowl
     was lofted from and let each column find its own seating height.  The
     correction fades out toward the top, where the double-bubble takes over. */
  const cowlCrownY = (z, x) => {
    const T = cowlTable;
    let i = 0;
    while (i < T.length - 2 && T[i + 1][0] < z) i++;
    const k = clampf((z - T[i][0]) / (T[i + 1][0] - T[i][0]), 0, 1);
    const L = (n) => lerp(T[i][n], T[i + 1][n], k);
    const hw = L(1), crown = L(2), low = L(3), nT = L(4), pinch = L(6);
    const cy = (crown + low) / 2, h = (crown - low) / 2;
    const ca = Math.pow(clampf(Math.abs(x) / hw, 0, 1), pinch / 2);
    const sa = Math.sqrt(Math.max(0, 1 - ca * ca));
    // the pressed creases sit the real surface a little inside the analytic one
    return cy + Math.pow(sa, 2 / nT) * h - 0.0025;
  };
  const scrPath = catmull3([
    [0, 0.928, 0.804], [0, 0.968, 0.760], [0, 1.014, 0.708],
    [0, 1.056, 0.660], [0, B.screenTopY, B.screenTopZ],
  ], seg(14));
  const scrRows = [];
  const scrHW = (t) => lerp(0.126, 0.092, ease(t, 0.9));
  const seatCentre = cowlCrownY(scrPath[0].z, 0);
  for (let i = 0; i < scrPath.length; i++) {
    const t = i / (scrPath.length - 1);
    const hw = scrHW(t);
    const row = [];
    const N = seg(24);
    for (let c = 0; c <= N; c++) {
      const u = (c / N) * 2 - 1, au = Math.abs(u);
      const z = scrPath[i].z + 0.014 * Math.pow(au, 2.0);
      // how far the cowl crown falls away at this lateral offset
      const seat = cowlCrownY(z, u * scrHW(0)) - seatCentre;
      // double bubble: raised centre spine between two shoulder troughs
      const bump = 0.010 * Math.exp(-Math.pow(u / 0.30, 2))
        - 0.004 * Math.exp(-Math.pow((au - 0.62) / 0.22, 2));
      row.push(V3(u * hw,
        scrPath[i].y + bump * (1 - t * 0.5)
          + seat * Math.pow(1 - t, 1.6)                 // seat on the cowl
          - 0.016 * Math.pow(au, 2.4) * t,              // residual sag up top
        z));
    }
    scrRows.push(row);
  }
  add(g, panelShell(scrRows, 0.0032), MAT.screen, "body.windscreen", { cast: false });

  /* instrument cluster under the screen */
  add(g, xform(filletBox(0.148, 0.026, 0.084, 0.010, { segments: seg(20), rings: seg(7) }),
    M.c(M.t(0, 0.964, 0.614), M.rx(-0.62))), MAT.plastic, "body.dashShell");
  add(g, xform(write((w) => extrudePlate(roundRect(0.060, 0.029, 0.010, seg(36)), 0.003,
    { axis: "z", bevel: 0.001, w })), M.c(M.t(0, 0.974, 0.629), M.rx(-0.62))),
    MAT.gauge, "body.dashFace");

  /* mirrors on winglet stalks, indicator lens in the leading edge */
  for (const s of [1, -1]) {
    /* Slim stalk: the housing carries the visual weight, so the arm stays
       narrow — a thick arm is what makes a mirror read as a bar.        */
    add(g, sweep(catmull3([
      [s * 0.112, 0.936, 0.690], [s * 0.168, 0.962, 0.680],
      [s * 0.224, 0.984, 0.666], [s * 0.268, 0.996, 0.654],
    ], seg(12)), (t) => roundRect(lerp(0.017, 0.009, t), lerp(0.019, 0.013, t), 0.005, seg(16)),
      { upright: true }), MAT.paintFlat, "body.mirrorStalk" + (s > 0 ? "R" : "L"));
    /* Housing: a teardrop shell that grows rearward to the glass face */
    // solve the housing origin so its outer edge lands on the overall width
    const hx = s * (B.mirrorHalfW - 0.076);
    const head = [];
    const HN = seg(8);
    for (let i = 0; i <= HN; i++) {
      const t = i / HN;
      const z = lerp(0.700, 0.594, t);
      const hw = lerp(0.010, 0.050, ease(t, 0.62));
      const hh = lerp(0.009, 0.037, ease(t, 0.55));
      head.push(catmull2([
        [-hw, -hh * 0.55], [-hw * 0.55, hh], [hw * 0.62, hh * 0.90],
        [hw, -hh * 0.15], [hw * 0.30, -hh],
      ], seg(30), true).map((p) => V3(hx + s * (0.026 * t) + p.x * s, 1.004 + p.y, z)));
    }
    add(g, orient(write((w) => {
      w.grid(head, { closeU: true });
      w.fan(head[0], true); w.fan(head[HN], false);
    })), MAT.paintFlat, "body.mirrorHead" + (s > 0 ? "R" : "L"));
    /* glass inset into the rear face */
    add(g, write((w) => w.fan(head[HN].map((p) =>
      V3(hx + s * 0.026 + (p.x - hx - s * 0.026) * 0.90, 1.004 + (p.y - 1.004) * 0.90,
        p.z + 0.004)), false)),
      MAT.chrome, "body.mirrorGlass" + (s > 0 ? "R" : "L"), { cast: false });
    /* indicator lens moulded into the leading edge */
    add(g, write((w) => w.grid([
      head[1].map((p) => V3(p.x, p.y, p.z + 0.002)),
      head[2].map((p) => V3(p.x, p.y, p.z + 0.001)),
    ], { closeU: true })), MAT.lensAmber,
      "body.indicatorFront" + (s > 0 ? "R" : "L"), { cast: false });
  }

  /* ======================================================================
     7.5 SIDE COWLS — flank panels from under the mirror to the belly,
     carrying the ZX-6R graphic and a hot-air louvre over the radiator.
     ==================================================================== */
  /* Each row is a flow line from the top edge down to the bottom edge.  The
     bottom of a row sits FORWARD of its top, so the trailing edge rakes
     forward as it descends instead of ending in a guillotine cut.       */
  const flankTable = [
    // zTop,  yTop,  zBot,  yBot,  halfW, edgeTuck
    [0.020, 0.648, 0.132, 0.318, 0.124, 0.60],
    [0.090, 0.678, 0.176, 0.330, 0.146, 0.58],
    [0.170, 0.710, 0.228, 0.352, 0.164, 0.56],
    [0.250, 0.738, 0.284, 0.384, 0.178, 0.55],
    [0.330, 0.760, 0.342, 0.428, 0.186, 0.54],
    [0.410, 0.778, 0.404, 0.486, 0.187, 0.54],
    [0.490, 0.792, 0.468, 0.554, 0.180, 0.56],
    [0.560, 0.804, 0.528, 0.630, 0.167, 0.58],
    [0.620, 0.814, 0.582, 0.706, 0.148, 0.62],
  ];
  const flankRows = (s) => {
    const rows = [];
    for (let i = flankTable.length - 1; i >= 0; i--) {
      const [zTop, yTop, zBot, yBot, hw, tuck] = flankTable[i];
      const row = [];
      const N = seg(30);
      for (let c = 0; c <= N; c++) {
        const v = c / N;                                    // top edge -> bottom edge
        let k = Math.pow(Math.sin(Math.PI * (0.10 + 0.80 * v)), 0.42);
        k = lerp(tuck, 1, k);
        // sharp feature line running the length of the panel
        k *= 1 - 0.075 * Math.exp(-Math.pow((v - 0.44) / 0.055, 2));
        row.push(V3(s * hw * k, lerp(yTop, yBot, ease(v, 1.12)), lerp(zTop, zBot, ease(v, 1.35))));
      }
      rows.push(row);
    }
    return rows;
  };
  for (const s of [1, -1]) {
    const rows = flankRows(s);
    add(g, panelShell(rows, 0.0042, { flip: s < 0 }), MAT.paintFlat,
      "body.sideCowl" + (s > 0 ? "R" : "L"));
    const R = rows.length, C = rows[0].length;
    addDecal(g, rows, Math.round(R * 0.32), Math.round(R * 0.54),
      Math.round(C * 0.10), Math.round(C * 0.44), MAT.decalZX6R,
      "body.decalZX6R" + (s > 0 ? "R" : "L"), { flipU: s < 0 });
    addDecal(g, rows, Math.round(R * 0.70), Math.round(R * 0.86),
      Math.round(C * 0.50), Math.round(C * 0.86), MAT.decalKawasaki,
      "body.decalKawasaki" + (s > 0 ? "R" : "L"), { flipU: s < 0 });
    /* hot-air louvre over the radiator, recessed into the panel */
    const vent = decalPatch(rows, 1, 4, Math.round(C * 0.14), Math.round(C * 0.40), -0.005);
    add(g, write((w) => w.grid(vent, { flip: vent.inward })),
      MAT.screenMesh, "body.sideVent" + (s > 0 ? "R" : "L"), { cast: false });
    /* inner return lip so the lower cut edge never shows hollow */
    const lip = decalPatch(rows, 0, R - 1, C - 3, C - 1, -0.018);
    add(g, write((w) => w.grid(lip, { flip: lip.inward })),
      MAT.plastic, "body.sideLip" + (s > 0 ? "R" : "L"), { cast: false });
  }

  /* ======================================================================
     7.6 BELLY PAN
     ==================================================================== */
  const bellyTable = [
    [-0.250, 0.052, 0.288, 0.242], [-0.160, 0.086, 0.278, 0.214],
    [-0.060, 0.113, 0.284, 0.194], [0.040, 0.126, 0.302, 0.182],
    [0.140, 0.130, 0.330, 0.182], [0.230, 0.126, 0.364, 0.194],
    [0.300, 0.116, 0.402, 0.218], [0.348, 0.100, 0.444, 0.258],
  ];
  const bellyRows = [];
  for (let i = bellyTable.length - 1; i >= 0; i--) {
    const [z, hw, yTop, yBot] = bellyTable[i];
    const row = [];
    const N = seg(30);
    for (let c = 0; c <= N; c++) {
      const u = (c / N) * 2 - 1;                            // +X edge -> -X edge
      const k = Math.pow(Math.max(0, 1 - Math.pow(Math.abs(u), 2.6)), 0.45);
      row.push(V3(-u * hw, lerp(yTop, yBot, k), z));
    }
    bellyRows.push(row);
  }
  add(g, panelShell(bellyRows, 0.0042, { flip: true }), MAT.paintFlat, "body.bellyPan");
  const bR = bellyRows.length, bC = bellyRows[0].length;
  addDecal(g, bellyRows, Math.round(bR * 0.44), Math.round(bR * 0.64),
    Math.round(bC * 0.58), Math.round(bC * 0.90), MAT.decalKawasaki, "body.decalBelly",
    { flipU: true });

  /* ======================================================================
     7.7 FENDERS
     ==================================================================== */
  /* Front mudguard.  Angles are measured in the wheel frame from straight
     ahead (0) through vertical (pi/2) to straight back (pi).  The guard has to
     reach past the fork axis, which sits at 90deg + rake = 113.5deg, otherwise
     it stops over the crown and reads as a floating shell.
     Its section is not a bent sheet: a raised centre spine, a crease either
     side of it, and skirts that curl down outboard of the tyre shoulders.  */
  const fenderA0 = 0.55, fenderA1 = 2.22;
  const forkA = Math.PI / 2 + D.rake;                 // where the fork crosses
  const fenderGap = (t) => 0.024 + 0.020 * Math.sin(Math.PI * clampf(t, 0, 1));
  const fenderHW = (t) => 0.086 - 0.040 * Math.pow(1 - t, 2.2);
  const fFender = [];
  {
    const RN = seg(26), N = seg(38);
    for (let i = 0; i <= RN; i++) {
      const t = i / RN;
      const a = lerp(fenderA0, fenderA1, t);
      const r = D.front.tyreR + fenderGap(t);
      const hw = fenderHW(t);
      // only let the skirt fall once the edge clears the tyre's half width
      const skirt = clampf((hw - D.front.tyreW * 0.46) / 0.028, 0, 1);
      const row = [];
      for (let c = 0; c <= N; c++) {
        const u = (c / N) * 2 - 1, au = Math.abs(u);
        let rr = r
          + 0.0042 * Math.exp(-Math.pow(u / 0.30, 2))              // centre spine
          - 0.0030 * Math.exp(-Math.pow((au - 0.46) / 0.09, 2))    // flanking crease
          - 0.044 * skirt * Math.pow(clampf((au - 0.32) / 0.68, 0, 1), 1.7);
        // the tip and tail pinch in slightly in plan
        const k = 1 - 0.10 * Math.pow(au, 6);
        row.push(V3(-u * hw * k,
          D.front.axle[1] + Math.sin(a) * rr, D.front.axle[0] + Math.cos(a) * rr));
      }
      fFender.push(row);
    }
  }
  add(g, panelShell(fFender, 0.0040, { flip: true }), MAT.paintFlat, "body.frontFender");
  /* mounting ears bridging the guard's flank to the fork sliders, on the fork
     axis so they land wherever rake puts the legs */
  {
    const t = (forkA - fenderA0) / (fenderA1 - fenderA0);
    const r = D.front.tyreR + fenderGap(t);
    const my = D.front.axle[1] + Math.sin(forkA) * r;
    const mz = D.front.axle[0] + Math.cos(forkA) * r;
    const mx = (fenderHW(t) + D.fork.halfTrack) / 2;
    pair(g, filletBox(D.fork.halfTrack - fenderHW(t) + 0.016, 0.022, 0.038, 0.006,
      { segments: seg(16), rings: seg(6) }).translate(mx, my, mz),
      MAT.paintFlat, "body.fenderStay");
    pair(g, xform(socketBolt(0.0050, 0.008), M.c(M.t(D.fork.halfTrack - 0.030, my, mz),
      M.rz(Math.PI / 2))), MAT.boltDark, "body.fenderBolt");
  }

  /* No rear guard.  Nothing covers the rear tyre at all: the wheel is open
     from swingarm to tail, and the only bodywork behind the seat unit is the
     plate bracket below.  A shell here is a defect — the part does not exist
     on this machine, and adding one fills the negative space that gives the
     tail its lift.                                                        */

  /* ======================================================================
     7.8 PLATE HANGER + INDICATORS
     ==================================================================== */
  add(g, sweep(catmull3([
    [0, 0.816, -0.788], [0, 0.756, -0.848], [0, 0.682, -0.908], [0, 0.606, -0.952],
  ], seg(12)), (t) => roundRect(lerp(0.026, 0.052, t), lerp(0.012, 0.006, t), 0.004, seg(16)),
    { upright: true }), MAT.plastic, "body.plateHanger");
  add(g, xform(write((w) => extrudePlate(roundRect(0.090, 0.058, 0.006, seg(40)), 0.003,
    { axis: "z", bevel: 0.001, w })), M.c(M.t(0, 0.588, B.plateZ + 0.008), M.rx(0.34))),
    MAT.plastic, "body.plate");
  add(g, xform(write((w) => extrudePlate(roundRect(0.082, 0.050, 0.005, seg(40)), 0.002,
    { axis: "z", bevel: 0.0008, w })), M.c(M.t(0, 0.588, B.plateZ + 0.012), M.rx(0.34))),
    MAT.plate, "body.plateFace");
  for (const s of [1, -1]) {
    add(g, tube(catmull3([
      [s * 0.026, 0.700, -0.906], [s * 0.086, 0.712, -0.918], [s * 0.130, 0.722, -0.926],
    ], seg(10)), 0.0068, seg(12)), MAT.plastic, "body.indStalk" + (s > 0 ? "R" : "L"));
    add(g, xform(revolve([
      V2(0, 0), V2(0.019, 0.002), V2(0.021, 0.012), V2(0.016, 0.024), V2(0, 0.028),
    ], { axis: "x", segments: seg(22), capStart: true }),
      M.t(s * 0.130, 0.722, -0.926)), MAT.lensAmber, "body.indRear" + (s > 0 ? "R" : "L"));
  }
  add(g, xform(write((w) => extrudePlate(roundRect(0.026, 0.014, 0.005, seg(24)), 0.004,
    { axis: "z", bevel: 0.001, w })), M.c(M.t(0, 0.534, -0.960), M.rx(0.34))),
    MAT.lensRed, "body.reflector");

  /* ======================================================================
     7.9 INNER PANELS
     ==================================================================== */
  add(g, loftZ([
    { z: 0.372, sec: secMove(roundRect(0.086, 0.030, 0.014, seg(28)), 0, 0.792) },
    { z: 0.300, sec: secMove(roundRect(0.108, 0.038, 0.016, seg(28)), 0, 0.776) },
    { z: 0.200, sec: secMove(roundRect(0.116, 0.044, 0.018, seg(28)), 0, 0.762) },
    { z: 0.100, sec: secMove(roundRect(0.112, 0.042, 0.018, seg(28)), 0, 0.758) },
    { z: 0.020, sec: secMove(roundRect(0.098, 0.036, 0.016, seg(28)), 0, 0.764) },
  ]), MAT.plastic, "body.airboxCover");
  add(g, sweep(catmull3([
    [-0.092, D.pivot[1] + 0.074, D.pivot[0] - 0.150],
    [-0.096, D.rear.axle[1] + 0.088, D.rear.axle[0] + 0.220],
    [-0.096, D.rear.axle[1] + 0.080, D.rear.axle[0] + 0.090],
  ], seg(12)), () => roundRect(0.020, 0.008, 0.005, seg(14)), { upright: true }),
    MAT.plastic, "body.chainGuard");
  return g;
}


export {
  addDecal, arcSuper, buildBody, buildControls, buildEngine, buildFrame, buildFrontEnd, buildSwingarm, chainPath, decalPatch, fractf, frameSparSection, helixPath, hexBolt, loftClosed, loftY, loftZ, makeCaliper, makeChain, makeRotor, makeSprocket, makeTyre, makeWheel, petalPoly, resampleTable, revolveAlong, revolveAlongPts, rimSection, rotorAlphaFor, socketBolt, spokeArm, sprocketPoly, tyreProfile,
};
