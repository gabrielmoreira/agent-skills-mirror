import { DoubleSide } from 'three'
import { MeshBasicNodeMaterial } from 'three/webgpu'
import {
  Fn,
  If,
  cameraProjectionMatrix,
  cameraProjectionMatrixInverse,
  cameraPosition,
  cameraViewMatrix,
  cameraWorldMatrix,
  dot,
  float,
  getScreenPosition,
  getViewPosition,
  max,
  mix,
  modelWorldMatrix,
  mrt,
  normalize,
  normalView,
  positionLocal,
  pow,
  reflect,
  refract,
  smoothstep,
  step,
  varying,
  vec2,
  vec3,
  vec4,
  viewportDepthTexture,
  viewportSafeUV,
} from 'three/tsl'
import type { Node } from 'three/webgpu'
import { fbm2, valueNoise2 } from './noise'
import { skyRadiance, sunColorUniform, sunDirectionUniform } from './sky'
import type { WaveSim } from './wave-sim'

/** Linear-HDR water body palette for the fixed golden-afternoon sky. */
const DEEP = vec3(0.005, 0.045, 0.09)
const SHALLOW = vec3(0.014, 0.13, 0.17)
const SSS_TINT = vec3(0.035, 0.2, 0.22)
const MIST = vec3(0.38, 0.5, 0.58)

export interface OceanMaterialOptions {
  /** Full three-cascade sampling + foam; false = far skirt (cascade 0 only). */
  detailed: boolean
  /** One shared opaque-frame copy, sampled at each surface's refracted UV. */
  sceneBackdrop: {
    sample: (uv: Node<'vec2'>) => Node<'vec4'>
  }
  /** Camera-medium authority: 0 above the displaced surface, 1 below it. */
  submerged: Node<'float'>
  /**
   * Half-size of the detailed mesh: fine cascades fade to zero approaching
   * this edge so the surface exactly matches the cascade-0-only skirt at the
   * seam. Zero disables the fade (skirt).
   */
  edgeFadeHalfSize?: number
}

/**
 * Shade the ocean surface with the spectral-ocean optics contract:
 * fold-aware normals from summed cascade derivatives, side-aware Fresnel,
 * shared skyRadiance for reflection, crest subsurface scatter, Jacobian foam
 * with history, and — from below — the true Snell's window with total
 * internal reflection outside it. Keep `submerged` at one for a permanently
 * underwater camera; use a displaced-waterline probe for live crossings.
 */
