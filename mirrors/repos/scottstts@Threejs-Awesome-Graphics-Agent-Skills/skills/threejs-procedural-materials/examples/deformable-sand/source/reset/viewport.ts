import type { SandCamera } from '../render/camera'
import type { WaveResetViewport } from './effect'

export function waveResetViewport(camera: SandCamera): WaveResetViewport {
  // The camera has no roll/yaw, so the bottom screen edge maps to one constant
  // bed Y. That is the last visible row the retreat has to cross. Restrict the
  // shoreline search to the X interval that is actually visible on that row;
  // timing against the full 0.8 m simulation bed makes the wave disappear from
  // the viewport well before the audio ends, especially in portrait layouts.
  const bottomLeft = camera.screenToBed(0, 1, 1, 1)
  const bottomRight = camera.screenToBed(1, 1, 1, 1)
  const minX = Math.min(bottomLeft.x, bottomRight.x)
  const maxX = Math.max(bottomLeft.x, bottomRight.x)
  const nearY = Math.max(bottomLeft.y, bottomRight.y)
  return { minX, maxX, nearY }
}
