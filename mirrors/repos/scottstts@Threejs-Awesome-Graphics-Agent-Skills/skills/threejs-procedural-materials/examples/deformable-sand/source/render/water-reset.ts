import { SAND } from '../config'
import { WAVE_RESET } from '../reset/effect'
import { waveShoreWgsl } from '../reset/wgsl'

export const WATER_FIELD_RESOLUTION = SAND.resolution
export const WATER_FIELD_FORMAT: GPUTextureFormat = 'rgba16float'
export const WATER_CAUSTIC_FORMAT: GPUTextureFormat = 'r16float'

const WATER_FIELD_TEXEL = SAND.extent / WATER_FIELD_RESOLUTION

const waterCommonWgsl = `
${waveShoreWgsl}
struct OverlayView {
  eye: vec4f,
  forward: vec4f,
  right: vec4f,
  up: vec4f,
  waveFront: vec4f,
  waveShape: vec4f,
  waveLook: vec4f,
}
struct WaveSample {
  height: f32,
  slope: vec2f,
  displacement: vec2f,
}
struct VertexOutput {
  @builtin(position) clip: vec4f,
  @location(0) uv: vec2f,
}
@group(0) @binding(0) var<uniform> overlay: OverlayView;
@vertex fn vertex(@builtin(vertex_index) index: u32) -> VertexOutput {
  let positions = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
  let clip = positions[index];
  var output: VertexOutput;
  output.clip = vec4f(clip, 0.0, 1.0);
  output.uv = clip * vec2f(0.5, -0.5) + vec2f(0.5);
  return output;
}
fn hash21(point: vec2f) -> f32 {
  let p3 = fract(vec3f(point.x, point.y, point.x) * vec3f(0.1031, 0.1030, 0.0973));
  let q = p3 + dot(p3, p3.yzx + vec3f(33.33));
  return fract((q.x + q.y) * q.z);
}
fn valueNoise(point: vec2f) -> f32 {
  let cell = floor(point);
  let blend = fract(point);
  let curve = blend * blend * (3.0 - 2.0 * blend);
  let a = hash21(cell);
  let b = hash21(cell + vec2f(1.0, 0.0));
  let c = hash21(cell + vec2f(0.0, 1.0));
  let d = hash21(cell + vec2f(1.0, 1.0));
  return mix(mix(a, b, curve.x), mix(c, d, curve.x), curve.y);
}
fn fbm(point: vec2f) -> f32 {
  var value = 0.0;
  var amplitude = 0.5;
  var position = point;
  for (var octave = 0; octave < 4; octave++) {
    value += valueNoise(position) * amplitude;
    position = mat2x2f(1.72, 1.14, -1.14, 1.72) * position + vec2f(13.7, 9.2);
    amplitude *= 0.5;
  }
  return value;
}
fn fieldUv(point: vec2f) -> vec2f {
  let halfExtent = max(overlay.waveFront.w, 0.0001);
  return clamp(point / (halfExtent * 2.0) + vec2f(0.5), vec2f(0.001), vec2f(0.999));
}
fn fieldWorld(uv: vec2f) -> vec2f {
  let halfExtent = overlay.waveFront.w;
  return (uv * 2.0 - vec2f(1.0)) * halfExtent;
}
fn filmDepth(waterDistance: f32) -> f32 {
  let entry = smoothstep(-overlay.waveShape.x * 0.08, overlay.waveShape.x * 1.25, waterDistance);
  let body = smoothstep(overlay.waveShape.x * 0.25, 0.17, waterDistance);
  return entry * mix(0.0010, 0.034, body);
}
fn frontCrest(waterDistance: f32) -> f32 {
  let center = overlay.waveShape.y * 0.46;
  let width = max(overlay.waveShape.y * 0.70, 0.008);
  let coordinate = (waterDistance - center) / width;
  return exp(-coordinate * coordinate * 2.2) * 0.0044;
}
`

