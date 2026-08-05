import { Color, LinearSRGBColorSpace } from "three/webgpu";
import {
  Fn,
  cameraProjectionMatrix,
  cameraViewMatrix,
  cos,
  equirectUV,
  exp,
  float,
  normalize,
  select,
  sin,
  sqrt,
  texture,
  vec2,
  vec3,
  vec4,
} from "three/tsl";

// Optical primitives for dielectric transmission.
//
// These are the parts of a glass material that are pure physics and carry no
// scene state: exact unpolarised Fresnel reflectance, a Cauchy dispersion
// model built from the two numbers glass catalogues actually publish, CIE 1931
// spectral reconstruction, Beer-Lambert absorption coefficients, and the two
// lookups an image-space transmission path needs — a rotatable equirectangular
// radiance probe and a world-point-to-buffer projection.

/**
 * Cauchy calibration constant 1/λ_F² − 1/λ_C² in nm⁻², taken from the F
 * (486.13 nm) and C (656.27 nm) Fraunhofer lines that define the Abbe number.
 */
export const CAUCHY_K = 1 / (486.13 * 486.13) - 1 / (656.27 * 656.27);

/** Helium d-line in nm — the wavelength a catalogue n_d is quoted at. */
export const LAMBDA_D = 589.29;

/**
 * Sampled band in nm. It is deliberately narrower than the 380–780 nm visible
 * range: the CIE curves are near zero at both ends, so spending samples there
 * buys no visible fire and only thins the band where dispersion is legible.
 */
export const LAMBDA_MIN = 415.0;
export const LAMBDA_MAX = 695.0;

/**
 * Cauchy n(λ) = A + B/λ² solved from a catalogue pair (n_d, V_d):
 *
 *   B = (n_d − 1) / (V_d · (1/λ_F² − 1/λ_C²))   [nm²]
 *   A = n_d − B/λ_d²
 *
 * Both coefficients are constant for a given glass, so they resolve on the
 * CPU; only the per-wavelength evaluation A + B/λ² belongs in the shader.
 * Driving dispersion from (n_d, V_d) rather than an ad-hoc per-channel IOR
 * offset is what makes the spread match a real material: V_d alone decides how
 * far apart the red and blue paths land.
 */
export function cauchyCoefficients(ior, abbe) {
  const b = (ior - 1) / (abbe * CAUCHY_K);
  return { a: ior - b / (LAMBDA_D * LAMBDA_D), b };
}

/**
 * Beer-Lambert extinction σ in 1/unit for a transmission tint carried over a
 * chosen depth: σ = −ln(t)/depth, where `t` is the tint's linear value, so a
 * path of `depth` units transmits exactly `tint`. Inverting the exponential
 * keeps the control perceptual — name the colour a thickness should show
 * rather than an extinction spectrum — and keeps thin and thick regions of one
 * body consistent, because both read the same σ over their own path length.
 *
 * Decode the sRGB literal exactly once, and decode it explicitly. A `Color`
 * built from an sRGB literal is already in the linear working space, so an
 * added `convertSRGBToLinear()` squares the transfer and inflates extinction by
 * roughly 2.3×. That mistake survives review easily: it only deepens the tint,
 * so tuning by eye absorbs it while the picker quietly stops meaning what it
 * says. Parsing as `LinearSRGBColorSpace` keeps the literal's raw components,
 * which makes the single decode below the only transfer applied and leaves σ
 * independent of the renderer's colour-management setting.
 */
export function absorptionCoefficients(tint, depth) {
  const linear = new Color()
    .setStyle(tint, LinearSRGBColorSpace)
    .convertSRGBToLinear();
  const unitDepth = Math.max(depth, 1e-3);
  return [
    -Math.log(Math.max(linear.r, 1e-4)) / unitDepth,
    -Math.log(Math.max(linear.g, 1e-4)) / unitDepth,
    -Math.log(Math.max(linear.b, 1e-4)) / unitDepth,
  ];
}

/**
 * Exact Fresnel reflectance for a dielectric interface n1 → n2 under
 * unpolarised light: F = ½(r_s² + r_p²). Returns 1 past the critical angle,
 * which is what makes total internal reflection fall out of the same
 * expression instead of needing a separate test.
 *
 * A Schlick approximation is not interchangeable here. The internal path
 * spends most of its interfaces near grazing incidence, exactly where Schlick
 * drifts, and it never reaches 1 at the critical angle, so TIR would leak.
 */
