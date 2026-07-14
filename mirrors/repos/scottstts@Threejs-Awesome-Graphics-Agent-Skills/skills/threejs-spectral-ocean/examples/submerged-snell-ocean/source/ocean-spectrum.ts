import { DataTexture, FloatType, NearestFilter, RGBAFormat } from 'three'
import type { Rng } from './random'

export interface SeaState {
  gravity: number
  depth: number
  windSpeed: number
  /** Direction in which the wind sea travels, in world-space radians. */
  windAzimuth: number
  fetch: number
  localScale: number
  swellScale: number
  swellAzimuth: number
  swellOmega: number
  shortWaveFade: number
}

export const DEFAULT_SEA_STATE: SeaState = {
  gravity: 9.81,
  depth: 500,
  windSpeed: 8.5,
  windAzimuth: (205 * Math.PI) / 180,
  fetch: 300_000,
  localScale: 1,
  swellScale: 0.45,
  swellAzimuth: (188 * Math.PI) / 180,
  swellOmega: 0.62,
  shortWaveFade: 0.003,
}

export interface CascadeBand {
  patchLength: number
  cutoffLow: number
  cutoffHigh: number
}

function jonswapTma(omega: number, sea: SeaState): number {
  const { gravity, windSpeed, fetch, depth } = sea
  if (omega <= 0) return 0
  const alpha = 0.076 * Math.pow((gravity * fetch) / (windSpeed * windSpeed), -0.22)
  const peakOmega = 22 * Math.pow((windSpeed * fetch) / (gravity * gravity), -0.33)
  const sigma = omega <= peakOmega ? 0.07 : 0.09
  const peakDistance = omega - peakOmega
  const resonance = Math.exp(
    -(peakDistance * peakDistance) / (2 * sigma * sigma * peakOmega * peakOmega),
  )
  const jonswap =
    ((alpha * gravity * gravity) / omega ** 5) *
    Math.exp(-1.25 * Math.pow(peakOmega / omega, 4)) *
    Math.pow(3.3, resonance)

  const normalizedDepthFrequency = omega * Math.sqrt(depth / gravity)
  let finiteDepth: number
  if (normalizedDepthFrequency <= 1) {
    finiteDepth = 0.5 * normalizedDepthFrequency * normalizedDepthFrequency
  } else if (normalizedDepthFrequency < 2) {
    finiteDepth = 1 - 0.5 * (2 - normalizedDepthFrequency) ** 2
  } else {
    finiteDepth = 1
  }
  return jonswap * finiteDepth
}

function wrapAngle(angle: number): number {
  while (angle > Math.PI) angle -= Math.PI * 2
  while (angle < -Math.PI) angle += Math.PI * 2
  return angle
}

function spreading(delta: number, omegaOverPeak: number): number {
  const cosine = Math.max(Math.cos(delta * 0.5), 0)
  const broadLobe = cosine * cosine
  const power = 4 + 24 * Math.min(1, Math.max(0, omegaOverPeak - 0.4))
  const focusedLobe = Math.pow(cosine, power)
  return (broadLobe * 0.35 + focusedLobe * 0.65) / Math.PI
}

/** Build a conjugate-packed JONSWAP × TMA directional spectrum. */
export function createSpectrumTexture(
  rng: Rng,
  band: CascadeBand,
  sea: SeaState,
  resolution: number,
): DataTexture {
  const n = resolution
  const deltaK = (Math.PI * 2) / band.patchLength
  const peakOmega = 22 * Math.pow(
    (sea.windSpeed * sea.fetch) / (sea.gravity * sea.gravity),
    -0.33,
  )
  const h0 = new Float32Array(n * n * 2)

  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      const kx = (x - n / 2) * deltaK
      const kz = (y - n / 2) * deltaK
      const kLength = Math.hypot(kx, kz)
      const offset = (y * n + x) * 2
      const inBand = kLength >= band.cutoffLow && kLength <= band.cutoffHigh

      if (!inBand || kLength < 1e-6) {
        h0[offset] = 0
        h0[offset + 1] = 0
        rng.next()
        rng.next()
        continue
      }

      const safeK = Math.max(kLength, band.cutoffLow > 0 ? band.cutoffLow : 1e-4)
      const tanhArgument = Math.min(safeK * sea.depth, 20)
      const tanhKd = Math.tanh(tanhArgument)
      const omega = Math.sqrt(sea.gravity * safeK * tanhKd)
      const sechSquared = tanhArgument >= 20 ? 0 : 1 / Math.cosh(tanhArgument) ** 2
      const dOmegaDk = Math.max(
        (
          sea.gravity * tanhKd +
          sea.gravity * safeK * sea.depth * sechSquared
        ) / (2 * omega),
        1e-6,
      )

      const theta = Math.atan2(kz, kx)
      const local =
        jonswapTma(omega, sea) *
        spreading(wrapAngle(theta - sea.windAzimuth), omega / peakOmega) *
        sea.localScale
      const swell =
        sea.swellScale *
        Math.exp(-(((omega - sea.swellOmega) / 0.12) ** 2)) *
        Math.pow(
          Math.max(Math.cos(wrapAngle(theta - sea.swellAzimuth) * 0.5), 0),
          48,
        ) *
        0.9
      const energy =
        (local + swell) *
        Math.exp(
          -(sea.shortWaveFade * sea.shortWaveFade) * kLength * kLength,
        )
      const amplitude = Math.sqrt(
        ((energy * 2 * dOmegaDk) / safeK) * deltaK * deltaK,
      )

      const u1 = Math.max(rng.next(), 1e-9)
      const u2 = rng.next()
      const magnitude = Math.sqrt(-2 * Math.log(u1))
      h0[offset] = (magnitude * Math.cos(Math.PI * 2 * u2) * amplitude) / Math.SQRT2
      h0[offset + 1] =
        (magnitude * Math.sin(Math.PI * 2 * u2) * amplitude) / Math.SQRT2
    }
  }

  const packed = new Float32Array(n * n * 4)
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      const mirrorX = (n - x) % n
      const mirrorY = (n - y) % n
      const offset = (y * n + x) * 2
      const mirrorOffset = (mirrorY * n + mirrorX) * 2
      const packedOffset = (y * n + x) * 4
      packed[packedOffset] = h0[offset]
      packed[packedOffset + 1] = h0[offset + 1]
      packed[packedOffset + 2] = h0[mirrorOffset]
      packed[packedOffset + 3] = -h0[mirrorOffset + 1]
    }
  }

  const texture = new DataTexture(packed, n, n, RGBAFormat, FloatType)
  texture.minFilter = NearestFilter
  texture.magFilter = NearestFilter
  texture.generateMipmaps = false
  texture.needsUpdate = true
  return texture
}

/** Partition the wavenumber domain into disjoint cascade bands. */
export function cascadeBands(
  patchLengths: number[],
  boundaryFactor: number,
): CascadeBand[] {
  const handoff = (index: number) =>
    ((Math.PI * 2) / patchLengths[index]) * boundaryFactor
  return patchLengths.map((patchLength, index) => ({
    patchLength,
    cutoffLow: index === 0 ? 1e-4 : handoff(index),
    cutoffHigh:
      index === patchLengths.length - 1 ? 1e4 : handoff(index + 1),
  }))
}
