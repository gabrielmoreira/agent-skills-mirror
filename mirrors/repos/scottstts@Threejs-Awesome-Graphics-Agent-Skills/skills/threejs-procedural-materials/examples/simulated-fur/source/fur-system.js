import * as THREE from "three/webgpu";
import {
  Fn, If, Loop, uniform, instancedArray, storage, instanceIndex, attribute,
  varying, cameraPosition, vec3, vec4, float, int, normalize, mix, dot, cross,
  length, max, min, smoothstep, pow, sqrt, saturate, sin, cos, abs, hash, time,
  clamp, exp, fract, floor, step,
} from "three/tsl";
import { mergeVertices } from "three/addons/utils/BufferGeometryUtils.js";
import {
  AREA, BODY_C, EYES, FLOOR, HEAD_C, HS, NECK, NOSE, PAWS, PARTS,
  P, S, SH, bodyPattern, bodyShape, nrm3, pattern, pawShape, shape, starGeo,
  sstep, surf, tailGeo,
} from "./fur-geometry.js";

export const FUR_LIGHT_RIG = [
  { direction: [-0.55, 0.78, 0.62], color: [1.0, 0.9, 0.76], intensity: 2.1 },
  { direction: [0.85, 0.2, 0.55], color: [0.84, 0.88, 1.0], intensity: 0.5 },
  { direction: [0.35, 0.6, -0.9], color: [1.0, 0.93, 0.84], intensity: 1.6 },
];

const COAT = {
  main: "#f2903b",
  cream: "#fff3e2",
  stripe: "#c8521a",
  blush: "#ff8b9c",
};

/**
 * Creates the groomed creature, simulated strand field, and interactive hand.
 * The host supplies an initialized WebGPU renderer, scene, camera, orbit
 * controls, and the room environment used by the facial materials.
 */
export function createSimulatedFur({ renderer, scene, camera, controls, envMap }) {
  if (!renderer?.compute || !scene || !camera || !controls) {
    throw new Error("Pass an initialized WebGPU renderer, scene, camera, and controls.");
  }

  const LIGHTS = FUR_LIGHT_RIG.map((light) => ({
    dir: new THREE.Vector3(...light.direction).normalize(),
    col: new THREE.Color(...light.color),
    i: light.intensity,
  }));
  const envTex = envMap ?? null;
  const proxies = [];
  const baseMeshes = [];

const uMain = uniform(new THREE.Color(COAT.main));
const uCream = uniform(new THREE.Color(COAT.cream));
const uStripe = uniform(new THREE.Color(COAT.stripe));
const uBlush = uniform(new THREE.Color(COAT.blush));

// ─────────────────────────────────────────────────────────────
// Creature body + face
// ─────────────────────────────────────────────────────────────
const creature = new THREE.Group();
scene.add(creature);

const bodyGroup = new THREE.Group();            // body, paws, tail
const headPivot = new THREE.Group();            // turns at the neck
const headInner = new THREE.Group();            // head space
creature.add(bodyGroup, headPivot);
headPivot.position.set(...NECK);
headPivot.add(headInner);
headInner.position.set(HEAD_C[0] - NECK[0], HEAD_C[1] - NECK[1], HEAD_C[2] - NECK[2]);
headInner.scale.setScalar(SH);

const skinPat = attribute('aPattern', 'vec4');
const skinMat = new THREE.MeshStandardNodeMaterial({ roughness: 0.95, metalness: 0, side: THREE.DoubleSide });
skinMat.colorNode = mix(mix(mix(uMain, uStripe, skinPat.y), uCream, skinPat.x), uBlush, skinPat.w).mul(0.3);
const proxyMat = new THREE.MeshBasicMaterial({
  color: 0x26c6ad,
  side: THREE.DoubleSide,
  wireframe: true,
  transparent: true,
  opacity: 0.48,
  depthWrite: false,
});
function addPart(parent, geo, proxyGeo) {
  const m = new THREE.Mesh(geo, skinMat);
  baseMeshes.push(m);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  const px = new THREE.Mesh(proxyGeo, proxyMat);
  px.visible = false;
  parent.add(px);
  proxies.push(px);
}
addPart(headInner, starGeo(shape, 220, 160, (d, p, o) => pattern(d, o)), starGeo(shape, 64, 48));
addPart(bodyGroup, starGeo(bodyShape, 160, 120, bodyPattern), starGeo(bodyShape, 48, 36));
for (const c of PAWS) addPart(bodyGroup, starGeo(pawShape(c), 48, 32, (d, p, o) => { o[0] = 1; o[1] = o[2] = o[3] = 0; }), starGeo(pawShape(c), 20, 14));
addPart(bodyGroup, tailGeo(220, 24, true), tailGeo(60, 10, false));

function placeOn(obj, dir, lift) {
  const s = surf(...nrm3(...dir));
  obj.position.set(s.p[0] + s.n[0] * lift, s.p[1] + s.n[1] * lift, s.p[2] + s.n[2] * lift);
  obj.lookAt(obj.position.x + s.n[0], obj.position.y + s.n[1], obj.position.z + s.n[2]);
  return obj;
}

const eyeMat = new THREE.MeshPhysicalMaterial({ color: 0x0c0806, roughness: 0.1, clearcoat: 1, clearcoatRoughness: 0.03, envMap: envTex, envMapIntensity: 0.9 });
const glintMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.3, 1.3, 1.3), toneMapped: false });
const lineMat = new THREE.MeshStandardMaterial({ color: 0x33201c, roughness: 0.6 });
const eyeGeo = new THREE.SphereGeometry(1, 48, 32);
const glintGeo = new THREE.SphereGeometry(1, 20, 14);
const arcGeo = new THREE.TorusGeometry(0.07, 0.013, 10, 40, Math.PI);

