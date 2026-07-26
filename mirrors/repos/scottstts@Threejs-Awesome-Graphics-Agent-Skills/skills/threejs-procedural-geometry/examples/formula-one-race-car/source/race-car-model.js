import * as THREE from "three/webgpu";
import {
  PART_LOG, PI, TAU, V2, V3, airfoilLoop, clamp01, curve1, gridGeometry, latheX, latheY,
  lerp, loftLoops, logPart, merge, mirrorX, plate, smooth01, smoother01, spline2, squircle,
  sweepSection, sweepTube, wingLoft, xform,
} from "./mesh-kit.js";
import { D } from "./design-contract.js";
import { MAT, TEX, U, buildMaterials } from "./race-car-materials.js";

/* =====================================================================================
   SECTION PLANS
   Bodywork is authored the way it is drawn: as semantic cross-sections swept along the
   car's longitudinal axis.  Each section is a fixed set of NAMED control points, so a
   parameter curve can move "max width" or "rim height" along the car without changing
   topology.  Triangle emission happens only at the end.
   ===================================================================================== */

/**
 * Centreline body half-section, 13 semantic control points running from the top
 * centreline, out over the deck/rim, down the flank, and back to the bottom centreline.
 * `tub` opens the section into a cockpit recess without changing the point count, which
 * is what lets the nose, cockpit and engine cover be ONE continuous loft.
 */
function chassisPts({ yRim, wRim, halfW, yShoulder, yBot, wBot, tub = 0, wTub = 0.18,
                      waist = 0, chine = 0.010, crown = 0.55, belly = 0.5 }){
  const open  = tub > 0.004;
  const yFloor = yRim - tub;
  const wFloor = open ? wTub : wRim * 0.30;
  const wWall  = open ? wTub * 1.10 : wRim * 0.66;
  const wallT  = open ? 0.62 : 0.42;                    // where the wall sample sits
  const dInner = open ? 0.004 : (yRim - yFloor) * crown * 0.30;
  return [
    [0,                              yFloor],
    [wFloor,                         yFloor + dInner],
    [wWall,                          yFloor + (yRim - yFloor) * wallT],
    [wRim * 0.94,                    yRim - (open ? 0.006 : 0.004)],
    [wRim,                           yRim],
    [lerp(wRim, halfW, 0.34),        lerp(yRim, yShoulder, 0.26)],
    [lerp(wRim, halfW, 0.76),        lerp(yRim, yShoulder, 0.68)],
    [halfW,                          yShoulder],
    [lerp(halfW, wBot, 0.26) - waist,        lerp(yShoulder, yBot, 0.30 * belly * 2)],
    [lerp(halfW, wBot, 0.68) - waist * 0.55, lerp(yShoulder, yBot, 0.72)],
    [wBot,                           yBot + chine],
    [wBot * 0.52,                    yBot + chine * 0.16],
    [0,                              yBot],
  ];
}

/**
 * Offset closed section for volumes that are not on the centreline (sidepods).
 * Four superellipse quadrants with independent exponents plus a lower-outboard
 * undercut — the term that actually creates the coke-bottle.
 */
function podPts({ xIn, xOut, yTop, yBot, nTop = 3.6, nBot = 2.4, nIn = 2.6,
                  undercut = 0, ucY = 0.5, ucW = 0.30, shelf = 0 }, n = 60){
  const cx = (xIn + xOut) * 0.5, cy = (yTop + yBot) * 0.5;
  const rOut = xOut - cx, rIn = cx - xIn, rTop = yTop - cy, rBot = cy - yBot;
  const pts = [];
  const q = (count, fx, fy) => { for (let i = 0; i < count; i++){ const a = (i / count) * PI * 0.5; pts.push([fx(a), fy(a)]); } };
  const sp = (v, e) => Math.pow(Math.max(v, 0), 2 / e);
  const nq = Math.max(6, n >> 2);
  q(nq, a => cx + rOut * sp(Math.sin(a), nTop),  a => cy + rTop * sp(Math.cos(a), nTop));   // top -> outboard
  q(nq, a => cx + rOut * sp(Math.cos(a), nBot),  a => cy - rBot * sp(Math.sin(a), nBot));   // outboard -> bottom
  q(nq, a => cx - rIn  * sp(Math.sin(a), nBot),  a => cy - rBot * sp(Math.cos(a), nBot));   // bottom -> inboard
  q(nq, a => cx - rIn  * sp(Math.cos(a), nIn),   a => cy + rTop * sp(Math.sin(a), nIn));    // inboard -> top
  if (undercut || shelf){
    const yU = lerp(yBot, yTop, ucY), h = (yTop - yBot) * ucW;
    for (const p of pts){
      const out = clamp01((p[0] - cx) / Math.max(rOut, 1e-4));
      if (undercut && out > 0){
        const g = Math.exp(-Math.pow((p[1] - yU) / h, 2));
        p[0] -= undercut * rOut * g * out;
      }
      if (shelf && out > 0.25 && p[1] > cy){                  // flat aero shelf on the shoulder
        const g = clamp01((p[1] - cy) / Math.max(rTop, 1e-4));
        p[1] -= shelf * rTop * g * g * out;
      }
    }
  }
  return pts;
}

/** Resample an open half-outline and mirror it into a closed ring at station z. */
function ringFromHalf(pts, z, n){
  const half = spline2(pts.map(p => V2(p[0], p[1])), n, { closed: false });
  const loop = [];
  for (let i = 0; i < n; i++) loop.push(V3(half[i].x, half[i].y, z));
  for (let i = n - 2; i > 0; i--) loop.push(V3(-half[i].x, half[i].y, z));
  return loop;
}
/** Resample a closed outline into a ring at station z. */
function ringFromClosed(pts, z, n){
  const loop2 = spline2(pts.map(p => V2(p[0], p[1])), n, { closed: true });
  return loop2.map(p => V3(p.x, p.y, z));
}

/** Evaluate a table of named parameter curves at z. */
function paramTrack(table){
  const curves = {};
  for (const k in table) curves[k] = curve1(table[k]);
  return (z) => { const o = {}; for (const k in curves) o[k] = curves[k](z); return o; };
}

/** Longitudinal sampling, optionally eased so ends carry more rings than the middle. */
function stationsFrom(zStart, zEnd, count, ease = 0){
  const zs = [];
  for (let i = 0; i <= count; i++){
    const t = i / count;
    const e = ease ? lerp(t, t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t), ease) : t;
    zs.push(lerp(zStart, zEnd, e));
  }
  return zs;
}
/* =====================================================================================
   BODYWORK
   The nose, survival cell, cockpit tub and engine cover are ONE continuous loft driven
   by parameter curves.  The cockpit is not a hole cut into a closed shell: the section
   itself opens into a recess (`tub`) and closes again, exactly like a lofted surface
   model.  Sidepods, floor, diffuser, airbox and halo are separate volumes positioned
   from the same contract.
   ===================================================================================== */

const BODY_RING = 96;          // ring resolution of the main hull
const BODY_ROWS = 168;         // longitudinal rings

/* ---- parameter curves for the main hull -------------------------------------------- */
const HULL = paramTrack({
  // deck / rim height along the car
  yRim: [[2.755,0.3520],[2.620,0.3960],[2.420,0.4400],[2.180,0.4850],[1.905,0.5460],
         [1.700,0.5790],[1.450,0.5980],[1.200,0.6010],[1.075,0.5990],[0.900,0.5900],
         [0.640,0.5830],[0.300,0.5790],[0.115,0.5760],[0.020,0.5900],[-0.070,0.6600],
         [-0.150,0.7600],[-0.235,0.8400],[-0.340,0.8200],[-0.560,0.7620],[-0.860,0.6820],
         [-1.150,0.5900],[-1.400,0.5020],[-1.560,0.4400],[-1.680,0.3900]],
  // half-width of the deck / rim
  wRim: [[2.755,0.0230],[2.620,0.0470],[2.420,0.0790],[2.180,0.1090],[1.905,0.1420],
         [1.700,0.1720],[1.450,0.2180],[1.200,0.2680],[1.075,0.2860],[0.900,0.2960],
         [0.640,0.3020],[0.300,0.3040],[0.115,0.3010],[0.020,0.2900],[-0.070,0.2500],
         [-0.150,0.2050],[-0.235,0.1780],[-0.340,0.1720],[-0.560,0.1600],[-0.860,0.1380],
         [-1.150,0.1100],[-1.400,0.0800],[-1.560,0.0600],[-1.680,0.0440]],
  // absolute maximum half-width of the section
  halfW: [[2.755,0.0300],[2.620,0.0620],[2.420,0.0990],[2.180,0.1340],[1.905,0.1780],
          [1.700,0.2160],[1.450,0.2680],[1.200,0.3150],[1.075,0.3350],[0.900,0.3560],
          [0.640,0.3720],[0.300,0.3860],[0.115,0.3840],[0.020,0.3760],[-0.070,0.3520],
          [-0.150,0.3220],[-0.235,0.3020],[-0.340,0.2960],[-0.560,0.2760],[-0.860,0.2380],
          [-1.150,0.1900],[-1.400,0.1380],[-1.560,0.1020],[-1.680,0.0740]],
  yShoulder: [[2.755,0.3260],[2.620,0.3480],[2.420,0.3720],[2.180,0.3900],[1.905,0.3980],
              [1.700,0.3900],[1.450,0.3720],[1.200,0.3560],[1.075,0.3480],[0.900,0.3400],
              [0.640,0.3340],[0.300,0.3280],[0.115,0.3260],[0.020,0.3320],[-0.070,0.3600],
              [-0.235,0.4200],[-0.560,0.4100],[-0.860,0.3760],[-1.150,0.3340],[-1.400,0.2960],
              [-1.680,0.2620]],
  yBot: [[2.755,0.3020],[2.620,0.2880],[2.420,0.2760],[2.180,0.2660],[1.905,0.2520],
         [1.700,0.2100],[1.450,0.1620],[1.200,0.1340],[1.075,0.1260],[0.900,0.1200],
         [0.640,0.1160],[0.300,0.1140],[0.115,0.1140],[0.020,0.1160],[-0.070,0.1220],
         [-0.235,0.1400],[-0.560,0.1620],[-0.860,0.1800],[-1.150,0.1960],[-1.400,0.2120],
         [-1.680,0.2280]],
  wBot: [[2.755,0.0200],[2.620,0.0430],[2.420,0.0740],[2.180,0.1000],[1.905,0.1320],
         [1.700,0.1680],[1.450,0.2020],[1.200,0.2280],[1.075,0.2380],[0.900,0.2460],
         [0.640,0.2520],[0.300,0.2540],[0.115,0.2520],[0.020,0.2460],[-0.070,0.2320],
         [-0.235,0.2020],[-0.560,0.1780],[-0.860,0.1500],[-1.150,0.1180],[-1.400,0.0860],
         [-1.680,0.0600]],
  // cockpit recess: opens just behind the front bulkhead, closes at the headrest
  tub:  [[1.180,0.0000],[1.120,0.0400],[1.020,0.2500],[0.900,0.2860],[0.500,0.2960],
         [0.220,0.2900],[0.115,0.2680],[0.040,0.1200],[-0.010,0.0000]],
  wTub: [[1.120,0.0700],[1.000,0.1500],[0.860,0.1880],[0.500,0.2020],[0.220,0.1960],
         [0.080,0.1500],[0.000,0.0700]],
  // lateral waist between the shoulder and the floor joint
  waist:[[2.755,0.0000],[1.905,0.0060],[1.450,0.0180],[1.075,0.0280],[0.640,0.0320],
         [0.115,0.0300],[-0.235,0.0220],[-0.860,0.0140],[-1.680,0.0040]],
  chine:[[2.755,0.0040],[1.905,0.0090],[1.075,0.0130],[0.115,0.0140],[-0.560,0.0120],[-1.680,0.0070]],
  crown:[[2.755,0.7000],[1.905,0.6200],[1.200,0.5400],[-0.235,0.5000],[-1.680,0.5600]],
});

