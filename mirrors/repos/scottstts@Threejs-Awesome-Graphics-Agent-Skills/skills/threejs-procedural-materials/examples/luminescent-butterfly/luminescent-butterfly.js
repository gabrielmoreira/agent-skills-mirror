import * as THREE from 'three/webgpu';
import {
  Fn, uniform, uv, vec2, vec3, vec4, float, color, texture, time, mix, smoothstep, step, sin, cos, fract, floor,
  dot, length, normalize, max, min, pow, abs, sqrt, exp, saturate, attribute, positionLocal, positionWorld,
  normalWorld, cameraPosition, normalMap, pass, renderOutput, mx_noise_float, mx_fractal_noise_float, screenUV,
  instancedBufferAttribute, viewportSize, positionView, cameraViewMatrix, normalView, BRDF_Lambert,
  perspectiveDepthToViewZ, convertToTexture, Loop, select, clamp, fwidth, atan, mrt, output, instanceIndex, varying, luminance,
  dFdx, dFdy, D_GGX, positionViewDirection, tangentView, bitangentView, log2, If, cross,
  reflect, cameraWorldMatrix, pmremTexture, atan as atanTSL, builtinAOContext, directionToColor, colorToDirection, sample,
  cameraProjectionMatrix, mod, frontFacing
} from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
import { ao } from 'three/addons/tsl/display/GTAONode.js';
export const LUMINESCENT_BUTTERFLY_DEFAULTS = {
  seed: 1729,
  exposure: 0.3, // starting value; the camera meter takes over (see "exposure")
  meter: { middleGray: 0.18, compensationEV: -2.8, min: 0.05, max: 2.0, // night scene: subject placed ~3 stops under middle grey
            up: 3.2, down: 1.1, every: 12 },
  wing: { gain: 4.0, membrane: 0.85, vein: 1.1, spot: 8 }, // gain: strength of the luminescence (the scene's main light)
  bloom: { strength: 0.45, radius: 0.55, threshold: 1.05 }, // threshold on the exposed (sensor) signal
  ao: { radius: 0.8, thickness: 0.6 }, // cm: about the gap between petal layers
  dof: { aperture: 0.032, samples: 48, highlight: 5.5 }, // highlight: luminance above which light is scattered // thin-lens aperture as CoC at infinity (fraction of frame height)
  bflyYaw: -7,
};
const rng = (seed) => { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
const lerp = (a, b, t) => a + (b - a) * t;
const sstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const D2R = Math.PI / 180;
const V3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
/* ============================================================ TSL helpers */
const hash21 = Fn(([p]) => fract(sin(dot(p, vec2(127.1, 311.7))).mul(43758.5453)));

const twinkle = Fn(([p, rate]) => {
  const ip = floor(p);
  const fp = fract(p);
  const h = hash21(ip);
  const h2 = hash21(ip.add(13.7));
  const c = vec2(h, h2).mul(0.6).add(0.2);
  const d = length(fp.sub(c));
  const on = step(0.8, hash21(ip.add(5.3)));
  const tw = sin(time.mul(mix(0.6, 2.4, h2).mul(rate)).add(h.mul(6.283))).mul(0.5).add(0.5);
  return on.mul(smoothstep(0.2, 0.0, d)).mul(tw.mul(tw).mul(tw));
});

/** A centimetre-scale luminescent butterfly with coherent articulated emission.
 * Supply a perch mesh and scene callbacks; own renderer, camera and navigation.
 */
export function taperTube(pts, r0, r1, seg = 32, radial = 7) {
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  const g = new THREE.TubeGeometry(curve, seg, 1, radial, false);
  const p = g.attributes.position, c = V3(), v = V3();
  for (let i = 0; i <= seg; i++) {
    curve.getPointAt(i / seg, c);
    const r = lerp(r0, r1, i / seg);
    for (let j = 0; j <= radial; j++) { const id = i * (radial + 1) + j; v.fromBufferAttribute(p, id).sub(c).multiplyScalar(r).add(c); p.setXYZ(id, v.x, v.y, v.z); }
  }
  g.computeVertexNormals();
  return g;
}

export async function createLuminescentButterfly({
  renderer, scene, camera, perchSurface, perchMesh, perchCenter, hero, setupStage = async () => {},
}) {
const P = LUMINESCENT_BUTTERFLY_DEFAULTS;
let NO_POST = false;
/* ============================================================ wings (authored masks) */
function catmullClosed(pts, n) {
  const c = new THREE.CatmullRomCurve3(pts.map(([a, b]) => V3(a, b, 0)), true, 'centripetal');
  return c.getSpacedPoints(n).slice(0, n).map((p) => [p.x, p.y]);
}

/* Wing painter. Coordinates are centimetres in the wing plane: a = chord (forward +), b = span (up +),
   root at the origin. Produces colour/coverage, masks (veins, gold spots, dark scales, cyan scales)
   and a corrugation normal map, all from one vein layout so every channel agrees. */
function makeWing(def) {
  const rand = rng(def.seed);
  let outline = catmullClosed(def.ctrl, 900);
  const rootDist = (p) => Math.hypot(p[0], p[1]);
  const centroid0 = outline.reduce((s, p) => [s[0] + p[0] / outline.length, s[1] + p[1] / outline.length], [0, 0]);
  if (def.scallop) {
    const idx = outline.map((_, i) => i).filter((i) => rootDist(outline[i]) > def.scallop.minR && outline[i][1] > (def.scallop.minB ?? -Infinity));
    const i0 = idx[0], i1 = idx[idx.length - 1];
    outline = outline.map(([a, b], i) => {
      if (i < i0 || i > i1) return [a, b];
      const s = (i - i0) / (i1 - i0);
      const fade = sstep(0, 0.05, s) * sstep(1, 0.95, s);
      const notch = def.scallop.depth * (1 - Math.pow(Math.abs(Math.sin(Math.PI * s * def.scallop.count)), 0.5)) * fade;
      const dx = centroid0[0] - a, dy = centroid0[1] - b, dl = Math.hypot(dx, dy);
      return [a + dx / dl * notch, b + dy / dl * notch];
    });
  }
  if (def.minB !== undefined) outline = outline.map(([a, b]) => [a, Math.max(b, def.minB)]);
  let minA = Infinity, maxA = -Infinity, minB = Infinity, maxB = -Infinity;
  for (const [a, b] of outline) { minA = Math.min(minA, a); maxA = Math.max(maxA, a); minB = Math.min(minB, b); maxB = Math.max(maxB, b); }
  const pad = 0.16; minA -= pad; maxA += pad; minB -= pad; maxB += pad;
  const wA = maxA - minA, wB = maxB - minB;
  const ppc = 2048 / Math.max(wA, wB);
  const W = Math.ceil(wA * ppc), H = Math.ceil(wB * ppc);
  const X = (a) => (a - minA) * ppc, Y = (b) => (maxB - b) * ppc;
  const mk = (fill) => { const c = document.createElement('canvas'); c.width = W; c.height = H; const x = c.getContext('2d', { willReadFrequently: true }); x.fillStyle = fill; x.fillRect(0, 0, W, H); x.lineCap = 'round'; x.lineJoin = 'round'; return x; };
  const path = (ctx) => { ctx.beginPath(); outline.forEach(([a, b], i) => i ? ctx.lineTo(X(a), Y(b)) : ctx.moveTo(X(a), Y(b))); ctx.closePath(); };
  const centroid = outline.reduce((s, p) => [s[0] + p[0] / outline.length, s[1] + p[1] / outline.length], [0, 0]);
  const outward = (i) => { const [a, b] = outline[i]; const dx = a - centroid[0], dy = b - centroid[1], l = Math.hypot(dx, dy); return [dx / l, dy / l]; };

  // vein layout: discal cell -> evenly spaced points on the outer margin
  const farIdx = outline.map((_, i) => i).filter((i) => rootDist(outline[i]) > def.veinMinR);
  const tg0 = farIdx[0], tg1 = farIdx[farIdx.length - 1];
  const cellPts = def.cell;
  const cellLen = [0]; let acc = 0;
  for (let i = 1; i < cellPts.length; i++) { acc += Math.hypot(cellPts[i][0] - cellPts[i - 1][0], cellPts[i][1] - cellPts[i - 1][1]); cellLen.push(acc); }
  const cellAt = (f) => { const L = f * acc; let i = 1; while (i < cellLen.length - 1 && cellLen[i] < L) i++; const k = (L - cellLen[i - 1]) / (cellLen[i] - cellLen[i - 1]); return [lerp(cellPts[i - 1][0], cellPts[i][0], k), lerp(cellPts[i - 1][1], cellPts[i][1], k)]; };
  const veins = [];
  for (let k = 0; k < def.veins; k++) {
    const ti = Math.round(lerp(tg0, tg1, k / (def.veins - 1)));
    const o = cellAt(k / (def.veins - 1)), t = outline[ti], ol = Math.hypot(o[0], o[1]) || 1;
    veins.push({ o, t, ti, c: [lerp(o[0], t[0], 0.45) + o[0] / ol * 0.16, lerp(o[1], t[1], 0.45) + o[1] / ol * 0.16] });
  }
  const bez = (v, s) => [
    (1 - s) * (1 - s) * v.o[0] + 2 * (1 - s) * s * v.c[0] + s * s * v.t[0],
    (1 - s) * (1 - s) * v.o[1] + 2 * (1 - s) * s * v.c[1] + s * s * v.t[1]];
  const cellMid = (k, s) => { const p = bez(veins[k], s), q = bez(veins[k + 1], s); return [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]; };
  const cellWidth = (k, s) => { const p = bez(veins[k], s), q = bez(veins[k + 1], s); return Math.hypot(p[0] - q[0], p[1] - q[1]); };
  const along = (ctx, fn, s0, s1, wfn, n = 28) => {
    let prev = fn(s0);
    for (let i = 1; i <= n; i++) {
      const s = lerp(s0, s1, i / n), cur = fn(s);
      ctx.lineWidth = Math.max(0.5, wfn(s) * ppc);
      ctx.beginPath(); ctx.moveTo(X(prev[0]), Y(prev[1])); ctx.lineTo(X(cur[0]), Y(cur[1])); ctx.stroke();
      prev = cur;
    }
  };
  const polyline = (ctx, pts, w) => { ctx.lineWidth = w * ppc; ctx.beginPath(); pts.forEach(([a, b], i) => i ? ctx.lineTo(X(a), Y(b)) : ctx.moveTo(X(a), Y(b))); ctx.stroke(); };
  const radial = (ctx, a, b, r, stops) => {
    const g = ctx.createRadialGradient(X(a), Y(b), 0, X(a), Y(b), r * ppc);
    stops.forEach(([o, c]) => g.addColorStop(o, c));
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(X(a), Y(b), r * ppc, 0, Math.PI * 2); ctx.fill();
  };
  const drawVeins = (ctx, scale) => {
    veins.forEach((v) => along(ctx, (s) => bez(v, s), 0, 1, (s) => lerp(0.026, 0.011, s) * scale));
    polyline(ctx, cellPts, 0.02 * scale);
    (def.rootVeins || []).forEach((pts) => polyline(ctx, pts, 0.03 * scale));
  };
  const nCells = veins.length - 1;
  // soft layers are drawn sharp on a scratch canvas, then blurred once while compositing
  const layer = (ctx, blurCm, draw, op = 'source-over', alpha = 1) => {
    const t = document.createElement('canvas'); t.width = W; t.height = H;
    const tx = t.getContext('2d'); tx.lineCap = 'round'; tx.lineJoin = 'round';
    draw(tx);
    ctx.save(); ctx.globalCompositeOperation = op; ctx.globalAlpha = alpha;
    ctx.filter = blurCm > 0 ? `blur(${Math.max(1, Math.round(blurCm * ppc))}px)` : 'none';
    ctx.drawImage(t, 0, 0); ctx.restore();
  };
  const bandAt = (ctx, style, k) => { // outer dark band hugging the margin, with an organic inner edge
    ctx.fillStyle = style;
    outline.forEach(([a, b], i) => {
      const kk = sstep(def.bandMinR, def.bandMinR + 0.45, rootDist(outline[i])) * sstep((def.bandMinB ?? -1e9) - 0.2, def.bandMinB ?? -1e9, b);
      if (kk <= 0) return;
      const wob = 0.86 + 0.2 * Math.sin(i * 0.05 + 1.3) * Math.sin(i * 0.019);
      ctx.beginPath(); ctx.arc(X(a), Y(b), def.band * kk * wob * k * ppc, 0, Math.PI * 2); ctx.fill();
    });
  };

  /* ---------------- colour */
  const cx = mk('#0a1a5a');
  cx.save(); path(cx); cx.clip();
  {
    const g = cx.createRadialGradient(X(0), Y(0), 0, X(0), Y(0), def.length * ppc);
    [[0, '#fff3da'], [0.1, '#e4f4ff'], [0.24, '#8fd0ff'], [0.42, '#3f92ff'], [0.62, '#215ce8'], [0.82, '#1534a6'], [1, '#0c206f']]
      .forEach(([o, c]) => g.addColorStop(o, c));
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
  }
  // cyan scale streaks running down the centre of every cell
  layer(cx, 0.05, (t) => { t.strokeStyle = 'rgba(70,215,255,0.55)'; for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.14, 0.8, (s) => cellWidth(k, s) * 0.42 * Math.sin(Math.PI * (s - 0.1) / 0.75)); }, 'screen');
  layer(cx, 0.012, (t) => { t.strokeStyle = 'rgba(200,250,255,0.45)'; for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.2, 0.7, (s) => cellWidth(k, s) * 0.1); }, 'screen');
  // smoky submarginal scales and costal patches
  layer(cx, 0.04, (t) => {
    t.strokeStyle = 'rgba(4,10,40,1)';
    for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.64, 0.95, (s) => cellWidth(k, s) * 0.95, 12);
    (def.patches || []).forEach(([a, b, r]) => radial(t, a, b, r, [[0, 'rgba(3,8,32,1)'], [1, 'rgba(3,8,32,0)']]));
  }, 'source-over', 0.5);
  layer(cx, 0.015, (t) => bandAt(t, 'rgba(3,7,26,1)', 1), 'source-over', 0.88);
  // cyan eyelets in the dark zone, one per cell
  const eyelets = [];
  for (let k = 0; k < nCells; k++) {
    const p = cellMid(k, 0.8), r = cellWidth(k, 0.8) * lerp(0.16, 0.24, rand());
    eyelets.push([p[0], p[1], r]);
    // irregular cyan scale patch, stretched along the cell
    for (let n = 0; n < 14; n++) {
      const q = cellMid(k, 0.7 + rand() * 0.22), rr = r * lerp(0.15, 0.5, rand());
      const off = cellWidth(k, 0.8) * 0.35;
      radial(cx, q[0] + (rand() - 0.5) * off, q[1] + (rand() - 0.5) * off, rr, [[0, `rgba(120,230,255,${lerp(0.25, 0.6, rand())})`], [0.6, 'rgba(45,150,255,0.18)'], [1, 'rgba(30,90,255,0)']]);
    }
  }
  // frost: fine crystalline streaks combed along the wing, densest mid-wing
  for (let n = 0; n < 14000; n++) {
    const a = lerp(minA, maxA, rand()), b = lerp(minB, maxB, rand());
    const d = Math.hypot(a, b) || 1;
    const mid = Math.exp(-Math.pow((d / def.length - 0.5) / 0.32, 2));
    if (rand() > 0.55 + 0.45 * mid) continue;
    const ang = Math.atan2(b, a) + (rand() - 0.5) * (rand() < 0.3 ? 1.8 : 0.6);
    const len = lerp(0.025, 0.13, Math.pow(rand(), 1.5));
    cx.strokeStyle = rand() < 0.75 ? `rgba(225,248,255,${lerp(0.06, 0.34, rand())})` : `rgba(10,30,120,${lerp(0.15, 0.4, rand())})`;
    cx.lineWidth = lerp(0.5, 1.3, rand());
    cx.beginPath(); cx.moveTo(X(a), Y(b)); cx.lineTo(X(a + Math.cos(ang) * len), Y(b + Math.sin(ang) * len)); cx.stroke();
  }
  for (let n = 0; n < 6000; n++) {
    const a = lerp(minA, maxA, rand()), b = lerp(minB, maxB, rand());
    cx.fillStyle = rand() < 0.8 ? `rgba(220,246,255,${lerp(0.12, 0.55, rand())})` : `rgba(110,255,255,${lerp(0.2, 0.75, rand())})`;
    cx.beginPath(); cx.arc(X(a), Y(b), lerp(0.4, 1.5, rand()), 0, Math.PI * 2); cx.fill();
  }
  // veins as little tubes: dark edge, gold body, pale highlight
  cx.strokeStyle = 'rgba(40,28,10,0.55)'; drawVeins(cx, 1.7);
  cx.strokeStyle = '#d6a456'; drawVeins(cx, 1.0);
  cx.strokeStyle = 'rgba(255,242,205,0.9)'; drawVeins(cx, 0.4);
  // costa and margin: dark sclerotised edge with a fine gold line
  cx.strokeStyle = '#05071a'; cx.lineWidth = 0.05 * ppc; path(cx); cx.stroke();
  cx.strokeStyle = 'rgba(255,214,150,0.85)'; cx.lineWidth = 0.012 * ppc; path(cx); cx.stroke();
  cx.restore();

  /* ---------------- cilia fringe (outside the membrane) */
  const fringe = [];
  for (let i = 0; i < outline.length; i += 2) {
    if (rootDist(outline[i]) < def.fringeMinR) continue;
    const [ox, oy] = outward(i), j = (rand() - 0.5) * 0.5;
    const len = lerp(0.045, 0.1, rand());
    const [a, b] = outline[i];
    fringe.push([a, b, a + (ox * Math.cos(j) - oy * Math.sin(j)) * len, b + (ox * Math.sin(j) + oy * Math.cos(j)) * len]);
  }
  const drawFringe = (ctx, style, w) => { ctx.strokeStyle = style; ctx.lineWidth = w; fringe.forEach(([a, b, c, d]) => { ctx.beginPath(); ctx.moveTo(X(a), Y(b)); ctx.lineTo(X(c), Y(d)); ctx.stroke(); }); };
  drawFringe(cx, 'rgba(255,226,175,0.8)', 1.1);

  /* ---------------- coverage */
  const ax = mk('#000');
  ax.fillStyle = '#fff'; path(ax); ax.fill();
  drawFringe(ax, 'rgba(255,255,255,0.55)', 1.2);

  /* ---------------- masks */
  const vx = mk('#000'); vx.save(); path(vx); vx.clip();
  vx.strokeStyle = '#fff'; drawVeins(vx, 0.9);
  vx.lineWidth = 0.02 * ppc; path(vx); vx.stroke();
  vx.restore();

  const sx = mk('#000');
  sx.save(); path(sx); sx.clip();
  const dot = (a, b, r, i = 1) => radial(sx, a, b, r, [[0, `rgba(255,255,255,${i})`], [0.5, `rgba(255,255,255,${i * 0.75})`], [1, 'rgba(255,255,255,0)']]);
  veins.forEach((v) => { const [ox, oy] = outward(v.ti); dot(v.t[0] - ox * 0.06, v.t[1] - oy * 0.06, 0.05); });
  for (let k = 0; k < nCells; k++) {
    const mi = Math.round((veins[k].ti + veins[k + 1].ti) / 2), [ox, oy] = outward(mi), [a, b] = outline[mi];
    dot(a - ox * def.band * 0.42, b - oy * def.band * 0.42, lerp(0.045, 0.065, rand()));
    if (rand() < 0.45) { const p = cellMid(k, lerp(0.35, 0.6, rand())); dot(p[0], p[1], 0.03, 0.8); }
  }
  sx.restore();
  drawFringe(sx, 'rgba(255,255,255,0.4)', 1.1);

  const dx = mk('#000'); dx.save(); path(dx); dx.clip();
  layer(dx, 0.04, (t) => {
    t.strokeStyle = 'rgba(255,255,255,0.42)';
    for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.64, 0.95, (s) => cellWidth(k, s) * 0.95, 12);
    (def.patches || []).forEach(([a, b, r]) => radial(t, a, b, r, [[0, 'rgba(255,255,255,0.9)'], [1, 'rgba(255,255,255,0)']]));
  });
  layer(dx, 0.015, (t) => bandAt(t, '#fff', 1));
  dx.globalCompositeOperation = 'destination-out';
  dx.restore();

  const yx = mk('#000'); yx.save(); path(yx); yx.clip();
  eyelets.forEach(([a, b, r]) => radial(yx, a, b, r * 1.3, [[0, 'rgba(255,255,255,0.35)'], [0.5, 'rgba(255,255,255,0.15)'], [1, 'rgba(255,255,255,0)']]));
  layer(yx, 0.012, (t) => { t.strokeStyle = 'rgba(255,255,255,0.45)'; for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.22, 0.68, (s) => cellWidth(k, s) * 0.08); });
  yx.restore();

  /* ---------------- corrugation height -> normal map: veins ride on ridges, cells sag between them */
  const hx = mk('rgb(128,128,128)'); hx.save(); path(hx); hx.clip();
  layer(hx, 0.03, (t) => { t.strokeStyle = 'rgba(30,30,30,0.6)'; for (let k = 0; k < nCells; k++) along(t, (s) => cellMid(k, s), 0.1, 1, (s) => cellWidth(k, s) * 0.5, 14); });
  layer(hx, 0.008, (t) => { t.strokeStyle = 'rgba(255,255,255,0.9)'; drawVeins(t, 1.6); });
  hx.restore();

  const cd = cx.getImageData(0, 0, W, H).data, ad = ax.getImageData(0, 0, W, H).data;
  const vd = vx.getImageData(0, 0, W, H).data, sd = sx.getImageData(0, 0, W, H).data;
  const dd = dx.getImageData(0, 0, W, H).data, yd = yx.getImageData(0, 0, W, H).data, hd = hx.getImageData(0, 0, W, H).data;
  const colData = new Uint8Array(W * H * 4), maskData = new Uint8Array(W * H * 4), nrmData = new Uint8Array(W * H * 4);
  const hAt = (x, y) => hd[(Math.min(H - 1, Math.max(0, y)) * W + Math.min(W - 1, Math.max(0, x))) * 4] / 255;
  const relief = 0.012 * ppc; // height units per pixel slope
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x, i4 = i * 4;
    colData[i4] = cd[i4]; colData[i4 + 1] = cd[i4 + 1]; colData[i4 + 2] = cd[i4 + 2]; colData[i4 + 3] = ad[i4];
    maskData[i4] = vd[i4]; maskData[i4 + 1] = sd[i4]; maskData[i4 + 2] = dd[i4]; maskData[i4 + 3] = yd[i4];
    const gx = (hAt(x + 1, y) - hAt(x - 1, y)) * relief, gy = (hAt(x, y + 1) - hAt(x, y - 1)) * relief;
    const l = Math.hypot(gx, gy, 1);
    nrmData[i4] = (-gx / l * 0.5 + 0.5) * 255; nrmData[i4 + 1] = (-gy / l * 0.5 + 0.5) * 255; nrmData[i4 + 2] = (1 / l * 0.5 + 0.5) * 255; nrmData[i4 + 3] = 255;
  }
  const mkTex = (data, srgb) => {
    const t = new THREE.DataTexture(data, W, H, THREE.RGBAFormat);
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
    t.anisotropy = 8; t.needsUpdate = true; return t;
  };

  // mesh: grid over the bounding box, keeping only cells that touch the (fringed) outline
  const inside = (a, b) => { let c = false; for (let i = 0, j = outline.length - 1; i < outline.length; j = i++) { const [ai, bi] = outline[i], [aj, bj] = outline[j]; if (((bi > b) !== (bj > b)) && (a < (aj - ai) * (b - bi) / (bj - bi) + ai)) c = !c; } return c; };
  const SA = 72, SB = Math.round(72 * wB / wA);
  const verts = [], uvs = [], idx = [], inV = [];
  for (let j = 0; j <= SB; j++) for (let i = 0; i <= SA; i++) {
    const a = lerp(minA, maxA, i / SA), b = lerp(minB, maxB, j / SB);
    verts.push(0, b, a); uvs.push(i / SA, (maxB - b) / wB); inV.push(inside(a, b));
  }
  for (let j = 0; j < SB; j++) for (let i = 0; i < SA; i++) {
    const a = j * (SA + 1) + i, b = a + 1, c = a + SA + 1, d = c + 1;
    if (inV[a] || inV[b] || inV[c] || inV[d]) idx.push(a, c, b, b, c, d);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setIndex(idx); geo.computeVertexNormals();
  const tg = new Float32Array((verts.length / 3) * 4); for (let i = 0; i < tg.length; i += 4) { tg[i + 2] = 1; tg[i + 3] = 1; }
  geo.setAttribute('tangent', new THREE.BufferAttribute(tg, 4));
  return {
    geo, colTex: mkTex(colData, true), maskTex: mkTex(maskData, false), nrmTex: mkTex(nrmData, false),
    size: new THREE.Vector2(wA, wB), rootUV: new THREE.Vector2((0 - minA) / wA, (maxB - 0) / wB), length: def.length,
    colData, maskData, W, H, ppc, minA, maxB,
    outline: outline.filter((_, i) => i % 12 === 0), outlineFull: outline,
  };
}

