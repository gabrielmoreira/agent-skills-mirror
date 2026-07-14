import {
  Fn,
  Loop,
  dot,
  float,
  floor,
  fract,
  mix,
  vec2,
  vec3,
} from 'three/tsl'
import type { Node } from 'three/webgpu'

type Vector2Node = Node<'vec2'>

export const hash21 = Fn(([point]: [Vector2Node]) => {
  const p3 = fract(vec3(point.x, point.y, point.x).mul(0.1031)).toVar()
  p3.addAssign(dot(p3, vec3(p3.y, p3.z, p3.x).add(33.33)))
  return fract(p3.x.add(p3.y).mul(p3.z))
})

export const valueNoise2 = Fn(([point]: [Vector2Node]) => {
  const cell = floor(point).toVar()
  const offset = fract(point).toVar()
  const smoothOffset = offset.mul(offset).mul(offset.mul(-2).add(3)).toVar()
  const a = hash21(cell)
  const b = hash21(cell.add(vec2(1, 0)))
  const c = hash21(cell.add(vec2(0, 1)))
  const d = hash21(cell.add(vec2(1, 1)))
  return mix(
    mix(a, b, smoothOffset.x),
    mix(c, d, smoothOffset.x),
    smoothOffset.y,
  )
})

/** Five-octave rotated fractional Brownian motion with output near [0, 1]. */
export const fbm2 = Fn(([point]: [Vector2Node]) => {
  const value = float(0).toVar()
  const amplitude = float(0.5).toVar()
  const samplePoint = point.toVar()
  Loop({ start: 0, end: 5 }, () => {
    value.addAssign(valueNoise2(samplePoint).mul(amplitude))
    const rotated = vec2(
      samplePoint.x.mul(0.8).sub(samplePoint.y.mul(0.6)),
      samplePoint.x.mul(0.6).add(samplePoint.y.mul(0.8)),
    )
    samplePoint.assign(rotated.mul(2.04))
    amplitude.mulAssign(0.5)
  })
  return value
})