export const waterFieldShader = `
${waterCommonWgsl}
struct FieldOutput {
  @location(0) surface: vec4f,
  @location(1) motion: vec4f,
}
fn packetEnvelope(point: vec2f, direction: vec2f, envelopeScale: f32, seed: f32, time: f32) -> f32 {
  let cross = vec2f(-direction.y, direction.x);
  let along = dot(point, direction) / envelopeScale;
  let across = dot(point, cross) / (envelopeScale * 0.82);
  let broad = fbm(vec2f(along * 0.55 + seed * 3.7 + time * 0.013, across * 0.62 - seed * 2.9));
  let detail = fbm(vec2f(along * 1.45 - seed * 5.3 - time * 0.018, across * 1.18 + seed * 4.1));
  let density = broad * 0.72 + detail * 0.28;
  return mix(0.74, 1.34, smoothstep(0.24, 0.82, density));
}
fn gerstnerPacket(
  point: vec2f,
  directionRaw: vec2f,
  wavelength: f32,
  amplitude: f32,
  speed: f32,
  steepness: f32,
  phaseOffset: f32,
  envelopeScale: f32,
  time: f32
) -> WaveSample {
  let direction = normalize(directionRaw);
  let cross = vec2f(-direction.y, direction.x);
  let envelope = packetEnvelope(point, direction, envelopeScale, phaseOffset, time * speed);
  let warp = vec2f(
    fbm(point * (0.52 / envelopeScale) + vec2f(phaseOffset * 2.1, -time * 0.022)),
    fbm(point * (0.47 / envelopeScale) + vec2f(-phaseOffset * 1.3, time * 0.018))
  ) - vec2f(0.5);
  let warpedPoint = point + warp * (wavelength * 0.26);
  let along = dot(warpedPoint, direction);
  let across = dot(warpedPoint, cross);
  let wavenumber = 6.28318530718 / wavelength;
  let sideband = sin(across * wavenumber * 0.38 + phaseOffset * 1.7) * 0.36;
  let phase = along * wavenumber - time * speed * wavenumber + phaseOffset + sideband;
  let sinePhase = sin(phase);
  let cosinePhase = cos(phase);
  let harmonic2 = sin(phase * 2.0 + 0.45);
  let harmonic3 = sin(phase * 3.0 - 1.10);
  let harmonic2d = cos(phase * 2.0 + 0.45);
  let harmonic3d = cos(phase * 3.0 - 1.10);
  let shapedAmplitude = amplitude * envelope;
  let height = shapedAmplitude * (sinePhase + harmonic2 * 0.18 + harmonic3 * 0.07);
  let slopeAlong = shapedAmplitude * wavenumber * (cosinePhase + harmonic2d * 0.36 + harmonic3d * 0.21);
  let slopeAcross = shapedAmplitude * wavenumber * 0.18 * cos(across * wavenumber * 0.65 + phaseOffset * 1.9);
  let displacement = direction * (shapedAmplitude * steepness * (cosinePhase + harmonic2d * 0.18)) * mix(0.78, 1.22, envelope - 0.74);
  return WaveSample(height, direction * slopeAlong + cross * slopeAcross, displacement);
}
fn waveField(point: vec2f, waterDistance: f32, time: f32) -> WaveSample {
  let shoreGain = mix(1.72, 0.84, smoothstep(-0.01, 0.20, waterDistance));
  let bodyGain = mix(1.0, 0.88, smoothstep(0.04, 0.20, waterDistance));
  let rippleGain = mix(0.96, 1.15, clamp(overlay.waveLook.z / 24.0, 0.75, 1.45));
  let drift = max(overlay.waveLook.w, 0.05) / 0.48;
  let coastWarp = vec2f(
    fbm(point * 0.85 + vec2f(time * 0.018, -time * 0.011)),
    fbm(point * 0.79 + vec2f(-time * 0.014, time * 0.016))
  ) - vec2f(0.5);
  let drivenPoint = point + coastWarp * vec2f(0.030, 0.042);

  let g0 = gerstnerPacket(drivenPoint, vec2f(0.10, -1.0), 0.340, 0.00185 * shoreGain, 0.55 * drift, 0.74, 0.0, 0.82, time);
  let g1 = gerstnerPacket(drivenPoint, vec2f(-0.22, -0.98), 0.235, 0.00135 * shoreGain, 0.50 * drift, 0.69, 1.7, 0.58, time);
  let g2 = gerstnerPacket(drivenPoint, vec2f(0.31, -0.95), 0.168, 0.00100 * shoreGain, 0.44 * drift, 0.63, 2.9, 0.42, time);
  let g3 = gerstnerPacket(drivenPoint, vec2f(0.83, -0.56), 0.112, 0.00064 * bodyGain, 0.38 * drift, 0.55, 4.4, 0.34, time);
  let c0 = gerstnerPacket(drivenPoint, vec2f(0.93, 0.38), 0.076, 0.00034 * rippleGain, 0.34 * drift, 0.34, 5.2, 0.24, time);
  let c1 = gerstnerPacket(drivenPoint, vec2f(0.70, -0.72), 0.061, 0.00028 * rippleGain, 0.31 * drift, 0.31, 2.4, 0.20, time);
  let c2 = gerstnerPacket(drivenPoint, vec2f(-0.13, 0.99), 0.050, 0.00022 * rippleGain, 0.29 * drift, 0.29, 4.5, 0.17, time);
  let c3 = gerstnerPacket(drivenPoint, vec2f(-0.83, 0.56), 0.041, 0.00017 * rippleGain, 0.26 * drift, 0.27, 0.9, 0.14, time);
  let c4 = gerstnerPacket(drivenPoint, vec2f(-0.55, -0.84), 0.034, 0.00013 * rippleGain, 0.24 * drift, 0.24, 2.9, 0.12, time);

  return WaveSample(
    g0.height + g1.height + g2.height + g3.height + c0.height + c1.height + c2.height + c3.height + c4.height,
    g0.slope + g1.slope + g2.slope + g3.slope + c0.slope + c1.slope + c2.slope + c3.slope + c4.slope,
    g0.displacement + g1.displacement + g2.displacement + g3.displacement + c0.displacement + c1.displacement + c2.displacement + c3.displacement + c4.displacement
  );
}
fn foamCoverage(point: vec2f, waterDistance: f32, time: f32) -> f32 {
  let foamReach = max(overlay.waveShape.y * 1.6, overlay.waveShape.z * 2.55);
  if (waterDistance < -overlay.waveShape.y * 1.1 || waterDistance > foamReach) { return 0.0; }
  let advect = vec2f(time * 0.19, -time * 0.58);
  let broadBreakup = fbm(point * 11.0 + advect) - 0.5;
  let fineBreakup = fbm(point * 27.0 + vec2f(-time * 0.44, time * 0.21)) - 0.5;
  let warpedDistance = waterDistance + (broadBreakup * 0.78 + fineBreakup * 0.22) * overlay.waveShape.y * 0.92;
  let frontCenter = overlay.waveShape.y * 0.20;
  let frontBand = 1.0 - smoothstep(overlay.waveShape.y * 0.18, overlay.waveShape.y * 1.08, abs(warpedDistance - frontCenter));
  let trail = smoothstep(0.0, overlay.waveShape.z * 0.30, warpedDistance)
    * (1.0 - smoothstep(overlay.waveShape.z * 0.56, overlay.waveShape.z * 2.45, warpedDistance));
  let frothA = smoothstep(0.47, 0.74, fbm(point * 19.0 + vec2f(time * 0.26, -time * 0.39)));
  let frothB = smoothstep(0.50, 0.78, fbm(point * 38.0 + vec2f(-time * 0.63, time * 0.31)));
  let stringers = smoothstep(0.58, 0.80, fbm(vec2f(point.x * 10.0, point.y * 26.0) + vec2f(time * 0.10, -time * 0.72)));
  let micro = smoothstep(0.78, 0.92, valueNoise(point * 121.0 + advect * 4.2));
  let frontFroth = frontBand * (0.56 + frothA * 0.32 + frothB * 0.20);
  let trailingFroth = trail * (frothA * 0.36 + frothB * 0.24 + stringers * 0.22 + micro * 0.08);
  return clamp(frontFroth + trailingFroth, 0.0, 1.0);
}
@fragment fn fragment(input: VertexOutput) -> FieldOutput {
  let point = fieldWorld(input.uv);
  let waterDistance = point.y - shorelineFront(point.x, overlay.waveFront.y, overlay.waveFront.z);
  var output: FieldOutput;
  if (waterDistance < -overlay.waveShape.x * 3.0) {
    output.surface = vec4f(0.0);
    output.motion = vec4f(0.0);
    return output;
  }
  let wave = waveField(point, waterDistance, overlay.waveFront.z);
  let foam = foamCoverage(point, waterDistance, overlay.waveFront.z);
  output.surface = vec4f(wave.height, wave.slope, foam);
  output.motion = vec4f(wave.displacement, 0.0, 0.0);
  return output;
}
`