const FORE = makeWing({
  seed: 11, length: 5.3,
  ctrl: [[0.1, 0.0], [0.38, 0.8], [0.42, 2.0], [0.22, 3.3], [-0.25, 4.4], [-0.85, 5.12], [-1.35, 5.3],
         [-1.78, 5.02], [-2.2, 4.2], [-2.6, 3.3], [-2.95, 2.45], [-3.15, 1.86], [-2.96, 1.52], [-2.2, 1.05], [-1.3, 0.55], [-0.5, 0.12]],
  scallop: { minR: 3.0, count: 9, depth: 0.035 },
  cell: [[0.16, 1.3], [-0.18, 2.65], [-0.62, 2.55], [-1.05, 2.3], [-0.98, 1.2]],
  rootVeins: [[[0, 0], [0.16, 1.3]], [[0, 0], [-0.98, 1.2]], [[0, 0], [-0.5, 0.3], [-1.6, 0.85], [-2.75, 1.55]], [[0, 0], [0.28, 1.6], [0.22, 3.0]]],
  veinMinR: 2.85, veins: 11, band: 0.34, bandMinR: 3.25, fringeMinR: 3.0,
  minB: 0, // no part of the forewing lies below its hinge axis
  patches: [[-0.5, 3.75, 0.34], [-1.0, 3.4, 0.28], [-1.95, 2.45, 0.3]],
});
const HIND = makeWing({
  seed: 23, length: 4.4,
  // the inner (anal) margin runs straight back from the root along the hinge axis, above the abdomen,
  // so flapping (a rotation about that axis) can never swing any of it down into the body
  ctrl: [[0.0, 0.0], [-0.25, 0.7], [-0.8, 1.55], [-1.7, 2.25], [-2.7, 2.5], [-3.55, 2.2], [-4.15, 1.5], [-4.4, 0.7],
         [-4.2, 0.12], [-3.6, 0.05], [-2.6, 0.03], [-1.6, 0.02], [-0.7, 0.01]],
  minB: 0, // no part of the hindwing lies below its hinge axis
  scallop: { minR: 2.6, minB: 0.25, count: 7, depth: 0.14 },
  cell: [[-0.45, 0.8], [-1.45, 1.15], [-1.75, 0.45], [-0.95, 0.12]],
  rootVeins: [[[0, 0], [-0.45, 0.8]], [[0, 0], [-0.95, 0.12]], [[0, 0], [-1.6, 0.06], [-3.0, 0.0]]],
  veinMinR: 2.4, veins: 9, band: 0.32, bandMinR: 2.6, bandMinB: 0.2, fringeMinR: 2.2,
});