const eyes = [], arcs = [];
for (const E of EYES) {
  const root = placeOn(new THREE.Group(), E, 0.012);
  const ball = new THREE.Mesh(eyeGeo, eyeMat);
  ball.scale.set(0.1, 0.125, 0.075);
  root.add(ball);
  const g1 = new THREE.Mesh(glintGeo, glintMat); g1.scale.set(0.024, 0.024, 0.01); g1.position.set(-0.034, 0.045, 0.066);
  const g2 = new THREE.Mesh(glintGeo, glintMat); g2.scale.set(0.011, 0.011, 0.006); g2.position.set(0.03, -0.036, 0.068);
  root.add(g1, g2);
  headInner.add(root);
  eyes.push(root);
  const arcRoot = placeOn(new THREE.Group(), E, 0.03);
  const arc = new THREE.Mesh(arcGeo, lineMat);
  arc.position.y = -0.03;
  arcRoot.add(arc);
  arcRoot.scale.setScalar(0.001);
  arcRoot.visible = false;
  headInner.add(arcRoot);
  arcs.push(arcRoot);
}

const noseGeo = new THREE.SphereGeometry(1, 32, 24);
{
  const p = noseGeo.attributes.position;
  for (let i = 0; i < p.count; i++) p.setX(i, p.getX(i) * (0.6 + 0.4 * (p.getY(i) * 0.5 + 0.5)));
  noseGeo.computeVertexNormals();
}
const nose = placeOn(new THREE.Group(), NOSE, 0.03);
const noseMesh = new THREE.Mesh(noseGeo, new THREE.MeshPhysicalMaterial({ color: 0xff7f98, roughness: 0.32, clearcoat: 0.6, clearcoatRoughness: 0.2, envMap: envTex, envMapIntensity: 0.6 }));
noseMesh.scale.set(0.072, 0.05, 0.048);
nose.add(noseMesh);
headInner.add(nose);

function facePoint(x, y, lift) {
  const s = surf(...nrm3(x, y, 1));
  return new THREE.Vector3(s.p[0] + s.n[0] * lift, s.p[1] + s.n[1] * lift, s.p[2] + s.n[2] * lift);
}
const mouthCurve = new THREE.CatmullRomCurve3([
  facePoint(-0.1, -0.165, 0.022), facePoint(-0.05, -0.215, 0.022), facePoint(0, -0.172, 0.022),
  facePoint(0.05, -0.215, 0.022), facePoint(0.1, -0.165, 0.022),
]);
headInner.add(new THREE.Mesh(new THREE.TubeGeometry(mouthCurve, 48, 0.0085, 8, false), lineMat));
const philtrum = new THREE.LineCurve3(facePoint(0, -0.105, 0.022), facePoint(0, -0.172, 0.022));
headInner.add(new THREE.Mesh(new THREE.TubeGeometry(philtrum, 4, 0.0075, 8, false), lineMat));

// soft contact shadow

function taperCapsule(r0, r1, len, radial = 28, cap = 7) {
  const pts = [];
  for (let i = 0; i <= cap; i++) { const a = -Math.PI / 2 + (i / cap) * Math.PI / 2; pts.push(new THREE.Vector2(Math.max(1e-4, Math.cos(a) * r0), Math.sin(a) * r0)); }
  for (let i = 0; i <= cap; i++) { const a = (i / cap) * Math.PI / 2; pts.push(new THREE.Vector2(Math.max(1e-4, Math.cos(a) * r1), len + Math.sin(a) * r1)); }
  const g = new THREE.LatheGeometry(pts, radial);
  g.rotateX(-Math.PI / 2);          // +Y axis -> -Z
  g.scale(1, 0.86, 1);              // fingers are a bit flatter than round
  return g;
}

const handSkin = new THREE.MeshPhysicalMaterial({
  color: 0xe8b294, roughness: 0.52, sheen: 0.6, sheenRoughness: 0.55, sheenColor: new THREE.Color(0xffb8a0),
  clearcoat: 0.06, clearcoatRoughness: 0.6, emissive: 0x3a120a, emissiveIntensity: 0.35,
});
const nailMat = new THREE.MeshPhysicalMaterial({ color: 0xf6d2c8, roughness: 0.25, clearcoat: 0.8, clearcoatRoughness: 0.1 });
const sleeveMat = new THREE.MeshPhysicalMaterial({ color: 0x55786a, roughness: 1, sheen: 1, sheenRoughness: 0.45, sheenColor: new THREE.Color(0xb9d6c6), side: THREE.DoubleSide });

const handRig = new THREE.Group();
const handCaps = [];                 // collider capsules in bone space: { obj, a, b, r }
const chains = [];
scene.add(handRig);

