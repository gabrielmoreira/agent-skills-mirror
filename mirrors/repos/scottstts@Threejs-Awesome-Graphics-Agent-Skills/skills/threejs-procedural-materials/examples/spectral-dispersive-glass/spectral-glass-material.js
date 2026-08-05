import * as THREE from "three/webgpu";
import {
  Break,
  Fn,
  If,
  Loop,
  cameraPosition,
  depth,
  dot,
  exp,
  float,
  mix,
  modelNormalMatrix,
  normalLocal,
  normalWorldGeometry,
  normalize,
  positionWorld,
  reflect,
  refract,
  select,
  texture,
  uniform,
  vec3,
  vec4,
} from "three/tsl";
import {
  LAMBDA_MAX,
  LAMBDA_MIN,
  absorptionCoefficients,
  cauchyCoefficients,
  createEnvironmentSampler,
  fresnelDielectric,
  projectToBufferUV,
  spectralWeight,
} from "./glass-optics.js";

// Spectral dispersive glass: a physically motivated transmission material for
// an arbitrary mesh, resolved in image space.
//
// Per fragment the material refracts the view ray into the body, finds the
// exit point by intersecting that interior ray against a back-face data buffer
// through repeated projection and refinement, then refracts out — or, past the
// critical angle, reflects internally and continues for several segments.
// Every interface uses exact unpolarised Fresnel, radiance is attenuated by
// Beer-Lambert over the true internal path length, and the whole path is
// traced once per wavelength with a Cauchy index of refraction before the
// samples are recombined through CIE 1931 into linear sRGB.
//
// Why image space rather than a BVH raytrace of the body: the exit search only
// needs a depth-like buffer, so it accepts meshes a geometric tracer cannot
// use — open sheets with no enclosed volume, several interpenetrating shells,
// inconsistent winding, and authored normals pointing either way. The cost is
// that the buffer only knows about surfaces the camera can see, which the
// fallback thickness and minimum wall below exist to cover.
//
// Host contract:
// - `environment` is an equirectangular HDR texture with mipmaps enabled,
//   `RepeatWrapping` on S and `ClampToEdgeWrapping` on T. Assign the same
//   texture behind the body through `backgroundNode` so transmission and
//   background agree.
// - The subject must already be placed and scaled: its world bounding box
//   fixes the fallback thickness and the maximum segment length.
// - `setSize` must track the drawing-buffer size in physical pixels, because
//   the interior ray addresses the buffer in that space.
// - `renderBackFaces` must run before the camera pass, every frame, with the
//   same camera. A stale buffer refracts the previous frame's silhouette.

/* ============================================================================
   Physical parameters
   ========================================================================== */

/** Refractive index n_d at the helium d-line: ordinary crown/soda-lime glass. */
const IOR = 1.5;

/** Abbe number V_d. Lower disperses harder; 32 reads as flint-like fire. */
const ABBE = 32;

/**
 * Wavelength samples per fragment across the band. Each one re-traces the
 * whole internal path, so this is the dominant cost. Below roughly 6 the fire
 * separates into discrete coloured copies of the environment instead of a
 * continuous spread.
 */
const SPECTRAL_SAMPLES = 8;

/** Internal path segments: TIR bounces plus the exit that ends the path. */
const PATH_SEGMENTS = 4;

/**
 * Exit-search refinements per segment. The first estimate reprojects the seed
 * thickness, and each further pass re-reads the buffer at the corrected point.
 * Three passes converge on gently curved bodies; they cannot recover a surface
 * the camera never saw.
 */
const EXIT_REFINEMENTS = 3;

/**
 * Assumed minimum wall thickness in world units. Open, zero-volume sheets
 * would otherwise transmit with no path length at all and lose their tint
 * entirely, so every surface is treated as at least this thick. Raise it to
 * make the tint permeate a whole body; lower it toward 0 for hollow
 * blown-glass thinness.
 */
const MIN_WALL = 0.08;

/**
 * Environment mip bias applied to every lookup on the path. 0 is polished
 * glass; higher levels read as surface micro-roughness, because a rougher
 * interface integrates a wider cone of incoming radiance.
 */
const FROST_LOD = 0;

