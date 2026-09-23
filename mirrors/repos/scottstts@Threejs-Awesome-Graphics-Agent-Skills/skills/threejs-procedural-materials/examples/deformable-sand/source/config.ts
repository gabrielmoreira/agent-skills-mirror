export const SAND = {
  resolution: 512, extent: 0.8, depth: 0.032, floor: 0.003,
  repose: 0.625, dynamicRepose: 0.48, rate: 32,
  step: 1 / 120, maxSteps: 4, radius: 0.012, indentation: 0.02,
  impactSpeedStart: 0.5, impactSpeedFull: 1.2, impactIndentation: 0.01,
  impactEvacuation: 0.86, impactEjectionFraction: 0.075,
  impactParticleMassMin: 0.0000012, impactParticleMassMax: 0.0000032,
  airborneGrainRadius: 0.00016, airborneReferenceMass: 0.000004,
  airborneShadowResolution: 512, airborneShadowStrength: 1.7,
  particles: 16384, maxContacts: 8,
} as const

export type Point = { x: number; y: number }
export type Stroke = {
  from: Point
  to: Point
  velocity: Point
  radius: number
  pressure: number
  active: boolean
}
export const idleStroke = (): Stroke => ({
  from: { x: 0, y: 0 }, to: { x: 0, y: 0 }, velocity: { x: 0, y: 0 },
  radius: SAND.radius, pressure: 0, active: false,
})
