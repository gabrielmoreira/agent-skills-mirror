import * as THREE from "three/webgpu";
import { color, transformedNormalWorld } from "three/tsl";

import { D, DEG, seg } from "./design-contract.js";
import {
  M, PARTS, TAU, V2, Writer, add, filletBox, instance, invertedCount, resetInvertedCount,
  revolve,
} from "./mesh-kit.js";
import { MAT, TEX, buildMaterials } from "./motorcycle-materials.js";
import { buildBody, buildControls, buildEngine, buildFrame, buildFrontEnd, buildSwingarm, hexBolt, makeCaliper, makeChain, makeRotor, makeSprocket, makeTyre, makeWheel } from "./motorcycle-parts.js";

/* ============================================================================
   7. ASSEMBLY
   ----------------------------------------------------------------------------
   Named subassemblies, each fed only by the design contract.
   ========================================================================== */

function assembleRunning(root) {
  const g = new THREE.Group(); g.name = "running";
  root.add(g);

  /* -- front wheel ---------------------------------------------------- */
  const fw = new THREE.Group();
  fw.name = "wheel.front";
  fw.position.set(0, D.front.axle[1], D.front.axle[0]);
  g.add(fw);
  fw.add(makeWheel({
    rimW: D.front.rimW, seatR: D.front.rimR, hubHalf: 0.0525, hubR: 0.0455,
    boreR: 0.0132, dishOut: 0.004, name: "wheel.front",
  }));
  fw.add(makeTyre({
    sectionW: D.front.tyreW, outerR: D.front.tyreR, seatR: D.front.rimR,
    rimW: D.front.rimW, name: "tyre.front",
  }));
  for (const s of [1, -1]) {
    const rot = makeRotor({
      outerR: D.front.discR, innerR: 0.1175, thick: D.front.discT,
      hubR: 0.0465, boltR: 0.0740, name: "rotor.front" + (s > 0 ? "R" : "L"), side: s,
    });
    rot.position.x = s * 0.0725;
    rot.scale.x = s;
    fw.add(rot);
  }
  // axle + spacers
  fw.add(new THREE.Mesh(revolve([
    V2(0, -0.108), V2(0.0125, -0.112), V2(0.0125, 0.112), V2(0, 0.108)],
    { axis: "x", segments: seg(24), capStart: true, capEnd: true }), MAT.bolt));
  fw.children[fw.children.length - 1].name = "axle.front";
  fw.children[fw.children.length - 1].userData.slot = "bolt";

  /* -- rear wheel ------------------------------------------------------ */
  const rw = new THREE.Group();
  rw.name = "wheel.rear";
  rw.position.set(0, D.rear.axle[1], D.rear.axle[0]);
  g.add(rw);
  rw.add(makeWheel({
    rimW: D.rear.rimW, seatR: D.rear.rimR, hubHalf: 0.0755, hubR: 0.0505,
    boreR: 0.0132, dishOut: -0.010, armDepth: 1.22, name: "wheel.rear",
  }));
  rw.add(makeTyre({
    sectionW: D.rear.tyreW, outerR: D.rear.tyreR, seatR: D.rear.rimR,
    rimW: D.rear.rimW, name: "tyre.rear",
  }));
  const rrot = makeRotor({
    outerR: D.rear.discR, innerR: 0.0790, thick: D.rear.discT,
    hubR: 0.0400, boltR: 0.0560, name: "rotor.rear", carrierArms: 4,
  });
  rrot.position.x = 0.0665;
  rw.add(rrot);

  /* cush-drive carrier + sprocket on the left */
  const carrier = new Writer();
  revolve([
    V2(0.052, -0.0755), V2(0.088, -0.0790), V2(0.092, -0.0880), V2(0.090, -0.0930),
    V2(0.062, -0.0940), V2(0.052, -0.0900),
  ], { axis: "x", segments: seg(48), w: carrier });
  add(rw, carrier.geometry(), MAT.alloyCast, "wheel.rear.cush");
  const spr = makeSprocket({
    teeth: 43, pitchR: D.rear.sprocketR, thick: D.rear.sprocketT, boreR: 0.062,
    name: "sprocket.rear", mat: MAT.alloyMachined,
  });
  spr.position.x = -0.0876;
  rw.add(spr);
  const sBolts = [];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * TAU + 0.4;
    sBolts.push(M.c(M.t(-0.0925, Math.sin(a) * 0.0605, Math.cos(a) * 0.0605), M.rz(Math.PI / 2)));
  }
  instance(rw, hexBolt(0.0058, 0.0048), MAT.boltDark, sBolts, "sprocket.bolts");

  rw.add(new THREE.Mesh(revolve([
    V2(0, -0.126), V2(0.0128, -0.130), V2(0.0128, 0.118), V2(0, 0.114)],
    { axis: "x", segments: seg(24), capStart: true, capEnd: true }), MAT.bolt));
  rw.children[rw.children.length - 1].name = "axle.rear";
  rw.children[rw.children.length - 1].userData.slot = "bolt";

  /* -- chain ------------------------------------------------------------ */
  g.add(makeChain({
    cA: D.countershaft, rA: D.frontSprocketR, cB: D.rear.axle, rB: D.rear.sprocketR,
    x: -0.0876, pitch: D.chainPitch, name: "chain",
  }));
  return { g, fw, rw };
}