/** Equirectangular probe rotation about Y, in radians. */
const ENVIRONMENT_ROTATION = 0;

/**
 * Transmission tint and the path length that shows it exactly: a half-unit
 * path through this glass transmits `#d0edda`. Together they become the
 * Beer-Lambert extinction spectrum — σ ≈ (0.922, 0.332, 0.710) 1/unit — so
 * thin and thick regions of one body stay consistent instead of being tinted
 * by a flat multiply.
 */
const TINT = "#d0edda";
const TINT_DEPTH = 0.5;

/**
 * Assumed thickness where the back-face buffer has no data, as a fraction of
 * the subject's bounding diagonal. This is the silhouette rim, where the exit
 * surface falls outside the visible buffer; a thin assumed wall there is far
 * less visible than a ray that escapes untinted.
 */
const FALLBACK_THICKNESS_RATIO = 0.015;

/**
 * Longest single interior segment, as a fraction of the bounding diagonal. It
 * bounds a refinement that lands on an unrelated distant surface, which would
 * otherwise stretch one segment across the whole scene.
 */
const MAX_SEGMENT_RATIO = 3.0;

/** Path throughput below which the remaining segments cannot change the image. */
const THROUGHPUT_CUTOFF = 0.004;

/** Diagnostic channels the material can output in place of the final image. */
export const GLASS_DEBUG_VIEWS = {
  final: 0,
  thickness: 1,
  exitNormal: 2,
  entryFresnel: 3,
};

/**
 * Pure geometric world normal, never flipped to face the camera by the
 * rasteriser. Both passes must agree on this vector: the data pass stores it
 * and the glass pass re-orients it along the ray it is currently following, so
 * authored normal direction and winding stop mattering.
 */
const geometricWorldNormal = normalize(modelNormalMatrix.mul(normalLocal));