export const waterCausticShader = `
${waterCommonWgsl}
@group(0) @binding(1) var fieldSampler: sampler;
@group(0) @binding(2) var surfaceField: texture_2d<f32>;
@group(0) @binding(3) var motionField: texture_2d<f32>;
fn sampleWave(point: vec2f) -> WaveSample {
  let uv = fieldUv(point);
  let surface = textureSampleLevel(surfaceField, fieldSampler, uv, 0.0);
  let motion = textureSampleLevel(motionField, fieldSampler, uv, 0.0);
  return WaveSample(surface.r, surface.gb, motion.rg);
}
fn waterSurface(point: vec2f, time: f32, wave: WaveSample) -> vec4f {
  let waterDistance = point.y - shorelineFront(point.x, overlay.waveFront.y, time);
  let depth = filmDepth(waterDistance);
  let crest = frontCrest(waterDistance);
  let surfaceHeight = ${SAND.depth} + max(0.0007, depth + crest + wave.height);
  let frontScale = max(overlay.waveShape.y * 1.35, 0.012);
  let frontInfluence = exp(-pow((waterDistance - overlay.waveShape.y * 0.30) / frontScale, 2.0));
  let frontSlope = 0.085 * frontInfluence;
  let slope = wave.slope + vec2f(0.0, frontSlope);
  return vec4f(normalize(vec3f(-slope.x, 1.0, -slope.y)), surfaceHeight);
}
fn flatLightLanding(surfacePoint: vec2f, time: f32, sunDirection: vec3f) -> vec2f {
  let waterDistance = surfacePoint.y - shorelineFront(surfacePoint.x, overlay.waveFront.y, time);
  let depth = filmDepth(waterDistance) + frontCrest(waterDistance);
  let originY = ${SAND.depth} + max(depth, 0.0007);
  let transmitted = refract(-sunDirection, vec3f(0.0, 1.0, 0.0), 1.0 / 1.333);
  let distance = (${SAND.depth} - originY) / min(transmitted.y, -0.0001);
  return surfacePoint + transmitted.xz * max(distance, 0.0);
}
fn waveLightLanding(surfacePoint: vec2f, time: f32, sunDirection: vec3f) -> vec2f {
  let wave = sampleWave(surfacePoint);
  let surface = waterSurface(surfacePoint, time, wave);
  let transmitted = refract(-sunDirection, surface.xyz, 1.0 / 1.333);
  let distance = (${SAND.depth} - surface.w) / min(transmitted.y, -0.0001);
  return surfacePoint + wave.displacement + transmitted.xz * max(distance, 0.0);
}
fn inverseLightSurface(bedPoint: vec2f, time: f32, sunDirection: vec3f) -> vec2f {
  var surfacePoint = bedPoint;
  for (var iteration = 0; iteration < 2; iteration++) {
    let landed = waveLightLanding(surfacePoint, time, sunDirection);
    surfacePoint -= (landed - bedPoint) * 0.92;
  }
  return surfacePoint;
}
fn differentialCaustic(bedPoint: vec2f, time: f32, sunDirection: vec3f) -> f32 {
  let surfacePoint = inverseLightSurface(bedPoint, time, sunDirection);
  let epsilon = ${WATER_FIELD_TEXEL.toFixed(9)};
  let dx = vec2f(epsilon, 0.0);
  let dz = vec2f(0.0, epsilon);
  let newCenter = waveLightLanding(surfacePoint, time, sunDirection);
  let newDx = waveLightLanding(surfacePoint + dx, time, sunDirection) - newCenter;
  let newDz = waveLightLanding(surfacePoint + dz, time, sunDirection) - newCenter;
  let oldCenter = flatLightLanding(surfacePoint, time, sunDirection);
  let oldDx = flatLightLanding(surfacePoint + dx, time, sunDirection) - oldCenter;
  let oldDz = flatLightLanding(surfacePoint + dz, time, sunDirection) - oldCenter;
  let oldArea = abs(oldDx.x * oldDz.y - oldDx.y * oldDz.x);
  let newArea = max(abs(newDx.x * newDz.y - newDx.y * newDz.x), oldArea * 0.10);
  let concentration = clamp(oldArea / max(newArea, 1e-8), 0.30, 8.0);
  let waterDistance = surfacePoint.y - shorelineFront(surfacePoint.x, overlay.waveFront.y, time);
  let depth = filmDepth(waterDistance) + frontCrest(waterDistance);
  let visibleDepth = smoothstep(0.002, 0.008, depth) * (1.0 - smoothstep(0.040, 0.075, depth));
  return mix(1.0, pow(concentration, 1.18), visibleDepth);
}
@fragment fn fragment(input: VertexOutput) -> @location(0) f32 {
  let bedPoint = fieldWorld(input.uv);
  let waterDistance = bedPoint.y - shorelineFront(bedPoint.x, overlay.waveFront.y, overlay.waveFront.z);
  if (waterDistance < -overlay.waveShape.x * 0.20) { return 1.0; }
  let sunDirection = normalize(vec3f(0.6967067, 0.65, -0.7173561));
  return differentialCaustic(bedPoint, overlay.waveFront.z, sunDirection);
}
`

