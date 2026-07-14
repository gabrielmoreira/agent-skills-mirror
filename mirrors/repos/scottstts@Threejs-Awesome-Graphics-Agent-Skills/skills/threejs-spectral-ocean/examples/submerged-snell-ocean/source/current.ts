import { Fn, cos, sin, vec3 } from 'three/tsl'
import type { Node } from 'three/webgpu'

/** Gentle shared curl field used to drift suspended particulates. */
export const currentFlow = Fn(
  ([position, time]: [Node<'vec3'>, Node<'float'>]) => {
    const x = position.x.mul(0.05)
    const z = position.z.mul(0.05)
    const first = sin(x.add(time.mul(0.11))).mul(
      cos(z.mul(1.3).sub(time.mul(0.07))),
    )
    const second = sin(z.mul(0.7).add(time.mul(0.05)).add(x.mul(0.4)))
    const third = cos(x.mul(1.7).sub(z.mul(0.6)).add(time.mul(0.09)))
    return vec3(
      first.mul(0.5).add(second.mul(0.2)),
      third.mul(0.12),
      second.mul(0.45).sub(first.mul(0.15)),
    )
  },
)