const flexU = uniform(0);
// Wing articulation: fore- and hindwing of a side hinge on one common line along the upper edge of
// the thorax (x = +-HINGE_X, y = HINGE_Y), so the flap is a rotation of both about the same axis.
const HINGE_X = 0.16, HINGE_Y = 0.64;
const FORE_LEAD = 4 * D2R;  // forewings sit a few degrees more open, overlapping their hindwings on the outside
const OPEN_MIN = 6 * D2R - 0.02, OPEN_MAX = 46 * D2R + 0.02; // stroke range including tremor
// Resting wing beat. A basking butterfly is not periodic: it holds its wings shut for a few seconds,
// opens them fairly slowly to a varying width, holds (settling slightly), and closes faster than it
// opened; now and then it gives a quick partial flick instead. The timeline is drawn once from a seed
// and loops, so every consumer (renderer, stance solver, audit, ?t=) sees the same motion.
// a(t) in [0, 1] is the opening (0 = 6 deg, 1 = 46 deg from vertical).
const FLAP = (() => {
  const r = rng(P.seed + 77), keys = []; // keys: [time, opening, easing of the segment that ends here]
  let t = 0;
  keys.push([0, 0, 'hold']);
  const push = (dt, a, ease) => { t += dt; keys.push([t, a, ease]); };
  while (t < 48) {
    push(lerp(1.6, 4.2, r()), 0, 'hold');                                   // rest, wings shut
    if (r() < 0.25) {                                                       // quick partial flick
      const a = lerp(0.25, 0.45, r());
      push(lerp(0.28, 0.4, r()), a, 'smooth');
      push(lerp(0.25, 0.35, r()), 0, 'smooth');
      if (r() < 0.4) { push(lerp(0.15, 0.3, r()), 0, 'hold'); push(lerp(0.26, 0.36, r()), a * 0.8, 'smooth'); push(lerp(0.24, 0.32, r()), 0, 'smooth'); }
    } else {                                                                // full basking opening
      const a = lerp(0.65, 1.0, r());
      push(lerp(1.0, 1.6, r()), a, 'open');
      const hold = lerp(0.8, 2.6, r());
      push(hold * 0.5, a * lerp(0.94, 1.0, r()), 'settle');                 // small settling while open
      push(hold * 0.5, a, 'settle');
      push(lerp(0.45, 0.7, r()), 0, 'close');
    }
  }
  const ease = {
    hold: () => 0,
    smooth: (x) => x * x * (3 - 2 * x),
    settle: (x) => x * x * (3 - 2 * x),
    open: (x) => 1 - Math.pow(1 - x, 2.2) * (1 - 0.35 * x),                  // brisk start, long settle
    close: (x) => x * x * x * (x * (6 * x - 15) + 10),                      // smootherstep, quicker overall
  };
  const opening = (time) => {
    const tt = ((time % t) + t) % t;
    let i = 1; while (i < keys.length - 1 && keys[i][0] < tt) i++;
    const [t0, a0] = keys[i - 1], [t1, a1, e] = keys[i];
    const x = Math.min(1, Math.max(0, (tt - t0) / (t1 - t0)));
    return e === 'hold' ? a0 : lerp(a0, a1, ease[e](x));
  };
  return { duration: t, opening };
})();
// Pose at time t, shared by the renderer, the stance solver and the audit. The trailing-edge flex
// follows the actual angular velocity of the wing (normalised to the fastest close in the timeline).
function wingPose(t) {
  const a = FLAP.opening(t);
  const vel = (FLAP.opening(t + 0.02) - FLAP.opening(t - 0.02)) / 0.04;   // opening per second
  const tremor = Math.sin(t * 7.3) * 0.006 + Math.sin(t * 11.1 + 1.3) * 0.004;
  return { open: (6 + 40 * a) * D2R + tremor, flex: THREE.MathUtils.clamp(-vel / 2.6, -1, 1) * 0.32 };
}
// CPU mirror of the wing vertex stage below: outward offset of wing point (a, b) from its hinge plane.
// The wing is pinned at its articulation, so camber fades to zero at the hinge axis.
function wingOutward(wing, a, b, flex) {
  const cs = Math.cos(wing.sweep), sn = Math.sin(wing.sweep);
  const yAxis = b * cs - a * sn, zBody = b * sn + a * cs + wing.rootZ; // yAxis: distance from the hinge axis
  const h = Math.max(yAxis + wing.rootY - 0.62, 0) / 5;
  return Math.sin(zBody * 0.75) * 0.03 * sstep(0, 0.8, yAxis) + h * h * flex * 0.5;
}
// The wing is solid exactly where it renders: coverage that survives the material's alpha test
// (opacity = coverage * >=0.94). Shared by the material, the fur sweep test and the audit.
const WING_ALPHA_TEST = 0.03, WING_SOLID = WING_ALPHA_TEST / 0.94;
function wingCoverage(W, a, b) {
  const x = Math.round((a - W.minA) * W.ppc - 0.5), y = Math.round((W.maxB - b) * W.ppc - 0.5);
  if (x < 0 || y < 0 || x >= W.W || y >= W.H) return 0;
  return W.colData[(y * W.W + x) * 4 + 3] / 255;
}
const pointInPoly = (poly, a, b) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [ai, bi] = poly[i], [aj, bj] = poly[j]; if (((bi > b) !== (bj > b)) && (a < (aj - ai) * (b - bi) / (bj - bi) + ai)) c = !c; } return c; };
// Scale lattice: ~0.24 x 0.16 mm shingles. The cell means of the shingle mask and of the luminous gain
// are integrated numerically from the same expressions, for the far-field fade and the wing lights.
const WING_SCALE = (() => {
  const S = { len: 0.024, wid: 0.016 };
  let mask = 0, gain = 0; const n = 64;
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const fu = (i + 0.5) / n * 2 - 1, fv = (j + 0.5) / n;
    const m = sstep(1.0, 0.86, Math.hypot(fu, (fv - 0.42) * 1.55)); // smoothstep(1, 0.86, x)
    mask += m; gain += m * (fv * 0.15 + 0.85);
  }
  S.meanMask = mask / (n * n);
  S.meanGain = 1.025 * gain / mask; // E[mix(0.75, 1.3, h)] = 1.025
  return S;
})();
// Sub-pixel glints (stochastic microfacet model). Where a pixel covers many scales, each scale is a
// small mirror whose tilt follows the scales' slope distribution D. For a light of solid angle W_L the
// chance that one scale reflects it into the eye is p = D(h) (n.h) W_L / (4 v.h). A pixel's footprint
// on the wing holds n = rho * A scales, so the number actually glinting is Poisson(n p). The specular
// term is scaled by (glinting / expected): the same mean as the smooth highlight, delivered as discrete
// glints. Draws are keyed to surface cells (a footprint-sized LOD of the wing) and to the reflection
// direction binned at the emitter's angular size, so a glint stays on the wing as the camera moves and
// changes only when the reflection geometry does. Where scales span pixels, they are shaded one by one
// instead (detail -> 1) and the factor is 1.
const poisson = (lambda, u1, u2) => {
  // inverse CDF for small means, normal approximation for large ones
  const k = float(0.0).toVar(), pk = exp(lambda.negate()).toVar(), cdf = pk.toVar();
  Loop(8, ({ i }) => {
    If(u1.greaterThan(cdf), () => { k.assign(float(i).add(1.0)); pk.mulAssign(lambda.div(float(i).add(1.0))); cdf.addAssign(pk); });
  });
  const gauss = lambda.add(sqrt(lambda).mul(sqrt(log2(max(u2, 1e-6)).mul(-2.0 * Math.LN2))).mul(cos(u1.mul(6.2831853))));
  return select(lambda.lessThan(4.0), k, max(floor(gauss.add(0.5)), 0.0));
};
class GlintLightingModel extends THREE.PhysicalLightingModel {
  constructor(glint, ...flags) { super(...flags); this.glint = glint; }
  direct(params, builder) {
    const before = params.reflectedLight.directSpecular.toVar();
    super.direct(params, builder);
    const added = params.reflectedLight.directSpecular.sub(before);
    params.reflectedLight.directSpecular.assign(before.add(added.mul(this.glintFactor(params, builder))));
  }
  // Environment: the cave is full of point-like glowworms, so each scale reflects either one of them or
  // dark rock. A few scale normals per footprint cell are drawn from the same tilt distribution and
  // the sharp cave probe is read in each one's mirror direction; their deviation from the smooth
  // (prefiltered) reflection is scaled by sqrt(samples / scales in the pixel), the spread of a true
  // average over that many scales.
  indirect(builder) {
    const env = scene.environment;
    if (env) {
      const { cm, detail, alpha, density, cell0 } = this.glint;
      const area = length(cross(dFdx(positionWorld), dFdy(positionWorld))).max(1e-9);
      const nScales = float(density).mul(area);
      const lod = floor(max(log2(sqrt(area).div(cell0)), 0.0));
      const id = floor(cm.div(float(cell0).mul(pow(2.0, lod)))).add(vec2(lod.mul(1013.0), lod.mul(-577.0)));
      const N = normalView, V = positionViewDirection, K = 4;
      const sum = vec3(0.0).toVar();
      for (let k = 0; k < K; k++) {
        const u1 = hash21(id.add(k * 7.13 + 0.5)), u2 = hash21(id.add(k * 3.71 + 11.3));
        const th = atanTSL(sqrt(alpha).mul(sqrt(u1.div(u1.oneMinus().max(1e-4))))); // GGX slope sample
        const ph = u2.mul(6.2831853);
        const m = normalize(tangentView.mul(sin(th).mul(cos(ph))).add(bitangentView.mul(sin(th).mul(sin(ph)))).add(N.mul(cos(th))));
        const rWorld = cameraWorldMatrix.mul(vec4(reflect(V.negate(), m), 0.0)).xyz;
        sum.addAssign(pmremTexture(env, rWorld, float(0.2)).rgb);
      }
      const pre = builder.context.radiance;
      const spread = sqrt(min(float(1.0), float(K).div(nScales.max(1.0))));
      builder.context.radiance.assign(mix(pre.add(sum.div(K).sub(pre).mul(spread)), pre, detail));
    }
    super.indirect(builder);
  }
  glintFactor({ lightDirection, lightNode }, builder) {
    const { cm, detail, alpha, density, cell0 } = this.glint;
    const light = lightNode.light;
    const R = light.userData.sourceRadius ?? light.radius ?? 0.05; // physical size of the emitter
    const lv = lightNode.getLightVector(builder);
    const d2 = dot(lv, lv);
    const omegaL = float(Math.PI * R * R).div(d2.add(R * R));          // solid angle of the emitter
    const N = normalView, V = positionViewDirection;
    const h = normalize(lightDirection.add(V));
    const nh = clamp(dot(N, h), 1e-4, 1.0), vh = clamp(dot(V, h), 1e-3, 1.0);
    const p = clamp(D_GGX({ alpha, dotNH: nh }).mul(nh).mul(omegaL).div(vh.mul(4.0)), 0.0, 1.0);
    // pixel footprint on the wing (cm^2) and the surface-cell LOD that matches it
    const area = length(cross(dFdx(positionWorld), dFdy(positionWorld))).max(1e-9);
    const lod = max(log2(sqrt(area).div(cell0)), 0.0);
    const l0 = floor(lod), lf = fract(lod);
    // reflection direction in slope space, binned at the emitter's angular size
    const slope = vec2(dot(h, tangentView), dot(h, bitangentView)).div(nh);
    const bin = floor(slope.div(sqrt(omegaL.div(Math.PI)).mul(2.0).max(1e-3)));
    const g = (level) => {
      const side = float(cell0).mul(pow(2.0, level));
      const id = floor(cm.div(side)).add(vec2(level.mul(1013.0), level.mul(-577.0)));
      const lambda = float(density).mul(side.mul(side)).mul(p);
      const key = id.add(bin.mul(vec2(37.17, 91.31)));
      const k = poisson(lambda, hash21(key), hash21(key.add(19.19)));
      return k.div(lambda.max(1e-6));
    };
    return mix(mix(g(l0), g(l0.add(1.0)), lf), float(1.0), detail);
  }
}
function makeWingMaterial(W, wing) {
  const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide, transparent: true, depthWrite: true, alphaTest: WING_ALPHA_TEST });
  const c = texture(W.colTex, uv());
  const k = texture(W.maskTex, uv());
  const veins = k.r, spots = k.g, dark = k.b, cyanScale = k.a;
  const cm = uv().sub(W.rootUV).mul(vec2(W.size.x, -W.size.y));
  const dcm = length(cm);
  const glow = exp(dcm.mul(-1.35));
  const memN = texture(W.nrmTex, uv()).rgb.mul(2.0).sub(1.0);
  const warm = color('#fff0cc');

  // ---- scales. The wing surface is a lattice of overlapping shingles in rows around the root, tips
  // pointing outward. Each scale is a structural-colour reflector: a chitin nano-layer whose thin-film
  // interference (iridescence, IOR 1.56) sets its hue by thickness and viewing angle, over a dark
  // melanin base. Scales differ slightly in tilt and film thickness, so as the wing moves each one
  // catches the lights at a different moment: that is the glitter. The luminous layer beneath shows
  // through each scale with its own strength. Detail fades to its mean where a scale is under ~2 px.
  const rowF = dcm.div(WING_SCALE.len);
  const row = floor(rowF);
  const acrossF = atan(cm.y, cm.x).mul(dcm).div(WING_SCALE.wid).add(row.mul(0.5)); // brick offset
  const cell = vec2(floor(acrossF), row).add(wing.fore ? 0.0 : 517.0);
  const fu = fract(acrossF).mul(2.0).sub(1.0), fv = fract(rowF);
  const h1 = hash21(cell), h2 = hash21(cell.add(7.31)), h3 = hash21(cell.add(3.17)), h4 = hash21(cell.add(11.9)), h5 = hash21(cell.add(5.53));
  // visible part of a scale: its rounded tip; the row beyond covers its base; thin dark sockets between
  const shingle = smoothstep(1.0, 0.86, length(vec2(fu, fv.sub(0.42).mul(1.55))));
  const detail = smoothstep(0.9, 0.35, max(fwidth(rowF), fwidth(acrossF)));
  const sMask = mix(float(WING_SCALE.meanMask), shingle, detail);
  const tilt = vec3(h1.sub(0.5).mul(0.55), h2.sub(0.5).mul(0.55).add(fv.sub(0.5).mul(0.35)), 1.0); // scattered + curved
  const scaleN = normalize(mix(vec3(0, 0, 1), tilt, detail));
  // far field: film thickness varies between footprint cells as it does between scales
  const farCell = floor(cm.div(WING_SCALE.len * 4.0));
  const thickness = mix(mix(300.0, 460.0, hash21(farCell.add(3.17))), mix(300.0, 460.0, h3), detail); // nm
  const gain = mix(float(WING_SCALE.meanGain), mix(0.75, 1.3, h4).mul(fv.mul(0.15).add(0.85)), detail);

  // pigment: the canvas pattern, broken up by domain-warped patches (cyan / deep blue / pale) and a
  // per-scale hue jitter, so no two neighbouring areas are identical
  const warp = vec2(mx_noise_float(vec3(cm.mul(1.6), 9.0)), mx_noise_float(vec3(cm.mul(1.6), 13.0))).mul(0.5);
  const patch = mx_fractal_noise_float(vec3(cm.mul(3.2).add(warp), wing.fore ? 5.0 : 21.0), 3, 2.0, 0.5, 1.0);
  const pale = mx_noise_float(vec3(cm.mul(7.0).add(warp.mul(2.0)), 2.0));
  let pigment = mix(c.rgb, c.rgb.mul(vec3(0.7, 1.08, 1.2)), smoothstep(-0.15, 0.55, patch).mul(0.65));
  pigment = mix(pigment, pigment.mul(vec3(1.2, 1.15, 0.95)).add(0.04), smoothstep(0.35, 0.8, pale).mul(0.45));
  pigment = pigment.mul(mix(vec3(1, 1, 1), vec3(0.88, 1.02, 1.12), h5.mul(detail).mul(0.6)));

  const membrane = mix(pigment, warm, glow.mul(0.55)).mul(gain).mul(sMask).mul(dark.mul(0.8).oneMinus()).mul(glow.mul(0.75).add(0.4)).mul(P.wing.membrane);
  const veinE = color('#ffc47a').mul(veins).mul(glow.mul(2.0).add(0.8)).mul(P.wing.vein);
  const spotE = color('#ffdca0').mul(spots).mul(P.wing.spot);
  const cyanE = color('#5fd8ff').mul(cyanScale).mul(1.3).mul(gain);
  m.colorNode = pigment.mul(0.12); // melanin-dark base beneath the reflective layer
  m.normalNode = normalMap(normalize(mix(memN, scaleN, sMask.mul(veins.oneMinus()))).mul(0.5).add(0.5));
  // a single scale is fairly smooth (0.2); unresolved, the spread of scale tilts widens the lobe (0.48)
  const scaleRough = mix(float(0.48), float(0.2), detail);
  m.roughnessNode = mix(float(0.55), scaleRough, sMask.mul(veins.oneMinus()));
  const glint = { cm, detail: detail.max(veins), alpha: scaleRough.mul(scaleRough), density: 1 / (WING_SCALE.len * WING_SCALE.wid), cell0: WING_SCALE.len };
  m.setupLightingModel = () => new GlintLightingModel(glint, false, false, true, false, false, false);
  m.metalnessNode = float(0.0);
  m.iorNode = float(1.56);
  m.specularIntensityNode = float(1.0);
  m.iridescenceNode = sMask.mul(veins.oneMinus());
  m.iridescenceIORNode = float(1.56);
  m.iridescenceThicknessNode = thickness;
  m.emissiveNode = membrane.add(veinE).add(spotE).add(cyanE).mul(P.wing.gain);
  m.opacityNode = c.a.mul(mix(0.94, 1.0, max(veins, dark)));

  // Out-of-plane shape as an outward offset (away from the dorsal midline), so both sides match.
  // Camber and the velocity-driven flex are evaluated in the shared body frame, so where a forewing
  // overlaps its hindwing both bend identically; the forewing stays outside through FORE_LEAD alone.
  // Mirrored on the CPU by wingOutward().
  const b = positionLocal.y, a = positionLocal.z;
  const cs = Math.cos(wing.sweep), sn = Math.sin(wing.sweep);
  const yAxis = b.mul(cs).sub(a.mul(sn));
  const zBody = b.mul(sn).add(a.mul(cs)).add(wing.rootZ);
  const h = max(yAxis.add(wing.rootY - 0.62), 0.0).div(5.0);
  const outward = sin(zBody.mul(0.75)).mul(0.03).mul(smoothstep(0.0, 0.8, yAxis)).add(h.mul(h).mul(flexU).mul(0.5));
  m.positionNode = vec3(outward.mul(wing.side), b, a);
  return m;
}

