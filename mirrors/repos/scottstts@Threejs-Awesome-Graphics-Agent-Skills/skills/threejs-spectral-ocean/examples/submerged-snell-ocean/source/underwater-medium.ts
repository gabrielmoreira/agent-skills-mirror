import {
  AdditiveBlending,
  AgXToneMapping,
  Camera,
  InstancedMesh,
  NoToneMapping,
  Scene,
  SRGBColorSpace,
  TetrahedronGeometry,
} from 'three'
import {
  MeshBasicNodeMaterial,
  MeshStandardNodeMaterial,
  RenderPipeline,
} from 'three/webgpu'
import type { Node, PassNode, WebGPURenderer } from 'three/webgpu'
import {
  Fn,
  If,
  Loop,
  cameraPosition,
  cameraProjectionMatrixInverse,
  cameraWorldMatrix,
  exp,
  exp2,
  float,
  fract,
  hash,
  instanceIndex,
  max,
  mix,
  mrt,
  normalGeometry,
  normalView,
  normalize,
  output,
  pass,
  positionGeometry,
  positionWorld,
  pow,
  renderOutput,
  screenUV,
  sin,
  smoothstep,
  uniform,
  vec2,
  vec3,
  vec4,
} from 'three/tsl'
import { bloom } from 'three/addons/tsl/display/BloomNode.js'
import { applyCaustics, causticWorldSample, CausticsPass } from './caustics'
import { currentFlow } from './current'
import { dreamGrade, gradeParams } from './grade'
import { fbm2, valueNoise2 } from './noise'
import { sunColorUniform, sunDirectionUniform } from './sky'

const SIGMA = vec3(0.026, 0.0085, 0.005)
const AMBIENT_DOWN = vec3(0.01, 0.075, 0.14)
const AMBIENT_UP = vec3(0.1, 0.32, 0.37)

export const underwaterDebugModes = new Map([
  ['final', 0],
  ['no-medium', 1],
  ['fog', 2],
  ['god-rays', 3],
  ['caustics', 4],
  ['depth', 5],
])

export interface UnderwaterMediumOptions {
  godraySteps?: number
  particulateCount?: number
}

/**
 * Composite aquatic extinction, in-scatter, full-resolution caustic god rays,
 * pre-tonemap bloom, AgX, a 32-cube grade, and a spatial vignette.
 */
export class UnderwaterMediumPipeline {
  readonly scenePass: PassNode
  readonly mediumEnabled = uniform(1)
  readonly interior = uniform(0)

  private readonly pipeline: RenderPipeline
  private readonly debugMode = uniform(0)
  private readonly timeUniform = uniform(0)
  private readonly particles: InstancedMesh
  private readonly scene: Scene

