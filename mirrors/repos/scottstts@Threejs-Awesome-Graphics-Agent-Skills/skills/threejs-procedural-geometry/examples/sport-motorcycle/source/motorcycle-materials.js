import * as THREE from "three/webgpu";
import {
  color, float, mix, mx_fractal_noise_float, mx_noise_float, positionWorld, texture, uv,
  vec2, vec3,
} from "three/tsl";

import { PAL, SEED } from "./design-contract.js";
import { TAU, clampf, ease, lerp, mulberry32, section, smooth01, sweep } from "./mesh-kit.js";

/* ============================================================================
   3. GENERATED SURFACE INPUTS + MATERIAL IDENTITIES
   ----------------------------------------------------------------------------
   Every texture below is generated at construction from the fixed seed; no
   external assets.  Materials are grouped by finish, not by part, because the
   whole machine is black-on-black: what separates a fairing from a case from a
   rotor here is specular response, not albedo.
   ========================================================================== */

const TEX = [];
function keep(t) { TEX.push(t); return t; }

function canvas2d(w, h) {
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  return [c, c.getContext("2d")];
}
function canvasTexture(c, { repeat = [1, 1], aniso = 8, srgb = false, wrap = THREE.RepeatWrapping } = {}) {
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = wrap;
  t.repeat.set(repeat[0], repeat[1]);
  t.anisotropy = aniso;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.needsUpdate = true;
  return keep(t);
}
/* height field -> tangent-space normal map (Sobel), wrapped */
function normalFromHeight(height, size, strength = 2.4, sizeY = null) {
  const H = sizeY || size;
  const data = new Uint8Array(size * H * 4);
  const at = (x, y) => height[((y % H) + H) % H * size + (((x % size) + size) % size)];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (at(x + 1, y) - at(x - 1, y)) * strength;
      const dy = (at(x, y + 1) - at(x, y - 1)) * strength;
      const inv = 1 / Math.hypot(dx, dy, 1);
      const i = (y * size + x) * 4;
      data[i] = (-dx * inv * 0.5 + 0.5) * 255;
      data[i + 1] = (dy * inv * 0.5 + 0.5) * 255;
      data[i + 2] = (inv * 0.5 + 0.5) * 255;
      data[i + 3] = 255;
    }
  }
  const t = new THREE.DataTexture(data, size, H, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8; t.needsUpdate = true;
  return keep(t);
}
/* value noise sampled on a torus so it tiles */
function tileNoise(size, freq, octaves, seedR) {
  const out = new Float32Array(size * size);
  const grid = [];
  for (let o = 0; o < octaves; o++) {
    const f = freq << o, g = new Float32Array(f * f);
    for (let i = 0; i < f * f; i++) g[i] = seedR();
    grid.push(g);
  }
  const sm = (t) => t * t * (3 - 2 * t);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let v = 0, amp = 1, norm = 0;
      for (let o = 0; o < octaves; o++) {
        const f = freq << o, g = grid[o];
        const fx = (x / size) * f, fy = (y / size) * f;
        const x0 = Math.floor(fx), y0 = Math.floor(fy);
        const tx = sm(fx - x0), ty = sm(fy - y0);
        const i00 = g[(y0 % f) * f + (x0 % f)], i10 = g[(y0 % f) * f + ((x0 + 1) % f)];
        const i01 = g[((y0 + 1) % f) * f + (x0 % f)], i11 = g[((y0 + 1) % f) * f + ((x0 + 1) % f)];
        v += amp * lerp(lerp(i00, i10, tx), lerp(i01, i11, tx), ty);
        norm += amp; amp *= 0.5;
      }
      out[y * size + x] = v / norm;
    }
  }
  return out;
}

