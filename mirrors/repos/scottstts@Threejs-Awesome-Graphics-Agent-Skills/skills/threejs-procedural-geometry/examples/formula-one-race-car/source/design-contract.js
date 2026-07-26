import { clamp01, smooth01 } from "./mesh-kit.js";

/*
   DESIGN CONTRACT — 2026 Formula 1 Technical Regulations, in metres.
   Frame: +X right, +Y up, +Z forward (nose).  Ground plane y = 0.
   Every subassembly is positioned from this table or from a sample of a surface built
   from it.  There are no late visual nudges and no global repair scale.
*/

export const D = (() => {
  const wheelbase   = 3.400;
  const frontAxleZ  =  1.720;
  const rearAxleZ   = frontAxleZ - wheelbase;   // -1.680

  const frontTyre = { od: 0.7200, width: 0.3720, rimOD: 0.4572 };  // 18" rim
  const rearTyre  = { od: 0.7300, width: 0.4060, rimOD: 0.4572 };

  const overallWidth = 1.900;
  // hub centres derived from the legal envelope, not chosen independently
  const frontHubX = overallWidth * 0.5 - frontTyre.width * 0.5 - 0.006;   // 0.708
  const rearHubX  = overallWidth * 0.5 - rearTyre.width  * 0.5 - 0.010;   // 0.687

  return {
    wheelbase, frontAxleZ, rearAxleZ, overallWidth,
    frontTyre, rearTyre, frontHubX, rearHubX,
    frontR: frontTyre.od * 0.5, rearR: rearTyre.od * 0.5,

    /* longitudinal stations */
    noseTipZ:      2.755,
    bulkheadZ:     1.905,   // front of the survival cell
    cockpitFrontZ: 1.075,   // forward cockpit-opening edge
    cockpitRearZ:  0.115,   // rear cockpit-opening edge / headrest
    rollHoopZ:    -0.235,
    sidepodInletZ: 0.640,
    sidepodEndZ:  -1.190,
    engineCoverEndZ: -1.640,
    rearCrashZ:   -2.130,
    diffuserExitZ:-2.045,
    rearWingLEZ:  -1.845,
    rearWingTEZ:  -2.360,
    frontWingLEZ:  2.965,
    frontWingTEZ:  2.235,

    /* heights */
    plankY:        0.0345,  // reference-plane / plank underside at the front axle
    rakeRise:      0.0455,  // extra floor height at the diffuser throat (rake)
    chassisTopY:   0.610,   // top deck of the survival cell at the bulkhead
    cockpitRimY:   0.585,
    rollHoopY:     0.955,   // regulation maximum height
    haloTopY:      0.935,
    beamWingY:     0.310,
    rearWingLowY:  0.605,
    rearWingTopY:  0.900,

    /* lateral */
    floorHalfW:    0.500,
    sidepodHalfW:  0.740,
    monoHalfW:     0.390,

    /* aero spans */
    frontWingSpan: 1.800,
    rearWingSpan:  0.955,
    beamWingSpan:  0.760,

    seed: 20260127,
  };
})();

/* Livery + material palette. Deep graphite base with the crimson/white flash set. */
export const PAL = {
  carbon:      0x0b0b0e,
  carbonWarm:  0x131318,
  bodyBlack:   0x131418,
  bodyGrey:    0x2e3036,
  bodyGloss:   0x1a1b20,
  red:         0xa8122c,
  redBright:   0xd4142f,
  redDeep:     0x6e0a1c,
  white:       0xe8ebee,
  whiteDim:    0xbfc4ca,
  silver:      0x8d939b,
  titanium:    0x7b8087,
  steel:       0x9aa1a9,
  goldTint:    0xb98f3c,
  tyre:        0x121214,
  tyreShoulder:0x18181b,
  rim:         0x1b1c20,
  brakeDisc:   0x2b2724,
  brakeGlow:   0x581206,
  visor:       0x120a06,
  helmetWhite: 0xdfe3e7,
  rainLight:   0xff1420,
};

/* Derived ride-height plane: the floor rakes upward toward the rear. */
export const floorY = (z) => {
  const t = clamp01((D.frontAxleZ - z) / (D.frontAxleZ - D.rearAxleZ));
  return D.plankY + D.rakeRise * smooth01(t);
};
/* projector frame — shared by the painters and by the material nodes */
export const PROJ = (() => {
  const Z1 = 3.10, Z0 = -2.60;                 // longitudinal span of the paint plane
  const zSpan = Z1 - Z0;                        // 5.70 m
  const SIDE_W = 3584, SIDE_LAYER_H = 700;      // two stacked layers: +X then -X
  const sidePPM = SIDE_W / zSpan;               // 628.77 px/m
  const hSpan = (SIDE_LAYER_H * 2) / sidePPM;   // full-texture vertical span
  const Y1 = 1.0580, Y0 = Y1 - SIDE_LAYER_H / sidePPM;
  const TOP_W = 2560, TOP_H = 900;
  const topPPM = TOP_W / zSpan;                 // 449.1 px/m
  const X1 = (TOP_H / topPPM) * 0.5, X0 = -X1;  // ±1.002 m
  return { Z1, Z0, zSpan, SIDE_W, SIDE_LAYER_H, sidePPM, hSpan, Y1, Y0, TOP_W, TOP_H, topPPM, X1, X0 };
})();