export const fresnelDielectric = Fn(([cosI, n1, n2]) => {
  const eta = n1.div(n2);
  const sinT2 = eta.mul(eta).mul(float(1.0).sub(cosI.mul(cosI)));
  const cosT = sqrt(float(1.0).sub(sinT2).max(1e-6));
  const rs = n1.mul(cosI).sub(n2.mul(cosT)).div(n1.mul(cosI).add(n2.mul(cosT)));
  const rp = n2.mul(cosI).sub(n1.mul(cosT)).div(n2.mul(cosI).add(n1.mul(cosT)));
  return select(
    sinT2.greaterThanEqual(1.0),
    float(1.0),
    rs.mul(rs).add(rp.mul(rp)).mul(0.5).clamp(0.0, 1.0),
  );
});

// One lobe of a piecewise-Gaussian colour matching fit: the two standard
// deviations make the lobe asymmetric about its peak.
const gaussianLobe = (x, mu, s1, s2) => {
  const t = x.sub(mu).div(select(x.lessThan(mu), float(s1), float(s2)));
  return exp(t.mul(t).mul(-0.5));
};

/**
 * CIE 1931 colour matching through multi-lobe piecewise-Gaussian fits,
 * followed by XYZ → linear sRGB. Returns the linear-sRGB weight of one
 * wavelength sample.
 *
 * Accumulate both `weight · radiance` and `weight` and divide at the end. The
 * running normalisation is what guarantees a dispersion-free path reconstructs
 * the environment exactly rather than picking up a spectral cast, and it keeps
 * the result stable when the sample count changes. Individual weights are
 * legitimately negative outside the sRGB gamut, so clamp the final sum, never
 * the per-sample weights.
 */
export const spectralWeight = Fn(([lam]) => {
  const X = gaussianLobe(lam, float(599.8), 37.9, 31.0).mul(1.056)
    .add(gaussianLobe(lam, float(442.0), 16.0, 26.7).mul(0.362))
    .sub(gaussianLobe(lam, float(501.1), 20.4, 26.2).mul(0.065));
  const Y = gaussianLobe(lam, float(568.8), 46.9, 40.5).mul(0.821)
    .add(gaussianLobe(lam, float(530.9), 16.3, 31.1).mul(0.286));
  const Z = gaussianLobe(lam, float(437.0), 11.8, 36.0).mul(1.217)
    .add(gaussianLobe(lam, float(459.0), 26.0, 13.8).mul(0.681));
  return vec3(
    X.mul(3.2404542).add(Y.mul(-1.5371385)).add(Z.mul(-0.4985314)),
    X.mul(-0.9692660).add(Y.mul(1.8760108)).add(Z.mul(0.0415560)),
    X.mul(0.0556434).add(Y.mul(-0.2040259)).add(Z.mul(1.0572252)),
  );
});

/**
 * Builds the environment radiance probe for a world-space direction.
 *
 * `rotation` spins the equirectangular map about Y in radians. `lod` is an
 * explicit mip level: 0 is the sharp map, higher levels give physically
 * plausible micro-roughness blur. The level must be explicit because every
 * lookup on the internal path happens inside a non-uniform loop, where implicit
 * derivatives are undefined.
 *
 * The texture must carry mipmaps, `RepeatWrapping` on S so the seam closes,
 * and `ClampToEdgeWrapping` on T so the poles do not wrap into each other.
 *
 * Give the visible background and the transmitted path the same probe. What
 * the viewer sees through the body has to be the radiance field they see
 * around it, or the body reads as a cutout of an unrelated scene.
 */
export function createEnvironmentSampler({ texture: environment, rotation }) {
  return Fn(([dir, lod]) => {
    const cs = cos(float(rotation));
    const sn = sin(float(rotation));
    const rotated = vec3(
      dir.x.mul(cs).sub(dir.z.mul(sn)),
      dir.y,
      dir.x.mul(sn).add(dir.z.mul(cs)),
    );
    return texture(environment, equirectUV(normalize(rotated)), lod).rgb;
  });
}

/**
 * World point → UV of a full-screen data buffer rendered with the current
 * camera. This is the addressing scheme that lets an interior ray query a
 * surface it cannot raytrace.
 *
 * V is inverted: the WebGPU backend rasterises render targets with Y flipped
 * relative to the classic GL convention. Verify this against a CPU raycast
 * mask of the buffer before trusting the path — a flipped V still produces a
 * plausible-looking image, just one where the interior samples the wrong
 * surface.
 */
export const projectToBufferUV = Fn(([p]) => {
  const clip = cameraProjectionMatrix.mul(cameraViewMatrix).mul(vec4(p, 1.0));
  const ndc = clip.xy.div(clip.w);
  return vec2(ndc.x.mul(0.5).add(0.5), ndc.y.mul(-0.5).add(0.5));
});
