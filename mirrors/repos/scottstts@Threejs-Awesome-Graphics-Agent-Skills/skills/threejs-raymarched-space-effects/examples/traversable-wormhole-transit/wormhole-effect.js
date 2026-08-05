import * as THREE from "three";
import {
  CELESTIAL_SPHERES_GLSL,
  createCelestialSphereUniforms,
} from "./celestial-spheres.js";

/* ==================================================================================
   TRAVERSABLE WORMHOLE — physically integrated gravitational lensing
   ----------------------------------------------------------------------------------
   The throat is an ultrastatic, spherically symmetric metric with a cylindrical
   neck and a smooth lensing shoulder on either side:

       ds^2 = -dt^2 + dl^2 + r(l)^2 (dtheta^2 + sin^2 theta dphi^2)

   l  : proper radial distance, negative on the far side (a single global coordinate
        that runs straight through the throat into the other universe)
   rho: throat radius            a: half-length of the cylindrical throat
   M  : lensing parameter, related to the lensing width by  W = 1.42953 M

   Because the metric is ultrastatic and spherically symmetric, every null geodesic
   stays in the plane spanned by the camera's radial vector and the ray's tangential
   component. That plane reduction is exact, kills the polar coordinate singularity,
   and leaves a 3-variable ODE system with one conserved quantity b = r^2 dpsi/dt:

       dl/dt   = p_l
       dpsi/dt = b / r^2
       dp_l/dt = b^2 (dr/dl) / r^3

   which is integrated with adaptive RK4 in the fragment shader, per pixel, until the
   ray escapes to the asymptotically flat region of one universe or the other. The
   image is then whatever celestial sphere the ray actually landed on. Nothing is
   faked in screen space: the crystal-ball sphere, the razor-thin distortion rim, the
   folding of the sky into a tube during transit, and the unfolding on the far side
   are all consequences of the integration.

   Shape is fixed at 2a/rho = 0.01, W/rho = 0.05. Nothing moves on its own; the
   observer is the only animation, and a still observer converges.
   ================================================================================== */

const W2M = 1.42953; // W = 1.42953 * M, the lensing width in terms of M

// --- wormhole: rho is the unit of length ------------------------------------------
const RHO = 1.0;
const W_OVER_RHO = 0.05; // lensing width / rho
const A_OVER_RHO = 0.005; // throat half-length / rho, i.e. 2a/rho = 0.01
const M_LENS = (W_OVER_RHO * RHO) / W2M;
const THROAT_A = A_OVER_RHO * RHO;

// --- integrator -------------------------------------------------------------------
// STEP_K 0.15 keeps the worst-case (grazing-the-rim) ray within ~0.13 px of a
// 40000-step solution at 1080p/50deg, for ~25-98 RK4 steps per ray.
const MAX_STEPS = 1024;
const STEP_K = 0.15;
const ESCAPE_RADIUS = 260.0;

// --- observer ---------------------------------------------------------------------
const FOV_DEGREES = 50.0;
const FOV_MIN = 15.0;
const FOV_MAX = 110.0;
const FOV_ZOOM_STEP = 0.06;
const FOV_SMOOTHING = 8.0;
const LOOK_SENSITIVITY = 0.0022;
const PITCH_LIMIT = 1.55;
const MOVE_SPEED = 1.0;
const BOOST_MULTIPLIER = 4.0;
const START_L = 6.0; // start where the throat is ~8.5deg across

// --- image ------------------------------------------------------------------------
const RENDER_SCALE = 0.65;
const EXPOSURE = 1.15;
const BLOOM = 0.62;
const BLOOM_COMPOSITE_GAIN = 0.35;
const BLOOM_THRESHOLD = 0.85;
const BLOOM_KNEE = 0.55;
const BLOOM_LEVELS = 5;
const GRAIN = 0.03;
const VIGNETTE = 0.34;
const ACCUMULATION_LIMIT = 512;

