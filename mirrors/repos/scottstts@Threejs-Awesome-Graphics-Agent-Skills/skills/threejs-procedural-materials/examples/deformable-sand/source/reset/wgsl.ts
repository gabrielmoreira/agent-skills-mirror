import { WAVE_RESET } from './effect'

export const waveShoreWgsl = `
const WAVE_SHORELINE_TILT = ${WAVE_RESET.shorelineTilt};
const WAVE_SHORELINE_AMPLITUDE = ${WAVE_RESET.shorelineAmplitude};
const WAVE_SHORELINE_FREQUENCY_A = ${WAVE_RESET.shorelineFrequencyA};
const WAVE_SHORELINE_FREQUENCY_B = ${WAVE_RESET.shorelineFrequencyB};
const WAVE_SHORELINE_FREQUENCY_C = ${WAVE_RESET.shorelineFrequencyC};
const WAVE_SHORELINE_SPEED_A = ${WAVE_RESET.shorelineSpeedA};
const WAVE_SHORELINE_SPEED_B = ${WAVE_RESET.shorelineSpeedB};
const WAVE_SHORELINE_SPEED_C = ${WAVE_RESET.shorelineSpeedC};
const WAVE_SHORELINE_BLEND = ${WAVE_RESET.shorelineBlend};

fn shorelineOffset(x: f32, time: f32) -> f32 {
  let breakerA = sin(x * WAVE_SHORELINE_FREQUENCY_A + time * WAVE_SHORELINE_SPEED_A);
  let breakerB = sin(x * WAVE_SHORELINE_FREQUENCY_B + time * WAVE_SHORELINE_SPEED_B + 1.7);
  let breakerC = sin(x * WAVE_SHORELINE_FREQUENCY_C - time * WAVE_SHORELINE_SPEED_C + 0.6);
  return x * WAVE_SHORELINE_TILT
    + WAVE_SHORELINE_AMPLITUDE * (breakerA + breakerB * WAVE_SHORELINE_BLEND)
    + WAVE_SHORELINE_AMPLITUDE * 0.55 * breakerC;
}

fn shorelineFront(x: f32, baseFront: f32, time: f32) -> f32 {
  return baseFront + shorelineOffset(x, time);
}
`
