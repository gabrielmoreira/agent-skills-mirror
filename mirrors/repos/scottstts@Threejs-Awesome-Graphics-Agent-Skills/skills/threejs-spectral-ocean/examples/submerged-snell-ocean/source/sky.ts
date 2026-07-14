import { BackSide, Color, Mesh, SphereGeometry, Vector3 } from 'three'
import { MeshBasicNodeMaterial } from 'three/webgpu'
import type { Node } from 'three/webgpu'
import {
  Fn,
  dot,
  float,
  max,
  mix,
  normalize,
  positionLocal,
  pow,
  smoothstep,
  uniform,
  vec3,
} from 'three/tsl'

const SUN_ELEVATION = (42 * Math.PI) / 180
const SUN_AZIMUTH = (215 * Math.PI) / 180
const SUN_COS_RADIUS = Math.cos((0.266 * Math.PI) / 180)

export const sunDirection = new Vector3(
  Math.cos(SUN_ELEVATION) * Math.sin(SUN_AZIMUTH),
  Math.sin(SUN_ELEVATION),
  Math.cos(SUN_ELEVATION) * Math.cos(SUN_AZIMUTH),
).normalize()

export const sunColor = new Color(1, 0.925, 0.79)
export const SUN_LIGHT_INTENSITY = 3.4
export const sunDirectionUniform = uniform(sunDirection)
export const sunColorUniform = uniform(sunColor)

/** Shared linear-HDR sky used by the dome, water reflection, and Snell window. */
export const skyRadiance = Fn(
  ([direction, discStrength]: [Node<'vec3'>, Node<'float'>]) => {
    const ray = normalize(direction).toVar()
    const up = max(ray.y, 0)
    const zenith = vec3(0.05, 0.2, 0.5)
    const horizon = vec3(0.4, 0.54, 0.68)
    const seaMist = vec3(0.32, 0.43, 0.52)
    const gradient = mix(horizon, zenith, pow(up, 0.48))
    const radiance = mix(
      seaMist,
      gradient,
      smoothstep(-0.08, 0.02, ray.y),
    ).toVar()
    const sunAmount = max(dot(ray, sunDirectionUniform), 0).toVar()

    const radiusSquared = float(1)
      .sub(sunAmount)
      .div(1 - SUN_COS_RADIUS)
      .toVar()
    const inDisc = smoothstep(1, 0.96, radiusSquared)
    const limbCoordinate = float(1).sub(radiusSquared).max(0).sqrt()
    const limbDarkening = float(0.3)
      .add(limbCoordinate.mul(0.93))
      .sub(limbCoordinate.mul(limbCoordinate).mul(0.23))
    const disc = inDisc
      .mul(limbDarkening)
      .mul(discStrength)
      .mul(1500)
    const aureole = pow(sunAmount, 3000)
      .mul(20)
      .add(pow(sunAmount, 260).mul(1.7))
      .add(pow(sunAmount, 18).mul(0.16))
    return radiance.mul(1.25).add(sunColorUniform.mul(aureole.add(disc)))
  },
)

export function createSkyDome(radius = 3400): Mesh {
  const material = new MeshBasicNodeMaterial()
  material.colorNode = skyRadiance(normalize(positionLocal), float(1))
  material.side = BackSide
  material.depthWrite = false
  material.fog = false
  const dome = new Mesh(new SphereGeometry(radius, 48, 24), material)
  dome.frustumCulled = false
  dome.renderOrder = -100
  return dome
}