{
  // palm: rounded superellipsoid, domed on the back, tapering to the wrist
  let g = new THREE.SphereGeometry(1, 72, 48);
  g.deleteAttribute('normal'); g.deleteAttribute('uv');
  g = mergeVertices(g);
  const p = g.attributes.position;
  const sp = (v, e) => Math.sign(v) * Math.pow(Math.abs(v), e);
  for (let i = 0; i < p.count; i++) {
    let X = sp(p.getX(i), 0.6) * 0.5, Y = sp(p.getY(i), 0.85) * 0.16, Z = sp(p.getZ(i), 0.6) * 0.56;
    X *= 1 - 0.16 * Math.max(0, Z / 0.56);
    if (Y > 0) Y *= 1 + 0.3 * (1 - (X / 0.5) ** 2);
    Y *= 1 + 0.18 * Math.max(0, -Z / 0.56);
    X -= 0.03 * Math.max(0, -Z / 0.56);
    p.setXYZ(i, X, Y, Z);
  }
  g.computeVertexNormals();
  handRig.add(new THREE.Mesh(g, handSkin));
  for (const x of [-0.3, 0, 0.3]) handCaps.push({ obj: handRig, a: new THREE.Vector3(x, -0.01, 0.35), b: new THREE.Vector3(x, -0.01, -0.42), r: 0.17 });

  // thenar (thumb muscle)
  const th = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 24), handSkin);
  th.scale.set(0.2, 0.12, 0.3);
  th.position.set(-0.3, -0.06, 0.14);
  th.rotation.y = 0.45;
  handRig.add(th);

  const chain = (pos, yaw, pitch, roll, radii, lens, weights) => {
    const joints = [];
    let parent = handRig;
    for (let i = 0; i < 3; i++) {
      const j = new THREE.Group();
      j.rotation.order = 'YXZ';
      if (i === 0) { j.position.copy(pos); j.rotation.set(pitch, yaw, roll); }
      else j.position.set(0, 0, -lens[i - 1]);
      parent.add(j);
      j.add(new THREE.Mesh(taperCapsule(radii[i], radii[i + 1], lens[i]), handSkin));
      handCaps.push({ obj: j, a: new THREE.Vector3(), b: new THREE.Vector3(0, 0, -lens[i]), r: Math.max(radii[i], radii[i + 1]) });
      joints.push(j);
      parent = j;
    }
    const r2 = radii[2], L2 = lens[2];
    const nail = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), nailMat);
    nail.scale.set(r2 * 0.72, r2 * 0.2, L2 * 0.5);
    nail.position.set(0, r2 * 0.64, -L2 * 0.68);
    nail.rotation.x = 0.08;
    joints[2].add(nail);
    const c = { joints, lens, pitch, tipR: radii[3], curl: 0.3, weights, ph: Math.random() * 6.28 };
    chains.push(c);
    return c;
  };
  const W = [0.5, 0.32, 0.18];
  chain(new THREE.Vector3(-0.3, 0.02, -0.42), 0.07, -0.04, 0, [0.105, 0.098, 0.091, 0.084], [0.44, 0.27, 0.21], W);   // index
  chain(new THREE.Vector3(-0.09, 0.03, -0.46), 0.0, -0.04, 0, [0.11, 0.102, 0.095, 0.088], [0.49, 0.31, 0.23], W);   // middle
  chain(new THREE.Vector3(0.12, 0.02, -0.44), -0.05, -0.04, 0, [0.103, 0.096, 0.089, 0.082], [0.46, 0.29, 0.22], W); // ring
  chain(new THREE.Vector3(0.31, 0.0, -0.38), -0.14, -0.04, 0, [0.088, 0.082, 0.076, 0.07], [0.35, 0.22, 0.19], W);   // pinky
  const thumb = chain(new THREE.Vector3(-0.38, -0.07, 0.12), 0.85, -0.28, -0.7, [0.14, 0.126, 0.114, 0.1], [0.3, 0.27, 0.23], [0.25, 0.4, 0.35]);
  thumb.isThumb = true;

  // wrist + forearm, then a chunky knit sleeve
  const arm = new THREE.Group();
  arm.position.set(0, 0.03, 0.38);
  arm.rotation.x = -0.26;
  handRig.add(arm);
  const fa = taperCapsule(0.25, 0.4, 6.5, 32, 6);
  fa.rotateY(Math.PI);
  fa.scale(1.3, 0.92, 1);
  arm.add(new THREE.Mesh(fa, handSkin));

  const sl = new THREE.CylinderGeometry(0.55, 0.47, 6, 96, 120, true);
  sl.rotateX(Math.PI / 2);            // axis along Z, radiusTop at +Z
  const sp2 = sl.attributes.position;
  for (let i = 0; i < sp2.count; i++) {
    const x = sp2.getX(i), y = sp2.getY(i), z = sp2.getZ(i);
    const a = Math.atan2(y, x), rr = Math.hypot(x, y);
    const zz = z + 3;                  // 0 at cuff
    const cuff = 1 - sstep(0.65, 0.8, zz);
    const rib = 0.028 * (0.5 + 0.5 * Math.cos(a * 26)) * cuff;
    const knit = 0.012 * Math.abs(Math.sin(a * 22 + Math.abs(Math.sin(zz * 34)) * 1.4)) * (1 - cuff);
    const s = (rr + rib + knit + 0.02 * cuff) / rr;
    sp2.setXYZ(i, x * s * 1.18, y * s * 0.95, z + 3 + 0.55);
  }
  sl.computeVertexNormals();
  arm.add(new THREE.Mesh(sl, sleeveMat));
  const lip = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.055, 14, 96), sleeveMat);
  lip.scale.set(1.18, 0.95, 1);
  lip.position.z = 0.56;
  arm.add(lip);

  handRig.traverse(o => { if (o.isMesh) o.castShadow = true; });
  handRig.scale.setScalar(HS);
  handRig.visible = false;
}