const WING_LAYOUT = [-1, 1].flatMap((side) => [
  { W: FORE, side, root: [side * HINGE_X, HINGE_Y, 0.22], sweep: 0.15, fore: true, rootY: HINGE_Y, rootZ: 0.22 },
  { W: HIND, side, root: [side * HINGE_X, HINGE_Y, -0.12], sweep: 0.0, fore: false, rootY: HINGE_Y, rootZ: -0.12 },
]);
// Swept volume of the wings. A wing is a surface through its hinge axis; flapping rotates it about that
// axis over [OPEN_MIN, OPEN_MAX]. A point is in the path of a wing exactly when its angle around the
// hinge axis lies inside that range and, at that angle, it falls inside the wing outline.
function inWingSweep(p, tol = 0.012) {
  for (const l of WING_LAYOUT) {
    const vx = p.x - l.root[0], vy = p.y - l.root[1], vz = p.z - l.root[2];
    const rho = Math.hypot(vx, vy); if (rho < 1e-4) continue;
    const phi = Math.atan2(l.side * vx, vy); // angle from vertical toward this wing's own side
    const lead = l.fore ? FORE_LEAD : 0, cs = Math.cos(-l.sweep), sn = Math.sin(-l.sweep);
    // the surface point at radius rho sits o outward of the hinge plane, i.e. at distance yo along it
    let o = 0, yo = rho;
    for (let it = 0; it < 3; it++) { yo = Math.sqrt(Math.max(rho * rho - o * o, 0)); o = wingOutward(l, yo * sn + vz * cs, yo * cs - vz * sn, 0); }
    const theta = phi - Math.atan2(o, yo);
    const slack = Math.atan2(tol + 0.03, rho); // surface thickness + flex envelope
    if (theta < OPEN_MIN + lead - slack || theta > OPEN_MAX + lead + slack) continue;
    if (wingCoverage(l.W, yo * sn + vz * cs, yo * cs - vz * sn) > WING_SOLID) return true;
  }
  return false;
}

/* ============================================================ butterfly */
const bfly = new THREE.Group();
scene.add(bfly);
const coreMat = new THREE.MeshPhysicalNodeMaterial();
{
  const n = mx_fractal_noise_float(positionLocal.mul(30.0), 2, 2.0, 0.5, 1.0);
  coreMat.colorNode = mix(color('#2a2622'), color('#8d8272'), n.mul(0.5).add(0.5));
  coreMat.roughnessNode = float(0.7);
  coreMat.sheenNode = color('#fff0d0');
  coreMat.sheenRoughnessNode = float(0.3);
}
function furMat(root, tip) {
  const m = new THREE.MeshStandardNodeMaterial({ side: THREE.DoubleSide });
  m.colorNode = mix(color(root), color(tip), pow(uv().y, 0.45));
  m.roughnessNode = float(0.62);
  return m;
}
const furThorax = furMat('#7a7064', '#fff8ec');
const furHead = furMat('#776d60', '#fffaf0');
const furAbd = furMat('#71675c', '#f2e7d2');
const eyeMat = new THREE.MeshPhysicalNodeMaterial();
{
  eyeMat.colorNode = color('#030409');
  eyeMat.roughnessNode = float(0.16);
  eyeMat.clearcoatNode = float(1.0);
  eyeMat.clearcoatRoughnessNode = float(0.03);
  eyeMat.sheenNode = color('#2a3d8a').mul(0.5);
}
const antMat = new THREE.MeshStandardNodeMaterial();
antMat.colorNode = mix(color('#1b1814'), color('#8f7d5e'), smoothstep(0.35, 0.65, fract(uv().x.mul(150.0))).mul(0.6));
antMat.roughnessNode = float(0.45);
const clubMat = new THREE.MeshStandardNodeMaterial();
clubMat.colorNode = color('#ffd9a0');
clubMat.emissiveNode = color('#ffc777').mul(14.0 * P.wing.gain); // bioluminescent antennal clubs, same luminescence as the wings
const legMat = new THREE.MeshPhysicalNodeMaterial();
legMat.colorNode = color('#2d2620');
legMat.roughnessNode = float(0.38);
legMat.clearcoatNode = float(0.5);
legMat.clearcoatRoughnessNode = float(0.25);
legMat.sheenNode = color('#d8c7a0').mul(0.6);


const wingRig = [];
// Body plan (cm, butterfly local frame): head, collar (patagia), meso- and metathorax, ringed abdomen.
// Fur is short and combed along the surface so the segmented form underneath stays readable.
const BODY = {
  head: V3(0, 0.44, 0.7), headR: V3(0.18, 0.18, 0.17),
  meso: V3(0, 0.42, 0.17), mesoR: V3(0.3, 0.32, 0.36),
  meta: V3(0, 0.39, -0.2), metaR: V3(0.26, 0.27, 0.25),
};
const abdMat = new THREE.MeshPhysicalNodeMaterial();
{
  // tergite rings: darker plates with pale intersegmental membranes
  const seg = fract(positionLocal.y.mul(7.0 / 1.85));
  abdMat.colorNode = mix(color('#3a332c'), color('#cdbfa6'), smoothstep(0.78, 0.97, seg).mul(0.8));
  abdMat.roughnessNode = float(0.6);
  abdMat.sheenNode = color('#fff0d0');
  abdMat.sheenRoughnessNode = float(0.35);
}
function buildButterfly() {
  const rand = rng(91);
  const solids = bfly.userData.solids = []; // analytic body solids, reused by the audit
  const ell = (c, r, mat = coreMat) => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), mat); m.scale.copy(r); m.position.copy(c); m.castShadow = true; bfly.add(m); solids.push({ c: c.clone(), r: r.clone() }); return m; };
  ell(BODY.head, BODY.headR);
  ell(BODY.meso, BODY.mesoR);
  ell(BODY.meta, BODY.metaR);
  ell(V3(0, 0.44, 0.47), V3(0.17, 0.17, 0.12)); // neck / prothorax
  const eyeDirs = [];
  for (const sx of [-1, 1]) {
    // compound eyes bulge from the sides of the head rather than sitting on it
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.128, 36, 24), eyeMat);
    eye.position.set(sx * 0.1, 0.47, 0.76); bfly.add(eye);
    solids.push({ c: eye.position.clone(), r: V3(0.128, 0.128, 0.128) });
    eyeDirs.push(eye.position.clone().sub(BODY.head).normalize());
  }
  // abdomen: seven tergites tapering to the tip
  const prof = [];
  for (let i = 0; i <= 70; i++) {
    const s = i / 70;
    const segPhase = (s * 7) % 1;
    const r = 0.21 * Math.pow(Math.sin(Math.PI * (s * 0.9 + 0.05)), 0.55) * (1 - 0.32 * s) * (0.9 + 0.1 * Math.sin(Math.PI * segPhase));
    prof.push(new THREE.Vector2(Math.max(r, 0.004), s * 1.85));
  }
  const abd = new THREE.Mesh(new THREE.LatheGeometry(prof, 32), abdMat);
  abd.rotation.x = -Math.PI / 2 - 0.12; abd.position.set(0, 0.27, -0.36);
  abd.castShadow = true; bfly.add(abd); abd.updateMatrix();
  bfly.userData.abdomen = { mesh: abd, length: 1.85, radius: (s) => 0.21 * Math.pow(Math.sin(Math.PI * (s * 0.9 + 0.05)), 0.55) * (1 - 0.32 * s) };

  // hairs: unit-length tapered strands scaled uniformly, so longer hairs are also thicker; each is
  // twisted randomly about its axis and bent in the vertex stage (see furMat) so the pelt reads soft
  // the bend is part of each strand's own geometry, so the per-hair twist below gives every hair its
  // own bend direction (bending in a shader after instancing would comb the whole pelt one way)
  const hair = new THREE.ConeGeometry(0.034, 1, 3, 4, true); hair.translate(0, 0.5, 0);
  { const hp = hair.attributes.position; for (let i = 0; i < hp.count; i++) { const y = hp.getY(i); hp.setX(i, hp.getX(i) + y * y * 0.3); } hair.computeVertexNormals(); }
  const furGroups = new Map();
  // The bent strand (as instanced) may not enter the wings' swept volume or the body: it is pressed
  // short where it would, as wing bases press the real pelt flat (the strand keeps its proportions).
  // fur lies over the body and never grows into it
  const abdInv = abd.matrix.clone().invert(), tv = V3();
  const insideBody = (v) => solids.some((sd) => ((v.x - sd.c.x) / sd.r.x) ** 2 + ((v.y - sd.c.y) / sd.r.y) ** 2 + ((v.z - sd.c.z) / sd.r.z) ** 2 < 1)
    || (tv.copy(v).applyMatrix4(abdInv), tv.y > 0 && tv.y < 1.85 && Math.hypot(tv.x, tv.z) < bfly.userData.abdomen.radius(tv.y / 1.85));
  const strand = (p, q, len, r) => { const pts = []; for (let k = 0; k <= 12; k++) { const y = k / 12; pts.push(V3(y * y * 0.3 * len * r, y * len, 0).applyQuaternion(q).add(p)); } return pts; };
  const put = (mat, p, dir, len, r = 1) => {
    const q = new THREE.Quaternion().setFromUnitVectors(V3(0, 1, 0), dir.normalize()).multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), rand() * 6.283));
    const blocked = (L) => strand(p, q, L, r).findIndex((v, i) => inWingSweep(v) || (i > 0 && insideBody(v)));
    for (let k = blocked(len), it = 0; k >= 0; k = blocked(len), it++) {
      len *= Math.max(0, k - 1) / 12;
      if (len < 0.012 || it > 8) return; // no room for this hair
    }
    if (!furGroups.has(mat)) furGroups.set(mat, []);
    furGroups.get(mat).push(new THREE.Matrix4().compose(p, q, V3(len * r, len, len * r)));
  };
  const jitter = (k) => V3(rand() - 0.5, rand() - 0.5, rand() - 0.5).multiplyScalar(k);
  // combed fur: lies along the surface in the comb direction, lifted from it by `lift`
  const ellipsoidFur = (mat, n, c, rad, lenA, lenB, comb, lift, fluff, skip) => {
    for (let i = 0; i < n; i++) {
      const d = V3(rand() * 2 - 1, rand() * 2 - 1, rand() * 2 - 1);
      if (d.lengthSq() > 1 || d.lengthSq() < 0.01) { i--; continue; }
      d.normalize();
      if (skip && skip(d)) continue;
      const p = c.clone().add(V3(d.x * rad.x, d.y * rad.y, d.z * rad.z));
      const nrm = V3(d.x / rad.x, d.y / rad.y, d.z / rad.z).normalize();
      const tang = comb.clone().addScaledVector(nrm, -comb.dot(nrm));
      put(mat, p, nrm.clone().multiplyScalar(lift).add(tang).add(jitter(fluff)), lerp(lenA, lenB, Math.pow(rand(), 0.8)));
    }
  };
  const back = V3(0, 0.1, -1);
  // head: short pile, a pale frontal tuft between the eyes, eyes left clear
  ellipsoidFur(furHead, 1500, BODY.head, BODY.headR, 0.025, 0.07, V3(0, 0.6, -0.3), 0.6, 0.4, (d) => eyeDirs.some((e) => d.dot(e) > 0.55));
  for (let i = 0; i < 300; i++) { // frons tuft between the eyes, below the antennae
    const p = BODY.head.clone().add(V3((rand() - 0.5) * 0.08, -0.02 + rand() * 0.1, 0.15 + rand() * 0.03));
    put(furHead, p, V3((rand() - 0.5) * 0.3, 0.35 + rand() * 0.3, 1).add(jitter(0.35)), lerp(0.05, 0.11, rand()));
  }
  // collar (patagia): long pale tufts sweeping back over the front of the thorax
  for (let i = 0; i < 1500; i++) {
    const a = lerp(-1.25, 1.25, rand()) * Math.PI * 0.62; // skip the throat
    const rr = lerp(0.14, 0.2, rand());
    const p = V3(Math.sin(a) * rr, 0.44 + Math.cos(a) * rr, 0.47 + (rand() - 0.5) * 0.08);
    const radial = V3(Math.sin(a), Math.cos(a), 0);
    put(furThorax, p, radial.multiplyScalar(0.7).add(V3(0, 0.15, -1)).add(jitter(0.5)), lerp(0.13, 0.24, rand()));
  }
  // thorax: dense dorsal pile combed back; the flanks thin out to show the dark sclerites
  const flank = (d) => d.y < -0.15 && rand() < 0.85;
  ellipsoidFur(furThorax, 6500, BODY.meso, BODY.mesoR, 0.07, 0.17, back, 0.55, 0.45, flank);
  ellipsoidFur(furThorax, 2600, BODY.meta, BODY.metaR, 0.06, 0.13, back, 0.5, 0.4, flank);
  // abdomen: short hair laid back along the rings
  for (let i = 0; i < 2600; i++) {
    const s = Math.pow(rand(), 1.3) * 0.94, a = rand() * Math.PI * 2;
    const r = 0.21 * Math.pow(Math.sin(Math.PI * (s * 0.9 + 0.05)), 0.55) * (1 - 0.32 * s);
    const pl = V3(Math.cos(a) * r, s * 1.85, Math.sin(a) * r).applyMatrix4(abd.matrix);
    const nl = V3(Math.cos(a), 0, Math.sin(a)).transformDirection(abd.matrix);
    const axis = V3(0, 1, 0).transformDirection(abd.matrix);
    put(furAbd, pl, nl.multiplyScalar(0.35).add(axis).add(jitter(0.3)), lerp(0.025, 0.07, rand()) * (1 - s * 0.4));
  }
  // labial palps: hairy brushes jutting forward beneath the eyes
  for (const sx of [-1, 1]) {
    const a0 = V3(sx * 0.035, 0.34, 0.8), a1 = V3(sx * 0.04, 0.47, 1.0);
    const axis = a1.clone().sub(a0).normalize();
    for (let i = 0; i < 220; i++) { // scaled palp: hairs laid forward along its axis
      const t = rand(), p = a0.clone().lerp(a1, t).add(V3((rand() - 0.5) * 0.03, (rand() - 0.5) * 0.03, 0));
      put(furHead, p, axis.clone().add(V3(sx * 0.12, 0.1, 0)).add(jitter(0.35)), lerp(0.04, 0.09, rand()) * (1 - t * 0.5), 0.8);
    }
  }
  for (const [mat, list] of furGroups) {
    const im = new THREE.InstancedMesh(hair, mat, list.length);
    im.userData.fur = true;
    list.forEach((mm, i) => im.setMatrixAt(i, mm));
    bfly.add(im);
  }

  // antennae: banded shafts with luminous clubs
  for (const sx of [-1, 1]) {
    const pts = [V3(sx * 0.05, 0.59, 0.8), V3(sx * 0.28, 1.28, 1.18), V3(sx * 0.68, 2.22, 1.76), V3(sx * 1.06, 3.05, 2.34)];
    const curve = new THREE.CatmullRomCurve3(pts);
    const ant = new THREE.Mesh(taperTube(pts, 0.013, 0.008, 80, 6), antMat);
    const tip = curve.getPoint(1), tng = curve.getTangent(1);
    const club = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), clubMat);
    club.scale.set(0.03, 0.13, 0.03);
    club.quaternion.setFromUnitVectors(V3(0, 1, 0), tng);
    club.position.copy(tip).addScaledVector(tng, 0.07);
    const pivot = new THREE.Group(); pivot.position.copy(pts[0]);
    ant.position.sub(pts[0]); club.position.sub(pts[0]);
    pivot.add(ant, club); pivot.userData.side = sx;
    bfly.add(pivot); wingRig.push({ antenna: pivot });
  }
  // coiled proboscis tucked under the head
  {
    const pts = []; for (let i = 0; i <= 60; i++) { const a = i / 60 * Math.PI * 4.2, r = 0.085 * (1 - i / 75); pts.push(V3(0, 0.3 - r * Math.cos(a) * 0.9, 0.82 + r * Math.sin(a) * 0.9)); }
    bfly.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, 0.01, 5), legMat));
  }

  // wings: openPivot (about the body axis) > sweepPivot (within the wing plane) > mesh
  const mkWing = (W, side, root, sweep, fore) => {
    const open = new THREE.Group(); open.position.set(...root);
    const sw = new THREE.Group(); sw.rotation.x = sweep;
    const rec = { side, fore, sweep, rootY: root[1], rootZ: root[2], W };
    const mesh = new THREE.Mesh(W.geo, makeWingMaterial(W, rec));
    mesh.castShadow = true;
    // draw order: far hind, far fore, near hind, near fore
    mesh.renderOrder = (side > 0 ? 0 : 2) + (fore ? 1 : 0);
    sw.add(mesh); open.add(sw); bfly.add(open);
    return Object.assign(rec, { open, sw, mesh });
  };
  // side -1 faces the camera in the hero shot
  wingRig.wings = WING_LAYOUT.map((l) => mkWing(l.W, l.side, l.root, l.sweep, l.fore));
}
buildButterfly();

