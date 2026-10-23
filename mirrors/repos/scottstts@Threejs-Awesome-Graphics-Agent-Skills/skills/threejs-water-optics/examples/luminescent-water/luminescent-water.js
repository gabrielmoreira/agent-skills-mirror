import * as THREE from 'three/webgpu';
import {
  Fn, If, Loop, Break, float, int, uint, vec2, vec3, vec4, uvec2,
  instanceIndex, instancedArray, uniform, texture, textureStore,
  mix, clamp, smoothstep, max, min, abs, sqrt, exp, pow, floor, dot, normalize, length,
  reflect, refract, select, inverseSqrt, log2, fwidth, dFdx, dFdy, Discard,
  positionLocal, positionWorld, positionGeometry, cameraPosition, cameraViewMatrix,
  attribute, equirectUV, pass, screenUV, hash, time, renderOutput
} from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';
import { fxaa } from 'three/addons/tsl/display/FXAANode.js';

/** Coupled shallow-water transport, luminous film, bed optics and caustics.
 * Supply terrain.tex/H and calibrated rock textures; own the renderer and camera.
 */
export async function createLuminescentWater({
  renderer, scene, camera, terrain, colorTex, normalTex, packTex, packMean, env,
}) {
const TW = 10.24, TL = 10.24;            // terrain tile width (x) and period (z)
const MRES = 1024;                       // macro terrain texels per side (1 cm)
const MT = TW / MRES;
const NX = 512, NZ = 1024, N = NX * NZ;  // shallow-water grid (1 cm cells)
const DX = 0.01;
const SW = NX * DX, SL = NZ * DX;        // 5.12 x 10.24
const SX0 = (TW - SW) / 2;               // sim x origin
const G = 9.81;
const MICRO_TILE = 1.6;                  // metres covered by one 4K texture tile
const MICRO_AMP = 0.055;                 // displacement amplitude (m)
const WATER_LEVEL = 0.0;
const H_EPS = 0.0006;
const VMAX = 4.0;
const DET_FREQ = 1.0 / 0.45;             // advected detail texture: tiles per metre
const LX = 128, LZ = 256;                // low-res luminance field for area lighting
const CAUS_X = 512, CAUS_Z = 1024;       // caustic mesh resolution (= sim resolution)
const CAUS_RT_X = 1024, CAUS_RT_Z = 2048;

const params = {
  exposure: 1.05, flow: 0.032, manning: 0.028, excitation: 1.0, emission: 1.0,
  caustics: 2.2, detail: 2.2, bloom: 0.5, substeps: 8, dispersion: true,
  vorticity: 3.0, boils: 0.5,
};

// ============================================================================================
//  Small CPU utilities: seeded rng + periodic gradient noise (for macro terrain + detail maps)
// ============================================================================================
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function makeNoise(rng) {
  const perm = new Uint16Array(1024); const p = [...Array(512).keys()];
  for (let i = 511; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
  for (let i = 0; i < 1024; i++) perm[i] = p[i & 511];
  const gx = new Float32Array(512), gy = new Float32Array(512);
  for (let i = 0; i < 512; i++) { const a = rng() * Math.PI * 2; gx[i] = Math.cos(a); gy[i] = Math.sin(a); }
  const fade = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  // periodic with integer period (px, py) in lattice units
  return (x, y, px, py) => {
    const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
    const x0 = ((xi % px) + px) % px, y0 = ((yi % py) + py) % py, x1 = (x0 + 1) % px, y1 = (y0 + 1) % py;
    const h = (a, b) => perm[perm[a & 511] + (b & 511)];
    const g = (hh, dx, dy) => gx[hh] * dx + gy[hh] * dy;
    const n00 = g(h(x0, y0), fx, fy), n10 = g(h(x1, y0), fx - 1, fy), n01 = g(h(x0, y1), fx, fy - 1), n11 = g(h(x1, y1), fx - 1, fy - 1);
    const u = fade(fx), v = fade(fy);
    return 1.4142 * ((n00 * (1 - u) + n10 * u) * (1 - v) + (n01 * (1 - u) + n11 * u) * v);
  };
}
const smooth = (a, b, x) => { const t = Math.min(Math.max((x - a) / (b - a), 0), 1); return t * t * (3 - 2 * t); };
function generateDetail(S = 512) {
  const rng = mulberry32(99), n1 = makeNoise(rng), n2 = makeNoise(rng);
  const h = new Float32Array(S * S);
  for (let j = 0; j < S; j++) for (let i = 0; i < S; i++) {
    // 3 octaves only (~11, 5.6, 2.8 cm): finer chop just aliases into caustic sparkle
    const u = i / S, v = j / S; let s = 0, a = 1, f = 4;
    for (let o = 0; o < 3; o++) { const nn = n1(u * f, v * f, f, f); s += a * (o < 1 ? nn : (1 - Math.abs(nn)) * 0.9 - 0.45); a *= 0.42; f *= 2; }
    h[j * S + i] = s;
  }
  // worley foam cells, two scales
  const worley = (cells, seed) => {
    const r = mulberry32(seed), pts = new Float32Array(cells * cells * 2);
    for (let k = 0; k < cells * cells; k++) { pts[k * 2] = r(); pts[k * 2 + 1] = r(); }
    const out = new Float32Array(S * S);
    for (let j = 0; j < S; j++) for (let i = 0; i < S; i++) {
      const x = i / S * cells, y = j / S * cells, cx = Math.floor(x), cy = Math.floor(y);
      let f1 = 9, f2 = 9;
      for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) {
        const gx = cx + ox, gy = cy + oy, wx = (gx % cells + cells) % cells, wy = (gy % cells + cells) % cells, k = wy * cells + wx;
        const dx = gx + pts[k * 2] - x, dy = gy + pts[k * 2 + 1] - y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < f1) { f2 = f1; f1 = d; } else if (d < f2) f2 = d;
      }
      out[j * S + i] = f2 - f1;
    }
    return out;
  };
  // zero mean, unit variance: the height doubles as the (mass-neutral) boil source
  let hm = 0, hv = 0; for (let k = 0; k < S * S; k++) hm += h[k]; hm /= S * S;
  for (let k = 0; k < S * S; k++) { h[k] -= hm; hv += h[k] * h[k]; } hv = 1 / Math.sqrt(hv / (S * S));
  for (let k = 0; k < S * S; k++) h[k] *= hv;
  const w1 = worley(14, 5), w2 = worley(38, 6);
  let gs = 0; const g = new Float32Array(S * S * 2);
  for (let j = 0; j < S; j++) for (let i = 0; i < S; i++) {
    const ip = (i + 1) % S, im = (i - 1 + S) % S, jp = (j + 1) % S, jm = (j - 1 + S) % S;
    const gx = (h[j * S + ip] - h[j * S + im]) * S / 2, gy = (h[jp * S + i] - h[jm * S + i]) * S / 2;
    g[(j * S + i) * 2] = gx; g[(j * S + i) * 2 + 1] = gy; gs += gx * gx + gy * gy;
  }
  const gn = 1 / Math.sqrt(gs / (S * S));
  const data = new Uint16Array(S * S * 4), toH = THREE.DataUtils.toHalfFloat;
  for (let k = 0; k < S * S; k++) {
    const foam = 0.55 * (1 - smooth(0.0, 0.16, w1[k])) + 0.45 * (1 - smooth(0.0, 0.2, w2[k])) + 0.15 * n2((k % S) / S * 40, Math.floor(k / S) / S * 40, 40, 40);
    data[k * 4] = toH(h[k]); data[k * 4 + 1] = toH(g[k * 2] * gn); data[k * 4 + 2] = toH(g[k * 2 + 1] * gn); data[k * 4 + 3] = toH(foam);
  }
  const t = new THREE.DataTexture(data, S, S, THREE.RGBAFormat, THREE.HalfFloatType);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
  t.generateMipmaps = true; t.needsUpdate = true;
  return t;
}

