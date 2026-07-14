import { HalfFloatType, LinearFilter, RepeatWrapping } from 'three'
import { StorageTexture } from 'three/webgpu'
import type { ComputeNode, WebGPURenderer } from 'three/webgpu'
import {
  Fn,
  float,
  instanceIndex,
  int,
  ivec2,
  max,
  min,
  texture,
  textureLoad,
  textureStore,
  uint,
  uniform,
  vec2,
  vec4,
} from 'three/tsl'
import type { Rng } from './random'
import { createFrequencyTexture, PackedIFFT } from './fft-compute'
import {
  cascadeBands,
  createSpectrumTexture,
  DEFAULT_SEA_STATE,
} from './ocean-spectrum'
import type { SeaState } from './ocean-spectrum'

export const OCEAN_PRESET = {
  resolution: 256,
  patchLengths: [250, 17, 5],
  boundaryFactor: 6,
  choppiness: 1.3,
  foamRecovery: 0.35,
  amplitude: 0.35,
} as const

interface Cascade {
  ifft: PackedIFFT
  evolve: ComputeNode
  assemble: [ComputeNode, ComputeNode]
  clear: [ComputeNode, ComputeNode]
  displacementMaps: [StorageTexture, StorageTexture]
  derivativesMap: StorageTexture
}

function createMapTexture(resolution: number): StorageTexture {
  const map = new StorageTexture(resolution, resolution)
  map.type = HalfFloatType
  map.wrapS = RepeatWrapping
  map.wrapT = RepeatWrapping
  map.minFilter = LinearFilter
  map.magFilter = LinearFilter
  map.generateMipmaps = false
  return map
}

/**
 * Three directional cascades evolve height and horizontal displacement,
 * transform both packed fields, and assemble derivatives, Jacobians, and
 * persistent foam history.
 */
export class WaveSim {
  readonly patchLengths: number[]
  readonly displacementNodes: ReturnType<typeof texture>[]
  readonly derivativeNodes: ReturnType<typeof texture>[]

  private readonly cascades: Cascade[]
  private readonly timeUniform = uniform(0)
  private readonly dtUniform = uniform(1 / 60)
  private current = 0
  private initialized = false