  constructor(
    renderer: WebGPURenderer,
    scene: Scene,
    camera: Camera,
    caustics: CausticsPass,
    options: UnderwaterMediumOptions = {},
  ) {
    this.scene = scene
    renderer.toneMapping = NoToneMapping
    const godraySteps = options.godraySteps ?? 14
    const causticSample = causticWorldSample(caustics.textureNode)

    const scenePass = pass(scene, camera, { samples: 4 })
    scenePass.setMRT(mrt({ output, normal: vec4(normalView, 1) }))
    this.scenePass = scenePass
    const sceneColor = scenePass.getTextureNode('output')
    const viewZ = scenePass.getViewZNode()

    const foggedNode = Fn(() => {
      const distance = viewZ.negate().min(3500).toVar()
      const ndc = vec2(
        screenUV.x.mul(2).sub(1),
        float(1).sub(screenUV.y).mul(2).sub(1),
      )
      const farHomogeneous = cameraProjectionMatrixInverse.mul(
        vec4(ndc, 1, 1),
      )
      const farView = farHomogeneous.xyz.div(farHomogeneous.w)
      const viewPosition = farView.mul(viewZ.div(farView.z))
      const worldPosition = cameraWorldMatrix.mul(vec4(viewPosition, 1)).xyz
      const rayDirection = worldPosition
        .sub(cameraPosition)
        .div(max(distance, 1e-4))
      const transmittance = exp(SIGMA.mul(distance).negate())
      const upness = smoothstep(-0.5, 0.75, rayDirection.y)
      const cameraDim = exp(cameraPosition.y.min(0).mul(0.03))
      const sunward = pow(
        max(rayDirection.dot(sunDirectionUniform), 0),
        6,
      ).mul(0.06)
      const interiorKeep = float(1).sub(this.interior.mul(0.94))
      const inscatter = mix(AMBIENT_DOWN, AMBIENT_UP, upness)
        .mul(cameraDim)
        .add(sunColorUniform.mul(sunward))
        .mul(interiorKeep)
      const fogged = sceneColor.rgb
        .mul(transmittance)
        .add(inscatter.mul(float(1).sub(transmittance.g)))
      return vec4(mix(sceneColor.rgb, fogged, this.mediumEnabled), 1)
    })()

    const raysNode = Fn(() => {
      const distance = viewZ.negate().min(3500).toVar()
      const ndc = vec2(
        screenUV.x.mul(2).sub(1),
        float(1).sub(screenUV.y).mul(2).sub(1),
      )
      const farHomogeneous = cameraProjectionMatrixInverse.mul(
        vec4(ndc, 1, 1),
      )
      const farView = farHomogeneous.xyz.div(farHomogeneous.w)
      const viewPosition = farView.mul(viewZ.div(farView.z))
      const worldPosition = cameraWorldMatrix.mul(vec4(viewPosition, 1)).xyz
      const rayDirection = worldPosition
        .sub(cameraPosition)
        .div(max(distance, 1e-4))
      const marchLength = distance.min(85)
      const stepLength = marchLength.div(godraySteps)
      const jitter = fract(
        sin(screenUV.x.mul(1741.37).add(screenUV.y.mul(921.13))).mul(
          43758.55,
        ),
      )
      const shaft = float(0).toVar()
      If(this.mediumEnabled.greaterThan(0.001), () => {
        Loop(
          { start: 0, end: godraySteps },
          (loopVariables: { i: Node<'int'> }) => {
            const index = loopVariables.i
            const distanceAlongRay = stepLength.mul(float(index).add(jitter))
            const samplePosition = cameraPosition.add(
              rayDirection.mul(distanceAlongRay),
            )
            const light = causticSample(samplePosition).g
            shaft.addAssign(light.mul(exp(distanceAlongRay.mul(-0.03))))
          },
        )
      })
      const interiorKeep = float(1).sub(this.interior.mul(0.94))
      return sunColorUniform
        .mul(shaft.mul(stepLength).mul(0.007))
        .mul(interiorKeep)
        .mul(this.mediumEnabled)
    })()

    const withMedium = vec4(foggedNode.rgb.add(raysNode), 1)
    const bloomNode = bloom(withMedium, 0.35, 0.55, 1)
    const hdr = withMedium.add(bloomNode)
    const exposed = hdr.mul(exp2(gradeParams.exposureEV))
    const mapped = renderOutput(exposed, AgXToneMapping, SRGBColorSpace)
    const graded = dreamGrade(mapped)
    const rawMapped = renderOutput(sceneColor, AgXToneMapping, SRGBColorSpace)
    const fogMapped = renderOutput(foggedNode, AgXToneMapping, SRGBColorSpace)
    const raysMapped = renderOutput(vec4(raysNode, 1), AgXToneMapping, SRGBColorSpace)
    const causticsMapped = renderOutput(
      vec4(caustics.textureNode.rgb, 1),
      AgXToneMapping,
      SRGBColorSpace,
    )
    const depthMapped = vec4(vec3(scenePass.getLinearDepthNode()), 1)

    const selected = Fn(() => {
      const result = graded.toVar()
      If(this.debugMode.equal(1), () => result.assign(rawMapped))
      If(this.debugMode.equal(2), () => result.assign(fogMapped))
      If(this.debugMode.equal(3), () => result.assign(raysMapped))
      If(this.debugMode.equal(4), () => result.assign(causticsMapped))
      If(this.debugMode.equal(5), () => result.assign(depthMapped))
      return result
    })()

    this.pipeline = new RenderPipeline(renderer, selected)
    this.pipeline.outputColorTransform = false
    this.particles = createParticulates(
      this.timeUniform,
      options.particulateCount ?? 18_000,
    )
    scene.add(this.particles)
  }