const raycaster = new THREE.Raycaster(), HERO = hero;
const perch = (() => {
  raycaster.setFromCamera(new THREE.Vector2(0.414 * 2 - 1, 1 - 0.497 * 2), HERO.cam);
  const h = raycaster.intersectObject(perchMesh, false)[0];
  return h ? h.point : V3(-3.3, 1.5, 0.9);
})();
{
  const fwd = perchCenter.clone().sub(perch); fwd.y = 0; fwd.normalize();
  fwd.y = 0.22; fwd.normalize();
  const up = V3(0, 1, 0).addScaledVector(fwd, -0.22).normalize();
  const right = V3().crossVectors(up, fwd).normalize();
  up.crossVectors(fwd, right).normalize();
  // local +X -> right (away from the hero camera), so the side -1 wings face the viewer
  bfly.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(right, up, fwd));
  bfly.rotateY(P.bflyYaw * D2R);
  bfly.position.copy(perch).addScaledVector(up, 0.24);
  bfly.updateMatrixWorld(true);
}
/* -------- wing clearance: smallest lift / pitch / yaw that keeps the whole flap above the petals */
{
  // upper envelope of the perchSurface around the perch, as a height field (max petal height per cell)
  const res = 0.06, n = 280, x0 = perch.x - n * res / 2, z0 = perch.z - n * res / 2;
  const hf = new Float32Array(n * n).fill(-1e9);
  perchMesh.updateMatrixWorld(true);
  const pa = perchSurface.geometry.attributes.position, v = V3();
  for (let i = 0; i < pa.count; i++) {
    v.fromBufferAttribute(pa, i).applyMatrix4(perchMesh.matrixWorld);
    const ix = Math.floor((v.x - x0) / res), iz = Math.floor((v.z - z0) / res);
    if (ix >= 0 && iz >= 0 && ix < n && iz < n && v.y > hf[iz * n + ix]) hf[iz * n + ix] = v.y;
  }
  const hd = hf.slice(); // dilate so sparse vertices form a closed surface
  for (let z = 0; z < n; z++) for (let x = 0; x < n; x++) {
    let m = -1e9;
    for (let dz = -2; dz <= 2; dz++) for (let dx = -2; dx <= 2; dx++) { const xx = x + dx, zz = z + dz; if (xx >= 0 && zz >= 0 && xx < n && zz < n) m = Math.max(m, hf[zz * n + xx]); }
    hd[z * n + x] = m;
  }
  const heightAt = (x, z) => { const ix = Math.floor((x - x0) / res), iz = Math.floor((z - z0) / res); return ix >= 0 && iz >= 0 && ix < n && iz < n ? hd[iz * n + ix] : -1e9; };
  const bodyPts = [V3(0, 0.08, 0.05), V3(0, 0.12, -0.6), V3(0, 0.08, -1.2), V3(0, 0.06, -2.05), V3(0, 0.25, 0.75)];
  const q0 = bfly.quaternion.clone(), p0 = bfly.position.clone(), up = V3(0, 1, 0);
  const wp = V3(), m4 = new THREE.Matrix4();
  const strokePoses = [];
  for (let tt = 0; tt < FLAP.duration; tt += 0.1) {
    const ps = wingPose(tt); // keep distinct (opening, flex) states only
    if (!strokePoses.some((q) => Math.abs(q.open - ps.open) < 0.01 && Math.abs(q.flex - ps.flex) < 0.03)) strokePoses.push(ps);
  }
  strokePoses.push({ open: OPEN_MIN, flex: 0.32 }, { open: OPEN_MAX, flex: -0.32 });
  const penetration = (pose) => {
    let pen = -1e9;
    for (const wg of wingRig.wings) {
      wg.open.rotation.z = -wg.side * (pose.open + (wg.fore ? FORE_LEAD : 0));
      wg.open.updateMatrixWorld(true);
      m4.copy(wg.mesh.matrixWorld);
      for (const [a, b] of wg.W.outline) {
        wp.set(wingOutward(wg, a, b, pose.flex) * wg.side, b, a).applyMatrix4(m4);
        const d = heightAt(wp.x, wp.z) + 0.1 - wp.y; if (d > pen) { pen = d; penetration.worst = [wg.fore ? 'fore' : 'hind', wg.side, a, b]; }
      }
    }
    for (const bp of bodyPts) { wp.copy(bp).applyMatrix4(bfly.matrixWorld); const d = heightAt(wp.x, wp.z) + 0.04 - wp.y; if (d > pen) { pen = d; penetration.worst = ['body', bp.z]; } }
    return pen;
  };
  const pose = (pitch, yaw, lift) => {
    bfly.quaternion.copy(q0).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch, yaw, 0, 'YXZ')));
    bfly.position.copy(p0).addScaledVector(up, lift);
    bfly.updateMatrixWorld(true);
  };
  let best = { cost: Infinity, pitch: 0, yaw: 0, lift: 0 };
  for (let pitch = -12; pitch <= 24; pitch += 4) for (let yaw = -30; yaw <= 30; yaw += 10) {
    for (let lift = 0; lift <= 1.2; lift += 0.05) {
      const cost = lift + Math.abs(pitch) * 0.012 + Math.abs(yaw) * 0.008;
      if (cost >= best.cost) break;
      pose(-pitch * D2R, yaw * D2R, lift);
      if (strokePoses.every((ps) => penetration(ps) <= 0)) { best = { cost, pitch, yaw, lift }; break; }
    }
  }
  pose(-best.pitch * D2R, best.yaw * D2R, best.lift);
  bfly.userData.clearance = best;
  bfly.userData.clearanceDebug = { penetration, pose, heightAt };
}
{
  // six segmented legs: femur up and out to the knee, tibia down, tarsus gripping the petal
  const toWorld = (v) => v.clone().applyMatrix4(bfly.matrixWorld);
  const toLocal = (v) => bfly.worldToLocal(v.clone());
  const LEGS = [ // hip z, knee [x, y, z], foot guess [x, z]
    { hz: 0.3, knee: [0.42, 0.36, 0.72], foot: [0.5, 1.12] },
    { hz: 0.08, knee: [0.6, 0.34, 0.16], foot: [0.8, 0.18] },
    { hz: -0.14, knee: [0.56, 0.32, -0.48], foot: [0.74, -0.88] },
  ];
  const joint = new THREE.SphereGeometry(1, 10, 8);
  const spine = new THREE.ConeGeometry(1, 1, 3, 1, true); spine.translate(0, 0.5, 0);
  const spines = [];
  for (const sx of [-1, 1]) LEGS.forEach((L) => {
    const coxaBase = V3(sx * 0.08, 0.2, L.hz - 0.04), hip = V3(sx * 0.18, 0.12, L.hz + 0.03);
    { const m = new THREE.Mesh(taperTube([coxaBase, coxaBase.clone().lerp(hip, 0.5).add(V3(0, -0.02, 0)), hip], 0.05, 0.034, 8), legMat); m.castShadow = true; bfly.add(m); }
    const knee = V3(sx * L.knee[0], L.knee[1], L.knee[2]);
    raycaster.set(toWorld(V3(sx * L.foot[0], 1.5, L.foot[1])), V3(0, -1, 0));
    const h = raycaster.intersectObject(perchMesh, false)[0];
    let foot = h ? toLocal(h.point) : V3(sx * L.foot[0], -0.32, L.foot[1]);
    if (foot.y < -0.8 || foot.y > 0.1) foot.y = -0.32;
    const ankle = knee.clone().lerp(foot, 0.7).add(V3(sx * 0.05, 0.06, 0));
    const tarsMid = ankle.clone().lerp(foot, 0.55).add(V3(sx * 0.03, 0.03, 0));
    const parts = [
      taperTube([hip, hip.clone().lerp(knee, 0.5).add(V3(0, 0.07, 0)), knee], 0.03, 0.022, 16),
      taperTube([knee, knee.clone().lerp(ankle, 0.5).add(V3(sx * 0.05, 0.03, 0)), ankle], 0.02, 0.014, 16),
      taperTube([ankle, tarsMid, foot], 0.01, 0.006, 16, 5),
    ];
    parts.forEach((g) => { const m = new THREE.Mesh(g, legMat); m.castShadow = true; bfly.add(m); });
    [[knee, 0.025], [ankle, 0.015]].forEach(([p, r]) => { const j = new THREE.Mesh(joint, legMat); j.position.copy(p); j.scale.setScalar(r); bfly.add(j); });
    for (let i = 1; i < 7; i++) { // tibial spines
      const p = knee.clone().lerp(ankle, i / 7);
      const d = ankle.clone().sub(knee).normalize().add(V3(sx * 0.6, -0.4, 0)).normalize();
      spines.push(new THREE.Matrix4().compose(p, new THREE.Quaternion().setFromUnitVectors(V3(0, 1, 0), d), V3(0.004, 0.045, 0.004)));
    }
  });
  const sp = new THREE.InstancedMesh(spine, legMat, spines.length);
  spines.forEach((m, i) => sp.setMatrixAt(i, m)); bfly.add(sp);
}