export class SpectralDispersiveGlass {
  /**
   * @param {THREE.Object3D} subject placed, scaled mesh hierarchy to render as
   *   glass. Every mesh under it is re-materialised.
   * @param {{ environment: THREE.Texture }} options equirectangular HDR probe.
   */
  constructor(subject, { environment } = {}) {
    if (!environment) {
      throw new Error("SpectralDispersiveGlass requires an environment texture.");
    }

    subject.updateMatrixWorld(true);
    const bounds = new THREE.Box3().setFromObject(subject);
    const diagonal = bounds.getSize(new THREE.Vector3()).length();
    const fallbackThickness = FALLBACK_THICKNESS_RATIO * diagonal;
    const maxSegment = MAX_SEGMENT_RATIO * diagonal;

    const debugView = uniform(GLASS_DEBUG_VIEWS.final);
    const cauchy = cauchyCoefficients(IOR, ABBE);
    const sigma = vec3(...absorptionCoefficients(TINT, TINT_DEPTH));

    /* ---- back-face data buffer ------------------------------------------
       World normal in xyz, distance from the camera in w. Half float because
       w is a scene-scale distance and the normal needs sign; nearest because
       the interior ray asks for one specific surface, and filtering across a
       silhouette would blend two unrelated ones. */
    const renderTarget = new THREE.RenderTarget(1, 1, {
      type: THREE.HalfFloatType,
      format: THREE.RGBAFormat,
      minFilter: THREE.NearestFilter,
      magFilter: THREE.NearestFilter,
      generateMipmaps: false,
      depthBuffer: true,
    });
    renderTarget.texture.name = "glassBackFaceData";

    // Single-binding fetch at explicit LOD 0: sampling stays legal inside the
    // non-uniform loops that read it.
    const backFaceData = Fn(([uv]) => texture(renderTarget.texture, uv, 0));

    const sampleEnvironment = createEnvironmentSampler({
      texture: environment,
      rotation: ENVIRONMENT_ROTATION,
    });

    /* ---- pass 1 material -------------------------------------------------
       A body of several overlapping shells with inconsistent winding makes
       facing tests unreliable, so do not cull. Rasterise both sides and write
       inverted fragment depth: the default less-than test then keeps the
       farthest surface along each view ray — the exit of the union hull, which
       is the physically sensible interface for image-space refraction. */
    const backFaceMaterial = new THREE.MeshBasicNodeMaterial();
    backFaceMaterial.side = THREE.DoubleSide;
    backFaceMaterial.blending = THREE.NoBlending;
    backFaceMaterial.toneMapped = false;
    backFaceMaterial.depthNode = depth.oneMinus();
    backFaceMaterial.outputNode = vec4(
      geometricWorldNormal,
      positionWorld.sub(cameraPosition).length(),
    );

    /* ---- pass 2 material ---------------------------------------------- */
    const glassColor = Fn(() => {
      const P1 = positionWorld;
      const camP = cameraPosition;
      const V = normalize(camP.sub(P1));
      const Ng = geometricWorldNormal;
      // Re-orient toward the viewer rather than trusting the authored side.
      const N1 = Ng.mul(select(dot(Ng, V).greaterThanEqual(0.0), 1.0, -1.0))
        .toVar();
      const I = V.negate();
      const cosI = dot(V, N1).clamp(1e-4, 1.0);
      const distFront = P1.sub(camP).length();

      // View-ray thickness at this fragment: the seed for the exit search.
      const uv0 = projectToBufferUV(P1).clamp(0.0, 1.0);
      const b0 = backFaceData(uv0).toVar();
      const dvSeed = select(
        b0.w.greaterThan(0.0),
        b0.w.sub(distFront).max(MIN_WALL),
        float(fallbackThickness),
      );

      // External specular reflection. Its direction is wavelength independent,
      // so it is resolved once outside the spectral loop.
      const Favg = fresnelDielectric(cosI, float(1.0), float(IOR));
      const reflection = sampleEnvironment(reflect(I, N1), float(FROST_LOD))
        .mul(Favg);

      const Csum = vec3(0.0).toVar();
      const Wsum = vec3(0.0).toVar();

      Loop(SPECTRAL_SAMPLES, ({ i }) => {
        // Stratified band centre for this sample, then the Cauchy index and
        // the CIE weight that belong to it.
        const fi = float(i).add(0.5).div(SPECTRAL_SAMPLES);
        const lam = mix(float(LAMBDA_MIN), float(LAMBDA_MAX), fi).toVar();
        const w = spectralWeight(lam).toVar();
        const n = float(cauchy.a).add(float(cauchy.b).div(lam.mul(lam))).toVar();

        const F1 = fresnelDielectric(cosI, float(1.0), n);
        const T1 = refract(I, N1, float(1.0).div(n)); // entry refraction (Snell)

        const contrib = vec3(0.0).toVar();
        const thr = float(1.0).sub(F1).toVar(); // path throughput
        const dir = T1.toVar();
        const orig = P1.toVar();
        const sLen = float(0.0).toVar(); // accumulated internal path length
        const tSeg = dvSeed.toVar();

        Loop(PATH_SEGMENTS, () => {
          // -- image-space exit search: refine the segment length against the
          // back-face buffer. Each pass reprojects the current estimate, so an
          // estimate that overshoots is pulled back onto a real surface.
          const Nb = vec3(0.0, 0.0, 1.0).toVar();
          const okB = float(0.0).toVar();
          for (let r = 0; r < EXIT_REFINEMENTS; r++) {
            const Pest = orig.add(dir.mul(tSeg));
            const uvE = projectToBufferUV(Pest).clamp(0.0, 1.0);
            const bb = backFaceData(uvE).toVar();
            If(bb.w.greaterThan(0.0), () => {
              // The buffer stores a distance along the camera ray through this
              // texel, so rebuild the surface point before measuring the
              // segment along the interior direction.
              const rayD = normalize(Pest.sub(camP));
              const Pb = camP.add(rayD.mul(bb.w));
              tSeg.assign(dot(Pb.sub(orig), dir).clamp(MIN_WALL, maxSegment));
              Nb.assign(bb.xyz);
              okB.assign(1.0);
            });
          }
          const exitP = orig.add(dir.mul(tSeg));
          sLen.addAssign(tSeg);

          // Outward exit normal, with a flat perpendicular exit as the
          // fallback where the buffer held nothing.
          const NbRaw = select(okB.greaterThan(0.5), Nb, dir.negate());
          const NbN = normalize(NbRaw)
            .mul(select(dot(NbRaw, dir).greaterThanEqual(0.0), 1.0, -1.0))
            .toVar();

          const cos2 = dot(dir, NbN).clamp(1e-4, 1.0);
          const F2 = fresnelDielectric(cos2, n, float(1.0)); // = 1 under TIR
          const T2 = refract(dir, NbN.negate(), n).toVar(); // exit, η = n → 1
          const okT = T2.dot(T2).greaterThan(1e-6); // false under TIR
          const att = exp(sigma.mul(sLen.negate())); // Beer-Lambert so far

          const Lexit = sampleEnvironment(
            normalize(select(okT, T2, dir)),
            float(FROST_LOD),
          );
          contrib.addAssign(
            att.mul(Lexit).mul(
              thr.mul(float(1.0).sub(F2)).mul(select(okT, 1.0, 0.0)),
            ),
          );

          // Whatever did not leave keeps travelling: the Fresnel-weighted
          // internal reflection continues the path. Under TIR F2 is exactly 1,
          // so the segment loses nothing but path length.
          thr.mulAssign(F2);
          dir.assign(reflect(dir, NbN));
          orig.assign(exitP);

          If(thr.lessThan(THROUGHPUT_CUTOFF), () => {
            Break();
          });
        });

        // Residual energy after the last segment leaves along the current ray.
        // Without it, a truncated path darkens the deepest parts of the body.
        contrib.addAssign(
          exp(sigma.mul(sLen.negate()))
            .mul(thr)
            .mul(sampleEnvironment(dir, float(FROST_LOD))),
        );

        Csum.addAssign(w.mul(contrib));
        Wsum.addAssign(w);
      });

      const transmission = Csum.div(Wsum.max(vec3(1e-4)));
      const outColor = transmission.add(reflection).max(vec3(0.0)).toVar();

      /* -- diagnostics ---------------------------------------------------
         Read these before touching the physics. Thickness exposes whether the
         buffer resolves the body at all, the exit normal exposes whether the
         stored orientation survives re-orientation, and entry Fresnel isolates
         the one term that is independent of the interior path. */
      If(debugView.greaterThan(0.5), () => {
        If(debugView.lessThan(1.5), () => {
          // 1: view-ray thickness, normalised against the bounding diagonal.
          const th = select(
            b0.w.greaterThan(0.0),
            b0.w.sub(distFront).div(diagonal * 0.6),
            float(0.0),
          ).clamp(0.0, 1.0);
          outColor.assign(vec3(th, th, th));
        });
        If(debugView.greaterThan(1.5).and(debugView.lessThan(2.5)), () => {
          // 2: stored back-face normal.
          outColor.assign(
            select(
              b0.w.greaterThan(0.0),
              normalize(b0.xyz).mul(0.5).add(0.5),
              vec3(0.0),
            ),
          );
        });
        If(debugView.greaterThan(2.5), () => {
          // 3: entry Fresnel.
          outColor.assign(vec3(Favg, Favg, Favg));
        });
      });

      return outColor;
    });

    const glassMaterial = new THREE.MeshBasicNodeMaterial();
    glassMaterial.colorNode = glassColor();
    // Winding is unreliable, so both sides draw and the nearest surface wins
    // through the depth test.
    glassMaterial.side = THREE.DoubleSide;

    subject.traverse((object) => {
      if (object.isMesh) object.material = glassMaterial;
    });

    this.subject = subject;
    this.diagonal = diagonal;
    this.material = glassMaterial;
    this.backFaceMaterial = backFaceMaterial;
    this.backFaceScene = new THREE.Scene();
    this.renderTarget = renderTarget;
    this.debugView = debugView;
    this.sampleEnvironment = sampleEnvironment;
    this.spectralSamples = SPECTRAL_SAMPLES;
    this.pathSegments = PATH_SEGMENTS;
    this.ior = IOR;
    this.abbe = ABBE;
    this.mirror = null;
    this.mirrorPairs = [];

    this.rebuildMirror();
  }

