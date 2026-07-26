import * as THREE from "three/webgpu";

/* ============================================================================
   1. DESIGN CONTRACT
   ----------------------------------------------------------------------------
   Units: metres.  Frame: +Z forward (nose), +Y up, +X to the rider's right.
   Origin: ground plane, midpoint of the wheelbase.  The machine is mirror
   symmetric about X = 0; right-hand parts are authored and mirrored.

   Every subassembly below is positioned from this table or from a sample taken
   on a surface generated from it.  Nothing is nudged into place afterwards.
   Real 636 cc supersport figures drive the primary numbers:
     wheelbase 1400 · seat 830 · length 2025 · width 710 · height 1100
     rake 23.5deg · trail 101 · 120/70-17 front · 180/55-17 rear
   ========================================================================== */

const DEG = Math.PI / 180;

const D = {
  /* --- primary chassis geometry --------------------------------------- */
  wheelbase: 1.400,
  rake: 23.5 * DEG,          // steering axis tilt from vertical
  tripleOffset: 0.030,       // fork axis ahead of steering axis
  seatHeight: 0.830,

  front: {
    axle: [0.700, 0.300],    // [z, y]
    tyreR: 0.300,            // 120/70 ZR17 -> 599.8mm OD
    tyreW: 0.120,
    rimR: 0.2159,            // 17 inch
    rimW: 0.0889,            // 3.5 inch
    discR: 0.155,            // 310mm petal disc
    discInnerR: 0.079,
    discT: 0.0050,
  },
  rear: {
    axle: [-0.700, 0.315],   // 180/55 ZR17 -> 629.8mm OD
    tyreR: 0.315,
    tyreW: 0.180,
    rimR: 0.2159,
    rimW: 0.1397,            // 5.5 inch
    discR: 0.110,            // 220mm petal disc
    discInnerR: 0.052,
    discT: 0.0045,
    sprocketR: 0.0982,       // 43T, 525 pitch
    sprocketT: 0.0068,
  },

  /* --- steering ------------------------------------------------------- */
  fork: {
    tubeR: 0.0275,           // 41mm stanchion + coating
    sliderR: 0.0345,
    halfTrack: 0.1055,       // fork centres either side of the wheel
    lowerClampL: 0.545,      // distance up the fork axis from the axle
    upperClampL: 0.672,
    topL: 0.715,
    sliderTopL: 0.345,       // slider/stanchion transition
    axleLugL: 0.048,
  },
  bar: { halfWidth: 0.268, y: 0.882, z: 0.394, rise: 4 * DEG, sweep: 9 * DEG },
  // grip centres ~536mm apart, bar ends just inside the mirrors

  /* --- swingarm & drive ----------------------------------------------- */
  pivot: [-0.145, 0.365],
  countershaft: [-0.156, 0.372],
  frontSprocketR: 0.0366,    // 15T
  chainPitch: 0.015875,      // 525 = 5/8"
  chainW: 0.0170,

  /* --- frame ---------------------------------------------------------- */
  headTube: { l0: 0.560, l1: 0.700, r: 0.0345 },  // along the steering axis
  spar: {
    // twin-spar perimeter rail, right side; sampled head -> pivot
    // The rail must pass UNDER the tank cover: run it too high and it becomes
    // the machine's top line in profile, hiding the tank hump entirely.
    path: [
      [0.074, 0.808, 0.432],
      [0.112, 0.812, 0.352],
      [0.134, 0.804, 0.232],
      [0.144, 0.788, 0.092],
      [0.145, 0.748, -0.028],
      [0.142, 0.646, -0.106],
      [0.134, 0.506, -0.138],
      [0.130, 0.428, -0.144],
    ],
  },
  subframe: {
    upper: [[0.072, 0.812, -0.128], [0.088, 0.836, -0.318], [0.086, 0.870, -0.520], [0.070, 0.882, -0.700], [0.052, 0.884, -0.826]],
    lower: [[0.062, 0.612, -0.166], [0.082, 0.686, -0.312], [0.086, 0.790, -0.470], [0.078, 0.856, -0.618]],
  },

  /* --- engine --------------------------------------------------------- */
  engine: {
    crank: [-0.018, 0.360],
    bankAngle: 27 * DEG,     // cylinder axis forward from vertical
    caseHalfW: 0.140,
    headHalfW: 0.128,
    sumpY: 0.176,
    deckL: 0.148,            // crank -> cylinder deck along the bank axis
    headL: 0.300,            // crank -> top of the cam cover
    bore: 0.067,
  },
  exhaust: {
    headerR: 0.0175,
    portY: 0.556, portZ: 0.268,
    collectorZ: -0.208, collectorY: 0.197,
    canA: [0.116, 0.244, -0.296],
    canB: [0.163, 0.331, -0.612],
    canR0: 0.035, canR1: 0.051,
  },
  radiator: { z0: 0.288, z1: 0.328, y0: 0.378, y1: 0.602, halfW: 0.146 },

  /* --- bodywork ------------------------------------------------------- */
  body: {
    noseZ: 0.928,
    screenTopZ: 0.618, screenTopY: 1.100,
    tankTopY: 0.874,
    tailTipZ: -0.944,
    plateZ: -0.978,
    maxHalfW: 0.187,         // widest point of the side cowl
    mirrorHalfW: 0.352,      // 710mm overall width
    fenderTipZ: 0.952,
  },

  /* --- misc ----------------------------------------------------------- */
  peg: { z: -0.208, y: 0.372, halfW: 0.186 },
  pillionPeg: { z: -0.486, y: 0.616, halfW: 0.152 },   // hanger roots on the subframe
};