/* --- 3.1 generated normal / detail maps ---------------------------------- */
function makeFlakeNormal() {                       // metallic paint flake
  const S = 512, R = mulberry32(SEED + 11);
  const h = new Float32Array(S * S);
  for (let i = 0; i < 5200; i++) {
    const x = (R() * S) | 0, y = (R() * S) | 0, r = 1 + R() * 1.6, a = (R() - 0.5) * 1.2;
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
      const d = Math.hypot(dx, dy);
      if (d > r) continue;
      const ix = ((x + dx) % S + S) % S, iy = ((y + dy) % S + S) % S;
      h[iy * S + ix] += a * (1 - d / r);
    }
  }
  return normalFromHeight(h, S, 0.9);
}
function makeCastNormal() {                        // sand-cast alloy grain
  const S = 512, R = mulberry32(SEED + 23);
  const base = tileNoise(S, 24, 4, R);
  const h = new Float32Array(S * S);
  for (let i = 0; i < S * S; i++) h[i] = base[i] * 0.55 + (R() - 0.5) * 0.16;
  return normalFromHeight(h, S, 1.5);
}
function makeBrushNormal() {                       // linear brushed metal
  const S = 512, R = mulberry32(SEED + 31);
  const h = new Float32Array(S * S);
  const lanes = new Float32Array(S);
  for (let x = 0; x < S; x++) lanes[x] = R();
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    h[y * S + x] = lanes[x] * 0.6 + (R() - 0.5) * 0.08 + Math.sin(x * 0.9 + lanes[x] * 9) * 0.05;
  }
  return normalFromHeight(h, S, 0.55);
}
function makeCarbonNormal() {                      // 2x2 twill weave
  const S = 512, cell = 32;
  const h = new Float32Array(S * S);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const cx = Math.floor(x / cell), cy = Math.floor(y / cell);
    const over = ((cx + cy) >> 1 & 1) === 0;
    const fx = (x % cell) / cell, fy = (y % cell) / cell;
    const along = over ? fy : fx, across = over ? fx : fy;
    h[y * S + x] = Math.sin(Math.PI * across) * 0.8 + Math.sin(Math.PI * along * 4) * 0.06 + (over ? 0.16 : 0);
  }
  return normalFromHeight(h, S, 1.9);
}
function makeGrainNormal() {                       // fine moulded-plastic grain
  const S = 256, R = mulberry32(SEED + 47);
  const n = tileNoise(S, 64, 3, R);
  return normalFromHeight(n, S, 0.7);
}
function makeSeatNormal() {                        // seat vinyl pebble + stitch
  const S = 512, R = mulberry32(SEED + 53);
  const n = tileNoise(S, 96, 2, R);
  const h = new Float32Array(S * S);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) h[y * S + x] = n[y * S + x] * 0.85;
  return normalFromHeight(h, S, 1.4);
}
function makeKnurlNormal() {                       // diamond knurl (pegs, bar ends)
  const S = 256, cell = 14;
  const h = new Float32Array(S * S);
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const a = ((x + y) % cell) / cell, b = ((x - y + S * 4) % cell) / cell;
    h[y * S + x] = Math.min(Math.sin(a * Math.PI), Math.sin(b * Math.PI));
  }
  return normalFromHeight(h, S, 2.6);
}