// ─────────────────────────────────────────────────────────────
// Grow strands (CPU, once)
// ─────────────────────────────────────────────────────────────
const rootArr = new Float32Array(S * 4);   // xyz root, w length
const nrmArr = new Float32Array(S * 4);    // xyz normal, w random
const flowArr = new Float32Array(S * 4);   // xyz groom direction, w bend
const patArr = new Float32Array(S * 4);    // cream, stripe, tip, blush
const posArr = new Float32Array(S * P * 4);

const pat = [0, 0, 0, 0];
for (let s = 0; s < S;) {
  // pick a part by area, then an area-uniform point on it
  let pick = Math.random() * AREA, part = PARTS[0];
  for (const pp of PARTS) { if (pick < pp.area) { part = pp; break; } pick -= pp.area; }
  const sf = part.sample();
  if (Math.random() * part.maxJ > sf.J) continue;
  if (part.cull(sf.pb)) continue;
  const r1 = Math.random(), r2 = Math.random(), r3 = Math.random();
  const { len, F, bend } = sf.groom(r1, r2, r3, pat);
  const n = sf.n, p = sf.p;
  rootArr.set([p[0], p[1], p[2], len], s * 4);
  nrmArr.set([n[0], n[1], n[2], r1 + (part.head ? 2 : 0)], s * 4);   // w: random, +2 flags head space
  flowArr.set([F[0], F[1], F[2], bend], s * 4);
  patArr.set(pat, s * 4);
  // rest pose in world (mirrors the solver's rest shape)
  let x = sf.pb[0], y = sf.pb[1], z = sf.pb[2];
  const seg = len / (P - 1);
  posArr.set([x, y, z, 1], s * P * 4);
  for (let i = 1; i < P; i++) {
    const t = i / (P - 1);
    const th = Math.min(bend * (0.45 + 0.8 * t), 1.45);
    const c = Math.cos(th), sn = Math.sin(th);
    x += (n[0] * c + F[0] * sn) * seg;
    y += (n[1] * c + F[1] * sn) * seg;
    z += (n[2] * c + F[2] * sn) * seg;
    y = Math.max(y, FLOOR);
    posArr.set([x, y, z, 1], (s * P + i) * 4);
  }
  s++;
}

// ─────────────────────────────────────────────────────────────
// GPU buffers + simulation (compute)
// ─────────────────────────────────────────────────────────────
const rootBuf = instancedArray(rootArr, 'vec4');
const nrmBuf = instancedArray(nrmArr, 'vec4');
const flowBuf = instancedArray(flowArr, 'vec4');
const combBuf = instancedArray(new Float32Array(S * 4), 'vec4');   // groom memory from petting
const posBuf = instancedArray(posArr, 'vec4');
const prevBuf = instancedArray(posArr.slice(), 'vec4');

const uHeadModel = uniform(new THREE.Matrix4());
const uBodyModel = uniform(new THREE.Matrix4());
const uHandBound = uniform(new THREE.Vector4(0, 1e3, 0, 0.01));
const capU = handCaps.map(() => ({
  a: uniform(new THREE.Vector4(0, 1e3, 0, 0.01)),   // xyz start, w radius
  b: uniform(new THREE.Vector3(0, 1e3, 0)),
  d: uniform(new THREE.Vector3()),                    // this frame's motion
}));
const uFriction = uniform(0.3);
const uCombGain = uniform(1.4);
const uCombDecay = uniform(0.994);
const uDamping = uniform(0.9);
const uGravity = uniform(new THREE.Vector3(0, -1.6 / 3600, 0));
const uStiffRoot = uniform(0.42);
const uStiffTip = uniform(0.14);
const uFloor = uniform(FLOOR);
const uWind = uniform(0.00022);
const uKink = uniform(0.16);