const macroTex = terrain.tex;
const detTex = generateDetail();
const uDt = uniform(1 / 60 / params.substeps), uDtF = uniform(1 / 60);
const uSlope = uniform(params.flow), uManning = uniform(params.manning);
const uMouse = uniform(new THREE.Vector4(0, 0, 0, 6)), uMouseVel = uniform(new THREE.Vector2());
const uResetA = uniform(0), uResetB = uniform(0), uOffA = uniform(new THREE.Vector2()), uOffB = uniform(new THREE.Vector2());
const uWA = uniform(0.5), uWB = uniform(0.5);
const uExcite = uniform(params.excitation), uEmit = uniform(params.emission), uCaustic = uniform(params.caustics), uDetail = uniform(params.detail);
const uDispMean = uniform(packMean);
const uVort = uniform(params.vorticity), uBoil = uniform(params.boils);
const uFoam = uniform(new THREE.Vector3(1.7, 1.35, 1.5));   // foam sources: breaking crests, convergence lines, rock impact
const uMoonDir = uniform(new THREE.Vector3(-0.35, 0.82, 0.45).normalize());
const uMoonCol = uniform(new THREE.Color(0.32, 0.42, 0.62));

// ============================================================================================
//  Shared TSL helpers: macro terrain fetch (manual bilinear on f32), full-detail bed height
// ============================================================================================
const macroAt = (xz) => texture(macroTex, vec2(xz.x.div(TW), xz.y.div(TL))).level(0);
const microAmp = (rock) => float(MICRO_AMP).mul(float(1).sub(rock.mul(0.82)));
const bedHeight = (xz, lod) => {
  const m = macroAt(xz);
  const d = texture(packTex, xz.div(MICRO_TILE)).level(lod).r;
  return m.x.add(d.sub(uDispMean).mul(microAmp(m.w)));
};
const simUV = (xz) => vec2(xz.x.sub(SX0).div(SW), xz.y.div(SL));
const glowColor = (g) => mix(vec3(0.0, 0.16, 1.0), vec3(0.08, 1.0, 0.92), smoothstep(0.0, 1.6, g));
// colour of the light leaving the river (caustic-lit bed + emission): teal-cyan, bluer when faint
const riverLightColor = (irr) => mix(vec3(0.06, 0.5, 1.0), vec3(0.12, 0.92, 0.95), smoothstep(0.0, 0.5, irr));

// ============================================================================================
//  GPU state
// ============================================================================================
const hB = [instancedArray(N, 'float'), instancedArray(N, 'float')];   // water depth
const vB = [instancedArray(N, 'vec2'), instancedArray(N, 'vec2')];     // staggered u (east face), w (north face)
const sB = instancedArray(N, 'float');                                 // positivity scale
const wB = instancedArray(N, 'float');                                 // vorticity at NE cell corner
const bedB = instancedArray(N, 'float');                               // sim bed height
const qB = [instancedArray(N, 'vec4'), instancedArray(N, 'vec4')];     // glow, foam, turbulence, wetness
const qT = instancedArray(N, 'vec4');                                  // MacCormack intermediate
const dB = [instancedArray(N, 'vec4'), instancedArray(N, 'vec4')];     // advected texture-space displacement, 2 phases
const lowA = instancedArray(LX * LZ, 'float'), lowB = instancedArray(LX * LZ, 'float'), lowC = instancedArray(LX * LZ, 'float');

function storageTex(w, h) {
  const t = new THREE.StorageTexture(w, h);
  t.type = THREE.HalfFloatType; t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false;
  t.wrapS = THREE.ClampToEdgeWrapping; t.wrapT = THREE.RepeatWrapping;
  return t;
}
const texA = storageTex(NX, NZ);  // eta, d(eta)/dx, d(eta)/dz, depth
const texB = storageTex(NX, NZ);  // vx, vz, foam, glow
const texC = storageTex(NX, NZ);  // advected displacement A.xy, B.xy
const texD = storageTex(NX, NZ);  // turbulence, wetness, strain, -
const texL = storageTex(LX, LZ);  // blurred luminance: near, wide

const iNX = int(NX), iNZ = int(NZ), one = int(1);
const IDX = (i, j) => j.add(iNZ).mod(iNZ).mul(iNX).add(i.add(iNX).mod(iNX));
const cellIJ = () => { const id = int(instanceIndex); return [id.mod(iNX), id.div(iNX), id]; };
function bilin(get, px, pz) {
  const fx = floor(px), fz = floor(pz), tx = px.sub(fx), tz = pz.sub(fz);
  const i0 = int(fx), j0 = int(fz), i1 = i0.add(one), j1 = j0.add(one);
  return mix(mix(get(IDX(i0, j0)), get(IDX(i1, j0)), tx), mix(get(IDX(i0, j1)), get(IDX(i1, j1)), tx), tz);
}
// monotone Catmull-Rom: sharp momentum advection without new extrema
const crW = (t) => { const t2 = t.mul(t), t3 = t2.mul(t); return [t2.sub(t.mul(0.5)).sub(t3.mul(0.5)), t3.mul(1.5).sub(t2.mul(2.5)).add(1.0), t3.mul(-1.5).add(t2.mul(2.0)).add(t.mul(0.5)), t3.mul(0.5).sub(t2.mul(0.5))]; };
function cubic(get, px, pz) {
  const fx = floor(px), fz = floor(pz), tx = px.sub(fx), tz = pz.sub(fz);
  const i0 = int(fx), j0 = int(fz), wx = crW(tx), wz = crW(tz);
  let acc = null, lo = null, hi = null;
  for (let dj = -1; dj <= 2; dj++) {
    let row = null;
    for (let di = -1; di <= 2; di++) {
      const v = get(IDX(i0.add(int(di)), j0.add(int(dj))));
      row = row ? row.add(v.mul(wx[di + 1])) : v.mul(wx[di + 1]);
      if ((di === 0 || di === 1) && (dj === 0 || dj === 1)) { lo = lo ? min(lo, v) : v; hi = hi ? max(hi, v) : v; }
    }
    acc = acc ? acc.add(row.mul(wz[dj + 1])) : row.mul(wz[dj + 1]);
  }
  return clamp(acc, lo, hi);
}
const Uget = (V) => (idx) => V.element(idx).x;
const Wget = (V) => (idx) => V.element(idx).y;
const velAt = (V, px, pz) => vec2(bilin(Uget(V), px.sub(0.5), pz), bilin(Wget(V), px, pz.sub(0.5)));
function backtrace(V, fi, fj, dtc) {   // RK2 in cell units
  const v1 = velAt(V, fi, fj);
  const mid = vec2(fi, fj).sub(v1.mul(dtc.mul(0.5)));
  const v2 = velAt(V, mid.x, mid.y);
  return vec2(fi, fj).sub(v2.mul(dtc));
}
// periodic-aware gaussian falloff around the stirring cursor (cell units)
const mouseFall = (px, pz) => {
  const dx = px.sub(uMouse.x), dz0 = pz.sub(uMouse.y), dz = dz0.sub(float(NZ).mul(floor(dz0.div(NZ).add(0.5))));
  return exp(dx.mul(dx).add(dz.mul(dz)).negate().div(uMouse.w.mul(uMouse.w))).mul(uMouse.z);
};

// ---------------------------------------------------------------------------------- init
const bedInit = Fn(() => {
  const [i, j, c] = cellIJ();
  const xz = vec2(float(i).add(0.5).mul(DX).add(SX0), float(j).add(0.5).mul(DX));
  bedB.element(c).assign(bedHeight(xz, float(Math.log2(DX / (MICRO_TILE / 4096)))));
})().compute(N);

const waterInit = Fn(() => {
  const [, , c] = cellIJ();
  const h = max(float(WATER_LEVEL).sub(bedB.element(c)), 0.0);
  const v = vec2(0.0, select(h.greaterThan(0.01), float(0.5), float(0.0)));
  const q = vec4(0.0, 0.0, 0.0, select(h.greaterThan(0.0), float(1.0), float(0.0)));
  hB[0].element(c).assign(h); hB[1].element(c).assign(h);
  vB[0].element(c).assign(v); vB[1].element(c).assign(v);
  qB[0].element(c).assign(q); qB[1].element(c).assign(q);
})().compute(N);
const fieldInit = Fn(() => {   // separate pass: WebGPU allows 8 storage buffers per stage
  const [, , c] = cellIJ();
  dB[0].element(c).assign(vec4(0.0)); dB[1].element(c).assign(vec4(0.0));
})().compute(N);

