import {
  AdditiveBlending,
  Color,
  HalfFloatType,
  InstancedMesh,
  LinearFilter,
  OrthographicCamera,
  PlaneGeometry,
  RenderTarget,
  RepeatWrapping,
  Scene,
} from 'three'
import { MeshBasicNodeMaterial } from 'three/webgpu'
import type {
  MeshStandardNodeMaterial,
  Node,
  WebGPURenderer,
} from 'three/webgpu'
import {
  Fn,
  dFdx,
  dFdy,
  exp,
  float,
  instanceIndex,
  max,
  normalize,
  positionGeometry,
  positionWorld,
  refract,
  texture,
  varying,
  vec2,
  vec3,
  vec4,
} from 'three/tsl'
import { sunDirectionUniform } from './sky'
import type { WaveSim } from './wave-sim'

export const CAUSTIC_TILE = 17
const GRID = 256
const PROJECT_DEPTH = 24

/**
 * Project the live 17 m wave band onto a virtual floor and encode the old to
 * new differential-area ratio as a repeating caustic concentration tile.
 */
export class CausticsPass {
  readonly renderTarget: RenderTarget
  readonly textureNode: ReturnType<typeof texture>

  private readonly scene = new Scene()
  private readonly camera = new OrthographicCamera(-1, 1, 1, -1, 0, 1)

  constructor(simulation: WaveSim, resolution = 1024) {
    this.renderTarget = new RenderTarget(resolution, resolution, {
      type: HalfFloatType,
      depthBuffer: false,
    })
    this.renderTarget.texture.wrapS = RepeatWrapping
    this.renderTarget.texture.wrapT = RepeatWrapping
    this.renderTarget.texture.minFilter = LinearFilter
    this.renderTarget.texture.magFilter = LinearFilter
    this.textureNode = texture(this.renderTarget.texture)

    const material = new MeshBasicNodeMaterial()
    material.blending = AdditiveBlending
    material.depthTest = false
    material.depthWrite = false

    const tile = float(CAUSTIC_TILE)
    const uv01 = positionGeometry.xy.mul(0.5).add(0.5)
    const worldXZ = uv01.mul(tile)
    const patchLength = simulation.patchLengths[1]
    const derivatives = simulation.derivativeNodes[1].sample(
      worldXZ.div(patchLength),
    )
    const displacement = simulation.displacementNodes[1].sample(
      worldXZ.div(patchLength),
    )
    const surfaceNormal = normalize(
      vec3(derivatives.x.negate(), 1, derivatives.y.negate()),
    )
    const eta = float(1 / 1.333)
    const flatRefract = refract(
      sunDirectionUniform.negate(),
      vec3(0, 1, 0),
      eta,
    )
    const waveRefract = refract(
      sunDirectionUniform.negate(),
      surfaceNormal,
      eta,
    )
    const depth = float(PROJECT_DEPTH)
    const oldPosition = worldXZ.add(
      flatRefract.xz.mul(depth.div(flatRefract.y.abs())),
    )
    const newPosition = worldXZ
      .add(displacement.xz)
      .add(
        waveRefract.xz.mul(
          depth.add(displacement.y).div(waveRefract.y.abs()),
        ),
      )
    const centered = newPosition.sub(
      flatRefract.xz.mul(depth.div(flatRefract.y.abs())),
    )
    const varyingOld = varying(oldPosition) as unknown as Node<'vec2'>
    const varyingNew = varying(newPosition) as unknown as Node<'vec2'>

    const instanceX = float(instanceIndex.mod(3)).sub(1).mul(2)
    const instanceY = float(instanceIndex.div(3)).sub(1).mul(2)
    const ndc = centered
      .div(tile)
      .mul(2)
      .sub(1)
      .add(vec2(instanceX, instanceY))
    material.vertexNode = vec4(ndc, 0, 1)
    material.colorNode = Fn(() => {
      const oldArea = dFdx(varyingOld).length().mul(dFdy(varyingOld).length())
      const newArea = max(
        dFdx(varyingNew).length().mul(dFdy(varyingNew).length()),
        1e-6,
      )
      const intensity = oldArea.div(newArea).mul(0.18)
      return vec4(vec3(intensity.min(6)), 1)
    })()

    const mesh = new InstancedMesh(
      new PlaneGeometry(2, 2, GRID, GRID),
      material,
      9,
    )
    mesh.frustumCulled = false
    this.scene.add(mesh)
    this.scene.background = new Color(0x000000)
  }

  update(renderer: WebGPURenderer): void {
    renderer.setRenderTarget(this.renderTarget)
    void renderer.render(this.scene, this.camera)
    renderer.setRenderTarget(null)
  }

  dispose(): void {
    this.renderTarget.dispose()
  }
}

/** Sample the projected caustic tile along the sun direction at world position. */
export function causticWorldSample(
  causticsNode: ReturnType<typeof texture>,
) {
  return Fn(([worldPosition]: [Node<'vec3'>]) => {
    const up = sunDirectionUniform.y.max(0.2)
    const travel = worldPosition.y.negate().div(up)
    const surfaceXZ = vec2(
      worldPosition.x.add(sunDirectionUniform.x.mul(travel)),
      worldPosition.z.add(sunDirectionUniform.z.mul(travel)),
    )
    const uv = surfaceXZ.div(CAUSTIC_TILE)
    const spread = float(0.0016)
    const red = causticsNode.sample(uv).r
    const green = causticsNode
      .sample(uv.add(vec2(spread, spread.negate())))
      .r
    const blue = causticsNode
      .sample(uv.add(vec2(spread.negate().mul(1.6), spread)))
      .r
    const depthFade = exp(worldPosition.y.mul(0.055)).min(1)
    return vec3(red, green, blue).mul(depthFade)
  })
}

/** Multiply received direct light by the live caustic concentration field. */
export function applyCaustics(
  material: MeshStandardNodeMaterial,
  causticsNode: ReturnType<typeof texture>,
  strength = 1.4,
): void {
  const sample = causticWorldSample(causticsNode)
  material.receivedShadowNode = Fn(([shadow]: [Node<'float'>]) => {
    const caustic = sample(positionWorld).g
    return shadow.mul(caustic.mul(strength).add(1))
  }) as unknown as typeof material.receivedShadowNode
}