/* -------- butterfly glow lights */
/* -------- wing light: each wing is an extended emitter. Its emitted radiance (the same terms the
   wing shader emits) is integrated over its area; a two-sided Lambertian emitter of radiance L and
   area A radiates the flux of an isotropic point source of intensity L*A/2, placed at the emission
   centroid. The lights ride on the wings and cast shadows. */
function wingEmission(W) {
  const gold = new THREE.Color('#ffc47a'), spot = new THREE.Color('#ffdca0'), cy = new THREE.Color('#5fd8ff'), warm = new THREE.Color('#fff0cc');
  const lin = (u) => Math.pow(u / 255, 2.2);
  const sum = V3(), cen = V3(); let wsum = 0, area = 0;
  const step = 4, cellArea = (step / W.ppc) ** 2;
  for (let y = 0; y < W.H; y += step) for (let x = 0; x < W.W; x += step) {
    const i4 = (y * W.W + x) * 4, cov = W.colData[i4 + 3] / 255;
    if (cov < 0.02) continue;
    const a = x / W.ppc + W.minA, b = W.maxB - y / W.ppc;
    const glow = Math.exp(-1.35 * Math.hypot(a, b));
    const vein = W.maskData[i4] / 255, sp = W.maskData[i4 + 1] / 255, dark = W.maskData[i4 + 2] / 255, cyn = W.maskData[i4 + 3] / 255;
    // scale coverage and luminous gain enter through their cell means; the pigment mottling is
    // luminance-neutral to within a few percent and is left out
    const k = (1 - dark * 0.8) * (glow * 0.75 + 0.4) * P.wing.membrane * WING_SCALE.meanMask * WING_SCALE.meanGain;
    const e = [0, 1, 2].map((c) => {
      const base = lerp(lin(W.colData[i4 + c]), [warm.r, warm.g, warm.b][c], glow * 0.55) * k;
      return (base + [gold.r, gold.g, gold.b][c] * vein * (glow * 2.0 + 0.8) * P.wing.vein + [spot.r, spot.g, spot.b][c] * sp * P.wing.spot + [cy.r, cy.g, cy.b][c] * cyn * 1.3 * WING_SCALE.meanGain) * P.wing.gain;
    });
    const opacity = cov * lerp(0.94, 1, Math.max(vein, dark));
    sum.x += e[0] * opacity * cellArea; sum.y += e[1] * opacity * cellArea; sum.z += e[2] * opacity * cellArea;
    area += opacity * cellArea;
    const lum = (0.2126 * e[0] + 0.7152 * e[1] + 0.0722 * e[2]) * opacity * cellArea;
    cen.x += a * lum; cen.y += b * lum; wsum += lum;
  }
  return { LA: sum, area, centroid: [cen.x / wsum, cen.y / wsum] };
}
// A wing is centimetres across, so close to it a point source (1/d^2) would deliver far more light than
// the wing can. Wing lights are finite emitters of equivalent radius R = sqrt(A/pi): irradiance
// I / (d^2 + R^2), the on-axis law of a disc, equal to the point law far away and bounded up close.
class WingLight extends THREE.PointLight {
  constructor(color, intensity, radius) { super(color, intensity, 0, 2); this.radius = radius; }
}
// A wing is also a flat Lambertian emitter, lit on both faces: its intensity falls off as |cos| of the
// angle from the wing normal (2|cos| keeps the same total flux as the isotropic L*A/2), so it lights
// what it faces and barely anything edge-on to it.
class WingLightNode extends THREE.PointLightNode {
  constructor(light = null) { super(light); this.radiusNode = uniform(0); this.normalNode = uniform(V3(1, 0, 0)); }
  update(frame) {
    super.update(frame);
    this.radiusNode.value = this.light.radius;
    this.normalNode.value.set(1, 0, 0).transformDirection(this.light.parent.matrixWorld); // wing plane normal
  }
  setupDirect(builder) {
    const lightVector = this.getLightVector(builder);
    const d2 = dot(lightVector, lightVector);
    const dir = normalize(lightVector);
    const nView = normalize(cameraViewMatrix.mul(vec4(this.normalNode, 0.0)).xyz);
    const lobe = abs(dot(dir, nView)).mul(2.0);
    return { lightDirection: dir, lightColor: this.colorNode.mul(lobe).div(d2.add(this.radiusNode.mul(this.radiusNode))) };
  }
}
renderer.library.addLight(WingLightNode, WingLight);
const wingLights = [];
const dustLights = []; // the same wing lights, as uniforms for airborne dust (see dustRadiance)
for (const wg of wingRig.wings) {
  const W = wg.fore ? FORE : HIND;
  W.emission ??= wingEmission(W);
  const I = W.emission.LA.clone().multiplyScalar(0.5), peak = Math.max(I.x, I.y, I.z);
  const light = new WingLight(new THREE.Color(I.x / peak, I.y / peak, I.z / peak), peak, Math.sqrt(W.emission.area / Math.PI));
  light.position.set(0, W.emission.centroid[1], W.emission.centroid[0]);
  light.castShadow = true;
  light.shadow.mapSize.set(512, 512);
  light.shadow.camera.near = 0.05; light.shadow.camera.far = 80;
  light.shadow.bias = -0.002; light.shadow.normalBias = 0.02;
  wg.mesh.add(light);
  wingLights.push(light);
  dustLights.push({ light, pos: uniform(V3()), col: uniform(V3()), rad: uniform(light.radius), nrm: uniform(V3(1, 0, 0)) });
}
// Lens: thin-lens camera shared by the depth-of-field pass and the emitter layer.
const focusU = uniform(28), apertureU = uniform(P.dof.aperture); // aperture: CoC radius at infinity, frame-height units
const tanHalfFovU = uniform(Math.tan(30 * D2R / 2)), lensOnU = uniform(0);

// The out-of-focus image of a point (bokeh) is the lens's aperture, not a flat disc:
//  - a 9-blade iris with rounded blades;
//  - mechanical vignetting: toward the frame edges the barrel clips the disc into a cat's eye;
//  - spherical aberration: behind the focus plane the disc has a brighter rim, in front a softer edge;
//  - faint concentric rings from aspherical elements;
//  - longitudinal chromatic aberration: green-cyan fringe behind focus, magenta in front.
// The intensity profiles are normalised to unit mean over the disc, so the light in a disc is unchanged.
const LENS = (() => {
  const rimP = (r) => 0.8 + 0.7 * sstep(0.6, 0.97, r), softP = (r) => 1.25 - 0.55 * sstep(0.3, 1.0, r);
  let a = 0, b = 0, w = 0;
  for (let i = 0; i < 400; i++) { const r = (i + 0.5) / 400; a += rimP(r) * r; b += softP(r) * r; w += r; }
  return { rimNorm: w / a, softNorm: w / b, blades: 9 };
})();
function lensAperture(local, R, behind, ndc) {
  const Rs = R.max(1e-3);
  const rho = length(local).div(Rs);
  const seg = (2 * Math.PI) / LENS.blades;
  const a = mod(atan(local.y, local.x).add(Math.PI), seg).sub(seg / 2);
  const boundary = mix(float(1.0), float(Math.cos(seg / 2)).div(cos(a)), 0.35);       // rounded blades
  const iris = clamp(boundary.sub(rho).mul(Rs).add(0.5), 0.0, 1.0);                  // 1 px antialiased edge
  const barrel = clamp(float(1.12).sub(length(local.add(ndc.mul(Rs.mul(0.6)))).div(Rs)).mul(Rs).add(0.5), 0.0, 1.0);
  const profile = mix(float(1.25).sub(smoothstep(0.3, 1.0, rho).mul(0.55)).mul(LENS.softNorm),
                      float(0.8).add(smoothstep(0.6, 0.97, rho).mul(0.7)).mul(LENS.rimNorm), behind)
                  .mul(sin(rho.mul(38.0)).mul(0.05).add(1.0));
  const fringe = smoothstep(0.75, 1.0, rho).mul(0.6).mul(smoothstep(1.5, 4.0, Rs));  // only on resolvable discs
  const tint = mix(vec3(1.0), mix(vec3(1.1, 0.85, 1.1), vec3(0.82, 1.08, 1.05), behind), fringe);
  return tint.mul(profile).mul(iris).mul(barrel);
}

// Glowworms (and a few drifting spores) are tiny steady emitters on the wall / in the air. They do not
// write depth, so the depth-of-field pass cannot know their distance from the depth buffer. Instead
// each emitter is imaged by the lens itself: a point source at distance z appears as a disc whose radius
// is the thin-lens circle of confusion at its own z, with its energy spread over that disc. They are
// depth-tested against the scene (so geometry in front hides them) and written to their own render
// target ("emitter layer"), which is added to the depth-of-field result before bloom.
const emitterMaterials = [];
// Dust motes do not glow on their own: they scatter the light falling on them. Each wing light (a
// Lambertian emitter of finite size, as in WingLightNode) and the moonlight contribute irradiance, and
// dust scatters strongly forward (Henyey-Greenstein, g = 0.7): motes between the eye and the glowing
// wings flare, motes lit from the side or front stay faint.
const dustMoon = { dir: uniform(V3(0, 1, 0)), col: uniform(V3()) };
const henyeyGreenstein = (cosT, g) => float((1 - g * g) / (4 * Math.PI)).div(pow(float(1 + g * g).sub(cosT.mul(2 * g)), 1.5));
function dustRadiance(centre, albedo) {
  const toEye = normalize(cameraPosition.sub(centre));
  let L = vec3(0.0);
  for (const l of dustLights) {
    const v = l.pos.sub(centre), d2 = dot(v, v), dir = v.div(sqrt(d2));
    const E = l.col.mul(abs(dot(dir, l.nrm)).mul(2.0)).div(d2.add(l.rad.mul(l.rad)));
    L = L.add(E.mul(henyeyGreenstein(dot(dir.negate(), toEye), 0.7)));
  }
  L = L.add(dustMoon.col.mul(henyeyGreenstein(dot(dustMoon.dir.negate(), toEye), 0.7)));
  return L.mul(albedo).mul(4.0); // radiance: albedo * irradiance * phase * 4 (isotropic phase -> albedo*E/pi)
}
function spriteCloud(list, { drift = 0, scatter = false } = {}) {
  const n = list.length;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 4);
  list.forEach((o, i) => { pos.set([o.p.x, o.p.y, o.p.z], i * 3); col.set([o.c.r, o.c.g, o.c.b, o.s], i * 4); });
  const pA = instancedBufferAttribute(new THREE.InstancedBufferAttribute(pos, 3));
  const cA = instancedBufferAttribute(new THREE.InstancedBufferAttribute(col, 4));
  const m = new THREE.SpriteNodeMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
  let centre = pA;
  if (drift > 0) {
    const ph = hash21(pA.xy);
    centre = pA.add(vec3(sin(time.mul(0.11).add(ph.mul(40.0))), sin(time.mul(0.07).add(ph.mul(21.0))).mul(0.6), cos(time.mul(0.09).add(ph.mul(13.0)))).mul(drift));
  }
  m.positionNode = centre;
  const z = cameraViewMatrix.mul(vec4(centre, 1.0)).z.negate();
  const coc = clamp(apertureU.mul(abs(z.sub(focusU))).div(z), 0.0, apertureU);    // disc radius / frame height
  const discDiameter = max(cA.w, coc.mul(z.mul(tanHalfFovU).mul(2.0)).mul(2.0).mul(lensOnU)); // world units
  m.scaleNode = discDiameter;
  const energy = cA.w.div(discDiameter).pow(2.0); // same light, spread over the larger disc
  const pxPerWorld = viewportSize.y.div(z.mul(tanHalfFovU).mul(2.0));
  const Rpx = varying(discDiameter.mul(pxPerWorld).mul(0.5));
  const clip = cameraProjectionMatrix.mul(cameraViewMatrix).mul(vec4(centre, 1.0));
  const ndc = varying(clip.xy.div(clip.w));
  const behind = varying(step(focusU, z).mul(lensOnU));
  const radiance = scatter ? varying(dustRadiance(centre, cA.xyz)) : cA.xyz;
  const local = uv().sub(0.5).mul(Rpx.mul(2.0));
  const aperture = select(lensOnU.greaterThan(0.5), lensAperture(local, Rpx, behind, ndc), vec3(smoothstep(1.0, 0.9, length(uv().sub(0.5)).mul(2.0))));
  m.colorNode = radiance.mul(aperture).mul(energy);
  m.opacityNode = float(1.0);
  emitterMaterials.push(m);
  const sprite = new THREE.Sprite(m); sprite.count = n; sprite.frustumCulled = false;
  return sprite;
}