/* --- 3.2 decals ----------------------------------------------------------- */
function decalCanvas(w, h, draw) {
  const [c, x] = canvas2d(w, h);
  x.clearRect(0, 0, w, h);
  draw(x, w, h);
  return c;
}
function zx6rDecal() {
  return decalCanvas(1024, 320, (x, w, h) => {
    x.save();
    x.translate(w * 0.5, h * 0.62);
    x.transform(1, 0, -0.26, 1, 0, 0);                   // italic lean
    x.font = "800 210px 'Arial Narrow', 'Helvetica Neue', Arial, sans-serif";
    x.textAlign = "center"; x.textBaseline = "alphabetic";
    const g = x.createLinearGradient(0, -150, 0, 60);
    g.addColorStop(0, "#f2f4f6"); g.addColorStop(0.52, "#c3c8cd"); g.addColorStop(1, "#8d949b");
    x.fillStyle = g;
    x.scale(0.86, 1);
    x.fillText("ZX-6R", 0, 0);
    x.restore();
  });
}
function kawasakiDecal(light = true) {
  return decalCanvas(1024, 200, (x, w, h) => {
    x.save();
    x.translate(w * 0.5, h * 0.74);
    x.transform(1, 0, -0.10, 1, 0, 0);
    x.font = "700 138px 'Arial Narrow', 'Helvetica Neue', Arial, sans-serif";
    x.textAlign = "center"; x.textBaseline = "alphabetic";
    x.fillStyle = light ? "#eef1f4" : "#101215";
    x.scale(1.02, 1);
    x.fillText("Kawasaki", 0, 0);
    x.restore();
  });
}
function ninjaDecal() {
  return decalCanvas(768, 220, (x, w, h) => {
    x.save();
    x.translate(w * 0.5, h * 0.72);
    x.transform(1, 0, -0.22, 1, 0, 0);
    x.font = "800 150px 'Arial Narrow', 'Helvetica Neue', Arial, sans-serif";
    x.textAlign = "center";
    x.fillStyle = "#e7ebee";
    x.fillText("Ninja", 0, 0);
    x.restore();
  });
}
/* tyre: sidewall lettering + shoulder siping, mapped u=circumference v=section */
function tyreMaps() {
  // canvas aspect matches the real surface: ~1.88 m of circumference against
  // ~0.34 m of section arc, so lettering is not stretched by the mapping
  const W = 2048, H = 288;
  const [c, x] = canvas2d(W, H);
  x.fillStyle = "#0b0b0d"; x.fillRect(0, 0, W, H);
  const R = mulberry32(SEED + 71);
  // subtle mould-release mottling across the whole carcass
  for (let i = 0; i < 2600; i++) {
    const v = 8 + R() * 14;
    x.fillStyle = `rgba(${v + 12},${v + 12},${v + 14},0.5)`;
    x.beginPath(); x.arc(R() * W, R() * H, 2 + R() * 14, 0, TAU); x.fill();
  }
  // moulded rings bracketing the sidewall lettering band
  const ring = (v0, v1, fill) => { x.fillStyle = fill; x.fillRect(0, v0 * H, W, (v1 - v0) * H); };
  ring(0.052, 0.060, "rgba(140,140,146,0.16)");
  ring(0.160, 0.168, "rgba(140,140,146,0.13)");
  ring(0.832, 0.840, "rgba(140,140,146,0.13)");
  ring(0.940, 0.948, "rgba(140,140,146,0.16)");
  const label = (vc, text, size, alpha, repeats, spacing = 0) => {
    x.save();
    x.font = `700 ${size}px 'Arial Narrow', Arial, sans-serif`;
    x.textAlign = "center"; x.textBaseline = "middle";
    x.fillStyle = `rgba(188,190,194,${alpha})`;
    if (spacing) x.letterSpacing = spacing + "px";
    for (let i = 0; i < repeats; i++) x.fillText(text, (i + 0.5) * (W / repeats), vc * H);
    x.restore();
  };
  label(0.098, "BRIDGESTONE", 16, 0.92, 2, 1.2);
  label(0.134, "BATTLAX HYPERSPORT S22", 10, 0.55, 2, 0.5);
  label(0.902, "BRIDGESTONE", 16, 0.92, 2, 1.2);
  label(0.866, "TUBELESS   RADIAL", 9, 0.5, 2, 0.7);
  const tex = canvasTexture(c, { srgb: true, aniso: 16 });

  // matching micro-relief: fine grain + raised lettering band
  const S = 512, hgt = new Float32Array(S * S);
  const NR = mulberry32(SEED + 73);
  const n = tileNoise(S, 128, 2, NR);
  for (let y = 0; y < S; y++) for (let x2 = 0; x2 < S; x2++) hgt[y * S + x2] = n[y * S + x2] * 0.8;
  return { map: tex, normal: normalFromHeight(hgt, S, 1.1) };
}
/* wire mesh for radiator core and fairing vents */
function meshScreen(pitch = 26, bar = 9) {
  const S = 256;
  const [c, x] = canvas2d(S, S);
  x.fillStyle = "rgba(0,0,0,0)"; x.clearRect(0, 0, S, S);
  x.fillStyle = "#1a1c20";
  for (let i = 0; i < S; i += pitch) { x.fillRect(i, 0, bar, S); x.fillRect(0, i, S, bar); }
  return canvasTexture(c, { srgb: true });
}
/* radiator fin strip (vertical louvres) */
function radiatorCore() {
  const S = 512;
  const [c, x] = canvas2d(S, S);
  x.fillStyle = "#0a0b0c"; x.fillRect(0, 0, S, S);
  for (let i = 0; i < S; i += 7) {
    x.fillStyle = i % 14 === 0 ? "#22262b" : "#131518";
    x.fillRect(i, 0, 3.4, S);
  }
  for (let j = 0; j < S; j += 46) { x.fillStyle = "#2c3138"; x.fillRect(0, j, S, 4); }
  return canvasTexture(c, { srgb: true, repeat: [1, 1] });
}
/* LED headlight reflector cells */
function ledFace() {
  const S = 512;
  const [c, x] = canvas2d(S, S);
  const g = x.createLinearGradient(0, 0, 0, S);
  g.addColorStop(0, "#20242a"); g.addColorStop(1, "#0c0e11");
  x.fillStyle = g; x.fillRect(0, 0, S, S);
  for (let y = 0; y < S; y += 18) for (let x2 = 0; x2 < S; x2 += 18) {
    const d = Math.hypot(x2 - S / 2, y - S / 2) / (S / 2);
    const v = Math.max(0, 1 - d) * 210;
    x.fillStyle = `rgb(${v * 0.86},${v * 0.92},${v})`;
    x.beginPath(); x.arc(x2 + 9, y + 9, 7.4, 0, TAU); x.fill();
  }
  return canvasTexture(c, { srgb: true, wrap: THREE.ClampToEdgeWrapping });
}