function buildHull(){
  const zs = stationsFrom(D.noseTipZ, D.engineCoverEndZ, BODY_ROWS, 0.35);
  const loops = zs.map(z => ringFromHalf(chassisPts(HULL(z)), z, BODY_RING / 2 + 1));
  const g = loftLoops(loops, { capStart: true, capEnd: true, capSegs: 5, capBulge: 0.42 });
  return logPart('hull:nose+monocoque+enginecover', g);
}

/** Padded liner just inside the cockpit recess, so the paint projector never shows
 *  through the opening.  It reuses the hull's own section points, contracted toward the
 *  recess axis.  Emitted as an OPEN sheet — closing the ring here would lid the cockpit. */
function buildCockpitLiner(){
  const zs = stationsFrom(1.140, 0.005, 62);
  const rows = zs.map(z => {
    const p = HULL(z);
    const pts = chassisPts(p).slice(0, 5);
    const axis = V2(0, p.yRim);
    const inset = 0.0045;
    const shrunk = pts.map(q => {
      const dx = q[0] - axis.x, dy = q[1] - axis.y, L = Math.hypot(dx, dy) || 1;
      return V2(q[0] - (dx / L) * inset, q[1] - (dy / L) * inset);
    });
    shrunk[0].x = 0;
    const half = spline2(shrunk, 24, { closed: false });
    const row = [];
    for (let i = 23; i > 0; i--) row.push(V3(-half[i].x, half[i].y, z));   // left rim -> centre
    for (let i = 0; i < 24; i++) row.push(V3( half[i].x, half[i].y, z));   // centre -> right rim
    return row;
  });
  return logPart('cockpit:liner', gridGeometry(rows, { closeU: false, flip: true }));
}

/** Cockpit rim: a swept bead around the opening — the crisp highlight that reads the
 *  aperture in every three-quarter view.  The bead half-width tapers to zero at both
 *  ends of the aperture so the loop closes on the centreline without a spike. */
function buildCockpitRim(){
  const zF = 1.152, zR = 0.002;
  const zs = stationsFrom(zF, zR, 66);
  const path = zs.map(z => {
    const p = HULL(z);
    const taper = smooth01(clamp01((zF - z) / 0.115)) * smooth01(clamp01((z - zR) / 0.100));
    return V3(p.wRim * taper, p.yRim + 0.0030 * taper, z);
  });
  const sec = (t) => {
    const s = Math.min(smooth01(clamp01(t / 0.10)), smooth01(clamp01((1 - t) / 0.10)));
    return squircle(0.0135 * lerp(0.35, 1, s), 0.0090 * lerp(0.35, 1, s), 2.6, 12);
  };
  const a = sweepSection(path, sec, { capStart: true, capEnd: true, capSegs: 3 });
  return logPart('cockpit:rim', merge([a, mirrorX(a)]));
}

/* ---- sidepods ---------------------------------------------------------------------- */
/* A 2026 sidepod is LOW and slab-sided, not a bulbous pontoon: a flat aero shelf on top,
   a hard shoulder, and a deep undercut that eats the lower outboard corner. */
const POD = paramTrack({
  xIn:  [[0.768,0.2660],[0.640,0.2520],[0.400,0.2400],[0.000,0.2320],
         [-0.400,0.2340],[-0.900,0.2120],[-1.320,0.1620]],
  xOut: [[0.768,0.5560],[0.640,0.6440],[0.400,0.7000],[0.000,0.7160],
         [-0.400,0.6780],[-0.900,0.5160],[-1.320,0.2420]],
  // straight top and bottom rails: an F1 sidepod is a wedge in profile, not a lozenge
  yTop: [[0.768,0.4640],[0.640,0.4740],[0.400,0.4780],[0.000,0.4700],
         [-0.400,0.4460],[-0.900,0.4020],[-1.320,0.3480]],
  yBot: [[0.768,0.2520],[0.640,0.2280],[0.400,0.2100],[0.000,0.2000],
         [-0.400,0.2020],[-0.900,0.2220],[-1.320,0.2640]],
  undercut: [[0.768,0.0400],[0.640,0.1800],[0.400,0.4200],[0.000,0.5800],
             [-0.400,0.6200],[-0.900,0.5000],[-1.320,0.2800]],
  ucY:  [[0.768,0.3000],[0.400,0.2200],[0.000,0.1700],[-0.900,0.2200],[-1.320,0.3000]],
  ucW:  [[0.768,0.4200],[0.000,0.3600],[-1.320,0.4200]],
  shelf:[[0.768,0.0800],[0.400,0.2200],[0.000,0.2600],[-0.900,0.1800],[-1.320,0.0600]],
  // very high top exponent => flat aero shelf meeting the flank on a hard crease
  nTop: [[0.768,5.0000],[0.400,6.2000],[0.000,6.6000],[-0.600,5.4000],[-1.320,3.6000]],
  nBot: [[0.768,3.2000],[0.000,3.6000],[-1.320,2.8000]],
  nIn:  [[0.768,3.2000],[0.000,3.4000],[-1.320,3.0000]],
});

const POD_FRONT_Z = 0.7680;      // the plane the inlet mouth lives in

function buildSidepod(){
  // front is left OPEN: the inlet lip ring closes it with a real aperture
  const zs = stationsFrom(POD_FRONT_Z, -1.320, 100, 0.25);
  const loops = zs.map(z => ringFromClosed(podPts(POD(z), 64), z, 72));
  const body = loftLoops(loops, { capStart: false, capEnd: true, capSegs: 5, capBulge: 0.55 });
  return logPart('sidepod:shell', body);
}

/** Inlet: a real aperture — the lip ring's OUTER outline is the sidepod's own front
 *  section, so mouth, lip and shell share one parameterisation and cannot drift apart. */
function buildSidepodInlet(){
  const zLip = POD_FRONT_Z;
  const p = POD(zLip);
  const outer = podPts(p, 64);
  const cx = (p.xIn + p.xOut) * 0.5, cy = (p.yTop + p.yBot) * 0.5;
  const inner = outer.map(q => [cx + (q[0] - cx) * 0.815, cy + (q[1] - cy) * 0.660]);
  const lip = plate(spline2(outer.map(q => V2(q[0], q[1])), 110, { closed: true }), {
    thickness: 0.026, bevel: 0.0065, bevelSegs: 3,
    holes: [spline2(inner.map(q => V2(q[0], q[1])), 96, { closed: true }).reverse()],
  });
  lip.translate(0, 0, zLip - 0.004);

  // throat: contracts and turns inboard as it runs back toward the radiator face
  const throat = [];
  for (let i = 0; i <= 26; i++){
    const t = i / 26, z = lerp(zLip - 0.014, 0.336, t);
    const s = lerp(1.0, 0.54, smooth01(t));
    const shift = -0.100 * smooth01(t);
    throat.push(ringFromClosed(inner.map(q => [cx + (q[0] - cx) * s + shift, cy + (q[1] - cy) * s - 0.012 * t]), z, 60));
  }
  const duct = loftLoops(throat, { flip: true, capEnd: true, capSegs: 3 });
  return { lip: logPart('sidepod:inletLip', lip), duct: logPart('sidepod:inletDuct', duct) };
}

/** Cooling exit louvres: a compact stack of longitudinal slots on the engine-cover
 *  shoulder, each one sunk into the local surface rather than floating on it. */
function buildLouvres(){
  const parts = [];
  const ROWS = 5, COLS = 4;
  for (let row = 0; row < ROWS; row++){
    for (let i = 0; i < COLS; i++){
      const z = -0.560 - i * 0.132;
      const p = HULL(z);
      const t = row / (ROWS - 1);
      const yc = lerp(p.yRim - 0.020, p.yShoulder + 0.020, t);
      const w  = (0.088 - i * 0.011) * (1 - 0.20 * Math.abs(t - 0.5) * 2);
      const h  = 0.0085;
      const outline = [];
      const N = 22;
      for (let k = 0; k < N; k++){
        const a = k / N * TAU;
        outline.push(V2(Math.cos(a) * w * 0.5, Math.sin(a) * h * 0.5));
      }
      const g = plate(outline, { thickness: 0.016, bevel: 0.0022 });
      g.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
      // ride the flank: interpolate x between the rim crest and the max-width station
      const xr = lerp(p.wRim, p.halfW, smooth01(t)) - 0.004;
      g.translate(xr, yc, z);
      parts.push(g, mirrorX(g));
    }
  }
  return logPart('enginecover:louvres', merge(parts));
}

/* ---- airbox and roll structure ----------------------------------------------------- */
/** Rounded-triangle roll-hoop intake.  Shell, lip and throat are ONE folded surface:
 *  the loft runs back over the outside, turns through the lip, and continues forward
 *  into the duct — so the aperture can never separate from the bodywork around it. */
function buildAirbox(){
  const sec = (w, hT, hB, squash) => {
    const pts = [];
    const N = 48;
    for (let i = 0; i < N; i++){
      const a = i / N * TAU, sx = Math.sin(a), cy = Math.cos(a);
      const rx = w * Math.sign(sx) * Math.pow(Math.abs(sx), 0.72);
      const cyc = (hT + hB) * 0.5, ry = (hT - hB) * 0.5;
      const shape = cy > 0 ? Math.pow(Math.abs(cy), 0.60) : -Math.pow(Math.abs(cy), 1.40);
      pts.push([rx * (cy > 0 ? 1 - squash * cy : 1), cyc + ry * shape]);
    }
    return pts;
  };
  const rows = [];
  // 1. outer shell, rear -> front
  const back = stationsFrom(-0.585, -0.082, 40);
  for (const z of back){
    const t = clamp01((-0.082 - z) / 0.503);
    rows.push(ringFromClosed(sec(lerp(0.1270, 0.1930, smooth01(Math.min(t * 1.55, 1))),
                                 lerp(0.9430, 0.8760, smooth01(t)),
                                 lerp(0.7580, 0.6960, smooth01(t)), 0.32), z, 60));
  }
  // 2. lip roll-over at the mouth plane
  for (let i = 1; i <= 4; i++){
    const t = i / 5;
    rows.push(ringFromClosed(sec(lerp(0.1270, 0.1055, t), lerp(0.9430, 0.9200, t),
                                 lerp(0.7580, 0.7760, t), 0.32), -0.082 + 0.010 * Math.sin(PI * t), 60));
  }
  // 3. throat running back inside, contracting
  for (let i = 0; i <= 12; i++){
    const t = i / 12, z = lerp(-0.086, -0.330, t), s = lerp(1.0, 0.56, smooth01(t));
    rows.push(ringFromClosed(sec(0.1045 * s, 0.8480 + 0.0740 * s, 0.8480 - 0.0740 * s, 0.32), z, 60));
  }
  const shell = loftLoops(rows, { capStart: true, capEnd: true, capSegs: 4, capBulge: 0.35 });
  return { shell: logPart('airbox:shell+throat', shell), throat: null };
}

/** Shark fin + rear engine-cover spine. */
function buildSharkFin(){
  const outline = [];
  const top = [[-0.360,0.815],[-0.620,0.790],[-0.900,0.742],[-1.180,0.672],[-1.430,0.588],[-1.640,0.500]];
  const bot = [[-1.640,0.402],[-1.400,0.508],[-1.140,0.596],[-0.860,0.672],[-0.600,0.730],[-0.360,0.772]];
  for (const p of top) outline.push(V2(p[0], p[1]));
  for (const p of bot) outline.push(V2(p[0], p[1]));
  const smoothed = spline2(outline, 130, { closed: true });
  const g = plate(smoothed, { thickness: 0.016, bevel: 0.005, bevelSegs: 3,
    warp: (x, y, w) => V3(w * (1 - 0.30 * clamp01((x + 1.64) / 1.28)), y, x) });
  return logPart('enginecover:sharkfin', g);
}