await setupStage({ hero, raycaster, bfly, dustMoon, spriteCloud, P });
// From here on the camera lens images the emitters, and they render into the emitter layer only.
lensOnU.value = 1;
for (const m of emitterMaterials) { m.mrtNode = mrt({ output: vec4(0.0), emitters: vec4(m.colorNode, 1.0) }); m.needsUpdate = true; }
function auditButterfly({ step = 0.05, furEvery = 4 } = {}) {
  const T0 = performance.now();
  const ART = 0.3; // articulation radius around each hinge root
  // a wing triangle takes part if any of it is solid; a hit only counts where the wing is solid
  const solidAt = (W, a, b) => wingCoverage(W, a, b) > WING_SOLID;
  const wings = wingRig.wings.map((wg) => {
    const g = wg.mesh.geometry, L = g.attributes.position.array, I = g.index.array;
    const tris = [];
    for (let i = 0; i < I.length; i += 3) {
      const ab = [0, 1, 2].map((k) => [L[I[i + k] * 3 + 2], L[I[i + k] * 3 + 1]]);
      const probes = [...ab, [(ab[0][0] + ab[1][0] + ab[2][0]) / 3, (ab[0][1] + ab[1][1] + ab[2][1]) / 3]];
      if (probes.some(([a, b]) => solidAt(wg.W, a, b))) tris.push(I[i], I[i + 1], I[i + 2]);
    }
    return { wg, L, n: L.length / 3, tris: Uint32Array.from(tris), world: new Float32Array(L.length), body: new Float32Array(L.length),
      name: `${wg.side < 0 ? 'L' : 'R'}-${wg.fore ? 'fore' : 'hind'}` };
  });

  // ---- geometry helpers
  const sub = (o, a, b) => { o[0] = a[0] - b[0]; o[1] = a[1] - b[1]; o[2] = a[2] - b[2]; return o; };
  const cross = (o, a, b) => { o[0] = a[1] * b[2] - a[2] * b[1]; o[1] = a[2] * b[0] - a[0] * b[2]; o[2] = a[0] * b[1] - a[1] * b[0]; return o; };
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const e1 = [0, 0, 0], e2 = [0, 0, 0], hv = [0, 0, 0], sv = [0, 0, 0], qv = [0, 0, 0], dv = [0, 0, 0];
  const hit = { t: 0, u: 0, v: 0 };
  const segTri = (p, q, a, b, c) => { // Moller-Trumbore on the segment p->q; fills hit
    sub(dv, q, p); sub(e1, b, a); sub(e2, c, a); cross(hv, dv, e2);
    const det = dot(e1, hv); if (Math.abs(det) < 1e-12) return false;
    const f = 1 / det; sub(sv, p, a);
    const u = f * dot(sv, hv); if (u < 0 || u > 1) return false;
    cross(qv, sv, e1); const v = f * dot(dv, qv); if (v < 0 || u + v > 1) return false;
    const t = f * dot(e2, qv); if (t < 0 || t > 1) return false;
    hit.t = t; hit.u = u; hit.v = v; return true;
  };
  // (a, b) wing coordinates at a point of a wing triangle: edge parameter or barycentric
  const abOnEdge = (Lab, i, j, t) => [lerp(Lab[i][0], Lab[j][0], t), lerp(Lab[i][1], Lab[j][1], t)];
  const abInTri = (Lab, u, v) => [Lab[0][0] * (1 - u - v) + Lab[1][0] * u + Lab[2][0] * v, Lab[0][1] * (1 - u - v) + Lab[1][1] * u + Lab[2][1] * v];
  // solid triangle/triangle intersection; Wa/Wb are wings (null = always solid, e.g. a petal)
  const EDGES = [[0, 1], [1, 2], [2, 0]];
  const triTri = (A, Aab, Wa, B, Bab, Wb) => {
    for (const [i, j] of EDGES) if (segTri(A[i], A[j], ...B)) {
      if ((!Wa || solidAt(Wa, ...abOnEdge(Aab, i, j, hit.t))) && (!Wb || solidAt(Wb, ...abInTri(Bab, hit.u, hit.v)))) return true;
    }
    for (const [i, j] of EDGES) if (segTri(B[i], B[j], ...A)) {
      if ((!Wb || solidAt(Wb, ...abOnEdge(Bab, i, j, hit.t))) && (!Wa || solidAt(Wa, ...abInTri(Aab, hit.u, hit.v)))) return true;
    }
    return false;
  };
  const abOf = (w, t3) => [0, 1, 2].map((k) => [w.L[w.tris[t3 + k] * 3 + 2], w.L[w.tris[t3 + k] * 3 + 1]]);
  const vtx = (arr, i) => [arr[i * 3], arr[i * 3 + 1], arr[i * 3 + 2]];
  const CELL = 0.2;
  const hashTris = (pos, tris) => {
    const h = new Map();
    for (let t = 0; t < tris.length; t += 3) {
      let x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
      for (let k = 0; k < 3; k++) { const i = tris[t + k] * 3; x0 = Math.min(x0, pos[i]); x1 = Math.max(x1, pos[i]); y0 = Math.min(y0, pos[i + 1]); y1 = Math.max(y1, pos[i + 1]); z0 = Math.min(z0, pos[i + 2]); z1 = Math.max(z1, pos[i + 2]); }
      for (let x = Math.floor(x0 / CELL); x <= Math.floor(x1 / CELL); x++) for (let y = Math.floor(y0 / CELL); y <= Math.floor(y1 / CELL); y++) for (let z = Math.floor(z0 / CELL); z <= Math.floor(z1 / CELL); z++) {
        const k = `${x},${y},${z}`; let c = h.get(k); if (!c) h.set(k, c = []); c.push(t);
      }
    }
    return h;
  };
  // candidates of hash h near an AABB, deduplicated with a stamp array (one fresh id per query)
  let Q = 0;
  const near = (h, stamp, x0, y0, z0, x1, y1, z1, fn) => {
    const id = ++Q;
    for (let x = Math.floor(x0 / CELL); x <= Math.floor(x1 / CELL); x++) for (let y = Math.floor(y0 / CELL); y <= Math.floor(y1 / CELL); y++) for (let z = Math.floor(z0 / CELL); z <= Math.floor(z1 / CELL); z++) {
      const c = h.get(`${x},${y},${z}`); if (!c) continue;
      for (const t of c) { if (stamp[t / 3] === id) continue; stamp[t / 3] = id; if (fn(t)) return true; }
    }
    return false;
  };
  const triOf = (pos, tris, t) => [vtx(pos, tris[t]), vtx(pos, tris[t + 1]), vtx(pos, tris[t + 2])];
  const aabb = (T) => [Math.min(T[0][0], T[1][0], T[2][0]), Math.min(T[0][1], T[1][1], T[2][1]), Math.min(T[0][2], T[1][2], T[2][2]),
    Math.max(T[0][0], T[1][0], T[2][0]), Math.max(T[0][1], T[1][1], T[2][1]), Math.max(T[0][2], T[1][2], T[2][2])];

  // ---- perchSurface triangles near the butterfly (static)
  perchMesh.updateMatrixWorld(true);
  const rp = perchSurface.geometry.attributes.position, RI = perchSurface.geometry.index.array;
  const rosePos = new Float32Array(rp.count * 3), tmp = V3();
  for (let i = 0; i < rp.count; i++) { tmp.fromBufferAttribute(rp, i).applyMatrix4(perchMesh.matrixWorld); rosePos.set([tmp.x, tmp.y, tmp.z], i * 3); }
  const roseTris = [];
  for (let i = 0; i < RI.length; i += 3) {
    const c = vtx(rosePos, RI[i]); if (Math.hypot(c[0] - bfly.position.x, c[1] - bfly.position.y, c[2] - bfly.position.z) < 8) roseTris.push(RI[i], RI[i + 1], RI[i + 2]);
  }
  const roseT = Uint32Array.from(roseTris), roseHash = hashTris(rosePos, roseT), roseStamp = new Int32Array(roseT.length / 3).fill(-1);

  // ---- body solids (butterfly-local)
  const solids = bfly.userData.solids, abd = bfly.userData.abdomen, abdInv = abd.mesh.matrix.clone().invert();
  const thorax = solids.slice(1, 4); // meso, meta, prothorax/neck: where wing bases articulate
  const inEll = (s, p) => ((p[0] - s.c.x) / s.r.x) ** 2 + ((p[1] - s.c.y) / s.r.y) ** 2 + ((p[2] - s.c.z) / s.r.z) ** 2 < 1;
  const inAbd = (p) => { tmp.set(p[0], p[1], p[2]).applyMatrix4(abdInv); const s = tmp.y / abd.length; return s > 0 && s < 1 && Math.hypot(tmp.x, tmp.z) < abd.radius(s); };

  // ---- fur segments (butterfly-local, bent strands: base -> mid -> tip)
  const hairs = [];
  bfly.children.filter((c) => c.isInstancedMesh && c.userData.fur).forEach((im) => {
    const m = new THREE.Matrix4();
    const strandPts = [0, 1, 2, 3, 4, 5, 6].map((k) => V3(0.3 * (k / 6) ** 2, k / 6, 0)); // the bent strand geometry
    for (let i = 0; i < im.count; i++) { im.getMatrixAt(i, m); hairs.push(strandPts.map((v) => v.clone().applyMatrix4(m))); }
  });

  const R = { frames: 0, wingWing: {}, wingBody: { hits: 0, frames: 0, worst: null }, articulation: { buried: 0 }, wingRose: { hits: 0, frames: 0, worst: null }, furWing: { hits: 0, framesTested: 0 }, furBody: { hairs: hairs.length, inside: 0 } };
  // fur <-> body (static): any strand point beyond the root inside a body solid
  for (const h of hairs) if (h.slice(1).some((v) => solids.some((sd) => inEll(sd, v.toArray())) || inAbd(v.toArray()))) R.furBody.inside++;
  const pairs = [[0, 1], [2, 3], [0, 2], [1, 3], [0, 3], [1, 2]];
  pairs.forEach(([a, b]) => { R.wingWing[`${wings[a].name} x ${wings[b].name}`] = { hits: 0, frames: 0 }; });
  const bflyInv = new THREE.Matrix4();
  const saved = wingRig.wings.map((wg) => wg.open.rotation.z), savedFlex = flexU.value;
  const total = Math.ceil(FLAP.duration / step); // the whole beat timeline
  for (let f = 0; f < total; f++) {
    const t = f * step;
    const pose = wingPose(t);
    for (const wg of wingRig.wings) wg.open.rotation.z = -wg.side * (pose.open + (wg.fore ? FORE_LEAD : 0));
    bfly.updateMatrixWorld(true); bflyInv.copy(bfly.matrixWorld).invert();
    for (const w of wings) {
      const M = w.wg.mesh.matrixWorld;
      for (let i = 0; i < w.n; i++) {
        const b = w.L[i * 3 + 1], a = w.L[i * 3 + 2];
        tmp.set(w.wg.side * wingOutward(w.wg, a, b, pose.flex), b, a).applyMatrix4(M);
        w.world[i * 3] = tmp.x; w.world[i * 3 + 1] = tmp.y; w.world[i * 3 + 2] = tmp.z;
        tmp.applyMatrix4(bflyInv); w.body[i * 3] = tmp.x; w.body[i * 3 + 1] = tmp.y; w.body[i * 3 + 2] = tmp.z;
      }
      w.root = V3(...w.wg.open.position.toArray());
      w.hash = hashTris(w.world, w.tris); w.stamp = new Int32Array(w.tris.length / 3).fill(-1);
    }
    // wing <-> wing
    pairs.forEach(([ia, ib], pi) => {
      const A = wings[ia], B = wings[ib], rec = R.wingWing[`${A.name} x ${B.name}`];
      let hits = 0;
      for (let t3 = 0; t3 < A.tris.length; t3 += 3) {
        const TA = triOf(A.world, A.tris, t3), bb = aabb(TA);
        const Aab = abOf(A, t3);
        if (near(B.hash, B.stamp, ...bb, (tb) => triTri(TA, Aab, A.wg.W, triOf(B.world, B.tris, tb), abOf(B, tb), B.wg.W))) hits++;
      }
      if (hits) { rec.hits += hits; rec.frames++; if (!rec.worst || hits > rec.worst.hits) rec.worst = { t: +t.toFixed(2), open: +(pose.open / D2R).toFixed(1), hits }; }
    });
    // wing <-> body (points: vertices of opaque triangles)
    let bodyHits = 0;
    for (const w of wings) {
      const seen = new Uint8Array(w.n);
      for (const i of w.tris) {
        if (seen[i]) continue; seen[i] = 1;
        if (!solidAt(w.wg.W, w.L[i * 3 + 2], w.L[i * 3 + 1])) continue;
        const pnt = vtx(w.body, i);
        const inside = solids.some((s) => inEll(s, pnt)) || inAbd(pnt);
        if (!inside) continue;
        const dRoot = Math.hypot(pnt[0] - w.root.x, pnt[1] - w.root.y, pnt[2] - w.root.z);
        if (dRoot < ART && thorax.some((s) => inEll(s, pnt))) { if (f === 0) R.articulation.buried++; continue; }
        bodyHits++;
        if (!R.wingBody.worst) R.wingBody.worst = { wing: w.name, t: +t.toFixed(2), at: pnt.map((v) => +v.toFixed(2)) };
      }
    }
    if (bodyHits) { R.wingBody.hits += bodyHits; R.wingBody.frames++; }
    // wing <-> petals
    let roseHits = 0;
    for (const w of wings) for (let t3 = 0; t3 < w.tris.length; t3 += 3) {
      const TA = triOf(w.world, w.tris, t3), bb = aabb(TA);
      const Aab = abOf(w, t3);
      if (near(roseHash, roseStamp, ...bb, (tr) => triTri(TA, Aab, w.wg.W, triOf(rosePos, roseT, tr), null, null))) roseHits++;
    }
    if (roseHits) { R.wingRose.hits += roseHits; R.wingRose.frames++; if (!R.wingRose.worst || roseHits > R.wingRose.worst.hits) R.wingRose.worst = { t: +t.toFixed(2), open: +(pose.open / D2R).toFixed(1), hits: roseHits }; }
    // fur <-> wings
    if (f % furEvery === 0) {
      R.furWing.framesTested++;
      for (const h of hairs) {
        const pts = h.map((v) => { tmp.copy(v).applyMatrix4(bfly.matrixWorld); return [tmp.x, tmp.y, tmp.z]; });
        const bb = [0, 1, 2].map((c) => Math.min(...pts.map((q) => q[c]))).concat([0, 1, 2].map((c) => Math.max(...pts.map((q) => q[c]))));
        for (const w of wings) {
          if (near(w.hash, w.stamp, ...bb, (tb) => {
            const TB = triOf(w.world, w.tris, tb), Bab = abOf(w, tb);
            for (let k = 0; k < pts.length - 1; k++) if (segTri(pts[k], pts[k + 1], ...TB) && solidAt(w.wg.W, ...abInTri(Bab, hit.u, hit.v))) return true;
            return false;
          })) {
            R.furWing.hits++;
            if ((R.furWing.samples ??= []).length < 12) R.furWing.samples.push({ wing: w.name, t: +t.toFixed(2), base: h[0].toArray().map((v) => +v.toFixed(3)), tip: h[h.length - 1].toArray().map((v) => +v.toFixed(3)) });
            break;
          }
        }
      }
    }
    R.frames++;
  }
  wingRig.wings.forEach((wg, i) => { wg.open.rotation.z = saved[i]; }); flexU.value = savedFlex; bfly.updateMatrixWorld(true);
  R.ms = Math.round(performance.now() - T0);
  R.pass = Object.values(R.wingWing).every((r) => r.hits === 0) && R.wingBody.hits === 0 && R.wingRose.hits === 0 && R.furWing.hits === 0 && R.furBody.inside === 0;
  return R;
}