/* --- 3.3 studio environment ---------------------------------------------
   A generated equirectangular softbox rig.  The whole machine is black
   lacquer and dark alloy: essentially all of its shape information arrives as
   reflected light, so the environment is a modelling tool, not a backdrop.  */
function studioEnvTexture() {
  const W = 1024, H = 512;
  const data = new Float32Array(W * H * 4);
  const boxes = [
    // azimuth, elevation, half-extents (deg), intensity, tint, edge softness
    { az: 28, el: 58, aw: 60, ah: 25, i: 6.4, c: [1.00, 0.99, 0.96], s: 0.40 },
    { az: -150, el: 52, aw: 56, ah: 22, i: 3.1, c: [0.96, 0.98, 1.00], s: 0.46 },
    { az: 92, el: 6, aw: 20, ah: 40, i: 2.5, c: [1.00, 1.00, 1.00], s: 0.52 },
    { az: -88, el: 10, aw: 24, ah: 42, i: 1.7, c: [0.95, 0.97, 1.00], s: 0.52 },
    { az: 176, el: 22, aw: 30, ah: 26, i: 2.2, c: [1.00, 0.99, 0.98], s: 0.55 },
    { az: 0, el: -4, aw: 34, ah: 14, i: 0.8, c: [1.00, 1.00, 1.00], s: 0.7 },
  ];
  const dAz = (a, b) => { let d = a - b; while (d > 180) d -= 360; while (d < -180) d += 360; return d; };
  for (let y = 0; y < H; y++) {
    const el = (0.5 - (y + 0.5) / H) * 180;                 // +90 zenith .. -90 nadir
    // studio shell: bright ceiling, luminous horizon, grey sweep floor.
    // Kept near unit average so a white diffuse surface tone-maps to white and
    // polished metal reflects a readable box rather than a clipped sheet.
    let base = el > 0
      ? lerp(0.46, 0.92, ease(el / 90, 0.7))
      : lerp(0.46, 0.085, ease(-el / 90, 0.55));
    for (let x = 0; x < W; x++) {
      const az = ((x + 0.5) / W) * 360 - 180;
      let r = base, g = base, b = base * 1.015;
      for (const S of boxes) {
        const u = Math.abs(dAz(az, S.az)) / S.aw;
        const v = Math.abs(el - S.el) / S.ah;
        const d = Math.hypot(Math.pow(u, 1.7), Math.pow(v, 1.7));
        const k = 1 - smooth01(clampf((d - (1 - S.s)) / S.s, 0, 1));
        if (k <= 0) continue;
        const w = k * k * S.i;
        r += w * S.c[0]; g += w * S.c[1]; b += w * S.c[2];
      }
      const i = (y * W + x) * 4;
      data[i] = r; data[i + 1] = g; data[i + 2] = b; data[i + 3] = 1;
    }
  }
  const tex = new THREE.DataTexture(data, W, H, THREE.RGBAFormat, THREE.FloatType);
  tex.mapping = THREE.EquirectangularReflectionMapping;
  tex.colorSpace = THREE.LinearSRGBColorSpace;
  tex.minFilter = tex.magFilter = THREE.LinearFilter;
  tex.generateMipmaps = false;
  tex.needsUpdate = true;
  return keep(tex);
}