/* Derived steering frame: the fork axis carries the front axle; the steering
   axis is the fork axis pushed back by the triple-clamp offset.            */
const AX = {
  up: new THREE.Vector3(0, Math.cos(D.rake), -Math.sin(D.rake)),
  fwd: new THREE.Vector3(0, Math.sin(D.rake), Math.cos(D.rake)),
};
/* point on the fork axis, L metres above the front axle, X half-track s */
const forkPt = (L, s = 0) => new THREE.Vector3(
  s,
  D.front.axle[1] + AX.up.y * L,
  D.front.axle[0] + AX.up.z * L,
);
/* point on the steering axis */
const steerPt = (L) => forkPt(L).addScaledVector(AX.fwd, -D.tripleOffset);

/* --------------------------------------------------------------------------
   Palette — metallic flat spark black with lime accents.
   -------------------------------------------------------------------------- */
const PAL = {
  fairing:      new THREE.Color(0x14161a),   // flat spark black, flake base
  fairingDeep:  new THREE.Color(0x0a0b0e),
  glossBlack:   new THREE.Color(0x0d0f13),
  charcoal:     new THREE.Color(0x24272c),
  gunmetal:     new THREE.Color(0x3a3f47),
  alloyDark:    new THREE.Color(0x2b2e33),
  castAlloy:    new THREE.Color(0x63676d),
  brightAlloy:  new THREE.Color(0x9aa0a7),
  chrome:       new THREE.Color(0xc9ced5),
  titanium:     new THREE.Color(0x8e9299),
  steel:        new THREE.Color(0x8b9098),
  rubber:       new THREE.Color(0x0c0c0e),
  rubberWorn:   new THREE.Color(0x191a1c),
  green:        new THREE.Color(0x67b62c),   // Kawasaki lime
  greenDeep:    new THREE.Color(0x3f7a17),
  lens:         new THREE.Color(0xd8e2ec),
  lensRed:      new THREE.Color(0x7a0d12),
  amber:        new THREE.Color(0xd8721a),
  seat:         new THREE.Color(0x121316),
  gold:         new THREE.Color(0xb9924a),
};

const QUALITY = { low: 0.55, med: 0.78, high: 1.0 };
let QS = QUALITY.high;                            // segment scale
const seg = (n) => Math.max(6, Math.round(n * QS));
const SEED = 20260724;

export {
  AX, D, DEG, PAL, QS, QUALITY, SEED, forkPt, seg, steerPt,
};

/** Segment-count scale. Lower tiers thin every revolve and sweep together. */
export function setQualityScale(scale) { QS = scale; }
export function qualityScale() { return QS; }