const simulate = Fn(() => {
  const s = int(instanceIndex);
  const base = s.mul(P);
  const rd = rootBuf.element(s);
  const nd = nrmBuf.element(s);
  const fd = flowBuf.element(s);

  const isHead = step(float(1.5), nd.w);
  const xf = (v, w) => mix(uBodyModel.mul(vec4(v, w)).xyz, uHeadModel.mul(vec4(v, w)).xyz, isHead);
  const root = xf(rd.xyz, 1).toVar();
  const N = normalize(xf(nd.xyz, 0)).toVar();
  const F0 = normalize(xf(fd.xyz, 0)).toVar();
  const bend = fd.w;
  const segLen = rd.w.div(P - 1).toVar();
  const comb = combBuf.element(s).xyz.mul(uCombDecay).toVar();

  posBuf.element(base).assign(vec4(root, 1));
  prevBuf.element(base).assign(vec4(root, 1));

  const gust = sin(time.mul(1.3).add(root.x.mul(3.0)).add(root.z.mul(2.0))).mul(0.5).add(0.5)
    .mul(sin(time.mul(0.37).add(root.y.mul(1.7))).mul(0.5).add(0.5));
  const parent = root.toVar();

  Loop({ start: 1, end: P, type: 'int', condition: '<' }, ({ i }) => {
    const idx = base.add(i);
    const t = float(i).div(P - 1);
    const p = posBuf.element(idx).xyz.toVar();
    const pp = prevBuf.element(idx).xyz;

    // verlet
    const newP = p.add(p.sub(pp).mul(uDamping)).add(uGravity).toVar();
    newP.addAssign(vec3(0.7, 0.0, 0.35).mul(uWind.mul(gust).mul(t)));

    // rest shape (angular spring toward groomed direction, bent by petting memory)
    const Fc = F0.add(comb);
    const Ft = Fc.sub(N.mul(dot(Fc, N)));
    const Fn_ = Ft.div(max(length(Ft), 1e-5));
    const theta = min(bend.mul(mix(float(0.45), float(1.25), t)).add(length(comb).mul(0.5).mul(t)), float(1.45));
    const jitter = vec3(hash(idx), hash(idx.add(7919)), hash(idx.add(15731))).sub(0.5).mul(uKink);
    const restRaw = N.mul(cos(theta)).add(Fn_.mul(sin(theta))).add(jitter);
    const restDir = restRaw.div(max(length(restRaw), 1e-5));
    const target = parent.add(restDir.mul(segLen));
    newP.assign(mix(newP, target, mix(uStiffRoot, uStiffTip, t)));

    // hand contact (palm, finger bones, thumb as capsules): collide, drag by friction, leave a groomed trail
    If(length(newP.sub(uHandBound.xyz)).lessThan(uHandBound.w), () => {
      for (const C of capU) {
        const A = C.a.xyz, R = C.a.w;
        const ab = C.b.sub(A);
        const hq = clamp(dot(newP.sub(A), ab).div(max(dot(ab, ab), 1e-8)), 0, 1);
        const q = A.add(ab.mul(hq));
        const toH = newP.sub(q);
        const dH = length(toH);
        If(dH.lessThan(R), () => {
          newP.assign(q.add(toH.div(max(dH, 1e-5)).mul(R)));
          newP.addAssign(C.d.mul(uFriction));
          const tang = C.d.sub(N.mul(dot(C.d, N)));
          comb.addAssign(tang.mul(uCombGain));
        });
      }
    });

    // stay above skin + floor
    const h = dot(newP.sub(root), N);
    const minH = segLen.mul(float(i)).mul(0.1);
    If(h.lessThan(minH), () => { newP.addAssign(N.mul(minH.sub(h))); });
    newP.assign(vec3(newP.x, max(newP.y, uFloor), newP.z));

    // inextensible segment
    const dv = newP.sub(parent);
    newP.assign(parent.add(dv.div(max(length(dv), 1e-6)).mul(segLen)));

    prevBuf.element(idx).assign(vec4(p, 1));
    posBuf.element(idx).assign(vec4(newP, 1));
    parent.assign(newP);
  });

  const cl = length(comb);
  combBuf.element(s).assign(vec4(comb.mul(min(float(1), float(1.3).div(max(cl, 1e-4)))), 0));
});
const simNode = simulate().compute(S);

// ─────────────────────────────────────────────────────────────
// Strand rendering: camera-facing tapered ribbons + hair shading
// ─────────────────────────────────────────────────────────────
const hairGeo = new THREE.InstancedBufferGeometry();
{
  const vcount = P * 2;
  hairGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vcount * 3), 3));
  const seg = new Float32Array(vcount), side = new Float32Array(vcount);
  for (let i = 0; i < P; i++) { seg[i * 2] = seg[i * 2 + 1] = i; side[i * 2] = -1; side[i * 2 + 1] = 1; }
  hairGeo.setAttribute('seg', new THREE.BufferAttribute(seg, 1));
  hairGeo.setAttribute('side', new THREE.BufferAttribute(side, 1));
  const idx = [];
  for (let i = 0; i < P - 1; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  hairGeo.setIndex(idx);
  hairGeo.setAttribute('aNormal', new THREE.InstancedBufferAttribute(nrmArr, 4));
  hairGeo.setAttribute('aPattern', new THREE.InstancedBufferAttribute(patArr, 4));
  hairGeo.instanceCount = S;
  hairGeo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 4);
}

const posRead = storage(posBuf.value, 'vec4', S * P).toReadOnly();
const uWidth = uniform(0.0034);

const segA = attribute('seg', 'float');
const sideA = attribute('side', 'float');
const hBase = int(instanceIndex).mul(P);
const pCur = posRead.element(hBase.add(int(segA))).xyz;
const pNext = posRead.element(hBase.add(int(min(segA.add(1), float(P - 1))))).xyz;
const pPrev = posRead.element(hBase.add(int(max(segA.sub(1), float(0))))).xyz;
const tv = pNext.sub(pPrev);
const hT = tv.div(max(length(tv), 1e-6));
const toCam = normalize(cameraPosition.sub(pCur));
const sc = cross(hT, toCam);
const sideDir = sc.div(max(length(sc), 1e-4));
const along = segA.div(P - 1);
const hWorld = pCur.add(sideDir.mul(sideA.mul(uWidth.mul(mix(float(1.0), float(0.15), along)))));
const aNrm = attribute('aNormal', 'vec4');
const hNrm = normalize(mix(uBodyModel.mul(vec4(aNrm.xyz, 0)).xyz, uHeadModel.mul(vec4(aNrm.xyz, 0)).xyz, step(float(1.5), aNrm.w)));