/* r(l) on the CPU, for observer stepping and readouts ------------------------------ */
export function wormholeRadius(l) {
  const al = Math.abs(l);
  if (al <= THROAT_A) return RHO;
  const x = (2 * (al - THROAT_A)) / (Math.PI * M_LENS);
  return RHO + M_LENS * (x * Math.atan(x) - 0.5 * Math.log(1 + x * x));
}

/* ================================ shaders ======================================== */

const VERTEX_SHADER = /* glsl */ `
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }
`;

const TRACE_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;

uniform vec2  uRes;
uniform vec2  uJitter;
uniform float uTanHalfFov;
uniform mat3  uCamRot;            // camera-local basis expressed in (e_l, A, B)
uniform vec3  uBasU, uBasA, uBasB; // sphere point + tangent frame, cartesian; A x B = U
uniform float uCamL;

uniform float uRho, uThroatA, uMlens;
uniform float uStepK, uREsc;
uniform int   uMaxSteps;
uniform int   uDebugMode;

${CELESTIAL_SPHERES_GLSL}

/* ------------------------------ wormhole shape ---------------------------------- */
float rOfL(float l){
  float al = abs(l);
  if (al <= uThroatA) return uRho;
  float x = 2.0*(al - uThroatA)/(PI*uMlens);
  return uRho + uMlens*(x*atan(x) - 0.5*log(1.0 + x*x));
}
float drOfL(float l){
  float al = abs(l);
  if (al <= uThroatA) return 0.0;
  float x = 2.0*(al - uThroatA)/(PI*uMlens);
  return sign(l)*(2.0/PI)*atan(x);
}

/* y = (l, psi, p_l);  b = r^2 dpsi/dt is conserved -------------------------------- */
vec3 geoDeriv(vec3 y, float b){
  float r  = max(rOfL(y.x), 1e-5);
  float ir = 1.0/r;
  return vec3( y.z,
               b*ir*ir,
               b*b*drOfL(y.x)*ir*ir*ir );
}