/* ---- floor, tunnels and diffuser ---------------------------------------------------- */
const FLOOR = paramTrack({
  halfW:  [[1.560,0.1900],[1.320,0.3500],[1.060,0.4500],[0.640,0.5060],[0.100,0.5240],
           [-0.500,0.5240],[-1.000,0.5100],[-1.400,0.4760],[-1.680,0.4420],[-2.045,0.4120]],
  topY:   [[1.560,0.1300],[1.320,0.1220],[1.060,0.1180],[0.640,0.1160],[0.100,0.1160],
           [-0.500,0.1300],[-1.000,0.1620],[-1.400,0.2300],[-1.680,0.3100],[-2.045,0.4000]],
  botY:   [[1.560,0.0470],[1.320,0.0400],[1.060,0.0370],[0.640,0.0355],[0.100,0.0380],
           [-0.500,0.0480],[-1.000,0.0620],[-1.400,0.0740],[-1.680,0.0820],[-2.045,0.0880]],
  tunH:   [[1.560,0.0060],[1.320,0.0260],[1.060,0.0480],[0.640,0.0700],[0.100,0.0760],
           [-0.500,0.0900],[-1.000,0.1300],[-1.400,0.2000],[-1.680,0.2680],[-2.045,0.3200]],
  keelW:  [[1.560,0.0900],[1.060,0.1200],[0.100,0.1300],[-0.500,0.1300],[-1.000,0.1250],[-2.045,0.1150]],
  edgeH:  [[1.560,0.0180],[1.060,0.0300],[0.100,0.0360],[-0.500,0.0360],[-1.000,0.0330],[-1.680,0.0280],[-2.045,0.0240]],
});

function floorPts(z){
  const p = FLOOR(z);
  const hw = p.halfW, top = p.topY, bot = p.botY, tun = p.tunH, kw = p.keelW, eh = p.edgeH;
  return [
    [0,             top],                              // top centreline (under the chassis)
    [kw * 1.6,      top],
    [hw * 0.62,     top - 0.004],
    [hw - 0.030,    top - 0.014],
    [hw,            top - 0.030],                      // outer edge, top
    [hw + 0.004,    top - 0.030 - eh * 0.55],          // edge fence face
    [hw - 0.006,    top - 0.030 - eh],                 // edge, bottom
    [hw - 0.055,    bot + tun * 0.34],                 // tunnel outer wall
    [hw - 0.140,    bot + tun * 0.92],                 // tunnel roof
    [hw - 0.255,    bot + tun],                        // tunnel apex
    [kw + 0.055,    bot + tun * 0.52],                 // tunnel inner wall
    [kw,            bot + 0.004],                      // keel shoulder
    [kw * 0.6,      bot],
    [0,             bot],                              // plank centreline
  ];
}

function buildFloor(){
  const zs = stationsFrom(1.560, D.diffuserExitZ, 132, 0.3);
  const loops = zs.map(z => ringFromHalf(floorPts(z), z, 52));
  const g = loftLoops(loops, { capStart: true, capEnd: true, capSegs: 4, capBulge: 0.30 });
  return logPart('floor:tunnels+diffuser', g);
}

/** Vertical strakes standing inside the diffuser, each one clipped to the local tunnel
 *  roof height so no strake ever protrudes through the floor surface. */
function buildDiffuserStrakes(){
  const parts = [];
  const rows = [
    { x: 0.176, z0: -1.180, z1: -2.030, frac: 0.80 },
    { x: 0.272, z0: -1.280, z1: -2.030, frac: 0.86 },
    { x: 0.358, z0: -1.380, z1: -2.030, frac: 0.84 },
  ];
  for (const r of rows){
    const out = [], n = 24;
    for (let i = 0; i <= n; i++){
      const t = i / n, z = lerp(r.z0, r.z1, t);
      const p = FLOOR(z);
      out.push(V2(z, p.botY + 0.004 + p.tunH * r.frac * smooth01(clamp01(t * 1.15))));
    }
    for (let i = n; i >= 0; i--){
      const t = i / n, z = lerp(r.z0, r.z1, t);
      const p = FLOOR(z);
      out.push(V2(z, p.botY + 0.002 + 0.006 * t));
    }
    const g = plate(out, { thickness: 0.0065, bevel: 0.0018,
      warp: (a, b, w) => V3(r.x + w, b, a) });
    parts.push(g, mirrorX(g));
  }
  return logPart('diffuser:strakes', merge(parts));
}

/** Floor-edge fences ahead of the tunnel inlets.  Each fence hangs from the floor's own
 *  upper surface down to just above the reference plane, curving outboard as it runs
 *  back — so it stands under the floor instead of poking through it. */
function buildFloorFences(){
  const parts = [];
  const defs = [
    { z0: 1.500, z1: 1.090, xs: 0.250, xe: 0.398, tw: 0.0055 },
    { z0: 1.400, z1: 0.980, xs: 0.336, xe: 0.462, tw: 0.0055 },
    { z0: 1.290, z1: 0.880, xs: 0.412, xe: 0.502, tw: 0.0050 },
  ];
  for (const d of defs){
    const out = [], n = 20;
    for (let i = 0; i <= n; i++){
      const t = i / n, z = lerp(d.z0, d.z1, t);
      out.push(V2(z, FLOOR(z).topY - 0.004));
    }
    for (let i = n; i >= 0; i--){
      const t = i / n, z = lerp(d.z0, d.z1, t);
      const p = FLOOR(z);
      const drop = smooth01(clamp01(t * 1.4)) * 0.70;
      out.push(V2(z, lerp(p.topY - 0.006, p.botY + 0.010, drop)));
    }
    const g = plate(out, { thickness: d.tw, bevel: 0.0016,
      warp: (a, b, w) => {
        const t = clamp01((d.z0 - a) / (d.z0 - d.z1));
        return V3(lerp(d.xs, d.xe, smooth01(t)) + w, b, a);
      } });
    parts.push(g, mirrorX(g));
  }
  return logPart('floor:edgeFences', merge(parts));
}

/** Skid plank on the reference plane. */
function buildPlank(){
  const zs = stationsFrom(1.400, -1.780, 46);
  const loops = zs.map(z => {
    const p = FLOOR(z);
    const w = Math.min(p.keelW * 0.92, 0.150);
    const y = p.botY;
    const pts = [[0, y + 0.0005], [w * 0.7, y + 0.0005], [w, y - 0.001], [w, y - 0.010],
                 [w * 0.7, y - 0.012], [0, y - 0.012]];
    return ringFromHalf(pts, z, 10);
  });
  return logPart('floor:plank', loftLoops(loops, { capStart: true, capEnd: true, capSegs: 2 }));
}

/* ---- halo ------------------------------------------------------------------------- */
function buildHalo(){
  const rearMount = V3(0.296, 0.598, 0.050);
  const apex      = V3(0.000, 0.9110, 1.0600);
  const ring = [];
  const K = 46;
  for (let i = 0; i <= K; i++){
    const t = i / K;
    // authored 3D path: sweeps out to maximum width mid-way, then closes at the apex
    const s = smooth01(t);
    const x = lerp(rearMount.x, apex.x, s) + Math.sin(t * PI) * 0.128;
    const y = lerp(rearMount.y, apex.y, smoother01(t)) + Math.sin(t * PI) * 0.052;
    const z = lerp(rearMount.z, apex.z, Math.pow(t, 0.86));
    ring.push(V3(x, y, z));
  }
  const secAt = (t) => {
    const w = lerp(0.0225, 0.0165, smooth01(t));
    const h = lerp(0.0330, 0.0245, smooth01(t));
    return squircle(w, h, 2.5, 16).map(p => V2(p.x, p.y));
  };
  const half = sweepSection(ring, secAt, { capStart: true, capEnd: false, capSegs: 3 });
  const hoop = merge([half, mirrorX(half)]);

  // centre pillar from the apex down to the chassis
  const pillar = [];
  for (let i = 0; i <= 16; i++){
    const t = i / 16;
    pillar.push(V3(0, lerp(0.9130, 0.5560, smooth01(t)), lerp(1.0560, 1.1420, t * t)));
  }
  const post = sweepSection(pillar, (t) => squircle(lerp(0.0175, 0.0245, t), lerp(0.0285, 0.0360, t), 2.4, 14),
                            { capStart: true, capEnd: true, capSegs: 3 });

  // rear mounting blocks
  const blocks = [];
  for (const s of [1, -1]){
    const g = plate([[-0.040,-0.030],[0.040,-0.030],[0.046,0.028],[-0.034,0.036]], { thickness: 0.030, bevel: 0.004 });
    g.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
    g.translate(s * 0.296, 0.588, 0.050);
    blocks.push(g);
  }
  return logPart('halo:hoop+pillar', merge([hoop, post, ...blocks]));
}

/** Small aero vane on top of the halo, as run since 2023. */
function buildHaloVane(){
  const out = [[1.030,0.905],[0.900,0.928],[0.760,0.936],[0.640,0.930],[0.600,0.916],
               [0.720,0.906],[0.870,0.898],[1.010,0.888]];
  const g = plate(spline2(out.map(p => V2(p[0], p[1])), 70, { closed: true }), {
    thickness: 0.030, bevel: 0.006, bevelSegs: 3,
    warp: (z, y, w) => V3(w * 1.5, y + Math.cos(w * 40) * 0.0006, z) });
  return logPart('halo:vane', g);
}

/* ---- cockpit surround details ------------------------------------------------------- */
function buildHeadrest(){
  const zs = stationsFrom(0.185, -0.070, 26);
  const loops = zs.map(z => {
    const t = clamp01((0.185 - z) / 0.255);
    const w = lerp(0.196, 0.168, smooth01(t));
    const yT = lerp(0.596, 0.660, smooth01(t));
    const yB = lerp(0.415, 0.470, t);
    return ringFromClosed(podPts({ xIn: -w, xOut: w, yTop: yT, yBot: yB, nTop: 2.6, nBot: 2.2, nIn: 2.6 }, 40), z, 44);
  });
  return logPart('cockpit:headrest', loftLoops(loops, { capStart: true, capEnd: true, capSegs: 4, capBulge: 0.6 }));
}

/** Mirrors: a faired stalk off the cockpit flank carrying a shallow rectangular pod.
 *  The pod is lofted across its WIDTH so it stays a flat mirror box, not a horn. */