const vTan = varying(hT, 'vTan');
const vAlong = varying(along, 'vAlong');
const vSide = varying(sideA, 'vSide');
const vPos = varying(hWorld, 'vPosW');
const vNrm = varying(hNrm, 'vNrmW');

const uSky = uniform(new THREE.Color(0.46, 0.48, 0.53));
const uGround = uniform(new THREE.Color(0.24, 0.2, 0.17));
const lightU = LIGHTS.map(L => ({ dir: uniform(L.dir.clone()), col: uniform(L.col.clone().multiplyScalar(L.i)) }));

const uHandOcc = uniform(new THREE.Vector4(0, 1e3, 0, 0));   // xyz under-palm point, w strength
const furShade = Fn(() => {
  const T = normalize(vTan).toVar();
  const N = normalize(vNrm).toVar();
  const V = normalize(cameraPosition.sub(vPos)).toVar();
  const t = vAlong;
  const pt = attribute('aPattern', 'vec4');
  const rnd = fract(attribute('aNormal', 'vec4').w);

  const base = mix(uMain, uStripe, pt.y).toVar();
  base.assign(mix(base, uCream, pt.x));
  base.assign(mix(base, uStripe.mul(0.4), pt.z));
  base.assign(mix(base, uBlush, pt.w));
  const albedo = base.mul(mix(float(0.78), float(1.12), rnd)).mul(mix(float(0.45), float(0.95), pow(t, 0.6))).toVar();
  const ao = mix(float(0.06), float(1.0), pow(t, 1.1));

  const col = albedo.mul(mix(uGround, uSky, N.y.mul(0.5).add(0.5))).mul(ao).toVar();
  const edge = float(1).sub(abs(dot(N, V)));

  for (const L of lightU) {
    const Ld = L.dir;
    const TL = dot(T, Ld);
    const sinTL = sqrt(saturate(float(1).sub(TL.mul(TL))));
    const vis = smoothstep(float(-0.4), float(0.55), dot(N, Ld)).mul(mix(float(0.22), float(1.0), t));
    const H = normalize(Ld.add(V));
    const th1 = dot(normalize(T.add(N.mul(-0.1))), H);
    const th2 = dot(normalize(T.add(N.mul(0.15))), H);
    const specR = pow(saturate(float(1).sub(th1.mul(th1))), 70).mul(0.16);
    const specTRT = pow(saturate(float(1).sub(th2.mul(th2))), 18).mul(0.5);
    const diff = albedo.mul(mix(float(0.45), float(1.0), sinTL)).mul(0.85);
    const spec = vec3(specR).add(albedo.mul(specTRT)).mul(mix(float(0.35), float(1.0), rnd));
    const back = saturate(dot(V.negate(), Ld));
    const trans = albedo.mul(pow(back, 3).mul(pow(edge, 1.5)).mul(0.9).mul(t));
    col.addAssign(L.col.mul(diff.add(spec).mul(vis).add(trans)));
  }
  // soft occlusion under the hand
  const hd = length(vPos.sub(uHandOcc.xyz));
  return col.mul(float(1).sub(uHandOcc.w.mul(float(1).sub(smoothstep(float(0.05), float(0.42), hd)))));
});

const hairMat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
hairMat.positionNode = hWorld;
hairMat.colorNode = furShade();
hairMat.opacityNode = float(1).sub(smoothstep(float(0.8), float(1.0), vAlong)).mul(float(1).sub(pow(abs(vSide), 4)));
hairMat.alphaToCoverage = true;
const hair = new THREE.Mesh(hairGeo, hairMat);
hair.frustumCulled = false;
// fur casts shadows: the shadow pass re-uses the strand positions (ribbons then face the light)
hairMat.castShadowPositionNode = hWorld;
hair.castShadow = true;
scene.add(hair);

// along the surface normal, fingers pointing "up/away" on screen. Each finger curls under a small
// feedback controller until its tip rests on (or digs into) the fur. The bones then drive the
// collision capsules in the fur solver, so what you see is what touches the fur.

  const pointer = {
    ndc: new THREE.Vector2(),
    x: 0, y: 0, inside: false, down: false, petting: false,
  };
  const raycaster = new THREE.Raycaster();

  function setPointer(ndc, x, y, inside = true) {
    pointer.ndc.copy(ndc);
    pointer.x = x;
    pointer.y = y;
    pointer.inside = inside;
  }
  function hitCreature() {
    raycaster.setFromCamera(pointer.ndc, camera);
    raycaster.far = Infinity;
    const hs = raycaster.intersectObjects(proxies, false);
    return hs.length ? hs[0] : null;
  }
  function beginPointer(ndc, x, y) {
    setPointer(ndc, x, y, true);
    pointer.down = true;
    pointer.petting = Boolean(hitCreature());
    if (pointer.petting) controls.enabled = false;
    return pointer.petting;
  }
  function movePointer(ndc, x, y) {
    setPointer(ndc, x, y, true);
  }
  function leavePointer() {
    if (!pointer.petting) pointer.inside = false;
  }
  function endPointer() {
    pointer.down = false;
    pointer.petting = false;
    controls.enabled = true;
  }