  constructor(rng: Rng, sea: SeaState = DEFAULT_SEA_STATE) {
    const {
      resolution,
      patchLengths,
      boundaryFactor,
      choppiness,
      foamRecovery,
      amplitude,
    } = OCEAN_PRESET
    this.patchLengths = [...patchLengths]
    const logN = Math.log2(resolution)
    const mask = uint(resolution - 1)
    const shift = uint(logN)
    const bands = cascadeBands(this.patchLengths, boundaryFactor)

    const cellOf = () => {
      const x = int(instanceIndex.bitAnd(mask))
      const y = int(instanceIndex.shiftRight(shift))
      return { x, y, cell: ivec2(x, y) }
    }

    this.cascades = bands.map((band, index) => {
      const spectrum = createSpectrumTexture(
        rng.fork(`ocean-cascade-${index}`),
        band,
        sea,
        resolution,
      )
      const frequencyPing = createFrequencyTexture(resolution)
      const frequencyPong = createFrequencyTexture(resolution)
      const ifft = new PackedIFFT(frequencyPing, frequencyPong, resolution)
      const displacementMaps: [StorageTexture, StorageTexture] = [
        createMapTexture(resolution),
        createMapTexture(resolution),
      ]
      const derivativesMap = createMapTexture(resolution)
      const twoPiOverPatch = (Math.PI * 2) / band.patchLength

      const evolve = Fn(() => {
        const { x, y, cell } = cellOf()
        const initial = textureLoad(texture(spectrum), cell)
        const centered = vec2(
          float(x).sub(resolution / 2),
          float(y).sub(resolution / 2),
        )
        const k = centered.mul(twoPiOverPatch)
        const kLength = max(k.length(), 1e-4)
        const omega = k.length()
          .mul(float(sea.gravity))
          .mul(min(kLength.mul(sea.depth), 20).tanh())
          .sqrt()
        const phase = omega.mul(this.timeUniform)
        const phaseCosine = phase.cos()
        const phaseSine = phase.sin()
        const height = vec2(
          initial.x
            .mul(phaseCosine)
            .sub(initial.y.mul(phaseSine))
            .add(
              initial.z
                .mul(phaseCosine)
                .sub(initial.w.mul(phaseSine.negate())),
            ),
          initial.x
            .mul(phaseSine)
            .add(initial.y.mul(phaseCosine))
            .add(
              initial.z
                .mul(phaseSine.negate())
                .add(initial.w.mul(phaseCosine)),
            ),
        ).mul(amplitude)
        const imaginaryHeight = vec2(height.y.negate(), height.x)
        const displacementX = imaginaryHeight.mul(k.x.div(kLength))
        const displacementZ = imaginaryHeight.mul(k.y.div(kLength))
        const horizontal = vec2(
          displacementX.x.sub(displacementZ.y),
          displacementX.y.add(displacementZ.x),
        )
        textureStore(frequencyPing, cell, vec4(height, horizontal))
      })().compute(resolution * resolution)

      const spatial = ifft.output
      const inverseSpacing = resolution / (2 * band.patchLength)
      const makeAssemble = (
        previous: StorageTexture,
        next: StorageTexture,
      ): ComputeNode =>
        Fn(() => {
          const { x, y, cell } = cellOf()
          const parity = float(
            int(instanceIndex.bitAnd(mask))
              .add(int(instanceIndex.shiftRight(shift)))
              .bitAnd(int(1)),
          )
          const sign = float(1).sub(parity.mul(2))
          const neighborSign = sign.negate()
          const xPlus = int(uint(x.add(1)).bitAnd(mask))
          const xMinus = int(uint(x.add(resolution - 1)).bitAnd(mask))
          const yPlus = int(uint(y.add(1)).bitAnd(mask))
          const yMinus = int(uint(y.add(resolution - 1)).bitAnd(mask))

          const center = textureLoad(texture(spatial), cell)
          const right = textureLoad(texture(spatial), ivec2(xPlus, y)).mul(neighborSign)
          const left = textureLoad(texture(spatial), ivec2(xMinus, y)).mul(neighborSign)
          const up = textureLoad(texture(spatial), ivec2(x, yPlus)).mul(neighborSign)
          const down = textureLoad(texture(spatial), ivec2(x, yMinus)).mul(neighborSign)

          const height = center.x.mul(sign)
          const horizontal = center.zw.mul(sign)
          const slopeX = right.x.sub(left.x).mul(inverseSpacing)
          const slopeZ = up.x.sub(down.x).mul(inverseSpacing)
          const dDxDx = right.z.sub(left.z).mul(inverseSpacing)
          const dDzDz = up.w.sub(down.w).mul(inverseSpacing)
          const dDxDz = up.z.sub(down.z).mul(inverseSpacing)
          const dDzDx = right.w.sub(left.w).mul(inverseSpacing)

          const jxx = float(1).add(dDxDx.mul(choppiness))
          const jzz = float(1).add(dDzDz.mul(choppiness))
          const jxz = dDxDz.add(dDzDx).mul(0.5).mul(choppiness)
          const jacobian = jxx.mul(jzz).sub(jxz.mul(jxz))
          const previousHistory = textureLoad(texture(previous), cell).w
          const recovered = previousHistory.add(
            this.dtUniform.mul(foamRecovery).div(max(jacobian, 0.5)),
          )
          const history = min(min(jacobian, recovered), 2)

          textureStore(
            next,
            cell,
            vec4(
              horizontal.x.mul(choppiness),
              height,
              horizontal.y.mul(choppiness),
              history,
            ),
          )
          textureStore(
            derivativesMap,
            cell,
            vec4(
              slopeX,
              slopeZ,
              dDxDx.mul(choppiness),
              dDzDz.mul(choppiness),
            ),
          )
        })().compute(resolution * resolution)

      const makeClear = (target: StorageTexture): ComputeNode =>
        Fn(() => {
          const { cell } = cellOf()
          textureStore(target, cell, vec4(0, 0, 0, 1))
        })().compute(resolution * resolution)

      return {
        ifft,
        evolve,
        assemble: [
          makeAssemble(displacementMaps[0], displacementMaps[1]),
          makeAssemble(displacementMaps[1], displacementMaps[0]),
        ],
        clear: [makeClear(displacementMaps[0]), makeClear(displacementMaps[1])],
        displacementMaps,
        derivativesMap,
      }
    })

    this.displacementNodes = this.cascades.map((cascade) =>
      texture(cascade.displacementMaps[0]),
    )
    this.derivativeNodes = this.cascades.map((cascade) =>
      texture(cascade.derivativesMap),
    )
  }

  private ensureInitialized(renderer: WebGPURenderer): void {
    if (this.initialized) return
    this.initialized = true
    for (const cascade of this.cascades) {
      renderer.compute(cascade.clear[0])
      renderer.compute(cascade.clear[1])
    }
  }

  update(renderer: WebGPURenderer, elapsed: number, delta: number): void {
    this.ensureInitialized(renderer)
    this.timeUniform.value = elapsed
    this.dtUniform.value = Math.min(delta, 0.1)
    renderer.compute(this.cascades.map((cascade) => cascade.evolve))

    const stageCount = this.cascades[0].ifft.stages.length
    for (let stage = 0; stage < stageCount; stage++) {
      renderer.compute(
        this.cascades.map((cascade) => cascade.ifft.stages[stage]),
      )
    }

    const parity = this.current
    renderer.compute(
      this.cascades.map((cascade) => cascade.assemble[parity]),
    )
    this.current = 1 - this.current

    for (let index = 0; index < this.cascades.length; index++) {
      this.displacementNodes[index].value =
        this.cascades[index].displacementMaps[this.current === 0 ? 0 : 1]
    }
  }
}