function buildMirrors(){
  const parts = [], glass = [];
  for (const s of [1, -1]){
    const stalk = [];
    for (let i = 0; i <= 12; i++){
      const t = i / 12;
      stalk.push(V3(s * lerp(0.310, 0.436, smooth01(t)), lerp(0.552, 0.578, t), lerp(0.792, 0.824, t)));
    }
    parts.push(sweepSection(stalk, (t) => squircle(lerp(0.017, 0.012, t), lerp(0.0090, 0.0072, t), 2.6, 12),
                            { capStart: true, capEnd: true, capSegs: 3 }));
    // pod: rings stacked outboard, each a flat rounded rectangle in (z,y)
    const pod = [];
    for (let i = 0; i <= 10; i++){
      const t = i / 10;
      const x = s * lerp(0.402, 0.512, t);
      const sc = Math.sin(PI * (0.22 + t * 0.60)) / Math.sin(PI * 0.52);
      const loop = [];
      for (let k = 0; k < 32; k++){
        const a = k / 32 * TAU, sx = Math.sin(a), cy = Math.cos(a);
        loop.push(V3(x,
          0.5860 + Math.sign(cy) * Math.pow(Math.abs(cy), 0.42) * 0.0345 * sc,
          0.8180 + Math.sign(sx) * Math.pow(Math.abs(sx), 0.42) * 0.0290 * sc));
      }
      pod.push(loop);
    }
    parts.push(loftLoops(pod, { capStart: true, capEnd: true, capSegs: 3, capBulge: 0.35 }));
    const gl = plate([[-0.0250,-0.0300],[0.0250,-0.0300],[0.0250,0.0300],[-0.0250,0.0300]].map(p => V2(p[0], p[1])),
      { thickness: 0.003, bevel: 0.0008 });
    gl.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
    gl.applyMatrix4(new THREE.Matrix4().makeRotationY(-s * 0.26));
    gl.translate(s * 0.4020, 0.5860, 0.8180);
    glass.push(gl);
  }
  return { housing: logPart('cockpit:mirrors', merge(parts)), glass: logPart('cockpit:mirrorGlass', merge(glass)) };
}
/* =====================================================================================
   AERODYNAMIC SURFACES
   Every wing element is a real spanwise loft of cambered sections: chord, incidence,
   thickness, camber and leading-edge anchor are all functions of span.  Nothing here is
   a scaled slab.  Negative camber and negative incidence produce the inverted, TE-up
   geometry that makes an F1 wing read correctly from any angle.
   ===================================================================================== */

/** Build one element from spanwise control curves, mirrored about the centreline. */
function wingElement({ name, x0, x1, steps = 26, leZ, leY, chord, incidence, thick, camber,
                       camberPos = 0.42, dihedral = null, teThick = 0.0035, sectionPoints = 56,
                       half = true, tips = null }){
  const stations = [];
  for (let i = 0; i <= steps; i++){
    const t = i / steps;
    const x = lerp(x0, x1, t);
    stations.push({
      le: V3(x, leY(t), leZ(t)),
      chord: chord(t),
      incidence: incidence(t),
      dihedral: dihedral ? dihedral(t) : 0,
      section: { thick: thick(t), camber: camber(t), camberPos, teThick },
    });
  }
  // an element that starts on the centreline is left open there, so the mirrored half
  // joins it seamlessly instead of showing a capped seam down the middle
  const roundTips = tips || [x0 > 0.004, true];
  const g = wingLoft(stations, { sectionPoints, roundTips });
  return logPart(name, half ? merge([g, mirrorX(g)]) : g);
}

/* ---- FRONT WING -------------------------------------------------------------------- */
function buildFrontWing(){
  const parts = [];
  const TIP = 0.8950;

  // spanwise rise: flat across the regulated neutral centre, lifting only outboard
  const rise = (t, amt) => amt * Math.pow(clamp01((t - 0.58) / 0.42), 1.75);

  // element 0 — main plane, with the regulation neutral central section
  parts.push(wingElement({
    name: 'frontwing:mainplane', x0: 0.0, x1: TIP, steps: 44, sectionPoints: 66,
    leZ: t => 2.9520 - 0.0260 * Math.pow(clamp01((t - 0.45) / 0.55), 1.6),
    leY: t => 0.0740 + 0.0180 * smooth01(clamp01((t - 0.14) / 0.44)) + rise(t, 0.0400),
    chord: t => 0.2880 - 0.0140 * smooth01(clamp01((t - 0.60) / 0.40)) - 0.0340 * Math.pow(clamp01((t - 0.88) / 0.12), 2),
    incidence: t => -0.050 - 0.070 * smooth01(clamp01((t - 0.14) / 0.60)),
    thick: t => 0.058 - 0.009 * t,
    camber: t => -0.030 - 0.046 * smooth01(clamp01((t - 0.14) / 0.58)),
    dihedral: t => -0.06 - 0.30 * Math.pow(clamp01((t - 0.70) / 0.30), 1.8),
  }));

  // element 1 — first flap, sitting above and behind the main plane's trailing edge
  parts.push(wingElement({
    name: 'frontwing:flap1', x0: 0.1300, x1: TIP - 0.005, steps: 38, sectionPoints: 58,
    leZ: t => 2.7040 - 0.0260 * Math.pow(clamp01((t - 0.45) / 0.55), 1.6),
    leY: t => 0.1330 + 0.0180 * smooth01(t) + rise(t, 0.0420),
    chord: t => 0.2100 + 0.0120 * Math.sin(PI * t) - 0.0320 * Math.pow(clamp01((t - 0.86) / 0.14), 2),
    incidence: t => -0.205 - 0.100 * smooth01(t),
    thick: t => 0.050 - 0.008 * t,
    camber: t => -0.072 - 0.026 * smooth01(t),
    dihedral: t => -0.10 - 0.34 * Math.pow(clamp01((t - 0.68) / 0.32), 1.8),
  }));

  // element 2 — outer flap, the movable one under the 2026 rules
  parts.push(wingElement({
    name: 'frontwing:flap2', x0: 0.2340, x1: TIP - 0.010, steps: 34, sectionPoints: 54,
    leZ: t => 2.5260 - 0.0240 * Math.pow(clamp01((t - 0.45) / 0.55), 1.6),
    leY: t => 0.2100 + 0.0180 * smooth01(t) + rise(t, 0.0440),
    chord: t => 0.1900 + 0.0100 * Math.sin(PI * t) - 0.0300 * Math.pow(clamp01((t - 0.86) / 0.14), 2),
    incidence: t => -0.345 - 0.115 * smooth01(t),
    thick: t => 0.044 - 0.007 * t,
    camber: t => -0.086 - 0.024 * smooth01(t),
    dihedral: t => -0.14 - 0.36 * Math.pow(clamp01((t - 0.66) / 0.34), 1.8),
  }));

  return merge(parts);
}

/** Front-wing endplate: authored outline, curled outboard toward the top rear so the
 *  plate generates outwash instead of standing flat. */
function buildFrontEndplate(){
  const out = [
    [2.9620,0.0720],[2.9560,0.1580],[2.9360,0.2260],[2.8880,0.2680],[2.7900,0.2860],
    [2.6400,0.2900],[2.5100,0.2800],[2.4180,0.2500],[2.3620,0.1940],[2.3400,0.1220],
    [2.3520,0.0620],[2.4400,0.0380],[2.6600,0.0330],[2.8700,0.0450],
  ];
  const outline = spline2(out.map(p => V2(p[0], p[1])), 160, { closed: true });
  // two louvre slots cut through the plate — the detail that stops it reading as a slab
  const slot = (z0, z1, y0, h) => {
    const s = [];
    const n = 12;
    for (let i = 0; i <= n; i++){ const t = i / n; s.push(V2(lerp(z0, z1, t), y0 + h * Math.sin(PI * (0.10 + t * 0.80)))); }
    for (let i = n; i >= 0; i--){ const t = i / n; s.push(V2(lerp(z0, z1, t), y0 - 0.0035)); }
    return s.reverse();
  };
  const curl = (z, y) => {
    const up = clamp01((y - 0.100) / 0.190);
    const back = clamp01((2.900 - z) / 0.540);
    return 0.052 * Math.pow(up, 1.7) * Math.pow(back, 1.20);
  };
  const g = plate(outline, { thickness: 0.0080, bevel: 0.0024, bevelSegs: 3,
    holes: [slot(2.6900, 2.4400, 0.2150, 0.0175), slot(2.7300, 2.4900, 0.1720, 0.0165)],
    warp: (z, y, w) => V3(0.8950 + w + curl(z, y), y, z) });

  // footplate turning the lower edge outward around the tyre
  const foot = [];
  const n = 26;
  for (let i = 0; i <= n; i++){ const t = i / n; foot.push(V2(lerp(2.920, 2.330, t), 0.034 + 0.009 * Math.sin(PI * t))); }
  for (let i = n; i >= 0; i--){ const t = i / n; foot.push(V2(lerp(2.920, 2.330, t), 0.007 + 0.004 * Math.sin(PI * t))); }
  const fp = plate(foot, { thickness: 0.046, bevel: 0.004, bevelSegs: 2,
    warp: (z, y, w) => {
      const t = clamp01((2.920 - z) / 0.590);
      return V3(0.8850 + w * (1 + 1.4 * t) + 0.026 * Math.pow(t, 1.4), y, z);
    } });

  const merged = merge([g, fp]);
  return logPart('frontwing:endplate', merge([merged, mirrorX(merged)]));
}

/** Slim faired pylons tying the wing assembly to the underside of the nose. */
function buildNosePylons(){
  const parts = [];
  for (const s of [1, -1]){
    const stations = [];
    for (let i = 0; i <= 10; i++){
      const t = i / 10;
      stations.push({
        le: V3(s * lerp(0.0700, 0.0560, t), lerp(0.1180, 0.2680, smoother01(t)), lerp(2.8300, 2.7100, t)),
        chord: lerp(0.2400, 0.1900, t),
        incidence: 0, dihedral: 0,
        section: { thick: 0.115, camber: 0, camberPos: 0.42, teThick: 0.003 },
        spanDir: V3(0, 1, 0), upDir: V3(s, 0, 0), chordDir: V3(0, 0, -1),
      });
    }
    parts.push(wingLoft(stations, { sectionPoints: 34, roundTips: [false, false] }));
  }
  return logPart('frontwing:pylons', merge(parts));
}

/* ---- REAR WING --------------------------------------------------------------------- */
function buildRearWing(){
  const parts = [];
  const SPAN = 0.4700;

  parts.push(wingElement({
    name: 'rearwing:mainplane', x0: 0.0, x1: SPAN, steps: 26, sectionPoints: 60,
    leZ: t => -1.8980 + 0.0140 * Math.pow(t, 2.2),
    leY: t => 0.7280 + 0.0130 * Math.pow(t, 2.0),
    chord: t => 0.2480 - 0.0180 * Math.pow(clamp01((t - 0.80) / 0.20), 2),
    incidence: t => -0.170 - 0.040 * Math.pow(t, 2),
    thick: t => 0.080 - 0.010 * t,
    camber: t => -0.062,
  }));

  parts.push(wingElement({
    name: 'rearwing:flap', x0: 0.0, x1: SPAN - 0.004, steps: 24, sectionPoints: 52,
    leZ: t => -2.1180 + 0.0100 * Math.pow(t, 2.2),
    leY: t => 0.8340 + 0.0140 * Math.pow(t, 2.0),
    chord: t => 0.2000 - 0.0160 * Math.pow(clamp01((t - 0.82) / 0.18), 2),
    incidence: t => -0.470 - 0.045 * Math.pow(t, 2),
    thick: t => 0.058 - 0.008 * t,
    camber: t => -0.086,
  }));

  return merge(parts);
}

function buildRearEndplate(){
  const out = [
    [-1.8300,0.6180],[-1.8460,0.7420],[-1.8560,0.8420],[-1.8720,0.9080],[-1.9400,0.9260],
    [-2.0800,0.9280],[-2.2100,0.9180],[-2.3060,0.8880],[-2.3560,0.8280],[-2.3660,0.7420],
    [-2.3600,0.6560],[-2.3200,0.6040],[-2.2200,0.5760],[-2.0600,0.5640],[-1.9200,0.5720],
  ];
  const outline = spline2(out.map(p => V2(p[0], p[1])), 150, { closed: true });
  const g = plate(outline, { thickness: 0.0090, bevel: 0.0028, bevelSegs: 3,
    warp: (z, y, w) => {
      const top = clamp01((y - 0.780) / 0.150);
      const back = clamp01((-1.880 - z) / 0.470);
      return V3(0.4700 + w + 0.030 * Math.pow(top, 2.0) * Math.pow(back, 1.2), y, z);
    } });
  // lower louvre strakes on the plate
  const strakes = [];
  for (let i = 0; i < 3; i++){
    const y0 = 0.612 + i * 0.040;
    const s = plate([[-1.930, y0], [-2.180, y0 + 0.012], [-2.180, y0 + 0.030], [-1.930, y0 + 0.020]].map(p => V2(p[0], p[1])),
      { thickness: 0.020, bevel: 0.002, warp: (z, y, w) => V3(0.4680 + w * 1.0, y, z) });
    strakes.push(s);
  }
  const one = merge([g, ...strakes]);
  return logPart('rearwing:endplate', merge([one, mirrorX(one)]));
}