const hand = {
  vis: 0, active: false, scratch: false, still: 0, lift: 0.1, init: false,
  pos: new THREE.Vector3(), quat: new THREE.Quaternion(), up: new THREE.Vector3(0, 1, 0),
  lastX: 0, lastY: 0, prevPos: new THREE.Vector3(),
  capPrev: handCaps.map(() => new THREE.Vector3()), capInit: false,
};
const _camUp = new THREE.Vector3(), _camFwd = new THREE.Vector3(), _n = new THREE.Vector3(), _tgt = new THREE.Vector3();
const _X = new THREE.Vector3(), _Z = new THREE.Vector3(), _F = new THREE.Vector3(), _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion();
const _A = new THREE.Vector3(), _B = new THREE.Vector3(), _M = new THREE.Vector3(), _dl = new THREE.Vector3(), _tip = new THREE.Vector3(), _o = new THREE.Vector3();

function poseFingers(oscillate) {
  for (const c of chains) {
    const osc = oscillate && !c.isThumb ? 0.42 * Math.sin(T * Math.PI * 2 * 7 + c.ph) + 0.12 : 0;
    const ow = [0.15, 0.45, 0.4];
    c.joints.forEach((j, i) => { j.rotation.x = (i === 0 ? c.pitch : 0) - (c.curl * c.weights[i] + osc * ow[i]); });
  }
  handRig.updateMatrixWorld(true);
}