  setDebugMode(mode: string): void {
    this.debugMode.value = underwaterDebugModes.get(mode) ?? 0
  }

  setInterior(value: number): void {
    this.interior.value = Math.min(1, Math.max(0, value))
  }

  update(elapsed: number): void {
    this.timeUniform.value = elapsed
  }

  render(): void {
    void this.pipeline.render()
  }

  dispose(): void {
    this.scene.remove(this.particles)
    this.particles.geometry.dispose()
    if (Array.isArray(this.particles.material)) {
      for (const material of this.particles.material) material.dispose()
    } else {
      this.particles.material.dispose()
    }
    this.pipeline.dispose()
  }
}

/** White-sand material with procedural ripples and live caustic lighting. */
export function createSeabedMaterial(
  caustics: CausticsPass,
): MeshStandardNodeMaterial {
  const material = new MeshStandardNodeMaterial()
  material.roughness = 1
  material.metalness = 0
  const xz = positionWorld.xz
  const tone = fbm2(xz.mul(0.02))
  const patchTone = fbm2(xz.mul(0.0045))
  const base = mix(
    vec3(0.48, 0.43, 0.33),
    vec3(0.58, 0.54, 0.43),
    tone,
  )
  material.colorNode = mix(
    base,
    vec3(0.33, 0.4, 0.3),
    patchTone.smoothstep(0.62, 0.85).mul(0.5),
  )
  material.normalNode = Fn(() => {
    const warp = fbm2(xz.mul(0.09)).mul(7)
    const firstBand = sin(xz.x.mul(1.9).add(xz.y.mul(0.9)).add(warp))
    const secondBand = sin(
      xz.x.mul(-1).add(xz.y.mul(2.3)).add(warp.mul(1.4)),
    )
    const micro = valueNoise2(xz.mul(7)).sub(0.5).mul(0.24)
    const slope = vec2(firstBand.mul(0.08), secondBand.mul(0.06)).add(micro)
    return normalize(normalGeometry.add(vec3(slope.x, 0, slope.y)))
  })()
  applyCaustics(material, caustics.textureNode, 1.15)
  return material
}

function createParticulates(
  timeUniform: Node<'float'>,
  count: number,
): InstancedMesh {
  const material = new MeshBasicNodeMaterial()
  material.blending = AdditiveBlending
  material.depthWrite = false
  material.transparent = true
  const boxSize = float(60)
  const half = boxSize.div(2)
  const seed = vec3(
    hash(instanceIndex.add(1)),
    hash(instanceIndex.add(7919)),
    hash(instanceIndex.add(104729)),
  )
  const base = seed.mul(boxSize)
  const drift = currentFlow(base, timeUniform)
    .mul(4)
    .add(vec3(0, timeUniform.mul(0.06), 0))
  const wrapped = fract(base.add(drift).sub(cameraPosition).div(boxSize))
    .mul(boxSize)
    .sub(half)
  const center = cameraPosition.add(wrapped)
  const size = hash(instanceIndex.add(31)).mul(0.5).add(0.5).mul(0.02)
  material.positionNode = center.add(positionGeometry.mul(size))
  const cameraDistance = wrapped.length()
  const fade = smoothstep(half.mul(0.95), half.mul(0.45), cameraDistance)
  const depthGlow = exp(center.y.mul(0.04)).min(1)
  material.colorNode = vec4(
    vec3(0.7, 0.82, 0.84).mul(0.5).mul(depthGlow),
    1,
  )
  material.opacityNode = fade
  const particles = new InstancedMesh(
    new TetrahedronGeometry(1, 0),
    material,
    count,
  )
  particles.frustumCulled = false
  return particles
}