// ---------------------------------------------------------------------------------- shallow water
// face velocity update: pressure gradient, wet/dry walls, Manning friction, body force
function faceVel(vAdv, vPerp, hA, hBb, bA, bBb, accel) {
  const eA = bA.add(hA), eB = bBb.add(hBb);
  const wetA = hA.greaterThan(H_EPS), wetB = hBb.greaterThan(H_EPS);
  const blocked = wetA.not().and(wetB.not()).or(wetA.not().and(bA.greaterThan(eB))).or(wetB.not().and(bBb.greaterThan(eA)));
  const hf = max(hA.add(hBb).mul(0.5), 0.0004);
  const v0 = vAdv.sub(uDt.mul(G / DX).mul(eB.sub(eA))).add(accel.mul(uDt));
  const sp = sqrt(v0.mul(v0).add(vPerp.mul(vPerp)));
  const fric = uDt.mul(G).mul(uManning).mul(uManning).mul(sp).div(pow(hf, 1.3333));
  const v1 = v0.div(fric.add(1.0)).mul(smoothstep(0.0, 0.003, hf));
  return select(blocked, float(0.0), clamp(v1, -VMAX, VMAX));
}
function makeVelPass(p) {
  const V = vB[p], H = hB[p], OUT = vB[1 - p], U = Uget(V), W = Wget(V);
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const ip = i.add(one), im = i.sub(one), jp = j.add(one), jm = j.sub(one);
    const fi = float(i), fj = float(j), dtdx = uDt.div(DX);
    const vC = V.element(c);
    const wAvg = W(c).add(W(IDX(i, jm))).add(W(IDX(ip, j))).add(W(IDX(ip, jm))).mul(0.25);
    const uAvg = U(c).add(U(IDX(im, j))).add(U(IDX(i, jp))).add(U(IDX(im, jp))).mul(0.25);
    const uAdv = cubic(U, fi.sub(vC.x.mul(dtdx)), fj.sub(wAvg.mul(dtdx)));
    const wAdv = cubic(W, fi.sub(uAvg.mul(dtdx)), fj.sub(vC.y.mul(dtdx)));
    const hC = H.element(c), hE = H.element(IDX(ip, j)), hN = H.element(IDX(i, jp));
    const bC = bedB.element(c), bE = bedB.element(IDX(ip, j)), bN = bedB.element(IDX(i, jp));
    // vorticity confinement (corner vorticity from previous substep) keeps eddies from dissipating numerically
    const om = (a, b) => wB.element(IDX(a, b)), aom = (a, b) => abs(om(a, b));
    const omU = om(i, j).add(om(i, jm)).mul(0.5);
    const gU = vec2(aom(ip, j).add(aom(ip, jm)).sub(aom(im, j)).sub(aom(im, jm)).mul(0.25), aom(i, j).sub(aom(i, jm)));
    const omW = om(i, j).add(om(im, j)).mul(0.5);
    const gW = vec2(aom(i, j).sub(aom(im, j)), aom(i, jp).add(aom(im, jp)).sub(aom(i, jm)).sub(aom(im, jm)).mul(0.25));
    const wetC = smoothstep(0.01, 0.04, hC);
    const vcU = gU.y.div(length(gU).add(1e-5)).mul(omU).mul(uVort).mul(DX).mul(wetC);
    const vcW = gW.x.div(length(gW).add(1e-5)).mul(omW).mul(uVort).mul(-DX).mul(wetC);
    // turbulent boils: upwelling modelled as a divergent forcing  a = k * turb * grad(phi), where phi is a
    // noise potential advected with the flow (mass-neutral since the depth update stays in flux form)
    const boilAt = (x, z, comp) => {
      const uvf = vec2(x.div(NX), z.div(NZ)), xz = vec2(x.mul(DX).add(SX0), z.mul(DX));
      const Dd = texture(texC, uvf).level(0), turb = texture(texD, uvf).level(0).x;
      const gA = texture(detTex, xz.add(Dd.xy).mul(DET_FREQ * 0.3)).level(0), gB = texture(detTex, xz.add(Dd.zw).mul(DET_FREQ * 0.3)).level(0);
      return gA[comp].mul(uWA).add(gB[comp].mul(uWB)).mul(turb).mul(uBoil);
    };
    const bU = boilAt(fi.add(1.0), fj.add(0.5), 'y'), bW = boilAt(fi.add(0.5), fj.add(1.0), 'z');
    const fu = mouseFall(fi.add(0.5), fj), fw = mouseFall(fi, fj.add(0.5));
    const aU = uMouseVel.x.sub(uAdv).mul(fu).mul(25.0).add(vcU).add(bU.mul(wetC));
    const aW = uMouseVel.y.sub(wAdv).mul(fw).mul(25.0).add(uSlope.mul(G)).add(vcW).add(bW.mul(wetC));
    OUT.element(c).assign(vec2(faceVel(uAdv, wAvg, hC, hE, bC, bE, aU), faceVel(wAdv, uAvg, hC, hN, bC, bN, aW)));
  })().compute(N);
}
function makeScalePass(p) {
  const V = vB[1 - p];
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const v = V.element(c), uW = V.element(IDX(i.sub(one), j)).x, wS = V.element(IDX(i, j.sub(one))).y;
    const out = max(v.x, 0.0).add(max(uW.negate(), 0.0)).add(max(v.y, 0.0)).add(max(wS.negate(), 0.0));
    sB.element(c).assign(min(float(1.0), float(1.0).div(out.mul(uDt.div(DX)).add(1e-6))));
    const wE = V.element(IDX(i.add(one), j)).y, uN = V.element(IDX(i, j.add(one))).x;
    wB.element(c).assign(wE.sub(v.y).sub(uN.sub(v.x)).div(DX));
  })().compute(N);
}
function makeHeightPass(p) {
  const H = hB[p], V = vB[1 - p], OUT = hB[1 - p];
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const iE = IDX(i.add(one), j), iW = IDX(i.sub(one), j), iN = IDX(i, j.add(one)), iS = IDX(i, j.sub(one));
    const hs = (k) => H.element(k).mul(sB.element(k));
    const hsC = hs(c), hsE = hs(iE), hsW = hs(iW), hsN = hs(iN), hsS = hs(iS);
    const vC = V.element(c), uE = vC.x, wN = vC.y, uW = V.element(iW).x, wS = V.element(iS).y;
    const FE = uE.mul(select(uE.greaterThan(0.0), hsC, hsE));
    const FW = uW.mul(select(uW.greaterThan(0.0), hsW, hsC));
    const FN = wN.mul(select(wN.greaterThan(0.0), hsC, hsN));
    const FS = wS.mul(select(wS.greaterThan(0.0), hsS, hsC));
    const hn = H.element(c).sub(uDt.div(DX).mul(FE.sub(FW).add(FN).sub(FS)));
    OUT.element(c).assign(max(hn, 0.0));
  })().compute(N);
}

// ---------------------------------------------------------------------------------- derived flow quantities
function flowMetrics(V, H, i, j, c) {
  const U = Uget(V), W = Wget(V), ip = i.add(one), im = i.sub(one), jp = j.add(one), jm = j.sub(one);
  const ux = U(c).sub(U(IDX(im, j))).div(DX), wz = W(c).sub(W(IDX(i, jm))).div(DX);
  const ucN = U(IDX(i, jp)).add(U(IDX(im, jp))), ucS = U(IDX(i, jm)).add(U(IDX(im, jm)));
  const wcE = W(IDX(ip, j)).add(W(IDX(ip, jm))), wcW = W(IDX(im, j)).add(W(IDX(im, jm)));
  const uz = ucN.sub(ucS).div(4 * DX), wx = wcE.sub(wcW).div(4 * DX);
  const sh = uz.add(wx);
  const strain = sqrt(ux.mul(ux).add(wz.mul(wz)).mul(2.0).add(sh.mul(sh)));
  const div = ux.add(wz);
  const hC = H.element(c), eC = bedB.element(c).add(hC);
  const etaN = (k) => { const hh = H.element(k); return select(hh.greaterThan(H_EPS), bedB.element(k).add(hh), eC); };
  const dryN = (k) => select(H.element(k).greaterThan(H_EPS), float(0.0), float(1.0));
  const gx = etaN(IDX(ip, j)).sub(etaN(IDX(im, j))).div(2 * DX);
  const gz = etaN(IDX(i, jp)).sub(etaN(IDX(i, jm))).div(2 * DX);
  const shore = dryN(IDX(ip, j)).add(dryN(IDX(im, j))).add(dryN(IDX(i, jp))).add(dryN(IDX(i, jm))).mul(0.25);
  const vc = vec2(U(c).add(U(IDX(im, j))), W(c).add(W(IDX(i, jm)))).mul(0.5);
  return { strain, div, gx, gz, hC, eC, shore, vc };
}