/** Swan-neck pylons: they meet the UPPER surface of the main plane, as on a modern car. */
function buildRearPylons(){
  const parts = [];
  for (const s of [1, -1]){
    // swan neck: meets the UPPER surface of the main plane, bowed forward
    parts.push(strut(V3(s * 0.0560, 0.4180, -1.6120), V3(s * 0.0880, 0.7960, -1.8860),
      { chord: 0.108, thickRatio: 0.24, taper: 0.70, steps: 16, bow: 0.034 }));
  }
  // DRS actuator pod on the centreline
  const pod = [];
  for (let i = 0; i <= 12; i++){
    const t = i / 12, z = lerp(-1.880, -2.070, t);
    const w = Math.sin(PI * (0.12 + t * 0.76)) * 0.044;
    const pts = [];
    for (let k = 0; k < 24; k++){ const a = k / 24 * TAU; pts.push([Math.sin(a) * w, 0.802 + Math.cos(a) * w * 0.78]); }
    pod.push(ringFromClosed(pts, z, 26));
  }
  parts.push(loftLoops(pod, { capStart: true, capEnd: true, capSegs: 3 }));
  return logPart('rearwing:pylons+DRSpod', merge(parts));
}

/* ---- BEAM WING --------------------------------------------------------------------- */
function buildBeamWing(){
  const parts = [];
  parts.push(wingElement({
    name: 'beamwing:upper', x0: 0.0, x1: 0.3820, steps: 18, sectionPoints: 44,
    leZ: t => -1.9200 - 0.0180 * Math.pow(t, 2),
    leY: t => 0.3560 + 0.0120 * Math.pow(t, 2),
    chord: () => 0.1720, incidence: () => -0.300,
    thick: () => 0.070, camber: () => -0.070,
  }));
  parts.push(wingElement({
    name: 'beamwing:lower', x0: 0.0, x1: 0.3620, steps: 16, sectionPoints: 40,
    leZ: t => -1.9600 - 0.0160 * Math.pow(t, 2),
    leY: t => 0.2760 + 0.0100 * Math.pow(t, 2),
    chord: () => 0.1420, incidence: () => -0.230,
    thick: () => 0.066, camber: () => -0.058,
  }));
  return merge(parts);
}

/* ---- REAR CRASH STRUCTURE, EXHAUST, RAIN LIGHT ------------------------------------- */
function buildRearStructure(){
  const zs = stationsFrom(-1.500, -2.130, 34);
  const loops = zs.map(z => {
    const t = clamp01((-1.500 - z) / 0.630);
    const w = lerp(0.098, 0.052, smoother01(t));
    const h = lerp(0.088, 0.046, smoother01(t));
    const yc = lerp(0.398, 0.352, t);
    const pts = [];
    for (let k = 0; k < 36; k++){
      const a = k / 36 * TAU, sx = Math.sin(a), cy = Math.cos(a);
      pts.push([Math.sign(sx) * Math.pow(Math.abs(sx), 0.62) * w,
                yc + Math.sign(cy) * Math.pow(Math.abs(cy), 0.62) * h]);
    }
    return ringFromClosed(pts, z, 40);
  });
  return logPart('rear:crashStructure', loftLoops(loops, { capStart: true, capEnd: true, capSegs: 4 }));
}

function buildExhaust(){
  const parts = [];
  // single central tailpipe
  const main = [];
  for (let i = 0; i <= 14; i++){
    const t = i / 14;
    main.push(V3(0, lerp(0.452, 0.436, t), lerp(-1.760, -2.062, t)));
  }
  parts.push(sweepTube(main, (t) => lerp(0.052, 0.044, t), 26, { capStart: true }));
  // inner liner so the pipe reads open
  const inner = [];
  for (let i = 0; i <= 8; i++){ const t = i / 8; inner.push(V3(0, lerp(0.446, 0.436, t), lerp(-1.960, -2.056, t))); }
  parts.push(sweepTube(inner, 0.036, 22, { }));
  // wastegate pipes
  for (const s of [1, -1]){
    const p = [];
    for (let i = 0; i <= 10; i++){
      const t = i / 10;
      p.push(V3(s * lerp(0.052, 0.084, t), lerp(0.470, 0.492, t), lerp(-1.840, -2.010, t)));
    }
    parts.push(sweepTube(p, 0.0185, 16, { capStart: true }));
  }
  return logPart('rear:exhaust', merge(parts));
}

function buildRainLight(){
  const g = plate([[-0.046,-0.052],[0.046,-0.052],[0.046,0.052],[-0.046,0.052]].map(p => V2(p[0], p[1])),
    { thickness: 0.020, bevel: 0.004, bevelSegs: 2 });
  g.translate(0, 0.322, -2.078);
  return logPart('rear:rainLight', g);
}

/* ---- BODY-MOUNTED VORTEX GENERATORS ------------------------------------------------- */
function buildVortexGenerators(){
  const parts = [];
  // sidepod shoulder fins
  for (let i = 0; i < 3; i++){
    const z0 = 0.520 - i * 0.115;
    const out = [];
    const n = 12;
    for (let k = 0; k <= n; k++){ const t = k / n; out.push(V2(lerp(z0, z0 - 0.135, t), 0.026 * Math.sin(PI * (0.15 + t * 0.7)))); }
    for (let k = n; k >= 0; k--){ const t = k / n; out.push(V2(lerp(z0, z0 - 0.135, t), -0.004)); }
    const g = plate(out, { thickness: 0.0055, bevel: 0.0015,
      warp: (z, y, w) => {
        const p = POD(z);
        return V3(p.xOut * (0.72 + i * 0.06) + w, p.yTop + y - 0.004, z);
      } });
    parts.push(g, mirrorX(g));
  }
  return logPart('aero:vortexGenerators', merge(parts));
}
/* =====================================================================================
   WHEELS, BRAKES, SUSPENSION
   Tyres are revolved from a measured carcass section (bead -> bulge -> shoulder -> crown)
   and carry a baked contact-patch deflection, so a parked car sits on a loaded tyre
   rather than a mathematically round one.  A second, undeflected carcass is emitted for
   the rolling presentation mode — the deflection is geometry, not a shader trick, so it
   cannot simply be spun.
   ===================================================================================== */

/** Measured carcass half-section, mirrored about the wheel centre plane.
 *  Points are (radius, axial); axial +ve is outboard. */
function tyreProfile({ R, halfW, rimR }){
  const bulge = halfW;                       // widest point of the sidewall
  const tread = halfW * 0.795;               // crown half-width
  const k = [
    [rimR,          halfW * 0.805],
    [rimR + 0.018,  halfW * 0.880],
    [R * 0.735,     bulge * 0.972],
    [R * 0.845,     bulge],
    [R * 0.918,     bulge * 0.958],
    [R * 0.966,     bulge * 0.882],
    [R * 0.9915,    tread * 1.010],
    [R * 0.99935,   tread * 0.800],
    [R,             tread * 0.400],
    [R,             0],
  ];
  const half = spline2(k.map(p => V2(p[0], p[1])), 30, { closed: false });
  const prof = [];
  // outboard bead -> crown -> inboard bead, so texture v maps outboard(0) to inboard(1)
  for (let i = 0; i < half.length; i++)      prof.push(V2(half[i].x,  half[i].y));
  for (let i = half.length - 2; i >= 0; i--) prof.push(V2(half[i].x, -half[i].y));
  return prof;
}

/** Radial deflection at the contact patch, applied in the wheel's own frame. */
function deflectTyre(geo, R, drop){
  return xform(geo, (x, y, z) => {
    const r = Math.hypot(y, z);
    if (r < 1e-5) return V3(x, y, z);
    // the ground is at local y = -R; squash only the lower arc, and bulge the sidewall
    const groundY = -(R - drop);
    if (y >= groundY) return V3(x, y, z);
    const over = (groundY - y) / Math.max(drop, 1e-5);
    const s = clamp01(over);
    const ny = lerp(y, groundY, smooth01(Math.min(s * 1.35, 1)));
    const widen = 1 + 0.085 * smooth01(Math.min(s, 1)) * clamp01(Math.abs(x) / (R * 0.5));
    return V3(x * widen, ny, z);
  });
}

function buildTyre({ R, halfW, rimR, drop }){
  const prof = tyreProfile({ R, halfW, rimR });
  // profile runs +X -> -X, so the revolved normals need flipping to face outward
  const round = latheX(prof, 108, { flip: true });
  const loaded = deflectTyre(latheX(prof, 108, { flip: true }), R, drop);
  return { round: logPart('tyre:carcass', round), loaded: logPart('tyre:carcassLoaded', loaded) };
}

/* ---- rim ---------------------------------------------------------------------------- */
function buildRim({ rimR, halfW }){
  const parts = [];
  const inner = rimR - 0.020;
  // barrel: outboard flange, drop centre, inboard flange
  const barrel = [
    V2(rimR,           halfW * 0.815),
    V2(rimR - 0.004,   halfW * 0.790),
    V2(rimR - 0.012,   halfW * 0.760),
    V2(inner,          halfW * 0.700),
    V2(inner,          halfW * 0.180),
    V2(inner - 0.012,  0.0),
    V2(inner,         -halfW * 0.180),
    V2(inner,         -halfW * 0.700),
    V2(rimR - 0.012,  -halfW * 0.760),
    V2(rimR - 0.004,  -halfW * 0.790),
    V2(rimR,          -halfW * 0.815),
  ];
  parts.push(latheX(spline2(barrel, 46, { closed: false }), 96, { flip: true }));

  // spoke face: an authored annulus with real windows, extruded and dished
  const N = 10;
  const ring = (r, seg = 72) => { const o = []; for (let i = 0; i < seg; i++){ const a = i / seg * TAU; o.push(V2(Math.cos(a) * r, Math.sin(a) * r)); } return o; };
  const windows = [];
  for (let i = 0; i < N; i++){
    const a0 = (i / N) * TAU + 0.055, a1 = ((i + 1) / N) * TAU - 0.055;
    const rIn = 0.074, rOut = rimR - 0.028;
    const w = [];
    const steps = 7;
    for (let k = 0; k <= steps; k++){ const a = lerp(a0, a1, k / steps); w.push(V2(Math.cos(a) * rOut, Math.sin(a) * rOut)); }
    for (let k = steps; k >= 0; k--){ const a = lerp(a0 + 0.10, a1 - 0.10, k / steps); w.push(V2(Math.cos(a) * rIn, Math.sin(a) * rIn)); }
    windows.push(w.reverse());
  }
  const face = plate(ring(rimR - 0.006), { thickness: 0.014, bevel: 0.0032, bevelSegs: 2, holes: windows });
  xform(face, (x, y, z) => {
    const r = Math.hypot(x, y);
    const dish = 0.020 * Math.pow(clamp01(r / rimR), 2.1);
    return V3(x, y, z - dish);
  });
  face.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
  face.translate(halfW * 0.560, 0, 0);
  parts.push(face);

  // centre boss + single wheel nut
  parts.push(latheX(spline2([V2(0.020, halfW * 0.62), V2(0.058, halfW * 0.64), V2(0.076, halfW * 0.60),
                             V2(0.080, halfW * 0.50), V2(0.074, halfW * 0.44), V2(0.030, halfW * 0.42)], 22, { closed: false }), 48));
  const nut = [];
  for (let i = 0; i < 6; i++){
    const a = i / 6 * TAU;
    nut.push(V2(Math.cos(a) * 0.0345, Math.sin(a) * 0.0345));
  }
  const nutG = plate(nut, { thickness: 0.030, bevel: 0.0035, bevelSegs: 2 });
  nutG.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
  nutG.translate(halfW * 0.700, 0, 0);
  parts.push(nutG);

  // valve stem
  const stem = [];
  for (let i = 0; i <= 6; i++){ const t = i / 6; stem.push(V3(halfW * 0.60 + 0.012 * t, rimR * 0.80 + 0.026 * t, 0.010 * t)); }
  parts.push(sweepTube(stem, 0.0042, 10, { capStart: true, capEnd: true }));

  return logPart('wheel:rim', merge(parts));
}

