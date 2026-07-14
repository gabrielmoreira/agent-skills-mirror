import {
  BufferAttribute,
  BufferGeometry,
  Mesh,
  PlaneGeometry,
  Scene,
  Vector3,
} from 'three'
import type { WebGPURenderer } from 'three/webgpu'
import { uniform, viewportTexture } from 'three/tsl'
import type { Node } from 'three/webgpu'
import { createOceanSurfaceMaterial } from './ocean-material'
import { WaveSim } from './wave-sim'
import type { Rng } from './random'

export const OCEAN_INNER_HALF_SIZE = 350
export const OCEAN_SKIRT_HOLE_HALF_SIZE = 348
export const OCEAN_SKIRT_OUTER_HALF_SIZE = 3200
const INNER_SIZE = OCEAN_INNER_HALF_SIZE * 2
const OUTER_SINK = 0.14

interface QuadBounds {
  minX: number
  maxX: number
  minZ: number
  maxZ: number
}

const SKIRT_QUADS: readonly QuadBounds[] = [
  {
    minX: -OCEAN_SKIRT_OUTER_HALF_SIZE,
    maxX: -OCEAN_SKIRT_HOLE_HALF_SIZE,
    minZ: -OCEAN_SKIRT_OUTER_HALF_SIZE,
    maxZ: OCEAN_SKIRT_OUTER_HALF_SIZE,
  },
  {
    minX: OCEAN_SKIRT_HOLE_HALF_SIZE,
    maxX: OCEAN_SKIRT_OUTER_HALF_SIZE,
    minZ: -OCEAN_SKIRT_OUTER_HALF_SIZE,
    maxZ: OCEAN_SKIRT_OUTER_HALF_SIZE,
  },
  {
    minX: -OCEAN_SKIRT_HOLE_HALF_SIZE,
    maxX: OCEAN_SKIRT_HOLE_HALF_SIZE,
    minZ: -OCEAN_SKIRT_OUTER_HALF_SIZE,
    maxZ: -OCEAN_SKIRT_HOLE_HALF_SIZE,
  },
  {
    minX: -OCEAN_SKIRT_HOLE_HALF_SIZE,
    maxX: OCEAN_SKIRT_HOLE_HALF_SIZE,
    minZ: OCEAN_SKIRT_HOLE_HALF_SIZE,
    maxZ: OCEAN_SKIRT_OUTER_HALF_SIZE,
  },
]

/** Build four exact rectangles around the detailed ocean's square seam. */
export function createOceanSkirtGeometry(): BufferGeometry {
  const positions: number[] = []
  const indices: number[] = []
  for (const quad of SKIRT_QUADS) {
    const first = positions.length / 3
    positions.push(
      quad.minX, 0, quad.minZ,
      quad.minX, 0, quad.maxZ,
      quad.maxX, 0, quad.maxZ,
      quad.maxX, 0, quad.minZ,
    )
    indices.push(first, first + 1, first + 2, first, first + 2, first + 3)
  }
  const geometry = new BufferGeometry()
  geometry.setAttribute(
    'position',
    new BufferAttribute(new Float32Array(positions), 3),
  )
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  geometry.computeBoundingBox()
  geometry.computeBoundingSphere()
  return geometry
}

export interface SubmergedOceanOptions {
  segments?: number
}

/**
 * Couple the three-cascade simulation to a detailed camera-following sheet
 * and a flat far skirt. The optical-side uniform stays submerged.
 */
export class SubmergedOcean {
  readonly simulation: WaveSim
  readonly inner: Mesh
  readonly outer: Mesh
  readonly submergedNode: Node<'float'>

  private readonly timeUniform = uniform(0)
  private readonly followStep: number

  constructor(
    scene: Scene,
    rng: Rng,
    options: SubmergedOceanOptions = {},
  ) {
    const segments = options.segments ?? 384
    this.followStep = INNER_SIZE / segments
    this.simulation = new WaveSim(rng)
    this.submergedNode = uniform(1)
    const sceneBackdrop = viewportTexture()
    const timeNode = this.timeUniform as unknown as Node<'float'>

    const innerGeometry = new PlaneGeometry(
      INNER_SIZE,
      INNER_SIZE,
      segments,
      segments,
    )
    innerGeometry.rotateX(-Math.PI / 2)
    this.inner = new Mesh(
      innerGeometry,
      createOceanSurfaceMaterial(this.simulation, timeNode, {
        detailed: true,
        edgeFadeHalfSize: OCEAN_INNER_HALF_SIZE,
        sceneBackdrop,
        submerged: this.submergedNode,
      }),
    )
    this.inner.frustumCulled = false
    this.inner.renderOrder = -100
    scene.add(this.inner)

    this.outer = new Mesh(
      createOceanSkirtGeometry(),
      createOceanSurfaceMaterial(this.simulation, timeNode, {
        detailed: false,
        sceneBackdrop,
        submerged: this.submergedNode,
      }),
    )
    this.outer.frustumCulled = false
    this.outer.renderOrder = -101
    scene.add(this.outer)
  }

  update(
    renderer: WebGPURenderer,
    cameraPosition: Vector3,
    elapsed: number,
    delta: number,
  ): void {
    this.timeUniform.value = elapsed
    this.simulation.update(renderer, elapsed, delta)
    const x = Math.round(cameraPosition.x / this.followStep) * this.followStep
    const z = Math.round(cameraPosition.z / this.followStep) * this.followStep
    this.inner.position.set(x, 0, z)
    this.outer.position.set(x, -OUTER_SINK, z)
  }

  dispose(scene: Scene): void {
    scene.remove(this.inner, this.outer)
    this.inner.geometry.dispose()
    this.outer.geometry.dispose()
    for (const material of [this.inner.material, this.outer.material]) {
      if (Array.isArray(material)) {
        for (const item of material) item.dispose()
      } else {
        material.dispose()
      }
    }
  }
}
