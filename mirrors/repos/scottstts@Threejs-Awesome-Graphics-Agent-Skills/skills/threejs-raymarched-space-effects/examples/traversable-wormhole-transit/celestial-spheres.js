import * as THREE from "three";

/* The two celestial spheres a lensed ray can land on, as one GLSL chunk.

   A geodesic renderer integrates a ray until it escapes, then asks "what is in
   that direction, in that universe?". Everything below answers that question
   and nothing below knows about the metric, so the chunk composes with any
   integrator that can hand it a direction and a ray-bundle footprint.

   The footprint is the contract that keeps the image stable: lensing conserves
   radiance but compresses solid angle enormously near a lensing rim, so every
   field here is filtered by the width of the pixel's ray bundle rather than
   point sampled, and each star field falls back to its own analytic mean
   radiance once one cell no longer covers a pixel. */
export const CELESTIAL_SPHERES_GLSL = /* glsl */ `
uniform vec3  uSunDir, uSaturnDir, uSaturnAxis;
uniform vec3  uPoleN, uCoreN, uPoleF, uCoreF;   // galactic frames, both universes

const float PI = 3.141592653589793;

/* ------------------------------ hash / noise ------------------------------------ */
float hash13(vec3 p){
  p = fract(p*0.1031);
  p += dot(p, p.zyx + 31.32);
  return fract((p.x + p.y)*p.z);
}
vec3 hash33(vec3 p){
  p = fract(p*vec3(0.1031, 0.1030, 0.0973));
  p += dot(p, p.yxz + 33.33);
  return fract((p.xxy + p.yxx)*p.zyx);
}
float vnoise(vec3 p){
  vec3 i = floor(p), f = fract(p);
  f = f*f*(3.0 - 2.0*f);
  float a = mix(mix(mix(hash13(i+vec3(0,0,0)), hash13(i+vec3(1,0,0)), f.x),
                    mix(hash13(i+vec3(0,1,0)), hash13(i+vec3(1,1,0)), f.x), f.y),
                mix(mix(hash13(i+vec3(0,0,1)), hash13(i+vec3(1,0,1)), f.x),
                    mix(hash13(i+vec3(0,1,1)), hash13(i+vec3(1,1,1)), f.x), f.y), f.z);
  return a;
}
float fbm(vec3 p, int oct){
  float amp = 0.5, sum = 0.0, tot = 0.0;
  for (int i = 0; i < 6; i++){
    if (i >= oct) break;
    sum += amp*vnoise(p); tot += amp;
    p *= 2.03; amp *= 0.5;
  }
  return sum/max(tot, 1e-4);
}
/* ridged multifractal: diffuse dust and HII shells are filamentary, not blobby */
float ridged(vec3 p, int oct){
  float amp = 0.5, sum = 0.0, tot = 0.0;
  for (int i = 0; i < 6; i++){
    if (i >= oct) break;
    float n = 1.0 - abs(2.0*vnoise(p) - 1.0);
    sum += amp*n*n; tot += amp;
    p = p*2.11 + 7.3; amp *= 0.55;
  }
  return sum/max(tot, 1e-4);
}
/* domain warp: turns isotropic noise into sheets, wisps and cavity walls */
vec3 warp3(vec3 p, float k, float s){
  return p + k*vec3(fbm(p + s, 2), fbm(p + s + 19.7, 2), fbm(p + s + 41.3, 2));
}

/* ------------------------------ star colour ------------------------------------- */
/* Planck locus (a piecewise fit to the blackbody chromaticity), normalised to
   unit luminance so the luminosity function alone sets brightness and temperature
   sets only hue. Faint stars are then mixed back toward white: below the cone
   threshold the eye reads a point source as colourless, which is why a real sky
   looks far less saturated than a naive tint ramp.                                 */
vec3 blackbody(float T){
  float t = clamp(T, 1700.0, 30000.0)*0.01;
  float r, g, b;
  if (t <= 66.0){ r = 255.0;                                      g = 99.4708025861*log(t) - 161.1195681661; }
  else          { r = 329.698727446*pow(t - 60.0, -0.1332047592); g = 288.1221695283*pow(t - 60.0, -0.0755148492); }
  if      (t >= 66.0) b = 255.0;
  else if (t <= 19.0) b = 0.0;
  else                b = 138.5177312231*log(t - 10.0) - 305.0447927307;
  vec3 c = clamp(vec3(r, g, b)/255.0, 0.0, 1.0);
  return c/max(dot(c, vec3(0.2126, 0.7152, 0.0722)), 1e-3);
}

/* ------------------------------- star fields ------------------------------------ */
/* Stars live on a cube-face lattice, one candidate per cell. Each is a Gaussian
   point-spread whose width follows the screen-space footprint of the (heavily
   lensed) sky direction and whose peak is scaled to hold total flux constant, so
   compression at a lensing rim brightens rather than aliases. Past one cell per
   pixel we fall back to the layer's analytic mean radiance — the correct "top mip"
   of the field, and also the physically right answer, since lensing conserves
   radiance. A second lobe at 3x the width carrying 4.5% of the flux is the PSF wing.

   Flux comes from the real number-count law N(<m) ~ 10^(0.6 m), which inverts to
   F ~ u^(-2/3) for uniform u: a heavy tail — a handful of dominant stars over a
   dense faint floor — instead of the flat field a naive random amplitude gives.
   Temperature is skewed hard toward late types and correlated with flux, because
   the main sequence is: the few stars that carry the frame come out blue-white, the
   floor comes out orange. Surface density follows the galactic disc and is evaluated
   at each star's own direction, not the pixel's, so nothing pops as the camera moves.

   No twinkle. There is no atmosphere out here.                                     */
const float U_MIN = 0.0016;      // clamp on the luminosity power law
const float S0    = 0.00030;     // intrinsic angular radius of a star

vec3 faceDirOf(float face, vec2 uv){
  vec3 v;
  if      (face < 1.5) v = vec3(1.0, uv.x, uv.y);
  else if (face < 3.5) v = vec3(uv.x, 1.0, uv.y);
  else                 v = vec3(uv.x, uv.y, 1.0);
  return normalize((mod(face, 2.0) < 0.5 ? 1.0 : -1.0)*v);
}

/* surface density of stars as a function of galactic latitude and longitude */
float discDens(vec3 dir, vec3 pole, vec3 core, float h){
  float sb  = dot(dir, pole);
  float lon = 0.42 + 0.58*smoothstep(-0.55, 0.95, dot(dir, core));
  return 0.34 + 1.72*exp(-0.5*sb*sb/(h*h))*lon;
}

vec3 starLayer(vec3 D, float foot, float cells, float baseDens, float lum, float seed,
               vec3 pole, vec3 core, float scaleH){
  vec3 ad = abs(D);
  float ma = max(ad.x, max(ad.y, ad.z));
  vec2 uv; float face;
  if      (ma == ad.x) { uv = D.yz/D.x; face = D.x > 0.0 ? 0.0 : 1.0; }
  else if (ma == ad.y) { uv = D.xz/D.y; face = D.y > 0.0 ? 2.0 : 3.0; }
  else                 { uv = D.xy/D.z; face = D.z > 0.0 ? 4.0 : 5.0; }

  float cellAng = 1.0/cells;
  float s  = clamp(max(S0, 0.62*foot), S0, 0.5*cellAng);
  float k  = (S0*S0)/(s*s);                     // flux-conserving peak
  float i2 = 1.0/(s*s);

  vec2 gi = floor(uv*cells);
  vec3 sum = vec3(0.0);
  for (int j = -1; j <= 1; j++){
    for (int i = -1; i <= 1; i++){
      vec2 cell = gi + vec2(float(i), float(j));
      vec3 h  = hash33(vec3(cell, face*17.0 + seed));
      vec3 sd = faceDirOf(face, (cell + h.xy)*cellAng);
      if (h.z > min(baseDens*discDens(sd, pole, core, scaleH), 1.0)) continue;

      vec3  dp = D - sd;
      float d2 = dot(dp, dp);
      vec3  h2 = hash33(vec3(cell + 91.7, face*17.0 + seed + 5.0));

      float u     = max(h2.x, U_MIN);
      float giant = step(0.972, h2.z);                        // ~3% evolved red giants
      float flux  = lum*pow(u, -0.6666667)*mix(1.0, 2.3, giant);   // N(<m) ~ 10^(0.6 m)
      float I     = flux*k*(exp(-0.5*d2*i2) + 0.005*exp(-d2*i2/18.0));
      if (I < 2.0e-4) continue;                               // below 8-bit, and below bloom

      // hot <-> luminous on the main sequence; the giants break that correlation,
      // which is exactly why the brightest stars in a real sky are not all blue
      float ts = clamp(0.62*pow(h2.y, 6.5) + 0.38*(1.0 - pow(u, 0.30)), 0.0, 1.0);
      ts = mix(ts, 0.015 + 0.05*h2.y, giant);
      vec3  cc = blackbody(mix(2700.0, 24000.0, ts));
      sum += I*mix(vec3(1.0), cc, clamp(0.35 + 0.55*log2(1.0 + flux*6.0), 0.35, 1.0));
    }
  }

  float meanFlux = lum*2.78*1.036;                            // E[u^-2/3] with u clamped, + giants
  float meanDens = min(baseDens*discDens(D, pole, core, scaleH), 1.0);
  vec3  meanRad  = vec3(0.98, 0.96, 1.00)*(meanDens*meanFlux*1.045*6.2831853*S0*S0*cells*cells);
  return mix(sum, meanRad, smoothstep(0.30, 1.25, foot*cells));
}

/* ------------------------------- galactic sky ----------------------------------- */
/* One galaxy model, instanced twice with different frames, palettes and seeds — the
   near universe and the far one. Ingredients, in the order light reaches the camera:

     - a dust column tau(D): thin, clumped, filamentary, hugging the disc. Extinction
       is exp(-tau * k) with k rising toward blue (A ~ 1/lambda), so the band is both
       dimmed and reddened and the dark nebulae are carved out of it rather than
       painted over it.
     - unresolved starlight — the milky band itself, plus a central bulge.
     - HII emission (H-alpha) and dust-scattered reflection nebulae, embedded in the
       disc, so on average half the dust column sits in front of them: sqrt(ext).
     - three resolved star layers sharing the same disc profile.                    */
vec3 galaxySky(vec3 D, float foot, float detail,
               vec3 pole, vec3 core, float seed, float scaleH,
               float dustAmp, float glowAmp, float nebAmp,
               vec3 cCool, vec3 cWarm, vec3 cEmis, vec3 cRefl,
               float sDens, float sLum){
  float sb    = dot(D, pole);
  float cd    = dot(D, core);
  float lon   = 0.42 + 0.58*smoothstep(-0.55, 0.95, cd);
  float disc  = exp(-0.5*sb*sb/(scaleH*scaleH));
  float hd    = scaleH*0.55;                                  // dust is thinner than stars
  float dpl   = exp(-0.5*sb*sb/(hd*hd));
  float bulge = pow(max(cd, 0.0), 3.2)*exp(-0.5*sb*sb/(0.11*0.11));

  /* --- dust column -> extinction, reddening, dark nebulae ---------------------- */
  vec3  qd   = warp3(D*2.6 + seed, 0.55, 3.1);
  float fil  = ridged(qd*1.7, 5);
  float bulk = smoothstep(0.28, 0.80, fbm(D*1.9 + seed*1.7, 4));
  float tau  = dustAmp*dpl*lon*(0.30*bulk + 1.25*smoothstep(0.34, 0.88, fil)*(0.35 + 0.65*bulk));
  vec3  ext  = exp(-tau*vec3(1.00, 1.24, 1.52));

  /* --- unresolved starlight: the milky band and the bulge ---------------------- */
  vec3  qm    = warp3(D*3.4 + seed*0.9, 0.34, 11.3);
  float clump = 0.50 + 0.85*fbm(qm*1.1, 5);
  float milky = disc*lon*clump + 1.9*bulge;
  vec3  c = glowAmp*milky*mix(cCool, cWarm,
              clamp(0.04 + 1.3*bulge + 0.85*(clump - 0.66), 0.0, 1.0))*ext;

  /* --- HII emission and reflection nebulae ------------------------------------- */
  /* the region mask gates everything: nebulae are a few discrete complexes strung
     along the arms, not an even wash over the whole plane. Within a complex the
     ionised gas runs from H-alpha red through to the O-III teal of the hottest
     cores, and the dust around it scatters the blue end of the local starlight. */
  float region = smoothstep(0.44, 0.80, fbm(D*1.3 + seed*2.1, 3));
  vec3  qn   = warp3(D*4.2 - seed*1.3, 0.70, 23.9);
  float hii  = region*smoothstep(0.50, 0.92, ridged(qn*1.25, 4));
  float knot = region*smoothstep(0.70, 0.98, ridged(qn*3.1 + 5.0, 3))*detail;
  float refl = smoothstep(0.48, 0.88, fbm(qn*0.8 + 31.0, 4))*(0.25 + 0.75*region);
  float oiii = smoothstep(0.40, 0.74, fbm(D*2.2 + seed*3.7, 3));
  vec3  cIon = mix(cEmis, vec3(0.20, 0.78, 0.66), oiii*0.5);
  float host = 0.22 + 0.78*disc*lon;
  c += nebAmp*host*(cIon*(hii + 1.9*knot) + cRefl*(1.10*refl + 0.25*hii))*sqrt(ext);

  /* --- resolved stars, dimmed by the dust that lies in front of them ------------ */
  c += starLayer(D, foot,  30.0, 0.46*sDens, 0.60*sLum, seed +  1.0, pole, core, scaleH)*mix(vec3(1.0), ext, 0.40);
  c += starLayer(D, foot, 104.0, 0.34*sDens, 0.18*sLum, seed + 11.0, pole, core, scaleH)*mix(vec3(1.0), ext, 0.75);
  c += starLayer(D, foot, 300.0, 0.22*sDens, 0.055*sLum, seed + 23.0, pole, core, scaleH)*ext;
  return c;
}

/* ------------------------------ ringed gas giant --------------------------------- */
/* Analytically ray-traced sphere + ring plane sitting on the celestial sphere, so it
   lenses through the wormhole exactly like the star field does.                     */
float ringDensity(float rad, float e){
  float d = 0.0;
  d += smoothstep(1.12, 1.20 + e, rad)*(1.0 - smoothstep(1.49, 1.53 + e, rad))*0.30;  // C
  d += smoothstep(1.52, 1.57 + e, rad)*(1.0 - smoothstep(1.91, 1.95 + e, rad))*0.95;  // B
  d += smoothstep(2.02, 2.06 + e, rad)*(1.0 - smoothstep(2.23, 2.27 + e, rad))*0.66;  // A
  d *= 0.86 + 0.14*sin(rad*173.0);                                                    // ringlets
  d *= mix(0.18, 1.0, smoothstep(0.0, 0.006 + e, abs(rad - 2.214)));                  // Encke
  return clamp(d, 0.0, 1.0);
}
/* returns PREMULTIPLIED colour in .rgb and coverage in .a */
vec4 saturnRender(vec3 D, float foot){
  float ang = 0.052;
  vec3  C   = uSaturnDir;
  float R   = sin(ang);
  float w   = max(foot, 2.0e-4);

  // --- planet -------------------------------------------------------------------
  float bq   = dot(D, C);
  float disc = bq*bq - (1.0 - R*R);
  float tS   = 1e9;
  float dAng = acos(clamp(bq, -1.0, 1.0));
  float aP   = (bq > 0.0) ? 1.0 - smoothstep(ang - w, ang + w, dAng) : 0.0;
  vec3  cP   = vec3(0.0);
  if (aP > 0.001){
    tS = bq - sqrt(max(disc, 0.0));
    vec3  N    = normalize(tS*D - C);
    float lat  = clamp(dot(N, uSaturnAxis), -1.0, 1.0);
    float la   = asin(lat);
    float turb = fbm(N*6.0 + vec3(0.0, la*3.0, 0.0), 4);
    float band = 0.5 + 0.5*sin(la*17.0 + turb*2.6 + sin(la*41.0)*0.5);
    vec3  base = mix(vec3(0.68, 0.55, 0.37), vec3(0.93, 0.85, 0.68), band);
    base = mix(base, vec3(0.56, 0.53, 0.47), smoothstep(0.55, 1.0, abs(lat)));
    float ndl  = max(dot(N, uSunDir), 0.0);
    float limb = pow(max(dot(N, -D), 0.0), 0.35);
    cP = base*(ndl*1.25*limb + 0.012);
  }

  // --- rings --------------------------------------------------------------------
  float aR = 0.0; vec3 cR = vec3(0.0); float tR = -1.0;
  float dn = dot(D, uSaturnAxis);
  if (abs(dn) > 1e-6){
    tR = dot(C, uSaturnAxis)/dn;
    if (tR > 0.0){
      vec3  q   = tR*D - C;
      float rad = length(q)/R;
      float e   = clamp(foot/max(ang, 1e-4), 0.0, 0.35);
      aR = ringDensity(rad, e);
      if (aR > 0.001){
        float proj = dot(q, uSunDir);
        float perp = length(q - proj*uSunDir);
        float shad = (proj < 0.0) ? mix(0.10, 1.0, smoothstep(R*0.92, R*1.08, perp)) : 1.0;
        cR = mix(vec3(0.70, 0.62, 0.48), vec3(0.97, 0.92, 0.82),
                 smoothstep(1.5, 2.1, rad))*shad*0.95;
      } else aR = 0.0;
    }
  }

  // --- depth-correct "over" composite, premultiplied -----------------------------
  vec3  front_c; float front_a; vec3 back_c; float back_a;
  if (tR > 0.0 && tR < tS){ front_c = cR; front_a = aR; back_c = cP; back_a = aP; }
  else                    { front_c = cP; front_a = aP; back_c = cR; back_a = aR; }
  vec3  pre = front_c*front_a + back_c*back_a*(1.0 - front_a);
  float cov = front_a + back_a*(1.0 - front_a);
  return vec4(pre, clamp(cov, 0.0, 1.0));
}

/* ------------------------------ celestial spheres -------------------------------- */
vec3 skyNear(vec3 D, float foot){          // this universe — its galaxy, sun and gas giant
  float detail = 1.0 - smoothstep(0.0035, 0.028, foot);
  vec3 c = galaxySky(D, foot, detail, uPoleN, uCoreN, 0.0, 0.185,
                     1.35, 0.160, 0.048,
                     vec3(0.50, 0.62, 0.94), vec3(1.00, 0.90, 0.72),   // cool arms / warm bulge
                     vec3(0.95, 0.26, 0.22), vec3(0.30, 0.48, 0.95),   // H-alpha / reflection
                     1.0, 1.0);

  /* The sun is the brightest thing in the frame by two orders of magnitude and it
     dominates the bloom, so its rendered image has to be invariant under sub-pixel
     motion. Flux invariance alone (footprint-wide feather, integral-normalised
     peak) is not enough, because the display clips it: ACES sends everything above
     ~2.5 to pure white, so of a smoothstep feather under a 420x peak only the
     bottom ~0.7% is visible on screen. However wide the feather is in linear
     light, the tone-mapped limb of a plain disc lives in ~0.1 px — a hard edge.
     And in motion the accumulator restarts every frame, so the frame IS one
     sample per pixel: a hard sub-pixel edge pops pixel-by-pixel as it crosses
     the grid, the bloom prefilter inherits the popping, and disc plus halo
     jitter — then freeze the instant the camera stops and 512-sample
     accumulation takes over.

     So, same recipe as the resolved stars above: a point-spread wide enough for
     the display. Flat core of radius R, Gaussian limb with sigma tied to the
     ray-bundle footprint. Under a 420x peak the visible ramp of
     exp(-q^2/2 sigma^2) runs from the ACES knee down to the sRGB toe in
     ~1.1-1.6 sigma, so sigma = 1.2 footprints keeps the on-screen limb >= 1.3 px
     at any magnification. Separation stays a chord, |D - sunDir| — near cos ~ 1
     a dot() comparison wastes all its precision against the ~1e-6 direction
     noise surviving the RK4. And the peak is still normalised by the profile's
     own integral, integral(P) 2 pi d dd = pi*(R^2 + sqrt(2 pi) R sigma
     + 2 sigma^2), so total flux is exactly 420 pi R^2 in every regime: lensing
     can squeeze the disc below a pixel and it dims into a wider splat instead
     of point-sampling in and out of existence.                                 */
  const float sunR = 0.0050;
  float sunD = length(D - uSunDir);
  float sunS = 1.2*max(foot, 1.0e-5);
  float sunQ = max(sunD - sunR, 0.0);
  c += vec3(1.00, 0.97, 0.92)*420.0
       *((sunR*sunR)/(sunR*sunR + 2.5066283*sunR*sunS + 2.0*sunS*sunS))
       *exp(-0.5*sunQ*sunQ/(sunS*sunS));
  c += vec3(1.00, 0.95, 0.88)*0.55*exp(-sunD*sunD/(2.0*0.0333*0.0333));

  vec4 s = saturnRender(D, foot);
  return c*(1.0 - s.a) + s.rgb;            // s.rgb is premultiplied
}

vec3 skyFar(vec3 D, float foot){           // the other side — older, dustier, redder
  float detail = 1.0 - smoothstep(0.0035, 0.028, foot);
  return galaxySky(D, foot, detail, uPoleF, uCoreF, 137.0, 0.235,
                   1.30, 0.300, 0.185,
                   vec3(0.46, 0.56, 0.90), vec3(1.00, 0.79, 0.54),
                   vec3(0.98, 0.32, 0.19), vec3(0.44, 0.40, 0.96),
                   1.30, 1.45);
}
`;