// ---------------------------------------------------------------------------------- MacCormack advection of glow / foam / turbulence
function makeScalarA(p, q) {
  const V = vB[p], Q = qB[q], D = dB[q], DO = dB[1 - q];
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const fi = float(i), fj = float(j);
    const bp = backtrace(V, fi, fj, uDtF.div(DX));
    qT.element(c).assign(bilin((k) => Q.element(k), bp.x, bp.y));
    const off = bp.sub(vec2(fi, fj)).mul(DX);
    const d = bilin((k) => D.element(k), bp.x, bp.y).add(vec4(off, off));
    DO.element(c).assign(vec4(select(uResetA.greaterThan(0.5), uOffA, d.xy), select(uResetB.greaterThan(0.5), uOffB, d.zw)));
  })().compute(N);
}
function makeScalarB(p, q) {
  const V = vB[p], H = hB[p], Q = qB[q], QO = qB[1 - q];
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const fi = float(i), fj = float(j), dtc = uDtF.div(DX);
    const qf = qT.element(c);
    const fwd = vec2(fi, fj).add(velAt(V, fi, fj).mul(dtc));
    const qr = bilin((k) => qT.element(k), fwd.x, fwd.y);
    const bp = backtrace(V, fi, fj, dtc);
    const i0 = int(floor(bp.x)), j0 = int(floor(bp.y));
    const a = Q.element(IDX(i0, j0)), b = Q.element(IDX(i0.add(one), j0)), cc = Q.element(IDX(i0, j0.add(one))), dd = Q.element(IDX(i0.add(one), j0.add(one)));
    const qOld = Q.element(c);
    const qn = clamp(qf.add(qOld.sub(qr).mul(0.5)), min(min(a, b), min(cc, dd)), max(max(a, b), max(cc, dd)));
    const m = flowMetrics(V, H, i, j, c);
    const slope = length(vec2(m.gx, m.gz)), speed = length(m.vc);
    const wet = m.hC.greaterThan(0.0015);
    const mf = mouseFall(fi, fj);
    const turbT = clamp(m.strain.mul(0.045).add(slope.mul(1.4)).add(mf), 0.0, 1.0);
    const turb = mix(qn.z, turbT, float(1.0).sub(exp(uDtF.negate().div(0.35))));
    // foam: breaking (steep surface at speed), strong convergence lines, water slamming into dry rock
    const foamSrc = smoothstep(0.55, 1.25, slope).mul(smoothstep(0.6, 1.6, speed)).mul(uFoam.x)
      .add(smoothstep(25.0, 80.0, m.div.negate()).mul(smoothstep(0.6, 1.6, speed)).mul(uFoam.y))
      .add(m.shore.mul(smoothstep(0.9, 1.9, speed)).mul(uFoam.z))
      .add(mf.mul(6.0));
    const foam = select(wet, qn.y.mul(exp(uDtF.negate().div(6.0))).add(foamSrc.mul(uDtF)), qn.y.mul(0.85));
    // dinoflagellates flash when shear stress exceeds a threshold, then fade
    const glowSrc = smoothstep(12.0, 50.0, m.strain).mul(2.2).add(foamSrc.mul(1.0)).add(mf.mul(12.0)).mul(uExcite);
    const glow = select(wet, qn.x.mul(exp(uDtF.negate().div(0.9))).add(glowSrc.mul(uDtF)), qn.x.mul(0.8));
    const wetness = select(wet, float(1.0), max(qOld.w.sub(uDtF.div(30.0)), 0.0));
    QO.element(c).assign(vec4(min(glow, 4.0), min(foam, 2.0), turb, wetness));
  })().compute(N);
}

// ---------------------------------------------------------------------------------- export to filterable render textures
function makeExport(p, q) {
  const V = vB[p], H = hB[p], Q = qB[q], D = dB[q];
  return Fn(() => {
    const [i, j, c] = cellIJ();
    const m = flowMetrics(V, H, i, j, c);
    const qc = Q.element(c);
    const wet = m.hC.greaterThan(H_EPS);
    const coord = uvec2(uint(i), uint(j));
    textureStore(texA, coord, vec4(select(wet, m.eC, bedB.element(c).sub(0.03)), m.gx, m.gz, m.hC));
    textureStore(texB, coord, vec4(m.vc, qc.y, qc.x));
    textureStore(texC, coord, D.element(c));
    textureStore(texD, coord, vec4(qc.z, qc.w, m.strain, 0.0));
  })().compute(N);
}

// ---------------------------------------------------------------------------------- low-res luminance (area light on bed & rocks)
const iLX = int(LX), iLZ = int(LZ);
const LIDX = (a, b) => b.add(iLZ).mod(iLZ).mul(iLX).add(clamp(a, int(0), int(LX - 1)));
function makeLowDown(p, q) {
  const H = hB[p], Q = qB[q];
  return Fn(() => {
    const id = int(instanceIndex), a = id.mod(iLX), b = id.div(iLX);
    const s = float(0.0).toVar();
    for (let oy = 0; oy < 4; oy++) for (let ox = 0; ox < 4; ox++) {
      const k = IDX(a.mul(int(4)).add(int(ox)), b.mul(int(4)).add(int(oy)));
      s.addAssign(Q.element(k).x.mul(0.35).add(0.06).mul(min(H.element(k), 0.12).div(0.12)));
    }
    lowA.element(id).assign(s.div(16.0));
  })().compute(LX * LZ);
}
const GW = [0.034, 0.072, 0.124, 0.168, 0.194, 0.168, 0.124, 0.072, 0.034, 0.010];
function makeBlur(src, dst, dirX, stride, toTex) {
  return Fn(() => {
    const id = int(instanceIndex), a = id.mod(iLX), b = id.div(iLX);
    const s = float(0.0).toVar();
    for (let k = -4; k <= 4; k++) {
      const o = int(k * stride);
      s.addAssign(src.element(dirX ? LIDX(a.add(o), b) : LIDX(a, b.add(o))).mul(GW[k + 4]));
    }
    if (toTex) textureStore(texL, uvec2(uint(a), uint(b)), vec4(lowC.element(id), s, 0.0, 1.0));
    else dst.element(id).assign(s);
  })().compute(LX * LZ);
}

const velPass = [makeVelPass(0), makeVelPass(1)];
const scalePass = [makeScalePass(0), makeScalePass(1)];
const heightPass = [makeHeightPass(0), makeHeightPass(1)];
const scalarA = [[makeScalarA(0, 0), makeScalarA(0, 1)], [makeScalarA(1, 0), makeScalarA(1, 1)]];
const scalarB = [[makeScalarB(0, 0), makeScalarB(0, 1)], [makeScalarB(1, 0), makeScalarB(1, 1)]];
const exportPass = [[makeExport(0, 0), makeExport(0, 1)], [makeExport(1, 0), makeExport(1, 1)]];
const lowDown = [[makeLowDown(0, 0), makeLowDown(0, 1)], [makeLowDown(1, 0), makeLowDown(1, 1)]];
const blurPasses = [makeBlur(lowA, lowB, true, 1), makeBlur(lowB, lowC, false, 1), makeBlur(lowC, lowB, true, 3), makeBlur(lowB, null, false, 3, true)];