/* ================================== main ========================================= */
void main(){
  vec2 p = (gl_FragCoord.xy + uJitter - 0.5*uRes)/uRes.y;
  vec3 dLocal = normalize(vec3(p.x*2.0*uTanHalfFov, p.y*2.0*uTanHalfFov, -1.0));
  vec3 n = uCamRot*dLocal;                 // components along (e_l, A, B)

  float m    = length(n.yz);               // tangential magnitude of the unit ray
  vec3  tHat = (m > 1e-9) ? normalize(n.y*uBasA + n.z*uBasB) : uBasA;
  float r0   = rOfL(uCamL);
  float b    = r0*m;                       // conserved angular momentum

  vec3 y = vec3(uCamL, 0.0, n.x);          // (l, psi, p_l)

  bool  capped = true;
  float taken  = 0.0;
  for (int i = 0; i < 1024; i++){
    if (i >= uMaxSteps) break;
    float r = rOfL(y.x);

    // escaped into an asymptotically flat region and still receding -> done
    if (r > uREsc && drOfL(y.x)*y.z > 0.0) { capped = false; break; }

    // adaptive step: curvature scale is M near the throat, ~r far away; inside the
    // cylindrical throat r is constant so the solution is linear and exact for any h
    float al = abs(y.x);
    float h;
    if (al <= uThroatA){
      h = min((uThroatA - al)/max(abs(y.z), 1e-4) + uStepK*uMlens, 40.0*(uThroatA + uRho));
    } else {
      h = uStepK*min(r, uMlens + 0.9*(al - uThroatA));
    }
    h = max(h, 1e-5);

    vec3 k1 = geoDeriv(y,              b);
    vec3 k2 = geoDeriv(y + 0.5*h*k1,   b);
    vec3 k3 = geoDeriv(y + 0.5*h*k2,   b);
    vec3 k4 = geoDeriv(y +     h*k3,   b);
    y += (h/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4);
    taken += 1.0;

    if (abs(y.x) > 1.0e7) { capped = false; break; }
  }

  // asymptotic direction: radial component dr/dt, tangential component b/r, in the
  // frame carried around by the swept angle psi
  float rf = max(rOfL(y.x), 1e-5);
  float cp = cos(y.y), sp = sin(y.y);
  vec3  uf =  uBasU*cp + tHat*sp;
  vec3  tf = -uBasU*sp + tHat*cp;
  vec3  D  = drOfL(y.x)*y.z*uf + (b/rf)*tf;
  D = (dot(D, D) > 1e-12) ? normalize(D) : uf;

  // ray-bundle footprint -> physically motivated filtering of the celestial sphere
  float foot = clamp(0.5*(length(dFdx(D)) + length(dFdy(D))), 0.0, 0.06);

  // A ray that never escaped is one winding the photon sphere at |l| ~ 0: its exit
  // direction is whatever the integrator happened to be pointing at, which speckles.
  // Those rays sample effectively the whole sphere, so hand them the maximum
  // footprint and let the filtering return the sky's mean radiance instead.
  if (capped) foot = 0.06;

  vec3 col;
  if (uDebugMode == 1){
    col = D*0.5 + 0.5;                                     // exit direction
  } else if (uDebugMode == 2){
    col = (y.x >= 0.0) ? vec3(0.10, 0.34, 0.90)            // which universe was hit
                       : vec3(0.95, 0.45, 0.12);
    col *= capped ? 0.12 : 1.0;
  } else if (uDebugMode == 3){
    col = vec3(clamp(taken/max(float(uMaxSteps), 1.0), 0.0, 1.0));   // RK4 step count
  } else if (uDebugMode == 4){
    float f = foot/0.06;                                   // ray-bundle footprint
    col = vec3(f, f*f, 1.0 - f);
  } else if (uDebugMode == 5){
    col = capped ? vec3(1.0, 0.12, 0.04) : vec3(0.03);     // iteration-capped rays
  } else {
    col = (y.x >= 0.0) ? skyNear(D, foot) : skyFar(D, foot);
  }
  gl_FragColor = vec4(col, 1.0);
}
`;

const ACCUM_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tCur, tPrev;
uniform float uWeight;
void main(){
  vec3 c = texture2D(tCur, vUv).rgb;
  if (uWeight >= 0.999){ gl_FragColor = vec4(c, 1.0); return; }  // never touch stale/NaN history
  vec3 p = texture2D(tPrev, vUv).rgb;
  gl_FragColor = vec4(mix(p, c, uWeight), 1.0);
}
`;

/* Every level of the bloom pyramid decimates by two, and the sun — even with its
   display-space limb — is only a texel or two wide at the levels that carry the
   halo. A 2x2 box (a single bilinear tap) or a 4-tap corner box re-partitions a
   source that small between output texels as it crosses their grid: total energy
   is conserved, but the shape the coarse levels hand back up morphs with
   sub-texel phase, and the reconstructed halo breathes while the camera moves.
   The 13-tap kernel below — five overlapping 2x2 boxes, half the weight on the
   centre one, DC gain exactly 1 — overlaps adjacent output texels enough that a
   compact source hands off smoothly, which is precisely the property a box
   lacks.                                                                        */