  /**
   * Builds the data pass's copy of the subject in its own scene, sharing
   * geometry and swapping in the data material, then pairs every node with its
   * copy so poses can be followed later.
   *
   * The constructor calls this. Call it again when the subject's *structure*
   * changes — meshes added or removed, a geometry swapped — because the pairing
   * is fixed at build time. Pose changes never need it; they are followed on
   * every pass.
   */
  rebuildMirror() {
    if (this.mirror) this.backFaceScene.remove(this.mirror);

    const mirror = this.subject.clone(true);
    mirror.traverse((object) => {
      if (object.isMesh) object.material = this.backFaceMaterial;
    });
    this.backFaceScene.add(mirror);
    this.mirror = mirror;

    // clone(true) preserves child order, so a parallel walk stays aligned.
    const pairs = [];
    const pair = (source, copy) => {
      if (!copy) return;
      pairs.push([source, copy]);
      for (let index = 0; index < source.children.length; index += 1) {
        pair(source.children[index], copy.children[index]);
      }
    };
    pair(this.subject, mirror);
    this.mirrorPairs = pairs;
  }

  /**
   * Registers the copy with the subject's current pose: the root takes the
   * subject's full world transform, so ancestor motion counts even though the
   * copy lives in its own scene, and every descendant takes its own local
   * matrix, visibility, and morph weights.
   *
   * A copy that is not followed is the quiet failure of this design: the
   * visible surface moves, the stored back faces do not, and the interior
   * refracts a pose the body no longer holds. What needs no work is what the
   * copy shares by reference — geometry buffers, so vertex edits propagate, and
   * skeletons, so skinned animation propagates. Morph weights are cloned into a
   * separate array and are copied here.
   */
  syncMirror() {
    this.subject.updateWorldMatrix(true, true);

    this.mirror.matrix.copy(this.subject.matrixWorld);
    this.mirror.matrix.decompose(
      this.mirror.position,
      this.mirror.quaternion,
      this.mirror.scale,
    );
    this.mirror.visible = this.subject.visible;

    for (let index = 1; index < this.mirrorPairs.length; index += 1) {
      const [source, copy] = this.mirrorPairs[index];
      copy.matrix.copy(source.matrix);
      copy.matrix.decompose(copy.position, copy.quaternion, copy.scale);
      copy.visible = source.visible;

      const weights = source.morphTargetInfluences;
      if (weights && copy.morphTargetInfluences) {
        for (let target = 0; target < weights.length; target += 1) {
          copy.morphTargetInfluences[target] = weights[target];
        }
      }
    }
  }