const butterflyFocus = V3(0, 1.2, 0.1).applyMatrix4(bfly.matrixWorld);
/* ============================================================ post pipeline */
const pipeline = new THREE.RenderPipeline(renderer);
// Ambient occlusion: a depth + normal pre-pass feeds GTAO, which attenuates only the indirect light
// (cave probe, ambient) of opaque materials. Direct light keeps its own shadow maps.
const prePass = pass(scene, camera);
prePass.transparent = false;
prePass.setMRT(mrt({ output: directionToColor(normalView), emitters: vec4(0.0) }));
const prePassNormal = prePass.getTextureNode('output');
const aoPass = ao(prePass.getTextureNode('depth'), sample((u) => colorToDirection(prePassNormal.sample(u))), camera);
aoPass.resolutionScale = 0.5;
aoPass.radius.value = P.ao.radius; aoPass.thickness.value = P.ao.thickness; aoPass.samples.value = 12;
const scenePass = pass(scene, camera);
scenePass.contextNode = builtinAOContext(aoPass.getTextureNode().sample(screenUV).r);
scenePass.setMRT(mrt({ output, emitters: vec4(0.0) })); // opaque surfaces write no emitter light (they occlude)
const sceneColor = scenePass.getTextureNode('output');
const emitterLayer = scenePass.getTextureNode('emitters');
const sceneDepth = scenePass.getTextureNode('depth');
const nearU = uniform(camera.near), farU = uniform(camera.far);
// Thin-lens depth of field. The circle of confusion follows the lens equation,
// CoC(z) = A * |z - z_focus| / z (radius, in frame heights), for gathered and scattered light alike.
const cocAt = (z) => clamp(apertureU.mul(abs(z.sub(focusU))).div(z), 0.0, apertureU);
const viewDistAt = (u) => perspectiveDepthToViewZ(sceneDepth.sample(u).r, nearU, farU).negate();
// Light is split by brightness. Everything up to the highlight level is gathered (below); the excess of
// bright pixels (antenna clubs, wing spots, glints: tiny sources a gather cannot sample without noise or
// leaking) is scattered: each such pixel is drawn as its own disc, sized by the CoC at its own depth,
// with its energy spread over that disc and hidden only where the scene is nearer than it.
const hiShare = (c) => clamp(luminance(c).sub(P.dof.highlight).div(max(luminance(c), 1e-4)), 0.0, 1.0);
const colorDepth = convertToTexture(vec4(sceneColor.rgb.mul(hiShare(sceneColor.rgb).oneMinus()), viewDistAt(uv())));
const highlightDepth = convertToTexture(vec4(sceneColor.rgb.mul(hiShare(sceneColor.rgb)), viewDistAt(uv())));
const bufferSizeU = uniform(new THREE.Vector2(1, 1)); // drawing-buffer pixels
const bokehScene = new THREE.Scene();
bokehScene.background = new THREE.Color(0x000000);
const bokehCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const bokehMesh = (() => {
  const m = new THREE.MeshBasicNodeMaterial({ transparent: true, depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending });
  const fi = float(instanceIndex);
  const gy = floor(fi.div(bufferSizeU.x)), gx = fi.sub(gy.mul(bufferSizeU.x));
  const cuv = vec2(gx, gy).add(0.5).div(bufferSizeU);              // this pixel, in texture coordinates
  const texel = highlightDepth.sample(cuv).level(0);
  const live = step(1e-5, luminance(texel.rgb));
  const rpx = max(cocAt(texel.a).mul(bufferSizeU.y), Math.sqrt(1 / Math.PI)); // disc radius in pixels (>= 1 px area)
  const halfSide = rpx.add(1.0).mul(live);                           // quad half-size, 1 px margin for the edge
  const yDown = renderer.backend.coordinateSystem === THREE.WebGPUCoordinateSystem;
  const ndc = vec2(cuv.x.mul(2.0).sub(1.0), yDown ? cuv.y.mul(-2.0).add(1.0) : cuv.y.mul(2.0).sub(1.0));
  m.vertexNode = vec4(ndc.add(positionLocal.xy.mul(halfSide.mul(4.0)).div(bufferSizeU)), 0.0, 1.0);
  const vLocal = varying(positionLocal.xy.mul(halfSide.mul(2.0)));   // pixels from the disc centre
  const vRadius = varying(rpx), vZ = varying(texel.a);
  const vRadiance = varying(texel.rgb.div(rpx.mul(rpx).mul(Math.PI)));
  const vNdc = varying(ndc), vBehind = varying(step(focusU, texel.a));
  const coverage = lensAperture(vLocal, vRadius, vBehind, vNdc);
  const visible = step(vZ.sub(vZ.mul(0.02).add(0.03)), colorDepth.sample(screenUV).a);
  m.colorNode = vRadiance.mul(coverage).mul(visible);
  m.opacityNode = float(1.0);
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), m);
  mesh.frustumCulled = false;
  bokehScene.add(mesh);
  return mesh;
})();
const bokehPass = pass(bokehScene, bokehCam);
const lensDof = Fn(() => {
  const uvc = uv();
  const aspect = viewportSize.x.div(viewportSize.y);
  const centre = colorDepth.sample(uvc);
  const zc = centre.a, cc = cocAt(zc);
  const px = float(1.0).div(viewportSize.y); // one pixel, in frame-height units
  const col = centre.rgb.toVar(), tot = float(1.0).toVar(), spread = float(0.0).toVar();
  const N = P.dof.samples;
  // every pixel uses its own rotation of the sample spiral (interleaved gradient noise), so the finite
  // sample set leaves unstructured noise for the reconstruction pass rather than shifted copies
  const fc = uvc.mul(viewportSize);
  const rot = fract(fract(fc.x.mul(0.06711056).add(fc.y.mul(0.00583715))).mul(52.9829189)).mul(6.2831853);
  Loop(N, ({ i }) => {
    const fi = float(i).add(0.5);
    const r = sqrt(fi.div(N)).mul(apertureU);
    const ang = fi.mul(2.39996323).add(rot);
    const su = uvc.add(vec2(cos(ang).div(aspect), sin(ang)).mul(r));
    const tap = colorDepth.sample(su);
    const zs = tap.a;
    const reach = select(zs.greaterThan(zc), min(cocAt(zs), cc.mul(2.0)), cocAt(zs));
    const m = smoothstep(r.sub(px), r.add(px), reach);
    col.addAssign(mix(col.div(tot), tap.rgb, m));
    tot.addAssign(1.0);
    spread.assign(max(spread, reach.mul(m)));
  });
  return vec4(col.div(tot), spread); // alpha: the widest disc that contributed here
});
// Reconstruction: the gather is a Monte Carlo estimate of the disc integral; its noise is filtered over
// the sample footprint, only where defocused light actually landed (in-focus pixels stay untouched).
const dofRaw = convertToTexture(lensDof());
const dofResolve = Fn(() => {
  const uvc = uv();
  const aspect = viewportSize.x.div(viewportSize.y);
  const centre = dofRaw.sample(uvc);
  const foot = min(centre.a, apertureU).mul(Math.sqrt(Math.PI / P.dof.samples)); // sample spacing at this blur
  const acc = centre.rgb.toVar(), wsum = float(1.0).toVar();
  Loop(12, ({ i }) => {
    const ang = float(i).mul(Math.PI / 6.0);
    const ring = select(i.lessThan(6), float(0.5), float(1.0));
    const tap = dofRaw.sample(uvc.add(vec2(cos(ang).div(aspect), sin(ang)).mul(foot).mul(ring)));
    const w = smoothstep(0.0, foot.mul(0.6).add(1e-5), tap.a); // only neighbours that are also defocused
    acc.addAssign(tap.rgb.mul(w)); wsum.addAssign(w);
  });
  return vec4(acc.div(wsum), 1.0);
});
const dofPass = convertToTexture(dofResolve());
// all light that reaches the sensor, then the glare of the optics over all of it
const imaged = convertToTexture(vec4(dofPass.rgb.add(bokehPass.getTextureNode('output').rgb).add(emitterLayer.rgb), 1.0));
const bloomPass = bloom(imaged, P.bloom.strength, P.bloom.radius, P.bloom.threshold / P.exposure);
// Exposure is set like a camera's: a 64x36 meter of the HDR image (before exposure), read back
// asynchronously, reduced to a weighted log-average (dark pixels down-weighted, the centre of frame
// weighted up), then exposure adapts toward middleGray / average, faster toward bright than dark.
// The renderer's exposure is the only exposure stage (consumed once by renderOutput).
const meterRT = new THREE.RenderTarget(64, 36, { type: THREE.UnsignedByteType, depthBuffer: false });
const meterQuad = new THREE.QuadMesh((() => {
  const m = new THREE.NodeMaterial();
  const l = luminance(texture(imaged.value, uv()).rgb);
  const enc = l.div(l.add(1.0)); // unbounded luminance into [0, 1)
  m.fragmentNode = vec4(enc, enc, enc, 1.0);
  return m;
})());
const meter = { pending: false, frame: 0, target: P.exposure, current: P.exposure, average: 0 };
function meterExposure(dt) {
  const M = P.meter;
  if (!NO_POST && !meter.pending && ++meter.frame % M.every === 0) {
    renderer.setRenderTarget(meterRT); meterQuad.render(renderer); renderer.setRenderTarget(null);
    meter.pending = true;
    renderer.readRenderTargetPixelsAsync(meterRT, 0, 0, 64, 36).then((px) => {
      // subject metering: centre-weighted log-average over the band between the 50th and 98th
      // luminance percentiles, so the black cave and specular extremes do not set the exposure
      const cells = [];
      for (let y = 0; y < 36; y++) for (let x = 0; x < 64; x++) {
        const e = px[(y * 64 + x) * 4] / 255, lum = e / Math.max(1e-4, 1 - e);
        const r2 = ((x + 0.5) / 64 - 0.5) ** 2 + ((y + 0.5) / 36 - 0.5) ** 2;
        cells.push([lum, 1 + 1.5 * Math.exp(-r2 / 0.06)]);
      }
      cells.sort((a, b) => a[0] - b[0]);
      let sum = 0, wsum = 0;
      for (let i = Math.floor(cells.length * 0.5); i < Math.floor(cells.length * 0.98); i++) { sum += Math.log(Math.max(cells[i][0], 1e-4)) * cells[i][1]; wsum += cells[i][1]; }
      meter.average = Math.exp(sum / wsum);
      meter.percentiles = [0.1, 0.5, 0.75, 0.9, 0.98].map((q) => +cells[Math.floor(q * (cells.length - 1))][0].toFixed(4));
      meter.target = THREE.MathUtils.clamp(M.middleGray / meter.average * 2 ** M.compensationEV, M.min, M.max);
    }).catch(() => {}).finally(() => { meter.pending = false; });
  }
  const speed = meter.target > meter.current ? M.up : M.down;
  meter.current += (meter.target - meter.current) * (1 - Math.exp(-Math.max(dt, 0) * speed));
  renderer.toneMappingExposure = meter.current;
  bloomPass.threshold.value = P.bloom.threshold / meter.current; // glare is a response of the exposed sensor
}
const hdrCol = NO_POST ? sceneColor.rgb.add(emitterLayer.rgb) : imaged.rgb.add(bloomPass.rgb);
const vd = screenUV.sub(0.5).mul(vec2(1.15, 1.0));
const vignette = smoothstep(0.95, 0.18, length(vd)).mul(0.62).add(0.38);
const graded = hdrCol.mul(NO_POST ? 1.0 : vignette).mul(vec3(0.92, 0.98, 1.08));
const display = renderOutput(vec4(graded, 1.0));
const grain = hash21(screenUV.mul(viewportSize).add(fract(time.mul(13.17)).mul(431.0))).sub(0.5).mul(NO_POST ? 0.0 : 0.028);
pipeline.outputColorTransform = false;
pipeline.outputNode = vec4(display.rgb.add(grain), 1.0);

/* ============================================================ animation */
let focusSnap = true;
const tmpV = V3();
function animateButterfly(t, dt) {
  // slow resting wing beat: long holds, unhurried open/close, small tremor (see wingPose)
  const { open, flex } = wingPose(t);
  flexU.value = flex;
  for (const wg of wingRig.wings) wg.open.rotation.z = -wg.side * (open + (wg.fore ? FORE_LEAD : 0));
  for (const r of wingRig) if (r.antenna) {
    r.antenna.rotation.x = Math.sin(t * 0.9 + r.antenna.userData.side) * 0.05;
    r.antenna.rotation.z = Math.sin(t * 0.63 + 2 * r.antenna.userData.side) * 0.04 * r.antenna.userData.side;
  }
  bfly.updateMatrixWorld();
  for (const d of dustLights) {
    d.light.getWorldPosition(d.pos.value);
    d.col.value.set(d.light.color.r, d.light.color.g, d.light.color.b).multiplyScalar(d.light.intensity);
    d.nrm.value.set(1, 0, 0).transformDirection(d.light.parent.matrixWorld);
  }
  return open;
}

const bufV2 = new THREE.Vector2(), camDir = V3();
let elapsed = 0, renderDelta = 0;
return {
  bfly, hero, butterflyFocus, auditButterfly,
  update(dt, orbitTarget) {
    dt = Math.min(dt, 0.05); elapsed += dt;
    animateButterfly(elapsed + 1.0, dt);
    const focusPoint = orbitTarget.distanceTo(butterflyFocus) < 9 ? butterflyFocus : orbitTarget;
  camera.getWorldDirection(camDir);
  const fd = Math.max(1, tmpV.copy(focusPoint).sub(camera.position).dot(camDir));
  focusU.value = focusSnap ? fd : lerp(focusU.value, fd, 1 - Math.exp(-dt * 6));
  focusSnap = false;

  tanHalfFovU.value = Math.tan(camera.fov * D2R / 2);
  renderer.getDrawingBufferSize(bufV2);
  if (bufV2.x !== bufferSizeU.value.x || bufV2.y !== bufferSizeU.value.y) { bufferSizeU.value.copy(bufV2); bokehMesh.count = bufV2.x * bufV2.y; }

    renderDelta = dt;
  },
  render() { pipeline.render(); meterExposure(renderDelta); },
  setDebugMode(mode) {
    NO_POST = mode === 'nopost';
    pipeline.outputNode = NO_POST ? renderOutput(vec4(sceneColor.rgb.add(emitterLayer.rgb), 1))
      : mode === 'scene' ? renderOutput(sceneColor)
      : mode === 'defocus' ? renderOutput(dofPass) : vec4(display.rgb.add(grain), 1.0);
    pipeline.needsUpdate = true;
  },
  dispose() {
    pipeline.dispose(); meterRT.dispose(); meterQuad.material.dispose();
    bokehMesh.geometry.dispose(); bokehMesh.material.dispose();
    const geometries = new Set(), materials = new Set();
    bfly.traverse(o => {
      if (o.geometry) geometries.add(o.geometry);
      if (o.material) materials.add(o.material);
      o.shadow?.dispose();
    });
    for (const g of geometries) g.dispose();
    for (const m of materials) m.dispose();
    for (const W of [FORE, HIND]) for (const v of Object.values(W)) if (v?.isTexture) v.dispose();
    bfly.removeFromParent();
  },
};
}