// ---------------------------------------------------------------------------------- river as an area light
// Emitted radiance of the water surface (luminous water column + caustic light leaking back out), over the
// whole terrain tile at 4 cm, blurred at ~8 / 25 / 75 cm. Rocks pick the radius matching their height above
// the water (a cone-traced approximation of the area-light integral) and its gradient gives light direction.
const FX = 256, FZ = 256, FN = FX * FZ;   // 4 cm cells over TW x TL
const eDown = instancedArray(FN, 'float'), eTmp = instancedArray(FN, 'float'), eL0 = instancedArray(FN, 'float'), eL1 = instancedArray(FN, 'float');
const texE = storageTex(FX, FZ);
const iFX = int(FX), iFZ = int(FZ);
const FIDX = (a, b) => b.add(iFZ).mod(iFZ).mul(iFX).add(clamp(a, int(0), int(FX - 1)));
function makeFieldDown(p, q) {
  const H = hB[p], Q = qB[q];
  return Fn(() => {
    const id = int(instanceIndex), a = id.mod(iFX), b = id.div(iFX);
    const i0 = a.mul(int(4)).sub(int(Math.round(SX0 / DX))), j0 = b.mul(int(4));
    const s = float(0.0).toVar();
    for (let oy = 0; oy < 4; oy++) for (let ox = 0; ox < 4; ox++) {
      const i = i0.add(int(ox)), k = IDX(i, j0.add(int(oy)));
      const inside = i.greaterThanEqual(int(0)).and(i.lessThan(iNX));
      const radiance = Q.element(k).x.mul(0.5).add(0.25).mul(smoothstep(0.0, 0.06, H.element(k)));
      s.addAssign(select(inside, radiance, float(0.0)));
    }
    eDown.element(id).assign(s.div(16.0));
  })().compute(FN);
}
function makeFieldBlur(src, dst, dirX, stride, toTex) {
  return Fn(() => {
    const id = int(instanceIndex), a = id.mod(iFX), b = id.div(iFX);
    const s = float(0.0).toVar();
    for (let k = -4; k <= 4; k++) {
      const o = int(k * stride);
      s.addAssign(src.element(dirX ? FIDX(a.add(o), b) : FIDX(a, b.add(o))).mul(GW[k + 4]));
    }
    if (toTex) textureStore(texE, uvec2(uint(a), uint(b)), vec4(eL0.element(id), eL1.element(id), s, 1.0));
    else dst.element(id).assign(s);
  })().compute(FN);
}
const fieldDown = [[makeFieldDown(0, 0), makeFieldDown(0, 1)], [makeFieldDown(1, 0), makeFieldDown(1, 1)]];
const fieldBlur = [
  makeFieldBlur(eDown, eTmp, true, 1), makeFieldBlur(eTmp, eL0, false, 1),
  makeFieldBlur(eL0, eTmp, true, 3), makeFieldBlur(eTmp, eL1, false, 3),
  makeFieldBlur(eL1, eTmp, true, 9), makeFieldBlur(eTmp, null, false, 9, true),
];

let P = 0, Qp = 0, simTime = 0, lastPhase = 0;
const T_RESET = 0.45;  // short enough that shear never smears the advected chop into marbled streaks
function simFrame() {
  const sub = params.substeps;
  uDt.value = 1 / 60 / sub;
  for (let s = 0; s < sub; s++) {
    renderer.compute(velPass[P]); renderer.compute(scalePass[P]); renderer.compute(heightPass[P]);
    P = 1 - P;
  }
  // two-phase texture advection (Neyret): reset each layer when its weight is zero
  simTime += 1 / 60;
  const ph = (simTime / T_RESET) % 1, phB = (ph + 0.5) % 1;
  uResetA.value = ph < lastPhase ? 1 : 0;
  uResetB.value = (phB < ((lastPhase + 0.5) % 1)) ? 1 : 0;
  if (uResetA.value) uOffA.value.set(Math.random() * 20, Math.random() * 20);
  if (uResetB.value) uOffB.value.set(Math.random() * 20, Math.random() * 20);
  lastPhase = ph;
  uWA.value = 1 - Math.abs(2 * ph - 1); uWB.value = 1 - Math.abs(2 * phB - 1);
  renderer.compute(scalarA[P][Qp]); renderer.compute(scalarB[P][Qp]); Qp = 1 - Qp;
  renderer.compute(exportPass[P][Qp]);
  renderer.compute(lowDown[P][Qp]);
  for (const b of blurPasses) renderer.compute(b);
  renderer.compute(fieldDown[P][Qp]);
  for (const b of fieldBlur) renderer.compute(b);
}

// ============================================================================================
//  Flow-advected sub-grid detail (shared by caustic & water shaders)
// ============================================================================================
function detailSample(xz, C, vertex) {
  const pA = xz.add(C.xy).mul(DET_FREQ), pB = xz.add(C.zw).add(vec2(0.37, 0.71)).mul(DET_FREQ);
  const sA = vertex ? texture(detTex, pA).level(0) : texture(detTex, pA);
  const sB = vertex ? texture(detTex, pB).level(0) : texture(detTex, pB);
  const nrm = inverseSqrt(uWA.mul(uWA).add(uWB.mul(uWB)));
  return { g: sA.yz.mul(uWA).add(sB.yz.mul(uWB)).mul(nrm), foam: sA.w.mul(uWA).add(sB.w.mul(uWB)) };
}
const detailAmp = (turb, h) => uDetail.mul(0.09).mul(mix(0.3, 1.0, turb)).mul(smoothstep(0.0, 0.012, h));

// ============================================================================================
//  Caustics: refract a dense grid through the simulated surface onto the bed and rasterise it
//  additively; intensity = undistorted area / refracted area (exact per-triangle Jacobian).
//  Light source = the luminescent surface film itself (scaled by local excitation).
// ============================================================================================
const causticRT = new THREE.RenderTarget(CAUS_RT_X, CAUS_RT_Z, { type: THREE.HalfFloatType, depthBuffer: false });
causticRT.texture.minFilter = causticRT.texture.magFilter = THREE.LinearFilter;
causticRT.texture.wrapS = THREE.ClampToEdgeWrapping; causticRT.texture.wrapT = THREE.RepeatWrapping;
const uCausFlip = uniform(-1);   // WebGPU render targets: NDC +y is texture row 0
function causticGeometry() {
  const margin = Math.round(CAUS_Z * 0.03), nx = CAUS_X + 1, nz = CAUS_Z + 1 + 2 * margin;
  const pos = new Float32Array(nx * nz * 3);
  for (let j = 0; j < nz; j++) for (let i = 0; i < nx; i++) {
    const k = (j * nx + i) * 3; pos[k] = SX0 + (i / CAUS_X) * SW; pos[k + 1] = 0; pos[k + 2] = ((j - margin) / CAUS_Z) * SL;
  }
  const idx = new Uint32Array((nx - 1) * (nz - 1) * 6); let o = 0;
  for (let j = 0; j < nz - 1; j++) for (let i = 0; i < nx - 1; i++) { const a = j * nx + i, b = a + 1, c = a + nx, d = c + 1; idx[o++] = a; idx[o++] = c; idx[o++] = b; idx[o++] = b; idx[o++] = c; idx[o++] = d; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e4); return g;
}
function causticMaterial(ior, mask) {
  const m = new THREE.MeshBasicNodeMaterial({ transparent: true, depthTest: false, depthWrite: false, side: THREE.DoubleSide });
  m.blending = THREE.AdditiveBlending;
  const P0 = positionGeometry.xz, uvS = simUV(P0);
  const A = texture(texA, uvS).level(0), B = texture(texB, uvS).level(0), C = texture(texC, uvS).level(0), D4 = texture(texD, uvS).level(0);
  const det = detailSample(P0, C, true), amp = detailAmp(D4.x, A.w);
  const Nn = normalize(vec3(A.y.add(det.g.x.mul(amp)).negate(), 1.0, A.z.add(det.g.y.mul(amp)).negate()));
  const L = vec3(0.04, -1.0, 0.025).normalize();
  const T = refract(L, Nn, 1.0 / ior);
  const S = vec3(P0.x, A.x, P0.y);
  const ty = max(T.y.negate(), 0.2);
  const bedAt = (xz) => { const a = texture(texA, simUV(xz)).level(0); return a.x.sub(a.w); };
  const t0 = A.w.div(ty);
  const t1 = max(S.y.sub(bedAt(S.xz.add(T.xz.mul(t0)))), 0.0).div(ty);
  const t2 = max(S.y.sub(bedAt(S.xz.add(T.xz.mul(t1)))), 0.0).div(ty);
  const Q = S.xz.add(T.xz.mul(t2));
  const Q0 = P0.add(L.xz.mul(A.w.div(L.y.negate())));
  // emitted light scales with the luminous water column above (thin films barely glow)
  const att = exp(t2.mul(-0.35)).mul(B.w.mul(0.4).add(0.3)).mul(smoothstep(0.0, 0.07, A.w));
  const vQ = Q.toVarying(), vQ0 = Q0.toVarying(), vAtt = att.toVarying();
  const uvQ = simUV(Q);
  m.vertexNode = vec4(uvQ.x.mul(2).sub(1), uvQ.y.mul(2).sub(1).mul(uCausFlip), 0.0, 1.0);
  m.colorNode = Fn(() => {
    const qx = dFdx(vQ), qy = dFdy(vQ), px = dFdx(vQ0), py = dFdy(vQ0);
    const a1 = abs(qx.x.mul(qy.y).sub(qx.y.mul(qy.x))), a0 = abs(px.x.mul(py.y).sub(px.y.mul(py.x)));
    const I = min(a0.div(max(a1, 1e-12)), 14.0).mul(vAtt);
    return vec4(vec3(...mask).mul(I), 1.0);
  })();
  return m;
}
const causticScene = new THREE.Scene();
const causticCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const cGeo = causticGeometry();
const causticMeshes = [
  new THREE.Mesh(cGeo, causticMaterial(1.331, [1, 0, 0])),
  new THREE.Mesh(cGeo, causticMaterial(1.334, [0, 1, 0])),
  new THREE.Mesh(cGeo, causticMaterial(1.338, [0, 0, 1])),
  new THREE.Mesh(cGeo, causticMaterial(1.334, [1, 1, 1])),
];
for (const m of causticMeshes) { m.frustumCulled = false; causticScene.add(m); }
function setDispersion(on) { causticMeshes.forEach((m, k) => { m.visible = on ? k < 3 : k === 3; }); }
setDispersion(params.dispersion);