const DOWN13_GLSL = /* glsl */ `
vec3 down13(sampler2D t, vec2 uv, vec2 px){
  vec3 a = texture2D(t, uv + px*vec2(-2.0, 2.0)).rgb;
  vec3 b = texture2D(t, uv + px*vec2( 0.0, 2.0)).rgb;
  vec3 c = texture2D(t, uv + px*vec2( 2.0, 2.0)).rgb;
  vec3 d = texture2D(t, uv + px*vec2(-2.0, 0.0)).rgb;
  vec3 e = texture2D(t, uv).rgb;
  vec3 f = texture2D(t, uv + px*vec2( 2.0, 0.0)).rgb;
  vec3 g = texture2D(t, uv + px*vec2(-2.0,-2.0)).rgb;
  vec3 h = texture2D(t, uv + px*vec2( 0.0,-2.0)).rgb;
  vec3 i = texture2D(t, uv + px*vec2( 2.0,-2.0)).rgb;
  vec3 j = texture2D(t, uv + px*vec2(-1.0, 1.0)).rgb;
  vec3 k = texture2D(t, uv + px*vec2( 1.0, 1.0)).rgb;
  vec3 l = texture2D(t, uv + px*vec2(-1.0,-1.0)).rgb;
  vec3 m = texture2D(t, uv + px*vec2( 1.0,-1.0)).rgb;
  return (j + k + l + m)*0.125
       + (4.0*e + 2.0*(b + d + f + h) + (a + c + g + i))*0.03125;
}
`;

const PREFILTER_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform vec2 uTexel;
uniform float uThresh, uKnee;
${DOWN13_GLSL}
void main(){
  vec3 c = down13(tSrc, vUv, uTexel);
  float br = max(c.r, max(c.g, c.b));
  float soft = clamp(br - uThresh + uKnee, 0.0, 2.0*uKnee);
  soft = soft*soft/(4.0*uKnee + 1e-5);
  float k = max(soft, br - uThresh)/max(br, 1e-5);
  gl_FragColor = vec4(c*k, 1.0);
}
`;

const DOWN_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform vec2 uTexel;
${DOWN13_GLSL}
void main(){
  gl_FragColor = vec4(down13(tSrc, vUv, uTexel), 1.0);
}
`;

const UP_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
uniform vec2 uTexel;
void main(){
  vec2 t = uTexel;
  vec3 s = texture2D(tSrc, vUv + t*vec2(-1.0, -1.0)).rgb
         + texture2D(tSrc, vUv + t*vec2( 0.0, -1.0)).rgb*2.0
         + texture2D(tSrc, vUv + t*vec2( 1.0, -1.0)).rgb
         + texture2D(tSrc, vUv + t*vec2(-1.0,  0.0)).rgb*2.0
         + texture2D(tSrc, vUv).rgb*4.0
         + texture2D(tSrc, vUv + t*vec2( 1.0,  0.0)).rgb*2.0
         + texture2D(tSrc, vUv + t*vec2(-1.0,  1.0)).rgb
         + texture2D(tSrc, vUv + t*vec2( 0.0,  1.0)).rgb*2.0
         + texture2D(tSrc, vUv + t*vec2( 1.0,  1.0)).rgb;
  gl_FragColor = vec4(s*(1.0/16.0), 1.0);
}
`;

/* Diagnostics are presented through this, not straight to the drawing buffer:
   the trace pass builds its ray directions from uRes, so it must keep rendering
   into the reduced-resolution target or every diagnostic view would be framed
   differently from the image it is meant to explain. It also keeps diagnostics
   out of the tone-mapped composite. */
const COPY_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tSrc;
void main(){ gl_FragColor = vec4(texture2D(tSrc, vUv).rgb, 1.0); }
`;

const COMPOSITE_FRAGMENT_SHADER = /* glsl */ `
precision highp float;
varying vec2 vUv;
uniform sampler2D tScene, tBloom;
uniform float uExposure, uBloom, uGrain, uVignette, uFrame;

vec3 aces(vec3 x){
  x *= 0.6;
  return clamp((x*(2.51*x + 0.03))/(x*(2.43*x + 0.59) + 0.14), 0.0, 1.0);
}
vec3 toSRGB(vec3 c){
  c = max(c, 0.0);
  return mix(12.92*c, 1.055*pow(c, vec3(1.0/2.4)) - 0.055, step(vec3(0.0031308), c));
}
float h21(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)))*43758.5453); }

void main(){
  vec3 c = texture2D(tScene, vUv).rgb + uBloom*texture2D(tBloom, vUv).rgb;
  c *= uExposure;
  c = aces(c);
  vec2 q = vUv - 0.5;
  c *= 1.0 - uVignette*dot(q, q)*1.9;
  c = toSRGB(c);
  c += (h21(vUv*vec2(1024.0, 768.0) + uFrame*0.137) - 0.5)*uGrain;
  gl_FragColor = vec4(c, 1.0);
}
`;