/* galactic frame: north pole, then the core direction orthogonalised against it */
function galacticFrame(px, py, pz, cx, cy, cz) {
  const pole = new THREE.Vector3(px, py, pz).normalize();
  const core = new THREE.Vector3(cx, cy, cz);
  core.addScaledVector(pole, -core.dot(pole)).normalize();
  return { pole, core };
}

/* Uniforms for `CELESTIAL_SPHERES_GLSL`.

   The far frame is deliberate: a ray fired straight down the throat comes out
   along +Z, so putting that universe's core there means the throat shows its
   galactic centre rather than its anticentre. Without this the sphere reads as
   a black hole instead of a window. */
export function createCelestialSphereUniforms() {
  const near = galacticFrame(-0.32, 0.90, 0.29, 0.86, 0.24, -0.45);
  const far = galacticFrame(0.68, 0.73, 0.06, -0.10, 0.06, 0.99);
  return {
    uSunDir: { value: new THREE.Vector3(-0.75, 0.28, 0.60).normalize() },
    uSaturnDir: { value: new THREE.Vector3(0.36, 0.14, -0.92).normalize() },
    uSaturnAxis: { value: new THREE.Vector3(0.08, 0.83, 0.55).normalize() },
    uPoleN: { value: near.pole },
    uCoreN: { value: near.core },
    uPoleF: { value: far.pole },
    uCoreF: { value: far.core },
  };
}