// ============================================================================================
//  Chunked LOD geometry (instanced, skirted) for terrain and water
// ============================================================================================
const CHUNK = 1.28;
function gridGeometry(seg) {
  const n = seg + 3, pos = new Float32Array(n * n * 3), nor = new Float32Array(n * n * 3), sk = new Float32Array(n * n);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const k = j * n + i, ii = Math.min(Math.max(i - 1, 0), seg), jj = Math.min(Math.max(j - 1, 0), seg);
    pos[k * 3] = ii / seg * CHUNK; pos[k * 3 + 2] = jj / seg * CHUNK; nor[k * 3 + 1] = 1;
    sk[k] = (i === 0 || j === 0 || i === n - 1 || j === n - 1) ? 1 : 0;
  }
  const idx = new Uint32Array((n - 1) * (n - 1) * 6); let o = 0;
  for (let j = 0; j < n - 1; j++) for (let i = 0; i < n - 1; i++) { const a = j * n + i, b = a + 1, c = a + n, d = c + 1; idx[o++] = a; idx[o++] = c; idx[o++] = b; idx[o++] = b; idx[o++] = c; idx[o++] = d; }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  g.setAttribute('skirt', new THREE.BufferAttribute(sk, 1)); g.setIndex(new THREE.BufferAttribute(idx, 1));
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e4); return g;
}
// one instanced draw per LOD level; per-instance chunk origin comes from a storage buffer
class ChunkSet {
  constructor(scene, x0, cols, segs, dists, makeMat, maxRows) {
    Object.assign(this, { x0, cols, dists });
    const max = cols * maxRows;
    this.meshes = segs.map((s, l) => {
      const offsets = instancedArray(max, 'vec4');
      const m = new THREE.Mesh(gridGeometry(s), makeMat(l, s, offsets.element(instanceIndex).xyz));
      m.frustumCulled = false; m.count = 0; m.userData.offsets = offsets; scene.add(m); return m;
    });
    this.box = new THREE.Box3();
  }
  update(cam, frustum, range, skip) {
    const cz = cam.position.z, r0 = Math.floor((cz - range) / CHUNK), r1 = Math.ceil((cz + range) / CHUNK);
    const n = this.meshes.map(() => 0);
    for (let r = r0; r <= r1; r++) for (let c = 0; c < this.cols; c++) {
      const x = this.x0 + c * CHUNK, z = r * CHUNK;
      if (skip && skip(c, r)) continue;
      this.box.min.set(x, -0.6, z); this.box.max.set(x + CHUNK, 2.2, z + CHUNK);
      if (!frustum.intersectsBox(this.box)) continue;
      const d = this.box.distanceToPoint(cam.position);
      let l = this.dists.findIndex((t) => d < t); if (l < 0) l = this.dists.length;
      const a = this.meshes[l].userData.offsets.value.array, k = n[l]++;
      a[k * 4] = x; a[k * 4 + 1] = 0; a[k * 4 + 2] = z;
    }
    this.meshes.forEach((m, l) => { m.count = n[l]; m.visible = n[l] > 0; m.userData.offsets.value.needsUpdate = true; });
  }
}

// ============================================================================================
//  Terrain material: displaced 4K riverbed + boulders, glow-lit from the water
// ============================================================================================
const ROCK_TILE = 1.1;
function terrainMaterial(lodIndex, seg, offset) {
  const spacing = CHUNK / seg, lod = Math.max(0, Math.log2(spacing / (MICRO_TILE / 4096)) - 1);
  const m = new THREE.MeshStandardNodeMaterial({ side: THREE.DoubleSide });
  m.positionNode = Fn(() => {
    const p = positionLocal.add(offset), sk = attribute('skirt', 'float');
    return vec3(p.x, bedHeight(p.xz, float(lod)).sub(sk.mul(0.25)), p.z);
  })();
  const P = positionWorld;
  const mm = macroAt(P.xz), rock = mm.w;
  const uvM = P.xz.div(MICRO_TILE);
  const Ng = normalize(vec3(mm.y.negate(), 1.0, mm.z.negate()));
  // bed: planar
  const albBed = texture(colorTex, uvM).rgb, ntB = texture(normalTex, uvM).xyz.mul(2).sub(1), pkB = texture(packTex, uvM);
  // rock: triplanar
  const tw = pow(abs(Ng), vec3(4.0)); const twn = tw.div(tw.x.add(tw.y).add(tw.z));
  const sx = P.zy.div(ROCK_TILE), sy = P.xz.div(ROCK_TILE), sz = P.xy.div(ROCK_TILE);
  const albRock = texture(colorTex, sx).rgb.mul(twn.x).add(texture(colorTex, sy).rgb.mul(twn.y)).add(texture(colorTex, sz).rgb.mul(twn.z));
  const nX = texture(normalTex, sx).xyz.mul(2).sub(1), nY = texture(normalTex, sy).xyz.mul(2).sub(1), nZ = texture(normalTex, sz).xyz.mul(2).sub(1);
  const nRock = normalize(Ng.add(vec3(0.0, nX.y, nX.x).mul(twn.x)).add(vec3(nY.x, 0.0, nY.y).mul(twn.y)).add(vec3(nZ.x, nZ.y, 0.0).mul(twn.z)));
  const mi = float(1).sub(rock.mul(0.82));
  const nBed = normalize(vec3(mm.y.sub(ntB.x.div(ntB.z).mul(mi)).negate(), 1.0, mm.z.sub(ntB.y.div(ntB.z).mul(mi)).negate()));
  const Nw = normalize(mix(nBed, nRock, rock));
  const gray = dot(albRock, vec3(0.3, 0.55, 0.15));
  // dark, slightly bluish-grey stone (dry albedo ~0.1-0.2); wet stone darkens and turns glossy
  const albR = mix(vec3(gray), albRock, 0.22).mul(0.55);
  const uvS = simUV(P.xz);
  const inSim = smoothstep(0.0, 0.01, uvS.x).mul(smoothstep(1.0, 0.99, uvS.x));
  const wetness = texture(texD, uvS).y.mul(inSim).mul(smoothstep(0.5, 0.0, P.y));
  const alb = mix(albBed.mul(0.9), albR, rock).mul(mix(1.0, 0.55, wetness));
  const ao = mix(pkB.b, float(1.0), rock.mul(0.6));
  m.colorNode = vec4(alb, 1.0);
  m.roughnessNode = mix(mix(pkB.g, float(0.85), rock), float(0.2), wetness);
  m.metalnessNode = float(0.0);
  m.aoNode = ao;
  m.normalNode = cameraViewMatrix.mul(vec4(Nw, 0.0)).xyz;

  // ---- illumination from the luminous river (area light) ----
  const uvE = vec2(P.x.div(TW), P.z.div(TL));
  const hgt = max(P.y.sub(WATER_LEVEL), 0.0);
  const E = texture(texE, uvE);
  const w1 = smoothstep(0.03, 0.3, hgt), w2 = smoothstep(0.3, 1.2, hgt);
  const irr = mix(mix(E.x, E.y, w1), E.z, w2);   // blur radius grows with height: wider, dimmer light
  // direction to the light: toward brighter water horizontally, down toward the surface vertically
  const ex = 1.5 / FX, ez = 1.5 / FZ;
  const lvl = (o) => { const s = texture(texE, uvE.add(o)); return mix(s.y, s.z, w2); };
  const grad = vec2(lvl(vec2(ex, 0)).sub(lvl(vec2(-ex, 0))), lvl(vec2(0, ez)).sub(lvl(vec2(0, -ez))));
  const gdir = grad.div(length(grad).add(1e-4));
  const horiz = smoothstep(0.0, 0.004, length(grad)).mul(0.9);
  const wi = normalize(vec3(gdir.x.mul(horiz), hgt.add(0.12).negate(), gdir.y.mul(horiz)));
  // area light: wrapped diffuse (light arrives from a broad solid angle, not a point)
  const diffuse = clamp(dot(Nw, wi).mul(0.7).add(0.3), 0.0, 1.0).mul(ao);
  const lightCol = riverLightColor(irr);
  const rockLight = lightCol.mul(irr).mul(diffuse).mul(uEmit).mul(2.6);
  // wet stone near the waterline mirrors the glowing water
  const V = normalize(cameraPosition.sub(P));
  const Rr = reflect(V.negate(), Nw);
  const fres = float(0.04).add(float(0.96).mul(pow(float(1.0).sub(clamp(dot(Nw, V), 0.0, 1.0)), 5.0)));
  const sheen = lightCol.mul(E.x.mul(1.4)).mul(fres).mul(wetness).mul(smoothstep(0.1, -0.5, Rr.y)).mul(uEmit);
  m.emissiveNode = alb.mul(rockLight).add(sheen);
  return m;
}