function assembleBrakes(root) {
  const g = new THREE.Group(); g.name = "brakes"; root.add(g);
  /* front: radial-mount monoblocs trailing the fork legs */
  for (const s of [1, -1]) {
    g.add(makeCaliper({
      axleY: D.front.axle[1], axleZ: D.front.axle[0], discX: s * 0.0725,
      phi: 135 * DEG, span: 21 * DEG, rIn: 0.116, rOut: 0.153,
      halfGap: 0.0082, thick: 0.021, name: "caliper.front" + (s > 0 ? "R" : "L"),
    }));
  }
  /* rear: single-piston sliding caliper on the swingarm torque arm */
  g.add(makeCaliper({
    axleY: D.rear.axle[1], axleZ: D.rear.axle[0], discX: 0.0665,
    phi: 166 * DEG, span: 17 * DEG, rIn: 0.076, rOut: 0.108,
    halfGap: 0.0078, thick: 0.019, name: "caliper.rear", mount: "bracket",
  }));
  add(g, filletBox(0.014, 0.030, 0.062, 0.007, { segments: seg(16), rings: seg(6) })
    .translate(0.0865, D.rear.axle[1] + 0.026, D.rear.axle[0] + 0.052),
    MAT.alloyAnodized, "caliper.rearBracket");
  return g;
}

function buildMotorcycle() {
  const root = new THREE.Group();
  root.name = "zx6r";
  buildFrame(root);
  buildEngine(root);
  buildSwingarm(root);
  buildFrontEnd(root);
  assembleRunning(root);
  assembleBrakes(root);
  buildControls(root);
  buildBody(root);
  return root;
}

export {
  assembleBrakes, assembleRunning, buildMotorcycle,
};

/* ============================================================================
   INSTANCE API
   ----------------------------------------------------------------------------
   One call builds materials, emits every subassembly, and returns the machine
   with its part registry, measured envelope, and the diagnostic modes the
   surfaces are authored against.
   ========================================================================== */

let wireMaterial = null;
let normalMaterial = null;
const slotMaterials = {};

function buildDebugMaterials() {
  if (wireMaterial) return;
  wireMaterial = new THREE.MeshBasicNodeMaterial({ wireframe: true });
  wireMaterial.colorNode = color(0x2b6cb0);
  normalMaterial = new THREE.MeshBasicNodeMaterial();
  normalMaterial.colorNode = transformedNormalWorld.mul(0.5).add(0.5);
}

/** Stable hue per material slot, so a slot keeps its colour across rebuilds. */
function slotMaterial(slot) {
  if (!slotMaterials[slot]) {
    let h = 0;
    for (let i = 0; i < slot.length; i++) h = (h * 31 + slot.charCodeAt(i)) >>> 0;
    const c = new THREE.Color().setHSL((h % 997) / 997, 0.62, 0.55);
    const m = new THREE.MeshBasicNodeMaterial();
    m.colorNode = color(c);
    slotMaterials[slot] = m;
  }
  return slotMaterials[slot];
}

export function createSportMotorcycle() {
  const materials = buildMaterials();
  const partStart = PARTS.length;
  resetInvertedCount();

  const root = buildMotorcycle();
  buildDebugMaterials();

  const stats = PARTS.slice(partStart);
  const totalTriangles = Math.round(stats.reduce((sum, p) => sum + p.tris, 0));
  const trianglesBySlot = {};
  for (const p of stats) trianglesBySlot[p.slot] = (trianglesBySlot[p.slot] ?? 0) + p.tris;
  const invertedFixups = invertedCount();
  const savedMaterials = new Map();

  const bounds = new THREE.Box3().setFromObject(root);

  return {
    object: root,
    materials,
    stats,
    totalTriangles,
    trianglesBySlot,
    /** Closed bodies the orientation guard had to flip. */
    invertedFixups,

    /** Measured envelope, for checking the model against the dimension contract. */
    measure() {
      return {
        length: +(bounds.max.z - bounds.min.z).toFixed(3),
        width: +(bounds.max.x - bounds.min.x).toFixed(3),
        height: +(bounds.max.y - bounds.min.y).toFixed(3),
        wheelbase: +(D.front.axle[0] - D.rear.axle[0]).toFixed(3),
        seatHeight: D.seatHeight,
      };
    },

    /**
     * final | topology | slots | normals | nobody | noglass.
     * `slots` is the load-bearing one: it colours every mesh by its material
     * slot, which is how a black-on-black machine is checked for finish
     * ownership at all.
     */
    setDebugMode(mode) {
      root.traverse((o) => {
        if (!o.isMesh) return;
        if (!savedMaterials.has(o)) savedMaterials.set(o, o.material);
        const base = savedMaterials.get(o);
        const slot = o.userData.slot || "misc";
        o.visible = true;
        if (mode === "topology") o.material = wireMaterial;
        else if (mode === "slots") o.material = slotMaterial(slot);
        else if (mode === "normals") o.material = normalMaterial;
        else {
          o.material = base;
          if (mode === "nobody") o.visible = !/^body\./.test(o.name);
          if (mode === "noglass") o.visible = !(slot === "glass" || slot === "screen");
        }
      });
    },

    dispose() {
      root.traverse((o) => { if (o.isMesh) o.geometry.dispose(); });
      for (const m of Object.values(materials)) m.dispose?.();
      for (const t of TEX) t.dispose?.();
      PARTS.length = partStart;
    },
  };
}