/** Aero rim cover — the closed outer face mandated since the 18" switch. */
function buildRimCover({ rimR, halfW }){
  const prof = [
    V2(rimR - 0.001, halfW * 0.812),
    V2(rimR - 0.014, halfW * 0.832),
    V2(rimR - 0.052, halfW * 0.845),
    V2(rimR - 0.110, halfW * 0.840),
    V2(rimR - 0.160, halfW * 0.822),
    V2(0.045,        halfW * 0.792),
    V2(0.020,        halfW * 0.770),
  ];
  const g = latheX(spline2(prof, 34, { closed: false }), 90);
  return logPart('wheel:rimCover', g);
}

/* ---- brakes -------------------------------------------------------------------------- */
function buildBrakeDisc({ rOut = 0.1550, rIn = 0.0760, thick = 0.032 } = {}){
  const ring = (r, seg = 84) => { const o = []; for (let i = 0; i < seg; i++){ const a = i / seg * TAU; o.push(V2(Math.cos(a) * r, Math.sin(a) * r)); } return o; };
  const holes = [ring(rIn, 60).reverse()];
  for (let row = 0; row < 2; row++){
    const r = rOut - 0.030 - row * 0.030, count = 26 - row * 4;
    for (let i = 0; i < count; i++){
      const a = i / count * TAU + row * 0.12;
      const cx = Math.cos(a) * r, cy = Math.sin(a) * r, hr = 0.0038;
      const h = [];
      for (let k = 0; k < 7; k++){ const b = k / 7 * TAU; h.push(V2(cx + Math.cos(b) * hr, cy + Math.sin(b) * hr)); }
      holes.push(h.reverse());
    }
  }
  const g = plate(ring(rOut, 96), { thickness: thick, bevel: 0.0020, bevelSegs: 1, holes });
  g.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
  return logPart('brake:disc', g);
}

function buildCaliper({ r = 0.168, span = 1.05, y0 = 0.25 } = {}){
  const parts = [];
  const path = [];
  const steps = 22;
  for (let i = 0; i <= steps; i++){
    const a = y0 + (i / steps) * span;
    path.push(V3(0, Math.sin(a) * r, Math.cos(a) * r));
  }
  parts.push(sweepSection(path, (t) => {
    const w = 0.030 + 0.010 * Math.sin(PI * t);
    const h = 0.058 + 0.014 * Math.sin(PI * t);
    return squircle(h, w, 3.0, 18).map(p => V2(p.y, p.x));
  }, { capStart: true, capEnd: true, capSegs: 3 }));
  // piston bosses
  for (let i = 0; i < 3; i++){
    const a = y0 + span * (0.20 + i * 0.30);
    for (const s of [1, -1]){
      const c0 = V3(s * 0.030, Math.sin(a) * r, Math.cos(a) * r);
      const c1 = V3(s * 0.046, Math.sin(a) * r, Math.cos(a) * r);
      parts.push(sweepTube([c0, c1], 0.0165, 14, { capEnd: true }));
    }
  }
  return logPart('brake:caliper', merge(parts));
}

/** Brake duct drum + inlet scoop + outboard fence. */
function buildBrakeDuct({ R, halfW, front }){
  const parts = [];
  const rD = front ? 0.212 : 0.222;
  const xIn = -halfW * 0.30, xOut = halfW * 0.34;
  const drum = [];
  for (let i = 0; i <= 16; i++){
    const t = i / 16, x = lerp(xIn, xOut, t);
    const r = rD * (0.94 + 0.06 * Math.sin(PI * t));
    const pts = [];
    for (let k = 0; k < 40; k++){
      const a = k / 40 * TAU;
      const squash = 1 - 0.16 * clamp01(-Math.sin(a));        // flattened at the bottom
      pts.push([Math.cos(a) * r * squash, Math.sin(a) * r * squash]);
    }
    drum.push(pts.map(p => V3(x, p[0], p[1])));
  }
  parts.push(loftLoops(drum, { flip: true }));

  // inlet scoop facing forward
  const scoop = [];
  for (let i = 0; i <= 12; i++){
    const t = i / 12;
    const z = lerp(0.300, 0.130, t);
    const w = lerp(0.052, 0.088, smooth01(t));
    const h = lerp(0.062, 0.100, smooth01(t));
    const yc = lerp(-0.085, -0.045, t);
    const pts = [];
    for (let k = 0; k < 28; k++){
      const a = k / 28 * TAU;
      pts.push(V3(lerp(xIn + 0.02, xOut - 0.03, 0.5) + Math.sin(a) * w * 0.5,
                  yc + Math.cos(a) * h * 0.5, z));
    }
    scoop.push(pts);
  }
  parts.push(loftLoops(scoop, { capStart: true }));

  // outboard turning fence
  const fence = [];
  const n = 20;
  for (let i = 0; i <= n; i++){ const a = -0.9 + (i / n) * 2.4; fence.push(V2(Math.cos(a) * (rD + 0.016), Math.sin(a) * (rD + 0.016))); }
  for (let i = n; i >= 0; i--){ const a = -0.9 + (i / n) * 2.4; fence.push(V2(Math.cos(a) * (rD - 0.030), Math.sin(a) * (rD - 0.030))); }
  const fg = plate(fence, { thickness: 0.007, bevel: 0.002 });
  fg.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
  fg.translate(xOut + 0.006, 0, 0);
  parts.push(fg);

  return logPart(front ? 'brake:duct.front' : 'brake:duct.rear', merge(parts));
}

/* ---- upright + hub ------------------------------------------------------------------ */
function buildUpright({ front }){
  const zTop = front ? 0.030 : 0.024;
  const body = [];
  for (let i = 0; i <= 16; i++){
    const t = i / 16;
    const y = lerp(0.202, -0.192, t);
    const w = 0.038 + 0.026 * Math.sin(PI * t) - 0.010 * Math.pow(t, 2);
    const d = 0.058 + 0.034 * Math.sin(PI * t);
    const loop = [];
    for (let k = 0; k < 30; k++){
      const a = k / 30 * TAU, sx = Math.sin(a), cy = Math.cos(a);
      loop.push(V3(Math.sign(sx) * Math.pow(Math.abs(sx), 0.7) * w,
                   y,
                   zTop + Math.sign(cy) * Math.pow(Math.abs(cy), 0.7) * d));
    }
    body.push(loop);
  }
  const hub = latheX(spline2([V2(0.030, -0.012), V2(0.064, 0.006), V2(0.072, 0.050),
                              V2(0.054, 0.074), V2(0.024, 0.074)], 20, { closed: false }), 36);
  return logPart(front ? 'suspension:upright.front' : 'suspension:upright.rear',
    merge([loftLoops(body, { capStart: true, capEnd: true, capSegs: 3 }), hub]));
}

/* ---- streamlined suspension members -------------------------------------------------- */
/** A faired member: constant streamwise airfoil section lofted along the leg axis. */
function strut(a, b, { chord = 0.062, thickRatio = 0.28, twist = 0, taper = 1, steps = 10, bow = 0 } = {}){
  const loops = [];
  const axis = V3().subVectors(b, a);
  const side = V3().crossVectors(axis, V3(0, 1, 0));
  if (side.lengthSq() < 1e-8) side.set(1, 0, 0);
  side.normalize();
  const up = V3().crossVectors(side, axis).normalize();
  for (let i = 0; i <= steps; i++){
    const t = i / steps;
    const c = V3().lerpVectors(a, b, t).addScaledVector(up, Math.sin(PI * t) * bow);
    const ch = chord * lerp(1, taper, t);
    const loop = airfoilLoop(30, { thick: thickRatio, camber: 0, teThick: 0.0026 });
    const ct = Math.cos(twist), st = Math.sin(twist);
    loops.push(loop.map(p => {
      const x = -(p.x - 0.34) * ch, y = p.y * ch;
      return V3(c.x, c.y + (x * st + y * ct), c.z + (x * ct - y * st));
    }));
  }
  return loftLoops(loops, { capStart: true, capEnd: true, capSegs: 3, capBulge: 0.5 });
}

function buildFrontSuspension(){
  const hx = 0.6280, ax = D.frontAxleZ;
  const parts = [
    // upper wishbone
    strut(V3(0.1900, 0.4020, ax + 0.268), V3(hx, 0.4300, ax + 0.014), { chord: 0.070, taper: 0.72, thickRatio: 0.24 }),
    strut(V3(0.1860, 0.3960, ax - 0.256), V3(hx, 0.4280, ax - 0.006), { chord: 0.066, taper: 0.74, thickRatio: 0.24 }),
    // lower wishbone
    strut(V3(0.2260, 0.1560, ax + 0.256), V3(hx + 0.012, 0.1720, ax + 0.016), { chord: 0.082, taper: 0.70, thickRatio: 0.22 }),
    strut(V3(0.2300, 0.1520, ax - 0.240), V3(hx + 0.012, 0.1700, ax - 0.008), { chord: 0.078, taper: 0.72, thickRatio: 0.22 }),
    // pushrod
    strut(V3(hx + 0.006, 0.1880, ax + 0.030), V3(0.2020, 0.4720, ax - 0.214), { chord: 0.040, taper: 0.90, thickRatio: 0.34 }),
    // steering track rod
    strut(V3(0.2000, 0.2380, ax + 0.150), V3(hx + 0.004, 0.2480, ax + 0.086), { chord: 0.038, taper: 0.92, thickRatio: 0.34 }),
  ];
  const one = merge(parts);
  return logPart('suspension:front', merge([one, mirrorX(one)]));
}

function buildRearSuspension(){
  const hx = 0.6060, ax = D.rearAxleZ;
  const parts = [
    strut(V3(0.1500, 0.3960, ax + 0.352), V3(hx, 0.4120, ax + 0.012), { chord: 0.072, taper: 0.72, thickRatio: 0.24 }),
    strut(V3(0.1480, 0.3900, ax - 0.226), V3(hx, 0.4100, ax - 0.010), { chord: 0.066, taper: 0.74, thickRatio: 0.24 }),
    strut(V3(0.1760, 0.1620, ax + 0.336), V3(hx + 0.012, 0.1740, ax + 0.014), { chord: 0.086, taper: 0.70, thickRatio: 0.22 }),
    strut(V3(0.1800, 0.1580, ax - 0.218), V3(hx + 0.012, 0.1720, ax - 0.010), { chord: 0.080, taper: 0.72, thickRatio: 0.22 }),
    // pullrod: outboard high, inboard low
    strut(V3(hx - 0.004, 0.4020, ax - 0.052), V3(0.1560, 0.2060, ax + 0.318), { chord: 0.040, taper: 0.90, thickRatio: 0.34 }),
    // toe link
    strut(V3(0.1520, 0.2320, ax - 0.240), V3(hx + 0.004, 0.2420, ax - 0.098), { chord: 0.036, taper: 0.92, thickRatio: 0.34 }),
  ];
  const one = merge(parts);
  return logPart('suspension:rear', merge([one, mirrorX(one)]));
}