// ============================================================================================
//  Water material
// ============================================================================================
const IOR = 1.333;
const SIG_A = vec3(0.42, 0.065, 0.035), SIG_S = 0.8;   // plankton-laden water is slightly turbid
function waterMaterial(lodIndex, seg, offset) {
  const m = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  m.positionNode = Fn(() => {
    const p = positionLocal.add(offset), sk = attribute('skirt', 'float');
    const A = texture(texA, simUV(p.xz)).level(0);
    return vec3(p.x, A.x.sub(sk.mul(0.04)), p.z);
  })();
  m.colorNode = Fn(() => {
    const Pw = positionWorld;
    const V = normalize(cameraPosition.sub(Pw));
    const uvS = simUV(Pw.xz);
    const A = texture(texA, uvS), B = texture(texB, uvS), C = texture(texC, uvS), D4 = texture(texD, uvS);
    const h = A.w, foamF = B.z, glow = B.w, turb = D4.x;
    // shoreline: the surface is interpolated between wet and dry cells; cut it where the sim says dry
    // (pebbles finer than the grid that break the surface are resolved by the depth test)
    If(h.lessThan(0.0012), () => { Discard(); });
    const det = detailSample(Pw.xz, C, false);
    // second, finer capillary layer (shading only): crisp ripples on top of the solver's swells
    const cap = detailSample(Pw.xz.mul(2.9).add(vec2(3.1, 7.7)), C.mul(2.9), false);
    // aeration: steep, fast, turbulent water entrains air. Bubbly water is milky, scatters strongly and is
    // rough at small scales -- what separates whitewater from a clear glassy surface. Patchy via bubble cells.
    const slopeS = length(vec2(A.y, A.z)), speedS = length(B.xy);
    const aer = clamp(
      smoothstep(0.55, 1.2, slopeS).mul(smoothstep(0.8, 1.8, speedS))
        .add(smoothstep(0.75, 1.0, turb).mul(0.2))
        .add(smoothstep(0.3, 0.9, foamF).mul(0.4))
        .mul(det.foam.mul(1.1).sub(0.05)), 0.0, 1.0);
    const amp = detailAmp(turb, h).mul(aer.mul(1.3).add(1.0));
    const capAmp = amp.mul(0.45).mul(smoothstep(4.0, 1.0, length(cameraPosition.sub(Pw))));
    const Nn = normalize(vec3(A.y.add(det.g.x.mul(amp)).add(cap.g.x.mul(capAmp)).negate(), 1.0, A.z.add(det.g.y.mul(amp)).add(cap.g.y.mul(capAmp)).negate()));
    const fw = max(fwidth(Pw.x), fwidth(Pw.z));
    const lod = clamp(log2(fw.mul(4096 / MICRO_TILE)).add(0.5), 0.0, 11.0);
    // --- interface
    const NdV = clamp(dot(Nn, V), 0.0, 1.0);
    const F = float(0.02).add(float(0.98).mul(pow(float(1.0).sub(NdV), 5.0)));
    const R = reflect(V.negate(), Nn);
    // reflection occlusion: march the reflected ray against the canyon height-field; banks reflect as
    // dark, faintly glow-lit rock instead of open sky
    const Ru = vec3(R.x, max(R.y, 0.02), R.z).normalize();
    const occ = float(0.0).toVar(), tr = float(0.03).toVar(), hitXZ = vec2(0.0).toVar();
    Loop(10, () => {
      const q = Pw.add(Ru.mul(tr));
      If(q.y.lessThan(macroAt(q.xz).x), () => { occ.assign(1.0); hitXZ.assign(q.xz); Break(); });
      tr.mulAssign(1.55);
    });
    // banks seen in reflection: dark stone lit by the river (same area-light field the rocks use)
    const Eh = texture(texE, vec2(hitXZ.x.div(TW), hitXZ.y.div(TL))).level(0);
    const rockR = vec3(0.004, 0.005, 0.006).add(riverLightColor(Eh.y).mul(Eh.y).mul(0.22).mul(uEmit));
    // steep faces tilted away mirror the luminous river itself
    const Ep = texture(texE, vec2(Pw.x.div(TW), Pw.z.div(TL))).level(0);
    const waterR = riverLightColor(Ep.x).mul(Ep.x).mul(0.9).mul(uEmit);
    const envR = mix(mix(texture(env, equirectUV(R)).rgb.mul(0.3), rockR, occ), waterR, smoothstep(0.0, -0.15, R.y));
    const Hh = normalize(uMoonDir.add(V)), NdH = max(dot(Nn, Hh), 0.0);
    const a2 = float(0.0036), dd = NdH.mul(NdH).mul(a2.sub(1.0)).add(1.0);
    const spec = uMoonCol.mul(a2.div(dd.mul(dd).mul(3.14159))).mul(max(dot(Nn, uMoonDir), 0.0)).mul(F).mul(0.6);
    // --- refraction ray traced through the displaced bed height-field
    const T = refract(V.negate(), Nn, 1.0 / IOR);
    const ty = max(T.y.negate(), 0.25);
    const tMax = min(h.add(0.1).div(ty), 1.2);
    const stepL = tMax.div(14.0);
    const t = float(0.0).toVar(), tPrev = float(0.0).toVar();
    Loop(14, () => {
      t.addAssign(stepL);
      const q = Pw.add(T.mul(t));
      If(q.y.lessThan(bedHeight(q.xz, lod)), () => { Break(); });
      tPrev.assign(t);
    });
    const lo = tPrev.toVar(), hi = t.toVar();
    Loop(5, () => {
      const mid = lo.add(hi).mul(0.5), q = Pw.add(T.mul(mid));
      If(q.y.lessThan(bedHeight(q.xz, lod)), () => { hi.assign(mid); }).Else(() => { lo.assign(mid); });
    });
    const s = hi;
    const Qh = Pw.add(T.mul(s));
    // --- bed shading at the hit point
    const mq = macroAt(Qh.xz), rock = mq.w;
    const uvM = Qh.xz.div(MICRO_TILE);
    const alb = texture(colorTex, uvM).level(lod).rgb, pk = texture(packTex, uvM).level(lod);
    const nt = texture(normalTex, uvM).level(lod).xyz.mul(2).sub(1);
    const mi = float(1).sub(rock.mul(0.82));
    const Nb = normalize(vec3(mq.y.sub(nt.x.div(nt.z).mul(mi)).negate(), 1.0, mq.z.sub(nt.y.div(nt.z).mul(mi)).negate()));
    // wet, silt-coated bed: darker, lower contrast, so the caustic web carries the image
    const lumA = dot(alb, vec3(0.3, 0.55, 0.15));
    const albD = mix(vec3(lumA), alb, 0.5);
    const albW = mix(vec3(0.16), pow(albD, vec3(1.3)), 0.6).mul(mix(0.85, 0.35, rock));
    const uvQ = simUV(Qh.xz);
    const caus = texture(causticRT.texture, uvQ).level(0).rgb;
    const gl = texture(texL, uvQ).level(0);
    const causCol = vec3(0.02, 0.78, 1.0);
    const bedLight = caus.mul(causCol).mul(uCaustic).mul(max(Nb.y, 0.0)).mul(3.2)
      .add(glowColor(gl.r.mul(3.0)).mul(gl.r.mul(0.5).add(gl.g.mul(0.3))).mul(uEmit))
      .add(vec3(0.004, 0.007, 0.012).mul(pk.b));
    const bedCol = albW.mul(bedLight);
    // --- participating medium: absorption, scattering (plankton turbidity + entrained bubbles), emission
    const sigB = aer.mul(30.0);                       // bubble scattering
    const sigS = float(SIG_S).add(sigB);
    const sigT = SIG_A.add(sigS);
    const Tr = exp(sigT.mul(s).negate());
    const gc = glowColor(glow);
    const emitV = gc.mul(glow.mul(0.35).add(0.022)).mul(uEmit);
    // plankton turbidity scatters the dim ambient luminous field; bubbles scatter the brighter in-water light
    // (caustic-lit field + own glow) and push it toward white
    const Lp = causCol.mul(gl.r).mul(0.6);
    const Ls = causCol.mul(gl.r.mul(1.2).add(gl.g.mul(0.5)).add(0.04)).mul(uCaustic).mul(0.4).add(gc.mul(glow.mul(0.6).add(0.03)).mul(uEmit));
    const LsW = mix(Ls, vec3(dot(Ls, vec3(0.3, 0.55, 0.15))).mul(vec3(0.85, 1.0, 1.05)), aer.mul(0.35));
    const inscatter = emitV.add(Lp.mul(SIG_S)).add(LsW.mul(sigB)).mul(float(1.0).sub(Tr)).div(sigT);
    const under = bedCol.mul(Tr).add(inscatter);
    // --- foam: bubbles riding the flow, lit by the moon and by the glow below
    // foam rafts: thin veils disappear, dense patches break into bubble membranes
    const cover = smoothstep(0.2, 0.7, foamF.mul(det.foam.mul(1.1).add(0.35))).mul(smoothstep(0.0, 0.004, h));
    // foam is a bright multiple-scatterer: lit by the luminous water around and beneath it, plus moonlight
    const foamLight = vec3(0.7, 0.95, 1.0).mul(gl.g.mul(2.2).add(gl.r.mul(2.6)).add(0.05)).add(gc.mul(glow.mul(1.2).add(0.1)));
    const foamCol = foamLight.mul(uEmit).add(uMoonCol.mul(max(Nn.y, 0.0).mul(0.35))).mul(mix(0.75, 1.0, det.foam));
    const surf = mix(under.mul(float(1.0).sub(F)).add(envR.mul(F)).add(spec), foamCol, cover);
    return vec4(surf, 1.0);
  })();
  return m;
}
// chunk masks: water chunks only where the channel can hold water
const waterCols = Math.round(SW / CHUNK), terrCols = Math.round(TW / CHUNK), rowsPerTile = Math.round(TL / CHUNK);
const waterMask = new Uint8Array(waterCols * rowsPerTile);
for (let r = 0; r < rowsPerTile; r++) for (let c = 0; c < waterCols; c++) {
  let wet = 0; const x0 = SX0 + c * CHUNK, z0 = r * CHUNK;
  for (let j = 0; j < 64 && !wet; j++) for (let i = 0; i < 64; i++) {
    const xi = Math.floor((x0 + (i + 0.5) / 64 * CHUNK) / MT), zi = Math.floor((z0 + (j + 0.5) / 64 * CHUNK) / MT);
    if (terrain.H[zi * MRES + xi] < WATER_LEVEL + 0.08) { wet = 1; break; }
  }
  waterMask[r * waterCols + c] = wet;
}
const maxRows = Math.ceil(60 / CHUNK) + 4;
const terrainChunks = new ChunkSet(scene, 0, terrCols, [256, 128, 64, 32, 16], [1.6, 4.0, 9, 18], terrainMaterial, maxRows);
const waterChunks = new ChunkSet(scene, SX0, waterCols, [128, 64, 32, 16], [3.5, 8, 16], waterMaterial, maxRows);
const waterSkip = (c, r) => !waterMask[(((r % rowsPerTile) + rowsPerTile) % rowsPerTile) * waterCols + c];