function updateHand(dt) {
  const engaged = pointer.inside && (!pointer.down || pointer.petting);
  const hit = engaged ? hitCreature() : null;

  // press and hold still → scratch
  const pxSpeed = Math.hypot(pointer.x - hand.lastX, pointer.y - hand.lastY) / Math.max(dt, 1e-3);
  hand.lastX = pointer.x; hand.lastY = pointer.y;
  hand.still = (pointer.petting && hit && pxSpeed < 90) ? hand.still + dt : 0;
  hand.scratch = hand.still > 0.22;
  const mode = !hit ? 'float' : hand.scratch ? 'scratch' : pointer.petting ? 'pet' : 'hover';

  _camUp.set(0, 1, 0).applyQuaternion(camera.quaternion);
  camera.getWorldDirection(_camFwd);
  if (hit) {
    _n.copy(hit.face.normal).transformDirection(hit.object.matrixWorld).normalize();
    const liftT = { hover: 0.1, pet: 0.028, scratch: 0.14 }[mode];
    hand.lift += (liftT - hand.lift) * (1 - Math.exp(-dt * 12));
    _tgt.copy(hit.point).addScaledVector(_n, hand.lift + 0.17 * HS);
  } else {
    _n.set(0, 1, 0).addScaledVector(_camFwd, -0.6).normalize();
    raycaster.setFromCamera(pointer.ndc, camera);
    raycaster.ray.at(camera.position.distanceTo(controls.target) - 1.2, _tgt);
    _tgt.y = Math.max(_tgt.y, FLOOR + 0.35);
    hand.lift = 0.1;
  }
  hand.up.lerp(_n, 1 - Math.exp(-dt * 10)).normalize();
  _F.copy(_camUp).addScaledVector(_camFwd, 0.8);
  _F.addScaledVector(hand.up, -_F.dot(hand.up));
  if (_F.lengthSq() < 1e-6) _F.set(0, 0, -1);
  _F.normalize();
  _Z.copy(_F).negate();
  _X.crossVectors(hand.up, _Z);
  _q.setFromRotationMatrix(_m4.makeBasis(_X, hand.up, _Z));

  if (!hand.init) { hand.pos.copy(_tgt); hand.quat.copy(_q); hand.prevPos.copy(_tgt); hand.init = true; }
  hand.prevPos.copy(hand.pos);
  hand.pos.lerp(_tgt, 1 - Math.exp(-dt * 18));
  hand.quat.slerp(_q, 1 - Math.exp(-dt * 12));
  hand.vis += ((pointer.inside ? 1 : 0) - hand.vis) * (1 - Math.exp(-dt * 10));

  handRig.visible = hand.vis > 0.02;
  handRig.position.copy(hand.pos);
  handRig.quaternion.copy(hand.quat);
  handRig.scale.setScalar(HS * Math.max(0.02, hand.vis));

  // fingers: curl until the tips rest where they should
  poseFingers(false);
  for (const c of chains) {
    if (!hit) { c.curl += (0.35 - c.curl) * (1 - Math.exp(-dt * 6)); continue; }
    c.joints[2].localToWorld(_tip.set(0, 0, -c.lens[2]));
    _o.copy(_tip).addScaledVector(hand.up, 0.6);
    raycaster.set(_o, _A.copy(hand.up).negate());
    raycaster.far = 1.6;
    const hs = raycaster.intersectObjects(proxies, false);
    raycaster.far = Infinity;
    if (!hs.length) { c.curl += (0.3 - c.curl) * 0.1; continue; }
    const gap = hs[0].distance - 0.6;
    const want = mode === 'hover' ? 0.09 : mode === 'pet' ? c.tipR * HS + 0.012 : c.tipR * HS * 0.35;
    c.curl += Math.max(-0.1, Math.min(0.1, (gap - want) * 5));
    c.curl = c.isThumb ? Math.max(-0.3, Math.min(1.0, c.curl)) : Math.max(-0.35, Math.min(1.8, c.curl));
  }
  poseFingers(mode === 'scratch');

  // bones → collision capsules
  const s = Math.max(0.02, hand.vis);
  handCaps.forEach((cap, i) => {
    cap.obj.localToWorld(_A.copy(cap.a));
    cap.obj.localToWorld(_B.copy(cap.b));
    _M.addVectors(_A, _B).multiplyScalar(0.5);
    _dl.subVectors(_M, hand.capPrev[i]);
    if (!hand.capInit) _dl.set(0, 0, 0);
    if (_dl.length() > 0.08) _dl.setLength(0.08);
    hand.capPrev[i].copy(_M);
    capU[i].a.value.set(_A.x, _A.y, _A.z, cap.r * HS * s + 0.006);
    capU[i].b.value.copy(_B);
    capU[i].d.value.copy(_dl);
  });
  hand.capInit = true;
  handRig.localToWorld(_M.set(0, 0, -0.55));
  uHandBound.value.set(_M.x, _M.y, _M.z, 1.4 * HS * s + 0.12);
  uFriction.value = { float: 0.2, hover: 0.25, pet: 0.6, scratch: 0.75 }[mode];

  if (hit) {
    handRig.localToWorld(_M.set(0, -0.3, -0.35));
    uHandOcc.value.set(_M.x, _M.y, _M.z, { hover: 0.3, pet: 0.5, scratch: 0.4 }[mode] * s);
  } else uHandOcc.value.w = 0;

  hand.active = !!hit;
  return hand.pos.distanceTo(hand.prevPos) / Math.max(dt, 1e-3);
}

  let T = 0, pleasure = 0, happy = 0, blinkT = 2.5, blinkPh = -1, petted = false;
  const look = new THREE.Vector2();

  let debugMode = "final";
  function setDebugMode(mode) {
    if (!["final", "skin", "strands", "contact"].includes(mode)) return;
    debugMode = mode;
    creature.visible = mode !== "strands";
    hair.visible = mode !== "skin";
    for (const proxy of proxies) proxy.visible = mode === "contact";
    return debugMode;
  }

  function update(deltaSeconds) {
    const dt = Math.min(Math.max(deltaSeconds, 0), 1 / 30);
    if (dt <= 0) return;
    T += dt;

    const pet = pointer.petting && hand.active ? 1 : 0;
    if (!pointer.petting) look.lerp(pointer.inside ? pointer.ndc : new THREE.Vector2(), 1 - Math.exp(-dt * 2.5));
    const br = Math.sin(T * 1.7);
    bodyGroup.scale.set(1 + br * 0.01, 1 + br * 0.012, 1 + br * 0.01);
    headPivot.position.set(NECK[0], NECK[1] + br * 0.008 - pet * 0.01, NECK[2]);
    headPivot.rotation.set(-look.y * 0.14, look.x * 0.4, Math.sin(T * 2.2) * 0.06 * happy);
    creature.position.set(Math.sin(T * 57) * 0.0012 * happy, 0, 0);
    creature.updateMatrixWorld(true);
    uHeadModel.value.copy(headInner.matrixWorld);
    uBodyModel.value.copy(bodyGroup.matrixWorld);

    const speed = updateHand(dt);
    if (pet && (speed > 0.15 || hand.scratch)) {
      pleasure = Math.min(2, pleasure + dt * (hand.scratch ? 1.6 : 0.7 + speed * 1.5));
      petted = true;
    } else pleasure = Math.max(0, pleasure - dt * 0.8);
    happy += ((pleasure > 0.35 ? 1 : 0) - happy) * (1 - Math.exp(-dt * 9));

    blinkT -= dt;
    if (blinkT < 0 && blinkPh < 0) { blinkPh = 0; blinkT = 2 + Math.random() * 4; }
    let blink = 1;
    if (blinkPh >= 0) {
      blinkPh += dt / 0.16;
      blink = 1 - Math.sin(Math.min(blinkPh, 1) * Math.PI) * 0.92;
      if (blinkPh >= 1) blinkPh = -1;
    }
    const eyeY = Math.max(0.001, (1 - happy) * blink);
    for (const e of eyes) { e.scale.set(1, eyeY, 1); e.visible = eyeY > 0.03; }
    for (const a of arcs) { a.scale.setScalar(Math.max(0.001, happy)); a.visible = happy > 0.03; }

    renderer.compute(simNode);
  }

  return {
    creature,
    hair,
    hand: handRig,
    proxies,
    update,
    beginPointer,
    movePointer,
    leavePointer,
    endPointer,
    setDebugMode,
    get debugMode() { return debugMode; },
    get petted() { return petted; },
    get mode() { return hand.scratch ? "scratch" : pointer.petting ? "pet" : pointer.inside ? "hover" : "idle"; },
    dispose() {
      scene.remove(creature, handRig, hair);
      hairGeo.dispose();
      hairMat.dispose();
      const geometries = new Set();
      for (const root of [creature, handRig]) {
        root.traverse((child) => {
          if (child.isMesh && child.geometry) geometries.add(child.geometry);
        });
      }
      for (const geometry of geometries) geometry.dispose();
      skinMat.dispose();
      proxyMat.dispose();
      eyeMat.dispose();
      glintMat.dispose();
      lineMat.dispose();
      handSkin.dispose();
      nailMat.dispose();
      sleeveMat.dispose();
      noseMesh.material.dispose();
    },
  };
}