export const waterOverlayShader = `
${waterCommonWgsl}
struct SurfaceHit {
  position: vec3f,
  normal: vec3f,
  waterDistance: f32,
}
@group(0) @binding(1) var postSampler: sampler;
@group(0) @binding(2) var sourceTexture: texture_2d<f32>;
@group(0) @binding(3) var surfaceField: texture_2d<f32>;
@group(0) @binding(4) var causticFieldTexture: texture_2d<f32>;
fn toLinear(color: vec3f) -> vec3f {
  let low = color / 12.92;
  let high = pow(max((color + 0.055) / 1.055, vec3f(0.0)), vec3f(2.4));
  return select(low, high, color > vec3f(0.04045));
}
fn toSrgb(color: vec3f) -> vec3f {
  let safe = max(color, vec3f(0.0));
  let low = safe * 12.92;
  let high = 1.055 * pow(safe, vec3f(1.0 / 2.4)) - 0.055;
  return select(low, high, safe > vec3f(0.0031308));
}
fn viewRay(uv: vec2f) -> vec3f {
  let screen = vec2f(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0);
  return normalize(
    overlay.forward.xyz
    + screen.x * overlay.eye.w * overlay.forward.w * overlay.right.xyz
    + screen.y * overlay.eye.w * overlay.up.xyz
  );
}
fn intersectBed(uv: vec2f) -> vec4f {
  let direction = viewRay(uv);
  let distance = (${SAND.depth} - overlay.eye.y) / direction.y;
  let world = overlay.eye.xyz + direction * distance;
  return vec4f(world.x, world.z, distance, select(0.0, 1.0, distance > 0.0));
}
fn projectWorld(world: vec3f) -> vec2f {
  let relative = world - overlay.eye.xyz;
  let forwardDistance = max(dot(relative, overlay.forward.xyz), 0.0001);
  let horizontal = dot(relative, overlay.right.xyz) / (forwardDistance * overlay.eye.w * overlay.forward.w);
  let vertical = dot(relative, overlay.up.xyz) / (forwardDistance * overlay.eye.w);
  return vec2f(horizontal * 0.5 + 0.5, 0.5 - vertical * 0.5);
}
fn sampleSurface(point: vec2f) -> vec4f {
  return textureSampleLevel(surfaceField, postSampler, fieldUv(point), 0.0);
}
fn waterSurface(point: vec2f, waterDistance: f32) -> vec4f {
  let wave = sampleSurface(point);
  let depth = filmDepth(waterDistance);
  let crest = frontCrest(waterDistance);
  let surfaceHeight = ${SAND.depth} + max(0.0007, depth + crest + wave.r);
  let frontScale = max(overlay.waveShape.y * 1.35, 0.012);
  let frontInfluence = exp(-pow((waterDistance - overlay.waveShape.y * 0.30) / frontScale, 2.0));
  let frontSlope = 0.085 * frontInfluence;
  let slope = wave.gb + vec2f(0.0, frontSlope);
  return vec4f(normalize(vec3f(-slope.x, 1.0, -slope.y)), surfaceHeight);
}
fn solveSurface(uv: vec2f, time: f32) -> SurfaceHit {
  let direction = viewRay(uv);
  var distance = (${SAND.depth} - overlay.eye.y) / direction.y;
  var position = overlay.eye.xyz + direction * distance;
  var waterDistance = position.z - shorelineFront(position.x, overlay.waveFront.y, time);
  var surface = waterSurface(position.xz, waterDistance);
  for (var iteration = 0; iteration < 3; iteration++) {
    distance = (surface.w - overlay.eye.y) / direction.y;
    position = overlay.eye.xyz + direction * distance;
    waterDistance = position.z - shorelineFront(position.x, overlay.waveFront.y, time);
    surface = waterSurface(position.xz, waterDistance);
  }
  position = overlay.eye.xyz + direction * ((surface.w - overlay.eye.y) / direction.y);
  waterDistance = position.z - shorelineFront(position.x, overlay.waveFront.y, time);
  surface = waterSurface(position.xz, waterDistance);
  return SurfaceHit(vec3f(position.x, surface.w, position.z), surface.xyz, waterDistance);
}
fn cloudMask(directionRaw: vec3f, time: f32) -> f32 {
  let direction = normalize(directionRaw);
  if (direction.y <= 0.018) { return 0.0; }
  var uv = direction.xz / max(direction.y, 0.055);
  uv = uv * 0.40 + vec2f(time * 0.0048, -time * 0.0027);
  let broad = valueNoise(uv * 0.78);
  let detail = valueNoise(uv * 2.05 + vec2f(12.7, -8.3));
  let wisps = valueNoise(uv * 4.3 + vec2f(-4.1, 9.6));
  let density = broad * 0.62 + detail * 0.28 + wisps * 0.10;
  return smoothstep(0.49, 0.68, density) * smoothstep(0.025, 0.24, direction.y);
}
fn skyRadiance(directionRaw: vec3f, sunDirection: vec3f, time: f32) -> vec3f {
  let direction = normalize(directionRaw);
  let upward = clamp(direction.y, -1.0, 1.0);
  let horizon = vec3f(0.74, 0.89, 1.06);
  let zenith = vec3f(0.12, 0.40, 0.90);
  let below = vec3f(0.035, 0.085, 0.10);
  var color = select(
    mix(horizon, below, clamp(-upward * 3.0, 0.0, 1.0)),
    mix(horizon, zenith, pow(max(upward, 0.0), 0.46)),
    upward >= 0.0
  );
  let cloud = cloudMask(direction, time);
  let sunAmount = max(dot(direction, sunDirection), 0.0);
  let cloudLight = mix(vec3f(0.72, 0.80, 0.90), vec3f(1.30, 1.18, 1.02), 0.55 + 0.45 * sunAmount);
  color = mix(color, cloudLight, cloud * 0.82);
  let innerAureole = pow(sunAmount, 420.0) * 1.8;
  let outerAureole = pow(sunAmount, 28.0) * 0.20;
  color += vec3f(1.0, 0.86, 0.64) * (innerAureole + outerAureole) * (1.0 - cloud * 0.62);
  return color;
}
fn fresnelDielectric(cosineIncident: f32, etaIncident: f32, etaTransmitted: f32) -> f32 {
  let cosI = clamp(cosineIncident, 0.0, 1.0);
  let eta = etaIncident / etaTransmitted;
  let sinT2 = eta * eta * max(0.0, 1.0 - cosI * cosI);
  if (sinT2 >= 1.0) { return 1.0; }
  let cosT = sqrt(max(0.0, 1.0 - sinT2));
  let rsNumerator = etaIncident * cosI - etaTransmitted * cosT;
  let rsDenominator = etaIncident * cosI + etaTransmitted * cosT;
  let rpNumerator = etaTransmitted * cosI - etaIncident * cosT;
  let rpDenominator = etaTransmitted * cosI + etaIncident * cosT;
  let rs = rsNumerator / max(abs(rsDenominator), 0.00001);
  let rp = rpNumerator / max(abs(rpDenominator), 0.00001);
  return clamp(0.5 * (rs * rs + rp * rp), 0.0, 1.0);
}
fn ggxDistribution(noH: f32, roughness: f32) -> f32 {
  let alpha = roughness * roughness;
  let alpha2 = alpha * alpha;
  let denominator = noH * noH * (alpha2 - 1.0) + 1.0;
  return alpha2 / max(3.14159265 * denominator * denominator, 0.0001);
}
fn smithVisibility(noV: f32, noL: f32, roughness: f32) -> f32 {
  let alpha = roughness * roughness;
  let k = alpha * 0.5;
  let gv = noV / max(noV * (1.0 - k) + k, 0.0001);
  let gl = noL / max(noL * (1.0 - k) + k, 0.0001);
  return gv * gl;
}
fn refractedBedWorld(surface: SurfaceHit, incident: vec3f, eta: f32) -> vec3f {
  let transmitted = refract(incident, surface.normal, eta);
  let distance = (${SAND.depth} - surface.position.y) / min(transmitted.y, -0.0001);
  return surface.position + transmitted * max(distance, 0.0);
}
fn edgeSafeRefractionUv(sampleUv: vec2f, dimensions: vec2f) -> vec2f {
  let halfTexel = vec2f(0.5) / dimensions;
  let span = max(vec2f(1.0) - halfTexel * 2.0, vec2f(1e-6));
  let normalized = (sampleUv - halfTexel) / span;
  // Mirror the finite scene color at the framebuffer boundary. This preserves
  // refractive motion all the way to the screen edge without ever collapsing
  // an out-of-range footprint onto one clamped row/column.
  let mirrored = vec2f(1.0) - abs(fract(normalized * 0.5) * 2.0 - vec2f(1.0));
  return halfTexel + mirrored * span;
}
@fragment fn fragment(input: VertexOutput) -> @location(0) vec4f {
  let source = textureSampleLevel(sourceTexture, postSampler, input.uv, 0.0);
  let bed = intersectBed(input.uv);
  if (bed.w < 0.5) { return source; }

  let shoreline = shorelineFront(bed.x, overlay.waveFront.y, overlay.waveFront.z);
  let waterDistance = bed.y - shoreline;
  let waterMask = smoothstep(-overlay.waveShape.x * ${WAVE_RESET.waterMaskBackstep}, overlay.waveShape.x, waterDistance);
  if (waterMask <= 0.0001) { return source; }

  let incident = viewRay(input.uv);
  let surface = solveSurface(input.uv, overlay.waveFront.z);
  let viewDirection = normalize(-incident);
  let noV = max(dot(surface.normal, viewDirection), 0.001);
  let sunDirection = normalize(vec3f(0.6967067, 0.65, -0.7173561));

  let reflectedDirection = reflect(incident, surface.normal);
  let fresnel = fresnelDielectric(noV, 1.0, 1.333);
  let reflection = skyRadiance(reflectedDirection, sunDirection, overlay.waveFront.z) * 2.15;

  let bedRed = refractedBedWorld(surface, incident, 1.0 / 1.3310);
  let bedGreen = refractedBedWorld(surface, incident, 1.0 / 1.3330);
  let bedBlue = refractedBedWorld(surface, incident, 1.0 / 1.3370);
  let projectedRed = projectWorld(bedRed);
  let projectedGreen = projectWorld(bedGreen);
  let projectedBlue = projectWorld(bedBlue);
  let sourceDimensions = max(vec2f(textureDimensions(sourceTexture, 0)), vec2f(1.0));
  let redSample = textureSampleLevel(sourceTexture, postSampler, edgeSafeRefractionUv(projectedRed, sourceDimensions), 0.0).rgb;
  let greenSample = textureSampleLevel(sourceTexture, postSampler, edgeSafeRefractionUv(projectedGreen, sourceDimensions), 0.0).rgb;
  let blueSample = textureSampleLevel(sourceTexture, postSampler, edgeSafeRefractionUv(projectedBlue, sourceDimensions), 0.0).rgb;
  let refractedSrgb = vec3f(redSample.r, greenSample.g, blueSample.b);
  var refractedBed = toLinear(refractedSrgb);

  let transmittedRay = refract(incident, surface.normal, 1.0 / 1.333);
  let pathLength = max((surface.position.y - ${SAND.depth}) / max(abs(transmittedRay.y), 0.06), 0.0);
  let causticField = textureSampleLevel(causticFieldTexture, postSampler, fieldUv(bedGreen.xz), 0.0).r;
  let causticPositive = max(causticField - 1.0, 0.0);
  let causticNegative = max(1.0 - causticField, 0.0);
  let causticLace = smoothstep(1.02, 1.16, causticField) * pow(clamp(causticPositive * 0.95, 0.0, 6.0), 1.10);
  let causticDepth = smoothstep(0.003, 0.010, pathLength) * (1.0 - smoothstep(0.038, 0.075, pathLength));
  let causticGain = 1.0 + causticPositive * 0.26 - causticNegative * 0.08;
  refractedBed *= vec3f(causticGain * 1.040, causticGain * 1.020, causticGain * 0.992);

  let extinction = vec3f(0.34, 0.075, 0.030) * mix(0.84, 1.16, overlay.waveLook.x);
  let transmittance = exp(-extinction * pathLength);
  let scatterColor = vec3f(0.018, 0.115, 0.17) * mix(0.68, 1.14, overlay.waveLook.x);
  var transmission = refractedBed * transmittance + scatterColor * (vec3f(1.0) - transmittance);
  let causticColor = vec3f(1.0, 0.97, 0.86) * 0.20 + vec3f(0.84, 0.94, 1.0) * 0.05;
  transmission += causticColor * (causticLace * causticDepth);

  let halfVector = normalize(viewDirection + sunDirection);
  let noL = max(dot(surface.normal, sunDirection), 0.0);
  let noH = max(dot(surface.normal, halfVector), 0.0);
  let voH = max(dot(viewDirection, halfVector), 0.0);
  let roughness = mix(0.055, 0.024, clamp(overlay.waveLook.y, 0.0, 1.0));
  let microFresnel = fresnelDielectric(voH, 1.0, 1.333);
  let specularBrdf = ggxDistribution(noH, roughness) * smithVisibility(noV, noL, roughness) * microFresnel
    / max(4.0 * noV * max(noL, 0.001), 0.001);
  let sunSpecular = vec3f(1.0, 0.88, 0.69) * specularBrdf * noL * 2.4;

  let sunMirror = max(dot(reflectedDirection, sunDirection), 0.0);
  let glitter = pow(sunMirror, 340.0) * 2.2 + pow(sunMirror, 85.0) * 0.24;
  let waveMicro = 0.68 + 0.32 * valueNoise(surface.position.xz * 84.0 + vec2f(overlay.waveFront.z * 1.4, -overlay.waveFront.z * 1.1));
  let sunGlitter = vec3f(1.0, 0.92, 0.76) * glitter * waveMicro;

  let nearFront = 1.0 - smoothstep(0.0, overlay.waveShape.y * 2.2, surface.waterDistance);
  let forwardScatter = pow(max(dot(viewDirection, -sunDirection), 0.0), 4.0) * nearFront;
  transmission += scatterColor * (nearFront * 0.08 + forwardScatter * 0.11) * (1.0 - fresnel);

  var waterColor = transmission * (1.0 - fresnel) + reflection * fresnel + sunSpecular + sunGlitter;
  let opticalWeight = mix(0.88, 1.0, overlay.waveShape.w) * waterMask;
  let sourceLinear = toLinear(source.rgb);
  var color = mix(sourceLinear, waterColor, opticalWeight);

  let foam = sampleSurface(surface.position.xz).a * waterMask;
  let foamLight = 0.62 + noL * 0.38;
  let foamColor = vec3f(0.94, 0.975, 1.0) * foamLight + reflection * 0.08;
  let foamOpacity = foam * mix(0.54, 0.82, smoothstep(0.0, 0.9, foam));
  color = mix(color, foamColor, foamOpacity);
  color += vec3f(1.0, 0.96, 0.88) * foam * sunGlitter * 0.07;

  return vec4f(clamp(toSrgb(color), vec3f(0.0), vec3f(1.0)), source.a);
}
`