// ============================================================================================
//  Post: bloom, grain, vignette (tone mapping by the renderer output transform)
// ============================================================================================
const post = new THREE.PostProcessing(renderer);
const scenePass = pass(scene, camera);
const sceneColor = scenePass.getTextureNode('output');
const bloomNode = bloom(sceneColor, params.bloom, 0.4, 0.45);
const composite = Fn(() => {
  const c = sceneColor.rgb.add(bloomNode.rgb);
  const vig = smoothstep(1.25, 0.35, length(screenUV.sub(0.5).mul(vec2(1.25, 1.0))));
  return vec4(c.mul(vig), 1.0);
})();
// tone map first, then FXAA on display-referred colour, then grain
post.outputColorTransform = false;
const aa = fxaa(renderOutput(composite));
post.outputNode = Fn(() => {
  const grain = hash(screenUV.mul(vec2(1931.7, 1373.3)).add(time.mul(61.7).fract().mul(97.0))).sub(0.5).mul(0.03);
  return vec4(aa.rgb.mul(float(1.0).add(grain)), 1.0);
})();
await renderer.computeAsync(bedInit);
await renderer.computeAsync(waterInit);
await renderer.computeAsync(fieldInit);
for (let k = 0; k < 240; k++) { simFrame(); if (k % 30 === 29) { await renderer.computeAsync(exportPass[P][Qp]); } }

const frustum = new THREE.Frustum(), pv = new THREE.Matrix4();
let acc = 0;
const finalOutput = post.outputNode;
return {
  update(dt) {
    acc += Math.min(dt, 0.1); let n = 0;
    while (acc >= 1 / 60 && n < 2) { simFrame(); acc -= 1 / 60; n++; }
    if (acc > 0.1) acc = 0;
  },
  stir(hit, velocity) {
    uMouseVel.value.copy(velocity);
    const zl = ((hit.z % SL) + SL) % SL;
    uMouse.value.set((hit.x - SX0) / DX - 0.5, zl / DX - 0.5, 1, 7);
  },
  endStir() { uMouse.value.z = 0; },
  render() {
    renderer.setRenderTarget(causticRT);
    renderer.setClearColor(0x000000, 0); renderer.clear();
    renderer.render(causticScene, causticCam);
    renderer.setRenderTarget(null);
    camera.updateMatrixWorld();
    pv.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
    frustum.setFromProjectionMatrix(pv);
    terrainChunks.update(camera, frustum, 40);
    waterChunks.update(camera, frustum, 40, waterSkip);
    post.render();
  },
  setDebugMode(mode) {
    post.outputNode = mode === 'nopost' ? renderOutput(sceneColor)
      : mode === 'caustics' ? renderOutput(texture(causticRT.texture))
      : mode === 'glow' ? renderOutput(texture(texL)) : finalOutput;
    post.needsUpdate = true;
  },
  dispose() {
    post.dispose(); causticRT.dispose(); detTex.dispose();
    for (const tex of [texA, texB, texC, texD, texE, texL]) tex.dispose();
    for (const mesh of [...terrainChunks.meshes, ...waterChunks.meshes, ...causticMeshes]) {
      mesh.removeFromParent(); mesh.geometry.dispose(); mesh.material.dispose();
    }
  },
};
}