export function createOceanSurfaceMaterial(
  sim: WaveSim,
  timeUniform: Node<'float'>,
  options: OceanMaterialOptions,
): MeshBasicNodeMaterial {
  const material = new MeshBasicNodeMaterial()
  material.side = DoubleSide
  material.fog = false
  // The viewport copy used by underwater refraction must be taken after the
  // opaque scene has rendered but before this surface shades. Alpha remains
  // one and depth still writes, so the ocean is visually/depth-wise opaque;
  // the transparent queue is only render-order ownership for the backdrop.
  material.transparent = true
  material.depthWrite = true
  // A transparent DoubleSide material normally draws back and front in two
  // passes. This is a single geometric sheet, and a second pass would copy
  // the first pass's water result into its own refraction backdrop.
  material.forceSinglePass = true
  // Screen-space AO estimates missing *diffuse* ambient light. This material
  // owns reflective/transmissive water optics, so cavity-multiplying its final
  // color is physically wrong and exposes GTAO's sampling lattice at grazing
  // incidence. Override the normal MRT's spare alpha receiver channel only.
  material.mrtNode = mrt({ normal: vec4(normalView, 0) })

  const patch = sim.patchLengths
  const cascadeCount = options.detailed ? 3 : 1

  // ── Vertex: displacement from summed cascades ──────────────────────────
  const baseWorld = modelWorldMatrix.mul(vec4(positionLocal, 1)).xyz
  const xz = baseWorld.xz

  // Keep the skirt flat; vertex-sampling waves at 187 m spacing aliases.
  // aliasing); the inner mesh fades ALL displacement to zero at its edge so
  // the two surfaces meet exactly.
  const edgeHalf = options.edgeFadeHalfSize ?? 0
  const edgeKeep =
    edgeHalf > 0
      ? float(1).sub(
          smoothstep(
            edgeHalf - 170,
            edgeHalf - 15,
            max(positionLocal.x.abs(), positionLocal.z.abs()),
          ),
        )
      : float(0)

  // Apply spectral LOD to vertex displacement by pixel footprint.
  // like the fragment side (the base plane sits at y = 0, so the grazing gap
  // is just camera height). Displaced geometry aliases at the horizon even
  // after normals flatten: silhouette teeth, and vHeight-driven body-color
  // stripes — the residual comb. Cascade 0 fades too; only edgeKeep used to
  // bound it, which left raw swell geometry out to the mesh diagonals.
  const vertexDistance = cameraPosition.sub(baseWorld).length()
  const vertexGap = cameraPosition.y.abs().max(0.5)
  const vertexFootprint = vertexDistance.mul(vertexDistance).mul(0.001).div(vertexGap)
  const vertexKeeps = [
    // Match the above-water cascade-0 normal cutoff. Keeping coarse vertex
    // displacement to 18 m/pixel left sub-pixel triangle rows even after the
    // fragment normal and height response had flattened, producing both the
    // dark comb and the faint gray band at the inner-mesh transition.
    float(1).sub(smoothstep(2.5, 5.5, vertexFootprint)),
    float(1).sub(smoothstep(0.35, 1.2, vertexFootprint)),
    float(1).sub(smoothstep(0.1, 0.4, vertexFootprint)),
  ]

  let displacement: Node<'vec3'> = sim.displacementNodes[0]
    .sample(xz.div(patch[0]))
    .xyz.mul(edgeKeep)
    .mul(vertexKeeps[0])
  for (let i = 1; i < cascadeCount; i++) {
    displacement = displacement.add(
      sim.displacementNodes[i].sample(xz.div(patch[i])).xyz.mul(edgeKeep).mul(vertexKeeps[i]),
    )
  }

  const foamHistory = options.detailed
    ? sim.displacementNodes[0].sample(xz.div(patch[0])).w.min(
        sim.displacementNodes[1].sample(xz.div(patch[1])).w,
      )
    : float(1)

  material.positionNode = positionLocal.add(displacement)

  const vWorldXZ = varying(xz) as unknown as Node<'vec2'>
  const vHeight = varying(displacement.y) as unknown as Node<'float'>
  const vFoam = varying(foamHistory) as unknown as Node<'float'>
  const vWorld = varying(baseWorld.add(displacement)) as unknown as Node<'vec3'>

  // ── Fragment ───────────────────────────────────────────────────────────
  const vEdgeKeep = varying(edgeKeep) as unknown as Node<'float'>
  const vDistance = varying(
    cameraPosition.sub(baseWorld.add(displacement)).length(),
  ) as unknown as Node<'float'>

  // Spectral LOD by PIXEL FOOTPRINT, not distance. The cascade maps carry no
  // mips; sampling them where one output pixel spans more than a band's
  // wavelength beats into comb/moiré patterns. At grazing incidence the
  // vertical footprint on the surface is distance²·pixelAngle / heightGap
  // (|viewDir.y| = heightGap/distance): a 4.4 m deck eye is under-sampled at
  // 200 m while a diver sees the same span steeply and keeps full detail —
  // pure distance fades can never serve both (the "horizon comb" artifact).
  const heightGap = cameraPosition.y.sub(vWorld.y).abs().max(0.5)
  const pixelFootprint = vDistance.mul(vDistance).mul(0.001).div(heightGap)
  // The shortest wavelengths are approximately 41 m, 2.8 m, and 0.83 m.
  // Cascade 0 needs a stricter keep for the narrow above-water GGX lobe:
  // attenuate while its shortest wave still spans ~16 pixels and finish by
  // ~8 pixels. Sampling first and flattening the reconstructed normal later
  // preserves the alias and creates a visible horizon comb.
  const keepCascade0Above = float(1).sub(smoothstep(2.5, 5.5, pixelFootprint))
  const keepCascade1 = float(1).sub(smoothstep(0.35, 1.2, pixelFootprint))
  const keepCascade2 = float(1).sub(smoothstep(0.1, 0.4, pixelFootprint))
  const cascadeKeeps = [float(1), keepCascade1, keepCascade2]

  const derivative0 = sim.derivativeNodes[0]
    .sample(vWorldXZ.div(patch[0]))
    .mul(vEdgeKeep)
  let derivatives: Node<'vec4'> = derivative0
  for (let i = 1; i < cascadeCount; i++) {
    derivatives = derivatives.add(
      sim.derivativeNodes[i].sample(vWorldXZ.div(patch[i])).mul(vEdgeKeep).mul(cascadeKeeps[i]),
    )
  }
  const aboveDerivatives = derivatives.sub(
    derivative0.mul(float(1).sub(keepCascade0Above)),
  )

  // Use the fold-aware slope denominator 1 + lambda * dD/dx. Optical side is a camera
  // medium state, never a per-triangle facing test: right at the crossing a
  // displaced sheet can expose nearby backfaces before the camera itself is
  // submerged. The surface must not mix two optical media in one frame.
  const slopeX = derivatives.x.div(max(0.18, derivatives.z.add(1)))
  const slopeZ = derivatives.y.div(max(0.18, derivatives.w.add(1)))
  const upNormal = normalize(vec3(slopeX.negate(), 1, slopeZ.negate()))
  const isAbove = float(1).sub(options.submerged)
  const sideSign = isAbove.mul(2).sub(1)
  const rawNormal = upNormal.mul(sideSign)

  const toCamera = cameraPosition.sub(vWorld)
  const viewDistance = toCamera.length()
  const viewDir = toCamera.div(viewDistance)

  // Normal flatten rides the same footprint (cascade-0 bottoms out ~41 m):
  // past it the surface hands off to the smooth mirror + analytic sky. The
  // 41 m tail still combs above ~λ/8, so complete the flatten by 16.
  const distanceFade = smoothstep(5.0, 16.0, pixelFootprint)
  const normal = normalize(mix(rawNormal, vec3(0, sideSign, 0), distanceFade))

  const sunDir = sunDirectionUniform

  // Trace the underwater Snell ray through the opaque framebuffer. The first
  // depth lookup estimates subject distance; the second projection starts at
  // the actual displaced interface hit point, preserving structure alignment
  // at the waterline. The framebuffer work is behind the same coherent camera-
  // medium uniform as the rest of the underwater pipeline, so above-water
  // frames pay no depth/color refraction samples.
  const incident = viewDir.negate()
  const refracted = refract(incident, normal, 1.333)
  const insideWindow = step(1e-5, dot(refracted, refracted))
  const refractedSample = Fn(() => {
    const sample = vec4(0).toVar()
    If(options.submerged.greaterThan(0.5), () => {
      const initialRefractedView = cameraViewMatrix.mul(vec4(refracted, 0)).xyz
      const initialRefractedUv = getScreenPosition(
        initialRefractedView,
        cameraProjectionMatrix,
      )
      const initialUvInside = step(0.002, initialRefractedUv.x)
        .mul(step(initialRefractedUv.x, 0.998))
        .mul(step(0.002, initialRefractedUv.y))
        .mul(step(initialRefractedUv.y, 0.998))
      const initialSafeUv = viewportSafeUV(
        initialRefractedUv.clamp(vec2(0.002), vec2(0.998)),
      )
      const initialDepth = viewportDepthTexture(initialSafeUv).r
      const initialSourceView = getViewPosition(
        initialSafeUv,
        initialDepth,
        cameraProjectionMatrixInverse,
      )
      const initialSourceWorld = cameraWorldMatrix.mul(vec4(initialSourceView, 1)).xyz
      const estimatedDistance = initialSourceWorld.sub(vWorld).length().clamp(0.5, 3200.0)

      const refractedTargetWorld = vWorld.add(refracted.mul(estimatedDistance))
      const refractedTargetView = cameraViewMatrix.mul(vec4(refractedTargetWorld, 1)).xyz
      const refractedUv = getScreenPosition(refractedTargetView, cameraProjectionMatrix)
      const uvInside = step(0.002, refractedUv.x)
        .mul(step(refractedUv.x, 0.998))
        .mul(step(0.002, refractedUv.y))
        .mul(step(refractedUv.y, 0.998))
        .mul(initialUvInside)
      const safeUv = viewportSafeUV(refractedUv.clamp(vec2(0.002), vec2(0.998)))
      const sceneColor = options.sceneBackdrop.sample(safeUv as Node<'vec2'>).rgb
      const sourceDepth = viewportDepthTexture(safeUv).r
      const sourceView = getViewPosition(safeUv, sourceDepth, cameraProjectionMatrixInverse)
      const sourceWorld = cameraWorldMatrix.mul(vec4(sourceView, 1)).xyz
      const sourceOffset = sourceWorld.sub(vWorld)
      const rayDistance = max(dot(sourceOffset, refracted), 0.0)
      const lateralError = sourceOffset.sub(refracted.mul(rayDistance)).length()
      const rayThickness = rayDistance.mul(0.015).add(0.35)
      const rayAlignment = float(1).sub(
        smoothstep(rayThickness, rayThickness.mul(3.0), lateralError),
      )
      const validity = step(0.05, sourceWorld.y)
        .mul(step(sourceView.length(), 3200.0))
        .mul(uvInside)
        .mul(rayAlignment)
        .mul(insideWindow)
      sample.assign(vec4(sceneColor, validity))
    })
    return sample
  })()
  const refractedScene = refractedSample.rgb
  const refractedSceneValid = refractedSample.a

  // ── Above-surface shading ──────────────────────────────────────────────
  // The FFT resolves down to ~0.83 m. Add two weak, independently advected
  // capillary bands below that limit so close water carries real small-scale
  // slope variation without rewriting the swell. Each band disappears once
  // its shortest structure is below the current pixel footprint.
  const aboveSlopeX = aboveDerivatives.x.div(max(0.18, aboveDerivatives.z.add(1)))
  const aboveSlopeZ = aboveDerivatives.y.div(max(0.18, aboveDerivatives.w.add(1)))
  let aboveNormal: Node<'vec3'> = normalize(
    vec3(aboveSlopeX.negate(), 1, aboveSlopeZ.negate()),
  )
  if (options.detailed) {
    const detailUvA = vWorldXZ
      .mul(1.7)
      .add(vec2(0.11, -0.07).mul(timeUniform))
    const detailUvB = vWorldXZ
      .mul(4.7)
      .add(vec2(-0.19, 0.13).mul(timeUniform))
    const heightA = valueNoise2(detailUvA)
    const detailA = vec2(
      valueNoise2(detailUvA.add(vec2(0.12, 0))).sub(heightA),
      valueNoise2(detailUvA.add(vec2(0, 0.12))).sub(heightA),
    ).div(0.12)
    const heightB = valueNoise2(detailUvB)
    const detailB = vec2(
      valueNoise2(detailUvB.add(vec2(0.08, 0))).sub(heightB),
      valueNoise2(detailUvB.add(vec2(0, 0.08))).sub(heightB),
    ).div(0.08)
    const detailKeepA = float(1)
      .sub(smoothstep(0.025, 0.12, pixelFootprint))
      .mul(vEdgeKeep)
    const detailKeepB = float(1)
      .sub(smoothstep(0.008, 0.035, pixelFootprint))
      .mul(vEdgeKeep)
    const capillarySlope = detailA
      .mul(detailKeepA)
      .add(detailB.mul(detailKeepB).mul(0.35))
    aboveNormal = normalize(
      normal.add(vec3(capillarySlope.x, 0, capillarySlope.y).mul(0.045)),
    )
  }

  const aboveHeight = vHeight.mul(keepCascade0Above)
  const heightMask = smoothstep(-1.7, 1.5, aboveHeight)
  const bodyBase = mix(DEEP, SHALLOW, heightMask)

  // Keep the resolved-wave scatter for the underwater TIR body.
  // Above-water optics use the capillary-enriched normal below.
  const crestLight = normalize(sunDir.negate().add(normal.mul(0.4)))
  const crestScatter = pow(max(dot(viewDir, crestLight), 0.0), 4.5)
    .mul(1.0)
    .mul(smoothstep(-0.1, 1.1, vHeight))

  const noV = max(dot(viewDir, aboveNormal), 0.001)
  const noL = max(dot(aboveNormal, sunDir), 0.0)
  const fresnelF0 = float(0.02037)
  const fresnel = fresnelF0.add(
    float(1)
      .sub(fresnelF0)
      .mul(pow(float(1).sub(noV), 5.0)),
  )
  const aboveCrestLight = normalize(sunDir.negate().add(aboveNormal.mul(0.4)))
  const aboveCrestScatter = pow(max(dot(viewDir, aboveCrestLight), 0.0), 4.5)
    .mul(smoothstep(-0.1, 1.1, aboveHeight))
  const forwardScatter = pow(max(dot(viewDir, sunDir.negate()), 0.0), 4.0)
    .mul(smoothstep(-0.15, 0.9, aboveHeight))
    .mul(float(1).sub(fresnel))
    .mul(0.32)
  const scatterLight = noL.mul(0.5).add(0.5)
  const body = bodyBase.add(
    SSS_TINT.mul(aboveCrestScatter.add(forwardScatter)).mul(scatterLight),
  )

  // discStrength 0: sunGlint below IS the disc's specular response — the
  // delta-light term. The aureole remains in the shared reflected sky.
  const skyReflection = skyRadiance(reflect(viewDir.negate(), aboveNormal), float(0))

  const halfVector = normalize(sunDir.add(viewDir))
  const noH = max(dot(aboveNormal, halfVector), 0.0)
  const voH = max(dot(viewDir, halfVector), 0.0)
  // The GGX lobe follows resolved FFT slopes while capillary slopes
  // shape the sun lane; capillary slopes break it into near-field facets.
  const roughness = float(0.075)
  const alpha2 = roughness.mul(roughness)
  const distributionDenominator = noH.mul(noH).mul(alpha2.sub(1)).add(1)
  const distribution = alpha2.div(
    distributionDenominator.mul(distributionDenominator).mul(Math.PI),
  )
  const smithK = roughness.add(1).mul(roughness.add(1)).div(8)
  const geometryV = noV.div(noV.mul(float(1).sub(smithK)).add(smithK))
  const geometryL = noL.div(noL.mul(float(1).sub(smithK)).add(smithK).max(1e-4))
  const microFresnel = fresnelF0.add(
    float(1)
      .sub(fresnelF0)
      .mul(pow(float(1).sub(voH), 5.0)),
  )
  const directSpecular = distribution
    .mul(geometryV)
    .mul(geometryL)
    .mul(microFresnel)
    .mul(noL)
    .div(max(noV.mul(noL).mul(4), 0.02))
  const sunGlint = sunColorUniform.mul(directSpecular).mul(3.4)

  let above = mix(body, skyReflection, fresnel).add(sunGlint)

  if (options.detailed) {
    // Jacobian foam: history-driven coverage × bubbly fbm detail, sun/sky lit.
    // Coverage only where the surface genuinely folded; fades with distance
    // so the fbm detail can never read as far-field shimmer.
    const coverage = float(1).sub(smoothstep(-0.05, 0.26, vFoam))
    const bubbleA = fbm2(vWorldXZ.mul(0.9).add(vec2(0.13, 0.07).mul(timeUniform)))
    const bubbleB = fbm2(vWorldXZ.mul(1.7).sub(vec2(0.11, 0.05).mul(timeUniform)))
    const foamKeep = float(1).sub(smoothstep(0.25, 0.8, pixelFootprint))
    const foamMask = coverage
      .mul(bubbleA.mul(bubbleB).mul(1.7).add(0.06))
      .mul(foamKeep)
      .clamp(0, 1)
    const foamAmbient = skyRadiance(aboveNormal, float(0)).mul(0.22)
    const foamShade = foamAmbient.add(
      sunColorUniform.mul(noL.mul(0.9).add(0.3)).mul(0.9),
    )
    above = mix(above, foamShade, foamMask)
  }

  // Aerial haze toward the horizon.
  const haze = float(1).sub(viewDistance.mul(0.0011).pow(2).negate().exp())
  const sunward = pow(max(dot(viewDir.negate(), sunDir), 0.0), 8.0)
  const hazeColor = MIST.add(sunColorUniform.mul(sunward).mul(0.4))
  above = mix(above, hazeColor, haze.clamp(0, 1))

  // ── Below-surface shading: Snell window and TIR underside ──────────────
  const skyThrough = skyRadiance(refracted, float(0)).mul(0.9)
  const windowGlint = pow(max(dot(refracted, sunDir), 0.0), 700.0)
    .mul(24.0)
    .mul(sunColorUniform)

  // Only real geometry in air participates below the surface. The sky dome
  // remains on the analytic path so its sub-pixel HDR sun cannot become
  // framebuffer-sampling noise.
  const aboveWaterStructure = refractedSceneValid
  const transmittedScene = mix(
    skyThrough.add(windowGlint),
    refractedScene,
    aboveWaterStructure,
  )

  // Exact unpolarised dielectric Fresnel for water -> air. Schlick alone
  // does not rise correctly into the critical angle, so it would let the
  // structure remain pasted over what should become total internal reflection.
  const cosIncident = max(dot(viewDir, normal), 0.0)
  const eta = float(1.333)
  const cosTransmitted = float(1)
    .sub(eta.mul(eta).mul(float(1).sub(cosIncident.mul(cosIncident))))
    .max(0.0)
    .sqrt()
  const rs = eta
    .mul(cosIncident)
    .sub(cosTransmitted)
    .div(eta.mul(cosIncident).add(cosTransmitted).max(1e-4))
  const rp = eta
    .mul(cosTransmitted)
    .sub(cosIncident)
    .div(eta.mul(cosTransmitted).add(cosIncident).max(1e-4))
  const interfaceFresnel = rs.mul(rs).add(rp.mul(rp)).mul(0.5)
  const interfaceTransmission = insideWindow.mul(float(1).sub(interfaceFresnel))

  // Outside the critical angle: total internal reflection. The mirror
  // reflects the UPWELLING water light — silvery teal near the medium's
  // horizontal ambient (medium.ts AMBIENT_* mix), not the deep body color.
  // A near-black ceiling here is what carved the bright "gap" band at the
  // surface silhouette against converged fog: the fogged underside must
  // start from a radiance close to what the fog converges to.
  const tirBody = vec3(0.035, 0.14, 0.19).add(SSS_TINT.mul(crestScatter).mul(0.5))

  const below = mix(tirBody, transmittedScene, interfaceTransmission)

  material.colorNode = vec4(mix(below, above, isAbove), 1.0)
  return material
}