/* ---- gearbox / rear-end structure ---------------------------------------------------- */
function buildGearbox(){
  const zs = stationsFrom(-1.150, -1.760, 30);
  const loops = zs.map(z => {
    const t = clamp01((-1.150 - z) / 0.610);
    const w = lerp(0.176, 0.100, smooth01(t));
    const yT = lerp(0.402, 0.372, t), yB = lerp(0.176, 0.212, t);
    return ringFromClosed(podPts({ xIn: -w, xOut: w, yTop: yT, yBot: yB, nTop: 3.0, nBot: 2.4, nIn: 3.0 }, 40), z, 44);
  });
  const box = loftLoops(loops, { capStart: true, capEnd: true, capSegs: 3 });
  // driveshaft fairings
  const shafts = [];
  for (const s of [1, -1]){
    shafts.push(strut(V3(s * 0.150, 0.298, D.rearAxleZ), V3(s * 0.600, 0.300, D.rearAxleZ),
      { chord: 0.086, thickRatio: 0.42, taper: 0.86, steps: 6 }));
  }
  return logPart('rear:gearbox+driveshafts', merge([box, ...shafts]));
}
/* =====================================================================================
   COCKPIT, DRIVER AND FINE DETAIL
   The small parts are what make a hero model read as modelled rather than approximated:
   camera pods, pitot, antennas, jack points, tow eyes, seat belts, wheel display.
   Every one is a real emitted surface, sized in millimetres from the same contract.
   ===================================================================================== */

/* ---- driver ------------------------------------------------------------------------- */
const HEAD = { x: 0, y: 0.6720, z: 0.3400 };

function buildHelmet(){
  const parts = [];
  const rows = [];
  const N = 44;
  for (let i = 0; i <= 30; i++){
    const t = i / 30;                                   // 0 = crown, 1 = neck
    const phi = 0.055 * PI + t * PI * 0.865;            // never start on a degenerate pole
    const rBase = 0.1345;
    const rr = rBase * Math.sin(phi) * (1 + 0.10 * Math.pow(clamp01((t - 0.55) / 0.45), 1.5));
    const yy = HEAD.y + rBase * Math.cos(phi) * 1.055;
    const loop = [];
    for (let k = 0; k < N; k++){
      const a = k / N * TAU;
      const sx = Math.sin(a), cz = Math.cos(a);
      // longer front-to-back than side-to-side, with a slight jaw taper
      const fz = cz > 0 ? 1.10 : 1.02;
      loop.push(V3(HEAD.x + sx * rr * 0.955, yy, HEAD.z + cz * rr * fz));
    }
    rows.push(loop);
  }
  parts.push(loftLoops(rows, { capStart: true, capEnd: true, capSegs: 4, capBulge: 0.7 }));

  // aero spoiler on the crown
  const sp = [];
  for (let i = 0; i <= 10; i++){
    const t = i / 10;
    sp.push(V3(0, HEAD.y + 0.128 - 0.010 * t, HEAD.z - 0.048 - 0.086 * t));
  }
  parts.push(sweepSection(sp, (t) => squircle(lerp(0.052, 0.030, t), lerp(0.008, 0.005, t), 2.6, 12),
    { capStart: true, capEnd: true, capSegs: 2 }));
  return logPart('driver:helmet', merge(parts));
}

function buildVisor(){
  const rows = [];
  for (let i = 0; i <= 8; i++){
    const t = i / 8;
    const yy = HEAD.y + 0.052 - t * 0.072;
    const loop = [];
    const halfSpan = 1.02 + 0.14 * Math.sin(PI * t);
    for (let k = 0; k <= 26; k++){
      const a = -halfSpan + (k / 26) * halfSpan * 2;
      const rr = 0.1352 * Math.sqrt(Math.max(1 - Math.pow((yy - HEAD.y) / 0.142, 2), 0.05));
      loop.push(V3(HEAD.x + Math.sin(a) * rr * 0.965, yy, HEAD.z + Math.cos(a) * rr * 1.10));
    }
    rows.push(loop);
  }
  return logPart('driver:visor', gridGeometry(rows, { closeU: false, flip: false }));
}

function buildDriverBody(){
  const parts = [];
  // shoulders / torso rising out of the tub
  const rows = [];
  for (let i = 0; i <= 16; i++){
    const t = i / 16;
    const z = lerp(0.520, 0.180, t);
    const w = 0.150 + 0.086 * Math.sin(PI * Math.pow(t, 0.75));
    const yT = 0.512 + 0.052 * Math.sin(PI * Math.pow(t, 0.8));
    const yB = 0.352;
    rows.push(ringFromClosed(podPts({ xIn: -w, xOut: w, yTop: yT, yBot: yB, nTop: 2.6, nBot: 2.2, nIn: 2.6 }, 34), z, 38));
  }
  parts.push(loftLoops(rows, { capStart: true, capEnd: true, capSegs: 3 }));
  // HANS collar
  const collar = [];
  for (let i = 0; i <= 8; i++){
    const t = i / 8;
    const w = 0.128 + 0.046 * t;
    collar.push(ringFromClosed(podPts({ xIn: -w, xOut: w, yTop: 0.566 - t * 0.018, yBot: 0.512 - t * 0.020, nTop: 2.4, nBot: 2.2, nIn: 2.4 }, 28),
      lerp(0.400, 0.250, t), 30));
  }
  parts.push(loftLoops(collar, { capStart: true, capEnd: true, capSegs: 2 }));
  // upper arms reaching the wheel
  for (const s of [1, -1]){
    parts.push(strut(V3(s * 0.166, 0.480, 0.352), V3(s * 0.118, 0.512, 0.596),
      { chord: 0.104, thickRatio: 0.86, taper: 0.80, steps: 8 }));
    // glove
    const gl = [];
    for (let i = 0; i <= 8; i++){
      const t = i / 8, r = 0.050 * Math.sin(PI * (0.22 + t * 0.66));
      const loop = [];
      for (let k = 0; k < 22; k++){ const a = k / 22 * TAU; loop.push(V3(s * (0.112 + Math.sin(a) * r), 0.522 + Math.cos(a) * r * 1.15, lerp(0.596, 0.660, t))); }
      gl.push(loop);
    }
    parts.push(loftLoops(gl, { capStart: true, capEnd: true, capSegs: 2 }));
  }
  return logPart('driver:body', merge(parts));
}

function buildSteeringWheel(){
  const parts = [];
  const cz = 0.6480, cy = 0.5280, tilt = -0.42;
  const R = new THREE.Matrix4().makeRotationX(tilt);
  // butterfly rim outline in the wheel plane
  const out = [
    [-0.108,0.052],[-0.052,0.076],[0.052,0.076],[0.108,0.052],[0.112,-0.010],
    [0.086,-0.058],[0.042,-0.074],[-0.042,-0.074],[-0.086,-0.058],[-0.112,-0.010],
  ];
  const holes = [
    [[-0.086,0.040],[-0.040,0.058],[-0.040,0.010],[-0.086,0.006]],
    [[0.086,0.040],[0.040,0.058],[0.040,0.010],[0.086,0.006]],
  ];
  const body = plate(spline2(out.map(p => V2(p[0], p[1])), 110, { closed: true }), {
    thickness: 0.030, bevel: 0.006, bevelSegs: 3,
    holes: holes.map(h => spline2(h.map(p => V2(p[0], p[1])), 40, { closed: true }).reverse()),
  });
  body.applyMatrix4(R); body.translate(0, cy, cz);
  parts.push(body);
  // grips
  for (const s of [1, -1]){
    const grip = [];
    for (let i = 0; i <= 8; i++){
      const t = i / 8;
      grip.push(V3(s * (0.100 + 0.006 * t), 0.030 - 0.076 * t, 0.014));
    }
    const g = sweepSection(grip, (t) => squircle(0.019, 0.016, 2.6, 12), { capStart: true, capEnd: true, capSegs: 2 });
    g.applyMatrix4(R); g.translate(0, cy, cz);
    parts.push(g);
  }
  // column
  const col = [V3(0, cy - 0.020, cz - 0.010), V3(0, cy - 0.062, cz - 0.140)];
  parts.push(sweepTube(col, 0.020, 14, { capStart: true, capEnd: true }));

  const face = plate([[-0.070,-0.030],[0.070,-0.030],[0.070,0.030],[-0.070,0.030]].map(p => V2(p[0], p[1])),
    { thickness: 0.004, bevel: 0.001 });
  face.applyMatrix4(R); face.translate(0, cy + 0.006, cz + 0.017);
  return { wheel: logPart('cockpit:steeringWheel', merge(parts)), face: logPart('cockpit:wheelDisplay', face) };
}

function buildBelts(){
  const parts = [];
  for (const s of [1, -1]){
    for (const spread of [0.052, 0.112]){
      const p = [];
      for (let i = 0; i <= 10; i++){
        const t = i / 10;
        p.push(V3(s * lerp(spread, spread * 1.9, t), lerp(0.502, 0.372, t), lerp(0.440, 0.238, t)));
      }
      parts.push(sweepSection(p, () => squircle(0.024, 0.0035, 2.2, 10), { capStart: true, capEnd: true, capSegs: 2 }));
    }
  }
  return logPart('cockpit:harness', merge(parts));
}

/* ---- camera pods, antennas, pitot ---------------------------------------------------- */
function buildCameraPods(){
  const parts = [], lenses = [];
  // slim streamlined housing: long in z, small in section — a camera fairing, not a ball
  const pod = (x, y, z, sc) => {
    const rows = [];
    const L = 0.108 * sc;
    for (let i = 0; i <= 14; i++){
      const t = i / 14;
      const taper = Math.pow(Math.sin(PI * (0.10 + t * 0.86)), 0.55);
      const w = sc * 0.0215 * taper;
      const h = sc * 0.0195 * taper;
      const zz = z + L * (0.42 - t);
      const loop = [];
      for (let k = 0; k < 24; k++){
        const a = k / 24 * TAU, sx = Math.sin(a), cy = Math.cos(a);
        loop.push(V3(x + Math.sign(sx) * Math.pow(Math.abs(sx), 0.78) * w,
                     y + Math.sign(cy) * Math.pow(Math.abs(cy), 0.78) * h, zz));
      }
      rows.push(loop);
    }
    parts.push(loftLoops(rows, { capStart: true, capEnd: true, capSegs: 3, capBulge: 0.45 }));
    const lens = latheX(spline2([V2(0.0008, 0), V2(sc * 0.0140, 0), V2(sc * 0.0150, sc * 0.0060)], 10, { closed: false }), 20);
    lens.applyMatrix4(new THREE.Matrix4().makeRotationY(-PI * 0.5));
    lens.translate(x, y, z + L * 0.44);
    lenses.push(lens);
  };
  pod(0, 0.9700, -0.2020, 1.25);                    // T-cam above the airbox
  pod(0.1580, 0.4620, 2.1400, 0.85);                // nose cameras
  pod(-0.1580, 0.4620, 2.1400, 0.85);
  pod(0.2440, 0.6380, 0.9200, 0.70);                // halo-side pods
  pod(-0.2440, 0.6380, 0.9200, 0.70);

  // pitot boom on the nose tip
  const boom = [V3(0, 0.3420, 2.7560), V3(0, 0.3480, 2.8620)];
  parts.push(sweepTube(boom, (t) => lerp(0.0075, 0.0042, t), 12, { capStart: true, capEnd: true }));

  // GPS / telemetry blisters on the engine cover
  for (const [x, y, z, r] of [[0, 0.7180, -0.7400, 0.030], [0.0860, 0.6820, -0.9100, 0.024], [-0.0860, 0.6820, -0.9100, 0.024]]){
    const g = latheY(spline2([V2(0.001, y + r * 0.62), V2(r * 0.62, y + r * 0.44), V2(r, y), V2(r * 1.02, y - r * 0.5)], 14, { closed: false }), 24);
    g.translate(x, 0, z);
    parts.push(g);
  }
  return { pods: logPart('detail:cameraPods', merge(parts)), lenses: logPart('detail:lenses', merge(lenses)) };
}

