import * as THREE from "three/webgpu";
import {
  color, float, fract, mix, mx_noise_float, normalWorld, positionLocal, positionWorld,
  pow, saturate, sin, smoothstep, step, texture, uniform, uv, vec2, vec3,
} from "three/tsl";
import { TAU } from "./mesh-kit.js";
import { PAL, PROJ } from "./design-contract.js";
import {
  buildCarbonTexture, buildLiverySide, buildLiveryTop, buildTyreWall, buildWheelFace,
} from "./race-car-textures.js";

/*
   MATERIALS
   One paint mechanism drives every painted panel: a two-plane livery projector whose
   plane weight comes from the world normal.  Everything else (carbon, rubber, metals,
   glass) is an explicit authored identity — no material is a tinted copy of another.
*/

const MAT = {};
const TEX = {};
const U = {
  livery:   uniform(1.0),   // paint coverage — 0 shows the bare structural finish
  projDbg:  uniform(0.0),   // projector-field diagnostic
  wear:     uniform(0.35),
  discGlow: uniform(0.18),
  sideSwap: uniform(0.0),   // which projector layer paints which flank (glyph handedness)
};

function buildMaterials(){
  TEX.side   = buildLiverySide();
  TEX.top    = buildLiveryTop();
  TEX.carbon = buildCarbonTexture(512);
  TEX.tyre   = buildTyreWall();
  TEX.face   = buildWheelFace();

  /* ---- the projector -------------------------------------------------------------- */
  const P = positionWorld, N = normalWorld;
  const uLong = float(PROJ.Z1).sub(P.z).div(PROJ.zSpan);
  const tSide = float(PROJ.Y1).sub(P.y).div(PROJ.hSpan);
  // Layer 0 (v in [0.5,1]) and layer 1 (v in [0,0.5]) differ ONLY in glyph handedness.
  // Which one belongs to which flank depends on the texture upload's Y orientation, so
  // the choice is a switch rather than an assumption.
  const sx  = step(0.0, P.x);
  const sel = mix(sx, float(1.0).sub(sx), U.sideSwap);
  const layerBase = sel.mul(0.5).add(0.5);
  const vSide = layerBase.sub(tSide);
  const uvSide = vec2(uLong, vSide);
  const vTop = float(1.0).sub(float(PROJ.X1).sub(P.x).div(PROJ.X1 * 2.0));
  const uvTop = vec2(uLong, vTop);

  const sideS = texture(TEX.side, uvSide);
  const topS  = texture(TEX.top,  uvTop);
  // normalised two-plane blend: a shoulder at 45 degrees must commit to one plane, not
  // take half the paint from each and print the graphic twice
  const wUp   = pow(saturate(N.y), 4.0);       // down-facing surfaces never take plan paint
  const wSide = pow(N.x.abs(), 4.0).add(pow(N.z.abs(), 4.0).mul(0.40));
  const topW  = wUp.div(wUp.add(wSide).add(0.0004));
  const inBand = step(0.0, uLong).mul(step(uLong, 1.0));
  // Nothing under the car is painted: a downward-facing surface low in the frame is
  // structural carbon, so the projector must not smear the flank graphics onto it.
  const underKill = smoothstep(-0.12, -0.55, N.y).mul(smoothstep(0.36, 0.17, P.y));
  const liveryRGB = mix(sideS.xyz, topS.xyz, topW);
  const liveryA   = mix(sideS.w,   topS.w,   topW)
    .mul(inBand).mul(float(1.0).sub(underKill)).mul(U.livery);

  /* ---- carbon substrate ----------------------------------------------------------- */
  const weaveUV = uv().mul(vec2(1, 1));
  const weave   = texture(TEX.carbon, weaveUV);
  const grainN  = mx_noise_float(P.mul(2.4)).mul(0.5).add(0.5);
  const flake   = mx_noise_float(P.mul(190.0)).mul(0.5).add(0.5);

  const carbonBase = mix(color(PAL.carbon), color(PAL.carbonWarm), weave.w.mul(0.85));
  const paintBase  = mix(color(PAL.bodyBlack), color(PAL.bodyGloss), grainN.mul(0.55))
    .add(color(0x20242c).mul(flake.mul(flake).mul(0.10)));

  /* ---- painted bodywork ----------------------------------------------------------- */
  function paintedBody({ name, weaveRepeat = [70, 110], base = paintBase, rough = 0.46, cc = 0.28, ccRough = 0.215, side = THREE.FrontSide }){
    const m = new THREE.MeshPhysicalNodeMaterial({ side });
    m.name = name;
    const substrate = mix(base, carbonBase, float(0.30).mul(weave.w.mul(0.6).add(0.4)));
    const col = mix(substrate, liveryRGB, liveryA);
    const dbg = mix(vec3(0.05, 0.10, 0.55), vec3(0.95, 0.42, 0.05), topW);
    m.colorNode = mix(col, dbg, U.projDbg);
    // gloss decals over satin paint; the weave adds micro-roughness where paint is thin
    m.roughnessNode = mix(
      float(rough).add(weave.w.mul(0.055)).sub(grainN.mul(0.03)),
      float(0.135),
      liveryA.mul(0.85));
    m.metalnessNode = float(0.0).add(flake.mul(flake).mul(0.05));
    m.clearcoat = cc;
    m.clearcoatRoughness = ccRough;
    const nm = TEX.carbon.clone();
    nm.needsUpdate = true;
    nm.repeat.set(weaveRepeat[0], weaveRepeat[1]);
    nm.wrapS = nm.wrapT = THREE.RepeatWrapping;
    m.normalMap = nm;
    m.normalScale = new THREE.Vector2(0.14, 0.14);
    return m;
  }

  MAT.body      = paintedBody({ name: 'body',      weaveRepeat: [46, 74] });
  MAT.bodyFine  = paintedBody({ name: 'bodyFine',  weaveRepeat: [30, 30] });
  MAT.wing      = paintedBody({ name: 'wing',      weaveRepeat: [26, 96], rough: 0.42, cc: 0.34, ccRough: 0.18, side: THREE.DoubleSide });
  MAT.plate     = paintedBody({ name: 'plate',     weaveRepeat: [18, 18], rough: 0.44, cc: 0.30, ccRough: 0.20, side: THREE.DoubleSide });

  /* ---- exposed structural carbon --------------------------------------------------- */
  function carbon({ name, repeat = [24, 24], rough = 0.30, cc = 0.85, ccr = 0.12, tint = 1.0, side = THREE.FrontSide }){
    const m = new THREE.MeshPhysicalNodeMaterial({ side });
    m.name = name;
    m.colorNode = carbonBase.mul(tint);
    m.roughnessNode = float(rough).add(weave.w.mul(0.08)).sub(grainN.mul(0.02));
    m.metalnessNode = float(0.02);
    m.clearcoat = cc; m.clearcoatRoughness = ccr;
    const nm = TEX.carbon.clone(); nm.needsUpdate = true;
    nm.repeat.set(repeat[0], repeat[1]); nm.wrapS = nm.wrapT = THREE.RepeatWrapping;
    m.normalMap = nm; m.normalScale = new THREE.Vector2(0.42, 0.42);
    return m;
  }
  MAT.carbonGloss  = carbon({ name: 'carbonGloss',  repeat: [40, 40], rough: 0.36, cc: 0.50, ccr: 0.18 });
  MAT.carbonFloor  = carbon({ name: 'carbonFloor',  repeat: [60, 130], rough: 0.40, cc: 0.45, ccr: 0.20, side: THREE.DoubleSide });
  MAT.carbonMatte  = carbon({ name: 'carbonMatte',  repeat: [30, 30], rough: 0.52, cc: 0.25, ccr: 0.4, tint: 0.86, side: THREE.DoubleSide });
  MAT.carbonDuct   = carbon({ name: 'carbonDuct',   repeat: [22, 22], rough: 0.62, cc: 0.10, ccr: 0.5, tint: 0.42, side: THREE.DoubleSide });

  /* ---- floor + diffuser take the projector too (crimson edge line) ----------------- */
  {
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'floor';
    const col = mix(carbonBase, liveryRGB, liveryA);
    m.colorNode = mix(col, mix(vec3(0.05,0.10,0.55), vec3(0.95,0.42,0.05), topW), U.projDbg);
    m.roughnessNode = mix(float(0.42).add(weave.w.mul(0.08)), float(0.20), liveryA);
    m.metalnessNode = float(0.02);
    m.clearcoat = 0.40; m.clearcoatRoughness = 0.20;
    const nm = TEX.carbon.clone(); nm.needsUpdate = true;
    nm.repeat.set(70, 150); nm.wrapS = nm.wrapT = THREE.RepeatWrapping;
    m.normalMap = nm; m.normalScale = new THREE.Vector2(0.36, 0.36);
    MAT.floor = m;
  }

  /* ---- metals ---------------------------------------------------------------------- */
  function metal({ name, col, rough, metalness = 1.0, cc = 0, ccr = 0.2 }){
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = name;
    m.colorNode = mix(color(col), color(col).mul(0.74), mx_noise_float(P.mul(34)).mul(0.5).add(0.5).mul(0.5));
    m.roughnessNode = float(rough).add(mx_noise_float(P.mul(80)).mul(0.5).add(0.5).mul(0.09));
    m.metalness = metalness;
    m.clearcoat = cc; m.clearcoatRoughness = ccr;
    return m;
  }
  MAT.titanium  = metal({ name: 'titanium', col: 0x5e6167, rough: 0.46 });
  MAT.steel     = metal({ name: 'steel',    col: PAL.steel,    rough: 0.18 });
  MAT.darkAlloy = metal({ name: 'darkAlloy',col: 0x3a3d43,     rough: 0.40 });
  MAT.gold      = metal({ name: 'gold',     col: PAL.goldTint, rough: 0.26 });
  MAT.anodRed   = metal({ name: 'anodRed',  col: 0x8e1024,     rough: 0.22, cc: 0.6, ccr: 0.15 });
  MAT.anodBlue  = metal({ name: 'anodBlue', col: 0x1d2f4a,     rough: 0.25 });

  /* heat-tinted inconel exhaust: temperature runs along the pipe */
  {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'exhaust';
    const heat = saturate(P.z.add(1.60).mul(-1.6));
    const c1 = color(0x6a6560), c2 = color(0x7d5a44), c3 = color(0x4a5a72);
    m.colorNode = mix(mix(c1, c2, saturate(heat.mul(1.7))), c3, saturate(heat.sub(0.55).mul(2.0)));
    m.roughnessNode = float(0.30).add(mx_noise_float(P.mul(120)).mul(0.5).add(0.5).mul(0.18));
    m.metalness = 1.0;
    MAT.exhaust = m;
  }

  /* ---- rubber ---------------------------------------------------------------------- */
  {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'rubber';
    const wall = texture(TEX.tyre, uv());
    const grain = mx_noise_float(positionLocal.mul(320)).mul(0.5).add(0.5);
    const base = mix(color(PAL.tyre), color(PAL.tyreShoulder), grain.mul(0.7));
    // v ~ 0.5 is the crown: scuffed, slightly glossier than the sidewalls
    const crown = smoothstep(0.30, 0.46, uv().y).mul(smoothstep(0.70, 0.54, uv().y));
    m.colorNode = mix(base, wall.xyz.add(base.mul(0.35)), wall.xyz.length().mul(1.4).clamp(0, 1))
      .mul(float(1.0).add(crown.mul(0.16)));
    m.roughnessNode = float(0.86).sub(crown.mul(0.24)).sub(grain.mul(0.10));
    m.metalness = 0.0;
    m.sheen = 0.35; m.sheenRoughness = 0.75;
    m.sheenColor = new THREE.Color(0x3a3a3e);
    m.clearcoat = 0.10; m.clearcoatRoughness = 0.65;
    MAT.rubber = m;
  }
  /* Mirroring the wheel geometry mirrors its UVs too, so one flank needs the sidewall
     wordmark sampled in reverse or the moulded lettering reads backwards. */
  {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'rubber.mirror';
    const flipUV = vec2(float(1.0).sub(uv().x), uv().y);
    const wall = texture(TEX.tyre, flipUV);
    const grain = mx_noise_float(positionLocal.mul(320)).mul(0.5).add(0.5);
    const base = mix(color(PAL.tyre), color(PAL.tyreShoulder), grain.mul(0.7));
    const crown = smoothstep(0.30, 0.46, uv().y).mul(smoothstep(0.70, 0.54, uv().y));
    m.colorNode = mix(base, wall.xyz.add(base.mul(0.35)), wall.xyz.length().mul(1.4).clamp(0, 1))
      .mul(float(1.0).add(crown.mul(0.16)));
    m.roughnessNode = float(0.86).sub(crown.mul(0.24)).sub(grain.mul(0.10));
    m.metalness = 0.0;
    m.sheen = 0.35; m.sheenRoughness = 0.75;
    m.sheenColor = new THREE.Color(0x3a3a3e);
    m.clearcoat = 0.10; m.clearcoatRoughness = 0.65;
    MAT.rubberMirror = m;
  }

  /* ---- wheel rim & aero cover ------------------------------------------------------ */
  {
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'rim';
    const ring = mx_noise_float(positionLocal.mul(70)).mul(0.5).add(0.5);
    m.colorNode = mix(color(0x121317), color(0x1e2025), ring.mul(0.55));
    m.roughnessNode = float(0.56).add(ring.mul(0.10));
    m.metalness = 0.55;
    m.clearcoat = 0.15; m.clearcoatRoughness = 0.40;
    MAT.rim = m;
  }
  {
    // lathe UV: u runs around the rim, v across the profile — no angle reconstruction needed
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'rimCover';
    const r = vec2(positionLocal.y, positionLocal.z).length();
    const spoke = sin(uv().x.mul(TAU * 10.0)).mul(0.5).add(0.5);
    const vane  = smoothstep(0.42, 0.46, fract(uv().x.mul(20.0)));
    m.colorNode = mix(color(0x0a0b0e), color(0x2b2e35), spoke.mul(smoothstep(0.070, 0.19, r)).mul(0.9).add(vane.mul(0.22)));
    m.roughnessNode = float(0.50).add(spoke.mul(0.08));
    m.metalness = 0.20;
    m.clearcoat = 0.30; m.clearcoatRoughness = 0.30;
    MAT.rimCover = m;
  }

  /* ---- carbon-carbon brake disc, hot ----------------------------------------------- */
  {
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'brakeDisc';
    const r = vec2(positionLocal.y, positionLocal.z).length();
    const rings = sin(r.mul(430.0)).mul(0.5).add(0.5);
    const drilled = sin(uv().x.mul(TAU * 36.0)).mul(0.5).add(0.5);
    const heat = smoothstep(0.075, 0.155, r).mul(U.discGlow);
    m.colorNode = mix(color(0x2a2724), color(0x413a34), rings.mul(0.6).add(drilled.mul(0.2)));
    m.emissiveNode = color(PAL.brakeGlow).mul(heat.mul(2.4));
    m.roughnessNode = float(0.60).sub(rings.mul(0.10));
    m.metalness = 0.15;
    MAT.brakeDisc = m;
  }

  /* ---- glass, lenses, lights -------------------------------------------------------- */
  {
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'visor';
    m.colorNode = color(0x0b0d10);
    m.roughness = 0.045; m.metalness = 0.0;
    m.transmission = 0.72; m.ior = 1.52; m.thickness = 0.006;
    m.attenuationColor = new THREE.Color(0x1a1208);
    m.attenuationDistance = 0.02;
    m.clearcoat = 1.0; m.clearcoatRoughness = 0.02;
    m.iridescence = 0.55; m.iridescenceIOR = 1.9; m.iridescenceThicknessRange = [180, 520];
    MAT.visor = m;
  }
  {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'mirror';
    m.colorNode = color(0xdfe4ea);
    m.roughness = 0.035; m.metalness = 1.0;
    MAT.mirror = m;
  }
  {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'lens';
    m.colorNode = color(0x05070b);
    m.roughness = 0.03; m.metalness = 0.1;
    m.clearcoat = 1.0; m.clearcoatRoughness = 0.02;
    MAT.lens = m;
  }
  {
    const m = new THREE.MeshStandardNodeMaterial();
    m.name = 'rainLight';
    const grid = step(0.35, fract(uv().x.mul(9.0))).mul(step(0.30, fract(uv().y.mul(4.0))));
    m.colorNode = color(0x3a0208);
    m.emissiveNode = color(PAL.rainLight).mul(grid.mul(9.0).add(0.35));
    m.roughness = 0.35; m.metalness = 0.0;
    MAT.rainLight = m;
  }
  {
    const m = new THREE.MeshBasicNodeMaterial();
    m.name = 'display';
    m.colorNode = texture(TEX.face, uv()).mul(1.6);
    MAT.display = m;
  }

  /* ---- driver ---------------------------------------------------------------------- */
  MAT.helmet = (() => {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'helmet';
    const band = smoothstep(0.40, 0.44, uv().y).mul(smoothstep(0.62, 0.58, uv().y));
    const crest = smoothstep(0.72, 0.76, uv().y);
    m.colorNode = mix(mix(color(PAL.helmetWhite), color(PAL.red), band), color(PAL.carbon), crest.mul(0.85));
    m.roughnessNode = float(0.10);
    m.metalness = 0.0; m.clearcoat = 1.0; m.clearcoatRoughness = 0.03;
    return m;
  })();
  MAT.suit = (() => {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'suit';
    const n = mx_noise_float(positionLocal.mul(220)).mul(0.5).add(0.5);
    m.colorNode = mix(color(0x15161a), color(0x24262b), n);
    m.roughnessNode = float(0.80).sub(n.mul(0.10));
    m.metalness = 0.0; m.sheen = 0.5; m.sheenRoughness = 0.8;
    m.sheenColor = new THREE.Color(0x585c62);
    return m;
  })();
  MAT.padding = (() => {
    const m = new THREE.MeshPhysicalNodeMaterial({ side: THREE.DoubleSide });
    m.name = 'padding';
    const n = mx_noise_float(positionLocal.mul(90)).mul(0.5).add(0.5);
    m.colorNode = mix(color(0x101115), color(0x1c1e23), n);
    m.roughnessNode = float(0.90).sub(n.mul(0.08));
    m.metalness = 0.0;
    return m;
  })();

  /* skid block: jabroc/wood composite under the plank */
  MAT.plank = (() => {
    const m = new THREE.MeshPhysicalNodeMaterial();
    m.name = 'plank';
    const g = mx_noise_float(P.mul(vec3(6, 6, 90))).mul(0.5).add(0.5);
    m.colorNode = mix(color(0x6a5540), color(0x3f3323), g).mul(float(1.0).sub(U.wear.mul(0.35)));
    m.roughnessNode = float(0.72).sub(g.mul(0.12));
    m.metalness = 0.0;
    return m;
  })();

  MAT.wireframe = new THREE.MeshBasicNodeMaterial({ wireframe: true, transparent: true, opacity: 0.55 });
  MAT.wireframe.colorNode = color(0x0e3d2a);

  return MAT;
}

export { MAT, TEX, U, buildMaterials };