  /**
   * Background radiance node for the same probe the transmission path reads.
   * Assign it to `scene.backgroundNode` so the body refracts the world the
   * viewer is actually looking at.
   *
   * The direction is the background mesh's geometric world normal, not
   * `positionWorld − cameraPosition`. A background node is drawn on a unit
   * sphere the renderer owns, and nothing guarantees where that sphere sits:
   * when it is centred on the world origin instead of the camera, a
   * position-derived direction squeezes the entire view into a cone of
   * half-angle `asin(1 / |cameraPosition|)` around the camera-to-origin axis.
   * The result still looks like a lit environment, just heavily magnified and
   * warped, so it is easy to mistake for a low-resolution probe. A sphere's
   * outward normal is translation invariant, so it is the true view direction
   * wherever the sphere is placed.
   */
  get backgroundNode() {
    return this.sampleEnvironment(normalize(normalWorldGeometry), float(0.0));
  }

  /** Size in physical pixels; must match the drawing buffer. */
  setSize(width, height) {
    this.renderTarget.setSize(Math.max(1, width), Math.max(1, height));
  }

  /** @param {keyof GLASS_DEBUG_VIEWS} view */
  setDebugView(view) {
    this.debugView.value = GLASS_DEBUG_VIEWS[view] ?? GLASS_DEBUG_VIEWS.final;
  }

  /**
   * Pass 1. Run this before the camera pass with the same camera. Render
   * targets are never tone mapped by the renderer, so the stored normals and
   * distances stay raw.
   */
  renderBackFaces(renderer, camera) {
    this.syncMirror();

    const previousTarget = renderer.getRenderTarget();
    renderer.setRenderTarget(this.renderTarget);
    renderer.render(this.backFaceScene, camera);
    renderer.setRenderTarget(previousTarget);
  }

  dispose() {
    this.renderTarget.dispose();
    this.material.dispose();
    this.backFaceMaterial.dispose();
    this.backFaceScene.clear();
  }
}