/* ---- jack points, tow eyes, tethers --------------------------------------------------- */
function buildServiceFittings(){
  const parts = [];
  // rear jack bracket
  const jack = [];
  for (let i = 0; i <= 8; i++){
    const t = i / 8;
    const loop = [];
    for (let k = 0; k < 20; k++){
      const a = k / 20 * TAU;
      loop.push(V3(Math.sin(a) * lerp(0.030, 0.019, t), 0.360 + Math.cos(a) * lerp(0.022, 0.015, t), lerp(-2.100, -2.230, t)));
    }
    jack.push(loop);
  }
  parts.push(loftLoops(jack, { capStart: true, capEnd: true, capSegs: 2 }));
  // front tow eye under the nose
  const eye = [];
  const n = 22;
  for (let i = 0; i < n; i++){ const a = i / n * TAU; eye.push(V2(Math.cos(a) * 0.028, Math.sin(a) * 0.028)); }
  const eyeHole = [];
  for (let i = n - 1; i >= 0; i--){ const a = i / n * TAU; eyeHole.push(V2(Math.cos(a) * 0.014, Math.sin(a) * 0.014)); }
  const g = plate(eye, { thickness: 0.014, bevel: 0.003, holes: [eyeHole] });
  g.applyMatrix4(new THREE.Matrix4().makeRotationY(PI * 0.5));
  g.translate(0, 0.2660, 2.4600);
  parts.push(g);
  // wheel tethers
  for (const s of [1, -1]){
    for (const [ax, hx] of [[D.frontAxleZ, 0.5600], [D.rearAxleZ, 0.5400]]){
      parts.push(sweepTube([V3(s * 0.200, 0.300, ax + 0.060), V3(s * hx, 0.300, ax + 0.030)], 0.0075, 8, { capStart: true, capEnd: true }));
    }
  }
  return logPart('detail:serviceFittings', merge(parts));
}

/* ---- radiator cores visible through the sidepod inlet ---------------------------------- */
function buildRadiatorCore(){
  const parts = [];
  for (const s of [1, -1]){
    const g = plate([[-0.086,-0.062],[0.086,-0.062],[0.086,0.062],[-0.086,0.062]].map(p => V2(p[0], p[1])),
      { thickness: 0.010, bevel: 0.001 });
    g.applyMatrix4(new THREE.Matrix4().makeRotationY(0.16 * s));
    g.translate(s * 0.3820, 0.3760, 0.4200);
    parts.push(g);
  }
  return logPart('detail:radiatorCore', merge(parts));
}

/* =====================================================================================
   ASSEMBLY
   The model is a semantic build order, not a bag of meshes: every part is added with the
   material identity it is made of, its own shadow participation, and a name that matches
   the part log.  Corner hardware is emitted ONCE per axle and mirrored per side, so the
   left and right wheels share geometry while keeping opposite winding and UV handedness.
   ===================================================================================== */

/** Complete car: geometry, materials, corner hardware, and presentation state. */
export function createFormulaOneRaceCar(){
  const materials = buildMaterials();
  const logStart = PART_LOG.length;

  const car = new THREE.Group();
  car.name = 'VF-26';
  const meshes = [];
  function add(geometry, material, name, parent = car, shadow = true){
    if (!geometry) return null;
    const m = new THREE.Mesh(geometry, material);
    m.name = name || material.name;
    m.castShadow = shadow; m.receiveShadow = shadow;
    parent.add(m);
    meshes.push(m);
    return m;
  }
  const pair = (geometry, material, name) => { add(geometry, material, name); add(mirrorX(geometry), material, name + '.L'); };

  /* ---- monocoque, nose, cockpit ---- */
  add(buildHull(), MAT.body, 'hull');
  add(buildCockpitLiner(), MAT.padding, 'cockpitLiner');
  add(buildCockpitRim(), MAT.carbonGloss, 'cockpitRim');
  add(buildHeadrest(), MAT.padding, 'headrest');

  /* ---- sidepods and cooling ---- */
  pair(buildSidepod(), MAT.body, 'sidepod');
  const inlet = buildSidepodInlet();
  pair(inlet.lip, MAT.bodyFine, 'inletLip');
  pair(inlet.duct, MAT.carbonDuct, 'inletDuct');
  add(buildRadiatorCore(), MAT.darkAlloy, 'radiator');
  add(buildLouvres(), MAT.carbonMatte, 'louvres');

  /* ---- airbox, roll structure, halo ---- */
  const ab = buildAirbox();
  add(ab.shell, MAT.body, 'airbox');
  add(buildSharkFin(), MAT.body, 'sharkFin');
  add(buildHalo(), MAT.carbonGloss, 'halo');
  add(buildHaloVane(), MAT.carbonGloss, 'haloVane');
  const mir = buildMirrors();
  add(mir.housing, MAT.bodyFine, 'mirrors');
  add(mir.glass, MAT.mirror, 'mirrorGlass', car, false);

  /* ---- floor, tunnels, diffuser ---- */
  add(buildFloor(), MAT.floor, 'floor');
  add(buildDiffuserStrakes(), MAT.carbonGloss, 'diffuserStrakes');
  add(buildFloorFences(), MAT.carbonGloss, 'floorFences');
  add(buildPlank(), MAT.plank, 'plank');
  add(buildVortexGenerators(), MAT.carbonGloss, 'vortexGenerators');

  /* ---- aerodynamic surfaces and rear end ---- */
  add(buildFrontWing(), MAT.wing, 'frontWing');
  add(buildFrontEndplate(), MAT.plate, 'frontEndplate');
  add(buildNosePylons(), MAT.plate, 'nosePylons');
  add(buildRearWing(), MAT.wing, 'rearWing');
  add(buildRearEndplate(), MAT.plate, 'rearEndplate');
  add(buildRearPylons(), MAT.carbonGloss, 'rearPylons');
  add(buildBeamWing(), MAT.wing, 'beamWing');
  add(buildRearStructure(), MAT.body, 'crashStructure');
  add(buildExhaust(), MAT.exhaust, 'exhaust');
  add(buildRainLight(), MAT.rainLight, 'rainLight', car, false);
  add(buildGearbox(), MAT.carbonMatte, 'gearbox');

  /* ---- corners ---- */
  const wheels = [];
  const cornerCache = {};
  function buildCorner(front, side){
    const R     = front ? D.frontR : D.rearR;
    const halfW = (front ? D.frontTyre.width : D.rearTyre.width) * 0.5;
    const rimR  = D.frontTyre.rimOD * 0.5;
    const hubX  = front ? D.frontHubX : D.rearHubX;
    const axleZ = front ? D.frontAxleZ : D.rearAxleZ;

    const key = front ? 'F' : 'R';
    if (!cornerCache[key]){
      const t = buildTyre({ R, halfW, rimR, drop: front ? 0.0135 : 0.0150 });
      cornerCache[key] = {
        tyreRound: t.round, tyreLoaded: t.loaded,
        rim: buildRim({ rimR, halfW }),
        cover: buildRimCover({ rimR, halfW }),
        disc: buildBrakeDisc({ rOut: front ? 0.1550 : 0.1500, rIn: 0.0760, thick: front ? 0.032 : 0.030 }),
        caliper: buildCaliper({ r: front ? 0.1700 : 0.1650 }),
        duct: buildBrakeDuct({ R, halfW, front }),
        upright: buildUpright({ front }),
      };
    }
    const C = cornerCache[key];
    const M = side > 0 ? (g => g) : mirrorX;

    const root = new THREE.Group();
    root.position.set(side * hubX, R, axleZ);
    car.add(root);

    const spin = new THREE.Group();
    root.add(spin);
    const tyre = add(M(C.tyreLoaded), side > 0 ? MAT.rubberMirror : MAT.rubber, `tyre.${key}${side > 0 ? 'L' : 'R'}`, spin);
    add(M(C.rim), MAT.rim, 'rim', spin);
    add(M(C.cover), MAT.rimCover, 'rimCover', spin);
    add(M(C.disc), MAT.brakeDisc, 'brakeDisc', spin);

    add(M(C.caliper), MAT.anodRed, 'caliper', root);
    add(M(C.duct), MAT.carbonDuct, 'brakeDuct', root);
    add(M(C.upright), MAT.titanium, 'upright', root);

    wheels.push({ spin, tyre, round: M(C.tyreRound), loaded: M(C.tyreLoaded), front });
  }
  for (const front of [true, false]) for (const side of [1, -1]) buildCorner(front, side);
  add(buildFrontSuspension(), MAT.carbonGloss, 'frontSuspension');
  add(buildRearSuspension(), MAT.carbonGloss, 'rearSuspension');

  /* ---- driver, cockpit, fine detail ---- */
  add(buildDriverBody(), MAT.suit, 'driver');
  add(buildHelmet(), MAT.helmet, 'helmet');
  add(buildVisor(), MAT.visor, 'visor', car, false);
  add(buildBelts(), MAT.padding, 'harness');
  const sw = buildSteeringWheel();
  add(sw.wheel, MAT.darkAlloy, 'steeringWheel');
  add(sw.face, MAT.display, 'wheelDisplay', car, false);
  const cams = buildCameraPods();
  add(cams.pods, MAT.bodyFine, 'cameraPods');
  add(cams.lenses, MAT.lens, 'lenses', car, false);
  add(buildServiceFittings(), MAT.titanium, 'serviceFittings');

  const stats = PART_LOG.slice(logStart);
  const totalTriangles = stats.reduce((sum, p) => sum + p.tris, 0);
  const originalMaterial = new Map();
  let rolling = false;

  return {
    object: car,
    meshes,
    wheels,
    materials,
    uniforms: U,
    stats,
    totalTriangles,

    /** Structural read of the emitted surfaces, with materials removed from the answer. */
    setWireframe(on){
      for (const m of meshes){
        if (on){
          if (!originalMaterial.has(m)) originalMaterial.set(m, m.material);
          m.material = MAT.wireframe;
        } else if (originalMaterial.has(m)){
          m.material = originalMaterial.get(m);
        }
      }
    },
    /** 0 shows the bare structural finish under the paint. */
    setLivery(on){ U.livery.value = on ? 1.0 : 0.0; },
    /** Which projector plane won each surface, as a two-colour field. */
    setProjectorDebug(on){ U.projDbg.value = on ? 1.0 : 0.0; },
    /**
     * Rolling swaps in the undeflected carcass. The contact patch is GEOMETRY, so a
     * parked tyre cannot simply be spun — the flat would orbit with it.
     */
    setRolling(on){
      rolling = on;
      for (const w of wheels) w.tyre.geometry = on ? w.round : w.loaded;
    },
    update({ delta = 0, elapsed = 0 } = {}){
      if (rolling){
        for (const w of wheels) w.spin.rotation.x -= delta * (w.front ? 7.4 : 7.3);
      }
      U.discGlow.value = 0.16 + 0.05 * Math.sin(elapsed * 0.6);
    },
    dispose(){
      const geometries = new Set();
      car.traverse((o) => { if (o.isMesh) geometries.add(o.geometry); });
      for (const w of wheels){ geometries.add(w.round); geometries.add(w.loaded); }
      for (const g of geometries) g.dispose();
      for (const m of Object.values(materials)) m.dispose?.();
      for (const t of Object.values(TEX)) t.dispose?.();
      PART_LOG.length = logStart;
    },
  };
}