/* --- 3.4 material bundles ------------------------------------------------ */
const MAT = {};
function buildMaterials() {
  const flakeN = makeFlakeNormal();
  const castN = makeCastNormal();
  const brushN = makeBrushNormal();
  const carbonN = makeCarbonNormal();
  const grainN = makeGrainNormal();
  const seatN = makeSeatNormal();
  const knurlN = makeKnurlNormal();
  const tyre = tyreMaps();

  const rep = (t, u, v) => { const c = t.clone(); c.wrapS = c.wrapT = THREE.RepeatWrapping; c.repeat.set(u, v); c.needsUpdate = true; return keep(c); };
  const wnoise = (s) => mx_noise_float(positionWorld.mul(s));
  const tag = (m, slot) => { m.userData.slot = slot; MAT[slot] = MAT[slot] || m; return m; };

  /* -- flat "Metallic Spark Black": aluminium flake under a matte clear -- */
  const flatBlack = new THREE.MeshPhysicalNodeMaterial();
  flatBlack.colorNode = mix(color(PAL.fairing), color(PAL.fairingDeep), wnoise(3.2).mul(0.5).add(0.5).mul(0.55));
  // flake is metallic, binder is not: a low base metalness with a sparse
  // high-frequency lift reads as suspended aluminium under a matte clear
  flatBlack.metalnessNode = float(0.12).add(wnoise(190).mul(0.5).add(0.5).pow(3).mul(0.30));
  flatBlack.roughnessNode = float(0.415).add(wnoise(52).mul(0.05));
  flatBlack.clearcoat = 0.62;
  flatBlack.clearcoatRoughness = 0.30;
  flatBlack.normalMap = rep(flakeN, 22, 22);
  flatBlack.normalScale = new THREE.Vector2(0.10, 0.10);
  tag(flatBlack, "paintFlat");

  /* -- satin black on cast alloy: wheels, hubs, chain guard ------------- */
  const wheelBlack = new THREE.MeshPhysicalNodeMaterial();
  wheelBlack.colorNode = mix(color(0x101216), color(0x07080a), wnoise(6).mul(0.5).add(0.5).mul(0.6));
  wheelBlack.metalness = 0.24;
  wheelBlack.roughnessNode = float(0.325).add(wnoise(58).mul(0.04));
  wheelBlack.clearcoat = 0.55;
  wheelBlack.clearcoatRoughness = 0.20;
  wheelBlack.normalMap = rep(castN, 7, 7);
  wheelBlack.normalScale = new THREE.Vector2(0.12, 0.12);
  tag(wheelBlack, "wheelBlack");

  /* -- gloss lacquer: tank cover, upper cowl crown, tail spine ---------- */
  const glossBlack = new THREE.MeshPhysicalNodeMaterial();
  glossBlack.colorNode = mix(color(PAL.glossBlack), color(0x1a1e24), wnoise(2.4).mul(0.5).add(0.5).mul(0.3));
  glossBlack.metalness = 0.28;
  glossBlack.roughnessNode = float(0.085).add(wnoise(64).mul(0.018));
  glossBlack.clearcoat = 1.0;
  glossBlack.clearcoatRoughness = 0.035;
  glossBlack.normalMap = rep(flakeN, 26, 26);
  glossBlack.normalScale = new THREE.Vector2(0.05, 0.05);
  tag(glossBlack, "paintGloss");

  /* -- charcoal graphic panel: the mid-grey wedge on nose and flank ----- */
  const graphite = new THREE.MeshPhysicalNodeMaterial();
  graphite.colorNode = mix(color(0x2a2e34), color(0x1b1e23), wnoise(4).mul(0.5).add(0.5));
  graphite.metalness = 0.42;
  graphite.roughnessNode = float(0.30).add(wnoise(60).mul(0.03));
  graphite.clearcoat = 0.85; graphite.clearcoatRoughness = 0.12;
  graphite.normalMap = rep(flakeN, 24, 24);
  graphite.normalScale = new THREE.Vector2(0.09, 0.09);
  tag(graphite, "paintGraphite");

  /* -- Kawasaki lime: rim pinstripe and accent flashes ------------------ */
  const lime = new THREE.MeshPhysicalNodeMaterial();
  lime.colorNode = color(PAL.green);
  lime.metalness = 0.1; lime.roughness = 0.16;
  lime.clearcoat = 1.0; lime.clearcoatRoughness = 0.05;
  tag(lime, "lime");

  /* -- unpainted structural alloy: frame, swingarm, triples ------------- */
  const anodized = new THREE.MeshPhysicalNodeMaterial();
  anodized.colorNode = mix(color(PAL.alloyDark), color(0x181b1f), mx_fractal_noise_float(positionWorld.mul(9), 3, 2.1, 0.5).mul(0.5).add(0.5).mul(0.7));
  anodized.metalness = 0.94;
  anodized.roughnessNode = float(0.335).add(wnoise(38).mul(0.055));
  anodized.normalMap = rep(castN, 5, 5);
  anodized.normalScale = new THREE.Vector2(0.34, 0.34);
  tag(anodized, "alloyAnodized");

  /* -- sand-cast engine alloy ------------------------------------------- */
  const castAlloy = new THREE.MeshPhysicalNodeMaterial();
  castAlloy.colorNode = mix(color(0x4a4e54), color(0x2c2f34), mx_fractal_noise_float(positionWorld.mul(14), 3, 2.2, 0.55).mul(0.5).add(0.5));
  castAlloy.metalness = 0.88;
  castAlloy.roughnessNode = float(0.545).add(wnoise(26).mul(0.075));
  castAlloy.normalMap = rep(castN, 9, 9);
  castAlloy.normalScale = new THREE.Vector2(0.75, 0.75);
  tag(castAlloy, "alloyCast");

  /* -- machined/brushed alloy: fork sliders, yokes, bar ends ------------ */
  const machined = new THREE.MeshPhysicalNodeMaterial();
  machined.colorNode = color(PAL.brightAlloy);
  machined.metalness = 1.0;
  machined.roughnessNode = float(0.215).add(wnoise(70).mul(0.035));
  machined.normalMap = rep(brushN, 4, 16);
  machined.normalScale = new THREE.Vector2(0.13, 0.035);
  tag(machined, "alloyMachined");

  /* -- hard chrome fork stanchion --------------------------------------- */
  const chrome = new THREE.MeshPhysicalNodeMaterial();
  chrome.colorNode = color(PAL.chrome);
  chrome.metalness = 1.0; chrome.roughness = 0.045;
  chrome.envMapIntensity = 1.25;
  tag(chrome, "chrome");

  /* -- brake rotor: bright steel, radial brushing, hole field ----------- */
  const rotor = new THREE.MeshPhysicalNodeMaterial();
  rotor.colorNode = mix(color(0x8f949b), color(0x6c7178), wnoise(40).mul(0.5).add(0.5).mul(0.55));
  rotor.metalness = 1.0;
  rotor.roughnessNode = float(0.30).add(wnoise(120).mul(0.06));
  rotor.normalMap = rep(brushN, 26, 1);
  rotor.normalScale = new THREE.Vector2(0.10, 0.22);
  tag(rotor, "rotorSteel");

  /* -- rotor carrier (hard-anodised inner spider) ----------------------- */
  const carrier = new THREE.MeshPhysicalNodeMaterial();
  carrier.colorNode = color(0x24272b);
  carrier.metalness = 0.95; carrier.roughness = 0.30;
  tag(carrier, "rotorCarrier");

  /* -- brushed titanium silencer with heat tint ------------------------- */
  const titanium = new THREE.MeshPhysicalNodeMaterial();
  const heat = positionWorld.z.add(0.34).mul(2.2).clamp(0, 1);
  // stock silencer: dark anodised shell, brighter only near the outlet
  titanium.colorNode = mix(color(0x33373d), color(0x767b83), heat)
    .mul(mix(vec3(1.02, 0.97, 0.93), vec3(1, 1, 1), heat));
  titanium.metalness = 1.0;
  titanium.roughnessNode = float(0.255).add(wnoise(90).mul(0.05));
  titanium.normalMap = rep(brushN, 2, 26);
  titanium.normalScale = new THREE.Vector2(0.06, 0.26);
  tag(titanium, "titanium");

  /* -- exhaust header: heat-stained stainless -------------------------- */
  const header = new THREE.MeshPhysicalNodeMaterial();
  const stain = mx_fractal_noise_float(positionWorld.mul(11), 3, 2.3, 0.5).mul(0.5).add(0.5);
  header.colorNode = mix(color(0x7c7f84), color(0x54484a), stain.mul(0.85));
  header.metalness = 1.0;
  header.roughnessNode = float(0.255).add(stain.mul(0.12));
  header.normalMap = rep(brushN, 2, 18);
  header.normalScale = new THREE.Vector2(0.05, 0.16);
  tag(header, "header");

  /* -- textured black moulding: inner panels, plate hanger, guards ------ */
  const plastic = new THREE.MeshPhysicalNodeMaterial();
  plastic.colorNode = color(0x131518);
  plastic.metalness = 0.0;
  plastic.roughnessNode = float(0.62).add(wnoise(48).mul(0.06));
  plastic.normalMap = rep(grainN, 14, 14);
  plastic.normalScale = new THREE.Vector2(0.5, 0.5);
  tag(plastic, "plastic");

  /* -- soft rubber: grips, hoses, boots -------------------------------- */
  const rubber = new THREE.MeshPhysicalNodeMaterial();
  rubber.colorNode = color(0x0e0f11);
  rubber.metalness = 0.0; rubber.roughness = 0.78;
  rubber.normalMap = rep(grainN, 8, 8);
  rubber.normalScale = new THREE.Vector2(0.6, 0.6);
  tag(rubber, "rubber");

  /* -- tyre carcass ----------------------------------------------------- */
  const tyreMat = new THREE.MeshPhysicalNodeMaterial();
  tyreMat.map = tyre.map;
  tyreMat.colorNode = texture(tyre.map, uv()).rgb.mul(mix(float(0.82), float(1.06), wnoise(24).mul(0.5).add(0.5)));
  tyreMat.metalness = 0.0;
  tyreMat.roughnessNode = float(0.80).add(wnoise(70).mul(0.06));
  tyreMat.normalMap = rep(tyre.normal, 12, 3);
  tyreMat.normalScale = new THREE.Vector2(0.55, 0.55);
  // a trace of sheen only: more than this reads as waxy or translucent rubber
  tyreMat.sheen = 0.06; tyreMat.sheenRoughness = 0.9;
  tyreMat.sheenColor = new THREE.Color(0x191b1e);
  tag(tyreMat, "tyre");

  /* -- seat vinyl ------------------------------------------------------- */
  const seat = new THREE.MeshPhysicalNodeMaterial();
  seat.colorNode = color(PAL.seat);
  seat.metalness = 0.0;
  seat.roughnessNode = float(0.545).add(wnoise(80).mul(0.05));
  seat.normalMap = rep(seatN, 9, 9);
  seat.normalScale = new THREE.Vector2(0.8, 0.8);
  seat.sheen = 0.55; seat.sheenRoughness = 0.55;
  seat.sheenColor = new THREE.Color(0x3a3f46);
  seat.clearcoat = 0.2; seat.clearcoatRoughness = 0.55;
  tag(seat, "seat");

  /* -- carbon twill ----------------------------------------------------- */
  const carbon = new THREE.MeshPhysicalNodeMaterial();
  carbon.colorNode = color(0x121418);
  carbon.metalness = 0.55;
  carbon.roughness = 0.22;
  carbon.clearcoat = 1.0; carbon.clearcoatRoughness = 0.06;
  carbon.normalMap = rep(carbonN, 10, 10);
  carbon.normalScale = new THREE.Vector2(0.7, 0.7);
  tag(carbon, "carbon");

  /* -- knurled contact surfaces ---------------------------------------- */
  const knurled = new THREE.MeshPhysicalNodeMaterial();
  knurled.colorNode = color(0x2b2e33);
  knurled.metalness = 0.9; knurled.roughness = 0.42;
  knurled.normalMap = rep(knurlN, 6, 3);
  knurled.normalScale = new THREE.Vector2(1.0, 1.0);
  tag(knurled, "knurled");

  /* -- fasteners -------------------------------------------------------- */
  const bolt = new THREE.MeshPhysicalNodeMaterial();
  bolt.colorNode = color(0x555a61);
  bolt.metalness = 1.0; bolt.roughness = 0.30;
  tag(bolt, "bolt");

  const boltDark = new THREE.MeshPhysicalNodeMaterial();
  boltDark.colorNode = color(0x1c1f23);
  boltDark.metalness = 0.95; boltDark.roughness = 0.36;
  tag(boltDark, "boltDark");

  /* -- drive chain ------------------------------------------------------ */
  const chain = new THREE.MeshPhysicalNodeMaterial();
  chain.colorNode = mix(color(0x4e5259), color(0x2a2d31), wnoise(160).mul(0.5).add(0.5));
  chain.metalness = 1.0; chain.roughness = 0.36;
  tag(chain, "chain");

  const chainGold = new THREE.MeshPhysicalNodeMaterial();
  chainGold.colorNode = color(0x9a7c3e);
  chainGold.metalness = 1.0; chainGold.roughness = 0.34;
  tag(chainGold, "chainGold");

  /* -- glazing ----------------------------------------------------------
     Alpha-blended rather than transmissive on purpose: a single transmissive
     material forces an extra full-scene pass per frame, and for thin tinted
     covers at this scale the refraction it buys is not visible.          */
  const headGlass = new THREE.MeshPhysicalNodeMaterial();
  headGlass.colorNode = color(0xb9c6d2);
  headGlass.opacity = 0.30;
  headGlass.transparent = true;
  headGlass.depthWrite = false;
  headGlass.roughness = 0.035; headGlass.metalness = 0.0;
  headGlass.clearcoat = 1.0; headGlass.clearcoatRoughness = 0.02;
  headGlass.side = THREE.DoubleSide;
  tag(headGlass, "glass");

  const screen = new THREE.MeshPhysicalNodeMaterial();
  screen.colorNode = color(0x39424d);
  screen.opacity = 0.34;
  screen.transparent = true;
  screen.depthWrite = false;
  screen.roughness = 0.035; screen.metalness = 0.0;
  screen.clearcoat = 1.0; screen.clearcoatRoughness = 0.02;
  screen.envMapIntensity = 1.5;
  screen.side = THREE.DoubleSide;
  tag(screen, "screen");

  const redLens = new THREE.MeshPhysicalNodeMaterial();
  redLens.colorNode = color(0x5a0a0f);
  redLens.emissiveNode = color(0xff2a18).mul(0.30);
  redLens.metalness = 0.0; redLens.roughness = 0.085;
  redLens.clearcoat = 1.0; redLens.clearcoatRoughness = 0.03;
  redLens.opacity = 0.92; redLens.transparent = true;
  tag(redLens, "lensRed");

  const amberLens = new THREE.MeshPhysicalNodeMaterial();
  amberLens.colorNode = color(0x8a4406);
  amberLens.metalness = 0.0; amberLens.roughness = 0.10;
  amberLens.clearcoat = 1.0; amberLens.clearcoatRoughness = 0.04;
  amberLens.opacity = 0.90; amberLens.transparent = true;
  tag(amberLens, "lensAmber");

  /* -- LED emitters ----------------------------------------------------- */
  const ledCold = new THREE.MeshPhysicalNodeMaterial();
  ledCold.colorNode = color(0x0e1116);
  ledCold.emissiveNode = color(0xdfeaff).mul(0.18);
  ledCold.metalness = 0.2; ledCold.roughness = 0.22;
  tag(ledCold, "led");

  const reflector = new THREE.MeshPhysicalNodeMaterial();
  reflector.colorNode = texture(ledFace(), uv()).rgb;
  reflector.metalness = 0.92; reflector.roughness = 0.13;
  tag(reflector, "reflector");

  /* -- radiator core, screens ------------------------------------------- */
  const radCore = new THREE.MeshPhysicalNodeMaterial();
  radCore.colorNode = texture(radiatorCore(), uv().mul(vec2(6, 1))).rgb;
  radCore.metalness = 0.7; radCore.roughness = 0.62;
  tag(radCore, "radiator");

  const mesh = new THREE.MeshPhysicalNodeMaterial();
  const meshTex = meshScreen();
  mesh.colorNode = color(0x0b0d0f);
  mesh.opacityNode = texture(meshTex, uv().mul(10)).a.mul(0.92).add(0.08);
  mesh.transparent = true;
  mesh.metalness = 0.6; mesh.roughness = 0.55;
  mesh.side = THREE.DoubleSide;
  tag(mesh, "screenMesh");

  /* -- instrument face --------------------------------------------------- */
  const gauge = new THREE.MeshPhysicalNodeMaterial();
  gauge.colorNode = color(0x05060a);
  gauge.emissiveNode = color(0x0a1520).mul(0.6);
  gauge.roughness = 0.12; gauge.metalness = 0.0;
  gauge.clearcoat = 1.0; gauge.clearcoatRoughness = 0.02;
  tag(gauge, "gauge");

  /* -- decal materials (conformal patches lifted off the parent surface) - */
  const decal = (canvas, { rough = 0.20, cc = 1.0 } = {}) => {
    const m = new THREE.MeshPhysicalNodeMaterial();
    const t = canvasTexture(canvas, { srgb: true, aniso: 16, wrap: THREE.ClampToEdgeWrapping });
    m.colorNode = texture(t, uv()).rgb;
    m.opacityNode = texture(t, uv()).a;
    m.transparent = true;
    m.metalness = 0.25; m.roughness = rough;
    m.clearcoat = cc; m.clearcoatRoughness = 0.06;
    m.polygonOffset = true; m.polygonOffsetFactor = -2; m.polygonOffsetUnits = -2;
    m.side = THREE.DoubleSide;
    m.userData.slot = "decal";
    return m;
  };
  MAT.decalZX6R = decal(zx6rDecal());
  MAT.decalKawasaki = decal(kawasakiDecal(true));
  MAT.decalKawasakiDark = decal(kawasakiDecal(false), { rough: 0.28 });

  const plateFace = new THREE.MeshPhysicalNodeMaterial();
  plateFace.colorNode = color(0xd9dbde);
  plateFace.metalness = 0.0;
  plateFace.roughnessNode = float(0.38).add(wnoise(180).mul(0.06));
  plateFace.clearcoat = 0.5; plateFace.clearcoatRoughness = 0.25;
  tag(plateFace, "plate");
  MAT.decalNinja = decal(ninjaDecal());

  /* -- studio floor ------------------------------------------------------ */
  const floor = new THREE.MeshStandardNodeMaterial();
  floor.colorNode = color(0xffffff);
  floor.roughness = 0.62; floor.metalness = 0.0;
  const rad = positionWorld.xz.length();
  floor.opacityNode = rad.smoothstep(1.85, 4.60).oneMinus();
  floor.transparent = true;
  floor.userData.slot = "floor";
  MAT.floor = floor;

  return MAT;
}


export {
  MAT, TEX, buildMaterials, canvas2d, canvasTexture, decalCanvas, kawasakiDecal, keep, ledFace, makeBrushNormal, makeCarbonNormal, makeCastNormal, makeFlakeNormal, makeGrainNormal, makeKnurlNormal, makeSeatNormal, meshScreen, ninjaDecal, normalFromHeight, radiatorCore, studioEnvTexture, tileNoise, tyreMaps, zx6rDecal,
};
