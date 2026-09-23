export {
  GRID,
  ROCKS,
  WAVES,
  bedHeight,
  collisionPosition,
  rockTop,
  terrainHeight,
} from "./source/coast.js";
export { makeNoiseTexture } from "./source/noise.js";
export { createShading } from "./source/shading.js";
export { ShoreSimulation } from "./source/simulation.js";
export { ContactSpray, sampleField } from "./source/spray.js";
export { packSurface, reconstructSurface } from "./source/surface.js";
export { buildWorld, gridGeometry } from "./source/world.js";
export { enableSolverAcceleration } from "./source/solver-accelerator.js";
