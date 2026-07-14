import { DataTexture, FloatType, NearestFilter, RGBAFormat } from 'three'
import { StorageBufferAttribute, StorageTexture } from 'three/webgpu'
import type { ComputeNode, Node, WebGPURenderer } from 'three/webgpu'
import {
  Fn,
  float,
  instanceIndex,
  int,
  ivec2,
  localId,
  select,
  storage,
  texture,
  textureLoad,
  textureStore,
  uint,
  vec2,
  vec4,
  workgroupArray,
  workgroupBarrier,
  workgroupId,
} from 'three/tsl'

export function createFrequencyTexture(resolution: number): StorageTexture {
  const texture = new StorageTexture(resolution, resolution)
  texture.type = FloatType
  texture.minFilter = NearestFilter
  texture.magFilter = NearestFilter
  texture.generateMipmaps = false
  return texture
}

/**
 * Transform two packed complex fields through a radix-2 inverse FFT. Each
 * 256-point row or column stays in one workgroup with explicit barriers.
 */
export class PackedIFFT {
  readonly stages: ComputeNode[] = []
  readonly output: StorageTexture

  constructor(ping: StorageTexture, pong: StorageTexture, resolution: number) {
    const logN = Math.log2(resolution)
    if (!Number.isInteger(logN) || resolution > 256) {
      throw new Error(
        `PackedIFFT requires a power-of-two workgroup size up to 256; received ${resolution}`,
      )
    }

    const makeAxis = (
      inputTexture: StorageTexture,
      outputTexture: StorageTexture,
      horizontal: boolean,
    ) => {
      const shared = workgroupArray('vec4', resolution) as unknown as {
        element(index: Node<'uint'>): Node<'vec4'>
      }

      return Fn(() => {
        const lane = localId.x.toVar()
        const line = int(workgroupId.x)
        const reversed = uint(0).toVar()
        const remaining = lane.toVar()
        for (let bit = 0; bit < logN; bit++) {
          reversed.assign(reversed.shiftLeft(1).bitOr(remaining.bitAnd(1)))
          remaining.assign(remaining.shiftRight(1))
        }

        const input = horizontal
          ? ivec2(int(reversed), line)
          : ivec2(line, int(reversed))
        shared.element(lane).assign(textureLoad(texture(inputTexture), input))
        workgroupBarrier()

        for (let stage = 0; stage < logN; stage++) {
          const groupSize = uint(1 << (stage + 1))
          const halfSize = uint(1 << stage)
          const local = lane.mod(groupSize)
          const top = local.lessThan(halfSize)
          const offset = local.mod(halfSize)
          const indexA = select(top, lane, lane.sub(halfSize))
          const indexB = indexA.add(halfSize)
          const a = shared.element(indexA).toVar()
          const b = shared.element(indexB).toVar()
          const angle = float(offset).mul((Math.PI * 2) / (1 << (stage + 1)))
          const sign = select(top, float(1), float(-1))
          const twiddle = vec2(angle.cos(), angle.sin()).mul(sign)
          const fieldOne = a.xy.add(
            vec2(
              b.x.mul(twiddle.x).sub(b.y.mul(twiddle.y)),
              b.x.mul(twiddle.y).add(b.y.mul(twiddle.x)),
            ),
          )
          const fieldTwo = a.zw.add(
            vec2(
              b.z.mul(twiddle.x).sub(b.w.mul(twiddle.y)),
              b.z.mul(twiddle.y).add(b.w.mul(twiddle.x)),
            ),
          )
          workgroupBarrier()
          shared.element(lane).assign(vec4(fieldOne, fieldTwo))
          workgroupBarrier()
        }

        const output = horizontal
          ? ivec2(int(lane), line)
          : ivec2(line, int(lane))
        textureStore(outputTexture, output, shared.element(lane))
      })().compute(resolution * resolution, [resolution])
    }

    this.stages.push(makeAxis(ping, pong, true))
    this.stages.push(makeAxis(pong, ping, false))
    this.output = ping
  }
}

/** Validate a centered DC impulse and one-bin complex sinusoid. */
export async function runFftSelfTest(
  renderer: WebGPURenderer,
  resolution = 64,
): Promise<{ maxErrorConstant: number; maxErrorWave: number }> {
  const ping = createFrequencyTexture(resolution)
  const pong = createFrequencyTexture(resolution)
  const ifft = new PackedIFFT(ping, pong, resolution)
  const readBuffer = new StorageBufferAttribute(
    new Float32Array(resolution * resolution * 4),
    4,
  )

  const runCase = async (
    impulseX: number,
    impulseY: number,
  ): Promise<Float32Array> => {
    const data = new Float32Array(resolution * resolution * 4)
    data[(impulseY * resolution + impulseX) * 4] = 1
    const input = new DataTexture(
      data,
      resolution,
      resolution,
      RGBAFormat,
      FloatType,
    )
    input.minFilter = NearestFilter
    input.magFilter = NearestFilter
    input.needsUpdate = true

    const mask = uint(resolution - 1)
    const shift = uint(Math.log2(resolution))
    const upload = Fn(() => {
      const x = int(instanceIndex.bitAnd(mask))
      const y = int(instanceIndex.shiftRight(shift))
      const cell = ivec2(x, y)
      textureStore(ping, cell, textureLoad(texture(input), cell))
    })().compute(resolution * resolution)
    renderer.compute(upload)
    for (const stage of ifft.stages) renderer.compute(stage)

    const download = Fn(() => {
      const x = int(instanceIndex.bitAnd(mask))
      const y = int(instanceIndex.shiftRight(shift))
      const value = textureLoad(texture(ifft.output), ivec2(x, y))
      storage(readBuffer, 'vec4', resolution * resolution)
        .element(instanceIndex)
        .assign(value)
    })().compute(resolution * resolution)
    renderer.compute(download)

    const pixels = new Float32Array(await renderer.getArrayBufferAsync(readBuffer))
    input.dispose()
    return pixels
  }

  const constant = await runCase(resolution / 2, resolution / 2)
  let maxErrorConstant = 0
  for (let y = 0; y < resolution; y++) {
    for (let x = 0; x < resolution; x++) {
      const sign = (x + y) % 2 === 0 ? 1 : -1
      const real = constant[(y * resolution + x) * 4] * sign
      const imaginary = constant[(y * resolution + x) * 4 + 1] * sign
      maxErrorConstant = Math.max(
        maxErrorConstant,
        Math.abs(real - 1),
        Math.abs(imaginary),
      )
    }
  }

  const wave = await runCase(resolution / 2 + 1, resolution / 2)
  let maxErrorWave = 0
  for (let y = 0; y < resolution; y++) {
    for (let x = 0; x < resolution; x++) {
      const sign = (x + y) % 2 === 0 ? 1 : -1
      const real = wave[(y * resolution + x) * 4] * sign
      const imaginary = wave[(y * resolution + x) * 4 + 1] * sign
      const phase = (Math.PI * 2 * x) / resolution
      maxErrorWave = Math.max(
        maxErrorWave,
        Math.abs(real - Math.cos(phase)),
        Math.abs(imaginary - Math.sin(phase)),
      )
    }
  }

  return { maxErrorConstant, maxErrorWave }
}