/* ================================ effect ========================================= */

const DEBUG_MODES = new Map([
  ["final", 0],
  ["exit-direction", 1],
  ["universe-side", 2],
  ["step-count", 3],
  ["ray-footprint", 4],
  ["iteration-capped", 5],
]);

/* Halton bases 2 and 3 supply the still-frame sample lattice. */
function halton2(index) {
  let f = 1;
  let r = 0;
  let i = index;
  while (i > 0) {
    f /= 2;
    r += f * (i % 2);
    i = Math.floor(i / 2);
  }
  return r;
}

function halton3(index) {
  let f = 1;
  let r = 0;
  let i = index;
  while (i > 0) {
    f /= 3;
    r += f * (i % 3);
    i = Math.floor(i / 3);
  }
  return r;
}

export function createTraversableWormholeTransitEffect() {
  const quadScene = new THREE.Scene();
  const quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), null);
  quad.frustumCulled = false;
  quadScene.add(quad);

  /* NOTE: do not set glslVersion: THREE.GLSL3 here. A non-raw ShaderMaterial is
     compiled as "#version 300 es" regardless (WebGLProgram always rewrites it), so
     dynamic loop bounds and dFdx/dFdy are available either way — but three only
     injects "out vec4 pc_fragColor" + the gl_FragColor alias when glslVersion is
     NOT GLSL3. Asking for GLSL3 opts out of that shim and the shaders fail to
     compile with "gl_FragColor : undeclared identifier". */
  const makeMaterial = (fragmentShader, uniforms, blending) =>
    new THREE.ShaderMaterial({
      vertexShader: VERTEX_SHADER,
      fragmentShader,
      uniforms,
      depthTest: false,
      depthWrite: false,
      blending: blending || THREE.NoBlending,
      transparent: Boolean(blending),
    });

  const traceUniforms = {
    uRes: { value: new THREE.Vector2(1, 1) },
    uJitter: { value: new THREE.Vector2() },
    uTanHalfFov: { value: Math.tan((FOV_DEGREES * Math.PI) / 360) },
    uCamRot: { value: new THREE.Matrix3() },
    uBasU: { value: new THREE.Vector3(0, 0, 1) },
    uBasA: { value: new THREE.Vector3(1, 0, 0) },
    uBasB: { value: new THREE.Vector3(0, 1, 0) },
    uCamL: { value: START_L },
    uRho: { value: RHO },
    uThroatA: { value: THROAT_A },
    uMlens: { value: M_LENS },
    uStepK: { value: STEP_K },
    uREsc: { value: ESCAPE_RADIUS },
    uMaxSteps: { value: MAX_STEPS },
    uDebugMode: { value: 0 },
    ...createCelestialSphereUniforms(),
  };
  const accumUniforms = { tCur: { value: null }, tPrev: { value: null }, uWeight: { value: 1 } };
  const prefilterUniforms = {
    tSrc: { value: null },
    uTexel: { value: new THREE.Vector2() },
    uThresh: { value: BLOOM_THRESHOLD },
    uKnee: { value: BLOOM_KNEE },
  };
  const downUniforms = { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() } };
  const upUniforms = { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() } };
  const copyUniforms = { tSrc: { value: null } };
  const compositeUniforms = {
    tScene: { value: null },
    tBloom: { value: null },
    uExposure: { value: EXPOSURE },
    uBloom: { value: BLOOM },
    uGrain: { value: GRAIN },
    uVignette: { value: VIGNETTE },
    uFrame: { value: 0 },
  };

  const traceMaterial = makeMaterial(TRACE_FRAGMENT_SHADER, traceUniforms);
  const accumMaterial = makeMaterial(ACCUM_FRAGMENT_SHADER, accumUniforms);
  const prefilterMaterial = makeMaterial(PREFILTER_FRAGMENT_SHADER, prefilterUniforms);
  const downMaterial = makeMaterial(DOWN_FRAGMENT_SHADER, downUniforms);
  const upMaterial = makeMaterial(UP_FRAGMENT_SHADER, upUniforms, THREE.AdditiveBlending);
  const copyMaterial = makeMaterial(COPY_FRAGMENT_SHADER, copyUniforms);
  const compositeMaterial = makeMaterial(COMPOSITE_FRAGMENT_SHADER, compositeUniforms);

  const targetOptions = {
    type: THREE.HalfFloatType,
    format: THREE.RGBAFormat,
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    depthBuffer: false,
    stencilBuffer: false,
    wrapS: THREE.ClampToEdgeWrapping,
    wrapT: THREE.ClampToEdgeWrapping,
  };
  const makeTarget = (width, height) =>
    new THREE.WebGLRenderTarget(
      Math.max(1, width | 0),
      Math.max(1, height | 0),
      targetOptions,
    );

  let sceneTarget = makeTarget(2, 2);
  let accumFront = makeTarget(2, 2);
  let accumBack = makeTarget(2, 2);
  let bloomTargets = [];
  let renderWidth = 2;
  let renderHeight = 2;
  let accumCount = 0;
  let frameNumber = 0;
  let debugMode = "final";

  /* The observer is a point on the sphere of radius r(l) plus a tangent frame
     carried with it, not a Cartesian camera: there is no global Cartesian chart
     that survives the throat. */
  const observer = {
    l: START_L,
    U: new THREE.Vector3(0, 0, 1),
    A: new THREE.Vector3(1, 0, 0),
    B: new THREE.Vector3(0, 1, 0), // A x B = U
    yaw: 0,
    pitch: 0,
    fov: FOV_DEGREES,
  };
  let targetFov = FOV_DEGREES;

  const camRot = new THREE.Matrix3();
  const rotationAxis = new THREE.Vector3();
  const rotation = new THREE.Quaternion();
  const tangent = new THREE.Vector3();

  const resetAccumulation = () => {
    accumCount = 0;
  };

  /* columns of uCamRot: camera x, y, z axes written in (e_l, A, B) components */
  function updateCamRot() {
    const cy = Math.cos(observer.yaw);
    const sy = Math.sin(observer.yaw);
    const cp = Math.cos(observer.pitch);
    const sp = Math.sin(observer.pitch);
    camRot.set(
      -sy, sp * cy, cp * cy, //  e_l component of (x, y, z)
      cy, sp * sy, cp * sy, //   A   component
      0.0, cp, -sp, //           B   component
    );
  }

  /* parallel-transport the sphere frame along a great circle */
  function rotateFrame(tHat, angle) {
    rotationAxis.crossVectors(observer.U, tHat);
    if (rotationAxis.lengthSq() < 1e-18) return;
    rotationAxis.normalize();
    rotation.setFromAxisAngle(rotationAxis, angle);
    observer.U.applyQuaternion(rotation);
    observer.A.applyQuaternion(rotation);
    observer.B.applyQuaternion(rotation);
    observer.U.normalize();
    observer.A.addScaledVector(observer.U, -observer.A.dot(observer.U)).normalize();
    observer.B.crossVectors(observer.U, observer.A); // keeps A x B = U
  }

  /* move by `distance` along a direction given in (e_l, A, B) components */
  function moveBy(cl, ca, cb, distance) {
    observer.l += cl * distance;
    const tm = Math.hypot(ca, cb);
    if (tm > 1e-9) {
      tangent
        .set(0, 0, 0)
        .addScaledVector(observer.A, ca / tm)
        .addScaledVector(observer.B, cb / tm);
      rotateFrame(tangent, (distance * tm) / Math.max(wormholeRadius(observer.l), 1e-4));
    }
  }

  function fly(deltaSeconds, forward, right, boost) {
    if (forward === 0 && right === 0) return;
    const r = wormholeRadius(observer.l);
    let v = MOVE_SPEED * deltaSeconds * Math.min(Math.max(0.1, r * 0.35), 14.0);
    if (boost) v *= BOOST_MULTIPLIER;
    updateCamRot();
    const m = camRot.elements; // column-major
    if (forward !== 0) moveBy(-m[6], -m[7], -m[8], forward * v); // forward = -z axis
    if (right !== 0) moveBy(m[0], m[1], m[2], right * v); //        right   = +x axis
    resetAccumulation();
  }

  function runPass(renderer, material, target) {
    quad.material = material;
    renderer.setRenderTarget(target ?? null);
    renderer.render(quadScene, quadCamera);
  }

  function allocate(width, height) {
    for (const target of [sceneTarget, accumFront, accumBack]) target?.dispose();
    for (const target of bloomTargets) target.dispose();
    bloomTargets = [];
    renderWidth = Math.max(2, Math.round(width * RENDER_SCALE));
    renderHeight = Math.max(2, Math.round(height * RENDER_SCALE));
    sceneTarget = makeTarget(renderWidth, renderHeight);
    accumFront = makeTarget(renderWidth, renderHeight);
    accumBack = makeTarget(renderWidth, renderHeight);
    let w = renderWidth >> 1;
    let h = renderHeight >> 1;
    for (let level = 0; level < BLOOM_LEVELS && w > 2 && h > 2; level += 1) {
      bloomTargets.push(makeTarget(w, h));
      w >>= 1;
      h >>= 1;
    }
    traceUniforms.uRes.value.set(renderWidth, renderHeight);
    compositeUniforms.uBloom.value = bloomTargets.length ? BLOOM * BLOOM_COMPOSITE_GAIN : 0;
    resetAccumulation();
  }

  return {
    get debugMode() {
      return debugMode;
    },
    get accumulatedSamples() {
      return accumCount;
    },
    get radialCoordinate() {
      return observer.l;
    },
    get sphereRadius() {
      return wormholeRadius(observer.l);
    },
    get universe() {
      return observer.l >= 0 ? "near" : "far";
    },
    get fieldOfView() {
      return observer.fov;
    },

    setSize(width, height) {
      allocate(width, height);
    },

    setDebugMode(mode) {
      debugMode = DEBUG_MODES.has(mode) ? mode : "final";
      traceUniforms.uDebugMode.value = DEBUG_MODES.get(debugMode) ?? 0;
      resetAccumulation();
    },

    /* pointer delta in CSS pixels */
    look(deltaX, deltaY) {
      const k = LOOK_SENSITIVITY * (observer.fov / FOV_DEGREES);
      observer.yaw -= deltaX * k;
      observer.pitch -= deltaY * k;
      observer.pitch = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, observer.pitch));
      resetAccumulation();
    },

    /* one wheel notch: +1 widens the field of view, -1 narrows it */
    zoom(direction) {
      targetFov = Math.max(
        FOV_MIN,
        Math.min(FOV_MAX, targetFov * (1 + Math.sign(direction) * FOV_ZOOM_STEP)),
      );
      resetAccumulation();
    },

    update(deltaSeconds, { forward = 0, right = 0, boost = false } = {}) {
      fly(deltaSeconds, forward, right, boost);
      observer.fov += (targetFov - observer.fov) * Math.min(1, deltaSeconds * FOV_SMOOTHING);
      if (Math.abs(observer.fov - targetFov) > 1e-3) resetAccumulation();
    },

    render(renderer) {
      const previousAutoClear = renderer.autoClear;
      renderer.autoClear = false; // the bloom upsample is additive into its target

      // the metric is fixed; only the observer changes
      updateCamRot();
      traceUniforms.uCamL.value = observer.l;
      traceUniforms.uTanHalfFov.value = Math.tan((observer.fov * Math.PI) / 360);
      traceUniforms.uCamRot.value.copy(camRot);
      traceUniforms.uBasU.value.copy(observer.U);
      traceUniforms.uBasA.value.copy(observer.A);
      traceUniforms.uBasB.value.copy(observer.B);

      if (debugMode !== "final") {
        traceUniforms.uJitter.value.set(0, 0);
        runPass(renderer, traceMaterial, sceneTarget);
        copyUniforms.tSrc.value = sceneTarget.texture;
        runPass(renderer, copyMaterial, null);
        renderer.autoClear = previousAutoClear;
        return;
      }

      frameNumber += 1;

      // Frame 0 after a reset IS the image while the observer moves, so sample it at
      // the pixel centre — the mean of the converged Halton set. Starting the
      // sequence at Halton #1 = (0, -1/6) instead leaves the whole frame sitting
      // 1/6 px below the converged still for as long as the observer moves (a snap
      // at every start and stop), and when a drag hesitates for a frame the restart
      // lands on index 2 or 3 at blend weight 1/2 or 1/3 — a sub-pixel hop the sun
      // is bright and small enough to show. In motion the sampling phase must be
      // stationary, not well-distributed.
      const still = accumCount < ACCUMULATION_LIMIT;
      const jx = accumCount === 0 ? 0 : still ? halton2(accumCount + 1) - 0.5 : Math.random() - 0.5;
      const jy = accumCount === 0 ? 0 : still ? halton3(accumCount + 1) - 0.5 : Math.random() - 0.5;
      traceUniforms.uJitter.value.set(jx, jy);

      runPass(renderer, traceMaterial, sceneTarget);

      // temporal accumulation (converges stills; harmless while moving)
      accumUniforms.tCur.value = sceneTarget.texture;
      accumUniforms.tPrev.value = accumFront.texture;
      accumUniforms.uWeight.value = accumCount > 0 ? 1 / (accumCount + 1) : 1;
      runPass(renderer, accumMaterial, accumBack);
      const swap = accumFront;
      accumFront = accumBack;
      accumBack = swap;
      accumCount = Math.min(accumCount + 1, ACCUMULATION_LIMIT);

      if (bloomTargets.length) {
        prefilterUniforms.tSrc.value = accumFront.texture;
        prefilterUniforms.uTexel.value.set(1 / renderWidth, 1 / renderHeight);
        runPass(renderer, prefilterMaterial, bloomTargets[0]);
        for (let level = 1; level < bloomTargets.length; level += 1) {
          const source = bloomTargets[level - 1];
          downUniforms.tSrc.value = source.texture;
          downUniforms.uTexel.value.set(1 / source.width, 1 / source.height);
          runPass(renderer, downMaterial, bloomTargets[level]);
        }
        for (let level = bloomTargets.length - 2; level >= 0; level -= 1) {
          const source = bloomTargets[level + 1];
          upUniforms.tSrc.value = source.texture;
          upUniforms.uTexel.value.set(1 / source.width, 1 / source.height);
          runPass(renderer, upMaterial, bloomTargets[level]);
        }
      }

      compositeUniforms.tScene.value = accumFront.texture;
      compositeUniforms.tBloom.value = bloomTargets.length
        ? bloomTargets[0].texture
        : accumFront.texture;
      compositeUniforms.uFrame.value = frameNumber % 1024;
      runPass(renderer, compositeMaterial, null);

      renderer.autoClear = previousAutoClear;
    },

    dispose() {
      quad.geometry.dispose();
      for (
        const material of [
          traceMaterial,
          accumMaterial,
          prefilterMaterial,
          downMaterial,
          upMaterial,
          copyMaterial,
          compositeMaterial,
        ]
      ) {
        material.dispose();
      }
      for (const target of [sceneTarget, accumFront, accumBack]) target?.dispose();
      for (const target of bloomTargets) target.dispose();
      bloomTargets = [];
    },
  };
}
