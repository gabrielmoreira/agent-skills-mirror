import * as THREE from 'three/webgpu';
import * as TSL from 'three/tsl';

export const thinFilmSoapBubbleDebugModes = Object.freeze([
  'final',
  'no-interreflection',
  'spherical-membranes',
  'rear-membranes'
]);

export function createThinFilmSoapBubbleSystem({
  environment,
  camera,
  controlsTarget,
  domElement
}) {
if (!environment || !camera || !controlsTarget || !domElement) {
  throw new Error('Soap bubble system requires environment, camera, controlsTarget, and domElement.');
}
const envMap = environment;
const scene = new THREE.Group();

// ---------------------------------------------------------------------------
// Scope and physical model
// ---------------------------------------------------------------------------
// Scene units are metres. The bubble is NOT treated as a glass sphere.
// A soap bubble is air | thin aqueous film | air. Because the media outside
// the film are nearly the same, the transmitted ray is essentially parallel
// to the incident ray; the visually dominant effect is wavelength-dependent
// coherent reflection from the two interfaces of the sub-micron film.
//
// Optics here:
//   * exact s/p Fresnel amplitude coefficients at air-film-air interfaces
//   * Airy thin-film reflectance (infinite internal reflections in the film)
//   * wavelength-dependent aqueous-film IOR (Cauchy approximation)
//   * finite spectral-band averaging around R/G/B effective wavelengths
//   * front AND rear membranes rendered as separate geometry passes
//   * RGB HDRI reflection sampled in world direction, never screen-space
//
// Limits that cannot be removed with an RGB HDRI + real-time rasterization:
//   * an RGB environment has radiance, not a measured spectrum, so the shader can
//     only filter representative RGB wavelength bands rather than reconstruct
//     the full spectral radiance field.
//   * nearby bubbles use a bounded analytic one-bounce model: a CPU-selected
//     local neighborhood is ray-tested as sphere proxies, then only the nearest
//     hit receives a two-membrane thin-film evaluation. There is no recursion.
//   * standard transparent blending uses one scalar destination attenuation;
//     reflected RGB energy is exact for the sampled bands, while transmitted
//     chromatic attenuation is represented by their mean reflectance.
// These are deliberately narrow approximations; there is no fake rainbow,
// glass refraction, screen-space distortion, or billboard shading.

// ---------------------------------------------------------------------------
// Deterministic helpers and CPU-side validation of the same optical equation
// ---------------------------------------------------------------------------
function mulberry32(seed) {
  return function() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(0x51A7B0B5);
const rand = (a = 0, b = 1) => a + (b - a) * rng();
let gaussianSpare = null;
function randNormal() {
  if (gaussianSpare !== null) {
    const v = gaussianSpare;
    gaussianSpare = null;
    return v;
  }
  const u1 = Math.max(1e-12, rng());
  const u2 = rng();
  const mag = Math.sqrt(-2 * Math.log(u1));
  gaussianSpare = mag * Math.sin(2 * Math.PI * u2);
  return mag * Math.cos(2 * Math.PI * u2);
}
function randLogNormal(median, logSigma) {
  return median * Math.exp(logSigma * randNormal());
}

const N_AIR = 1.000277;
function filmIOR(lambdaNm) {
  // Compact Cauchy approximation for a water-like soap solution in visible light.
  const um = lambdaNm * 1e-3;
  return 1.322 + 0.00306 / (um * um);
}
function thinFilmReflectanceCPU(cos0, thicknessNm, lambdaNm) {
  const n0 = N_AIR;
  const n2 = N_AIR;
  const n1 = filmIOR(lambdaNm);
  const c0 = Math.max(1e-6, Math.min(1, Math.abs(cos0)));
  const s0sq = Math.max(0, 1 - c0 * c0);
  const eta = n0 / n1;
  const c1 = Math.sqrt(Math.max(0, 1 - eta * eta * s0sq));
  const c2 = c0;

  const r01s = (n0 * c0 - n1 * c1) / (n0 * c0 + n1 * c1);
  const r12s = (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2);
  const r01p = (n1 * c0 - n0 * c1) / (n1 * c0 + n0 * c1);
  const r12p = (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2);
  const phi = 4 * Math.PI * n1 * thicknessNm * c1 / lambdaNm;
  const cp = Math.cos(phi);

  const airy = (a, b) => {
    const ab = a * b;
    const num = a * a + b * b + 2 * ab * cp;
    const den = 1 + ab * ab + 2 * ab * cp;
    return num / Math.max(1e-12, den);
  };
  return 0.5 * (airy(r01s, r12s) + airy(r01p, r12p));
}

function runPhysicsSelfTests() {
  const failures = [];
  const nearZero = thinFilmReflectanceCPU(1, 0, 550);
  if (Math.abs(nearZero) > 1e-8) failures.push(`zero-thickness R=${nearZero}`);

  for (const c of [1, 0.8, 0.4, 0.1, 0.01]) {
    for (const d of [180, 320, 520, 900, 1400]) {
      for (const l of [440, 460, 545, 610, 640]) {
        const R = thinFilmReflectanceCPU(c, d, l);
        if (!Number.isFinite(R) || R < -1e-7 || R > 1 + 1e-7) {
          failures.push(`unphysical R=${R} at cos=${c}, d=${d}, lambda=${l}`);
        }
      }
    }
  }

  const grazing = thinFilmReflectanceCPU(0.002, 520, 550);
  if (!(grazing > 0.75 && grazing <= 1.000001)) failures.push(`grazing Fresnel R=${grazing}`);

  if (failures.length) throw new Error(`Physics self-tests failed:\n${failures.join('\n')}`);
  return true;
}

runPhysicsSelfTests();

// ---------------------------------------------------------------------------
// TSL optical model
// ---------------------------------------------------------------------------
const F = TSL.float;
const PI4 = 4 * Math.PI;

// Bounded inter-bubble reflection. We do NOT render per-bubble cubemaps and do
// NOT test all bubbles per fragment. The CPU picks a small local neighborhood;
// the shader intersects only those analytic proxies and shades the nearest hit.
const INTER_BUBBLE_CANDIDATES = 6;
const INTER_BUBBLE_PROXY_MARGIN = 1.005;
const INTER_BUBBLE_RAY_EPSILON = 5e-4; // metres

function aqueousIORNode(lambdaNm) {
  const um = F(lambdaNm * 1e-3);
  return F(1.322).add(F(0.00306).div(um.mul(um)));
}

function airyReflectanceNode(r01, r12, cosPhi) {
  const ab = r01.mul(r12);
  const numerator = r01.mul(r01)
    .add(r12.mul(r12))
    .add(ab.mul(cosPhi).mul(2));
  const denominator = F(1)
    .add(ab.mul(ab))
    .add(ab.mul(cosPhi).mul(2));
  return numerator.div(TSL.max(denominator, F(1e-6)));
}

function monochromaticFilmR(cos0, thicknessNm, lambdaNm) {
  const n0 = F(N_AIR);
  const n2 = F(N_AIR);
  const n1 = aqueousIORNode(lambdaNm);
  const c0 = TSL.clamp(TSL.abs(cos0), F(0.001), F(1));
  const sin0sq = F(1).sub(c0.mul(c0));
  const eta = n0.div(n1);
  const c1 = TSL.sqrt(TSL.max(F(0), F(1).sub(eta.mul(eta).mul(sin0sq))));
  const c2 = c0;

  const r01s = n0.mul(c0).sub(n1.mul(c1)).div(n0.mul(c0).add(n1.mul(c1)));
  const r12s = n1.mul(c1).sub(n2.mul(c2)).div(n1.mul(c1).add(n2.mul(c2)));
  const r01p = n1.mul(c0).sub(n0.mul(c1)).div(n1.mul(c0).add(n0.mul(c1)));
  const r12p = n2.mul(c1).sub(n1.mul(c2)).div(n2.mul(c1).add(n1.mul(c2)));

  const phi = F(PI4).mul(n1).mul(thicknessNm).mul(c1).div(F(lambdaNm));
  const cp = TSL.cos(phi);
  const Rs = airyReflectanceNode(r01s, r12s, cp);
  const Rp = airyReflectanceNode(r01p, r12p, cp);
  return Rs.add(Rp).mul(0.5);
}

function spectralBandR(cos0, thicknessNm, centerNm, halfWidthNm) {
  // A small 3-tap spectral band suppresses unrealistically razor-thin high-order
  // interference that a monochromatic RGB channel would otherwise produce.
  const a = monochromaticFilmR(cos0, thicknessNm, centerNm - halfWidthNm);
  const b = monochromaticFilmR(cos0, thicknessNm, centerNm);
  const c = monochromaticFilmR(cos0, thicknessNm, centerNm + halfWidthNm);
  return a.mul(0.25).add(b.mul(0.5)).add(c.mul(0.25));
}

function buildShapeField(localDir, uModes) {
  const x = localDir.x, y = localDir.y, z = localDir.z;

  // Real-valued low-order spherical-harmonic-like radial modes (l >= 2 only;
  // no l=0 volume mode and no l=1 translation mode).
  const y20  = y.mul(y).mul(3).sub(1).mul(0.5);
  const y22c = x.mul(x).sub(z.mul(z));
  const y22s = x.mul(z).mul(2);
  const y31  = x.mul(y.mul(y).mul(5).sub(1));
  const y33  = x.mul(x.mul(x).sub(x.mul(z.mul(z)).mul(3)));

  const f = y20.mul(uModes[0])
    .add(y22c.mul(uModes[1]))
    .add(y22s.mul(uModes[2]))
    .add(y31.mul(uModes[3]))
    .add(y33.mul(uModes[4]));

  // Euclidean gradients of the polynomial representatives. Projecting the
  // gradient onto the sphere tangent plane yields the exact normal of the
  // radial graph r(s) = 1 + f(s): n ∝ s - grad_S(f)/(1+f).
  const gx = uModes[1].mul(x).mul(2)
    .add(uModes[2].mul(z).mul(2))
    .add(uModes[3].mul(y.mul(y).mul(5).sub(1)))
    .add(uModes[4].mul(x.mul(x).sub(z.mul(z)).mul(3)));

  const gy = uModes[0].mul(y).mul(3)
    .add(uModes[3].mul(x).mul(y).mul(10));

  const gz = uModes[1].mul(z).mul(-2)
    .add(uModes[2].mul(x).mul(2))
    .add(uModes[4].mul(x).mul(z).mul(-6));

  const grad = TSL.vec3(gx, gy, gz);
  const radialProjection = TSL.dot(grad, localDir);
  const gradSurface = grad.sub(localDir.mul(radialProjection));
  const radius = F(1).add(f);
  const normalLocal = TSL.normalize(localDir.sub(gradSurface.div(TSL.max(radius, F(0.85)))));

  return { f, radius, normalLocal };
}

function createBubbleUniforms() {
  return {
    modes: [TSL.uniform(0), TSL.uniform(0), TSL.uniform(0), TSL.uniform(0), TSL.uniform(0)],
    volumeScale: TSL.uniform(1),
    meanThicknessNm: TSL.uniform(520),
    filmPhase: TSL.uniform(0),
    filmSeed: TSL.uniform(rand(-20, 20)),

    // Rupture uniforms. The hole is defined on the same local spherical parameter
    // used by the live deformed shell, so the tear follows the actual membrane
    // rather than a screen-space mask. burstCosTheta = cos(geodesic hole radius).
    burstActive: TSL.uniform(0),
    burstDirLocal: TSL.uniform(new THREE.Vector3(0, 0, 1)),
    burstCosTheta: TSL.uniform(1),
    burstRimDotHalfWidth: TSL.uniform(0),

    reflectionPeers: Array.from({ length: INTER_BUBBLE_CANDIDATES }, () => ({
      center: TSL.uniform(new THREE.Vector3(1e4, 1e4, 1e4)),
      radius: TSL.uniform(0),
      meanThicknessNm: TSL.uniform(520)
    }))
  };
}

function approximateSecondaryThickness(meanThicknessNm, worldRadial) {
  // Preserve the dominant physical thickness structure for reflected bubbles:
  // gravity drainage plus the bottom Plateau-border thickening. We intentionally
  // omit the high-frequency Marangoni noise on secondary rays to bound cost.
  const drainage = F(1).sub(worldRadial.y.mul(0.24));
  const bottom = TSL.smoothstep(F(0.35), F(0.95), worldRadial.y.negate());
  return TSL.clamp(
    meanThicknessNm.mul(drainage).add(bottom.mul(bottom).mul(260)),
    F(170), F(1450)
  );
}

function secondaryFilmR(rayDir, outwardNormal, worldRadial, meanThicknessNm) {
  const cos0 = TSL.clamp(TSL.abs(TSL.dot(rayDir, outwardNormal)), F(0.001), F(1));
  const thicknessNm = approximateSecondaryThickness(meanThicknessNm, worldRadial);
  return TSL.clamp(TSL.vec3(
    spectralBandR(cos0, thicknessNm, 610, 12),
    spectralBandR(cos0, thicknessNm, 545, 10),
    spectralBandR(cos0, thicknessNm, 460, 10)
  ), F(0), F(0.999));
}

function bubbleAwareReflectionRadiance(rayOrigin, rayDir, U) {
  const background = TSL.texture(envMap, TSL.equirectUV(rayDir)).rgb;

  // Cheap broad/narrow pass: intersect only K CPU-selected peers, remember the
  // nearest positive root, and defer all Airy/HDRI work until after selection.
  const nearestT = F(1e6).toVar();
  const farT = F(1e6).toVar();
  const hitCenter = TSL.vec3(0).toVar();
  const hitMeanThickness = F(520).toVar();

  for (const peer of U.reflectionPeers) {
    const oc = rayOrigin.sub(peer.center);
    const b = TSL.dot(oc, rayDir);
    const c = TSL.dot(oc, oc).sub(peer.radius.mul(peer.radius));
    const disc = b.mul(b).sub(c);

    TSL.If(disc.greaterThanEqual(F(0)), () => {
      const root = TSL.sqrt(TSL.max(disc, F(0)));
      const tNear = b.negate().sub(root);
      const tFar = b.negate().add(root);
      const tCandidate = TSL.select(
        tNear.greaterThan(F(INTER_BUBBLE_RAY_EPSILON)),
        tNear,
        tFar
      );

      TSL.If(tCandidate.greaterThan(F(INTER_BUBBLE_RAY_EPSILON)), () => {
        TSL.If(tCandidate.lessThan(nearestT), () => {
          nearestT.assign(tCandidate);
          farT.assign(tFar);
          hitCenter.assign(peer.center);
          hitMeanThickness.assign(peer.meanThicknessNm);
        });
      });
    });
  }

  const radiance = background.toVar();
  TSL.If(nearestT.lessThan(F(9e5)), () => {
    const pNear = rayOrigin.add(rayDir.mul(nearestT));
    const nNear = TSL.normalize(pNear.sub(hitCenter));
    const RNear = secondaryFilmR(rayDir, nNear, nNear, hitMeanThickness);
    // Explicit LOD keeps texture sampling valid inside non-uniform control flow.
    const reflectedNear = TSL.texture(
      envMap, TSL.equirectUV(TSL.reflect(rayDir, nNear)), TSL.int(0)
    ).rgb;

    const pFar = rayOrigin.add(rayDir.mul(farT));
    const nFar = TSL.normalize(pFar.sub(hitCenter));
    const RFar = secondaryFilmR(rayDir, nFar, nFar, hitMeanThickness);
    const reflectedFar = TSL.texture(
      envMap, TSL.equirectUV(TSL.reflect(rayDir, nFar)), TSL.int(0)
    ).rgb;

    const one = TSL.vec3(1);
    const TNear = one.sub(RNear);
    const TFar = one.sub(RFar);

    // One-bounce shell transport. The far-membrane reflection must transmit
    // through the near membrane again on its return; including that factor keeps
    // the approximation energy-consistent instead of making reflected bubbles
    // artificially bright. Higher cavity bounces are deliberately omitted.
    const throughFar = RFar.mul(TNear).mul(reflectedFar)
      .add(TFar.mul(background));
    const secondaryAppearance = RNear.mul(reflectedNear)
      .add(TNear.mul(throughFar));

    radiance.assign(secondaryAppearance);
  });

  return radiance;
}

function createBubbleMaterial(side, U) {
  const isBackMaterial = side === THREE.BackSide;
  const mat = new THREE.MeshBasicNodeMaterial();
  mat.side = side;
  mat.transparent = true;
  mat.depthTest = true;
  mat.depthWrite = false;
  mat.blending = THREE.NormalBlending;
  mat.opacity = 1;
  mat.forceSinglePass = true;

  mat.positionNode = TSL.Fn(() => {
    const s = TSL.normalize(TSL.positionGeometry);
    const shape = buildShapeField(s, U.modes);
    return s.mul(shape.radius).mul(U.volumeScale);
  })();

  mat.fragmentNode = TSL.Fn(() => {
    // Radial deformation keeps the local direction invariant, so normalized
    // deformed local position is the sphere parameter used by the mode field.
    const localDir = TSL.normalize(TSL.positionLocal);

    // A puncture opens as a geodesic circle on the membrane. Classical
    // Taylor-Culick dynamics sets the CPU-side angular radius; here we perform
    // the actual membrane removal in object space. fwidth keeps the physically
    // microscopic liquid rim energy-visible without inflating its integrated
    // coverage when it becomes narrower than a pixel.
    const burstDot = TSL.dot(localDir, U.burstDirLocal);
    const burstPixelWidth = TSL.max(TSL.fwidth(burstDot).mul(1.15), F(1e-5));
    const burstPhysicalWidth = TSL.max(U.burstRimDotHalfWidth, F(1e-7));
    const burstRenderWidth = TSL.max(burstPixelWidth, burstPhysicalWidth);
    const burstDelta = TSL.abs(burstDot.sub(U.burstCosTheta));
    const burstRimProfile = F(1).sub(TSL.smoothstep(F(0), burstRenderWidth, burstDelta));
    const burstCoverage = TSL.min(F(1), burstPhysicalWidth.div(burstRenderWidth));
    const burstRimCoverage = burstRimProfile.mul(burstCoverage).mul(U.burstActive);
    const shellCoverageBurst = F(1).sub(TSL.smoothstep(
      U.burstCosTheta.sub(burstPixelWidth),
      U.burstCosTheta.add(burstPixelWidth),
      burstDot
    ));
    const shellCoverage = TSL.mix(F(1), shellCoverageBurst, U.burstActive);

    TSL.If(U.burstActive.greaterThan(F(0.5)), () => {
      // Keep a one-pixel analytical reconstruction band for the liquid rim, but
      // discard the already-open interior completely.
      TSL.If(burstDot.greaterThan(U.burstCosTheta.add(burstRenderWidth.mul(1.25))), () => {
        TSL.Discard();
      });
    });

    const shape = buildShapeField(localDir, U.modes);
    const N = TSL.transformNormal(shape.normalLocal, TSL.modelWorldMatrix);
    const I = TSL.normalize(TSL.positionWorld.sub(TSL.cameraPosition));
    const cos0 = TSL.clamp(TSL.abs(TSL.dot(I, N)), F(0.001), F(1));

    // Gravity drainage: top film is thinner; bottom film / incipient Plateau
    // border is thicker. The local texture field is advected around the sphere
    // to represent tangential surface circulation / Marangoni flow.
    const worldRadial = TSL.normalize(TSL.transformDirection(localDir, TSL.modelWorldMatrix));
    const c = TSL.cos(U.filmPhase);
    const s = TSL.sin(U.filmPhase);
    const advected = TSL.vec3(
      c.mul(localDir.x).add(s.mul(localDir.z)),
      localDir.y,
      s.negate().mul(localDir.x).add(c.mul(localDir.z))
    );

    const n1 = TSL.triNoise3D(advected.mul(2.7).add(TSL.vec3(U.filmSeed, U.filmPhase.mul(0.08), F(0))), F(0), F(0));
    const n2 = TSL.triNoise3D(advected.mul(6.2).add(TSL.vec3(F(7.1), U.filmSeed.mul(0.7), U.filmPhase.mul(-0.05))), F(0), F(0));
    const drainage = F(1).sub(worldRadial.y.mul(0.24));
    const bottom = TSL.smoothstep(F(0.35), F(0.95), worldRadial.y.negate());

    let thicknessNm = U.meanThicknessNm.mul(drainage)
      .add(n1.mul(48))
      .add(n2.mul(18))
      .add(bottom.mul(bottom).mul(260));
    thicknessNm = TSL.clamp(thicknessNm, F(170), F(1450));

    // Representative linear-sRGB spectral bands. Exact full-spectrum filtering
    // is impossible because an RGB EXR does not contain spectral radiance.
    const Rr = spectralBandR(cos0, thicknessNm, 610, 12);
    const Rg = spectralBandR(cos0, thicknessNm, 545, 10);
    const Rb = spectralBandR(cos0, thicknessNm, 460, 10);
    const filmR = TSL.clamp(TSL.vec3(Rr, Rg, Rb), F(0), F(0.999));

    // Removed film mass accumulates in the retracting rim. Once it is many
    // wavelengths thick it no longer behaves like a coherent thin film, so use
    // an incoherent water/air Fresnel term for the rim instead of rainbow Airy
    // interference. The rim coverage is mass-derived and anti-aliased above.
    const waterF0 = F(Math.pow((1.333 - N_AIR) / (1.333 + N_AIR), 2));
    const oneMinusCos = F(1).sub(cos0);
    const waterFresnel = waterF0.add(F(1).sub(waterF0).mul(
      oneMinusCos.mul(oneMinusCos).mul(oneMinusCos).mul(oneMinusCos).mul(oneMinusCos)
    ));
    const rimR = TSL.vec3(waterFresnel);
    const R = TSL.clamp(
      filmR.mul(shellCoverage).add(rimR.mul(burstRimCoverage)),
      F(0), F(0.999)
    );

    // Reflection direction is genuinely 3D and tied to the deformed membrane.
    // The ray first checks nearby bubbles analytically; if none is hit it falls
    // through to the same HDRI sample used by the primary environment path.
    const reflectedDir = TSL.reflect(I, N);
    const reflectionOrigin = TSL.positionWorld.add(
      reflectedDir.mul(INTER_BUBBLE_RAY_EPSILON)
    );
    const reflectedRadiance = bubbleAwareReflectionRadiance(
      reflectionOrigin, reflectedDir, U
    );

    // Normal alpha blending can only attenuate the destination by one scalar.
    // Choose mean spectral R as alpha, then divide source RGB by alpha so the
    // *reflected* contribution after blending is exactly reflectedRadiance * R.
    const alpha = TSL.clamp(R.x.add(R.y).add(R.z).div(3), F(0.001), F(0.985));

    // The back membrane is rendered before the front membrane. Front blending will
    // later supply one transmission through the near film. To model the camera ray's
    // *entry* through that same near film as well, pre-attenuate the rear reflection
    // by one extra spectral transmission estimate here. This prevents the rear light
    // images from appearing too strong while keeping the existing two-pass structure.
    const entryTransmissionEstimate = TSL.vec3(1).sub(R);
    const reflectedWeight = isBackMaterial ? R.mul(entryTransmissionEstimate) : R;
    const sourceRGB = reflectedRadiance.mul(reflectedWeight).div(alpha);

    return TSL.vec4(sourceRGB, alpha);
  })();

  return mat;
}

// ---------------------------------------------------------------------------
// Bubble mechanics
// ---------------------------------------------------------------------------
const RHO_AIR = 1.204;       // kg/m^3
const RHO_INSIDE = 1.185;    // slightly warmer / moister enclosed air
const RHO_WATER = 997;       // kg/m^3
const G = 9.80665;           // m/s^2
const CD_SPHERE = 0.47; // high-Re fallback; normal operation uses Reynolds-dependent drag below
const AIR_DYNAMIC_VISCOSITY = 1.81e-5; // Pa*s at room temperature
const GAMMA_EFFECTIVE = 0.056; // N/m, two soap-film interfaces combined
const ADDED_MASS_COEFF = 0.5;
const BUBBLE_COUNT = 20;
const geometry = new THREE.IcosahedronGeometry(1, 5);

const tmpA = new THREE.Vector3();
const tmpB = new THREE.Vector3();
const tmpC = new THREE.Vector3();
const tmpD = new THREE.Vector3();
const tmpQ = new THREE.Quaternion();

// Persistent finite-difference / integrator scratch. The fixed-step simulation
// runs thousands of force evaluations per second, so keeping this allocation-free
// avoids garbage-collector stalls being mistaken for irregular physical motion.
const vortSamplePos = Array.from({ length: 6 }, () => new THREE.Vector3());
const vortSampleVel = Array.from({ length: 6 }, () => new THREE.Vector3());
const stepAir = new THREE.Vector3();
const stepRel = new THREE.Vector3();
const stepForce = new THREE.Vector3();
const stepVort = new THREE.Vector3();
const stepRelDir = new THREE.Vector3();
const stepLocalDir = new THREE.Vector3();
const stepInvQ = new THREE.Quaternion();

function airVelocityAt(p, t, out = new THREE.Vector3()) {
  // Base ambient drift. Eddies are smooth compact vortices; unlike independent
  // xyz noise, these velocity components are constructed from rotations and are
  // approximately divergence-free in their local planes.
  out.set(0.028, 0.050, -0.004);

  const eddies = [
    { c: [-0.55 + 0.18 * Math.sin(t * 0.11), -0.20 + 0.10 * Math.cos(t * 0.13), 0.02], a: [0,0,1], core: 0.62, strength: 0.115 },
    { c: [ 0.48 + 0.14 * Math.cos(t * 0.09),  0.22 + 0.12 * Math.sin(t * 0.12),-0.08], a: [0,0,1], core: 0.52, strength:-0.095 },
    { c: [ 0.05, -0.05 + 0.15 * Math.sin(t * 0.07), 0.10 * Math.cos(t * 0.10)], a: [1,0,0], core: 0.70, strength: 0.060 }
  ];

  for (const e of eddies) {
    tmpA.set(p.x - e.c[0], p.y - e.c[1], p.z - e.c[2]);
    tmpB.set(e.a[0], e.a[1], e.a[2]).normalize();
    const axial = tmpA.dot(tmpB);
    tmpC.copy(tmpA).addScaledVector(tmpB, -axial);
    const r2 = tmpC.lengthSq();
    const falloff = Math.exp(-r2 / (e.core * e.core));
    tmpD.crossVectors(tmpB, tmpC);
    if (tmpD.lengthSq() > 1e-12) {
      tmpD.multiplyScalar((e.strength / e.core) * falloff);
      out.add(tmpD);
    }
  }

  // Weak large-scale vertical shear, not independent positional jitter.
  out.y += 0.012 * Math.sin(1.7 * p.x + 0.24 * t);
  out.x += 0.008 * Math.sin(1.3 * p.y - 0.17 * t);
  return out;
}

function airVorticityAt(p, t, out = new THREE.Vector3()) {
  // Central finite differences of curl(u), used for physically meaningful spin.
  // Sample positions must not alias airVelocityAt()'s internal scratch vectors.
  const h = 0.035;
  vortSamplePos[0].copy(p); vortSamplePos[0].x += h;
  vortSamplePos[1].copy(p); vortSamplePos[1].x -= h;
  vortSamplePos[2].copy(p); vortSamplePos[2].y += h;
  vortSamplePos[3].copy(p); vortSamplePos[3].y -= h;
  vortSamplePos[4].copy(p); vortSamplePos[4].z += h;
  vortSamplePos[5].copy(p); vortSamplePos[5].z -= h;

  const xp = airVelocityAt(vortSamplePos[0], t, vortSampleVel[0]);
  const xm = airVelocityAt(vortSamplePos[1], t, vortSampleVel[1]);
  const yp = airVelocityAt(vortSamplePos[2], t, vortSampleVel[2]);
  const ym = airVelocityAt(vortSamplePos[3], t, vortSampleVel[3]);
  const zp = airVelocityAt(vortSamplePos[4], t, vortSampleVel[4]);
  const zm = airVelocityAt(vortSamplePos[5], t, vortSampleVel[5]);
  const inv2h = 1 / (2 * h);

  const dUz_dy = (yp.z - ym.z) * inv2h;
  const dUy_dz = (zp.y - zm.y) * inv2h;
  const dUx_dz = (zp.x - zm.x) * inv2h;
  const dUz_dx = (xp.z - xm.z) * inv2h;
  const dUy_dx = (xp.y - xm.y) * inv2h;
  const dUx_dy = (yp.x - ym.x) * inv2h;

  out.set(dUz_dy - dUy_dz, dUx_dz - dUz_dx, dUy_dx - dUx_dy);
  return out;
}

function modeBasis(dir) {
  const x = dir.x, y = dir.y, z = dir.z;
  return [
    0.5 * (3 * y * y - 1),
    x * x - z * z,
    2 * x * z,
    x * (5 * y * y - 1),
    x * (x * x - 3 * z * z)
  ];
}

const volumeSamples = [];
for (let i = 0; i < 384; i++) {
  // Fibonacci sphere, deterministic and uniform enough for volume preservation.
  const y = 1 - 2 * (i + 0.5) / 384;
  const r = Math.sqrt(Math.max(0, 1 - y * y));
  const phi = i * Math.PI * (3 - Math.sqrt(5));
  volumeSamples.push(new THREE.Vector3(Math.cos(phi) * r, y, Math.sin(phi) * r));
}

function volumeScaleForModes(modes) {
  let meanR3 = 0;
  for (const s of volumeSamples) {
    const b = modeBasis(s);
    let f = 0;
    for (let k = 0; k < 5; k++) f += modes[k].a * b[k];
    const rr = Math.max(0.82, 1 + f);
    meanR3 += rr * rr * rr;
  }
  meanR3 /= volumeSamples.length;
  return Math.pow(meanR3, -1 / 3);
}

function bubbleMechanicalProperties(radius, opticalThicknessNm, insideDensity = RHO_INSIDE) {
  const V = (4 / 3) * Math.PI * radius ** 3;
  const A = 4 * Math.PI * radius ** 2;
  const crossArea = Math.PI * radius ** 2;
  const filmMass = RHO_WATER * A * (opticalThicknessNm * 1e-9);
  const internalMass = insideDensity * V;
  const addedMass = ADDED_MASS_COEFF * RHO_AIR * V;
  return { V, A, crossArea, filmMass, inertialMass: internalMass + filmMass + addedMass };
}

function dragCoefficientForBubble(radius, relSpeed) {
  // Schiller-Naumann correlation for a sphere, smoothly approaching the usual
  // ~0.44-0.47 inertial-regime coefficient. This lets differently sized bubbles
  // acquire genuinely different drag response instead of sharing one Cd.
  const Re = (2 * radius * RHO_AIR * relSpeed) / AIR_DYNAMIC_VISCOSITY;
  if (Re < 1e-6) return 0;
  if (Re < 1000) return 24 / Re * (1 + 0.15 * Math.pow(Re, 0.687));
  return 0.44;
}

function runMechanicsSelfTests() {
  const failures = [];

  for (const radius of [0.075, 0.10, 0.155]) {
    const props = bubbleMechanicalProperties(radius, 520);
    if (!(props.V > 0 && props.filmMass > 0 && props.inertialMass > props.filmMass)) {
      failures.push(`invalid mass/volume at R=${radius}`);
    }

    for (const l of [2, 3]) {
      const coeff = (l - 1) * (l + 1) * (l + 2);
      const omega = Math.sqrt(coeff * GAMMA_EFFECTIVE / ((RHO_AIR + RHO_INSIDE) * radius ** 3));
      if (!Number.isFinite(omega) || omega <= 0) failures.push(`invalid mode omega at R=${radius}, l=${l}`);
    }
  }

  for (const radius of [0.05, 0.10, 0.195]) {
    for (const speed of [0.01, 0.08, 0.30]) {
      const Cd = dragCoefficientForBubble(radius, speed);
      if (!Number.isFinite(Cd) || Cd <= 0 || Cd > 30) {
        failures.push(`invalid drag coefficient Cd=${Cd} at R=${radius}, v=${speed}`);
      }
    }
  }

  // Verify that the numerical radial-mode volume correction actually preserves
  // the enclosed volume for a deliberately distorted test bubble.
  const testModes = [
    { a: 0.032 }, { a: -0.019 }, { a: 0.014 }, { a: 0.010 }, { a: -0.008 }
  ];
  const scale = volumeScaleForModes(testModes);
  let correctedMeanR3 = 0;
  for (const dir of volumeSamples) {
    const basis = modeBasis(dir);
    let f = 0;
    for (let k = 0; k < 5; k++) f += testModes[k].a * basis[k];
    correctedMeanR3 += Math.pow(Math.max(0.82, 1 + f) * scale, 3);
  }
  correctedMeanR3 /= volumeSamples.length;
  if (Math.abs(correctedMeanR3 - 1) > 2e-4) {
    failures.push(`volume correction error=${correctedMeanR3 - 1}`);
  }

  const probeU = airVelocityAt(new THREE.Vector3(0.13, -0.21, 0.07), 1.7, new THREE.Vector3());
  const probeW = airVorticityAt(new THREE.Vector3(0.13, -0.21, 0.07), 1.7, new THREE.Vector3());
  if (![probeU.x, probeU.y, probeU.z, probeW.x, probeW.y, probeW.z].every(Number.isFinite)) {
    failures.push('air-flow/vorticity field produced a non-finite value');
  }

  if (failures.length) throw new Error(`Mechanics self-tests failed:\n${failures.join('\n')}`);
}

runMechanicsSelfTests();

// ---------------------------------------------------------------------------
// Film rupture / Taylor-Culick retraction
// ---------------------------------------------------------------------------
// b.surfaceTension stores the *combined* driving tension of the two air/liquid
// interfaces. Therefore the usual v_TC = sqrt(2*gamma/(rho*h)) becomes simply
// sqrt(gammaEffective/(rho*h)) here. At sub-micron h this is several-to-tens of
// metres per second, so a normal-speed bubble pop genuinely lasts only a few
// rendered frames. We intentionally do not slow that down for effect.
function taylorCulickSpeed(effectiveSurfaceTension, thicknessNm) {
  const h = Math.max(1e-12, thicknessNm * 1e-9);
  return Math.sqrt(effectiveSurfaceTension / (RHO_WATER * h));
}

function smoothstepCPU(edge0, edge1, x) {
  const t = THREE.MathUtils.clamp((x - edge0) / Math.max(1e-12, edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

function runBurstSelfTests() {
  const failures = [];
  for (const h of [220, 520, 1200]) {
    const v = taylorCulickSpeed(GAMMA_EFFECTIVE, h);
    if (!Number.isFinite(v) || v <= 0.1 || v > 100) failures.push(`invalid Taylor-Culick speed ${v} at h=${h}nm`);
  }

  // Instability scales used by the Lagrangian breakup model must remain finite
  // over the scene's actual bubble/thickness range.
  for (const Rtest of [0.05, 0.10, 0.195]) {
    for (const htest of [220e-9, 520e-9, 1200e-9]) {
      const lambda = Math.sqrt(Rtest * htest);
      const tau = Math.sqrt(RHO_WATER * Math.pow(Rtest * htest, 1.5) / GAMMA_EFFECTIVE);
      if (!(lambda > 0 && lambda < 0.01)) failures.push(`invalid rim wavelength ${lambda}`);
      if (!(tau > 0 && tau < 0.02)) failures.push(`invalid rim instability tau ${tau}`);
    }
  }

  // Removed cap volume must equal the rim volume implied by our cross-section.
  const R = 0.1, h = 520e-9;
  for (const theta of [0.2, 0.8, 1.6, 2.7]) {
    const capArea = 2 * Math.PI * R * R * (1 - Math.cos(theta));
    const rimLength = 2 * Math.PI * R * Math.sin(theta);
    const crossSection = h * capArea / rimLength;
    const err = Math.abs(crossSection * rimLength - h * capArea);
    if (err > 1e-14) failures.push(`rim mass conservation error=${err} at theta=${theta}`);
  }
  if (failures.length) throw new Error(`Burst self-tests failed:
${failures.join('\n')}`);
}

runBurstSelfTests();

// ---------------------------------------------------------------------------
// Camera-aware inflow / recycling
// ---------------------------------------------------------------------------
// Respawning is a boundary condition, not a force. A replacement bubble is
// sampled fully outside the CURRENT camera frustum, then a short copy of the
// same buoyancy + drag equations is integrated forward. We accept only spawn
// points whose unmodified physical trajectory naturally intersects the view.
// This prevents visible materialization even after orbiting or panning.
const viewFrustum = new THREE.Frustum();
const viewProjection = new THREE.Matrix4();
const spawnSphere = new THREE.Sphere();
const spawnForward = new THREE.Vector3();
const spawnRight = new THREE.Vector3();
const spawnUp = new THREE.Vector3();
const spawnCenter = new THREE.Vector3();
const spawnCandidate = new THREE.Vector3();
const spawnCandidateVelocity = new THREE.Vector3();
const spawnSimPosition = new THREE.Vector3();
const spawnSimVelocity = new THREE.Vector3();
const spawnSimAir = new THREE.Vector3();
const spawnSimRel = new THREE.Vector3();
const spawnSimForce = new THREE.Vector3();

function refreshViewFrustum() {
  camera.updateMatrixWorld();
  viewProjection.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  viewFrustum.setFromProjectionMatrix(
    viewProjection,
    camera.coordinateSystem,
    camera.reversedDepth
  );
}

function sphereTouchesCurrentView(position, radius, padding = 1.0) {
  spawnSphere.center.copy(position);
  spawnSphere.radius = radius * padding;
  return viewFrustum.intersectsSphere(spawnSphere);
}

function sampleOutsideFrustum(radius, t, outPosition, outVelocity, releaseJitter = 0.012) {
  camera.getWorldDirection(spawnForward).normalize();
  spawnRight.setFromMatrixColumn(camera.matrixWorld, 0).normalize();
  spawnUp.setFromMatrixColumn(camera.matrixWorld, 1).normalize();

  const targetDepth = Math.max(0.80, camera.position.distanceTo(controlsTarget));
  const depth = targetDepth * rand(0.86, 1.12);
  const halfHeight = Math.tan(THREE.MathUtils.degToRad(camera.fov * 0.5)) * depth;
  const halfWidth = halfHeight * camera.aspect;
  const mx = radius / Math.max(halfWidth, 1e-4) * 1.55 + rand(0.07, 0.18);
  const my = radius / Math.max(halfHeight, 1e-4) * 1.55 + rand(0.07, 0.18);

  let nx, ny;
  switch (Math.floor(rand(0, 4))) {
    case 0: nx = -1 - mx; ny = rand(-0.92, 0.92); break;
    case 1: nx =  1 + mx; ny = rand(-0.92, 0.92); break;
    case 2: nx = rand(-0.92, 0.92); ny = -1 - my; break;
    default:nx = rand(-0.92, 0.92); ny =  1 + my; break;
  }

  spawnCenter.copy(camera.position).addScaledVector(spawnForward, depth);
  outPosition.copy(spawnCenter)
    .addScaledVector(spawnRight, nx * halfWidth)
    .addScaledVector(spawnUp, ny * halfHeight);

  airVelocityAt(outPosition, t, outVelocity);
  // Tiny release variation represents unresolved local air turbulence. It is
  // not aimed at the camera and does not bias the trajectory toward the view.
  outVelocity.add(spawnSimForce.set(rand(-releaseJitter, releaseJitter), rand(-0.65 * releaseJitter, releaseJitter), rand(-0.55 * releaseJitter, 0.55 * releaseJitter)));
}

function trajectoryNaturallyEntersView(position, velocity, b, t) {
  const radius = b.radius;
  const props = bubbleMechanicalProperties(radius, b.initialThicknessNm, b.internalDensity);
  spawnSimPosition.copy(position);
  spawnSimVelocity.copy(velocity);

  const dt = 1 / 30;
  const horizon = 7.0;
  for (let elapsed = 0; elapsed < horizon; elapsed += dt) {
    if (sphereTouchesCurrentView(spawnSimPosition, radius, 0.94)) return true;

    const air = airVelocityAt(spawnSimPosition, t + elapsed, spawnSimAir);
    const rel = spawnSimRel.copy(air).sub(spawnSimVelocity);
    const relSpeed = rel.length();
    const force = spawnSimForce.set(
      0,
      (RHO_AIR * props.V - b.internalDensity * props.V - props.filmMass) * G,
      0
    );
    if (relSpeed > 1e-7) {
      const Cd = dragCoefficientForBubble(radius, relSpeed);
      const dragMag = 0.5 * RHO_AIR * Cd * props.crossArea * relSpeed * relSpeed;
      force.addScaledVector(rel, dragMag / relSpeed);
    }
    spawnSimVelocity.addScaledVector(force, dt / props.inertialMass);
    spawnSimPosition.addScaledVector(spawnSimVelocity, dt);
  }
  return false;
}

function choosePhysicalOffscreenSpawn(b, t, outPosition, outVelocity) {
  const radius = b.radius;
  refreshViewFrustum();

  // Usually succeeds in a few attempts. More attempts are cheap because this
  // runs only when a bubble crosses the simulation's outflow boundary.
  for (let attempt = 0; attempt < 96; attempt++) {
    sampleOutsideFrustum(radius, t, spawnCandidate, spawnCandidateVelocity, b.releaseVelocityJitter);
    if (sphereTouchesCurrentView(spawnCandidate, radius, 1.15)) continue;
    if (!trajectoryNaturallyEntersView(spawnCandidate, spawnCandidateVelocity, b, t)) continue;
    outPosition.copy(spawnCandidate);
    outVelocity.copy(spawnCandidateVelocity);
    return true;
  }

  // Extremely oblique camera orientations can make natural entry rare. Rather
  // than inject a camera-seeking force, keep sampling a strictly offscreen
  // boundary and accept the best available physical release. It remains hidden
  // at birth and will be recycled again later if its airflow carries it away.
  sampleOutsideFrustum(radius, t, outPosition, outVelocity, b.releaseVelocityJitter);
  while (sphereTouchesCurrentView(outPosition, radius, 1.15)) {
    sampleOutsideFrustum(radius, t, outPosition, outVelocity, b.releaseVelocityJitter);
  }
  return false;
}

const bubbles = [];
let simulationNow = performance.now() * 0.001;

function respawnBubble(b, initial = false) {
  b.age = 0;
  b.state = 'alive';
  b.burstStartTime = -1;
  b.burstDuration = 0;
  b.burstSpeed = 0;
  b.burstFilmThicknessNm = 0;
  b.U.burstActive.value = 0;
  b.U.burstCosTheta.value = 1;
  b.U.burstRimDotHalfWidth.value = 0;
  b.back.visible = true;
  b.front.visible = true;

  // A log-normal diameter distribution is a better model for a population made
  // by repeated film breakup / bubble release than a uniform min-max draw: most
  // bubbles cluster around a characteristic size, with a real small/large tail.
  b.radius = THREE.MathUtils.clamp(randLogNormal(0.105, 0.34), 0.050, 0.195);
  b.group.scale.setScalar(b.radius);

  // Soap concentration, evaporation history, and enclosed-air temperature are
  // never identical bubble-to-bubble. These small variations feed directly into
  // film mass, buoyancy, capillary frequency, damping and optical interference.
  b.initialThicknessNm = THREE.MathUtils.clamp(650 + 95 * randNormal(), 470, 880);
  b.currentMeanThicknessNm = b.initialThicknessNm;
  b.asymptoticThicknessNm = THREE.MathUtils.clamp(350 + 45 * randNormal(), 260, 450);
  b.drainageTime = THREE.MathUtils.clamp(randLogNormal(14.5, 0.24), 9.0, 23.0);
  b.surfaceTension = THREE.MathUtils.clamp(0.056 + 0.0032 * randNormal(), 0.049, 0.063);
  b.internalDensity = THREE.MathUtils.clamp(1.185 + 0.008 * randNormal(), 1.165, 1.200);
  b.modeDampingScale = THREE.MathUtils.clamp(randLogNormal(1.0, 0.18), 0.72, 1.38);

  // Unresolved release-scale turbulence excites capillary modes. Its effect on
  // shape is converted through Weber number below rather than directly assigning
  // an arbitrary deformation percentage.
  b.releaseTurbulence = THREE.MathUtils.clamp(randLogNormal(0.15, 0.30), 0.075, 0.30);
  b.releaseVelocityJitter = 0.10 * b.releaseTurbulence;
  b.turbulenceRms = THREE.MathUtils.clamp(randLogNormal(0.16, 0.28), 0.080, 0.30);
  b.turbulenceTau = THREE.MathUtils.clamp(randLogNormal(1.05, 0.25), 0.55, 1.85);
  b.microTurbulence.set(
    randNormal() * b.turbulenceRms,
    randNormal() * b.turbulenceRms,
    randNormal() * b.turbulenceRms
  );

  b.outsideTime = 0;
  b.hasEnteredView = false;

  const t = simulationNow;
  choosePhysicalOffscreenSpawn(b, t, b.group.position, b.velocity);
  b.angularVelocity.set(0, 0, 0);
  b.group.quaternion.setFromEuler(new THREE.Euler(rand(-0.5,0.5), rand(-Math.PI,Math.PI), rand(-0.5,0.5)));

  const releaseWe = RHO_AIR * b.releaseTurbulence * b.releaseTurbulence * b.radius / b.surfaceTension;
  const l2Impulse = THREE.MathUtils.clamp(0.006 + 0.95 * releaseWe, 0.007, 0.040);
  const l3Impulse = l2Impulse * 0.46;
  for (let k = 0; k < b.modes.length; k++) {
    const amp = k < 3 ? l2Impulse : l3Impulse;
    b.modes[k].a = THREE.MathUtils.clamp(randNormal() * amp * 0.55, -amp, amp);
    b.modes[k].v = randNormal() * amp * (k < 3 ? 2.8 : 3.6);
  }
  b.filmPhase = rand(-Math.PI, Math.PI);
}

function createBubble(index) {
  const U = createBubbleUniforms();
  const backMaterial = createBubbleMaterial(THREE.BackSide, U);
  const frontMaterial = createBubbleMaterial(THREE.FrontSide, U);
  const back = new THREE.Mesh(geometry, backMaterial);
  const front = new THREE.Mesh(geometry, frontMaterial);
  back.frustumCulled = true;
  front.frustumCulled = true;

  const group = new THREE.Group();
  group.add(back, front);
  scene.add(group);

  const modes = [
    { l: 2, a: 0, v: 0 },
    { l: 2, a: 0, v: 0 },
    { l: 2, a: 0, v: 0 },
    { l: 3, a: 0, v: 0 },
    { l: 3, a: 0, v: 0 }
  ];

  const b = {
    index, U, group, back, front, radius: 0.1, age: 0, outsideTime: 0, hasEnteredView: false,
    velocity: new THREE.Vector3(), angularVelocity: new THREE.Vector3(),
    modes, filmPhase: 0,
    initialThicknessNm: 650, asymptoticThicknessNm: 350, currentMeanThicknessNm: 650, drainageTime: 14.5,
    surfaceTension: GAMMA_EFFECTIVE, internalDensity: RHO_INSIDE,
    modeDampingScale: 1, releaseTurbulence: 0.15, releaseVelocityJitter: 0.015,
    turbulenceRms: 0.16, turbulenceTau: 1.05, microTurbulence: new THREE.Vector3(),
    state: 'alive', burstStartTime: -1, burstDuration: 0, burstSpeed: 0, burstFilmThicknessNm: 0,
    burstDirLocal: new THREE.Vector3(0, 0, 1),
    burstCenter: new THREE.Vector3(), burstQuaternion: new THREE.Quaternion(), burstVelocity: new THREE.Vector3(),
    burstModes: [0, 0, 0, 0, 0], burstVolumeScale: 1
  };
  respawnBubble(b, true);
  return b;
}

for (let i = 0; i < BUBBLE_COUNT; i++) bubbles.push(createBubble(i));

const reflectionNeighborScratch = [];
function reflectionProxyRadiusFor(b) {
  // Conservative bound for the live radial graph. The first three basis terms
  // are bounded by 1 in magnitude; the l=3 y31-like term peaks at ~1.377.
  // Multiplying by the existing volume correction keeps the proxy tied to the
  // actual deformed geometry rather than using a fixed visual fudge radius.
  const m = b.modes;
  const envelope = Math.abs(m[0].a) + Math.abs(m[1].a) + Math.abs(m[2].a)
    + 1.38 * Math.abs(m[3].a) + Math.abs(m[4].a);
  return b.radius * b.U.volumeScale.value * (1 + envelope) * INTER_BUBBLE_PROXY_MARGIN;
}

function updateReflectionNeighborhoods() {
  // With only 20 bubbles the CPU O(N^2) center pass is tiny. It replaces an
  // O(N) per-fragment GPU loop with just K candidates. Rank by approximate
  // angular size, so a slightly farther large bubble can beat a tiny close one.
  for (const b of bubbles) {
    reflectionNeighborScratch.length = 0;
    for (const other of bubbles) {
      if (other === b || other.state !== 'alive') continue;
      const primaryProxy = reflectionProxyRadiusFor(b);
      const otherProxy = reflectionProxyRadiusFor(other);
      const d = Math.max(1e-4, b.group.position.distanceTo(other.group.position) - primaryProxy);
      const angularScore = d / Math.max(otherProxy, 1e-4);
      reflectionNeighborScratch.push({ other, score: angularScore, proxyRadius: otherProxy });
    }
    reflectionNeighborScratch.sort((a, c) => a.score - c.score);

    for (let k = 0; k < INTER_BUBBLE_CANDIDATES; k++) {
      const peerU = b.U.reflectionPeers[k];
      const entry = reflectionNeighborScratch[k];
      const selected = entry?.other;
      if (selected) {
        peerU.center.value.copy(selected.group.position);
        peerU.radius.value = entry.proxyRadius;
        peerU.meanThicknessNm.value = selected.currentMeanThicknessNm;
      } else {
        peerU.center.value.set(1e4, 1e4, 1e4);
        peerU.radius.value = 0;
        peerU.meanThicknessNm.value = 520;
      }
    }
  }
}

function updateBubble(b, dt, t) {
  // Once punctured, a coherent closed bubble no longer exists. Retraction is
  // integrated separately at real wall-clock time below; translation over those
  // few milliseconds is negligible compared with the capillary edge velocity.
  if (b.state !== 'alive') return;

  b.age += dt;

  // Film drains gradually as the bubble ages. This mean thickness is also used
  // in the film mass, coupling optics back into mechanics at first order.
  const meanThicknessNm = b.asymptoticThicknessNm +
    (b.initialThicknessNm - b.asymptoticThicknessNm) * Math.exp(-b.age / b.drainageTime);
  b.currentMeanThicknessNm = meanThicknessNm;
  const props = bubbleMechanicalProperties(b.radius, meanThicknessNm, b.internalDensity);

  // Unresolved atmospheric turbulence is represented as an Ornstein-Uhlenbeck
  // velocity process: finite RMS energy and finite correlation time, rather than
  // frame-to-frame white-noise jitter. It continuously excites both translation
  // and the capillary modes and gives each bubble a different natural history.
  const turbDecay = Math.exp(-dt / b.turbulenceTau);
  const turbNoise = b.turbulenceRms * Math.sqrt(Math.max(0, 1 - turbDecay * turbDecay));
  b.microTurbulence.multiplyScalar(turbDecay);
  b.microTurbulence.x += randNormal() * turbNoise;
  b.microTurbulence.y += randNormal() * turbNoise;
  b.microTurbulence.z += randNormal() * turbNoise;

  const air = airVelocityAt(b.group.position, t, stepAir).add(b.microTurbulence);
  const rel = stepRel.copy(air).sub(b.velocity); // fluid velocity relative to bubble
  const relSpeed = rel.length();

  // Buoyancy + actual weight of enclosed gas and liquid film.
  const force = stepForce.set(0, (RHO_AIR * props.V - b.internalDensity * props.V - props.filmMass) * G, 0);

  // Quadratic aerodynamic drag, opposite bubble-relative airflow and therefore
  // in the direction of (air velocity - bubble velocity).
  if (relSpeed > 1e-7) {
    const Cd = dragCoefficientForBubble(b.radius, relSpeed);
    const dragMag = 0.5 * RHO_AIR * Cd * props.crossArea * relSpeed * relSpeed;
    force.addScaledVector(rel, dragMag / relSpeed);
  }

  // Semi-implicit Euler is stable enough at the capped real-time step here.
  b.velocity.addScaledVector(force, dt / props.inertialMass);
  b.group.position.addScaledVector(b.velocity, dt);

  // A neutrally deformable sphere in a slowly varying flow tends toward half
  // the local fluid vorticity. Relax rotational velocity toward that target.
  const vort = airVorticityAt(b.group.position, t, stepVort).multiplyScalar(0.5);
  b.angularVelocity.lerp(vort, 1 - Math.exp(-dt / 0.75));
  const spin = b.angularVelocity.length();
  if (spin > 1e-7) {
    tmpQ.setFromAxisAngle(tmpA.copy(b.angularVelocity).multiplyScalar(1 / spin), spin * dt);
    b.group.quaternion.premultiply(tmpQ).normalize();
  }

  // Rayleigh-Lamb-style capillary shape modes. Natural frequency scales as
  // sqrt(gamma / (rho * R^3)); aerodynamic deformation scales with Weber no.
  const relForcing = relSpeed > 1e-5
    ? stepRelDir.copy(rel).multiplyScalar(1 / relSpeed)
    : stepRelDir.set(0, 1, 0);
  const invQ = stepInvQ.copy(b.group.quaternion).invert();
  const qLocal = stepLocalDir.copy(relForcing).applyQuaternion(invQ);
  const basis = modeBasis(qLocal);
  const rhoEff = RHO_AIR + b.internalDensity;
  const We = RHO_AIR * relSpeed * relSpeed * b.radius / b.surfaceTension;
  const l2Strength = Math.min(0.032, 0.17 * We);

  for (let k = 0; k < b.modes.length; k++) {
    const m = b.modes[k];
    const coeff = (m.l - 1) * (m.l + 1) * (m.l + 2);
    const omega = Math.sqrt(coeff * b.surfaceTension / (rhoEff * b.radius ** 3));
    const zeta = (m.l === 2 ? 0.045 : 0.065) * b.modeDampingScale;
    const target = (m.l === 2 ? l2Strength : l2Strength * 0.26) * basis[k];
    const accel = omega * omega * (target - m.a) - 2 * zeta * omega * m.v;
    m.v += accel * dt;
    m.a += m.v * dt;
    m.a = THREE.MathUtils.clamp(m.a, m.l === 2 ? -0.045 : -0.020, m.l === 2 ? 0.045 : 0.020);
  }

  // Surface circulation speed is coupled to local air speed and vorticity;
  // thickness texture motion is therefore not a free-running visual animation.
  b.filmPhase += dt * (0.20 + 0.85 * relSpeed + 0.15 * spin);

  const volScale = volumeScaleForModes(b.modes);
  for (let k = 0; k < 5; k++) b.U.modes[k].value = b.modes[k].a;
  b.U.volumeScale.value = volScale;
  b.U.meanThicknessNm.value = meanThicknessNm;
  b.U.filmPhase.value = b.filmPhase;

  // Camera-aware lifecycle. A new offscreen bubble is allowed to complete its
  // naturally inward trajectory. Once it has genuinely entered the frustum,
  // recycling is enabled only after it stays well outside an expanded view for
  // a while. This avoids both in-frame births and orbit/pan-induced popping.
  const actuallyVisible = sphereTouchesCurrentView(b.group.position, b.radius, 1.0);
  const nearView = sphereTouchesCurrentView(b.group.position, b.radius, 2.4);
  if (actuallyVisible) b.hasEnteredView = true;

  if (b.hasEnteredView) {
    if (nearView) {
      b.outsideTime = 0;
    } else {
      b.outsideTime += dt;
      if (b.outsideTime > 2.4) respawnBubble(b, false);
    }
  } else if (b.age > 10.0 && !nearView) {
    // Camera motion can invalidate the entry prediction made at spawn time.
    // Re-sample the offscreen inflow boundary rather than steering the bubble.
    respawnBubble(b, false);
  }
}

// ---------------------------------------------------------------------------
// Interactive puncture + low-cost visible liquid-drop aftermath
// ---------------------------------------------------------------------------
const raycaster = new THREE.Raycaster();
const pointerNDC = new THREE.Vector2();
const pointerDown = new THREE.Vector2();
let pointerDownTime = 0;

// The coherent film still retracts with Taylor-Culick physics in the membrane
// shader. For the aftermath we deliberately resolve only the few millimetre-scale
// drops that are visually meaningful at this camera distance. The much more
// numerous microscopic film drops are treated as unresolved aerosol rather than
// rasterizing thousands of sub-pixel particles. This is both faster and, at normal
// viewing distance, closer to what a real camera actually lets you perceive.
const VISIBLE_DROP_POOL_SIZE = 64;
const VISIBLE_DROP_MAX_AGE = 3.0;
const WATER_SURFACE_TENSION = 0.056; // N/m, same effective soap solution scale
const MIN_VISIBLE_DROP_RENDER_RADIUS = 0.0011; // 1.1 mm visual floor for readability
const Y_AXIS = new THREE.Vector3(0, 1, 0);

function createVisibleDropMaterial() {
  // Thick detached liquid is no longer a coherent nanometre film. Keep this
  // deliberately cheap: a real 3-D surface with water/air Fresnel reflection,
  // rather than MeshPhysical transmission (which would add a costly scene pass).
  const mat = new THREE.MeshBasicNodeMaterial();
  mat.transparent = true;
  mat.depthTest = true;
  mat.depthWrite = false;
  mat.blending = THREE.NormalBlending;
  mat.side = THREE.FrontSide;

  mat.fragmentNode = TSL.Fn(() => {
    const N = TSL.normalize(TSL.normalWorld);
    const I = TSL.normalize(TSL.positionWorld.sub(TSL.cameraPosition));
    const cosI = TSL.clamp(TSL.abs(TSL.dot(I, N)), F(0), F(1));
    const f0 = F(Math.pow((1.333 - N_AIR) / (1.333 + N_AIR), 2));
    const omc = F(1).sub(cosI);
    const fresnel = f0.add(F(1).sub(f0).mul(
      omc.mul(omc).mul(omc).mul(omc).mul(omc)
    ));
    const reflected = TSL.texture(envMap, TSL.equirectUV(TSL.reflect(I, N))).rgb;

    // A weak body term keeps the millimetre drop readable away from its bright
    // Fresnel edge while the HDR reflection supplies the physically important
    // highlight. This is much cheaper than screen-space transmission.
    const alpha = TSL.clamp(F(0.34).add(fresnel.mul(0.46)), F(0.34), F(0.94));
    const body = TSL.texture(envMap, TSL.equirectUV(N.negate())).rgb.mul(0.095);
    const rgb = reflected.mul(F(0.28).add(fresnel.mul(1.55)))
      .add(body)
      .add(TSL.vec3(fresnel.mul(0.06)));
    return TSL.vec4(rgb, alpha);
  })();
  return mat;
}

const visibleDropGeometry = new THREE.IcosahedronGeometry(1, 4);
const visibleDropMaterial = createVisibleDropMaterial();
const visibleDropMesh = new THREE.InstancedMesh(
  visibleDropGeometry,
  visibleDropMaterial,
  VISIBLE_DROP_POOL_SIZE
);
visibleDropMesh.count = 0;
visibleDropMesh.frustumCulled = false;
visibleDropMesh.renderOrder = 1200;
visibleDropMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(visibleDropMesh);

const visibleDrops = Array.from({ length: VISIBLE_DROP_POOL_SIZE }, (_, index) => ({
  index,
  active: false,
  ownerIndex: -1,
  age: 0,
  lastTime: 0,
  radius: 0.0015,
  position: new THREE.Vector3(),
  velocity: new THREE.Vector3(),
  capillaryPhase: 0,
  capillaryOmega: 0,
  surfaceTension: WATER_SURFACE_TENSION
}));
const freeVisibleDropIndices = [];
for (let i = VISIBLE_DROP_POOL_SIZE - 1; i >= 0; i--) freeVisibleDropIndices.push(i);

const dropAir = new THREE.Vector3();
const dropRel = new THREE.Vector3();
const dropForce = new THREE.Vector3();
const dropMotionDir = new THREE.Vector3();
const dropQuatScratch = new THREE.Quaternion();
const dropScaleScratch = new THREE.Vector3();
const dropMatrixScratch = new THREE.Matrix4();
const burstRingDir = new THREE.Vector3();
const burstLocalNormal = new THREE.Vector3();
const burstLocalTangent = new THREE.Vector3();
const burstLocalAzimuth = new THREE.Vector3();
const burstWorldNormal = new THREE.Vector3();
const burstWorldTangent = new THREE.Vector3();
const burstWorldAzimuth = new THREE.Vector3();
const burstOriginScratch = new THREE.Vector3();
const burstVelocityScratch = new THREE.Vector3();

function localSurfaceRadiusFromSnapshot(b, dir) {
  const basis = modeBasis(dir);
  let f = 0;
  for (let k = 0; k < 5; k++) f += b.burstModes[k] * basis[k];
  return Math.max(0.82, 1 + f) * b.burstVolumeScale;
}

function approximateBurstThicknessNm(b, localDir) {
  // Match the existing gravity-drainage field at the puncture. The puncture
  // thickness determines the local Taylor-Culick retraction speed.
  burstWorldNormal.copy(localDir).applyQuaternion(b.group.quaternion).normalize();
  const drainage = 1 - burstWorldNormal.y * 0.24;
  const bottom = smoothstepCPU(0.35, 0.95, -burstWorldNormal.y);
  return THREE.MathUtils.clamp(
    b.currentMeanThicknessNm * drainage + bottom * bottom * 260,
    170, 1450
  );
}

function averageBurstFilmThicknessNm(b) {
  // Total liquid mass belongs to the whole membrane, not only the click point.
  let sum = 0;
  for (const localDir of volumeSamples) {
    burstWorldNormal.copy(localDir).applyQuaternion(b.burstQuaternion).normalize();
    const drainage = 1 - burstWorldNormal.y * 0.24;
    const bottom = smoothstepCPU(0.35, 0.95, -burstWorldNormal.y);
    sum += THREE.MathUtils.clamp(
      b.currentMeanThicknessNm * drainage + bottom * bottom * 260,
      170, 1450
    );
  }
  return sum / volumeSamples.length;
}

function makeBasisAroundDirection(dir, outA, outB) {
  if (Math.abs(dir.y) < 0.88) outA.set(0, 1, 0);
  else outA.set(1, 0, 0);
  outA.cross(dir).normalize();
  outB.crossVectors(dir, outA).normalize();
}

function sphericalSurfaceFrame(b, theta, phi, outPos, outTangent, outAzimuth, outNormal) {
  const cp = Math.cos(phi), sp = Math.sin(phi);
  const c = Math.cos(theta), st = Math.sin(theta);
  burstRingDir.copy(b.burstBasisA).multiplyScalar(cp).addScaledVector(b.burstBasisB, sp);
  burstLocalNormal.copy(b.burstDirLocal).multiplyScalar(c).addScaledVector(burstRingDir, st).normalize();
  burstLocalTangent.copy(b.burstDirLocal).multiplyScalar(-st).addScaledVector(burstRingDir, c).normalize();
  burstLocalAzimuth.crossVectors(burstLocalNormal, burstLocalTangent).normalize();

  const rr = localSurfaceRadiusFromSnapshot(b, burstLocalNormal);
  outNormal.copy(burstLocalNormal).applyQuaternion(b.burstQuaternion).normalize();
  outTangent.copy(burstLocalTangent).applyQuaternion(b.burstQuaternion).normalize();
  outAzimuth.copy(burstLocalAzimuth).applyQuaternion(b.burstQuaternion).normalize();
  outPos.copy(b.burstCenter).addScaledVector(outNormal, b.radius * rr);
  return outPos;
}

function allocateVisibleDrop() {
  let idx = freeVisibleDropIndices.pop();
  if (idx === undefined) {
    // Rare case: if the user bursts many bubbles in rapid succession, recycle the
    // oldest drop instead of growing the pool or creating a performance spike.
    let oldest = null;
    for (const d of visibleDrops) {
      if (d.active && (!oldest || d.age > oldest.age)) oldest = d;
    }
    if (!oldest) return null;
    idx = oldest.index;
  }
  const d = visibleDrops[idx];
  d.active = true;
  return d;
}

function releaseVisibleDrop(d) {
  if (!d.active) return;
  d.active = false;
  d.ownerIndex = -1;
  if (!freeVisibleDropIndices.includes(d.index)) freeVisibleDropIndices.push(d.index);
}

function chooseVisibleDropCount() {
  // This is the *visible* coarse-grained aftermath. Bias toward 3-4 resolvable
  // millimetre-scale fragments, because at real-time speed that is what the eye
  // actually follows after the shell snaps away.
  return THREE.MathUtils.clamp(Math.round(3.15 + 0.75 * randNormal()), 2, 5);
}

function prepareVisibleBurstDrops(b, now) {
  const avgThicknessNm = averageBurstFilmThicknessNm(b);
  b.burstAverageFilmThicknessNm = avgThicknessNm;
  const filmVolume = 4 * Math.PI * b.radius * b.radius * avgThicknessNm * 1e-9;
  const count = chooseVisibleDropCount();

  // Only a minority of the membrane volume is resolved as visible fragments.
  // That keeps the fragments in the millimetre regime rather than turning the
  // whole bubble into a few implausibly giant drops, while the rest is the
  // unresolved micro-spray you perceive only as a fleeting mist.
  const resolvedFraction = THREE.MathUtils.clamp(0.26 + 0.05 * randNormal(), 0.16, 0.38);
  const resolvedVolume = filmVolume * resolvedFraction;

  const heroIndex = Math.floor(rng() * count);
  const weights = [];
  let sumW = 0;
  for (let i = 0; i < count; i++) {
    const heroBias = i === heroIndex ? rand(1.45, 2.10) : rand(0.55, 1.05);
    const w = heroBias * Math.exp(0.22 * randNormal());
    weights.push(w);
    sumW += w;
  }

  b.pendingVisibleDrops = [];
  for (let i = 0; i < count; i++) {
    const volume = resolvedVolume * weights[i] / sumW;
    const radius = Math.cbrt(3 * volume / (4 * Math.PI));
    const late = i === heroIndex || rng() < 0.55;
    b.pendingVisibleDrops.push({
      released: false,
      volume,
      radius,
      // Most visible fragments come late, near the antipodal collapse, because
      // that is where the swept liquid is most concentrated at real-time speed.
      releaseFraction: late
        ? THREE.MathUtils.clamp(0.78 + 0.20 * rng(), 0.72, 0.985)
        : THREE.MathUtils.clamp(0.54 + 0.22 * rng(), 0.48, 0.86),
      phi: rand(0, Math.PI * 2),
      speedFraction: THREE.MathUtils.clamp(0.74 + 0.16 * randNormal(), 0.50, 1.05),
      transverse: randNormal(),
      late
    });
  }
  b.unresolvedBurstMistVolume = filmVolume - resolvedVolume;
}

function releasePreparedDrop(b, spec, now) {
  const d = allocateVisibleDrop();
  if (!d) return;

  const theta = Math.PI * Math.min(spec.releaseFraction, 0.992);
  sphericalSurfaceFrame(
    b, theta, spec.phi,
    burstOriginScratch, burstWorldTangent, burstWorldAzimuth, burstWorldNormal
  );

  // The dominant visible fragments are shed from the retracting rim and from the
  // final antipodal collapse. Earlier releases mostly follow the rim tangent;
  // very late releases get a stronger outward kick from the collapsing knot.
  const launchSpeed = b.burstSpeed * spec.speedFraction;
  const collapseBias = smoothstepCPU(0.70, 0.98, spec.releaseFraction);
  burstVelocityScratch.copy(b.burstVelocity)
    .addScaledVector(burstWorldTangent, launchSpeed * (0.88 - 0.20 * collapseBias))
    .addScaledVector(burstWorldAzimuth, launchSpeed * (0.09 + 0.05 * collapseBias) * spec.transverse)
    .addScaledVector(burstWorldNormal, launchSpeed * (0.04 + 0.28 * collapseBias) * rand(-0.6, 1.0))
    .addScaledVector(Y_AXIS, -Math.min(0.65, launchSpeed * rand(0.03, 0.09)));

  d.position.copy(burstOriginScratch)
    .addScaledVector(burstWorldNormal, spec.radius * rand(0.15, 0.45))
    .addScaledVector(burstWorldTangent, spec.radius * rand(0.5, 1.4));
  d.velocity.copy(burstVelocityScratch);
  d.radius = spec.radius;
  d.ownerIndex = b.index;
  d.age = 0;
  d.lastTime = now;
  d.capillaryPhase = rand(0, Math.PI * 2);
  d.surfaceTension = b.surfaceTension;
  // Rayleigh l=2 mode for a free liquid drop: omega^2 = 8 sigma / (rho r^3).
  d.capillaryOmega = Math.sqrt(
    8 * d.surfaceTension / (RHO_WATER * Math.max(d.radius ** 3, 1e-15))
  );
}

function updateVisibleDrops(now) {
  let instanceIndex = 0;

  for (const d of visibleDrops) {
    if (!d.active) continue;

    const elapsed = THREE.MathUtils.clamp(now - d.lastTime, 0, 1 / 30);
    // A few real droplets only need a modest integrator. 240 Hz is plenty for
    // millimetre drops and is orders of magnitude cheaper than the old 0.5 ms
    // thousands-of-particles solver.
    const substeps = Math.max(1, Math.ceil(elapsed / (1 / 240)));
    const h = elapsed / substeps;

    let lastRelSpeed = 0;
    for (let step = 0; step < substeps; step++) {
      const sampleTime = d.lastTime + (step + 0.5) * h;
      const air = airVelocityAt(d.position, sampleTime, dropAir);
      const rel = dropRel.copy(air).sub(d.velocity);
      const speed = rel.length();
      lastRelSpeed = speed;
      const V = (4 / 3) * Math.PI * d.radius ** 3;
      const mass = RHO_WATER * V;
      const area = Math.PI * d.radius ** 2;
      const force = dropForce.set(0, -(RHO_WATER - RHO_AIR) * V * G, 0);

      if (speed > 1e-6) {
        const Re = (2 * d.radius * RHO_AIR * speed) / AIR_DYNAMIC_VISCOSITY;
        const Cd = Re < 1000
          ? 24 / Math.max(Re, 1e-6) * (1 + 0.15 * Math.pow(Re, 0.687))
          : 0.44;
        const dragMag = 0.5 * RHO_AIR * Cd * area * speed * speed;
        force.addScaledVector(rel, dragMag / speed);
      }

      d.velocity.addScaledVector(force, h / mass);
      d.position.addScaledVector(d.velocity, h);
    }

    d.age += elapsed;
    d.lastTime = now;

    if (d.age > VISIBLE_DROP_MAX_AGE || d.position.distanceToSquared(camera.position) > 100) {
      releaseVisibleDrop(d);
      continue;
    }

    // These are actual geometry droplets. Keep their volume constant while
    // surface tension and aerodynamic pressure deform them. A falling water drop
    // is not a teardrop: it tends toward an oblate/oscillating shape.
    dropMotionDir.copy(d.velocity);
    if (dropMotionDir.lengthSq() < 1e-8) dropMotionDir.set(0, -1, 0);
    dropMotionDir.normalize();
    dropQuatScratch.setFromUnitVectors(Y_AXIS, dropMotionDir);

    const renderRadius = Math.max(d.radius, MIN_VISIBLE_DROP_RENDER_RADIUS);
    const Weber = RHO_AIR * lastRelSpeed * lastRelSpeed * (2 * d.radius)
      / Math.max(d.surfaceTension, 1e-9);
    const aerodynamicFlatten = THREE.MathUtils.clamp(0.055 * Weber, 0, 0.22);
    const capillaryOscillation = 0.13
      * Math.exp(-d.age * 2.6)
      * Math.sin(d.capillaryOmega * d.age + d.capillaryPhase);
    const launchStretch = 0.34
      * Math.exp(-d.age * 14.0)
      * THREE.MathUtils.clamp(lastRelSpeed / 2.4, 0, 1.25);
    const parallel = THREE.MathUtils.clamp(
      1 - aerodynamicFlatten + capillaryOscillation + launchStretch,
      0.76,
      1.85
    );
    const transverseScale = 1 / Math.sqrt(parallel); // volume preserving

    dropScaleScratch.set(
      renderRadius * transverseScale,
      renderRadius * parallel,
      renderRadius * transverseScale
    );
    dropMatrixScratch.compose(d.position, dropQuatScratch, dropScaleScratch);
    visibleDropMesh.setMatrixAt(instanceIndex++, dropMatrixScratch);
  }

  visibleDropMesh.count = instanceIndex;
  if (instanceIndex > 0) visibleDropMesh.instanceMatrix.needsUpdate = true;
}

function beginBubbleBurst(b, localDir, now) {
  if (b.state !== 'alive') return;

  b.state = 'bursting';
  b.burstStartTime = now;
  b.burstDirLocal.copy(localDir).normalize();
  b.burstCenter.copy(b.group.position);
  b.burstQuaternion.copy(b.group.quaternion);
  b.burstVelocity.copy(b.velocity);
  for (let k = 0; k < 5; k++) b.burstModes[k] = b.modes[k].a;
  b.burstVolumeScale = b.U.volumeScale.value;
  b.burstBasisA = b.burstBasisA || new THREE.Vector3();
  b.burstBasisB = b.burstBasisB || new THREE.Vector3();
  makeBasisAroundDirection(b.burstDirLocal, b.burstBasisA, b.burstBasisB);

  b.burstFilmThicknessNm = approximateBurstThicknessNm(b, b.burstDirLocal);
  b.burstSpeed = taylorCulickSpeed(b.surfaceTension, b.burstFilmThicknessNm);
  b.burstDuration = Math.PI * b.radius / b.burstSpeed;
  b.burstShellDone = false;
  b.burstShellDoneTime = -1;

  b.U.burstActive.value = 1;
  b.U.burstDirLocal.value.copy(b.burstDirLocal);
  b.U.burstCosTheta.value = 1;
  b.U.burstRimDotHalfWidth.value = 1e-7;

  prepareVisibleBurstDrops(b, now);
}

function updateBurstAnimations(now) {
  for (const b of bubbles) {
    if (b.state !== 'bursting') continue;

    const elapsed = Math.max(0, now - b.burstStartTime);
    const progress = THREE.MathUtils.clamp(elapsed / Math.max(b.burstDuration, 1e-5), 0, 1);
    const theta = Math.PI * progress;
    const cosTheta = Math.cos(theta);

    if (!b.burstShellDone) {
      b.U.burstCosTheta.value = cosTheta;

      // Analytically collect swept film into the retracting rim solely to derive
      // the shader's physical rim width. No CPU rim mesh, no ligament pool, and
      // no millisecond substep loop are required.
      const avgThickness = b.burstAverageFilmThicknessNm * 1e-9;
      const filmVolume = 4 * Math.PI * b.radius * b.radius * avgThickness;
      const sweptVolume = filmVolume * 0.5 * (1 - cosTheta);
      const rimLength = Math.max(2 * Math.PI * b.radius * Math.sin(theta), 1e-8);
      const rimRadius = Math.sqrt(Math.max(0, sweptVolume / rimLength) / Math.PI);
      const angularHalfWidth = Math.min(0.045, rimRadius / Math.max(b.radius, 1e-6));
      b.U.burstRimDotHalfWidth.value = Math.max(
        1e-7,
        Math.max(1e-5, Math.sin(theta)) * angularHalfWidth
          + 0.5 * angularHalfWidth * angularHalfWidth
      );

      for (const spec of b.pendingVisibleDrops || []) {
        if (!spec.released && progress >= spec.releaseFraction) {
          spec.released = true;
          releasePreparedDrop(b, spec, now);
        }
      }

      if (progress >= 1) {
        b.burstShellDone = true;
        b.burstShellDoneTime = now;
        b.back.visible = false;
        b.front.visible = false;
        b.U.burstActive.value = 0;

        // If frame cadence skipped over a scheduled release during this very fast
        // rupture, release it now instead of silently losing it.
        for (const spec of b.pendingVisibleDrops || []) {
          if (!spec.released) {
            spec.released = true;
            releasePreparedDrop(b, spec, now);
          }
        }
      }
    }

    // Respawn the owning bubble shortly after the shell has vanished. Detached
    // drops are independent scene objects and keep falling after respawn.
    if (b.burstShellDone && now - b.burstShellDoneTime > 0.10) {
      respawnBubble(b, false);
    }
  }
}

function pickBubbleAt(clientX, clientY, now) {
  const rect = domElement.getBoundingClientRect();
  pointerNDC.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  pointerNDC.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointerNDC, camera);

  const hits = raycaster.intersectObjects(bubbles.map(b => b.front), false);
  for (const hit of hits) {
    const b = hit.object.userData.bubble;
    if (!b || b.state !== 'alive') continue;

    b.group.updateWorldMatrix(true, false);
    const localDir = b.group.worldToLocal(hit.point.clone()).normalize();
    beginBubbleBurst(b, localDir, now);
    return b;
  }
  return null;
}

for (const b of bubbles) b.front.userData.bubble = b;

function onPointerDown(e) {
  if (e.button !== 0) return;
  pointerDown.set(e.clientX, e.clientY);
  pointerDownTime = performance.now();
}

function onPointerUp(e) {
  if (e.button !== 0) return;
  const dx = e.clientX - pointerDown.x;
  const dy = e.clientY - pointerDown.y;
  const moved = Math.hypot(dx, dy);
  const heldMs = performance.now() - pointerDownTime;
  if (moved <= 5 && heldMs < 450) {
    pickBubbleAt(e.clientX, e.clientY, simulationNow);
  }
}

domElement.addEventListener('pointerdown', onPointerDown);
domElement.addEventListener('pointerup', onPointerUp);

function prewarmBubbleHistory() {
  // Seed several seconds of unseen history before the first rendered frame.
  // Therefore bubbles visible on frame 1 have already crossed the frustum edge
  // in simulation time; none are born/materialized inside the image.
  refreshViewFrustum();
  const dt = 1 / 60;
  const duration = 6.5;
  const start = simulationNow - duration;
  for (let elapsed = 0; elapsed < duration; elapsed += dt) {
    const t = start + elapsed;
    for (const b of bubbles) updateBubble(b, dt, t);
  }
}

prewarmBubbleHistory();
updateReflectionNeighborhoods();

function updateTransparentOrder() {
  // Normal transparent-object sorting is center-based; explicit dynamic ordering
  // keeps each rear membrane immediately before its corresponding front membrane.
  const ordered = [...bubbles].sort((a, b) => {
    const da = camera.position.distanceToSquared(a.group.position);
    const db = camera.position.distanceToSquared(b.group.position);
    return db - da; // far to near
  });
  for (let i = 0; i < ordered.length; i++) {
    ordered[i].back.renderOrder = i * 2;
    ordered[i].front.renderOrder = i * 2 + 1;
  }
}

let simAccumulator = 0;
const FIXED_STEP = 1 / 120;
const MAX_STEPS = 5;
let debugMode = 'final';

function applyDebugMode() {
  const spherical = debugMode === 'spherical-membranes';
  const rearOnly = debugMode === 'rear-membranes';
  const noInterreflection = debugMode === 'no-interreflection';

  for (const b of bubbles) {
    if (spherical) {
      for (const mode of b.U.modes) mode.value = 0;
      b.U.volumeScale.value = 1;
    }
    if (noInterreflection) {
      for (const peer of b.U.reflectionPeers) peer.radius.value = 0;
    }
    const shellVisible = b.state === 'alive' ||
      (b.state === 'bursting' && !b.burstShellDone);
    b.back.visible = shellVisible;
    b.front.visible = shellVisible && !rearOnly;
  }
  visibleDropMesh.visible = !rearOnly;
}

function update(frameDelta) {
  const frameDt = Math.min(0.05, Math.max(0, frameDelta));
  simulationNow += frameDt;
  simAccumulator += frameDt;

  refreshViewFrustum();

  let steps = 0;
  while (simAccumulator >= FIXED_STEP && steps < MAX_STEPS) {
    for (const b of bubbles) updateBubble(b, FIXED_STEP, simulationNow);
    simAccumulator -= FIXED_STEP;
    steps++;
  }
  if (steps === MAX_STEPS) simAccumulator = 0; // avoid spiral-of-death after tab stalls

  // Rupture uses the same advancing clock as the mechanics, retaining its
  // millisecond-scale Taylor-Culick front while allowing an inspection host to pause.
  updateBurstAnimations(simulationNow);
  updateVisibleDrops(simulationNow);

  updateReflectionNeighborhoods();
  updateTransparentOrder();
  applyDebugMode();
}

return {
  group: scene,
  bubbles,
  visibleDropMesh,
  setDebugMode(mode) {
    debugMode = thinFilmSoapBubbleDebugModes.includes(mode) ? mode : 'final';
    applyDebugMode();
  },
  update,
  metrics() {
    return {
      bubbles: String(BUBBLE_COUNT),
      reflectionPeers: String(INTER_BUBBLE_CANDIDATES),
      visibleDropPool: String(VISIBLE_DROP_POOL_SIZE),
      physicsChecks: 'pass'
    };
  },
  dispose() {
    domElement.removeEventListener('pointerdown', onPointerDown);
    domElement.removeEventListener('pointerup', onPointerUp);
    const geometries = new Set();
    const materials = new Set();
    scene.traverse((object) => {
      if (object.geometry) geometries.add(object.geometry);
      if (Array.isArray(object.material)) {
        for (const material of object.material) materials.add(material);
      } else if (object.material) {
        materials.add(object.material);
      }
    });
    for (const geometry of geometries) geometry.dispose();
    for (const material of materials) material.dispose();
    scene.clear();
  }
};
}
